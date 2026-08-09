#!/usr/bin/env python3
"""Manuscript prose style — journal register, not repository register. ($0, stdlib)

WHY THIS EXISTS. This repository's house style is loud on purpose: glyphs that make a warning
impossible to skim past, bold that pins the load-bearing clause, and running commentary about why a
rule exists. That style earns its keep in CLAUDE.md, in the roadmap and in the JSON artifacts, where
the reader is a maintainer or an agent who needs to be stopped from repeating a specific mistake.

It is wrong in a manuscript. A journal reader is not being warned, and prose that keeps insisting on
its own honesty reads as advocacy rather than as a report. The tics are also recognisable as
machine-written, which costs the paper credibility it has otherwise earned.

WHAT IT CHECKS. Only files in TARGETS, and only their bodies. Frontmatter, fenced code, and any
section under an "Appendix" heading are exempt, because superseded-value bookkeeping is required by
CLAUDE.md rule 1.2 and belongs in an appendix rather than in the running text.

WHAT IT CANNOT CHECK. Whether the argument is any good, whether the register is consistent, or
whether a sentence is merely bad. It catches recurring mechanical tells. A clean run means the
known tics are absent, not that the prose is well written.

Usage:
  python3 research/manuscripts/lint_style.py                    # check (preflight / CI)
  python3 research/manuscripts/lint_style.py --report           # counts per file, exit 0
  python3 research/manuscripts/lint_style.py path/to/file.md    # check specific files
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

#: Manuscript bodies held to journal register. A file is added here when it becomes a submission
#: text; a memo, a plan or a findings note is NOT a submission text and must not be listed.
TARGETS = [
    "research/manuscripts/response-endpoint-indolent-tumours.md",
    # ⭐ ADDED 2026-08-09, the day four endpoints were taken to submission form. Gate 5 checks
    # REGISTER, and until now it enforced that on exactly one file while three other submission
    # texts drifted freely — a rule filed where it cannot fire is absent (CLAUDE.md §6). Measured
    # before the rewrites: 96 findings in the ATR package (bold 42.4/1000 against a limit of 12),
    # 283 in the surface-target landscape, and em-dashes at 18.7/1000 against a limit of 6 in the
    # repurposing menu. All are clean now, and this list is what stops them going back.
    # ⛔ SUBMISSION TEXTS ONLY. A memo, a plan or a findings note must not be added here — the
    # house style is CORRECT everywhere else in this repository.
    "research/manuscripts/emc-mtap-prmt5-hypothesis.md",
    "research/manuscripts/emc-mtap-prmt5-hypothesis-SI.md",
    "research/manuscripts/emc-atr-collaborator-package.md",
    "research/manuscripts/repurposing-hypotheses.md",
    "research/manuscripts/emc-surface-target-landscape.md",
    "research/manuscripts/emc-surface-target-landscape-si.md",
]

# Densities are per 1000 words. They are deliberately generous: the aim is to catch prose that
# leans on a device, not to ban the device. A paper that trips one of these is not using emphasis,
# it is using emphasis instead of sentence structure.
MAX_BOLD_PER_1000 = 12.0
MAX_EMDASH_PER_1000 = 6.0

GLYPHS = "⭐⛔⚠★◐○●✅❌📏⏱⏰📱🔬⚖⊕⇢⭑📊🌙♦✕⏸➜▸→⇒✦❗❓‼"

BANNED = [
    (r"\bthat is the point\b", "rhetorical closer; state the point instead of announcing it"),
    (r"\bwhich is precisely why\b", "rhetorical connective; use 'because' or start a new sentence"),
    (r"\bfor (that|this) reason\b(?=[^.]*\bstated\b)", "meta-commentary about ordering"),
    (r"\bstated (first|here|at full strength)\b", "narration about how the paper states things"),
    (r"\bdeliberately\b", "usually defends a choice the reader has not questioned"),
    (r"\b(Crucially|Importantly|Notably|Significantly),", "tells the reader what to find important"),
    (r"\bit is worth (noting|remembering|saying)\b", "if it is worth saying, say it"),
    (r"\bworth noting\b", "if it is worth noting, note it"),
    (r"\bthe honest (verb|answer|form|version|statement)\b", "self-describing candour"),
    (r"\bstated honestly\b", "self-describing candour"),
    (r"\brather than deflect(ed|ing)?\b", "self-describing candour"),
    (r"\bto be clear\b", "filler"),
    (r"\bcosts? (a sentence|nothing)\b", "rhetorical costing; give the actual cost"),
    (r"\bis not a (bug|feature)\b", "engineering idiom, out of register"),
    (r"\bthe whole (point|of it) is\b", "rhetorical closer"),
    (r"\bdoes exactly that\b", "self-congratulation"),
    (r"\breason (this|it) exists\b", "meta-commentary"),
    (r"\blet me\b", "first-person address, out of register for a manuscript"),
    (r"\bwe should be clear\b", "filler"),
]

SELF_REFERENTIAL = [
    (r"\bthis (paper|manuscript|section) (does not|refuses to|declines to)\b.{0,40}\b(hide|soften|smooth|deflect)",
     "narration about the paper's own candour"),
    (r"\b(stated|placed|put) in the abstract rather than\b", "narration about the paper's own structure"),
    (r"\bthe objection that would sink\b", "dramatised limitation"),
    (r"\bat (its|their) full strength\b", "dramatised limitation"),
    (r"\bthis is the (finding|objection|argument) with the\b", "editorialising about the paper's own content"),
]

SECOND_PERSON = re.compile(r"(?<![\w-])(you|your|yours)(?![\w-])", re.I)

# A short sentence opening with a negation or restriction and carrying no finite verb is the
# fragment-for-emphasis tic ("Not a landmark result.", "Only in one direction.").
FRAGMENT = re.compile(r"(?:^|(?<=[.!?]\s))(Not|Never|Only|No)\b([^.!?]{0,60})[.!?]")
FINITE_VERB = re.compile(
    r"\b(is|are|was|were|has|have|had|does|do|did|will|would|can|could|may|might|must|shall|"
    r"should|remains?|becomes?|shows?|gives?|carries|holds?|means?|makes?)\b", re.I)

HEADING_VERBS = re.compile(
    r"\b(is|are|was|were|does|do|did|cannot|can|must|should|would|will|has|have|means|makes|"
    r"leaves|gives|shows|comes|goes|fails|survives|changes)\b", re.I)


def _strip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[i + 1:], i + 1
    return lines, 0


def _body_lines(path):
    """Yield (lineno, text) for body prose: no frontmatter, no fences, no appendices."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read().split("\n")
    body, offset = _strip_frontmatter(raw)
    in_fence = False
    in_appendix = False
    seen_title = False
    table_header_next = False
    out = []
    for i, line in enumerate(body):
        lineno = offset + i + 1
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        heading_text = None
        if m:
            in_appendix = bool(re.match(r"^appendix\b", m.group(2).strip(), re.I))
            # The document title is the first H1 and is exempt from the noun-phrase rule. A paper
            # title is allowed to be a sentence -- that is what titles are -- and holding it to a
            # rule written for section headings would force a worse title to satisfy a linter.
            if m.group(1) == "#" and not seen_title:
                seen_title = True
            else:
                heading_text = m.group(2)
        if in_appendix:
            continue
        # A markdown table's header row legitimately uses bold; its separator marks it.
        is_sep = bool(re.match(r"^\|[\s:|-]+\|?$", stripped))
        out.append((lineno, line, table_header_next, heading_text))
        table_header_next = is_sep
    return out


