#!/usr/bin/env python3
"""No deposit sentence credits the mature-parent screen with all three condemned designs.

⛔ WHY THIS EXISTS, AND IT IS THE MOST PERSISTENT DEFECT IN THIS LEDGER. Three designs are condemned
for pairing their whole catalytic gap against the patient's own un-rearranged *NR4A3* allele. The
mature-parent screen READ TWO OF THEM. The third sits at the *TAF15* exon-6 :: *NR4A3* intron-2
cryptic-exon seam, whose acceptor half is intronic and therefore absent from every mature transcript,
so the screen has nothing to look at: the canonical file records `not_screened`, not zero.

The claim "all three cleared the mature-parent screen" has now been written into the deposit FIVE
TIMES, in five different sentences, across two review rounds:

  Box 1                    "the mature-parent screen clears or cannot read"          correct
  §2.6 listing             "Two of the three cleared ... the third's seam that       correct
                            screen cannot address"
  §2.6 "Two things"        "Each had already cleared the mature-parent exclusion,    WRONG (round 6)
                            and so had every other design at its seam"
  §3                       "three designs the mature-parent screen passed"           WRONG (round 7)
  §2.6 (round-6 repair)    "passed two of them ... at the third's seam it never      correct
                            ran at all"

⚠ ROUND 7's DEFECT WAS FOUND BY A REVIEWER *AFTER* ROUND 6 FIXED THE SAME CLAIM ELSEWHERE. That is
the "one home fixed, the others left" mechanism, and the repair for round 6 did not search for the
others — so the class survived its own fix. A guard is the only thing that ends this: a reviewer
finds one home per round, a derived assertion finds all of them at once.

★ THE COUNTS ARE DERIVED FROM THE CANONICAL FILE, NEVER TYPED. If the screen ever does gain the
ability to read the cryptic-exon seam, this test's expected numbers move with the artifact and the
forbidden phrasings become sayable — which is the correct behaviour, and the reason none of the
numbers below is a literal.

$0, stdlib, no network.
"""
import csv
import os
import re

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ASO = os.path.join(os.path.dirname(_HERE), "aso")
_CSV = os.path.join(_ASO, "fusion-junction-aso-sequences.csv")

DEPOSIT_DOCUMENTS = (
    "fusion-junction-aso-research-article.md",
    "fusion-junction-aso-supplementary-information.md",
    "fusion-junction-aso-submission-tables.md",
)

#: The verbs a sentence uses to say the screen looked and found nothing wrong. `cannot read`,
#: `could not read` and `not_screened` are deliberately absent: those are the honest forms.
_CLEARANCE = r"(?:passed|passes|cleared|clears|clean at|cleanly through)"

#: ⭐ THE QUALIFIERS THAT ACTUALLY CORRECT THE COUNT, AND ONLY THOSE. Deliberately NARROW:
#: round 6's defective sentence also said the screen was "structurally unable to see intronic
#: sequence" and "cannot look at the compartment in question" — true statements that did NOT
#: stop it asserting that all three had cleared. A rescue list wide enough to admit those
#: would have passed the defect this file exists to catch.
_RESCUE = (r"cannot read|could not read|cannot address|never r[au]n|not_screened"
           r"|two of the|passed two")


def _flat(text):
    """⛔ FLATTEN FIRST. The manuscript hard-wraps at ~100 columns and every one of the five homes
    above spans a line break somewhere. A guard that searches line by line finds none of them."""
    return re.sub(r"\s+", " ", text)


def _sentence_around(flat, start, end):
    """The whole sentence a match sits in.

    ⛔ THE RESCUE MUST READ THE SENTENCE, NOT THE MATCHED SPAN (fixed while writing this file). The
    offender patterns stop AT the clearance verb, so Box 1's correct "the mature-parent screen
    clears or cannot read" matched as "...screen clears" and the qualifier four words later was
    outside the string the rescue searched. The guard's first run flagged two CORRECT sentences,
    which is the "unbounded match set" mechanism arriving inside the very guard written to end a
    different one.
    """
    left = flat.rfind(".", 0, start) + 1
    right = flat.find(".", end)
    return flat[left: right if right != -1 else len(flat)]


