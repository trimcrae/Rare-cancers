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
#: ⛔ THE THIRD FIELD, ADDED 2026-09-02. `rate_liable` is the scramble null's HEADLINE number — "10.0%
#: of such scrambles pair a parent's whole catalytic gap" — and neither half of this file bound it.
#: Found by running a mutation against the freshly-scoped argmax half: 10.0 -> 6.2, the mononucleotide
#: arm's value at the same cut, passed all thirteen tests. ★ THAT IS THE ONE-OF-A-PAIR SHAPE FOR THE
#: THIRD TIME IN TWO DAYS — predicate then ensemble, membership then argmax, and now the field the
#: other two are computed against. The rule that keeps catching this repository is that a guard binds
#: the thing in front of it; the discipline is to enumerate the axes and the fields, not to fix the
#: instance.
_LIABLE = re.compile(r"scrambles?\s+pair\s+a\s+parent'?s?\s+whole\s+catalytic\s+gap", re.I)

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


#: How each null ensemble is named in prose. ⛔ THE AXIS THE GUARD HAD NO OPINION ABOUT UNTIL
#: ROUND 31, AND THE ONE THE DEFECT LIVED ON. A sentence that names its ensemble is making a claim
#: about THAT ensemble, and admitting another arm's value is the same looseness the cut fix closed
#: one axis earlier.
_ENSEMBLE_WORDS = (
    ("scrambled_dinucleotide", (r"dinucleotide[- ]preserving", r"\bdinucleotide\b")),
    ("scrambled_mononucleotide", (r"mononucleotide",)),
)


def _ensemble_named_in(window):
    """The ensemble NEAREST the claim, or None.

    ⛔⛔ NEAREST, NOT FIRST-IN-A-PRIORITY-LIST, AND THE DIFFERENCE IS A WRONG ANSWER RATHER THAN A
    MISSED ONE. The first version walked a fixed order and returned the first arm it found anywhere
    in the window, so a passage that discusses the mononucleotide arm and then the dinucleotide one
    would bind a mononucleotide claim to the dinucleotide values — the guard confidently checking
    the wrong thing, which is worse than not checking. Scanning for the LAST mention before the
    claim follows how the prose actually refers: the arm most recently named is the one "such
    scrambles" means.
    ⚠ AND THE LOOKBACK IS SENTENCE-BOUNDED RATHER THAN A CHARACTER COUNT (see `_ensemble_window`).
    A number that happens to fit today is fitted to the instance; a sentence boundary is a unit of
    the thing being read.
    """
    w = window.lower()
    best, where = None, -1
    for name, pats in _ENSEMBLE_WORDS:
        for pat in pats:
            for m in re.finditer(pat, w):
                if m.start() > where:
                    best, where = name, m.start()
    return best


#: How far back an ENSEMBLE may be established, in sentences. A cut is restated per claim; an arm is
#: named once and referred to anaphorically after — "such scrambles", "the same null". Measured on
#: the journal article: the antecedent of the control sentence's "such scrambles" sits 284 characters
#: back, across two sentence boundaries, and a 200-character window could not see it. ⚠ THE FIX IS
#: NOT A BIGGER NUMBER. Three sentences is the span over which this corpus actually carries a
#: referent; if a paper ever needs more, that paper's sentence should name its arm instead.
_ENSEMBLE_LOOKBACK_SENTENCES = 3


def _ensemble_window(text, start, end):
    """`text` back to the start of the third preceding sentence, forward to `end`."""
    pre = text[:start]
    bounds = [m.end() for m in re.finditer(r"(?<=[.;])\s+", pre)]
    cut = bounds[-_ENSEMBLE_LOOKBACK_SENTENCES] if len(bounds) >= _ENSEMBLE_LOOKBACK_SENTENCES else 0
    return text[cut:end]


