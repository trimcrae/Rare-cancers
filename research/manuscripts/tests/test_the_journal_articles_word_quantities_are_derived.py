#!/usr/bin/env python3
"""The JOURNAL ARTICLE's quantities written in WORDS, each tied to the artifact that owns it.

⛔⛔ WHY THIS EXISTS — THE HALF OF AUT-PD-148 THAT LANDED IN THE HARNESS AND NOT IN THE PAPER.
`claim_ablation.py` learned on 2026-09-01 that a quantity spelled `six` is still a quantity, so a
class of sentence that had always been unfalsifiable became testable for the first time. Run at full
depth on 2026-09-02 (`S40-COVERAGE-INFLATION.md`), the ablation gate then found **twelve sentences
the census marks `covered` whose number nothing reads** — eleven in this document — and every one of
the fourteen blind perturbations was a word rather than a digit:

    six->ten  seven->three  ten->six  fourth->eighth  second->fourth  five->nine  two->six  four->nine

Those sentences were never unguarded by accident. `test_journal_article_numbers.py` and its five
siblings harvest DIGITS out of this article; a value the article spells out was invisible to all of
them, so the crediting rule counted a prose-shaped witness — `test_universal_claims_are_scoped_to_
what_was_measured.py`, which reads WORDING and cannot see a number — as coverage for a numeric claim.

⛔ THE REFUSED FIX, RECORDED SO IT IS NOT RE-PROPOSED. The alternative was to tighten
`claim_coverage.covered` so a numeric sentence is credited only to a numeric witness. Measured over
34 ablated sentences it had recall 8/8 and **precision 8/27 = 30%**, and it clears the red by
SHRINKING the gate's own population — the anti-gaming case `research/autonomy/amendment_guard.py:190`
names, "a bar may not be changed by the cycle it blocked". This file goes the other way: the paper
becomes more guarded and the population is untouched.

⛔ EVERY EXPECTED VALUE IS DERIVED, NEVER TYPED. A guard asserting that the word "six" appears pins a
SPELLING, not a fact; it would survive the artifact changing underneath it, which is the whole defect.
Each block below loads the artifact that owns the count, computes the word the article must print,
and checks EVERY site that prints it. A failure means the article and its evidence have diverged —
fix whichever is wrong, and never paste the current value in as a literal to make it green.

⚠ WHAT THIS FILE DELIBERATELY DOES NOT BIND, stated here rather than implied to be covered:
  · "the two to four per wing taken here as usual" (§3) — an ADOPTED convention with no retrieved
    record anywhere under `research/`; `review-backlog-2026-08-19.md` A5 already names it as one of
    three uncited literature claims, and the prose says "taken here as usual" for that reason.
    Deriving it would mean inventing an artifact to derive it from.
  · "The fourth records …" (§2) — the ordinal of a screen inside a five-item prose enumeration. No
    committed artifact orders the five screens, so the ordinal has no home; the sentence is bound
    through its parent COUNT instead, which does have one.
"""
from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
ASO = os.path.join(MANUSCRIPTS, "aso")
MOD = os.path.join(REPO, "research", "modalities")

ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")
#: The retrieved RNase-H1 gap-length record. Quotes copied from full texts on `literature-cache`;
#: this is the only home in the working branch for what PMID 24981949 actually says.
GAP_LENGTH_LIT = os.path.join(ASO, "lit-targets-aso-gap-length.json")
#: The mature-parent gap-pairing screen — owns the liability threshold, the parent list, the geometry.
GAP_PAIRING = os.path.join(MOD, "aso-parent-gap-pairing.json")
#: The exhaustive pre-mRNA scan — owns the mismatch budget.
PREMRNA = os.path.join(MOD, "aso-premrna-offtarget.json")
#: The RefSeq alignment screen — owns the near-match identity threshold the budget is matched to.
ALIGNMENT = os.path.join(MOD, "junction-aso-offtarget.json")
#: The energy re-score — owns which stage of the industry framework it is, and the named reagents.
ENERGY = os.path.join(MOD, "aso-offtarget-duplex-energy.json")
#: The coverage arms — the second, independent home for how many reagents the paper names.
COVERAGE = os.path.join(ASO, "fusion-junction-aso-reagent-coverage.json")

#: Cardinals as this article spells them. Indexed by value, so the caller writes `_word(n)` and
#: never a literal.
_CARDINAL = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
             "eleven", "twelve", "thirteen", "fourteen")


def _required(path, what):
    """⛔ A missing committed artifact is a finding, never a silent pass.

    Same rule as `test_journal_article_numbers.py`: every path here is `git ls-files`-tracked, so its
    absence is a broken tree, and `pytest.skip` on it would make this guard indistinguishable from
    one that never ran (`test_no_guard_can_silently_not_run.py`).
    """
    if not os.path.exists(path):
        pytest.fail(f"{what} is missing at {path}. It is committed, so regenerate it rather than "
                    "passing over the assertions that depend on it.")
    return path


