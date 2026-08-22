"""⛔⛔ THE GENERATED DISPLAY-ITEM FILE, WHOSE NINE SENTENCES NOTHING SELECTIVE READ.

`claim_coverage.py` measured `fusion-junction-aso-journal-tables.md` at **0 of 9** — the file that
carries BOTH display items into BOTH built PDFs and ships standalone in the archive. Round 14's
BLOCKER lived in it (a caption counting four designs at two seams over a two-row, one-seam table),
and the repair derived that ONE count and left every other sentence a typed literal. Measured
2026-08-22, each of these passed every linter, all 879 tests and both PDF rebuilds:

  * `CONDEMNED` pointed at an ORDERABLE design: Table 2 printed **DO NOT ORDER** against a design
    the canonical file clears, and **orderable** against one it condemns, at two seams, one
    substitution apart — under a caption still reading "one seam", "a single-base slide" and
    "the condemned member pairs its whole catalytic gap … at the ten-base-pair criterion".
  * "Neither may be substituted for the other, and neither is named for synthesis" inverted to
    "Either may be substituted … and one is named for synthesis" — the file's order-safety predicate,
    reversed in both PDFs.
  * Table 1's caption drifted "two reagents"→"three reagents" and "ten"→"eleven-base-pair criterion".
    That IS round 14's blocker, reinstated in the other table's caption.
  * the two test articles swapped between seams (E-N ↔ T-N*), against a repository record that
    quotes both constructs verbatim.
  * the file's own "no sequence may be administered to any person or animal" removed.

★ THE RULE: **a caption is read against the rows it sits over, and a verdict cell is read out of the
canonical file — never typed beside it.** Counts, verdicts, relations, provenance and the scope bound
are all claims about the rows; the round-14 fix bound only the count. Quantity and relation both.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
TABLES = os.path.join(ASO, "fusion-junction-aso-journal-tables.md")
SEQ_CSV = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
#: The engineered constructs of PMID:31020999, each with its exon-numbered junction and the source
#: sentence that names it. This is the artifact the generator's own comment says does not exist.
CONSTRUCTS = os.path.join(REPO, "research", "modalities", "emc-fet-construct-designs.json")

_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
          "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
_NUMBER = {v: k for k, v in _WORDS.items()}


def _need(path, what):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.basename(path)} is missing, so {what} is unchecked. It is a "
                    "committed artifact, so its absence is a broken tree and not a skip.")
    return path


def _plain(text):
    """Emphasis stripped by BALANCED PAIR ONLY.

    ⛔ A BLANKET `re.sub(r"[*`]", "", …)` RENAMES A TEST ARTICLE. The cell reads `T-N*, engineered
    construct`, and the asterisk is part of the construct name — the generator's own comment records
    that T-N and T-N* are different constructs in PMID:31020999. Stripping every asterisk turns one
    into the other, silently, inside the guard meant to check it. (`_flat` in
    `test_named_reagents_carry_the_acceptor_the_csv_gives_them.py` strips exactly that way; it does
    not read this cell today.)
    """
    text = re.sub(r"\s+", " ", text.replace("`", "")).strip()
    for _ in range(4):
        new = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        new = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", new)
        if new == text:
            break
        text = new
    return text


@pytest.fixture(scope="module")
def rows_by_sequence():
    with io.open(_need(SEQ_CSV, "the canonical record"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))
    assert rows, f"{SEQ_CSV} carries no rows"
    return {r["sequence"]: r for r in rows if r["geometry"] == "5-6-5"}


@pytest.fixture(scope="module")
def criterion(rows_by_sequence):
    """The duplex length the do-not-order verdict is set at, DERIVED from the record.

    ⛔ NOT TYPED. `ten` is the number a caption states and round 15's blocker was that nothing read
    it as a word. It is recoverable from the data: the flag partitions the panel exactly, so the
    criterion is one more than the longest duplex that is not flagged.
    """
    yes = [int(r["mature_parent_duplex_through_gap_bp"]) for r in rows_by_sequence.values()
           if r["pairs_a_wild_type_parent_through_the_gap"] == "True"
           and r["mature_parent_duplex_through_gap_bp"].lstrip("-").isdigit()]
    no = [int(r["mature_parent_duplex_through_gap_bp"]) for r in rows_by_sequence.values()
          if r["pairs_a_wild_type_parent_through_the_gap"] == "False"
          and r["mature_parent_duplex_through_gap_bp"].lstrip("-").isdigit()]
    assert yes and no, "the parent-pairing flag no longer partitions the panel"
    assert min(yes) == max(no) + 1, (
        f"the flag does not partition the panel at one length: flagged from {min(yes)} bp, "
        f"unflagged to {max(no)} bp — the criterion is no longer recoverable from the record")
    return min(yes)


