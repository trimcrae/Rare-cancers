"""⛔⛔ THE CLAIMS `claim_coverage.py` FOUND THAT NO SELECTIVE INSTRUMENT READ.

Fifteen review rounds, and the BLOCKER count rose rather than fell: three distinct in round 14, six
in round 15. Read together, every one of those nine was the same shape — a surface with ZERO
instruments, not a number a guard got wrong. So the blocker rate was tracking how many new LENSES
each round introduced, not how many defects remained: a new seat looks somewhere nobody looked and
finds the first thing there, and that never converges by iteration because there is always another
unexamined patch.

`research/manuscripts/claim_coverage.py` was written to end that by ENUMERATING the patches instead
of sampling them. It asks, of every assertive sentence, whether any SELECTIVE committed pattern
matches it. This file closes the mechanically-checkable part of the residue — every claim below was
on that uncovered list and is now bound to the artifact that decides it.

⛔ THE LIVE COVERAGE FIGURES ARE NOT IN THIS DOCSTRING AND MUST NOT BE COPIED INTO IT. They have one
home, `research/manuscripts/claim-coverage.json` (regenerate: `python3
research/manuscripts/claim_coverage.py --write`), which carries every censused document rather than
this one, and they move whenever a guard is added or a sentence is edited. A count typed here is a
second copy that nothing re-measures — which is precisely what happened below.

⚠ HISTORY, NOT A CURRENT READING (retained 2026-08-27). This paragraph used to state, in the present
tense, "Its first honest run: **76 of 124 sentences in the journal article, and 47 of the 66 that
state a number.**" That was the census's FIRST run, taken while `claim_coverage.py` was still being
written and BEFORE any census artifact was committed, so it cannot be re-derived from this
repository: the earliest committed `claim-coverage.json` — `1fd33bbbb`, 2026-08-27, the same commit
that added this module — already read 80 of 154 (54 of 78) for the same document. The 76/124 is kept
because it is the EVIDENCE FOR ENUMERATING rather than sampling, which is this file's whole argument;
it is not a statement about the paper as it now stands. For that, read the artifact.

⚠ MECHANICALLY CHECKABLE IS NOT THE SAME AS IMPORTANT, and this file covers only the first. A claim
like "no such design is reported in the literature retrieved here" is on the uncovered list too and
cannot be bound to an artifact at all — it is bounded by a fetch record and by honesty. The census
names those separately rather than letting them hide among the ones a test can hold.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")
SEQ_CSV = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
GAP_PAIRING = os.path.join(REPO, "research", "modalities", "aso-parent-gap-pairing.json")
PREMRNA = os.path.join(REPO, "research", "modalities", "aso-premrna-offtarget.json")

_JUNCTION = re.compile(r"^([A-Z0-9]+)_e(\d+)__([A-Z0-9]+)_e(\d+)$")


@pytest.fixture(scope="module")
def prose():
    return re.sub(r"\s+", " ", io.open(ARTICLE, encoding="utf-8").read())


def _artifact(path, what):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.basename(path)} is missing, so {what} is unchecked")
    return json.load(io.open(path, encoding="utf-8"))


def _rows():
    with io.open(SEQ_CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))


def _named_reagents():
    rows = _rows()
    seqs = set(re.findall(r"5′-([ACGT]{16})-3′",
                          re.sub(r"\s+", " ", io.open(ARTICLE, encoding="utf-8").read())))
    named = {r["sequence"]: r for r in rows if r["sequence"] in seqs
             and r["junction"].endswith("_e3") and "best available" in (r.get("role") or "")}
    return named


def test_the_panels_single_acceptor_is_the_panels_own(prose):
    """⛔ "Every design in the panel joins its donor to *NR4A3* exon 3" — DERIVED, NOT ASSERTED.

    This is the sentence that makes §4's exon-2 discussion coherent: the cell models are reported at
    exon 2, so they carry a panel junction only under the exon-3 reading. If a later panel ever
    admitted an exon-2 record, this sentence would silently become false and the argument built on
    it would collapse — and round 15's blocker was in this exact neighbourhood.
    """
    per = _artifact(GAP_PAIRING, "the panel")["per_design"]
    acceptors = {_JUNCTION.match(d["junction"]).group(4) for d in per if _JUNCTION.match(d["junction"])}
    stated = re.search(r"Every design in the panel joins its donor to \*?NR4A3\*? exon (\d+)", prose)
    assert stated, ("§4 no longer states which acceptor every panel design joins; that sentence is "
                    "what makes the exon-2 cell-model discussion readable")
    assert acceptors == {stated.group(1)}, (
        f"the article says every panel design joins *NR4A3* exon {stated.group(1)}; the panel's own "
        f"records carry acceptor exon(s) {sorted(acceptors)}")


def _geometry():
    """The architecture the panel was tiled at, read from the canonical file rather than typed."""
    geoms = {r["geometry"] for r in _named_reagents().values()}
    assert len(geoms) == 1, f"the named reagents span geometries {sorted(geoms)}"
    return geoms.pop()


def _wing_length():
    """The locked wing of the panel's architecture: the first number of `wing-gap-wing`."""
    return int(_geometry().split("-")[0])


