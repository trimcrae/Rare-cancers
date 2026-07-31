"""ROWS THAT ARE DIFFERENT MUST NOT RENDER THE SAME — the board's leg column.

MEASURED 2026-07-31. `render_board` truncated the leg name to 18 characters, and RUNG 5a-KS's four unit ids
share a 20-character prefix. All four rows therefore printed the identical string `5aks_d0_to_d terna`: the
arm (`nr4a1` vs `nr4a3`) and the replicate (`r0` vs `r1`) — the only things that distinguish the four legs —
were exactly what the truncation removed.

The damage was real, not cosmetic. Two legs condemned by the idle guard were read off that board as "both on
the nr4a3 arm", which made an arm-specific hang the leading hypothesis and aimed an hour of diagnosis at it.
The committed `5aks-market-hold.json` snapshots say the two were `nr4a1_r1` and `nr4a3_r0` — one from EACH
arm — and that host losses ran 7 to 7 across the arms that day. The pattern was manufactured by the renderer.

This is CLAUDE.md §1's "a row we are paying and a row the gate refused must never render alike", seen from
the other side.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import inflight_board as ib  # noqa: E402

FIVE_AKS = ["5aks_d0_to_d__ternary_nr4a1_r0_dt4.0fs_wu1.0_5aks",
            "5aks_d0_to_d__ternary_nr4a1_r1_dt4.0fs_wu1.0_5aks",
            "5aks_d0_to_d__ternary_nr4a3_r0_dt4.0fs_wu1.0_5aks",
            "5aks_d0_to_d__ternary_nr4a3_r1_dt4.0fs_wu1.0_5aks"]


def _rows():
    return [{"name": n, "pct": 30.2, "usd_per_ns": "RTX 4090 $0.00533/ns · 1.56× basis",
             "state": "STARTING", "why": "", "eta_s": 3600} for n in FIVE_AKS]


def test_four_legs_render_as_four_distinguishable_rows():
    txt = ib.render(_rows())
    body = [ln for ln in txt.splitlines()[2:] if ln.strip()]
    assert len(body) == 4
    first_cells = [ln.split()[0] for ln in body]
    assert len(set(first_cells)) == 4, \
        "the leg column collapsed distinct units to one string: %r" % first_cells
    # and the two facts that were lost must be present in each cell
    for n, cell in zip(FIVE_AKS, first_cells):
        assert ("nr4a1" in cell) == ("nr4a1" in n)
        assert cell.endswith(n.split("_dt")[0][-2:]) or n.split("_dt")[0][-2:] in cell


def test_the_full_unit_id_survives():
    txt = ib.render(_rows())
    for n in FIVE_AKS:
        assert n in txt, "a board that cannot be grepped for a unit id is a board nobody can join to S3"


def test_the_columns_still_line_up_when_names_differ_in_length():
    rows = _rows() + [{"name": "short", "pct": 1.0, "usd_per_ns": "—", "state": "NO HOST",
                       "why": "x", "eta_s": None}]
    lines = [ln for ln in ib.render(rows).splitlines() if ln.strip() and not ln.startswith("-")]
    # every row's ETA cell must start at the same column, or the widest name has broken the table
    starts = {ln.index("$") if "$" in ln else None for ln in lines[1:] if "$" in ln}
    assert len(starts) == 1, "the $/ns column drifted: %r" % starts


# =============================================================================================================
# ...and the SHORTENER upstream of the column, which collapsed them a second time
# =============================================================================================================
def test_short_name_keeps_the_paralogue_and_the_replicate():
    """`render()`'s truncation was only half of it. `short_name` returned `f"{uid.split('__')[0]} {env}"`, so
    all four 5a-KS units became the single string `5aks_d0_to_d ternary` BEFORE the column ever saw them — on
    the one lane whose entire experiment is the nr4a1 vs nr4a3 comparison. A shortener that drops the
    discriminator cannot be rescued by a wider column, so both had to change."""
    names = [ib.short_name(n) for n in FIVE_AKS]
    assert len(set(names)) == 4, names
    for n, s in zip(FIVE_AKS, names):
        assert ("nr4a1" in s) == ("nr4a1" in n), s
        assert s.endswith("r0") == ("_r0_" in n), s


def test_short_name_did_not_regress_the_lanes_that_already_read_well():
    """The triangle's T2/T3 identity and the replicates' `valB rN` labels were already distinguishing, and
    they come from `valb_triangle_legs` rather than from a table typed here. Nothing about them changes."""
    assert ib.short_name("calib_hi_to_lo__ternary_vhl_r1_dt4.0fs_wu1.0_edge_reps") == "valB r1 ternary"
    assert ib.short_name("calib_hi_to_lo__binary_vhl_r2_dt4.0fs_wu1.0_edge_reps") == "valB r2 binary"


def test_the_rendered_board_distinguishes_four_5aks_rows_end_to_end():
    """The property that actually failed in production: name -> short_name -> column, all three together."""
    rows = [{"name": ib.short_name(n), "pct": 30.2, "usd_per_ns": "RTX 4090 $0.005/ns · 1.5x basis [bid]",
             "state": "STARTING", "why": "", "eta_s": 3600} for n in FIVE_AKS]
    body = [ln for ln in ib.render(rows).splitlines()[2:] if ln.strip()]
    firsts = [ln.split("  ")[0].strip() for ln in body]
    assert len(set(firsts)) == 4, firsts