def _word(n):
    if not 0 <= n < len(_CARDINAL):
        pytest.fail(f"the artifact gives {n}, which this article has no spelling for — the count "
                    "has moved far enough that the sentence needs rewriting, not the guard relaxing")
    return _CARDINAL[n]


@pytest.fixture(scope="module")
def prose():
    return open(_required(ARTICLE, "the journal article"), encoding="utf-8").read()


@pytest.fixture(scope="module")
def flat(prose):
    """The article with its hard wrapping collapsed.

    It is wrapped at ~100 columns, so every construction below straddles a line break in the raw
    file. Matching the flattened text keeps the patterns readable as the sentences they bind.
    """
    return re.sub(r"\s+", " ", prose)


@pytest.fixture(scope="module")
def geometry():
    """The gapmer geometry as the screen that used it records it."""
    return json.load(open(_required(GAP_PAIRING, "the mature-parent gap-pairing screen")))


def _every_site(flat_text, pattern, expected, what):
    """⛔⛔ EVERY SITE THAT STATES THE QUANTITY, NOT WHETHER IT APPEARS SOMEWHERE.

    The same rule `test_journal_article_numbers._every_site` holds, and for the same measured reason:
    a membership test (`value in prose`) stays green while ONE of several sites drifts, which is the
    one-fact-one-place defect rather than a check for it. `expected` is a string for a one-group
    pattern and a tuple for several; a pattern that matches nothing is a failure, because a guard
    whose regex has stopped reaching its sentence is a guard that cannot fail.
    """
    seen = [m.groups() if len(m.groups()) > 1 else m.group(1)
            for m in re.finditer(pattern, flat_text)]
    assert seen, (f"no site in the journal article matches the construction that states {what} "
                  f"(/{pattern}/). Either the sentence was rewritten — re-anchor this pattern — or "
                  "it was deleted, in which case say so rather than deleting the guard.")
    wrong = [s for s in seen if s != expected]
    assert not wrong, (f"{what}: the article states {wrong} at {len(wrong)} of {len(seen)} site(s) "
                       f"where its artifact gives {expected!r}")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# §1 — the RNase-H1 premise: a retrieved gap length, and this panel's own hybrid-length threshold
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_the_rnase_h1_gap_lengths_are_the_retrieved_records_own(flat, geometry):
    """⛔ "at least six nucleotides, with seven to ten the working range" — RETRIEVED, and until now
    read by nothing. A blind review seat measured exactly this in
    `PUB-ASO-…-seat-citations-and-instruments.json`: mutating "with seven to ten the working range"
    to "two to four" left `lint_citations`, `lint_claims` and every non-staleness test GREEN. The
    values are correct at the pin — they are quoted verbatim in `lit-targets-aso-gap-length.json`
    from PMID 24981949's full text on `literature-cache` — so the defect was never the number, it
    was that nothing compared the sentence to the quote it restates.

    ★ THE THREE NUMBERS COME FROM THE QUOTE, NOT FROM THIS FILE. A change to the retrieved record
    reddens the sentence, which is the direction that makes the citation load-bearing.
    ⛔ AND THE FOURTH NUMBER IN THE SAME SENTENCE IS THIS PANEL'S OWN, NOT THE LITERATURE'S — the
    article says so ("a length of hybrid rather than a count of gap nucleotides"), and it is
    `MIN_DUPLEX_BP`, carried into the screen artifact as `method.min_duplex_bp`.
    """
    lit = json.load(open(_required(GAP_LENGTH_LIT, "the retrieved gap-length record")))
    records = [r for r in lit["records"] if r.get("pmid") == "24981949"]
    assert len(records) == 1, (
        "the retrieved gap-length record no longer holds exactly one entry for PMID 24981949, which "
        f"is the source superscript 13 of the journal article resolves to; it holds {len(records)}")
    quoted = " ".join(q.get("fragment", "") + " " + q.get("context_verbatim", "")
                      for q in records[0]["quotes"])

    minima = set(re.findall(r"gap of (\w+) DNA nucleotides is necessary", quoted))
    assert len(minima) == 1, (
        f"the quotes for PMID 24981949 state minimum gap length(s) {sorted(minima)}; the article "
        "restates one value, so the record must carry one")
    ranges = set(re.findall(r"DNA gap size between (\d+) and (\d+) nucleotides is optimal", quoted))
    assert len(ranges) == 1, (
        f"the quotes for PMID 24981949 state working range(s) {sorted(ranges)}; the article "
        "restates one, so the record must carry one")
    minimum = minima.pop()
    lo, hi = (int(x) for x in ranges.pop())

    _every_site(flat,
                r"DNA gap of at least (\w+) nucleotides, with (\w+) to (\w+) the working range",
                (minimum, _word(lo), _word(hi)),
                "the RNase-H1 gap length and its working range, as PMID 24981949 is quoted stating them")

    threshold = geometry["method"]["min_duplex_bp"]
    _every_site(flat,
                r"counts a liability only at (\w+) contiguous base pairs of duplex through that gap",
                _word(threshold),
                "the hybrid length at which this panel's screen counts a liability "
                "(aso-parent-gap-pairing.json method.min_duplex_bp)")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# §2 — the five screens: how many parents the fourth one searched, and which stage the re-score is
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_the_parent_transcript_count_is_the_screens_own_parent_list(flat, geometry):
    """⛔ "any of six wild-type parent transcripts" — the size of the corpus the fourth screen ran
    over, stated in the Methods and read by nothing. It is `method.parents_searched`, whose six
    entries each carry their own searched length in `method.parent_nt_searched`; a partner gene
    entering or leaving the panel moves it, and the sentence would not have noticed.

    ⚠ THE ORDINAL "The fourth" IS NOT BOUND HERE AND IS NOT CLAIMED TO BE. No committed artifact
    orders the five screens — the enumeration exists only in this paragraph — so binding it would
    mean pinning the paragraph's own prose to itself. It is named in the module docstring as open.
    """
    parents = geometry["method"]["parents_searched"]
    assert isinstance(parents, list) and parents, (
        "the gap-pairing screen records no parent list, so this guard has nothing to bind to")
    assert len(parents) == len(set(parents)), f"the screen's parent list repeats a gene: {parents}"
    _every_site(flat,
                r"longest contiguous duplex any of (\w+) wild-type parent transcripts",
                _word(len(parents)),
                "the number of wild-type parent transcripts the mature-parent screen searched "
                f"({', '.join(parents)})")