@pytest.fixture(scope="module")
def tables():
    """{number: {"caption": str, "header": [...], "rows": [dict]}} from the generated file."""
    text = io.open(_need(TABLES, "the journal display items"), encoding="utf-8").read()
    out = {}
    for chunk in re.split(r"(?m)^(?=\*\*Table \d+\.)", text)[1:]:
        n = int(re.match(r"\*\*Table (\d+)\.", chunk).group(1))
        lines = chunk.splitlines()
        caption = _plain(" ".join(l for l in lines
                                  if l.strip() and not l.lstrip().startswith("|")))
        pipes = [l for l in lines if l.lstrip().startswith("|")]
        assert len(pipes) >= 3, f"Table {n} has no rows"
        header = [c.strip() for c in pipes[0].strip().strip("|").split("|")]
        rows = [dict(zip(header, [_plain(c) for c in l.strip().strip("|").split("|")]))
                for l in pipes[2:]]
        out[n] = {"caption": caption, "header": header, "rows": rows}
    assert out, "the display-item file holds no table at all, so this guard asserted nothing"
    return out


def _sequences(table):
    out = []
    for row in table["rows"]:
        found = [m.group(1) for cell in row.values()
                 for m in re.finditer(r"5[′']-([ACGT]{12,25})-3[′']", cell)]
        assert len(found) == 1, f"a row prints {len(found)} sequences: {row}"
        out.append(found[0])
    return out


def _duplex_cell(row):
    bp = int(row["mature_parent_duplex_through_gap_bp"])
    return "none at any length" if not bp else f"{bp} bp, wild-type {row['mature_parent_duplex_gene']}"


def _seam_cell(junction):
    donor, acceptor = junction.split("__")
    gene, exon = donor.rsplit("_e", 1)
    agene, aexon = acceptor.rsplit("_e", 1)
    return f"{gene} e{exon}::{agene} e{aexon}"


# ── 1 · the preamble's provenance claim, cell by cell ─────────────────────────────────────────
def test_every_printed_cell_is_the_column_the_preamble_promises(tables, rows_by_sequence):
    """⛔ "Every cell below is a column of fusion-junction-aso-sequences.csv" — CHECKED, not trusted.

    The one claim the whole page rests on. It was a typed literal describing a generator nobody
    joined to the data, and Table 2's verdict column was never read from `do_not_order` at all.
    """
    wrong = []
    for n, table in sorted(tables.items()):
        for seq, printed in zip(_sequences(table), table["rows"]):
            row = rows_by_sequence.get(seq)
            if row is None:
                wrong.append(f"Table {n}: {seq} has no 5-6-5 row in the canonical file")
                continue
            checks = {"seam": _seam_cell(row["junction"]),
                      "margin": row["gap_level_margin"],
                      "WT gap duplex (bp)": _duplex_cell(row)}
            for column, expected in checks.items():
                if column in printed and printed[column] != expected:
                    wrong.append(f"Table {n} {seq}: {column!r} prints {printed[column]!r}; the "
                                 f"canonical file gives {expected!r}")
    assert not wrong, ("a printed cell is not the column the preamble says it is:\n  "
                       + "\n  ".join(wrong) + "\n\nfusion-junction-aso-sequences.csv decides. "
                       "Fix the generator, never the CSV.")


# ── 2 · the verdict, which is the reason this file exists ─────────────────────────────────────
def test_the_verdict_column_is_read_from_the_canonical_file(tables, rows_by_sequence):
    """⛔⛔ DO NOT ORDER WAS A TYPED STRING (measured 2026-08-22).

    The generator prints `DO NOT ORDER` for every member of `CONDEMNED` and `orderable` for its
    twin, reading neither from `do_not_order`. Point `CONDEMNED` at a cleared design — one edit, the
    kind a panel refresh makes — and the table condemns a design the record clears and clears one it
    condemns, with every gate green. This is the ordering document; the verdict is the product.
    """
    wrong = []
    for n, table in sorted(tables.items()):
        if "verdict" not in table["header"]:
            continue
        for seq, printed in zip(_sequences(table), table["rows"]):
            row = rows_by_sequence[seq]
            says_no = printed["verdict"].upper().startswith("DO NOT ORDER")
            if says_no != bool(row["do_not_order"]):
                wrong.append(
                    f"Table {n}: {seq} is printed {printed['verdict']!r} while the canonical file "
                    f"says {row['do_not_order'][:60] or '(orderable)'!r}")
    assert not wrong, ("the verdict a table prints disagrees with the file a laboratory orders "
                       "from:\n  " + "\n  ".join(wrong))