def _rates(field, cut=None, ensemble=None):
    """Every printed-form rate for `field`, optionally scoped to one cut and ONE ENSEMBLE.

    ⛔⛔ `ensemble` WAS ADDED 2026-09-02 BECAUSE WITHOUT IT THIS GUARD BLESSED A REAL DEFECT — the
    one it was written for, one round after it was written. The accepted set was a UNION over all
    ten null ensembles, so a sentence naming the dinucleotide null could print the MONONUCLEOTIDE
    arm's value and pass. Round 31's regression seat mutation-tested it on scratch copies: at cut
    seven, 38.8 -> 47.9 passed, -> 64.0 passed, -> 52.3 passed; only a number belonging to no
    ensemble at that cut failed.
    ★ AND THE DEFECT IT MISSED WAS EXACTLY THAT. The research article said "Read at seven, the same
    null returns 74.3% ... and 38.8%" with a DINUCLEOTIDE antecedent, and 74.3/38.8 are the
    mononucleotide arm; the dinucleotide null at seven is 85.4/47.9. Both printed figures
    understated, in a sentence whose whole job is to warn a laboratory that a scramble passing at
    ten is not certified at seven.
    ⚠ THE SHAPE OF THE MISS IS THE ONE `paper-hardening` §8b.2 NAMES: the guard was scoped by
    PREDICATE and CUT and simply had no opinion about the third axis. Scoping by a property you did
    not think of is not possible; what is possible is to make the axis a parameter, so the next
    caller that needs it has one instead of a union.
    """
    d = json.load(open(NULL, encoding="utf-8"))
    out = set()
    for name, ens in d["null_ensembles"].items():
        if ensemble is not None and name != ensemble:
            continue
        ladder = ens.get("cut_ladder") or {}
        rows = [ladder[str(cut)]] if cut is not None and str(cut) in ladder else list(ladder.values())
        for row in rows:
            v = row.get(field)
            if isinstance(v, (int, float)):
                out.add(f"{v * 100:.1f}")
    return out


def _membership_rates(cut=None, ensemble=None):
    return _rates("rate_pairing_NR4A3_specifically", cut, ensemble)


def _argmax_rates(cut=None, ensemble=None):
    return _rates("rate_liable_attributed_to_NR4A3", cut, ensemble)

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
        # ⛔⛔ THE THIRD AXIS, ADDED 2026-09-02 AFTER THIS GUARD BLESSED THE DEFECT IT EXISTS FOR.
        # The research article said "Read at seven, the same [dinucleotide] null returns ... 38.8%",
        # and 38.8 is the MONONUCLEOTIDE arm; the dinucleotide value is 47.9. Both printed figures
        # understated, in the sentence whose job is to warn a lab that a scramble passing at ten is
        # not certified at seven. Scoped by predicate and by cut, this guard had no opinion about
        # WHICH ensemble, so it accepted any arm's value — measured by round 31's regression seat:
        # 47.9, 64.0 and 52.3 all passed in place of 38.8.
        # ★ A sentence that NAMES its ensemble is admissible only against that ensemble. One that
        # names none is unchanged from before: the union, which is all the sentence has claimed.
        ensemble = _ensemble_named_in(_ensemble_window(text, m.start(), m.end() + 40))
        allowed = _membership_rates(cut, ensemble)
        where = f"the {cut}-base-pair cut" if cut else "any cut (the sentence names none)"
        whose = f"the {ensemble} null" if ensemble else "any null ensemble (the sentence names none)"
        assert any(p in allowed for p in pcts), (
            f"{name} prints {pcts} beside a MEMBERSHIP claim about {whose} read at {where}, and "
            f"none is a `rate_pairing_NR4A3_specifically` value there. Two different substitutions "
            "reach this line: the argmax field `rate_liable_attributed_to_NR4A3`, which reads "
            "plausibly and is a different QUANTITY, and another ensemble's value at the same cut, "
            "which is the right quantity from the wrong ARM.")


@pytest.mark.parametrize("name", DOCS)
def test_every_liable_rate_printed_is_the_liable_field_of_the_arm_it_names(name):
    """The scramble null's headline rate, bound to (field, cut, ensemble) like the other two.

    ⛔ IT WAS UNBOUND UNTIL 2026-09-02 AND NOTHING NOTICED, because both existing halves keyed off
    NR4A3-specific wordings and this claim mentions no gene at all. A guard family that covers two of
    three fields reads as complete — the file had thirteen passing tests over it.
    """
    text = _text(name)
    for m in _LIABLE.finditer(text):
        window = text[max(0, m.start() - 160): m.end() + 60]
        pcts = re.findall(r"(\d+\.\d)%", window)
        if not pcts:
            continue
        cut = _cut_named_in(window)
        ensemble = _ensemble_named_in(_ensemble_window(text, m.start(), m.end() + 60))
        allowed = _rates("rate_liable", cut, ensemble)
        assert any(p in allowed for p in pcts), (
            f"{name} prints {pcts} for the share of scrambles pairing a parent's whole catalytic "
            f"gap at cut {cut!r} on {ensemble!r}, and none is a `rate_liable` value there. The "
            "other arm's value at the same cut is the substitution to expect — it is the right "
            "quantity from the wrong ensemble.")


