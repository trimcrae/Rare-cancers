"""Universal and counted claims must not be wider than the quantity that was actually measured.

⛔ WHY. On 2026-08-18 an exhaustive audit of all 251 universal/counted sentences in the manuscript
returned six findings, two of them CONFIRMED CONTRADICTIONS of the paper's own content. Every one had
the same shape: a sentence whose scope was left open ("every", "the only", "outside every") while the
measurement behind it covered a subset. None was a wrong number — the arithmetic was right in all six
— so no numeric test could have caught them.

⛔⛔ AND THEY WERE MISSED BY EIGHT PRIOR BLIND SCREENS. The class only started surfacing once the
screening brief was widened to name it explicitly. That is the reason this file exists: a screener
finds this class only if it is told to look, and a test is told every time.

The six, and what each now has to say instead:

1. §2.10 / Table 4 caption — ΔΔG°37 was called the margin over "the best duplex either parent can
   form". The generator (junction_aso_thermo.py) scores only the two SEAM runs, donor-side and
   acceptor-side, which by the paper's own identity reach at most ten base pairs. 87 of the 190
   designs pair a mature parent at ten or more base pairs somewhere else. "Best" was wider than the
   search.
2. §4.3 / §5 — "It falls outside every parent count reported here" / "Every parent count requires the
   catalytic gap paired in full". The hit is sense-strand, intron–exon-spanning and one gap mismatch
   short, so it sits inside §2.5's 53, forty and 21 — which are parent counts. §5's version named
   "the 21 designs of §2.5" as a count in the same sentence that denied such counts exist.
3. §2.9 — "the 16-mer surviving at that junction". Two 16-mers survive at TCF12 exon 7.
4. §4.4 — an optional arm "only at EWSR1 exon 12", defended against TAF15 exon 6 alone while Table 2
   shows lower-margin registers clearing the parent screen at two of the other three junctions.
5. §2.7 — "The genome scan, screen 5, removes that bound", said of both liability classes. Screen 5
   runs at two mismatches; an eleven-base-pair run inside a 16-mer carries five.
6. §5 — "Every screened count outside §2.9 is for one architecture", falsified by §4.2 and Table 5.

★ EACH TEST BELOW PINS THE CORRECTED SCOPE, NOT THE WORDING. The prose may be rewritten freely; what
may not come back is the open quantifier over a measurement that does not reach that far.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ARTICLE = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
TABLES = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-submission-tables.md")


def _read(path):
    if not os.path.exists(path):
        pytest.fail(f"missing artefact: {path}")
    return open(path, encoding="utf-8").read()


def _body():
    text = _read(ARTICLE)
    return re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)


def _sentences(text):
    """Prose sentences only — table rows and fenced blocks carry no universals to audit."""
    prose = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    prose = "\n".join(ln for ln in prose.splitlines() if not ln.lstrip().startswith("|"))
    prose = prose.replace("\n", " ")
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", prose) if s.strip()]


# ── 1 · the free-energy margin is over the seam, not over the transcriptome ──────────────────


def test_the_free_energy_margin_is_never_called_the_best_duplex_a_parent_can_form():
    """ΔΔG°37 scores the donor-side and acceptor-side seam runs. It does not search a parent."""
    for path in (ARTICLE, TABLES):
        text = _read(path)
        for bad in ("best duplex either parent can form",
                    "best duplex the parents can form",
                    "best parent duplex"):
            assert bad not in text, (
                f"{os.path.basename(path)} calls the free-energy margin '{bad}'. The generator scores "
                "only the two seam runs at the junction; 87 designs pair a mature parent longer than "
                "that elsewhere, so this phrasing claims a search that was never run. See §2.5.")


def test_the_free_energy_section_says_what_the_margin_is_not_scored_against():
    """Naming the seam is not enough — the reader has to be told the mature duplexes are excluded."""
    body = _body()
    where = body.find("Scored as free energies")
    assert where != -1, "§2.10's free-energy result no longer opens with 'Scored as free energies'."
    opening = body[where:where + 900]
    assert "at the junction itself" in opening, (
        "§2.10 must say the comparison is to the runs a parent pairs AT THE JUNCTION, not to any "
        "duplex it can form.")
    assert "§2.5" in opening and "not scored here" in opening, (
        "§2.10 must state that the mature-parent duplexes of §2.5 are not what the free energy "
        "scores. Without that the 'every one of the 190 designs' claim reads as proteome-wide.")


# ── 2 · no universal quantifier over the parent counts ──────────────────────────────────────


def test_no_sentence_quantifies_universally_over_the_parent_counts():
    """§2.5 reports 53 / forty / 21 as parent counts that do NOT require a fully paired gap."""
    # The quantifier has to GOVERN the noun. A sentence that scopes the set first and then
    # distributes over it ("the mature-parent counts … so each is a floor") is exactly the
    # corrected form, so proximity — not mere co-occurrence — is what this looks for.
    governs = re.compile(r"\b(every|all|each|any|no other|the only)\b[\w\s,-]{0,20}?\bparent counts?\b",
                         re.I)
    offenders = [s for s in _sentences(_body()) if governs.search(s)]
    assert not offenders, (
        "a sentence quantifies universally over 'parent count(s)':\n  "
        + "\n  ".join(offenders[:4])
        + "\n\n§2.5 reports 53 designs with a pre-mRNA near-match, forty on the sense strand and 21 "
          "pairing all of the gap but one or two positions. None of those requires the gap paired in "
          "full, so any 'every parent count …' sentence is false of the paper's own content. Say "
          "'the headline parent counts' and name what sits outside them.")


def test_the_premrna_hit_of_section_4_3_is_placed_inside_the_wider_tallies():
    """It is sense-strand, intron–exon-spanning and one gap mismatch short: it is one of the 21."""
    body = _body()
    where = body.find("intron–exon-spanning near-match in wild-type *TAF15* pre-mRNA")
    assert where != -1, "§4.3's TAF15 pre-mRNA near-match sentence has moved or been reworded away."
    passage = body[where:where + 900]
    assert "headline parent counts" in passage, (
        "§4.3 must scope the exclusion to the HEADLINE parent counts — the hit is inside §2.5's "
        "wider tallies.")
    for tally in ("53", "forty", "21"):
        assert tally in passage, (
            f"§4.3 must name the wider tally '{tally}' that this hit does sit inside, so a reader "
            "cannot conclude the paper counted it nowhere.")


def test_the_parent_exclusion_is_scoped_to_the_screen_that_makes_it():
    """Screen 1 excludes parent records. Screen 3's near-match counts ARE parent counts.

    Found by this file, not by the 251-claim audit: §6 said parent records were "excluded from every
    near-match count reported here", but §2.5 opens "Of the 190 designs, 53 have a near-match
    somewhere in parent pre-mRNA" — a near-match count that is nothing but parent records.
    """
    body = _body()
    assert "excluded from every near-match count" not in body, (
        "§6 excludes parent records from 'every near-match count reported here'. §2.5 reports 53 "
        "designs with a near-match in parent pre-mRNA, from screen 3, where the parent records are "
        "the measurement. Scope the exclusion to screen 1.")
    where = body.find("Records of the six parent genes are counted")
    assert where != -1, "§6's parent-record exclusion has moved or been reworded away."
    passage = body[where:where + 500]
    assert "this screen's near-match counts" in passage, (
        "§6 must scope the parent-record exclusion to the alignment screen that makes it.")
    assert "§2.5" in passage, (
        "§6 must point at §2.5, where parent near-match counts ARE reported, so the exclusion cannot "
        "be read as covering the whole paper.")


def test_the_two_nine_design_sets_are_never_left_to_look_like_one():
    """§3 discusses two DISJOINT sets of nine designs, two sentences apart, and never says so.

    Found by a blind reader of the deposit PDF, 2026-08-19. The first nine are Table 4's — the
    designs with no sense-strand near-match. The second nine are §2.5's intron–exon-spanning
    pre-mRNA sites. §2.5 states they cannot overlap: "None of the nine designs with no sense-strand
    near-match on either transcript screen carries one." Equal size, adjacent paragraphs, opposite
    meaning — a reader carries the liability onto the paper's cleanest molecules.

    This is the counted-phrase cousin of the universal-claim class: not a wrong number, a number
    whose referent is left open.
    """
    body = _body()
    assert "None of the nine designs with no sense-strand near-match" in body, (
        "§2.5's disjointness statement is gone — it is the evidence that the two sets of nine do not "
        "overlap, and without it the §3 passage cannot be checked at all.")
    where = body.find("The two parent compartments of §2.5 sharpen that")
    assert where != -1, "§3's parent-compartment passage has moved or been reworded away."
    passage = body[where:where + 400]
    assert "a different nine" in passage, (
        "§3 introduces a second set of nine designs two sentences after Table 4's nine, with nothing "
        "marking them as disjoint. Say 'a different nine' and point at §2.5.")
    assert "§2.5" in passage, (
        "§3 must cite §2.5, where the disjointness is established, so the distinction is checkable "
        "rather than asserted.")


# ── 3 · TCF12 exon 7 has two surviving 16-mers, not one ─────────────────────────────────────


_NUMBER_WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def _survivors_at_tcf12_exon7():
    """Derived, not asserted: Table 4's survivors plus the design the deeper pass added.

    Table 4 prints one row per design whose hit list is complete, with a 'survives' verdict in the
    last column. §2.4 reports a seventh design that failed at the remote service on the shallow pass
    and came back clean at the deeper ceiling — it is a survivor that Table 4 has no row for.
    """
    count = 0
    for row in _read(TABLES).splitlines():
        if not row.startswith("|") or "TCF12 e7::NR4A3 e3" not in row:
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cells[-1].strip("* ").lower() == "yes":
            count += 1
    body = _body()
    late = re.search(
        r"one — (5′-[ACGT]+-3′) at \*TCF12\* exon 7 — with three near-matches and none\s+on\s+the sense strand",
        body)
    if late:
        count += 1
    return count


def test_the_number_of_surviving_16mers_at_tcf12_exon7_is_stated_correctly():
    """§2.9's gap-length contrast compares an 18-mer against the 16-mers at the same junction."""
    n = _survivors_at_tcf12_exon7()
    assert n == 2, (
        f"derived {n} surviving 16-mers at TCF12 exon 7; the test's premise has changed. Re-derive "
        "before editing §2.9 — Table 4's 'survives' column and §2.4's late-returning design are the "
        "two sources.")
    body = _body()
    where = body.find("5′-CAGGGCATATCAAGCGCT-3′ at *TCF12* exon 7 returns no near-match")
    assert where != -1, "§2.9's gap-length contrast sentence has moved or been reworded away."
    sentence = body[where:where + 260]
    assert "the 16-mer surviving at that junction" not in sentence, (
        "§2.9 names 'the 16-mer surviving at that junction' in the definite singular, but two "
        "survive there — and the one Table 4 flags returns two near-matches, not three.")
    assert f"{_NUMBER_WORD[n]} 16-mers" in sentence, (
        f"§2.9 must say '{_NUMBER_WORD[n]} 16-mers' at TCF12 exon 7, matching what Table 4 and §2.4 "
        "between them establish.")


