"""⛔⛔ THE SCRAMBLE-CONTROL NULL RATES ARE STATED AT SIX SITES ACROSS TWO PAPERS AND NOTHING BOUND
ANY OF THEM. Round 30's arithmetic seat, 2026-09-02, and the gap is what let its blocker survive.

★ THE BLOCKER THIS EXISTS TO PREVENT RECURRING, because the number was not wrong — the PREDICATE
was. `aso-parent-null.json` carries two different readings side by side at every cut:

    rate_liable_attributed_to_NR4A3   an ARGMAX  — NR4A3 is the LONGEST pairing parent
    rate_pairing_NR4A3_specifically   MEMBERSHIP — NR4A3 is paired at all

At the seven-base-pair cut those are 23.9% and 38.8%: **14.8 percentage points apart**. §4.4 printed
the argmax under the words "doing so against wild-type *NR4A3*", which ask for membership. The
producing module says so in its own comment — "a field named `against_NR4A3` reads as the second and
is the first" — and round 26 had ALREADY repaired the identical phrasing in the journal article and
tightened `test_journal_article_numbers.py` so "do so against" fails there. The extended report's two
copies were never touched, because the guard was bound to one document.

⛔ AND THE DIRECTION IS WHY IT IS A BLOCKER RATHER THAN A TYPO. That sentence warns a laboratory that
a scramble which passes the ten-base-pair rule is NOT certified to spare the parent transcripts at a
looser cut. Understating the rate weakens the warning it is making.

★★ SO THIS BINDS THE NUMBERS TO THE ARTIFACT AND THE PREDICATE TO THE WORDS, at every site in every
outgoing document — scoped by the PROPERTY ("a document that prints one of these rates") rather than
by a list of files, which is the fix `paper-hardening` §8b.2 measured: every list-scoped fix in that
audit regressed at a sibling, and every predicate-scoped one held.
"""
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.dirname(MANUSCRIPTS)
NULL = os.path.join(REPO, "modalities", "aso-parent-null.json")

#: Every outgoing document. ⛔ NOT A HAND-KEPT LIST OF THE ONES THAT HAPPEN TO CITE THESE RATES —
#: that is the shape that failed. Any outgoing document is in scope; one that prints no rate simply
#: contributes no assertions.
ASO = os.path.join(MANUSCRIPTS, "aso")
DOCS = ["fusion-junction-aso-research-article.md",
        "fusion-junction-aso-journal-article.md",
        "fusion-junction-aso-supplementary-information.md"]

#: ⛔ THE TWO PREDICATES, AND THE WORDINGS THAT ASK FOR EACH. A sentence naming NR4A3 alongside one
#: of these rates is making one of two different claims, and the artifact answers them differently.
_MEMBERSHIP = re.compile(r"pair(?:ing|s)?\s+wild-type\s+\*?NR4A3\*?\s+specifically", re.I)
_ARGMAX = re.compile(r"the\s+longest\s+is\s+wild-type\s+\*?NR4A3\*?", re.I)
#: The wording that reads as membership to any reader and was silently carrying the argmax.
_AMBIGUOUS = re.compile(r"(?:do|does|doing)\s+so\s+against\s+wild-type\s+\*?NR4A3\*?", re.I)


def _ladder(ensemble, cut):
    d = json.load(open(NULL, encoding="utf-8"))
    return d["null_ensembles"][ensemble]["cut_ladder"][str(cut)]


#: Cuts are written as words in the prose and as keys in the artifact.
_WORD_CUT = {"six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
             "twelve": 12, "thirteen": 13}


def _cut_named_in(window):
    """The base-pair cut this sentence is read at, or None when it names none.

    ⚠ NONE IS NOT A PASS. A sentence with no cut falls back to every cut's values, which is weaker
    but still binds the FIELD; it is reported in the failure message so a reader can see which
    check actually ran rather than assuming the strict one did.
    """
    w = window.lower()
    for word, n in _WORD_CUT.items():
        if re.search(rf"\b{word}[- ]base[- ]pair\b", w) or re.search(rf"\bread at {word}\b", w):
            return n
    m = re.search(r"\b(\d{1,2})[- ]base[- ]pair\b", w)
    return int(m.group(1)) if m else None


def _rates(field, cut=None):
    d = json.load(open(NULL, encoding="utf-8"))
    out = set()
    for ens in d["null_ensembles"].values():
        ladder = ens.get("cut_ladder") or {}
        rows = [ladder[str(cut)]] if cut is not None and str(cut) in ladder else list(ladder.values())
        for row in rows:
            v = row.get(field)
            if isinstance(v, (int, float)):
                out.add(f"{v * 100:.1f}")
    return out


def _membership_rates(cut=None):
    return _rates("rate_pairing_NR4A3_specifically", cut)


def _argmax_rates(cut=None):
    return _rates("rate_liable_attributed_to_NR4A3", cut)

def _text(name):
    p = os.path.join(ASO, name)
    if not os.path.exists(p):
        pytest.fail(f"{name} is missing, so what it prints is unknown")
    return " ".join(open(p, encoding="utf-8").read().split())


