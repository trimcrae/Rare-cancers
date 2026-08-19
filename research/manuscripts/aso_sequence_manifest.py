#!/usr/bin/env python3
"""Every oligonucleotide the deposit names, as CSV and FASTA — the canonical machine-readable form.

⛔ WHY THIS EXISTS, AND IT IS A WRONG-REAGENT HAZARD. Measured 2026-08-17 by extracting the text
layer of the built submission PDF: a sequence in a table cell arrives as a bare base string with NO
`5′-`/`-3′` delimiters, immediately adjacent to a numeric cell —

    CAGGGCATATCATCAAACCA   3   123   6   189 ...

so whether the sequence and the next column fuse is a property of the READER's PDF extractor, not of
the document. One extractor returned `5′-GGGCATATCATCAAAC3′3 8 123 → 6`, i.e. a 16-mer with a
trailing digit and a lost delimiter. For a paper whose entire deliverable is orderable oligos, a
reader who copy-pastes and orders that has synthesised a different molecule, and every number in this
paper is false of it. bioRxiv's own full-text HTML/XML conversion inherits the same text layer.

⭐ THE FIX IS NOT ONLY TO PAD THE CELLS. Padding makes today's extractor behave; it does not make the
PDF a machine-readable record, and the next extractor is not ours to control. The durable fix is that
the deposit ships the sequences in a format that was never typeset, which the manuscript names as
CANONICAL, so nobody has to copy anything out of a PDF at all.

⚠ EVERY FIELD IS DERIVED FROM THE SAME ARTIFACTS THE TABLES ARE BUILT FROM. A sequence here and the
same sequence in a table row cannot diverge without the generator being wrong first, which is the
property `submission_tables.py` already holds and the reason this file reads artifacts rather than
parsing the manuscript. ⛔ Never re-type a sequence into this file.

⛔ THE CONDEMNED DESIGNS ARE INCLUDED, FLAGGED, NOT OMITTED. Three designs pair their whole catalytic
gap against the patient's own un-rearranged NR4A3 allele and the paper says not to carry them
forward. Leaving them out would repeat the defect a cold reader already found in the tables banner:
a reader who has transcribed one cannot check it against a list that does not carry it. Two of them
are one- and two-position register shifts of a reagent the paper recommends, sharing 15 of 16 bases.
They travel here with `do_not_order` set, which is the only form in which naming them is safe.

    python3 research/manuscripts/aso_sequence_manifest.py
    python3 research/manuscripts/aso_sequence_manifest.py --check    # exit 1 if stale
"""
import argparse
import csv
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(ROOT, ".."))
MOD = os.path.join(ROOT, "modalities")
ASO = os.path.join(HERE, "aso")

OUT_CSV = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
OUT_FASTA = os.path.join(ASO, "fusion-junction-aso-sequences.fasta")

#: The three documents a depositor uploads. The coverage guard below asserts that every sequence
#: they NAME appears in this manifest — that is the contract, and it is what makes the manifest
#: canonical rather than merely adjacent.
DOCS = ("fusion-junction-aso-research-article.md",
        "fusion-junction-aso-submission-tables.md",
        "fusion-junction-aso-supplementary-information.md")

#: A sequence as the manuscripts write it, and as a bare table cell. Both forms are collected,
#: because the table cells are exactly the ones that lose their delimiters in the PDF text layer.
_IN_PROSE = re.compile(r"5[′']-([ACGT]{12,25})-3[′']")
_IN_CELL = re.compile(r"\|\s*(?:5[′']-)?([ACGT]{14,22})(?:-3[′'])?\s*\|")


def _load(*parts):
    p = os.path.join(MOD, *parts)
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _named_in_documents():
    """Every distinct sequence the three deposit documents name, in either written form."""
    out = set()
    for name in DOCS:
        p = os.path.join(ASO, name)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding="utf-8").read()
        out |= set(_IN_PROSE.findall(txt))
        out |= set(_IN_CELL.findall(txt))
    return out


