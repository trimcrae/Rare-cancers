#!/usr/bin/env python3
r"""Verify — and repair — the roadmap's `:NNNN` line citations into the paper and the SI.

⛔ WHY THIS EXISTS. The roadmap cites the manuscript and SI by LINE NUMBER, in the form

    *"the quoted phrase"* (`:2200–2203`)

and line numbers drift every time the cited file gains a paragraph above the citation. A verification read
on 2026-08-06 found **every one of 39 such citations stale**, by a systematic +16 to +35 lines into the paper
and +15 to +35 into the SI — i.e. not a typo but the accumulated drift of ordinary edits. Nothing detected
it, because a wrong line number is still a well-formed link: it points somewhere, just not at the sentence.

⭐ THE POINT IS THAT THE QUOTE MAKES IT CHECKABLE. Each citation sits immediately after the phrase it cites,
so the true line can be DERIVED by searching the target for that phrase — the same way a human would check
one, and the reason this defect is fixable in bulk rather than one at a time.

⚠ WHAT THIS DELIBERATELY DOES NOT DO: invent a citation for a quote it cannot find. A phrase that does not
appear in the target is reported as UNRESOLVED and left alone — it may be a paraphrase, or the sentence may
have been rewritten, and silently repointing it at the nearest match is how a citation comes to vouch for
something it does not say.

⛔⛔ AND THE FIXER IS SILENT ABOUT EVERY OTHER COPY OF THE SAME FACT — WHICH IS WHY THIS FILE NOW
ENUMERATES THEM. Measured 2026-08-27 (AUT-PD-031), and it put a RED TRUNK on `main` for hours. An edit to
the paper shifted its lines by one; `--fix` corrected the roadmap's 18 drifted citations, printed
`rewrote 18 citation(s)`, exited 0 — and `research/modalities/instrument-census.json` and `.md`, which
EMBED the roadmap's citation-bearing cells verbatim behind a SEPARATE generator, stayed stale. The
staleness was found THREE COMMITS LATER by a `PREFLIGHT_MODALITIES=1` run, because the census guard lives
in the modalities suite while the edit that broke it ran under `PREFLIGHT_TESTS=1`.
★ THE CLASS: a fact with two homes and one fixer. Silence from a tool that just said "18 rewritten" reads
as completeness. So `--fix` now DERIVES — never types — the list of every tracked file that carries the
`:NNNN` syntax, splits it into copies GENERATED from a declared generator and hand-written carriers,
asks each generator about its own copy, and **exits non-zero when the rewrite succeeded but a downstream
copy is now stale**. A non-zero exit is the one thing that cannot be read as "done".

⛔⛔ AND THE SECOND HALF, MEASURED 2026-09-02 (still AUT-PD-031): ASKING A GENERATOR A QUESTION IT DOES
NOT UNDERSTAND IS NOT A READING, AND THE TOOL WAS PRINTING IT AS ONE. The first version had two values,
ok and not-ok, so anything that was not exit 0 became "reports its committed copy stale". On the trunk
`research-ledger.json` names `priority.py` as its producer in the same header form the census uses —
the literal declaration is NOT reproduced inside this window, and the reason is `GENERATOR_DECL_HEADER_
LINES` below — and `priority.py` takes no `--check` at all: it takes `--json/--write/--explain/--limit`.
So a `--fix` run printed a
MANUFACTURED staleness finding (an argparse usage error) directly beside the real census one. §4: an
absent reading is not a reading of absence, and a plausible-looking record is more dangerous than an
empty one; folding the two together also teaches the reader to discount the block holding the real find.
★ THREE THINGS ARE NOW SAYABLE — `GEN_FRESH`, `GEN_STALE`, `GEN_UNMEASURED` — and three exit codes say
them: `0` clean, `1` something is WRONG NOW, `2` nothing known-wrong and a copy could not be asked.
⛔ `2` IS NOT A SOFTENING. It is non-zero, it stops a `&&` chain, and it can never be read as done; what
it refuses to do is claim the tree is broken when the truth is that one copy is unmeasurable. That
matters because `research-ledger.json` is unmeasurable BY CONSTRUCTION — `priority.py` stamps
`age_factor_as_of` from today's date, so the ledger is not byte-reproducible from the graph and cannot
honestly carry a read-only `--check` at all. Folding it into `1` would leave `--fix` red every run of
every day over a condition nobody can clear, and §6 already names what that produces.
⛔ AND THE PROHIBITION IN `check_generated_carriers` IS NOW ENFORCED RATHER THAN WRITTEN. It said "this
function must never regenerate" while handing `--check` to any path a file declared — and a generator
shaped like `instrument_census.py` (`if "--check" in argv: … else: WRITE`) rewrites the tree on any argv
it does not recognise. `_advertises_check` reads the generator's source and refuses to run one that
never mentions the flag: today's carriers were safe by luck, and "RECORDED IS NOT ENFORCED" is the most
expensive sentence in this repository.
⛔ THE VERDICT IS BUILT IN ONE PLACE (`verdict`) SO NO PATH CAN PRINT A SUCCESS THAT READS AS
COMPLETENESS. The rewrite count may never be the last line; every run — green, red, check or fix — ends
by counting the hand-written carriers it did NOT check, in files and in citations; and there is no ✓
while any copy is stale or unmeasured. `rewrote 18 citation(s)` was TRUE; being the last thing said is
what made it read as done.

⛔⛔ WHY IT NAMES RATHER THAN REPAIRS, AND THIS IS THE DELIBERATE PART. Repairing more copies is the
tempting fix and it is the dangerous one: it would repair them to a WRONG shared value, silently.
  (1) The generated copies are GENERATED. Their correct content is whatever their generator derives from
      the roadmap; a value written here by a different code path is one no generator produces, so the
      next `--check` fails anyway and the tree meanwhile carries an unowned number.
  (2) The resolver is context-dependent, and the contexts differ. `LOOKBACK`/`QUOTE` attach a citation to
      the nearest preceding quoted phrase, and the downstream copy's surrounding cells are not the
      roadmap's. Measured on today's tree: for `:2140–2142` the roadmap's context yields the quote
      `'* (`:2200–2203`) | ✓ **PASSES, in scope** | `R11` |…'` and the census's yields
      `'* (`:2200–2203`) | ✓ **PASSES, in scope** | `PASSES` |…'` — the SAME citation, a DIFFERENT quote,
      because the census table has a column the roadmap does not. Both currently fail to resolve; one
      ordinary edit is all it takes for them to resolve to different lines, and then the "repair" silently
      repoints a citation at a sentence it does not quote.
  (3) For the hand-written carriers the target file is not even knowable here — this repository uses the
      same `:NNNN` syntax for lines in `.py` files, in sibling `.md` files and in the roadmap. "Repair"
      would mean guessing a target, and guessing a target is how a fabricated citation gets written.
  (4) ⛔⛔ AND SOME OF THEM ARE PINNED ON PURPOSE, SO "REPAIR" WOULD DESTROY THE THING THEY RECORD.
      The largest hand-written carrier on the trunk, `research/manuscripts/program/map-audit-strategy.md`
      (131 citations), states its own basis in its header: *"Audited: …nr4a3-program-map.md at commit
      `f67d0781` (459 lines, 2026-08-02…)"*. Its line numbers are a SNAPSHOT OF A NAMED COMMIT, not live
      pointers — advancing them to today's lines would silently re-date an audit and break the one thing
      that makes it checkable. A fixer cannot tell a pinned reference from a rotted one, and this is the
      case where being wrong is worst.
So: fix what is derivable from a quote in the file this tool owns; NAME everything else.

⛔⛔ AND UNTIL 2026-09-01 IT CHECKED 18 OF THE ROADMAP'S 56 CITATIONS AND SAID NOTHING ABOUT THE OTHER 38
(AUT-PD-134). The old `scan()` walked the citations, looked back 400 characters for a quoted phrase, and
`continue`d when it found none — so 14 citations were never reported in any line of output, and the summary
line's denominator was the 42 that survived that filter rather than the 56 that exist. A tool that prints
`18 correct · 0 DRIFTED · 24 unresolved (42 quoted citations)` reads as a full accounting of the file. It
was not one, and the guard on it only required `>= 10` resolved, so the reachable share could fall to a
quarter without anything going red.
★ THE FOUR MECHANISMS, EACH MEASURED ON THE TRUNK OF 2026-09-01 AND EACH FIXED HERE:
  (1) **The lookback window manufactured phantom quotes.** The old code searched `text[start-400:start]`,
      a slice that routinely cuts through the middle of an earlier quote — leaving its CLOSING `"*` in the
      window, which then paired with the next OPENING `*"` and produced a "quote" spanning two table cells.
      `:2140` was attached to `'* (`:2200–2203`) | ✓ **PASSES, in scope** | `R11` |…'`, a string that
      appears nowhere in any manuscript and never could. Quotes are now located over the WHOLE file once,
      so a quote is either wholly inside the lookback or not a candidate at all.
  (2) **`*"…"*` also matched inside `**"…"**`.** Bold-plus-quotes is ordinary prose here
      (`**THE "LBD" QUALIFIER IS LOAD-BEARING**`), and the old pattern's opening `*"` matched the second
      asterisk of a `**"`. That swallowed a real citation quote 900 characters later: the paper quote
      *"**four** NR4A3-unique cysteines"* was consumed by a span opening at an unrelated `**"no" outcome`.
      The opening is now `(?<!\*)\*"`. ⚠ The CLOSING deliberately has no matching guard, because the
      trunk really does write `*"…"***` where a citation quote sits inside a bold run.
  (3) **A quote can follow its citation.** The roadmap writes `` `:2508`: *"…"* ``, `` `:2478` says *"…"* ``
      and `` SI `:229` — *"…"* ``. Backwards-only attachment missed all three AND mis-attributed the next
      citation, which then reached back past them for someone else's quote. `TRAILING` handles this form
      and is deliberately a narrow grammar — punctuation and one attributive verb — read off the trunk.
  (4) **A quoted phrase can wrap over more than two lines.** `_find` joined at most two, so a quote that
      the paper wraps across three or four was reported UNRESOLVED. Two live citations were wrong by +68
      and +15 lines behind that limit. The join window is now derived from the needle's own length.
⭐ AND THE ATTACHMENT NOW CARRIES A CONFIDENCE, WHICH IS WHAT SEPARATES THE TWO HALVES THE LEDGER SAID MUST
NOT BE FIXED AS ONE. A citation whose quote is separated from it by ANOTHER citation or by a sentence
boundary is `confident=False`: still CHECKED and still reported, but **`--fix` refuses to rewrite it**.
Correctness (did we attach the right quote?) is answered by refusing to act where the answer is unclear;
staleness (has the paper stopped saying this?) is answered by `not_found`, unchanged and still never
repaired. Neither can hide inside the other, and no match was loosened to raise a count: every status is
reached by requiring the quoted text VERBATIM, modulo the same `_norm` typography folding as before.
⛔ EVERY CITATION IS NOW REPORTED. `no_quote`, `quote_too_short` and `inside_a_quote` are printed as their
own classes rather than dropped, and the total is asserted against the roadmap's own citation count, so
the denominator can no longer shrink silently.

Usage:
    python3 research/manuscripts/line_citations.py            # check, non-zero exit if any drifted
    python3 research/manuscripts/line_citations.py --fix      # rewrite the drifted ones in place

Exit codes: 0 nothing outstanding · 1 something is WRONG NOW (a stale copy, or a drift left for a
reader) · 2 nothing known-wrong and a generated copy could not be asked.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAP = os.path.join(HERE, "nr4a3-program-map.md")
PAPER = os.path.join(HERE, "degrader", "nr4a3-degrader-paper.md")
SI = os.path.join(HERE, "degrader", "nr4a3-degrader-paper-SI.md")

#: A citation: a backticked `:NNNN` or `:NNNN–NNNN`, en dash or hyphen.
CITE = re.compile(r"`:(\d+)(?:[–-](\d+))?`")

#: The quoted phrase this repo uses, `*"…"*`. Non-greedy, and it may span the wrapped line.
#: ⛔ THE OPENING REFUSES `**"`. Bold-plus-quotes is ordinary prose in these documents, and matching the
#: second asterisk of a `**"` opens a span that runs to the next `"*` anywhere in the file — measured
#: 2026-09-01, one such span swallowed the genuine quote 900 characters downstream and handed the citation
#: a phrase from an unrelated paragraph. ⚠ THE CLOSING HAS NO SUCH GUARD ON PURPOSE: the trunk writes
#: `**SI `:229` — *"Lead — NR4A3-selective (the validated path)"***`, a citation quote inside a bold run,
#: so refusing `"*` followed by `*` would drop a real quote. The asymmetry is measured, not aesthetic.
QUOTE = re.compile(r'(?<!\*)\*"(.+?)"\*', re.S)

#: ⭐ THE TRAILING FORM: a citation followed by the phrase it cites. Three spellings are on the trunk —
#: `` `:2508`: *"…"* ``, `` `:2478` says *"…"* `` and `` SI `:229` — *"…"* `` — and a backwards-only
#: attachment missed every one of them, then let the NEXT citation reach back past them and take a quote
#: that was never its own. The grammar is deliberately narrow (punctuation plus one attributive verb, all
#: read off the trunk rather than invented): widening it to "any nearby quote" is how `:92–99`, a citation
#: with no quote at all, acquires the quote of the sentence after it.
TRAILING = re.compile(r'\A[\s:—–\-]{0,3}(?:says|reads|states)?[\s:—–\-]{0,3}(?=(?<!\*)\*")')

#: An elided quote, `*"A … B"*`. The elision is the author's; the literal string can never appear in the
#: target, so the old resolver reported every one of them UNRESOLVED and could not tell an elision from a
#: paraphrase. Each part is now required VERBATIM and IN ORDER, which is the elision's actual meaning and
#: is strictly stronger than matching either part alone.
ELIDE = re.compile(r"\s*(?:…|\.\.\.)\s*")

#: What makes an attachment UNCONFIDENT: another citation, or a sentence/cell boundary, standing between
#: the quote and the citation. Such a citation is still checked and still reported — it is only barred
#: from `--fix`, because rewriting on a guessed attachment is how a citation comes to vouch for a
#: sentence it does not contain.
INTERVENING = re.compile(r"[.;|]\s|\n\s*\n")

#: Shorter than this, a quoted phrase does not identify a line and the resolver refuses to guess.
MIN_NEEDLE = 12

#: Every citation gets exactly one of these, and the count is asserted against the roadmap's own citation
#: count by the test suite — the denominator cannot shrink silently again.
STATUSES = ("ok", "drifted", "not_found", "ambiguous", "quote_too_short", "no_quote", "inside_a_quote")

#: How far back to look for the quote that a citation belongs to. A citation follows its quote closely;
#: scanning further would start attaching citations to whatever quote happened to appear earlier.
LOOKBACK = 400

#: A citation preceded by "SI" within this many characters targets the SI, not the paper.
SI_HINT = re.compile(r"\bSI\b[^.]{0,80}$")

#: ⭐ WHAT AN EXIT CODE MEANS HERE. `EXIT_UNMEASURED` is deliberately NON-ZERO and deliberately NOT
#: `EXIT_WRONG`: see `verdict`. Ordered, so `max()` never downgrades a real fault to a standing one.
EXIT_CLEAN, EXIT_UNMEASURED, EXIT_WRONG = 0, 2, 1


def _norm(s):
    """Fold the typography apart from the content: smart quotes, dashes, markdown emphasis, whitespace.

    The roadmap quotes the paper through a markdown round-trip, so `**bold**` inside a quoted phrase and a
    straight vs curly apostrophe are noise. Matching on the raw string finds nothing and would report every
    citation UNRESOLVED, which reads as "the checker is broken" rather than "the citation is fine".
    """
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-")
    # ⛔ AND THE MARKDOWN BACKSLASH ESCAPE, symmetrically on both sides. The roadmap quotes the paper from
    # inside a TABLE CELL, where a literal `|` must be written `\|`; the paper, not being in a table,
    # writes it bare. Measured 2026-09-01: `*"a wedge contribution of roughly **\|S\| ≳ 0.65 kcal/mol**
    # (2σ)"*` (`:1798`) failed to resolve for that reason alone, while the sentence sat at paper `:1871` —
    # a citation wrong by +73 lines that the checker reported as an unresolvable paraphrase.
    s = re.sub(r"[*`_\\]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _load(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    return lines, [_norm(l) for l in lines]


def _find(needle, norm_lines):
    """Every 1-indexed line at which `needle` BEGINS, or `None` if it is too short to identify one.

    ⭐ IT RETURNS A LIST, NOT A LINE, so a quote that occurs twice is `ambiguous` rather than silently
    pointed at whichever copy came first. Two roadmap citation pairs already share one quoted phrase while
    citing DIFFERENT lines (`:387–394`/`:2549`, `:1405`/`:1425`), so a first-match resolver would collapse
    both onto one line the moment that phrase became findable.

    ⛔ THE JOIN WINDOW IS DERIVED FROM THE NEEDLE, not fixed at two lines. The old two-line limit was not a
    rule about citations, it was a guess about wrapping, and two live citations were wrong by +68 and +15
    lines behind it. Growth stops as soon as the accumulator is longer than the needle can require, and the
    match must BEGIN inside the first line of the window — without that anchor a long enough window
    contains the needle from almost any starting line, which reports every citation as ambiguous.
    """
    n = _norm(needle)
    parts = [p for p in ELIDE.split(n) if p]
    if len(parts) > 1:
        parts = [p for p in parts if len(p) >= MIN_NEEDLE]
    if not parts or min(len(p) for p in parts) < MIN_NEEDLE:
        return None                      # too short to identify a line; refuse rather than guess
    budget = sum(len(p) for p in parts) + 400
    hits = []
    for i, first in enumerate(norm_lines):
        if not first:
            continue
        acc, j = first, i + 1
        while True:
            k = acc.find(parts[0])
            if 0 <= k < len(first):
                pos, whole = k + len(parts[0]), True
                for p in parts[1:]:
                    k2 = acc.find(p, pos)
                    if k2 < 0:
                        whole = False
                        break
                    pos = k2 + len(p)
                if whole:
                    hits.append(i + 1)
                    break
            if j >= len(norm_lines) or len(acc) > budget or j - i > 12:
                break
            acc, j = acc + " " + norm_lines[j], j + 1
    return hits


def _attach(text, quotes, spans, cite):
    """The quote this citation cites, and whether the attachment is trustworthy enough to REWRITE on.

    Returns `(quote_span_or_None, confident)`. The trailing form wins outright — it is unambiguous and it
    is the form the backwards-only resolver both missed and mis-attributed. Otherwise the nearest quote
    ENDING before the citation and within `LOOKBACK` is taken, and the attachment is marked unconfident if
    anything stands between them that could mean the quote belongs to someone else.
    """
    cs, ce = cite.start(), cite.end()
    trailing = TRAILING.match(text[ce:])
    if trailing:
        q = next((q for q in quotes if q[0] == ce + trailing.end()), None)
        if q:
            return q, True
    back = [q for q in quotes if q[1] <= cs and cs - q[1] <= LOOKBACK]
    if not back:
        return None, True
    q = back[-1]
    gap = text[q[1]:cs]
    return q, not (CITE.search(gap) or INTERVENING.search(gap))


def scan():
    """One record per citation in the roadmap — EVERY citation, each carrying a `status` from `STATUSES`.

    ⛔ NOTHING IS DROPPED. The previous version `continue`d past any citation with no quote in its lookback
    window, so 14 of the roadmap's 56 citations produced no output at all and the summary line's
    denominator was 42. A citation this tool cannot check is now REPORTED as one it cannot check.
    """
    with open(MAP, encoding="utf-8") as fh:
        text = fh.read()
    paper_raw, paper = _load(PAPER)
    si_raw, si = _load(SI)

    quotes = [(m.start(), m.end(), m.group(1)) for m in QUOTE.finditer(text)]
    cites = list(CITE.finditer(text))
    spans = [(m.start(), m.end()) for m in cites]

    out = []
    for m in cites:
        rec = {
            "span": (m.start(), m.end()),
            "cited": int(m.group(1)),
            "cited_end": int(m.group(2)) if m.group(2) else None,
            "true": None,
            "target": None,
            "quote": None,
            "confident": True,
        }
        if any(q[0] < m.start() and q[1] > m.end() for q in quotes):
            # A citation INSIDE a quoted phrase is part of the quotation, not a reference of this file's.
            rec["status"] = "inside_a_quote"
            out.append(rec)
            continue
        q, confident = _attach(text, quotes, spans, m)
        rec["confident"] = confident
        if q is None:
            rec["status"] = "no_quote"
            out.append(rec)
            continue
        rec["quote"] = q[2]
        before = text[max(0, m.start() - LOOKBACK):m.start()]
        rec["target"] = "SI" if SI_HINT.search(before) else "paper"
        hits = _find(q[2], si if rec["target"] == "SI" else paper)
        if hits is None:
            rec["status"] = "quote_too_short"
        elif not hits:
            rec["status"] = "not_found"
        elif len(hits) > 1:
            rec["status"] = "ambiguous"
        else:
            rec["true"] = hits[0]
            rec["status"] = "ok" if hits[0] == rec["cited"] else "drifted"
        out.append(rec)
    return text, out


#: ⛔ HOW A DOWNSTREAM COPY DECLARES THE GENERATOR THAT OWNS IT. Both forms are already in use on the
#: trunk: the markdown view opens with an HTML comment naming its producer, and the JSON carries a
#: `_generated_by` key. Reading the generator OUT OF THE FILE is what keeps this enumeration derived; a
#: list of generators typed here would be one more copy of a fact, which is the defect this whole section
#: exists to stop making.
GENERATOR_DECL = (
    re.compile(r"GENERATED by ([A-Za-z0-9_./-]+\.py)"),
    re.compile(r'_generated_by"?\s*[:=]\s*"([A-Za-z0-9_./-]+\.py)"'),
)

#: ⛔ THE DECLARATION IS A HEADER, AND THE WINDOW IS WHY THIS FILE DOES NOT CLASSIFY ITSELF.
#: ⚠ MEASURED WHILE WRITING THIS (2026-08-28): the first version searched the whole file, and the very
#: comment above — which quoted both declaration forms verbatim so a reader could see them — made
#: `line_citations.py` match its own detector and report itself as a generated copy of the instrument
#: census. That is the one-of-a-pair class again, in the smallest possible form: a detector and a
#: document that describes it, living in one file. Anchoring to the header is the honest rule anyway —
#: a generated artifact says so at the top, where a reader meets it — and it is checked: today's two
#: generated carriers declare on line 1 (the `.md`) and line 3 (the `.json`).
#: ⚠ THE FAILURE DIRECTION IS NAMED, NOT SILENT. A generated file that declared its producer below this
#: window would be classed hand-written — but a hand-written carrier is still PRINTED by
#: `report_carriers`, so it degrades to "named but not `--check`ed", never to "not mentioned".
GENERATOR_DECL_HEADER_LINES = 40


def _tracked_files():
    """Every path `git ls-files` reports, repo-relative.

    ⛔ RAISES rather than returning empty. An absent reading is not a reading of absence: if git is
    unavailable this function must not hand back `[]`, because `[]` renders as "no other file carries a
    line citation" — the exact false completeness this module was extended to remove.
    """
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("line_citations: `git ls-files` failed (%s). The downstream-carrier "
                           "enumeration cannot be derived, and an empty list would read as 'no other "
                           "copies exist'.\n%s" % (r.returncode, (r.stderr or "").strip()))
    return [f for f in r.stdout.split("\0") if f]


def declared_generator(body):
    """The producer this file's HEADER declares, or None. PURE — the one place the window is applied."""
    header = "\n".join(body.split("\n")[:GENERATOR_DECL_HEADER_LINES])
    for rx in GENERATOR_DECL:
        m = rx.search(header)
        if m:
            return m.group(1)
    return None


