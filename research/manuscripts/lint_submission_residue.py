#!/usr/bin/env python3
"""Unverified-LLM-output residue in the documents that go OUT. ($0, stdlib, offline)

⛔ WHY THIS EXISTS, AND THE COST IS NOT A RED BUILD. A preprint server now applies a
**one-year submission ban** where there is "incontrovertible evidence" of unverified LLM output, and
the three triggers it names are exactly what an unattended drafting loop produces: **hallucinated
references, residual model meta-comments, unremoved placeholder text.** That sanction attaches to
the author's name and ORCID, not to this repository, and it is not undone by a commit.
⚠ THE POLICY ITSELF IS STILL NOT READ FROM ITS OWN PAGE, AND ITS EXACT WORDING IS DELIBERATELY NOT
QUOTED AS FACT. arxiv.org is refused by this sandbox's egress proxy, so no session here has read the
policy page directly. What IS now corroborated (2026-08-28, WebSearch, at least eight
independent outlets — see `research/method-watch-autonomy-prior-art-2.md` §5 for the list): the
policy was announced May 2026 by Thomas Dietterich, chair of arXiv's CS section — a one-strike,
one-year ban, reinstatement conditioned on a subsequent submission first being accepted at a
reputable peer-reviewed venue, enforced by moderator flag plus section-chair confirmation with an
author appeal right. **What this module implements is the CHECKLIST of the three named triggers.**
See `_POLICY_PROVENANCE` for the grade of every field. Nothing in this file, and nothing it prints,
may be cited as the policy's verbatim text.

WHAT IT CHECKS — two of the three triggers, and only those:

    2. residual model meta-comments   the assistant talking about the TASK rather than about the
                                      science: "As an AI language model", "Here is the revised
                                      section", "Let me know if you'd like", a stray
                                      "Note: I could not verify".
    3. unremoved placeholder text     TODO, TKTK, FIXME, XXX, lorem ipsum, `[insert citation]`,
                                      `<placeholder>`, `[DATE]`, `[Name]`, a bare `[ ]`.

⛔ IT DOES NOT CHECK TRIGGER 1, AND THAT IS A SCOPE DECISION WITH EVIDENCE BEHIND IT.
`lint_citations.py` (gate 6) already asks the one question an offline checker can answer about a
reference — does this identifier ALSO appear in a tracked fetch product — and a second guard over
the same corpus would be an overlapping wall, not new coverage. What `lint_citations` does NOT reach
is recorded in `UNCOVERED_BY_LINT_CITATIONS` below rather than papered over with a weaker check.

★★ THE SCOPE IS THE DESIGN, AND IT IS WHAT KEEPS THE GATE ALIVE. Every word above appears
LEGITIMATELY, and often, in this repository's own working prose: CLAUDE.md, AGENTS.md, the skills,
the ledger and the program docs discuss TODOs, placeholders and model behaviour constantly and
correctly, plans are written as `- [ ]` checklists, and outreach templates carry `[NAME]` on
purpose. Measured 2026-08-28 over the whole tracked corpus, with this file's rules and its
frontmatter exemption both live: **132 of the 398 tracked `.md` files that are NOT submission
documents match at least one rule here, 314 matches in total, and every one of them is honest
prose.** ⚠ *Superseded, retained: "197 of the 398 … 275 matches in total." That pair was measured
with the PROTOTYPE rules — a looser `empty-bracket` lookahead and no frontmatter exemption — so it
counted `canonical_for: []` in the frontmatter of files the shipped gate never reads. It was wrong
the moment the rules were tightened and it read as current for the rest of the session, which is
the defect rule 1 exists to stop, sitting inside the gate that enforces it. The live number is what
`test_the_protection_is_scope_and_not_a_weak_pattern` now re-derives on every run.* A linter that flags true statements gets switched off — `lint_claims.py`'s
founding lesson, and `lint_style.py` paid for it again when a cover letter's "Thank you for
considering this manuscript" was reported as a defect. So this gate reads ONLY the documents that
actually go out, and it derives that set from committed artifacts rather than from a hand-list that
drifts: see `targets()`.

⭐ A LEDGER, NOT A WALL — the shape `lint_citations` established, for the same reason. The corpus
carries real, KNOWN, deliberate placeholders on the day this gate was written: a submission date the
repository cannot supply and must not invent, an author block a draft has not filled. Failing the
build on those would produce a red gate the next session turns off. They are enumerated in
`submission-residue-baseline.json` with a reason each, **and the baseline is the finding** — it names
for the first time exactly which outgoing documents carry an unfilled slot. Anything NEW fails
immediately, which is the case this gate exists for. A baseline row that no longer matches is an
ERROR telling you to delete it, so the list can only shrink honestly.

WHAT IT CANNOT CHECK. Whether a reference is real (that is gate 6's question, partially). Whether a
sentence is machine-written in style rather than in content (that is `lint_style.py`). Whether a
number is right. A clean run means the named trigger shapes are absent from the outgoing documents;
it is not a statement that the prose was verified.

Usage:
  python3 research/manuscripts/lint_submission_residue.py            # check (preflight / CI)
  python3 research/manuscripts/lint_submission_residue.py --report   # every finding, exit 0
  python3 research/manuscripts/lint_submission_residue.py --targets  # the derived corpus, exit 0
  python3 research/manuscripts/lint_submission_residue.py --baseline # first-time ledger, once only
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASELINE = os.path.join(HERE, "submission-residue-baseline.json")

#: ⚠ WRITTEN AS A PROVENANCE RECORD, NOT AS A CITATION, AND THE DISTINCTION IS §7's. The repository's
#: first golden rule forbids writing an identifier or a quotation from recollection; the policy page
#: is unreadable from here, so what is asserted is the GRADE of the evidence and nothing else.
_POLICY_PROVENANCE = {
    "what_is_known": "a one-strike, one-year submission ban for incontrovertible evidence of "
                     "unverified LLM output, with three named triggers: hallucinated references, "
                     "residual model meta-comments, unremoved placeholder text; reinstatement "
                     "requires a subsequent submission first be accepted at a reputable "
                     "peer-reviewed venue; enforced by moderator flag + section-chair confirmation, "
                     "with an author appeal right",
    "grade": "SEARCH — corroborated 2026-08-28 across ≥8 independent secondary outlets (named in "
             "research/method-watch-autonomy-prior-art-2.md §5); still not arXiv's own policy page",
    "recorded_in": "research/method-watch-autonomy-prior-art-2.md §5",
    "policy_wording": "UNKNOWN (verbatim) — only paraphrased secondary reporting has been read; see "
                      "what_is_known for the corroborated substance",
    "policy_date": "SEARCH-grade: announced May 2026",
    "policy_scope": "UNKNOWN — which submission classes it covers has not been read from the "
                    "policy page itself; named official is Thomas Dietterich, chair of arXiv's CS "
                    "section",
    "why_unread": "arxiv.org is refused at this sandbox's egress proxy",
}

#: ⛔ TRIGGER 1 IS GATE 6's, AND THIS IS WHAT GATE 6 STILL DOES NOT REACH (measured 2026-08-28 by
#: reading `lint_citations.py`, not by assuming). Recorded here so the next reader does not build a
#: second overlapping guard, and does not believe trigger 1 is closed.
#:   * A reference with NO machine-readable identifier is invisible. `PATTERNS` matches PMID, PMCID,
#:     DOI, NCT and GEO only, so an author-title-journal-year reference carrying none of those is
#:     never extracted and can be wholly invented. Gate 6 reads no author, title or year.
#:   * ✅ CLOSED 2026-08-28, AUT-PD-057 — arXiv identifiers ARE now matched. This bullet used to
#:     read that `arXiv:2606.27687` appeared in this repository's own prose and anchored nothing,
#:     and that adding the pattern was declined HERE because it would newly flag every existing
#:     arXiv citation at once — a separate, deliberate act with its own baseline rather than a side
#:     effect of this gate. That act has now happened: `lint_citations.PATTERNS` gained an `ARXIV`
#:     entry (three context-anchored forms, no bare-digit form — the bare shape collides with real
#:     DOI fragments), 67 arXiv identifiers surfaced in prose, 54 were already anchored by fetch
#:     products, and the remaining 13 were checked one at a time and ledgered with the date and
#:     channel of the check. The gap is removed from `UNCOVERED_BY_LINT_CITATIONS` below rather
#:     than reworded, which is what that list's guard asks for when a gap genuinely closes.
#:   * An ANCHORED identifier is not a VERIFIED one. The anchor proves a fetch happened for that
#:     identifier; the author list, title, journal and year printed beside it in prose are unread.
#:   * The prose-only identifiers carried as `unverified_at_baseline` in the provenance ledger pass.
#:   * A known-negative control in a fetch corpus anchors itself (documented in `lint_citations`).
#:   * ⛔⛔ AND A FETCH THAT **FAILED** CAN ANCHOR A CITATION — AUT-PD-038, measured 2026-08-27 on a
#:     SUBMISSION MANUSCRIPT's reference list. `fusion-junction-aso-journal-references.md` cited DOI
#:     10.1089/nat.2024.0072 anchored by three records in `research/literature/browser-fetch.json`,
#:     every one a 403 whose stored text was a bot-protection interstitial and whose own note read
#:     "403 persisted under a real browser". Three records saying WE COULD NOT READ THIS satisfied a
#:     gate that exists to establish that somebody did. The anchor test is `the identifier appears in
#:     a tracked .json`, which is a PRESENCE test, and CLAUDE.md §4 names that failure in as many
#:     words: "a populated field is not a measured one… presence is never evidence of provenance".
#:     ⭐ This is the same family as the four gaps above and is the one with a filed fix: make the
#:     anchor predicate read the RECORD's own status rather than the file it sits in.
#: ⭐ THE HONEST STATE: trigger 1 is PARTIALLY covered, by gate 6, for identifier-bearing references
#: only. This gate adds nothing to it, and says so rather than implying the checklist is complete.
UNCOVERED_BY_LINT_CITATIONS = (
    "a reference carrying no PMID/PMCID/DOI/NCT/GEO identifier is never extracted",
    "an anchored identifier's author list, title, journal and year are unchecked",
    "prose-only identifiers baselined as unverified_at_baseline pass",
    "a known-negative control identifier in a fetch corpus anchors itself",
    "a record of a fetch that FAILED still anchors — the predicate is presence in a tracked "
    "json, not a successful retrieval (AUT-PD-038, measured on a submission reference list)",
)


# ─────────────────────────────── the corpus that goes out ───────────────────────────────

def _load(rel, name):
    """Import a committed module by path, so its declarations stay their own single home."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _publication_documents(root):
    """Every manuscript a publication endpoint points at — `systems/graph/publications.json`.

    ⚠ THE SAME MODEL POINTER `lint_claims._publication_documents` READS, and for the same reason: a
    paper cannot be drafted without becoming checked in the same commit, because `systems_check`'s
    [B4] requires the endpoint's `document.file` to exist. A hand-list drifts; this cannot.
    """
    path = os.path.join(root, "systems", "graph", "publications.json")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []
    rows = data if isinstance(data, list) else data.get("publications", [])
    out = []
    for row in rows:
        f = (row.get("document") or {}).get("file")
        if f:
            out.append(f)
    return out


