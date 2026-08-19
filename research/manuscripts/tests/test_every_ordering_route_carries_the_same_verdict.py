#!/usr/bin/env python3
"""Every route a reader can take to a sequence must reach the same do-not-order verdict.

⛔⛔ WHY THIS EXISTS — THE SAME DEFECT, THREE TIMES, IN THREE DIFFERENT CARRIERS.

  2026-08-18  §2.4, §2.7 and §4.4 each named "the three" *TCF12* exon-7 designs and meant three
              different sets. A laboratory ordering from §2.4's list got a design §2.7 excludes for
              an eleven-base-pair duplex with wild-type *TCF12*.
  2026-08-19  Table 3's do-not-order key never reached the manuscript build at all, because the
              manuscript style never calls `render_float`.
  2026-08-19  (this file) A blind order-walkthrough followed the ONE selection rule the paper
              states for its canonical CSV — rank by gap-level margin — and at five of the 36 panel
              junctions it returned a design that pairs a wild-type parent through the whole
              catalytic gap at eleven base pairs, four of them against wild-type *NR4A3*. Table 3
              marks every one of those ⚑ "do not order". The CSV carried `do_not_order` on 3 of 780
              rows, and 83 rows flagged as pairing a parent carried nothing. In the same pass Table
              4 was found printing five ⚑ designs with no marker and a final column reading "yes".

★ THE PATTERN, WHICH IS WHY THIS IS A TEST AND NOT THREE FIXES. Each carrier was individually
correct: Table 3 marked its rows, §2.6 named its three, the CSV held a `role` column with the right
answer in it. The hazard is never inside one carrier — it is that a reader takes ONE route, and the
routes disagreed about which molecules must not be ordered. So the assertion is agreement across
routes, not correctness within one.

⚠ WHAT "DO NOT ORDER" MEANS HERE IS A THRESHOLD VERDICT, NOT A CLEARANCE. The flag is set at ten
base pairs; 175 of 190 panel designs pair a parent through the whole gap at seven and 181 at any
length. Every carrier must therefore say that an unflagged row is a reading at one cut — asserted
below — because a reader who takes absence of a flag for safety has been misled by a true statement.
"""
from __future__ import annotations

import csv
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
CSV_PATH = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
FASTA = os.path.join(ASO, "fusion-junction-aso-sequences.fasta")
TABLES = os.path.join(ASO, "fusion-junction-aso-submission-tables.md")
PAPER = os.path.join(ASO, "fusion-junction-aso-research-article.md")

#: The criterion the paper is stated on.
MIN_PARENT_DUPLEX_BP = 10


def _need(path):
    """⛔ NOT A SKIP. Every path this file reads is a COMMITTED artifact (2026-08-19, lane C2).

    `git ls-files research/manuscripts/aso/` carries the canonical CSV, the FASTA, the tables file,
    the article and the built PDF. So an absence here is a broken tree, never a partial checkout —
    and a skip on a broken tree is the exact shape of the pypdf/pymupdf defect this suite was just
    audited for: the whole cross-carrier agreement check evaporating with its input while the run
    reports green. Fail, and name the file.
    """
    if not os.path.exists(path):
        pytest.fail(
            f"{os.path.basename(path)} is missing at {path}. It is a committed artifact, so its "
            "absence is a broken tree and not a reason to stop checking that every ordering route "
            "reaches the same verdict — restore or regenerate it.")
    return path


def _csv_rows():
    lines = [l for l in open(_need(CSV_PATH), encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines))


def test_every_parent_pairing_row_of_the_canonical_record_says_do_not_order():
    """⛔ 83 rows were flagged as pairing a wild-type parent and told a reader nothing."""
    rows = _csv_rows()
    flagged = [r for r in rows if r["pairs_a_wild_type_parent_through_the_gap"] == "True"]
    assert flagged, "no row pairs a wild-type parent — the column has stopped being computed"
    silent = [r["sequence"] for r in flagged if not r["do_not_order"]]
    assert not silent, (
        f"{len(silent)} rows pair a wild-type parent through the whole gap and carry no "
        f"`do_not_order`: {silent[:6]}. The paper tells a reader to order from this file INSTEAD "
        "of the PDF, so a verdict that lives only in Table 3 does not reach them.")


