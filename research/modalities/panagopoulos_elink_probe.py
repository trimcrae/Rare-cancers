#!/usr/bin/env python3
"""Ask ONE paper at a time whether it deposited sequences — so a zero is a MEASURED zero.

⭐ THE QUESTION. Panagopoulos et al. 2002 (PMID 12378528) is the 18-case series that supplies the
whole within-partner breakpoint distribution for EWSR1::NR4A3. Its abstract names type 1 (EWS exon
12 :: CHN exon 3, ten tumours) and type 5 (exon 13 :: exon 3, two cases) and leaves the remaining
EWSR1-rearranged tumours' transcript types UNNAMED. The full text is genuinely paywalled: eight
Wiley endpoints 403 including the issue TOC, Unpaywall/OpenAlex/OpenAIRE/Semantic Scholar all
closed with no repository copy, no PMCID, a Lund submitted-version record that is metadata with no
file, a thesis repository item with zero attached bitstreams, and all 72 citing papers fetched
without one restating the type table. So the prose route is closed.

⭐ WHY THE SEQUENCE-DATABASE ROUTE IS ASKED INSTEAD, AND WHY IT IS ASKED AGAIN. `elink` from a
paper's PubMed record to `nuccore` returns the sequences deposited WITH it, and that route has
broken this exact problem open twice: the TCF12::NR4A3 breakpoint came back as GenBank AF289510.1
(chromosome-tagged source features splitting the record at the junction) after ~1,030 papers failed
to supply it, and EWSR1 exon 10 :: NR4A3 intron-2 cryptic exon came back as AF524261.1.

⛔⛔ AND THE EXISTING RECORD CANNOT SAY WHETHER THIS PAPER WAS EVER ASKED — WHICH IS THE ENTIRE
REASON THIS FILE IS SEPARATE FROM `nr4a3_nuccore_sweep.py`. That sweep batches PMIDs 100 at a time
and stores ONLY batch totals: `nr4a3-nuccore-sweep-inputs.json` shows PMID 12378528 sitting inside
`searches[114..117].ids` and four elink calls recording `n_in: 100, n_linked: 741` and friends, with
no per-PMID result anywhere. That artifact therefore cannot distinguish

    (a) "elink returned nothing for PMID 12378528"        <- an ANSWER
    (b) "PMID 12378528's result was never separated out"  <- NOT an answer

and only (a) closes the question. An absent reading is not a reading of absence. So every call here
carries exactly ONE id, and the id NCBI echoes back in the linkset is checked against the id asked
for, so the result can never again be ambiguous about which paper was asked.

WHAT IT PRODUCES. Per PMID and per target database, the verbatim request URL, the HTTP status, the
echoed linkset id, the link names, and the UID list. Outcomes are graded into three states that must
never be collapsed: LINKED, MEASURED_ZERO, and ERROR_NO_MEASUREMENT — the last is a failure to
observe and is NEVER reported as a zero.

⛔ ORDER OF READING, AND IT IS ENFORCED BY CONSTRUCTION. Where a deposit comes back, its junction is
DERIVED from the record's own nucleotide sequence against this repository's committed transcript
models FIRST (`sequence_derived_junction`), and the depositor's own annotation is extracted only
afterwards into a SEPARATE field (`depositor_annotation`), with an explicit agreement verdict. The
derivation function never receives the annotation text. That ordering is what made the AF524261.1
recovery trustworthy — the alignment named EWSR1 exon 10, and the depositor's misc_feature note then
independently agreed.

⛔ WHAT THIS IS NOT. Not a breakpoint distribution. Not a coverage, efficacy, safety,
therapeutic-window or clinical-readiness claim. Not a patient count. A deposit is one tumour or one
construct, never a series.

$0 — NCBI E-utilities on a free CPU runner. Pure stdlib. The dev sandbox's egress proxy 403s NCBI on
CONNECT, which is why this runs on a runner (CLAUDE.md §6).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from emc_fusion_read_scan import ACCEPTOR, JunctionScanner, exon_seq, load_genes  # noqa: E402
from nr4a3_nuccore_sweep import (  # noqa: E402
    assign_junction,
    classify_material,
    discover_junction,
    parse_flatfile,
)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "Rare-cancers/panagopoulos_elink_probe (+https://github.com/trimcrae/Rare-cancers)"
OUT = os.path.join(HERE, "panagopoulos-elink-probe.json")

# ---------------------------------------------------------------------------- what is being asked
#
# ⛔ THE PMIDs ARE THE INPUT, NOT A FINDING. They are the two series in the pooled within-partner
# basis. Everything else about each paper below — title, authors, journal — is left EMPTY here and
# filled in at runtime from `esummary`, because a probe that names its own targets from memory
# cannot prove it aimed at the right paper. The runtime title is the proof of aim.
TARGETS = [
    {
        "pmid": "12378528",
        "why_this_paper": (
            "The 18-case series that supplies the whole within-partner breakpoint distribution. Its "
            "abstract names type 1 (EWS exon 12 :: CHN exon 3) and type 5 (exon 13 :: exon 3) and "
            "leaves the remaining EWSR1-rearranged tumours' transcript types unnamed. That unnamed "
            "block is the largest remaining piece of unreachable coverage."
        ),
        "what_a_deposit_would_settle": (
            "A deposited chimeric cDNA from this series would name an exon pair the abstract does "
            "not — turning an inferred distribution row into a sequence-derived one."
        ),
    },
    {
        "pmid": "29937513",
        "why_this_paper": (
            "The second series in the pooled within-partner basis. A whole-transcriptome cohort may "
            "have deposited per-case junctions."
        ),
        "what_a_deposit_would_settle": (
            "Per-case junction deposits would give a second, independent within-partner "
            "distribution rather than a second copy of the same one."
        ),
    },
]

TARGET_DBS = ["nuccore", "protein"]

# ---------------------------------------------------------------------------------- the controls
#
# ⛔⛔ AN INSTRUMENT THAT CANNOT RE-FIND A KNOWN LINK IS NOT ENTITLED TO REPORT AN ABSENCE, and a
# zero from a silently-broken query is indistinguishable from a zero from a paper that deposited
# nothing. That is the whole risk of this probe: its expected result IS a zero, so a query that
# quietly stopped working would produce exactly the answer being looked for. Both controls run in
# the SAME job against the SAME endpoint in the SAME session as the targets, because a control that
# passed yesterday says nothing about the network path the targets took today.
#
# The positive control's ground truth is NOT typed here. It is read at runtime from
# research/literature/tcf12-nr4a3-breakpoint-primary-sources.json, which committed the PMID, the
# nuccore UID and the accession when the TCF12 breakpoint was recovered.
POSITIVE_CONTROL_SOURCE = os.path.join(
    HERE, "..", "literature", "tcf12-nr4a3-breakpoint-primary-sources.json"
)

# A syntactically valid id that indexes no record. Expects LINKED=0 *and* an empty/absent linkset —
# it proves the pipeline does not manufacture links, which a positive control alone cannot.
NEGATIVE_CONTROL_PMID = "999999999"

MAX_RECORD_BP = 100_000  # same deposit-sized ceiling the sweep uses; a fusion cDNA is < a few kb


def _get(url, timeout=60, tries=3):
    """Every network read this module makes goes through here, and it records what it did."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", "replace")
                return {
                    "url": url,
                    "http_status": r.status,
                    "body": body,
                    "sha256_of_body": hashlib.sha256(body.encode()).hexdigest(),
                    "n_attempts": i + 1,
                }
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    return {
        "url": url,
        "http_status": None,
        "body": "",
        "sha256_of_body": None,
        "n_attempts": tries,
        "error": f"{type(last).__name__}: {last}",
    }


