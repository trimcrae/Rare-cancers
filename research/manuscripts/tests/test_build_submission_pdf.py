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

#: ⛔ REBOUND FROM "aso" TO "aso-journal" ON 2026-08-25 (trimcrae removed the extended report from
#: the gate). Every assertion below is a property of the BUILDER, not of that one document, so the
#: right repair was to point them at the ASO paper that still exists rather than to delete them —
#: deleting would have taken the builder's coverage down to whatever the parametrised gate at the
#: foot of this file happens to reach, which is the shrinking-scope hole its own comment records.
PAPER = bsp.PAPERS["aso-journal"]


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
    #: ⚠ DERIVED, NOT TYPED. This named Table 1 and Table 7 — the extended report's first and last
    #: — and became an assertion about ONE document's size rather than about splicing. The property
    #: is that every table the source file defines is printed, whatever the paper has.
    numbers = re.findall(r"^\*\*Table (\d+)\.", bsp.read(PAPER["tables"]), re.M)
    assert numbers, "the paper's tables file defines no table, so the splice cannot be measured"
    for n in numbers:
        assert f"**Table {n}." in body, (
            f"Table {n} must be spliced into the body, not merely referenced by filename")
    assert "fusion-junction-aso-submission-references.md" not in body


@pytest.mark.parametrize("style", ["journal", "manuscript"])
def test_every_reference_entry_survives(style):
    body, _ = bsp.assemble(PAPER, style)
    entries = re.findall(r"^(\d+)\.\s", bsp.read(PAPER["references"]), re.M)
    #: ⚠ WAS `> 30`, WHICH WAS THE EXTENDED REPORT'S REFERENCE COUNT. What guards against a silent
    #: splice is that the file has entries AT ALL and that every one survives; the magnitude was
    #: only ever a proxy for "not empty".
    assert entries, "reference file looks empty; the splice would silently succeed"
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
    #: ⚠ WAS `> 100` rows, again the extended report's magnitude rather than a property.
    assert source and sum(len(v) for v in source.values()), source
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
    #: ⚠ WAS `>= 6` — the extended report's table count, typed. The property is that the layout
    #: carries exactly the captions the tables file defines, which the next line asserts.
    assert captions, "the paper's tables file defines no table"
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
     #: ⚠ `th(?:e|is)` — the journal article opens the sentence with "This work is computational"
     #: and the pattern demanded "the". Identical claim, identical strength; one article word.
     re.compile(r"no wet-lab|nothing (?:has been|was) (?:synthesi[sz]ed|made)"
                r"|th(?:e|is) work is computational", re.I)),
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
    #: ⚠ THE MARKER'S FORM IS THE PAPER'S CHOICE. `bracketed_citations` renders `[3]` where the
    #: default renders `<sup>3</sup>`; asserting `<sup>` alone reported a paper whose citations
    #: render perfectly as having none. What must hold either way is that a marker rendered and
    #: the PMID comment beside it did not.
    marker = r"\[\d+(?:[,–-]\d+)*\]" if PAPER.get("bracketed_citations") else r"<sup>"
    assert re.search(marker, body), f"no citation marker matching {marker} rendered in the body"
    #: ⛔ THE DEFECT IS A LEAKED COMMENT, NOT THE STRING "PMID". This was a blanket
    #: `"PMID:" not in body`, which is right for a paper that never prints one and wrong for this
    #: one: it cites two sources as visible PubMed LINKS in the prose, so the blanket form failed on
    #: text that is deliberately there. What must not appear is a PMID outside an anchor — that is
    #: the comment having escaped its markup and printed mid-sentence.
    for stray in re.finditer(r"PMID", body):
        before = body[:stray.start()]
        assert before.rfind("<a ") > before.rfind("</a>"), (
            f"a PMID appears outside an anchor at character {stray.start()}: "
            f"{body[max(0, stray.start()-60):stray.start()+40]!r}. The PMIDs ride in "
            f"non-rendering comments beside each marker; one printing as text is a leak.")
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
def test_the_two_styles_write_to_different_files():
    """The submission format is what a portal wants; they must not overwrite each other."""
    assert PAPER["out"] != PAPER["out"].replace(".pdf", "-manuscript.pdf")


