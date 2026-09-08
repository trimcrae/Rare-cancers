#!/usr/bin/env python3
"""W1 — assemble a PROPOSED Supplementary Table S3.

Scope (established from, not invented by, this script):
  emc-atr-collaborator-package-changelog.md, 2026-08-10 entry:
    "Supplementary Table S3, holding the cut coordinates, assembled cDNA length and open reading
     frame for each reported junction, from emc-fet-construct-designs.json"

Reads ONE committed input, copies selected recorded fields verbatim, emits markdown.
It computes NO value. Every cell is either a copied JSON leaf, a fixed label, or UNRESOLVED.
"""
import json, hashlib, sys, datetime

SRC = sys.argv[1] if len(sys.argv) > 1 else "research/modalities/emc-fet-construct-designs.json"
raw = open(SRC, "rb").read()
DIGEST = hashlib.sha256(raw).hexdigest()
NBYTES = len(raw)
d = json.loads(raw)

U = "UNRESOLVED"

# (column header, JSON path template relative to a construct, extractor)
COLS = [
    ("Junction (label)",                       "constructs[{i}].label",                                              lambda c: c["label"]),
    ("Reported rank",                          "constructs[{i}].reported_rank",                                      lambda c: c["reported_rank"]),
    ("5' transcript",                          "constructs[{i}].junction_in_exon_numbering.five_prime_transcript",   lambda c: c["junction_in_exon_numbering"]["five_prime_transcript"]),
    ("5' last exon retained (transcript rank)","constructs[{i}].junction_in_exon_numbering.five_prime_last_exon_retained_transcript_rank", lambda c: c["junction_in_exon_numbering"]["five_prime_last_exon_retained_transcript_rank"]),
    ("3' transcript",                          "constructs[{i}].junction_in_exon_numbering.three_prime_transcript",  lambda c: c["junction_in_exon_numbering"]["three_prime_transcript"]),
    ("3' first exon retained (transcript rank)","constructs[{i}].junction_in_exon_numbering.three_prime_first_exon_retained_transcript_rank", lambda c: c["junction_in_exon_numbering"]["three_prime_first_exon_retained_transcript_rank"]),
    ("CUT — 5' cDNA nt retained",              "constructs[{i}].junction_in_nucleotide_numbering.five_prime_cdna_nt_retained",   lambda c: c["junction_in_nucleotide_numbering"]["five_prime_cdna_nt_retained"]),
    ("CUT — 5' coding nt retained",            "constructs[{i}].junction_in_nucleotide_numbering.five_prime_coding_nt_retained", lambda c: c["junction_in_nucleotide_numbering"]["five_prime_coding_nt_retained"]),
    ("5' UTR length (nt)",                     "constructs[{i}].junction_in_nucleotide_numbering.five_prime_utr5_len_nt",        lambda c: c["junction_in_nucleotide_numbering"]["five_prime_utr5_len_nt"]),
    ("CUT — 3' cDNA resume offset (0-based)",  "constructs[{i}].junction_in_nucleotide_numbering.three_prime_cdna_resume_offset_0based", lambda c: c["junction_in_nucleotide_numbering"]["three_prime_cdna_resume_offset_0based"]),
    ("3' UTR nt read through",                 "constructs[{i}].junction_in_nucleotide_numbering.three_prime_utr_nt_read_through", lambda c: c["junction_in_nucleotide_numbering"]["three_prime_utr_nt_read_through"]),
    ("Assembled cDNA length (nt)",             "constructs[{i}].junction_in_nucleotide_numbering.fusion_cdna_len_nt",            lambda c: c["junction_in_nucleotide_numbering"]["fusion_cdna_len_nt"]),
    ("ORF length (nt)",                        "constructs[{i}].junction_in_nucleotide_numbering.fusion_orf_len_nt",             lambda c: c["junction_in_nucleotide_numbering"]["fusion_orf_len_nt"]),
    ("ORF length (aa)",                        "constructs[{i}].protein_length_aa",                                   lambda c: c["protein_length_aa"]),
    ("5' residues fully encoded",              "constructs[{i}].junction_in_residue_numbering.five_prime_residues_fully_encoded", lambda c: c["junction_in_residue_numbering"]["five_prime_residues_fully_encoded"]),
    ("Codon split across junction",            "constructs[{i}].junction_in_residue_numbering.codon_split_across_the_junction",  lambda c: c["junction_in_residue_numbering"]["codon_split_across_the_junction"]),
    ("Seam residue index (1-based)",           "constructs[{i}].junction_in_residue_numbering.seam_residue_index_1based",        lambda c: c["junction_in_residue_numbering"]["seam_residue_index_1based"]),
    ("Junction context (aa)",                  "constructs[{i}].junction_in_residue_numbering.junction_context_aa",   lambda c: c["junction_in_residue_numbering"]["junction_context_aa"]),
    ("Junction context (nt)",                  "constructs[{i}].junction_in_residue_numbering.junction_context_nt",   lambda c: c["junction_in_residue_numbering"]["junction_context_nt"]),
    ("Extra junction-encoded residues",        "constructs[{i}].domains_retained_and_lost.n_extra_junction_encoded_residues",    lambda c: c["domains_retained_and_lost"]["n_extra_junction_encoded_residues"]),
    ("In frame (self-check)",                  "constructs[{i}].self_checks.in_frame",                                lambda c: c["self_checks"]["in_frame"]),
    ("5' start matches partner (self-check)",  "constructs[{i}].self_checks.five_prime_start_matches_partner",        lambda c: c["self_checks"]["five_prime_start_matches_partner"]),
    ("3' C-terminus intact (self-check)",      "constructs[{i}].self_checks.three_prime_c_terminus_intact",           lambda c: c["self_checks"]["three_prime_c_terminus_intact"]),
    # No genomic breakpoint coordinate is recorded for any emitted construct in this input.
    ("CUT — genomic breakpoint coordinates",   "(no such key in the input)",                                          lambda c: U),
]

