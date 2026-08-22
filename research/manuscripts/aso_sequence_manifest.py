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

⛔ THE CONDEMNED DESIGNS ARE INCLUDED, FLAGGED, NOT OMITTED. Two different screens condemn a design
and both verdicts ship: 3 designs pair the patient's own un-rearranged NR4A3 allele at a
non-canonical acceptor, and 249 pair a wild-type parent gene through the whole catalytic gap at the
ten-base-pair criterion — 252 of 780 records in all, recomputed 2026-08-19 and derived into the
header rather than typed into it. Leaving any of them out would repeat the defect a cold reader
already found in the tables banner: a reader who has transcribed one cannot check it against a list
that does not carry it. Two of the three are one- and two-position register shifts of a reagent the
paper recommends, sharing 15 of 16 bases. They travel here with `do_not_order` set, in COLUMN 2, on
the defline as well, which is the only form in which naming them is safe.

⚠ AND THE FILE DISTINGUISHES THREE STATES, NOT TWO. Condemned, measured-and-under-the-criterion, and
never measured at all — the last carried by an explicit token rather than by an empty cell, because
the two intron-2 cryptic-exon seams have no mature-parent duplex measurement in any artifact and
three blank cells in a row read exactly like a design that came back clean.

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
import textwrap

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

#: ⛔⛔ THE SECOND SCREEN'S CONDEMNATIONS NEVER REACHED THIS FILE (round 8, reviewer B).
#: §3 of both papers says the two screens together condemn 93 of 190, and this manifest carried
#: `do_not_order` on 87 — because nothing here ever read the pre-mRNA screen. `grep -i premrna`
#: over this module returned zero. The six missing records are five molecules, two of them at
#: TCF12_e5__NR4A3_e3, a junction this same file grades `published_exon_resolved_breakpoint`.
#: The Declarations of both papers tell a laboratory to order FROM THIS FILE rather than by
#: transcribing from the article, so a design the paper condemns was shipping unflagged.
#: ⚠ The two reasons stay distinct, exactly as the parent/allele reasons do, so a reader can see
#: WHICH screen condemned a row rather than being told only that something did.
_PREMRNA_DO_NOT_ORDER = (
    "DO NOT ORDER — carries a sense-strand near-match in parent precursor RNA that pairs its whole "
    "catalytic gap and touches intronic sequence, which no screen over mature transcripts can see")

#: The pre-mRNA screen's own liability flag. `n_invisible_to_mature_screens` and
#: `n_hybridisable_gap_fully_paired` select the SAME 19 designs of 190 in
#: `aso-premrna-offtarget.json`, which is the count both papers print.
_PREMRNA_ARTIFACTS = ("aso-premrna-offtarget.json", "aso-premrna-offtarget-genomic.json",
                      "aso-premrna-offtarget-18mer-5-8-5.json",
                      "aso-premrna-offtarget-20mer-5-10-5.json",
                      "aso-premrna-offtarget-ewsr1intron2.json",
                      "aso-premrna-offtarget-taf15intron2.json",
                      "aso-premrna-offtarget-noncoding-acceptor.json")


def _premrna_condemned():
    """Every antisense sequence the pre-mRNA screen finds gap-paired and intron-touching."""
    # ⛔ NO try/except HERE, DELIBERATELY. The first draft of this function swallowed OSError so a
    # mistyped path returned an EMPTY set and stamped nothing — a screen that reports while
    # measuring nothing, which is the exact failure this repository keeps paying for. A missing
    # artifact must break the build loudly: it means the pre-mRNA screen is not in the deposit.
    out = set()
    for name in _PREMRNA_ARTIFACTS:
        data = _load(name)
        for rec in data.get("per_design", ()):
            if (rec.get("n_invisible_to_mature_screens") or 0) > 0 and (
                    rec.get("n_hybridisable_gap_fully_paired") or 0) > 0:
                out.add(rec["antisense_5to3"])
    return out


def _stamp_the_premrna_liability(rows):
    """Condemn rows the pre-mRNA screen condemns and the mature-parent screen never saw."""
    condemned = _premrna_condemned()
    stamped = 0
    for row in rows:
        if row["sequence"] in condemned and not row["do_not_order"]:
            row["do_not_order"] = _PREMRNA_DO_NOT_ORDER
            stamped += 1
    return stamped


#: The criterion the whole paper is stated on. A duplex through the whole gap at or above this
#: length is a liability; below it, the paper reports the run and does not count it.
MIN_PARENT_DUPLEX_BP = 10

