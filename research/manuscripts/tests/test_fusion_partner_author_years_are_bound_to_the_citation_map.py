"""⛔ CITATION YEARS IN THE FUSION-PARTNER SYNTHESIS WERE UNBOUND, AND ONE SENTENCE'S COVERAGE RESTED
ENTIRELY ON ITS §-REFERENCE (AUT-PD-133).

★ MEASURED 2026-08-28 (CYC-0069) by ablation: perturbing *"Huang 2023"* to *"Huang 2027"* in
**"Neither found the partner to carry the prognosis."** turned NO guard red. That sentence stopped being
BLIND only because AUT-PD-105 bound its §-references in the same cycle, and the ablation harness stops at
the first trip — so the gate was green over an unwatched year, and the row was filed rather than left for
the gate's silence to imply coverage.

⚠ WHY NOTHING ELSE SEES IT, AND IT IS THE ORTHOGONALITY CLAUDE.md §7 RECORDS. `lint_claims` reads claim
STRENGTH; a wrong year is a claim of the same strength about a different paper. `lint_citations` reads
identifier PROVENANCE — does this PMID appear in some tracked JSON — and an author-year mention carries no
identifier for it to anchor. The sibling relations guard owns a `_NAMED_SERIES` regex that does read
author-year pairs, but only inside the superlative-comparison sentences it decides; a year drifting
anywhere else in the document passes every instrument this repository has.

⭐ THE BINDING SOURCE IS AN ARTIFACT, NOT THE REFERENCE LIST. `emc-fusion-partner-pooling.json` →
`citations` records each source's `authors`, `year` and `pmid` as one machine-readable row, and every
prose author-year mention is a restatement of one of those rows. Checking the prose against the artifact
is the same shape as the sibling guards that check its numbers, and it means a corrected year has ONE home
(CLAUDE.md §1) instead of one per document.

⛔ THE DOCUMENT SET IS DERIVED, NOT TYPED. Every `.md` beside the artifact is scanned, so a fourth prose
document is covered the day it lands rather than the day somebody remembers to add it here — the failure
mode a typed member list has every time in this repository.

⚠ WHAT THIS DELIBERATELY DOES NOT DO: decide whether a citation is APT. A correct year on the wrong paper,
or the right paper cited for a claim it does not make, is invisible here and is a reading job. This guard
answers one question — does the prose name the year the artifact records — and says nothing else.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import unicodedata

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
PARTNER = os.path.join(MANUSCRIPTS, "fusion-partner")
ARTIFACT = os.path.join(PARTNER, "emc-fusion-partner-pooling.json")

#: An author-year mention as these documents write it: `Huang 2023`, `Llombart-Bosch 2022`.
NAMED = re.compile(r"\b([A-Z][a-zA-Z]+(?:-[A-Z][a-zA-Z]+)?)\s+((?:19|20)\d{2})\b")

#: The same, followed closely by the identifier it claims — `Huang 2023, PMID 36948401`. Bounded to one
#: sentence-free run so it cannot reach across a full stop and pair a surname with a stranger's PMID.
NAMED_WITH_PMID = re.compile(
    r"\b([A-Z][a-zA-Z]+(?:-[A-Z][a-zA-Z]+)?)\s+((?:19|20)\d{2})\b[^.\n]{0,60}?PMID\s+(\d+)")


def _fold(s):
    """Drop diacritics so `Sjögren 2003` in the prose meets `Sjogren H, …` in the artifact.

    ⚠ FOLDING IS NOT NORMALISING THE CLAIM. Only the surname's typography is folded; the year and the
    PMID are compared as written, because those are the facts under test.
    """
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


@pytest.fixture(scope="module")
def recorded():
    """surname -> the citation rows the artifact holds for it, keyed off `authors`, not `short`.

    ⛔ `authors` RATHER THAN `short`, deliberately. `short` already contains the author-year string the
    prose uses (`"Huang 2023"`), so deriving the expectation from it would compare the prose against a
    copy of itself and pass however far both had drifted from the record. `authors` is the fetched author
    string and `year` is a separate field, so the surname and the year come from two places that a single
    edit cannot move together.
    """
    with open(ARTIFACT, encoding="utf-8") as fh:
        art = json.load(fh)
    rows = collections.defaultdict(list)
    for cid, c in art["citations"].items():
        assert c.get("authors") and c.get("year"), (
            f"citation {cid} in {os.path.relpath(ARTIFACT, MANUSCRIPTS)} records no author or no year, so "
            f"no prose mention of it can be decided against the artifact.")
        rows[_fold(c["authors"].split()[0]).rstrip(",")].append(c)
    assert rows, "the citation map is empty — this guard would then check nothing and still pass"
    return dict(rows)


@pytest.fixture(scope="module")
def prose():
    """Every prose document beside the artifact, DERIVED from the directory rather than listed."""
    docs = {os.path.basename(p): _fold(open(p, encoding="utf-8").read())
            for p in sorted(glob.glob(os.path.join(PARTNER, "*.md")))}
    assert docs, f"no prose documents found in {PARTNER} — the derivation, not the corpus, is what broke"
    return docs


@pytest.mark.committed_artifact
def test_the_corpus_and_the_citation_map_are_both_covered_whole(prose, recorded):
    """⛔ A GUARD THAT NARROWS ITS OWN SCOPE CANNOT BE CAUGHT BY ITS OWN RESULT.

    Both halves of this file's coverage are re-derived here by a DIFFERENT implementation from the one
    the fixtures use, because asserting a derivation against itself proves nothing:

      * the document corpus, against `git ls-files` rather than a filesystem glob — a corpus quietly
        narrowed to one file would leave every other document unchecked and every assertion green;
      * the citation rows, against the artifact's own `citations` count — a `recorded` built from only
        the rows carrying a PMID would silently stop watching the three congress-abstract and review
        sources, which are exactly the rows with the least other machinery around them.
    """
    import subprocess
    root = os.path.dirname(os.path.dirname(MANUSCRIPTS))
    r = subprocess.run(["git", "-C", root, "ls-files", "--", os.path.relpath(PARTNER, root)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    tracked = {os.path.basename(p) for p in r.stdout.split("\n") if p.endswith(".md")}
    assert tracked, "git lists no tracked .md beside the artifact — the second derivation is broken"
    assert tracked <= set(prose), (
        "these tracked prose documents are not being scanned, so a year could drift in them without "
        "anything going red: " + ", ".join(sorted(tracked - set(prose)))
    )

    # ⭐ AND THE FOLD'S LIVE CONTRIBUTION IS MEASURED ON THE REAL CORPUS, not asserted as a constant. If
    # the tracked prose names any accented surname beside a year — five such mentions on the trunk of
    # 2026-09-01, `Sjögren 2003` and `Klubíčková 2022` — then folding must reach mentions the raw text
    # hides. The check disables itself if the corpus one day has none, which is the honest behaviour: it
    # asserts what is there rather than what somebody expected to be there.
    raw = "\n".join(open(os.path.join(PARTNER, n), encoding="utf-8").read() for n in sorted(prose))
    accented = re.search(r"\b[A-Z][a-zA-Z]*[^\x00-\x7F][a-zA-Z\u00c0-\u024f]*\s+(?:19|20)\d{2}\b", raw)
    if accented:
        gained = set(NAMED.findall(_fold(raw))) - set(NAMED.findall(raw))
        assert gained, (
            f"the prose names an accented source beside a year ({accented.group(0)!r}) and folding "
            f"diacritics reaches no mention the raw text does not, so those mentions are unchecked."
        )

    art = json.load(open(ARTIFACT, encoding="utf-8"))
    assert sum(len(v) for v in recorded.values()) == len(art["citations"]), (
        f"the surname index holds {sum(len(v) for v in recorded.values())} of the artifact's "
        f"{len(art['citations'])} citation rows. The rows it dropped are sources no prose mention of "
        f"them can be checked against."
    )


def _mismatches(text, recorded):
    """[(surname, year_written, years_recorded, context)] for every mention the artifact contradicts."""
    out = []
    for m in NAMED.finditer(text):
        surname, year = m.group(1), int(m.group(2))
        if surname not in recorded:
            continue                      # not a source this synthesis cites; not this guard's business
        years = {int(c["year"]) for c in recorded[surname]}
        if year not in years:
            out.append((surname, year, sorted(years),
                        text[max(0, m.start() - 70):m.end() + 25].replace("\n", " ")))
    return out


@pytest.mark.committed_artifact
def test_every_author_year_in_the_prose_is_the_year_the_citation_map_records(prose, recorded):
    """⛔ THE ROW'S OWN ABLATION, AS A STANDING GUARD: `Huang 2023` -> `Huang 2027` must go red."""
    bad = []
    for name, text in prose.items():
        for surname, wrote, years, ctx in _mismatches(text, recorded):
            bad.append(f"{name}: writes `{surname} {wrote}`; "
                       f"{os.path.relpath(ARTIFACT, MANUSCRIPTS)} records {surname} at {years}.\n"
                       f"    …{ctx}…")
    assert not bad, (
        "%d author-year mention(s) name a year the citation map does not record:\n  " % len(bad)
        + "\n  ".join(bad)
        + "\n⛔ Fix the PROSE if the artifact is right, and the ARTIFACT if the source is. Never both — "
          "the year has one home."
    )


