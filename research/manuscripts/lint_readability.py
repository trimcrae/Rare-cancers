#!/usr/bin/env python3
"""Readability SCREEN for submission texts — where to look, never whether the prose is good. ($0, stdlib)

⚠ WHY THIS EXISTS. trimcrae, 2026-08-27, on the ASO preprint v1 (doi 10.32388/VL3LJR): "A big issue
with the preprint v1 is readability. It's written in a very difficult to understand style." Measured
on the published text: mean sentence 28.8 words, 22% over 40 words, a 101-word sentence in the
methods, Flesch-Kincaid 15.3 — against 23.2 words and grade 13.0 for this repository's own MTAP
hypothesis, so the subject matter did not force it.

⛔⛔ AND THE SECOND HALF OF WHAT HE SAID IS THE DESIGN: "Good prose is going to come from better
writing style rather than metrics. Though the metrics could be a decent screening layer." So this
module SCREENS. It prints the sentences most likely to be unreadable, with line numbers, and the
`scientific-writing` skill does the actual work. It does NOT score prose quality, and it must never
become the thing a cycle optimises: Flesch-Kincaid counts syllables and words, and cannot see a
missing character, a buried stress position or an argument that does not follow. A paper can hit any
target and still be unreadable.

★ SO THE EXIT CODE IS DELIBERATELY NARROW. `--check` fails on exactly two things, both unambiguous
and neither satisfiable by making the paper say less:
  * a sentence longer than the ceiling — always worth splitting, and splitting drops no content;
  * a FALL in caution markers against the committed baseline — the failure mode that matters, where a
    pass buys readability by quietly dropping a hedge, a null or a limitation.
⛔ A BAD SCORE IS REPORTED AND NEVER FAILS THE BUILD. Gating on a mean would be an instruction to
write shorter sentences by any means available, including deleting the difficult truth, and this loop
optimises what it is measured on.

⚠ WHAT IT CANNOT MEASURE, SAID PLAINLY SO A GREEN RUN IS NOT MISREAD: whether the paper is clear,
whether its story is in order, whether a paragraph leads with its point, or whether any sentence
means what its author intended. A clean run means no sentence exceeds the ceiling and no caution was
lost. Nothing else.

Usage:
  python3 research/manuscripts/lint_readability.py --report [FILE ...]   # the screen; exit 0 always
  python3 research/manuscripts/lint_readability.py --caution FILE        # caution markers, itemised
  python3 research/manuscripts/lint_readability.py --check [FILE ...]    # the two hard rules
  python3 research/manuscripts/lint_readability.py --write-baseline      # re-pin caution counts
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASELINE = os.path.join(HERE, "readability-baseline.json")

# ⛔ THE BASELINE IS PINNED PER SUBMISSION TEXT, SO A DOCUMENT ENTERING `lint_style.TARGETS` MUST BE
# PINNED IN THE SAME COMMIT — `--write-baseline` is not automatic and nothing used to notice.
# ⚠ Measured 2026-08-28 (AUT-PD-141): `fusion-junction-aso-journal-references.md` was added to
# `TARGETS` that day and never pinned, so `publish_bar` clause 7 read `baseline.get(doc) is None`
# for a component of the paper posted at doi 10.32388/VL3LJR and returned PASS on its caution half
# while comparing against nothing. `tests/test_every_publication_endpoint_is_style_screened_or_
# recorded.py::test_the_caution_baseline_covers_every_screened_document` now fails on that gap.
#
# ⛔⛔ AND A REGENERATION IS NOT A FREE ACT, WHICH IS WHY THAT GAP WAS CLOSED BY ADDING ONE KEY
# RATHER THAN BY RUNNING THIS FLAG. `--write-baseline` re-pins EVERY document at once, so it
# silently accepts any FALL as the new floor — the exact laundering `--check` exists to refuse,
# performed by the tool that defines the floor. A dry comparison on 2026-08-28 would have raised 8
# pins and LOWERED one.
# ⚠ THAT LOWERED PIN IS AN OPEN FINDING, RECORDED HERE BECAUSE THE JSON CANNOT HOLD IT — this
# function writes four keys and would delete any note added beside them.
# `fusion-junction-aso-supplementary-information.md` is pinned at 7.8 and `measure()` produces 7.7.
# Both were checked at 648114f, the single commit that created this module AND the baseline, with
# the document byte-identical (17 markers over 2,211 words) then and now. No hedge left the SI; the
# pinned value was never reproducible from this generator. Correcting it changes a pinned figure and
# is a deliberate act (CLAUDE.md rule 1.2), not a side effect of some other commit.
# ★ SO: BEFORE RUNNING `--write-baseline`, DIFF IT FIRST. Any key whose value FALLS is a hedge, a
# null or a limitation to account for by name, or a stale pin to correct on the record — never a
# number to overwrite in passing.

#: ⛔ THE CEILING IS A SPLITTING PROMPT, NOT A STYLE OPINION, and it is set from measurement rather
#: than taste: at 60 words the published ASO article has 7 sentences (4.7%) over the line, every one
#: of which is genuinely three thoughts joined by dashes. A 40-word line would have flagged 33 and
#: become noise; a 100-word line would have flagged 2 and missed the methods sentence that prompted
#: this file. ⚠ Raising it to make a document pass is the edit this comment exists to make visible.
SENTENCE_CEILING = 60

#: Hedges, explicit nulls, and the vocabulary of an honest limitation. ⛔ THIS LIST IS THE ONE THING
#: HERE THAT PROTECTS THE SCIENCE — see the module docstring. Every entry is bounded (`\b`) because an
#: unbounded alternation is both a false witness somewhere and a false alarm somewhere else
#: (paper-hardening §8b.1d: `clear` matches inside "nu·clear", in a paper about a NUCLEAR receptor).
_CAUTION = re.compile(
    r"\b(?:may|might|could|appears?|suggests?|consistent with|cannot|could not|"
    r"not established|not demonstrated|no evidence|no difference|not significant|"
    r"unverified|unknown|UNKNOWN|untested|not tested|unadjusted|confounded|"
    r"limitation|caveat|preliminary|hypothes(?:is|ised|ized)|"
    r"we did not|does not|do not|is not|are not|was not|were not|neither|nor)\b",
    # ⛔ CASE-INSENSITIVE, AND THE REASON IS THE WHOLE POINT OF THE RATCHET. Measured 2026-08-27 by
    # this module's own guard test: splitting one long sentence into five dropped the marker count
    # 10 -> 8, because the hedges that had been mid-sentence ("and no difference was...", "we did
    # not test...") became SENTENCE-INITIAL ("No difference was...", "We did not test..."), and a
    # case-sensitive pattern stopped seeing them. ⚠ THAT IS THE RATCHET PUNISHING THE ONE MOVE THE
    # `scientific-writing` skill most wants — splitting — and being blind to every hedge a writer
    # puts at the start of a sentence, which is where careful writers put them.
    re.IGNORECASE,
)

#: A number carrying an interval is a caution marker too — dropping the interval and keeping the
#: point estimate is exactly the "readable but overstated" edit §4 of the skill warns about.
_INTERVAL = re.compile(r"\b(?:95\s?%\s?CI|\bCI\b|±|\bIQR\b|\brange\b|\bp\s?=|\bP\s?=)")


def body(md: str) -> list[tuple[int, str]]:
    """Return (line_number, text) for prose lines only.

    ⛔ EXTRACTION IS WHERE THIS KIND OF TOOL GOES WRONG, AND IT DID HERE FIRST. An exploratory pass
    written before this module reported a 108-word sentence in the ASO article. There is no such
    sentence: a `Keywords.` line had been glued to the next paragraph across a `---` rule, and
    citation markup (`<sup>23</sup>`, `<!--PMID:29937513-->`) was being counted as words. A gate built
    on that would have flagged sentences for CARRYING CITATIONS — a red on true input, which is worse
    than a green on false input because the first thing anyone does is loosen it
    (paper-hardening §8b.1). Hence: markup dies before any counting happens, and a horizontal rule is
    a hard sentence boundary.
    """
    out: list[tuple[int, str]] = []
    in_front = False
    in_code = False
    in_appendix = False
    for i, raw in enumerate(md.split("\n"), start=1):
        s = raw.rstrip()
        if i == 1 and s.strip() == "---":
            in_front = True
            continue
        if in_front:
            if s.strip() == "---":
                in_front = False
            continue
        if s.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^#{1,6}\s+Appendix\b", s.strip(), re.I):
            in_appendix = True
        if in_appendix:
            continue
        t = s.strip()
        if not t or t == "---" or t.startswith("|") or t.startswith(">"):
            continue
        if re.match(r"^#{1,6}\s", t):
            continue
        # markup, in the order that matters
        t = re.sub(r"<!--.*?-->", " ", t)                      # PMID comments
        # ⛔ SUPERSCRIPTS DIE WITH THEIR CONTENTS. Stripping only the TAGS leaves the citation
        # NUMBER behind as a word: measured, `<sup>23</sup>` turned a 14-word sentence into a
        # 16-word one, so a densely cited sentence would drift toward the ceiling for citing things.
        t = re.sub(r"<sup\b[^>]*>.*?</sup>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<sub\b[^>]*>.*?</sub>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<[^>]+>", " ", t)                          # any remaining tag
        t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)             # images
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)          # links -> their text
        t = re.sub(r"`[^`]*`", " ", t)                          # inline code
        t = re.sub(r"[*_]{1,3}", "", t)                          # emphasis
        t = re.sub(r"^\s*[-*+]\s+", "", t)                      # list bullets
        t = re.sub(r"^\s*\d+\.\s+", "", t)                      # numbered items
        t = " ".join(t.split())
        if t:
            out.append((i, t))
    return out


_ABBREV = re.compile(r"\b(?:e\.g|i\.e|vs|cf|et al|Fig|Eq|approx|ca|Dr|Prof|No)\.", re.I)


def paragraphs(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Join wrapped lines back into paragraphs, keeping each paragraph's first line number.

    ⛔⛔ THIS STEP IS NOT OPTIONAL AND ITS ABSENCE FAILS SILENTLY IN THE FLATTERING DIRECTION.
    Measured 2026-08-27, on the first run of this module: these manuscripts are HARD-WRAPPED at about
    100 columns, so splitting sentences per LINE chopped every real sentence at its wrap points. The
    published ASO article — 150 sentences, mean 28.8 words, longest 101 — reported as 359 sentences,
    mean 11.8, longest 21, and ZERO over the ceiling. A screen built on that would have called the
    very paper that prompted it exemplary.

    ⚠ IT IS THE SAME CLASS AS THE PHANTOM 108-WORD SENTENCE `body` describes, in the opposite
    direction, which is why both are recorded: an extractor can manufacture a finding OR erase one,
    and the erasing kind is more dangerous because nobody goes looking when a gate is green. A
    paragraph break, a list item, a table row, a heading and a horizontal rule are hard boundaries;
    a line wrap inside a paragraph is not.
    """
    out: list[tuple[int, str]] = []
    start: int | None = None
    buf: list[str] = []
    prev: int | None = None
    for ln, text in lines:
        if prev is not None and ln != prev + 1:
            # `body` drops blank lines, headings, tables and rules, so a gap in the line numbers IS
            # the paragraph boundary — no second pass over the raw text needed.
            out.append((start, " ".join(buf)))
            buf, start = [], None
        if start is None:
            start = ln
        buf.append(text)
        prev = ln
    if buf and start is not None:
        out.append((start, " ".join(buf)))
    return out


