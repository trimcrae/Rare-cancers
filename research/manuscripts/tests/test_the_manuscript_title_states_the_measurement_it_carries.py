"""The title is a claim, and nothing in the suite read it.

⛔ WHY THIS FILE EXISTS. The title is the one sentence that reaches every reader — a search result,
a citation line, a preprint server's listing — and for most of them it is the ONLY sentence. It
states three quantitative things:

  * a RATE ("Nearly half of junction-spanning gapmer designs …"), which is 87/190;
  * a CRITERION ("… over a ten-base-pair duplex through the catalytic gap"), which is the cut the
    whole paper is stated at and which §2.5 says is adopted rather than measured; and
  * a TRADE ("… and a longer gap trades gap-level margin against parent-paired gap DNA"), which is
    §2.9's identity.

Every one of the three can go stale silently. The rate word is not a number, so no numeric linter
sees it; a cut that moved from ten would leave the title reading ten with every count beneath it
recomputed; and the trade clause names two quantities that Figure 3's own axis was found (2026-08-19)
to be a DIFFERENT quantity from the one its caption claimed — `parent_paired_gap_dna_nt`, arithmetic
on the design's own seam, against the searched mature-parent duplex. A title naming the wrong pair
of quantities is that same confusion at the top of the paper.

★ NOTHING HERE IS TYPED. The rate comes from `aso-parent-null.json`'s `observed`, the criterion from
its `method.min_duplex_bp`, and the two traded quantities are required to be §2.9's own — read out
of §2.9 at run time, because §2.9 is what the title is summarising.

⚠ THE RATE IS CHECKED AS A BAND, NOT AS A STRING. "Nearly half" is a claim with a truth condition:
it is true of 0.4579 and false of 0.62. The bands below are what each English quantifier licenses,
so the guard fires both when the measurement moves out from under the word and when the word is
changed to one the measurement does not support.
"""
from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
#: ⛔ BOTH TITLES (round 14 seat 4). This guard opened the extended report only, so the CONDENSED
#: submission's title — the one that reaches a NAT reader, a search result and a citation line —
#: was checked by nothing at all. That is the ninth instrument this review has found bound to one
#: of a pair while its docstring reasons about "the title".
ARTICLES = {
    "extended-report": os.path.join(MANUSCRIPTS, "aso",
                                    "fusion-junction-aso-research-article.md"),
    "journal-article": os.path.join(MANUSCRIPTS, "aso",
                                    "fusion-junction-aso-journal-article.md"),
}
ARTICLE = ARTICLES["extended-report"]

#: ⭐⭐ WHAT KIND OF CLAIM EACH TITLE MAKES, DECLARED PER PAPER (2026-08-24, trimcrae).
#:
#: ⛔ READ THIS BEFORE CHANGING A ROW. This file was written on the premise that BOTH ASO titles
#: state the central negative — its own words: "a title that drops the proportion drops the
#: finding." That premise held while both papers were the same argument at two lengths. It stopped
#: holding when the condensed article was retitled to what a laboratory receives (reagents, test
#: articles, an experiment) rather than to what the screen found, because the paper's stated purpose
#: is to be a blueprint a wet lab can execute. The extended report is unchanged and still states
#: the measurement.
#:
#: ⚠ THIS IS A SCOPING, NOT A RELAXATION, AND THE DIFFERENCE IS THE WHOLE POINT. A
#: `deliverable` title is not exempt from checking — it is held to the OPPOSITE contract: it must
#: carry no rate, no ratio, no criterion and no liability predicate AT ALL, so there is nothing in
#: it that can go stale silently. Put a number back in that title and the checks below fail and
#: tell you to move the row to `measurement`. The one thing this file must never become is a file
#: that silently checks nothing, which is exactly what it caught itself doing twice: a bare
#: `return` that made the predicate check vacuous on the extended report (round 16 seat 5), and an
#: alternation satisfied by the unit inside "ten-base-pair" (same round).
TITLE_CONTRACT = {
    "extended-report": "measurement",
    "journal-article": "deliverable",
}
MEASUREMENT_PAPERS = sorted(k for k, v in TITLE_CONTRACT.items() if v == "measurement")


