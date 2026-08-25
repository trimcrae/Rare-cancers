#!/usr/bin/env python3
"""Build the individual, double-spaced files a Nucleic Acid Therapeutics submission uploads
BESIDE the manuscript, rather than composed into it.

⛔ WHY SEPARATE FILES AT ALL. Checklist items A7 ("upload individual files, not one composed
PDF") and A9 ("figure legends in a separate double-spaced file"). Every word in these files
already exists — in the manuscript, where the PDF builder reads it. What did not exist was a
standalone document per part, and a submission that does not conform is returned before peer
review (`build_submission_docx.py` quotes the guideline verbatim).

⛔⛔ AND THE ONE THING THIS FILE MUST NEVER DO IS RETYPE A WORD OF THE MANUSCRIPT. A second copy
of a legend, a title or a disclosure is the one-of-a-pair defect this repository keeps paying
for: the manuscript gets corrected, the separate file does not, and the submission carries two
descriptions of one thing. So every part is CUT OUT of the manuscript at build time, by the same
anchors the PDF builder uses, and this script owns no prose of its own — grep it; there is none.
If a legend or a disclosure is wrong, it is wrong in the manuscript, which is the only place to
fix it.

★ THE SET OF PARTS IS DECLARED; WHAT GOES IN EACH IS DERIVED. `build_submission_pdf.PAPERS`
already declares which display items each paper ships, and the manuscript already declares its
own section headings. A paper that gains a figure gains a legend here with no edit, and a part
whose source section is MISSING fails the build rather than shipping a short file.

⚠ DOUBLE-SPACED MEANS MEASURED, NOT ASSERTED. The spacing comes from
`build_submission_pdf.NAT_SUBMISSION_CSS`, which is where this repository already keeps the fact
that a NAT submission is 12 pt on 2.0 — imported, never restated. After conversion the .docx is
opened and its paragraph properties are READ: Word stores line spacing in twentieths of a point,
so double spacing at any size is `w:line="480" w:lineRule="auto"` (480 = 2 x 240). A file that
merely looks roomy fails. This matters because the HTML->Word path is a converter, not a promise:
`build_submission_docx.py` records LibreOffice silently dropping every inline SVG from a document
that otherwise converted perfectly.

⛔ THE TITLE PAGE IS THE IDENTITY FILE AND IS NOT PART OF A BLINDED UPLOAD. Under the
double-anonymized reading of NAT's self-contradicting guidelines the manuscript that reaches a
reviewer is `*-anonymized.pdf`, and everything `build_submission_pdf.anonymise` strips out of it
— the author, the correspondence address, the ORCID — is what this page carries instead. Uploading
both to a blinded slot would undo the redaction; the upload manifest in SUBMISSION-PACKET.md is
where each file's slot is named.

⚠ REQUIRES LibreOffice WITH THE WRITER FILTERS, exactly as `build_submission_docx.py` does, and for
the same reasons — both filters named explicitly, `libreoffice-core` alone is not enough.

    python3 research/manuscripts/build_submission_parts.py                 # every paper and part
    python3 research/manuscripts/build_submission_parts.py --paper aso-journal
    python3 research/manuscripts/build_submission_parts.py --part title-page
    python3 research/manuscripts/build_submission_parts.py --check         # verify, write nothing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_submission_pdf as bsp  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

#: Same filters `build_submission_docx.py` names, for the same measured reasons: without the input
#: filter the HTML loads as a Writer/Web document, and `--convert-to docx` alone aborts with "no
#: export filter found".
DOCX_FILTER = "docx:MS Word 2007 XML"
HTML_FILTER = "HTML (StarWriter)"

#: The papers that ship separate submission parts. ⛔ NAMED, NOT DERIVED FROM "has figures":
#: `build_submission_pdf` also builds a vaccine paper, and quietly writing a submission artefact
#: for a paper nobody asked about is how a submission folder grows files whose provenance
#: no one can explain.
PAPERS = ("aso-journal", "aso")

#: Word stores line spacing in twentieths of a point. Single is 240; double is 480.
#: `lineRule="auto"` makes it a multiple of the line rather than an exact height, which is what
#: "double-spaced" means to a copy-editor — the spacing follows the type size instead of
#: clipping it.
_DOUBLE_LINE_TWIPS = 480


def _manuscript(paper):
    return open(os.path.join(HERE, paper["manuscript"]), encoding="utf-8").read()


def _title(paper):
    return re.sub(r"[*_`]", "", re.search(r"^#\s+(.*)$", _manuscript(paper), re.M).group(1))


def _legend_blocks(paper):
    """(label, markdown) per figure legend, cut from the manuscript. Never written here.

    ⛔ THE SAME ANCHOR THE PDF USES. `split_figures` finds a legend by the literal `**Figure N.`
    that opens its paragraph and reads to the next such opener; matching any other way would let
    the two builders disagree about where a legend ends, which is the defect that produces a
    truncated caption in one artefact and a whole one in the other.
    """
    body = _manuscript(paper)
    figures = paper.get("figures") or {}
    if not figures:
        raise SystemExit("this paper declares no figures, so it has no legends to separate")
    _, end, after_heading = bsp.section_span(body, "Figure legends")
    section = body[after_heading:end]
    out = {}
    for prefix in figures:
        m = re.match(r"(?:Supplementary )?Figure S?(\d+)\.", prefix)
        if not m:
            raise SystemExit(f"figure key {prefix!r} is neither 'Figure N.' nor "
                             f"'Supplementary Figure SN.'")
        number = int(m.group(1)) + (bsp.SUPPLEMENTARY_SORT_BASE
                                    if "Supplementary" in prefix else 0)
        match = re.search(r"^\*\*" + re.escape(prefix)
                          + r".*?(?=^\*\*(?:Supplementary )?Figure S?\d+\.|\Z)",
                          section, re.M | re.S)
        if not match:
            raise SystemExit(
                f"⛔ no legend for {figures[prefix]}: the manuscript's '## Figure legends' section "
                f"has no paragraph opening '**{prefix}'. A submission whose legends file is short "
                f"one figure is returned; fix the manuscript, not this script.")
        out[number] = (prefix, match.group(0).strip())
    return [out[k] for k in sorted(out)]


#: What a Sage title page carries, in the order Sage's own manuscript-preparation list gives it,
#: and where each part is CUT FROM in the manuscript. `heading` names a `## ` section; `label`
#: names a bold run-in paragraph; `required` False means a paper may legitimately not carry it.
#: ⛔ NOTHING HERE IS A STRING OF PROSE — every entry is an ADDRESS. The moment one of these
#: becomes a default value rather than a lookup, the title page starts disagreeing with the paper.
_TITLE_PAGE_PARTS = (
    {"label": "Author.", "required": True},
    {"pattern": r"(?m)^\*Independent [Rr]esearcher[^\n]*(?:\n(?!\s*\n)[^\n]*)*",
     "what": "the affiliation, correspondence address and ORCID", "required": True},
    {"label": "Running title.", "required": True},
    {"heading": "Keywords", "required": True},
    {"heading": "Acknowledgments", "required": True},
    {"heading": "Author Disclosure Statement", "required": True},
    #: ⚠ THE FUNDING STATEMENT IS A RUN-IN PARAGRAPH INSIDE `## Statements and Declarations`,
    #: not a section of its own, and Sage asks for it on the title page. Cut by its own label so
    #: the rest of that section — ethics, consent, data availability — stays in the manuscript
    #: where the reviewer reads it.
    {"label": "Funding statement.", "required": True},
)


def _run_in_paragraph(body, label):
    """The paragraph opening `**{label}**`, whole, including its continuation lines."""
    m = re.search(r"(?m)^\*\*" + re.escape(label) + r"\*\*[^\n]*(?:\n(?!\s*\n)[^\n]*)*", body)
    return m.group(0).strip() if m else ""


def _title_page_blocks(paper):
    """(label, markdown) per title-page element, cut from the manuscript. Never written here.

    ⛔ A TITLE PAGE IS THE EASIEST FILE IN A SUBMISSION TO RETYPE AND THE WORST ONE TO GET WRONG:
    the portal states, verbatim, that "the author information you enter at submission must exactly
    match what is included on your manuscript and/or title page". Two hand-kept copies of a name,
    an ORCID or a disclosure is precisely the mismatch that sentence is about, so every element
    below is read out of the manuscript at build time and a missing one fails the build.
    """
    body = _manuscript(paper)
    #: ⚠ "Title." IS THE ONE STRING THIS SCRIPT CONTRIBUTES, and it is a field label rather than
    #: prose — the manuscript's title is an H1 with no label of its own, and a title page that
    #: opens with a bare sentence reads as a stray line. It is carried as the block's LABEL so
    #: `_probe` strips it back off: what gets verified against the manuscript is the title.
    out = [("Title.", "**Title.** " + _title(paper))]
    for part in _TITLE_PAGE_PARTS:
        if "heading" in part:
            try:
                _, end, after = bsp.section_span(body, part["heading"])
            except (SystemExit, ValueError, AttributeError):
                text = ""
            else:
                text = body[after:end].strip().strip("-").strip()
            #: ⚠ THE HEADING TRAVELS WITH THE SECTION — UNLESS THE SECTION ALREADY SAYS IT.
            #: Without it the disclosure and the acknowledgment arrive as two unlabelled
            #: paragraphs and a copy-editor cannot tell which is which. But `## Keywords` opens
            #: with its own run-in `**Keywords.**`, so adding the heading printed the word twice
            #: on consecutive lines. The heading text is the MANUSCRIPT'S own either way; whether
            #: to repeat it is decided by looking at the section, not by naming an exception.
            already = re.match(r"\s*\*\*" + re.escape(part["heading"]) + r"[.:]?\*\*", text or "")
            text = f"### {part['heading']}\n\n{text}" if text and not already else text
            label, what = part["heading"], f"the '## {part['heading']}' section"
        elif "label" in part:
            text = _run_in_paragraph(body, part["label"])
            label, what = part["label"], f"the '**{part['label']}**' paragraph"
        else:
            m = re.search(part["pattern"], body)
            text, label, what = (m.group(0).strip() if m else ""), "", part["what"]
        if not text:
            if part.get("required"):
                raise SystemExit(
                    f"⛔ the title page cannot be built: {what} is not in "
                    f"{paper['manuscript']}. A title page assembled around a hole would either "
                    f"ship short or invite someone to type the missing line here, and a typed "
                    f"line is the copy that goes stale. Fix the manuscript.")
            continue
        out.append((label, text))
    return out


#: Each part: how its blocks are cut, what the standalone file is called, its H1, and the
#: shortest probe `_verify` will accept for one of its blocks.
#: ⚠ `min_probe_words` IS PER PART BECAUSE THE BLOCKS ARE NOT THE SAME SHAPE. A legend is a
#: paragraph and a six-word probe of it is a real content check; "**Author.** Tristan D. McRae"
#: is three words long in total, and demanding six of it would fail a correct file. What both
#: need is a probe made of CONTENT rather than of the label, which `_probe` guarantees for each.
PARTS = {
    "title-page": {
        #: ⛔ THE JOURNAL SUBMISSION ONLY, AND MEASURED RATHER THAN ASSUMED. The extended report
        #: carries no `## Keywords` section because it is deposited rather than submitted, so
        #: building it a title page would either fail the build or ship a page with a hole —
        #: and the honest reading of both outcomes is that a paper with no venue has no title
        #: page to upload.
        "papers": ("aso-journal",),
        "blocks": _title_page_blocks,
        "suffix": "-title-page.docx",
        "h1": "Title page",
        "min_probe_words": 2,
        #: ⛔ NO PROVENANCE LINE ON THIS ONE. Every other part opens with "<part> for: <title>",
        #: which is what tells a copy-editor holding a loose legends file which paper it belongs
        #: to. A title page states the title as its first line of content, so the same line puts
        #: the title on the page TWICE, two lines apart — the one file in the envelope where the
        #: reader is reading the title itself rather than looking for it.
        "names_the_paper": True,
        "why": "checklist A7: the identity file uploaded beside a blinded manuscript",
    },
    "figure-legends": {
        "papers": PAPERS,
        "blocks": _legend_blocks,
        "suffix": "-figure-legends.docx",
        "h1": "Figure legends",
        "min_probe_words": 6,
        "why": "checklist A9: figure legends in a separate double-spaced file",
    },
}


#: {manuscript path: {part name: that part's file, both relative to this directory}}.
#: ⚠ EXPORTED SO `submission_packet.py` CAN NAME THESE FILES WITHOUT RECONSTRUCTING A SUFFIX.
#: The upload manifest has to say which file goes in which slot; the moment it derives the name
#: itself, renaming a part here silently drops a row from the checklist a depositor reads at the
#: portal, which is the failure mode that module's `--check` exists for.
PAPERS_BY_MANUSCRIPT = {
    bsp.PAPERS[p]["manuscript"]: {
        name: bsp.PAPERS[p]["manuscript"].replace(".md", part["suffix"])
        for name, part in sorted(PARTS.items()) if p in part["papers"]
    }
    for p in PAPERS
}


def _html(paper, part, blocks):
    title = _title(paper)
    #: ⚠ EACH BLOCK IS ITS OWN PARAGRAPH AND NOTHING ELSE IS ADDED. No numbering of our own, no
    #: restated figure titles, no "see Figure N" cross-references: the text as the manuscript
    #: has it, so a copy-editor diffing the two files finds them identical.
    body = "\n\n".join(text for _label, text in blocks)
    html_body = bsp.markdown_to_html(f"# {part['h1']}\n\n{body}")
    #: ⛔ `h2 { break-before: page }` in NAT_SUBMISSION_CSS would put a two-paragraph file on
    #: three pages. The rest of that block — 12 pt on 2.0, 25 mm margins — is exactly what A7 and
    #: A9 ask for, so the page break is switched off here rather than the spacing being restated.
    css = bsp.MANUSCRIPT_CSS + bsp.NAT_SUBMISSION_CSS + """