@pytest.mark.parametrize("name", DOCS)
def test_a_membership_rate_read_at_a_named_cut_names_its_ensemble(name):
    """⛔⛔ THE REGRESSION PATH THE ENSEMBLE FIX LEFT OPEN, CLOSED BY MEASUREMENT RATHER THAN BY HOPE.

    `_ensemble_named_in` can only bind what a sentence claims, so deleting the word
    "dinucleotide-preserving" from the sentence that carries the defect makes the guard fall back to
    the union and go quiet. Mutation-tested 2026-09-02: with the ensemble word removed, restoring
    the wrong arm's value passes all ten tests in this file. One word is the whole difference
    between a bound claim and an unbound one.

    ★ THE PROPERTY, AND IT IS A REAL ONE RATHER THAN A PATCH ON THIS SENTENCE. Ten null ensembles
    give ten different membership rates at any given cut — 38.8 and 47.9 differ by nine points at
    seven. A sentence precise enough to name its cut and not its arm is therefore not checkable by
    anyone, reader or guard, and the number it prints could be any of ten.

    ⚠ VERIFIED SAFE ON TRUE INPUT BEFORE IT WAS ADDED, which is `paper-hardening` §8b.1's rule: over
    all three outgoing documents, every membership sentence that names a cut already names an
    ensemble, so this reds nothing that is currently right. A gate that fires on honest prose is one
    somebody loosens.
    """
    text = _text(name)
    for m in _MEMBERSHIP.finditer(text):
        window = text[max(0, m.start() - 160): m.end() + 40]
        if "design" in text[max(0, m.start() - 90): m.start()].lower():
            continue
        if not re.findall(r"(\d+\.\d)%", window):
            continue
        cut = _cut_named_in(window)
        if not cut:
            continue
        assert _ensemble_named_in(window), (
            f"{name} reads a membership rate at the {cut}-base-pair cut without naming which null "
            "ensemble it is reading. The ten arms give ten different values there — the "
            "mononucleotide and dinucleotide scrambles are nine points apart at seven — so the "
            "sentence cannot be checked by a reader or by this file. Name the arm.\n\n"
            f"...{window[-160:]}")


@pytest.mark.parametrize("name", DOCS)
def test_every_argmax_rate_printed_is_the_argmax_field(name):
    """The mirror assertion. ⛔ BOTH DIRECTIONS OR NEITHER: 'the right field is present' and 'the
    wrong field is absent' fail differently, and a guard that checks only one is half a guard
    (`paper-hardening` §8b)."""
    text = _text(name)
    for m in _ARGMAX.finditer(text):
        window = text[max(0, m.start() - 200): m.end() + 40]
        pcts = re.findall(r"(\d+\.\d)%", window)
        if not pcts:
            continue          # the journal article states this one as a count, not a rate
        # ⛔⛔ SCOPED BY CUT AND ENSEMBLE LIKE ITS MEMBERSHIP TWIN, ADDED 2026-09-02 — AND UNTIL THEN
        # THIS HALF WAS A UNION OVER BOTH AXES WHILE THE OTHER HALF HAD BOTH. Round 31 bound
        # membership to (cut, ensemble) and left this function reading every row of every arm, so
        # the file LOOKED symmetric and was not. Round 32's regression seat measured the cost: at
        # the journal article's control sentence, 3.9 -> 1.8 — the wrong arm at the right cut, the
        # exact defect round 31 was convened for — still passed, as did 24.5, 29.4 and 3.5.
        # ★ ONE-OF-A-PAIR, INSIDE THE FIX FOR A ONE-OF-A-PAIR DEFECT. `paper-hardening` §8b.2 says a
        # fix bound to one call site regresses at its sibling; here the sibling was eighty lines
        # below, in the same file, named "The mirror assertion".
        cut = _cut_named_in(window)
        ensemble = _ensemble_named_in(_ensemble_window(text, m.start(), m.end() + 40))
        allowed = _argmax_rates(cut, ensemble)
        where = f"the {cut}-base-pair cut" if cut else "any cut (the sentence names none)"
        whose = f"the {ensemble} null" if ensemble else "any ensemble (the sentence names none)"
        assert any(p in allowed for p in pcts), (
            f"{name} prints {pcts} beside an ARGMAX claim about {whose} read at {where}, and none "
            "is a `rate_liable_attributed_to_NR4A3` value there. The membership field "
            "`rate_pairing_NR4A3_specifically` reads plausibly and is a different QUANTITY; another "
            "arm's value at the same cut is the right quantity from the wrong ARM.")


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
