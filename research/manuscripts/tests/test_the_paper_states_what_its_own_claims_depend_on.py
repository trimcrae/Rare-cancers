"""⛔⛔ ABSENCE HAS NO ANCHOR — the one defect class no pattern-matching guard can find by itself.

Every other guard in this suite asks "is this sentence right?". None of them can ask "is the sentence
there at all?", because a deleted sentence matches nothing and fires nothing. Round 14 produced two
BLOCKERS of exactly that shape, both created by the six-page length cut:

  * **A gapmer paper at an oligonucleotide-therapeutics journal that never states its own chemistry.**
    Measured at the pin: `phosphorothioate` 0, `methylcytosine` 0, `CpG` 0, `Tm` 0 — while the same
    PDF printed a specific 16-mer six times. Two `phosphorothioate` mentions had existed and the cut
    removed both. A reader could not have ordered the molecule the paper is about.
  * **§5's void figure was deleted, orphaning the sentence that needed it.** The gate says a decision
    turns on "the void figure for the count proposed", a per-replicate-count quantity — and the cut
    left the paper printing it for exactly one count.

★ THE RULE THIS ENCODES: **a paper must state the things its own claims depend on.** Each requirement
below exists because some OTHER sentence in the paper, or the genre itself, is unreadable without it —
and each names that reason. This is not style enforcement and must not become a topic wish-list: a
requirement whose absence would not break another claim does not belong here.

⚠ WHY IT IS A KEYWORD CHECK AND WHY THAT IS ACCEPTABLE HERE. Everywhere else this suite binds a claim
to the artifact that decides it, because a keyword check cannot tell right from wrong. For ABSENCE it
can: the question is only "is the subject raised", and a paper that raises it wrongly is caught by
the guards that do read values. Alternations stay wide for that reason.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import claim_coverage  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")
COVERAGE = os.path.join(ASO, "claim-coverage.json")

#: (label, pattern, why its ABSENCE would break something else in the paper)
REQUIRED = [
    # ⛔⛔ THIS ALTERNATION ACCEPTED EITHER BACKBONE (round 16 seat 5). "Both reagents are
    # phosphodiester throughout" satisfied the guard whose entire purpose is that the paper states
    # the chemistry a reader must order — so the one guard on the subject passed a paper naming the
    # WRONG one. A presence check standing in for a correctness check.
    # ★ The canonical file's header states the linkage; only that word counts.
    ("the backbone chemistry",
     r"phosphorothioate",
     "§2 names two 16-mers for synthesis and §8 gives only the SUGAR geometry. Without the backbone "
     "a reader cannot order the molecule the paper is about, and round 14 shipped exactly that: "
     "zero mentions in a PDF that printed a specific sequence six times."),
    ("the gapmer geometry",
     r"5-6-5|five-six-five",
     "every liability count in the paper is a count over designs of one geometry; the rate is "
     "meaningless without it."),
    ("the cleavage mechanism the gap is for",
     r"RNase[- ]?H1?",
     "the whole selection rule is 'a parent pairs the CATALYTIC GAP'. Why a gap has a catalytic "
     "role at all is unstated without this."),
    ("the duplex criterion the counts are taken at",
     r"ten[- ]base[- ]pair|10\s*bp|ten or more contiguous base pairs",
     "87 of 190 is a different number at every cut — 175 of 190 at seven. The count without its "
     "criterion is not a result (round 15 BLOCKER)."),
    ("a chance baseline for the headline rate",
     r"null|chance|scramble|chimera",
     "§3's own argument is that the observed rate is not resolved against a chimeric null. A rate "
     "printed with no baseline reads as a finding."),
    ("the threshold the falsification experiment turns on",
     r"cut of \d|threshold",
     "§5 exists to name an experiment that could falsify the ranking. An experiment with no "
     "decision rule cannot falsify anything, and the cover letter tells the editor it has one."),
    # ⛔⛔ THE ARTIFACTS DENY THESE IN THEIR OWN PROSE AND NOTHING READ THE PAPER FOR THEM (round 16
    # seat 3, P1-b). Across the committed record, `_what_this_is_not` fields deny safety 56 times,
    # efficacy 50, selectivity 39 — and also knockdown, tolerability, delivery, a significance test
    # and a cleavage measurement, SEVEN of which `lint_claims` does not name. Measured: the paper is
    # honest about every one of them today, each appearing only in a denying or design frame. So the
    # risk is not a wrong claim, it is DELETION — absence fires no other guard in this suite, and a
    # length cut that removed either sentence would turn an honest paper into one that over-claims
    # by omission, with every remaining number still correct.
    # ★ This is what turning an artifact's own denial into an assertion looks like: not a ban on the
    # words, which would red on honest usage, but a floor under the sentences that do the denying.
    ("that the work is computational and the reagents are not for administration",
     r"work is computational[^.]{0,120}not for administration",
     "the artifacts' `_what_this_is_not` fields deny safety 56 times, efficacy 50 and selectivity "
     "39 across the committed record. ⚠ MEASURED, AND THE ANSWER WAS NOT THE EXPECTED ONE: the "
     "words 'efficacy', 'potency', 'therapeutic window' and 'clinical readiness' appear NOWHERE in "
     "the delivered journal PDF — that explicit denial list is carried by the extended report and "
     "by front matter the builder strips, and the condensed paper is narrower by page budget. So "
     "the floor is the sentence the reader actually receives, in the abstract, which is what stops "
     "a length cut turning an honest paper into one that over-claims by omission."),
    ("that the screens address hybridisation, not cleavage",
     r"hybridi[sz]ation rather than cleavage",
     "every screen in the paper is a sequence-pairing calculation, and no RNase-H1 assay exists in "
     "this repository. Without this sentence a reader takes a predicted duplex for a demonstrated "
     "cut, which is the single largest over-reading the whole design invites."),
    ("where the artefacts are",
     r"zenodo|doi:",
     "every number in the paper is claimed to re-derive from released artefacts; without the "
     "pointer that claim is unfalsifiable."),
    ("that nothing was synthesised or tested",
     r"has been synthesi[sz]ed|nothing (?:here )?(?:has been|was) synthesi[sz]ed|not for administration",
     "the scope bound. A paper naming orderable reagents without it reads as a wet-lab report."),
]


@pytest.fixture(scope="module")
def prose():
    """What a READER RECEIVES — the built PDF's text layer, not the markdown source.

    ⛔⛔ THIS READ THE RAW FILE, AND THAT REINSTATED ROUND 14'S BLOCKER VERBATIM (round 16 seat 5,
    2026-08-22). The builder strips HTML comments, so moving the paper's only printed mention of the
    backbone into `<!-- ... -->` left this guard green against the source while the REBUILT PDF
    contained ZERO occurrences — which is exactly round 14's defect: a PDF that prints a specific
    sequence six times and never says what chemistry to order it in.
    ★ The requirement is about the delivered document, so the delivered document is what is read.
    """
    pdf = os.path.join(ASO, "fusion-junction-aso-journal-article.pdf")
    assert os.path.exists(pdf), (
        f"the built journal PDF is missing: {pdf}. It is a committed artifact, so its absence is a "
        "broken tree, and these requirements are about what a reader receives.")
    try:
        from pdfminer.high_level import extract_text
    except ImportError as exc:  # pragma: no cover - CI installs it; a miss is a finding
        pytest.fail(
            f"pdfminer.six is not importable ({exc}), so nothing read the delivered PDF and every "
            "requirement below asserted nothing. A guard that cannot run is not a guard that passed.")
    text = re.sub(r"\s+", " ", extract_text(pdf))
    assert len(text) > 5000, (
        f"the journal PDF's text layer came out at {len(text)} characters, which is not a six-page "
        "paper. Every requirement below would pass or fail on an empty read.")
    return text


@pytest.mark.parametrize("label,pattern,why", REQUIRED, ids=[r[0] for r in REQUIRED])
def test_the_article_states_it(label, pattern, why, prose):
    assert re.search(pattern, prose, re.I), (
        f"the journal article no longer states {label}.\n\nWHY THAT MATTERS: {why}\n\n"
        "⛔ IF A LENGTH CUT REMOVED IT, THE CUT IS THE DEFECT. Absence fires no other guard in this "
        "suite — a deleted sentence matches nothing — which is why this file exists and why two "
        "round-14 blockers were both deletions.")


# ---------------------------------------------------------------------------------------------
# ⛔ AND A RATCHET, so the census is a gate rather than a tool nobody runs.
# ---------------------------------------------------------------------------------------------

#: Measured 2026-08-22 by `python3 research/manuscripts/claim_coverage.py --write`, the first run
#: after its selectivity filter was added. These are FLOORS, not targets: coverage may rise freely
#: and may not fall. ⚠ Raising a floor is a deliberate act — do it when you have closed a class, and
#: never to make a red run green.
COVERAGE_FLOOR = {"journal-article": {"covered": 66, "with_a_number_covered": 44},
                  "journal-tables": {"covered": 4, "with_a_number_covered": 1},
                  "cover-letter": {"covered": 6, "with_a_number_covered": 4}}
#: ⛔ `journal-article.covered` 67 -> 66 ON 2026-08-24, SAME DAY, AND FOR A DELETED SENTENCE AGAIN.
#: trimcrae removed his diagnosis from the whole submission envelope, so the manuscript's pointer
#: sentence — "a non-financial interest is disclosed to the editor in the accompanying cover
#: letter" — had to go with it: with the letter no longer declaring one, that sentence would have
#: been false in a published paper. It was bound (by test_the_envelope_declares_one_interest.py),
#: so removing it costs one covered sentence, and the cover letter's own census falls 11 -> 10 for
#: the same edit. ⚠ The ratchet's remedy was checked and does not apply: the sentence is GONE, not
#: reworded, and re-anchoring a guard to a sentence the author deleted is not available.
#: ⛔⛔ `journal-article.covered` 68 -> 67 ON 2026-08-24, AND THE CAUSE IS A DELETED SECTION.
#: This is the THIRD documented downward correction, and like both before it, it is licensed by a
#: measurement rather than by a red run. In order, because the order is the lesson:
#:   1. trimcrae capped publication spend at $600. The condensed article is charged per typeset page,
#:      so the six-page budget stopped being a preference and became the cap; the reviewer-requested
#:      Tm column and the measured exon-numbering finding had pushed the build to seven pages.
#:   2. Section 6 ("Beyond the panel") was cut on his instruction — measured as exactly the cut that
#:      returns the article to six pages. It carried THREE covered sentences.
#:   3. One of its claims survived, reworded into the abstract ("Also released is the procedure that
#:      produced the 190 designs"), and is covered there. Net: -3 +1 = -2 covered.
#:   4. ⚠ THE RATCHET'S OWN REMEDY WAS CHECKED FIRST AND DID NOT APPLY. It says to find the reworded
#:      sentence and re-anchor rather than lower the floor. All three sentences were confirmed ABSENT
#:      from the document by literal substring search, not reworded past a pattern — a section the
#:      author removed cannot be re-anchored to a document that no longer contains it.
#:   5. ★ AND THE MEASURE THAT MATTERS DID NOT MOVE: 69/129 = 53.5% before, 67/126 = 53.2% after.
#:      The paper got SHORTER; its binding to artifacts did not get looser. An absolute floor cannot
#:      tell those two apart, which is the one real limitation of this ratchet and is recorded here
#:      rather than designed around, because a ratio floor would let a paper shed bound sentences
#:      and unbound ones together and still read green.
#: ⛔⛔ `cover-letter.covered` 7 -> 6 ON 2026-08-23, AND THE SEVENTH WAS THE STRING "sub-miss-ion".
#: This is the second documented downward correction and, like the first, it is licensed by a
#: measurement rather than by a red run. What happened, in order, because the order is the lesson:
#:   1. The letter was edited (a false bioRxiv statement removed) and `covered` fell 7 -> 6.
#:   2. This ratchet fired and printed its own remedy: find the reworded sentence, do NOT lower the
#:      floor. ⚠ THE SENTENCE HAD NOT BEEN REWORDED. It is byte-identical in both versions —
#:      confirmed by censusing the pre-edit letter inside a `claim_ablation` clone, which is the
#:      only way to census an old revision, since witness discovery greps for the BASENAME.
#:   3. The sentence was credited to `test_the_manuscript_title_states_the_measurement_it_carries.py`
#:      by one harvested pattern: `...|miss(?:es|ed)?|...` WITH NO WORD BOUNDARIES, matching the
#:      middle of "sub**miss**ion". All five of its hits in the letter were the word "submission".
#:   4. The edit added sentences containing "submission", the pattern crossed `MAX_MATCH_SHARE`, and
#:      the census dropped it as non-selective — which is the selectivity filter working correctly
#:      and by accident, since the pattern was never selective and the document merely grew.
#: ★ THE FIX WENT INTO THE GUARD, NOT THE FLOOR: `_PAIRING_VERBS` and `_SPARING_VERBS` are now
#: `\b`-bounded (and refuse a hyphen-introduced "pair", because `\b` alone still matches the unit
#: inside "ten-base-pair"). ⛔ That mattered in the OTHER direction too, which is the part worth
#: keeping: unbounded `clear(?:s|ed)?` matches inside "nu**clear**", and a title of this paper —
#: about an orphan NUCLEAR receptor — would have failed a guard that says the title asserts the
#: inverse of the central negative. A gate that reds on true input is the worse failure.
#: ⛔ SO 6 IS THE TRUE READING AND 7 NEVER WAS. Do not read this entry as permission to lower a
#: floor that falls: the license here is (a) the sentence was proven unchanged, (b) the crediting
#: pattern was proven to be a substring artifact, and (c) the artifact was FIXED. Absent all three,
#: a falling floor is the regression it looks like.
#: ⛔⛔ THESE FLOORS WERE SET ON INFLATED NUMBERS AND ARE NOW CORRECTED DOWNWARD (round 16 seat 4).
#: The first ratchet read 82/53 and 27/15. Those came from a census that applied EVERY test file's
#: patterns to EVERY document, so a pattern from a test that never opens the cover letter could mark
#: a cover-letter sentence covered. Scoped to the tests that actually name each document, the true
#: readings are 51/40 and 6/3 — the letter was over-reported by more than four times, and the seat
#: reviewing it reached ~5 by hand-audit independently.
#: ⚠ SO THE MAP THE ROUND WAS PLANNED FROM WAS TOO OPTIMISTIC, AND IN THE DANGEROUS DIRECTION:
#: inflating COVERED shrinks UNCOVERED, which HIDES surfaces. The uncovered work lists handed to the
#: seats were SUBSETS of the truth. Their findings stand; the residue is larger than they were told.
#: ⛔ A FLOOR LOWERED IS NORMALLY THE FAILURE THIS RATCHET EXISTS TO STOP. It is legitimate here for
#: one reason only: the MEASUREMENT changed, not the coverage. No binding was removed. Lowering a
#: floor because a run went red would be the defect; lowering it because the instrument was proved
#: wrong is the correction. Say which, in the commit, every time.
#: ⛔⛔ THE PARAGRAPH THAT STOOD HERE DESCRIBED A STATE THIS FILE HAD ALREADY FIXED (round 17 seat A,
#: 2026-08-23). It said journal-tables "sits at 0 of 9", is "DELIBERATELY ABSENT rather than pinned at
#: zero", that "only two test files name that document" and that "of 34 in-scope patterns exactly one
#: matches anything" — every number wrong, and contradicted by the FLOOR CONSTANT THREE LINES ABOVE
#: IT, which pins that document at 4/1. Measured now: 4 of 10, six test files naming it, 90 in-scope
#: patterns. ⚠ Narration ages; a constant does not. When they disagree the constant is the reading and
#: the prose is the bug — which is this suite's own subject, committed into its own margin.
#:
#: ⛔⛔ AND THESE FLOORS MOVED DOWN A SECOND TIME (51/40 -> 44/33), WHICH IS TWICE IN ONE SESSION AND
#: MUST NOT BECOME A HABIT. The cause is again the instrument, not the coverage: the census counted a
#: pattern as binding if it matched FEW sentences, when the property needed is that it DISTINGUISHES
#: one — so bold spans, code spans, an ISO date and a whitespace pattern were all scored as coverage.
#: ★ Unlike the first correction, this one is not argued from inspection. Six of the seven numbered
#: sentences that lost their only witness were ABLATED — the number perturbed in the real file, the
#: named witness re-run — and all six stayed green. Their coverage was false. That evidence is what
#: licenses the lower floor, and `test_the_census_word_covered_survives_ablation.py` keeps taking it.


def test_claim_coverage_has_not_regressed():
    """⛔ A TOOL THAT NOBODY RUNS PROTECTS EXACTLY AS MUCH AS A BROKEN ONE.

    `claim_coverage.py` exists because fifteen rounds of iteration could not converge while surfaces
    with zero instruments kept being discovered one lens at a time. Its value is entirely in being
    re-run: a rewrite that drops a bound construction silently un-covers the sentence it bound, which
    is the same failure the census was written to expose.
    """
    if not os.path.exists(COVERAGE):
        pytest.fail("claim-coverage.json is missing — run "
                    "`python3 research/manuscripts/claim_coverage.py --write` and commit it")

    # ⛔⛔ THIS RATCHET USED TO COMPARE TWO COMMITTED CONSTANTS AND MEASURE NOTHING (round 16 seat 5,
    # 2026-08-22). It read the committed `claim-coverage.json` and compared it to the floors above —
    # both checked-in values. A census change regenerates the JSON with `--write`, so the artifact and
    # the floor move together and the gate stays green through exactly the regression it exists to
    # catch. A populated field is not a measured one.
    # ★ The census is now RUN HERE, and the committed artifact is checked against that live reading,
    # so a stale deposit artifact fails as loudly as a lost binding.
    live = {}
    for paper in COVERAGE_FLOOR:
        rows = claim_coverage.census(paper)
        numbered = [r for r in rows if r["has_number"]]
        live[paper] = {"covered": sum(1 for r in rows if r["covered"]),
                       "with_a_number_covered": sum(1 for r in numbered if r["covered"])}

    committed = json.load(io.open(COVERAGE, encoding="utf-8"))["papers"]
    stale = [f"{p}.{f}: committed {committed.get(p, {}).get(f)!r}, census now reports {v!r}"
             for p, fields in live.items() for f, v in fields.items()
             if committed.get(p, {}).get(f) != v]
    assert not stale, (
        "claim-coverage.json disagrees with what claim_coverage.py now computes:\n  "
        + "\n  ".join(stale)
        + "\n\nThe committed census is a deposit artifact and is out of date. Re-run "
          "`python3 research/manuscripts/claim_coverage.py --write` and commit it in this change.")

    got = live
    regressed = []
    for paper, floors in COVERAGE_FLOOR.items():
        for field, floor in floors.items():
            now = got.get(paper, {}).get(field)
            if now is None:
                regressed.append(f"{paper}.{field} is no longer reported by the census")
            elif now < floor:
                regressed.append(f"{paper}.{field}: {now} < floor {floor}")
    assert not regressed, (
        "fewer sentences are read by a selective instrument than when the floor was set:\n  "
        + "\n  ".join(regressed)
        + "\n\nSomething that used to be bound is not any more. Find what stopped matching — a "
          "reworded sentence usually — and re-anchor the guard to it. Do NOT lower the floor.")