h2 { break-before: auto; }
h1 { font-size: 14pt; }
"""
    provenance = ("" if part.get("names_the_paper")
                  else f'<p class="version">{part["h1"]} for: {title}</p>')
    return bsp.page_shell(f"{title} — {part['h1'].lower()}", css, provenance + html_body)


def _normalise(s):
    """One spelling of quotes and whitespace, so a probe and the converted text can be compared.

    LibreOffice re-encodes typographic quotes and collapses whitespace differently from the source
    markdown; without this the comparison fails on punctuation and reports a block as missing.
    `&apos;` is what the converter writes for a straight apostrophe inside its XML.
    """
    s = s.replace("&apos;", "'").replace("&quot;", '"').replace("&amp;", "&")
    s = re.sub(r"[‘’ʼ]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[‐-―]", "-", s)
    return re.sub(r"\s+", " ", s).strip()


def flatten(text):
    """Markdown as a reader of the converted document sees it: no emphasis, no link targets.

    ⛔ A MARKDOWN LINK IS TWO STRINGS IN THE SOURCE AND ONE IN THE DOCUMENT, and taking the source
    form as the probe failed a correct file. The affiliation block carries
    `[0000-0002-…](https://orcid.org/0000-0002-…)`; the converter renders the label and puts the
    target in the .rels part, so the first dozen words of the SOURCE include a URL the document
    legitimately does not show. Exported rather than kept private because the guard that compares
    the shipped .docx against the manuscript has to flatten BOTH SIDES the same way — normalising
    one and not the other reports a correctly cut block as typed by hand.
    """
    return _normalise(re.sub(r"[*_`]", "", re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)))


def _probe(label, text, floor):
    """The words `_verify` looks for: this block's CONTENT, with its label taken off the front.

    ⛔⛔ THE PROBE HAS TO BE THE BLOCK'S WORDS, NOT ITS LABEL — MUTATION-TESTED, AND THE FIRST
    VERSION FAILED. It was `legend.split(".")[0] + "."`, which on "**Figure 1. One 16-mer spans…"
    splits at the FIRST full stop and yields the probe "Figure 1." — so the check asserted only
    that the string "Figure 1." appeared somewhere. Rewriting the entire legend body to "Something
    else entirely" passed it. A guard that fires only when the figure NUMBER vanishes is not a
    content check.
    ★ So the label is stripped off and the probe is the first dozen words of the block proper:
    long enough that no other paragraph carries it, short enough to survive the converter's
    whitespace and entity handling.
    """
    plain = flatten(text)
    after = plain.split(_normalise(label), 1)[-1].strip() if label else plain
    probe = " ".join(after.split()[:12])
    assert len(probe.split()) >= floor, (
        f"the block for {label or 'an unlabelled element'} is too short to probe ({probe!r}); "
        f"a block of under {floor} words past its label is itself the finding")
    return probe


def _verify(docx, part, blocks):
    """Read the converted file back: is every block there, and is it really double-spaced?"""
    with zipfile.ZipFile(docx) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    text = _normalise(re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml)))

    missing = []
    for label, block in blocks:
        if _probe(label, block, part["min_probe_words"]) not in text:
            missing.append(label or block.split("\n", 1)[0][:40])
    if missing:
        raise SystemExit(
            f"⛔ {os.path.basename(docx)} converted but is missing: "
            f"{', '.join(missing)}. LibreOffice drops content silently — this repository has "
            f"measured it dropping every inline SVG from a document that otherwise looked "
            f"perfect — so an absent block is a conversion failure, not a formatting one.")

    #: ⛔⛔ THE SPACING IS READ, NOT ASSUMED. `line-height: 2.0` in the CSS is a request; what the
    #: journal receives is whatever the converter wrote. Paragraphs with no explicit `w:spacing`
    #: inherit the document default, so both are collected and the DEFAULT is what must be double
    #: when the paragraphs are silent.
    spacings = [int(v) for v in re.findall(r'<w:spacing[^/>]*w:line="(\d+)"', xml)]
    with zipfile.ZipFile(docx) as zf:
        styles = zf.read("word/styles.xml").decode("utf-8") if \
            "word/styles.xml" in zf.namelist() else ""
    default = re.search(r'<w:docDefaults>.*?<w:spacing[^/>]*w:line="(\d+)"', styles, re.S)
    default_line = int(default.group(1)) if default else None
    #: ⚠ AND THE FIRST VERSION OF THIS CHECK WAS THE BUG, WHICH IS WHY THE TWO SOURCES ARE
    #: COMBINED RATHER THAN ONE PREFERRED. It looked only at per-paragraph `w:spacing` and failed a
    #: file that was correctly double-spaced: LibreOffice put `w:line="480"` in `<w:docDefaults>`
    #: and left the paragraphs silent, which is the normal Word idiom for "the whole document is
    #: double-spaced". A guard that reads one of two places reports a correct file as broken, and
    #: the next session would have "fixed" the document.
    effective = spacings if spacings else ([default_line] if default_line else [])
    if not effective:
        raise SystemExit(
            f"⛔ {os.path.basename(docx)} declares no line spacing anywhere — neither on its "
            f"paragraphs nor in its document defaults — so nothing in the file says it is "
            f"double-spaced. {part['why']} asks for a double-spaced file.")
    if min(effective) < _DOUBLE_LINE_TWIPS:
        raise SystemExit(
            f"⛔ {os.path.basename(docx)} is not double-spaced: the smallest line value in force "
            f"is {min(effective)} (paragraph values {sorted(set(spacings)) or 'none'}, document "
            f"default {default_line}), and double is {_DOUBLE_LINE_TWIPS} twips (2 x 240). The "
            f"CSS asked for 2.0 and the converter did not honour it.")
    return {"blocks": len(blocks), "words": len(text.split()),
            "line_spacing_twips": sorted(set(effective)),
            "line_spacing_source": "paragraphs" if spacings else "document default",
            "double_spacing_twips": _DOUBLE_LINE_TWIPS}


def out_path(paper, part_name):
    """Where this paper's copy of this part lives. The packet reads this, never a second list."""
    return os.path.join(HERE, bsp.PAPERS[paper]["manuscript"].replace(
        ".md", PARTS[part_name]["suffix"]))