def _condemned_for_the_wild_type_allele():
    """(total condemned, how many the mature-parent screen actually read) — from the canonical file."""
    seen = {}
    with open(_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if "un-rearranged NR4A3" in (row.get("do_not_order") or ""):
                seen[row["sequence"]] = row
    assert seen, ("no design in the canonical file is condemned for pairing the un-rearranged "
                  "NR4A3 allele; this guard has lost its subject and must be re-derived, not deleted")
    read = sum(1 for r in seen.values()
               if (r.get("mature_parent_duplex_through_gap_bp") or "") != "not_screened")
    return len(seen), read


def test_the_screen_read_fewer_of_them_than_there_are():
    """The premise. If this ever stops holding, the phrasings below stop being defects."""
    total, read = _condemned_for_the_wild_type_allele()
    assert read < total, (
        f"the mature-parent screen now reads all {total} condemned designs, so 'all three cleared "
        "it' would be TRUE. Re-derive this file against the new artifact rather than deleting it.")


@pytest.mark.parametrize("name", DEPOSIT_DOCUMENTS)
def test_no_sentence_credits_the_screen_with_every_condemned_design(name):
    path = os.path.join(_ASO, name)
    assert os.path.exists(path), (
        f"{path} is missing. A deposit document that is absent is a failure, never a skip.")
    total, read = _condemned_for_the_wild_type_allele()
    flat = _flat(open(path, encoding="utf-8").read())
    spelt = {2: "two", 3: "three", 4: "four", 5: "five"}[total]

    real = _real_offenders(flat, spelt)
    assert not real, (
        f"{len(real)} sentence(s) in {name} credit the mature-parent screen with all {total} "
        f"condemned designs; it read {read}. Say 'clears or cannot read', as Box 1 does.\n  "
        + "\n  ".join(o[:190] for o in real))


def _real_offenders(flat, spelt):
    """Every clearance claim over the whole condemned set that no qualifier rescues.

    ⭐ ONE DETECTION, USED BY BOTH THE GUARD AND ITS PROOF. Written separately at first, and the
    proof's copy searched for the FIRST match in the document — which is Box 1's CORRECT sentence —
    so it reported the guard as proven while never touching the reintroduced defect at all. A proof
    that does not run the thing it is proving is the vacuous-proof failure in a new costume.
    """
    offenders = []
    for pattern in (
        #: (a) the count and the screen in one clause, with a clearance verb.
        rf"\b(?:all )?{spelt}\b[^.]{{0,90}}?mature-parent (?:screen|exclusion)"
        rf"[^.]{{0,40}}?{_CLEARANCE}",
        #: (b) the same, with the screen named first -- the shape §3 took.
        rf"mature-parent (?:screen|exclusion)[^.]{{0,60}}?{_CLEARANCE}[^.]{{0,60}}?\ball {spelt}\b",
        #: (c) "Each"/"every one of them" over the condemned set, which is how round 6's read.
        rf"\b(?:each|every one)\b[^.]{{0,70}}?{_CLEARANCE}[^.]{{0,40}}?"
        rf"mature-parent (?:screen|exclusion)",
    ):
        for m in re.finditer(pattern, flat, re.I):
            offenders.append((m.group(0), _sentence_around(flat, m.start(), m.end())))

    #: ⭐ THE RESCUE, AND IT IS THE POINT OF THE WHOLE GUARD. A sentence may name all three together
    #: PROVIDED the same sentence says the screen could not read one of them. Box 1's "clears or
    #: cannot read" is the canonical form and every other home should match it.
    return [span for span, sentence in offenders if not re.search(_RESCUE, sentence, re.I)]


def test_this_guard_fails_on_both_defects_it_was_written_for():
    """Prove it against the two REAL sentences, not a toy — and prove each mutation landed."""
    path = os.path.join(_ASO, DEPOSIT_DOCUMENTS[0])
    original = open(path, encoding="utf-8").read()
    total, _ = _condemned_for_the_wild_type_allele()
    spelt = {2: "two", 3: "three"}[total]

    assert not _real_offenders(_flat(original), spelt), (
        "the document already trips this guard, so the proof below could not tell a working guard "
        "from a broken one")

    for fixed, broken in (
        # round 7, §3
        ("three designs the mature-parent screen clears or cannot read",
         "three designs the mature-parent screen passed"),
        # round 6, §2.6 — ⚠ THE WHOLE SENTENCE, BOTH CLAUSES. Mutating only the first clause left
        # "at the third's seam it never ran at all" standing, which the rescue then matched, and the
        # proof reported the guard as broken when it was the MUTATION that was wrong. A partial
        # mutation does not reproduce the defect; it produces a third sentence that is neither.
        ("The mature-parent exclusion had passed two of them, and every other design at their seam;\n"
         "at the third's seam it never ran at all, on that design or on any other there.",
         "Each had already cleared the mature-parent exclusion, and so had every other design at "
         "its seam."),
    ):
        assert original.count(fixed) == 1, (
            f"the sentence this proof mutates has been reworded: {fixed!r}. Re-anchor the proof on "
            "the text that is there now — an unexercised guard is an absent one.")
        mutated = original.replace(fixed, broken, 1)
        assert mutated != original, "the mutation did not change the text; this proof would be vacuous"
        assert _real_offenders(_flat(mutated), spelt), (
            f"reintroducing {broken!r} did NOT trip the guard that exists for it")