@pytest.mark.committed_artifact
def test_an_identifier_written_beside_an_author_year_is_that_source_s_identifier(prose, recorded):
    """⛔ THE YEAR AND THE PMID MUST AGREE ABOUT WHICH PAPER IS MEANT.

    `Huang 2023, PMID 36948401` welds a human-readable label to a machine-readable one, and the two can
    drift apart in either direction: a corrected year beside an uncorrected identifier reads as a
    different paper, and a copied identifier beside a correct year cites a stranger. Both are provenance
    defects and neither carries a claim for `lint_claims` to weigh.
    """
    bad = []
    for name, text in prose.items():
        for m in NAMED_WITH_PMID.finditer(text):
            surname, year, pmid = m.group(1), int(m.group(2)), m.group(3)
            rows = [c for c in recorded.get(surname, []) if int(c["year"]) == year]
            if not rows:
                continue                  # the year half is this file's other test; do not double-report
            known = {c.get("pmid") for c in rows if c.get("pmid")}
            if known and pmid not in known:
                bad.append(f"{name}: writes `{surname} {year} … PMID {pmid}`; the citation map gives "
                           f"{surname} {year} the PMID(s) {sorted(known)}.")
    assert not bad, "\n  ".join(["%d identifier(s) contradict the year beside them:" % len(bad)] + bad)


