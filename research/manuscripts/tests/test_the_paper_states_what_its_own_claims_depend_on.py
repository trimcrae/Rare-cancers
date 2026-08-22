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
    ("the backbone chemistry",
     r"phosphorothioate|phosphodiester",
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
    return re.sub(r"\s+", " ", io.open(ARTICLE, encoding="utf-8").read())


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
                  "cover-letter": {"covered": 7, "with_a_number_covered": 4}}
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
#: ⛔ journal-tables sits at 0 of 9 and is DELIBERATELY ABSENT rather than pinned at zero: a floor of
#: zero reads as covered-enough. It is an open finding — and round 16 established WHY it is zero, which
#: is worse than the arithmetic bug first suspected: only two test files name that document, no pin is
#: homed to it, and of 34 in-scope patterns exactly one matches anything (`5′|[.;:]`, a punctuation
#: splitter hitting all nine sentences). The display items the journal article cites have essentially
#: no instruments.
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