#: ⛔⛔ ONE GEOMETRY VOCABULARY, BECAUSE THE THREE CONDEMNED DESIGNS WERE THE ONES OUTSIDE IT
#: (2026-08-17). The source artifacts spell the same architecture two ways: the panel and gap
#: artifacts write `5-6-5`, the non-canonical-acceptor screen writes `5-6-5 (LNA-DNA-LNA)`. The
#: shipped CSV inherited both — 176 rows against 30 — and ALL THREE `do_not_order` designs were in
#: the 30. So a reader filtering `geometry == "5-6-5"`, the spelling 85% of the file uses, received
#: a list of 5-6-5 designs with every design the paper condemns silently removed from it. That is
#: this manifest's own founding hazard turned inward, and it is worse than the PDF one it was built
#: to fix, because a filtered CSV looks complete.
#:
#: ⚠ NORMALISED, NOT REWRITTEN AT SOURCE. The parenthetical is correct where the screen writes it;
#: what cannot stand is two vocabularies in one column of one file. The chemistry it spells out is
#: in this file's header for every row, so nothing is lost by dropping it here.
_GEOMETRY_SYNONYMS = {"5-6-5 (LNA-DNA-LNA)": "5-6-5",
                      "5-8-5 (LNA-DNA-LNA)": "5-8-5",
                      "5-10-5 (LNA-DNA-LNA)": "5-10-5"}


def _geometry(raw):
    """The one spelling of a gapmer architecture this file uses."""
    text = str(raw or "").strip()
    return _GEOMETRY_SYNONYMS.get(text, text)


#: Fields where two sources naming the same sequence MUST agree, and where a disagreement is a
#: defect to surface rather than a tie to break. Deliberately not the whole record: `role`,
#: `junction` and `clinical_tier` are the naming source's editorial view of the design and the
#: blocks legitimately word them differently — the first source's stands.
_MERGED_FIELDS = ("gap_level_margin", "mature_parent_duplex_through_gap_bp",
                  "mature_parent_duplex_gene", "parent_paired_gap_dna_nt",
                  "parent_seam_hybrid_bp", "geometry", "length_nt")