#: Companion roles a submission carries beside its manuscript. The suffixes are the ones
#: `submission_packet._companion` already resolves; the stem-shortening rule is its too.
#: ⛔ COVER LETTERS ARE DELIBERATELY NOT HERE (trimcrae, 2026-08-30: *"Remove all checks on cover
#: letters"*). A letter is written once, by hand, at the moment a paper goes to a publisher — it is
#: never a preprint artifact — so every gate on it was per-paper maintenance bought with nothing.
#: Removing it from the corpus is what retires the per-rule `in_cover_letters` exemption below.
_COMPANION_SUFFIXES = (("-SI.md", "-si.md", "-supplementary-information.md"),)


def targets(root=ROOT):
    """The documents that actually go out, derived from four committed declarations.

    ⛔ NOT A HAND-LIST, AND THAT IS THE POINT. Every source below is an artifact some other part of
    this repository already maintains for its own reasons, so a paper cannot join the outgoing set
    without joining this gate in the same commit:

      1. `systems/graph/publications.json` -> `publications[].document.file` — the model's own
         pointer from a publication endpoint to its manuscript.
      2. `lint_style.TARGETS` — the declared SUBMISSION TEXTS, which is what that list means and
         says it means ("a memo, a plan or a findings note must not be added here").
      3. `build_submission_pdf.PAPERS` — the manuscripts, tables and reference files that are
         actually built into the PDFs that get uploaded.
      4. `submission-metrics.json` -> `rows[].file` and `companion_files` — the papers in submission
         form, with the venue named.

    Plus the SI companion of each, by the directory convention
    `submission_packet._companion` already owns.

    ⚠ A SOURCE THAT CANNOT BE READ IS NOT SILENTLY SKIPPED — it raises, because a gate that quietly
    narrows its own corpus is the "reports while measuring nothing" defect this repository keeps
    paying for. The one exception is `publications.json`, which `systems_check` polices.
    """
    found = set(_publication_documents(root))

    # ⚠ THIS SOURCE IS REDUNDANT TODAY AND IS KEPT ANYWAY — measured, not assumed. Mutation M12
    # (2026-08-28) deleted this line and every test stayed green: the corpus is 39 documents with it
    # and 39 without, because every file in `lint_style.TARGETS` is currently reachable through
    # `publications.json` or the companion scan. That is an EQUIVALENT mutation on today's tree, not
    # an uncovered path — and it stops being equivalent the moment a submission text is added to
    # that list and to no publication endpoint, which is exactly the "half the submission left the
    # linted set and nothing said so" failure `lint_claims.DEFAULT_TARGETS` has recorded three times.
    # The test asserts the INVARIANT (`set(style.TARGETS) <= corpus`) rather than this mechanism.
    style = _load("research/manuscripts/lint_style.py", "_lsr_lint_style")
    found |= set(style.TARGETS)

    builder = _load("research/manuscripts/build_submission_pdf.py", "_lsr_build_submission_pdf")
    for paper in builder.PAPERS.values():
        for key_ in ("manuscript", "tables", "references", "supplementary"):
            if paper.get(key_):
                found.add("research/manuscripts/" + paper[key_])
        for extra in (paper.get("supplementary_for_review") or ()):
            found.add("research/manuscripts/" + extra)

    with open(os.path.join(root, "research/manuscripts/submission-metrics.json"),
              encoding="utf-8") as fh:
        metrics = json.load(fh)
    for row in metrics.get("rows", []):
        found.add("research/manuscripts/" + row["file"])
        for comp in (row.get("companion_files") or []):
            found.add("research/manuscripts/" + comp)

    packet = _load("research/manuscripts/submission_packet.py", "_lsr_submission_packet")
    for rel in sorted(found):
        if not (rel.startswith("research/manuscripts/") and rel.endswith(".md")):
            continue
        stem = rel[len("research/manuscripts/"):-len(".md")]
        for suffixes in _COMPANION_SUFFIXES:
            comp = packet._companion(stem, suffixes)
            if comp:
                found.add("research/manuscripts/" + comp)

    return sorted(rel for rel in found
                  if rel.endswith(".md") and os.path.exists(os.path.join(root, rel)))


