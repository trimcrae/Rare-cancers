"""A claim is a QUANTITY and a RELATION. Every other guard reads the quantity. This reads the relation.

⛔⛔ THE MEASUREMENT THAT FORCED THIS (round 16 seat 3, 2026-08-22). Seventy-three predicate
inversions were applied one at a time to the journal article, each followed by the full regeneration
chain and BOTH PDF styles rebuilt, then twelve linter/generator gates and all fifty-eight test files.

    66 of the 73 survived every gate.
    44 of those 66 sit in sentences `claim_coverage.py` calls COVERED.

That second line is the important one, and it is why this file exists rather than another census
tweak: "covered" was measuring whether a NUMBER in the sentence was watched. The verb next to it was
not, anywhere. Three of the survivors are unshippable:

  · the paper's central negative inverts at ALL FOUR of its prose homes — the pins and
    `test_journal_article_numbers.py` anchor on `transcript(s)` and restart at `pair`, so inserting
    "fail to" in the gap between them satisfies both, and it renders in the built 6-page PDF;
  · every operative statement in Declarations inverts, one of them by DELETING A SINGLE WORD and
    staying word-count neutral: "Research use only, and **for** administration to any person or
    animal" — an unsafe instruction, shipped, with the page footer three lines below still saying
    the opposite because both come from the same builder;
  · the two named reagents' clearance claims invert against their own CSV rows ("neither pairs" ->
    "both pair"), which is the difference between a reagent a lab may order and one it may not.

★ THE SHAPE OF THE GUARD. Each row is a claim SITE (`span`), the relation its artifact computes
(`require`), and that relation's inverse (`forbid`). Both halves are asserted separately, because
"the right verb is present" and "no wrong verb is present" fail differently — a sentence reading
"pair or spare" satisfies the first. `span` is checked at EVERY occurrence, since the central
negative has four prose homes and round 15 shipped a fix to one of a pair more than once.

⚠ AND THE TABLE IS MUTATION-TESTED AGAINST ITSELF. A row whose `span` stops matching after a
rewording has silently stopped guarding — the exact defect this file is about — so a missing site is
an ERROR, never a skip, and every `forbid` must still match the inversion it names.
"""
from __future__ import annotations

import io
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ASO = os.path.join(os.path.dirname(HERE), "aso")
ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")