@pytest.mark.parametrize("name", DOCS)
def test_no_outgoing_document_uses_the_ambiguous_against_wording(name):
    """⛔ THE PREDICATE, NOT THE NUMBER. "do so against wild-type NR4A3" reads as membership to
    every reader and was carrying the argmax. Say which one is meant.

    ⚠ This is the assertion round 26 added to `test_journal_article_numbers.py` — for ONE document.
    Here it is scoped to every outgoing document, which is the whole point: the extended report's
    two copies survived that repair for four rounds because the guard could not see them.
    """
    hits = _AMBIGUOUS.findall(_text(name))
    assert not hits, (
        f"{name} says {hits[0]!r}. That phrasing asks for MEMBERSHIP (NR4A3 is paired at all) and "
        "the artifact's `rate_liable_attributed_to_NR4A3` is an ARGMAX (NR4A3 is the longest "
        "pairing parent) — 14.8 points apart at the seven-base-pair cut. Write either 'pair "
        "wild-type NR4A3 specifically' with `rate_pairing_NR4A3_specifically`, or 'the longest is "
        "wild-type NR4A3' with the argmax. Do not leave the reader to guess which.")


@pytest.mark.parametrize("name", DOCS)
def test_every_membership_rate_printed_is_the_membership_field(name):
    """A sentence saying 'pair NR4A3 specifically' must print `rate_pairing_NR4A3_specifically`,
    rounded to one decimal, for a cut the artifact actually carries."""
    text = _text(name)
    for m in _MEMBERSHIP.finditer(text):
        window = text[max(0, m.start() - 160): m.end() + 40]
        # ⛔ THE SUBJECT DISCRIMINATES, AND TWO NARROWER GUESSES DID NOT. This is forced by a RED ON
        # TRUE INPUT: the first draft matched any "pair wild-type NR4A3 specifically" and flagged
        # §2's description of what the table's columns hold — "how many DESIGNS pair wild-type NR4A3
        # specifically" — which carries no rate and needs none. `paper-hardening` §8b.1: a gate that
        # reds on true input is worse than one that greens on false input, because the first thing
        # anyone does is loosen it.
        # ⚠ AND "does the window mention scrambles?" WAS NOT ENOUGH — that same sentence sits beside
        # "scramble null beside it", so the word is present and the subject is not. Measured, not
        # reasoned: the narrowing was applied, the test stayed red, and the window was printed.
        # ★ A count of DESIGNS is a different claim with its own guard; this file owns the rate over
        # SCRAMBLES, and the immediate lead-in is what says which one a sentence is making.
        lead = text[max(0, m.start() - 90): m.start()].lower()
        if "design" in lead:
            continue
        pcts = re.findall(r"(\d+\.\d)%", window)
        assert pcts, (
            f"{name} claims scrambles 'pair wild-type NR4A3 specifically' with no percentage beside "
            "it, so nothing can check which reading it means")
        # ⛔⛔ THE CUT IS PART OF THE CLAIM, AND WITHOUT IT THIS GUARD WAS LOOSE ENOUGH TO MISS A
        # REAL REVERSION. Measured by mutation: reverting the ten-base-pair site from 4.0% to the
        # argmax's 3.9% was NOT caught, because 3.9 is a legitimate membership value at some other
        # cut. A guard that accepts any value from any row checks the FIELD and not the CLAIM.
        # ★ So when the sentence names its cut — "at the ten-base-pair criterion", "Read at seven" —
        # only that cut's values are admissible.
        cut = _cut_named_in(window)
        allowed = _membership_rates(cut)
        where = f"the {cut}-base-pair cut" if cut else "any cut (the sentence names none)"
        assert any(p in allowed for p in pcts), (
            f"{name} prints {pcts} beside a MEMBERSHIP claim read at {where}, and none is a "
            f"`rate_pairing_NR4A3_specifically` value there. The argmax field "
            "`rate_liable_attributed_to_NR4A3` reads plausibly and is a different quantity — that "
            "is the substitution this file exists for.")


@pytest.mark.parametrize("name", DOCS)
def test_every_argmax_rate_printed_is_the_argmax_field(name):
    """The mirror assertion. ⛔ BOTH DIRECTIONS OR NEITHER: 'the right field is present' and 'the
    wrong field is absent' fail differently, and a guard that checks only one is half a guard
    (`paper-hardening` §8b)."""
    text = _text(name)
    d = json.load(open(NULL, encoding="utf-8"))
    allowed = set()
    for ens in d["null_ensembles"].values():
        for row in (ens.get("cut_ladder") or {}).values():
            v = row.get("rate_liable_attributed_to_NR4A3")
            if isinstance(v, (int, float)):
                allowed.add(f"{v * 100:.1f}")
    for m in _ARGMAX.finditer(text):
        window = text[max(0, m.start() - 200): m.end() + 40]
        pcts = re.findall(r"(\d+\.\d)%", window)
        if not pcts:
            continue          # the journal article states this one as a count, not a rate
        assert any(p in allowed for p in pcts), (
            f"{name} prints {pcts} beside an ARGMAX claim and none is a "
            "`rate_liable_attributed_to_NR4A3` value in aso-parent-null.json")


def test_the_two_readings_really_do_differ_so_this_guard_is_not_vacuous():
    """⛔⛔ THE POSITIVE CONTROL. If the two fields were equal everywhere, every assertion above
    would pass by construction and this file would be ceremony. `paper-hardening` §8b: a mutation
    that never lands reports exactly what a guard that never fires reports.
    """
    row = _ladder("scrambled_mononucleotide", 7)
    argmax = row["rate_liable_attributed_to_NR4A3"]
    member = row["rate_pairing_NR4A3_specifically"]
    assert abs(member - argmax) > 0.10, (
        "the argmax and membership rates are within 10 points at the seven-base-pair cut, so the "
        "substitution this file guards against would no longer change a printed number. Re-derive "
        "the null before trusting these assertions — they may be passing vacuously.")