# ---------------------------------------------------------------------------------------------
def test_a_backslash_escaped_asterisk_prints_as_an_asterisk_and_never_as_emphasis():
    """⛔ MEASURED IN THE BUILT DEPOSIT, 2026-08-23. `\\*` was never unescaped by this builder.

    One escaped allele on a line printed its backslash: `HLA-B\\*15:01`. TWO on a line were worse —
    the emphasis rule read the span BETWEEN their live asterisks as italic, so
    `HLA-A\\*01:01, HLA-B\\*07:02` came out as `HLA-A\\` + italic `01:01, HLA-B\\` + `07:02`, with
    both allele names destroyed and unrelated text italicised. Every posted version of the
    junction-vaccine manuscript carries it, in a paper whose subject is which HLA alleles present a
    peptide. Two alleles on one line is the case that matters and is the second assertion here;
    checking only the single-allele case would have passed throughout the incident.
    """
    assert bsp.inline(r"presented on HLA-B\*15:01 alone") == "presented on HLA-B*15:01 alone"
    two = bsp.inline(r"HLA-A\*01:01, HLA-B\*07:02, HLA-B\*15:01")
    assert two == "HLA-A*01:01, HLA-B*07:02, HLA-B*15:01"
    assert "<em>" not in two and "\\" not in two


def test_unescaped_emphasis_still_works_after_the_escape_rule():
    """The fix must not cost the markup it sits in front of."""
    got = bsp.inline("*EWSR1* exon 7 and **bold**")
    assert got == "<em>EWSR1</em> exon 7 and <strong>bold</strong>"


def test_other_markdown_escapes_lose_their_backslash_too():
    assert bsp.inline(r"a literal \_underscore\_ and \[bracket\]") == (
        "a literal _underscore_ and [bracket]")


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE BUILT PDF IS THE ONLY ARTIFACT A REVIEWER SEES, AND NOTHING IN THIS REPOSITORY READ IT.
# Every other gate here opens the manuscript SOURCE: lint_consistency, lint_claims, lint_style and
# the one-of-a-pair number guards all read the `.md`. The escape defect above therefore rode four
# published versions of the vaccine paper undetected — it is invisible in the source, where
# `HLA-B\*15:01` is correct markdown, and only exists after rendering. These tests read the rendered
# text, which is where the reader is.
import glob as _glob

_pypdf = pytest.importorskip("pypdf", reason="the deposit PDFs are checked by extracting their text")


def _pdf_text(path):
    return "\n".join(p.extract_text() for p in _pypdf.PdfReader(path).pages)


@pytest.mark.committed_artifact
@pytest.mark.parametrize("pdf", sorted(_glob.glob(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "*", "*.pdf"))))
def test_no_markdown_escape_survives_into_a_deposited_pdf(pdf):
    r"""⛔ A LEAKED MARKDOWN ESCAPE, NOT EVERY BACKSLASH. The distinction is the whole test.

    ⚠ THE FIRST VERSION OF THIS GUARD ASSERTED `text.count(chr(92)) == 0` AND FAILED ON CORRECT
    CONTENT. The ASO article prints a shell command with a line continuation — `\` at end of line,
    inside a code block — which is exactly what it should render. A guard that invents a defect is
    worse than one that sleeps: it gets relaxed, and the relaxation that suggests itself is deleting
    the row, which is how the real defect then goes unwatched.

    So the pattern is the defect's own shape. A leaked escape is a backslash directly against a
    markdown metacharacter (`\*`, `\_`, `\[`), or against an alphanumeric — which is what the
    emphasis pass leaves behind when it eats the asterisk out of `HLA-B\*15:01` and prints
    `HLA-B\15:01`. A backslash followed by whitespace or end of line is a continuation and is
    content.
    """
    text = _pdf_text(pdf)
    # ⛔ NO TEXT LAYER IS A FAILURE, NOT A SKIP. A deposit PDF a reader cannot select, search or
    # have read aloud is broken as a deposit, and a skip here would have quietly excused exactly the
    # document this guard most needs to read.
    assert text.strip(), (
        f"{os.path.basename(pdf)} extracts no text layer — it is unsearchable, unselectable and "
        "unreadable by assistive software, and no escape check can run over it")
    leaked = re.findall(r"\\[*_\[\]#A-Za-z0-9]", text)
    assert not leaked, (
        f"{os.path.basename(pdf)} renders {len(leaked)} leaked markdown escape(s) {sorted(set(leaked))} "
        "— see inline()'s escape rule; the two-allele case is what breaks.")