def _contract(paper):
    assert paper in TITLE_CONTRACT, (
        f"{paper} has no entry in TITLE_CONTRACT, so nothing declares what kind of claim its title "
        "makes and every check below would silently choose one for it.")
    return TITLE_CONTRACT[paper]


def _assert_states_no_measurement(paper, title):
    """A `deliverable` title's contract: it carries nothing that can go stale.

    ⛔ EVERY CHANNEL THE `measurement` CHECKS POLICE IS REFUSED HERE, not ignored. If a rate word,
    an `n of N`, a base-pair criterion or a liability predicate ever appears in this title, it is
    making a quantitative claim again and must be checked as one.
    """
    offenders = []
    if _RATE_SCANNER.search(title):
        offenders.append(f"a rate word ({_RATE_SCANNER.search(title).group(0).strip()!r})")
    if re.search(r"\b\d+ of \d+\b", title):
        offenders.append("an 'n of N' ratio")
    if re.search(r"\b([a-z]+|\d+)[- ]base[- ]pairs?\b|\b(\d+)\s*bp\b", title, re.I):
        offenders.append("a base-pair criterion")
    if _LIABILITY_PREDICATE.search(title):
        offenders.append("the liability predicate")
    assert not offenders, (
        f"{paper}'s title is declared `deliverable` in TITLE_CONTRACT — a title that names what the "
        f"paper provides and states no measurement — but it now carries "
        f"{', '.join(offenders)}:\n  {title}\n\n"
        "A number in a title goes stale silently, which is why this file exists. Either take it out, "
        f"or move {paper!r} to `measurement` in TITLE_CONTRACT so the rate, criterion and predicate "
        "checks apply to it again.")
NULL = os.path.join(REPO, "research", "modalities", "aso-parent-null.json")

_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen sixteen seventeen eighteen nineteen twenty").split()

#: What an English quantifier over a proportion licenses. Longest phrases first — the scanner is
#: leftmost-longest, so "nearly half" is never read as "half".
_RATE_BANDS = [
    ("more than half", (0.500, 1.000)),
    ("just under half", (0.430, 0.500)),
    ("just over half", (0.500, 0.570)),
    ("nearly half", (0.400, 0.500)),
    ("almost half", (0.400, 0.500)),
    ("about half", (0.450, 0.550)),
    ("a majority of", (0.500, 1.000)),
    ("a minority of", (0.000, 0.500)),
    ("nearly a third", (0.280, 0.334)),
    ("about a third", (0.290, 0.380)),
    ("a third of", (0.300, 0.370)),
    ("a quarter of", (0.200, 0.300)),
    ("two thirds of", (0.620, 0.710)),
    ("most", (0.500, 1.000)),
    ("half of", (0.475, 0.525)),
    ("every", (1.000, 1.000)),
    ("all", (1.000, 1.000)),
    ("none of", (0.000, 0.000)),
    ("no ", (0.000, 0.000)),
]
#: ⛔⛔ WITHOUT WORD BOUNDARIES THIS IS A FALSE-RED LANDMINE, NOT A GUARD (round 16 seat 5).
#: Measured: "the ALLele frequency" and "an overALL rate" both match `all` (band [1.0, 1.0]), and
#: "ALMOST every" matches `most` — so an HONEST title containing any of those ordinary words fails
#: against a CORRECT measurement. A gate that goes red on true input is worse than one that goes
#: green on false input, because the first thing anyone does is loosen it.
#: ⚠ `(?!\w)` not `\b`: several bands end in a space ("no ", "a third of"), where `\b` would not
#: match. Leftmost-longest ordering above is preserved — the alternation order is unchanged.
_RATE_SCANNER = re.compile(
    "|".join(rf"(?<!\w){re.escape(p)}(?!\w)" for p, _ in _RATE_BANDS), re.I)


def _rate_scanner_is_not_vacuous():
    """The anchors must not have stopped the scanner matching a real quantifier."""
    return bool(_RATE_SCANNER.search("nearly half of designs"))


def _artifact():
    if not os.path.exists(NULL):
        pytest.fail("aso-parent-null.json is missing; the title's rate and criterion are unchecked")
    return json.load(open(NULL, encoding="utf-8"))