#: (id, span, require, forbid, decided_by, an inversion the `forbid` half MUST catch)
POLARITY = [
    ("liability-predicate",
     r"\b87\b[^.]{0,140}catalytic gap[^.]{0,160}\.",
     r"\bpair\b|\bpairs\b|\bpairing\b|\bpaired\b",
     r"\bfails? to pair\b|\bspares?\b|\bfrom pairing\b|\bunpaired\b|\bavoids?\b|\bmiss(?:es)?\b|\bclears?\b",
     "aso-parent-gap-pairing.json:corpus.n_with_parent_duplex_through_gap and the CSV column "
     "`pairs_a_wild_type_parent_through_the_gap`",
     "87 of 190 designs fail to pair a wild-type parent through the catalytic gap."),
    ("liable-definition",
     r"A design is\s+liable where[^.]{0,200}\.",
     r"liable where a wild-type parent pairs",
     r"liable where no\b|liable where none\b|fails? to pair",
     "aso-parent-null.json:method.min_duplex_bp and the same CSV column",
     "A design is liable where no wild-type parent pairs the whole gap."),
    ("precursor-class",
     r"designs carry a sense-strand near-match in parent precursor RNA[^.]{0,80}\.",
     r"pairing the gap in full",
     r"leaving the gap unpaired|not pairing the gap",
     "the precursor-RNA screen record",
     "designs carry a sense-strand near-match in parent precursor RNA, leaving the gap unpaired."),
    ("named-reagents-clear-the-cut",
     r"top gap-level margin of three:[^.]{0,260}\.",
     r"neither pairs a wild-type parent through the gap",
     r"both pair a wild-type parent through the gap",
     "the CSV rows for the two named sequences, "
     "`pairs_a_wild_type_parent_through_the_gap` = no for each",
     "top gap-level margin of three: both pair a wild-type parent through the gap."),
    ("research-use-only",
     r"\*\*Research use only[^*]{0,90}\*\*",
     r"and not for administration to any person or animal",
     r"and for administration to any person or animal",
     "the constant build_submission_pdf.py stamps into every page footer",
     "**Research use only, and for administration to any person or animal.**"),
    ("order-after-sequencing",
     r"Order from the canonical record[^#]{0,320}?sequencing\.",
     r"\bnot until the breakpoint has been established\b",
     r"\beven before the breakpoint\b|\bwithout waiting\b",
     "the ordering rule test_every_ordering_route_carries_the_same_verdict.py enforces elsewhere",
     "Order from the canonical record even before the breakpoint is known, before sequencing."),
    ("ethics-not-applicable",
     r"Ethics approval, consent to participate[^#]{0,220}?involved\.",
     r"No human\s+subjects, human material or animals were involved",
     r"(?<!No )Human\s+subjects, human material and animals were involved",
     "the repository's no-wet-lab invariant",
     "Ethics approval, consent to participate. Human subjects, human material and animals "
     "were involved."),
    ("competing-interests",
     r"\*\*Competing interests\.\*\*[^#]{0,320}",
     r"declares no financial competing interests",
     r"declares financial competing interests",
     "the cover letter: 'I received no funding and have no financial competing interests'",
     "**Competing interests.** The author declares financial competing interests."),
    ("ai-use",
     r"\*\*Use of artificial intelligence\.\*\*[^#]{0,140}",
     r"A large language model \(Claude, Anthropic\) was used",
     r"No large language model was used",
     "the repository's own AI-use record",
     "**Use of artificial intelligence.** No large language model was used."),
    ("deposit-not-yet-posted",
     r"inside that deposit;[^#]{0,140}",
     r"prepared for bioRxiv and not yet\s+posted",
     r"posted on bioRxiv already",
     "deposit-state.json:pending",
     "inside that deposit; it was posted on bioRxiv already."),
    ("coverage-is-not-a-measurement",
     r"That prices which published junctions[^.]{0,220}\.",
     r"it is not a coverage measurement, no patient having been screened",
     r"it is a coverage measurement, patients having been screened",
     "fusion-junction-aso-reagent-coverage.json:_what_this_is_not[0]",
     "That prices which published junctions are modelled: it is a coverage measurement, "
     "patients having been screened."),
    ("no-prior-nr4a3-design",
     r"(?:No|Such)\s+(?:such design|a design) is reported[^.]{0,180}\.",
     r"No\s+such design is reported",
     r"Such\s+a design is reported",
     "fusion-junction-aso-priorart-evidence.json, the what-this-does-not-establish field",
     "Such a design is reported in the prior literature."),
    ("backbone-is-phosphorothioate",
     r"Both reagents are phospho[a-z]+",
     r"phosphorothioate",
     r"phosphodiester",
     "the sequences CSV header: 'every internucleoside linkage is a phosphorothioate'",
     "Both reagents are phosphodiester throughout."),
    ("acceptor-reagents-not-interchangeable",
     r"A reagent selected for one acceptor is[^.]{0,60}\.",
     r"is\s+not valid for the other",
     r"is\s+valid for the other",
     "the CSV: the exon-2 sequences differ from the exon-3 sequences",
     "A reagent selected for one acceptor is valid for the other."),
    # ⛔⛔ A CLINICAL FACT UNDER A REAL PMID INVERTS AS FREELY AS ANY OTHER PREDICATE (round 16
    # seat 3). "responds poorly" -> "responds well" states the opposite of the cited source while
    # the citation, the superscript and the PMID anchor all stay put — and CLAUDE.md §7 is explicit
    # that claim STRENGTH is orthogonal to citation PROVENANCE, so a hedge-checking linter cannot
    # see it. This is the one clinical claim the condensed paper makes in its own voice.
    # ⚠ `decided_by` here is a CITATION, not an artifact, and that is the honest description: the
    # guard binds the polarity to the source, and the source is what makes the claim checkable by a
    # reader. It cannot verify the source says it; nothing available here can.
    # ⚠ `\s+` between every word: the sentence wraps mid-phrase in the source ("cytotoxic" ends
    # line 68, "chemotherapy" opens line 69), and a literal-space pattern reports the claim missing
    # when it is simply typeset over two lines.
    ("chemotherapy-response",
     r"The\s+disease\s+responds[^.]{0,140}chemotherapy",
     r"responds\s+poorly\s+to\s+conventional\s+cytotoxic\s+chemotherapy",
     r"responds\s+well\b|responds\s+favourably\b|is\s+responsive\s+to\b|responds\s+strongly\b",
     "PMID:41055792, the source cited at that sentence",
     "The disease responds well to conventional cytotoxic chemotherapy"),
    ("margin-is-the-shorter-side",
     r"gap-level margin is the count of junction-unique bases[^.]{0,90}\.",
     r"on\s+the shorter side of the breakpoint",
     r"on\s+the longer side of the breakpoint",
     "the CSV column gap_level_margin, computed on the shorter side",
     "gap-level margin is the count of junction-unique bases on the longer side of the "
     "breakpoint."),
]


