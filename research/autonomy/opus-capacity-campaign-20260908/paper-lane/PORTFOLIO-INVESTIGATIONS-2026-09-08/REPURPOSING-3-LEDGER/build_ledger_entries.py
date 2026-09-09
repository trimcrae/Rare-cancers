#!/usr/bin/env python3
"""Build the UNAPPLIED ledger diff for REPURPOSING-3's four new unanchored identifiers.

Writes a candidate copy of research/manuscripts/citation-provenance-ledger.json into this lane's
directory. It does NOT touch the real ledger. The diff is produced with `git diff --no-index`.

Every metadata string below is copied VERBATIM from the PubMed MCP tool responses recorded in
checks/02..05. Nothing here is typed from memory.
"""
import json
import os

#: 2026-09-08: this walk was one level short on the first run (checks/06, exit 1, FileNotFoundError
#: on .../research/research/manuscripts/...). The file sits six directories below the repo root, so
#: seven dirname() applications are needed: the first strips the filename.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))))
LEDGER = os.path.join(ROOT, "research/manuscripts/citation-provenance-ledger.json")
#: ⛔ THE CANDIDATE MUST NOT LIVE IN THE REPOSITORY, AND THIS IS MEASURED, NOT CAUTIOUS
#: (checks/10 and checks/11, 2026-09-08). `lint_citations._tracked()` scans committed AND
#: untracked-but-not-ignored files, and any `.json` is an ANCHOR. A copy of the ledger sitting in
#: the tree therefore anchors every identifier the ledger names: with the copy present and the
#: REAL ledger otherwise unchanged, unanchored fell 548 -> 446 and all four REPURPOSING-3 errors
#: disappeared without a single ledger row being added. That is the 2026-08-07 self-anchoring
#: incident exactly — a gate turned green by adding a file. So the candidate is written OUTSIDE
#: the checkout (scratchpad), the diff is generated from there, and only the diff is retained.
OUT = os.environ.get(
    "LEDGER_CANDIDATE_OUT",
    "/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/citation-provenance-ledger.candidate.json",
)

#: The two REPURPOSING-3 files the gate measured (checks/01), plus this lane's own FINDING.md,
#: which quotes the same four identifiers while explaining them. `files` is descriptive: the gate
#: keys only on `key`, so this list is for a human reader, not for the matcher.
FILES = [
    "research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3-LEDGER/FINDING.md",
    "research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3/FINDING.md",
    "research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3/FIVE-REFERENCE-TABLE.md",
]

HIGUCHI_BY = (
    "PubMed MCP connector, tool response-date 2026-09-08 20:42:25 UTC (the session clock had rolled "
    "to 2026-09-09; the stamp here is the one the tool returned). Two independent calls, both "
    "recorded in full: convert_article_ids(id_type=doi, ids=['10.1002/cam4.1438']) returned "
    "{pmcid: PMC5943440, pmid: 29573200, doi: 10.1002/cam4.1438}, and "
    "convert_article_ids(id_type=pmcid, ids=['PMC5943440']) returned the same triple from the other "
    "direction; get_article_metadata(pmids=['29573200']) then returned the record whose title, "
    "journal.iso_abbreviation, publication_date.year and article_types are copied into this row. "
    "The DOI, PMID and PMCID cited in prose all appear in that one record, so the three rows added "
    "for this paper are three forms of ONE retrieval, not three checks."
)
HIGUCHI_TITLE = ("Anti-tumor effects of a nonsteroidal anti-inflammatory drug zaltoprofen on "
                 "chondrosarcoma via activating peroxisome proliferator-activated receptor gamma "
                 "and suppressing matrix metalloproteinase-2 expression.")