# ── 4 · the optional arm is placed, not unique ──────────────────────────────────────────────


def test_the_optional_margin_arm_is_not_claimed_to_be_the_only_one_available():
    """Table 2 shows lower-margin registers clearing the parent screen at two other §4.1 junctions."""
    contrary = {}
    for row in _read(TABLES).splitlines():
        m = re.match(r"\|\s*(EWSR1 e13|TCF12 e5)::NR4A3 e3\s*\|[^|]*\|\s*(\d+) of 5\s*\|", row)
        if m:
            contrary[m.group(1)] = int(m.group(2))
    assert contrary, (
        "Table 2 no longer prints a 'designs clearing the parent screen' count for EWSR1 e13 or "
        "TCF12 e5; this test's evidence base has moved.")
    assert all(v >= 2 for v in contrary.values()), (
        f"Table 2 now shows {contrary}; with one margin-3 register per junction, a count below 2 "
        "would mean no lower-margin register clears there and the exclusivity claim could return. "
        "Re-derive §4.4 before relaxing this.")
    body = _body()
    assert "and only at *EWSR1* exon 12" not in body, (
        "§4.4 claims the margin contrast is available 'only at EWSR1 exon 12'. Table 2 shows "
        f"{contrary} designs clearing the parent screen at the other two §4.1 junctions, so "
        "lower-margin registers survive there too. The arm is PLACED at the lead junction.")
    where = body.find("*TAF15* exon 6 cannot supply the same arm")
    assert where != -1, "§4.4's TAF15 exon-6 disqualifier has moved or been reworded away."
    passage = body[where:where + 700]
    assert "Table 2" in passage and "not because it is the" in passage, (
        "§4.4 must say why the arm sits at EWSR1 exon 12 rather than at the junctions Table 2 shows "
        "could carry one — otherwise the TAF15 disqualifier reads as a proof of uniqueness.")


