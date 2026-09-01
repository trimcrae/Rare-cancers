#!/usr/bin/env python3
"""A generator's hand-typed prose may not contradict the machine table beside it (AUT-PD-181).

⛔⛔ THE DEFECT, AND IT IS MEASURED HISTORY RATHER THAN A RISK. `census_route_expression_grading.py`
emits, per route, a `genes` table lifted from `emc-expression-panels.json` AND an `observed`
paragraph typed by hand. Until 2026-08-29 RT-ALK-HIT's paragraph read *"Both kinases the lead names
are NOT READABLE on EITHER platform — ALK and ROS1 have no probe on GPL6244 or GPL3290"*, while the
table emitted by the SAME function from the SAME artifact carried ALK readable on GPL6244 and ROS1
readable on both. The false sentence stood twenty days and propagated by copy into
`systems/graph/routes.json`'s grade, the generated route view, a literature record, and a ledger item
that was queued BECAUSE of it. Nothing measured the agreement, because nothing could: prose and table
were two independent statements of one fact, which is CLAUDE.md §1 exactly.

⭐ WHAT THIS GUARD IS AND — MORE IMPORTANTLY — WHAT IT IS NOT.
The honest fix is to DERIVE the readability sentence from the table in the generator, at which point
the two cannot disagree. That edit belongs in `research/modalities/census_route_expression_grading.py`
and was not made here: this file was written by a sprint seat that did not own that path (see
`research/autonomy/sprint-2026-09-01/S10-SCHEMA.md`). ⛔ SO THIS IS THE SECOND-BEST FIX — an assertion
of the prose AGAINST the table, which the ledger row names as the alternative — and it should be
DELETED, not extended, the day the sentence is derived.

★ THE CONTRACT, STATED SO THE COVERAGE IS NOT OVERREAD. The checker reduces each route block's prose
to CLAUSES, and only a clause that carries all of
  (a) at least one gene symbol from that route's own `genes` table,
  (b) a platform reference (`GPL6244`, `GPL3290`, or "both/either platform"), and
  (c) exactly one unambiguous polarity
is checked. Everything else is skipped, and the ambiguous ones are REPORTED BY NAME rather than
silently dropped — a guard whose coverage is invisible is the `subagent_width` failure again.
Measured on the committed artifact: 5 readability assertions and 16 direction assertions, 0 failures,
1 clause honestly reported as too tangled to reduce.

⛔ THE TWO FALSE-POSITIVE HAZARDS, BOTH REAL, BOTH HANDLED EXPLICITLY.
  1. A RETRACTED SENTENCE QUOTED INLINE. RT-ALK-HIT's corrected paragraph quotes the false sentence
     in single quotes so a reader can see what changed. A naive checker fires on the retraction it
     was written to record. `_strip_retracted` removes a quoted span ONLY when a retraction cue
     ("it read", "CORRECTED", "retract", …) sits in the 220 characters before it — the same shape
     `lint_consistency.py` already uses to clear a correctly-written retraction.
  2. A GROUP CLAIM THAT NAMES A MEMBER. "the GDNF-family ligands are LOWER on both" is a claim about
     a group mean, and GDNF-the-gene is +0.027 on GPL6244 — checking the group sentence against the
     member's cell reports a contradiction that is not one. Measured: without `_GROUP_NOUN` this
     exact clause is the only failure on a green artifact. Direction clauses containing group
     language are therefore skipped, and so are ones where the symbol is not the clause's subject.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODALITIES = os.path.join(ROOT, "research", "modalities")
GENERATOR = os.path.join(MODALITIES, "census_route_expression_grading.py")
ARTIFACT = os.path.join(MODALITIES, "census-route-expression-grading.json")

#: The platform key as the panel artifact spells it, keyed by the name the PROSE uses.
PLATFORM = {"GPL6244": "GSE24369_series_matrix.txt.gz",
            "GPL3290": "GSE4303-GPL3290_series_matrix.txt.gz"}

#: Clause boundaries. ⚠ NOT a bare " and " — that would split "ALK and ROS1 have no probe on GPL6244
#: or GPL3290" (the original false sentence) into two halves that each lose something, and the point
#: of this guard is that THAT sentence fails it.
_CLAUSE = re.compile(r"(?<=[.;:])\s+|\s+—\s+|\s+--\s+|,\s+and\s+|,\s+but\s+|,\s+while\s+|,\s+so\s+")

_READ = re.compile(r"\breadable\b|\bprobe\b|\bunreadable\b|\bunread\b", re.I)
_NEG = re.compile(r"\b(not|no|never|neither|nor|cannot|absent|without|missing|lacks|lacking|"
                  r"unmapped)\b", re.I)
_RETRACT = re.compile(r"it read|CORRECTED|retract|superseded|said until|old sentence|first said",
                      re.I)
_BOTH = re.compile(r"\b(both|either)\s+(platform|array|series)|\bon\s+(BOTH|both|either)\b")
_HIGHER = re.compile(r"\bHIGHER\b|\bhigher\b|\belevated\b|\bis up\b|\bare up\b")
_LOWER = re.compile(r"\bLOWER\b|\blower\b|\bis down\b|\bare down\b|\breduced\b")
_SUBJECT = re.compile(r"\b(is|are|sits|sit|reads|read)\b")

#: ⛔ Group language. A clause containing any of these is talking about a MODULE, not a gene, even
#: when it names one — see hazard 2 in the docstring. Widening this list is the correct fix if a
#: future prose edit trips this guard falsely; the failure message says so.
_GROUP_NOUN = re.compile(
    r"\b(module|family|group|panel|set|axis|arm|locus|machine|machinery|contrast|programme|program|"
    r"metagene|guardians|together|members?|complex|signature|methylosome|ligands|output)\b", re.I)

#: How far before a readability word a negation may sit and still govern it. "no probe", "NOT
#: READABLE", "the single missing ALK probe" all fit; "readable on GPL6244 … and not on GPL3290"
#: does not, and is reported as ambiguous rather than guessed at.
_NEG_REACH = 16


def _strip_retracted(text: str) -> str:
    out, i = [], 0
    for m in re.finditer(r"'([^']{20,})'", text):
        if _RETRACT.search(text[max(0, m.start() - 220):m.start()]):
            out.append(text[i:m.start()])
            i = m.end()
    out.append(text[i:])
    return "".join(out)


def _platforms(clause: str) -> list[str]:
    if _BOTH.search(clause):
        return list(PLATFORM)
    return [p for p in PLATFORM if p in clause]


def _readability_polarity(clause: str) -> str | None:
    """'neg' | 'pos' | 'ambiguous' | None (no readability claim in this clause)."""
    m = _READ.search(clause)
    if not m:
        return None
    if _NEG.search(clause[max(0, m.start() - _NEG_REACH):m.start()]):
        return "neg"
    if _NEG.search(clause):
        return "ambiguous"
    return "pos"


def _clauses(route: dict):
    genes = route.get("genes") or {}
    for field, text in route.items():
        if not isinstance(text, str):
            continue
        for clause in _CLAUSE.split(_strip_retracted(text)):
            symbols = [g for g in genes if re.search(rf"\b{re.escape(g)}\b", clause)]
            if not symbols:
                continue
            platforms = _platforms(clause)
            if not platforms:
                continue
            yield field, clause, symbols, platforms, genes


def readability_claims(routes: dict):
    """(failure, ambiguous) — prose readability assertions checked against the emitted table."""
    failures, ambiguous = [], []
    checked = 0
    for rid, route in routes.items():
        for field, clause, symbols, platforms, genes in _clauses(route):
            polarity = _readability_polarity(clause)
            if polarity is None:
                continue
            if polarity == "ambiguous":
                ambiguous.append(f"{rid}.{field}: {clause.strip()[:160]}")
                continue
            want = polarity == "pos"
            for symbol in symbols:
                for platform in platforms:
                    got = bool(genes[symbol].get(PLATFORM[platform], {}).get("readable"))
                    checked += 1
                    if got != want:
                        failures.append(
                            f"{rid}.{field}: the prose asserts {symbol} is "
                            f"{'READABLE' if want else 'NOT READABLE'} on {platform}, but the "
                            f"`genes` table emitted by the same function from the same artifact "
                            f"says readable={got}  ::  {clause.strip()[:200]}")
    return failures, ambiguous, checked


def direction_claims(routes: dict):
    """(failure, checked) — prose HIGHER/LOWER assertions against `delta_emc_minus_comparator`."""
    failures = []
    checked = 0
    for rid, route in routes.items():
        for field, clause, symbols, platforms, genes in _clauses(route):
            if _GROUP_NOUN.search(clause):
                continue
            higher, lower = bool(_HIGHER.search(clause)), bool(_LOWER.search(clause))
            if higher == lower:
                continue
            for symbol in symbols:
                after = clause[clause.find(symbol) + len(symbol):][:24]
                if not _SUBJECT.search(after):
                    continue
                for platform in platforms:
                    delta = genes[symbol].get(PLATFORM[platform], {}).get(
                        "delta_emc_minus_comparator")
                    if delta is None:
                        continue
                    checked += 1
                    if (delta > 0) != higher:
                        failures.append(
                            f"{rid}.{field}: the prose asserts {symbol} is "
                            f"{'HIGHER' if higher else 'LOWER'} in EMC on {platform}, but the "
                            f"`genes` table says delta_emc_minus_comparator={delta}  ::  "
                            f"{clause.strip()[:200]}. ⚠ If this clause is a GROUP claim that merely "
                            f"names a member gene, the fix is one word in `_GROUP_NOUN`, not a "
                            f"change to the prose.")
    return failures, checked


@pytest.fixture(scope="module")
def built():
    """⛔ THE PROSE IS READ FROM THE GENERATOR, NOT ONLY FROM THE COMMITTED JSON. The sentence is
    typed in the `.py`; checking only the artifact would leave a window in which the source is wrong
    and the guard is green because nobody has regenerated yet."""
    spec = importlib.util.spec_from_file_location("_crg_under_test", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_crg_under_test"] = module
    spec.loader.exec_module(module)
    return module.build()


@pytest.fixture(scope="module")
def committed():
    with open(ARTIFACT, encoding="utf-8") as fh:
        return json.load(fh)


def test_the_committed_artifact_is_what_the_generator_emits(built, committed):
    """A stale artifact means the prose this guard checked is not the prose anybody reads."""
    assert built == committed, (
        "research/modalities/census-route-expression-grading.json is not what "
        "census_route_expression_grading.py emits — re-run the generator.")


def test_no_prose_readability_claim_contradicts_the_table_beside_it(built):
    """⛔ THE AUT-PD-181 REGRESSION TEST. This is the assertion the RT-ALK-HIT sentence failed for
    twenty days with nothing to notice."""
    failures, _ambiguous, checked = readability_claims(built["routes"])
    assert checked >= 5, (
        f"only {checked} readability assertion(s) were reachable — the clause reducer has stopped "
        "seeing prose it used to see, which makes this guard green for the wrong reason.")
    assert failures == [], "\n".join(failures)


def test_no_prose_direction_claim_contradicts_the_table_beside_it(built):
    failures, checked = direction_claims(built["routes"])
    assert checked >= 16, (
        f"only {checked} direction assertion(s) were reachable — see the note above; a guard that "
        "quietly stops checking is worse than no guard.")
    assert failures == [], "\n".join(failures)


def test_the_clauses_this_guard_cannot_reduce_are_named_not_hidden(built):
    """⭐ COVERAGE IS PART OF THE VERDICT. One clause in the corrected RT-ALK-HIT paragraph mixes a
    positive and a negative readability claim across a conjunction and cannot be reduced to one
    polarity. That is a real limit of a clause-level checker and it is REPORTED — the ledger item
    this guard closes was filed against a checker that hid what it could not read."""
    _failures, ambiguous, _checked = readability_claims(built["routes"])
    assert len(ambiguous) <= 2, (
        "the number of unreducible readability clauses has grown; each one is prose no guard is "
        "checking:\n" + "\n".join(ambiguous))


def test_the_retraction_stripper_does_not_swallow_a_live_claim():
    """⛔ MUTATION-CHECKED IN BOTH DIRECTIONS. Hazard 1's fix is an escape hatch — quote a false
    sentence and it stops being checked — so the stripper must fire ONLY behind a retraction cue."""
    retracted = ("⛔ CORRECTED 2026-08-29: it read 'ALK and ROS1 have no probe on GPL6244 or "
                 "GPL3290' and that was false.")
    assert "no probe" not in _strip_retracted(retracted)
    live = "The lead names two kinases and 'ALK and ROS1 have no probe on GPL6244 or GPL3290'."
    assert "no probe" in _strip_retracted(live), (
        "a quoted sentence with no retraction cue in front of it was stripped — that turns quoting "
        "into a way to smuggle an unchecked claim past this guard.")


def test_the_original_false_sentence_would_be_caught(built):
    """⛔⛔ THE MUTATION TEST, ON A DEEP COPY AND NEVER ON THE TREE (CLAUDE.md §6, 2026-08-27). Put
    the twenty-day-old false sentence back into an in-memory copy of the artifact and the guard must
    go red. A guard that has never been shown to fail is a guard nobody has tested."""
    mutated = json.loads(json.dumps(built))
    mutated["routes"]["RT-ALK-HIT"]["observed"] = (
        "Both kinases the lead names are NOT READABLE on EITHER platform. "
        "ALK and ROS1 have no probe on GPL6244 or GPL3290.")
    failures, _ambiguous, _checked = readability_claims(mutated["routes"])
    assert failures, "the sentence that stood for twenty days still passes"
    assert any("ROS1" in f and "GPL6244" in f for f in failures), failures


def test_a_flipped_direction_claim_would_be_caught(built):
    mutated = json.loads(json.dumps(built))
    mutated["routes"]["RT-ARGININE"]["observed"] = (
        "ASS1 is LOWER in EMC than in comparator sarcomas on BOTH platforms.")
    failures, _checked = direction_claims(mutated["routes"])
    assert any("ASS1" in f for f in failures), failures


def test_an_unreadable_gene_claimed_readable_would_be_caught(built):
    """The other polarity: RT-NR2F1's gene really is unreadable on both platforms, and a sentence
    claiming otherwise must fail — the direction the twenty-day error did NOT run in."""
    mutated = json.loads(json.dumps(built))
    mutated["routes"]["RT-NR2F1"]["observed"] = (
        "NR2F1 is readable on both platforms and sits mid-array.")
    failures, _ambiguous, _checked = readability_claims(mutated["routes"])
    assert any("NR2F1" in f for f in failures), failures
