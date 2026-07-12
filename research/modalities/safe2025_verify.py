#!/usr/bin/env python3
"""
Primary-source verification for the "Safe 2025 NR4A3-selective analogues" citation, so the anchor-warhead
decision (Zaienne-2022 cmpd 19 vs the Safe-reported NR4A3-selective indole-3-carbinol series) is made on
verified data, not a second-hand review claim.

Safe 2025 is a *review* — Safe S, et al. "Orphan nuclear receptor transcription factors as drug targets,"
Transcription 16:224-260 (2025); PMID 40646688; PMC12263127; doi 10.1080/21541264.2025.2521766. It CITES
NR4A3-selective carboxymethyl-indole-3-carbinol analogues (IC50 ~8-47 uM, de-repressing MYC) but is a
SECONDARY source for them. This script pulls the review's full text (Europe PMC), extracts the passages that
describe those compounds, and harvests the reference-list entries near those passages so we can identify +
later fetch the PRIMARY med-chem paper.

Pure stdlib (urllib only) so it runs on a GitHub Actions CPU runner (the dev sandbox egress-proxy 403s PMC).
Writes safe2025-verify.json. Never fabricates: records exactly what the fetched text says, with the source URL
and an HTTP/parse status, and flags anything it could not retrieve.
"""
import json
import re
import sys
import urllib.request
import urllib.error

PMCID = "PMC12263127"
PMID = "40646688"
DOI = "10.1080/21541264.2025.2521766"
UA = "rare-cancers-research/1.0 (NR4A3 anchor verification; mailto:trimcrae@gmail.com)"

# Keywords that mark the passages we care about (the NR4A3-selective indole series + its selectivity claim).
KW = [
    "carboxymethyl", "indole-3-carbinol", "CDIM", "C-DIM", "diindolyl",
    "NOR-1", "NOR1", "NR4A3", "MYC", "selective", "IC50", "IC₅₀",
]


def _get(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace"), r.status


def fetch_fulltext_xml():
    """Europe PMC full-text XML for the review (open-access; PMC12263127)."""
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML"
    try:
        body, status = _get(url, accept="application/xml")
        return {"url": url, "http_status": status, "ok": status == 200, "body": body}
    except urllib.error.HTTPError as e:
        return {"url": url, "http_status": e.code, "ok": False, "body": ""}
    except Exception as e:  # noqa: BLE001
        return {"url": url, "http_status": None, "ok": False, "error": str(e), "body": ""}


def strip_tags(xml):
    xml = re.sub(r"<xref[^>]*>.*?</xref>", " ", xml, flags=re.S)
    xml = re.sub(r"<[^>]+>", " ", xml)
    xml = re.sub(r"\s+", " ", xml)
    return xml


def sentences_with_keywords(text):
    hits = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        low = sent.lower()
        matched = [k for k in KW if k.lower() in low]
        # require a compound/selectivity keyword co-occurring with an NR4A3 keyword to reduce noise
        has_cpd = any(k.lower() in low for k in ["carboxymethyl", "indole-3-carbinol", "cdim", "c-dim", "diindolyl"])
        has_tgt = any(k.lower() in low for k in ["nor-1", "nor1", "nr4a3", "myc"])
        if has_cpd and (has_tgt or "selective" in low or "ic50" in low or "ic₅₀" in low):
            hits.append({"text": sent.strip()[:800], "keywords": sorted(set(matched))})
    return hits[:40]


def reference_entries(xml):
    """Harvest <ref>...</ref> blocks so we can find the PRIMARY citation for the indole-3-carbinol series."""
    refs = []
    for m in re.finditer(r"<ref\b[^>]*>(.*?)</ref>", xml, flags=re.S):
        block = m.group(1)
        # pull a DOI/PMID if present
        doi = re.search(r"10\.\d{4,9}/[^\s\"<]+", block)
        txt = strip_tags(block)
        low = txt.lower()
        if any(k in low for k in ["indol", "nr4a3", "nor-1", "nor1", "cdim", "c-dim", "carbinol", "myc"]):
            refs.append({"text": txt.strip()[:500], "doi": doi.group(0) if doi else None})
    return refs[:30]


def main():
    out = {
        "purpose": "Verify the Safe-2025 NR4A3-selective indole-3-carbinol compounds at/near primary source "
                   "for the anchor-warhead decision.",
        "review_citation": {"pmid": PMID, "pmcid": PMCID, "doi": DOI,
                            "note": "Safe-group REVIEW (secondary source for the compounds)."},
        "disclaimer": "Records only what the fetched review text states. Primary med-chem paper for the "
                      "indole-3-carbinol series must still be fetched + read before adoption. No structures or "
                      "selectivity magnitudes are asserted beyond what appears verbatim below.",
    }
    ft = fetch_fulltext_xml()
    out["fulltext_fetch"] = {k: ft[k] for k in ("url", "http_status", "ok") if k in ft}
    if ft.get("ok") and ft.get("body"):
        xml = ft["body"]
        text = strip_tags(xml)
        out["compound_passages"] = sentences_with_keywords(text)
        out["candidate_primary_refs"] = reference_entries(xml)
        out["n_passages"] = len(out["compound_passages"])
        out["n_candidate_refs"] = len(out["candidate_primary_refs"])
    else:
        out["error"] = "Could not fetch review full text; retry or supply an alternate OA source."
    with open("safe2025-verify.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"safe2025_verify: fetch_ok={ft.get('ok')} passages={out.get('n_passages', 0)} "
          f"refs={out.get('n_candidate_refs', 0)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