def test_the_selection_rule_the_paper_states_does_not_return_a_condemned_design():
    """★ THE WALKTHROUGH ITSELF, kept as a test rather than as a paragraph in a report.

    Rank the panel by the one rule the paper states — gap-level margin — and check what comes back.
    This is allowed to return a condemned design; what is NOT allowed is for the file to be silent
    about it, so the assertion is that every such design carries its verdict.
    """
    rows = [r for r in _csv_rows() if r["geometry"] == "5-6-5"
            and r["role"] in ("screened design", "best available at this junction")]
    by_junction: dict[str, list[dict]] = {}
    for r in rows:
        by_junction.setdefault(r["junction"], []).append(r)
    assert len(by_junction) >= 30, len(by_junction)
    unguarded = []
    for junction, group in by_junction.items():
        top = max(group, key=lambda r: (int(r["gap_level_margin"]), r["sequence"]))
        if top["pairs_a_wild_type_parent_through_the_gap"] == "True" and not top["do_not_order"]:
            unguarded.append((junction, top["sequence"]))
    assert not unguarded, (
        f"ranking by gap-level margin returns an unflagged parent-pairing design at {unguarded}")


def test_the_canonical_record_says_which_column_to_select_on():
    """The paper's answer lives in `role`, and a reader who does not know that cannot reach it."""
    rows = _csv_rows()
    assert any(r["role"] == "best available at this junction" for r in rows)
    paper = " ".join(open(_need(PAPER), encoding="utf-8").read().split())
    assert "`role` column carries" in paper, (
        "§6 must name the column that encodes the paper's own selection; gap-level margin is the "
        "only rule it states and that rule returns condemned designs")


def test_the_fasta_carries_the_verdict_and_the_role_on_the_defline():
    """A FASTA record is the form most likely to be pasted straight into an order form."""
    text = open(_need(FASTA), encoding="utf-8").read()
    deflines = [l for l in text.splitlines() if l.startswith(">")]
    assert deflines, "the FASTA holds no records"
    csv_by_seq = {r["sequence"]: r for r in _csv_rows()}
    #: ⛔ THE JOIN IS ASSERTED, NOT ASSUMED (2026-08-19). This read `if row is None: continue`, so a
    #: FASTA record with no row in the canonical CSV — a renamed column, a regenerated CSV, a
    #: sequence present in one carrier and not the other — silently left the loop and every
    #: assertion below went unexecuted for it. A record the join cannot reach is the one most likely
    #: to be carrying the wrong verdict, because nothing has checked it against anything.
    unjoined = [line[1:].split()[0] for line in deflines
                if line[1:].split()[0] not in csv_by_seq]
    assert not unjoined, (
        f"{len(unjoined)} FASTA record(s) have no row in the canonical CSV: {unjoined[:6]}. The two "
        "carriers are generated from one source and must join completely; a record in only one of "
        "them cannot be checked for its verdict at all.")
    fasta_seqs = {line[1:].split()[0] for line in deflines}
    missing_row = sorted(set(csv_by_seq) - fasta_seqs)
    assert not missing_row, (
        f"{len(missing_row)} canonical sequence(s) are in the CSV and not in the FASTA: "
        f"{missing_row[:6]}. A reader taking the FASTA route never meets them.")
    missing_tag, missing_role = [], []
    for line in deflines:
        seq = line[1:].split()[0]
        row = csv_by_seq[seq]
        if row["do_not_order"] and "DO NOT ORDER" not in line:
            missing_tag.append(seq)
        if row["role"] and "role=" not in line:
            missing_role.append(seq)
    assert not missing_tag, f"deflines without the do-not-order tag: {missing_tag[:6]}"
    assert not missing_role, f"deflines without `role`: {missing_role[:6]}"
    assert "AN UNTAGGED RECORD IS NOT A CLEARANCE" in text, (
        "the FASTA header must say that an untagged record is a reading at one threshold")