# ── 5 · screen 5 lifts the six-transcript bound for one class only ──────────────────────────


def test_the_genome_scan_is_scoped_to_the_class_its_threshold_can_see():
    """Screen 5 runs at ≤2 mismatches. An 11–12 bp run inside a 16-mer carries 4–5."""
    body = _body()
    where = body.find("exhaustive over six parent transcripts and silent about every")
    assert where != -1, "§2.7's six-transcript bound sentence has moved or been reworded away."
    passage = body[where:where + 700]
    assert "The genome scan, screen 5, removes that bound." not in passage, (
        "§2.7 says screen 5 removes the six-transcript bound for BOTH liability classes. It runs at "
        "two mismatches, so it cannot see a mature-parent duplex of eleven or twelve base pairs — "
        "the class §2.5 calls invisible to the alignment screens at any setting.")
    assert "pre-mRNA class alone" in passage, (
        "§2.7 must say screen 5 lifts the bound for the pre-mRNA class alone.")
    assert "two\nmismatches" in passage or "two mismatches" in passage, (
        "§2.7 must give the reason — screen 5's two-mismatch threshold — not just the restriction.")


# ── 6 · the one-geometry bound names its own exception ──────────────────────────────────────


def test_the_one_geometry_bound_admits_the_5_8_5_counts_that_sit_outside_section_2_9():
    """§4.2 and Table 5 both print screened counts for the 5-8-5 18-mer."""
    tables = _read(TABLES)
    assert re.search(r"\|\s*gap-length control\s*\|.*\|\s*5-8-5\s*\|", tables), (
        "Table 5's 5-8-5 gap-length control row is gone; this test's evidence base has moved.")
    body = _body()
    where = body.find("**One geometry.**")
    assert where != -1, "§5's one-geometry bound has moved or been retitled."
    passage = body[where:where + 500]
    assert "Every screened count outside §2.9" not in passage, (
        "§5 bounds the paper to one architecture 'outside §2.9', but §4.2 and Table 5 both sit "
        "outside §2.9 and both print screened counts for the 5-8-5 18-mer.")
    assert "5-8-5" in passage, (
        "§5's one-geometry bound must name the 5-8-5 counts §4.2 and Table 5 carry, so the bound is "
        "not falsified by the paper's own display items.")