def test_the_near_match_definition_is_the_screens_own_ceiling(prose):
    """⛔ A DEFINITION WITH NUMBERS IN IT IS A CRITERION, AND CRITERIA WERE THE ROUND-15 BLOCKER.

    "14 or more of its 16 positions" is 2 mismatches on a 16-mer, which is `method.max_mismatches`.
    Nothing read it: changing 14 to 13 would have redefined every near-match the paper reports while
    every count stayed put.
    """
    ceiling = _artifact(PREMRNA, "the precursor screen")["method"]["max_mismatches"]
    m = re.search(r"near-match is a transcript window pairing a design at (\d+) or more of its "
                  r"(\d+) positions", prose)
    assert m, "§8's near-match definition has been reworded; re-anchor this guard to it ⛔ CHECK THE MEANING BEFORE THE REGEX: if the claim was INVERTED or DROPPED, re-anchoring makes the guard agree with the new wording and the finding disappears. Re-anchor only when the sentence says the same thing in different words."
    at_least, length = int(m.group(1)), int(m.group(2))
    # ⛔⛔ THE DIFFERENCE IS NOT THE DEFINITION (round 16 seat 5, mutation M03). This asserted only
    # `length - at_least == ceiling`, so "14 or more of its 16" -> "13 or more of its 15" PRESERVES
    # the checked quantity and redefines the window the screen was run over. The design length is a
    # fact about the panel, not a free parameter of the sentence.
    designed = {len(q) for q in _named_reagents()}
    assert designed == {length}, (
        f"the article defines a near-match over {length} positions; the named reagents are "
        f"{sorted(designed)}-mers per the canonical file. A window that is not the design length "
        "describes a screen that was not run.")
    assert length - at_least == ceiling, (
        f"the article defines a near-match as {at_least} of {length} positions, which allows "
        f"{length - at_least} mismatches; the screen was run at max_mismatches={ceiling}")


def _synthesis_reagents(prose):
    """The reagents §2 names FOR SYNTHESIS, read off the sentence that names them.

    ⛔⛔ WHY NOT `_named_reagents()` (2026-08-24). That helper returns every 16-mer the article
    prints whose canonical row is an exon-3 "best available at this junction" design, and until this
    date that set happened to equal the synthesis pair. §2 then gained a THIRD such sequence —
    5′-GGGCATATCTCCACGG-3′ at *EWSR1* exon 13, printed so a laboratory holding USZ20-EMC1 can order
    the molecule §4 sends it to, and explicitly NOT named for synthesis. The g-tract sentence below
    says "Both", so a guard reading three molecules is no longer reading that sentence's subject.
    ★ THE FIX IS TO READ THE SUBJECT FROM THE PROSE, not to widen the claim to whatever is printed:
    "Both" is a count, and a guard that silently accepts three has stopped checking it.
    """
    m = re.search(r"The (two) reagents named for synthesis are.*?\(Table 1\)", prose)
    assert m, ("§2 no longer names its synthesis reagents in the sentence this guard reads. "
               "⛔ CHECK THE MEANING BEFORE THE REGEX: if the paper now names a different number "
               "of reagents, that is a change to what it asks a laboratory to make, not a wording "
               "change to re-anchor past.")
    seqs = re.findall(r"5′-([ACGT]{16})-3′", m.group(0))
    assert len(seqs) == 2, (
        f"§2 says TWO reagents are named for synthesis and that sentence prints {len(seqs)}: "
        f"{seqs}. The count and the sequences must agree — a reader orders what is printed.")
    return seqs