# ------------------------------------------------------------------- the single-PMID elink itself


def elink_one(pmid, to_db):
    """ONE PubMed id, ONE target database, and the answer graded into three states.

    ⛔ THE THREE STATES ARE THE POINT. Collapsing ERROR_NO_MEASUREMENT into MEASURED_ZERO is how a
    network failure gets published as a scientific negative, so the grading is explicit and the
    evidence for each grade is carried alongside it.
    """
    url = (
        f"{EUTILS}/elink.fcgi?dbfrom=pubmed&db={to_db}&retmode=json"
        f"&id={urllib.parse.quote(str(pmid))}"
    )
    rec = _get(url)
    out = {
        "pmid_asked": str(pmid),
        "to_db": to_db,
        "request_url_verbatim": url,
        "http_status": rec["http_status"],
        "sha256_of_response_body": rec["sha256_of_body"],
        "n_attempts": rec["n_attempts"],
    }
    if rec.get("error"):
        out["error"] = rec["error"]

    if rec["http_status"] != 200 or not rec["body"]:
        out["verdict"] = "ERROR_NO_MEASUREMENT"
        out["⛔ how_to_read_this"] = (
            "The endpoint did not answer. This is a FAILURE TO OBSERVE and must never be reported "
            "as 'the paper deposited nothing'."
        )
        out["response_body_verbatim"] = rec["body"][:2000]
        return out

    try:
        j = json.loads(rec["body"])
    except Exception as e:  # noqa: BLE001
        out["verdict"] = "ERROR_NO_MEASUREMENT"
        out["parse_error"] = f"{type(e).__name__}: {e}"
        out["response_body_verbatim"] = rec["body"][:2000]
        out["⛔ how_to_read_this"] = (
            "The endpoint answered with something that is not the expected JSON. FAILURE TO "
            "OBSERVE, not a zero."
        )
        return out

    linksets = j.get("linksets", [])
    out["n_linksets"] = len(linksets)

    # ⛔⛔ THE ECHO CHECK — THE ONE THING THAT MAKES THIS PROBE WORTH RUNNING AT ALL. NCBI echoes the
    # ids it actually resolved. Without checking it, a result is only evidence that SOME query ran;
    # with it, the record can name which paper was asked. This is exactly the ambiguity the batched
    # sweep left behind, so it is asserted rather than assumed.
    echoed = []
    for ls in linksets:
        echoed.extend(str(x) for x in ls.get("ids", []))
    out["linkset_ids_echoed_by_ncbi"] = echoed
    out["echo_matches_requested_pmid"] = echoed == [str(pmid)]

    # ⛔⛔ THE LINKNAME IS THE ANSWER, AND MERGING THE LINK SETS DESTROYS IT. Measured 2026-08-15 on
    # this very probe's first run: PMID 12378528 came back with 7 nuccore links and the run reported
    # "returned 7 records" — literally true and thoroughly misleading, because ALL SEVEN were
    # `pubmed_nuccore_refseq`: curated RefSeq reference records (NM_006981 NR4A3, NM_003487 TAF15,
    # …) that merely CITE the paper in their bibliography. Every paper about a gene links to that
    # gene's RefSeq entry; it says nothing about whether the authors deposited anything.
    #
    # The link set that means "the authors deposited this" is the bare `pubmed_nuccore`, and the
    # positive control PROVES the distinction is real rather than assumed: PMID 11156374 returns
    # BOTH `pubmed_nuccore` (carrying uid 13540159 = AF289510.1, the actual chimeric cDNA) and
    # `pubmed_nuccore_refseq`, in the same job, against the same endpoint, in the same session.
    # So the two are separated here and never summed.
    by_name = {}
    for ls in linksets:
        for db in ls.get("linksetdbs", []):
            name = db.get("linkname")
            if not name:
                continue
            by_name.setdefault(name, []).extend(str(x) for x in db.get("links", []))
    by_name = {k: sorted(set(v), key=lambda s: (len(s), s)) for k, v in by_name.items()}

    primary = f"pubmed_{to_db}"          # the authors' own submissions
    refseq = f"pubmed_{to_db}_refseq"    # curated records that cite the paper

    out["links_by_linkname"] = by_name
    out["linknames_returned"] = sorted(by_name)
    out["primary_deposit_linkname"] = primary
    out["primary_deposit_uids"] = by_name.get(primary, [])
    out["n_primary_deposits"] = len(out["primary_deposit_uids"])
    out["refseq_reference_uids"] = by_name.get(refseq, [])
    out["n_refseq_references"] = len(out["refseq_reference_uids"])
    out["⚠ what_the_two_link_sets_mean"] = (
        f"`{primary}` = sequence records SUBMITTED with this paper — the thing being looked for. "
        f"`{refseq}` = curated RefSeq entries that cite this paper in their bibliography; every "
        "paper about a gene links to that gene's RefSeq record, so it is not evidence of a deposit."
    )
    # kept so nothing downstream silently loses a uid, but it is NEVER the reported answer
    out["linked_uids_all_linknames_merged"] = sorted(
        {u for v in by_name.values() for u in v}, key=lambda s: (len(s), s)
    )
    out["n_linked"] = len(out["linked_uids_all_linknames_merged"])

    if not out["echo_matches_requested_pmid"]:
        out["verdict"] = "ERROR_NO_MEASUREMENT"
        out["⛔ how_to_read_this"] = (
            f"NCBI's linkset echoed ids {echoed!r}, which is not exactly the single id "
            f"{pmid!r} that was asked for. The response cannot be attributed to this paper, so it "
            "is not a measurement of this paper."
        )
        return out

    if out["n_primary_deposits"] > 0:
        out["verdict"] = "PRIMARY_DEPOSITS_PRESENT"
        out["✅ how_to_read_this"] = (
            f"elink pubmed->{to_db} for PMID {pmid} returned {out['n_primary_deposits']} record(s) "
            f"under `{primary}` — sequences submitted with this paper. They are analysed below; a "
            "link is not yet a junction."
        )
    elif out["n_refseq_references"] > 0:
        out["verdict"] = "NO_PRIMARY_DEPOSIT_ONLY_REFSEQ_REFERENCES"
        out["✅ how_to_read_this"] = (
            f"elink pubmed->{to_db} for PMID {pmid} returned 0 records under `{primary}` and "
            f"{out['n_refseq_references']} under `{refseq}`. The endpoint answered 200 and the "
            f"linkset echoed exactly id {pmid}, so this is a MEASURED zero for DEPOSITS by this "
            "paper specifically — the records it does link are curated reference entries that cite "
            "it, not submissions from it."
        )
    else:
        out["verdict"] = "MEASURED_ZERO"
        out["✅ how_to_read_this"] = (
            f"elink pubmed->{to_db} for PMID {pmid} returned 0 records of any kind. The endpoint "
            f"answered 200, the linkset echoed exactly id {pmid}, and it carried no link set at "
            "all. A MEASURED zero for THIS paper, not a batch total and not a failed read."
        )
    return out