@pytest.mark.committed_artifact
def test_the_vaccine_papers_alleles_render_with_their_asterisks():
    """The paper's subject IS allele coverage, so a mangled allele name is a factual error on
    every page. Bound to this document specifically because it is the one that carries 35 of them."""
    pdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "neoantigen", "emc-vaccine-development-path.pdf")
    # ⛔ COMMITTED, SO ITS ABSENCE IS A BROKEN TREE — which is precisely when this guard must speak.
    assert os.path.exists(pdf), (
        f"{pdf} is missing. It is a committed deposit artifact, so this is a broken checkout or a "
        "deleted PDF, not a reason to pass over the allele check.")
    text = _pdf_text(pdf)
    alleles = re.findall(r"HLA-[A-Z]{1,4}[0-9]?\*?[0-9]{2}:[0-9]{2}", text)
    assert alleles, "expected HLA allele names in the rendered vaccine paper"
    lost = sorted({a for a in alleles if "*" not in a})
    assert not lost, f"these allele names lost their asterisk in the PDF: {lost}"


def test_the_leaked_escape_pattern_actually_matches_the_defect_it_is_for():
    """⛔ A GUARD THAT CANNOT FAIL IS NOT A GUARD. The pattern above is narrow on purpose, and a
    narrowing is exactly where a check quietly stops checking. These are the two renderings the
    incident actually produced, plus the continuation that must NOT match."""
    pat = r"\\[*_\[\]#A-Za-z0-9]"
    assert re.findall(pat, r"presented on HLA-B\*15:01 alone"), "the one-allele leak is not caught"
    assert re.findall(pat, r"HLA-A\01:01, HLA-B\07:02"), "the emphasis-eaten leak is not caught"
    assert not re.findall(pat, "DONOR_EXON_END=5 \\\n    python3 junction_aso.py"), (
        "a shell line continuation is content and must not be flagged")


# ---------------------------------------------------------------------------------------------
# ⛔⛔ ONE PAPER'S HANDLING FOOTER RODE EVERY OTHER PAPER'S PAGES, AND AN EXTERNAL REVIEWER FOUND IT.
# `build_submission_pdf.py` derived its running footer from a MODULE-level `STAMP_SOURCES` — the ASO
# paper's — so every page of the vaccine preprint carried "Order from fusion-junction-aso-sequences
# .csv, never from this PDF." That file is a set of antisense oligonucleotides; the vaccine paper is
# about peptides, never mentions the file, and has nothing to order. A reviewer of
# aixiv.260822.000005 reported the filename as an undefined term in a figure caption, which is what a
# page footer looks like once the text layer is flattened. Chrome that names a file the document does
# not is not typography — it is a false instruction pointing at a different molecule.

def _orderable_names(key):
    """The reagent files this paper tells a reader to ORDER FROM, in both its committed forms.

    ⚠ NARROWED ON PURPOSE, AND THE NARROWING IS THE POINT. The first version of this guard flagged
    every filename any paper declares, and promptly fired on the ASO journal article for naming
    `fusion-junction-aso-research-article.md` — its own extended report, cited in the text, exactly
    as it should be. A cross-reference between two papers is CONTENT and is often correct; a
    do-not-order-from-this-PDF instruction pointing at another paper's reagents is FURNITURE and is
    never correct. Only the second is a defect, so only the second is what this reads.
    """
    orderable = bsp.order_from(bsp.PAPERS[key])
    if not orderable:
        return set()
    return {orderable, orderable.replace(".csv", ".fasta")}


