#!/usr/bin/env python3
"""
Transcriptome-wide off-target screen for the fusion-junction gapmer ASOs.

WHY: junction_aso.py only checks that a gapmer's target window is not a *perfect*
substring of the two parent CDSs. A real specificity claim needs a transcriptome-wide
near-match search: could the antisense oligo hybridise (with a few mismatches) to some
OTHER human transcript and trigger RNase-H cleavage there? This script answers that for
the committed fusion-specific designs.

HOW: for each top fusion-specific gapmer, take its 16-mer target_mRNA (sense) window and
BLAST it (blastn-short, low-complexity filter OFF — these SYGQ-derived windows are
GC/repeat-biased) against human RefSeq RNA via the NCBI BLAST URL API. We then flag, per
oligo, any near-complementary off-target transcript that is NOT EWSR1 or NR4A3, and — the
RNase-H-relevant part — whether the match covers the central DNA-gap region (positions
WING..LEN-WING), since RNase-H cleavage needs the DNA:RNA duplex contiguous across the gap;
a match confined to a wing is a weaker (affinity-only) liability than a gap-spanning match.

INTERNET REQUIRED (NCBI). The dev sandbox blocks outbound HTTPS, so this is meant to run on
a GitHub-hosted runner (.github/workflows/aso-offtarget.yml), which publishes the result JSON
to the `modalities-cache` branch — the same pattern as depmap_sarcoma_dependency.py.

Graceful degradation: if a BLAST query fails/times out, that oligo is recorded with
status="screen_failed" rather than crashing the run, so partial results still publish.

Output: junction-aso-offtarget.json
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import junction_aso as ja   # reuse the committed design logic (no duplication)

OUT = os.path.join(os.path.dirname(__file__), "junction-aso-offtarget.json")

BLAST = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
PARENT_ACCS = {"NM_005243", "NM_006981"}          # EWSR1, NR4A3 (the intended on-/parent hits)
PARENT_GENES = ("EWSR1", "EWS RNA", "NR4A3", "NOR-1", "nuclear receptor subfamily 4 group A member 3")
N_OLIGOS = 6                                       # screen the top N fusion-specific designs
NEAR_MATCH_MIN_IDENT = 14                          # >=14/16 identical bases counts as a near match
POLL_MAX_S = 600                                   # cap per-query polling at 10 min


def _http(url, data=None, timeout=120):
    req = urllib.request.urlopen(url if data is None else urllib.request.Request(url, data=data),
                                 timeout=timeout)
    return req.read().decode("utf-8", "replace")


def blast_put(seq):
    """Submit a short blastn search restricted to human RefSeq RNA; return the RID."""
    params = {
        "CMD": "Put", "PROGRAM": "blastn", "DATABASE": "refseq_rna",
        "QUERY": seq, "WORD_SIZE": "7", "EXPECT": "1000", "HITLIST_SIZE": "50",
        "FILTER": "F", "MEGABLAST": "off", "ENTREZ_QUERY": "txid9606[ORGN]",
    }
    html = _http(BLAST, data=urllib.parse.urlencode(params).encode())
    m = re.search(r"^\s*RID = (\S+)", html, re.M)
    if not m:
        raise RuntimeError("no RID returned from BLAST Put")
    return m.group(1)


def blast_poll(rid):
    """Poll until the search is READY; raise on FAILED/UNKNOWN or timeout."""
    waited = 0
    while waited < POLL_MAX_S:
        html = _http(BLAST + "?" + urllib.parse.urlencode(
            {"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo"}))
        m = re.search(r"Status=(\w+)", html)
        status = m.group(1) if m else "UNKNOWN"
        if status == "READY":
            return
        if status in ("FAILED", "UNKNOWN"):
            raise RuntimeError(f"BLAST status {status} for RID {rid}")
        time.sleep(20)
        waited += 20
    raise RuntimeError(f"BLAST poll timeout for RID {rid}")


def blast_hits(rid):
    """Fetch XML results and return parsed HSPs."""
    xml = _http(BLAST + "?" + urllib.parse.urlencode(
        {"CMD": "Get", "RID": rid, "FORMAT_TYPE": "XML"}), timeout=180)
    root = ET.fromstring(xml)
    hits = []
    for hit in root.iter("Hit"):
        hid = (hit.findtext("Hit_accession") or "")
        hdef = (hit.findtext("Hit_def") or "")
        for hsp in hit.iter("Hsp"):
            ident = int(hsp.findtext("Hsp_identity") or 0)
            alen = int(hsp.findtext("Hsp_align-len") or 0)
            qfrom = int(hsp.findtext("Hsp_query-from") or 0)
            qto = int(hsp.findtext("Hsp_query-to") or 0)
            hits.append({"acc": hid, "defn": hdef, "identity": ident, "align_len": alen,
                         "q_from": qfrom, "q_to": qto})
    return hits


def is_parent(h):
    acc = h["acc"].split(".")[0]
    if acc in PARENT_ACCS:
        return True
    d = h["defn"].upper()
    return any(g.upper() in d for g in PARENT_GENES)


def classify(h):
    """RNase-H relevance: does the matched query span the central DNA gap [WING, LEN-WING]?"""
    gap_lo, gap_hi = ja.WING + 1, ja.OLIGO_LEN - ja.WING       # 1-based inclusive gap span
    spans_gap = h["q_from"] <= gap_lo and h["q_to"] >= gap_hi
    return "gap_spanning_cleavage_risk" if spans_gap else "wing_only_affinity_risk"


def screen_one(design):
    target = design["target_mRNA_5to3"]
    rec = {"antisense_5to3": design["antisense_5to3"], "target_mRNA_5to3": target,
           "gc_percent": design["gc_percent"], "specificity_margin": design["specificity_margin"]}
    try:
        rid = blast_put(target)
        blast_poll(rid)
        hits = blast_hits(rid)
        offt = [h for h in hits
                if h["identity"] >= NEAR_MATCH_MIN_IDENT and not is_parent(h)]
        # dedup by accession, keep the strongest HSP
        best = {}
        for h in offt:
            k = h["acc"]
            if k not in best or h["identity"] > best[k]["identity"]:
                h["risk"] = classify(h)
                best[k] = h
        ranked = sorted(best.values(), key=lambda h: (-h["identity"], h["acc"]))
        rec.update({
            "status": "screened",
            "blast_rid": rid,
            "n_parent_or_intended_hits": sum(1 for h in hits if is_parent(h)),
            "n_offtarget_near_matches": len(ranked),
            "n_gap_spanning_offtargets": sum(1 for h in ranked
                                             if h["risk"] == "gap_spanning_cleavage_risk"),
            "offtargets": ranked[:15],
        })
    except Exception as e:  # noqa: BLE001 — never crash the whole screen on one query
        rec.update({"status": "screen_failed", "error": str(e)})
    return rec


def main():
    ews = ja.fetch_cds(ja.EWSR1_MRNA)
    nr4 = ja.fetch_cds(ja.NR4A3_MRNA)
    ja.EWSR1_full, ja.NR4A3_full = ews, nr4
    left, right, fusion = ja.build_fusion_cds(ews, nr4)
    designs = [o for o in ja.design(left, right, fusion) if o["fusion_specific"]][:N_OLIGOS]

    screened = []
    for i, d in enumerate(designs):
        print(f"  screening oligo {i+1}/{len(designs)}: {d['target_mRNA_5to3']}", file=sys.stderr)
        screened.append(screen_one(d))
        time.sleep(3)   # be polite to NCBI between submissions

    n_ok = sum(1 for r in screened if r["status"] == "screened")
    n_clean = sum(1 for r in screened
                  if r.get("status") == "screened" and r.get("n_gap_spanning_offtargets", 1) == 0)
    result = {
        "_note": ("Transcriptome-wide off-target screen of the fusion-junction gapmer ASOs "
                  "(blastn-short vs human RefSeq RNA, NCBI BLAST URL API). A clean oligo has "
                  "zero gap-spanning off-target near-matches (the RNase-H-cleavable liability). "
                  "Wing-only matches are weaker (affinity) liabilities. Predicted specificity, "
                  "not validated; confirm by the parental-/off-target-sparing wet-lab controls."),
        "method": {
            "db": "refseq_rna (txid9606[ORGN])", "program": "blastn (short, FILTER off)",
            "near_match_threshold": f">= {NEAR_MATCH_MIN_IDENT}/{ja.OLIGO_LEN} identical",
            "gap_region_1based": [ja.WING + 1, ja.OLIGO_LEN - ja.WING],
            "breakpoint_model": "assumed canonical breakpoint (same as junction_aso.py)",
        },
        "n_oligos_screened": len(screened),
        "n_screened_ok": n_ok,
        "n_oligos_no_gap_spanning_offtarget": n_clean,
        "oligos": screened,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "oligos"}, indent=2))


if __name__ == "__main__":
    main()