def _text(article=None):
    article = article or ARTICLE
    if not os.path.exists(article):
        pytest.fail(f"{os.path.basename(article)} is missing; its title is unchecked")
    return open(article, encoding="utf-8").read()


def _front_matter_title(article=None):
    m = re.search(r'^title:\s*"(.+?)"\s*$', _text(article), flags=re.M)
    assert m, "the front matter carries no `title:` line; nothing names this deposit"
    return " ".join(m.group(1).split())


def _h1(article=None):
    m = re.search(r"^#\s+(.+?)\s*$", _text(article), flags=re.M)
    assert m, "the manuscript has no H1; the rendered document has no title"
    return " ".join(m.group(1).split())


def _plain(title):
    """Markdown emphasis stripped — the YAML title carries none and the H1 does."""
    return re.sub(r"[*_`]", "", title)


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_front_matter_title_and_the_printed_title_are_the_same_claim(paper):
    """Two copies of one sentence in one file is a divergence waiting to happen.

    The YAML title is what the repository's own tooling indexes; the H1 is what the PDF builds
    print. A round that edits one and not the other ships a deposit whose metadata and cover page
    disagree, and nothing else in the suite compares them.
    """
    front, h1 = _plain(_front_matter_title(ARTICLES[paper])), _plain(_h1(ARTICLES[paper]))
    assert front == h1, (
        "the front-matter `title:` and the printed H1 have diverged.\n"
        f"  front matter: {front}\n"
        f"  H1          : {h1}\n"
        "One of them is what a reader sees and the other is what the tooling indexes.")


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_titles_rate_word_is_one_the_measurement_supports(paper):
    """87 of 190 is 45.8%. "Nearly half" is true of that; "most" would not be."""
    observed = _artifact()["observed"]
    rate = observed["n_liable"] / observed["n_designs"]
    title = _plain(_front_matter_title(ARTICLES[paper]))
    if _contract(paper) == "deliverable":
        _assert_states_no_measurement(paper, title)
        return
    # ⭐ AN EXACT RATIO IS A RATE, AND A STRICTLY BETTER ONE (2026-08-22). The condensed title says
    # "87 of 190" where the extended report says "nearly half": no band to license, both numbers
    # checked against the artifact directly, and the reader is told the denominator. A guard that
    # accepted only English quantifiers would have refused the more precise title — so it accepts
    # either, and an exact ratio is checked EXACTLY rather than against a band.
    exact = re.findall(r"\b(\d+) of (\d+)\b", title)
    for n, d in exact:
        assert (int(n), int(d)) == (observed["n_liable"], observed["n_designs"]), (
            f"the title states {n} of {d}; the screen measured "
            f"{observed['n_liable']} of {observed['n_designs']} "
            "(aso-parent-null.json:observed). Either the title or the measurement has moved.")
    found = [m.group(0).lower().strip() for m in _RATE_SCANNER.finditer(title)]
    assert found or exact, (
        f"the title states no rate at all: {title!r}. It carries this paper's central negative — "
        f"{observed['n_liable']} of {observed['n_designs']} designs pair a wild-type parent — and a "
        "title that drops the proportion drops the finding.")
    bands = dict(_RATE_BANDS)
    for phrase in found:
        low, high = bands[phrase]
        assert low <= rate <= high, (
            f"the title says {phrase!r}, which licenses a rate in [{low:.3f}, {high:.3f}]; the "
            f"measurement is {observed['n_liable']}/{observed['n_designs']} = {rate:.4f} "
            f"(aso-parent-null.json:observed). Either the word or the measurement has moved.")


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_title_states_the_criterion_the_artifact_was_read_at(paper):
    """The rate is meaningless without its cut, and the cut is adopted rather than measured."""
    cut = _artifact()["method"]["min_duplex_bp"]
    title = _plain(_front_matter_title(ARTICLES[paper]))
    if _contract(paper) == "deliverable":
        _assert_states_no_measurement(paper, title)
        return
    # ⚠ THREE SPELLINGS, ONE PROPERTY. The extended report writes "a ten-base-pair duplex"; the
    # condensed title, which is built to a page budget where every character is charged for, writes
    # "at 10 bp". Both name the same cut, and a guard that admitted only the hyphenated form would
    # be enforcing a house style rather than a measurement.
    stated = re.search(r"\b([a-z]+|\d+)[- ]base[- ]pairs?\b|\b(\d+)\s*bp\b", title, re.I)
    assert stated, (
        f"the title states a rate with no criterion: {title!r}. The same designs are 92.1% liable "
        f"at seven base pairs and 3.2% at thirteen (aso-parent-null.json:cut_sensitivity), so a "
        "rate without its cut is not a claim.")
    token = (stated.group(1) or stated.group(2)).lower()
    value = int(token) if token.isdigit() else (_WORDS.index(token) if token in _WORDS else None)
    assert value == cut, (
        f"the title states a {token}-base-pair criterion; the artifact was read at "
        f"{cut} (aso-parent-null.json:method.min_duplex_bp).")