# ------------------------------------------------------------------------------- paper provenance


def pubmed_summary(pmid):
    """Name the paper from NCBI, so the record proves which paper was asked — not just which number.

    ⛔ Every field here is quoted from the response. Nothing about these papers is typed from
    memory anywhere in this module.
    """
    url = f"{EUTILS}/esummary.fcgi?db=pubmed&retmode=json&id={urllib.parse.quote(str(pmid))}"
    rec = _get(url)
    out = {"request_url_verbatim": url, "http_status": rec["http_status"]}
    try:
        r = json.loads(rec["body"])["result"][str(pmid)]
    except Exception:  # noqa: BLE001
        out["resolved"] = False
        out["⚠ note"] = "esummary did not resolve this id to a record"
        out["response_body_verbatim"] = rec["body"][:600]
        return out
    if r.get("error"):
        out["resolved"] = False
        out["ncbi_error_verbatim"] = str(r.get("error"))
        return out
    out["resolved"] = True
    out["title_verbatim"] = r.get("title")
    out["journal_verbatim"] = r.get("fulljournalname") or r.get("source")
    out["pubdate_verbatim"] = r.get("pubdate")
    out["volume"] = r.get("volume")
    out["pages"] = r.get("pages")
    authors = [a.get("name") for a in (r.get("authors") or []) if a.get("name")]
    out["first_author_verbatim"] = authors[0] if authors else None
    out["n_authors"] = len(authors)
    out["doi"] = next(
        (i.get("value") for i in (r.get("articleids") or []) if i.get("idtype") == "doi"), None
    )
    out["pmcid"] = next(
        (i.get("value") for i in (r.get("articleids") or []) if i.get("idtype") == "pmc"), None
    )
    return out


# ------------------------------------------------------------------- fetching what came back, if any