def _tables():
    return open(_need(TABLES), encoding="utf-8").read()


def _table_span(text, number):
    start = text.find(f"**Table {number}.")
    end = text.find(f"**Table {number + 1}.")
    return text[start:end if end > 0 else len(text)]


@pytest.mark.parametrize("number", [3, 4])
def test_a_table_printing_orderable_designs_marks_the_ones_not_to_order(number):
    """⛔ TABLE 4 IS IN THIS LIST BECAUSE IT FAILED. It printed five ⚑ designs unmarked, under a
    final column reading "yes" — a near-match verdict a reader took for a verdict on the design."""
    span = _table_span(_tables(), number)
    assert span, f"Table {number} is not in the tables file"
    csv_by_seq = {r["sequence"]: r for r in _csv_rows()}
    unmarked, unjoined, seen = [], [], 0
    for line in span.splitlines():
        #: ⛔ THE SEQUENCE IS NOT ALWAYS IN THE FIRST CELL, AND THIS GUARD'S TABLE-3 ARM MATCHED
        #: NOTHING FOR AS LONG AS IT HAS EXISTED (measured 2026-08-19, against HEAD and against the
        #: working tree). The needle was `line.startswith("| 5′-")`; Table 3 prints junction, designs
        #: screened and margin before the sequence, so all 38 of its rows were skipped, `unmarked`
        #: stayed empty, and the parametrised case passed on `assert "⚑" in span` alone — on the very
        #: table this file's own header says the do-not-order key failed to reach. Table 4 puts the
        #: sequence first, so that arm was real and this one was decoration.
        if not line.startswith("|"):
            continue
        for seq in re.findall(r"5[′']-([ACGT]+)-3[′']", line):
            seen += 1
            row = csv_by_seq.get(seq)
            #: ⛔ A PRINTED SEQUENCE THAT DOES NOT JOIN IS THE WORST CASE, NOT AN EXEMPT ONE. This
            #: was `if row and …`, and it also filtered the CSV to 5-6-5 before joining, so a table
            #: row printing an 18-mer or a 20-mer joined to nothing and was passed over in silence —
            #: exactly the reader about to order something no carrier has a verdict for.
            if row is None:
                unjoined.append(seq)
                continue
            if row["pairs_a_wild_type_parent_through_the_gap"] == "True" and "⚑" not in line:
                unmarked.append(seq)
    assert seen, f"Table {number} prints no sequence at all, so this guard asserted nothing"
    assert not unjoined, (
        f"Table {number} prints {len(unjoined)} sequence(s) with no row in the canonical CSV: "
        f"{unjoined[:6]}. Nothing in the deposit carries a verdict for them.")
    assert not unmarked, (
        f"Table {number} prints {len(unmarked)} design(s) that pair a wild-type parent through the "
        f"whole gap with no ⚑: {unmarked}. Every table printing an orderable sequence carries the "
        "same verdict, or a reader who reads only this one is misled.")
    assert "⚑" in span, f"Table {number} lost its do-not-order marker entirely"


def test_no_carrier_lets_an_absent_marker_read_as_a_clearance():
    """The flag is a verdict at ten base pairs, and every carrier has to say so."""
    tables = _tables()
    for number in (3, 4):
        span = _table_span(tables, number)
        assert "not a clearance" in span, (
            f"Table {number}'s notes must state that an unmarked row is a reading at the "
            "ten-base-pair cut and not a clearance")


