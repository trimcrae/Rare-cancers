#!/usr/bin/env python3
"""CLOSED-ROUTES-2 — reconcile the standing closed-routes negative record against the
route closures this campaign evidenced.

READ-ONLY on everything outside this lane. NO network. This script CATALOGUES closures;
it does not test, probe, retry or reopen any of them. Every route below is established by
retained lane evidence, never by a fresh request.
"""
import hashlib, json, os, re, subprocess, sys, datetime

REPO = "/home/user/Rare-cancers"
LANEROOT = ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
            "PORTFOLIO-INVESTIGATIONS-2026-09-08")
RECORD = "research/manuscripts/methods-record/closed-routes-negative-record.md"
OUT = os.path.join(REPO, LANEROOT, "CLOSED-ROUTES-2", "closed-route-coverage.json")


def _bounded(tok):
    """Literal token match with alphanumeric boundaries, so a short route code such as
    "B1" cannot be matched inside a sha256 hex digest (the first version of this scan
    reported CR-NO-LOCAL-TRANSCRIPTOME as in-record on exactly that false positive;
    the failed run is preserved in checks/02-build-coverage/)."""
    pat = re.escape(tok)
    if tok[:1].isalnum():
        pat = r"(?<![0-9A-Za-z])" + pat
    if tok[-1:].isalnum():
        pat = pat + r"(?![0-9A-Za-z])"
    return pat


def sha256(rel):
    p = os.path.join(REPO, rel)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


