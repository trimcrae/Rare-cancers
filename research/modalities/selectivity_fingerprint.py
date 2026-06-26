"""
Pure classification of a candidate's NR4A selectivity FINGERPRINT across the family-wide opened-pocket
docking scores — no deps (TESTING.md #3), so the matrix job runs the unit-tested logic.

The matrix job (nr4a3_matrix.py) docks each candidate into the **opened** conformer of NR4A3, NR4A1 and
NR4A2 (state-matched — each paralogue's own metad-opened pocket, NOT a static off-target model, which is
what removes the opened-target-vs-static-off-target confound) and calls `classify()` to place the
candidate in a matrix cell. Docking dG are **screening priors, not affinities**, so these cells are
triage HYPOTHESES, to be quantified later by MM-GBSA (per-residue) and selectivity FEP.

Conventions: dG in kcal/mol (more negative = stronger). A candidate "engages" a paralogue if its dG into
that paralogue's opened pocket is <= `engage_thresh`. Selectivity margin m = dG_offtarget - dG_target
(positive => target favoured).
"""

ENGAGE_THRESH = -7.0   # docking dG below which a pocket counts as 'engaged' (permissive triage cutoff)
SEL_MARGIN = 1.0       # kcal/mol margin to call a preference — docking-noise-aware, triage only

# Matrix cell label keyed by the engaged-paralogue set.
_CELL = {
    frozenset(): "none",
    frozenset({"NR4A3"}): "NR4A3-only",
    frozenset({"NR4A1"}): "NR4A1-only",
    frozenset({"NR4A2"}): "NR4A2-only",
    frozenset({"NR4A1", "NR4A3"}): "NR4A1+NR4A3",
    frozenset({"NR4A2", "NR4A3"}): "NR4A2+NR4A3",
    frozenset({"NR4A1", "NR4A2"}): "NR4A1+NR4A2",
    frozenset({"NR4A1", "NR4A2", "NR4A3"}): "pan-NR4A",
}

# Application of each cell — gated by degradation DIRECTION (the disease must want those paralogue(s)
# DOWN) and by the AML anti-target. Used only for the human-readable matrix report.
_APPLICATION = {
    "NR4A3-only": "LEAD — EMC / AciCC / NR4A3-fusion sarcomas (selective, systemic)",
    "pan-NR4A": "second mode — ex-vivo immuno (reverse T-cell exhaustion; transient)",
    "NR4A1+NR4A3": "ANTI-TARGET — combined loss is leukaemogenic (AML); design AWAY",
    "NR4A2-only": "weak — degrading Nurr1 is usually wrong-direction (neuroprotective)",
    "NR4A1-only": "weak — Nur77 context-dependent",
    "NR4A2+NR4A3": "uncommon — no clean degrader rationale",
    "NR4A1+NR4A2": "uncommon — no clean degrader rationale (NR4A3 spared)",
    "none": "no engagement",
}


def application(cell):
    """Human-readable application note for a matrix cell (direction- and safety-gated)."""
    return _APPLICATION.get(cell, "unclassified")


def classify(dg3, dg1, dg2, engage_thresh=ENGAGE_THRESH, sel_margin=SEL_MARGIN):
    """Place a candidate in the selectivity matrix from its three opened-pocket docking dG.

    Returns a dict with the engaged set, the matrix `cell`, the `application` note, NR4A3 selectivity
    margins, and boolean flags `nr4a3_selective` / `pan_nr4a` / `anti_target` (the AML-risk NR4A1+NR4A3
    combination, sparing NR4A2). dG may be None (failed dock) — treated as 'not engaged'."""
    eng = {
        "NR4A3": dg3 is not None and dg3 <= engage_thresh,
        "NR4A1": dg1 is not None and dg1 <= engage_thresh,
        "NR4A2": dg2 is not None and dg2 <= engage_thresh,
    }
    engaged = [k for k in ("NR4A1", "NR4A2", "NR4A3") if eng[k]]
    s = frozenset(engaged)
    cell = _CELL.get(s, "+".join(sorted(engaged)) or "none")

    m1 = None if (dg1 is None or dg3 is None) else round(dg1 - dg3, 2)   # +ve => NR4A3 over NR4A1
    m2 = None if (dg2 is None or dg3 is None) else round(dg2 - dg3, 2)   # +ve => NR4A3 over NR4A2
    nr4a3_selective = bool(eng["NR4A3"] and m1 is not None and m2 is not None
                           and m1 >= sel_margin and m2 >= sel_margin)
    pan_nr4a = bool(len(engaged) == 3 and m1 is not None and m2 is not None
                    and abs(m1) < sel_margin and abs(m2) < sel_margin)
    anti_target = bool(eng["NR4A1"] and eng["NR4A3"] and not eng["NR4A2"])

    return {
        "engages": engaged,
        "cell": cell,
        "application": application(cell),
        "dG": {"NR4A3": dg3, "NR4A1": dg1, "NR4A2": dg2},
        "margin_vs_NR4A1": m1,
        "margin_vs_NR4A2": m2,
        "nr4a3_selective": nr4a3_selective,
        "pan_nr4a": pan_nr4a,
        "anti_target": anti_target,
    }


def matrix_summary(rows):
    """Group classified candidates (each a dict with a 'cell' key) into a cell->count census and pull
    out the actionable sets (NR4A3-selective leads, pan-NR4A leads, flagged anti-targets)."""
    census = {}
    for r in rows:
        census[r["cell"]] = census.get(r["cell"], 0) + 1
    return {
        "cell_census": census,
        "nr4a3_selective": [r for r in rows if r.get("nr4a3_selective")],
        "pan_nr4a": [r for r in rows if r.get("pan_nr4a")],
        "anti_targets": [r for r in rows if r.get("anti_target")],
    }