def test_a_table_with_no_verdict_column_prints_no_condemned_design(tables, rows_by_sequence):
    """⛔ THE ONE-OF-A-PAIR ARM. Table 1 has no verdict column and `_lead` filters on `role` alone,
    so a panel refresh that made a condemned design the best available at a lead junction would
    print it as "a reagent named for synthesis" with nothing beside it. 0 of 37 best-available rows
    carry a verdict today and nothing asserts that it stays 0."""
    exposed = []
    for n, table in sorted(tables.items()):
        if "verdict" in table["header"]:
            continue
        for seq in _sequences(table):
            if rows_by_sequence[seq]["do_not_order"]:
                exposed.append(f"Table {n}: {seq} is condemned by the canonical file and this "
                               "table carries no verdict column")
    assert not exposed, "\n  ".join(exposed)


# ── 3 · the caption counts the rows it sits over — round 14's blocker, both tables ─────────────
_COUNT_OF_ROWS = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?:near-identical\s+)?(reagents?|designs?)\b", re.I)
_COUNT_OF_SEAMS = re.compile(
    r"\bat\s+(one|two|three|four|five|six)\s+seams?\b", re.I)


def test_each_caption_counts_the_rows_it_sits_over(tables, rows_by_sequence):
    """⛔⛔ ROUND 14's BLOCKER, IN BOTH CAPTIONS RATHER THAN ONE.

    "Four near-identical designs at two seams" survived the cut to a two-row, one-seam table and
    shipped in both PDFs; `--check` was clean throughout, because a generator reproduces its own
    output faithfully. The repair derived Table 2's count from `CONDEMNED` and left Table 1's
    "The two reagents named for synthesis" typed — measured 2026-08-22, "three reagents" over a
    two-row table passes every gate.
    """
    wrong = []
    for n, table in sorted(tables.items()):
        seqs = _sequences(table)
        for m in _COUNT_OF_ROWS.finditer(table["caption"]):
            if _WORDS[m.group(1).lower()] != len(seqs):
                wrong.append(f"Table {n}'s caption says {m.group(0)!r} over {len(seqs)} row(s)")
        seams = {rows_by_sequence[s]["junction"] for s in seqs}
        for m in _COUNT_OF_SEAMS.finditer(table["caption"]):
            if _WORDS[m.group(1).lower()] != len(seams):
                wrong.append(f"Table {n}'s caption says {m.group(0)!r} over {len(seams)} seam(s): "
                             f"{sorted(seams)}")
    assert not wrong, ("a caption counts something the table below it does not hold:\n  "
                       + "\n  ".join(wrong) + "\n\nDerive the count in the generator; do not type "
                       "it beside rows that are derived.")


# ── 4 · the caption's RELATIONS, which the round-14 repair did not touch ──────────────────────
def _one_slide(a, b):
    return a[1:] == b[:-1] or b[1:] == a[:-1]


def test_a_caption_claiming_a_single_base_slide_prints_a_single_base_slide(tables):
    """⛔ THE RELATION HALF. "Each pair is two consecutive registers of one seam differing by a
    single-base slide" is a literal; `_twin` reads the canonical file's cross-reference cell without
    checking that the relation it records IS a slide. That cell also records "1 substitution" and
    "2 substitutions" pairings, and 53 condemned 5-6-5 rows carry one."""
    for n, table in sorted(tables.items()):
        if "single-base slide" not in table["caption"]:
            continue
        seqs = _sequences(table)
        pairs = list(zip(seqs[::2], seqs[1::2]))
        assert pairs, f"Table {n}'s caption describes pairs and the table has no pair of rows"
        bad = [(a, b) for a, b in pairs if not _one_slide(a, b)]
        assert not bad, (
            f"Table {n}'s caption says each pair differs by a single-base slide; these do not: "
            f"{bad}. Two 16-mers one register apart satisfy a[1:] == b[:-1].")


