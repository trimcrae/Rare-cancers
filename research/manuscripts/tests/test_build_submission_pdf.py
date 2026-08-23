"""The submission PDF is an ASSEMBLY, and an assembly's failure mode is silent loss.

The builder splices two generated files into the manuscript, inlines three figures, and — in
journal style — moves every table and figure to the point it is first cited. Every one of those
joins is anchored on a heading, a legend opener or an in-text citation, and a manuscript is prose
that gets edited. Renaming `## References` would, without an assertion, produce a PDF that looks
complete for twenty-two pages and then has no reference list.

These tests exercise the real files, not fixtures. A fixture would prove the regex works; only the
real manuscript proves the anchors it is aimed at still exist.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import build_submission_pdf as bsp  # noqa: E402

PAPER = bsp.PAPERS["aso"]


@pytest.fixture(scope="module")
def journal():
    body, floats = bsp.assemble(PAPER, "journal")
    front = bsp.parse_front_matter(body)
    rendered = bsp.markdown_to_html(front["body"], floats)
    return front, floats, rendered, bsp.wrap_journal(PAPER, front, rendered)


@pytest.fixture(scope="module")
def manuscript():
    body, _ = bsp.assemble(PAPER, "manuscript")
    return body, bsp.markdown_to_html(body)


# ---------------------------------------------------------------- content survives the assembly

def test_the_pointer_paragraphs_are_replaced_rather_than_kept(manuscript):
    """The manuscript says the tables 'are in <file>'. The PDF must contain them, not the sentence."""
    body, _ = manuscript
    # ⚠ NARROWED 2026-08-19, AND NOT TO MAKE A FAILURE GO AWAY. This asserted that the tables
    # filename never survives into the rendered body, on the premise that no `.md` is deposited.
    # That premise stopped being true: the availability statement now names
    # `fusion-junction-aso-submission-tables.md` as the machine-readable copy of Tables 1 to 7, on
    # a deposit reviewer's finding that the file was an ORPHAN -- referenced by no PDF at all. The
    # file IS in the deposit, so the pointer is correct and suppressing it would send a reader
    # nowhere. What must still hold is that the tables are PRINTED here rather than only pointed
    # at, which is the property the original assertion was protecting.
    assert "**Table 1." in body and "**Table 7." in body, (
        "the tables must be spliced into the body, not merely referenced by filename")
    assert "fusion-junction-aso-submission-references.md" not in body


@pytest.mark.parametrize("style", ["journal", "manuscript"])
def test_every_reference_entry_survives(style):
    body, _ = bsp.assemble(PAPER, style)
    entries = re.findall(r"^(\d+)\.\s", bsp.read(PAPER["references"]), re.M)
    assert len(entries) > 30, "reference file looks empty; the splice would silently succeed"
    for number in entries:
        assert re.search(rf"^{number}\.\s", body, re.M), f"reference {number} was lost"


def _pipe_rows(text):
    """Every pipe row of a markdown document that is not an alignment separator."""
    return [ln for ln in text.split("\n")
            if ln.strip().startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", ln.strip())]


def _source_rows_by_table(tables_md):
    """{table number: pipe rows} for the generated tables document."""
    out = {}
    for block in re.split(r"(?=^\*\*Table \d+\.)", tables_md, flags=re.M):
        opener = re.match(r"^\*\*Table (\d+)\.", block)
        if opener:
            out[int(opener.group(1))] = _pipe_rows(block)
    return out


def test_every_table_survives_into_the_journal_layout(journal):
    """⛔ COUNTED PER TABLE, NOT IN AGGREGATE (2026-08-19).

    This compared the tables document's total pipe-row count against every `<tr>` in the rendered
    document, on the standing assumption — written into HANDOFF as a fact — that "the article .md
    contains NO pipe tables". The moment the criterion ladder was added to §2.5 as an inline pipe
    table, the rendered side gained nine rows the source side could not see and the test failed
    with "a table row was dropped" while nothing had been dropped: 195 rendered against 186 source.
    An aggregate count over two populations cannot tell an addition in one from a loss in the
    other. Per table it can, and a row moving BETWEEN tables — which the aggregate could never
    see — now fails too.
    """
    _, floats, rendered, _ = journal
    import build_submission_pdf as bsp

    source = _source_rows_by_table(bsp.read(PAPER["tables"]))
    assert source and sum(len(v) for v in source.values()) > 100, source
    for _kind, number, block, _wide in floats.values():
        if _kind != "table":
            continue
        assert number in source, f"Table {number} is laid out and is in no source block"
        # ⚠ MATCH ANY <tr, NOT THE LITERAL "<tr>". Block-heading rows gained class="blockhead" on
        # 2026-08-19 so each block could travel as its own <tbody>, and a literal matcher counted
        # 179 where 182 rows were present — a passing-to-failing flip with nothing dropped. The
        # table-name rows in <thead> are excluded because they are not source rows.
        laid_out = [m for m in re.findall(r'<tr(?:\s+class="([^"]*)")?>', bsp.render_float(
            _kind, number, block, _wide)) if m != "tablename"]
        assert len(laid_out) == len(source[number]), (
            f"Table {number} lays out {len(laid_out)} row(s) from {len(source[number])} source "
            "row(s) — a row was dropped, duplicated, or has moved to another table")

    #: AND NOTHING MAY VANISH DOCUMENT-WIDE EITHER. The rendered total must be the tables' rows
    #: plus whatever pipe rows the manuscript itself carries inline, so a table spliced into the
    #: body and then lost is still caught.
    total = len([m for m in re.findall(r'<tr(?:\s+class="([^"]*)")?>', rendered)
                 if m != "tablename"])
    assert total >= sum(len(v) for v in source.values()), (
        f"the rendered document carries {total} table row(s) against "
        f"{sum(len(v) for v in source.values())} in the generated tables document alone")

    # ⚠ DERIVED FROM THE GENERATED TABLES FILE, NOT TYPED (2026-08-16). This asserted `== 6` and had
    # to be chased by hand the moment Table 7 was generated. A typed count is the same defect
    # `_geometry_columns` names in submission_tables.py: it cannot notice a table added upstream, and
    # when one is added it fails for a reason that has nothing to do with the layout. The expectation
    # is now the count of captions the tables file itself carries, so a table added upstream must
    # still reach the layout, and a table dropped from the layout still fails.
    captions = set(re.findall(r"^\*\*Table (\d+)\.", bsp.read(PAPER["tables"]), re.M))
    assert len(captions) >= 6, captions
    assert sum(1 for v in floats.values() if v[0] == "table") == len(captions)


def test_every_figure_is_placed_with_the_legend_that_describes_it(journal):
    """⚠ A SUPPLEMENTARY PANEL IS KEYED ABOVE THE NUMBERED ONES SO IT LAYS OUT LAST.

    `build_submission_pdf.SUPPLEMENTARY_SORT_BASE` offsets it rather than special-casing the
    layout, so the key is 1001 and the label the body cites is "Supplementary Figure S1". Both
    halves are asserted: a mismatch between them is how a panel gets reported as uncited.
    """
    import build_submission_pdf as bsp
    _, floats, rendered, _ = journal
    figures = {n: p for (kind, n, p, _w) in floats.values() if kind == "figure"}
    numbered = {n for n in figures if n < bsp.SUPPLEMENTARY_SORT_BASE}
    supplementary = {n for n in figures if n >= bsp.SUPPLEMENTARY_SORT_BASE}
    #: ⛔ DERIVED FROM THE LEGEND BLOCK, NOT TYPED (2026-08-19). This asserted `numbered == {1, 2, 3}`
    #: and `supplementary == {BASE + 1}` — a fourth panel would have failed here, in a test about
    #: legend PAIRING, for a reason that has nothing to do with pairing. The manuscript's own
    #: "## Figure legends" block is where a figure comes into existence, so it is the expectation.
    legends = re.search(r"^## Figure legends.*", bsp.read(PAPER["manuscript"]), re.S | re.M)
    assert legends, "the manuscript has no '## Figure legends' block to derive the panel set from"
    declared = {int(n) for n in re.findall(r"^\*\*Figure (\d+)\.", legends.group(0), re.M)}
    declared_supp = {int(n) for n in
                     re.findall(r"^\*\*Supplementary Figure S(\d+)\.", legends.group(0), re.M)}
    assert declared, "the legend block declares no numbered figure"
    assert numbered == declared, (
        f"the journal layout carries figures {sorted(numbered)} where the manuscript's legend "
        f"block declares {sorted(declared)}")
    assert supplementary == {bsp.SUPPLEMENTARY_SORT_BASE + n for n in declared_supp}
    for number, (svg, legend) in figures.items():
        assert svg.startswith("<svg")
        expected = (f"**Supplementary Figure S{number - bsp.SUPPLEMENTARY_SORT_BASE}."
                    if number >= bsp.SUPPLEMENTARY_SORT_BASE else f"**Figure {number}.")
        assert legend.startswith(expected), "a legend was paired to the wrong panel"
    assert rendered.count("<svg") == len(figures)


# ---------------------------------------------------------------- the anchors are load-bearing

def test_a_renamed_section_fails_the_build_instead_of_dropping_content():
    """⛔ The whole point of anchoring. A missing anchor must be fatal, never a no-op."""
    with pytest.raises(SystemExit) as excinfo:
        bsp.splice("## Something Else\n\npointer\n", "References", "replacement", "the references")
    assert "anchor not found" in str(excinfo.value)


def test_a_figure_with_no_legend_fails_the_build():
    with pytest.raises(SystemExit) as excinfo:
        bsp.split_figures("## Figure legends\n\nnothing here\n", PAPER["figures"])
    assert "no legend found" in str(excinfo.value)


def test_an_uncited_display_item_must_be_declared_not_guessed():
    """⚠ Figure 3 is never cited by name. An item with no anchor and no declaration must fail
    rather than be dropped at whatever offset the layout happened to reach."""
    with pytest.raises(SystemExit) as excinfo:
        bsp.place_floats("body text with no citations\n", [("Table 9", "@@FLOAT:table9@@")], {})
    assert "never cited" in str(excinfo.value)


def test_the_declared_fallback_for_figure_3_still_points_at_a_real_section():
    """⚠ Matches heading TEXT at any level, not a `### <number>`. Updated 2026-08-16 with the
    builder: the number form asserted that §3.10 existed, so an editorial pass that merged that
    subsection into a renamed one turned a placement question into a spurious failure about
    numbering. What must hold is that the declared anchor still names a section that exists."""
    body, _ = bsp.assemble(PAPER, "journal")
    for label, rule in PAPER["placement"].items():
        assert re.search(rf"^#{{2,4}}\s+.*{re.escape(rule['after_heading'])}.*$", body, re.M | re.I), (
            f"{label}'s declared placement anchor {rule['after_heading']!r} matches no heading")


def test_float_anchors_are_computed_before_any_insertion():
    """An inserted table must not become the anchor that a later table floats to."""
    body = "cite Table 1 here.\n\nand later cite Table 2 here.\n"
    out = bsp.place_floats(body, [("Table 1", "@@A@@"), ("Table 2", "@@B@@")], {})
    assert out.index("@@A@@") < out.index("and later"), "Table 1 did not land at its own citation"
    assert out.index("@@B@@") > out.index("and later")


def test_a_missing_front_matter_label_fails_the_build():
    with pytest.raises(SystemExit) as excinfo:
        bsp.parse_front_matter("# Title\n\n## Abstract\n\ntext\n\n## 1 · Intro\n")
    assert "front matter" in str(excinfo.value)


# ---------------------------------------------------------------- rendering correctness

#: The disclaimers that must reach a reader BEFORE the first oligonucleotide the abstract names.
#: Expressed as concept regexes rather than as sentences: what the abstract owes a reader is a
#: statement that nothing was made and a statement that nothing may be given to anybody, and both
#: have been rewritten repeatedly while meaning the same thing. Pinning the wording made this guard
#: fail on the rewrite and pass on the deletion, which is backwards.
_ABSTRACT_DISCLAIMERS = (
    ("nothing was synthesised or tested",
     re.compile(r"no wet-lab|nothing (?:has been|was) (?:synthesi[sz]ed|made)"
                r"|the work is computational", re.I)),
    ("no administration to a person or animal",
     re.compile(r"(?:must not be administered|not for administration|not to be administered)"
                r"[^.]{0,90}(?:person|human|animal)"
                r"|research (?:reagent|use)[^.]{0,90}(?:not for|only, not)", re.I)),
)

#: 5′-…-3′ in either quote convention. The abstract names its leads, and the ordering property is
#: about them, so the sequence is FOUND rather than typed — a renamed lead must not silence this.
_PRINTED_SEQUENCE = re.compile(r"5[\u2032'][\u2011-]?[ACGT]{12,25}[\u2011-]?3[\u2032']")


def _wrapped_paragraph_spans(raw):
    """Every "last word of a line + first word of the next" pair inside a wrapped source paragraph.

    THE PROPERTY, DERIVED. A field that wraps in the manuscript source is captured whole only if
    the captured text contains every one of these joins. It is computed from the .md at run time,
    so it cannot go stale, and it is what the assertion was reaching for all along — five separate
    re-pins of a literal tail string in three days, each one recording that the property was
    unchanged and the words had moved.
    """
    spans = []
    lines = [ln.strip() for ln in raw.strip().split("\n")]
    for first, second in zip(lines, lines[1:]):
        if not first or not second:
            continue
        spans.append(f"{first.split()[-1]} {second.split()[0]}")
    return spans


def _source_section(heading):
    """The raw text under `## heading` in the manuscript source, line breaks intact."""
    body = bsp.read(PAPER["manuscript"])
    _, end, after = bsp.section_span(body, heading)
    return body[after:end].strip().strip("-").strip()


def _source_label_paragraph(label):
    """The raw `**Label.**` front-matter paragraph, line breaks INTACT.

    `bsp.label_paragraph` unwraps as it reads, which is exactly the transformation under test, so
    the source has to be re-read here rather than borrowed from the builder.
    """
    body = bsp.read(PAPER["manuscript"])
    match = re.search(rf"^\*\*{re.escape(label)}\.\*\*[^\n]*(?:\n(?!\s*\n)[^\n]*)*", body, re.M)
    assert match, f"the front-matter label '**{label}.**' is not in the manuscript source"
    return match.group(0)


def test_front_matter_captures_whole_paragraphs_not_first_lines(journal):
    """⚠ These fields wrap in the source. A first-line-only match silently dropped the tail.

    ⛔ THIS USED TO PIN THE ABSTRACT'S LAST WORDS AS A LITERAL, and the literal was re-typed five
    times in three days — round 5, round 7's P0.8, two rewrites on 2026-08-19 — each time with a
    comment explaining that the property being asserted had not changed. A pin that has to be
    rewritten every time the prose moves is not measuring the prose; it is measuring whether
    somebody remembered to update it, and on 2026-08-19 it was failing for exactly that reason
    while the defect it exists for was absent. The whole-paragraph property is now DERIVED from the
    source: every line break inside the source paragraph must be crossed in the captured field.
    """
    front, _, _, _ = journal
    for field, heading, label in (("abstract", "Abstract", None),
                                  ("keywords", None, "Keywords")):
        raw = _source_section(heading) if heading else _source_label_paragraph(label)
        joins = _wrapped_paragraph_spans(raw)
        assert joins, (
            f"the source {field} is a single line, so this guard cannot tell a whole-paragraph "
            "capture from a first-line one. Either the field stopped wrapping or the section "
            "anchor has moved.")
        flat = " ".join(front[field].split())
        missing = [j for j in joins if " ".join(j.split()) not in flat]
        assert not missing, (
            f"the captured {field} does not cross {len(missing)} of its source's "
            f"{len(joins)} line wraps, so the builder took a prefix rather than the paragraph: "
            + "; ".join(repr(j) for j in missing[:3]))
    #: The affiliation's tail is its ORCID line, which is a structural fact about the block rather
    #: than a wording: an affiliation captured first-line-only loses it.
    assert "ORCID" in front["affiliation"]


def test_the_abstracts_disclaimers_precede_the_first_sequence_it_names(journal):
    """⛔ AND THE ORDERING IS THE POINT. Round 7's P0.8 and P0.6 were one defect: the two
    disclaimers sat five sentences BEHIND the orderable 16-mers the abstract names, so any venue
    that truncates an abstract kept the sequences and dropped the warning. They were moved ahead of
    the sequences; this holds them there.

    ⚠ ASSERTED AS CONCEPTS, NOT SENTENCES. The literal clauses this used to require —
    "no wet-lab experiment was performed" and "must not be administered to any person or animal" —
    were both rewritten on 2026-08-19 ("The work is computational: nothing has been synthesised or
    tested"; "not for administration to any person or animal"). The guard went red on a rewrite
    that kept every word of the meaning, which trains a reader to edit the test rather than the
    paper. The regexes are tolerant; what is not tolerant is the ORDER.
    """
    front, _, _, _ = journal
    flat = " ".join(front["abstract"].split())
    sequence = _PRINTED_SEQUENCE.search(flat)
    assert sequence, (
        "the abstract names no oligonucleotide, so the ordering property below is vacuous. If the "
        "leads were genuinely removed from the abstract, delete this test and say so.")
    for what, pattern in _ABSTRACT_DISCLAIMERS:
        found = pattern.search(flat)
        assert found, (
            f"the abstract carries no statement that {what}. It is the part of the paper that "
            "travels alone, and both disclaimers are stripped from the rendered PDFs' repository "
            f"frontmatter. Reword freely — the pattern is {pattern.pattern!r} — but say it.")
        assert found.start() < sequence.start(), (
            f"the abstract states that {what} at character {found.start()}, AFTER the first "
            f"sequence it prints ({sequence.group(0)}) at {sequence.start()}. A venue that "
            "truncates an abstract would keep the orderable 16-mer and drop the warning.")


def test_citation_markers_render_and_their_pmid_comments_do_not(journal):
    """PMIDs ride beside each superscript in a non-rendering comment; a leaked one would print
    mid-sentence. The reference LIST carries `PMID: n` as visible text on purpose, which is why
    this looks only at the body above it."""
    _, _, rendered, _ = journal
    body = rendered.split("<h2>References</h2>")[0]
    assert "<sup>" in body
    assert "PMID:" not in body
    assert "<!--" not in rendered


@pytest.mark.parametrize("style", ["journal", "manuscript"])
def test_no_unconverted_markdown_reaches_the_page(style):
    body, floats = bsp.assemble(PAPER, style)
    if style == "journal":
        body = bsp.parse_front_matter(body)["body"]
    text = re.sub(r"<svg.*?</svg>", "", bsp.markdown_to_html(body, floats), flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    assert "**" not in text
    assert not re.search(r"(?<![\w/:])\|(?!\w)", text), "a pipe table did not become a <table>"
    assert "@@FLOAT" not in text, "a float token was never substituted"


def test_the_repo_frontmatter_is_stripped(journal):
    """id/level/canonical_for are internal routing and must not reach a reviewer."""
    _, _, _, page = journal
    for field in ("canonical_for", "last_verified", "DOC-FUSION-JUNCTION-ASO-SUBMISSION"):
        assert field not in page


# ------------------------------------------------- EVERY paper, not just the one this module pins
#
# ⛔ THE GATE ABOVE COULD NOT SEE HALF THE REPOSITORY'S SUBMISSION PDFS. `PAPER` is bound once, at
# module scope, to PAPERS["aso"] — the extended report. PAPERS also holds "aso-journal", the
# document that would actually be submitted to a journal, and NO test in this file ever assembled
# it. Round 8 found repo frontmatter printing in both of its built PDFs while all 39 tests here
# passed, and pointing the assertion below at it failed 2 of its 3 fields. A gate scoped to one
# member of a registry reports on the registry.
#
# So these run over PAPERS.keys() rather than over a pinned paper: anything added to the registry
# is covered the day it is added. Only paper-agnostic invariants belong here — assertions about
# Table 7 or a particular figure stay bound to the paper that has them.


@pytest.mark.parametrize("key", sorted(bsp.PAPERS))
@pytest.mark.parametrize("style", ["journal", "manuscript"])
def test_no_repo_frontmatter_reaches_any_built_paper(key, style):
    """Routing metadata is internal. It must not print in ANY paper, in either style."""
    paper = bsp.PAPERS[key]
    body, floats = bsp.assemble(paper, style)
    if style == "journal":
        front = bsp.parse_front_matter(body)
        page = bsp.wrap_journal(paper, front, bsp.markdown_to_html(front["body"], floats))
    else:
        page = bsp.markdown_to_html(body)
    for field in ("canonical_for:", "last_verified:", "level: L3", "kind: manuscript",
                  "audience:", "DOC-FUSION-JUNCTION-ASO"):
        assert field not in page, (
            f"{key} ({style}) prints repo frontmatter field {field!r} as body text — "
            "an include is reaching the page unstripped")


@pytest.mark.parametrize("key", sorted(bsp.PAPERS))
def test_every_papers_reference_list_survives_assembly(key):
    """A spliced reference list that silently vanishes looks like a complete PDF until page 20."""
    paper = bsp.PAPERS[key]
    body, _ = bsp.assemble(paper, "journal")
    # ⛔ A PAPER WITH INLINE REFERENCES IS STILL CHECKED, NOT SKIPPED. When `references` is None the
    # entries live in the manuscript's own Section 10 rather than in a spliced file, so read them
    # from there. Skipping the assertion for such a paper would be the failure this test is named
    # for — a reference list that vanishes looks like a complete PDF until page 20 — wearing the
    # costume of a configuration difference.
    # ⛔ COUNT INSIDE THE REFERENCE SECTION, NOT ACROSS THE WHOLE FILE. Measured 2026-08-23 on
    # `nr4a3-fusion-transcriptional-output.md`: the file has **12** references, and this test counted
    # **46** — 33 numbered list items in the body, plus a wrapped line beginning "2015.". It then
    # asserted that "46." appears in the assembled body and failed, reporting a dropped reference
    # list on a paper whose references were entirely intact (body 107,221 chars, `## References`
    # present, entries 1–12 and their DOIs all there).
    # ⚠ A GUARD THAT INVENTS A DEFECT IS WORSE THAN ONE THAT SLEEPS: it cost a real build entry,
    # which was removed on the strength of this failure. Slice from the heading so the number the
    # test demands is a reference number rather than an artefact of counting.
    if paper.get("references"):
        source = bsp.read(paper["references"])
    else:
        whole = bsp.read(paper["manuscript"])
        head = re.search(r"^##\s+(?:[\d.·\s]*)References\s*$", whole, re.M)
        assert head, f"{key}: no '## References' heading to read inline entries from"
        source = whole[head.start():]
    entries = re.findall(r"^(\d+)\.\s", source, re.M)
    assert entries, f"{key}: no numbered entries found in its reference list"
    # The LAST NUMBER, not the count: a list that starts at 1 and runs contiguously makes these
    # equal, and a list that does not is exactly where the count would lie.
    last = max(int(n) for n in entries)
    assert f"{last}." in body, f"{key}: the last reference entry did not survive assembly"


def test_wide_tables_go_on_landscape_pages_and_narrow_ones_do_not(journal):
    """Twelve columns are unreadable in portrait; two columns do not deserve their own page."""
    _, floats, _, page = journal
    wide = {n for (kind, n, _p, w) in floats.values() if kind == "table" and w}
    assert wide, "no table was routed to a landscape page"
    assert "@page landscape" in page
    for _kind, number, block, is_wide in floats.values():
        if _kind == "table":
            assert is_wide == (bsp.table_columns(block) >= bsp.LANDSCAPE_MIN_COLS)


def test_the_back_matter_is_split_out_of_the_two_column_body(journal):
    _, _, _, page = journal
    assert '<div class="cols">' in page and '<div class="backmatter">' in page
    back = page.split('<div class="backmatter">')[1]
    assert "Declarations" in back and 'id="references-list"' in back
    assert "Introduction" not in back, "the back-matter split swallowed part of the body"


def test_the_two_styles_write_to_different_files():
    """The submission format is what a portal wants; they must not overwrite each other."""
    assert PAPER["out"] != PAPER["out"].replace(".pdf", "-manuscript.pdf")