def esummary_db(db, uids):
    meta = {}
    for i in range(0, len(uids), 200):
        batch = uids[i : i + 200]
        url = (
            f"{EUTILS}/esummary.fcgi?db={db}&retmode=json&id={','.join(str(u) for u in batch)}"
        )
        rec = _get(url, timeout=120)
        try:
            res = json.loads(rec["body"])["result"]
        except Exception:  # noqa: BLE001
            continue
        for uid in res.get("uids", []):
            r = res.get(uid, {})
            try:
                slen = int(r.get("slen") or 0)
            except (TypeError, ValueError):
                slen = 0
            meta[str(uid)] = {
                "uid": str(uid),
                "title_verbatim": r.get("title", ""),
                "slen": slen,
                "accession": r.get("accessionversion") or r.get("caption"),
                "createdate": r.get("createdate"),
                "subtype": r.get("subtype"),
            }
        time.sleep(0.35)
    return meta


def efetch_flat(db, uids, rettype):
    """GenBank/GenPept flatfiles WITH sequence, size-gated the way the sweep is.

    The size gate is not optional: alias tokens can link whole-genome records, and fetching those
    with `gbwithparts` is what OOM-killed two Actions runners before the sweep had this ceiling.
    """
    out, notes = {}, []
    for i in range(0, len(uids), 20):
        batch = uids[i : i + 20]
        url = (
            f"{EUTILS}/efetch.fcgi?db={db}&rettype={rettype}&retmode=text"
            f"&id={','.join(str(u) for u in batch)}"
        )
        rec = _get(url, timeout=120)
        notes.append({"url": url, "http_status": rec["http_status"], "n_bytes": len(rec["body"])})
        for chunk in re.split(r"\n(?=LOCUS\s)", rec["body"]):
            if not chunk.strip().startswith("LOCUS"):
                continue
            m = re.search(r"^ACCESSION\s+(\S+)", chunk, re.M)
            if m:
                out[m.group(1)] = chunk
        time.sleep(0.4)
    return out, notes


# ------------------------------------------ derive first, read the depositor's annotation second


def extract_depositor_annotation(text):
    """The depositor's OWN words about the record. Read only AFTER the junction is derived.

    ⛔ This function is called on the flatfile text; `analyse_deposit` below calls it strictly after
    the sequence-derived junction has been computed, and never passes its output into the
    derivation. That ordering is the guard against reading an exon number off a title and then
    'confirming' it.
    """
    ann = {}
    m = re.search(r"^DEFINITION\s+(.*?)(?=^\w|\Z)", text, re.M | re.S)
    ann["definition_verbatim"] = " ".join(m.group(1).split()) if m else None
    ann["notes_verbatim"] = [" ".join(n.split()) for n in re.findall(r'/note="([^"]+)"', text)][:12]
    ann["misc_features_verbatim"] = [
        " ".join(b.split())
        for b in re.findall(r"^\s{5}(misc_feature\s+[\s\S]*?)(?=^\s{5}\w|\Z)", text, re.M)
    ][:12]
    ann["cds_lines_verbatim"] = [
        " ".join(b.split())
        for b in re.findall(r"^\s{5}(CDS\s+[\s\S]*?)(?=^\s{5}\w|\Z)", text, re.M)
    ][:8]
    # exon numbers the depositor NAMES anywhere in the flatfile, quoted with their context
    ann["exon_mentions_verbatim"] = [
        " ".join(s.split())
        for s in re.findall(r"[^\n]{0,90}\bexons?\s+\d+[^\n]{0,90}", text, re.I)
    ][:20]
    ann["reference_pubmed_ids"] = sorted(set(re.findall(r"^\s+PUBMED\s+(\d+)", text, re.M)))
    return ann


def _derived_exon_pair(derived, seam):
    """The exon pair as a comparable tuple, from whichever derivation produced one."""
    if derived and derived.get("donor") and derived.get("acceptor"):
        return (
            derived.get("partner_gene"),
            derived["donor"].get("exon"),
            derived["acceptor"].get("exon"),
        )
    if seam:
        s = seam[0]
        return (s.get("partner_gene"), s.get("partner_exon"), s.get("acceptor_site"))
    return None


def analyse_deposit(acc, text, genes, scanner):
    """Everything asserted about one deposited record, in the order it must be read.

    STEP 1 parses structure and pulls the sequence. STEP 2 derives the junction from that sequence
    alone. STEP 3 — and only then — extracts what the depositor wrote, and STEP 4 compares them.
    """
    rec = parse_flatfile(text)
    seq = rec.pop("sequence", "")

    out = {
        "accession": rec.get("accession"),
        "version": rec.get("version"),
        "definition_is_reported_below_not_here": True,
        "length_bp": rec.get("length_bp"),
        "organism": rec.get("organism"),
        "tissue_types_verbatim": rec.get("tissue_types"),
        "cell_lines_verbatim": rec.get("cell_lines"),
        "chromosome_tagged_source_features": rec.get("chromosome_split"),
        "sequence_len": len(seq),
        "material_class": classify_material(rec),
    }

    # ---- STEP 2: DERIVE. The annotation has not been read at this point.
    seam = assign_junction(seq, genes, scanner) if seq else {"seam_match": [], "longest_blocks": {}}
    discovered = discover_junction(seq, genes) if seq else None
    out["sequence_derived_junction"] = {
        "_how": (
            "Derived from this record's OWN nucleotide sequence against the repository's committed "
            "transcript models. No title, definition or note was read to produce it."
        ),
        "seam_matcher": seam,
        "maximal_alignment": discovered,
    }
    out["is_nr4a3_fusion_by_sequence"] = bool(seam["seam_match"]) or (
        ACCEPTOR in seam["longest_blocks"] and len(seam["longest_blocks"]) > 1
    )

    # ---- STEP 3: only now, the depositor's own words.
    out["depositor_annotation"] = extract_depositor_annotation(text)

    # ---- STEP 4: do they agree?
    pair = _derived_exon_pair(discovered, seam["seam_match"])
    out["derived_exon_pair"] = pair
    if pair is None:
        out["agreement_with_depositor"] = "NO_DERIVED_JUNCTION — nothing to compare"
    else:
        ann_text = " ".join(
            [out["depositor_annotation"].get("definition_verbatim") or ""]
            + out["depositor_annotation"]["notes_verbatim"]
            + out["depositor_annotation"]["misc_features_verbatim"]
            + out["depositor_annotation"]["exon_mentions_verbatim"]
        )
        donor_exon = pair[1]
        named = bool(donor_exon) and bool(
            re.search(rf"\bexons?\s+(?:\d+\s+(?:to|through|-)\s+)?{donor_exon}\b", ann_text, re.I)
        )
        out["agreement_with_depositor"] = (
            f"DEPOSITOR_NAMES_THE_SAME_DONOR_EXON ({donor_exon})"
            if named
            else f"DEPOSITOR_DOES_NOT_STATE_A_DONOR_EXON — the derived call ({donor_exon}) stands "
            "on the alignment alone"
        )
    out["sequence_verbatim"] = seq
    out["flatfile_head_verbatim"] = "\n".join(text.splitlines()[:16])
    return out