def _rows():
    """Every design the deposit can name, with the properties its tables print.

    Sources, all of them the tables' own:
      * `aso-per-junction-table.json` — the 38-junction 5-6-5 panel, every design at every register.
      * `aso-gap-length-tradeoff.json` — the 5-8-5 and 5-10-5 geometries at the lead seam.
      * the noncoding-acceptor screen — the exon-2 and cryptic-exon seams, including the three
        designs condemned on the un-rearranged allele.
    """
    rows, by_sequence = [], {}

    def add(**kw):
        """First source to name a sequence owns its row; later sources FILL ITS BLANKS.

        ⛔ WHY NOT FIRST-WINS-AND-DISCARD (2026-08-17). Each artifact computes a different subset of
        the parent-duplex quantities: the per-junction table has the mature-parent SEARCH and not
        the seam arithmetic, the gap-length artifact has all three. A design present in both — the
        lead 16-mer is — was written from whichever block ran first and the other block's columns
        were dropped on the floor, so the lead shipped with `parent_paired_gap_dna_nt` empty while
        the number sat in an artifact this generator had already opened. An empty cell would then
        have meant "the block that won the race did not compute this", which is not a fact about
        the design and is not what the header says a blank means.

        ⚠ FILLS ONLY WHAT IS EMPTY, AND NEVER OVERWRITES. If two artifacts disagree about a value
        the merge must not silently pick one, so a conflict raises instead — that disagreement
        would be a real defect upstream and hiding it here is how it would ship.
        """
        seq = kw["sequence"]
        kw["length_nt"] = len(seq)
        first = by_sequence.get(seq)
        if first is None:
            by_sequence[seq] = kw
            rows.append(kw)
            return
        for field, value in kw.items():
            if value in ("", None):
                continue
            held = first.get(field)
            if held in ("", None):
                first[field] = value
            elif held != value and field in _MERGED_FIELDS:
                raise RuntimeError(
                    f"{seq}: sources disagree on {field}: {held!r} vs {value!r}")

    per = _load("aso-per-junction-table.json")
    for j in per["junctions"]:
        label = j["junction_label"]
        best = (j.get("best_available") or {}).get("antisense_5to3")
        for d in j.get("designs", []):
            seq = d.get("antisense_5to3")
            if not seq:
                continue
            add(sequence=seq,
                junction=label,
                geometry="5-6-5",
                gap_level_margin=d.get("gap_specificity_margin"),
                # ⚠ `parent_duplex_bp`/`parent` in THIS artifact are the search quantity — the same
                # measurement the gap artifact calls `mature_parent_duplex_through_whole_gap_bp`,
                # under a shorter name. The seam arithmetic is not computed here, so it stays blank
                # rather than being back-derived: a value this table never held would be ours.
                mature_parent_duplex_through_gap_bp=d.get("parent_duplex_bp"),
                mature_parent_duplex_gene=d.get("parent") or "",
                parent_paired_gap_dna_nt="",
                parent_seam_hybrid_bp="",
                # ⚠ THE POLARITY IS THE ARTIFACT'S, NOT A RE-DERIVATION. `parent_is_liability` true
                # means the design pairs a wild-type parent through the whole catalytic gap, which
                # is this paper's central negative — not a quality score.
                pairs_a_wild_type_parent_through_the_gap=bool(d.get("parent_is_liability")),
                role=("best available at this junction" if seq == best else "screened design"),
                do_not_order="",
                clinical_tier=j.get("clinical_tier", ""))

    # ⛔ THE WHOLE `per_design` LIST, NOT JUST THE LEAD SEAM'S THREE GEOMETRIES. The first version of
    # this generator read only `lead_reagent_at_the_most_commonly_reported_seam.by_geometry`, and the
    # coverage contract below caught it immediately: `CAGGGCATATCAAGCGCT`, the 18-mer §2.7 names at
    # TCF12 exon 7, is in `per_design` and nowhere in the lead-seam block. 798 records — the 190
    # 5-6-5 designs plus 266 at 5-8-5 and 342 at 5-10-5.
    gap = _load("aso-gap-length-tradeoff.json")
    for d in gap.get("per_design", []):
        seq = d.get("antisense_5to3")
        if not seq:
            continue
        n = len(seq)
        add(sequence=seq, junction=d.get("junction", ""),
            geometry={16: "5-6-5", 18: "5-8-5", 20: "5-10-5"}.get(n, ""),
            gap_level_margin=d.get("gap_specificity_margin"),
            # ⚠ THE ONLY BLOCK THAT CARRIES ALL THREE. `donor` is NOT a parent-duplex gene — it is
            # the design's own donor partner — and it used to be written into the gene column
            # beside a duplex length it has nothing to do with. The duplex gene here is the one the
            # search returned, which is null when the search found nothing.
            mature_parent_duplex_through_gap_bp=d.get("mature_parent_duplex_through_whole_gap_bp"),
            mature_parent_duplex_gene=d.get("mature_parent_duplex_gene") or "",
            parent_paired_gap_dna_nt=d.get("parent_paired_gap_dna_nt"),
            parent_seam_hybrid_bp=d.get("parent_seam_hybrid_bp"),
            pairs_a_wild_type_parent_through_the_gap="",
            role="screened design", do_not_order="", clinical_tier="")

    nc = _load("noncoding-acceptor", "aso-noncoding-acceptor-screened-table.json")
    # ⚠ THIS ARTIFACT'S `geometry` IS A BLOCK, NOT A STRING — {oligo_len, wing, gap_nt,
    # architecture, gap_region_1based} — where the panel artifact's is a bare label. Read the
    # architecture out rather than letting a dict reach a CSV cell, which is how it first failed.
    nc_geom = nc.get("geometry")
    if isinstance(nc_geom, dict):
        nc_geom = nc_geom.get("architecture") or nc_geom.get("oligo_len") or ""
    nc_geom = _geometry(nc_geom)
    wt = nc.get("⭐_wild_type_NR4A3_cleavage_liability", {})
    condemned = set(wt.get("designs_cleaving_wild_type_NR4A3") or [])
    condemned |= set((wt.get("positive_control") or {}).get("observed_designs") or [])
    for j in nc.get("junctions", []):
        for d in j.get("designs", []):
            seq = d.get("antisense_5to3")
            if not seq:
                continue
            bad = seq in condemned
            add(sequence=seq, junction=j.get("junction_label", ""), geometry=nc_geom,
                gap_level_margin=d.get("gap_specificity_margin"),
                mature_parent_duplex_through_gap_bp=d.get("parent_duplex_bp"),
                mature_parent_duplex_gene=d.get("parent") or "",
                parent_paired_gap_dna_nt="", parent_seam_hybrid_bp="",
                pairs_a_wild_type_parent_through_the_gap=bool(d.get("parent_is_liability")),
                role="non-canonical acceptor seam",
                do_not_order=("DO NOT ORDER — pairs its whole catalytic gap against the patient's "
                              "own un-rearranged NR4A3 allele" if bad else ""),
                clinical_tier=j.get("clinical_tier", ""))

    # ⛔ THE CRYPTIC-EXON SEAMS ARE A THIRD SOURCE, AND THE CONTRACT FOUND THAT TOO. The
    # noncoding-acceptor table covers the NR4A3 exon-2 acceptors only; the intron-2 cryptic-exon
    # seams live in their own artifacts, which is where `ATGAGGGCCTTGTGTG` — the reagent §2.6 names
    # as the one the TAF15 seam keeps — actually is. Reading only the exon-2 table looked complete
    # and was not.
    for fn in ("aso-taf15-intron2-designs.json", "aso-ewsr1-intron2-designs.json"):
        blk = _load(fn)
        label = blk.get("junction_label") or blk.get("_generic_label_from_the_builder") or ""
        for d in blk.get("designs", []):
            seq = d.get("antisense_5to3")
            if not seq:
                continue
            bad = seq in condemned
            add(sequence=seq, junction=label, geometry=_geometry(d.get("architecture")),
                gap_level_margin=d.get("gap_specificity_margin"),
                mature_parent_duplex_through_gap_bp="", mature_parent_duplex_gene="",
                parent_paired_gap_dna_nt="", parent_seam_hybrid_bp="",
                pairs_a_wild_type_parent_through_the_gap=bool(bad),
                role="intron-2 cryptic-exon seam",
                do_not_order=("DO NOT ORDER — pairs its whole catalytic gap against the patient's "
                              "own un-rearranged NR4A3 allele" if bad else ""),
                clinical_tier="")

    # ⛔ A CONDEMNED DESIGN THAT REACHED NO ROW ABOVE STILL SHIPS. If the screen's shape changes and
    # one of them stops appearing in a junction block, silently dropping it is the failure this
    # manifest exists to prevent — so they are added explicitly, last, and only if still missing.
    for seq in sorted(condemned):
        add(sequence=seq, junction="", geometry="5-6-5", gap_level_margin="",
            mature_parent_duplex_through_gap_bp="", mature_parent_duplex_gene="",
            parent_paired_gap_dna_nt="", parent_seam_hybrid_bp="",
            pairs_a_wild_type_parent_through_the_gap=True, role="condemned design",
            do_not_order=("DO NOT ORDER — pairs its whole catalytic gap against the patient's own "
                          "un-rearranged NR4A3 allele"), clinical_tier="")

    rows.sort(key=lambda r: (r["junction"], -(r["length_nt"]), r["sequence"]))
    return rows