def test_the_caption_verdict_relation_holds_over_the_rows(tables, rows_by_sequence, criterion):
    """⛔ "the condemned member pairs its whole catalytic gap … at the N-base-pair criterion and the
    orderable member does not" — a claim about the two rows, typed above them."""
    claim = re.compile(r"condemned member pairs its whole catalytic gap.*?"
                       r"and the orderable member does not", re.I | re.S)
    for n, table in sorted(tables.items()):
        if not claim.search(table["caption"]):
            continue
        wrong = []
        for seq, printed in zip(_sequences(table), table["rows"]):
            row = rows_by_sequence[seq]
            pairs_gap = row["pairs_a_wild_type_parent_through_the_gap"] == "True"
            says_no = printed.get("verdict", "").upper().startswith("DO NOT ORDER")
            if says_no != pairs_gap:
                wrong.append(f"{seq}: printed {printed.get('verdict')!r}, pairs a wild-type parent "
                             f"through the gap = {pairs_gap} at "
                             f"{row['mature_parent_duplex_through_gap_bp']} bp")
        assert not wrong, (
            f"Table {n}'s caption says the condemned member pairs its whole catalytic gap at the "
            f"{_NUMBER[criterion]}-base-pair criterion and the orderable one does not; the rows say "
            "otherwise:\n  " + "\n  ".join(wrong))


_NAMED_FOR_SYNTHESIS = re.compile(
    r"\b(neither|none|one|both|either)\b[^.;]{0,40}?\bnamed for synthesis\b", re.I)
_QUANTIFIER = {"neither": 0, "none": 0, "one": 1, "both": 2}


def test_a_caption_saying_which_rows_are_named_for_synthesis_is_right(tables):
    """⛔ THE SENTENCE A SHARPER TABLE WOULD ORPHAN. "neither is named for synthesis" is true of
    today's pair and typed. The canonical file records a condemned design ONE slide from the *TAF15*
    reagent this paper names for synthesis — a sharper pair than the printed one, and the generator's
    own comment says the sharper pair is what Table 2 is for. Printing it makes this sentence false
    while every gate stays green."""
    named = set()
    for n, table in sorted(tables.items()):
        if "verdict" not in table["header"]:
            named |= set(_sequences(table))
    assert named, "no table names a reagent for synthesis, so this guard asserted nothing"
    for n, table in sorted(tables.items()):
        m = _NAMED_FOR_SYNTHESIS.search(table["caption"])
        if not m:
            continue
        here = len(set(_sequences(table)) & named)
        want = _QUANTIFIER.get(m.group(1).lower())
        if want is None:                       # "either …" reads as at least one
            assert here >= 1, (f"Table {n}'s caption says {m.group(0)!r} and none of its rows is "
                               "named for synthesis")
            continue
        assert here == want, (
            f"Table {n}'s caption says {m.group(0)!r}; {here} of its rows is/are a reagent another "
            "table of this file names for synthesis. Derive the quantifier from the rows.")


_PROHIBITION = re.compile(r"\bneither\s+may\s+be\s+substituted\b", re.I)
_PERMISSION = re.compile(r"\b(?:either|each|any|one)\s+may\s+be\s+substituted\b", re.I)


def test_the_pair_table_keeps_its_substitution_prohibition(tables):
    """⛔ THE FILE'S ONE ORDER-SAFETY PREDICATE, WHICH NOTHING READ.

    The generator's own header states the property: "Neither member of a pair may be substituted for
    the other." Measured 2026-08-22, inverting it to "Either may be substituted for the other" passed
    every linter, all 879 tests and both PDF rebuilds — a predicate, not a quantity, which is the
    half the guard set was never built on.
    """
    for n, table in sorted(tables.items()):
        if "verdict" not in table["header"]:
            continue
        caption = table["caption"]
        assert not _PERMISSION.search(caption), (
            f"Table {n}'s caption permits substituting one member of a near-identical pair for the "
            f"other: {_PERMISSION.search(caption).group(0)!r}. The two carry OPPOSITE verdicts.")
        assert _PROHIBITION.search(caption), (
            f"Table {n} prints a near-identical pair carrying opposite verdicts and its caption no "
            "longer forbids substituting one for the other. That prohibition is the reason the "
            "table exists; a length cut that removes it fires nothing else in this suite.")


