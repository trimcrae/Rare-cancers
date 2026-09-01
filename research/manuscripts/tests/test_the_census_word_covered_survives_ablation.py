"""Does "covered" survive being tested? The census's own claim, ablated.

⛔⛔ WHY THIS GATE EXISTS — THE ROUND-16 DIAGNOSIS, WHICH IS ABOUT THE REVIEW PROCESS ITSELF.

`claim_coverage.py` was written after fifteen review rounds would not converge. Every blocker was a
surface with ZERO instruments, so the blocker rate tracked how many new LENSES a round introduced,
not how many defects the paper held. The fix was to enumerate surfaces instead of sampling them.

Round 16 pointed three seats at the enumerator and found the SAME defect one level up: the census
credited a guard's regexes to documents that guard never opens (22 of 27 "covered" cover-letter
sentences were false positives), its selectivity threshold could not be represented on a nine-
sentence document, and it scored "matches few sentences" where "distinguishes this sentence" was
meant — so bold spans, code spans and an ISO date counted as coverage.

★★ THE STRUCTURAL FINDING. Every fix ships a NEW INSTRUMENT, and every new instrument is a new claim
asserted in prose and measured nowhere. Each round's fix REFILLS the pool the next round drains, so
iteration cannot converge: reviewing instruments by READING them never catches up with writing them.
This is CLAUDE.md's "a property asserted in prose about a value passed by a caller is not a property;
it is a hope", applied to the review process rather than to a workflow.

★ WHAT CHANGES THE SHAPE. "Sentence S is covered by witness W" is FALSIFIABLE IN ONE OPERATION: it
predicts that if S changed, W would go red. So change it and look. This gate is different in kind
from the fixes that preceded it — it introduces NO new hand-written constant, and it derives its
expectation from the census's OWN output, so it cannot drift from what the census claims.

⛔⛔ AND THE FIRST VERSION OF THIS MEASUREMENT WAS ITSELF FABRICATED, WHICH IS WHY THE CONTROL BELOW
IS NOT OPTIONAL. `ablate()` located sentences with `sentence in text`; the flattener joins lines, so
nothing ever matched, no mutation ever landed, and seven guards were reported BLIND on the strength
of a file that was never edited. The reading was about to justify narrowing the census. It was caught
by asking "can this harness produce a RED at all?" — not by any run going red.
★ SO: a sample in which nothing was applied FAILS here. An absent reading is not a reading of absence.
"""
from __future__ import annotations

import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import claim_ablation  # noqa: E402
import claim_coverage  # noqa: E402

#: Ablation runs the real guards in subprocesses, so it is priced per sentence. A bounded, evenly
#: spaced sample runs per commit; `PREFLIGHT_FULL=1` takes every numbered covered sentence.
SAMPLE = 6

#: ⛔⛔ THE DOCUMENTS ABLATED ARE THE ONES CARRYING A MEASURED COVERAGE FLOOR, AND THIS MODULE MUST
#: NOT NAME A MANUSCRIPT ANYWHERE IN ITS SOURCE — INCLUDING IN A CONSTANT (measured 2026-08-26).
#: `claim_ablation.guards_reading` collects every test module whose SOURCE contains a document's
#: basename and re-runs it inside the ablation clone. A first attempt at widening the census wrote
#: the three papers here as literal paths; that made THIS module a witness of the journal article,
#: so every ablation re-ran the module that performs ablations, inside a clone, without bound. The
#: symptom was not a failure: it was a preflight whose pytest stage produced no output for twenty
#: minutes while nine 19-module pytest subprocesses stacked up. Verified against HEAD, where the
#: same grep returns zero.
#: ★ `claim_coverage.COVERAGE_FLOOR` lives in the census module, which is not scanned for patterns
#: or for witnesses, so reading the scope from there names nothing here. It is also the honest
#: predicate: the documents whose coverage is HELD are exactly the ones whose "covered" is a claim
#: worth falsifying.
#: ⚠ A DOCUMENT WITH NO FLOOR IS NOT ABLATED, and that is a cost decision rather than a claim about
#: it. Ablation runs the real guards in subprocesses per sentence; the census is a ~1.5 s pure-CPU
#: screen. An unfloored document has its coverage counted and its committed count checked for
#: staleness, but never falsified by perturbation.
#: ⛔ NO DOCUMENT IS OUT. Individual SENTENCES with a recorded census false positive are skipped by
#: `_sample` below, with the counterexample written into the census module rather than this gate
#: relaxed — `claim_coverage.ABLATION_BLOCKED_BY_A_KNOWN_FALSE_POSITIVE` carries the sentence, the
#: crediting pattern and the perturbation that proved nothing notices. Widening the ablation scope to
#: the floored documents is what FOUND the first one, on the first run.
#: ⚠ IT USED TO BE A DOCUMENT, AND THE COST WAS MEASURED ON 2026-08-27 (AUT-PROP-025). One recorded
#: blind sentence took a 269-sentence manuscript out of this gate entirely. A `PREFLIGHT_FULL=1`
#: sweep of all 76 of its covered numbered sentences returned `applied=71 blind=3 skipped=5`: the
#: recorded sentence is still blind, two more are blind for the identical reason, and 68 go red — so
#: 68 falsifiable claims were going unfalsified to buy cover for three that are not. All three blinds
#: are named in the census module with their perturbations; the document is back in the gate.
#: An exemption should cost what the defect costs and no more.
PAPERS = tuple(claim_coverage.COVERAGE_FLOOR)