rows, prov = [], []
for i, c in enumerate(d["constructs"]):
    cells = []
    for hdr, path, fn in COLS:
        v = fn(c)
        cells.append(v)
        prov.append((c["id"], hdr, path.format(i=i), v))
    rows.append((c["id"], cells))

# Reported fusions with NO sourced transcript-level junction: recorded as such, not emitted as
# constructs. They appear as UNRESOLVED rows so the table does not silently drop a reported fusion.
gap_rows = []
for j, g in enumerate(d["partners_with_no_sourced_transcript_junction"]):
    gap_rows.append((g["fusion"], g["status"],
                     f"partners_with_no_sourced_transcript_junction[{j}].fusion",
                     f"partners_with_no_sourced_transcript_junction[{j}].status"))

def fmt(v):
    if v is True: return "yes"
    if v is False: return "no"
    return str(v)

def md_cell(v):
    """Markdown-escape only. The pipe in a junction-context string is part of the recorded value;
    escaping it for the table changes rendering, never the value (provenance JSON keeps it raw)."""
    return fmt(v).replace("|", "\\|")

out = []
out.append("# PROPOSED Supplementary Table S3 — per-junction assembly coordinates\n")
out.append("**Status: PROPOSED. Not applied to any manuscript or shared artifact.**\n")
out.append(f"Source (single input): `{SRC}`  \nsha256 `{DIGEST}`  \nsize {NBYTES:,} B  \n"
           f"Assembled {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} by `build_table_s3.py`.\n")
out.append("Every cell below is a verbatim copy of a recorded JSON leaf, a fixed column label, or "
           "`UNRESOLVED`. No value in this table was derived, inferred, rounded or interpolated.\n")
out.append(f"Input's own status line: {d['⛔_STATUS_OF_EVERYTHING_BELOW']}\n")

# transposed layout: one column per junction (4 junctions, many fields) reads better
ids = [r[0] for r in rows]
out.append("| Field | " + " | ".join(ids) + " |")
out.append("|---|" + "---|" * len(ids))
for k, (hdr, path, _) in enumerate(COLS):
    out.append("| " + hdr + " | " + " | ".join(md_cell(r[1][k]) for r in rows) + " |")
out.append("")
out.append("## Reported fusions with no sourced transcript-level junction\n")
out.append("| Fusion | Every assembly field | Recorded status |")
out.append("|---|---|---|")
for f, s, _, _ in gap_rows:
    out.append(f"| {f} | {U} | {s} |")
out.append("")
out.append("## Limits, copied verbatim from the input's `_limits`\n")
for L in d["_limits"]:
    out.append(f"- {L}")
out.append("")

open("/tmp/claude-0/w1-lane/PROPOSED-supplementary-table-s3.md", "w").write("\n".join(out))

p = ["# Row and field provenance — PROPOSED Supplementary Table S3\n",
     f"Input `{SRC}`, sha256 `{DIGEST}`, {NBYTES:,} B.\n",
     "Paths are Python-style into the parsed JSON. Every table cell appears here.\n",
     "| Row (construct id) | Column | JSON path | Value as emitted |", "|---|---|---|---|"]
for cid, hdr, path, v in prov:
    p.append(f"| {cid} | {hdr} | `{path}` | {md_cell(v)} |")
p.append("")
p.append("| Gap row | Column | JSON path |")
p.append("|---|---|---|")
for f, s, fp, sp in gap_rows:
    p.append(f"| {f} | Fusion | `{fp}` |")
    p.append(f"| {f} | Recorded status | `{sp}` |")
    p.append(f"| {f} | all assembly fields | UNRESOLVED — no such record in the input |")
p.append("")
p.append("Limits block: `_limits[0..%d]`, copied verbatim." % (len(d['_limits'])-1))
p.append("Input status line: `⛔_STATUS_OF_EVERYTHING_BELOW`.")
p.append("")
open("/tmp/claude-0/w1-lane/PROVENANCE-table-s3.md", "w").write("\n".join(p))

json.dump({"input": SRC, "sha256": DIGEST, "bytes": NBYTES,
           "cells": [{"row": c, "column": h, "json_path": p_, "value": v} for c, h, p_, v in prov]},
          open("/tmp/claude-0/w1-lane/provenance-cells.json", "w"), indent=1)
print("wrote table, provenance md, provenance json;", len(prov), "provenanced cells")