def test_the_titles_trade_clause_names_the_two_quantities_section_2_9_trades():
    """§2.9's identity is between the gap-level margin and the parent-paired gap DNA.

    ⚠ THIS IS THE AXIS FIGURE 3 GOT WRONG. Its ordinate is `parent_paired_gap_dna_nt` — arithmetic
    on the design's own seam — while its caption called it the parent duplex the design concedes,
    which is the SEARCHED mature-parent quantity. The title trades two named quantities; both have
    to be quantities §2.9 actually trades, or the top line of the paper carries the same conflation.

    ⚠ EXTENDED REPORT ONLY, AND DELIBERATELY — NOT A ONE-OF-A-PAIR GAP. §2.9's gap-length series was
    moved whole out of the condensed submission for the six-page budget, so its title states no
    trade and must not: a guard demanding one there would demand a claim the paper no longer makes.
    The three tests above ARE parametrised over both, because a rate word, a criterion and the
    front-matter/H1 agreement are owed by any title of this work.
    """
    title = _plain(_front_matter_title())
    clause = re.search(r"\btrades?\s+(.+)$", title, re.I)
    assert clause, (
        f"the title no longer states the gap-length trade: {title!r}. §2.9's identity — margin and "
        "parent-paired gap DNA are complements inside one gap — is the paper's second result.")
    sides = [s.strip(" .,;") for s in re.split(r"\bagainst\b|\bfor\b", clause.group(1)) if s.strip()]
    assert len(sides) == 2, (
        f"the title's trade clause names {len(sides)} quantit(ies), not two: {sides}. A trade is "
        "between two things.")

    body = re.sub(r"^---\n.*?\n---\n", "", _text(), flags=re.S)
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"^#{2,3}\s*([\d.]+)\s*·", body, flags=re.M)]
    section = None
    for index, (start, number) in enumerate(heads):
        if number == "2.9":
            section = body[start:heads[index + 1][0] if index + 1 < len(heads) else len(body)]
    assert section, "§2.9 is not in the manuscript, so the title's trade clause has no source"
    flat = " ".join(_plain(section).split()).lower()
    for side in sides:
        assert side.lower() in flat, (
            f"the title trades {side!r}, which §2.9 never names. The two quantities §2.9 trades are "
            "complements inside one gap; a title naming something else is claiming a different "
            "result from the one measured. §2.9 is the section this clause summarises.")