def test_the_tables_preamble_reaches_the_deposit_pdf():
    """⛔ The block that exists to be checked against was dropped from every build.

    `fusion-junction-aso-submission-tables.md` opens with three things a reader needs before the
    first row: the research-use banner, the chemistry paragraph that defines 5-6-5/5-8-5/5-10-5, and
    a "Do not order these three sequences" block that PRINTS the three condemned designs so a reader
    holding a transcribed sequence has something to check it against. `split_tables` keyed its
    blocks from `^\\*\\*Table N\\.` onward, so all three were discarded: measured 2026-08-19, the
    string "Do not order these three sequences" occurred zero times in the 66-page deposit.

    ⚠ THE CLOSEST PRINTED SEQUENCE SHARES 15 OF 16 BASES with one of the three, which is the whole
    reason that block prints them rather than describing them.

    ⛔⛔ AND UNTIL 2026-08-19 THIS GUARD HAD NEVER RUN ANYWHERE THAT GATES A COMMIT. It read the
    PDF through `pymupdf`, which `.github/workflows/tests.yml` has never installed, so every CI run
    took `pytest.skip("pymupdf is not installed in this sandbox")` and reported green for the check
    that the three condemned sequences reach the deposit. The instrument is now `pdfminer.six`,
    which CI does install, and both the missing parser and the missing PDF are failures — the PDF is
    a committed artifact, so its absence is a broken tree.
    """
    pdf = _need(os.path.join(ASO, "fusion-junction-aso-research-article-manuscript.pdf"))
    try:
        from pdfminer.high_level import extract_text
    except ImportError as exc:  # pragma: no cover - CI installs it; a miss is a finding
        pytest.fail(
            f"pdfminer.six is not importable ({exc}), so nothing read the deposit PDF and the "
            "preamble check asserted nothing. CI installs it; a guard that cannot run is not a "
            "guard that passed.")
    text = " ".join(extract_text(pdf).split())
    source = open(_need(TABLES), encoding="utf-8").read()
    for opener in ("Do not order these three sequences",
                   "Research use only, and not for administration to any person or animal",
                   "what the `geometry` column"):
        flat = opener.replace("`", "")
        assert flat in source.replace("`", ""), (
            f"the tables file no longer opens with {opener!r}; re-anchor this guard")
        assert flat in text, (
            f"{opener!r} is in the tables file and NOT in the built deposit — the preamble is being "
            "dropped again. It carries the three condemned sequences a reader checks a transcription "
            "against, and a reader of the PDF alone would never meet it.")


# ───────────────────────── the verdict, recomputed rather than compared to its own generator
#: The six parent transcripts every screen in this paper searches, and the file the screens
#: themselves read them from. Mature sequence is rebuilt here from the record's exon spans, which is
#: the one step the CSV's own producer also takes — so the two agree on the INPUT and on nothing else.
PREMRNA_SEQS = os.path.join(REPO, "research", "modalities", "aso-premrna-sequences.json")
_COMPLEMENT = str.maketrans("ACGT", "TGCA")


def _mature_parents():
    import json  # noqa: PLC0415

    genes = json.load(open(_need(PREMRNA_SEQS), encoding="utf-8"))["genes"]
    out = {}
    for gene, rec in genes.items():
        spliced = "".join(rec["sequence"][a:b + 1] for a, b in rec["exon_spans_0based_inclusive"])
        assert len(spliced) == rec["exonic_nt"], (
            f"{gene}: the exon spans splice to {len(spliced)} nt against the record's own "
            f"{rec['exonic_nt']}, so the parent transcript this check searches is not the one the "
            "record describes.")
        out[gene] = spliced
    return out


def _longest_parent_duplex_through_the_gap(sequence, geometry, parents):
    """Longest contiguous perfect duplex a mature parent can form that COVERS the whole gap.

    ⛔ WRITTEN OUT HERE ON PURPOSE. The point of this function is that it shares no code with
    `aso_parent_gap_pairing.py`; it takes the design's own bases and the parent transcripts and
    nothing else. It is not a faster version of that module and must never import it.
    """
    wing, gap, _ = (int(x) for x in geometry.split("-"))
    target = sequence.translate(_COMPLEMENT)[::-1]      # the mRNA the antisense oligo hybridises to
    n, lo, hi = len(target), wing, wing + gap
    assert n == wing * 2 + gap, (sequence, geometry)
    core, best = target[lo:hi], (0, None)
    for gene, seq in parents.items():
        at = seq.find(core)
        while at >= 0:
            start = at - lo
            if 0 <= start and start + n <= len(seq):
                left = lo
                while left - 1 >= 0 and seq[start + left - 1] == target[left - 1]:
                    left -= 1
                right = hi - 1
                while right + 1 < n and seq[start + right + 1] == target[right + 1]:
                    right += 1
                if right - left + 1 > best[0]:
                    best = (right - left + 1, gene)
            at = seq.find(core, at + 1)
    return best


