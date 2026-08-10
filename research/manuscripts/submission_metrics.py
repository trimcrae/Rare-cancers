#!/usr/bin/env python3
"""Measure each submission-form manuscript against the limits its chosen venue is believed to set.

WHY THIS EXISTS. The per-journal author-guideline pages for two of the three venues cannot be
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
    "BJC-Article": {
        "journal": "British Journal of Cancer (Springer Nature)",
        "limits": {"main_words": 5000, "abstract_words": 200, "display_items": 8,
                   "references": 80},
        "provenance": "nature.com pages DO answer; these were read from the journal's own guide to "
                      "authors at HTTP 200",
    },
}

MANUSCRIPTS = {
    "emc-mtap-prmt5-hypothesis.md": "GCC-Research-Article",
    "emc-atr-collaborator-package.md": "GCC-Research-Article",
    "repurposing-hypotheses.md": "CROH-Review",
    "emc-surface-target-landscape.md": "BJC-Article",
}

#: Headings that end the main text. Matched case-insensitively at any heading level.
TAIL = re.compile(r"^#+\s*(declarations?|data (and|&) code|data availability|references|"
                  r"acknowledge?ments?|competing interests|funding|author contributions|"
                  r"display items|appendix)\b", re.I | re.M)
HEAD = re.compile(r"^#+\s*(background|introduction|1[.\s])", re.I | re.M)


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


def measure(path):
    raw = open(path, encoding="utf-8").read()
    _assert_comments_closed(path, raw)
    body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)      # frontmatter
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)           # editorial comments
    body = re.sub(r"```.*?```", "", body, flags=re.S)            # fenced blocks

    ab = re.search(r"^#+\s*Abstract\s*$(.*?)(?=^#+\s)", body, re.S | re.M)
    abstract_words = len(ab.group(1).split()) if ab else None

    start = HEAD.search(body)
    tail = TAIL.search(body, start.start() if start else 0)
    main = body[start.start():tail.start()] if start and tail else body
    main_words = len(strip_tables(main).split())

    figures = len(re.findall(r"!\[", body))
    tables = len(re.findall(r"^\*\*Table\s", body, re.M))
    refs = len(re.findall(r"^\s{0,3}\d{1,3}\.\s+\S", body, re.M))
    return {"main_words": main_words, "abstract_words": abstract_words,
            "figures": figures, "tables": tables, "display_items": figures + tables,
            "references": refs}


def main():
    rows, over = [], 0
    for fname, vkey in MANUSCRIPTS.items():
        v = VENUES[vkey]
        m = measure(os.path.join(REPO, "research", "manuscripts", fname))
        flags = []
        for key, lim in v["limits"].items():
            got = m.get(key)
            if lim is not None and got is not None and got > lim:
                flags.append(f"{key} {got} > {lim}")
                over += 1
        rows.append({"file": fname, "venue": v["journal"], "measured": m,
                     "limits": v["limits"], "limits_provenance": v["provenance"],
                     "over_limit": flags})
        state = "OVER: " + "; ".join(flags) if flags else "within believed limits"
        print(f"{fname:40s} {vkey:22s} main={m['main_words']:5d}w  abs={m['abstract_words']}w  "
              f"items={m['display_items']:2d}  refs={m['references']:2d}  {state}")

    out = os.path.join(REPO, "research", "manuscripts", "submission-metrics.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({
            "_what": "What each submission-form manuscript actually is, measured, against the limits "
                     "its venue is believed to set.",
            "_why": "Two of three venues block automated retrieval of their author guidelines with "
                    "deliberate security controls that persist under a real browser. The limits stay "
                    "unverified; this pins down OUR side so checking theirs is a sixty-second job.",
            "⛔_the_limits_below_are_not_verified": "Only the BJC row was read from the journal's own "
                    "page. The other two are search-derived. Do not cite them as retrieved facts.",
            "⚠_none_of_this_gates_the_preprint": "bioRxiv sets no word, abstract or display-item "
                    "limit, and its deposit being free is verified verbatim at primary source.",
            "counting_rule": "Main text runs from the first substantive heading to the last heading "
                    "before Declarations, excluding frontmatter, HTML comments, fenced blocks, the "
                    "abstract, table bodies, references and every Appendix.",
            "rows": rows,
        }, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"\nwrote {os.path.relpath(out, REPO)} — {over} limit(s) exceeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