# Each route: id, one-line closure statement, the class of closure, the lane that
# evidenced it, and its OWN evidence paths (repo-relative). A row with no lane evidence
# path may NOT be emitted -- enforced below.
ROUTES = [
    dict(
        route_id="CR-GPL3290-ACCESSION-BRIDGE",
        statement=("The GPL3290 EST-accession->symbol bridge is not in this checkout: it is "
                   "constructed at run time by fetching GEO acc.cgi / GPL3290.annot.gz / "
                   "GPL3290_family.soft.gz, so the platform's readability can only be bounded "
                   "offline, never made exact."),
        closure_class="artifact-absent-built-at-run-time-from-a-network-source",
        lane="FUSION-OUTPUT-3",
        evidence_paths=[
            f"{LANEROOT}/FUSION-OUTPUT-3/FINDING.md",
            f"{LANEROOT}/FUSION-OUTPUT-3/checks/04-platform-coverage-final/",
            f"{LANEROOT}/FUSION-OUTPUT-3/platform-coverage.json",
        ],
        record_tokens=["GPL3290", "acc.cgi", "accession bridge"],
    ),
    dict(
        route_id="CR-HPA-RNATSS-EMPTY",
        statement=("HPA's per-tissue nTPM column is already requested by the producer's query "
                   "string (rnatss) and comes back empty, so rna_tissue_specific_nTPM is null "
                   "and vital_tissue is [] on all 45 scored rows: the 21-tissue vital screen has "
                   "never had an input on any row."),
        closure_class="upstream-source-returns-no-data-for-a-requested-field",
        lane="SURFACE-2",
        evidence_paths=[
            f"{LANEROOT}/SURFACE-2/FINDING.md",
            f"{LANEROOT}/SURFACE-2/checks/01-audit/",
            f"{LANEROOT}/SURFACE-2/WINDOW-CONSISTENCY-AUDIT.tsv",
        ],
        record_tokens=["rnatss", "Human Protein Atlas", "vital_tissue", "vital-tissue"],
    ),
    dict(
        route_id="CR-CLINICALTRIALS-GOV-EGRESS",
        statement=("Direct HTTPS to clinicaltrials.gov is refused at this sandbox's egress "
                   "proxy: CONNECT tunnel failed, response 403, curl exit 56. The refusal is "
                   "the standing record; it was not retried, reworded, model-switched or "
                   "proxied around by any later lane."),
        closure_class="egress-refusal-at-the-proxy",
        lane="STRATEGY-ARCH-2",
        evidence_paths=[
            f"{LANEROOT}/PUB-STRATEGY-ARCH/checks/01-connectivity-probe/exit_code.txt",
            f"{LANEROOT}/PUB-STRATEGY-ARCH/checks/01-connectivity-probe/stderr.txt",
            f"{LANEROOT}/STRATEGY-ARCH-2/FINDING.md",
            f"{LANEROOT}/CARE-DELIVERY-3/FINDING.md",
        ],
        record_tokens=["clinicaltrials.gov", "curl exit 56", "CONNECT", "egress"],
    ),
    dict(
        route_id="CR-NO-LOCAL-TRANSCRIPTOME",
        statement=("emc_fourth_cohort_quant.py::map_probes_to_genes obtains its reference only "
                   "by urlopen against ftp.ensembl.org cdna/ncrna; there is no local cache and "
                   "no local transcriptome anywhere in the checkout, so the reference half of a "
                   "k >= 6 re-run is route B1/B2 and stays closed. It was not attempted."),
        closure_class="local-input-absent-remote-route-already-closed",
        lane="MATRIX-ADDRESS-3",
        evidence_paths=[
            f"{LANEROOT}/MATRIX-ADDRESS-3/FINDING.md",
            f"{LANEROOT}/MATRIX-ADDRESS-3/checks/03-committed-label-source-inventory/",
            f"{LANEROOT}/MATRIX-ADDRESS-3/relaxed-k-label-recovery.json",
        ],
        record_tokens=["ftp.ensembl.org", "transcriptome", "route B1", "B1/B2"],
    ),
    dict(
        route_id="CR-FOUR-REFERENCES-NO-PMC",
        statement=("Four PUB-REPURPOSING references -- [2], [8], [9], [14] -- have no PubMed "
                   "Central record at all, agreed by two independent retrieval modes (the id "
                   "converter and the PubMed-to-PMC link database). Not a lossy extraction: no "
                   "retrievable body of any kind. All four are read at abstract level only."),
        closure_class="no-open-record-exists-for-the-source",
        lane="REPURPOSING-3",
        evidence_paths=[
            f"{LANEROOT}/REPURPOSING-3/FINDING.md",
            f"{LANEROOT}/REPURPOSING-3/checks/01-convert-five-pmids-to-pmcid/",
            f"{LANEROOT}/REPURPOSING-3/checks/04-related-pubmed-pmc-all-five/",
            f"{LANEROOT}/REPURPOSING-3/FIVE-REFERENCE-TABLE.md",
        ],
        record_tokens=["no PubMed Central record", "PMC record", "REPURPOSING"],
    ),
    dict(
        route_id="CR-PMC10054153-EMPTY-BODY",
        statement=("The zaltoprofen reference [12] has a PMC record, PMC10054153, that returns "
                   "an empty full_text string reproducibly under both accepted id forms. "
                   "Abstract only; the body is not retrievable by any route this session may "
                   "take."),
        closure_class="record-exists-but-returns-an-empty-body",
        lane="REPURPOSING-3",
        evidence_paths=[
            f"{LANEROOT}/REPURPOSING-3/FINDING.md",
            f"{LANEROOT}/REPURPOSING-3/checks/02-fulltext-ref12-PMC10054153/",
            f"{LANEROOT}/REPURPOSING-3/checks/03-fulltext-ref12-retry-numeric-id/",
        ],
        record_tokens=["PMC10054153", "zaltoprofen", "empty full_text"],
    ),
    dict(
        route_id="CR-MORIOKA-TABLES-DROPPED",
        statement=("morioka2016trabectedin (PMC4946242) returns abstract and narrative only: "
                   "all tables, all figures and all legends are stripped, and the in-text "
                   "pointers arrive as bare punctuation. The lane therefore asserts NO absence "
                   "for that series on any element -- UNKNOWN, not zero."),
        closure_class="retrieval-returns-a-partial-body-tables-dropped",
        lane="CARE-DELIVERY-3",
        evidence_paths=[
            f"{LANEROOT}/CARE-DELIVERY-3/FINDING.md",
            f"{LANEROOT}/CARE-DELIVERY-3/checks/03-pmc-fulltext-morioka2016trabectedin/",
            f"{LANEROOT}/CARE-DELIVERY-3/care-delivery-element-coverage-v3.json",
        ],
        record_tokens=["morioka", "PMC4946242", "trabectedin"],
    ),
    dict(
        route_id="CR-HLA-C-NO-FREQUENCY-B8",
        statement=("The committed AFND mirror snapshot carries loci A and B only, and route B8 "
                   "(HLA-C) is closed and was not approached. C*04:01 and C*12:03 therefore have "
                   "no frequency in this checkout, and the population share for whom an "
                   "HLA-C-restricted junction epitope is the relevant one cannot be computed "
                   "here -- reported UNKNOWN, never substituted."),
        closure_class="closed-route-leaves-a-quantity-permanently-uncomputable-here",
        lane="HLA-COVERAGE-2",
        evidence_paths=[
            f"{LANEROOT}/HLA-COVERAGE-2/FINDING.md",
            f"{LANEROOT}/HLA-COVERAGE-2/checks/01-panel-coverage/",
            f"{LANEROOT}/HLA-COVERAGE-2/panel-coverage.json",
        ],
        record_tokens=["HLA-C", "route B8", "AFND"],
    ),
    dict(
        route_id="CR-Q92570-3-SEQUENCE-ABSENT",
        statement=("The NR4A3 isoform-3 sequence Q92570-3 is not in this checkout, so the offset "
                   "of DMPCVQAQY within it is carried from a committed artifact and could not be "
                   "independently re-verified. TrEMBL sits outside both novelty strata, so "
                   "'novel' never means absent from every human protein."),
        closure_class="reference-sequence-absent-verification-bounded",
        lane="NEOANTIGEN-4",
        evidence_paths=[
            f"{LANEROOT}/NEOANTIGEN-4/FINDING.md",
            f"{LANEROOT}/NEOANTIGEN-4/checks/01-novelty-audit/",
            f"{LANEROOT}/NEOANTIGEN-4/neoantigen4-novelty-audit.json",
        ],
        record_tokens=["Q92570-3", "TrEMBL", "Swiss-Prot"],
    ),
]


