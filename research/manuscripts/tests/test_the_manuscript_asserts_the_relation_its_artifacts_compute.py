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
    # ⛔⛔ THIS SPAN BOUND ONE OF THE CENTRAL NEGATIVE'S FOUR PROSE HOMES (round 17 seat B). The
    # window was `{0,160}` and the §2 site sits 161 characters from its terminal period, so
    # "pair" -> "fail to pair" there shipped with 4 linters and 983 tests green. Measured: 1 site
    # bound at {0,160}, 2 at {0,400}, and four `catalytic gap` sites have tails over 160.
    # ⚠ A WINDOW IS A DISGUISED LIST — it enumerates the sentence lengths a row happens to fit, and
    # a sentence that grows by one word leaves the guard without any signal that it did.
    ("liability-predicate",
     r"\b87\b[^.]{0,300}catalytic gap[^.]{0,400}\.",
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
    # ⚠ RE-ANCHORED 2026-08-23 when the Declarations were restructured to Nucleic Acid
    # Therapeutics' required template, which splits the single "Ethics approval, consent to
    # participate and consent for publication" statement into three headed ones. The RELATION is
    # unchanged; only its heading moved. ⛔ The `forbid` half now admits "or animals" as well as
    # "and animals": the cheapest inversion of this sentence is deleting the word "No", which
    # leaves the conjunction alone, and the old pattern demanded a conjunction swap the inverter
    # has no reason to make.
    ("ethics-not-applicable",
     r"\*\*Ethical considerations\.\*\*[^#]{0,220}?required\.",
     r"No human\s+subjects, human material or animals were involved",
     r"(?<!No )Human\s+subjects, human material (?:or|and) animals were involved",
     "the repository's no-wet-lab invariant",
     "**Ethical considerations.** Human subjects, human material or animals were involved, and "
     "ethics approval was required."),
    # ⚠ RE-ANCHORED 2026-08-23: "**Competing interests.**" -> the venue's required
    # "**Declaration of conflicting interest.**". Relation unchanged.
    # ⚠ RE-ANCHORED AGAIN 2026-08-25, and the wording is the VENUE'S, not a preference. Nucleic Acid
    # Therapeutics requires the heading "Author Disclosure Statement" verbatim, immediately after
    # Acknowledgments, carrying the sentence "No competing financial interests exist." So the claim
    # moved out of Statements and Declarations into a section of its own. ⛔ THE RELATION IS
    # UNCHANGED AND MUST STAY SCOPED TO *FINANCIAL* INTERESTS: the author has a non-financial one,
    # and `test_the_envelope_declares_one_interest.py` is the guard that stops this paper ever
    # denying it. A row here that read "no competing interests" would be the misstatement that guard
    # exists to catch.
    ("competing-interests",
     r"## Author Disclosure Statement[^#]{0,320}",
     r"No competing financial interests exist",
     # ⛔ THE INVERSE NEEDLE MUST NOT MATCH INSIDE ITS OWN POSITIVE. "Competing financial interests
     # exist" is a substring of "NO competing financial interests exist", and the search is
     # case-insensitive, so without the lookbehind this row reported the inversion as present at the
     # moment the paper stated the correct thing. Same trap `test_the_envelope_declares_one_interest`
     # records against its survivorship needle.
     r"(?<!No )Competing financial interests exist",
     "the cover letter: 'I received no funding and have no financial competing interests'",
     "## Author Disclosure Statement\n\nCompeting financial interests exist."),
    ("ai-use",
     r"\*\*Use of artificial intelligence\.\*\*[^#]{0,140}",
     r"A large language model \(Claude, Anthropic\) was used",
     r"No large language model was used",
     "the repository's own AI-use record",
     "**Use of artificial intelligence.** No large language model was used."),
    # ⛔⛔ THE RELATION THIS ROW GUARDS CHANGED, NOT JUST ITS WORDING (2026-08-23). The sentence
    # said the extended report was "prepared for bioRxiv and not yet posted". bioRxiv DECLINED the
    # submission — the author is unaffiliated — so a paper claiming a bioRxiv deposit was in
    # preparation was stating something that is not going to happen. The claim is now the weaker
    # and true one: it is not posted as a preprint anywhere, so the archived copy is what a reader
    # cites. ⚠ `forbid` uses a lookbehind rather than naming a server, because the failure mode is
    # the word "not" going missing, not the word "bioRxiv" coming back.
    # ⛔ RETIRED 2026-08-25, AND RETIRED AS A DECISION RATHER THAN AS A REWORDING. The sentence this
    # row guarded — "it is not posted as a preprint, so the archived copy is the citable one" — was
    # REMOVED from Data availability on trimcrae's checklist item 17: the captured Sage guidelines
    # say "Accepts preprints? Yes" and ask for the DOI in a designated field, so arguing the
    # distinction pre-empted an objection this venue does not raise. The positive half survives and
    # carries what a reader needs ("the archived copy is the citable one").
    # ⚠ AND THE CONDITION THE ROW WAS WRITTEN FOR IS ALSO GONE: it names "deposit-state.json: a
    # `pending` Zenodo draft", and that file now carries a `published` block alone — DOI
    # 10.5281/zenodo.22061075, published 2026-08-23 — with no `pending` key at all. The window
    # between drafting a corrected version and publishing it, which is the whole thing this row
    # made legible, closed two days before the row failed.
    # ★ If a preprint IS ever posted, the disclosure comes back and so does a row for it.
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


# ─────────────────────────────────────────────────────────────────────────────────────────────
# ⛔⛔ SCOPE BY THE PROPERTY, NOT BY A LIST (round 17 seat B, 2026-08-23).
#
# Seat B's shape verdict, measured over 33 mutations: "fixes bound to a PREDICATE held; every fix
# whose scope is a LIST regressed at a sibling" — ARTICLE (1 of 3), DOCUMENTS (4 of 6), PAPERS
# (2 of 4), one span (1 of 4 homes), the re-anchor messages (5 of 7), the early-return repair
# (1 of 12). Six of eleven, AND IN THREE THE SIBLING WAS NAMED IN THE FIX'S OWN COMMENT — including
# a check headed "⛔ EVERY DOCUMENT, NOT THE TWO OBVIOUS ONES" that enumerated four and missed two.
#
# ★ A list is a thing somebody must remember to extend; a predicate is not. So the safety-critical
# Declarations lines are not checked against a named set of files — every document that CONTAINS the
# clause must state it correctly, which is a rule that extends itself to a document added tomorrow.
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: (what it is, the clause that puts a document in scope, the form it must take, the inversion)
SAFETY_CLAUSES = [
    ("the no-administration instruction",
     re.compile(r"administration to any person or animal", re.I),
     re.compile(r"not for administration to any person or animal", re.I),
     "a document telling a reader a research reagent MAY be administered is the one sentence in "
     "this submission that could hurt somebody"),
    ("the no-wet-lab statement",
     re.compile(r"human\s+subjects, human material", re.I),
     re.compile(r"No human\s+subjects, human material (?:or|and) animals were involved", re.I),
     "this repository has no wet lab; a document claiming human subjects were involved is a "
     "fabricated ethics claim"),
]


def _aso_documents():
    """Every markdown document in the submission directory. Derived, never enumerated."""
    found = sorted(f for f in os.listdir(ASO) if f.endswith(".md"))
    assert found, f"no markdown documents under {ASO}, so this guard reads nothing"
    return found


@pytest.mark.parametrize("clause", SAFETY_CLAUSES, ids=[c[0] for c in SAFETY_CLAUSES])
def test_every_document_stating_a_safety_clause_states_it_the_right_way_round(clause):
    """⛔ THE DOCUMENT SET IS WHATEVER CONTAINS THE CLAUSE, SO A NEW DOCUMENT IS IN SCOPE BY DEFAULT."""
    label, in_scope, correct, why = clause
    checked, wrong = [], []
    for name in _aso_documents():
        text = re.sub(r"\s+", " ", io.open(os.path.join(ASO, name), encoding="utf-8").read())
        for m in in_scope.finditer(text):
            window = text[max(0, m.start() - 120):m.end() + 40]
            checked.append(name)
            if not correct.search(window):
                wrong.append((name, window.strip()[-150:]))
    assert checked, (
        f"no document in {os.path.basename(ASO)} states {label}, so this guard is vacuous. Either "
        "the clause was reworded everywhere at once, or it was dropped — both are findings.")
    assert not wrong, (
        f"{len(wrong)} document(s) state {label} the wrong way round. WHY THAT MATTERS: {why}.\n  "
        + "\n  ".join(f"{n}: …{w}" for n, w in wrong))


def test_the_safety_clause_scope_is_derived_and_catches_more_than_one_document():
    """⛔ A DERIVED SCOPE THAT RESOLVES TO ONE FILE IS A LIST WITH EXTRA STEPS.

    The defect this replaces was a guard reading the journal article while the same clause shipped
    in the extended report and the supplementary information. If the derivation ever collapses to a
    single document, it has stopped doing the thing it was written for.
    """
    hits = {name for name in _aso_documents()
            if SAFETY_CLAUSES[0][1].search(
                re.sub(r"\s+", " ", io.open(os.path.join(ASO, name), encoding="utf-8").read()))}
    assert len(hits) >= 3, (
        f"the no-administration clause was found in {len(hits)} document(s): {sorted(hits)}. It is "
        "carried by the journal article, the extended report, the supplementary information and the "
        "deposit tables; a derivation finding fewer has stopped reading the siblings, which is the "
        "exact regression this section exists to prevent.")