def test_the_named_reagents_g_tract_claim_is_read_off_their_sequences(prose):
    """⛔ "Both begin 5′-GGG, a contiguous locked G-tract" — a SEQUENCE property, from the sequences."""
    named = _synthesis_reagents(prose)
    rows = {r["sequence"] for r in _rows()}
    unknown = [s for s in named if s not in rows]
    assert not unknown, (
        f"§2 names {unknown} for synthesis and the canonical sequence file carries no such row. A "
        "sequence printed as an order must be one the canonical file decides the properties of.")
    m = re.search(r"Both begin 5′-([ACGT]+), a contiguous locked", prose)
    assert m, "§2's G-tract sentence has been reworded; re-anchor this guard ⛔ CHECK THE MEANING BEFORE THE REGEX: if the claim was INVERTED or DROPPED, re-anchoring makes the guard agree with the new wording and the finding disappears. Re-anchor only when the sentence says the same thing in different words."
    tract = m.group(1)
    # ⛔⛔ "STARTS WITH" IS NOT THE CLAIM (round 16 seat 5, mutation M04). The sentence says the
    # tract is a CONTIGUOUS LOCKED G-tract, and a prefix check alone accepted widening it to a
    # 9-mer that is neither all-G nor inside the locked wing — both reagents still "begin" with it,
    # so the guard stayed green while the sentence described a different molecule feature.
    assert set(tract) == {"G"}, (
        f"the article calls 5′-{tract} a G-tract; it is not all G. A tract naming other bases is "
        "not the homopolymer run the sentence claims.")
    wing = _wing_length()
    assert len(tract) <= wing, (
        f"the article calls 5′-{tract} ({len(tract)} nt) a contiguous LOCKED G-tract, but the "
        f"{_geometry()} architecture locks only the {wing}-nt wing. A tract longer than the wing "
        "runs into the DNA gap, where the bases are not locked.")
    wrong = sorted(s for s in named if not s.startswith(tract))
    assert not wrong, (
        f"the article says both named reagents begin 5′-{tract}; {wrong} do not, per the canonical "
        "sequence file")


def test_the_taf15_reagents_clean_precursor_claim_is_the_screens_own(prose):
    """⛔ AN ABSENCE CLAIM, WHICH IS THE HARDEST KIND TO NOTICE GOING WRONG.

    "The *TAF15* reagent carries no sense-strand precursor site" is a claim about a count being ZERO.
    Nothing read it, and a zero that becomes a one produces no new number anywhere in the prose —
    the sentence simply stops being true.
    """
    named = _named_reagents()
    taf = [s for s, r in named.items() if r["junction"].startswith("TAF15")]
    assert len(taf) == 1, f"expected one named TAF15 reagent; found {taf}"
    per = _artifact(PREMRNA, "the precursor screen")["per_design"]
    rows = [d for d in per if d["antisense_5to3"] == taf[0]]
    assert rows, f"{taf[0]} is not in the precursor screen at all, so the claim is unverifiable"
    # ⛔⛔ `or 0` READ A NULL AS A ZERO (round 16 seat 5, mutation M05). Setting `n_hybridisable`
    # to null in the screen record made an ABSENCE claim pass by turning a missing measurement into
    # a measured absence — CLAUDE.md's "an absent reading is not a reading of absence", inside the
    # guard written for the hardest-to-notice claim in the paper.
    missing = [d for d in rows if d.get("n_hybridisable") is None]
    assert not missing, (
        f"the precursor screen records no `n_hybridisable` for {len(missing)} row(s) of {taf[0]}, "
        "so whether it carries a sense-strand precursor site was never measured. That is not the "
        "same as measuring zero, and the article states an absence.")
    hits = max(int(d["n_hybridisable"]) for d in rows)
    stated_clean = re.search(r"\*?TAF15\*? reagent carries no sense-strand precursor site", prose)
    assert stated_clean, "§2's TAF15 precursor sentence has been reworded; re-anchor this guard ⛔ CHECK THE MEANING BEFORE THE REGEX: if the claim was INVERTED or DROPPED, re-anchoring makes the guard agree with the new wording and the finding disappears. Re-anchor only when the sentence says the same thing in different words."
    assert hits == 0, (
        f"the article says the TAF15 reagent carries no sense-strand precursor site; the precursor "
        f"screen records {hits} hybridisable hit(s) for {taf[0]}")