#: ⛔⛔ THREE PARENT-DUPLEX QUANTITIES, AND TWO OF THEM READ 8 FOR THE LEAD DESIGN (2026-08-17).
#: This file first shipped ONE column, `longest_parent_duplex_bp`; a first correction split it into
#: two and asserted in the header that "the paper's tables print the second". Reading the tables
#: against the artifacts showed that claim was FALSE and the split still wrong, because there are
#: three quantities, not two, and they are computed two different ways:
#:
#:   mature_parent_duplex_through_gap_bp  a SEARCH over every window of all six mature parent
#:                                        transcripts for a duplex spanning the design's whole
#:                                        catalytic gap. The parent it finds is usually NOT the
#:                                        design's own parent. ⭐ THIS is the quantity Tables 2, 3,
#:                                        5 and 7 print. 0 means the search found none.
#:   parent_paired_gap_dna_nt             ARITHMETIC on the design's own seam: max(donor, acceptor)
#:                                        bases of gap DNA, guaranteed by construction rather than
#:                                        found. Complement of the gap-level margin.
#:   parent_seam_hybrid_bp                that run plus the LNA wing on the same side — the whole
#:                                        contiguous hybrid the design presents to its own parent.
#:
#: For the lead 5-6-5 the first and third BOTH read 8, from different genes (*TFG* by search;
#: *EWSR1*/*NR4A3* by arithmetic) — so a wrong join looks right on the very design a reader is most
#: likely to check. They separate on the 5-8-5 control, where the search returns 0 and the seam
#: hybrid is 9. Worse, the two-column version carried the SEARCH quantity for rows sourced from the
#: per-junction and non-canonical-acceptor tables and the ARITHMETIC one for rows sourced from the
#: gap-length artifact — one column name, two quantities, decided by a provenance the CSV did not
#: print. Each now has its own column, populated only where that quantity is actually measured.
#:
#: `test_aso_sequence_manifest.py` holds the join: every duplex figure the submission tables print
#: must equal this file's `mature_parent_duplex_through_gap_bp` for the same sequence.
_FIELDS = ("sequence", "length_nt", "geometry", "junction", "gap_level_margin",
           "mature_parent_duplex_through_gap_bp", "mature_parent_duplex_gene",
           "parent_paired_gap_dna_nt", "parent_seam_hybrid_bp",
           "pairs_a_wild_type_parent_through_the_gap", "role", "clinical_tier", "do_not_order")

