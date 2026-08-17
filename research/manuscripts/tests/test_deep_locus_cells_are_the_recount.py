#!/usr/bin/env python3
"""Tables 2, 3 and 4 must report ONE locus count per molecule per depth — the recounted one.

⛔ WHY THIS EXISTS (round-5 review, P0.3, 2026-08-16). `submission_tables._deep_lookup` read
`n_loci_with_a_gap_spanning_hit` straight off the deep screens into the third deep column of Tables
3 and 4. That field was computed at SCREEN time under a `locus_of` that took the symbol as the last
parenthesised token before the first comma, so every gene whose own description carries a comma lost
its symbol and each transcript variant fell back to its own accession — corrected in 5233cf867, and
uncorrectable in a committed screen without re-running the search. Table 2 and the Results already
counted loci with the fixed parser. The two therefore printed different numbers for the SAME
molecule at the SAME depth:

    TCF12 e5  GGGCATATCCATCAGA   Table 3: 17   Table 2 and §3.3: 1   (seventeen PIK3CG variants)
    TCF12 e3  GGGCATATCTGATCCA   Table 3: 56   recount: 6
    the lead  GGGCATATCATCAAAC   Table 3: 14   Table 2 and §5.3: 6

⛔ AND THE DEFECT WAS INVISIBLE TO EVERY EXISTING GUARD, WHICH IS WHY THE GUARD IS THIS SHAPE. The
generator was consistent with itself, the artifact it read was committed and current, and each table
was internally coherent — nothing was stale and nothing crashed. What was wrong was a relationship
BETWEEN two tables, and the only way to see it is to read both rendered tables and compare the cells
a reader would compare. `aso_gap_length_tradeoff._blast_rows` even carried a comment asserting the
stale field was read by nobody; a comment cannot check that, and this file is what replaced it.

⚠ WHAT THIS DOES NOT ASSERT. Nothing here says a locus count is a measurement of off-target
activity, and nothing converts one into a risk. These are consistency assertions over committed
artifacts and the tables generated from them.
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MAN))
MOD = os.path.join(REPO, "research", "modalities")
TABLES = os.path.join(MAN, "aso", "fusion-junction-aso-submission-tables.md")
GENERATOR = os.path.join(MAN, "submission_tables.py")
sys.path.insert(0, MOD)
sys.path.insert(0, MAN)


def _tables_text():
    if not os.path.exists(TABLES):
        pytest.skip("the generated tables file is not present in this checkout")
    return open(TABLES, encoding="utf-8").read()


def _block(txt, table, nxt):
    """The rendered rows of one table: the pipe-delimited lines between two table headings."""
    body = txt[txt.index(f"**Table {table}."):]
    if nxt is not None and f"**Table {nxt}." in body:
        body = body[:body.index(f"**Table {nxt}.")]
    rows = [ln for ln in body.splitlines() if ln.startswith("|") and "---" not in ln]
    return [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in rows[1:]]


def _seq(cell):
    m = re.fullmatch(r"5′-([ACGT]+)-3′", cell)
    return m.group(1) if m else None


#: Every marker glyph a junction cell may carry, stripped before the cell becomes an artifact key.
#: ⛔ STRIPPED BY CLASS, NOT ONE GLYPH AT A TIME (fixed 2026-08-17). This stripped only " ‡", so
#: when Table 3 gained a "†" marking the three junctions where no design clears the parent screen,
#: those cells produced keys like `TAF15_e14__NR4A3_e3_†`, matched no artifact, and dropped silently
#: out of the lookup. NOTHING FAILED: this file's global `assert checked` / `assert inflated` guards
#: are satisfied by the other rows, so 3 of 38 cells stopped being checked against the recount while
#: the suite stayed green. That is the shape this repository keeps paying for — a check that
#: narrows its own coverage and still reports success — and a per-glyph strip list guarantees the
#: next marker repeats it. A class regex cannot.
_MARKERS = re.compile(r"[‡†*※]+\s*$")


def _label(cell):
    """`EWSR1 e12::NR4A3 e3 ‡` → `EWSR1_e12__NR4A3_e3` — the junction key the artifacts use."""
    return _MARKERS.sub("", cell.strip()).strip().replace("::", "__").replace(" ", "_")


def _count(cell):
    """A locus cell as an integer, censoring marker stripped, or None where there is no reading.

    ⚠ "—" IS NOT ZERO and never becomes one here: a design the deeper re-screen returned no result
    for has no count, and rendering that as 0 is the flattering direction these tables have gone
    wrong in before.
    """
    cell = cell.strip()
    if cell in ("—", "-", ""):
        return None
    return int(cell.lstrip("≥≤").strip())


def _table3():
    """{(junction, design): deep gap-spanning locus cell} from the rendered Table 3."""
    out = {}
    for r in _block(_tables_text(), 3, 4):
        seq = _seq(r[3])
        if seq is None:                       # the all-submissions-failed row carries no design
            continue
        out[(_label(r[0]), seq)] = _count(r[10])
    return out


def _table4():
    out = {}
    for r in _block(_tables_text(), 4, 5):
        seq = _seq(r[0])
        if seq is None:
            continue
        out[(_label(r[1]), seq)] = _count(r[12])
    return out


def _table2():
    """{(junction, design): deep gap-paired (transcripts, loci)} from the rendered Table 2."""
    out = {}
    for r in _block(_tables_text(), 2, 3):
        seq = _seq(r[3])
        if seq is None:                       # a junction with no design clearing the parent screen
            continue
        cell = r[6]
        if cell.strip() in ("—", "-", ""):
            continue
        n, loci = (x.strip() for x in cell.split("→"))
        out[(_label(r[0]), seq)] = (int(n), int(loci))
    return out


def _deep_records():
    """{(junction, design): oligo} over the deep screens of the geometry the manuscript reports."""
    import aso_screen_sets as ass  # noqa: PLC0415
    try:
        screens = ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN, root=MOD,
                                   select=ass.is_deep)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no deep screen set in this checkout ({exc})")
    out = {}
    for s in screens:
        lab = s.junction_label
        if not lab:
            continue
        for o in (s.artifact.get("oligos") or []):
            if o.get("status") == "screened":
                out[(lab, o["antisense_5to3"])] = (o, s.geometry)
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The guard the defect asked for: the two tables, read as a reader reads them
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_table3_and_table2_agree_on_every_design_they_both_carry():
    """⛔ THE ONE CHECK THAT WOULD HAVE CAUGHT P0.3, AND IT IS A CHECK BETWEEN TABLES.

    Table 3's representative design at a junction is chosen by gap-level margin and Table 2's by
    parent liability, so the two carry the same molecule at only some junctions — which is exactly
    the population where a reader can put the two cells side by side. Every one of them must agree,
    because both columns are the same quantity at the same depth for the same molecule.
    """
    t3, t2 = _table3(), _table2()
    shared = sorted(set(t3) & set(t2))
    assert shared, "Tables 2 and 3 share no design; the comparison this guard exists for is vacuous"
    bad = [(k, t3[k], t2[k][1]) for k in shared if t3[k] != t2[k][1]]
    assert not bad, (
        "Table 3 and Table 2 print different gap-spanning locus counts at the deeper ceiling for "
        "the same molecule — one of them is not the recount. "
        + "; ".join(f"{lab}/{seq}: Table 3 {a}, Table 2 {b}" for (lab, seq), a, b in bad))
    # the lead reagent is the row a clinical reader goes to, so it is named rather than left to
    # the population above
    lead = [k for k in shared if k[1] == "GGGCATATCATCAAAC"]
    assert lead, "the lead reagent is in neither table's shared set; re-read before relaxing this"


def test_every_deep_locus_cell_is_the_recount_and_not_the_screens_stored_field():
    """The same fact stated against the artifacts rather than against the other table.

    ⛔ THE STORED FIELD IS AN OVER-COUNT AND THE ERROR IS ONE-DIRECTIONAL: a failed symbol parse can
    only SPLIT a locus, never merge two. So a cell matching the stored field where the two differ is
    always the inflated one, and this asserts the recount on every rendered deep cell of Tables 3
    and 4 — not only on the ones Table 2 happens to share.
    """
    from aso_gap_length_tradeoff import recount_loci  # noqa: PLC0415

    deep = _deep_records()
    cells = {**_table3(), **_table4()}
    checked = inflated = 0
    for key, printed in cells.items():
        rec = deep.get(key)
        if rec is None or printed is None:
            continue
        o, _ = rec
        want = recount_loci(o)
        checked += 1
        assert printed == want["n_loci_with_a_gap_spanning_hit"], (
            f"{key[0]}/{key[1]}: the table prints {printed} gap-spanning loci at the deeper "
            f"ceiling; the corrected parser recounts {want['n_loci_with_a_gap_spanning_hit']} "
            f"(the screen's own superseded field says "
            f"{o.get('n_loci_with_a_gap_spanning_hit')})")
        if (o.get("n_loci_with_a_gap_spanning_hit") or 0) > want["n_loci_with_a_gap_spanning_hit"]:
            inflated += 1
    assert checked, "no rendered deep cell could be matched to a screen record"
    assert inflated, (
        "no deep record in this checkout differs from its screen's stored locus count, so this "
        "guard cannot currently tell the recount from the stale field. That is a change in the "
        "corpus, not a pass — re-derive before relaxing it")


def test_the_deep_lookup_never_reads_the_screens_superseded_locus_field():
    """The source-level half, and it is the half a comment used to do badly.

    ⚠ THE OTHER TWO TESTS COMPARE OUTPUTS, so they only see the defect where the stale field and the
    recount happen to differ — 30 of 187 records today, and a corpus in which they agreed everywhere
    would let the wrong code back in silently. This asserts the deep path cannot read the field at
    all. Scoped to `_deep_lookup` because the collapse artifact's same-named field IS legitimate
    reading elsewhere in the generator: the collapse computes it itself and marks the truncated case.
    """
    import inspect  # noqa: PLC0415

    import submission_tables as ST  # noqa: PLC0415

    src = inspect.getsource(ST._deep_lookup)
    body = src.split('"""')[-1]              # the code, not the docstring that explains the defect
    assert "recount_loci" in body, "_deep_lookup no longer routes through the shared recount"
    # ⚠ THE FIELD NAME IS NOT BANNED OUTRIGHT, because the recount RETURNS a key of that name — the
    # two are the same quantity computed by different code, and banning the string would only push
    # the next author into aliasing it. What is banned is reading it off anything but the recount's
    # own result, so every occurrence must be subscripted from that result.
    reads = re.findall(r'(\S{0,8})"n_loci_with_a_gap_spanning_hit"', body)
    stale = [r for r in reads if not r.endswith("loci[")]
    assert not stale, (
        f"_deep_lookup reads a gap-spanning locus count from something other than the recount "
        f"({stale}). The screens' own field was computed before the locus parser was corrected and "
        f"over-counts; the deep columns must come from aso_gap_length_tradeoff.recount_loci")


