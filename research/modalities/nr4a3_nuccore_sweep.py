#!/usr/bin/env python3
"""Recover NR4A3 fusion breakpoints from DEPOSITED SEQUENCE RECORDS, not from published prose.

⭐ WHY THIS ROUTE, AND WHY IT COMES BEFORE RAW READS. The TCF12::NR4A3 breakpoint — the one
junction ~1,030 open-access papers could not produce — was never published as prose. The authors
DEPOSITED the chimeric cDNA (GenBank AF289510.1), whose two chromosome-tagged `source` features
split the record at the junction. The routes that reached it cost nothing: an `elink` from the
report's PubMed record to `nuccore`, and a `nuccore` term search. Raw reads are far more expensive
to work with, so the cheap sequence-database route is exhausted first.

⛔ THE ALIAS TRAP, AND IT IS THE WHOLE REASON THIS MODULE EXISTS RATHER THAN ONE `esearch`.
AF289510's DEFINITION line reads "TCF12-TEC fusion protein mRNA". It does not contain the string
"NR4A3". NR4A3 was called TEC, CHN, NOR1, NOR-1, MINOR and CSMF across the era in which fusion
cDNAs were actually deposited, and its partners carry their own retired names — TAF15 was TAF2N,
RBP56 and hTAFII68; TCF12 was HTF4 and HEB; EWSR1 was EWS. A sweep that searches only current
symbols searches only the years in which nobody deposited. Every alias below is used.

⚠ AND THE CORPUS CANNOT DRIVE THIS. The three literature sweeps are PMC open-access, which
effectively begins in the 2000s; the deposits cluster in the 1990s and early 2000s. So this module
runs its own PubMed search across ALL eras rather than starting from the corpus PMIDs — starting
from them would systematically miss exactly the records worth finding.

WHAT IT PRODUCES. For every deposited record retrieved, the junction is assigned by matching the
record's own nucleotide sequence against this repository's committed transcript models
(`aso-premrna-sequences.json`), reusing the seam matcher in `emc_fusion_read_scan`. So the exon
pair is DERIVED from the deposit, never read off a title, and the seam is quoted verbatim.

⛔ WHAT IT IS NOT. Not a breakpoint distribution — a deposit is one tumour or one construct, and
several are ENGINEERED constructs rather than patient material, which this module labels and never
conflates. Not a coverage, efficacy, safety, therapeutic-window or clinical-readiness claim. Not a
patient count.

$0 — NCBI E-utilities on a free CPU runner. Pure stdlib. The dev sandbox's egress proxy 403s NCBI
on CONNECT, which is why this runs on a runner (CLAUDE.md §6).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from emc_fusion_read_scan import (  # noqa: E402
    ACCEPTOR,
    JunctionScanner,
    exon_seq,
    intron_seq,
    load_genes,
    revcomp,
)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "Rare-cancers/nr4a3_nuccore_sweep (+https://github.com/trimcrae/Rare-cancers)"
OUT = os.path.join(HERE, "nr4a3-nuccore-sweep.json")
OUT_INPUTS = os.path.join(HERE, "nr4a3-nuccore-sweep-inputs.json")

# ⛔ THE ALIASES ARE THE INSTRUMENT. See the header: AF289510 says "TEC", not "NR4A3".
ACCEPTOR_ALIASES = ["NR4A3", "TEC", "CHN", "NOR1", "NOR-1", "MINOR", "CSMF"]
PARTNER_ALIASES = {
    "EWSR1": ["EWSR1", "EWS"],
    "TAF15": ["TAF15", "TAF2N", "RBP56", "hTAFII68", "TAFII68"],
    "TCF12": ["TCF12", "HTF4", "HEB"],
    "TFG": ["TFG"],
    "FUS": ["FUS", "TLS"],
    "HSPA8": ["HSPA8", "HSC70"],
}

# The positive control. Its ground truth is committed in
# research/literature/tcf12-nr4a3-breakpoint-primary-sources.json: bases 1..263 are chromosome 15
# (TCF12) and 264..421 are chromosome 9 (TEC/NR4A3). An instrument that cannot re-find this record
# is not entitled to report that anything else is absent.
POSITIVE_CONTROL_ACCESSION = "AF289510"
NEGATIVE_CONTROL_TERM = "ZZZQQQ_not_a_real_gene_fusion_xyzzy"


def _get(url, timeout=60, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return {"url": url, "http_status": r.status, "body": r.read().decode("utf-8", "replace")}
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    return {"url": url, "http_status": None, "body": "", "error": f"{type(last).__name__}: {last}"}


def esearch(db, term, retmax=200):
    url = (
        f"{EUTILS}/esearch.fcgi?db={db}&retmode=json&retmax={retmax}"
        f"&term={urllib.parse.quote(term)}"
    )
    rec = _get(url)
    ids, count = [], None
    try:
        j = json.loads(rec["body"])
        ids = j["esearchresult"].get("idlist", [])
        count = int(j["esearchresult"].get("count", 0))
    except Exception:  # noqa: BLE001
        pass
    return {"db": db, "term": term, "http_status": rec["http_status"], "count": count, "ids": ids}


def elink(from_db, to_db, ids):
    if not ids:
        return {"ids": [], "linked": []}
    url = (
        f"{EUTILS}/elink.fcgi?dbfrom={from_db}&db={to_db}&retmode=json"
        f"&id={','.join(str(i) for i in ids)}"
    )
    rec = _get(url)
    linked = []
    try:
        j = json.loads(rec["body"])
        for ls in j.get("linksets", []):
            for db in ls.get("linksetdbs", []):
                linked.extend(db.get("links", []))
    except Exception:  # noqa: BLE001
        pass
    return {"from": from_db, "to": to_db, "n_in": len(ids), "http_status": rec["http_status"],
            "linked": sorted(set(linked))}


def efetch_genbank(uids):
    """GenBank flatfile WITH the sequence — `gbwithparts`, the format AF289510 was read in."""
    if not uids:
        return {}
    out = {}
    for i in range(0, len(uids), 20):
        batch = uids[i : i + 20]
        url = (
            f"{EUTILS}/efetch.fcgi?db=nuccore&rettype=gbwithparts&retmode=text"
            f"&id={','.join(str(u) for u in batch)}"
        )
        rec = _get(url, timeout=120)
        body = rec["body"]
        for chunk in re.split(r"\n(?=LOCUS\s)", body):
            if not chunk.strip().startswith("LOCUS"):
                continue
            m = re.search(r"^ACCESSION\s+(\S+)", chunk, re.M)
            acc = m.group(1) if m else None
            if acc:
                out[acc] = chunk
        time.sleep(0.4)
    return out


# ------------------------------------------------------------------- GenBank flatfile parsing


def parse_flatfile(text):
    """Everything this module asserts about a record comes from here, and each field is quoted."""
    rec = {}
    m = re.search(r"^LOCUS\s+(\S+)\s+(\d+)\s+bp", text, re.M)
    if m:
        rec["locus"] = m.group(1)
        rec["length_bp"] = int(m.group(2))
    m = re.search(r"^DEFINITION\s+(.*?)(?=^\w|\Z)", text, re.M | re.S)
    if m:
        rec["definition"] = " ".join(m.group(1).split())
    m = re.search(r"^ACCESSION\s+(\S+)", text, re.M)
    if m:
        rec["accession"] = m.group(1)
    m = re.search(r"^VERSION\s+(\S+)", text, re.M)
    if m:
        rec["version"] = m.group(1)
    rec["pubmed_ids"] = sorted(set(re.findall(r"^\s+PUBMED\s+(\d+)", text, re.M)))
    m = re.search(r"^\s+/organism=\"([^\"]+)\"", text, re.M)
    if m:
        rec["organism"] = m.group(1)
    rec["tissue_types"] = sorted(set(re.findall(r'/tissue_type="([^"]+)"', text)))
    rec["cell_lines"] = sorted(set(re.findall(r'/cell_line="([^"]+)"', text)))
    rec["notes"] = [" ".join(n.split()) for n in re.findall(r'/note="([^"]+)"', text)][:8]
    rec["maps"] = sorted(set(re.findall(r'/map="([^"]+)"', text)))

    # ⭐ the AF289510 pattern: chromosome-tagged source features that split the record
    srcs = []
    for m in re.finditer(r"^\s{5}source\s+(\S+)\n((?:^\s{21}.*\n)*)", text, re.M):
        span, quals = m.group(1), m.group(2)
        chrom = re.search(r'/chromosome="([^"]+)"', quals)
        mp = re.search(r'/map="([^"]+)"', quals)
        srcs.append(
            {
                "span": span,
                "chromosome": chrom.group(1) if chrom else None,
                "map": mp.group(1) if mp else None,
            }
        )
    rec["source_features"] = srcs
    rec["chromosome_split"] = [s for s in srcs if s["chromosome"]]

    # sequence
    m = re.search(r"^ORIGIN.*?\n(.*?)^//", text, re.M | re.S)
    if m:
        rec["sequence"] = re.sub(r"[^acgtnACGTN]", "", m.group(1)).upper()
    return rec


# ------------------------------------------------------- assigning the junction from the deposit


def assign_junction(seq, genes, scanner):
    """Name the exon pair from the deposited sequence itself.

    Two independent readings, and they are reported separately on purpose:
      * `seam_match` — the exact partner-exon-end | NR4A3-acceptor-start seam, the same matcher
        the read scan uses. This is what NAMES the exon pair.
      * `longest_blocks` — the longest exact block of the deposit attributable to each gene's
        spliced transcript, which says how much of the record each gene accounts for and catches
        a record that is not a fusion at all.
    """
    out = {"seam_match": [], "longest_blocks": {}}
    if not seq:
        return out

    for s in (seq, revcomp(seq)):
        scanner.reset()
        scanner._scan_text(f"@d\n{s}\n+\n{'I' * len(s)}\n")
        for j in scanner.junctions.values():
            gene, exon = j["donor"].rsplit("_exon", 1)
            out["seam_match"].append(
                {
                    "partner_gene": gene,
                    "partner_exon": int(exon),
                    "acceptor_site": j["acceptor_site"],
                    "seam_verbatim": j["seam_verbatim"],
                    "strand": "+" if s is seq else "-",
                }
            )
        if out["seam_match"]:
            break

    # how much of the record does each gene explain?
    for gname, g in genes.items():
        spliced = "".join(
            exon_seq(g, i) for i in range(1, len(g["exon_spans_0based_inclusive"]) + 1)
        ).upper()
        best = 0
        for s in (seq, revcomp(seq)):
            for k in range(0, len(s) - 24, 12):
                probe = s[k : k + 24]
                if probe in spliced:
                    n = 24
                    while k + n < len(s) and s[k : k + n + 1] in spliced:
                        n += 1
                    best = max(best, n)
        if best >= 24:
            out["longest_blocks"][gname] = best
    return out


def classify_material(rec):
    """A patient tumour and an engineered construct are both informative and are NOT the same
    evidence. Conflating them would let a lab plasmid stand in for a patient's breakpoint."""
    text = " ".join(
        [rec.get("definition", "")] + rec.get("notes", []) + rec.get("cell_lines", [])
        + rec.get("tissue_types", [])
    ).lower()
    if re.search(r"vector|plasmid|construct|synthetic|expression cassette|clone[d]? into", text):
        return "ENGINEERED_CONSTRUCT"
    if rec.get("tissue_types") or re.search(r"tumou?r|chondrosarcoma|biopsy|patient", text):
        return "PATIENT_MATERIAL"
    if rec.get("cell_lines"):
        return "CELL_LINE"
    return "CANNOT_DETERMINE"