def test_the_condemning_column_is_recomputed_from_the_sequence_not_read_off_its_neighbour():
    """⛔⛔ THE GUARD WAS COMPARING TWO OUTPUTS OF ONE EXPRESSION (2026-08-19).

    `test_every_parent_pairing_row_of_the_canonical_record_says_do_not_order` checks
    `pairs_a_wild_type_parent_through_the_gap` against `do_not_order`, and
    `aso_sequence_manifest.py` sets both from the same comparison of the same column against the
    same threshold. Two fields one generator writes from one expression agree by construction: the
    check could not fail while the generator was self-consistent, however wrong the column itself
    was. What nothing recomputed was the QUANTITY the verdict rests on.

    ⚠ THE THRESHOLD IS THE PAPER'S, THE MEASUREMENT IS THIS FILE'S. The duplex length is recomputed
    from the design's own bases against the six mature parent transcripts, and the do-not-order flag
    is asserted against THAT rather than against the neighbouring column — so a generator that
    mis-set the column, the flag, or the comparison between them fails here.
    """
    parents = _mature_parents()
    assert len(parents) >= 6, sorted(parents)
    rows, recomputed = _csv_rows(), 0
    duplex_wrong, flag_wrong, gene_wrong, verdict_wrong = [], [], [], []
    for row in rows:
        printed = row["mature_parent_duplex_through_gap_bp"]
        if not printed.lstrip("-").isdigit():
            continue                       # the third state: no reading at this cut, not a zero
        run, gene = _longest_parent_duplex_through_the_gap(
            row["sequence"], row["geometry"], parents)
        recomputed += 1
        if int(printed) != run:
            duplex_wrong.append((row["sequence"], row["geometry"], printed, run))
        if run and row["mature_parent_duplex_gene"] and gene != row["mature_parent_duplex_gene"]:
            gene_wrong.append((row["sequence"], gene, row["mature_parent_duplex_gene"]))
        liable = run >= MIN_PARENT_DUPLEX_BP
        if (row["pairs_a_wild_type_parent_through_the_gap"] == "True") != liable:
            flag_wrong.append((row["sequence"], run, row["pairs_a_wild_type_parent_through_the_gap"]))
        if liable and not row["do_not_order"]:
            verdict_wrong.append((row["sequence"], run))
    assert recomputed > 700, (
        f"only {recomputed} rows were recomputed; the canonical file has {len(rows)}. A check that "
        "silently stops covering the file is the failure this whole test exists to remove.")
    assert not duplex_wrong, (
        f"{len(duplex_wrong)} row(s) print a parent-duplex length this file cannot reproduce from "
        f"the sequence and the six parent transcripts: {duplex_wrong[:6]} (sequence, geometry, "
        "printed, recomputed).")
    assert not gene_wrong, f"{len(gene_wrong)} row(s) name the wrong parent: {gene_wrong[:6]}"
    assert not flag_wrong, (
        f"{len(flag_wrong)} row(s) carry a parent-pairing flag that disagrees with the duplex this "
        f"file measures at the {MIN_PARENT_DUPLEX_BP} bp criterion: {flag_wrong[:6]}")
    assert not verdict_wrong, (
        f"{len(verdict_wrong)} row(s) reach the {MIN_PARENT_DUPLEX_BP} bp criterion on an "
        f"independent measurement and carry no do-not-order verdict: {verdict_wrong[:6]}")


