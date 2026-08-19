#!/usr/bin/env python3
"""
Proteome-wide novelty test for the EWSR1::NR4A3 junction peptides.

Question this answers: are the junction-spanning peptides absent from the HUMAN
PROTEOME, or only from the two parent proteins? `fusion_breakpoints.py` filters each
candidate against wild-type EWSR1 and wild-type NR4A3 alone (`emit_junction`'s novelty
filter: `k not in ews_prot and k not in nr4_prot`). That is a two-protein test, and the
neoantigen manuscript and `PUB-NEOANTIGEN` both say so explicitly: "absent from the
normal proteome" has never been a claim this repo could make. This script is the test
that would let it be made — or that would find the counterexamples.

⛔ WHAT A PASS DOES AND DOES NOT LICENCE. A peptide absent from every human protein is
NOT self at the sequence level. It is NOT thereby shown to be presented, immunogenic,
safe, or free of TCR cross-reactivity: a T-cell receptor sees a surface, not a string,
and a peptide differing from a self peptide at a non-contact position can still be
cross-recognised. This is an exact-substring test and nothing more. It removes one
specific, previously-unexcluded failure mode (the peptide is simply a normal human
peptide) and leaves every other one standing.

Source (CI-fetchable, citable, reproducible):
  - UniProtKB human reference proteome UP000005640, reviewed (Swiss-Prot) entries,
    WITH isoform sequences, streamed as FASTA from the UniProt REST API. Isoforms are
    included deliberately: a junction peptide that matches no canonical sequence but
    does match an alternatively-spliced isoform is exactly the counterexample this test
    exists to find, and a canonical-only search would miss it.
  - TrEMBL (unreviewed) is NOT searched. It is predicted-and-unreviewed, so a hit there
    is not evidence that a normal protein carries the peptide; a MISS there is also not
    evidence of absence. Including it would trade a clean statement for a noisy one.
    The scope searched is recorded in the output and must be quoted with the result.

Method:
  - Peptides: every distinct `novel_peptides` entry across the in-frame junctions of
    fusion-breakpoint-neoantigens.json (the transcript-model artifact). Each is flagged
    with whether it is also a predicted binder in that artifact's ranked list, so the
    result can be read for the screen's leads specifically as well as in bulk.
  - Search: exact substring, over the concatenated proteome with a sentinel between
    records so no match can straddle two proteins. A hit records every accession whose
    sequence contains it.
  - The two parent proteins are searched like any other. They should not hit (the input
    is already parent-filtered); if one does, the upstream filter is broken and this
    script says so rather than quietly agreeing.

Output: junction-proteome-novelty.json
"""

import bisect
import gzip
import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(__file__)
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
OUT = os.path.join(HERE, "junction-proteome-novelty.json")

PROTEOME_URL = (
    "https://rest.uniprot.org/uniprotkb/stream"
    "?query=%28proteome%3AUP000005640%29+AND+%28reviewed%3Atrue%29"
    "&format=fasta&includeIsoform=true&compressed=true"
)
PARENTS = {"P56945": "EWSR1", "Q92570": "NR4A3"}
SENTINEL = "\x00"


def fetch_proteome(url=PROTEOME_URL, tries=4):
    """Stream the reviewed human proteome FASTA. Returns [(accession, name, seq)]."""
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rare-cancers/junction-novelty"})
            with urllib.request.urlopen(req, timeout=600) as r:
                raw = r.read()
            break
        except Exception as e:                                    # noqa: BLE001
            last = e
            print(f"  proteome fetch attempt {attempt + 1} failed: {e}", file=sys.stderr)
    else:
        raise RuntimeError(f"proteome fetch failed after {tries} attempts: {last}")

    try:
        text = gzip.decompress(raw).decode("utf-8", "replace")
    except (OSError, gzip.BadGzipFile):
        text = raw.decode("utf-8", "replace")

    entries, acc, name, chunks = [], None, None, []
    for line in io.StringIO(text):
        line = line.rstrip("\n")
        if line.startswith(">"):
            if acc:
                entries.append((acc, name, "".join(chunks)))
            parts = line[1:].split("|")
            acc = parts[1] if len(parts) > 2 else line[1:].split()[0]
            name = parts[2].split(" OS=")[0] if len(parts) > 2 else ""
            chunks = []
        elif line:
            chunks.append(line.strip())
    if acc:
        entries.append((acc, name, "".join(chunks)))
    return entries