#: ⛔ A HAND-WRITTEN CARRIER THAT DECLARES A BASIS COMMIT. AUT-PD-031 closed the fixer's silence about
#: downstream copies and left one honest residual: the tool NAMES the hand-written carriers and CHECKS
#: none, so that surface is UNMEASURED rather than measured-clean — and the row says plainly that deciding
#: which are pinned-by-design versus genuinely rotted "is a reading job nobody has done".
#: ⭐ THIS DOES NOT DO THE READING, AND IT MUST NOT BE MISTAKEN FOR IT. It reports the one half a machine
#: can settle: whether the file's own header names the COMMIT its line numbers were taken against. A
#: document that does is stating that its references are a snapshot, and advancing them would silently
#: re-date the audit it records — the case where "repair" is worst. A document that does not has declared
#: nothing, which is NOT evidence that its references are current: an absent reading is not a reading of
#: absence, so both classes print as unchecked and neither is called clean.
#: ⚠ MEASURED ON THE TRUNK, 2026-09-01, and the wording is the measurement's: three of the sixteen
#: hand-written carriers name a basis commit in their header — `program/map-audit-strategy.md` (131
#: citations, *"Audited: … at commit `f67d0781`"*) and the two ASO red-team rounds (12 between them,
#: round 7 stating outright that *"every finding below is anchored on a verbatim quote and a line number
#: at commit"*). The other thirteen carry about 287 citations and declare nothing either way.
PIN_DECL = re.compile(r"\bcommit\s+`?([0-9a-f]{7,40})`?", re.I)