def _sample(rows, paper):
    """Deterministic, evenly spaced — never random: a flaky gate teaches people to re-run it.

    ⛔ THE EXEMPTED SENTENCES COME OUT BEFORE THE SPACING, NOT AFTER, so a document does not lose a
    sample slot to a sentence this gate has already agreed not to ask about.

    ⛔⛔ THE POPULATION IS "STATES A QUANTITY", NOT "CONTAINS A DIGIT" (AUT-PD-148, 2026-09-01). This
    line used to read `re.search(r"\\d", r["sentence"])`, which is the SECOND of the two copies of
    that rule — the first was in `claim_ablation.ablate` — and a sentence had to pass BOTH for its
    quantity to be tested at all. So a claim written in words was unfalsifiable twice over: the
    harness said "the sentence states no number" and this gate never offered it.
    ★ MEASURED, AND THE CASE THAT DISCRIMINATES IS A SENTENCE THAT IS WELL GUARDED:
      "*FUS* is a further reported partner, in two of five variant cases in a recent series, and
       supplies eight of the junctions modelled here."
      before  ablate -> not-applied, "the sentence states no number"
      after   ablate -> applied, "two -> six", RED — 25 guard modules noticed, including the one
              written for that very clause, which reads the two and the five out of a committed
              abstract quotation.
    So the old reading was not "this claim is unwatched"; it was the instrument declining to look at
    a claim that IS watched. The predicate now has one home, `claim_ablation.states_a_quantity`.
    """
    covered = [r for r in rows if r["covered"]
               and claim_ablation.states_a_quantity(r["sentence"])
               and not claim_coverage.ablation_exempt(paper, r["sentence"])]
    if os.environ.get("PREFLIGHT_FULL") or len(covered) <= SAMPLE:
        return covered
    step = len(covered) / SAMPLE
    return [covered[int(i * step)] for i in range(SAMPLE)]


@pytest.mark.parametrize("paper", PAPERS)
def test_a_covered_sentence_has_a_witness_that_actually_goes_red(paper):
    """⛔ THE CENSUS SAYS THIS SENTENCE IS WATCHED. CHANGE IT AND SEE WHO NOTICES.

    A witness that stays green when the number moves was never binding the sentence. That inflates
    `covered`, which shrinks the UNCOVERED list, which HIDES surfaces — the comfortable direction,
    and therefore the one to distrust.
    """
    rows = _sample(claim_coverage.census(paper), paper)
    assert rows, (
        f"the census reports no covered sentence stating a number in {paper}, so this gate has "
        "nothing to ablate and its silence would mean nothing. Either every numbered claim in that "
        "document has lost its witness — the regression this suite exists to catch — or the census "
        "stopped reading the file.")

    blind, applied, skipped = [], 0, []
    for row in rows:
        result = claim_ablation.ablate(paper, row)
        if result["status"] != claim_ablation.APPLIED:
            skipped.append((row["sentence"], result["reason"]))
            continue
        applied += 1
        if not result["red"]:
            blind.append((row["sentence"], row["read_by"], result["reason"]))

    # ⛔ THE CONTROL, AND IT COMES FIRST. If nothing was applied, "no blind guards" is not a result —
    # it is the harness failing to edit the file, which is exactly how this measurement was
    # fabricated once already.
    assert applied, (
        f"not one of {len(rows)} sampled {paper} sentences could be perturbed, so this gate measured "
        "NOTHING and its silence means nothing:\n  "
        + "\n  ".join(f"{s[:90]!r}\n      {why}" for s, why in skipped[:6])
        + "\n\nThe census and the file have diverged — usually `claim_coverage.sentences()` building "
          "a sentence that has no home in the raw document. Fix the splitter, not this floor.")

    assert not blind, (
        f"{len(blind)} of {applied} perturbed {paper} sentences changed their number and NO witness "
        "the census names went red:\n  "
        + "\n  ".join(f"{s[:90]!r}\n      census credits: {', '.join(w)}\n      perturbed: {why}"
                      for s, w, why in blind)
        + "\n\nThose sentences are counted as covered and are not. Either bind them for real, or the "
          "pattern that claims them is structure rather than content — see "
          "`claim_coverage._binds_literal_text`. Do not lower the coverage floor to match.")