HIGUCHI_NOTE_TAIL = (
    "PubMed article_types, verbatim: ['Case Reports', 'Journal Article', "
    "'Research Support, Non-U.S. Gov't']; citation, verbatim: volume 7, issue 5, pages 1944-1954. "
    "⚠ WHAT THIS ROW DOES NOT SAY: the record was read, its identifiers agree with the prose and its "
    "type is Case Reports as the prose states — nothing here evaluates the n=1 report's clinical "
    "meaning, and the citing prose explicitly draws no efficacy, safety, selectivity or "
    "therapeutic-window conclusion from it. The patient in it has grade 2 cervical chondrosarcoma, "
    "NOT extraskeletal myxoid chondrosarcoma."
)
CHOW_BY = (
    "PubMed MCP connector, tool response-date 2026-09-08 (session clock 2026-09-09). ⚠ THE "
    "CONVERTER DID NOT RESOLVE IT: convert_article_ids(id_type=doi) returned the bare echo "
    "{doi: 10.1097/CCO.0b013e32812143d9} with no pmid and no pmcid — which looks identical to a DOI "
    "that does not exist, and is the same shape recorded for DOI:10.1016/j.jclinepi.2017.08.010 on "
    "2026-08-27. It was resolved instead by lookup_article_by_citation(journal='Curr Opin Oncol', "
    "year=2007, volume='19', first_page='371', author='Chow'), which returned PMID 17545802; "
    "get_article_metadata(pmids=['17545802']) then returned a record whose identifiers.doi is "
    "10.1097/CCO.0b013e32812143d9 — matching the cited DOI exactly. That match, not the converter, "
    "is what anchors this row."
)

NEW = [
    {
        "files": FILES,
        "id": "10.1002/cam4.1438",
        "key": "DOI:10.1002/cam4.1438",
        "kind": "DOI",
        "note": "Retrieved 2026-09-08 by the PubMed MCP connector for REPURPOSING-3, which cites this "
                "paper as the adjacent zaltoprofen record found while reading reference [12]. " + HIGUCHI_NOTE_TAIL,
        "status": "verified",
        "checked_on": "2026-09-08",
        "checked_by": "REPURPOSING-3-LEDGER lane, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Retrieval "
                      "transcripts retained at research/autonomy/opus-capacity-campaign-20260908/"
                      "paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3-LEDGER/checks/.",
        "verified_on": "2026-09-08",
        "verified_by": HIGUCHI_BY,
        "verified_source": "PubMed",
        "verified_title": HIGUCHI_TITLE,
        "verified_journal": "Cancer Med",
        "verified_year": "2018",
        "verified_pmid": "29573200",
        "verified_pmcid": "PMC5943440",
    },
    {
        "files": FILES,
        "id": "10.1097/CCO.0b013e32812143d9",
        "key": "DOI:10.1097/CCO.0b013e32812143d9",
        "kind": "DOI",
        "note": "Reference [9] of research/manuscripts/repurposing/repurposing-hypotheses.md, quoted by "
                "REPURPOSING-3. PubMed article_types, verbatim: ['Journal Article', 'Review'] — which is "
                "what the citing prose calls it (a 2007 narrative review). PubMed returned no PMC "
                "identifier for it, consistent with REPURPOSING-3's recorded 'no PMC record' finding. "
                "citation, verbatim: volume 19, issue 4, pages 371-6.",
        "status": "verified",
        "checked_on": "2026-09-08",
        "checked_by": "REPURPOSING-3-LEDGER lane, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Retrieval "
                      "transcripts retained at research/autonomy/opus-capacity-campaign-20260908/"
                      "paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3-LEDGER/checks/.",
        "verified_on": "2026-09-08",
        "verified_by": CHOW_BY,
        "verified_source": "PubMed",
        "verified_title": "Update on chondrosarcomas.",
        "verified_journal": "Curr Opin Oncol",
        "verified_year": "2007",
        "verified_pmid": "17545802",
        "verified_pmcid": None,
    },
    {
        "files": FILES,
        "id": "PMC5943440",
        "key": "PMCID:PMC5943440",
        "kind": "PMCID",
        "note": "The PMCID form of DOI:10.1002/cam4.1438, added in this same change. ONE retrieval, three "
                "identifier forms: the PubMed record returned for PMID 29573200 carries all three, and "
                "convert_article_ids was additionally run in the pmcid direction on PMC5943440 itself and "
                "returned the same triple. This row is NOT an independent second check. " + HIGUCHI_NOTE_TAIL,
        "status": "verified",
        "checked_on": "2026-09-08",
        "checked_by": "REPURPOSING-3-LEDGER lane, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Retrieval "
                      "transcripts retained at research/autonomy/opus-capacity-campaign-20260908/"
                      "paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3-LEDGER/checks/.",
        "verified_on": "2026-09-08",
        "verified_by": HIGUCHI_BY,
        "verified_source": "PubMed",
        "verified_title": HIGUCHI_TITLE,
        "verified_journal": "Cancer Med",
        "verified_year": "2018",
        "verified_pmid": "29573200",
        "verified_pmcid": "PMC5943440",
    },
    {
        "files": FILES,
        "id": "29573200",
        "key": "PMID:29573200",
        "kind": "PMID",
        "note": "The PMID form of DOI:10.1002/cam4.1438, added in this same change. It is the identifier "
                "get_article_metadata was actually called with, so of the three forms it is the one the "
                "record was fetched by. " + HIGUCHI_NOTE_TAIL,
        "status": "verified",
        "checked_on": "2026-09-08",
        "checked_by": "REPURPOSING-3-LEDGER lane, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Retrieval "
                      "transcripts retained at research/autonomy/opus-capacity-campaign-20260908/"
                      "paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3-LEDGER/checks/.",
        "verified_on": "2026-09-08",
        "verified_by": HIGUCHI_BY,
        "verified_source": "PubMed",
        "verified_title": HIGUCHI_TITLE,
        "verified_journal": "Cancer Med",
        "verified_year": "2018",
        "verified_pmid": "29573200",
        "verified_pmcid": "PMC5943440",
    },
]