# ─────────────────────────────────── the two triggers ───────────────────────────────────

#: (rule id, pattern, one line of why).
#: ⚠ THREE OF THESE ONCE CARRIED A PER-RULE COVER-LETTER EXEMPTION, retired 2026-08-30 with the
#: letters themselves. "Please let me know if you need anything further" and "feel free to contact
#: me" are correspondence conventions, and "I have revised the section" is what a response-to-
#: reviewers letter says; none of the three is a convention in a MANUSCRIPT, where each remains the
#: assistant addressing its requester — so with no letter in the corpus the rules are unconditional.
_RAW_RULES = (
    # ── trigger 2: residual model meta-comments ──────────────────────────────────────────
    ("ai-self-reference",
     r"(?i)\bas an?\s+(?:AI|A\.I\.|artificial intelligence|large language model|"
     r"language model|AI language model|AI assistant)\b",
     "the assistant naming itself"),
    ("ai-self-reference",
     r"(?i)\bI(?:'m|’m| am)\s+an?\s+(?:AI|language model|large language model|AI assistant)\b",
     "the assistant naming itself"),
    ("ai-self-reference",
     r"(?i)\bmy (?:knowledge cut-?off|training data|training cut-?off)\b",
     "the assistant describing its own training"),
    ("assistant-opener",
     r"(?m)^\s*(?:\*\*|_)?(?:Certainly|Sure|Of course|Absolutely|Great question|No problem)[!,]",
     "a chat-reply opener at the start of a line"),
    ("handover",
     r"(?i)\b(?:here|below)\s+(?:is|are|'s|’s)\s+(?:the|a|an|your)\s+"
     r"(?:revised|updated|rewritten|corrected|edited|complete|full|final|new)\b",
     "the assistant handing back an artefact"),
    ("handover",
     r"(?i)\bI(?:'ve|’ve| have)\s+(?:updated|revised|rewritten|corrected|edited)\s+"
     r"the\s+(?:section|paragraph|text|draft|manuscript|document|above|following|passage)\b",
     "the assistant reporting what it did to the document"),
    ("handover", r"(?i)\bwould you like me to\b", "the assistant offering further work"),
    ("handover", r"(?i)\bis there anything else\b", "the assistant offering further work"),
    ("handover", r"(?i)\bI hope (?:this|that) helps\b", "a chat sign-off"),
    ("handover-correspondence", r"(?i)\blet me know if you\b",
     "a chat sign-off; in a manuscript it is the assistant addressing its requester"),
    ("handover-correspondence",
     r"(?i)\bfeel free to (?:ask|let me|reach out|modify|adjust|edit|use)\b",
     "a chat sign-off; in a manuscript it is the assistant addressing its requester"),
    ("assistant-refusal", r"(?i)\bI(?:'m|’m| am) sorry,? but\b",
     "the assistant refusing the task"),
    ("assistant-refusal", r"(?i)\bI apolog(?:ise|ize) for\b",
     "the assistant apologising to its requester"),
    ("assistant-refusal",
     r"(?i)\bI cannot (?:provide|access|browse|generate|create|assist|help|comply|fulfil|fulfill)\b",
     "the assistant refusing the task"),
    ("assistant-note",
     r"(?i)\bNote:\s*I (?:could not|couldn'?t|was unable to|cannot|can'?t|have not|haven'?t)\s+"
     r"(?:verify|confirm|find|locate|access|check)\b",
     "an aside to the requester about what the assistant could not do"),
    # ── trigger 3: unremoved placeholder text ────────────────────────────────────────────
    ("todo-marker", r"\b(?:TODO|FIXME|TKTK|TBD|TBC)\b", "an unresolved work marker"),
    ("todo-marker", r"\bXXX+\b", "an unresolved work marker"),
    ("lorem", r"(?i)\blorem ipsum\b", "filler text"),
    ("bracket-placeholder",
     r"(?i)\[\s*(?:insert|placeholder|citation needed|citation-needed|todo|tbd|name|city|country|"
     r"affiliation|email|address|editor|orcid|date|year|title|journal|volume|pages)\b[^\]]{0,40}\]"
     r"(?![\(\[])",
     "an unfilled bracketed slot"),
    # ⛔ THE QUALIFIER-PLUS-SLOT FORM, AND THE `\s` BEFORE THE ALTERNATION IS LOAD-BEARING. This
    # rule catches `[ARCHIVE DOI]` and `[PREPRINT DOI]` — the exact placeholders
    # `aso_archive_manifest.py` was written because the submission manuscript carried. Without the
    # required space it also matched `[PMID 17515897]` and every other bracketed citation tag in the
    # degrader SI: five false alarms on real, anchored references, measured before this line.
    ("uppercase-slot",
     r"\[[A-Z][A-Z ]{0,30}\s(?:DOI|DATE|NAME|ORCID|TITLE|CITY|COUNTRY|AFFILIATION|EMAIL|ADDRESS|"
     r"EDITOR|YEAR|TBD)\](?![\(\[])",
     "an unfilled bracketed slot in the repository's own shouting-caps form"),
    ("angle-placeholder",
     r"(?i)<\s*(?:placeholder|insert|todo|name|value|date|year|author)\b[^>]{0,40}>",
     "an unfilled angle-bracket slot"),
    ("ref-placeholder", r"\bREF\?|\[REF\]|\[CITATION\]",
     "a reference the author meant to come back to"),
    ("citation-needed", r"(?i)\bcitation needed\b",
     "a reference the author meant to come back to"),
    ("author-year-template", r"\(YEAR\)|\bAuthors? et al\.\s*\(?YEAR\)?",
     "a citation template that was never filled in"),
    # ⚠ THE TWO LOOKAROUNDS ARE NOT SYMMETRIC, AND THE FIRST DRAFT'S `(?!\S)` MISSED THE COMMONEST
    # CASE: an empty bracket at the end of a sentence — "detected in 4/9 tumours []." — is followed
    # by a full stop, so a "must be whitespace" lookahead refused the one place a dropped citation
    # actually lands. Left: not a word character or a closing bracket, so `x[]` in code is not a
    # finding. Right: not a word character or an opening bracket, so a markdown `[]()` link and a
    # reference-style `[][1]` are not findings either.
    ("empty-bracket", r"(?<![\w\]\)])\[\s*\](?![\w\(\[])",
     "an empty bracket where something belonged"),
    ("template-marker", r"\{\{[^}\n]{0,60}\}\}", "an unrendered template marker"),
)