def build(name, part_name, check_only):
    paper = bsp.PAPERS[name]
    part = PARTS[part_name]
    blocks = part["blocks"](paper)
    out = out_path(name, part_name)

    if check_only:
        if not os.path.exists(out):
            raise SystemExit(f"⛔ {os.path.relpath(out, REPO)} does not exist; build it first")
        counts = _verify(out, part, blocks)
        print(f"{name} [{part_name}]: {os.path.relpath(out, REPO)} — {counts['blocks']} block(s), "
              f"{counts['words']} words, line spacing {counts['line_spacing_twips']} twips")
        return counts

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise SystemExit(
            "⛔ no `soffice` on PATH. These double-spaced files are required submission "
            "artefacts, so this is a real gap and not an optional export: install "
            "`libreoffice-writer` — `libreoffice-core` alone reports every input as unloadable — "
            "or run this on a runner that has it.")

    html = _html(paper, part, blocks)
    with tempfile.TemporaryDirectory() as work:
        src = os.path.join(work, os.path.basename(out).replace(".docx", ".html"))
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(html)
        env = dict(os.environ, HOME=work)
        proc = subprocess.run(
            [soffice, "--headless", "--norestore",
             f"-env:UserInstallation=file://{os.path.join(work, 'profile')}",
             "--infilter=" + HTML_FILTER, "--convert-to", DOCX_FILTER,
             "--outdir", work, src],
            capture_output=True, text=True, timeout=900, env=env)
        made = src.replace(".html", ".docx")
        if not os.path.exists(made):
            raise SystemExit(f"⛔ LibreOffice did not write a .docx.\n"
                             f"stdout: {proc.stdout.strip()}\nstderr: {proc.stderr.strip()}")
        counts = _verify(made, part, blocks)
        shutil.move(made, out)

    #: The same shape of build stamp every other deliverable here carries: hashes, not mtimes.
    stamp = {
        "_what": "sha256 of the manuscript this file was cut from, written by "
                 "build_submission_parts.py, plus what the converted archive was measured to "
                 "contain. Current when the hash matches the file on disk; mtimes are not "
                 "evidence, because the regeneration chain rewrites unchanged files.",
        "artifact": os.path.basename(out),
        "part": part_name,
        "built_from": {paper["manuscript"]: hashlib.sha256(
            open(os.path.join(HERE, paper["manuscript"]), "rb").read()).hexdigest()},
        "measured": counts,
    }
    with open(out + ".build-stamp.json", "w", encoding="utf-8") as fh:
        json.dump(stamp, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print(f"{name} [{part_name}]: wrote {os.path.relpath(out, REPO)} — {counts['blocks']} "
          f"block(s), {counts['words']} words, line spacing {counts['line_spacing_twips']} twips "
          f"(double = {_DOUBLE_LINE_TWIPS}), {os.path.getsize(out):,} B")
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--paper", action="append", choices=PAPERS,
                    help="build just this paper's files (repeatable)")
    ap.add_argument("--part", action="append", choices=sorted(PARTS),
                    help="build just this part (repeatable)")
    ap.add_argument("--check", action="store_true",
                    help="verify what is on disk and write nothing")
    args = ap.parse_args(argv)
    for name in (args.paper or PAPERS):
        for part_name in (args.part or sorted(PARTS)):
            if name not in PARTS[part_name]["papers"]:
                #: ⚠ SAID OUT LOUD RATHER THAN SKIPPED IN SILENCE. A regeneration chain whose
                #: output does not mention a paper reads as a paper that was built; this is the
                #: line that distinguishes "not applicable" from "forgotten".
                print(f"{name} [{part_name}]: not applicable — this part is built for "
                      f"{', '.join(PARTS[part_name]['papers'])}")
                continue
            build(name, part_name, args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