# ------------------------------------------------------------------------------------- queries


def build_queries():
    qs = []
    for a in ACCEPTOR_ALIASES:
        for pg, pal in PARTNER_ALIASES.items():
            for p in pal:
                qs.append((f'"{p}-{a}"[All Fields] OR "{p}::{a}"[All Fields] OR "{p}/{a}"[All Fields]',
                           f"{pg}x{a}"))
    extra = [
        ('"extraskeletal myxoid chondrosarcoma"[All Fields]', "disease-name"),
        ('"myxoid chondrosarcoma"[All Fields] AND fusion[All Fields]', "disease+fusion"),
        ('NR4A3[Gene Name] AND fusion[All Fields]', "gene-name+fusion"),
        ('"fusion protein mRNA"[All Fields] AND (TEC[All Fields] OR NR4A3[All Fields])', "fusion-mRNA"),
        ('"chimeric" [All Fields] AND (NR4A3[All Fields] OR TEC[All Fields] OR CHN[All Fields]) '
         'AND chondrosarcoma[All Fields]', "chimeric+disease"),
        ('t(9;22)[All Fields] AND chondrosarcoma[All Fields]', "t9;22"),
        ('t(9;17)[All Fields] AND chondrosarcoma[All Fields]', "t9;17"),
        ('t(9;15)[All Fields] AND chondrosarcoma[All Fields]', "t9;15"),
    ]
    qs.extend(extra)
    return qs


