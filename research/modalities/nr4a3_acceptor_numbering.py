#!/usr/bin/env python3
"""Which transcript-exon rank is NR4A3's FIRST CODING exon, across every annotated transcript?

⭐ WHY THIS EXISTS. The condensed ASO article tiles every design against NR4A3 **transcript exon
3** — the first coding exon of ENST00000395097, whose exons 1 and 2 are non-coding
(`nr4a3-exon-audit.json`). The only two fusion-positive EMC cell models
(USZ20-EMC1 / USZ22-EMC2, PMID 36316541) are reported at NR4A3 **"exon 2"**, with no transcript
accession, no sequenced exon-exon boundary and no junction sequence. So the manuscript cannot say
whether its reagents engage the only available test articles, and reports that gap honestly.

⛔ THE QUESTION IS NOT "WHICH EXON DID THEY MEAN" — nobody here can read their intent. It is the
narrower one annotation CAN answer: **is there an annotated NR4A3 transcript on which the first
coding exon is transcript exon 2?** If yes, "exon 2" is a numbering an author could reach while
naming the SAME physical seam this panel targets, and the discordance is plausibly notational. If
no annotated transcript places the first coding exon at rank 2, then "exon 2" names a non-coding
exon on every model available, and the discordance is real.

⚠ WHAT THIS DOES NOT ESTABLISH. It does not establish the breakpoint of either cell model, does not
decide which transcript a tumour transcribes, and does not license quoting either reagent as valid
for those models. Only RNA sequencing of the test article settles that, which is what the
manuscript already requires before any oligonucleotide is ordered. This narrows a notational
ambiguity; it does not close a biological one.

NETWORK. Ensembl REST, 403'd at CONNECT by the dev sandbox (CLAUDE.md §6), so this runs on a
GitHub Actions runner and publishes back to the triggering branch.

Run:
    python3 research/modalities/nr4a3_acceptor_numbering.py           # fetch + write (CI)
    python3 research/modalities/nr4a3_acceptor_numbering.py --check   # offline: re-read the artifact
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import emc_fet_construct_designs as efc   # noqa: E402  — ONE home for the Ensembl fetch helper

ENS = "https://rest.ensembl.org"
SYMBOL = "NR4A3"
OUT = os.path.join(HERE, "nr4a3-acceptor-exon-numbering.json")

#: The acceptor this repository's whole design panel is tiled against, on the canonical transcript.
#: Named here so the artifact states what it is being compared to rather than leaving it implied.
PANEL_ACCEPTOR = {"transcript": "ENST00000395097", "transcript_exon_rank": 3}

#: The RefSeq mRNA every off-target screen in this repository names as `NR4A3_mRNA`. Its exon
#: numbering is what a reader reconciling this paper against those screens would use.
SCREEN_REFSEQ = "NM_006981"


def _exon_rows(tr):
    """Per-exon coding length for one transcript, in transcript order."""
    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    trans = tr.get("Translation")
    if not trans:
        return [{"transcript_exon_rank": i, "coding_nt_in_exon": 0, "is_coding": False}
                for i, _ in enumerate(exons, start=1)]
    lo, hi = trans["start"], trans["end"]
    rows = []
    for rank, ex in enumerate(exons, start=1):
        cstart, cend = max(ex["start"], lo), min(ex["end"], hi)
        clen = max(0, cend - cstart + 1)
        rows.append({"transcript_exon_rank": rank, "coding_nt_in_exon": clen,
                     "is_coding": clen > 0})
    return rows


def _first_coding_rank(rows):
    for r in rows:
        if r["is_coding"]:
            return r["transcript_exon_rank"]
    return None


def build() -> dict:
    look = efc._fetch(f"{ENS}/lookup/symbol/homo_sapiens/{SYMBOL}?expand=1", "application/json")
    out = []
    for tr in look["Transcript"]:
        rows = _exon_rows(tr)
        first = _first_coding_rank(rows)
        rec = {
            "transcript": tr["id"],
            "biotype": tr.get("biotype"),
            "is_canonical": bool(tr.get("is_canonical") == 1),
            "is_mane_select": any(t.get("type") == "MANE_Select"
                                  for t in (tr.get("Tag") or [])) or None,
            "n_transcript_exons": len(rows),
            "n_noncoding_5prime_exons": (first - 1) if first else None,
            "first_coding_transcript_exon_rank": first,
            "translated": first is not None,
        }
        #: RefSeq mRNA accessions this transcript is cross-referenced to. This is how a reader gets
        #: from an Ensembl exon rank to the numbering a RefSeq-indexed report would have used.
        try:
            xr = efc._fetch(
                f"{ENS}/xrefs/id/{tr['id']}?content-type=application/json&external_db=RefSeq_mRNA",
                "application/json")
            rec["refseq_mrna"] = sorted({x.get("primary_id") for x in xr if x.get("primary_id")})
        except Exception as exc:  # noqa: BLE001 — an xref gap is reported, never guessed around
            rec["refseq_mrna"] = None
            rec["refseq_lookup_error"] = str(exc)
        out.append(rec)

    coding = [r for r in out if r["translated"]]
    ranks = sorted({r["first_coding_transcript_exon_rank"] for r in coding})
    at_two = [r["transcript"] for r in coding if r["first_coding_transcript_exon_rank"] == 2]
    at_three = [r["transcript"] for r in coding if r["first_coding_transcript_exon_rank"] == 3]
    carrying_screen_refseq = [r["transcript"] for r in out
                              if r.get("refseq_mrna") and SCREEN_REFSEQ in r["refseq_mrna"]]

    return {
        "_what": ("Every annotated NR4A3 transcript, with the transcript-exon rank of its first "
                  "CODING exon. Answers one narrow question: can 'NR4A3 exon 2' name the first "
                  "coding exon on some annotated transcript?"),
        "_why": ("The two fusion-positive EMC cell models (PMID 36316541) are reported at NR4A3 "
                 "'exon 2' with no transcript accession; this panel is tiled at transcript exon 3 "
                 "of ENST00000395097, which is that transcript's first coding exon."),
        "⛔_what_this_is_not": (
            "NOT a determination of either cell model's breakpoint, NOT a claim about which "
            "transcript any tumour expresses, and NOT a licence to quote any reagent as valid for "
            "those models. RNA sequencing of the test article remains required before synthesis."),
        "_method": ("Ensembl REST lookup/symbol?expand=1; per-exon coding length computed by "
                    "intersecting each exon with the CDS span, the same construction "
                    "nr4a3_exon_audit and emc_fet_construct_designs use. RefSeq mRNA accessions "
                    "read from the xrefs endpoint, not typed."),
        "panel_acceptor": PANEL_ACCEPTOR,
        "screen_refseq": SCREEN_REFSEQ,
        "n_transcripts": len(out),
        "n_coding_transcripts": len(coding),
        "first_coding_exon_ranks_observed": ranks,
        "transcripts_with_first_coding_exon_at_rank_2": at_two,
        "transcripts_with_first_coding_exon_at_rank_3": at_three,
        "transcripts_cross_referenced_to_screen_refseq": carrying_screen_refseq,
        "a_transcript_numbering_exists_where_exon_2_is_the_first_coding_exon": bool(at_two),
        "transcripts": out,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--check" in argv:
        if not os.path.exists(OUT):
            print(f"{os.path.basename(OUT)} is not built", file=sys.stderr)
            return 1
        d = json.load(open(OUT, encoding="utf-8"))
        print(f"{d['n_transcripts']} transcripts, {d['n_coding_transcripts']} coding; "
              f"first-coding-exon ranks {d['first_coding_exon_ranks_observed']}; "
              f"rank-2 numbering exists: "
              f"{d['a_transcript_numbering_exists_where_exon_2_is_the_first_coding_exon']}")
        return 0
    d = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}: {d['n_transcripts']} transcripts, ranks "
          f"{d['first_coding_exon_ranks_observed']}, rank-2 exists "
          f"{d['a_transcript_numbering_exists_where_exon_2_is_the_first_coding_exon']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
