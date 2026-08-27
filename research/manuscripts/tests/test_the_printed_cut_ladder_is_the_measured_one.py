"""Every cell of §2.5's cut-ladder table must be the artifact's own number.

⛔ WHY THIS EXISTS, AND IT IS NOT HYPOTHETICAL. The ladder was measured on 2026-08-19 and typed into
the manuscript as an eleven-column table. Two of its 88 cells were wrong on the first printing: the
"strongest null" column carried the `exon_terminus_chimera` rate at every cut, but at cuts 6 and 9
the strongest arm is `exon_terminus_chimera_novel_acceptor` (98.2 against the printed 97.8; 56.8
against the printed 56.2). The signed-excess column beside it had been computed against the TRUE
maximum, so the table contradicted itself in the same row and the error was invisible to any check
that read one column at a time. A guard-suite audit found it by reading, which is the instrument
this file replaces.

★ THE TABLE IS THE PAPER'S ANSWER TO "IS 87 OF 190 A FINDING OR AN ARTEFACT OF THE CUT?", so a
stale or mistyped cell in it is not a typo — it is the evidence for the central negative. Every cell
is recomputed here from `aso-parent-null.json` and compared to what the manuscript prints.
"""
from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAPER = os.path.join(os.path.dirname(HERE), "aso", "fusion-junction-aso-research-article.md")
#: ⛔⛔ THE ONE-OF-A-PAIR DEFECT, RE-CREATED IN THE GUARD FOR THIS PAPER'S CENTRAL NEGATIVE
#: (round 9, citations-and-instruments seat, 2026-08-27). `PAPER` above is the EXTENDED REPORT.
#: The submitted journal article carries the same sentence — "across cuts of six to thirteen base
#: pairs the excess over the strongest null changes sign four times" — and NOTHING read it, so
#: inverting it there ("does not change sign", "changes sign once") passed every gate in the repo.
#: ⚠ The `flips == 4` half was always derived from the artifact and always bound; it is the
#: PROSE half that was bound in one document of two. That is the class this suite has now found
#: seven times, and it keeps recurring because a guard written for one document looks complete.
#: ★ Both are asserted below, by iterating a tuple rather than by a second copied assertion —
#: a copied assertion is how the pair separates again the next time a paper is added.
JOURNAL = os.path.join(os.path.dirname(HERE), "aso", "fusion-junction-aso-journal-article.md")
PAPERS_CARRYING_THE_SIGN_CHANGE_CLAIM = (PAPER, JOURNAL)
ART = os.path.join(os.path.dirname(os.path.dirname(HERE)), "modalities", "aso-parent-null.json")


def _art():
    if not os.path.exists(ART):
        pytest.fail(f"the null artifact is missing: {ART}")
    return json.load(open(ART, encoding="utf-8"))


def _rows():
    """The ladder rows as printed, keyed by cut. Fails loudly rather than passing on no match."""
    if not os.path.exists(PAPER):
        pytest.fail(f"the manuscript is missing: {PAPER}")
    text = open(PAPER, encoding="utf-8").read()
    rows = {}
    for line in text.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("*").strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 11 or not re.fullmatch(r"\d+", cells[0]):
            continue
        rows[cells[0]] = cells
    assert rows, (
        "no cut-ladder row was found in the manuscript. Either the table has moved or its shape "
        "changed; re-anchor this guard rather than deleting it — the table is the paper's answer "
        "on whether the criterion drives the result")
    return rows


def test_the_ladder_column_headed_for_the_published_junctions_names_designs():
    """The header must not promise junctions where the cells count designs.

    ⚠ FIVE junctions carry a published exon-resolved breakpoint; 25 designs are tiled across them.
    A header reading "junctions" over a denominator of 25 is a denominator switch inside one cell.
    """
    art, rows = _art(), _rows()
    n_junctions = len(art["cut_sensitivity"]["published_breakpoint_junctions"])
    text = open(PAPER, encoding="utf-8").read()
    header = next((ln for ln in text.split("\n")
                   if ln.startswith("| cut (bp)") or "published-breakpoint" in ln and ln.startswith("|")), "")
    assert "published-breakpoint" in header, "the ladder's header row has moved; re-anchor"
    assert "designs still liable" in header, (
        f"the column counts designs across the {n_junctions} published-breakpoint junctions, and "
        "its header must say so — it read 'published-breakpoint junctions still liable' over cells "
        f"denominated in designs, which is a denominator switch inside a single cell")
    assert f"{n_junctions} published-breakpoint" in header or "five published-breakpoint" in header, (
        "the header should name how many such junctions there are, so the denominator is placeable")


def test_the_ladder_prints_every_cut_the_artifact_measures():
    art, rows = _art(), _rows()
    cuts = [str(c) for c in art["cut_sensitivity"]["cut_ladder_bp"]]
    assert sorted(rows, key=int) == sorted(cuts, key=int), (
        f"the table prints cuts {sorted(rows, key=int)} and the artifact measures {cuts}. A cut "
        "measured and not printed is a cut the reader cannot check the criterion against")


