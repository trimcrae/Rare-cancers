#!/usr/bin/env python3
"""Citation TYPE agreement — when prose calls a paper a review, is it one? ($0, stdlib, offline)

⛔ WHY THIS EXISTS, AND IT IS NOT HYPOTHETICAL (2026-08-26). A partner-stratified metastasis claim was
attributed to "the review literature" and cited four PMCIDs. **One of them was a review.** The other
three were a Japanese national-registry outcome cohort (PMC12398172, n = 171) and two single-patient
case reports (PMC12376927, PMC9131214). Every identifier was real. Every identifier was ANCHORED in a
tracked artifact. `lint_citations` was green throughout — correctly — and the misattribution survived
two full cycles before a blind adversarial seat read the papers. The correction is row A11 of
`fusion-partner/emc-fusion-partner-correction-register.md`.

⭐ WHY THE EXISTING GUARD CANNOT CATCH IT, AND IS NOT DEFICIENT FOR FAILING TO. `lint_citations` asks
whether an identifier has an ORIGIN — does it appear in a tracked fetch product, or is it typed from
memory. Its own baseline text says the quiet part: *"an ANCHORED identifier is not thereby verified
either."* Three of these four were anchored, so origin was never the question. The question was
whether the paper behind the identifier is the KIND of paper the sentence says it is, and that is a
third axis, orthogonal to both provenance and claim strength:

    lint_claims        how strongly is the claim WORDED        (R1-R5)
    lint_citations     does the identifier have an ORIGIN      (anchored / ledgered)
    THIS FILE          is the paper the TYPE prose says it is  (PubMed `article_types`)

⭐ EXTEND OR SIT BESIDE — AND THIS IS BOTH, ON PURPOSE.
  * It SITS BESIDE `lint_citations` as its own module because it answers a different question from a
    different data source (a fetched metadata cache, not the git tree), because its failures have a
    different remedy (fix the sentence, or fetch the row — never "add a ledger entry"), and because
    that file's 40-line header is one incident's narrative that a second incident would dilute.
  * It EXTENDS `lint_citations` at the CALL SITE: `lint_citations.check()` invokes it, so the single
    command `python3 research/manuscripts/lint_citations.py` runs both. That is deliberate and it is
    not laziness. Preflight gate ordinals are derived from the script's `== heading ==` lines by
    `systems_check.check_preflight_gate_list`, and hard-coded in four documents besides. A new
    heading renumbers every gate below it; this guard does not warrant that churn, and a guard bolted
    onto a gate that already runs everywhere is wired more strongly than one given its own heading.
  * It REUSES `lint_citations`' scanning primitives by import rather than by copy — the lesson that
    file's own `extract()` docstring records, after two tests re-implemented `_scan`'s inner loop
    against a data shape they did not own.

⚠ WHAT THIS BINDS, AND IT IS DELIBERATELY NARROW. Only type words that PubMed actually assigns as a
MeSH *publication type*, and only where prose puts the identifier in a direct attributive position
after the type word. Everything the scanner does not bind is listed in `NOT_BOUND` with its reason —
read that list before concluding the guard covers a case, because CLAUDE.md §7's warning is the
governing risk here: a gate that goes red on honest work gets switched off, taking the case it exists
for with it. ⭐ MEASURED ON THE TREE IT WAS WRITTEN AGAINST: **22 type claims found, 22 correct, 0
false positives, and therefore NO BASELINE AND NO AMNESTY LIST** — green on the real corpus from its
first commit, which is the state `lint_citations`' 216-row ledger could not reach. (A first,
proximity-based cut found 58 hits over 26 files, most of them prose ABOUT the incident, paper titles
containing "review of literature", and "clears peer review". The attributive form and the four
rejection rules took that to 18 with nothing honest lost; binding list tails took it to 22.)

⛔ CACHE, NEVER CALL. Preflight is offline and deterministic. The PubMed connector is the FETCHER and
`citation-article-types.json` is what the gate READS; a linter that dialled out would put the commit
loop at the mercy of somebody else's uptime. A missing row is an ERROR that names the fetch, never a
silent pass — `_MISSING_HELP` is that message and `test_a_missing_cache_row_is_an_error` pins it.

⚠ PubMed's terms require attribution and a resolvable DOI link wherever its metadata travels. The
cache carries `doi_url` on every record; this linter prints it in every failure, and anything that
quotes a row must do the same.

Usage:
  python3 research/manuscripts/lint_citation_types.py            # check (runs inside gate 6)
  python3 research/manuscripts/lint_citation_types.py --report   # every claim found, always exits 0
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(HERE, "citation-article-types.json")

sys.path.insert(0, HERE)
import lint_citations as LC  # noqa: E402  (the primitives live there; see the header)

#: ⛔ ONE ROW PER TYPE WORD, AND EVERY ROW'S RIGHT-HAND SIDE IS A REAL MeSH PUBLICATION TYPE.
#: A claim is satisfied when the cached `article_types` contains ANY of the accepted types. The
#: accepted sets are unions rather than single strings because NLM does not index consistently, and
#: a guard that demanded the tightest possible type would manufacture false alarms — the failure
#: direction CLAUDE.md §7 says gets a gate switched off.
#: ⚠ "systematic review" accepts plain `Review` and therefore binds NO MORE TIGHTLY than "review".
#: That is honest rather than lazy: NLM assigns `Systematic Review` unevenly, and pretending the
#: distinction is checkable would be a property asserted in a comment rather than in code.
TYPE_RULES = {
    "systematic review": ("Systematic Review", "Review"),
    "meta-analysis": ("Meta-Analysis",),
    "randomised controlled trial": ("Randomized Controlled Trial",),
    "case report": ("Case Reports",),
    "review": ("Review", "Systematic Review"),
}

#: ⛔ WHAT THIS GUARD DELIBERATELY DOES NOT BIND, WITH THE REASON. Read this before adding a word.
#: An entry here is a decision, not an omission, and each one was checked against the corpus.
NOT_BOUND = {
    "cohort study": "PubMed has NO publication type for a study design. A cohort study is typed "
                    "`Journal Article` like everything else, so `article_types` can neither confirm "
                    "nor deny the claim, and a rule that could only ever pass is a rule that reports "
                    "while measuring nothing.",
    "case series": "Same. NLM types some case series `Case Reports` and most not at all; the "
                   "repository's own prose says '18-case series' of a paper typed `Journal Article`, "
                   "which is not an error in the prose.",
    "trial": "PubMed types the REPORT, not the study. A secondary analysis, a long-term follow-up "
             "and a design paper of a real trial all legitimately carry only `Journal Article`, so "
             "this would fire on honest sentences. `randomised controlled trial` IS bound because "
             "`Randomized Controlled Trial` is assigned to the report of the randomisation itself.",
    "phase N trial": "Same as `trial`. `Clinical Trial, Phase II` exists as a type but is applied to "
                     "the primary report only.",
    "preprint": "A preprint is not in PubMed at all in the general case, so the cache cannot hold it.",
    "retracted": "Not a prose type-claim. `Retracted Publication` IS read from the cache and "
                 "reported (see `_retraction_advisories`), but it is ADVISORY and never sets the "
                 "exit code — whether a retracted paper may still be cited is a content decision "
                 "for a human, not a linter's call.",
}

#: ⛔ THE SCANNER IS ATTRIBUTIVE, NOT PROXIMITY-BASED, AND THAT CHOICE IS THE WHOLE FALSE-POSITIVE
#: BUDGET. A first cut fired on any sentence containing a type word and an identifier: 58 hits over
#: 26 files, most of them prose ABOUT the incident, titles containing "review of literature", and
#: "clears peer review". This form requires the identifier to sit in the attributive slot that
#: FOLLOWS the type word — `review (PMID X)`, `review, PMID X`, `review's full text, PMC X`,
#: `review — Author et al. 2020, **PMID X**` — which is how this repository actually writes them.
_TYPE_ALT = (r"systematic review|meta-?analys[ie]s"
             r"|randomi[sz]ed[- \w]{0,40}?controlled trial|case reports?|review")

#: ⚠ `[^.;!?|]{0,70}` IS TWO GUARANTEES IN A CHARACTER CLASS AND A THIRD IN ITS CEILING.
#: `.;!?` keep the claim inside one sentence. `|` keeps it inside one MARKDOWN TABLE CELL — without
#: it the scanner walked out of `method-watch-autonomy-prior-art.md`'s own incident table, matched
#: the `Review` in one row and the PMCID in the NEXT, and reported the documentation of the bug as
#: the bug. The 70-character ceiling is what stops a match reaching an unrelated identifier two
#: clauses later.
_SCAN = re.compile(
    r"(?P<pre>[\w-]{0,12}\s?)(?P<type>%s)\b(?P<conn>[^.;!?|]{0,70}?)"
    r"(?:PMID[:\s]*(?P<pmid>\d{6,9})|(?P<pmc>PMC\d{6,9})"
    r"|pubmed\.ncbi\.nlm\.nih\.gov/(?P<pmid2>\d{6,9}))" % _TYPE_ALT,
    re.I)

#: ⛔⛔ A TYPE WORD FOLLOWED BY A **LIST** BINDS EVERY IDENTIFIER IN IT, NOT JUST THE FIRST — AND
#: THIS IS THE 2026-08-26 SENTENCE'S OWN SHAPE. That claim named FOUR PMCIDs behind one "the review
#: literature", and three of them were wrong. A scanner that stopped at the first identifier would
#: have checked PMC12398172 and walked past the two case reports, i.e. caught one third of the defect
#: it was written for. ⚠ The continuation is deliberately narrow: only list punctuation, markdown
#: emphasis and the words `and`/`or` may separate the members. A prose word between two identifiers
#: means the second belongs to a new clause, so the run stops there rather than reaching forward.
#: ⚠ AND NO NEWLINE IS IN THE SEPARATOR CLASS, WHICH IS A KNOWN UNDER-BINDING: a list WRAPPED across
#: source lines binds only the members before the wrap. Allowing `\n` would let a run cross a blank
#: line into the next paragraph's first identifier, and under-binding is the safe direction for a
#: gate whose false positives get it switched off. Recorded rather than fixed silently.
_LIST_TAIL = re.compile(
    r"(?:[ \t,;·&*`]|\band\b|\bor\b){1,12}?"   # `.match(text, pos)` anchors it; Python has no \G
    r"(?:PMID[:\s]*(?P<pmid>\d{6,9})|(?P<pmc>PMC\d{6,9}))", re.I)

#: ⛔ THE WORD "REVIEW" IS OVERLOADED IN THIS REPOSITORY AND MOST USES ARE NOT PUBLICATION TYPES.
#: `peer review`, `under review`, `external review`, a `blind`/`adversarial`/`red-team` review round
#: — this repository runs review ROUNDS on its own manuscripts and writes about them constantly.
#: A negation ("not a review", "no review") is excluded for the obvious reason: the sentence is
#: saying what the paper is NOT, and asserting agreement with it would invert the claim.
_BAD_PRE = re.compile(
    r"(?:peer[- ]|under\s+|external\s+|adversarial\s+|blind\s+|red-?team\s+|internal\s+"
    r"|not\s+(?:an?\s+)?|no\s+|nor\s+(?:an?\s+)?)$", re.I)

_MISSING_HELP = (
    "no row for %s in %s. ⛔ THIS IS NOT A PASS — the guard cannot check a claim it has no metadata "
    "for, so it fails. Fetch it in an interactive session (the connector is the fetcher, this gate "
    "is offline): PubMed MCP `convert_article_ids` (id_type='pmcid') if you have only a PMCID, then "
    "`get_article_metadata` with the PMID, and copy `identifiers`, `journal.iso_abbreviation`, "
    "`publication_date.year`, `title` and `article_types` into a record verbatim. The file's "
    "`_how_to_refresh` carries the same steps.")


def load_cache(path=CACHE):
    """(records_by_pmid, index) — the index maps every id form onto its PMID, built at load time.

    ⛔ BUILT, NOT STORED. A second copy of the PMCID->PMID mapping inside the artifact is a second
    place a fact would live (CLAUDE.md §1), and the copy that drifts is always the one nobody reads.
    """
    if not os.path.exists(path):
        return None, None
    doc = json.load(open(path, encoding="utf-8"))
    recs = doc["records"]
    index = {}
    for pmid, rec in recs.items():
        index[("PMID", pmid)] = pmid
        if rec.get("pmcid"):
            index[("PMCID", rec["pmcid"])] = pmid
    return recs, index


def claims(paths=None, root=ROOT):
    """[(file, line, type_word, kind, identifier, quote)] — every TYPE CLAIM in tracked prose.

    A "type claim" is a sentence putting an identifier in the attributive slot after a bound type
    word. Rejected shapes are documented at `_reject`; they are rejected silently because each is a
    construction that is NOT a claim, not a claim this guard is choosing to skip.
    """
    if paths is None:
        paths = [f for f in LC._tracked() if f.endswith(LC.PROSE_SUFFIXES)]
    out = []
    for rel in paths:
        try:
            text = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
        except (OSError, IsADirectoryError):
            continue
        for m in _SCAN.finditer(text):
            if _reject(m):
                continue
            if m.group("pmc"):
                kind, ident = "PMCID", m.group("pmc")
            else:
                kind, ident = "PMID", (m.group("pmid") or m.group("pmid2"))
            word = _normalise_type(m.group("type"))
            if word not in TYPE_RULES:
                continue
            line = text[:m.start("type")].count("\n") + 1
            quote = " ".join(text[m.start("type"):m.end()].split())
            out.append((rel, line, word, kind, ident, quote))
            # ⭐ AND THE REST OF THE LIST, IF THE SENTENCE IS A LIST. See `_LIST_TAIL`.
            pos = m.end()
            while True:
                t = _LIST_TAIL.match(text, pos)
                if not t:
                    break
                if t.group("pmc"):
                    k2, i2 = "PMCID", t.group("pmc")
                else:
                    k2, i2 = "PMID", t.group("pmid")
                out.append((rel, text[:pos].count("\n") + 1, word, k2, i2,
                            quote + " …, " + (i2 if k2 == "PMCID" else "PMID " + i2)))
                pos = t.end()
    return out


def _reject(m):
    """True when a syntactic match is not a type claim. Each rule closed a measured false positive."""
    if _BAD_PRE.search(m.group("pre")):
        return True
    conn = m.group("conn")
    # ⛔ AN UNMATCHED CLOSING BRACKET MEANS THE TYPE WORD WAS INSIDE A PARENTHETICAL THAT CLOSED
    # BEFORE THE IDENTIFIER, so the identifier is not what the type word describes. Measured on
    # `aso-citations-priorart-2026-08-08.md:336`: "(a *KIT* mutation in an EMC case report) and
    # PMID: 25097177" — the case report is PMID 29937513, sitting BEFORE the phrase, and the
    # scanner would otherwise have pinned the type onto the next identifier it could see.
    if conn.count(")") > conn.count("(") or conn.count("]") > conn.count("["):
        return True
    if re.search(r"\n\s*\n", conn):          # a paragraph break is not an apposition
        return True
    return False


def _normalise_type(word):
    w = re.sub(r"\s+", " ", word.strip().lower())
    if re.match(r"^meta-?analys[ie]s$", w):
        return "meta-analysis"
    if re.match(r"^case reports?$", w):
        return "case report"
    if w.startswith("randomi"):
        return "randomised controlled trial"
    return w


def _cite(rec):
    """PubMed attribution + the DOI link its terms require, on every line this file emits."""
    return "PubMed: %s %s (%s %s) types=%s doi=%s" % (
        rec["pmid"], (rec.get("title") or "")[:60], rec.get("journal"), rec.get("year"),
        rec["article_types"], rec.get("doi_url") or "n/a")


def evaluate(found, recs, index):
    """(errors, advisories). An error is a wrong type claim or a claim with no cached metadata."""
    errors, advis, seen = [], [], set()
    for rel, line, word, kind, ident, quote in found:
        pmid = index.get((kind, ident))
        if pmid is None:
            errors.append(("MISSING", rel, line, word, "%s %s" % (kind, ident), quote, None))
            continue
        rec = recs[pmid]
        if not set(TYPE_RULES[word]) & set(rec["article_types"]):
            errors.append(("MISMATCH", rel, line, word, "%s %s" % (kind, ident), quote, rec))
        if "Retracted Publication" in rec["article_types"] and pmid not in seen:
            seen.add(pmid)
            advis.append((rel, line, rec))
    return errors, advis


def check(argv_report=False):
    recs, index = load_cache()
    if recs is None:
        print("::error::no publication-type cache at %s — the guard cannot run, so it fails."
              % os.path.relpath(CACHE, ROOT), file=sys.stderr)
        return 2
    found = claims()
    errors, advis = evaluate(found, recs, index)
    if argv_report:
        for rel, line, word, kind, ident, quote in sorted(found):
            pmid = index.get((kind, ident))
            types = recs[pmid]["article_types"] if pmid else ["<NOT CACHED>"]
            print("%-64s:%-5d %-28s %-14s %s" % (rel[-64:], line, word, "%s %s" % (kind, ident), types))
        print("\n%d type claim(s), %d error(s), %d retraction advisory(ies)"
              % (len(found), len(errors), len(advis)))
        print("According to PubMed; publication types and DOIs are PubMed's, cached in %s"
              % os.path.relpath(CACHE, ROOT))
        return 0
    for why, rel, line, word, ident, quote, rec in errors:
        if why == "MISSING":
            print("::error::%s:%d TYPE CLAIM WITH NO CACHED METADATA — prose calls %s \"a %s\" "
                  "(\"%s\") and there is %s"
                  % (rel, line, ident, word, quote, _MISSING_HELP
                     % (ident, os.path.relpath(CACHE, ROOT))), file=sys.stderr)
        else:
            print("::error::%s:%d WRONG PUBLICATION TYPE — prose calls %s \"a %s\" (\"%s\"), which "
                  "requires one of %s, but PubMed types it %s. Either the sentence names the wrong "
                  "paper or it names the right paper as the wrong kind of thing; both are the "
                  "2026-08-26 defect. [%s]"
                  % (rel, line, ident, word, quote, list(TYPE_RULES[word]),
                     rec["article_types"], _cite(rec)), file=sys.stderr)
    for rel, line, rec in advis:
        print("lint_citation_types: ADVISORY (exit code unaffected) %s:%d cites a paper PubMed "
              "types as a Retracted Publication — [%s]" % (rel, line, _cite(rec)))
    print("lint_citation_types: %d type claim(s) checked against %d cached record(s), %d error(s)%s"
          % (len(found), len(recs), len(errors),
             ", %d retraction advisory(ies)" % len(advis) if advis else ""))
    if errors:
        print("lint_citation_types: %d type claim(s) disagree with PubMed — see errors above"
              % len(errors), file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true", help="list every claim found, always exits 0")
    a = ap.parse_args(argv)
    return check(argv_report=a.report)


if __name__ == "__main__":
    sys.exit(main())