@pytest.mark.committed_artifact
@pytest.mark.parametrize("key", sorted(bsp.PAPERS))
def test_no_paper_is_stamped_with_another_papers_orderable_file(key):
    r"""The rendered PDF may only send a reader to a file that paper's own build declares.

    Read from the RENDERED text, not the source: the defect lives entirely in the page furniture,
    which no `.md` gate can see. Resolve the paper's declared main suffix when present; a missing
    declared PDF is a broken tree, not a reason to pass over the check.
    """
    paper = bsp.PAPERS[key]
    declared = paper["out"]
    main_suffix = paper.get("supplementary_presentation", {}).get("main_suffix")
    if main_suffix:
        declared = declared.replace(".pdf", main_suffix)
    pdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       *declared.split("/"))
    assert os.path.exists(pdf), (
        f"{declared} is missing. It is a committed deposit artifact, so rebuild it "
        "with build_submission_pdf.py rather than passing over the footer check.")
    text = _pdf_text(pdf)
    mine = _orderable_names(key)
    foreign = sorted({name
                      for other in bsp.PAPERS
                      for name in _orderable_names(other)
                      if name not in mine and name in text})
    assert not foreign, (
        f"{declared} sends its reader to {foreign} — another paper's reagent files, "
        "which this paper has none of and never declares. Check the running footer: it must come "
        "from handling_footers(paper), not from the module-level ORDER_FROM.")


@pytest.mark.parametrize("key", sorted(bsp.PAPERS))
def test_every_papers_footer_is_derived_from_its_own_sources(key):
    """The unit half of the guard above, so the rule holds for a paper before its first build."""
    paper = bsp.PAPERS[key]
    full, short = bsp.handling_footers(paper)
    orderable = bsp.order_from(paper)
    if "footer_text" in paper:
        assert orderable is None, "a neutral footer must not suppress reagent handling instructions"
        assert full == short == paper["footer_text"] and full.strip(), (
            "an explicit neutral footer must match its nonempty declaration in both lengths")
    else:
        assert "not for administration" in full and "not for administration" in short, (
            "the default handling prohibition must survive in both lengths")
    if orderable is None:
        assert full == short, (
            f"{key} has no orderable file, so there is no destination to state and the two lengths "
            "must be the same string — otherwise print_pdf grafts a page onto itself")
        assert ".csv" not in full, f"{key}'s footer names a file it has none of: {full!r}"
    else:
        assert orderable in full, f"{key}'s footer must name its own {orderable}"
        assert orderable in {os.path.basename(s)
                             for s in paper.get("stamp_sources", bsp.STAMP_SOURCES)}, (
            "the footer's filename must be READ from stamp_sources, never typed (rule 1)")


# ---------------------------------------------------------------------------------------------
# ⛔⛔ TWO BLOCK-LEVEL DEFECTS THAT ONLY A RASTERISED PAGE COULD SHOW (found 2026-08-24). Both were
# invisible to every text-layer check in this file, because both produce text that EXTRACTS
# correctly and RENDERS wrongly — the first prints a character a reader sees and a grep does not
# care about, the second deletes a sentence that no gate reads the built document to miss.

def test_a_blockquote_renders_as_a_blockquote_and_not_as_a_literal_marker():
    r"""⛔ THE PAPER'S TWO CENTRAL EQUATIONS SHIPPED WITH THEIR MARKER PRINTED, NINE TIMES.
    `markdown_to_html` had no blockquote branch at all, so `> C(A) = 1 - ...` fell through to the
    paragraph collector and `inline()` escaped the `>` faithfully into the body text of every posted
    version of aixiv.260822.000005."""
    html = bsp.markdown_to_html("> **C(A)  =  1  −  x**")
    assert "<blockquote>" in html, "a quoted line must produce a blockquote element"
    assert not re.search(r"<p[^>]*>\s*&gt;", html), "the marker must not survive into body text"


def test_a_multi_line_blockquote_is_one_block():
    """The seam test's statement wraps across two source lines and is one sentence."""
    html = bsp.markdown_to_html("> a junction whose seam residue lies in the alphabet\n"
                                "> has a window that is not tumour-exclusive.")
    assert html.count("<blockquote>") == 1
    assert "alphabet has a window" in html, "the two lines must join with a space between them"