def test_the_censoring_marker_is_only_ever_the_lower_bound_one():
    """A recount over a truncated list is a LOWER bound, so it may only ever be marked "≥".

    ⛔ THE TWO MARKERS IN THIS TABLE MEAN OPPOSITE THINGS AND ARE NOT INTERCHANGEABLE. "≤" marks a
    default-depth cell still carrying the screen's frozen over-counting figure; "≥" marks a count
    made over a truncated sample of the hits. Marking a lower bound "≤" would assert the opposite of
    what the screen knows, and the table's own legend would then contradict its cells.

    ⚠ NO DEEP CELL CARRIES EITHER MARKER TODAY — the deep re-screens retain every hit — so this
    asserts a property of the renderer rather than of the current corpus.
    """
    import inspect  # noqa: PLC0415

    import submission_tables as ST  # noqa: PLC0415

    src = inspect.getsource(ST._deep_cells)
    assert "≤" not in src.split('"""')[-1], (
        "_deep_cells can emit the upper-bound marker on a recounted cell, which is a lower bound")
    deep = _deep_records()
    truncated = [k for k, (o, _) in deep.items()
                 if len(o.get("offtargets") or []) != o.get("n_offtarget_near_matches")]
    assert not truncated, (
        f"{len(truncated)} deep record(s) store fewer hits than they report, so a deep locus count "
        f"is no longer exact: {truncated[:3]}. That is a result about the re-screens, not a test "
        f"failure — the renderer will mark them '≥', and the legend's claim that no deep hit list "
        f"is truncated must be re-derived")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# P0.4 — the superlative, held against the artifacts rather than against the prose
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_lead_reagent_does_not_carry_the_panels_heaviest_gap_paired_load():
    """⛔ THE FACT THAT FALSIFIES "the heaviest disclosed transcriptome load of any design here".

    The lead `GGGCATATCATCAAAC` carries 123 gap-paired sense-strand near-matches at the deeper
    ceiling. That is the maximum among the designs TABLE 2 prints, and Table 2 prints one design per
    junction; it is NOT the maximum among the designs the paper discloses, because Table 3 prints a
    different representative at most junctions and the panel is tiled five registers deep. A
    superlative scoped to "any design considered here" is therefore false, and the counter-example
    is in the paper's own Table 3.

    ⚠ ASSERTED AS A PROPERTY, NOT AS A PINNED NUMBER. Pinning 240 would go stale the moment a screen
    is re-run; the property "the lead is not the maximum" is what any such sentence rests on, and
    the failure message carries the live numbers a corrected sentence would need.
    """
    import junction_aso_locus_collapse as C  # noqa: PLC0415

    LEAD = "GGGCATATCATCAAAC"
    loads = {}
    for (lab, seq), (o, geom) in _deep_records().items():
        lo, hi = geom.gap_region_1based
        paired = [h for h in (o.get("offtargets") or [])
                  if not h.get("is_minus_strand")
                  and h["q_from"] <= lo and h["q_to"] >= hi and h.get("gap_mismatches") == 0]
        loads[(lab, seq)] = (len(paired), len({C.locus_of(h) for h in paired}))
    assert loads, "no deep record carries a gap-paired count"

    lead = {k: v for k, v in loads.items() if k[1] == LEAD}
    assert lead, f"the lead reagent {LEAD} has no deep record in this checkout"
    lead_n = max(n for n, _ in lead.values())
    top = max(loads.items(), key=lambda kv: kv[1][0])
    above = sorted((v[0], k) for k, v in loads.items() if v[0] > lead_n)

    assert above, (
        f"no design in the deep panel now exceeds the lead's {lead_n} gap-paired near-matches, so "
        f"the superlative the round-5 review withdrew would have become true. That is a change in "
        f"the corpus and must be re-derived, not assumed")
    assert top[0][1] != LEAD, (
        f"the lead reagent now holds the panel maximum ({top[1][0]}); re-derive §5.3")
    # the numbers a corrected sentence needs, in the failure message of the assertion that names them
    assert len(above) >= 1, above
    assert top[1][0] > lead_n, (
        f"panel maximum {top[1][0]} gap-paired near-matches at {top[1][1]} loci, held by "
        f"{top[0][1]} at {top[0][0]}; {len(above)} deep record(s) exceed the lead's {lead_n}")