def declared_pin(body):
    """The basis commit this file's HEADER names, or None. PURE — same window as `declared_generator`.

    ⛔ THE HEADER WINDOW IS THE POINT, and it is the same trap that caught the generator detector: this
    module's own docstring QUOTES `map-audit-strategy.md`'s declaration verbatim so a reader can see the
    form, and a whole-file search would make `line_citations.py` report itself as a pinned audit.
    """
    header = "\n".join(body.split("\n")[:GENERATOR_DECL_HEADER_LINES])
    m = PIN_DECL.search(header)
    return m.group(1) if m else None


def carriers():
    """DERIVED: every tracked file other than the roadmap that carries the `:NNNN` citation syntax.

    Returns [(relpath, generator_or_None)], sorted. `generator` is the path the file itself declares as
    its producer, so a copy that arrives behind a new generator is enumerated the day it lands — no entry
    here, and none in `MEMBERS`-style list anywhere, has to be edited for that to work.

    ⚠ IT DELIBERATELY EXCLUDES NOTHING BUT THE ROADMAP. `line_citations.py` and its own test carry the
    syntax in prose and in a regex and are reported like any other carrier. An exclusion list is a typed
    fact, and the first thing a typed exclusion list does is grow a line for the file that actually broke.
    """
    map_rel = os.path.relpath(MAP, ROOT).replace(os.sep, "/")
    out = []
    for f in _tracked_files():
        if f == map_rel:
            continue
        try:
            with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                body = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        if not CITE.search(body):
            continue
        out.append((f, declared_generator(body)))
    return sorted(out)