_HEADER = [
    "# Fusion-junction ASO designs — the CANONICAL machine-readable record of every sequence this",
    "# deposit names. Generated by research/manuscripts/aso_sequence_manifest.py from the same",
    "# artifacts the submission tables are built from; do not edit by hand.",
    "#",
    "# RESEARCH USE ONLY, AND NOT FOR ADMINISTRATION TO ANY PERSON OR ANIMAL. None of these is a",
    "# medicine or a candidate drug. None has been synthesised or tested by anyone.",
    "#",
    "# CHEMISTRY. Sequences are written 5' to 3' as the ANTISENSE strand. The geometry column gives",
    "# the gapmer architecture: 5-6-5 is five locked-nucleic-acid nucleotides, a six-nucleotide DNA",
    "# gap and five LNA nucleotides, on a phosphorothioate backbone; 5-8-5 and 5-10-5 are the same",
    "# five-nucleotide LNA wings around gaps of eight and ten. Ordering the bases without the",
    "# modifications gives a different molecule, about which nothing in the paper is true.",
    "#",
    "# ⛔ THREE PARENT-DUPLEX COLUMNS, AND THEY ARE NOT INTERCHANGEABLE. Join on the right one:",
    "#   mature_parent_duplex_through_gap_bp — a SEARCH over all six mature parent transcripts for a",
    "#     duplex spanning this design's whole catalytic gap, with the gene it found in",
    "#     mature_parent_duplex_gene. 0 means the search found none. ⭐ This is the quantity the",
    "#     paper's tables print under 'longest mature-parent duplex through the gap'.",
    "#   parent_paired_gap_dna_nt — ARITHMETIC on the design's OWN seam: gap nucleotides one of its",
    "#     own two parents pairs by construction. Not a search result.",
    "#   parent_seam_hybrid_bp — that run plus the LNA wing beside it.",
    "# For the lead 16-mer the first and third both read 8, from DIFFERENT genes, so a wrong join",
    "# looks right on that design; they separate elsewhere. A blank means the source artifact for",
    "# that row does not compute the quantity — not that it is zero.",
    "#",
    "# READ do_not_order FIRST. A non-empty value means the paper names that design as one NOT to be",
    "# carried forward.",
]