def _word_count(entries):
    n = 0
    for _, line, _, _ in entries:
        n += len(re.findall(r"[A-Za-z][A-Za-z'-]*", line))
    return max(n, 1)


def lint_file(path):
    findings = []
    full = os.path.join(ROOT, path) if not os.path.isabs(path) else path
    if not os.path.exists(full):
        return None
    entries = _body_lines(full)
    words = _word_count(entries)

    bold_runs = 0
    emdashes = 0

    for lineno, line, is_table_header, heading in entries:
        for ch in line:
            if ch in GLYPHS:
                findings.append((lineno, "ERROR", "glyph",
                                 f"decorative glyph {ch!r} in manuscript body"))
                break

        emdashes += line.count("—")

        for m in re.finditer(r"\*\*(.+?)\*\*", line):
            bold_runs += 1
            if is_table_header or heading:
                continue
            prefix = line[:m.start()]
            # Bold opening a line, a list item or a table cell is a label; bold after running
            # text is emphasis inside a sentence, which is the tic.
            if re.search(r"[A-Za-z0-9,)][\s]*$", prefix) and not re.match(r"^[\s>|*\-+\d.]*$", prefix):
                findings.append((lineno, "ERROR", "bold-midsentence",
                                 f"bold inside a sentence: **{m.group(1)[:48]}**"))

        for pat, why in BANNED:
            mm = re.search(pat, line, re.I)
            if mm:
                findings.append((lineno, "ERROR", "banned-phrase",
                                 f"{mm.group(0)!r} — {why}"))
        for pat, why in SELF_REFERENTIAL:
            mm = re.search(pat, line, re.I)
            if mm:
                findings.append((lineno, "ERROR", "self-referential",
                                 f"{mm.group(0)[:48]!r} — {why}"))

        mm = SECOND_PERSON.search(re.sub(r"`[^`]*`", "", line))
        if mm and not line.strip().startswith(">"):
            findings.append((lineno, "ERROR", "second-person",
                             f"{mm.group(0)!r} addresses the reader directly"))

        if heading:
            h = re.sub(r"\*\*|`|[0-9]+\s*·\s*", "", heading).strip()
            if h.endswith("?"):
                findings.append((lineno, "ERROR", "heading-style",
                                 f"heading is a question: {h[:60]!r}"))
            elif HEADING_VERBS.search(h) or len(h.split()) > 10:
                findings.append((lineno, "ERROR", "heading-style",
                                 f"heading is a sentence, not a noun phrase: {h[:60]!r}"))

        for mm in FRAGMENT.finditer(line):
            frag = mm.group(0)
            if not FINITE_VERB.search(frag) and len(frag.split()) <= 8:
                findings.append((lineno, "ERROR", "fragment",
                                 f"sentence fragment used for emphasis: {frag.strip()!r}"))

    bold_density = bold_runs * 1000.0 / words
    emdash_density = emdashes * 1000.0 / words
    if bold_density > MAX_BOLD_PER_1000:
        findings.append((0, "ERROR", "bold-density",
                         f"{bold_runs} bold runs over {words} words = "
                         f"{bold_density:.1f}/1000, limit {MAX_BOLD_PER_1000}"))
    if emdash_density > MAX_EMDASH_PER_1000:
        findings.append((0, "ERROR", "emdash-density",
                         f"{emdashes} em-dashes over {words} words = "
                         f"{emdash_density:.1f}/1000, limit {MAX_EMDASH_PER_1000}"))

    return {"path": path, "words": words, "findings": findings,
            "bold_per_1000": round(bold_density, 1),
            "emdash_per_1000": round(emdash_density, 1)}


def main(argv):
    report = "--report" in argv
    paths = [a for a in argv if not a.startswith("--")] or TARGETS

    results = [r for r in (lint_file(p) for p in paths) if r]
    if not results:
        print("lint_style: no target files present — nothing to check")
        return 0

    errors = 0
    for r in results:
        by_kind = {}
        for _, sev, kind, _ in r["findings"]:
            by_kind[kind] = by_kind.get(kind, 0) + 1
            if sev == "ERROR":
                errors += 1
        print(f"\n{r['path']}  ({r['words']} words, bold {r['bold_per_1000']}/1000, "
              f"em-dash {r['emdash_per_1000']}/1000)")
        if not r["findings"]:
            print("  clean")
            continue
        print("  " + ", ".join(f"{k}={v}" for k, v in sorted(by_kind.items())))
        if not report:
            for lineno, sev, kind, msg in r["findings"][:200]:
                loc = f"{r['path']}:{lineno}" if lineno else r["path"]
                print(f"  ::{sev.lower()} file={r['path']},line={lineno}::[{kind}] {loc}: {msg}")

    print(f"\nlint_style: {errors} ERROR across {len(results)} file(s)")
    if report:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