#: ⛔⛔ THE THIRD STATE NEEDED A TOKEN, BECAUSE A BLANK CELL IS READ AS A READING (2026-08-19).
#: Ten rows at the two intron-2 cryptic-exon seams have NO mature-parent duplex measurement at all:
#: `aso-taf15-intron2-designs.json` and `aso-ewsr1-intron2-designs.json` carry `clears_parent_
#: exclusion` and `exact_parent_hits` and no `parent_duplex_bp` — checked, not assumed. The search
#: was never run there. Those rows used to ship with an empty duplex cell, an empty liability cell
#: and an empty `do_not_order`, under a header sentence promising that an empty value is "a reading
#: at that one cut and NOT a clearance". That sentence was FALSE of them: it is not a reading at
#: all, and three empty cells in a row are indistinguishable from a design that was measured and
#: came back short. The state now has a token that no numeric column and no boolean column can be
#: confused with, and the header describes all three states rather than two.
#: ⚠ `do_not_order` DELIBERATELY DOES NOT TAKE THE TOKEN. That column is a condemnation with a
#: stated reason — the whole deposit's safety logic keys on it, and §2.6 keeps one of these very
#: designs as the reagent the TAF15 seam carries — so a third value there would either condemn a
#: design the paper recommends or make "non-empty" stop meaning "condemned". The unmeasured state
#: is carried by the columns that would otherwise assert a measurement.
NOT_SCREENED = "not_screened"