RULES = tuple((rid, re.compile(pat), why) for rid, pat, why in _RAW_RULES)


def _body(text):
    """`text` with any YAML frontmatter blanked, LINE COUNT PRESERVED.

    ⛔ FRONTMATTER IS REPOSITORY METADATA AND IT DOES NOT GO OUT — the PDF builders strip it, and
    `lint_style.py` exempts it for the same reason. Measured before this exemption existed: the
    `canonical_for: []` and `related: [DOC-...]` keys that the manuscripts' frontmatter carries
    produced 34 findings across 39 documents, none of them prose, which is precisely the cry-wolf
    volume that gets a gate switched off.
    ⚠ BLANKED, NOT REMOVED. A finding's value is the file and line a reader can open; re-numbering
    the body would send them to the wrong line at the moment the gate has failed.
    """
    if not text.startswith("---"):
        return text
    m = re.match(r"^---\r?\n.*?\r?\n---[ \t]*\r?\n", text, re.S)
    if not m:
        return text
    head = text[:m.end()]
    return "\n" * head.count("\n") + text[m.end():]


def scan_text(text, rel=""):
    """[(rule id, line, matched text, the whole line)] for one document's body."""
    body = _body(text)
    lines = text.splitlines()
    out = []
    for rid, pat, _why in RULES:
        for m in pat.finditer(body):
            n = body.count("\n", 0, m.start()) + 1
            quote = lines[n - 1].strip() if n - 1 < len(lines) else ""
            out.append((rid, n, m.group(0).strip(), quote))
    return sorted(out, key=lambda f: (f[1], f[0]))