#: ⛔ THE READ-ONLY FLAG THIS TOOL HANDS A GENERATOR — AND THE ONE IT REFUSES TO HAND BLIND.
CHECK_FLAG = "--check"

#: ⛔ HOW A GENERATOR SAYS "I DO NOT TAKE THAT FLAG". argparse exits 2 and writes one of these; a bare
#: `if "--check" in argv` generator writes nothing of the kind. Matching the refusal is what separates
#: *no reading* from *a reading that the copy is stale* — a distinction the first version of this
#: function did not have, and got wrong on the trunk (see `GEN_UNMEASURED`).
FLAG_REFUSED = re.compile(r"unrecognized arguments?|invalid choice|no such option|unknown option", re.I)

#: ⛔⛔ THE THREE THINGS THIS TOOL CAN HONESTLY SAY ABOUT A GENERATED COPY, AND `UNMEASURED` IS NOT A
#: SOFTER `STALE`. ⚠ MEASURED ON THE TRUNK, 2026-09-02, and this is AUT-PD-031's own defect one level in:
#: `research-ledger.json` declares *"GENERATED by research/autonomy/priority.py"* in its header, and
#: `priority.py` has no `--check` — it takes `--json/--write/--explain/--limit`. So the old two-valued
#: version handed it `--check`, argparse exited 2, and `--fix` printed
#:     ⛔ THE REWRITE SUCCEEDED AND THE TREE IS NOT CONSISTENT YET. 2 generator report its committed
#:        copy stale:  python3 research/autonomy/priority.py
#:            usage: priority.py [-h] [--json] [--write] …
#:            priority.py: error: unrecognized arguments: --check
#: — a MANUFACTURED staleness finding printed beside a real one. Nothing about the ledger was stale;
#: the generator had simply not been asked a question it understands. §4: an absent reading is not a
#: reading of absence, and a plausible-looking record is more dangerous than an empty one. Folding the
#: two together also teaches a reader to discount the block that contains the real finding.
GEN_FRESH, GEN_STALE, GEN_UNMEASURED = "fresh", "stale", "unmeasured"


