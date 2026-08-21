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
that want an editable file; this is the PDF route.

⚠ IT DOES NEED `pypdf`, AND THAT IS A DELIBERATE CHANGE (2026-08-19). Chromium's `printToPDF`
cannot write an Info dictionary and cannot vary a footer by page, and a deposit artefact needs
both: a screener opening Document Properties on the old build read a headless-Chrome UA string and
no author, and the full handling sentence was repeated into 66 running footers, where it spliced
into body sentences in content order. `_postprocess` does both with `pypdf` and VERIFIES the result
page by page. A missing `pypdf` is a hard failure rather than a silently thinner PDF: producing an
artefact that looks finished and is not is the failure mode this file's history is made of.

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
#: ⛔ OPT-IN PER PAPER, AND THE DEFAULT IS THE OLD BEHAVIOUR (2026-08-20). Setting narrow tables in
#: one column instead of spanning both is right for a short article and WRONG for the preprint,
#: which is already deposited: the first version of this flag was a module-level False and silently
#: re-laid-out the preprint from 58 pages to 41, so the repository's PDF would no longer have been
#: the artefact on bioRxiv. A paper opts in with `layout: {"tables_in_column": True}`.
_TABLES_IN_COLUMN = False

PAPERS = {
    #: ⭐ THE CONDENSED JOURNAL SUBMISSION, ADDED 2026-08-20. Same work as "aso" below, second
    #: document: 3,113 main-text words against that one's 35,501. It carries its own references and
    #: tables companions and NO supplementary file — the preprint is its extended report.
    "aso-journal": {
        "layout": {"tables_in_column": True, "no_provenance_line": True,
                   "backmatter_in_flow": True},
        #: Nucleic Acid Therapeutics, MEASURED from 14 of its own published articles by
        #: scripts/venue_typeset_geometry.py (research/literature/venue-typeset-geometry.json):
        #: US Letter, two columns of 239pt with a 12pt gutter, 9.8pt body on 10.9pt leading, and a
        #: ~60pt left margin. The leading is the number that matters — 1.11x the body size against
        #: this repository's house 1.40x — and it is why an A4 house-style page count was never a
        #: safe proxy for a venue that bills per printed page.
        #: 239 + 12 + 239 = 490pt of measure inside a 612pt trim leaves 61pt each side.
        #: ⚠ line_height 1.125 renders 11.2pt against the measured 10.9pt, and no value lands on
        #: 10.9: the render quantises, with 1.112 giving 10.5 and everything from 1.125 up giving
        #: 11.2. 11.2 is the nearer of the two and errs LOOSE, so the page count it produces cannot
        #: be an under-estimate of the bill. The page count is 7 at both settings, which is the
        #: reason this residual is recorded rather than chased.
        "geometry": {"page_size": "Letter", "margin": "35mm 21.5mm 25mm 21.5mm",
                     "landscape_margin": "21.5mm 20mm", "font_pt": 9.8,
                     "line_height": 1.125, "column_gap_mm": 4.2},
        "manuscript": "aso/fusion-junction-aso-journal-article.md",
        "tables": "aso/fusion-junction-aso-journal-tables.md",
        "references": "aso/fusion-junction-aso-journal-references.md",
        "stamp_sources": (
            "aso/fusion-junction-aso-journal-article.md",
            "aso/fusion-junction-aso-journal-tables.md",
            "aso/fusion-junction-aso-journal-references.md",
            "aso/fusion-junction-aso-sequences.csv",
        ),
        "figures": {"Figure 1.": "aso-multipartner-seam.svg"},
        "journal": {
            "article_type": "Article",
            "section": "",
            "preprint_note": "The extended report of this work is deposited as a preprint on Research Square.",
        },
        "out": "aso/fusion-junction-aso-journal-article.pdf",
    },
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
        "supplementary": "aso/fusion-junction-aso-supplementary-information.md",
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

    # ⛔ THE PREAMBLE WAS BEING DROPPED, AND IT IS THE PART THAT EXISTS TO BE CHECKED AGAINST
    # (blind order-walkthrough, 2026-08-19). Keying blocks from `**Table N.` onward discarded
    # everything before Table 1: the research-use banner, the chemistry paragraph that defines
    # 5-6-5/5-8-5/5-10-5, and — worst — the "Do not order these three sequences" block, which prints
    # the three condemned designs precisely so a reader holding a transcribed sequence has something
    # to check it against. Measured: the string "Do not order these three sequences" occurred ZERO
    # times in 66 pages of the built deposit. The block is now carried with Table 1 rather than
    # emitted separately, so it travels wherever the tables travel and needs no placement of its own.
    lead = tables_md[:starts[0][1]]
    lead = re.sub(r"^<!--.*?-->\s*", "", lead, flags=re.S)      # the generated-file marker
    lead = re.sub(r"^#\s+.*?\n", "", lead, count=1)             # the tables file's own H1
    lead = lead.strip()
    if lead:
        blocks[starts[0][0]] = lead + "\n\n" + blocks[starts[0][0]]
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


# --------------------------------------------------------------------------- deposit identity

def deposit_filenames(paper):
    """Source-file name -> the name of the file a DOWNLOADER actually receives.

    ⛔ THE DEPOSIT POINTED AT FILES THAT ARE NOT IN IT (blind screen of the built PDFs, 2026-08-19).
    Both full PDFs sent the reader to `fusion-junction-aso-supplementary-information.md` for §S1-§S6
    and the SI PDF sent them back to `fusion-junction-aso-research-article.md` for the § numbers.
    Neither `.md` is deposited: what travels is the rendered PDF beside it. A reader holding the
    deposit is told to open a file they do not have and cannot get without a checkout.

    ⚠ THE SUBSTITUTION IS AT RENDER TIME AND THE MANUSCRIPT IS NOT EDITED. The `.md` names are
    correct IN THE REPOSITORY, which is where the manuscript lives; they are wrong only in the
    artefact, which is what this file makes. Both names are derived from `paper["out"]`, so a
    renamed output cannot leave a stale pointer behind.
    """
    out = os.path.basename(paper["out"])
    article_md = os.path.basename(paper["manuscript"])
    supplementary_md = os.path.basename(paper.get("supplementary", ""))
    names = {
        #: The submission-format build is the one to upload (see this module's docstring), so a
        #: cross-reference to "the main text" resolves to that file and not to the typeset preview.
        article_md: out.replace(".pdf", "-manuscript.pdf"),
    }
    if supplementary_md:
        names[supplementary_md] = out.replace(".pdf", "-supplementary-information.pdf")
    # ⭐ AND ONE .md THAT TRAVELS AS ITSELF. The availability statement names
    # `fusion-junction-aso-submission-tables.md` as the machine-readable copy of Tables 1 to 7, and
    # it IS in the deposit — so it is the one .md filename a reader may correctly be sent to, and
    # mapping it to a PDF would point at a file that does not exist. It maps to itself so the
    # unmapped-name report stays quiet about a pointer that is right.
    # ⚠ SEPARATE, STILL OPEN: a bioRxiv screener records that Markdown is not among the accepted
    # supplementary types, so this file may yet need a rendered companion. That is a deposit-format
    # decision, not a broken pointer, and it is tracked as its own item.
    names.setdefault("fusion-junction-aso-submission-tables.md",
                     "fusion-junction-aso-submission-tables.md")
    return names


_MD_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.md\b")


def apply_deposit_filenames(text, paper, where):
    """Rewrite every deposited-document filename in `text`, and REPORT the ones with no mapping.

    ⚠ AN UNMAPPED `.md` IS PRINTED, NOT SWALLOWED. A name this map does not know is either a
    repository artefact a reader is not expected to open (fine) or a deposited file whose PDF nobody
    declared (not fine, and invisible unless it is said out loud).
    """
    names = deposit_filenames(paper)
    for source, deposited in names.items():
        text = text.replace(source, deposited)
    _NEVER_BREAK.update(names.values())
    _NEVER_BREAK.update({ORDER_FROM, ORDER_FROM.replace(".csv", ".fasta")})
    unmapped = sorted({m.group(0) for m in _MD_NAME_RE.finditer(text)}
                      - set(names.values()) - set(names))
    if unmapped:
        print(f"  ⚠ {where}: no deposited filename declared for {', '.join(unmapped)} — "
              f"a reader is sent to a file that does not travel with the deposit", file=sys.stderr)
    return text


def build_provenance():
    """(short commit, dirty?, ISO date) for the title page, read from git without writing to it.

    ⛔ NO FILE IN THE DEPOSIT CARRIED A DATE OR A VERSION (blind screen, 2026-08-19). Two people
    citing "the preprint" could hold different documents and neither could tell — and the deposit's
    own staleness incident is exactly that failure with the manuscript instead of the reader.

    ⚠ A DIRTY TREE IS PRINTED AS DIRTY. A build from uncommitted work is not reproducible from the
    commit it names, and a title page that quietly implies it is would be the more dangerous half of
    the same defect. `--no-optional-locks` keeps this read-only: git may otherwise refresh its index
    while answering, and this function must not write anything at all.
    """
    def git(*args):
        try:
            return subprocess.run(("git", "--no-optional-locks", "-C", REPO) + args,
                                  capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception:                                   # pragma: no cover - env dependent
            return ""
    commit = git("rev-parse", "--short", "HEAD")
    #: ⛔ THE BUILD'S OWN OUTPUTS ARE NOT UNCOMMITTED WORK (reviewer screen, 2026-08-20). The SI is
    #: rendered after the article in the same invocation, so by the time it read the tree the
    #: article PDF it had just written was sitting there unstaged — and the SI title page printed
    #: "tree not clean at build time" beside an article title page, at the same commit, that
    #: printed clean. Two provenance lines disagreeing about one build is worse than either verdict.
    #: What the line asserts is that the SOURCES this document was rendered from are the committed
    #: ones, so the artefacts this run writes are excluded and everything else — every manuscript,
    #: table, figure and generator — still makes the build dirty.
    _OUTPUTS = (".pdf", ".build-stamp.json", ".build.html")
    dirty = any(not line[3:].strip().strip('"').endswith(_OUTPUTS)
                for line in git("status", "--porcelain").splitlines() if line.strip())
    return commit, dirty, time.strftime("%Y-%m-%d", time.gmtime())


def provenance_line(paper, style):
    """The one line under the author block saying WHICH document this is and where it came from."""
    commit, dirty, date = build_provenance()
    what = {"journal": "typeset preview", "manuscript": "submission format",
            "supplementary": "supplementary information"}[style]
    #: ⛔ A SUBMITTED PAPER DOES NOT CARRY ITS BUILD METADATA (reviewer read, 2026-08-20). The line
    #: is right for a document under internal review, where which commit rendered it is the
    #: question. On a manuscript going to an editor it is noise, and "tree not clean at build time"
    #: reads as an admission. Papers opt out; the default keeps it, so no existing build moves.
    if (paper or {}).get("layout", {}).get("no_provenance_line"):
        return ""
    stamp = commit or "commit unknown"
    if dirty:
        stamp += ", tree not clean at build time"
    return f"Version of {date} · {what} · built from {stamp}"


def _fold_the_figure_legends_preamble(body, paper):
    """Move the note under "## Figure legends" to the END of the section, off its own page.

    ⛔ A PAGE CARRYING A HEADING AND FOUR SENTENCES (blind screen of the deposit, 2026-08-19).
    Manuscript page 56 held "Figure legends" plus the note explaining the two independent S-series,
    and nothing else: 612 characters against a median page of 4,777. The cause is structural rather
    than typographic — the tables section ends in a landscape run, so the heading opens a fresh
    portrait page, and Figure 1's panel is capped at 218 mm and cannot fit underneath four
    sentences, so it goes to the next page and takes the whole legend block with it.

    ★ THREE PLACEMENTS WERE BUILT AND MEASURED, because the obvious one does not work (2026-08-19):
      note below Figure 1's legend, own paragraph  -> 67 pages, a NEW 511-character page 57
      note appended INTO Figure 1's legend         -> 67 pages, a new 385-character page 57
      note after the LAST legend, own paragraph    -> 66 pages, no page under 865 characters
    The first two only move the stranding: page 56 has room for the panel or for the note, not for
    both, and everything between Figure 1's legend and Figure 2 gets the rest of a page that
    `break-before: page` then ends. After the last legend there is no forced break to strand it
    against. It is also where the note reads best: it is about the supplementary panel and the two
    S-numbered series, and the supplementary panel is the legend it now follows.

    ⚠ NOTHING IS DELETED AND THE PARAGRAPH TRAVELS INTACT — this moves a note, it does not edit one.
    ⚠ IF THE SECTION HAS NO PREAMBLE the body is returned unchanged.
    """
    try:
        _, end, after = section_span(body, "Figure legends")
    except SystemExit:
        return body
    section = body[after:end]
    first = re.search(r"^\*\*(?:Supplementary )?Figure S?\d+\.", section, re.M)
    if not first or not section[:first.start()].strip():
        return body
    preamble = section[:first.start()].strip()
    folded = section[first.start():].rstrip() + "\n\n" + preamble
    return body[:after] + "\n\n" + folded.strip() + "\n\n" + body[end:]


# --------------------------------------------------------------------------- assembly

def assemble(paper, style="journal"):
    """Return (markdown, prerendered_floats). In manuscript style the float map is empty."""
    body = strip_frontmatter(read(paper["manuscript"]))
    tables = split_tables(strip_generated_banner(read(paper["tables"])))
    references = strip_generated_banner(read(paper["references"]))

    if style == "manuscript":
        body = splice(body, "Tables", "\n\n".join(tables[n] for n in sorted(tables)), "the tables")
        body = splice(body, "References", references, "the reference list")
        body = _fold_the_figure_legends_preamble(body, paper)
        body = apply_deposit_filenames(body, paper, "manuscript style")
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
    body = apply_deposit_filenames(body, paper, "journal style")

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

    global _TABLES_IN_COLUMN
    _TABLES_IN_COLUMN = bool((paper.get("layout") or {}).get("tables_in_column"))
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
#: ⛔ AND AN ACCESSION IS THE SAME HAZARD ONE CHARACTER SMALLER (reviewer screen of the built
#: deposit, 2026-08-20): `AL158209.1--NEBL` was read out of the PDF as `AL15820 9.1--NEBL`. It
#: reaches the page as a code span, and a code span over `CODE_BREAKABLE_MIN` is given `<wbr/>`
#: after each of its separators, so the renderer is free to put the accession's version suffix and
#: its fusion partner on the next line — and it sits in the one sentence of §3 that makes a
#: contested claim about a widely used cell line, where a reader who cannot resolve the identifier
#: cannot check the claim. A versioned accession and a `--`-joined fusion call are IDENTIFIERS, not
#: paths: they are copied whole or they are useless, so they join the atomic set.
#: Covers DepMap models (ACH-######), Cellosaurus RRIDs (with or without the RRID: prefix),
#: GEO series (GSE#####), versioned INSDC/RefSeq accessions, and fusion calls written `A--B`.
_ACCESSION = r"[A-Z]{1,3}[_]?\d{5,9}\.\d{1,2}"
ATOMIC_ID_RE = re.compile(
    r"\b(?:RRID:CVCL_[A-Za-z0-9]+|CVCL_[A-Za-z0-9]+|ACH-\d{6}|GSE\d{4,6}"
    + r"|(?:" + _ACCESSION + r"|[A-Z][A-Za-z0-9.]{1,14})--(?:" + _ACCESSION + r"|[A-Z][A-Za-z0-9.]{1,14})"
    + r"|" + _ACCESSION + r")\b")

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

#: Below this, a token is short enough that moving it whole to the next line costs little. Above it,
#: an identifier that HAS a safe break point should take one.
#:
#: ⛔ THE LENGTH THRESHOLD ALONE LEFT TWO LINES STRETCHED TO NEAR-ILLEGIBILITY (blind screen of the
#: built manuscript PDF, 2026-08-18). `emc-atr-vulnerability.json` is 26 characters and
#: `aso_parent_gap_pairing.py` is 25 — both under 44, so both stayed atomic, and the justified line
#: BEFORE each carried about ten word-spaces of stretch. The screen made the distinction this code
#: had missed: the paper's blanket refusal to break an unbreakable token is a SEQUENCE-safety rule,
#: because a newline a reader copies out of a base string is invisible in a synthesis order form.
#: A filename or a module name carries no such hazard and can break at a separator.
#:
#: ⚠ AND A SEQUENCE CANNOT BE BROKEN BY THIS CHANGE, WHICH IS WHY IT IS SAFE. `CODE_BREAK_AFTER`
#: inserts `<wbr/>` only after `/ _ . = -`; a bare base string contains none of them, so it receives
#: no break opportunity at any length. `code.brk` relaxes `white-space` only — `word-break` and
#: `overflow-wrap` stay `normal`, so nothing breaks anywhere a `<wbr/>` was not placed. Held by
#: `tests/test_code_spans_never_break_a_sequence.py`.
CODE_BREAKABLE_MIN = 12

#: ⛔ THE DEPOSIT'S OWN FILENAMES ARE NOT PATHS AND MUST NOT BREAK LIKE ONE. A path fragment is still
#: recognisable — "research/" then "manuscripts" reads as one path — but a FILENAME fragment is a
#: different, wrong name that reads as hyphenation: the built PDFs printed the paper's most repeated
#: instruction as `fusion-junction-aso-sequences.` / `csv` in Box 1 and `fusion-` /
#: `junction-aso-sequences.fasta` in §6 (blind screen, 2026-08-19). These are the names a reader is
#: told to ORDER FROM or to open, so they are set atomic where they fit, and where they are too long
#: to fit a column they are given break opportunities after `.` and `/` ONLY — never at a hyphen,
#: which is the break a reader silently repairs by deleting the character.
#: ⚠ Populated at render time by `apply_deposit_filenames`, because two of the four are derived from
#: the output filename and only that function knows it.
_NEVER_BREAK = set()
CODE_BREAK_AFTER_SAFE = re.compile(r"(?<=[/.])(?=[^\s/.])")

#: A locator a reader has to be able to copy: it is set `nowrap` and never given a `<wbr/>`, and it
#: is turned into a live link. ⛔ MEASURED IN THE BUILT PDF, NOT ASSUMED (blind screen of the deposit,
#: 2026-08-19): the repository URL is written in the manuscript as a code span, so `CODE_BREAK_AFTER`
#: offered it break opportunities after every `.`, `/` and `-` and the text layer of the deposited
#: manuscript read `github. com/trimcrae/Rare-cancers`. The DOI being a placeholder, that URL is the
#: only working locator in the whole deposit, and it could not be copied out of it.
_LOOKS_LIKE_A_URL = re.compile(r"^(?:https?://|www\.|[a-z0-9-]+\.(?:com|org|net|io|gov|edu)/)\S+$")

#: A bare DOI as the reference list prints it, and a PMID as it prints those. Both are linked at
#: render time. ⛔ THE LINK IS BUILT FROM THE IDENTIFIER ON THE PAGE AND FROM NOTHING ELSE — no
#: identifier is recalled, completed or invented here (CLAUDE.md §7); a DOI that is wrong in the
#: reference list stays wrong and now resolves to the same wrong place, which is the honest
#: behaviour for a renderer.
DOI_RE = re.compile(r"\bdoi:(10\.\d{4,9}/[^\s<>]*[^\s<>.,;)\]])", re.I)
PMID_RE = re.compile(r"\bPMID:\s?(\d{4,9})\b")
URL_RE = re.compile(r"\bhttps?://[^\s<>()\[\]]+[^\s<>()\[\].,;]")

#: ⛔ U+2691 (⚑) AND U+25C6 (◆) MUST BE SET IN AN EMBEDDABLE FACE, AND ONLY IN BOLD DOES IT MATTER.
#: Measured 2026-08-19, one glyph at a time, in built PDFs: in a `font-weight: 700` run neither
#: character exists in Liberation Sans/Serif Bold, Chromium's fallback for them cannot be embedded
#: as a Type0 subset, and Skia emits a TYPE 3 font carrying that single glyph — five pages of each
#: full PDF. † (U+2020), ¹, ·, — and ≥ all resolve inside the bold face and are clean; ⚑ and ◆ are
#: the only two that fall through. Type 3 is a standing reject at PMC and several journal PDF
#: checkers. Wrapping just these two in a span that names DejaVu Sans removes the Type 3 font
#: entirely (measured: 5 pages -> 0) and also removes the bogus advance width the Type 3 glyph
#: carried, which was extracting as a double space after every marker.
MARKER_GLYPH_RE = re.compile(r"[⚑◆]")

#: ⛔ A DISPLAY-ITEM REFERENCE IS ONE TOKEN AND MUST NOT BREAK ACROSS A LINE. Measured in the built
#: manuscript PDF (2026-08-20): §2.2's only citation of Figure 2 extracted as "…and FUS (Figure" /
#: "2). Five cover…", so a reader — or a reviewer checking that display items are cited in order —
#: reads a paragraph that appears to cite no figure at all, and the next number they meet in the
#: body is Figure 3. The numbering was already in citation order; the LINE BREAK is what made it
#: look otherwise. Fixed where every other typesetting defect in this file is fixed: at render, by
#: binding the label to its number with a no-break space.
FLOAT_REF_RE = re.compile(
    r"\b((?:Supplementary\s+)?(?:Figure|Table|Box|Panel|Section|Equation)s?)\s+(?=S?\d)")

#: ⛔⛔ A TOKEN CARRYING A BASE STRING IS NEVER BREAKABLE, WHATEVER SEPARATORS IT HAS. Checked while
#: relaxing the rule above: `5′-GGGCATATCATCAAAC-3′` contains two hyphens, so the separator rule
#: would have given it break opportunities after `5′-` and before `3′` — leaving the delimiter on
#: the line above its bases, which is precisely the invisible-newline hazard the `.seq` rule exists
#: to prevent and the one this whole deposit was rebuilt around. Delimited sequences normally reach
#: the page as `.seq` spans rather than code spans, so this is a belt on top of a brace; it is here
#: because "it does not currently take that path" is not a property anyone can rely on later.
_LOOKS_LIKE_A_SEQUENCE = re.compile(r"[ACGT]{12,}")


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
    if literal in _NEVER_BREAK:
        if len(literal) <= CODE_NOWRAP_MAX:
            return "<code>" + escaped + "</code>"
        #: ⚠ THE SAFE BREAK SET IS ONLY USED WHEN IT ACTUALLY FITS. The deposited SI filename is 66
        #: characters with one dot in it, so breaking after dots alone leaves a 63-character run —
        #: wider than the journal's 88 mm column, and an overflowing token is a worse defect than an
        #: ambiguous break. When that happens the ordinary break set is used and the name can break
        #: at a hyphen like any other long path.
        if max(len(part) for part in CODE_BREAK_AFTER_SAFE.split(literal)) <= CODE_NOWRAP_MAX:
            return '<code class="brk">' + CODE_BREAK_AFTER_SAFE.sub("<wbr/>", escaped) + "</code>"
        return '<code class="brk">' + CODE_BREAK_AFTER.sub("<wbr/>", escaped) + "</code>"
    #: A URL is a locator, not a path: it is copied whole or it is useless, and it is also the one
    #: kind of code span that can be made live. It never receives a break opportunity.
    if _LOOKS_LIKE_A_URL.match(literal):
        href = literal if literal.startswith("http") else "https://" + literal
        return (f'<a class="loc" href="{_html.escape(href, quote=True)}"><code>'
                + escaped + "</code></a>")
    breakable = (CODE_BREAK_AFTER.search(escaped) is not None
                 and not _LOOKS_LIKE_A_SEQUENCE.search(literal))
    if len(literal) <= CODE_NOWRAP_MAX and not (breakable and len(literal) > CODE_BREAKABLE_MIN):
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
    def _seq_span(m):
        #: `pad` only where a space follows — see the `.seq.pad` comment in the stylesheet.
        after = m.string[m.end():m.end() + 1]
        cls = "seq pad" if (after == "" or after.isspace()) else "seq"
        return keep(f'<span class="{cls}">' + m.group(0) + "</span>")

    #: ⛔⛔ LOCATORS ARE STASHED BEFORE IDENTIFIERS, AND THE ORDER IS THE WHOLE FIX (reviewer screen
    #: of the built deposit, 2026-08-20). An accession is an identifier AND the tail of the URL that
    #: resolves it, so with the identifier rules running first, the accession inside
    #: `https://www.ncbi.nlm.nih.gov/nuccore/AF289510.1` was replaced by its stash placeholder, the
    #: URL rule then stashed the mangled string whole, and the single-pass unstash at the bottom of
    #: this function never reached the placeholder nested inside it — so the deposit printed
    #: `https://www.ncbi.nlm.nih.gov/nuccore/2`, the stash INDEX, for eight of the nine entries in
    #: Data sources. Six of those are the only pointers a reader has to the records carrying §2.3's
    #: *TCF12* and *TFG* breakpoint claims, and every one resolved to the wrong record. A URL is
    #: now stashed whole and its contents are never re-scanned, which is the correct reading anyway:
    #: the accession inside a locator is part of the locator, not a second thing to mark up.
    text = DOI_RE.sub(lambda m: keep(f'<a class="loc" href="https://doi.org/{m.group(1)}">'
                                     + f"doi:{m.group(1)}</a>"), text)
    text = PMID_RE.sub(lambda m: keep(
        f'<a class="loc" href="https://pubmed.ncbi.nlm.nih.gov/{m.group(1)}/">'
        + f"PMID: {m.group(1)}</a>"), text)
    text = URL_RE.sub(lambda m: keep(f'<a class="loc" href="{m.group(0)}">{m.group(0)}</a>'), text)
    text = SEQUENCE_RE.sub(_seq_span, text)
    text = ATOMIC_ID_RE.sub(lambda m: keep('<span class="seq">' + m.group(0) + "</span>"), text)
    #: The two marker glyphs that would otherwise become a Type 3 font wherever they land in bold.
    #: Applied to EVERY rendered string rather than only to the table labels, because the labels are
    #: where they became bold today and a bold table cell or a bold caption clause is where they
    #: would become bold tomorrow.
    text = MARKER_GLYPH_RE.sub(lambda m: keep('<span class="mk">' + m.group(0) + "</span>"), text)
    #: Bind "Figure"/"Table"/"Box" to the number that names the display item, so the pair cannot be
    #: split by a line or column break. U+00A0 rather than a nowrap span: the reference is two
    #: ordinary words and must still justify, hyphenate and stretch like the prose around it.
    text = FLOAT_REF_RE.sub(lambda m: m.group(1) + "\u00a0", text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", r"<em>\1</em>", text)
    #: ⚠ TO A FIXED POINT, NOT ONE PASS. The ordering above is what keeps a placeholder from being
    #: stashed inside another fragment; this loop is the guard that a future reordering cannot
    #: silently print a stash INDEX into the deposit the way the accession bug did. Bounded, and a
    #: survivor is a hard failure rather than a character a reader has to notice.
    for _ in range(8):
        expanded = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
        if expanded == text:
            break
        text = expanded
    if "\x00" in text:
        raise SystemExit("inline(): a stash placeholder survived expansion — a rule is nesting "
                         "stashed fragments and the deposit would print a stash index")
    return text


def render_table(rows, label=None):
    """`label` rides in the <thead>, which paged media REPEATS on every continuation page.

    ⛔ A CONTINUATION PAGE CARRIED NO TABLE IDENTITY (blind screen of the built journal PDF,
    2026-08-18). Four of the seven tables run over two or three landscape pages, and each
    continuation opened directly with a repeated column-header row — no number, no "(continued)".
    A reader landing on one had to page backwards to learn which table they were in. The column
    headers repeat because they are in <thead>; the table's own name was not, so it did not.
    """
    def cells(line):
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]

    head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
    # ⛔ A WIDE TABLE IN THE BODY OVERPRINTS THE COLUMN BESIDE IT (blind PDF screen, 2026-08-19,
    # graded BLOCK). Journal style sets the body in two columns; the LANDSCAPE_MIN_COLS rule that
    # rescues wide tables lives in `render_float`, which only the SPLICED display items reach. An
    # eleven-column pipe table written inline in §2.5 therefore rendered at full body width inside
    # a 6 mm-wide column and printed straight over ~22 lines of the neighbouring prose — 69 box
    # collisions on one page, and the reader loses BOTH the table and the text under it.
    # A body table at or above the same column threshold now spans both columns and sets smaller,
    # which is the treatment the float path already gives its own wide tables.
    # ⛔ AND NOT INSIDE A FLOAT. Scoping this on column count ALONE broke the deposit: Tables 2 to
    # 6 also clear LANDSCAPE_MIN_COLS, so they picked up `table-layout: fixed` on top of the
    # landscape stylesheet that already sizes them, their sequence cells overflowed their columns
    # and were overprinted by the next cell, and the journal PDF printed `5′-GGGCATATCCATCAGA3-3′`
    # — a corrupted 16-mer with the neighbouring cell's digit fused in. 0 of 93 sequence cells came
    # out well formed against 93 of 93 in the submission format. That is the wrong-reagent hazard
    # this deposit's PDF seat exists to catch, and it was introduced by the fix for the previous
    # one (blind PDF screen, 2026-08-19).
    wide_body = len(head) >= LANDSCAPE_MIN_COLS and not _IN_FLOAT
    out = [f'<table class="wide-body-table">' if wide_body else "<table>", "<thead>"]
    if label:
        out.append(f'<tr class="tablename"><th colspan="{len(head)}">{inline(label)}</th></tr>')
    out.append("<tr>")
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead>")
    #: ⛔ ONE <tbody> PER BLOCK, BECAUSE `break-after: avoid` ON A <tr> IS IGNORED HERE. Measured
    #: 2026-08-19: with the rule on the heading row, page 45 still ended with the heading plus
    #: exactly one row and page 46 still carried the other five. Chromium honours `break-inside`
    #: on a row GROUP, so each block becomes its own tbody and travels whole.
    open_body = False
    for row in body:
        #: ⛔ A BLOCK HEADING MUST NOT BE THE LAST ROW ON A PAGE (blind screen, 2026-08-19). Table 7
        #: is three blocks with DIFFERENT denominators, and its caption exists to say they are not
        #: comparable. Page 45 ended with the bolded heading "Over each geometry's whole design
        #: space" plus exactly one row; the block's remaining seven rows opened page 46 under a bare
        #: repeated column header, so a reader met "87 of 190 | 88 of 266 | 87 of 342" with no way
        #: to tell which of the three denominators applied — the precise confusion the caption is
        #: written to prevent. A block heading is a row whose only filled cell is its first and is
        #: bold; `break-after: avoid` keeps it with what it labels.
        is_head = bool(row) and row[0].startswith("**") and not any(c.strip() for c in row[1:])
        if is_head or not open_body:
            if open_body:
                out.append("</tbody>")
            out.append('<tbody class="rowblock">')
            open_body = True
        klass = ' class="blockhead"' if is_head else ""
        out.append(f"<tr{klass}>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
    if open_body:
        out.append("</tbody>")
    out.append("</table>")
    return "".join(out)



#: The cut a table's own caption states for its marked rows — "ten" out of "at the ten-base-pair
#: criterion applied throughout" (Table 3) or "⚑ marks ten base pairs or more, the criterion applied
#: throughout" (Table 4). ⛔ READ FROM THE CAPTION, NEVER TYPED HERE (rule 1): the criterion has one
#: home, the generated caption, and a running header that restated it would be a second one.
_CRITERION_RE = re.compile(r"\b([A-Za-z]+)[ -]base[ -]pairs?\b(?=[^.]{0,48}criterion)")
#: ⛔ IT USED TO REQUIRE TABLE 3's AND TABLE 4's EXACT WORDING, AND TABLE 2 WRITES IT DIFFERENTLY
#: (blind screen of both built PDFs, 2026-08-19). Table 2's caption says "an unmarked row here is
#: not a clearance on any wider ground" — lower-cased, with one extra word — so the caveat matched
#: nowhere on the one table whose EVERY row is unmarked, and whose continuation pages therefore
#: carried a bare title over duplex readings of 8 and 9 against a cut of ten.
_NOT_A_CLEARANCE_RE = re.compile(r"\b[Aa]n unmarked row (?:here )?is not a clearance\b")
#: ⚠ CASE-INSENSITIVE BECAUSE THE CAPTION SHOUTS IT. `_cut_caveat()` in `submission_tables.py`
#: emits "That ten-base-pair cut is a criterion this work ADOPTS rather than measures", and this
#: pattern was written lower-case, so the clause it exists to carry reached no running header in
#: either build — measured on the Table 4 continuation pages, which stated the criterion and then
#: stopped.
_ADOPTED_RE = re.compile(r"adopts? rather than measures", re.I)


def _first_clause(text, limit):
    """`text` collapsed to one line and cut at the last clause boundary within `limit`."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text.rstrip(" .")
    head = text[:limit]
    #: ⛔ A CUT AT A CLAUSE BOUNDARY READS AS A PHRASE; A CUT AT A BARE SPACE READS AS A DEFECT
    #: (reviewer screen of the built deposit, 2026-08-20). Table 5's continuation band printed
    #: "…and §4's two contrast" and stopped there, mid-noun-phrase, while every other table's band
    #: happened to fall on a comma and read as complete. The band is a running identity and is
    #: SUPPOSED to be short; what it must not do is look like the caption itself broke off. An
    #: ellipsis is added only on the word-boundary fallback, so the bands that already end on a
    #: clause are unchanged.
    for sep in ("; ", " — ", ", "):
        cut = head.rfind(sep)
        if cut > limit // 2:
            return head[:cut].rstrip(" ,;—")
    cut = head.rfind(" ")
    if cut > limit // 2:
        return head[:cut].rstrip(" ,;—") + " …"
    return head.rstrip()


def _caption_title(block):
    """The bolded title sentence of a generated table's caption, without its number.

    ⚠ SEARCHED, NOT ANCHORED AT THE START. Table 1's block does not begin with its own opener: the
    tables file's preamble — the research-use banner, the chemistry paragraph and the three
    condemned sequences — is carried with Table 1 so it travels wherever the tables travel. Anchoring
    here left exactly one table, in exactly one style, with a bare "Table 1" on its continuation
    page (measured in the built journal PDF, 2026-08-19).
    """
    match = re.search(r"^\*\*Table \d+\.\s*(.+?)\*\*", block.strip(), re.S | re.M)
    #: ⚠ 200, NOT 92 (reviewer screen, 2026-08-20). At 92 exactly one table's title clause did not
    #: fit — Table 5's, which stopped on "…and §4's two contrast" — and on its CONTINUATION page
    #: that band is the only caption a reader sees for a page of rows whose column heads mean
    #: nothing without the clause that was cut. The bound exists so a band cannot run to a
    #: paragraph, not to clip the one caption that is longer than the rest.
    return _first_clause(match.group(1), 200) if match else None


def _marker_note(block, marker):
    """The caption's own opening sentence for `marker`, as the caption writes it."""
    match = re.search(rf"^{re.escape(marker)}\s+(.+?)(?<![A-Z])\.\s", block, re.M | re.S)
    return _first_clause(match.group(1), 96) if match else None


def table_label(number, block):
    """The identity a table's CONTINUATION pages carry, built from that table's own caption.

    ⛔ IT RIDES IN <thead>, WHICH PAGED MEDIA REPEATS ON EVERY PAGE, AND IT IS THE ONLY THING THAT
    DOES. A reader landing on page two of a three-page table meets the column headers, the rows and
    this line — the caption, its numbered notes and its marker keys are all a page back.

    ⛔⛔ AND IT USED TO DROP BOTH HALVES OF THE CRITERION THE CAPTION CARRIES (blind screen of the
    built PDFs, 2026-08-19). The caption says a marked design pairs a wild-type parent "at the
    ten-base-pair criterion applied throughout" and, in the same note, "An unmarked row is not a
    clearance". The header said only "pairs a wild-type parent through the whole catalytic gap; do
    not order it" — so a reader on a continuation page was given a prohibition with no cut attached
    and, worse, was left to read every unmarked row as cleared. Measured before the fix: 6 of the 7
    ⚑-carrying pages of the journal build and 7 of 9 in the manuscript build stated no cut, and 8
    and 9 respectively stated no clearance caveat. Both halves are now read out of the caption.

    ⚠ AND THE LABEL WAS OTHERWISE JUST A NUMBER. Table 2's continuation pages read "Table 2" and
    nothing else, and Table 6's carried ◆ rows with no ◆ branch in this function at all. The title
    is now carried too, so a continuation page says which table it is rather than only which number.
    """
    #: ⛔ A MARKER KEY IS EARNED BY THE ROWS, AND ITS WORDS COME FROM THE CAPTION. The two styles
    #: used to disagree about this: the manuscript path read the markers off the GRID and the journal
    #: path off the whole block, so a caption that merely MENTIONS ⚑ — as the tables file's preamble,
    #: which travels with Table 1, does — put a do-not-order key on the continuation pages of a table
    #: with no marked row in it. Detection is on the grid; the criterion and the ◆ gloss are still
    #: read from the caption, which is where they are written.
    grid = "\n".join(ln for ln in block.split("\n") if ln.strip().startswith("|"))
    label = f"Table {number}"
    title = _caption_title(block)
    if title:
        label += ". " + title
    if re.search(r"[¹²³⁴⁵⁶⁷⁸⁹]", grid):
        label += "  ·  numbered notes are under the caption, on this table's first page"
    if "†" in grid:
        label += ("  —  † no design at this junction clears the parent screen; "
                  "do not order the sequence in a marked row")
    if "⚑" in grid:
        label += ("  —  ⚑ this design pairs a wild-type parent through the whole catalytic gap; "
                  "do not order it")
    #: ⚑ and † are both readings at one cut, so the cut and the caveat are stated ONCE for the pair
    #: rather than repeated behind each marker.
    #: ⛔⛔ AND A TABLE WITH NO MARKER IN ITS GRID GOT NEITHER HALF, WHICH IS THE WRONG WAY ROUND
    #: (blind screen of both built PDFs, 2026-08-19). This whole block was gated on a marker being
    #: present, so TABLE 2 — the table its own caption calls "the table one reagent is chosen from",
    #: whose every row is unmarked because no row reaches the cut — carried a bare title across
    #: three continuation pages of the manuscript build and two of the journal build, over 38 rows
    #: whose longest-parent-duplex readings run to nine against a criterion of ten. A reader
    #: arriving on one of those pages had the prohibition's cut nowhere and no statement that an
    #: unmarked row is not a clearance; the absence of a marker read as the absence of a liability,
    #: which is exactly the inference the caption exists to refuse. The criterion and the caveat are
    #: properties of the CAPTION, not of the markers, so they are carried whenever the caption
    #: states both — and the clause says which rows it is read over, since "the marker is read at"
    #: is meaningless on a table with no marker.
    markers = [m for m in ("†", "⚑") if m in grid]
    criterion = _CRITERION_RE.search(block)
    not_a_clearance = _NOT_A_CLEARANCE_RE.search(block)
    if markers or (criterion and not_a_clearance):
        tail = []
        if criterion:
            subject = ("both markers are" if len(markers) == 2 else
                       "the marker is" if markers else "every row is")
            clause = f"{subject} read at the {criterion.group(1)}-base-pair criterion"
            #: ⚠ ONLY IF THE CAPTION SAYS SO. A header that added the clause anyway would be a
            #: second, louder home for a claim the caption did not make.
            if _ADOPTED_RE.search(block):
                clause += ", which this work adopts rather than measures"
            tail.append(clause)
        if not_a_clearance:
            tail.append("an unmarked row is not a clearance, only a reading at that one cut")
        if tail:
            label += "  ·  " + "; ".join(tail)
    #: ◆ is an IDENTIFICATION marker, not a prohibition, and a continuation page that carried ◆ rows
    #: with no key at all invited reading it as one. Its gloss is the caption's own first sentence.
    if "◆" in grid:
        note = _marker_note(block, "◆")
        label += "  —  ◆ " + (note or "see the caption for what this marker identifies")
        if re.search(r"marker identifies and does not rank", block):
            label += "; the marker identifies and does not rank"
    return label


def _label_for_spliced_table(lines, table_end, rows):
    """Rebuild the <thead> label for a table spliced into the body (manuscript style).

    Mirrors render_float, which manuscript style never reaches. The caption sits ABOVE the grid in
    the generated tables file, so the block is recovered by scanning back for the nearest
    "**Table n." opener and taking everything from there to the end of the grid — the caption, its
    notes and the rows, which is exactly what `table_label` reads.
    """
    for k in range(table_end - len(rows) - 1, max(-1, table_end - len(rows) - 60), -1):
        m = re.match(r"^\*\*Table (\d+)\.", lines[k].strip())
        if m:
            return table_label(m.group(1), "\n".join(lines[k:table_end]))
    return None


def markdown_to_html(text, floats=None):
    floats = floats or {}
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)          # PMID markers: non-rendering
    lines = text.split("\n")
    out, i = [], 0
    #: True from a "**Table n." / "**Figure n." opener until the display item itself (a pipe row or
    #: an <svg>) or the next heading. Everything in that span is a caption FOOTNOTE and has to break
    #: like part of the caption, not like body prose. Tracked here rather than by the render_float
    #: flag because MANUSCRIPT style never calls render_float -- `assemble` returns an empty float
    #: map and splices the tables straight into the body, which is why keying this off the float
    #: path silently did nothing to the deposit PDF.
    in_caption = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("|") or stripped.startswith("#") or stripped.startswith("<svg"):
            in_caption = False

        #: ⛔ A FENCED BLOCK IS THE ONE PLACE IN THE PAPER WHERE LINE BREAKS CARRY MEANING, AND THIS
        #: RENDERER USED TO HAVE NO RULE FOR IT (reviewer screen of the built deposit, 2026-08-20).
        #: §4.5's invocation — the only runnable command the paper gives, and the deliverable it
        #: calls "the procedure as well as the reagents" — reached the page as justified body prose:
        #: the ``` fences printed as literal backticks, the two invocations collapsed onto one line
        #: with an orphaned `\`, and `DONOR_EXON_END=5` broke across the line as `DONOR_EXON_` /
        #: `END=5` because the inline code path had offered it a `<wbr/>` after the underscore. A
        #: reader who copies that gets a command that cannot run, on a variable the same section says
        #: the builder REFUSES to default. Fences are now their own block: contents are escaped and
        #: never re-parsed as markdown, so nothing inside can be given a break opportunity.
        if stripped.startswith("```"):
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1                                          # the closing fence
            out.append("<pre>" + _html.escape("\n".join(block), quote=False) + "</pre>")
            continue

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
            #: ⛔⛔ THE TABLE LABEL MUST BE COMPUTED HERE, NOT ONLY IN render_float — A WRONG-REAGENT
            #: HAZARD REACHED THE DEPOSIT PDF BECAUSE IT WAS NOT (blind safety screen, 2026-08-19).
            #: `_CURRENT_TABLE_LABEL` carries Table 3's "† ... do not order the sequence in a marked
            #: row" key, and it rides in <thead>, which paged media repeats on every continuation
            #: page. That was verified in the JOURNAL build and never in the deposit build. Measured:
            #: journal style emits 7 <tr class="tablename"> rows, MANUSCRIPT STYLE EMITTED ZERO,
            #: because the label is set by render_float and manuscript style never calls it —
            #: `assemble` returns an empty float map and splices the tables into the body. The
            #: consequence in the shipped artefact: the legend printed on p36 while all three marked
            #: rows sat on pp38-39, so the paper's only in-table ordering prohibition was unreachable
            #: from every page it applied to. A reader met a printed 16-mer, a bare dagger, and no key.
            #: The same dead branch had already produced the caption-footnote defect earlier the same
            #: day; fixing that one and not auditing what else depended on it is what let this ship.
            label = _CURRENT_TABLE_LABEL or _label_for_spliced_table(lines, i, rows)
            out.append('<div class="tablewrap">'
                       + render_table(rows, label) + "</div>")
            continue

        #: ⛔ A NUMBER THAT HAPPENS TO OPEN A LINE IS NOT A LIST (reviewer screen, 2026-08-20).
        #: Table 6's note wraps as "…at 48 of its own" / "56. Both columns count records the search
        #: returned…", so this rule promoted "56." to an ordered-list item: the caption appeared to
        #: end without a full stop, a large-type "56." stood alone as a heading, and the sentence
        #: resumed underneath it mid-clause. CommonMark forbids exactly this — an ordered marker may
        #: not interrupt a paragraph unless it numbers 1 — and that is the rule adopted here rather
        #: than a fix to the one generator, because the number in that cell is derived and the next
        #: regeneration can put any number at the start of any line.
        item = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if item and item.group(2)[:-1].isdigit() and item.group(2) != "1." \
                and i > 0 and lines[i - 1].strip() and not lines[i - 1].lstrip().startswith(("#", "|", "-", "*")):
            item = None
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
                li = inline(m.group(3))
                out.append(("<li data-seq=\"1\">" if 'class="seq"' in li else "<li>")
                           + li + "</li>")
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
            #: ⛔ A SUPPLEMENTARY LEGEND IS A LEGEND (found 2026-08-19 by a guard this lane's own
            #: change tripped). The pattern was `^\*\*(Figure|Table) \d+\.`, which does not match
            #: "**Supplementary Figure S1." — so the supplementary panel's legend rendered as a
            #: bare <p> with no break rule at all, and any note after it fell through too. Exactly
            #: the class-that-no-element-carries shape `test_no_page_is_nearly_empty` exists to
            #: catch, sitting in the builder unnoticed because nothing had yet been placed after it.
            opener = re.match(r"^\*\*(?:Supplementary )?(Figure|Table) S?\d+\.", joined)
            # ⚠ A TABLE CAPTION AND A FIGURE LEGEND SIT ON OPPOSITE SIDES OF THEIR ITEM, so they
            # cannot carry the same break rule: a legend must stay with the figure ABOVE it and a
            # caption with the table BELOW it. They shared one class until 2026-08-17 and the
            # caption therefore had no rule at all.
            css = ""
            if opener:
                in_caption = True
                css = ' class="legend caption"' if opener.group(1) == "Table" else ' class="legend"'
            elif in_caption or _IN_FLOAT_CAPTION:
                #: ⛔ A FOOTNOTE UNDER A CAPTION IS PART OF THE CAPTION BLOCK AND MUST BREAK LIKE ONE
                #: (blind screen of the deposit PDF, 2026-08-19). Only the paragraph matching
                #: "**Table n." got a class; every numbered note and marker note after it fell
                #: through to a BARE <p>, so `p.legend { break-inside: avoid; orphans: 3; widows: 3 }`
                #: never applied to them. Table 6's "◆" note split across the page boundary and left
                #: its last line alone: manuscript page 42 carried 110 characters against a median of
                #: 4,235, with the table it describes not starting until page 43.
                #:
                #: ⚠⚠ AND THE WIDOW RULE ADDED THAT SAME MORNING WAS WRITTEN AS THE FIX FOR THIS
                #: PAGE, in a comment naming the exact orphaned sentence. It could not have worked:
                #: the rule was keyed to a class the orphaned element did not carry. A fix whose
                #: comment names the symptom is not evidence the symptom is gone — the PDF is.
                css = ' class="legend note"'
            rendered = inline(joined)
            #: ⛔ A PARAGRAPH THAT PRINTS A SEQUENCE IS SET RAGGED-RIGHT — see the `[data-seq]` rule
            #: in COMMON for what was measured. ⚠ IT IS AN ATTRIBUTE AND NOT A CLASS ON PURPOSE:
            #: `test_no_page_is_nearly_empty` counts the exact string `class="legend note"`, and a
            #: caption footnote that happened to print a sequence would have become
            #: `class="legend note hasseq"` and quietly dropped out of another lane's guard.
            seq_attr = ' data-seq="1"' if 'class="seq"' in rendered else ""
            out.append(f"<p{css}{seq_attr}>{rendered}</p>")
        else:
            i += 1
    return "\n".join(out)


#: The label a continuation page carries, e.g. "Table 5 (continued on this page)". Set by
#: `render_float` for the duration of one table's render, because `markdown_to_html` reaches the
#: grid without knowing which display item it belongs to.
_CURRENT_TABLE_LABEL = None

#: True while `render_float` is rendering a display item's caption block, so `markdown_to_html`
#: can tell a caption footnote from body prose. Body paragraphs must NOT gain `.legend`.
_IN_FLOAT_CAPTION = False

#: ⛔ True while ANY part of a float is rendering, caption or grid. `_IN_FLOAT_CAPTION` covers
#: only the caption; the wide-body-table rule below must not reach a float's GRID, whose column
#: widths the landscape stylesheet already sets.
_IN_FLOAT = False


def render_float(kind, number, payload, wide):
    """A table or figure set as a float, with its caption."""
    global _IN_FLOAT
    _IN_FLOAT = True
    try:
        return _render_float(kind, number, payload, wide)
    finally:
        _IN_FLOAT = False


def _render_float(kind, number, payload, wide):
    classes = ["float", kind]
    if wide:
        classes.append("landscape-float")
    elif kind == "table" and _TABLES_IN_COLUMN:
        classes.append("col-float")
    else:
        classes.append("span-float")
    global _CURRENT_TABLE_LABEL, _IN_FLOAT_CAPTION
    if kind == "figure":
        svg, legend = payload
        _IN_FLOAT_CAPTION = True
        try:
            inner = f'<div class="panel">{svg}</div>' + markdown_to_html(legend)
        finally:
            _IN_FLOAT_CAPTION = False
    else:
        #: ⛔ A SAFETY MARKER MUST TRAVEL WITH THE ROWS IT MARKS, NOT ONLY WITH ITS CAPTION (blind
        #: screen of the built journal PDF, 2026-08-18). Table 3 runs over three pages; its "†"
        #: rows appear on the continuation pages while the key — the sentence saying not to order
        #: the sequence in a marked row — is printed only under the caption on the first. A reader
        #: opening at a continuation page saw a printed 16-mer flagged with a bare dagger and no
        #: statement of what the dagger meant. Everything else on a continuation page is
        #: recoverable by turning back; this one is the wrong-reagent hazard the whole deposit is
        #: built around, so it rides in the <thead>, which paged media repeats on every page.
        #: ⚠ A CONTINUATION PAGE REPEATS THE MARKED COLUMN HEADERS AND NOT THE NOTES THAT DEFINE
        #: THEM. Superscript note markers ride in the header row, so a reader landing on page two of
        #: a three-page table meets "on the sense strand¹" with note ¹ a page back. The notes
        #: themselves are too long to repeat on every page without swamping the table, so the header
        #: says where they are instead — which is the difference between a reader who knows to turn
        #: back and one who does not know anything is missing.
        #: ⛔ ONE IMPLEMENTATION, SHARED WITH THE MANUSCRIPT STYLE. These two paths had separate
        #: copies of this logic, and the copy the deposit build used was the one that fell behind:
        #: `_label_for_spliced_table` is the manuscript style's, and everything verified in the
        #: journal build had to be re-verified there by hand. `table_label` is now both.
        _CURRENT_TABLE_LABEL = table_label(number, payload if isinstance(payload, str) else "")
        _IN_FLOAT_CAPTION = True
        try:
            inner = markdown_to_html(payload)
        finally:
            _CURRENT_TABLE_LABEL = None
            _IN_FLOAT_CAPTION = False
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
/* ⛔ AND IT MUST NOT MERGE WITH WHAT FOLLOWS IT. Measured in the built PDFs (2026-08-20): the
   tightest gap between a sequence's closing prime and the next word was 1.87 pt, under the 3 pt
   x-tolerance every common PDF text extractor defaults to, so `…CATCAAAC-3′ (antisense` came out
   of the text layer as one run. The prime is a narrow glyph whose ink stops short of its advance,
   so the gap an extractor measures is smaller than the gap a reader sees.
   ⚠ THE PADDING IS CONDITIONAL, AND THAT IS THE WHOLE POINT. A first attempt set it on `.seq`
   unconditionally and the built PDF printed `5′-CAGTGGGCTCTCCACG-3′ ,` — a visible space before a
   comma, which reads as a typo and is a worse defect than the one it fixed. `pad` is added by the
   renderer only where a WHITESPACE follows the sequence, so a sequence that ends a clause keeps
   its punctuation tight against the prime. */
pre { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 0.82em;
      background: #f4f4f4; border-left: 2pt solid #c8d2dc; padding: 5pt 7pt; margin: 0 0 8pt 0;
      white-space: pre-wrap; word-break: normal; overflow-wrap: normal; hyphens: none;
      line-height: 1.35; text-align: left; break-inside: avoid; }
.seq { white-space: nowrap; hyphens: none; }
.seq.pad { margin-right: 0.16em; }
/* ⛔ A JUSTIFIED LINE IS EMITTED IN SEVERAL PIECES AND CHROMIUM DOES NOT EMIT THEM IN VISUAL ORDER.
   MEASURED ONE VARIABLE AT A TIME ON RENDERED PDFs (2026-08-19): over a control paragraph set in
   this stylesheet, `text-align: justify` produces 8 same-line reading-order inversions in 184 text
   runs and `text-align: left` produces 0 in 122 — a justified line is broken into segments and the
   segments are painted out of order, so a content-order extractor reads them out of order too.
   font-kerning, font-variant-ligatures, text-rendering, letter-spacing, word-spacing and
   text-wrap: stable were each tried ON TOP of justification and every one measured identically to
   plain justify, 8/184. There is no lever but the alignment.

   ★ THE CONSEQUENCE IS THE DEPOSIT'S HIGHEST-STAKES TEXT: pdfminer returned "…agrees
   5′-CAGGGCATATCTTGCA-3′ exon exon 17, 9, at at independently" where the page reads
   "…5′-GGGCATATCTCTATAA-3′ at exon 17, 5′-CAGGGCATATCTTGCA-3′ at exon 9" — the sequence and the
   junction it belongs to, swapped. So the rule is scoped exactly to the hazard: a paragraph that
   PRINTS a sequence goes ragged-right, and every other paragraph stays justified.

   ★★ MEASURED IN THE BUILT PDFs with pdfminer's DEFAULT LAParams — the settings this repository's
   guards and a stock pdfminer install use. The test asks whether each of the 66 delimited sequences
   the article prints in prose is still CONTIGUOUS with the 40 source characters that follow it,
   compared on letters and digits only so a hyphenation or a line break cannot be mistaken for a
   reordering:
       journal, two columns    12 of 66 broken  ->  0 of 66
       manuscript, one column   0 of 66 broken  ->  0 of 66
   ⚠ AND THE INSTRUMENT IS PART OF THE RESULT, WHICH IS WHY IT IS NAMED. Read with
   `line_margin=0.35` the same two journal builds measure 24 -> 16 rather than 12 -> 0: a tight line
   margin makes every line its own text box and `boxes_flow` then interleaves the two columns, which
   swamps the signal. On that same reading a GLOBAL `text-align: left` scores 17 against this rule's
   16 — the blunt version of the fix is not the better one, which is why justification is kept
   everywhere a sequence is not printed. The single-column submission build, the one that is
   deposited, measured clean under every setting tried. */
p[data-seq], li[data-seq] { text-align: left; }
/* A DOI, a PMID or a URL is copied whole or it is worthless, and its own hyphens are the break
   points a renderer reaches for first. `nowrap` is safe here for a measured reason: the longest
   locator this paper prints is 33 characters — `doi:10.1016/S1470-2045(19)30319-5`, counted over
   all 48 — and the narrowest container either style produces is the journal's 88 mm column, which
   holds far more than that at the 7.9 pt the reference list is set at. */
a.loc { white-space: nowrap; hyphens: none; word-break: normal; overflow-wrap: normal; }
a.loc code { white-space: nowrap; }
/* ⛔ THE TWO GLYPHS THAT BECOME A TYPE 3 FONT IN BOLD. See MARKER_GLYPH_RE for the measurement.
   `font-weight: inherit` is deliberate — DejaVu Sans Bold carries both, so the marker keeps the
   weight of the text it sits in and only the FACE changes. */
.mk { font-family: 'DejaVu Sans', 'Liberation Sans', sans-serif; font-weight: inherit; }
a { color: #14507d; text-decoration: none; }
table { border-collapse: collapse; width: 100%; font-family: 'Liberation Sans', Helvetica, Arial,
        sans-serif; line-height: 1.28; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
/* A block heading row belongs to the rows beneath it, never to the page above. */
tr.blockhead { break-after: avoid; break-before: auto; }
tbody.rowblock { break-inside: avoid; }
tr.tablename th { text-align: left; font-weight: 700; background: #eef3f8; color: #123a5e;
                  border-bottom: 0; letter-spacing: 0.01em; }

/* ⚠ `overflow-wrap: anywhere` — the obvious choice for a twelve-column table — also shrinks a
   cell's MIN-CONTENT width to a single character, so the browser sized every column far too narrow
   and broke headers mid-word ("designs screene / d"). `break-word` wraps at spaces and breaks only
   a word that genuinely cannot fit, which is what the long oligo sequences need. */
th, td { border: 0.4pt solid #b9c2cb; padding: 2.2pt 4.8pt; text-align: left;
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
p { margin: 0 0 8pt 0; text-align: justify;  text-wrap: pretty;  orphans: 2; widows: 2; }
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
tr.tablename th { text-align: left; font-weight: 700; background: #eef3f8; color: #123a5e;
                  border-bottom: 0; letter-spacing: 0.01em; }

table { font-size: 7.4pt; }
/* Each display item takes its own page, EXCEPT the first: `break-before: page` on every figure left
   the "Figure legends" heading and its two-sentence preamble alone on a page with nothing under
   them (measured 2026-08-17). The first figure now follows the preamble it belongs to. */
figure.figure { margin: 0 0 6pt 0; text-align: center; break-inside: avoid; break-before: page; }
figure.figure.lead { break-before: auto; }
figure.figure svg { max-height: 218mm; width: auto; }
/* ⛔ WIDOW CONTROL, BECAUSE `break-inside: avoid` SILENTLY GIVES UP ON A LONG BLOCK (2026-08-19).
   Table 5's caption is the longest in the paper — taller than a page in this format — so the
   renderer cannot honour `avoid` and falls back to breaking it wherever it lands. It landed with a
   single trailing clause alone on its own page: manuscript page 42 carried the running head and
   "reagent's own loci are neither cleaner nor dirtier for being its own." and nothing else, 110
   characters against a median page of 4,362. `avoid` is a preference; orphans/widows is the floor
   that applies once the preference is abandoned, and it is what stops a one-line page. */
p.legend { font-size: 9pt; text-align: left; margin-bottom: 16pt; break-before: avoid;
           break-inside: avoid; orphans: 3; widows: 3; }
/* A table caption must not be stranded at the foot of a page away from its table. */
p.legend.caption { break-before: auto; break-after: avoid; margin-bottom: 4pt; }
/* ⛔ CAPTION FOOTNOTES ARE SET TIGHTER THAN FIGURE LEGENDS, AND THIS IS A MEASURED FIX, NOT A
   PREFERENCE (2026-08-19). Chromium's print path does not honour `widows`/`orphans` inside a box
   it has already given up on for `break-inside: avoid`, so no widow rule could stop Table 6's
   caption block spilling one line onto its own page. The block simply has to FIT. Table 6 carries
   seven notes under its caption at 16pt of margin each -- about eight lines of pure inter-paragraph
   space where one line had to be recovered. Tightening only these (never the caption itself, never
   a figure legend) reclaims it structurally, and `test_no_page_is_nearly_empty` measures the
   result on every build so the next content change cannot quietly bring the page back. */
p.legend.note { margin-bottom: 7pt; }
section.landscape { page: landscape; }
/* The identity block under the title: which document this is, and which build. */
p.version { font-size: 8.4pt; color: #46545f; margin: -6pt 0 12pt 0; text-align: left; }
p.sitrace { font-size: 9pt; margin: 0 0 10pt 0; text-align: left; }
p.sitrace .of { font-style: italic; }
"""

#: ⭐ THE VENUE'S OWN GEOMETRY, WHERE IT HAS BEEN MEASURED (2026-08-20). A page charge makes the
#: printed page count a cost, and no journal publishes the typeset design that decides it, so it is
#: measured off the journal's own published PDFs by scripts/venue_typeset_geometry.py and applied
#: here. A paper with no `geometry` key keeps the values below, which is why adding this moved no
#: existing build: the preprint renders byte-identically before and after.
#: ⚠ These are OUR RENDERING of the venue's geometry, not the venue's own typesetting. The page
#: count that follows is a much better estimate than an arbitrary house style, and it is still an
#: estimate: the journal sets copy, not just measure, and its production house is not this script.
DEFAULT_GEOMETRY = {
    "page_size": "A4", "margin": "16mm 14mm 15mm 14mm", "landscape_margin": "14mm 12mm",
    "font_pt": 9.0, "line_height": 1.40, "column_gap_mm": 6.0,
}

def journal_css(paper=None):
    g = dict(DEFAULT_GEOMETRY)
    g.update((paper or {}).get("geometry") or {})
    return COMMON + f"""
@page {{ size: {g["page_size"]}; margin: {g["margin"]}; }}
@page landscape {{ size: {g["page_size"]} landscape; margin: {g["landscape_margin"]}; }}

body {{ font-family: 'Liberation Serif', 'Times New Roman', Times, serif;
       font-size: {g["font_pt"]}pt;
       line-height: {g["line_height"]}; color: #14181c; margin: 0; hyphens: auto; }}
""" + JOURNAL_CSS_REST + f"""
/* ⛔ LAST, NOT FIRST. The main sheet below sets `.cols {{ column-gap: 6mm }}` itself, so an
   override placed above it is dead on arrival — later rule wins at equal specificity. Measured:
   the first version of this hook emitted the gap before the sheet and changed nothing. */
.cols {{ column-gap: {g["column_gap_mm"]}mm; }}
"""

JOURNAL_CSS_REST = """

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
.version { font-size: 7.6pt; color: #5a6b7a; margin: -6pt 0 10pt 0; letter-spacing: 0.01em; }

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
p { margin: 0 0 5pt 0; text-align: justify;  text-wrap: pretty;  orphans: 2; widows: 2; }
.cols > p + p { text-indent: 1.1em; }
hr { display: none; }
ol, ul { margin: 0 0 6pt 0; padding-left: 13pt; }
li { margin-bottom: 3pt; text-align: justify; }

/* ⚠ JUSTIFIED LINES BEFORE AN UNBREAKABLE 16-20-MER STRETCH, AND THERE IS NO SAFE LEVER. Three
   blind screens have now flagged the inter-word rivers, in both styles. `hyphens: auto` is already
   on WITH `lang="en"` on the root element (checked — Chromium silently declines to hyphenate
   without it), and the remaining cause is a 20-character token that must NOT break: breaking a
   sequence is the wrong-reagent hazard this whole deposit is built to prevent.

   ⭐ THE "NO SAFE LEVER" CLAIM IS NOW MEASURED RATHER THAN ASSERTED (2026-08-19). Baseline over
   BODY PROSE ONLY (spans >=10 pt; table and caption lines are set at 6.9-9 pt and measuring them
   alongside body text moves the median enough to change a verdict): 1,520 lines, median inter-word
   gap 3.12 pt, worst line 11.02 pt, 20 lines above 2x median and 3 above 3x.

   Two content-safe levers were tried and NEITHER HELPED:
     hyphenate-limit-chars: 5 2 2   -> identical on every figure. A no-op in this Chromium.
     .seq { font-size: 0.94em }     -> max 10.95, >2x 22, >2.5x 8, >3x 5. MIXED, not an improvement
                                      and not a clear regression either: narrowing the token
                                      re-wraps whole paragraphs and merely relocates the stretch.
   ⚠ An earlier note here called that second result "strictly worse". It was not — that reading came
   from an instrument that included table lines. Both levers are within noise of the baseline, which
   is a stronger statement of the same conclusion: the cause really is the unbreakable token, and
   nothing that leaves the token intact moves it.

   `text-wrap: pretty` remains the one improvement that cannot alter content. The residual
   stretching is an ACCEPTED limitation, and `test_justification_does_not_degrade` pins the
   measurement so a future change cannot make it worse unnoticed. */
/* --- floats: tables and figures set where they are first cited --- */
.float { break-inside: avoid; margin: 4pt 0 9pt 0; }
/* ⛔ MUST OUTRANK `.float` AND `.tablewrap`, WHICH BOTH CARRY `break-inside: avoid` (2026-08-20).
   A narrow table set in one column is taller than the space left at the foot of a column, so an
   unbreakable one JUMPS and leaves the rest of that column blank -- measured as ~2,000 characters
   of white on page 1. Rows stay unbreakable; the table itself may split. The first attempt put
   these rules above `.float` and changed nothing, at equal specificity. */
.float.col-float, .float.col-float .tablewrap { break-inside: auto; }
.float.col-float tr, .float.col-float tbody.rowblock { break-inside: avoid; }
/* ⛔ A FIGURE FORCING ITS OWN PAGE COSTS A SHORT PAPER A WHOLE PAGE (2026-08-20). `figure.figure`
   carries `break-before: page` so that each display item of the 58-page preprint gets its own
   page. In a 7-page article the same rule ended page 2 at 3,769 characters against a 6,809
   maximum -- half a page of white to place one figure. Papers that opt into in-column tables get
   in-flow figures too: the figure lands where it is cited, which is also where a reader wants it. */
.cols figure.figure { break-before: auto; }
.span-float { column-span: all; }
.col-float { margin: 0 0 8pt 0; }
.col-float table { break-inside: auto; }
.col-float tr { break-inside: avoid; }
.col-float table { font-size: 6.6pt; line-height: 1.2; width: 100%; }
/* ⛔ See the wide_body comment in the table emitter: an inline table wider than the column it
   sits in overprints its neighbour. Spanning both columns and shrinking is what makes it
   readable at all; break-inside keeps it from splitting across the span boundary. */
.wide-body-table { column-span: all; font-size: 6.4pt; line-height: 1.22; break-inside: avoid;
                   width: 100%; table-layout: fixed; margin: 2mm 0 3mm 0; }
.wide-body-table td, .wide-body-table th { padding: 0.6mm 1.35mm; word-break: normal;
                                           overflow-wrap: anywhere; }
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
.backmatter-inline { font-size: 7.9pt; line-height: 1.36; }
.backmatter-inline h2 { font-family: 'Liberation Sans', Helvetica, sans-serif; font-size: 8.6pt;
                        margin: 10pt 0 3pt 0; }
.backmatter-inline p { margin: 0 0 4pt 0; }
.backmatter h2 { font-family: 'Liberation Sans', Helvetica, sans-serif; font-size: 8.6pt;
                 color: #123a5e; margin: 9pt 0 4pt 0; font-weight: 700; break-after: avoid; }
.backmatter h2:first-child { margin-top: 0; }
.backmatter p { margin: 0 0 4pt 0; }
#references-list { padding-left: 11pt; }
#references-list li { text-align: left; margin-bottom: 2.6pt; }
"""


def wrap_manuscript(front_title, body_html, front_block=""):
    body_html = re.sub(r"(<h2>Tables</h2>)(.*?)(?=<h2>)",
                       lambda m: '<section class="landscape">' + m.group(1) + m.group(2)
                       + "</section>", body_html, count=1, flags=re.S)
    body_html = re.sub(r"(<h2>References</h2>.*?)<ol", r'\1<ol id="references-list"',
                       body_html, count=1, flags=re.S)
    #: The identity block goes directly under the H1, which is where a screener looks and where the
    #: old build carried nothing at all: no date, no version, no build.
    if front_block:
        body_html = re.sub(r"(</h1>)", r"\1" + front_block, body_html, count=1)
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


def wrap_journal(paper, front, body_html, doc_title=None):
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
        f'<p class="version">{_html.escape(provenance_line(paper, "journal"))}</p>'
        '<div class="abstract"><h2>Abstract</h2>'
        f'<p>{inline(front["abstract"])}</p></div>'
        f'<p class="kw"><strong>Keywords</strong> &nbsp;{inline(front["keywords"])}</p>'
    )
    return page_shell(doc_title or re.sub(r"[*_`]", "", front["title"]), journal_css(paper),
                      head + (
                          # ⛔ A SECOND `column-count` CONTAINER CANNOT SHARE A PAGE WITH THE FIRST,
                          # so splitting the back matter out forces a page break wherever the body
                          # happens to end. On the 58-page preprint that costs nothing. On a 7-page
                          # article it left page 5 at 3,917 characters against a 6,751 maximum —
                          # half a page of billed white to start Declarations on a fresh one.
                          # Papers opt in to flowing the back matter in the same columns; the
                          # smaller back-matter type is kept either way.
                          f'<div class="cols">{main}'
                          f'<div class="backmatter-inline">{back}</div></div>'
                          if (paper.get("layout") or {}).get("backmatter_in_flow")
                          else f'<div class="cols">{main}</div>'
                               f'<div class="backmatter">{back}</div>'))


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


#: The documents a built PDF is a rendering OF. A stamp beside each PDF records the sha256 of each
#: at build time, so "is this PDF current?" is answered by CONTENT rather than by mtime.
STAMP_SOURCES = (
    "aso/fusion-junction-aso-research-article.md",
    "aso/fusion-junction-aso-submission-tables.md",
    "aso/fusion-junction-aso-submission-references.md",
    "aso/fusion-junction-aso-sequences.csv",
)


#: The file the paper tells a reader to order from, read out of the stamped source list above so the
#: running footer and the build stamp cannot come to name different files (rule 1).
ORDER_FROM = next(os.path.basename(p) for p in STAMP_SOURCES if p.endswith(".csv"))

#: The handling statement in both lengths. ⛔ THE FULL SENTENCE IS THE ONE THAT MATTERS AND IT IS NOT
#: FREE. It carries the destination — order from the CSV, never from this PDF — and at 110
#: characters, repeated on every page, it is also the string that splices into a body sentence at
#: every page boundary in content order (measured: 27 sentences in the journal build, 50 in the
#: manuscript build, in the order pypdf and every non-layout indexer reads). The short rule keeps
#: the prohibition and drops the destination, and is used ONLY on pages from which nothing can be
#: ordered: no sequence, no table, not page 1. `_postprocess` verifies that split page by page.
FOOTER_FULL = ("Research use only — not for administration. "
               f"Order from {ORDER_FROM}, never from this PDF.")
FOOTER_SHORT = "Research use only — not for administration."


def templates(running_head, footer_text):
    # 8px = 6 pt, the floor below which a screen reader called the header unreadable. It was 7px
    # (5.2 pt) because the full 30-word title had to be squeezed in; the declared running title is
    # five words and needs no squeezing.
    style = ("font-size:8px;font-family:'Liberation Sans',Helvetica,sans-serif;color:#7c8b99;"
             "width:100%;padding:0 14mm;display:flex;justify-content:space-between;")
    header = (f'<div style="{style}"><span>{_html.escape(running_head)}</span>'
              '<span></span></div>')
    #: ⛔ THE FOOTER CARRIES THE HANDLING STATEMENT ON EVERY PAGE (blind safety screen, 2026-08-19).
    #: 20 of the 27 pages that print a sequence carried no handling language of any kind — 125 of
    #: ~194 printed instances — because captions do not repeat onto table continuation pages. Those
    #: are exactly the pages a reader reaches by extraction, search or print-selection, and every
    #: per-table safeguard silently dropped out on them. A running footer is the only element paged
    #: media puts on every page unconditionally.
    footer = (f'<div style="{style}">'
              f"<span>{_html.escape(footer_text)}</span>"
              '<span class="pageNumber"></span></div>')
    return header, footer


#: A page from which something could be ordered keeps the FULL handling sentence. The test is on the
#: RENDERED page, not on the source: what matters is what a reader holding that one sheet can see.
_PAGE_HAS_SEQUENCE = re.compile(r"5[′'’]\s?-\s?[ACGTUacgtu]{8,40}\s?-\s?3[′'’]|\b[ACGT]{12,}\b")
_PAGE_HAS_TABLE = re.compile(r"^\s*Table \d+", re.M)


def _pages_needing_the_full_footer(reader):
    keep = {0}                                              # page 1 always states the destination
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if _PAGE_HAS_SEQUENCE.search(text) or _PAGE_HAS_TABLE.search(text):
            keep.add(index)
    return keep


def _body_of(page, head):
    """A page's text with the running head, either footer and the page number removed."""
    text = re.sub(r"\s+", " ", page.extract_text() or "")
    for chrome_bit in (head, FOOTER_FULL, FOOTER_SHORT):
        text = text.replace(re.sub(r"\s+", " ", chrome_bit), " ")
    return re.sub(r"[^A-Za-z0-9]", "", text)


def _repair_outline_titles(writer, headings):
    """Put the spaces back into the bookmark titles Chromium builds from a WRAPPED heading.

    ⛔ MEASURED IN THE BUILT PDF (2026-08-19). `generateDocumentOutline` names each entry from the
    heading's LAID-OUT lines and joins them without a separator, so the document's own title — the
    only entry a reader is certain to see — read "…against the NR4A3fusions of extraskeletal myxoid
    chondrosarcoma pair a wild-typeparent gene…" in the navigation pane. Any heading that wraps is
    affected; the short ones happen not to.

    ⚠ REPAIRED BY EXACT MATCH ONLY. Each entry is matched to a heading of the rendered document with
    all whitespace removed, and rewritten only when exactly that heading is found. A title this
    cannot match is left as Chromium wrote it rather than guessed at.
    """
    from pypdf.generic import NameObject, TextStringObject
    index = {}
    for heading in headings:
        index.setdefault(re.sub(r"\s+", "", heading), " ".join(heading.split()))
    root = writer._root_object.get("/Outlines")
    repaired, seen = 0, set()

    def walk(node):
        nonlocal repaired
        child = node.get("/First")
        while child is not None:
            obj = child.get_object()
            if id(obj) in seen:
                break
            seen.add(id(obj))
            title = str(obj.get("/Title", ""))
            want = index.get(re.sub(r"\s+", "", title))
            if want and want != title:
                obj[NameObject("/Title")] = TextStringObject(want)
                repaired += 1
            walk(obj)
            child = obj.get("/Next")

    if root is not None:
        walk(root.get_object())
    return repaired


_HEADING_RE = re.compile(r"<h([1-3])[^>]*>(.*?)</h\1>", re.S | re.I)


def headings_of(html):
    """The text of every heading the rendered page carries, for the outline repair above."""
    out = []
    for _level, inner in _HEADING_RE.findall(html):
        text = _html.unescape(re.sub(r"<[^>]+>", "", inner))
        if text.strip():
            out.append(" ".join(text.split()))
    return out


def _postprocess(full_pdf, short_pdf, pdf_path, running_head, meta, headings=()):
    """Assemble the delivered PDF: short rule on body pages, and a real Info dictionary.

    ⛔ TWO RENDERS, ONE LAYOUT, AND THE EQUALITY IS CHECKED RATHER THAN ASSUMED. The two prints
    differ only in a footer template, which sits in the page margin and cannot reflow the content
    box — but "cannot" is the word this file's history keeps disproving, so every page's body text
    is compared between the two renders and any difference at all aborts the splice and ships the
    full-footer render unchanged. A wrong page grafted into a deposit is far worse than a long
    footer on it.

    ⛔ AND THE METADATA IS THE OTHER HALF. Before this, all three PDFs carried `/Creator` =
    a headless-Chrome UA string, no `/Author`, no `/Subject`, no `/Keywords`, and — between the two
    full builds — a byte-identical `/Title`, so the deposit contained two 200-page-equivalent
    documents that Document Properties could not tell apart.
    """
    try:
        import pypdf
    except ImportError as exc:                              # pragma: no cover - env dependent
        raise SystemExit(
            f"pypdf is not importable ({exc}), so this build could set no PDF metadata and could "
            "not vary the handling footer by page. Both are deposit requirements — install pypdf "
            "rather than shipping a PDF whose Document Properties name headless Chrome.")
    import io

    full = pypdf.PdfReader(io.BytesIO(full_pdf))
    writer = pypdf.PdfWriter(clone_from=io.BytesIO(full_pdf))
    grafted = 0
    if short_pdf:
        short = pypdf.PdfReader(io.BytesIO(short_pdf))
        keep = _pages_needing_the_full_footer(full)
        same_length = len(short.pages) == len(full.pages)
        bodies_match = same_length and all(
            _body_of(full.pages[i], running_head) == _body_of(short.pages[i], running_head)
            for i in range(len(full.pages)))
        if not bodies_match:
            print("  ⚠ the two footer renders do not paginate identically — shipping the full "
                  "handling sentence on every page", file=sys.stderr)
        else:
            for index in range(len(full.pages)):
                if index in keep:
                    continue
                writer.add_page(short.pages[index])
                donor = writer.pages[-1]
                writer.pages[index][pypdf.generic.NameObject("/Contents")] = donor.raw_get(
                    "/Contents")
                writer.pages[index][pypdf.generic.NameObject("/Resources")] = donor.raw_get(
                    "/Resources")
                del writer.pages[len(writer.pages) - 1]
                grafted += 1
    writer.add_metadata({k: v for k, v in meta.items() if v})
    _repair_outline_titles(writer, headings)
    #: Grafting a page's content leaves the render it replaced in the file as an orphan, and cloning
    #: brings a second copy of every shared font subset. Measured on the journal build: 2,560 KB
    #: before this call and 2,074 KB after, with the outline, all 111 link annotations and the Info
    #: dictionary intact. A deposit file is uploaded and downloaded, so 19% is worth one call.
    try:
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    except Exception as exc:                                # pragma: no cover - pypdf < 4.x
        print(f"  ⚠ could not compress the output ({exc}); the PDF is correct but larger",
              file=sys.stderr)
    with open(pdf_path, "wb") as fh:
        writer.write(fh)
    return grafted, len(full.pages)


def print_pdf(chrome, html_path, pdf_path, running_head, meta=None, split_footer=True,
              headings=()):
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

        def render(footer_text):
            header, footer = templates(running_head, footer_text)
            #: ⛔ `generateDocumentOutline` IS THE WHOLE FIX FOR "NO BOOKMARKS" AND IT IS ONE FLAG.
            #: Measured 2026-08-19: 0 outline entries across 116 pages with six numbered sections,
            #: seven tables, four figures, Declarations and 52 references. Chromium builds the
            #: outline from the heading elements the builder already emits.
            return base64.b64decode(ws.call(
                "Page.printToPDF", printBackground=True, preferCSSPageSize=True,
                generateDocumentOutline=True, displayHeaderFooter=True,
                headerTemplate=header, footerTemplate=footer)["data"])

        full_pdf = render(FOOTER_FULL)
        short_pdf = render(FOOTER_SHORT) if split_footer else None
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
    return _postprocess(full_pdf, short_pdf, pdf_path, running_head, meta or {}, headings)


# --------------------------------------------------------------------------- driver


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
    #: ⛔ THIS USED TO IGNORE ITS `paper` ARGUMENT AND ITERATE THE MODULE CONSTANT (fixed 2026-08-20,
    #: when a second paper was registered). With one entry in PAPERS the bug was invisible; with two
    #: it stamps the second paper's PDF with the FIRST paper's hashes, so the stamp reports current
    #: for a PDF built from something else — the exact failure the stamp exists to prevent.
    stamp = {"built_from": {}}
    for rel in paper.get("stamp_sources", STAMP_SOURCES):
        src = os.path.join(HERE, rel)
        if os.path.exists(src):
            stamp["built_from"][rel] = hashlib.sha256(open(src, "rb").read()).hexdigest()
    stamp["_what"] = ("sha256 of each document this PDF renders, written by build_submission_pdf.py. "
                      "A PDF is current when every hash here matches the file on disk; mtimes are "
                      "not evidence, because the regeneration chain rewrites unchanged files.")
    with open(pdf_path.replace(".pdf", ".build-stamp.json"), "w", encoding="utf-8") as fh:
        json.dump(stamp, fh, indent=1, sort_keys=True)
        fh.write("\n")

def build_supplementary(paper, html_only=False):
    """Render the Supplementary Information to PDF, with the repository front matter stripped.

    ⛔ WHY THIS EXISTS. The manuscript names `fusion-junction-aso-supplementary-information.md` as the
    file deposited beside it, and until 2026-08-19 there was no build for it at all — so the SI would
    have been uploaded as raw markdown carrying its YAML front matter: `id: DOC-...`, `level: L3`,
    `status: live`, `canonical_for:`, `audience:`, `last_verified:`, and a build note reading "THIS
    DOCUMENT IS IN NEITHER PDF BUILD, so nothing in it is stripped before a reader sees it". That note
    was true and was the bug. It is the one place the "no internal repository artefacts in a deposited
    document" rule failed, and `.md` is not a format bioRxiv expects for supplementary material.
    """
    src = paper.get("supplementary")
    if not src:
        return 0
    body = apply_deposit_filenames(strip_frontmatter(read(src)), paper, "supplementary")
    title_m = re.search(r"^#\s+(.*)$", body, re.M)
    title = re.sub(r"[*_`]", "", title_m.group(1)) if title_m else "Supplementary Information"
    #: ⛔ THE SI DID NOT NAME ITS OWN PAPER AND DID NOT SAY IT WAS UN-REFEREED (blind screen,
    #: 2026-08-19). "peer review" appeared once in each full PDF and ZERO times in the SI; its title
    #: block carried a short standalone title that appears nowhere in the article, so an SI
    #: forwarded on its own — which is how a supplement travels — was traceable to no paper and
    #: announced itself as nothing in particular. Both facts are READ from the article and from the
    #: paper's own masthead declaration rather than restated here.
    article_title = re.search(r"^#\s+(.*)$", strip_frontmatter(read(paper["manuscript"])), re.M)
    article_pdf = deposit_filenames(paper)[os.path.basename(paper["manuscript"])]
    front_block = (
        '<p class="sitrace">Supplementary Information to <span class="of">'
        + inline(article_title.group(1)) + "</span>"
        + (f' — deposited as <code>{_html.escape(article_pdf)}</code>' if article_pdf else "")
        + ".</p>"
        + f'<p class="version">{_html.escape(paper.get("journal", {}).get("preprint_note", ""))}'
        + f' · {_html.escape(provenance_line(paper, "supplementary"))}</p>')
    page = wrap_manuscript(title, markdown_to_html(body), front_block)
    out_name = paper["out"].replace(".pdf", "-supplementary-information.pdf")
    html_path = os.path.join(HERE, out_name.replace(".pdf", ".build.html"))
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    if html_only:
        print(f"SI: wrote {os.path.relpath(html_path, REPO)} (--html-only)")
        return 0
    chrome = find_chrome()
    if not chrome:
        print(f"SI: no chromium found; HTML is at {os.path.relpath(html_path, REPO)}")
        return 1
    pdf_path = os.path.join(HERE, out_name)
    meta = {
        "/Title": f"Supplementary Information — {re.sub(r'[*_`]', '', article_title.group(1))}",
        "/Subject": ("Supplementary Information to a preprint manuscript, not peer reviewed. The "
                     f"main text is {article_pdf}."),
        "/Author": re.sub(r"[*_`]", "",
                          label_paragraph(strip_frontmatter(read(paper["manuscript"])), "Author")),
        "/Keywords": re.sub(r"[*_`]", "",
                            label_paragraph(strip_frontmatter(read(paper["manuscript"])),
                                            "Keywords")),
        "/Creator": "build_submission_pdf.py (supplementary), Chromium print-to-PDF",
        "/CreationDate": time.strftime("D:%Y%m%d%H%M%S+00'00'", time.gmtime()),
    }
    print_pdf(chrome, html_path, pdf_path, declared_running_title(body)
              if re.search(r"running[- ]title", body, re.I) else title[:60], meta,
              headings=headings_of(page))
    #: ⚠ THE INTERMEDIATE IS DELETED HERE, AS IT IS IN `build` (2026-08-19). Without this the SI
    #: build left a `.build.html` beside the deposit artefacts on every run — untracked, so it
    #: turned up as a new file in `git status` and invited being committed as though it were a
    #: deliverable. No `.build.html` is tracked anywhere in this repository, and none should be.
    os.remove(html_path)
    print(f"SI: wrote {os.path.relpath(pdf_path, REPO)} "
          f"({os.path.getsize(pdf_path) // 1024} KB)")
    return 0


#: ⛔ THE TWO FULL BUILDS MUST NOT BE INTERCHANGEABLE IN A FILE MANAGER (blind screen of the deposit,
#: 2026-08-19). Both carried a byte-identical `/Title` and 99.76% identical text, neither named the
#: other, and the shorter, more canonical-looking filename is the typeset PREVIEW while the one to
#: upload is `…-manuscript.pdf`. A downloader taking the obvious file deposits the wrong artefact.
#: Each format now says in its own title and subject what it is and which file the other one is.
FORMATS = {
    "journal": ("[typeset preview]",
                "Typeset preview of a preprint manuscript. NOT the deposited version — the file to "
                "cite and deposit is {other}."),
    "manuscript": ("[submission manuscript]",
                   "Submission-format preprint manuscript: the version of record for this deposit. "
                   "A typeset preview of the same text is {other}."),
}


def build(name, paper, style="journal", html_only=False):
    body, floats = assemble(paper, style)
    # ⛔ ONE SOURCE FOR THE RUNNING HEAD IN BOTH STYLES. The manuscript declares it; neither
    # renderer may substitute anything else, and a manuscript that stops declaring one fails the
    # build rather than falling back to the full title.
    running = declared_running_title(body)
    suffix, subject = FORMATS[style]
    other = os.path.basename(paper["out"].replace(".pdf", "-manuscript.pdf")
                             if style == "journal" else paper["out"])
    plain_title = re.sub(r"[*_`]", "", re.search(r"^#\s+(.*)$", body, re.M).group(1))
    meta = {
        "/Title": f"{plain_title} {suffix}",
        "/Subject": subject.format(other=other),
        "/Author": re.sub(r"[*_`]", "", label_paragraph(body, "Author")),
        "/Keywords": re.sub(r"[*_`]", "", label_paragraph(body, "Keywords")),
        #: ⛔ NOT A BROWSER UA STRING. `/Creator` is what a screener reads under "Application", and
        #: it said `Mozilla/5.0 … HeadlessChrome/141.0.0.0`. `/Producer` stays Skia, which is true.
        "/Creator": f"build_submission_pdf.py ({style} style), Chromium print-to-PDF",
        "/CreationDate": time.strftime("D:%Y%m%d%H%M%S+00'00'", time.gmtime()),
    }
    if style == "journal":
        front = parse_front_matter(body)
        page = wrap_journal(paper, front, markdown_to_html(front["body"], floats),
                            meta["/Title"])
        out_name = paper["out"]
    else:
        page = wrap_manuscript(
            meta["/Title"], markdown_to_html(body, floats),
            f'<p class="version">{_html.escape(provenance_line(paper, "manuscript"))}</p>')
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
    grafted, pages = print_pdf(chrome, html_path, pdf_path, running, meta,
                               headings=headings_of(page))
    os.remove(html_path)
    _write_build_stamp(pdf_path, paper)
    size = os.path.getsize(pdf_path)
    print(f"{name} [{style}]: wrote {os.path.relpath(pdf_path, REPO)} "
          f"({size / 1024:.0f} KB, {pages} pages; the full handling sentence is on "
          f"{pages - grafted} of them and the short rule on {grafted})")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", choices=sorted(PAPERS))
    ap.add_argument("--style", choices=("journal", "manuscript"), default="journal",
                    help="journal = typeset article (default); manuscript = submission format")
    ap.add_argument("--html-only", action="store_true")
    args = ap.parse_args(argv)
    names = [args.paper] if args.paper else sorted(PAPERS)
    rc = max(build(n, PAPERS[n], args.style, args.html_only) for n in names)
    for n in names:
        rc = max(rc, build_supplementary(PAPERS[n], args.html_only))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