# --------------------------------------------------------------------------------- the probe run


def load_positive_control():
    """PMID and expected UID read from the COMMITTED record, never typed here."""
    with open(os.path.abspath(POSITIVE_CONTROL_SOURCE)) as fh:
        d = json.load(fh)
    for r in d.get("records", []):
        if r.get("kind") == "sequence_deposit" and r.get("cites_pmid"):
            return {
                "pmid": str(r["cites_pmid"]),
                "expected_nuccore_uid": str(r.get("ncbi_nuccore_uid")),
                "expected_accession": r.get("version") or r.get("accession"),
                "_source": "research/literature/tcf12-nr4a3-breakpoint-primary-sources.json",
            }
    raise SystemExit("⛔ could not read the positive control from the committed record")


def run_probe():
    t0 = time.time()
    genes = load_genes()
    scanner = JunctionScanner(genes)

    pc = load_positive_control()

    # ---- CONTROLS FIRST, in the same session and against the same endpoint as the targets.
    pos = elink_one(pc["pmid"], "nuccore")
    # ⛔ The control asserts the DISCRIMINATION the whole probe rests on, not merely that something
    # came back: the known deposit must appear under the PRIMARY linkname `pubmed_nuccore`. If it
    # only showed up in the merged list, the probe could not tell a submission from a citation.
    pos_ok = (
        pos["verdict"] == "PRIMARY_DEPOSITS_PRESENT"
        and pc["expected_nuccore_uid"] in pos.get("primary_deposit_uids", [])
    )
    neg = elink_one(NEGATIVE_CONTROL_PMID, "nuccore")
    neg_ok = neg.get("n_linked", None) == 0

    controls = {
        "positive": {
            "what_it_proves": (
                "That elink pubmed->nuccore is answering correctly RIGHT NOW, on this network path, "
                "in this job, AND that a real deposit lands under the primary `pubmed_nuccore` "
                "linkname rather than the refseq one. Without it a zero from a broken query looks "
                "exactly like a zero from a paper that deposited nothing — and a zero is this "
                "probe's expected result."
            ),
            "observed_primary_deposit_uids": None,  # filled below from the result
            **pc,
            "result": pos,
            "passed": pos_ok,
            "⛔ if_this_failed": (
                "Any 'this paper deposited nothing' statement below is UNSUPPORTED — an instrument "
                "that cannot re-find a known deposit cannot certify an absence."
            ),
        },
        "negative": {
            "what_it_proves": (
                "That the pipeline does not manufacture links for an id that indexes nothing."
            ),
            "pmid": NEGATIVE_CONTROL_PMID,
            "result": neg,
            "passed": neg_ok,
        },
    }
    gate_ok = bool(pos_ok and neg_ok)

    # ---- THE TARGETS, one PMID and one database per call.
    findings = []
    for t in TARGETS:
        pmid = t["pmid"]
        entry = {
            "pmid": pmid,
            "why_this_paper": t["why_this_paper"],
            "what_a_deposit_would_settle": t["what_a_deposit_would_settle"],
            "paper_identified_at_runtime": pubmed_summary(pmid),
            "elink": {},
            "deposits_analysed": [],
        }
        time.sleep(0.35)
        for db in TARGET_DBS:
            r = elink_one(pmid, db)
            entry["elink"][db] = r
            time.sleep(0.35)

            # The curated citing records are IDENTIFIED but not sequence-analysed: they are
            # wild-type gene entries, and fetching 143 of them to rediscover that would be waste.
            # Naming them keeps the negative bounded — a reader can see exactly what WAS returned.
            if r.get("refseq_reference_uids"):
                rs_meta = esummary_db(db, r["refseq_reference_uids"])
                r["refseq_references_identified"] = [
                    {
                        "uid": u,
                        "accession": rs_meta.get(u, {}).get("accession"),
                        "title_verbatim": rs_meta.get(u, {}).get("title_verbatim"),
                    }
                    for u in r["refseq_reference_uids"]
                ]
                time.sleep(0.35)

            if r["verdict"] != "PRIMARY_DEPOSITS_PRESENT":
                continue

            uids = r["primary_deposit_uids"]
            meta = esummary_db(db, uids)
            r["esummary_of_primary_deposits"] = meta
            keep = [
                u
                for u in uids
                if meta.get(str(u)) and meta[str(u)]["slen"] <= MAX_RECORD_BP
            ]
            r["uids_kept_for_fetch"] = keep
            r["uids_dropped_on_size"] = [
                {"uid": u, "slen": meta[str(u)]["slen"], "title_verbatim": meta[str(u)]["title_verbatim"]}
                for u in uids
                if meta.get(str(u)) and meta[str(u)]["slen"] > MAX_RECORD_BP
            ]
            if not keep:
                continue
            rettype = "gbwithparts" if db == "nuccore" else "gp"
            flat, fetch_notes = efetch_flat(db, keep, rettype)
            r["efetch_calls"] = fetch_notes
            for acc, text in sorted(flat.items()):
                if db == "nuccore":
                    entry["deposits_analysed"].append(
                        {"db": db, **analyse_deposit(acc, text, genes, scanner)}
                    )
                else:
                    # A protein deposit carries no nucleotide junction, so nothing is derived from
                    # it; its DEFINITION and CDS coded_by are reported as the depositor's words.
                    entry["deposits_analysed"].append(
                        {
                            "db": db,
                            "accession": acc,
                            "⚠ note": (
                                "Protein record — no nucleotide sequence, so no junction is derived "
                                "here. Its coded_by points at the nucleotide record, which is where "
                                "a junction would be derived."
                            ),
                            "depositor_annotation": extract_depositor_annotation(text),
                            "flatfile_head_verbatim": "\n".join(text.splitlines()[:16]),
                        }
                    )

        # ---- the one-line answer for this paper, stated so it can be quoted directly
        lines = []
        for db in TARGET_DBS:
            r = entry["elink"][db]
            if r["verdict"] == "ERROR_NO_MEASUREMENT":
                lines.append(
                    f"elink pubmed->{db} for PMID {pmid} DID NOT PRODUCE A MEASUREMENT "
                    f"(http_status={r['http_status']})"
                )
            else:
                # ⛔ Both numbers, always. Stating only the total is what made the first run's
                # "returned 7 records" read as a deposit count when it was a citation count.
                lines.append(
                    f"elink pubmed->{db} for PMID {pmid} returned "
                    f"{r['n_primary_deposits']} records deposited with the paper "
                    f"(linkname {r['primary_deposit_linkname']}) and "
                    f"{r['n_refseq_references']} curated RefSeq records that merely cite it"
                )
        entry["answer_for_the_record"] = "; ".join(lines)
        entry["all_calls_measured"] = all(
            entry["elink"][db]["verdict"] != "ERROR_NO_MEASUREMENT" for db in TARGET_DBS
        )
        entry["deposited_any_sequence"] = any(
            entry["elink"][db].get("n_primary_deposits", 0) > 0 for db in TARGET_DBS
        )
        findings.append(entry)

    art = {
        "_title": "Per-PMID elink probe: did these two series deposit sequences?",
        "_generated_by": "research/modalities/panagopoulos_elink_probe.py",
        "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_cost": "$0 — NCBI E-utilities on a free GitHub Actions CPU runner; no GPU, no rental",
        "_why_this_exists": (
            "research/modalities/nr4a3-nuccore-sweep-inputs.json records elink only as batch totals "
            "(n_in: 100, n_linked: 741 and similar), so it cannot say whether any SPECIFIC PMID was "
            "answered. Every call here carries exactly one id and checks the id NCBI echoes back."
        ),
        "_what_this_is_not": [
            "Not a breakpoint distribution — a deposit is one tumour or one construct.",
            "Not a coverage, efficacy, safety, therapeutic-window or clinical-readiness claim.",
            "Not a patient count.",
            "Not a statement about what the paywalled full text says.",
        ],
        "_reading_order_enforced": (
            "For every deposit, the junction is derived from the record's own sequence BEFORE the "
            "depositor's annotation is extracted, and the two are reported in separate fields with "
            "an explicit agreement verdict."
        ),
        "control_gate": controls,
        "control_gate_passed": gate_ok,
        "⛔ gate_scope": (
            "A FAILED gate does not make a retrieved record wrong, but it does make any ZERO here "
            "unsupported — an unproven instrument cannot certify an absence."
        ),
        "findings": findings,
        "_wall_s": round(time.time() - t0, 1),
    }
    return art