#: What `corpus.n_with_parent_duplex_through_gap` COUNTS: designs that form a parent duplex. A title
#: stating that count must say the designs do that, not the opposite of it.
#:
#: ⛔ WHY THIS EXISTS (round 15 seat 2, BLOCKER). The guards above check the title's arithmetic and
#: never its predicate. Changing one word at all three authored homes — `pair` to `spare` — and
#: regenerating the three views that render the title passed EVERY gate, because every number in the
#: title was still correct. The paper's one universally-read sentence then said 87 designs SPARE a
#: wild-type parent, when 87 is the count that FAILS the parent screen. This file's own docstring
#: enumerates "three quantitative things" the title states; the RELATION between the rate and the
#: thing counted was not among them.
#:
#: ⚠ AN INVERTING VERB IS THE WHOLE RISK, so the inverters are named rather than the affirmatives
#: guessed at. A synonym of "pair" that nobody listed fails loudly and gets added; a synonym of
#: "spare" that nobody listed is the defect shipping. The asymmetry is deliberate — a title is
#: rewritten every few rounds and this list must be the thing that resists it.
#: ⛔⛔ WORD BOUNDARIES, AND THEY WERE MISSING (measured 2026-08-23, and it is the SECOND time this
#: repository has paid for exactly this). `miss(?:es|ed)?` with no `\b` matches the middle of
#: "sub**miss**ion" — every occurrence of the word "submission" in the cover letter was scoring as
#: an inverting verb. It surfaced from the coverage census, which credited a retraction paragraph to
#: this guard purely on that substring and then withdrew the credit when the letter grew and the
#: pattern crossed the selectivity cap; the "lost binding" was never a binding.
#: ⛔ THE LIVE HAZARD IS THE OTHER DIRECTION AND IT IS WORSE. `clear(?:s|ed)?` matches inside
#: "nu**clear**" and "un**clear**", and this is a paper about an orphan NUCLEAR receptor: a title
#: reading "… a wild-type parent of this nuclear receptor" would have failed a guard whose message
#: says the title states the inverse of the paper's central negative. A gate that reds on true input
#: is worse than one that greens on false input, because the first thing anyone does is loosen it.
#: The affirmative half has the same shape — unbounded `pair(?:s|ed|ing)?` matches "re**pair**" and
#: "im**pair**ed" — which is the guard going quiet rather than loud, and is how
#: `\bpairs?\b`-matching-"ten-base-pair" was found before.
#: ⚠ AND A HYPHEN IS A WORD BOUNDARY, so `\bpair\b` still matches the UNIT inside "ten-base-pair".
#: That is this repository's oldest instance of this defect and `\b` alone does not fix it; the
#: affirmative half therefore also refuses a "pair" that a hyphen introduces.
#:
#: ⛔⛔ THE BOUNDS ARE WRITTEN INTO THE LITERALS, AND THE FIRST FIX PUT THEM IN A FUNCTION INSTEAD —
#: WHICH CORRECTED THIS GUARD AND LEFT THE DEFECT LIVE ONE FILE OVER (measured 2026-08-23, hours
#: after the first fix). `_verb(alts)` returned `r"\b(?:" + alts + r")\b"`, so at RUNTIME the
#: pattern was bounded and `clear` stopped matching inside "nuclear" — proven. But
#: `claim_coverage._test_patterns` harvests regexes by STATICALLY READING THE SOURCE, so what it
#: saw was the unbounded string literal that goes IN to the call, not the bounded value that comes
#: out. The census went on crediting cover-letter sentences to this guard on `miss` inside
#: "sub-miss-ion", exactly as before, and the ablation gate caught it again.
#: ★ THE GENERAL RULE, WHICH IS WORTH MORE THAN THE INSTANCE: A PATTERN COMPOSED AT RUNTIME IS
#: INVISIBLE TO ANYTHING THAT READS SOURCE. Any instrument that harvests literals — this census,
#: a grep-based audit, a reviewer skimming the file — sees the pattern BEFORE composition. So a
#: regex that other tooling reads must be complete where it is written, and the cost of that is
#: repeating six characters twice.
_PAIRING_VERBS = (r"\b(?:(?<!-)pair(?:s|ed|ing)?|form(?:s)?\s+a\s+duplex|are\s+liable"
                  r"|carry\s+a\s+duplex|let\s+a\s+(?:mature\s+)?wild-type\s+parent)\b")