def sweep(budget_s=2400, retmax=200):
    t0 = time.time()
    genes = load_genes()
    scanner = JunctionScanner(genes)
    inputs = {"searches": [], "elinks": [], "controls": {}}

    # ---- control gate. An instrument that cannot re-find the known deposit, or that returns
    # something for a term that cannot exist, is not entitled to report an absence.
    pos = esearch("nuccore", f"{POSITIVE_CONTROL_ACCESSION}[Accession]")
    neg = esearch("nuccore", NEGATIVE_CONTROL_TERM)
    inputs["controls"] = {
        "positive": {**pos, "expect": "nonzero", "passed": bool(pos["ids"])},
        "negative": {**neg, "expect": "zero", "passed": neg["count"] == 0},
    }
    gate_ok = inputs["controls"]["positive"]["passed"] and inputs["controls"]["negative"]["passed"]

    uids = set()
    # ---- route 1: nuccore term searches
    for term, label in build_queries():
        if time.time() - t0 > budget_s:
            inputs["⚠ budget"] = "search budget exhausted; remaining queries not run"
            break
        r = esearch("nuccore", term, retmax=retmax)
        r["label"] = label
        inputs["searches"].append(r)
        uids.update(r["ids"])
        time.sleep(0.35)

    # ---- route 2: PubMed across ALL eras -> elink to nuccore
    pm_terms = [
        '"extraskeletal myxoid chondrosarcoma"[All Fields]',
        'NR4A3[All Fields] AND fusion[All Fields]',
        '(TEC[All Fields] OR CHN[All Fields] OR NOR1[All Fields]) AND chondrosarcoma[All Fields]',
        'EWS[All Fields] AND (NOR1[All Fields] OR TEC[All Fields] OR CHN[All Fields])',
        'TAF2N[All Fields] OR RBP56[All Fields] AND chondrosarcoma[All Fields]',
    ]
    pmids = set()
    for term in pm_terms:
        if time.time() - t0 > budget_s:
            break
        r = esearch("pubmed", term, retmax=retmax)
        r["label"] = "pubmed"
        inputs["searches"].append(r)
        pmids.update(r["ids"])
        time.sleep(0.35)
    pmids = sorted(pmids)
    for i in range(0, len(pmids), 100):
        if time.time() - t0 > budget_s:
            inputs["⚠ elink budget"] = "elink budget exhausted"
            break
        e = elink("pubmed", "nuccore", pmids[i : i + 100])
        inputs["elinks"].append({k: v for k, v in e.items() if k != "linked"} | {"n_linked": len(e["linked"])})
        uids.update(e["linked"])
        time.sleep(0.35)

    # ---- fetch and assign
    uids = sorted(uids)
    flat = efetch_genbank(uids)
    records = []
    for acc, text in sorted(flat.items()):
        rec = parse_flatfile(text)
        seq = rec.pop("sequence", "")
        rec["material"] = classify_material(rec)
        rec["junction"] = assign_junction(seq, genes, scanner)
        rec["sequence_len"] = len(seq)
        rec["is_nr4a3_fusion"] = bool(rec["junction"]["seam_match"]) or (
            ACCEPTOR in rec["junction"]["longest_blocks"]
            and len(rec["junction"]["longest_blocks"]) > 1
        )
        rec["flatfile_head"] = "\n".join(text.splitlines()[:14])
        records.append(rec)

    hits = [r for r in records if r["junction"]["seam_match"]]
    by_pair = {}
    for r in hits:
        for s in r["junction"]["seam_match"]:
            key = f'{s["partner_gene"]}_exon{s["partner_exon"]}__{s["acceptor_site"]}'
            by_pair.setdefault(key, []).append(r.get("version") or r.get("accession"))

    art = {
        "_title": "NR4A3 fusion junctions recovered from deposited sequence records",
        "_generated_by": "research/modalities/nr4a3_nuccore_sweep.py",
        "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_cost": "$0 — NCBI E-utilities on a free CPU runner; no GPU, no rental",
        "_what_this_is_not": [
            "Not a breakpoint distribution — a deposit is one tumour or one construct.",
            "Not a patient count; engineered constructs are labelled and never counted as tumours.",
            "Not an efficacy, potency, safety, therapeutic-window or clinical-readiness claim.",
        ],
        "_how_the_exon_pair_is_derived": (
            "By matching the deposit's OWN nucleotide sequence against this repository's committed "
            "transcript models, never by reading a title. The seam is quoted verbatim."
        ),
        "control_gate": inputs["controls"],
        "control_gate_passed": gate_ok,
        "⛔ gate_scope": (
            "A failed gate does not make the findings below wrong; it makes any ABSENCE claim "
            "unsupported. Records actually retrieved are still records."
        ),
        "n_queries": len(inputs["searches"]),
        "n_uids_retrieved": len(uids),
        "n_records_parsed": len(records),
        "n_records_with_an_assigned_junction": len(hits),
        "junctions_by_exon_pair": by_pair,
        "records_with_a_junction": hits,
        "all_records": records,
        "_wall_s": round(time.time() - t0, 1),
    }
    return art, inputs