def _advertises_check(abs_gen):
    """Does the generator's OWN SOURCE contain the flag this tool is about to hand it?

    ⛔⛔ THIS IS THE ENFORCEMENT OF A PROHIBITION THAT WAS PREVIOUSLY ONLY WRITTEN DOWN. The old
    docstring said "this function must never regenerate" and nothing made that true: it handed
    `--check` to whatever path a file declared, and a generator shaped like `instrument_census.py`
    (`if "--check" in argv: … else: WRITE`) regenerates the tree on ANY argv it does not recognise.
    Today's three carriers happen to be safe — one implements `--check`, one rejects it through
    argparse — so the tree was protected by luck rather than by a check. "RECORDED IS NOT ENFORCED"
    is this repository's most expensive sentence; a static read of the generator's source is what
    makes it enforced, and it costs one file read and executes nothing.
    ⚠ IT IS DELIBERATELY A TOKEN SEARCH, NOT A PARSE. A generator that merely MENTIONS `--check` and
    does not implement it is still caught, one step later, by `FLAG_REFUSED` — two independent
    mechanisms for one hazard, because the failure this guards is silent tree mutation.
    """
    try:
        with open(abs_gen, encoding="utf-8") as fh:
            return CHECK_FLAG in fh.read()
    except (OSError, UnicodeDecodeError):
        return False