def findings(paths=None, root=ROOT):
    """[(rel, rule id, line, matched text, line text)] over the outgoing corpus."""
    out = []
    for rel in (targets(root) if paths is None else paths):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue
        for rid, line, hit, quote in scan_text(text, rel):
            out.append((rel, rid, line, hit, quote))
    return out


# ────────────────────────────────────── the ledger ──────────────────────────────────────

def key(rel, rule_id, hit):
    """A baseline row's identity — file, rule and matched TEXT, never the line number.

    ⛔ NOT THE LINE. A baseline keyed to a line number is amnesty for whatever drifts onto that line;
    keyed to the text, a row covers exactly the string it was written for and nothing else, and an
    edit that moves a paragraph does not turn the gate red.
    """
    return "%s|%s|%s" % (rel, rule_id, " ".join(str(hit).split()))


def load_baseline(path=BASELINE):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _why_for(rule_id):
    return next(w for rid, _p, w in RULES if rid == rule_id)


def check(report=False, root=ROOT, baseline_path=BASELINE, paths=None):
    #: ⚠ `paths` EXISTS FOR THE TESTS AND FOR NOTHING ELSE, and it is a real corpus rather than a
    #: mock: a test that plants a trigger must run the gate END TO END on a copy, because a scanner
    #: that finds the residue and a gate that then exits 0 are the same defect this repository keeps
    #: paying for. Preflight and CI never pass it, so the live corpus is always the derived one.
    corpus = targets(root) if paths is None else list(paths)
    found = findings(paths=corpus, root=root)
    doc = load_baseline(baseline_path)
    if doc is None:
        # ⚠ --report SURVEYS, so it must run before a baseline exists; the CHECK must not.
        if not report:
            print("::error::no submission-residue baseline — run --baseline once to create %s"
                  % os.path.relpath(baseline_path, root), file=sys.stderr)
            return 2
        doc = {"entries": []}
    known = {e["key"] for e in doc["entries"]}
    seen = set()
    new = []
    for rel, rid, line, hit, quote in found:
        k = key(rel, rid, hit)
        seen.add(k)
        if k not in known:
            new.append((rel, rid, line, hit, quote))
    # ⛔ A ROW THAT NO LONGER MATCHES IS AN ERROR, NOT A SHRUG. An unpruned row is standing
    # permission for the placeholder to come back: re-introduce the same string in the same file and
    # it is baselined again, silently. The remedy is one deleted line and the message says so.
    stale = [e for e in doc["entries"] if e["key"] not in seen]

    if report:
        for rel, rid, line, hit, quote in found:
            mark = " " if key(rel, rid, hit) in known else "*"
            print("%s %-58s:%-5d %-22s %s" % (mark, rel[-58:], line, rid, hit[:44]))
        print("\n%d finding(s) in %d outgoing document(s); %d baselined, %d NEW (*), %d stale row(s)"
              % (len(found), len(corpus), len(found) - len(new), len(new), len(stale)))
        return 0

    for rel, rid, line, hit, quote in new:
        print("::error::%s:%d UNVERIFIED-OUTPUT RESIDUE (%s) — %r is %s. This is one of the shapes "
              "a preprint server bans submitters over, and the sanction attaches to the author, not "
              "to this repository. Fix the document; do not baseline it. (line: %s)"
              % (rel, line, rid, hit, _why_for(rid), quote[:120]), file=sys.stderr)
    for e in stale:
        print("::error::%s BASELINE ROW IS RESOLVED — %r no longer appears under rule %s. Delete "
              "the row from %s; a row kept past its finding is standing permission for the same "
              "string to return unnoticed."
              % (e["file"], e["text"], e["rule"], os.path.relpath(baseline_path, root)),
              file=sys.stderr)

    print("lint_submission_residue: %d outgoing document(s), %d finding(s), %d baselined, "
          "%d new, %d stale baseline row(s)"
          % (len(corpus), len(found), len(found) - len(new), len(new), len(stale)))
    print("lint_submission_residue: hallucinated references are gate 6's trigger and remain "
          "PARTIAL — %d named gaps in UNCOVERED_BY_LINT_CITATIONS."
          % len(UNCOVERED_BY_LINT_CITATIONS))
    return 1 if (new or stale) else 0