def _csv_text(rows):
    buf = io.StringIO()
    for line in _HEADER:
        buf.write(line + "\n")
    w = csv.DictWriter(buf, fieldnames=_FIELDS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in _FIELDS})
    return buf.getvalue()


def _fasta_text(rows):
    """FASTA, because a synthesis order form and every sequence tool read it.

    ⚠ THE DEFLINE CARRIES THE WARNING. A FASTA record is the form most likely to be pasted straight
    into an order, so a condemned design must announce itself on the one line that travels with the
    bases rather than in a column somebody dropped.
    """
    #: ⛔ THE FASTA CARRIED NO HEADER AT ALL UNTIL 2026-08-19 (blind safety screen). The CSV opens
    #: with a RESEARCH USE ONLY block and a CHEMISTRY block; this file — the one a synthesis order
    #: form actually consumes, and the one §6 names canonical beside the CSV — opened straight on a
    #: defline. 781 records were reachable without meeting a single handling statement, and the file
    #: never said which strand it holds. `;` is the FASTA comment character and every common parser
    #: skips these lines.
    out = [
        "; Fusion-junction ASO designs — canonical machine-readable record (with the CSV beside it).",
        "; RESEARCH USE ONLY. Not for administration to any person or animal. No sequence here is a",
        "; medicine or a candidate drug; none has been synthesised or tested.",
        "; Sequences are written 5' to 3' as the ANTISENSE strand.",
        "; CHEMISTRY: LNA/DNA/LNA gapmers on a phosphorothioate backbone, geometry per record. The",
        "; bases alone, ordered as unmodified DNA, are a DIFFERENT MOLECULE.",
        "; Records tagged DO NOT ORDER pair their whole catalytic gap against a wild-type parent.",
        "; Establish the target breakpoint by RNA sequencing before ordering: each design is specific",
        "; to the exon pair or pairs it was tiled at.",
    ]
    for r in rows:
        tags = [r["geometry"], r["junction"] or "no-panel-junction"]
        if r.get("gap_level_margin") != "":
            tags.append(f"gap_level_margin={r['gap_level_margin']}")
        if r.get("do_not_order"):
            tags.append(r["do_not_order"])
        tags.append("antisense 5'->3', research use only")
        out.append(f">{r['sequence']} {' | '.join(t for t in tags if t)}")
        out.append(r["sequence"])
    return "\n".join(out) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    rows = _rows()
    csv_text, fasta_text = _csv_text(rows), _fasta_text(rows)

    # ⛔ THE COVERAGE CONTRACT, ASSERTED AT BUILD TIME RATHER THAN HOPED FOR. If the manuscript names
    # a sequence this manifest does not carry, the manifest is not canonical and saying so in the
    # paper would be false. Failing here is the whole point: it is cheaper than a reader discovering
    # it at an order form.
    named = _named_in_documents()
    missing = sorted(named - {r["sequence"] for r in rows})
    if missing:
        print(f"⛔ {len(missing)} sequence(s) named in the deposit documents are NOT in this "
              f"manifest: {missing[:6]}{' …' if len(missing) > 6 else ''}", file=sys.stderr)
        return 1

    if args.check:
        stale = []
        for path, text in ((OUT_CSV, csv_text), (OUT_FASTA, fasta_text)):
            old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if old != text:
                stale.append(os.path.relpath(path, REPO))
        if stale:
            print(f"STALE: {', '.join(stale)} would change — re-run without --check", file=sys.stderr)
            return 1
        print(f"sequence manifest is current ({len(rows)} sequences, {len(named)} named in the "
              f"documents and all present)")
        return 0

    with open(OUT_CSV, "w", encoding="utf-8") as fh:
        fh.write(csv_text)
    with open(OUT_FASTA, "w", encoding="utf-8") as fh:
        fh.write(fasta_text)
    n_bad = sum(1 for r in rows if r.get("do_not_order"))
    print(f"wrote {os.path.relpath(OUT_CSV, REPO)} and {os.path.relpath(OUT_FASTA, REPO)}: "
          f"{len(rows)} sequences, {n_bad} flagged do-not-order, "
          f"{len(named)} named in the deposit documents and all present", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