def _article():
    """The article with its line wrapping collapsed.

    ⛔ EVERY SPAN BELOW IS WRITTEN WITH ORDINARY SPACES, AND THE SOURCE WRAPS MID-PHRASE. The
    chemotherapy sentence breaks between "cytotoxic" and "chemotherapy"; without this, that row
    reported its claim MISSING on a correct paper, and a reflow of any other paragraph would do the
    same to its row. A missing span is an ERROR here — correctly, since a row that stops matching
    has stopped guarding — so the failure would have been loud but wrong, and a gate that reds on
    honest input gets loosened. Normalising once is cheaper than anchoring sixteen patterns.
    """
    return re.sub(r"\s+", " ", io.open(ARTICLE, encoding="utf-8").read())


def _errors(text):
    """Every polarity violation, at every occurrence of every claim site."""
    bad = []
    for cid, span, require, forbid, src, _inv in POLARITY:
        hits = list(re.finditer(span, text, re.I | re.S))
        if not hits:
            bad.append(f"{cid}: the claim site is not in the document at all")
            continue
        for m in hits:
            win = m.group(0)
            if not re.search(require, win, re.I):
                bad.append(f"{cid}: the relation is NOT asserted at its own site — decided by {src}")
            if re.search(forbid, win, re.I):
                bad.append(f"{cid}: the INVERSE of the relation is asserted — decided by {src}")
    return bad


def test_no_claim_asserts_the_inverse_of_what_its_artifact_computes():
    """⛔ THE VERB IS THE CLAIM. 66 of 73 inversions shipped green before this existed."""
    bad = _errors(_article())
    assert not bad, (
        "the journal article states a relation its own artifact contradicts:\n  "
        + "\n  ".join(bad)
        + "\n\nEvery number in the sentence can be correct while the verb states the opposite "
          "result. Check the artifact named on each line and fix the SENTENCE — never the row, "
          "unless the artifact itself changed.")


@pytest.mark.parametrize("row", POLARITY, ids=[r[0] for r in POLARITY])
def test_every_polarity_row_still_finds_the_claim_it_guards(row):
    """⛔⛔ A ROW WHOSE SITE STOPPED MATCHING HAS SILENTLY STOPPED GUARDING.

    This is the defect the whole file is about, one level up: a reworded sentence slips out of its
    own `span`, the row finds nothing, and a table of fifteen guards quietly becomes a table of
    fourteen. A missing site is an ERROR, never a skip.
    """
    cid, span, _req, _forbid, src, _inv = row
    assert re.search(span, _article(), re.I | re.S), (
        f"{cid}: no sentence in the journal article matches this row's claim site, so the row is "
        f"guarding nothing. Either the claim was REWORDED — re-anchor `span` to it — or it was "
        f"REMOVED, in which case {src} no longer has a home in the paper and that is the finding.")


@pytest.mark.parametrize("row", POLARITY, ids=[r[0] for r in POLARITY])
def test_every_forbid_pattern_still_catches_the_inversion_it_names(row):
    """⛔ AN ALTERNATION NOBODY MATCHES IS AN ALTERNATION THAT HAS STOPPED GUARDING.

    Each row carries the inverted sentence it exists to reject. Asserting against that string rather
    than against the live document is what keeps the check honest as the paper is reworded: the
    `forbid` half is never exercised by a clean document, so nothing else would ever notice it going
    stale. This is the lesson the title guard learned when `\\bpairs?\\b` was found matching the unit
    inside "ten-base-pair" rather than the verb.
    """
    cid, _span, require, forbid, _src, inverted = row
    assert re.search(forbid, inverted, re.I), (
        f"{cid}: this row's `forbid` pattern no longer matches the inversion it names, so an "
        f"inverted claim would pass:\n  forbid : {forbid}\n  misses : {inverted!r}")
    assert not re.search(require, inverted, re.I) or cid == "liability-predicate", (
        f"{cid}: the inversion example also satisfies `require`, so the two halves do not "
        f"discriminate:\n  require: {require}\n  example: {inverted!r}")


def test_the_polarity_table_actually_fires_on_an_inverted_document():
    """⛔⛔ THE POSITIVE CONTROL. Everything above argues from a GREEN document; prove it can go red.

    Substituting each row's own inversion into the article must produce at least as many errors as
    rows substituted. Without this, a `span` that silently stopped matching would leave the main
    check passing on a paper it is no longer reading.
    """
    text = _article()
    fired = 0
    for cid, span, _req, _forbid, _src, inverted in POLARITY:
        m = re.search(span, text, re.I | re.S)
        if not m:
            continue
        mutated = text[:m.start()] + inverted + text[m.end():]
        if any(e.startswith(cid) for e in _errors(mutated)):
            fired += 1
    assert fired == len(POLARITY), (
        f"only {fired} of {len(POLARITY)} polarity rows fire when their own inversion is "
        "substituted into the article. A row that cannot catch the sentence it names is inert, and "
        "the main check above is passing on claims nothing reads.")