# ───────────────────────────────── the article body is a carrier too, and nothing was checking it
#: The ways this deposit says "this molecule must not be ordered". A FAMILY, not a sentence: the
#: article condemns a design in prose ("is excluded by an eleven-base-pair duplex with wild-type
#: TCF12", "Neither may be ordered for the other", "puts that register in the do-not-order class"),
#: the tables condemn it with ⚑, and pinning any one wording would make an editorial pass look like
#: a safety regression.
_VERDICT = re.compile(
    r"(⚑"
    r"|do[ -]not[ -]order"
    r"|(?:not|never)\s+(?:to\s+be\s+)?(?:be\s+)?(?:ordered|used|synthesised|made)"
    r"|(?:may|must|should)\s+not\s+be\s+(?:ordered|used|made)"
    r"|neither\s+may\s+be\s+ordered"
    r"|is\s+excluded|are\s+excluded|excluded\s+by"
    r"|pairs?\s+(?:its|their|the)\s+whole\s+catalytic\s+gap"
    r"|pairs?\s+a\s+wild-type\s+parent"
    r"|duplex\s+(?:with|against)\s+wild-type"
    r"|condemn)", re.I)

#: MEASURED over both carriers 2026-08-19, on flattened text: the worst condemned occurrence in the
#: article sits 401 characters from a verdict and the median 46; in the tables file the worst is 154.
#: The CLEAN occurrences are nothing like as close — median 450 in the article and 1,987 in the
#: tables, worst 14,268 and 17,699 — so this bound is a property of the condemned sequences and not
#: of the document's verdict density. 600 is roughly 1.5x the measured worst, about two sentences.
_VERDICT_WINDOW_CHARS = 600

_CARRIERS = {"the article body": lambda: PAPER, "the tables file": lambda: TABLES}


@pytest.mark.parametrize("carrier", sorted(_CARRIERS))
def test_no_carrier_prints_a_condemned_sequence_out_of_reach_of_its_verdict(carrier):
    """⛔ THE PARAMETRISED CARRIER CHECK REACHED THE TABLES AND NOT THE PROSE (2026-08-19).

    Table 3 and Table 4 were checked row by row; the article body prints 26 distinct sequences of
    its own, nine of them condemned, and nothing joined any of them to the canonical file. A reader
    transcribing a 16-mer out of a results paragraph is the same reader the table check exists for.

    ⚠ A PROPERTY, NOT TODAY'S SENTENCES. What is asserted is that a condemned sequence and a verdict
    on it occur within a bounded distance, over a FAMILY of ways of saying so — so the paragraph can
    be rewritten freely and cannot quietly become a paragraph that prints the molecule and not the
    reason.
    """
    text = " ".join(open(_need(_CARRIERS[carrier]()), encoding="utf-8").read().split())
    by_seq = {r["sequence"]: r for r in _csv_rows()}
    verdicts = [m.span() for m in _VERDICT.finditer(text)]
    assert verdicts, f"{carrier} carries no do-not-order vocabulary at all"

    def gap(a, b):
        return 0 if a[0] < b[1] and b[0] < a[1] else (b[0] - a[1] if b[0] >= a[1] else a[0] - b[1])

    printed = [(m.span(), m.group(1))
               for m in re.finditer(r"5[′']-([ACGT]{12,25})-3[′']", text)]
    assert printed, f"{carrier} prints no sequence, so this guard asserted nothing"
    unknown = sorted({s for _, s in printed if s not in by_seq})
    assert not unknown, (
        f"{carrier} prints {len(unknown)} sequence(s) that are not in the canonical file: "
        f"{unknown[:6]}. A sequence no carrier holds a verdict for is the one a reader cannot check.")
    condemned = [(sp, s) for sp, s in printed if by_seq[s]["do_not_order"]]
    assert condemned, (
        f"{carrier} prints no condemned sequence at all. If that is true it is a real change and "
        "this guard has to be re-derived against it, not deleted.")
    stranded = [(s, min(gap(sp, v) for v in verdicts)) for sp, s in condemned
                if min(gap(sp, v) for v in verdicts) > _VERDICT_WINDOW_CHARS]
    assert not stranded, (
        f"{carrier} prints {len(stranded)} condemned sequence(s) with no verdict within "
        f"{_VERDICT_WINDOW_CHARS} characters: {stranded[:6]} (sequence, distance). A reader "
        "transcribing one from here meets the molecule and not the reason it must not be made.")
