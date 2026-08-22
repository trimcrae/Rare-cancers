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
PAPERS = ("journal-article", "journal-tables", "cover-letter")


def _sample(rows):
    """Deterministic, evenly spaced — never random: a flaky gate teaches people to re-run it."""
    covered = [r for r in rows if r["covered"] and re.search(r"\d", r["sentence"])]
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
    rows = _sample(claim_coverage.census(paper))
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


def test_the_ablation_harness_can_produce_a_red_at_all():
    """⛔⛔ THE POSITIVE CONTROL, AS ITS OWN TEST, BECAUSE ITS ABSENCE ONCE FABRICATED A READING.

    Everything above is an argument from a GREEN run: "the witness did not go red, therefore it
    binds." That argument is worth nothing unless this harness can go red on demand. A pinned figure
    stated in the article is the known-binding case — `lint_consistency.py` enforces every pin — so
    if perturbing one does not fire, the harness is dead and every reading above is noise.
    """
    rows = claim_coverage.census("journal-article")
    pinned = [r for r in rows
              if r["covered"] and re.search(r"\d", r["sentence"])
              and any(w.startswith("pin:") for w in r["read_by"])]
    if not pinned:
        pytest.fail(
            "no sentence in the journal article is credited to a pin, so this suite has no "
            "known-binding case to calibrate against. Every ablation verdict is uncalibrated.")

    result = claim_ablation.ablate("journal-article", pinned[0])
    assert result["status"] == claim_ablation.APPLIED, (
        f"the control sentence could not be perturbed ({result['reason']}), so the harness is not "
        f"editing the file at all:\n  {pinned[0]['sentence'][:120]}")
    assert result["red"], (
        f"a PINNED figure was changed ({result['reason']}) and nothing went red:\n"
        f"  {pinned[0]['sentence'][:120]}\n  census credits: {', '.join(pinned[0]['read_by'])}\n\n"
        "`lint_consistency.py` enforces every pin, so this cannot be a true negative. The harness is "
        "not running the guards, or not writing the file — every other verdict in this module is "
        "meaningless until it does.")


def test_the_document_is_byte_identical_after_an_ablation():
    """⛔ THE MANUSCRIPT IS A DEPOSIT ARTIFACT. A test that corrupts one to measure it is a defect."""
    path = claim_coverage.PAPERS["journal-article"]
    before = io.open(path, encoding="utf-8").read()
    rows = [r for r in claim_coverage.census("journal-article")
            if r["covered"] and re.search(r"\d", r["sentence"])]
    claim_ablation.ablate("journal-article", rows[0], witnesses=[])
    assert io.open(path, encoding="utf-8").read() == before, (
        f"{os.path.basename(path)} was not restored after an ablation. The restore is in a `finally` "
        "and digest-verified; if this fires, the process was killed mid-mutation — recover the file "
        "from git before doing anything else.")