# ── 5 · the criterion, as a WORD ──────────────────────────────────────────────────────────────
def test_every_criterion_a_caption_states_is_the_one_the_record_sets(tables, criterion):
    """⛔ ROUND 15's BLOCKER WAS THAT "ten" IS A WORD. It is bound in the article now and was not
    bound here: "eleven-base-pair criterion" over the same rows passes every gate."""
    stated = set()
    for table in tables.values():
        stated |= {m.group(1).lower()
                   for m in re.finditer(r"\b([a-z]+)-base-pair criterion\b", table["caption"], re.I)}
    assert stated, "no caption states the criterion its verdicts are taken at"
    assert stated == {_NUMBER[criterion]}, (
        f"the captions state {sorted(stated)} as the criterion; the canonical record sets the "
        f"do-not-order flag at {criterion} base pairs ({_NUMBER[criterion]}).")


# ── 6 · the literature cell, against the record that quotes it ────────────────────────────────
def test_the_test_article_cells_are_the_constructs_the_record_names(tables):
    """⛔ SWAPPABLE, AND AN ARTIFACT DECIDES IT (measured 2026-08-22).

    The generator calls this map "a LITERATURE FACT … the one thing here that no artifact in this
    repository measures". `emc-fet-construct-designs.json` carries each construct's exon-numbered
    junction AND the source sentence naming it — "E-N, corresponding to EWSR1 (exons 1-12)-NR4A3
    (exons 3-8)" — so the map is derivable, and swapping E-N for T-N* between the two seams passed
    every gate.
    """
    record = json.load(io.open(_need(CONSTRUCTS, "the engineered constructs"), encoding="utf-8"))
    by_junction = {}
    for c in record["constructs"]:
        j = c["junction_in_exon_numbering"]
        key = (f'{j["five_prime_gene"]}_e{j["five_prime_last_exon_retained_transcript_rank"]}'
               f'__{j["three_prime_gene"]}_e{j["three_prime_first_exon_retained_transcript_rank"]}')
        for source in c.get("breakpoint_sources", []):
            m = re.match(r"\s*([A-Z]-[A-Z]\*?),\s*corresponding to", source.get("quote", ""))
            if m:
                by_junction.setdefault(key, set()).add(m.group(1))
    assert by_junction, "the construct record no longer quotes a construct name; re-anchor this"
    wrong = []
    for n, table in sorted(tables.items()):
        if "test article" not in table["header"]:
            continue
        for printed in table["rows"]:
            key = printed["seam"].replace("::", "__").replace(" ", "_")
            name = printed["test article"].split(",")[0].strip()
            known = by_junction.get(key)
            if known is None:
                wrong.append(f"Table {n}: no construct record for seam {printed['seam']}")
            elif name not in known:
                wrong.append(f"Table {n}: {printed['seam']} is given test article {name!r}; "
                             f"the construct record names {sorted(known)} at that junction")
    assert not wrong, ("a test-article cell disagrees with the record that quotes the construct:\n  "
                       + "\n  ".join(wrong))


# ── 7 · absence, which fires nothing else ─────────────────────────────────────────────────────
REQUIRED_OF_THIS_FILE = [
    ("the instruction to order from the canonical file",
     r"ordered from that file rather than transcribed|[Oo]rder from the canonical record",
     "this page prints four orderable 16-mers with no chemistry on it. The instruction is what "
     "sends a reader to the record that specifies the backbone, the wings and the geometry."),
    ("the scope bound",
     r"has been synthesi[sz]ed|nothing (?:here )?(?:has been|was) synthesi[sz]ed"
     r"|may be administered to any person or animal|not for administration",
     "the file ships standalone in the archive deposit. A downloader who opens it alone meets four "
     "orderable sequences; removing this line passed every gate on 2026-08-22."),
]


@pytest.mark.parametrize("label,pattern,why", REQUIRED_OF_THIS_FILE,
                         ids=[r[0] for r in REQUIRED_OF_THIS_FILE])
def test_the_display_item_file_states_it(label, pattern, why):
    text = io.open(_need(TABLES, "the journal display items"), encoding="utf-8").read()
    assert re.search(pattern, text, re.I), (
        f"the generated display-item file no longer states {label}.\n\nWHY: {why}\n\n"
        "⛔ A deleted sentence matches nothing and fires nothing, which is why absence is asserted "
        "rather than left to the linters.")