def selftest():
    """Offline. The parser and the assigner are asserted against the KNOWN control record."""
    fails = []
    genes = load_genes()
    sc = JunctionScanner(genes)

    # A synthetic flatfile in the exact shape of AF289510, including the chromosome-tagged split.
    tcf12 = exon_seq(genes["TCF12"], 5)[-120:]
    n3 = exon_seq(genes[ACCEPTOR], 3)[:120]
    seq = (tcf12 + n3).lower()
    body = "".join(
        f"{i + 1:>9} " + " ".join(seq[i : i + 60][j : j + 10] for j in range(0, 60, 10)) + "\n"
        for i in range(0, len(seq), 60)
    )
    flat = (
        f"LOCUS       AF289510       {len(seq)} bp    mRNA    linear   PRI 15-JUL-2016\n"
        "DEFINITION  Homo sapiens TCF12-TEC fusion protein mRNA, partial cds.\n"
        "ACCESSION   AF289510\n"
        "VERSION     AF289510.1\n"
        "REFERENCE   1\n"
        "  PUBMED   11156374\n"
        "FEATURES             Location/Qualifiers\n"
        f"     source          1..{len(seq)}\n"
        '                     /organism="Homo sapiens"\n'
        '                     /tissue_type="extraskeletal myxoid chondrosarcoma"\n'
        f"     source          1..{len(tcf12)}\n"
        '                     /chromosome="15"\n'
        '                     /map="15q21"\n'
        f"     source          {len(tcf12) + 1}..{len(seq)}\n"
        '                     /chromosome="9"\n'
        '                     /map="9q22"\n'
        "ORIGIN\n" + body + "//\n"
    )
    rec = parse_flatfile(flat)

    def chk(c, m):
        if not c:
            fails.append(m)

    chk(rec.get("accession") == "AF289510", f"accession misparsed: {rec.get('accession')}")
    chk(rec.get("version") == "AF289510.1", f"version misparsed: {rec.get('version')}")
    chk("11156374" in rec.get("pubmed_ids", []), "PUBMED cross-reference not parsed")
    chk(len(rec.get("chromosome_split", [])) == 2, f"chromosome split not parsed: {rec.get('chromosome_split')}")
    chk(
        rec.get("tissue_types") == ["extraskeletal myxoid chondrosarcoma"],
        f"tissue_type not parsed: {rec.get('tissue_types')}",
    )
    chk(rec.get("length_bp") == len(seq), f"length misparsed: {rec.get('length_bp')}")
    chk(len(rec.get("sequence", "")) == len(seq), "ORIGIN sequence misparsed")
    chk(classify_material(rec) == "PATIENT_MATERIAL", f"material: {classify_material(rec)}")

    j = assign_junction(rec.get("sequence", ""), genes, sc)
    got = {(s["partner_gene"], s["partner_exon"], s["acceptor_site"]) for s in j["seam_match"]}
    chk(
        ("TCF12", 5, "NR4A3_exon3_start") in got,
        f"POSITIVE CONTROL FAILED: junction not assigned from the deposit ({got or 'nothing'})",
    )
    chk(ACCEPTOR in j["longest_blocks"] and "TCF12" in j["longest_blocks"],
        f"longest_blocks did not attribute both genes: {j['longest_blocks']}")

    # a NON-fusion record must not be assigned a junction
    plain = "".join(exon_seq(genes[ACCEPTOR], i) for i in range(1, 5)).upper()
    j2 = assign_junction(plain, genes, sc)
    chk(not j2["seam_match"], f"NEGATIVE CONTROL FAILED: wild-type NR4A3 cDNA assigned a junction: {j2['seam_match']}")

    # the alias table must actually carry the names the deposits use
    chk("TEC" in ACCEPTOR_ALIASES and "CHN" in ACCEPTOR_ALIASES and "NOR1" in ACCEPTOR_ALIASES,
        "acceptor alias table lost a name the deposits actually use")
    chk("TAF2N" in PARTNER_ALIASES["TAF15"] and "RBP56" in PARTNER_ALIASES["TAF15"],
        "TAF15 alias table lost a retired name")
    qs = build_queries()
    chk(any("TEC" in q for q, _ in qs), "no query uses the TEC alias — AF289510 would be missed")
    chk(len(qs) > 25, f"only {len(qs)} queries built")

    if fails:
        print("SELFTEST FAILED")
        for f in fails:
            print("  ⛔", f)
        return 1
    print(f"selftest OK — {len(qs)} queries, alias-aware, control record parsed and assigned")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--budget-s", type=int, default=2400)
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

    art, inputs = sweep(budget_s=args.budget_s)
    with open(OUT, "w") as fh:
        json.dump(art, fh, indent=1)
    with open(OUT_INPUTS, "w") as fh:
        json.dump({"_generated_utc": art["_generated_utc"], **inputs}, fh, indent=1)

    print(f"control gate passed : {art['control_gate_passed']}")
    print(f"queries run         : {art['n_queries']}")
    print(f"UIDs retrieved      : {art['n_uids_retrieved']}")
    print(f"records parsed      : {art['n_records_parsed']}")
    print(f"junctions assigned  : {art['n_records_with_an_assigned_junction']}")
    print("\nexon pairs recovered:")
    for k, v in sorted(art["junctions_by_exon_pair"].items()):
        print(f"  {k}: {v}")
    print(f"\nwrote {OUT} and {OUT_INPUTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