_SPARING_VERBS = (r"\b(?:spare(?:s|d)?|avoid(?:s|ed)?|clear(?:s|ed)?|miss(?:es|ed)?"
                  r"|escape(?:s|d)?|do(?:es)?\s+not\s+pair|fail\s+to\s+pair)\b")


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_title_says_the_designs_do_what_the_count_counts(paper):
    """⛔ THE PREDICATE, NOT ONLY THE ARITHMETIC. One word inverts the paper's central negative."""
    title = _plain(_front_matter_title(ARTICLES[paper]))
    observed = _artifact()["observed"]
    exact = re.search(rf"\b{observed['n_liable']}\b\s+of\s+\b{observed['n_designs']}\b(.{{0,80}})",
                      title)
    if not exact:
        # SKIP IS DELIBERATE: the extended report's title states its rate as the quantifier "nearly
        # half" rather than as an explicit n-of-N, and `test_the_titles_rate_word_is_one_the_
        # measurement_supports` owns that form — it checks the word against the band the measurement
        # licenses. This test is about the PREDICATE beside an explicit ratio, and there is no
        # explicit ratio here to sit beside. A title that gains one is covered from that day.
        pytest.skip(f"{paper}'s title states no explicit n-of-N ratio; the rate-band test owns it")
    tail = exact.group(1)
    assert not re.search(_SPARING_VERBS, tail, re.I), (
        f"the title says {observed['n_liable']} of {observed['n_designs']} designs SPARE or CLEAR a "
        "wild-type parent. That count is `corpus.n_with_parent_duplex_through_gap` — the designs "
        f"that FAIL the parent screen. As written the title states the inverse of this paper's "
        f"central negative:\n  {title}")
    assert re.search(_PAIRING_VERBS, tail, re.I), (
        f"the title states {observed['n_liable']} of {observed['n_designs']} but names no verb this "
        "guard recognises as what that count counts (a parent duplex being FORMED). Either the "
        "predicate was inverted, or a new phrasing needs adding to _PAIRING_VERBS — deliberately, "
        f"and only after checking it means what the field means:\n  {title}")


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE PREDICATE, WHICH EVERY INSTRUMENT IN THIS FILE WAS BLIND TO (round 15 seat 2, BLOCKER).
#
# Changing ONE WORD at all three authored homes — `pair` → `spare` — and regenerating the views
# passed every gate. The title then said 87 designs SPARE a wild-type parent, when 87 is the count
# that FAILS the parent screen: the inverse of the paper's central negative, on the one sentence
# that reaches every reader. Every NUMBER was still correct, which is precisely why nothing fired.
#
# ⚠ AND THE NEAR-MISS IS THE MORE INSTRUCTIVE HALF. A stronger inversion ("clear every wild-type
# parent") WAS caught — but only because `_RATE_SCANNER` happened to match "every" as a quantifier
# and then asserted 1.000 ≤ 0.4579. A guard that catches a semantic inversion only when the
# inversion happens to contain a quantifier word is not covering the property; it is getting lucky.
#
# ★ THE GENERAL LESSON, AND IT IS WHY THIS BLOCK EXISTS RATHER THAN A ONE-LINE ASSERT: this file's
# docstring says the title "states three quantitative things" and lists rate, criterion and trade.
# A claim is a quantity AND a relation, and the whole guard set was built on the quantity half.
# ---------------------------------------------------------------------------------------------

#: What `corpus.n_with_parent_duplex_through_gap` COUNTS: designs that form the duplex. A title
#: stating that count must assert that relation.
#: ⛔⛔ `\bpairs?\b` MATCHED THE UNIT, NOT THE VERB, AND THAT MADE THE GUARD BELOW VACUOUS
#: (round 16 seat 5, 2026-08-22). The extended report's title contains "pair" TWICE: once as its
#: main verb ("partner genes pair a wild-type parent gene") and once inside the criterion
#: ("a ten-base-**pair** duplex"). A word-boundary alternation cannot tell them apart, so inverting
#: the verb to "spare" left the pattern still matching — on the unit — and
#: `test_the_predicate_patterns_are_exercised_by_the_titles_they_police` still passed. Measured:
#: inverting BOTH titles at once gave `15 passed, 2 skipped`.
#: ★ A hyphen is the tell: a compound unit ("ten-base-pair", "parent-paired") is never the sentence's
#: relation. Excluding a preceding hyphen or word character keeps the verb and drops both units.
_LIABILITY_PREDICATE = re.compile(
    r"(?<![-\w])pairs?\b|\bform(?:s|ing)? a duplex\b|\bare liable\b|(?<![-\w])paired\b", re.I)

