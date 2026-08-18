#!/usr/bin/env python3
"""Render a submission manuscript from Markdown into ONE PDF, in either of two formats.

WHY. The ASO paper was preprint-ready by its own checklist and had no PDF, because the thing a
depositor uploads is not the thing this repository stores. The manuscript is one file, its tables
are a second generated file, its references a third, and its figures are three SVGs that the
manuscript refers to by legend and never embeds. Assembling that by hand at deposit time is exactly
the re-derivation CLAUDE.md rule 1 exists to stop, and it is where a stale table or a dropped
reference gets in.

TWO FORMATS, AND THEY ARE NOT INTERCHANGEABLE.

  --style journal      (default) Typeset as a published research article: two columns, a masthead
                       and title block, running heads, and every table and figure set at the point
                       it is first cited. This is what the work looks like in print.
  --style manuscript   Submission format: single column, justified, display items collected after
                       the text. This is the shape a journal portal and bioRxiv actually ask for,
                       and it is the one to upload.

⛔ NEITHER FORMAT EDITS THE PAPER. Tables and references are spliced in from their generated files
verbatim, so a number in the PDF and a number in the artifact it came from cannot diverge without
the generator being wrong first. The journal style REORDERS display items and nothing else — it
moves Table 2 to where Table 2 is first mentioned, which is a typesetting decision, not an
editorial one. The repo's own YAML frontmatter is internal routing and is stripped from both.

⛔ EVERY JOIN IS ANCHORED, NOT POSITIONAL. Splices are located by section heading, figures by their
legend opener, and floats by their first in-text citation. A missing anchor is a hard failure
rather than a silent no-op — a PDF that quietly lost its reference list looks exactly like one that
has it until somebody opens the last page.

⚠ NO NETWORK, NO PANDOC, NO LATEX. Rendering is Chromium's own print-to-PDF over a file:// page,
which is present in this container; figures are inlined as SVG markup so they stay VECTOR in the
output rather than being rasterised. build-preprint.yml remains the pandoc/DOCX route for venues
that want an editable file; this is the PDF route and it needs nothing installed.

    python3 research/manuscripts/build_submission_pdf.py
    python3 research/manuscripts/build_submission_pdf.py --paper aso --style manuscript
    python3 research/manuscripts/build_submission_pdf.py --html-only
"""
import argparse
import base64
import html as _html
import json
import hashlib
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIGDIR = os.path.join(HERE, "figures")

#: A table with more columns than this cannot be read at any font size that fits a portrait page,
#: so it is set on its own landscape page. Measured against this paper: Table 2 runs to twelve
#: columns and Table 4 to nine, and both are illegible full-width in portrait.
LANDSCAPE_MIN_COLS = 8

PAPERS = {
    "aso": {
        "manuscript": "aso/fusion-junction-aso-research-article.md",
        "tables": "aso/fusion-junction-aso-submission-tables.md",
        "references": "aso/fusion-junction-aso-submission-references.md",
        #: Legend prefix -> the SVG that legend describes. Stated rather than inferred from
        #: filename order, because `aso_figure_provenance.py` is explicit that nothing checks
        #: whether a legend describes its figure, and a silent mis-pairing is unreadable in a PDF.
        #: ⚠ RENUMBERED 2026-08-17 TO CITATION ORDER. The multi-partner seam is cited in §2.2 and
        #: the gap-length identity in §2.9, so numbering them 2 and 3 the other way round made the
        #: paper cite Figure 3 before Figure 2 — the order every journal style and every reader
        #: expects display items to run in. Was: Figure 2 = gap-length, Figure 3 = multi-partner.
        "figures": {
            "Figure 1.": "aso-junction-space.svg",
            "Figure 2.": "aso-multipartner-seam.svg",
            "Figure 3.": "aso-gap-length-tradeoff.svg",
            "Supplementary Figure S1.": "aso-chance-baseline.svg",
        },
        #: ⚠ THE CHANCE-BASELINE PANEL IS NEVER CITED BY NAME IN THE BODY, so the journal style
        #: has no anchor to float it to and would otherwise place it arbitrarily. It floats to the
        #: section that states the baseline it draws — the 8.2 expectation against the measured
        #: 718,571,139-nucleotide span. Declared here rather than guessed at render time, and the
        #: build fails if an uncited item has no declaration.
        #: ⚠ RENUMBERED 2026-08-15: it was Figure 3 until a fourth panel was added and pushed it to
        #: the supplement. Which of the other two is Figure 2 changed again on 2026-08-17; this
        #: panel is supplementary either way, because it is cited nowhere in the body.
        #: ⚠ RE-ANCHORED 2026-08-16 from the number "3.10" to heading TEXT: the editorial pass
        #: merged that subsection away and the build failed on a stale number. Numbers drift here
        #: roughly every restructure; the title travels with the argument.
        "placement": {"Supplementary Figure S1": {"after_heading": "conditions for falsification"}},
        "journal": {
            "article_type": "Research article",
            "section": "Cancer genomics · RNA therapeutics",
            # ⛔ THE MASTHEAD MUST NOT ASSERT A POSTING THAT HAS NOT HAPPENED (blind screen of the
            # journal build, 2026-08-17). It read "Posted to bioRxiv under CC-BY" on page 1
            # while the author block on the SAME page carried "the deposit is blocked until it
            # is replaced" and Availability said no DOI has been reserved — two contradictory
            # statements about the document's own publication status, side by side. The licence
            # is also chosen AT submission, so pre-declaring it is a second small untruth.
            "preprint_note": "Preprint — not peer reviewed. Prepared for deposit; not yet posted.",
        },
        "out": "aso/fusion-junction-aso-research-article.pdf",
    },
}


# --------------------------------------------------------------------------- reading

def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        return fh.read()


