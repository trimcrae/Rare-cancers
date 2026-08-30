"""⛔ THREE DOCUMENTS GO TO THE EDITOR IN ONE ENVELOPE AND THEY DISAGREED ABOUT THE AUTHOR.

The submitted manuscript, the cover letter and the extended report it cites each carry a Competing
interests declaration. Until 2026-08-22 they named DIFFERENT non-financial interests: the letter and
the extended report declared that the author is a survivor of extraskeletal myxoid chondrosarcoma —
the disease the work is about — and the manuscript itself declared something else entirely, an
observation about publication bias in the literature.

⛔⛔ AND A PRIOR ROUND HAD ALREADY FOUND IT. `fusion-junction-aso-paper-redteam-round8.md:213` records
"drops the survivorship disclosure the extended report makes". The repair substituted a HOMONYM — the
manuscript's replacement text contained the word "survivorship", about publication survivorship — so
every grep-shaped check of whether round 8 had landed came back green while the manuscript still said
something else. That is why this guard reads the CLAIM and not the token.

★ WHAT THE AUTHOR DECIDED (trimcrae, 2026-08-22, asked directly): "EMC survivor doesn't need to be in
the manuscript." A diagnosis is the author's own medical information and disclosing it in a published
paper is their call, not a guard's. Telling the EDITOR is the part that bears on the review, and the
cover letter is a normal and sufficient route for it.

⚠ SO THE PROPERTY IS NOT "every document declares it". It is that the manuscript does not claim
there are NO non-financial interests, because that would be false. An omission is a choice; a false
negative declaration is a misstatement.

⛔ AND THE COVER LETTER IS NO LONGER READ HERE. trimcrae, 2026-08-30: *"That's just cruft. I've told
you like 3 times now. Remove all checks on cover letters."* A letter is hand-written once, at the
moment a paper goes to a publisher, and it is not a preprint artifact — the author writes his own
declaration into it then. Every guard below reads the MANUSCRIPT, which is the document that gets
published and the one this repository generates.
"""
from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")

JOURNAL_ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")
JOURNAL_TABLES = os.path.join(ASO, "fusion-junction-aso-journal-tables.md")

#: The caption of whichever numbered table actually carries the control oligonucleotides. Matched on
#: what the table IS, not on its number, because the number is the thing under test.
_CONTROLS_TABLE = re.compile(r"^\*\*Table (\d+)\.[^*\n]*control oligonucleotide", re.M | re.I)
#: How the manuscript points at it. The literal is quoted from the manuscript itself.
_ARTICLE_POINTS_AT = re.compile(r"named as sequences \(Table (\d+)\)")

#: The disclosure as a PROPERTY rather than a phrase: the author has this disease.
#:
#: ⚠ AND NOT ITS NEGATION. The first version of this pattern carried a bare
#: `survivor of extraskeletal myxoid chondrosarcoma` alternative, which matched "I am NOT a survivor
#: of extraskeletal myxoid chondrosarcoma" — so a mutation that reversed the disclosure passed the
#: guard written to protect it. A needle that matches the negation of its own property is worse than
#: no needle: it reports the claim as present at the moment it is denied.
_PATIENT_INTEREST = re.compile(
    r"(?<!not )(?:author is|I am) a survivor of extraskeletal myxoid chondrosarcoma"
    r"|the author is a survivor of (?:the disease|extraskeletal myxoid chondrosarcoma)", re.I)

#: A blanket denial. "no financial competing interests" is fine and true; "no competing interests"
#: unqualified, or "no non-financial interests", is not.
_DENIES_NON_FINANCIAL = re.compile(
    r"no non-financial (?:competing )?interests?"
    r"|declares? no competing interests?(?!\s*:)", re.I)


def _flat(path):
    assert os.path.exists(path), f"{os.path.basename(path)} is missing; re-anchor this guard"
    with open(path, encoding="utf-8") as fh:
        return " ".join(fh.read().split())


def test_the_diagnosis_appears_nowhere_in_the_submission_envelope():
    """⛔ THE AUTHOR'S DIAGNOSIS IS OUT OF THE ENVELOPE ENTIRELY (trimcrae, 2026-08-24).

    ⚠ THIS REVERSES WHAT THIS FILE USED TO REQUIRE, AND THE REVERSAL IS THE AUTHOR'S TO MAKE.
    Until today the contract was "the manuscript may omit it, the cover letter must declare it",
    resting on his 2026-08-22 answer that it "doesn't need to be in the manuscript". Asked again on
    2026-08-24 he removed it from the letter too. A diagnosis is the author's own medical
    information; whether to disclose it anywhere is his decision and not a guard's, and an external
    reviewer asking for it in the published declaration does not change whose decision it is.

    ★ SO THE PROPERTY FLIPS DIRECTION BUT DOES NOT WEAKEN. It is no longer "is it declared" but
    "is it absent from BOTH documents", which is checkable in exactly the same way and fails just as
    loudly if a later edit — or a later reviewer's advice — puts it back.
    """
    m = _PATIENT_INTEREST.search(_flat(JOURNAL_ARTICLE))
    assert not m, (
        f"the manuscript names the author's diagnosis: ...{m.group(0)}...\n\n"
        "It was removed on 2026-08-24 at the author's instruction. Do not reinstate it on a "
        "reviewer's advice — it is his medical information and his call, and this guard exists "
        "because it was put back once already.")