def sentences(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Split into sentences, keeping each one's starting line number."""
    out: list[tuple[int, str]] = []
    for ln, text in paragraphs(lines):
        guarded = _ABBREV.sub(lambda m: m.group(0).replace(".", "\x00"), text)
        for part in re.split(r"(?<=[.!?])\s+(?=[A-Z(“\"])", guarded):
            p = part.replace("\x00", ".").strip()
            # ⚠ THREE WORDS, NOT FOUR. The threshold exists to drop fragments (a table label, a
            # stray list stub), not prose. At four it silently discarded real short sentences —
            # "The reagent works." — which both undercounts sentences AND inflates the reported
            # mean, since the mean is exactly what short sentences pull down. A screen that hides
            # good writing from its own average is measuring the wrong thing.
            if len(p.split()) >= 3 and re.search(r"[a-z]{3}", p):
                out.append((ln, p))
    return out


_VOWELS = re.compile(r"[aeiouy]+")


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(_VOWELS.findall(w))
    if w.endswith("e") and n > 1:
        n -= 1
    return max(1, n)


def measure(path: str) -> dict | None:
    text = open(os.path.join(ROOT, path) if not os.path.isabs(path) else path,
                encoding="utf-8").read()
    ss = sentences(body(text))
    if not ss:
        return None
    lens = [len(s.split()) for _, s in ss]
    words = sum(lens)
    syl = sum(_syllables(w) for _, s in ss for w in s.split())
    n = len(ss)
    srt = sorted(lens)
    caution = sum(len(_CAUTION.findall(s)) + len(_INTERVAL.findall(s)) for _, s in ss)
    return {
        "path": path,
        "sentences": n,
        "words": words,
        "mean_len": round(words / n, 1),
        "median_len": srt[n // 2],
        "p90_len": srt[min(n - 1, int(n * 0.9))],
        "max_len": srt[-1],
        "over_ceiling": sum(1 for x in lens if x > SENTENCE_CEILING),
        "pct_over_40": round(100 * sum(1 for x in lens if x > 40) / n, 1),
        "flesch_reading_ease": round(206.835 - 1.015 * (words / n) - 84.6 * (syl / words), 1),
        "flesch_kincaid_grade": round(0.39 * (words / n) + 11.8 * (syl / words) - 15.59, 1),
        "caution_markers": caution,
        "caution_per_1000w": round(1000 * caution / words, 1),
        "worst": [{"line": ln, "words": len(s.split()), "text": s[:160]}
                  for ln, s in sorted(ss, key=lambda t: -len(t[1].split()))[:10]],
    }


def _targets(explicit: list[str]) -> list[str]:
    if explicit:
        return explicit
    # ⭐ ONE HOME FOR "IS THIS A SUBMISSION TEXT": lint_style.py's TARGETS. Duplicating that list here
    # is the one-of-a-pair defect this repository has paid for seven times (paper-hardening §6) — a
    # document added to one list and not the other would be silently unscreened.
    sys.path.insert(0, HERE)
    from lint_style import TARGETS  # noqa: E402
    return [t for t in TARGETS if os.path.exists(os.path.join(ROOT, t))]


def _load_baseline() -> dict:
    if not os.path.exists(BASELINE):
        return {}
    return json.load(open(BASELINE, encoding="utf-8")).get("caution_per_1000w", {})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true", help="the screen: distribution + worst sentences")
    ap.add_argument("--caution", metavar="FILE", help="itemise the caution markers in one file")
    ap.add_argument("--check", action="store_true", help="the two hard rules")
    ap.add_argument("--write-baseline", action="store_true", help="re-pin the caution counts")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args(argv)

    if args.caution:
        m = measure(args.caution)
        if not m:
            print(f"no prose found in {args.caution}")
            return 0
        text = open(os.path.join(ROOT, args.caution), encoding="utf-8").read()
        found = _CAUTION.findall(text) + _INTERVAL.findall(text)
        print(f"{args.caution}: {m['caution_markers']} caution marker(s), "
              f"{m['caution_per_1000w']} per 1000 words")
        from collections import Counter
        for tok, c in Counter(x.lower() for x in found).most_common(25):
            print(f"  {c:>4}  {tok}")
        return 0

    paths = _targets(args.files)
    rows = [m for m in (measure(p) for p in paths) if m]

    if args.write_baseline:
        json.dump({
            "_what": "Caution markers per 1000 words, per submission text, at the moment this was "
                     "pinned. A readability pass may raise it; a FALL is what --check refuses.",
            "_why": "A revision that reads better because a hedge, a null or a limitation quietly "
                    "left is worse than the dense original — it is now readable AND overstated, and "
                    "on a posted paper it is overstated under a DOI.",
            "_regenerate": "python3 research/manuscripts/lint_readability.py --write-baseline, and "
                           "say in the commit message which qualification changed and why.",
            "caution_per_1000w": {m["path"]: m["caution_per_1000w"] for m in rows},
        }, open(BASELINE, "w", encoding="utf-8"), indent=2)
        print(f"pinned caution baselines for {len(rows)} document(s) -> {BASELINE}")
        return 0

    if args.report or not args.check:
        print(f"{'document':<52}{'sent':>5}{'mean':>6}{'p90':>5}{'max':>5}"
              f"{'>60w':>6}{'FKGL':>6}{'caution/1kw':>13}")
        for m in rows:
            print(f"{m['path'].split('/')[-1][:51]:<52}{m['sentences']:>5}{m['mean_len']:>6}"
                  f"{m['p90_len']:>5}{m['max_len']:>5}{m['over_ceiling']:>6}"
                  f"{m['flesch_kincaid_grade']:>6}{m['caution_per_1000w']:>13}")
        if len(rows) == 1 and rows[0]["worst"]:
            print(f"\nlongest sentences in {rows[0]['path']} — the screen's whole output:")
            for w in rows[0]["worst"]:
                flag = "⛔" if w["words"] > SENTENCE_CEILING else "  "
                print(f"  {flag} line {w['line']:>5}  {w['words']:>3}w  {w['text'][:120]}")
        print("\n⚠ This is a SCREEN. It says where to look. Whether the prose is good is decided by "
              "reading it — see the `scientific-writing` skill.")
        if not args.check:
            return 0

    base = _load_baseline()
    problems: list[str] = []
    for m in rows:
        if m["over_ceiling"]:
            worst = [w for w in m["worst"] if w["words"] > SENTENCE_CEILING]
            problems.append(
                f"{m['path']}: {m['over_ceiling']} sentence(s) over {SENTENCE_CEILING} words. "
                f"Longest is {m['max_len']}w at line {worst[0]['line']}. Split them — splitting drops "
                f"no content. ⛔ Do not delete a clause to get under the line, and do not raise the "
                f"ceiling.")
        was = base.get(m["path"])
        if was is not None and m["caution_per_1000w"] < was:
            problems.append(
                f"{m['path']}: caution fell {was} -> {m['caution_per_1000w']} markers per 1000 words. "
                f"⛔ A readability pass that costs a hedge, a null or a limitation has made the paper "
                f"worse, not better. Name which qualification left and why; if it left on purpose, "
                f"re-pin with --write-baseline IN THE SAME COMMIT.")

    if problems:
        print("\n⛔ readability check FAILED:")
        for p in problems:
            print(f"   {p}")
        return 1
    print(f"\n✅ readability check OK ({len(rows)} document(s)): no sentence over "
          f"{SENTENCE_CEILING} words, no caution lost. ⚠ This does NOT mean the prose is clear.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