def _pairs_a_parent(duplex_bp):
    """True where a recorded duplex through the whole gap reaches the criterion, else the sentinel.

    ⚠ THE THIRD STATE IS NOT `False` AND IS NO LONGER BLANK. No duplex length recorded for a row
    means the mature-parent search did not run on it, which is not the same as a row measured and
    found clean — the distinction this repository has paid for more than once.
    """
    if duplex_bp in (None, ""):
        return NOT_SCREENED
    try:
        return int(duplex_bp) >= MIN_PARENT_DUPLEX_BP
    except (TypeError, ValueError):
        return NOT_SCREENED


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
                # ⛔ NOTHING TO REPORT HERE, AND THE SENTINEL PASS BELOW SAYS SO. These two
                # artifacts hold no `parent_duplex_bp` at all — only `clears_parent_exclusion`,
                # which is the exact-hit screen and a different question — so there is no duplex
                # length to report and no threshold verdict to derive from one. Left blank at this
                # point so a later source may still fill it; `_stamp_the_unmeasured_state` marks
                # whatever is still blank when every source has been read.
                mature_parent_duplex_through_gap_bp="", mature_parent_duplex_gene="",
                parent_paired_gap_dna_nt="", parent_seam_hybrid_bp="",
                # ⛔ THIS COLUMN READ A HARD `False` WHERE THE SCREEN WAS NEVER RUN (2026-08-19).
                # It was written as `bool(bad)` — the un-rearranged-allele verdict — so nine
                # cryptic-exon rows with NO mature-parent duplex recorded at all announced that no
                # wild-type parent pairs their gap. §2.6 says the opposite in terms: at these seams
                # "their counts are absent rather than low and must not be read beside the panel's".
                # The header already defines the third state; the column simply was not using it,
                # and one column was carrying two different questions' answers.
                pairs_a_wild_type_parent_through_the_gap="",
                role="intron-2 cryptic-exon seam",
                do_not_order=("DO NOT ORDER — pairs its whole catalytic gap against the patient's "
                              "own un-rearranged NR4A3 allele" if bad else ""),
                clinical_tier="")

    # ⛔ A CONDEMNED DESIGN THAT REACHED NO ROW ABOVE STILL SHIPS. If the screen's shape changes and
    # one of them stops appearing in a junction block, silently dropping it is the failure this
    # manifest exists to prevent — so they are added explicitly, last, and only if still missing.
    # ⛔ AND IT MUST NOT ASSERT THE MATURE-PARENT VERDICT WHILE DOING SO (2026-08-19). This block
    # used to write `pairs_a_wild_type_parent_through_the_gap=True`, which filled the blank left by
    # the intron-2 block on `TGATGAGGGCCTTGTG` — the ONE row in the file with a blank duplex cell, a
    # `True` liability flag and a non-empty `do_not_order`. That `True` was not a measurement. The
    # screen behind this block is stated in its own artifact as an "exhaustive <=2-mismatch scan of
    # the NR4A3 UNSPLICED sequence", and the same artifact says in terms that "a clean parent screen
    # is not an answer" because "that screen searches MATURE cDNA only" — a different compartment,
    # a different instrument. So the row announced a mature-parent duplex at ten base pairs that no
    # search had ever looked for. A populated field is not a measured one; the condemnation is real
    # and stays, and the mature-parent columns say they were not screened.
    for seq in sorted(condemned):
        add(sequence=seq, junction="", geometry="5-6-5", gap_level_margin="",
            mature_parent_duplex_through_gap_bp="", mature_parent_duplex_gene="",
            parent_paired_gap_dna_nt="", parent_seam_hybrid_bp="",
            pairs_a_wild_type_parent_through_the_gap="", role="condemned design",
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

    _stamp_the_unmeasured_state(rows)
    # ⚠ BEFORE the twin pass: that pass partitions on `do_not_order`, so a row condemned here must
    # already carry its verdict or it would be offered as the clean member of a near-identical pair.
    _stamp_the_premrna_liability(rows)
    _mark_the_near_identical_twins(rows)
    rows.sort(key=lambda r: (r["junction"], -(r["length_nt"]), r["sequence"]))
    return rows


def _mark_the_near_identical_twins(rows):
    """Name, on every row, the nearest design of the OPPOSITE verdict — measured, not asserted.

    ⛔⛔ THE HAZARD THIS FILE WAS BUILT FOR HAS A SECOND HALF, AND ONLY THE FIRST WAS COVERED. The
    module docstring already records that two condemned designs are one- and two-position register
    shifts of a reagent the paper recommends, sharing 15 of 16 bases. Measured across the whole
    file rather than at the lead seam, that is not a curiosity: 21 clean/condemned pairs differ by
    at most two substitutions at the same length, and 141 more are a single-base slide of one
    another, so 136 of the clean designs sit one slid register away from a design the paper
    condemns. A reader who transcribes a sequence by eye, or who slides a register while tiling
    their own, lands on the opposite verdict without anything in either carrier telling them the
    neighbour exists. A verdict beside the sequence answers "is THIS one safe"; it does not answer
    "what is one keystroke away", and for a 16-mer read off a page those are the same question.
    ⚠ AN EMPTY CELL HERE IS A COMPUTED NEGATIVE, NOT AN ABSENT READING. The comparison runs for
    every row against every condemned or clean row of the same length, so blank means no neighbour
    of the opposite verdict was found within one slide or two substitutions — which the header says
    in terms, because this file has already been burned once by a blank that meant two things.
    """
    condemned = sorted(r["sequence"] for r in rows if r["do_not_order"])
    clean = sorted(r["sequence"] for r in rows if not r["do_not_order"])
    for row in rows:
        seq = row["sequence"]
        others = clean if row["do_not_order"] else condemned
        best = None
        for other in others:
            if len(other) != len(seq) or other == seq:
                continue
            distance = sum(1 for a, b in zip(seq, other) if a != b)
            if distance <= 2:
                rank, how = distance, f"{distance} substitution{'s' if distance > 1 else ''}"
            elif seq[1:] == other[:-1] or seq[:-1] == other[1:]:
                rank, how = 3, "a single-base slide"
            else:
                continue
            if best is None or (rank, other) < best[:2]:
                best = (rank, other, how)
        row["near_identical_design_with_a_different_verdict"] = (
            f"{best[1]} ({best[2]}; {'orderable' if row['do_not_order'] else 'DO NOT ORDER'})"
            if best else "")


#: The columns that would otherwise assert a mature-parent reading the row does not have.
_UNMEASURED_COLUMNS = ("mature_parent_duplex_through_gap_bp", "mature_parent_duplex_gene",
                       "pairs_a_wild_type_parent_through_the_gap")


def _stamp_the_unmeasured_state(rows):
    """Mark every row the mature-parent duplex search never ran on, ONCE, after every source.

    ⛔ ONE PLACE, AND AFTER THE MERGE, NOT INSIDE A SOURCE BLOCK. A source cannot know whether a
    later block will supply the measurement — `add()` fills blanks precisely so it can — so a
    sentinel written at read time would either lose a real value or collide with one (the
    un-rearranged-allele fallback names two designs the non-canonical-acceptor screen HAS measured
    at 8 bp, and stamping there raised on the conflict). Blank at the end of the merge is the only
    honest test of "never measured", and it is applied to the duplex length, the gene it names and
    the threshold verdict together, so no reader can meet one of the three in isolation.
    """
    for row in rows:
        if row.get("mature_parent_duplex_through_gap_bp") in ("", None):
            for column in _UNMEASURED_COLUMNS:
                row[column] = NOT_SCREENED


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
#: ⛔⛔ `do_not_order` IS COLUMN 2 AND THAT IS AN ORDER-SAFETY PROPERTY, NOT A PREFERENCE
#: (2026-08-19). It shipped as column 14 of 14, under a header block whose own instruction is
#: "READ do_not_order FIRST" — and 14 columns is past the right edge of a default spreadsheet
#: window, so the one cell that says do not order this was the one cell a reader had to scroll to
#: find. The verdict now sits immediately beside the sequence it condemns, which is the only
#: arrangement in which reading the sequence and reading the verdict are the same act. Every
#: consumer in this repository reads this file with `csv.DictReader` and joins by header NAME, not
#: by position — checked across `test_every_ordering_route_carries_the_same_verdict.py`,
#: `test_aso_sequence_manifest_joins.py` and `test_pdf_text_layer_is_orderable.py` — so the move
#: costs them nothing.
_FIELDS = ("sequence", "do_not_order", "near_identical_design_with_a_different_verdict",
           "length_nt", "geometry", "junction",
           "also_tiled_at_junctions", "gap_level_margin",
           "mature_parent_duplex_through_gap_bp", "mature_parent_duplex_gene",
           "parent_paired_gap_dna_nt", "parent_seam_hybrid_bp",
           "pairs_a_wild_type_parent_through_the_gap", "role", "clinical_tier")

#: ⛔⛔ THE COLUMN HEADER IS LINE 1 AND THE PROSE FOLLOWS IT, NOT THE OTHER WAY ROUND (2026-08-19).
#: This file shipped with 55 comment lines ahead of the column header, and MEASURED with pandas
#: 3.0.5 a default `pandas.read_csv(path)` did not return a wrong frame — it RAISED:
#:
#:     ParserError: Error tokenizing data. C error: Expected 1 fields in line 5, saw 2
#:
#: because line 1 carries no comma, so one field was inferred for the whole file, and line 5 does.
#: Excel put the real header on row 56. A canonical machine-readable record that the two commonest
#: readers cannot open is not canonical, and the reader who then falls back to copying sequences
#: out of the PDF is doing the exact thing this file exists to prevent.
#: ⭐ THE FIX KEEPS THE BLOCK. The header row goes first, so both readers get the right columns; the
#: prose follows as `#` lines, which pandas pads out to the full width instead of rejecting, and
#: which `pandas.read_csv(path, comment='#')` drops entirely for the clean 780-row frame. The
#: order-safety banner still precedes the first sequence in the file, which is the property that
#: matters. ⚠ ONE INVARIANT MAKES IT WORK: a comment line must never parse to MORE fields than the
#: table has, or the C parser raises on it — enforced below rather than trusted, because the failure
#: is a raise at a reader's terminal and not a wrong value we could see here.


def _paper():
    """Title, author, preprint status and the archive DOI, read from the manuscript.

    ⛔ NEVER TYPED HERE, AND THE DOI IS NEVER INVENTED. A plausible-looking DOI in a file a
    laboratory orders from would be worse than none, because it would resolve to somebody else's
    record or to nothing at all. So it is read out of the manuscript, character for character,
    whatever it says.

    ⚠ AND WHAT IT SAYS CHANGED (2026-08-20). Until the deposition was created there was no reserved
    identifier and the manuscript carried a bracketed `[ARCHIVE DOI — PLACEHOLDER …]` block; this
    function matched that block specifically, so the moment the real DOI replaced it the generator
    stopped with "the archive-DOI placeholder could not be read". That is the right failure — it
    refused to carry a stale string — but the pattern now has to admit both, because a deposit that
    has an identifier and a deposit that does not are both states this file must be able to
    describe, and a future paper will start in the second one.
    """
    path = os.path.join(ASO, "fusion-junction-aso-research-article.md")
    text = open(path, encoding="utf-8").read()
    flat = " ".join(text.split())
    front = text.split("---", 2)[1] if text.startswith("---") else ""

    def one(pattern, where, what):
        m = re.search(pattern, where, re.M)
        if not m:
            raise RuntimeError(
                f"{what} could not be read out of fusion-junction-aso-research-article.md — the "
                "carriers must not state it from memory, so the generator stops here")
        return " ".join(m.group(1).split())

    return {
        "title": one(r'^title:\s*"(.+)"\s*$', front, "the manuscript title"),
        "date": one(r"^date:\s*(\S+)\s*$", front, "the manuscript date"),
        "author": one(r"\*\*Author\.\*\*\s*(.+)", text, "the author"),
        "preprint": one(r"\*\*Preprint status\.\*\*\s*(.+?)(?=\*\*)", flat, "the preprint status"),
        #: Either a reserved DOI as the manuscript links it, or the placeholder block that says
        #: there is none. Whichever is there is copied; neither is completed or corrected here.
        "doi": one(r"\*\*Data and code availability\.\*\*[^.]*?"
                   r"(\[(?:ARCHIVE DOI[^\]]*|doi:10\.\d{4,9}/[^\]]+)\])", flat,
                   "the archive DOI, or the placeholder block standing in for it"),
        "repo": one(r"(github\.com/[\w.-]+/[\w.-]+)", flat, "the repository URL"),
    }


def _chemistry_sentences():
    """The linkage specification, lifted from §6 of the manuscript rather than re-derived.

    ⛔ THE CSV USED TO CONTRADICT §6 OUTRIGHT. Its header said NUCLEOBASE MODIFICATION IS NOT
    SPECIFIED BY THIS DEPOSIT and that whether the locked cytosines are 5-methylcytosine is a vendor
    default; §6 says the opposite in terms — locked cytosines ARE 5-methylcytosine and the gap
    cytosines are unmethylated 2'-deoxycytidine, specified precisely so that two suppliers filling
    the same base string do not ship two molecules. The carrier a vendor quotes from was the one
    telling them to choose. Reading the sentences out of the manuscript is what keeps the two from
    diverging again.
    """
    text = open(os.path.join(ASO, "fusion-junction-aso-research-article.md"),
                encoding="utf-8").read()
    sentences = re.split(r"(?<=[.]) (?=[A-Z0-9(])", " ".join(text.split()))
    out = {}
    for key, anchor in (("linkages", "internucleoside linkages"),
                        ("bicycle", "The bicycle is named"),
                        ("nucleobases", "5-methylcytosine"),
                        ("termini", "free 5′-hydroxyl")):
        hits = [s for s in sentences if anchor in s]
        if len(hits) != 1:
            raise RuntimeError(
                f"§6's chemistry sentence for {key!r} (anchor {anchor!r}) matched {len(hits)} "
                "sentences, not 1 — the carriers must not state the chemistry from memory")
        out[key] = hits[0]
    return out


def _wrap(prefix, text, width=98):
    """One paragraph as comment lines, at a width a terminal and a spreadsheet cell both survive."""
    return [prefix + line for line in textwrap.wrap(text, width=width - len(prefix)) or [""]]


def _notes(rows, carrier="csv"):
    """The header block, with every number DERIVED from the artifacts and the rows themselves.

    ⚠ ONE BLOCK, TWO CARRIERS, AND ONLY THE MECHANICS DIFFER. A reader receives the CSV or the
    FASTA, not both, so every statement of substance is rendered into each. What is carrier-specific
    is only where the verdict physically sits and how the file is opened — and getting THAT wrong
    in the other carrier ("column 2" in a file with no columns) would teach a reader that the block
    was written for somebody else and can be skimmed.

    ⛔ NOT ONE FIGURE IN THIS BLOCK IS TYPED. The block previously said the margin rule returns a
    condemned design at eight of the 40 junctions this file keys a row to. Recomputed here: the file
    keys a row to 43 distinct junctions, 42 of which carry a 5-6-5 register, and it is over those 42
    that the rule returns a condemned design at 8 — so the denominator was wrong and the numerator
    was right, which is the shape of error a reader cannot catch. It also said 181 designs pair a
    parent at ANY length; 181 is the count at SIX base pairs, the shortest cut on the ladder in
    `aso-parent-null.json`, and that artifact records no any-length figure at all.
    """
    paper, chem = _paper(), _chemistry_sentences()
    null = _load("aso-parent-null.json")
    ladder = null["cut_sensitivity"]["observed_cut_ladder"]
    cuts = sorted(int(c) for c in ladder)
    shortest, loose = str(cuts[0]), "7"
    n_designs = null["observed"]["n_designs"]
    criterion = MIN_PARENT_DUPLEX_BP

    keyed = sorted({r["junction"] for r in rows if r["junction"]})
    panel_junctions = sorted({r["junction"] for r in rows
                              if r["junction"] and r["geometry"] == "5-6-5"})
    condemned = [r for r in rows if r["do_not_order"]]
    allele = [r for r in condemned if "un-rearranged" in r["do_not_order"]]
    twins = [r for r in rows if r["near_identical_design_with_a_different_verdict"]]
    n_twins = len(twins)
    n_twin_pairs = sum(1 for r in twins
                       if "substitution" in r["near_identical_design_with_a_different_verdict"]
                       and not r["do_not_order"])
    n_twin_slides = sum(1 for r in twins
                        if "slide" in r["near_identical_design_with_a_different_verdict"]
                        and not r["do_not_order"])
    unmeasured = [r for r in rows
                  if r["pairs_a_wild_type_parent_through_the_gap"] == NOT_SCREENED]
    spanning = [r for r in rows if r["also_tiled_at_junctions"]]
    spanning_565 = [r for r in spanning if r["geometry"] == "5-6-5"]
    # ⛔ 190 AND 176 ARE THE PANEL'S, NOT THIS FILE'S, AND BOTH ARE READ RATHER THAN TYPED. This
    # file holds more 5-6-5 rows than the panel does, because the non-canonical-acceptor and
    # cryptic-exon seams are 5-6-5 too; quoting the panel's counts off this file's row count would
    # be a third denominator nobody asked for.
    series = (_load("offtarget-chance-baseline.json") or {}).get(
        "figure_series", {}).get("series", [])
    n_molecules = len(series)
    n_multi = sum(1 for s in series if len(s.get("junctions") or []) > 1)
    linkages = {}
    for r in rows:
        linkages.setdefault(r["length_nt"], 0)
        linkages[r["length_nt"]] += 1
    linkage_note = "; ".join(f"{n}-mer {n - 1} linkages ({linkages[n]} records)"
                             for n in sorted(linkages))
    by_margin_condemned, by_margin_recoverable = 0, 0
    for junction in panel_junctions:
        group = [r for r in rows if r["junction"] == junction and r["geometry"] == "5-6-5"
                 and str(r["gap_level_margin"]) != ""]
        if not group:
            continue
        top = max(group, key=lambda r: (int(r["gap_level_margin"]), r["sequence"]))
        if top["do_not_order"]:
            by_margin_condemned += 1
            if any(not r["do_not_order"] for r in group):
                by_margin_recoverable += 1

    lines = []

    def para(*text, prefix="# "):
        lines.extend(_wrap(prefix, " ".join(text)))

    def gap():
        lines.append("#")

    para("Fusion-junction ASO designs — the CANONICAL machine-readable record of every sequence "
         "this deposit names. Generated by research/manuscripts/aso_sequence_manifest.py from the "
         "same artifacts the submission tables are built from. Do not edit by hand. Encoding is "
         "UTF-8.")
    gap()
    where = ("in COLUMN 2, beside the sequence it condemns"
             if carrier == "csv" else "on the defline, tagged DO NOT ORDER")
    parent_paired = [r for r in condemned if "wild-type parent gene" in r["do_not_order"]]
    premrna = [r for r in condemned if "parent precursor RNA" in r["do_not_order"]]
    assert len(parent_paired) + len(premrna) + len(allele) == len(condemned), (
        "the three condemnation classes must partition the condemned set — a row carrying none of "
        "them would vanish from this banner without changing its total")
    para(f"⛔ ORDER SAFETY. READ THE do_not_order VERDICT — {where} — BEFORE ORDERING ANY SEQUENCE "
         "IN THIS FILE. A verdict means the paper names that design as one NOT to be carried "
         f"forward. {len(condemned)} of the {len(rows)} records carry one: "
         # ⛔ COUNT EACH CLASS, NEVER DERIVE ONE BY SUBTRACTION. This read
         # `len(condemned) - len(allele)`, which was right while there were exactly two classes and
         # silently absorbed the five pre-mRNA rows into the mature-parent count the moment a third
         # arrived — attributing to "pairs a wild-type parent at the criterion" five rows whose own
         # column reads False at 7, 7, 7, 7 and 9 bp. A banner that misdescribes a verdict is worse
         # than one that omits it, and this is the file the Declarations route a laboratory to.
         f"{len(parent_paired)} pair their whole catalytic gap against a wild-type parent "
         f"gene at the criterion below, {len(premrna)} carry a sense-strand near-match in parent "
         "precursor RNA that pairs the gap in full and touches intronic sequence, "
         f"and {len(allele)} pair the patient's own un-rearranged "
         "NR4A3 allele at a non-canonical acceptor.")
    gap()
    para("⛔ AND CHECK THE NEIGHBOUR BEFORE YOU ORDER. "
         "near_identical_design_with_a_different_verdict names, for each record, the closest design "
         "in this file that carries the OPPOSITE verdict — within two substitutions at the same "
         f"length, or one base slid. {n_twins} of the {len(rows)} records have one, and on "
         f"{n_twin_pairs + n_twin_slides} of them the record itself is orderable while its "
         f"neighbour is condemned — {n_twin_pairs} within two substitutions and {n_twin_slides} a "
         "single base slid. A transcription error of one base can therefore carry a reader from a "
         "design the paper keeps to one it condemns. An EMPTY cell here is a computed negative — "
         "the comparison ran and found no such neighbour — not a missing reading.")
    gap()
    para("RESEARCH USE ONLY. NOT FOR ADMINISTRATION TO ANY PERSON OR ANIMAL. None of these is a "
         "medicine or a candidate drug. None has been synthesised or tested by anyone. No efficacy "
         "and no safety result is reported for any sequence here.")
    gap()
    if carrier == "csv":
        para("HOW TO READ THIS FILE. The column header is line 1, so pandas.read_csv(path) and a "
             "spreadsheet import both find the columns without options. These # lines are prose; "
             "pandas.read_csv(path, comment='#') drops them and returns the "
             f"{len(rows)} data rows alone. Join by column NAME — the column order is not an "
             "interface and has changed once already, to put the verdict beside the sequence.")
    else:
        para("HOW TO READ THIS FILE. These ; lines are FASTA comments and every common parser "
             f"skips them. {len(rows)} records follow, each a defline and one sequence line, and "
             "the defline carries the same fields the CSV beside this file carries as columns. The "
             "two are generated together from the same rows and cannot disagree.")
    gap()
    para("THE PAPER. " + paper["title"])
    para("Author: " + paper["author"] + ". Manuscript date " + paper["date"] +
         " (front matter of fusion-junction-aso-research-article.md).", prefix="#   ")
    para(paper["preprint"], prefix="#   ")
    para("Archive: " + paper["doi"], prefix="#   ")
    para("Repository: " + paper["repo"] + ". Version: this file is regenerated from the "
         "repository and carries no separate version of its own; the archived version has not been "
         "deposited, as the line above says.", prefix="#   ")
    gap()
    para("CHEMISTRY — THE FULL SPECIFICATION, FROM SECTION 6 OF THE MANUSCRIPT. Ordering the bases "
         "without these modifications gives a DIFFERENT MOLECULE about which nothing in the paper "
         "is true. Sequences are written 5' to 3' as the ANTISENSE strand.")
    para("Architecture: the geometry column gives the gapmer per record. 5-6-5 is a five-nucleotide "
         "locked wing, a six-nucleotide DNA gap and a five-nucleotide locked wing; 5-8-5 and 5-10-5 "
         "are the same wings around gaps of eight and ten.", prefix="#   ")
    # ⛔ THE COUNT COMES BEFORE THE QUOTE, BECAUSE §6's COUNT IS THE 16-MER's AND MOST OF THIS FILE
    # IS NOT A 16-MER. Quoting "every one of the 15 internucleoside linkages" first and correcting
    # it after would leave the wrong number as the last thing a hurried reader saw, on 574 of the
    # 780 records.
    para("Linkages: every internucleoside linkage is a phosphorothioate, and the count is the "
         "record's own length minus one — " + linkage_note + ".", prefix="#   ")
    para("Section 6 states it for the 16-mer: " + chem["linkages"], prefix="#     ")
    para("Bicycle: β-D-oxy-LNA. " + chem["bicycle"], prefix="#   ")
    para("Nucleobases: " + chem["nucleobases"], prefix="#   ")
    para("Termini and salt: " + chem["termini"], prefix="#   ")
    para("Not modelled: the free energies in the paper are computed for an unmodified DNA:RNA "
         "hybrid, and backbone stereochemistry is not modelled anywhere in this work.",
         prefix="#   ")
    gap()
    para("⛔ THREE PARENT-DUPLEX COLUMNS, AND THEY ARE NOT INTERCHANGEABLE. Join on the right one:")
    para("mature_parent_duplex_through_gap_bp — a SEARCH over all six mature parent transcripts for "
         "a duplex spanning this design's whole catalytic gap, with the gene it found in "
         "mature_parent_duplex_gene. 0 means the search found none. ⭐ This is the quantity the "
         "paper's tables print under 'longest mature-parent duplex through the gap'.", prefix="#   ")
    para("parent_paired_gap_dna_nt — ARITHMETIC on the design's OWN seam: gap nucleotides one of "
         "its own two parents pairs by construction. Not a search result.", prefix="#   ")
    para("parent_seam_hybrid_bp — that run plus the LNA wing beside it.", prefix="#   ")
    para("For the lead 16-mer the first and third both read 8, from DIFFERENT genes, so a wrong "
         "join looks right on that design; they separate elsewhere. A blank in the last two means "
         "the source artifact for that row does not compute the quantity — not that it is zero.")
    gap()
    para("⛔ THREE STATES, NOT TWO, AND EVERY ONE OF THEM IS VISIBLE:")
    para(f"CONDEMNED — do_not_order carries a reason and "
         f"pairs_a_wild_type_parent_through_the_gap reads True, or another screen condemned the "
         f"row. {len(condemned)} records.", prefix="#   ")
    para(f"MEASURED AND UNDER THE CRITERION — do_not_order is empty and "
         f"pairs_a_wild_type_parent_through_the_gap reads False, from a duplex length in "
         f"mature_parent_duplex_through_gap_bp. ⚠ THAT IS A READING AT ONE CUT, {criterion} base "
         f"pairs, AND NOT A CLEARANCE: of the {n_designs} panel designs "
         f"{ladder[loose]['n_liable']} pair a parent through the whole gap at {loose} base pairs "
         f"and {ladder[shortest]['n_liable']} do so at {shortest}, the shortest cut measured in "
         "research/modalities/aso-parent-null.json. Nothing here is a reading at any other cut.",
         prefix="#   ")
    # ⛔ THE CLASS IS NOT UNIFORM IN ITS VERDICT AND SAYING SO IS THE POINT. All of these rows are
    # unscreened by the MATURE-PARENT search, but one of them is condemned by a DIFFERENT screen
    # (the un-rearranged-allele scan), so a reader who reads "not screened" as "no verdict" is
    # wrong about exactly one row -- and it is the row that must not be ordered. Both counts are
    # derived here rather than typed, so the sentence cannot go stale if the class changes size.
    _ns_condemned = [r for r in unmeasured if r.get("do_not_order", "").strip()]
    para(f"NOT SCREENED — the three mature-parent columns all read {NOT_SCREENED}. "
         f"{len(unmeasured)} records, at the two NR4A3 intron-2 cryptic-exon seams, whose source "
         "artifacts hold no parent-duplex length at all. The search never ran on them, so there is "
         "no reading to be under or over the criterion. ⚠ THAT IS NOT THE SAME AS NO VERDICT: "
         f"{len(_ns_condemned)} of these {len(unmeasured)} carries a do_not_order set by another "
         "screen, and the remaining "
         f"{len(unmeasured) - len(_ns_condemned)} carry none. An empty do_not_order on such a row "
         "means only that no OTHER screen condemned it, and never that this one cleared it.",
         prefix="#   ")
    gap()
    para("`role` IS THE SELECTION COLUMN. `best available at this junction` marks the design the "
         "paper itself carries there. Ranking on gap_level_margin is NOT the paper's rule: this "
         f"file keys a row to {len(keyed)} distinct junctions, {len(panel_junctions)} of them carry "
         f"a 5-6-5 register, and over those {len(panel_junctions)} the rule returns a do_not_order "
         f"design at {by_margin_condemned} — at {by_margin_recoverable} of which a clean register "
         "was available and the rule did not pick it.")
    gap()
    para("⛔ EXON NUMBERS IN `junction` ARE TRANSCRIPT EXON INDICES, NOT CODING-EXON INDICES — "
         "counted from the transcript 5' end, including non-coding exons. The two conventions "
         "differ for TCF12, TFG and NR4A3, and this is the axis an earlier version of this work was "
         "withdrawn on. Match a breakpoint against these models: ENST00000397938 (EWSR1), "
         "ENST00000605844 (TAF15), ENST00000333725 (TCF12), ENST00000254108 (FUS), "
         "ENST00000240851 (TFG), ENST00000395097 (NR4A3), ENST00000325455 (PGR).")
    gap()
    para("`clinical_tier` grades whether a patient breakpoint is reported at that exon pair: "
         "published_exon_resolved_breakpoint, partner_published_this_exon_not_reported, or "
         "no_published_exon_resolved_breakpoint. It is written for the 16-mer panel and the "
         "non-canonical seams only; a blank means the row's source does not grade it, not that no "
         "breakpoint is published.")
    gap()
    para("`junction` IS ONE JUNCTION, NOT ALL OF THEM. Establish the target breakpoint by RNA "
         f"sequencing before ordering. {len(spanning)} records here span more than one junction and "
         f"each still has ONE row: {len(spanning_565)} of them are 16-mers, which is why the "
         f"{n_designs} design records of the 5-6-5 panel are {n_molecules} distinct molecules "
         f"({n_multi} molecules tiled at more than one junction account for the "
         f"{n_designs - n_molecules} extra records). `also_tiled_at_junctions` carries the other "
         "junctions; search both columns before concluding that a junction has no reagent.")
    return lines


def _as_comment_rows(lines, width):
    """Comment lines, checked to be safe in a CSV a default reader opens.

    ⛔ THE CHECK IS THE POINT. A comment line that parses to MORE fields than the table has makes
    pandas raise on the whole file, which is the failure this layout was built to remove; and a
    double quote at a field boundary changes what the parser thinks a field is. Both are cheap to
    prove here and expensive to discover at a reader's terminal, so neither is trusted.
    """
    out = []
    for line in lines:
        safe = line.replace('"', "'")
        n = len(next(csv.reader([safe])))
        if n > width:
            raise RuntimeError(
                f"header line parses to {n} CSV fields, more than the table's {width}, so a "
                f"default pandas.read_csv would raise on it: {line[:80]!r}")
        out.append(safe)
    return out


def _csv_text(rows):
    """The CSV, with the COLUMN HEADER FIRST so a default reader opens it. See the note above."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_FIELDS, lineterminator="\n")
    w.writeheader()
    for line in _as_comment_rows(_notes(rows), len(_FIELDS)):
        buf.write(line + "\n")
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
    #: ⛔ AND IT CARRIED A DIFFERENT, SHORTER STORY THAN THE CSV UNTIL 2026-08-19. The two carriers
    #: are the same record and a reader receives ONE of them, so a fact that reaches only the CSV
    #: reaches half the readers. Both now render the SAME derived block — the paper's identity, the
    #: full linkage specification from §6, the three states and every count — and the FASTA adds
    #: only what is specific to a defline.
    out = [";" + line[1:] for line in _notes(rows, carrier="fasta")]
    out += [
        "; ⚠ AN UNTAGGED RECORD IS NOT A CLEARANCE. A record tagged DO NOT ORDER carries the",
        "; reason on its defline; a record with no tag was either measured under the criterion at",
        f"; that one cut or, where its defline reads parent_duplex={NOT_SCREENED}, never measured at",
        "; all. Neither is a clearance.",
        "; role=best-available names the design the paper itself carries at that junction. Ranking",
        "; these records by gap_level_margin is NOT the paper's selection rule and returns a tagged",
        "; design at several junctions.",
        "; Each defline reads: sequence, then geometry, junction, any further junctions the same",
        "; molecule is tiled at, gap_level_margin, role, clinical_tier, the mature-parent duplex,",
        "; and the do-not-order verdict where there is one.",
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
        #: ⛔ THE UNMEASURED STATE HAS TO REACH THE DEFLINE TOO, AND NOT AS A NUMBER. Rendering the
        #: sentinel through the numeric branch would have produced `parent_duplex=not_screenedbp
        #: (not_screened)`, which reads as a malformed measurement rather than as the absence of
        #: one; and dropping the tag would have made an unscreened record look exactly like a
        #: record whose search returned nothing.
        duplex = r.get("mature_parent_duplex_through_gap_bp")
        if duplex == NOT_SCREENED:
            tags.append(f"parent_duplex={NOT_SCREENED} — the mature-parent search did not run at "
                        "this seam, so this is NOT a clearance")
        elif duplex not in ("", None):
            gene = r.get("mature_parent_duplex_gene") or "unnamed"
            tags.append(f"parent_duplex={duplex}bp ({gene})")
        if r.get("do_not_order"):
            tags.append(r["do_not_order"])
        #: ⛔ THE NEIGHBOUR TRAVELS ON THE DEFLINE TOO. A FASTA record is the form most likely to be
        #: pasted straight into an order form, and a reader who pastes one base wrong has ordered
        #: the neighbour. Naming it here is the only warning that arrives with the bases.
        if r.get("near_identical_design_with_a_different_verdict"):
            tags.append("⚠ near-identical design with the opposite verdict: "
                        + r["near_identical_design_with_a_different_verdict"])
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