def write_baseline(root=ROOT, path=BASELINE):
    """First-time ledger write. Refuses once the ledger exists — growing it is a deliberate act.

    ⚠ THE SAME REFUSAL `lint_citations --baseline` CARRIES, for the same reason: a self-service
    baseline is an off-switch with a JSON file in front of it.
    """
    if os.path.exists(path):
        print("::error::%s already exists — a baseline is written once. Adding a row is a hand edit "
              "with a `why`, and it records that a human decided that slot may stand."
              % os.path.relpath(path, root), file=sys.stderr)
        return 2
    entries = [{"key": key(rel, rid, hit), "file": rel, "rule": rid, "text": hit,
                "line_when_written": line, "why": "UNREVIEWED — written by --baseline"}
               for rel, rid, line, hit, _q in findings(root=root)]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"entries": entries}, fh, indent=1)
        fh.write("\n")
    print("wrote %d row(s) to %s" % (len(entries), os.path.relpath(path, root)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true", help="every finding, always exits 0")
    ap.add_argument("--targets", action="store_true", help="the derived outgoing corpus, exits 0")
    ap.add_argument("--baseline", action="store_true", help="first-time ledger write, once only")
    a = ap.parse_args(argv)
    if a.targets:
        for rel in targets():
            print(rel)
        return 0
    if a.baseline:
        return write_baseline()
    return check(report=a.report)


if __name__ == "__main__":
    sys.exit(main())
