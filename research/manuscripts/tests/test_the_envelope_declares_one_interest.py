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

⚠ SO THE PROPERTY IS NOT "every document declares it". It is:
  1. the cover letter — which the editor reads — DOES declare it; and
  2. the manuscript does not claim there are NO non-financial interests, because that would be
     false. An omission is a choice; a false negative declaration is a misstatement.
Both halves matter. Dropping (1) hides a real interest from the person it bears on; dropping (2)
turns a private decision into an untrue sentence in a published paper.
"""
from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")

COVER_LETTER = os.path.join(ASO, "fusion-junction-aso-cover-letter.md")
JOURNAL_ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")

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


def test_the_cover_letter_discloses_the_interest_to_the_editor():
    """⛔ THE EDITOR IS THE PERSON IT BEARS ON, AND THE LETTER IS HOW THEY LEARN IT."""
    text = _flat(COVER_LETTER)
    assert _PATIENT_INTEREST.search(text), (
        "the cover letter no longer discloses the author's non-financial interest to the editor. "
        "The author chose to keep it out of the published manuscript (2026-08-22) — that choice "
        "rests on the editor being told here. If this line goes, the interest is disclosed nowhere "
        "in the envelope at all.\n\nDo not satisfy this by adding the WORD 'survivorship': round 8's "
        "repair did exactly that and the disclosure stayed missing for four rounds.")


def test_the_manuscript_does_not_deny_an_interest_it_has():
    """⛔ AN OMISSION IS A CHOICE; A FALSE NEGATIVE DECLARATION IS A MISSTATEMENT.

    The manuscript may leave the diagnosis out. It may not say there are no non-financial interests,
    because there is one — and the cover letter in the same envelope says so.
    """
    text = _flat(JOURNAL_ARTICLE)
    m = _DENIES_NON_FINANCIAL.search(text)
    assert not m, (
        "the submitted manuscript denies having any non-financial competing interest, and the cover "
        f"letter in the same envelope discloses one:\n  ...{text[max(0, m.start() - 90):m.end() + 90]}..."
        "\n\nDeclare the financial interests specifically (as it does) and say nothing that denies "
        "the other kind.")


def test_the_manuscript_points_at_where_the_interest_is_disclosed():
    """⚠ SO A READER OF THE PAPER ALONE KNOWS THE QUESTION WAS ANSWERED SOMEWHERE.

    Not a journal requirement, and not a claim about the interest's content — a pointer, so the
    absence reads as a routing decision rather than as nothing having been considered.
    """
    text = _flat(JOURNAL_ARTICLE)
    assert re.search(r"non-financial interest[^.]{0,80}cover letter", text, re.I), (
        "the manuscript's Competing interests no longer says that a non-financial interest is "
        "disclosed to the editor in the cover letter. With the diagnosis deliberately out of the "
        "published text, this sentence is the only thing distinguishing a considered omission from "
        "an oversight.")