def main():
    missing = [r["route_id"] for r in ROUTES if not r.get("evidence_paths")]
    if missing:
        print("REFUSED - row(s) with no lane evidence path: %s" % missing, file=sys.stderr)
        return 3

    # Every declared evidence path must exist, re-checked at the moment of use.
    bad = []
    for r in ROUTES:
        for p in r["evidence_paths"]:
            if not os.path.exists(os.path.join(REPO, p)):
                bad.append((r["route_id"], p))
    if bad:
        print("REFUSED - evidence path does not exist: %s" % bad, file=sys.stderr)
        return 4

    record_text = open(os.path.join(REPO, RECORD), encoding="utf-8").read()
    record_sha = sha256(RECORD)

    rows = []
    for r in ROUTES:
        hits = {t: bool(re.search(_bounded(t), record_text, re.IGNORECASE))
                for t in r["record_tokens"]}
        in_record = any(hits.values())
        rows.append(dict(
            route_id=r["route_id"],
            closure_statement=r["statement"],
            closure_class=r["closure_class"],
            evidenced_by_lane=r["lane"],
            evidence_locator=r["evidence_paths"],
            record_scan_tokens=hits,
            in_record="yes" if in_record else "no",
        ))

    doc = dict(
        id="ART-CLOSED-ROUTES-2-COVERAGE",
        lane="CLOSED-ROUTES-2",
        campaign="OPUS-CAPACITY-CAMPAIGN-20260908",
        generated_utc=datetime.datetime.now(datetime.timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
        question=("Which of this campaign's newly evidenced route closures does the standing "
                  "negative record already carry, and which are uncatalogued?"),
        standing_record=dict(path=RECORD, sha256_at_use=record_sha),
        method=("Case-insensitive literal scan of the standing record for each route's own "
                "identifying tokens. A route counts as in-record only if at least one of its "
                "tokens appears in the record text. NO network request of any kind was made; "
                "every closure below is established by retained lane evidence."),
        scope_note=("The standing record's declared scope is the seven THERAPEUTIC routes filed "
                    "against PUB-CLOSED-ROUTES. Every row here is a RETRIEVAL or DATA-ACCESS "
                    "closure, a different class. Cataloguing a closure does not reopen it and "
                    "is not a plan to retry it."),
        n_routes=len(rows),
        n_in_record=sum(1 for x in rows if x["in_record"] == "yes"),
        n_uncatalogued=sum(1 for x in rows if x["in_record"] == "no"),
        routes=rows,
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote %s" % OUT)
    print("routes=%d in_record=%d uncatalogued=%d"
          % (doc["n_routes"], doc["n_in_record"], doc["n_uncatalogued"]))
    for x in rows:
        print("  %-34s in_record=%-3s lane=%s" % (x["route_id"], x["in_record"], x["evidenced_by_lane"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