def _first_paper_whose_covered_numbers_are_pinned():
    """The known-binding calibration case, FOUND rather than named — this module names no manuscript.

    A pin is enforced by `lint_consistency.py` for every document it is homed to, so a censused
    sentence credited to one is the case where a red is guaranteed if the harness works at all.
    Which document supplies it does not matter; that one exists does.
    """
    for paper in PAPERS:
        pinned = [r for r in claim_coverage.census(paper)
                  if r["covered"] and re.search(r"\d", r["sentence"])
                  and any(w.startswith("pin:") for w in r["read_by"])]
        if pinned:
            return paper, pinned[0]
    pytest.fail(
        "no censused sentence in any floored document is credited to a pin, so this suite has no "
        "known-binding case to calibrate against. Every ablation verdict is uncalibrated.")


def test_the_ablation_harness_can_produce_a_red_at_all():
    """⛔⛔ THE POSITIVE CONTROL, AS ITS OWN TEST, BECAUSE ITS ABSENCE ONCE FABRICATED A READING.

    Everything above is an argument from a GREEN run: "the witness did not go red, therefore it
    binds." That argument is worth nothing unless this harness can go red on demand. A pinned figure
    stated in the article is the known-binding case — `lint_consistency.py` enforces every pin — so
    if perturbing one does not fire, the harness is dead and every reading above is noise.
    """
    paper, row = _first_paper_whose_covered_numbers_are_pinned()
    result = claim_ablation.ablate(paper, row)
    assert result["status"] == claim_ablation.APPLIED, (
        f"the control sentence in {paper} could not be perturbed ({result['reason']}), so the "
        f"harness is not editing the file at all:\n  {row['sentence'][:120]}")
    assert result["red"], (
        f"a PINNED figure in {paper} was changed ({result['reason']}) and nothing went red:\n"
        f"  {row['sentence'][:120]}\n  census credits: {', '.join(row['read_by'])}\n\n"
        "`lint_consistency.py` enforces every pin, so this cannot be a true negative. The harness is "
        "not running the guards, or not writing the file — every other verdict in this module is "
        "meaningless until it does.")


def test_the_document_is_byte_identical_after_an_ablation():
    """⛔ THE MANUSCRIPT IS A DEPOSIT ARTIFACT. A test that corrupts one to measure it is a defect."""
    paper, _ = _first_paper_whose_covered_numbers_are_pinned()
    path = claim_coverage.PAPERS[paper]
    before = io.open(path, encoding="utf-8").read()
    rows = [r for r in claim_coverage.census(paper)
            if r["covered"] and re.search(r"\d", r["sentence"])]

    # ⛔⛔ THIS TEST WAS VACUOUS FROM THE DAY IT WAS WRITTEN (round 17 seat A, 2026-08-23). It took
    # `rows[0]`, whose sentence has no verbatim home in the raw file, so `ablate` returned
    # NOT_APPLIED before performing a single write — instrumented: ZERO writes. It asserted a file
    # was unchanged after an operation that never began, and passed on every run.
    # ⚠ `ablate` returns a `status` FOR THIS REASON and the docstring says a caller reading `red`
    # without checking it is reading absence as evidence. The test written to guard the manuscript
    # against corruption made exactly that mistake about itself.
    result = None
    for row in rows:
        result = claim_ablation.ablate(paper, row, witnesses=[])
        if result["status"] == claim_ablation.APPLIED:
            break
    assert result is not None and result["status"] == claim_ablation.APPLIED, (
        "no covered numbered sentence could be perturbed at all, so this test performed no write "
        "and its assertion below is about an operation that never happened. That is the failure "
        "mode it exists to detect, one level up.")
    assert io.open(path, encoding="utf-8").read() == before, (
        f"{os.path.basename(path)} was not restored after an ablation. The restore is in a `finally` "
        "and digest-verified; if this fires, the process was killed mid-mutation — recover the file "
        "from git before doing anything else.")