#: Its inverse. Listed separately and asserted separately, because "the right verb is present" and
#: "no wrong verb is present" fail differently: a title reading "pair or spare" satisfies the first.
_SPARING_PREDICATE = re.compile(
    r"\bspares?\b|\bclears?\b|\bavoids?\b|\bexcludes?\b|\bprotects?\b|\bmiss(?:es)?\b", re.I)


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_titles_predicate_is_the_relation_the_artifact_counts(paper):
    """⛔ WHAT THE COUNT DOES, NOT ONLY WHAT THE COUNT IS."""
    title = _plain(_front_matter_title(ARTICLES[paper]))
    observed = _artifact()["observed"]
    # ⚠ THE `deliverable` BRANCH IS NOT THE BARE `return` THIS COMMENT WARNS ABOUT. That defect was
    # an early exit that asserted NOTHING; this one asserts the opposite contract first and only
    # then returns, so the case can still fail. Removing the call below would recreate the defect.
    if _contract(paper) == "deliverable":
        _assert_states_no_measurement(paper, title)
        return
    # ⛔⛔ THIS WAS A BARE `return`, AND IT MEANT THIS TEST NEVER ASSERTED ANYTHING ON THE EXTENDED
    # REPORT (round 16 seat 5, 2026-08-22). Round 15 added the predicate check because a title could
    # be inverted -- "87 designs SPARE a wild-type parent" -- with every number still correct. The
    # check was then gated on the title containing the literal count, and the extended report states
    # its rate as the quantifier "nearly half". So the gate never opened, the body never ran, and the
    # case reported PASSED rather than skipped -- which also put it outside
    # `test_no_guard_can_silently_not_run.py`, whose scope is `pytest.skip`, not early returns.
    # Measured on the pinned tree: inverting the extended report's title to "spare" was GREEN.
    # ★ THE GATE IS THE COUNT, NOT ONE SPELLING OF IT. The rate test accepts either an exact `n of N`
    # or a quantifier licensed by `_RATE_BANDS`; so does this one, and a title stating the count in
    # NO form is a failure here rather than a silent pass -- "some other way" must never be able to
    # mean "no way at all".
    states_exact = bool(re.search(rf"\b{observed['n_liable']}\b", title))
    states_rate = bool(_RATE_SCANNER.search(title))
    assert states_exact or states_rate, (
        f"{paper}'s title states this paper's central count in no form this suite recognises -- "
        f"neither the literal {observed['n_liable']} nor a quantifier in `_RATE_BANDS`:\n  {title}\n\n"
        "The predicate check below cannot run without one, and a title that carries no proportion "
        "has dropped the finding. Extend `_RATE_BANDS` if the wording is new and honest.")

    assert _LIABILITY_PREDICATE.search(title), (
        f"the title states {observed['n_liable']} of {observed['n_designs']} without saying those "
        "designs PAIR a wild-type parent: {title!r}\n\n"
        "`corpus.n_with_parent_duplex_through_gap` counts designs that FORM the duplex. A title "
        "carrying that count under any other relation states a different result.".format(
            title=title))
    inverted = _SPARING_PREDICATE.search(title)
    assert not inverted, (
        f"the title says {observed['n_liable']} designs {inverted.group(0)!r} a wild-type parent, "
        f"and {observed['n_liable']} is the count that FAILS the parent screen — "
        f"`n_with_parent_duplex_through_gap`, the designs a parent pairs. The title states the "
        f"inverse of this paper's central negative:\n  {title}")


