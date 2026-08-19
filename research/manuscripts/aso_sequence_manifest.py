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


#: ⛔ THE SECOND "DO NOT ORDER" REASON, AND IT IS NOT THE SAME AS THE FIRST (2026-08-19). A design
#: that pairs a wild-type PARENT — the donor gene, or NR4A3 — through the whole catalytic gap is
#: the paper's central negative and must not be ordered. That is a different condemnation from the
#: three designs that pair the patient's own UN-REARRANGED NR4A3 allele at a non-canonical
#: acceptor, and the two reasons stay distinct so a reader can see which screen condemned a row.
_PARENT_PAIRED_DO_NOT_ORDER = (
    "DO NOT ORDER — pairs its whole catalytic gap against a wild-type parent gene at the "
    "ten-base-pair criterion, which is this paper's central negative")

#: The criterion the whole paper is stated on. A duplex through the whole gap at or above this
#: length is a liability; below it, the paper reports the run and does not count it.
MIN_PARENT_DUPLEX_BP = 10


def _pairs_a_parent(duplex_bp):
    """True where a recorded duplex through the whole gap reaches the criterion, else ''.

    ⚠ THE EMPTY STRING IS A THIRD STATE AND IS NOT `False`. A blank means no duplex length was
    recorded for that row at all, which is not the same as a row measured and found clean — the
    distinction this repository has paid for more than once.
    """
    if duplex_bp in (None, ""):
        return ""
    try:
        return int(duplex_bp) >= MIN_PARENT_DUPLEX_BP
    except (TypeError, ValueError):
        return ""


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
                # ⛔⛔ THIS COLUMN WAS EMPTY ON EVERY PANEL ROW, AND THAT WAS A WRONG-REAGENT HAZARD
                # (measured 2026-08-19). The paper states exactly one selection rule for this file —
                # rank by gap-level margin — and following it returns a design this file condemns at
                # EIGHT of the 40 junctions it keys a row to. At three of those every register is
                # condemned, so the rule costs a reader a clean design at the other five. Table 3 marks every one of those ⚑
                # "do not order"; the CSV the paper tells a reader to order FROM instead of the PDF
                # carried no flag at all, on 83 such rows. A canonical record that is safe only for
                # a reader who also has the table is not canonical.
                # ⚠ THE REASON STRING DIFFERS FROM THE UN-REARRANGED-ALLELE ONE ON PURPOSE. These
                # designs engage a wild-type PARENT — the donor gene or NR4A3 — which is the central
                # negative; the three below engage the patient's own un-rearranged NR4A3 allele
                # through a non-canonical acceptor. Both are "do not order", for different reasons,
                # and collapsing them would lose which screen condemned the design.
                do_not_order=(_PARENT_PAIRED_DO_NOT_ORDER
                              if d.get("parent_is_liability") else ""),
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
            # ⛔ WAS BLANK ON ALL 576 LONGER-GEOMETRY ROWS. This artifact records the duplex length
            # rather than the artifact's own boolean, so the flag is derived from it at the same
            # ten-base-pair criterion the panel rows use — the criterion §2.9 states these three
            # geometries' 87/88/87 liable counts on. A blank column read as "clean" to anyone who
            # did not know it was simply never filled.
            pairs_a_wild_type_parent_through_the_gap=_pairs_a_parent(
                d.get("mature_parent_duplex_through_whole_gap_bp")),
            role="screened design",
            do_not_order=(_PARENT_PAIRED_DO_NOT_ORDER
                          if _pairs_a_parent(
                              d.get("mature_parent_duplex_through_whole_gap_bp")) is True else ""),
            clinical_tier="")

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
                # ⛔ THE SELECTION COLUMN WAS EMPTY AT EVERY NON-PANEL SEAM (2026-08-19). Both this
                # file's header and §6 tell a reader that `role = best available at this junction`
                # is where the paper's own answer lives — and no row at the four *NR4A3* exon-2
                # seams carried it, though this artifact states `best_available` for each. So at
                # three seams with a PUBLISHED patient breakpoint the only rule a reader could
                # execute on the file was gap-level margin, which at *EWSR1* exon 7 returns
                # `AGTGGGCTTCTGCTGC` where §2.6 and Table 5 both name `CAGTGGGCTTCTGCTG`. The fix
                # for the panel stopped at the panel's edge; these seams are where two registers
                # are condemned outright, so it is where the column was needed most.
                role=("best available at this junction"
                      if seq == ((j.get("best_available") or {}).get("antisense_5to3"))
                      else "non-canonical acceptor seam"),
                # ⚠ TWO CONDEMNATIONS REACH THESE ROWS AND THE UN-REARRANGED-ALLELE ONE WINS. A
                # design at a non-canonical acceptor can both engage the patient's own allele and
                # pair a wild-type parent; the allele reason is the more specific and is the one
                # §2.6 names, so it is reported, and the parent reason covers the rest.
                do_not_order=("DO NOT ORDER — pairs its whole catalytic gap against the patient's "
                              "own un-rearranged NR4A3 allele" if bad else
                              (_PARENT_PAIRED_DO_NOT_ORDER
                               if d.get("parent_is_liability") else "")),
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
                # ⛔ THIS COLUMN READ A HARD `False` WHERE THE SCREEN WAS NEVER RUN (2026-08-19).
                # It was written as `bool(bad)` — the un-rearranged-allele verdict — so nine
                # cryptic-exon rows with NO mature-parent duplex recorded at all announced that no
                # wild-type parent pairs their gap. §2.6 says the opposite in terms: at these seams
                # "their counts are absent rather than low and must not be read beside the panel's".
                # The header already defines the third state; the column simply was not using it,
                # and one column was carrying two different questions' answers.
                pairs_a_wild_type_parent_through_the_gap=_pairs_a_parent(
                    d.get("parent_duplex_bp")),
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

    # ⛔⛔ A MOLECULE CAN SPAN MORE THAN ONE JUNCTION, AND THIS FILE NAMED ONLY ONE OF THEM
    # (cross-document audit, 2026-08-19). Nine of the 16-mers are junction-spanning at two or three
    # partners' junctions at once — the 190 design records collapse to 176 molecules for exactly
    # that reason, which Supplementary Figure S1's legend states. Each reached this file once,
    # keyed to whichever junction named it first. So `GGGCATATCATCAAAC`, printed in Tables 2 and 3
    # for *EWSR1* e12, *FUS* e10 AND *TAF15* e11, appeared here under *EWSR1* e12 alone: a
    # laboratory with a *FUS* e10 or *TAF15* e11 breakpoint, searching the record every document
    # calls canonical and tells them to order from, found NOTHING for its junction and would have
    # concluded the panel has no reagent for it. Two of the 38 panel junctions were unreachable.
    # ⚠ THE OTHER JUNCTIONS GO IN THEIR OWN COLUMN RATHER THAN INTO `junction`. One row per
    # molecule is what makes the file a record of molecules; duplicating the row per junction would
    # reintroduce the 190-versus-176 conflation this deposit has already been burned by.
    # ⛔ AND THE FIRST VERSION OF THIS BLOCK STOPPED AT THE 16-MER PANEL'S EDGE (same day). It read
    # `offtarget-chance-baseline.json`, whose series is the 176 sixteen-mers ONLY, so it filled the
    # column for 9 molecules and left it blank on every 5-8-5 and 5-10-5 row — including
    # `AGGGCATATCATCAAACC`, the gap-length control arm §4.2 tells a laboratory to synthesise
    # alongside the lead and which Table 7 heads as spanning three partners' breakpoints. A reader
    # at *FUS* exon 10 searching for their control found six rows for their junction, so they never
    # consulted the second column at all, and the arm the paper names was not among them.
    # `aso-gap-length-tradeoff.json` carries the same fact for all three geometries — 81 rows — so
    # it is the source, with the 16-mer series kept only as a cross-check that the two agree.
    # ⚠ UNION, NEVER OVERWRITE, AND THAT IS NOT A STYLE CHOICE. The artifact carries one row PER
    # JUNCTION for a multi-junction design — 33 duplicate (sequence, geometry) keys — and each row
    # lists the OTHER junctions from its own point of view. Assigning instead of unioning let the
    # last row win, which dropped *TAF15* exon 11 from the lead reagent's record entirely: the
    # column went from naming the junction to hiding it, which is the defect this block exists to
    # fix, reintroduced by the fix. Caught by re-running the search a laboratory would run.
    spans: dict[tuple[str, str], set[str]] = {}

    def _span(seq, geometry, junctions):
        spans.setdefault((seq, geometry), set()).update(junctions)

    for rec in (_load("aso-gap-length-tradeoff.json") or {}).get("per_design", []):
        others = rec.get("also_exact_at_junctions") or []
        if others:
            _span(rec["antisense_5to3"], _geometry(rec.get("architecture")),
                  list(others) + [rec["junction"]])
    for rec in (_load("offtarget-chance-baseline.json") or {}).get(
            "figure_series", {}).get("series", []):
        junctions = rec.get("junctions") or []
        if len(junctions) > 1:
            _span(rec["antisense_5to3"], "5-6-5", junctions)
    for row in rows:
        others = spans.get((row["sequence"], row["geometry"]), set())
        row["also_tiled_at_junctions"] = "; ".join(
            sorted(j for j in others if j and j != row["junction"]))

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
_FIELDS = ("sequence", "length_nt", "geometry", "junction", "also_tiled_at_junctions",
           "gap_level_margin",
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
    "# ⚠ NUCLEOBASE MODIFICATION IS NOT SPECIFIED BY THIS DEPOSIT: whether the locked cytosines",
    "# are 5-methylcytosine is a vendor default this work does not fix, and the free energies in",
    "# the paper are computed for an unmodified DNA:RNA hybrid.",
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
    "# carried forward. It is set at a ten-base-pair parent duplex: an EMPTY value is a reading at",
    "# that one cut and NOT a clearance, since 175 of the 190 panel designs pair a parent through",
    "# the whole gap at seven base pairs and 181 do so at any length.",
    "#",
    "# `role` IS THE SELECTION COLUMN. `best available at this junction` marks the design the paper",
    "# itself carries there. Ranking on gap_level_margin is NOT the paper's rule and returns a",
    "# do_not_order design at eight of the 40 junctions this file keys a row to, and at five of them",
    "# a clean register was available and the rule did not pick it.",
    "#",
    "# ⛔ EXON NUMBERS IN `junction` ARE TRANSCRIPT EXON INDICES, NOT CODING-EXON INDICES — counted",
    "# from the transcript 5' end, including non-coding exons. The two conventions differ for TCF12,",
    "# TFG and NR4A3, and this is the axis an earlier version of this work was withdrawn on. Match a",
    "# breakpoint against these models: ENST00000397938 (EWSR1), ENST00000605844 (TAF15),",
    "# ENST00000333725 (TCF12), ENST00000254108 (FUS), ENST00000240851 (TFG), ENST00000395097",
    "# (NR4A3), ENST00000325455 (PGR).",
    "#",
    "# `clinical_tier` grades whether a patient breakpoint is reported at that exon pair:",
    "# published_exon_resolved_breakpoint, partner_published_this_exon_not_reported, or",
    "# no_published_exon_resolved_breakpoint. It is written for the 16-mer panel and the",
    "# non-canonical seams only; a blank means the row's source does not grade it, not that no",
    "# breakpoint is published.",
    "#",
    "# `junction` IS ONE JUNCTION, NOT ALL OF THEM. Nine 16-mers span two or three junctions at",
    "# once — this is why 190 design records are 176 distinct molecules — and each has ONE row.",
    "# `also_tiled_at_junctions` carries the rest; search both columns before concluding that a",
    "# junction has no reagent.",
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
        "; bases alone, ordered as unmodified DNA, are a DIFFERENT MOLECULE. Nucleobase modification is",
        "; NOT specified here: whether locked cytosines are 5-methylcytosine is a vendor default",
        "; this work does not fix.",
        "; A record tagged DO NOT ORDER carries the reason on its defline. Two reasons exist: it",
        "; pairs its whole catalytic gap against a wild-type parent gene at the ten-base-pair",
        "; criterion, or it pairs the patient's own un-rearranged NR4A3 allele at a non-canonical",
        "; acceptor. ⚠ AN UNTAGGED RECORD IS NOT A CLEARANCE. The tag is applied at ten base pairs;",
        "; 175 of the 190 panel designs pair a parent through the whole gap at seven, and 181 at any",
        "; length, so absence of the tag is a statement about that one cut and nothing more.",
        "; role=best-available names the design the paper itself carries at that junction. Ranking",
        "; these records by gap_level_margin is NOT the paper's selection rule and returns a tagged",
        "; design at several junctions.",
        "; Establish the target breakpoint by RNA sequencing before ordering: each design is specific",
        "; to the exon pair or pairs it was tiled at. Nine of the 16-mers span two or three",
        "; junctions at once; each has ONE record, whose defline names the junction it is keyed to",
        "; and then 'also tiled at' the others. Search both before concluding a junction has no",
        "; reagent.",
    ]
    for r in rows:
        tags = [r["geometry"], r["junction"] or "no-panel-junction"]
        if r.get("gap_level_margin") != "":
            tags.append(f"gap_level_margin={r['gap_level_margin']}")
        #: ⛔ ROLE AND THE PARENT DUPLEX TRAVEL ON THE DEFLINE (2026-08-19). A reader ordering from
        #: this file had no way to reach the paper's own answer: `role` is the column that names it
        #: and the FASTA did not carry it, so the only rule available was gap_level_margin — which
        #: selects a do-not-order design at several junctions. The duplex length comes with it
        #: because the tag is a threshold verdict and the length is the measurement behind it.
        #: ⛔ A MOLECULE SPANNING MORE THAN ONE JUNCTION MUST SAY SO ON ITS OWN DEFLINE. The header
        #: already promises "the exon pair OR PAIRS it was tiled at"; without this the promise was
        #: unkept, and a reader searching this file for their junction found nothing.
        if r.get("also_tiled_at_junctions"):
            tags.append(f"also tiled at {r['also_tiled_at_junctions']}")
        if r.get("role"):
            tags.append(f"role={r['role']}")
        if r.get("clinical_tier"):
            tags.append(f"clinical_tier={r['clinical_tier']}")
        if r.get("mature_parent_duplex_through_gap_bp") not in ("", None):
            gene = r.get("mature_parent_duplex_gene") or "unnamed"
            tags.append(f"parent_duplex={r['mature_parent_duplex_through_gap_bp']}bp ({gene})")
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