def test_the_paper_and_the_tables_have_one_home_for_the_lead_reagents_locus_count():
    """§5.3, Table 3 and Table 2 all state the lead's deep locus count; it is one number.

    ⚠ THE MANUSCRIPT IS READ HERE, NOT WRITTEN. This asserts the three agree — the P0.3 defect was
    that they did not — and says nothing about how the sentence is worded.
    """
    from aso_gap_length_tradeoff import recount_loci  # noqa: PLC0415

    LEAD = "GGGCATATCATCAAAC"
    deep = _deep_records()
    recs = {k: v for k, v in deep.items() if k[1] == LEAD}
    if not recs:
        pytest.skip("the lead reagent has no deep record in this checkout")
    counts = {recount_loci(o)["n_loci_with_a_gap_spanning_hit"] for o, _ in recs.values()}
    assert len(counts) == 1, f"the lead's three seams disagree about its locus count: {counts}"
    n = counts.pop()

    t3 = {k: v for k, v in _table3().items() if k[1] == LEAD}
    t2 = {k: v for k, v in _table2().items() if k[1] == LEAD}
    assert t3 and t2, "the lead reagent is missing from Table 3 or Table 2"
    assert set(t3.values()) == {n}, (f"Table 3 prints {set(t3.values())} for the lead; the recount "
                                     f"is {n}")
    assert {loci for _, loci in t2.values()} == {n}, (
        f"Table 2 prints {sorted({loci for _, loci in t2.values()})} for the lead; the recount is {n}")


if __name__ == "__main__":  # standalone run, the convention the other test files here follow
    import traceback
    failed = 0
    for name, fn in sorted(dict(globals()).items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except Exception:  # noqa: BLE001
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(json.dumps({"failed": failed}))
    sys.exit(1 if failed else 0)