def load_peptides():
    """Distinct novel junction peptides, each tagged with its junctions and binder status."""
    bp = json.load(open(BREAKPOINTS))
    binders = {b["peptide"]: b for b in bp.get("predicted_binders_ranked", [])}
    peps = {}
    for jn in bp.get("junctions", []):
        label = jn.get("junction_label") or jn.get("label") or jn.get("id") or "?"
        for p in jn.get("novel_peptides", []):
            rec = peps.setdefault(p, {"peptide": p, "junctions": [], "predicted_binder": None})
            if label not in rec["junctions"]:
                rec["junctions"].append(label)
    for p, rec in peps.items():
        b = binders.get(p)
        if b:
            rec["predicted_binder"] = {"allele": b.get("allele"), "class": b.get("class"),
                                       "affinity_nM": b.get("affinity_nM")}
    return bp, sorted(peps.values(), key=lambda r: r["peptide"])


def main():
    if not os.path.exists(BREAKPOINTS):
        print("  fusion-breakpoint-neoantigens.json absent; nothing to test", file=sys.stderr)
        return 1
    bp, peptides = load_peptides()
    print(f"  {len(peptides)} distinct novel junction peptides to test", file=sys.stderr)

    entries = fetch_proteome()
    print(f"  proteome: {len(entries)} reviewed sequences (isoforms included)", file=sys.stderr)
    # Sentinel-joined haystack: no match can straddle a record boundary.
    hay = SENTINEL.join(seq for _, _, seq in entries)
    offsets, pos = [], 0
    for acc, name, seq in entries:
        offsets.append((pos, pos + len(seq), acc, name))
        pos += len(seq) + 1

    starts = [o[0] for o in offsets]

    def locate(idx):
        k = bisect.bisect_right(starts, idx) - 1
        if k < 0:
            return None, None
        start, end, acc, name = offsets[k]
        return (acc, name) if start <= idx < end else (None, None)

    found, absent, parent_hits = [], [], []
    for rec in peptides:
        p = rec["peptide"]
        hits, i = [], hay.find(p)
        while i != -1:
            acc, name = locate(i)
            if acc and not any(h["accession"] == acc for h in hits):
                hits.append({"accession": acc, "protein": name})
                if acc.split("-")[0] in PARENTS:
                    parent_hits.append({"peptide": p, "accession": acc,
                                        "parent": PARENTS[acc.split("-")[0]]})
            i = hay.find(p, i + 1)
        out = dict(rec, proteome_hits=hits, novel_proteome_wide=not hits)
        (absent if not hits else found).append(out)

    binder_hits = [r for r in found if r["predicted_binder"]]
    result = {
        "_note": ("Proteome-wide exact-substring novelty test for the EWSR1::NR4A3 junction "
                  "peptides. Closes the gap that fusion_breakpoints.py filters novelty against "
                  "wild-type EWSR1 and NR4A3 ONLY. An exact-match miss is NOT presentation, NOT "
                  "immunogenicity, NOT safety and NOT absence of TCR cross-reactivity."),
        "⛔_what_this_is_not": ("A peptide absent from every reviewed human protein is not thereby "
                               "a safe or usable target. A TCR reads a peptide-MHC surface, so a "
                               "peptide differing from a self peptide at a non-contact position can "
                               "still be cross-recognised. This test excludes exactly one failure "
                               "mode: that the peptide is simply a normal human peptide."),
        "_input": {"file": "fusion-breakpoint-neoantigens.json",
                   "artifact_utc": bp.get("_utc"),
                   "coordinate_system": "TRANSCRIPT (the corrected model)",
                   "n_inframe_junctions": bp.get("n_inframe_junctions")},
        "_proteome": {"source": "UniProtKB REST stream", "url": PROTEOME_URL,
                      "proteome_id": "UP000005640", "reviewed_only": True,
                      "isoforms_included": True, "trembl_included": False,
                      "n_sequences": len(entries), "n_residues": sum(len(s) for _, _, s in entries)},
        "_method": ("exact substring search of each peptide against the sentinel-joined proteome; "
                    "every containing accession recorded; no mismatch tolerance"),
        "_cost": "$0 — CI only, one public UniProt fetch, no GPU and no rental.",
        "n_peptides_tested": len(peptides),
        "n_novel_proteome_wide": len(absent),
        "n_found_in_proteome": len(found),
        "n_predicted_binders_found_in_proteome": len(binder_hits),
        "⛔_upstream_filter_check": (
            {"parent_protein_hits": parent_hits,
             "verdict": "BROKEN — a parent-filtered peptide matched a parent protein"}
            if parent_hits else
            {"parent_protein_hits": [], "verdict": "consistent — no parent-filtered peptide hit a parent"}),
        "peptides_found_in_proteome": found,
        "peptides_novel_proteome_wide": absent,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print(f"  {len(absent)}/{len(peptides)} novel proteome-wide; "
          f"{len(found)} found in a human protein ({len(binder_hits)} of them predicted binders)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
