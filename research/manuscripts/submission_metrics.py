#!/usr/bin/env python3
"""Measure each submission-form manuscript against the limits its chosen venue is believed to set.

WHY THIS EXISTS. The per-journal author-guideline pages for most of these venues cannot be
retrieved by any automated means: onlinelibrary.wiley.com serves a JavaScript bot challenge and
www.sciencedirect.com blocks the datacenter IP outright, and both persist under a real headless
browser run from CI. Those are deliberate security controls and are not something to defeat. So the
word, abstract and display-item limits recorded here remain SEARCH-DERIVED, and are marked as such.

⛔ THIS TOOL DOES NOT VERIFY THE LIMITS. It verifies OUR SIDE of the comparison — what each
manuscript actually is — so that checking the limits becomes a sixty-second job for a human with a
browser on the journal's own page, rather than a rewrite discovered after a desk rejection. A
format mismatch is returned by an editor; it is not a cost and not a scientific defect. It does not
touch the preprint at all: bioRxiv sets no word, abstract or display-item limit, and that its
deposit is free IS verified at primary source.

⚠ THE COUNTING RULE IS EXPLICIT, BECAUSE TWO EARLIER COUNTS OF THE SAME FILE DISAGREED BY 2,166
WORDS (4,553 against 6,719) purely through counting different things. Here, MAIN TEXT means the
sections a journal counts: from the first substantive section heading through the last one before
Declarations. It EXCLUDES frontmatter, HTML editorial comments, the abstract, keywords, the
display-item captions block, declarations, references and every Appendix — and it excludes table
BODIES, since journals count tables as display items rather than as words.

⛔⛔ A DISPLAY ITEM OR A REFERENCE THAT LIVES IN A COMPANION FILE IS STILL THIS PAPER'S, AND
COUNTING ONLY THE MANUSCRIPT FILE REPORTS ZERO FOR IT (2026-08-12). The fusion-junction ASO
manuscript keeps its tables in `…-submission-tables.md` and its references in
`…-submission-references.md`, both GENERATED so that a cell and its source cannot diverge — which is
good practice and made every display-item and reference counter here read 0. A row of measured
zeroes on a paper that has several display items and thirty references is the "a populated field is
not a measured one" defect in its other direction: a field that is present, plausible and false. So
the counters read the manuscript AND its declared `COMPANIONS`, and figures and tables are counted as
DISTINCT NUMBERS rather than as caption lines, so an embed and its own caption cannot count twice.

⛔ THIS DOCSTRING WAS ITSELF A SECOND COPY OF THE NUMBERS, AND IT WENT STALE (2026-08-13). It said
"29 references" and "two tables" while the module's own output said 30 and three, and elsewhere it
carried "4,249 words … 265" against an emitted 5,621 and 268. A generator whose prose disagrees with
its own artifact is the worst place for a duplicate number, because a reader has no reason to distrust
it. Counts are named in words here and quoted nowhere: `submission-metrics.json` is the one home, and
the checklist and submission plan point at it rather than restating it.

⚠ THE SAME PASS CORRECTED THREE EXISTING COUNTS, none of which changed a verdict — see
`SUPERSEDED_MEASUREMENTS` below, which is the appendix rule 1.2 requires and not a changelog.

    python3 research/manuscripts/submission_metrics.py
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: ⚠ `limits` are SEARCH-DERIVED and unverified — see the module docstring. `None` means the venue
#: sets no limit of that kind, or none was found. Provenance is carried per venue so a reader never
#: mistakes one of these for a retrieved fact.
VENUES = {
    "bioRxiv-preprint": {
        "journal": "bioRxiv (preprint; the journal submission goes to Nucleic Acid Therapeutics)",
        "limits": {"main_words": None, "abstract_words": None, "display_items": None,
                   "references": None},
        #: ⛔ THE FLAG THAT SEPARATES "NO LIMIT" FROM "UNREAD". Without it the grader reads four
        #: nulls as ignorance and reports the one venue whose rules are fully known as ungraded.
        "no_limits_by_policy": True,
        "provenance": ("VERIFIED at primary source: bioRxiv sets no word, abstract or display-item "
                       "limit and its deposit is free — the one venue fact in this table that was "
                       "read rather than searched. ⚠ ALL-`None` IS A STATEMENT, NOT A GAP: it means "
                       "this manuscript is measured and ungated, which is the honest state while the "
                       "journal is undecided. A journal's limits apply when one is chosen, and "
                       "cutting the abstract to any particular cap before then means cutting twice, "
                       "because the venues under consideration disagree on both length AND whether a "
                       "structured abstract is wanted at all."),
    },
    "GCC-Research-Article": {
        "journal": "Genes, Chromosomes and Cancer (Wiley)",
        "limits": {"main_words": None, "abstract_words": 250, "display_items": None,
                   "references": None},
        "provenance": "search-derived; onlinelibrary.wiley.com serves a bot challenge to CI and to "
                      "a real headless browser alike",
    },
    "CROH-Review": {
        "journal": "Critical Reviews in Oncology/Hematology (Elsevier)",
        "limits": {"main_words": 8000, "abstract_words": 250, "display_items": 6,
                   "references": None},
        "provenance": "search-derived; sciencedirect.com blocks the datacenter IP",
    },
    #: ⭐ REOPENED 2026-08-20 (trimcrae), AND THE LIMITS ARE UNREAD RATHER THAN ABSENT. Nucleic Acid
    #: Therapeutics was this paper's preferred venue and was eliminated on its mandatory
    #: Publishing Services Fee of $90 per typeset page, roughly $700-1,100 for a full-length
    #: manuscript. Condensing the paper to a five-page journal article changes that arithmetic, and
    #: trimcrae has relaxed the standing $0 rule for THIS paper on that basis. ⛔ THE FOUR `None`s
    #: BELOW MEAN NOBODY HAS READ THE GUIDELINES, NOT THAT SAGE SETS NO LIMIT — the distinction the
    #: `no_limits_by_policy` flag exists to make, and this row does NOT carry it. The article types
    #: SAGE offers for this journal, its word, abstract, display-item and reference caps, and the
    #: CURRENT per-page fee are all unread; the $90 figure predates the Liebert-to-SAGE transition.
    #: ⛔ Do not borrow the BJC row's caps for this row merely because both are journal Articles.
    "NAT-Article": {
        "journal": "Nucleic Acid Therapeutics (SAGE)",
        "limits": {"main_words": None, "abstract_words": None, "display_items": None,
                   "references": None},
        "provenance": (
            "UNREAD, AND NOW ESTABLISHED AS UNREACHABLE BY EVERY AUTOMATED ROUTE. The journal "
            "transferred from Mary Ann Liebert to SAGE; the Liebert-era pages return 403, and "
            "journals.sagepub.com returns 403 to the egress proxy, to a plain CI fetch and to a "
            "real headless Chromium alike -- re-confirmed 2026-08-23 by Actions run 32644971152, "
            "whose author-instructions and journal-home fetches both came back HTTP 403 with the "
            "Cloudflare body 'Just a moment...'. in.sagepub.com answers 200 and carries no limits. "
            "SO THIS IS AN AUTHOR ACTION, NOT A DEFERRED FETCH: the page loads normally in a human "
            "browser and no further tooling will change that. Three things to read there before "
            "submitting. (1) The editorial rule that manuscripts CLAIMING ANTISENSE EFFICACY must "
            "carry at least two control oligodeoxynucleotides or be returned without review -- "
            "surfaced from search snippets and NOT from the page, so a lead to confirm rather than "
            "a fact; this paper claims no efficacy, runs no assay, and specifies three controls for "
            "the experiment it proposes, so it is very likely out of scope. (2) Word, abstract and "
            "display-item limits for the article type. (3) Whether the $90/page Publishing Services "
            "Fee survived the SAGE transfer -- at six pages that is about $540."
        ),
    },
    "BJC-Article": {
        "journal": "British Journal of Cancer (Springer Nature)",
        "limits": {"main_words": 5000, "abstract_words": 200, "display_items": 8,
                   "references": 80},
        "provenance": "nature.com pages DO answer; these were read from the journal's own guide to "
                      "authors at HTTP 200",
    },
    # ⛔⛔ READ AT LAST, AND IT DISQUALIFIES THE VENUE (2026-08-12). The guide was never missing —
    # the URLs being guessed were. `/cgt/for-authors` and `/cgt/submission-guidelines` 404, and
    # `/cgt/authors-and-referees/gta` returns 200: the same shape that already worked for the
    # British Journal of Cancer row above, confirmed by harvesting the journal home's own links,
    # which carry "Guide For Authors" pointing exactly there.
    #
    # ⛔ THE $0 CONSTRAINT FAILS HERE, verbatim from that page: "After final layout for
    # publication, each page of an article will incur a fixed charge of £145 / $238 per page …
    # Page charges will NOT apply to authors who choose to pay an article processing charge to
    # make their paper open access." So the subscription route carries a MANDATORY per-page charge
    # and the only escape is the APC. That is the Nucleic Acid Therapeutics trap again at 2.6× the
    # price — NAT was rejected at $90/page — and it is why "hybrid, no APC on the subscription
    # route" was never a sufficient test. This row is retained rather than deleted because the
    # measured numbers below are still the honest measurement of the manuscript, and because the
    # next venue must be tested against the FULL fee schedule, not the APC question alone.
    #
    # ⚠ AND THERE IS NO "SHORT COMMUNICATION" AT THIS JOURNAL. The types are Article, Review,
    # Brief Communication (2 pages, one display item, 10 references), Perspective and
    # Correspondence. ⛔ AND THE MANUSCRIPT NO LONGER FITS ARTICLE EITHER: graded against the limits
    # in this row it is OVER on main words and OVER on display items, and inside only on references,
    # with an abstract far over the 200-word cap. The measured values are in this module's own output
    # and are deliberately not repeated here; the comparison is NOT one this module makes, because
    # `MANUSCRIPTS` grades the ASO paper against `bioRxiv-preprint`, which sets no limits, so its
    # `over_limit` is empty by construction and is silent about CGT.
    # ⚠ Superseded, retained: "The manuscript's shape fits Article on words, display items and
    # references", and "this manuscript's is structured and longer. Both would have to change". The
    # first was retired 2026-08-15 by the regenerated measurement — the paper roughly quadrupled
    # after that comment was written and crossed two of the three caps. The second was retired on
    # 2026-08-14, when the abstract was made UNSTRUCTURED (submission-plan Sec 1c): the format is
    # already right for this journal, and only the length would still have to change.
    "CGT-Article": {
        "journal": "Cancer Gene Therapy (Springer Nature)",
        "limits": {"main_words": 12000, "abstract_words": 200, "display_items": 7,
                   "references": 60},
        "provenance": "READ at primary source: nature.com/cgt/authors-and-referees/gta, HTTP 200, "
                      "2026-08-12, via a real headless browser (see "
                      "research/literature/venue-policy-browser-fetch.json → cgt_gta). "
                      "⛔ FEE-DISQUALIFIED: the same page states a MANDATORY charge of "
                      "£145 / $238 per page on the subscription route, waived only for authors who "
                      "pay the open-access APC. The $0 constraint is binding, so this venue cannot "
                      "be used. ⚠ The abstract limit is for an UNSTRUCTURED abstract, which is the "
                      "form the ASO abstract now has, so length is the only remaining gap on the "
                      "abstract. ⚠ Superseded, retained: 'this manuscript's is structured, so the "
                      "format as well as the length is wrong for this journal' — retired 2026-08-14 "
                      "when the abstract was made unstructured (submission-plan Sec 1c).",
    },
}

MANUSCRIPTS = {
    "mtap-prmt5/emc-mtap-prmt5-hypothesis.md": "GCC-Research-Article",
    "dependency/emc-atr-collaborator-package.md": "GCC-Research-Article",
    "repurposing/repurposing-hypotheses.md": "CROH-Review",
    "surface-targets/emc-surface-target-landscape.md": "BJC-Article",
    # ⛔ GRADED AGAINST A VENUE ITS OWN PLANNING DOCUMENT HAD DISQUALIFIED (fixed 2026-08-13). This
    # row said `CGT-Article` for a day after `fusion-junction-aso-submission-plan.md` §1c eliminated
    # Cancer Gene Therapy on its read fee schedule, so every run printed an OVER verdict against an
    # abstract limit no venue in play imposes — a red flag pointing at a decision already made, which
    # is how a real one gets ignored. The venue is open; bioRxiv is the immediate destination and
    # sets no limits, so that is what the paper is measured against until a journal is chosen.
    "aso/fusion-junction-aso-research-article.md": "bioRxiv-preprint",
    #: ⭐ THE CONDENSED JOURNAL SUBMISSION, ADDED 2026-08-20. Same work, second document:
    #: the preprint above is the extended report and stays measured against bioRxiv, while
    #: this row is measured against the journal actually being submitted to. Both rows are
    #: real and neither supersedes the other.
    "aso/fusion-junction-aso-journal-article.md": "NAT-Article",
}

#: Files that carry display items or reference entries belonging to a manuscript but living outside
#: it. Kept separate from MANUSCRIPTS so a paper with no companions needs no entry at all.
#: ⚠ MAIN TEXT AND THE ABSTRACT ARE NEVER READ FROM A COMPANION — only display items and
#: references are, because those are the two things a journal counts wherever they physically sit.
COMPANIONS = {
    "aso/fusion-junction-aso-journal-article.md": [
        "aso/fusion-junction-aso-journal-tables.md",
        "aso/fusion-junction-aso-journal-references.md",
    ],
    "aso/fusion-junction-aso-research-article.md": [
        "aso/fusion-junction-aso-submission-tables.md",
        "aso/fusion-junction-aso-submission-references.md",
    ],
}

#: ⛔ THE FIGURE FILES A PORTAL ACTUALLY WANTS UPLOADED, for manuscripts whose figures are NOT
#: markdown embeds (2026-08-12). `submission_packet.figures_for()` discovers figures by matching
#: `![...](path)`, which is right for a paper that embeds its images and reports ZERO for a paper
#: that carries a Figure legends section instead — and this file's own counter had already been
#: corrected for exactly that, so the packet was printing "none; this paper's display items are all
#: tables" for a paper with three figures whose PDFs sit committed beside the manuscript. The
#: consequence is not cosmetic: that line is the upload checklist, so it told the author to submit
#: nothing.
#: ⛔ DERIVED FROM THE PDF BUILDER'S FIGURE MAP, NOT RETYPED (2026-08-17). This list was hand-kept
#: and drifted: it named the junction-space, multi-partner-seam and chance-baseline panels and
#: omitted `aso-gap-length-tradeoff.svg` — the paper's FIGURE 3, the panel behind the gap-length
#: identity in §2.9. The upload checklist therefore told the author to submit three of four figure
#: files, and the missing one was a main-text figure, not a supplementary panel. The header note
#: this replaces asserted "there is no committed link between 'Figure 1' in the prose and
#: `aso-junction-space.svg`" — which stopped being true when `build_submission_pdf.PAPERS` began
#: pairing each legend opener to its SVG so the renderer could not mis-set a legend. That map is
#: the committed link, and it is the one a build failure already polices, so this reads it rather
#: than keeping a second copy that only a reader would notice going stale.
#: ⚠ SUPPLEMENTARY PANELS COUNT. `Supplementary Figure S1` is a file the portal still wants
#: uploaded, so no legend prefix is filtered out here. Paths stay relative to this directory, and
#: `submission_packet` reports each one MISSING if it is absent, so a wrong entry in the source map
#: fails loudly rather than silently shrinking the checklist.
def _figure_files_from_the_pdf_builder():
    #: This module is normally run as a script, which puts its own directory on the path. It is not
    #: always, so the sibling import is made to work from any working directory rather than
    #: degrading to an empty checklist the one time somebody imports it.
    _here = os.path.dirname(os.path.abspath(__file__))
    if _here not in sys.path:
        sys.path.insert(0, _here)
    from build_submission_pdf import PAPERS
    out = {}
    for spec in PAPERS.values():
        manuscript = spec.get("manuscript")
        figures = spec.get("figures") or {}
        if manuscript and figures:
            out[manuscript] = ["figures/" + svg for svg in figures.values()]
    return out


FIGURE_FILES = _figure_files_from_the_pdf_builder()

#: ⚠ THE APPENDIX RULE 1.2 REQUIRES: values this file used to emit, why they were wrong, and what
#: replaced them. None of these changed a verdict — every affected row was and remains within every
#: believed limit — but a superseded number stays quotable unless it is registered as superseded.
SUPERSEDED_MEASUREMENTS = [
    {"row": "surface-targets/emc-surface-target-landscape.md", "field": "figures",
     "was": 0, "now": 1,
     "why": "The figure counter matched only `![` image embeds. This manuscript's Figure 1 is a "
            "caption in its Display items block with no embedded image file, so a real figure "
            "counted as zero. Figures are now counted as distinct figure NUMBERS drawn from embeds "
            "and captions together."},
    {"row": "surface-targets/emc-surface-target-landscape.md", "field": "display_items",
     "was": 5, "now": 6,
     "why": "Follows the figure correction above; the five tables are unchanged. Still inside the "
            "believed limit of 8."},
    {"row": "surface-targets/emc-surface-target-landscape.md", "field": "references",
     "was": 21, "now": 18,
     "why": "The reference counter matched every numbered line anywhere in the file, so three "
            "numbered lines inside Appendix A were counted as references. It now reads the "
            "References section only."},
    {"row": "dependency/emc-atr-collaborator-package.md", "field": "references",
     "was": 16, "now": 8,
     "why": "Same defect, larger: the eight-item numbered list in the Limitations section was "
            "counted as eight extra references, exactly doubling a reference list of 8."},
    {"row": "mtap-prmt5/emc-mtap-prmt5-hypothesis.md", "field": "main_words",
     "was": 5222, "now": 5213,
     "why": "Nine `---` section dividers were counted as nine words; a horizontal rule is not a "
            "word. Rules are now blanked before counting."},
    {"row": "mtap-prmt5/emc-mtap-prmt5-hypothesis.md", "field": "abstract_words",
     "was": 250, "now": 249,
     "why": "Same divider defect. Worth registering rather than waving through: 250 against a "
            "believed cap of 250 reads as sitting exactly on the line, and it never was."},
    {"row": "dependency/emc-atr-collaborator-package.md", "field": "main_words",
     "was": 3161, "now": 3153, "why": "Eight `---` dividers counted as words."},
    {"row": "dependency/emc-atr-collaborator-package.md", "field": "abstract_words",
     "was": 239, "now": 238, "why": "One `---` divider counted as a word."},
    {"row": "repurposing/repurposing-hypotheses.md", "field": "main_words",
     "was": 5037, "now": 5030, "why": "Seven `---` dividers counted as words."},
]

#: Headings that end the main text. Matched case-insensitively at any heading level.
#: ⚠ THE DISPLAY-ITEM BLOCK IS NOT ALWAYS CALLED "Display items". The ASO manuscript splits it into
#: `## Tables` and `## Figure legends`, and until both were listed here its three figure legends
#: were counted as main-text prose — a silent ~430-word overstatement against a word limit, which is
#: the one number this file exists to get right. These two alternatives are anchored to end-of-line
#: rather than closed with `\b`, so a section genuinely about tables ("Tables and their sources")
#: cannot truncate the main text by accident.
TAIL = re.compile(r"^#+\s*(?:(?:declarations?|data (?:and|&) code|data availability|references|"
                  r"acknowledge?ments?|competing interests|funding|author contributions|"
                  r"display items|appendix)\b"
                  r"|(?:figure legends?|tables?)\s*$)", re.I | re.M)
HEAD = re.compile(r"^#+\s*(background|introduction|1[.\s])", re.I | re.M)

#: The References section, so a numbered list elsewhere in the file cannot inflate the count.
REF_HEAD = re.compile(r"^#+\s*(?:\d+\.\s*)?references\b", re.I | re.M)
REF_END = re.compile(r"^#+\s*appendix\b", re.I | re.M)
NUMBERED = re.compile(r"^\s{0,3}\d{1,3}\.\s+\S", re.M)

FIG_EMBED = re.compile(r"!\[([^\]]*)\]")
FIG_ALT_NUM = re.compile(r"\s*Figure\s*(\d+)", re.I)
FIG_CAPTION = re.compile(r"^\*\*Figure\s*(\d+)", re.M)
TAB_CAPTION = re.compile(r"^\*\*Table\s*(\d+)", re.M)


def strip_tables(text):
    """Drop table rows and their separator lines; journals count tables as display items."""
    return "\n".join(l for l in text.split("\n")
                     if not re.match(r"^\s*\|", l) and not re.match(r"^\s*\|?[-: |]+\|", l))


def _assert_comments_closed(path, raw):
    """An unterminated `<!--` hides everything after it from every markdown renderer.

    ⛔ THIS HAPPENED, AND THE COMMENT-STRIP HERE IS WHY IT WENT UNNOTICED (2026-08-10). A scripted
    edit to `emc-surface-target-landscape.md` replaced a block ending at the first blank line, and
    the blank line it found sat AFTER the `-->`, so the terminator was consumed. The manuscript then
    rendered as an HTML comment from the byline down. The regex below strips `<!--.*?-->` and needs
    the closing token to match, so with the terminator gone it stripped nothing, quietly counted the
    editorial block as prose, and reported a plausible number. A silent no-op on malformed input is
    worse than a crash.

    ⚠ COUNTING TOKENS IS THE WRONG TEST, and the first version of this guard failed on its own
    subject: the repaired file MENTIONS "<!--" in prose inside the comment, explaining the very
    defect, so opens and closes do not balance while the structure is perfectly sound. The property
    that matters is not symmetry but whether the strip actually consumes every opener.
    """
    residue = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    if "<!--" in residue:
        line = raw[:raw.rindex("<!--")].count("\n") + 1 if "<!--" in raw else "?"
        raise SystemExit(
            f"{path}: an editorial comment opening near line {line} is never closed, so every "
            f"markdown renderer hides the rest of the manuscript. Fix the file, not this check.")


def prepare(path):
    """Read one markdown file and strip everything no journal counts.

    ⚠ A HORIZONTAL RULE IS NOT A WORD, and `"---".split()` says it is one. Section dividers were
    being counted as prose — 9, 8 and 7 words of main text in three manuscripts, and one word of
    abstract in three, which put the MTAP abstract at an apparent 250 against a believed cap of 250
    when it is really 249. Blanked rather than deleted, so line structure and every `^#`-anchored
    heading match survive untouched.
    """
    raw = open(path, encoding="utf-8").read()
    _assert_comments_closed(path, raw)
    body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)      # frontmatter
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)           # editorial comments
    body = re.sub(r"```.*?```", "", body, flags=re.S)            # fenced blocks
    return re.sub(r"^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*$", "", body, flags=re.M)


def count_display_items(bodies):
    """Distinct figure and table NUMBERS across a manuscript and its companions.

    ⚠ NUMBERS, NOT CAPTION LINES. A figure that is both embedded (`![Figure 3](…)`) and captioned
    (`**Figure 3.** …`) is ONE display item, and counting lines would report two. An embed whose alt
    text carries no figure number cannot be deduplicated against a caption, so it is counted on its
    own — over-counting an unnumbered figure is the safe direction against a display-item cap.
    """
    figures, tables, unnumbered = set(), set(), 0
    for body in bodies:
        for alt in FIG_EMBED.findall(body):
            m = FIG_ALT_NUM.match(alt)
            if m:
                figures.add(m.group(1))
            else:
                unnumbered += 1
        figures.update(FIG_CAPTION.findall(body))
        tables.update(TAB_CAPTION.findall(body))
    return len(figures) + unnumbered, len(tables)


def count_references(bodies):
    """Numbered entries inside a References section, wherever that section lives.

    ⛔ SCOPED TO THE SECTION, BECAUSE "every numbered line in the file" IS NOT A REFERENCE COUNT.
    That is what this counted until 2026-08-12, and it read a numbered Limitations list as eight
    extra references in one manuscript and three Appendix lines as references in another. An
    Appendix ends the section for the same reason it ends the main text: rule 1.2 puts superseded
    values there, and a superseded reference is not a reference.
    """
    total = 0
    for body in bodies:
        h = REF_HEAD.search(body)
        if not h:
            continue
        end = REF_END.search(body, h.end())
        total += len(NUMBERED.findall(body[h.end():end.start() if end else len(body)]))
    return total


def measure(path, companion_paths=()):
    body = prepare(path)
    companions = [prepare(p) for p in companion_paths]

    ab = re.search(r"^#+\s*Abstract\s*$(.*?)(?=^#+\s)", body, re.S | re.M)
    abstract_words = len(ab.group(1).split()) if ab else None

    start = HEAD.search(body)
    tail = TAIL.search(body, start.start() if start else 0)
    main = body[start.start():tail.start()] if start and tail else body
    main_words = len(strip_tables(main).split())

    figures, tables = count_display_items([body] + companions)
    return {"main_words": main_words, "abstract_words": abstract_words,
            "figures": figures, "tables": tables, "display_items": figures + tables,
            "references": count_references([body] + companions)}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    rows, over, unread = [], 0, 0
    for fname, vkey in MANUSCRIPTS.items():
        v = VENUES[vkey]
        companions = COMPANIONS.get(fname, [])
        m = measure(os.path.join(REPO, "research", "manuscripts", fname),
                    [os.path.join(REPO, "research", "manuscripts", c) for c in companions])
        flags = []
        for key, lim in v["limits"].items():
            got = m.get(key)
            if lim is not None and got is not None and got > lim:
                flags.append(f"{key} {got} > {lim}")
                over += 1
        # ⚠ A ROW WHOSE LIMITS ARE ALL UNREAD MUST NOT PRINT AS "within believed limits". There is
        # nothing to be within, and a green line against no limit is the most confident-looking
        # false reassurance this file could emit.
        # ⛔ `None` WAS DOING TWO JOBS AND THEY MEAN OPPOSITE THINGS (2026-08-13). A `None` limit is
        # "nobody has read this journal's guidelines" for Cancer Gene Therapy and "this venue imposes
        # no such limit" for bioRxiv, and the grader could not tell them apart: it inferred
        # "unread" from the absence of any numeric limit, so the venue whose rules ARE fully known —
        # because there are none — reported as the least known of all. A venue therefore declares
        # `no_limits_by_policy` rather than having it guessed from its nulls.
        graded = [k for k, lim in v["limits"].items() if lim is not None]
        read = bool(graded) or bool(v.get("no_limits_by_policy"))
        rows.append({"file": fname, "venue": v["journal"], "measured": m,
                     "companion_files": companions,
                     "figure_files": FIGURE_FILES.get(fname, []),
                     "limits": v["limits"], "limits_provenance": v["provenance"],
                     "limits_read": read,
                     "no_limits_by_policy": bool(v.get("no_limits_by_policy")),
                     "over_limit": flags})
        if flags:
            state = "OVER: " + "; ".join(flags)
        elif v.get("no_limits_by_policy"):
            state = "no limits to exceed — this venue sets none"
        elif graded:
            state = "within believed limits"
        else:
            state = "⛔ NOT GRADED — this venue's limits have never been read"
            unread += 1
        print(f"{fname:47s} {vkey:24s} main={m['main_words']:5d}w  abs={m['abstract_words']}w  "
              f"items={m['display_items']:2d}  refs={m['references']:2d}  {state}")

    out = os.path.join(REPO, "research", "manuscripts", "submission-metrics.json")
    payload = {
            "_what": "What each submission-form manuscript actually is, measured, against the limits "
                     "its venue is believed to set.",
            "_why": "Most of these venues block automated retrieval of their author guidelines with "
                    "deliberate security controls that persist under a real browser. The limits stay "
                    "unverified; this pins down OUR side so checking theirs is a sixty-second job.",
            "⛔_the_limits_below_are_not_verified": "They fall into three states and the difference "
                    "matters. READ: only the BJC row was retrieved from the journal's own guide to "
                    "authors at HTTP 200. SEARCH-DERIVED: the two GCC rows and the CROH row come "
                    "from search summaries, because Wiley serves a bot challenge and Elsevier "
                    "blocks the datacenter IP; do not cite them as retrieved facts. UNREAD: the "
                    "Cancer Gene Therapy row carries no limits at all — its `null`s mean nobody has "
                    "seen the guidelines, NOT that the journal sets no limit. That row is reported "
                    "ungraded rather than compliant, and its numbers must never be borrowed from "
                    "the BJC row merely because both journals are Springer Nature.",
            "⛔_the_CGT_fee_schedule_is_unread_and_that_is_a_live_submission_risk": "The $0 route "
                    "for Cancer Gene Therapy rests on ONE page: nature.com/cgt/open-access (HTTP "
                    "200) states that open access requires an APC and that authors 'can also choose "
                    "to publish under the traditional publishing model (no APC charges apply)'. "
                    "That answers the APC question and ONLY the APC question. Page charges, colour "
                    "charges, submission fees and over-length charges on the subscription route are "
                    "UNREAD, because they live in the author guidelines and every author-guideline "
                    "path tried returned 404. ⛔ THIS IS NOT A HYPOTHETICAL: Nucleic Acid "
                    "Therapeutics passed the no-APC test and then turned out to levy mandatory "
                    "Publishing Services Fees of $90 per page on every accepted manuscript. It "
                    "REMAINS the venue — the fee is why the article carries a six-page budget "
                    "rather than why it was dropped (trimcrae, 2026-08-22). ⚠ Superseded, retained: "
                    "this read \"was rejected anyway once its guidelines were read\", which "
                    "contradicted the same packet's own venue table. "
                    "The same question has not been put to CGT. Until a "
                    "CGT author-guideline or fee page is read, the venue's compliance with the $0 "
                    "constraint is established for APCs and unestablished overall.",
            "⚠_none_of_this_gates_the_preprint": "bioRxiv sets no word, abstract or display-item "
                    "limit, and its deposit being free is verified verbatim at primary source.",
            "counting_rule": "Main text runs from the first substantive heading to the last heading "
                    "before Declarations, excluding frontmatter, HTML comments, fenced blocks, the "
                    "abstract, table bodies, the display-item block under any of its names "
                    "('Display items', 'Tables', 'Figure legends'), references and every Appendix. "
                    "Figures and tables are counted as DISTINCT NUMBERS across the manuscript and "
                    "its `companion_files`, so an embedded figure and its own caption count once "
                    "and a table generated into a separate file still counts. References are the "
                    "numbered entries inside a References section, wherever that section lives; a "
                    "numbered list anywhere else in the file is not a reference.",
            "⚠_superseded_measurements": SUPERSEDED_MEASUREMENTS,
            "rows": rows,
    }
    doc = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    # ⛔ `--check` EXISTS BECAUSE main() USED TO OPEN THIS FILE FOR WRITE UNCONDITIONALLY.
    # Every other deposit document defers to submission-metrics.json as "the one home" for the word
    # counts, so when it goes stale they are all confidently wrong in one place — which is exactly
    # what round 7 measured (263 main words and 9 abstract words out). There was no way to ASK
    # whether it was current: the only way to find out was to regenerate it and read the diff, which
    # is not something a gate can do without also writing.
    if "--check" in argv:
        if not os.path.exists(out):
            print(f"⛔ {out} does not exist; run without --check to generate it", file=sys.stderr)
            return 1
        have = open(out, encoding="utf-8").read()
        if have == doc:
            print(f"OK {os.path.relpath(out, REPO)} reproduces byte-for-byte")
            return 0
        try:
            hv = {r["file"]: r["measured"] for r in json.loads(have).get("rows", [])}
        except Exception:  # noqa: BLE001 — a corrupt file is a failure, not a crash
            hv = {}
        print(f"⛔ {os.path.relpath(out, REPO)} DOES NOT reproduce — the counts every other "
              "deposit document defers to are stale:", file=sys.stderr)
        for r in rows:
            was, now = hv.get(r["file"]), r["measured"]
            if was != now:
                for k in sorted(set(was or {}) | set(now or {})):
                    a, b = (was or {}).get(k), (now or {}).get(k)
                    if a != b:
                        print(f"   {r['file']}: {k} {a} -> {b}", file=sys.stderr)
        return 1

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"\nwrote {os.path.relpath(out, REPO)} — {over} limit(s) exceeded, "
          f"{unread} paper(s) ungraded because the venue's limits are unread")
    return 0


if __name__ == "__main__":
    sys.exit(main())
