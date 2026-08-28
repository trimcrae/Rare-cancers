#!/usr/bin/env python3
"""Check the sentences a commit CHANGED, not the whole manuscript.

⛔ WHY THIS EXISTS, AND IT IS MEASURED. Across review rounds 15 and 16 of the fusion-junction ASO
paper, the defects stopped coming from the original text and started coming from the REPAIRS:

    round 15   2 of 7 findings were introduced by round 14's fixes
    round 16   4 of 4 findings were introduced by rounds 13-15's fixes
    then       a pre-build review of those 4 fixes found 5 further problems IN THEM, one a
               claim the manuscript refutes 300 lines away

An agent scoped to the diff found all four; a whole-document reader had walked past them twice. That
is the argument for this file: the changed lines are where the defects are, and they are the lines a
reviewer is least likely to re-read because they were just repaired.

★ WHAT IT CHECKS, all of it mechanical and none of it a matter of taste:

  1. CROSS-REFERENCES RESOLVE. Every "§x.y", "Table n", "Figure n", "Box 1" and informal "The X
     section" introduced by the diff must name something that exists. Round 15 found a pointer
     promising what its target denied; this catches the cheaper failure of a pointer naming nothing
     at all.
     ⚠ ROUND 11 OF THE ASO JOURNAL ARTICLE (2026-08-28): a seat found that this check could never
     have caught its OWN document's round-10 repair — "The Controls section above" — because the
     journal article carries no "§N ·" numbering at all; it uses ordinary unnumbered headings, and
     the only informal cross-reference this repository's guards had ever resolved was the numeric
     "§N" symbol. The word "section" spelled out and pointed at a heading BY NAME was invisible to
     every gate. Added the single-preceding-capitalised-word check below for exactly that shape.
  2. PAIRED NUMERIC LISTS ARE BOUND IN A POSSIBLE ORDER. Inside an N-mer, a paired run of L leaves
     exactly N - L positions unpaired, so the two lists run in OPPOSITE directions. Writing both
     ascending inverts the mapping - which is exactly how "eleven or twelve ... four or five" got in.
  3. NEW UNIVERSALS OVER COUNTED NOUNS ARE REPORTED. A repair that closes a gap by widening a claim
     is the single most common defect this paper has produced. These are WARNINGS, not errors: a
     universal can be perfectly true, and the point is to force one deliberate look at each new one.

⚠ WHAT IT DOES NOT DO. It cannot tell whether a resolvable pointer's target actually SAYS what the
pointer promises, or whether a new claim is true. Those need a reader. This is the cheap pass that
runs every time, so the expensive reader spends its attention on what is left.

    python3 research/manuscripts/lint_changed_prose.py                 # working tree vs HEAD
    python3 research/manuscripts/lint_changed_prose.py HEAD~3..HEAD    # an explicit range
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
# ⛔ THE JOURNAL ARTICLE WAS MISSING FROM THIS LIST UNTIL ROUND 8, AND IT IS THE RISKIER HALF.
# This linter exists to catch a qualifier dropped from a claim. The journal article is a ~13x
# compression of the extended report, so it is where a bound gets dropped BY CONSTRUCTION — and it
# was the one document the linter never read. Round 8 found dropped qualifiers on the 10-bp
# criterion, the "floor over that subset" bound, the parent-sparing reports and the all-screen-clear
# count, none of which this gate could have seen. Anything spliced into a built paper belongs here.
DEFAULT_TARGETS = [
    # ⛔ THE EXTENDED REPORT WAS REMOVED FROM THIS TARGET LIST ON 2026-08-25 (trimcrae:
    # "Remove any checks requiring it from the gate"). Nothing in the gate reads
    # fusion-junction-aso-research-article.md any more; the file stays in the tree as history.
    "research/manuscripts/aso/fusion-junction-aso-journal-article.md",
    "research/manuscripts/aso/fusion-junction-aso-journal-references.md",
    "research/manuscripts/submission_tables.py",
    # ⚠ THE JOURNAL TABLES CARRY PROSE, AND NOTHING WAS READING IT (rounds 11-13, filed three times).
    # `fusion-junction-aso-journal-tables.md` holds both `DO NOT ORDER` verdicts and two long
    # captions, and it is spliced into both journal PDFs — so a qualifier dropped from a caption
    # ships to a reader while every prose instrument looks elsewhere. The generator is listed beside
    # it for the same reason `submission_tables.py` is: the caption is written in the generator, so
    # that is where a widened claim is actually typed.
    "research/manuscripts/aso/fusion-junction-aso-journal-tables.md",
    "research/manuscripts/aso_journal_tables.py",
    # ⭐ THE EMC VACCINE PATH, ADDED 2026-08-22 AT ROUND 1 OF ITS HARDENING CYCLE. It entered a review
    # cycle carrying exactly the gap the comment above records for the journal article: this linter's
    # whole job is "a qualifier dropped by an edit", and it could not read the one document about to
    # be edited by an adversarial review. Round 1 then dropped and restored qualifiers in that paper
    # a dozen times over. ⛔ The §-reference resolution below is per-target, so adding it here also
    # stops its §1-§10 references being validated against a different document's headings.
    "research/manuscripts/neoantigen/emc-vaccine-development-path.md",
]

WORD2NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}
_NUMWORD = "|".join(WORD2NUM)

_RUN_LIST = re.compile(
    rf"(?:run of|runs of)\s+((?:{_NUMWORD}|\d+)(?:\s+or\s+(?:{_NUMWORD}|\d+))*)\s+base pairs?"
    rf"|((?:{_NUMWORD}|\d+)(?:-\s*or\s+|\s+or\s+)(?:{_NUMWORD}|\d+))-?\s*base-pair", re.I)
_GAP_LIST = re.compile(
    rf"(?:leaves|carries|leaving|carrying)\s+((?:{_NUMWORD}|\d+)(?:\s+or\s+(?:{_NUMWORD}|\d+))*)"
    rf"\s+(?:positions? unpaired|mismatch(?:es)?|unpaired positions?)", re.I)
_NMER = re.compile(r"\b(\d+)-mer\b")
# A single capitalised word directly before "section" — "The Controls section", "the Discussion
# section" — never a 2+ word phrase, which is what let "Earlier versions of this section" and
# "That is the mechanism this section" (both real sentences in this repository, sentence-initial
# capital two-to-four words upstream of "section") false-positive when first tried.
_SECTION_REF = re.compile(r"\b([A-Z][A-Za-z'/-]*)\s+section\b")
_SECTION_REF_STOP = {"this", "that", "same", "above", "below", "following", "preceding", "prior",
                      "subsequent", "relevant", "whole", "entire", "current", "said", "latter",
                      "former", "next", "new", "final", "last", "every", "each", "any", "no",
                      "the", "a", "an"}

_COUNTED_NOUNS = ("counts?", "screens?", "designs?", "reagents?", "junctions?", "criteri(?:on|a)",
                  "rules?", "duplex(?:es)?", "sites?", "near-matches", "geometr(?:y|ies)",
                  "thresholds?", "registers?", "parents?", "tall(?:y|ies)")
_GOVERNS = re.compile(
    rf"\b(every|all|each|any|none of|no other|the only|only one)\b[\w\s,'’-]{{0,25}}?"
    rf"\b(?:{'|'.join(_COUNTED_NOUNS)})\b", re.I)


def _git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).stdout


def added_hunks(rev_range, targets):
    """[(path, joined_text)] — one entry per contiguous run of ADDED lines, joined into prose.

    Returns (path, neighbourhood, added_only). The neighbourhood carries context so a sentence that
    wraps across lines can be parsed whole; `added_only` carries just the new text, because a warning
    about a NEW claim must not fire on an unchanged line that merely sits nearby. Two of the first
    three warnings this file ever raised came from context lines, and a warning that fires on text
    the author did not touch is one the author learns to skip.

    ⛔ JOINED, NOT PER-LINE, AND THAT IS THE WHOLE POINT. The manuscript is hard-wrapped at about
    100 columns, so a single sentence routinely spans two or three source lines. The first version
    of this file matched per line and therefore could not see the very defect it was written for:
    "…leaves five or four" sat on one line and "positions unpaired respectively" on the next, so the
    paired-list check never fired. It was caught by testing the linter against the known defect
    rather than by reading it. A checker whose unit of analysis is smaller than a sentence cannot
    check sentences.
    """
    #: ⛔ -U2, NOT -U0, AND CONTEXT LINES ARE KEPT. Second measured failure of this instrument: with
    #: -U0 the diff holds only the modified line, so a sentence whose tail sits on the FOLLOWING
    #: unchanged line is still cut in half. The injected test defect — "…leaves four or five" with
    #: "positions unpaired respectively" wrapped onto the next line — survived the first two versions
    #: of this function for exactly that reason. The unit of analysis has to be the changed
    #: NEIGHBOURHOOD; a hunk is analysed only if it actually contains an addition.
    args = ["diff", "-U2"]
    if rev_range:
        args.append(rev_range)
    args += ["--", *targets]
    out, path, hunks = _git(*args), None, []
    current, added = [], []
    def _flush():
        if added:
            hunks.append((path, " ".join(current), " ".join(added)))
        current.clear(); added.clear()
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            _flush()
            path = line[6:]
        elif line.startswith("@@"):
            _flush()
        elif line.startswith("+") and not line.startswith("+++"):
            current.append(line[1:].strip()); added.append(line[1:].strip())
        elif line.startswith(" "):
            current.append(line[1:].strip())
    _flush()
    return hunks


def _known_anchors(article):
    """⛔⛔ THE ANCHORS OF *THIS* DOCUMENT, NOT OF WHICHEVER ONE CAME FIRST IN THE TARGET LIST.

    This resolved every target's §-references against `DEFAULT_TARGETS[0]` — the extended report —
    for as long as the journal article has been a target. The two documents do not share a section
    numbering: the report runs §1-§6 (Introduction, Results, Discussion, Reagents, Bounds, Methods)
    and the journal article runs §1-§8 (…, §7 Discussion, §8 Methods). So the check was wrong in
    BOTH directions at once, and the quiet direction is the dangerous one:

      * §7 and §8 in the journal article errored as naming no section, when both exist;
      * and every journal-article reference to §1-§6 was validated against the REPORT's section of
        that number — a different section — so a cross-reference pointing at the wrong place passed.

    A false alarm gets noticed on the next run. A cross-reference silently validated against another
    document's headings is the same shape as the one-of-a-pair guards this repository has been
    finding all week: an instrument bound to one member of a pair while reporting on both.
    """
    text = open(article, encoding="utf-8").read()
    sections = set(re.findall(r"^#{2,3}\s+(\d+(?:\.\d+)?)\s*·", text, re.M))
    tables = set(re.findall(r"\*\*Table (\d+)\.", text))
    figures = set(re.findall(r"\*\*(?:Supplementary )?Figure (S?\d+)\.", text))
    tables |= set(re.findall(r"\*\*Table (\d+)\.",
                             open(os.path.join(HERE, "aso",
                                               "fusion-junction-aso-submission-tables.md"),
                                  encoding="utf-8").read()))
    # ⚠ EVERY HEADING, NUMBERED OR NOT — for "The X section" informal references, which the §N
    # scheme above cannot see on a document (the journal article) that carries no section numbers
    # at all. Markdown emphasis markers stripped so "**Controls**" and "Controls" bind the same.
    headings = {re.sub(r"[*_`]", "", h).strip().lower()
                for h in re.findall(r"^#{2,3}\s+(.+)$", text, re.M)}
    return sections, tables, figures, headings


def _anchors_for(path, cache={}):
    """The anchor sets for the document a changed hunk actually lives in.

    A target with no headings of its own (the reference list, a generator) keeps being checked
    against the extended report, which is where its §-references point.
    """
    full = os.path.join(REPO, path)
    if path not in cache:
        own = _known_anchors(full) if os.path.exists(full) else (set(), set(), set(), set())
        if own[0] or own[3]:
            cache[path] = own
        else:
            fallback = _known_anchors(os.path.join(REPO, DEFAULT_TARGETS[0]))
            cache[path] = (fallback[0], own[1] | fallback[1], own[2] | fallback[2],
                            own[3] | fallback[3])
    return cache[path]


def _to_int(tok):
    tok = tok.strip().lower()
    return WORD2NUM.get(tok, int(tok) if tok.isdigit() else None)


def _split_list(blob):
    return [_to_int(p) for p in re.split(r"\s*(?:-\s*)?or\s+", blob) if _to_int(p) is not None]


def main(argv):
    rev_range = argv[1] if len(argv) > 1 else None
    targets = DEFAULT_TARGETS
    rows = added_hunks(rev_range, targets)
    errors, warnings = [], []

    for path, line, added in rows:
        base = os.path.basename(path)
        sections, tables, figures, headings = _anchors_for(path)

        for ref in re.findall(r"§(\d+(?:\.\d+)?)", line):
            if ref not in sections:
                errors.append(f"{base}: §{ref} names no section — {line.strip()[:110]}")
        for ref in re.findall(r"\bTable (\d+)", line):
            if ref not in tables:
                errors.append(f"{base}: Table {ref} does not exist — {line.strip()[:110]}")
        for ref in re.findall(r"\bFigure (S?\d+)", line):
            if ref not in figures:
                errors.append(f"{base}: Figure {ref} does not exist — {line.strip()[:110]}")
        for word in _SECTION_REF.findall(line):
            if word.lower() in _SECTION_REF_STOP:
                continue
            if not any(re.search(rf"\b{re.escape(word.lower())}\b", h) for h in headings):
                errors.append(f"{base}: '{word} section' names no heading it can resolve to — "
                               f"{line.strip()[:110]}")

        nmer, run, gap = _NMER.search(line), _RUN_LIST.search(line), _GAP_LIST.search(line)
        if nmer and run and gap:
            n = int(nmer.group(1))
            runs = _split_list(run.group(1) or run.group(2) or "")
            gaps = _split_list(gap.group(1) or "")
            if runs and gaps and len(runs) == len(gaps):
                bad = [(a, b) for a, b in zip(runs, gaps) if a + b != n]
                if bad:
                    errors.append(
                        f"{base}: paired lists bound in an impossible order — "
                        + " and ".join(f"{a}+{b}={a + b}" for a, b in bad)
                        + f" (each must total {n}) — {line.strip()[:110]}")

        m = _GOVERNS.search(added)
        if m:
            warnings.append(f"{base}: new universal '{m.group(0).strip()}' — {added.strip()[:110]}")

    print(f"lint_changed_prose: {len(rows)} changed passage(s) over "
          f"{rev_range or 'the working tree'}")
    for w in warnings:
        print(f"  ⚠ WARN  {w}")
    for e in errors:
        print(f"  ⛔ ERROR {e}")
    if warnings:
        print(f"\n{len(warnings)} new universal claim(s) over counted nouns. Each may be true; "
              "check each against the section or table it is about before shipping. A repair that "
              "closes a gap by widening a claim is this paper's most common self-inflicted defect.")
    if errors:
        print(f"\n{len(errors)} ERROR(s): a changed line names something that does not exist, or "
              "binds a numeric pair in an order the arithmetic forbids.")
        return 1
    print("   OK" if not warnings else "   OK (warnings above are for a human to clear)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