def test_the_energy_rescore_is_the_stage_its_own_artifact_says_it_is(flat):
    """⛔ "the energy-based second stage adopted here" — an ordinal inside the industry framework
    (PMID 39912803), and the artifact that IMPLEMENTS that stage states which one it is:
    "This panel had the first stage and not the second." The manuscript's ordinal is read off that
    sentence rather than typed, so a re-description of the framework in the artifact reddens the
    paper instead of silently disagreeing with it.

    ⚠ THIS BINDS PROSE TO PROSE INSIDE AN ARTIFACT, which is weaker than binding to a field, and it
    is the strongest binding available: the stage index is not carried as a value anywhere. Recorded
    as such rather than dressed up — if `aso_offtarget_duplex_energy.py` ever emits the index as a
    field, this should move onto it.
    """
    energy = json.load(open(_required(ENERGY, "the duplex-energy re-score")))
    staged = re.findall(r"had the (\w+) stage and not the (\w+)", energy.get("_why", ""))
    assert len(staged) == 1, (
        "the duplex-energy artifact no longer states which stage of the off-target framework it is "
        f"(found {staged!r} in `_why`), so the manuscript's ordinal has no home. Restore the "
        "statement in the artifact; do not type the ordinal here.")
    _had, _is = staged[0]
    _every_site(flat, r"the energy-based (\w+) stage adopted here", _is,
                "which stage of the 2025 off-target framework the energy re-score is")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# §2/§3 — the locked wings: what the geometry implies, stated twice in two different sentences
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_the_locked_residue_floor_is_the_geometrys_own(flat, geometry):
    """⛔ "the fusion duplex pairs all ten locked residues where each parent pairs five" — the ONLY
    quantitative thing the Methods say about the thermodynamics, since no absolute melting point is
    reported. Both numbers fall straight out of the wing length: a 5-6-5 design carries `2 * wing`
    locked residues, and a wild-type parent supplies one side of the junction, so it can reach one
    wing. Nothing read either.

    ★ The energy artifact states the same fact in its own words ("The intended duplex pairs all ten
    locked residues of a 5-6-5 design"), and the two are cross-checked here so this guard cannot be
    satisfied by a geometry the re-score never ran at.
    """
    wing = int(geometry["_geometry"]["wing"])
    architecture = geometry["_geometry"]["architecture"]
    assert architecture.startswith(f"{wing}-"), (
        f"the screen's architecture string {architecture!r} does not open with its own wing length "
        f"{wing}; the geometry block disagrees with itself, so nothing downstream of it is safe")
    energy = json.load(open(_required(ENERGY, "the duplex-energy re-score")))
    assert int(energy["method"]["geometry"]["wing"]) == wing, (
        "the gap-pairing screen and the duplex-energy re-score ran at different wing lengths "
        f"({wing} vs {energy['method']['geometry']['wing']}), so the sentence they jointly support "
        "is about neither of them")
    _every_site(flat,
                r"the fusion duplex pairs all (\w+) locked residues where each parent pairs (\w+)",
                (_word(2 * wing), _word(wing)),
                "the locked residues the intended duplex pairs and the one wing a parent can reach, "
                f"from the {architecture} geometry both screens ran at")