def test_the_hazard_distance_is_the_panels_worst_case_not_the_printed_pairs(rows_by_sequence, tables):
    """⛔⛔ THE NUMBER SIZES AN OFF-BY-ONE IN A SYNTHESIS ORDER, SO IT MUST BE THE PANEL'S MINIMUM.

    Round 16 seat 2: `_slides_to_a_named_lead` minimised over `CONDEMNED` — the pair Table 2 happens
    to PRINT — and reported **two** slides, for the *EWSR1* reagent. The canonical file records
    `AGGGCATATCTTGTGT`: DO NOT ORDER, 11 bp against wild-type *NR4A3*, and **one** single-base slide
    from `GGGCATATCTTGTGTG`, the *TAF15* reagent this paper names for synthesis. It was printed in
    neither journal PDF. So the caption understated by a factor of two the distance between a
    reagent a reader is told to buy and a design that fails the paper's central screen — a SCOPE
    bug, not an arithmetic one, which is why seat 2 could not break the arithmetic.

    ★ Minimised over the whole condemned class, read from the canonical file, so the caption cannot
    quietly narrow back to whatever the table happens to print.
    """
    named = {q for t in tables.values() for q in _sequences(t)} & set(rows_by_sequence)
    named = {q for q in named if not rows_by_sequence[q].get("do_not_order")}
    assert named, "no orderable reagent appears in the tables, so there is no hazard distance"

    closest = None
    for seq, row in rows_by_sequence.items():
        if not row.get("do_not_order"):
            continue
        for lead in named:
            if _one_slide(seq, lead):
                closest = 1
    assert closest == 1, (
        "no condemned 5-6-5 design is a single-base slide from a reagent named for synthesis. "
        "Either the canonical file changed or this guard is reading the wrong column; the caption's "
        "stated distance has to be re-derived either way, not left at whatever it says.")

    caption = " ".join(t["caption"] for t in tables.values())
    assert "one single-base slide" in caption, (
        "the closest condemned design is ONE single-base slide from a reagent this paper names for "
        f"synthesis, and no caption says so:\n  {caption[:400]}\n\n"
        "A larger number here tells a reader the hazard is further away than it is.")


def test_the_display_items_name_the_chemistry_and_geometry_of_what_they_print():
    """⛔⛔ FOUR ORDERABLE SEQUENCES, ZERO MENTIONS OF THE CHEMISTRY (round 16 seat 5, 2026-08-22).

    Measured on the two tables documents:

        fusion-junction-aso-submission-tables.md   phosphorothioate 7   5-6-5 18   gapmer 6
        fusion-junction-aso-journal-tables.md      phosphorothioate 0   5-6-5  0   gapmer 0

    `test_table_captions_state_the_right_geometry.py` asserts exactly this and is scoped to the
    DEPOSIT document, so the display items that actually ship with the journal submission were
    unread — one-of-a-pair again. Round 14's blocker was a paper that printed a specific sequence
    six times and never said what chemistry to order it in; a display item is the place a reader
    copies a sequence FROM, and journals routinely reproduce tables apart from the text.

    ★ THE PROPERTY IS GUARDED FOR BOTH DOCUMENTS, BY THE GUARD THAT SUITS EACH. The deposit
    document states it per caption; this one states it once in the preamble, because the caption
    placement cost a seventh page and the preamble did not — 6 pages at 386 words against 7 at 376,
    which is float displacement, not length. So this asserts the DOCUMENT states it, not each
    caption.
    """
    text = io.open(_need(TABLES, "the journal display items"), encoding="utf-8").read()
    printed = re.findall(r"5[′']-([ACGT]{12,25})-3[′']", text)
    assert printed, "the journal display items print no sequence, so this guard is vacuous"

    lowered = text.lower()
    for term, why in (
            ("phosphorothioate",
             "ordering these bases as unmodified DNA gives a different molecule, and this is the "
             "page a reader copies the sequence from"),
            ("5-6-5",
             "every count in the paper is over designs of one geometry; a sequence without it is "
             "not orderable as the thing that was screened")):
        assert term in lowered, (
            f"the journal display items print {len(printed)} orderable sequence(s) and never say "
            f"{term!r}. WHY THAT MATTERS: {why}.\n\n"
            "The deposit tables state it; this document is the one that ships with the submission.")