def check_generated_carriers(found):
    """Ask each distinct declared generator about its own copy: [(generator, status, output)].

    `status` is one of `GEN_FRESH` / `GEN_STALE` / `GEN_UNMEASURED`. ⭐ THE GENERATOR IS THE AUTHORITY ON
    ITS OWN COPY, so this asks it rather than re-deriving the copy here — and when it cannot ask, it
    says so in a class of its own rather than reporting an answer it did not get.
    """
    results = []
    for gen in sorted({g for _, g in found if g}):
        abs_gen = os.path.normpath(os.path.join(ROOT, gen))
        # ⛔ THE GENERATOR PATH COMES OUT OF A FILE, AND THIS FUNCTION EXECUTES IT. `GENERATOR_DECL`'s
        # character class admits `.` and `/`, so a declaration reading `../../anything.py` is well-formed.
        # Refuse anything that resolves outside the repository, and report the refusal rather than
        # skipping it silently — a generator we would not run is a copy we are not checking.
        if os.path.commonpath([abs_gen, ROOT]) != ROOT:
            results.append((gen, GEN_UNMEASURED,
                            "declared generator resolves OUTSIDE the repository; refused, so this copy "
                            "was NOT checked"))
            continue
        if not os.path.isfile(abs_gen):
            results.append((gen, GEN_UNMEASURED,
                            "declared generator does not exist at that path, so this copy was NOT "
                            "checked"))
            continue
        if not _advertises_check(abs_gen):
            results.append((gen, GEN_UNMEASURED,
                            "its source never mentions `%s`, and a generator that does not recognise a "
                            "flag may REGENERATE on it — so it was NOT RUN and this copy is UNMEASURED. "
                            "Give it a read-only `%s`, or check the copy from its own gate."
                            % (CHECK_FLAG, CHECK_FLAG)))
            continue
        r = subprocess.run([sys.executable, abs_gen, CHECK_FLAG], cwd=ROOT,
                           capture_output=True, text=True)
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        if r.returncode == 0:
            results.append((gen, GEN_FRESH, out))
        elif FLAG_REFUSED.search(out):
            results.append((gen, GEN_UNMEASURED,
                            "it REFUSED the flag rather than answering — this is NOT a staleness "
                            "reading, the copy is UNMEASURED:\n" + out))
        else:
            results.append((gen, GEN_STALE, out))
    return results


def report_carriers(found, header):
    gen_rows = [(f, g) for f, g in found if g]
    hand_rows = [f for f, g in found if not g]
    print("\n%s" % header)
    print("  ⛔ %d GENERATED cop%s of a roadmap cell — these carry the citation VERBATIM and go stale "
          "the moment the roadmap's changes:" % (len(gen_rows), "y" if len(gen_rows) == 1 else "ies"))
    for f, g in gen_rows:
        print("       %s   (regenerate: python3 %s)" % (f, g))
    if not gen_rows:
        print("       (none)")
    print("  ⚠ %d hand-written file%s also carr%s the `:NNNN` syntax. This tool CANNOT check them: it "
          "resolves a citation only from a quote in the roadmap, and this repository uses the same syntax "
          "for lines in .py files and in sibling .md files. They are NAMED, not fixed:"
          % (len(hand_rows), "" if len(hand_rows) == 1 else "s", "ies" if len(hand_rows) == 1 else "y"))
    for f in hand_rows:
        try:
            with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                body = fh.read()
        except (OSError, UnicodeDecodeError):
            print("       %s   (unreadable — not classified)" % f)
            continue
        pin = declared_pin(body)
        n = len(CITE.findall(body))
        # ⛔ BOTH LINES SAY "UNCHECKED". The pin note narrows the reading job AUT-PD-031 left open — it
        # says which of these must NOT be advanced — and it never promises the rest are current.
        print("       %-64s %3d citation(s)  %s"
              % (f, n, ("its header names basis commit %s — these read as a SNAPSHOT; advancing them "
                        "would re-date what the document records" % pin) if pin
                 else "no basis commit declared; unchecked either way"))


def hand_written_surface(found):
    """(files, citations) this tool NAMES and does not check. DERIVED from `found`, never typed."""
    hand = [f for f, g in found if not g]
    n = 0
    for f in hand:
        try:
            with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                n += len(CITE.findall(fh.read()))
        except (OSError, UnicodeDecodeError):
            continue
    return len(hand), n