CLASS_NOTE_KEY = "_repurposing3_class_added_2026_09_08"
CLASS_NOTE = (
    "⛔ THESE 4 ROWS ARE NOT PART OF THE 2026-08-07 BASELINE AND ARE NOT AN AMNESTY. They are the four "
    "identifiers that REPURPOSING-3's prose (FINDING.md and FIVE-REFERENCE-TABLE.md, campaign "
    "OPUS-CAPACITY-CAMPAIGN-20260908) introduced into the gate on 2026-09-08 — DOI 10.1002/cam4.1438, "
    "DOI 10.1097/CCO.0b013e32812143d9, PMCID PMC5943440 and PMID 29573200 — measured by re-running "
    "lint_citations.py and filtering its 463 ::error:: lines to that path (checks/01). ⭐ EACH WAS "
    "RETRIEVED BEFORE IT WAS RECORDED, by the PubMed MCP connector, and every title, journal "
    "abbreviation, year and article-type string in these rows is copied verbatim from the returned "
    "record; no citation was typed from recollection, which is the failure the gate exists for. "
    "⚠ THEY ARE THREE FORMS OF TWO PAPERS, NOT FOUR CHECKS: 10.1002/cam4.1438, PMC5943440 and "
    "29573200 are one Cancer Med 2018 record, and each row says so. ⚠ AND `verified` HERE MEANS WHAT "
    "IT MEANS ELSEWHERE IN THIS FILE — the identifier was fetched and PubMed answered. No fetch "
    "product in this repository carries these four; the count falls the honest way when a CI job with "
    "real egress writes a committed record for them. Nothing in lint_citations.py, its matcher, its "
    "baseline or any allowlist was changed to accommodate them."
)


def main():
    with open(LEDGER, encoding="utf-8") as fh:
        doc = json.load(fh)
    known = {e["key"] for e in doc["entries"]}
    for row in NEW:
        assert row["key"] not in known, "refusing to duplicate an existing ledger key: %s" % row["key"]
    doc["entries"].extend(NEW)
    assert CLASS_NOTE_KEY not in doc
    doc[CLASS_NOTE_KEY] = CLASS_NOTE
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print("wrote %s (%d entries, +%d)" % (OUT, len(doc["entries"]), len(NEW)))


if __name__ == "__main__":
    main()
