#!/usr/bin/env python3
"""Verify — and repair — the roadmap's `:NNNN` line citations into the paper and the SI.

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
re-runs each generator's own `--check`, and **exits non-zero when the rewrite succeeded but a downstream
copy is now stale**. A non-zero exit is the one thing that cannot be read as "done".

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

Usage:
    python3 research/manuscripts/line_citations.py            # check, non-zero exit if any drifted
    python3 research/manuscripts/line_citations.py --fix      # rewrite the drifted ones in place
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
QUOTE = re.compile(r'\*"(.+?)"\*', re.S)

#: How far back to look for the quote that a citation belongs to. A citation follows its quote closely;
#: scanning further would start attaching citations to whatever quote happened to appear earlier.
LOOKBACK = 400

#: A citation preceded by "SI" within this many characters targets the SI, not the paper.
SI_HINT = re.compile(r"\bSI\b[^.]{0,80}$")


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
    s = re.sub(r"[*`_]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _load(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    return lines, [_norm(l) for l in lines]


def _find(needle, norm_lines):
    """1-indexed line of the first line containing `needle`, or None.

    Falls back to a two-line join, because a quoted phrase in the target is frequently wrapped.
    """
    n = _norm(needle)
    if len(n) < 12:                      # too short to identify a line; refuse rather than guess
        return None
    for i, l in enumerate(norm_lines):
        if n in l:
            return i + 1
    for i in range(len(norm_lines) - 1):
        if n in norm_lines[i] + " " + norm_lines[i + 1]:
            return i + 1
    return None


def scan():
    """[(pos, start, end, cited_line, true_line, target, quote)] for every citation carrying a quote."""
    with open(MAP, encoding="utf-8") as fh:
        text = fh.read()
    paper_raw, paper = _load(PAPER)
    si_raw, si = _load(SI)

    out = []
    for m in CITE.finditer(text):
        before = text[max(0, m.start() - LOOKBACK):m.start()]
        quotes = QUOTE.findall(before)
        if not quotes:
            continue
        quote = quotes[-1]
        target = "SI" if SI_HINT.search(before) else "paper"
        true_line = _find(quote, si if target == "SI" else paper)
        out.append({
            "span": (m.start(), m.end()),
            "cited": int(m.group(1)),
            "cited_end": int(m.group(2)) if m.group(2) else None,
            "true": true_line,
            "target": target,
            "quote": quote,
        })
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


def carriers():
    """DERIVED: every tracked file other than the roadmap that carries the `:NNNN` citation syntax.

    Returns [(relpath, generator_or_None)], sorted. `generator` is the path the file itself declares as
    its producer, so a copy that arrives behind a new generator is enumerated the day it lands — no entry
    here, and none in `MEMBERS`-style list anywhere, has to be edited for that to work.

    ⚠ IT DELIBERATELY EXCLUDES NOTHING BUT THE ROADMAP. `line_citations.py` and its own test carry the
    syntax in prose and in a regex and are reported like any other carrier. An exclusion list is a typed
    fact, and the first thing a typed exclusion list does is grow a line for the file that actually broke.
    """
    map_rel = os.path.relpath(MAP, ROOT)
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


def check_generated_carriers(found):
    """Run each distinct declared generator's own `--check` and return [(generator, ok, output)].

    ⭐ THE GENERATOR IS THE AUTHORITY ON ITS OWN COPY, so this asks it rather than re-deriving the copy
    here. ⛔ AND IT ONLY EVER PASSES `--check`: this function must never regenerate, because a linter that
    silently rewrites a deposit artifact is a worse bug than the staleness it is reporting.
    """
    results = []
    for gen in sorted({g for _, g in found if g}):
        abs_gen = os.path.normpath(os.path.join(ROOT, gen))
        # ⛔ THE GENERATOR PATH COMES OUT OF A FILE, AND THIS FUNCTION EXECUTES IT. `GENERATOR_DECL`'s
        # character class admits `.` and `/`, so a declaration reading `../../anything.py` is well-formed.
        # Refuse anything that resolves outside the repository, and report the refusal rather than
        # skipping it silently — a generator we would not run is a copy we are not checking.
        if os.path.commonpath([abs_gen, ROOT]) != ROOT:
            results.append((gen, False, "declared generator resolves OUTSIDE the repository; refused"))
            continue
        if not os.path.isfile(abs_gen):
            results.append((gen, False, "declared generator does not exist at that path"))
            continue
        r = subprocess.run([sys.executable, abs_gen, "--check"], cwd=ROOT,
                           capture_output=True, text=True)
        results.append((gen, r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()))
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
        print("       %s" % f)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite drifted citations in place")
    args = ap.parse_args(argv)

    text, cites = scan()
    drifted = [c for c in cites if c["true"] and c["true"] != c["cited"]]
    unresolved = [c for c in cites if not c["true"]]
    ok = [c for c in cites if c["true"] and c["true"] == c["cited"]]

    for c in drifted:
        print(f"  DRIFTED  {c['target']} `:{c['cited']}` -> :{c['true']}   {c['quote'][:64]!r}")
    for c in unresolved:
        print(f"  UNRESOLVED  {c['target']} `:{c['cited']}` — quote not found, LEFT ALONE   "
              f"{c['quote'][:64]!r}")

    found = carriers()

    if args.fix and drifted:
        # rewrite back-to-front so earlier spans keep their offsets
        for c in sorted(drifted, key=lambda x: -x["span"][0]):
            s, e = c["span"]
            span = str(c["true"]) if c["cited_end"] is None else \
                f"{c['true']}–{c['true'] + (c['cited_end'] - c['cited'])}"
            text = text[:s] + f"`:{span}`" + text[e:]
        with open(MAP, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"\nrewrote {len(drifted)} citation(s) in {os.path.relpath(MAP, ROOT)}")
        report_carriers(found, "⛔ THIS IS NOT THE WHOLE TREE. Other files carry the same line numbers:")

        stale = [(g, out) for g, okg, out in check_generated_carriers(found) if not okg]
        if stale:
            print("\n⛔ THE REWRITE SUCCEEDED AND THE TREE IS NOT CONSISTENT YET. "
                  "%d generator report%s its committed copy stale:" % (len(stale), "s" if len(stale) == 1
                                                                       else ""))
            for g, out in stale:
                print("     python3 %s" % g)
                for line in (out or "(no output)").split("\n"):
                    print("        %s" % line)
            # ⛔ NON-ZERO ON PURPOSE, AND IT IS THE WHOLE POINT OF AUT-PD-031. `rewrote 18 citation(s)`
            # followed by exit 0 is what read as "done" and shipped a red trunk. A caller cannot mistake
            # a non-zero exit for completeness, and no automated caller runs `--fix` (fast_checks.py and
            # tests.yml both run the checker with no arguments), so nothing green is being turned red.
            return 1
        print("\n✓ every declared generator reports its committed copy still reproduces.")
        return 0

    print(f"\nline_citations: {len(ok)} correct · {len(drifted)} DRIFTED · {len(unresolved)} unresolved "
          f"({len(cites)} quoted citations)")
    # ⚠ REPORTED, NOT GATED, in check mode. This checker is a member of the fast six and its name is
    # "roadmap line citations resolve"; failing it because an unrelated cell of a generated view drifted
    # would be a second gate wearing the first one's name. The staleness of a generated copy is gated by
    # preflight's generated-artifact loop, which now carries the census row.
    report_carriers(found, "Other files carrying the `:NNNN` syntax — NOT checked by this tool:")
    return 1 if drifted else 0


if __name__ == "__main__":
    sys.exit(main())