def test_the_manuscript_does_not_deny_an_interest_it_has():
    """⛔ AN OMISSION IS A CHOICE; A FALSE NEGATIVE DECLARATION IS A MISSTATEMENT.

    ⚠ THIS HALF IS UNCHANGED BY THE 2026-08-24 DECISION, AND IT IS THE HALF THAT KEEPS THE PAPER
    HONEST. Removing the disclosure from the envelope does not make the interest cease to exist, so
    the manuscript still may not say there are none. Declaring the financial interests specifically,
    and saying nothing about the other kind, is true in a way that "no competing interests" is not.
    """
    text = _flat(JOURNAL_ARTICLE)
    m = _DENIES_NON_FINANCIAL.search(text)
    assert not m, (
        "the submitted manuscript denies having any non-financial competing interest, and it has "
        f"one:\n  ...{text[max(0, m.start() - 90):m.end() + 90]}..."
        "\n\nDeclare the financial interests specifically (as it does) and say nothing that denies "
        "the other kind.")


def test_the_manuscript_does_not_point_at_a_disclosure_that_is_not_there():
    """⛔ A POINTER TO A DISCLOSURE THAT NO LONGER EXISTS IS A FALSE STATEMENT IN A PUBLISHED PAPER.

    The manuscript used to say the interest was "disclosed to the editor in the accompanying cover
    letter" — correct while the letter declared it, and false the moment it did not. The two moved
    together on 2026-08-24; this asserts they stay together.
    """
    text = _flat(JOURNAL_ARTICLE)
    m = re.search(r"non-financial interest[^.]{0,80}cover letter", text, re.I)
    assert not m, (
        f"the manuscript still says a non-financial interest is disclosed in the cover letter — "
        f"...{m.group(0)}... — but the letter no longer discloses one. Remove the sentence, or "
        "restore the disclosure to the letter; they may not disagree.")


def test_the_manuscript_names_the_table_the_controls_are_actually_in():
    """⛔ THE MANUSCRIPT TELLS A SCREENER WHERE TO LOOK, AND A WRONG NUMBER THERE COSTS THE
    SUBMISSION.

    Nucleic Acid Therapeutics returns a manuscript WITHOUT REVIEW when its control-oligonucleotide
    rule is not met, so the sentence naming the screened controls is read before anyone reads the
    result. A screener who opens that table and finds the reagents instead of the controls has been
    told something false about compliance, at the one step where being wrong is expensive.

    ⛔⛔ AND THE NUMBER IS THE PART THAT ROTS. The tables file is GENERATED — renumber a display item
    in `aso_journal_tables.py` and the hand-written manuscript keeps pointing at the old one,
    silently, because nothing reads a number for meaning.

    ★ SO THE TABLE IS FOUND BY WHAT IT CONTAINS, NEVER BY ITS NUMBER. The caption that says it holds
    the control oligonucleotides decides which number is right, and the manuscript is then read
    against that. Nothing here hard-codes a 2.
    """
    tables = open(JOURNAL_TABLES, encoding="utf-8").read()
    found = _CONTROLS_TABLE.findall(tables)
    assert len(found) == 1, (
        f"⛔ {len(found)} table(s) in fusion-junction-aso-journal-tables.md have a caption naming "
        f"the control oligonucleotides, and this guard needs exactly one to decide which number "
        f"the manuscript should be pointing at. Found: {found or 'none'}.")
    number = found[0]

    article = re.sub(r"\s+", " ", open(JOURNAL_ARTICLE, encoding="utf-8").read())
    stated = _ARTICLE_POINTS_AT.search(article)
    assert stated, (
        "⛔ the manuscript no longer names the table its control oligonucleotides are in. A "
        "screener applying the journal's two-control rule reads that sentence before the result.")
    assert stated.group(1) == number, (
        f"⛔ the manuscript points at Table {stated.group(1)} for the control oligonucleotides and "
        f"they are in Table {number}. The tables file is generated, so the number moves there and "
        f"stays put in the hand-written manuscript.")