def test_the_predicate_patterns_are_exercised_by_the_titles_they_police():
    """⛔ AN ALTERNATION NOBODY MATCHES IS AN ALTERNATION THAT HAS STOPPED GUARDING.

    Both patterns above are hand-written alternations, which is the shape this review has repeatedly
    found going stale. This asserts the positive one actually fires on a real title, so a rewording
    that slips past it fails HERE rather than passing silently in the test above.
    """
    # ⛔⛔ "ANY TITLE MATCHES" WAS TOO WEAK, AND IT PASSED ON AN INVERTED PAIR (round 16 seat 5).
    # With both titles inverted to "spare", this still reported green, because `\bpairs?\b` was
    # matching the UNIT inside "ten-base-pair". The alternation is now anchored against compound
    # units (above), and this guard asks the stronger question: EVERY policed title must match, so a
    # single reworded title fails here instead of hiding behind its sibling.
    # ⚠ SCOPED TO THE `measurement` TITLES (2026-08-24). A `deliverable` title is REQUIRED to carry
    # no liability predicate, so demanding one of every title would make the two contracts
    # contradict. The alternation is still proven live two ways: every measurement-stating title
    # must match it, and the synthetic assertions below fail if it can be satisfied by a unit alone
    # — so it cannot go stale merely because fewer real titles exercise it.
    assert MEASUREMENT_PAPERS, (
        "no paper is declared `measurement` in TITLE_CONTRACT, so _LIABILITY_PREDICATE is exercised "
        "by no real title at all and the predicate check is vacuous everywhere.")
    titles = {k: _plain(_front_matter_title(ARTICLES[k])) for k in MEASUREMENT_PAPERS}
    missing = sorted(k for k, t in titles.items() if not _LIABILITY_PREDICATE.search(t))
    assert not missing, (
        f"{', '.join(missing)}: the title does not match _LIABILITY_PREDICATE, so the predicate "
        "check above is vacuous for that paper.\n"
        + "\n".join(f"  {k}: {titles[k]}" for k in missing)
        + "\n\nEither the title was reworded past the alternation — extend it — or it no longer "
        "states the relation the count counts, which is the defect the check exists to catch.")

    # ⛔ AND THE ALTERNATION MUST NOT BE SATISFIABLE BY A UNIT ALONE. This is the exact regression:
    # a title whose only match is inside a hyphenated measurement carries no relation at all. Asserted
    # against a synthetic string so it holds no matter how the real titles are later reworded.
    unit_only = ("In silico, nearly half of designs spare a wild-type parent gene over a "
                 "ten-base-pair duplex, trading margin against parent-paired gap DNA")
    assert not _LIABILITY_PREDICATE.search(unit_only), (
        "_LIABILITY_PREDICATE matches a title whose only 'pair' is the unit inside 'ten-base-pair' "
        f"or the modifier in 'parent-paired' — and whose verb is 'spare', the inversion this file "
        f"exists to catch:\n  {unit_only}\n\n"
        f"matched: {_LIABILITY_PREDICATE.search(unit_only).group(0)!r}\n"
        "The compound-unit anchors have been relaxed; a unit is never the sentence's relation.")
    assert _SPARING_PREDICATE.search(unit_only), (
        "_SPARING_PREDICATE no longer matches 'spare', so the inversion check above is vacuous.")


def test_the_rate_scanner_reads_quantifiers_and_not_the_words_that_contain_them():
    """⛔ A GATE THAT GOES RED ON TRUE INPUT GETS LOOSENED, WHICH IS HOW A GUARD DIES.

    `_RATE_SCANNER` had no word boundaries, so ordinary English containing a band as a SUBSTRING
    resolved as a rate claim: "allele" and "overall" both yielded `all` at [1.0, 1.0], and "Almost"
    yielded `most`. A title stating a correct measurement would have failed for containing the word
    "overall". Both directions are asserted, because anchoring too hard would silently stop the
    scanner matching anything at all.
    """
    for honest in ("the allele frequency of NR4A3 fusions",
                   "an overall rate across the panel",
                   "Almost certainly a modelling artefact"):
        found = [m.group(0) for m in _RATE_SCANNER.finditer(honest)]
        assert not found, (
            f"the rate scanner reads {found} inside ordinary words in {honest!r}, so an honest "
            "title would fail against a correct measurement.")

    for real, expect in (("nearly half of designs", "nearly half"),
                         ("most designs pair a parent", "most"),
                         ("all 190 designs", "all")):
        found = [m.group(0).lower() for m in _RATE_SCANNER.finditer(real)]
        assert expect in found, (
            f"the rate scanner no longer reads {expect!r} in {real!r}; the boundary anchors have "
            "been tightened past the quantifiers they exist to find, and every rate check above is "
            "now vacuous.")