def test_the_reagent_wing_the_chemistry_paragraph_states_is_the_geometrys_own(flat, geometry):
    """⛔ "wings of five contiguous β-D-oxy-locked residues" — §3's chemistry paragraph restating the
    Methods geometry, and the sentence the hepatotoxicity premise then hangs off. A drift here would
    put the paper's own safety discussion on a molecule it never screened.

    ⛔ WHAT IS NOT BOUND, AND MUST NOT BE FAKED: the same sentence's "against the two to four per
    wing taken here as usual" is an adopted convention with NO retrieved record in this repository
    — `review-backlog-2026-08-19.md` A5 names it as one of three uncited literature claims, and the
    prose flags it as adopted. Binding it would require typing the number here, which is precisely
    the failure this file exists to avoid. It stays open, and is reported as open.
    """
    wing = int(geometry["_geometry"]["wing"])
    _every_site(flat,
                r"with wings of (\w+) contiguous β-D-oxy-locked residues",
                _word(wing),
                "the locked wing length of the reagents, from the geometry the panel was tiled at")


def test_the_mismatch_ceiling_is_the_two_search_screens_own(flat):
    """⛔ "the two-mismatch ceiling the near-match screens run at" — §3's argument that a high-affinity
    chemistry may retain activity past the screens' own sensitivity. The whole caveat is calibrated
    on that number, and it is stated in words, so no digit-harvesting guard could see it.

    ★ TWO ARTIFACTS OWN IT AND THEY MUST AGREE. The pre-mRNA scan carries the budget directly
    (`method.max_mismatches`); the RefSeq alignment screen carries the identity threshold it was
    matched to (`method.near_match_threshold`, ">= 14/16 identical"), and 16 - 14 is the same
    number. Checking the pair is not decoration: `aso-premrna-offtarget.json` says in its own
    `why_this_threshold` that the two arms exist to "describe the same liability class", and a
    silent divergence between them would make the article's plural "screens" false.
    """
    premrna = json.load(open(_required(PREMRNA, "the exhaustive pre-mRNA scan")))
    alignment = json.load(open(_required(ALIGNMENT, "the RefSeq alignment screen")))
    budget = int(premrna["method"]["max_mismatches"])
    threshold = alignment["method"]["near_match_threshold"]
    m = re.match(r">=\s*(\d+)\s*/\s*(\d+) identical", threshold)
    assert m, (f"the alignment screen states its near-match threshold as {threshold!r}, which this "
               "guard cannot read as an identity fraction — re-anchor it rather than dropping the "
               "cross-check, because the article's plural 'screens' depends on the two agreeing")
    identical, length = int(m.group(1)), int(m.group(2))
    assert length - identical == budget, (
        f"the alignment screen admits {length - identical} mismatch(es) at {threshold!r} while the "
        f"pre-mRNA scan admits {budget}; they no longer describe the same liability class, so the "
        "article's single 'two-mismatch ceiling' is not a property of both")
    _every_site(flat, r"so the (\w+)-mismatch ceiling the near-match screens run at", _word(budget),
                "the mismatch ceiling both near-match screens run at")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# §3 — how many reagents the paper actually names
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_the_named_reagent_count_is_the_artifacts_own(flat):
    """⛔ "which published junctions the two reagents address" — the coverage sentence, immediately
    after the 68.4% the whole Results section turns on. The percentage is bound; the count of
    reagents it is a percentage FOR was not, so the panel could gain or lose an arm and this
    sentence would keep saying two.

    ★ TWO INDEPENDENT ARTIFACTS, CHECKED AGAINST EACH OTHER. `aso-offtarget-duplex-energy.json`
    names the reagents it re-scored; `fusion-junction-aso-reagent-coverage.json` carries one arm per
    reagent and is what the 68.4% is computed from. They must name the same junctions, or the
    coverage figure is not about the reagents the screens measured.
    """
    energy = json.load(open(_required(ENERGY, "the duplex-energy re-score")))
    coverage = json.load(open(_required(COVERAGE, "the reagent-coverage artifact")))
    named = set(energy["named_reagents"])
    arms = {a["reagent_junction"] for a in coverage["arms"]}
    assert named == arms, (
        f"the re-scored named reagents {sorted(named)} are not the coverage arms {sorted(arms)}; the "
        "coverage figure and the screens are about different molecules")
    _every_site(flat, r"which published junctions the (\w+) reagents address", _word(len(arms)),
                "the number of named reagents the coverage figure prices")