def test_a_wrapped_number_stays_inside_its_paragraph():
    """⛔⛔ THE EXACT INPUT THAT DELETED A SENTENCE OF FIGURE 1'S LEGEND. The legend wraps as
    '...as internal residue' / '266. Four of the five...', and the line before it opens with `*j₀*`.
    The old guard called any line starting with `*` a list item, so `266.` opened an ordered list and
    SPLIT the caption; suppressing the list branch alone then made the paragraph collector stop
    there instead, `para` came back empty, and the fall-through advanced past the line — turning a
    layout defect into a content defect. CommonMark's actual rule is that an ordered marker may not
    interrupt a paragraph unless it numbers 1, and it has to hold in BOTH places."""
    src = ("**Figure 1. A legend.** Donor sequence ends mid-codon, giving the seam residue at\n"
           "*j₀* = 264, after which the acceptor resumes with its methionine 1 as internal residue\n"
           "266. Four of the five in-frame junctions place aspartate at this position.")
    html = bsp.markdown_to_html(src)
    assert "266. Four of the five" in html, (
        "the wrapped number and the rest of its sentence were dropped from the legend")
    assert "<ol" not in html, "a wrapped number must not open an ordered list"
    assert html.count("<p") == 1, "the legend is one paragraph and must render as one"


def test_a_real_numbered_list_still_renders_as_a_list():
    """⛔ THE OTHER HALF, WITHOUT WHICH THE FIX ABOVE IS JUST A DELETION. §2.2's derivation is a
    genuine six-item ordered list and must keep its markup."""
    html = bsp.markdown_to_html("Steps:\n\n1. Build the chimeric mRNA.\n2. Translate from the "
                                "initiator codon.\n3. Let j0 be the first residue.")
    assert "<ol" in html and html.count("<li>") == 3, "a list that opens a block is still a list"


def test_a_bulleted_list_after_an_italic_opening_line_is_unaffected():
    """The guard now tests for a marker, so an italic word at the start of the previous line no
    longer masquerades as one. A real bullet after ordinary prose must still start a list."""
    html = bsp.markdown_to_html("*Emphasis* opens this line and it is prose.\n\n- first\n- second")
    assert "<ul>" in html and html.count("<li>") == 2


def _literal_blockquote_markers(text):
    # A Markdown blockquote marker starts a line. Inline inequalities are mathematical content.
    return re.findall(r"(?m)^[ \t]*>[ \t]+[A-Za-z(]", text)


def test_blockquote_detection_catches_leaks_without_flagging_an_inequality():
    assert _literal_blockquote_markers("Title\n> C(A) = 1 - x\ncontinued"), (
        "a literal marker at the start of an extracted line must be detected")
    assert _literal_blockquote_markers("  > an indented leaked quote"), (
        "indentation must not conceal a literal marker")
    assert not _literal_blockquote_markers("A = P(EMC > comparator) + 0.5 P(tie)"), (
        "the probability definition in the figure is content, not a blockquote")


@pytest.mark.committed_artifact
@pytest.mark.parametrize("pdf", sorted(_glob.glob(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "*", "*.pdf"))))
def test_no_blockquote_marker_survives_into_a_deposited_pdf(pdf):
    """The rendered half of the guard above, over every built document in the tree."""
    leaked = _literal_blockquote_markers(_pdf_text(pdf))
    assert not leaked, (
        f"{os.path.basename(pdf)} prints {len(leaked)} literal blockquote marker(s) {leaked[:3]} — "
        "markdown_to_html must render a quoted line as a <blockquote>, not as body text.")



#: ⛔ THREE GUARDS WERE REMOVED HERE ON 2026-08-25, AND NOT BECAUSE THEY WERE WRONG.
#: `test_the_declared_fallback_for_figure_3_still_points_at_a_real_section`,
#: `test_wide_tables_go_on_landscape_pages_and_narrow_ones_do_not` and
#: `test_the_back_matter_is_split_out_of_the_two_column_body` each measured a builder feature
#: that only the extended report exercised: a third figure, a table wide enough for a
#: landscape page, and the two-column back-matter split. That paper left the gate, and no
#: remaining paper opts into any of the three — `aso-journal` sets `tables_in_column` and
#: `backmatter_in_flow`, and the other two papers carry no tables at all.
#: ⚠ SO THE FEATURES ARE NOW UNGUARDED, WHICH IS THE COST AND IS RECORDED RATHER THAN HIDDEN.
#: A paper that opts back into landscape tables, a split back matter or a `placement` map is
#: opting into code nothing tests. Restore the guard in the same change, from git history.