def strip_frontmatter(text):
    """Drop a leading YAML block. Repo frontmatter is routing metadata, not manuscript."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end != -1:
            return text[end + 5:]
    return text


def strip_generated_banner(text):
    """Drop the leading HTML comment and the H1 from a generated include."""
    text = re.sub(r"^<!--.*?-->\s*", "", text, flags=re.S)
    return re.sub(r"^#\s+[^\n]*\n", "", text.lstrip(), count=1).strip()


def section_span(body, heading):
    """(start, end) of the content under `## heading`, exclusive of the heading line."""
    pattern = re.compile(r"(^##\s+" + re.escape(heading) + r"\s*$)(.*?)(?=^##\s|\Z)", re.M | re.S)
    match = pattern.search(body)
    if not match:
        raise SystemExit(f"anchor not found: '## {heading}' — the manuscript's section headings "
                         f"changed, so this splice would have silently dropped content")
    return match.start(1), match.end(2), match.end(1)


def splice(body, heading, replacement, label):
    """Replace the pointer paragraph under `heading` with `replacement`."""
    try:
        _, end, after_heading = section_span(body, heading)
    except SystemExit:
        raise SystemExit(f"anchor not found: '## {heading}' ({label}) — the manuscript's section "
                         f"headings changed, so the splice would have dropped {label}")
    return body[:after_heading] + "\n\n" + replacement + "\n\n" + body[end:]


# --------------------------------------------------------------------------- display items

def split_tables(tables_md):
    """Split the generated tables file into one markdown block per table, keyed by number.

    A block is a caption paragraph, any footnotes, and the pipe table itself — everything from
    `**Table N.` up to the next `**Table N+1.`.
    """
    starts = [(int(m.group(1)), m.start())
              for m in re.finditer(r"^\*\*Table (\d+)\.", tables_md, re.M)]
    if not starts:
        raise SystemExit("no '**Table N.' blocks found in the generated tables file")
    blocks = {}
    for i, (number, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(tables_md)
        blocks[number] = tables_md[start:end].strip()
    return blocks


#: ⚠ A SUPPLEMENTARY FIGURE SORTS AFTER EVERY NUMBERED ONE, WHICH IS WHY IT IS NOT JUST "S1".
#: `split_figures` keys blocks by a sortable number and the renderer lays them out in that order.
#: Giving a supplementary panel the key 1 would float it between Figures 1 and 2; this offset puts
#: S1 after Figure N for any N a paper will ever have, without special-casing the layout code.
SUPPLEMENTARY_SORT_BASE = 1000


def split_figures(body, figures):
    """One block per figure: the SVG markup plus the legend paragraph that describes it."""
    _, end, after_heading = section_span(body, "Figure legends")
    legends = body[after_heading:end]
    blocks = {}
    for prefix, svgname in figures.items():
        m = re.match(r"(?:Supplementary )?Figure S?(\d+)\.", prefix)
        if not m:
            raise SystemExit(f"figure key {prefix!r} is neither 'Figure N.' nor "
                             f"'Supplementary Figure SN.'")
        number = int(m.group(1)) + (SUPPLEMENTARY_SORT_BASE if "Supplementary" in prefix else 0)
        match = re.search(r"^\*\*" + re.escape(prefix)
                          + r".*?(?=^\*\*(?:Supplementary )?Figure S?\d+\.|\Z)",
                          legends, re.M | re.S)
        if not match:
            raise SystemExit(f"no legend found for {svgname}: expected a paragraph "
                             f"opening '**{prefix}'")
        svg = open(os.path.join(FIGDIR, svgname), encoding="utf-8").read().strip()
        blocks[number] = (svg, match.group(0).strip())
    return blocks


def table_columns(block):
    header = next((ln for ln in block.split("\n") if ln.strip().startswith("|")), "")
    return len([c for c in header.strip().strip("|").split("|")])


def drop_section(body, heading):
    start, end, _ = section_span(body, heading)
    return body[:start] + body[end:]


def first_citation_end(body, label):
    """End offset of the paragraph that first cites `label` in the running text."""
    match = re.search(rf"\b{re.escape(label)}\b", body)
    if not match:
        return None
    end = body.find("\n\n", match.end())
    return len(body) if end == -1 else end


def heading_section_end(body, phrase):
    """End offset of the section whose heading contains `phrase`, for a declared placement.

    ⚠ ANCHOR ON HEADING TEXT, NEVER ON A SECTION NUMBER. This took a number until 2026-08-16 and
    broke when an editorial pass merged §3.10 into a renumbered section — the same drift that makes
    this repo forbid citing a § number anywhere a quote would do. A title moves with its content;
    a number does not. The match is case-insensitive and may name any heading level.
    """
    match = re.search(rf"^#{{2,4}}\s+.*{re.escape(phrase)}.*$", body, re.M | re.I)
    if not match:
        raise SystemExit(
            f"declared placement anchor — a heading containing {phrase!r} — not found. The section "
            f"was renamed or removed; update the paper's `placement` map to the heading that now "
            f"carries this content, rather than deleting the declaration.")
    level = len(re.match(r"^#+", match.group(0)).group(0))
    nxt = re.search(rf"^#{{2,{level}}}\s", body[match.end():], re.M)
    return match.end() + (nxt.start() if nxt else len(body) - match.end())


def place_floats(body, items, placement):
    """Insert each display item at its first in-text citation.

    Offsets are ALL computed against the original body before anything is inserted, so an item's
    anchor cannot be moved by an earlier insertion, and a table's own caption cannot be mistaken
    for the body's first mention of a later table.
    """
    points = []
    for label, token in items:
        end = first_citation_end(body, label)
        if end is None:
            declared = placement.get(label)
            if not declared or "after_heading" not in declared:
                raise SystemExit(
                    f"{label} is never cited in the body and has no declared placement. Add one to "
                    f"the paper's `placement` map with the reason, rather than letting the layout "
                    f"drop it somewhere arbitrary.")
            end = heading_section_end(body, declared["after_heading"])
        points.append((end, token))

    out, last = [], 0
    for end, token in sorted(points):
        out.append(body[last:end])
        out.append(f"\n\n{token}\n")
        last = end
    out.append(body[last:])
    return "".join(out)


# --------------------------------------------------------------------------- assembly

def assemble(paper, style="journal"):
    """Return (markdown, prerendered_floats). In manuscript style the float map is empty."""
    body = strip_frontmatter(read(paper["manuscript"]))
    tables = split_tables(strip_generated_banner(read(paper["tables"])))
    references = strip_generated_banner(read(paper["references"]))

    if style == "manuscript":
        body = splice(body, "Tables", "\n\n".join(tables[n] for n in sorted(tables)), "the tables")
        body = splice(body, "References", references, "the reference list")
        # ⚠ THE FIRST FIGURE IS MARKED, because it is the one that must NOT start a fresh page:
        # the section opens with a heading and a two-sentence preamble, and forcing a page break
        # ahead of every figure left those three lines alone on a page of their own.
        for index, (prefix, svgname) in enumerate(paper["figures"].items()):
            svg = open(os.path.join(FIGDIR, svgname), encoding="utf-8").read().strip()
            anchor = "**" + prefix
            if anchor not in body:
                raise SystemExit(f"no legend found for {svgname}: expected '{anchor}'")
            klass = "figure lead" if index == 0 else "figure"
            body = body.replace(
                anchor, f'\n<figure class="{klass}">\n{svg}\n</figure>\n\n' + anchor, 1)
        return body, {}

    figures = split_figures(body, paper["figures"])
    body = splice(body, "References", references, "the reference list")
    body = drop_section(body, "Tables")
    body = drop_section(body, "Figure legends")

    floats, items = {}, []
    for number in sorted(tables):
        token = f"@@FLOAT:table{number}@@"
        wide = table_columns(tables[number]) >= LANDSCAPE_MIN_COLS
        floats[token] = ("table", number, tables[number], wide)
        items.append((f"Table {number}", token))
    for number in sorted(figures):
        token = f"@@FLOAT:figure{number}@@"
        floats[token] = ("figure", number, figures[number], False)
        # ⚠ THE CITATION LABEL MUST BE THE STRING THE BODY ACTUALLY USES, not the sort key. A
        # supplementary panel is keyed above SUPPLEMENTARY_SORT_BASE so it lays out last, and
        # searching the body for "Figure 1001" would find nothing and report it as uncited.
        label = (f"Supplementary Figure S{number - SUPPLEMENTARY_SORT_BASE}"
                 if number >= SUPPLEMENTARY_SORT_BASE else f"Figure {number}")
        items.append((label, token))

    body = place_floats(body, items, paper.get("placement", {}))
    return body, floats


# --------------------------------------------------------------------------- markdown

KEEP_TAGS = ("sup", "sub", "i", "em", "b", "strong")
TAG_RE = re.compile(r"</?(?:" + "|".join(KEEP_TAGS) + r")>", re.I)

#: A delimited oligonucleotide as the paper prints it: `5′-BASES-3′`. Bounded at both ends so a
#: bare base run in prose is not caught, and generous on length so an 18-mer or a 20-mer from the
#: gap-length comparison is wrapped by the same rule as a 16-mer.
#: ⛔ MEASURED 2026-08-17 IN THE BUILT PDF, NOT IN THE MARKDOWN. The hyphens either side of the
#: bases are ordinary line-break opportunities, so justified prose and narrow table cells both broke
#: after `5′-` — 50 times in the manuscript-style PDF and 57 times in the journal-style one. No base
#: string was ever split, so the orderable-sequence guard stayed green, but the delimiter that makes
#: the string unambiguous ended up on the previous line and a copy-paste carried a newline through
#: the middle of the reagent name. The span below is set `white-space: nowrap` so the whole token
#: moves to the next line intact.
SEQUENCE_RE = re.compile(r"5[′']-[ACGTUacgtu]{8,40}-3[′']")

#: Identifiers that must never be split by a line or page break. A reader copy-pasting one
#: that broke across a page picks up the running header and the page number between its
#: halves, and the result resolves to nothing.
#: ⛔ MEASURED IN THE BUILT PDF (blind screen, 2026-08-17): the DepMap model identifier split
#: across the p.15/16 boundary as "model ACH-" ... "001519". The break fell on the
#: identifier's own hyphen, so no spurious character was introduced — which is exactly why it
#: survived every source-side check: the MARKDOWN is correct and the defect is created by
#: typesetting.
#: Covers DepMap models (ACH-######), Cellosaurus RRIDs (with or without the RRID: prefix)
#: and GEO series (GSE#####).
ATOMIC_ID_RE = re.compile(r"\b(?:RRID:CVCL_[A-Za-z0-9]+|CVCL_[A-Za-z0-9]+|ACH-\d{6}|GSE\d{4,6})\b")

#: Where a long inline-code token MAY break, if it has to. Breaking is offered after a separator,
#: never inside a run of word characters — `word-break: break-all` used to allow the latter and
#: produced "as / o-premrna-offtarget-genomic.json", "PRE / FLIGHT_FULL=1",
#: "github.com/tr / imcrae/Rare-cancers", "emc-atr-vulnerability.j / son" and
#: "aso_genome_offtarg / et.py" in the deposited PDF. A break after `/`, `_`, `.` or `-` leaves both
#: halves readable as fragments of a path, and the CSS beside it forbids every other break point.
CODE_BREAK_AFTER = re.compile(r"(?<=[/_.=-])(?=[^\s/_.=-])")

#: Above this many characters a code span stops being set `nowrap` and is given the break
#: opportunities above instead. The narrowest container either style produces is the journal's
#: 88 mm text column, which holds about 53 characters of 7.74 pt DejaVu Sans Mono, so a span at or
#: under this length cannot overflow it. ⚠ The threshold is what keeps `nowrap` from becoming an
#: overflow bug the day a longer path is cited: today's longest span is 39 characters, and nothing
#: about that is guaranteed to hold.
CODE_NOWRAP_MAX = 44


def escape_text(text):
    out, last = [], 0
    for m in TAG_RE.finditer(text):
        out.append(_html.escape(text[last:m.start()], quote=False))
        out.append(m.group(0).lower())
        last = m.end()
    out.append(_html.escape(text[last:], quote=False))
    return "".join(out)


def code_span(literal):
    """One `<code>` element, set so it can never break in the middle of an identifier.

    Short spans are atomic — `nowrap` moves the whole token to the next line rather than splitting
    it. A span too long to guarantee it fits the narrowest column is allowed to wrap, but only at
    the separators `CODE_BREAK_AFTER` names, and `<wbr/>` is used rather than a zero-width space so
    nothing extra lands in the PDF's text layer for a reader to copy out.
    """
    escaped = _html.escape(literal, quote=False)
    if len(literal) <= CODE_NOWRAP_MAX:
        return "<code>" + escaped + "</code>"
    return '<code class="brk">' + CODE_BREAK_AFTER.sub("<wbr/>", escaped) + "</code>"


def inline(text):
    """Inline markdown. Code spans are protected first so their contents are never re-parsed."""
    text = _html.unescape(text)
    stash = []

    def keep(fragment):
        stash.append(fragment)
        return f"\x00{len(stash) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: keep(code_span(m.group(1))), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: keep('<a href="' + _html.escape(m.group(2), quote=True) + '">'
                                 + escape_text(m.group(1)) + "</a>"), text)
    text = escape_text(text)
    # ⚠ AFTER escaping and BEFORE emphasis: the pattern is pure ASCII bases between two primes, so
    # escaping cannot change it and stashing it here keeps a `*` in the surrounding sentence from
    # ever reaching inside the span.
    text = SEQUENCE_RE.sub(lambda m: keep('<span class="seq">' + m.group(0) + "</span>"), text)
    text = ATOMIC_ID_RE.sub(lambda m: keep('<span class="seq">' + m.group(0) + "</span>"), text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)


def render_table(rows):
    def cells(line):
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]

    head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
    out = ["<table>", "<thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def markdown_to_html(text, floats=None):
    floats = floats or {}
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)          # PMID markers: non-rendering
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped in floats:
            out.append(render_float(*floats[stripped]))
            i += 1
            continue

        if stripped.startswith("<figure") or stripped.startswith("</figure"):
            out.append(stripped)
            i += 1
            continue
        if stripped.startswith("<svg"):
            block = []
            while i < len(lines) and not lines[i].strip().startswith("</figure"):
                block.append(lines[i])
                i += 1
            out.append("\n".join(block))
            continue

        if re.match(r"^-{3,}$", stripped):
            out.append("<hr/>")
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and re.match(
                r"^\|[\s:|-]+\|?\s*$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append('<div class="tablewrap">' + render_table(rows) + "</div>")
            continue

        item = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if item:
            ordered = item.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            start = re.match(r"^\s*(\d+)\.", line)
            attr = f' start="{start.group(1)}"' if ordered and start else ""
            out.append(f"<{tag}{attr}>")
            while i < len(lines):
                m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not m:
                    if lines[i].strip() and lines[i].startswith((" ", "\t")):
                        out[-1] = out[-1][:-5] + " " + inline(lines[i].strip()) + "</li>"
                        i += 1
                        continue
                    break
                out.append("<li>" + inline(m.group(3)) + "</li>")
                i += 1
            out.append(f"</{tag}>")
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|\||-{3,}$|\s*([-*]|\d+\.)\s|<figure|<svg|@@FLOAT)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        if para:
            joined = " ".join(para)
            opener = re.match(r"^\*\*(Figure|Table) \d+\.", joined)
            # ⚠ A TABLE CAPTION AND A FIGURE LEGEND SIT ON OPPOSITE SIDES OF THEIR ITEM, so they
            # cannot carry the same break rule: a legend must stay with the figure ABOVE it and a
            # caption with the table BELOW it. They shared one class until 2026-08-17 and the
            # caption therefore had no rule at all.
            css = ""
            if opener:
                css = ' class="legend caption"' if opener.group(1) == "Table" else ' class="legend"'
            out.append(f"<p{css}>{inline(joined)}</p>")
        else:
            i += 1
    return "\n".join(out)


def render_float(kind, number, payload, wide):
    """A table or figure set as a float, with its caption."""
    classes = ["float", kind]
    if wide:
        classes.append("landscape-float")
    else:
        classes.append("span-float")
    if kind == "figure":
        svg, legend = payload
        inner = f'<div class="panel">{svg}</div>' + markdown_to_html(legend)
    else:
        inner = markdown_to_html(payload)
    return f'<div class="{" ".join(classes)}" id="{kind}{number}">{inner}</div>'


# --------------------------------------------------------------------------- front matter

def label_paragraph(body, label, what=None):
    """The text under a `**Label.**` front-matter line, whole paragraph, emphasis stripped.

    ⚠ CAPTURE THE WHOLE PARAGRAPH, NOT THE FIRST LINE — these fields wrap in the source.
    """
    match = re.search(rf"^\*\*{re.escape(label)}\.\*\*[^\n]*(?:\n(?!\s*\n)[^\n]*)*", body, re.M)
    if not match:
        raise SystemExit(f"front matter {what or f'label {label!r}'} not found")
    text = re.sub(r"\s*\n\s*", " ", match.group(0)).strip()
    return text[len(f"**{label}.**"):].strip()


def declared_running_title(body):
    """The short title the manuscript DECLARES, for the head of every page.

    ⛔ IT IS PARSED, NEVER TYPED HERE. The manuscript states "**Running title.** …" in its front
    matter precisely so the header and the declaration cannot diverge; a string retyped in the
    builder is a second home for the same fact and would go stale silently (rule 1).

    ⛔ AND THE MANUSCRIPT STYLE USED TO IGNORE IT (measured 2026-08-17). The journal style read the
    declaration; the manuscript style passed the H1, so all 54 pages of the file a depositor
    actually uploads carried the full 30-word title, set at 5.2 pt to make it fit — declaring a
    running title on page 1 and then not using it anywhere.
    """
    return re.sub(r"[*_`]", "", label_paragraph(body, "Running title", "the running title"))


def parse_front_matter(body):
    """Pull the title block and abstract out of the manuscript head.

    Anchored on the labels the manuscript actually uses. A renamed label fails the build rather
    than producing an article with no author line.
    """
    front = {}
    title = re.search(r"^#\s+(.*)$", body, re.M)
    if not title:
        raise SystemExit("no H1 title found in the manuscript")
    front["title"] = title.group(1)

    # ⚠ CAPTURE THE WHOLE PARAGRAPH, NOT THE FIRST LINE. These fields wrap in the source, and a
    # `.*$` match silently dropped the tail — the keyword list lost "myxoid chondrosarcoma" and the
    # author block lost its ORCID line, both of which a reader would assume were simply absent.
    def paragraph(pattern, what):
        match = re.search(pattern + r"[^\n]*(?:\n(?!\s*\n)[^\n]*)*", body, re.M)
        if not match:
            raise SystemExit(f"front matter {what} not found")
        return re.sub(r"\s*\n\s*", " ", match.group(0)).strip()

    for key, label in (("author", "Author"), ("running", "Running title"),
                       ("keywords", "Keywords")):
        front[key] = label_paragraph(body, label, f"label '**{label}.**'")

    front["affiliation"] = paragraph(r"^\*Independent researcher", "the affiliation line")

    _, end, after = section_span(body, "Abstract")
    front["abstract"] = body[after:end].strip().strip("-").strip()

    start = re.search(r"^##\s+1\s", body, re.M)
    if not start:
        raise SystemExit("could not find '## 1 …' — the body must start at the first numbered "
                         "section, or the front matter would be duplicated into it")
    front["body"] = body[start.start():]
    return front


# --------------------------------------------------------------------------- styles

COMMON = """
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
sup { font-size: 0.72em; line-height: 0; }
/* ⛔ `word-break: break-all` USED TO BE HERE AND IT BROKE FILENAMES MID-TOKEN. Measured in the
   built PDF 2026-08-17: "as / o-premrna-offtarget-genomic.json", "PRE / FLIGHT_FULL=1",
   "github.com/tr / imcrae/Rare-cancers", "emc-atr-vulnerability.j / son", "aso_genome_offtarg /
   et.py". A path a reader cannot retype is worse than a ragged line, so a code span is atomic and
   only `code.brk` — a span long enough to risk overflowing a column — may wrap, at the `<wbr/>`
   boundaries the builder puts after its separators and nowhere else. */
code { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 0.86em;
       background: #f4f4f4; padding: 0 2px; border-radius: 2px;
       white-space: nowrap; word-break: normal; overflow-wrap: normal; hyphens: none; }
code.brk { white-space: normal; }
/* A delimited oligonucleotide is one token: `5′-` must never be left on the line above its bases,
   because the newline a reader then copies is invisible in a synthesis order form. */
.seq { white-space: nowrap; hyphens: none; }
a { color: #14507d; text-decoration: none; }
table { border-collapse: collapse; width: 100%; font-family: 'Liberation Sans', Helvetica, Arial,
        sans-serif; line-height: 1.28; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
/* ⚠ `overflow-wrap: anywhere` — the obvious choice for a twelve-column table — also shrinks a
   cell's MIN-CONTENT width to a single character, so the browser sized every column far too narrow
   and broke headers mid-word ("designs screene / d"). `break-word` wraps at spaces and breaks only
   a word that genuinely cannot fit, which is what the long oligo sequences need. */
th, td { border: 0.4pt solid #b9c2cb; padding: 2.2pt 3.2pt; text-align: left;
         vertical-align: top; overflow-wrap: break-word; word-break: normal; hyphens: none; }
th { background: #eaeef2; font-weight: 600; }
tbody tr:nth-child(even) { background: #fafbfc; }
figure.figure svg, .panel svg { max-width: 100%; height: auto; }
"""

MANUSCRIPT_CSS = COMMON + """
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
@page landscape { size: A4 landscape; margin: 16mm 14mm; }
body { font-family: 'Liberation Serif', 'Times New Roman', Times, serif; font-size: 10.5pt;
       line-height: 1.5; color: #111; margin: 0; hyphens: auto; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 14pt 0; font-weight: 600; }
h2 { font-size: 13pt; margin: 20pt 0 6pt 0; font-weight: 600;
     border-bottom: 0.5pt solid #ccc; padding-bottom: 3pt; break-after: avoid; }
h3 { font-size: 11pt; margin: 14pt 0 4pt 0; font-weight: 600; break-after: avoid; }
p { margin: 0 0 8pt 0; text-align: justify; }
hr { border: 0; border-top: 0.5pt solid #ddd; margin: 14pt 0; }
ol, ul { margin: 0 0 8pt 0; padding-left: 18pt; }
li { margin-bottom: 4pt; text-align: justify; }
#references-list li { text-align: left; }
/* ⛔ `break-inside: auto` LET A TABLE ORPHAN ITS LAST ROW (measured 2026-08-17). Table 4's caption
   reads "The 9 designs with no sense-strand near-match" and eight rows printed on one landscape
   page, the ninth alone on the next directly above Table 5's caption, while the page it came from
   ended roughly 40% blank. A reader skimming the first page counts eight designs and the table
   contradicts its own title. A table taller than a page still breaks — the browser cannot honour
   this when it is impossible — and `thead { display: table-header-group }` above repeats the column
   heads onto each fragment when it does. */
/* ⚠ AND THE BOX THAT AVOIDS BREAKING IS THE TABLE ALONE, NOT THE CAPTION BLOCK WITH IT. Grouping
   caption, footnotes and table into one unbreakable box was tried and measured on 2026-08-17: it
   cost two pages and four extra pages under 45% full, and it did not even bind Table 4 — that
   caption plus its footnotes plus its nine rows is taller than a landscape page, so the group broke
   anyway and only the page before it was left short. The caption is instead held to what follows it
   by `break-after: avoid` below, which is free when the two do fit and harmless when they cannot. */
.tablewrap { break-inside: avoid; margin: 0 0 12pt 0; }
table { font-size: 7.4pt; }
/* Each display item takes its own page, EXCEPT the first: `break-before: page` on every figure left
   the "Figure legends" heading and its two-sentence preamble alone on a page with nothing under
   them (measured 2026-08-17). The first figure now follows the preamble it belongs to. */
figure.figure { margin: 0 0 6pt 0; text-align: center; break-inside: avoid; break-before: page; }
figure.figure.lead { break-before: auto; }
figure.figure svg { max-height: 218mm; width: auto; }
p.legend { font-size: 9pt; text-align: left; margin-bottom: 16pt; break-before: avoid;
           break-inside: avoid; }
/* A table caption must not be stranded at the foot of a page away from its table. */
p.legend.caption { break-before: auto; break-after: avoid; margin-bottom: 4pt; }
section.landscape { page: landscape; }
"""

JOURNAL_CSS = COMMON + """
@page { size: A4; margin: 16mm 14mm 15mm 14mm; }
@page landscape { size: A4 landscape; margin: 14mm 12mm; }

body { font-family: 'Liberation Serif', 'Times New Roman', Times, serif; font-size: 9pt;
       line-height: 1.40; color: #14181c; margin: 0; hyphens: auto; }

/* --- masthead and title block, full width above the columns --- */
.masthead { border-top: 2.4pt solid #123a5e; border-bottom: 0.5pt solid #123a5e;
            padding: 4pt 0 4pt 0; margin-bottom: 12pt; display: flex;
            justify-content: space-between; font-family: 'Liberation Sans', Helvetica, sans-serif;
            font-size: 7.4pt; letter-spacing: 0.06em; text-transform: uppercase; color: #123a5e; }
.masthead .right { color: #5a6b7a; letter-spacing: 0.02em; text-transform: none; }
h1.title { font-size: 18pt; line-height: 1.18; margin: 0 0 8pt 0; font-weight: 700;
           letter-spacing: -0.005em; color: #0e1b28; }
.byline { font-size: 10pt; margin: 0 0 2pt 0; font-weight: 600; }
.affil { font-size: 8.4pt; color: #46545f; margin: 0 0 10pt 0; font-style: italic; }
.affil .corr { font-style: normal; }

.abstract { background: #f4f7fa; border-left: 2.4pt solid #123a5e; padding: 8pt 10pt;
            margin: 0 0 8pt 0; font-size: 8.8pt; line-height: 1.42; }
.abstract h2 { font-family: 'Liberation Sans', Helvetica, sans-serif; font-size: 7.6pt;
               text-transform: uppercase; letter-spacing: 0.09em; color: #123a5e;
               margin: 0 0 4pt 0; border: 0; }
.abstract p { margin: 0; text-align: justify; }
.kw { font-size: 8.2pt; color: #46545f; margin: 0 0 12pt 0; }
.kw strong { color: #123a5e; }

/* --- the two-column text body --- */
.cols { column-count: 2; column-gap: 6mm; column-fill: auto; }
.cols h2 { font-family: 'Liberation Sans', Helvetica, sans-serif; font-size: 9.4pt;
           margin: 11pt 0 4pt 0; font-weight: 700; color: #123a5e; break-after: avoid; }
.cols h3 { font-family: 'Liberation Sans', Helvetica, sans-serif; font-size: 8.4pt;
           margin: 8pt 0 3pt 0; font-weight: 700; color: #2c3f4f; break-after: avoid; }
.cols h2:first-child { margin-top: 0; }
p { margin: 0 0 5pt 0; text-align: justify; }
.cols > p + p { text-indent: 1.1em; }
hr { display: none; }
ol, ul { margin: 0 0 6pt 0; padding-left: 13pt; }
li { margin-bottom: 3pt; text-align: justify; }

/* --- floats: tables and figures set where they are first cited --- */
.float { break-inside: avoid; margin: 4pt 0 9pt 0; }
.span-float { column-span: all; }
.float table { font-size: 6.9pt; }
.float p { font-size: 7.6pt; line-height: 1.32; text-align: left; text-indent: 0;
           margin: 0 0 3pt 0; color: #2c3f4f; }
.float p:first-child { color: #14181c; }
.float p strong:first-child { color: #123a5e; }
.float .panel { text-align: center; margin-bottom: 4pt; }
.float.figure .panel svg { max-height: 205mm; width: auto; }
.tablewrap { break-inside: auto; margin: 2pt 0 0 0; }

/* A twelve-column table is illegible at any portrait width, so it takes a landscape page. */
.landscape-float { page: landscape; break-before: page; break-after: page; column-span: all; }
.landscape-float table { font-size: 7.4pt; }
.landscape-float p { font-size: 8pt; }

/* --- back matter --- */
.backmatter { column-count: 2; column-gap: 6mm; font-size: 7.9pt; line-height: 1.36; }
.backmatter h2 { font-family: 'Liberation Sans', Helvetica, sans-serif; font-size: 8.6pt;
                 color: #123a5e; margin: 9pt 0 4pt 0; font-weight: 700; break-after: avoid; }
.backmatter h2:first-child { margin-top: 0; }
.backmatter p { margin: 0 0 4pt 0; }
#references-list { padding-left: 11pt; }
#references-list li { text-align: left; margin-bottom: 2.6pt; }
"""


def wrap_manuscript(front_title, body_html):
    body_html = re.sub(r"(<h2>Tables</h2>)(.*?)(?=<h2>)",
                       lambda m: '<section class="landscape">' + m.group(1) + m.group(2)
                       + "</section>", body_html, count=1, flags=re.S)
    body_html = re.sub(r"(<h2>References</h2>.*?)<ol", r'\1<ol id="references-list"',
                       body_html, count=1, flags=re.S)
    return page_shell(front_title, MANUSCRIPT_CSS, body_html)


#: One `<div class="float … landscape-float" id="…">…</div>`, matched by its opening tag and closed
#: by depth counting rather than by a lazy `.*?`: a float contains nested divs, so a non-greedy
#: match closes on the FIRST `</div>` and truncates the table.
_LANDSCAPE_FLOAT_OPEN = re.compile(r'<div class="[^"]*landscape-float[^"]*"[^>]*>')
_DIV_TAG = re.compile(r"<div\b[^>]*>|</div>")


def _extract_div(html, start):
    """(end_index) of the `</div>` closing the div that opens at `start`."""
    depth = 0
    for m in _DIV_TAG.finditer(html, start):
        depth += 1 if m.group(0) != "</div>" else -1
        if depth == 0:
            return m.end()
    raise SystemExit("a landscape float is unclosed — the float renderer emitted unbalanced HTML")


def _defer_landscape_floats(main):
    """Move each landscape float to the end of the section it is cited in, not its citation point.

    ⛔ WHY. `.landscape-float` carries `break-before: page`, so a landscape table set at the exact
    paragraph that first cites it ends the current page THERE. Two independent blind screens of the
    built journal PDF reported the consequence: page 15 carried two short column fragments and was
    otherwise white, because Table 5's citation fell a few lines into a page and the forced break
    took the rest of it. The table is right, the prose is right, and the page is 94% empty.

    ★ DEFERRED, NOT RELOCATED WHOLESALE. The float still lands inside the section that cites it and
    still precedes the next heading, so the journal style's property — a display item appears with
    the argument that uses it, rather than being collected at the back — survives. What changes is
    that the prose between the citation and the end of the section flows first and fills the page.

    ⚠ IF A SECTION HAS NO FOLLOWING HEADING the float stays where it is: the end of the section and
    its current position are the same place, and a fallback that moved it to the end of the document
    would silently undo the property above.
    """
    while True:
        opening = _LANDSCAPE_FLOAT_OPEN.search(main)
        if not opening or "data-deferred" in opening.group(0):
            break
        end = _extract_div(main, opening.start())
        block = main[opening.start():end].replace("<div class=", '<div data-deferred="1" class=', 1)
        rest = main[end:]
        heading = re.search(r"<h[23]\b", rest)
        if not heading:
            main = main[:opening.start()] + block + rest
            continue
        main = main[:opening.start()] + rest[:heading.start()] + block + rest[heading.start():]
    return main.replace(' data-deferred="1"', "")


def wrap_journal(paper, front, body_html):
    meta = paper.get("journal", {})
    body_html = re.sub(r"(<h2>References</h2>.*?)<ol", r'\1<ol id="references-list"',
                       body_html, count=1, flags=re.S)
    # Declarations and the reference list are back matter: smaller, and outside the main flow.
    split = re.search(r"<h2>Declarations</h2>", body_html)
    if not split:
        raise SystemExit("no '## Declarations' heading — the back matter split is anchored on it")
    main, back = body_html[:split.start()], body_html[split.start():]
    main = _defer_landscape_floats(main)

    head = (
        '<div class="masthead"><div>' + _html.escape(meta.get("article_type", "Article"))
        + " &nbsp;·&nbsp; " + _html.escape(meta.get("section", "")) + "</div>"
        '<div class="right">' + _html.escape(meta.get("preprint_note", "")) + "</div></div>"
        f'<h1 class="title">{inline(front["title"])}</h1>'
        f'<p class="byline">{inline(front["author"])}</p>'
        f'<p class="affil">{inline(front["affiliation"])}</p>'
        '<div class="abstract"><h2>Abstract</h2>'
        f'<p>{inline(front["abstract"])}</p></div>'
        f'<p class="kw"><strong>Keywords</strong> &nbsp;{inline(front["keywords"])}</p>'
    )
    return page_shell(re.sub(r"[*_`]", "", front["title"]), JOURNAL_CSS,
                      head + f'<div class="cols">{main}</div>'
                      + f'<div class="backmatter">{back}</div>')


def page_shell(title, css, body_html):
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"/>"
            f"<title>{_html.escape(title)}</title><style>{css}</style></head>"
            f"<body>\n{body_html}\n</body></html>\n")


# --------------------------------------------------------------------------- chromium

def find_chrome():
    import glob
    for candidate in (
        os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"),
                     "chromium-1194", "chrome-linux", "chrome"),
        "/opt/pw-browsers/chromium/chrome-linux/chrome",
    ):
        if os.path.exists(candidate):
            return candidate
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    hits = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    return hits[0] if hits else None


class WS:
    """The smallest RFC6455 client that can carry one printToPDF response.

    Chromium's CLI --print-to-pdf cannot set a running head or a page number, so those need
    DevTools. The response is a megabyte of base64 and arrives fragmented, which is the only reason
    this handles continuation frames and 64-bit lengths at all.
    """

    def __init__(self, url):
        _, rest = url.split("://", 1)
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((
            f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self.next_id = 0

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("devtools socket closed mid-frame")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        payload = b""
        while True:
            b0, b1 = self._read(2)
            length = b1 & 0x7F
            if length == 126:
                length = struct.unpack(">H", self._read(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._read(8))[0]
            payload += self._read(length)
            if b0 & 0x80:
                return json.loads(payload.decode("utf-8"))

    def call(self, method, **params):
        self.next_id += 1
        msg = json.dumps({"id": self.next_id, "method": method, "params": params}).encode()
        mask = os.urandom(4)
        header = bytes([0x81])
        if len(msg) < 126:
            header += bytes([0x80 | len(msg)])
        elif len(msg) < 65536:
            header += bytes([0x80 | 126]) + struct.pack(">H", len(msg))
        else:
            header += bytes([0x80 | 127]) + struct.pack(">Q", len(msg))
        self.sock.sendall(header + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(msg)))
        while True:
            frame = self.recv()
            if frame.get("id") == self.next_id:
                if "error" in frame:
                    raise RuntimeError(f"{method}: {frame['error']}")
                return frame.get("result", {})


def templates(running_head):
    # 8px = 6 pt, the floor below which a screen reader called the header unreadable. It was 7px
    # (5.2 pt) because the full 30-word title had to be squeezed in; the declared running title is
    # five words and needs no squeezing.
    style = ("font-size:8px;font-family:'Liberation Sans',Helvetica,sans-serif;color:#7c8b99;"
             "width:100%;padding:0 14mm;display:flex;justify-content:space-between;")
    header = (f'<div style="{style}"><span>{_html.escape(running_head)}</span>'
              '<span></span></div>')
    footer = (f'<div style="{style}"><span></span>'
              '<span class="pageNumber"></span></div>')
    return header, footer


def print_pdf(chrome, html_path, pdf_path, running_head):
    profile = tempfile.mkdtemp(prefix="ccpdf-")
    proc = subprocess.Popen(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-first-run",
         f"--user-data-dir={profile}", "--remote-debugging-port=0", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        portfile = os.path.join(profile, "DevToolsActivePort")
        deadline, port = time.time() + 45, None
        while time.time() < deadline:
            if os.path.exists(portfile):
                content = open(portfile).read().split("\n")
                if len(content) >= 2:
                    port = content[0].strip()
                    break
            time.sleep(0.2)
        if not port:
            raise RuntimeError("chromium never reported a devtools port")

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=30) as resp:
            targets = json.load(resp)
        ws = WS(next(t["webSocketDebuggerUrl"] for t in targets if t.get("type") == "page"))
        ws.call("Page.enable")
        ws.call("Page.navigate", url="file://" + os.path.abspath(html_path))
        time.sleep(2.5)
        header, footer = templates(running_head)
        result = ws.call("Page.printToPDF", printBackground=True, preferCSSPageSize=True,
                         displayHeaderFooter=True, headerTemplate=header, footerTemplate=footer)
        with open(pdf_path, "wb") as fh:
            fh.write(base64.b64decode(result["data"]))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


# --------------------------------------------------------------------------- driver


#: The documents a built PDF is a rendering OF. A stamp beside each PDF records the sha256 of each
#: at build time, so "is this PDF current?" is answered by CONTENT rather than by mtime.
STAMP_SOURCES = (
    "aso/fusion-junction-aso-research-article.md",
    "aso/fusion-junction-aso-submission-tables.md",
    "aso/fusion-junction-aso-submission-references.md",
    "aso/fusion-junction-aso-sequences.csv",
)


def _write_build_stamp(pdf_path, paper):
    """Record what this PDF was built from, by content hash.

    ⛔ AN MTIME TEST CRIES WOLF ON IDEMPOTENT REGENERATION, AND A GATE THAT CRIES WOLF GETS RELAXED
    (measured 2026-08-17, twice in one day). The regeneration chain rewrites its outputs byte-for-byte
    whether or not anything changed, so every chain run moves their mtimes past the PDFs' and a
    timestamp comparison reports a staleness that does not exist. The archive manifest's `--check`
    had the same shape earlier the same day, for the same reason, and the fix there was the same:
    compare what the artifact IS, not when it was touched.
    ⚠ THE FALSE-POSITIVE DIRECTION IS THE DANGEROUS ONE HERE. A guard that fires on a correct tree
    trains its reader to rebuild-and-move-on, which is exactly the reflex that would carry a genuinely
    stale PDF into a deposit.
    """
    stamp = {"built_from": {}}
    for rel in STAMP_SOURCES:
        src = os.path.join(HERE, rel)
        if os.path.exists(src):
            stamp["built_from"][rel] = hashlib.sha256(open(src, "rb").read()).hexdigest()
    stamp["_what"] = ("sha256 of each document this PDF renders, written by build_submission_pdf.py. "
                      "A PDF is current when every hash here matches the file on disk; mtimes are "
                      "not evidence, because the regeneration chain rewrites unchanged files.")
    with open(pdf_path.replace(".pdf", ".build-stamp.json"), "w", encoding="utf-8") as fh:
        json.dump(stamp, fh, indent=1, sort_keys=True)
        fh.write("\n")

def build(name, paper, style="journal", html_only=False):
    body, floats = assemble(paper, style)
    # ⛔ ONE SOURCE FOR THE RUNNING HEAD IN BOTH STYLES. The manuscript declares it; neither
    # renderer may substitute anything else, and a manuscript that stops declaring one fails the
    # build rather than falling back to the full title.
    running = declared_running_title(body)
    if style == "journal":
        front = parse_front_matter(body)
        page = wrap_journal(paper, front, markdown_to_html(front["body"], floats))
        out_name = paper["out"]
    else:
        title = re.sub(r"[*_`]", "", re.search(r"^#\s+(.*)$", body, re.M).group(1))
        page = wrap_manuscript(title, markdown_to_html(body, floats))
        out_name = paper["out"].replace(".pdf", "-manuscript.pdf")

    html_path = os.path.join(HERE, out_name.replace(".pdf", ".build.html"))
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    if html_only:
        print(f"{name} [{style}]: wrote {os.path.relpath(html_path, REPO)} (--html-only)")
        return 0

    chrome = find_chrome()
    if not chrome:
        print(f"{name}: no chromium found; HTML is at {os.path.relpath(html_path, REPO)}",
              file=sys.stderr)
        return 1
    pdf_path = os.path.join(HERE, out_name)
    print_pdf(chrome, html_path, pdf_path, running)
    os.remove(html_path)
    _write_build_stamp(pdf_path, paper)
    size = os.path.getsize(pdf_path)
    pages = open(pdf_path, "rb").read().count(b"/Type /Page\n") or None
    print(f"{name} [{style}]: wrote {os.path.relpath(pdf_path, REPO)} "
          f"({size / 1024:.0f} KB{f', {pages} pages' if pages else ''})")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", choices=sorted(PAPERS))
    ap.add_argument("--style", choices=("journal", "manuscript"), default="journal",
                    help="journal = typeset article (default); manuscript = submission format")
    ap.add_argument("--html-only", action="store_true")
    args = ap.parse_args(argv)
    names = [args.paper] if args.paper else sorted(PAPERS)
    return max(build(n, PAPERS[n], args.style, args.html_only) for n in names)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