@pytest.mark.committed_artifact
def test_the_binding_actually_reaches_the_prose(prose, recorded):
    """⭐ THE GUARD ON THE GUARD, AND ITS BOUND IS DERIVED FROM THE ARTIFACT.

    Both tests above pass trivially if the surname derivation stops matching anything — a change to
    `authors`' shape, a rename of the artifact's `citations` key, or a diacritic the fold no longer
    removes would make `recorded` and the prose disjoint and leave the suite green while checking zero
    mentions. That is the failure `line_citations.py`'s `>= 10` floor was measured to permit on
    2026-09-01, in the same week, and a typed floor here would age the same way.

    ⛔ SO THE BOUND IS NOT A NUMBER. Every surname the artifact records for a source the synthesis
    actually POOLS must be found in the prose, because a pooled cohort that is never named in the text is
    a different defect and the sibling guards would already be red. The count moves with the artifact.
    """
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    pooled = set(art["analyses"]["B_outcome_by_partner"]["pooled_cohorts"]) | \
        set(art["analyses"]["C_partner_prevalence"]["cohorts_pooled"])
    assert pooled, "the artifact pools nothing, so this guard's bound is empty"

    all_text = "\n".join(prose.values())
    seen = {(s, int(y)) for s, y in NAMED.findall(all_text)}
    missing = []
    for surname, rows in recorded.items():
        for c in rows:
            cid = f"{surname.lower()}-{c['year']}"
            if not any(p.startswith(cid) for p in pooled):
                continue
            if (surname, int(c["year"])) not in seen:
                missing.append(f"{surname} {c['year']} ({cid})")
    assert not missing, (
        "the citation map pools these cohorts and the prose never names any of them by author-year, so "
        "the binding above is checking nothing for them: " + ", ".join(sorted(missing))
    )


def test_a_drifted_year_and_a_swapped_identifier_are_both_caught():
    """⭐⭐ THE POSITIVE CONTROL, ON SYNTHETIC TEXT.

    The three tests above are assertions about committed documents: they say what the tree looks like
    today, not that the checker still works. This one breaks each fact the checker is supposed to hold and
    requires it to notice, so a resolver that has quietly stopped resolving fails HERE, where the message
    names the mechanism, instead of passing everywhere in silence.
    """
    recorded = {"Huang": [{"authors": "Huang SC, Lee JC,", "year": 2023, "pmid": "36948401"}]}
    assert not _mismatches("as Huang 2023 reports, the partner matters", recorded)
    drift = _mismatches("as Huang 2027 reports, the partner matters", recorded)
    assert drift and drift[0][:3] == ("Huang", 2027, [2023]), drift

    m = NAMED_WITH_PMID.search("Huang 2023, PMID 36948401, whose Table 1")
    assert m and m.group(3) == "36948401", "the identifier pattern no longer reads an adjacent PMID"
    assert NAMED_WITH_PMID.search("Huang 2023 is a series. PMID 99999999 belongs elsewhere") is None, (
        "the identifier pattern reached across a full stop and paired a surname with a stranger's PMID"
    )
    assert not _mismatches("as Sjogren 2003 reports", {"Sjogren": [{"year": 2003}]})

    # ⛔ ASSERTED ON `_fold` ITSELF, NOT THROUGH `_mismatches`. The first version of this line ran
    # `_mismatches(_fold("as Sjögren 2003 reports"), …)` and expected no mismatch — which an IDENTITY
    # `_fold` also satisfies, because `NAMED`'s `[A-Z][a-zA-Z]+` never matches `Sjögren` at all and a
    # mention nobody sees cannot mismatch. Mutation N3, 2026-09-01: removing the fold left this green.
    folded = _fold("as Sjögren 2003 reports")
    m = NAMED.search(folded)
    assert m and (m.group(1), m.group(2)) == ("Sjogren", "2003"), (
        "the diacritic fold stopped working, so an accented surname no longer matches `NAMED` and every "
        "mention of one drops out of the check silently — the shape of an absent reading read as a "
        "reading of absence."
    )