def verdict(found, gen_results, rewrote=None, needs_review=0):
    """THE LAST WORD OF EVERY RUN — `(lines, exit_code)`, built in ONE place. Pure; takes no I/O.

    ⛔⛔ THIS FUNCTION EXISTS SO THAT NO CODE PATH CAN PRINT A SUCCESS THAT READS AS COMPLETENESS.
    AUT-PD-031's whole cost was one sentence: `rewrote 18 citation(s)`, exit 0, while a second copy of
    the same line numbers stayed stale — and the sentence was TRUE. Truth was never the problem; being
    the LAST THING SAID was. So the rewrite count is no longer allowed to be the final line, and the
    final line is assembled here from the whole picture:
      · every generated copy that is STALE            → named, and the exit is non-zero;
      · every generated copy that is UNMEASURED       → named SEPARATELY, and the exit is non-zero;
      · the hand-written surface this tool cannot check → COUNTED IN EVERY RUN, in files and citations,
        whether or not anything is wrong, because "N files were never checked" is exactly the fact that
        a clean-looking run hides.
    ⛔ AND THERE IS NO ✓ WHILE ANYTHING IS UNRESOLVED. A tick beside an unmeasured copy is the same
    false completeness in a smaller font.

    `gen_results is None` means the generators were NOT ASKED in this mode (the checker does not run
    them — see the note in `main`), and the verdict says that rather than letting silence imply it.

    ⭐⭐ THREE EXIT CODES, BECAUSE THE FIX FOR A SILENT TOOL MUST NOT BE A PERMANENTLY RED ONE.
      `0` nothing outstanding · `1` something is WRONG NOW (a copy is STALE, or drifted citations were
      left for a reader) · `2` nothing is known to be wrong and a copy is UNMEASURED.
    ⚠ MEASURED, AND IT IS WHY THIS IS NOT COSMETIC: `research-ledger.json` is UNMEASURABLE BY
    CONSTRUCTION, not by omission. Its generator writes `score_inputs.age_factor_as_of` from TODAY'S
    DATE, so the ledger is not byte-reproducible from the graph and `priority.py` cannot honestly have a
    read-only `--check` at all. Folding that into `1` would make `--fix` red on every run of every day,
    for a condition nobody can clear — and CLAUDE.md §6 already names what that produces: "a gate that
    reddens under load is one people learn to re-run — worse than no gate." ⛔ THE ANSWER IS NOT EXIT 0.
    A standing condition is still a condition; `2` is non-zero, so it still stops a `&&` chain and still
    cannot be read as done — it simply does not claim the tree is broken when what is true is that one
    copy cannot be asked.
    """
    n_hand, n_hand_cites = hand_written_surface(found)
    n_copies = len([1 for _, g in found if g])
    n_gen = len({g for _, g in found if g})
    lines, code, clauses = [], EXIT_CLEAN, []

    if rewrote is not None:
        clauses.append("rewrote %d citation(s) in %s" % (rewrote, os.path.relpath(MAP, ROOT).replace(os.sep, "/")))
    if needs_review:
        clauses.append("LEFT %d drifted citation(s) for a reader" % needs_review)
        code = EXIT_WRONG

    if gen_results is None:
        clauses.append("%d generated cop%s behind %d generator(s) NOT ASKED in check mode (run --fix, "
                       "which asks each)" % (n_copies, "y" if n_copies == 1 else "ies", n_gen))
    else:
        stale = [(g, o) for g, st, o in gen_results if st == GEN_STALE]
        unmeasured = [(g, o) for g, st, o in gen_results if st == GEN_UNMEASURED]
        fresh = [g for g, st, _ in gen_results if st == GEN_FRESH]
        if stale:
            lines.append("\n⛔ THE TREE IS NOT CONSISTENT YET — %d generated cop%s of these line numbers "
                         "%s STALE:" % (len(stale), "y" if len(stale) == 1 else "ies",
                                        "is" if len(stale) == 1 else "are"))
            for g, out in stale:
                lines.append("     python3 %s" % g)
                for line in (out or "(no output)").split("\n"):
                    lines.append("        %s" % line)
            code = EXIT_WRONG
        if unmeasured:
            lines.append("\n⛔ AND %d GENERATED COP%s UNMEASURED — this tool could not ask, which is NOT "
                         "the same as an answer:" % (len(unmeasured),
                                                     "Y IS" if len(unmeasured) == 1 else "IES ARE"))
            for g, out in unmeasured:
                lines.append("     %s" % g)
                for line in (out or "(no output)").split("\n"):
                    lines.append("        %s" % line)
            # ⛔⛔ NEVER DOWNGRADES A REAL FAULT, AND `max()` IS THE WRONG TOOL FOR THAT — measured by
            # the guard on this contract, 2026-09-02. The exit NUMBERS are conventional (1 is the
            # ordinary shell failure, so WRONG must own it) and they run OPPOSITE to severity, so
            # `max(EXIT_WRONG, EXIT_UNMEASURED)` returns UNMEASURED and quietly downgrades a stale copy
            # to a standing condition. Severity is stated, not inferred from the integers.
            code = EXIT_WRONG if code == EXIT_WRONG else EXIT_UNMEASURED
        clauses.append("of %d generator(s) behind %d generated cop%s: %d fresh · %d STALE · %d UNMEASURED"
                       % (n_gen, n_copies, "y" if n_copies == 1 else "ies",
                          len(fresh), len(stale), len(unmeasured)))

    # ⛔ ALWAYS, IN EVERY MODE AND EVERY OUTCOME. This clause is the one a green run must still carry.
    clauses.append("%d hand-written carrier(s) holding %d citation(s) were NOT CHECKED by this tool"
                   % (n_hand, n_hand_cites))
    lines.append("\nline_citations verdict: " + " · ".join(clauses) + ".")
    return lines, code


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite drifted citations in place")
    args = ap.parse_args(argv)

    text, cites = scan()
    by = {st: [c for c in cites if c["status"] == st] for st in STATUSES}
    drifted = [c for c in by["drifted"] if c["confident"]]
    needs_review = [c for c in by["drifted"] if not c["confident"]]

    for c in drifted + needs_review:
        tag = "DRIFTED " if c["confident"] else "DRIFTED?"
        print(f"  {tag}  {c['target']} `:{c['cited']}` -> :{c['true']}   {c['quote'][:64]!r}"
              + ("" if c["confident"] else "   ⚠ attachment not confident — NOT auto-fixed"))
    for c in by["ambiguous"]:
        print(f"  AMBIGUOUS  {c['target']} `:{c['cited']}` — the quote occurs more than once, LEFT ALONE  "
              f" {c['quote'][:64]!r}")
    for c in by["not_found"]:
        print(f"  NOT FOUND  {c['target']} `:{c['cited']}` — quote not in the target, LEFT ALONE   "
              f"{c['quote'][:64]!r}")
    for c in by["quote_too_short"]:
        print(f"  TOO SHORT  {c['target']} `:{c['cited']}` — quoted phrase is under {MIN_NEEDLE} characters "
              f"and cannot identify a line   {c['quote'][:64]!r}")
    for c in by["no_quote"]:
        print(f"  NO QUOTE   `:{c['cited']}` — no quoted phrase attached, so nothing to check against")
    for c in by["inside_a_quote"]:
        print(f"  QUOTED     `:{c['cited']}` — appears INSIDE a quoted phrase; it is part of the "
              f"quotation, not a reference of this file's")

    found = carriers()

    if args.fix:
        # ⛔ EVERY `--fix` RUN ASKS, EVEN ONE THAT REWRITES NOTHING. `--fix` is a human saying "make the
        # tree consistent"; a run that finds no drift and exits 0 without asking the generators answers a
        # narrower question than the one asked, in a way the operator cannot see. It is human-invoked and
        # has no automated caller (`fast_checks.py` and `tests.yml` both run the checker with no
        # arguments), so the few tens of milliseconds are free.
        if drifted:
            # rewrite back-to-front so earlier spans keep their offsets
            for c in sorted(drifted, key=lambda x: -x["span"][0]):
                s0, e0 = c["span"]
                span = str(c["true"]) if c["cited_end"] is None else \
                    f"{c['true']}–{c['true'] + (c['cited_end'] - c['cited'])}"
                text = text[:s0] + f"`:{span}`" + text[e0:]
            with open(MAP, "w", encoding="utf-8") as fh:
                fh.write(text)
        if needs_review:
            print("⛔ AND LEFT %d DRIFTED CITATION(S) ALONE, because the quote they were attached to is "
                  "separated from them by another citation or a sentence boundary. Rewriting on a guessed "
                  "attachment is how a citation comes to vouch for a sentence it does not contain — these "
                  "need a reader, not a fixer." % len(needs_review))
        report_carriers(found, "⛔ THIS IS NOT THE WHOLE TREE. Other files carry the same line numbers:")
        # ⛔ THE RESULT AND THE EXIT CODE BOTH COME OUT OF `verdict`, WHICH IS THE POINT OF AUT-PD-031:
        # the rewrite count is never the last thing said, and no exit is 0 while a copy is stale or
        # unmeasured. Nothing green is being turned red — no automated caller runs `--fix`.
        lines, code = verdict(found, check_generated_carriers(found),
                              rewrote=len(drifted), needs_review=len(needs_review))
        for line in lines:
            print(line)
        return code

    # ⛔ THE DENOMINATOR IS EVERY CITATION IN THE ROADMAP, and the classes sum to it. The old summary read
    # "(42 quoted citations)" while the file held 56 — a full-looking accounting of a filtered subset is
    # what let the checked share fall to a third without anything saying so (AUT-PD-134).
    checked = len(by["ok"]) + len(by["drifted"])
    print(f"\nline_citations: {len(by['ok'])} correct · {len(drifted)} DRIFTED · "
          f"{len(needs_review)} drifted-but-unconfident · {len(by['ambiguous'])} ambiguous · "
          f"{len(by['not_found'])} quote not found · {len(by['quote_too_short'])} quote too short · "
          f"{len(by['no_quote'])} carry no quote · {len(by['inside_a_quote'])} inside a quotation")
    print(f"  coverage: {checked} of {len(cites)} citations in {os.path.relpath(MAP, ROOT).replace(os.sep, '/')} were resolved "
          f"to a line ({100.0 * checked / len(cites):.0f}%). The rest are NAMED above, not skipped.")
    # ⚠ REPORTED, NOT GATED, in check mode. This checker is a member of the fast six and its name is
    # "roadmap line citations resolve"; failing it because an unrelated cell of a generated view drifted
    # would be a second gate wearing the first one's name. The staleness of a generated copy is gated by
    # preflight's generated-artifact loop, which now carries the census row.
    report_carriers(found, "Other files carrying the `:NNNN` syntax — NOT checked by this tool:")
    # ⛔ ONLY A CONFIDENT DRIFT GATES. An unconfident one is a citation this tool declines to repoint; it
    # was reported as UNRESOLVED and ungated before this change too, so nothing that used to be red has
    # been made green — what changed is that it is now named as a drift a READER has to settle.
    # ⚠ AND THE CHECKER STILL DOES NOT ASK THE GENERATORS — `gen_results=None` — which is a scoping
    # decision, not an oversight: this checker is a member of the fast six under the name "roadmap line
    # citations resolve", and failing it because an unrelated cell of a generated view drifted would be a
    # second gate wearing the first one's name. What changed is that the run now SAYS it did not ask,
    # instead of ending on a coverage percentage that reads like a full accounting of the tree.
    lines, _ = verdict(found, None)
    for line in lines:
        print(line)
    return EXIT_WRONG if drifted else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