# ------------------------------------------------------------------------------------- selftest


def selftest():
    """Offline. Asserts the grading logic and the derive-before-annotation ordering."""
    fails = []

    def chk(c, m):
        if not c:
            fails.append(m)

    genes = load_genes()
    sc = JunctionScanner(genes)

    # ---- the three verdicts must be distinguishable, and an error must never grade as a zero
    err = {"http_status": None, "body": "", "sha256_of_body": None, "n_attempts": 3}
    saved = globals()["_get"]
    try:
        globals()["_get"] = lambda url, timeout=60, tries=3: dict(err, url=url, error="boom")
        r = elink_one("12378528", "nuccore")
        chk(r["verdict"] == "ERROR_NO_MEASUREMENT", f"a dead endpoint graded {r['verdict']}")
        chk("n_linked" not in r, "an unobserved call must not report a link count at all")

        # a 200 whose linkset echoes a DIFFERENT id is not a measurement of the paper asked about
        globals()["_get"] = lambda url, timeout=60, tries=3: {
            "url": url, "http_status": 200, "sha256_of_body": "x", "n_attempts": 1,
            "body": json.dumps({"linksets": [{"dbfrom": "pubmed", "ids": ["99999"]}]}),
        }
        r = elink_one("12378528", "nuccore")
        chk(r["verdict"] == "ERROR_NO_MEASUREMENT",
            f"a linkset echoing the wrong id graded {r['verdict']} — it must not be a measurement")

        # a real, empty linkset for the right id IS a measured zero
        globals()["_get"] = lambda url, timeout=60, tries=3: {
            "url": url, "http_status": 200, "sha256_of_body": "x", "n_attempts": 1,
            "body": json.dumps({"linksets": [{"dbfrom": "pubmed", "ids": ["12378528"]}]}),
        }
        r = elink_one("12378528", "nuccore")
        chk(r["verdict"] == "MEASURED_ZERO", f"an empty linkset for the right id graded {r['verdict']}")
        chk(r["n_linked"] == 0 and r["echo_matches_requested_pmid"],
            "a measured zero must record both the count and the echo check")

        # a real deposit -> PRIMARY_DEPOSITS_PRESENT, and the uid list is carried
        globals()["_get"] = lambda url, timeout=60, tries=3: {
            "url": url, "http_status": 200, "sha256_of_body": "x", "n_attempts": 1,
            "body": json.dumps({"linksets": [{"dbfrom": "pubmed", "ids": ["11156374"],
                                              "linksetdbs": [{"linkname": "pubmed_nuccore",
                                                              "links": ["13540159"]}]}]}),
        }
        r = elink_one("11156374", "nuccore")
        chk(r["verdict"] == "PRIMARY_DEPOSITS_PRESENT" and r["primary_deposit_uids"] == ["13540159"],
            f"a real deposit graded {r['verdict']} / {r.get('primary_deposit_uids')}")
        chk(r["linknames_returned"] == ["pubmed_nuccore"], "link names must be recorded")

        # ⛔⛔ THE REGRESSION THIS PROBE'S FIRST RUN ACTUALLY SHIPPED. Seven `pubmed_nuccore_refseq`
        # links and nothing under `pubmed_nuccore` is NOT a deposit — it is a paper being cited by
        # the RefSeq entries of the genes it studied. Grading this as a hit is exactly how the
        # unreachable-coverage question would have been answered backwards.
        globals()["_get"] = lambda url, timeout=60, tries=3: {
            "url": url, "http_status": 200, "sha256_of_body": "x", "n_attempts": 1,
            "body": json.dumps({"linksets": [{"dbfrom": "pubmed", "ids": ["12378528"],
                                              "linksetdbs": [{"linkname": "pubmed_nuccore_refseq",
                                                              "links": ["27894356", "1519243370"]}]}]}),
        }
        r = elink_one("12378528", "nuccore")
        chk(r["verdict"] == "NO_PRIMARY_DEPOSIT_ONLY_REFSEQ_REFERENCES",
            f"⛔ refseq-only links graded {r['verdict']} — a citation is not a deposit")
        chk(r["n_primary_deposits"] == 0,
            f"refseq-only links reported {r['n_primary_deposits']} deposits — must be 0")
        chk(r["n_refseq_references"] == 2, "the citing records must still be counted and named")
        chk(r["n_linked"] == 2,
            "the merged total must remain available, but it is not the reported answer")

        # and the two link sets must never be summed into the deposit count
        globals()["_get"] = lambda url, timeout=60, tries=3: {
            "url": url, "http_status": 200, "sha256_of_body": "x", "n_attempts": 1,
            "body": json.dumps({"linksets": [{"dbfrom": "pubmed", "ids": ["11156374"],
                                              "linksetdbs": [
                                                  {"linkname": "pubmed_nuccore",
                                                   "links": ["13540159"]},
                                                  {"linkname": "pubmed_nuccore_refseq",
                                                   "links": ["27894356", "1519243370"]}]}]}),
        }
        r = elink_one("11156374", "nuccore")
        chk(r["n_primary_deposits"] == 1 and r["n_refseq_references"] == 2 and r["n_linked"] == 3,
            f"mixed link sets misattributed: primary={r['n_primary_deposits']} "
            f"refseq={r['n_refseq_references']} merged={r['n_linked']}")
        chk(r["primary_deposit_uids"] == ["13540159"],
            "the deposit uid must be recoverable from the primary link set alone")
    finally:
        globals()["_get"] = saved

    # ---- the request must carry exactly ONE id. This is the whole reason the module exists.
    url = elink_one.__doc__ and None
    globals()["_get"] = lambda u, timeout=60, tries=3: {
        "url": u, "http_status": 200, "sha256_of_body": "x", "n_attempts": 1,
        "body": json.dumps({"linksets": [{"ids": ["12378528"]}]}),
    }
    r = elink_one("12378528", "nuccore")
    globals()["_get"] = saved
    idpart = urllib.parse.parse_qs(urllib.parse.urlparse(r["request_url_verbatim"]).query).get("id", [""])[0]
    chk("," not in idpart, f"the request batched ids: id={idpart!r} — a batched call cannot answer per-PMID")
    chk(idpart == "12378528", f"the request asked for {idpart!r}, not the PMID requested")
    chk("dbfrom=pubmed" in r["request_url_verbatim"] and "db=nuccore" in r["request_url_verbatim"],
        "the request did not name dbfrom=pubmed and db=nuccore")

    # ---- the positive control's ground truth must be READ, not typed
    pc = load_positive_control()
    chk(pc["pmid"].isdigit() and pc["expected_nuccore_uid"].isdigit(),
        f"positive control not readable from the committed record: {pc}")

    # ---- derive-before-annotate, on a synthetic deposit whose ANNOTATION IS DELIBERATELY WRONG.
    # ⛔ This is the ordering assertion: the flatfile below says "exon 99" while the SEQUENCE is a
    # TCF12 exon 5 :: NR4A3 exon 3 seam. A module that read the annotation first would echo 99.
    tcf12 = exon_seq(genes["TCF12"], 5)[-150:]
    n3 = exon_seq(genes[ACCEPTOR], 3)[:150]
    seq = (tcf12 + n3).lower()
    body = "".join(
        f"{i + 1:>9} " + " ".join(seq[i : i + 60][j : j + 10] for j in range(0, 60, 10)) + "\n"
        for i in range(0, len(seq), 60)
    )
    flat = (
        f"LOCUS       TEST0001       {len(seq)} bp    mRNA    linear   PRI 15-AUG-2026\n"
        "DEFINITION  Homo sapiens TCF12-TEC fusion protein mRNA, partial cds.\n"
        "ACCESSION   TEST0001\n"
        "VERSION     TEST0001.1\n"
        "REFERENCE   1\n"
        "  PUBMED   12378528\n"
        "FEATURES             Location/Qualifiers\n"
        f"     source          1..{len(seq)}\n"
        '                     /organism="Homo sapiens"\n'
        '                     /tissue_type="extraskeletal myxoid chondrosarcoma"\n'
        "     misc_feature    1..150\n"
        '                     /note="contains exon 99 of TCF12"\n'
        "ORIGIN\n" + body + "//\n"
    )
    a = analyse_deposit("TEST0001", flat, genes, sc)
    chk(a["derived_exon_pair"] is not None, "no junction was derived from a synthetic fusion deposit")
    chk(a["derived_exon_pair"][0] == "TCF12" and a["derived_exon_pair"][1] == 5,
        f"⛔ ORDERING FAILURE: derived pair {a['derived_exon_pair']} — the sequence says TCF12 exon 5; "
        "the annotation's 'exon 99' must not influence it")
    chk("exon 99" in " ".join(a["depositor_annotation"]["notes_verbatim"]),
        "the depositor's annotation must still be REPORTED, just not used to derive")
    chk("DOES_NOT_STATE" in a["agreement_with_depositor"] or "99" not in a["agreement_with_depositor"],
        f"disagreement not surfaced: {a['agreement_with_depositor']}")
    chk(a["is_nr4a3_fusion_by_sequence"], "a real fusion deposit was not recognised as one")
    chk("12378528" in a["depositor_annotation"]["reference_pubmed_ids"],
        "the flatfile's PUBMED cross-reference must be captured")

    # a wild-type record must not be handed a junction
    plain = "".join(exon_seq(genes[ACCEPTOR], i) for i in range(1, 5)).upper()
    j2 = assign_junction(plain, genes, sc)
    chk(not j2["seam_match"], f"NEGATIVE CONTROL FAILED: wild-type cDNA assigned a junction: {j2['seam_match']}")

    # ---- the targets must be the two PMIDs this probe was built to answer, asked in both dbs
    chk([t["pmid"] for t in TARGETS] == ["12378528", "29937513"],
        f"target list drifted: {[t['pmid'] for t in TARGETS]}")
    chk(TARGET_DBS == ["nuccore", "protein"], f"target dbs drifted: {TARGET_DBS}")

    if fails:
        print("SELFTEST FAILED")
        for f in fails:
            print("  ⛔", f)
        return 1
    print("selftest OK — grading, single-id requests, and derive-before-annotate all asserted")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    rc = selftest()
    if rc:
        print("⛔ refusing to fetch: the offline selftest failed")
        return rc
    if not args.fetch:
        print("nothing to do; pass --fetch")
        return 0

    art = run_probe()
    with open(OUT, "w") as fh:
        json.dump(art, fh, indent=1)

    print("=" * 78)
    print(f"control gate passed : {art['control_gate_passed']}")
    pos = art["control_gate"]["positive"]
    print(f"  positive  PMID {pos['pmid']} -> expected uid {pos['expected_nuccore_uid']} "
          f"({pos['expected_accession']}): {pos['result']['verdict']}, "
          f"primary_deposit_uids={pos['result'].get('primary_deposit_uids')}, "
          f"linknames={pos['result'].get('linknames_returned')}")
    neg = art["control_gate"]["negative"]
    print(f"  negative  PMID {neg['pmid']}: {neg['result']['verdict']}, "
          f"n_linked={neg['result'].get('n_linked')}")
    print("=" * 78)
    for f in art["findings"]:
        p = f["paper_identified_at_runtime"]
        print(f"\nPMID {f['pmid']}")
        print(f"  paper (from esummary): {p.get('first_author_verbatim')} — "
              f"{(p.get('title_verbatim') or '')[:110]}")
        print(f"  journal: {p.get('journal_verbatim')} {p.get('pubdate_verbatim')}  doi={p.get('doi')}")
        for db in TARGET_DBS:
            r = f["elink"][db]
            print(f"  elink pubmed->{db}: verdict={r['verdict']} "
                  f"http={r['http_status']} echo_ok={r.get('echo_matches_requested_pmid')}")
            print(f"     DEPOSITED WITH THE PAPER ({r.get('primary_deposit_linkname')}): "
                  f"{r.get('n_primary_deposits')}   uids={r.get('primary_deposit_uids')}")
            print(f"     curated RefSeq records that merely cite it: {r.get('n_refseq_references')}")
        print(f"  ANSWER: {f['answer_for_the_record']}")
        for d in f["deposits_analysed"]:
            print(f"    - {d.get('accession')} [{d.get('db')}] "
                  f"derived_pair={d.get('derived_exon_pair')} "
                  f"agree={d.get('agreement_with_depositor')}")
    print(f"\nwrote {OUT}  ({art['_wall_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