@pytest.mark.parametrize("cut", [str(c) for c in (6, 7, 8, 9, 10, 11, 12, 13)])
def test_every_printed_cell_is_the_measured_value(cut):
    art, rows = _art(), _rows()
    cs, ne = art["cut_sensitivity"], art["null_ensembles"]
    if cut not in rows:
        pytest.fail(f"cut {cut} is measured but not printed in §2.5's ladder")
    c = rows[cut]
    obs = cs["observed_cut_ladder"][cut]
    pub = cs["observed_cut_ladder_at_published_breakpoint_junctions"][cut]

    assert c[1] == str(obs["n_liable"]), f"cut {cut}: liable count"
    assert c[2] == f"{100 * obs['rate_liable']:.1f}", f"cut {cut}: liable rate"
    lo, hi = (100 * x for x in obs["rate_liable_wilson95"])
    assert c[3] == f"{lo:.1f}–{hi:.1f}", f"cut {cut}: Wilson interval"

    # ⛔ THE CELL THAT WAS WRONG. The strongest null is an argmax over the ensembles AT THIS CUT and
    # it is not the same arm at every cut, so it cannot be read off one ensemble.
    arm = max(ne, key=lambda k: ne[k]["cut_ladder"][cut]["rate_liable"])
    strongest = 100 * ne[arm]["cut_ladder"][cut]["rate_liable"]
    assert c[4].startswith(f"{strongest:.1f}"), (
        f"cut {cut}: the strongest null is {arm} at {strongest:.1f}%, and the table prints {c[4]!r}")
    assert arm.replace("exon_terminus_chimera_novel_acceptor", "novel acceptor").split("_")[0] in c[4], (
        f"cut {cut}: the cell must name which arm is strongest, because they change places")

    scr = 100 * ne["scrambled_mononucleotide"]["cut_ladder"][cut]["rate_liable"]
    assert c[5] == f"{scr:.1f}", f"cut {cut}: scramble null"

    excess = 100 * obs["rate_liable"] - strongest
    assert c[6] == f"{excess:+.1f}".replace("-", "−"), (
        f"cut {cut}: the signed excess must be computed against the SAME null the row names "
        f"({excess:+.1f}), which is exactly what it was not on first printing")

    want = "inside" if lo <= strongest <= hi else ("outside, above" if strongest > hi else "outside, below")
    assert c[7] == want, f"cut {cut}: the null sits {want} the observed interval"
    assert c[8] == f"{cs['n_junctions_with_a_clearing_design_by_cut'][cut]} of 38", f"cut {cut}: junctions"
    # ⛔ THIS COLUMN IS DESIGNS, NOT JUNCTIONS, AND THE HEADER SAID JUNCTIONS UNTIL 2026-08-19.
    # There are FIVE published-breakpoint junctions in the panel and 25 designs across them, so a
    # cell reading "25 of 25" under a junction header told a reader every one of five junctions was
    # liable using a denominator of 25. The guard pinned the cell and therefore CERTIFIED the
    # mislabel — which is why the denominator is now derived from the artifact and the header is
    # asserted to name designs.
    n_pub_designs = art["cut_sensitivity"]["observed_cut_ladder_at_published_breakpoint_junctions"]
    total_pub = max(v["n_liable"] for v in n_pub_designs.values())
    assert c[9] == f"{pub['n_liable']} of {total_pub}", (
        f"cut {cut}: this column counts DESIGNS at the five published-breakpoint junctions")
    assert c[10] == str(obs["n_pairing_NR4A3_specifically"]), (
        f"cut {cut}: this column is the NR4A3-SPECIFIC count, not the attributed one "
        f"({obs['n_pairing_NR4A3_specifically']} against {obs['n_liable_attributed_to_NR4A3']}); "
        "the two diverge as the cut loosens and only one of them is per-gene")


def test_the_prose_claim_of_four_sign_changes_is_the_measured_one():
    """The paragraph's load-bearing claim, derived rather than trusted."""
    art = _art()
    cs, ne = art["cut_sensitivity"], art["null_ensembles"]
    signs = []
    for cut in (str(c) for c in cs["cut_ladder_bp"]):
        obs = 100 * cs["observed_cut_ladder"][cut]["rate_liable"]
        strongest = max(100 * ne[k]["cut_ladder"][cut]["rate_liable"] for k in ne)
        signs.append(obs > strongest)
    flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
    assert flips == 4, (
        f"the excess over the strongest null now changes sign {flips} times, not four. §2.5 says "
        "four; recompute the sentence rather than the guard")
    for path in PAPERS_CARRYING_THE_SIGN_CHANGE_CLAIM:
        text = open(path, encoding="utf-8").read()
        assert "changes sign four times" in text, (
            f"{os.path.basename(path)} no longer carries the sign-change claim. "
            "The sign-change claim has been reworded away from the measured value. "
            "⛔ CHECK THE MEANING BEFORE THE REGEX: if the claim was INVERTED or DROPPED, "
            "re-anchoring makes the guard agree with the new wording and the finding "
            "disappears. Re-anchor only when the sentence says the same thing in different "
            "words. It is the sentence that replaced 'ten is the cut at which the observed "
            "rate stands clear of every null', so it must keep saying what the ladder "
            "measures.")
