"""
Pure MM-GBSA selectivity-rescoring logic (no deps — TESTING.md #3), so the rescoring verdicts run the
unit-tested arithmetic.

The MM-GBSA job (`nr4a3_mmgbsa.py`) re-scores the matrix's docked poses with a single-snapshot,
1-trajectory MM-GBSA endpoint energy (enthalpy + GB solvation, NO configurational entropy, NO ensemble
average) — a better-than-docking energy model for TRIAGE, not an affinity. This module turns the three
per-target endpoint ΔG into NR4A3-selectivity margins and a verdict that compares the MM-GBSA selectivity
to the original docking selectivity: did the docking-level NR4A3 preference SURVIVE the better energy model?

Sign convention (identical to the docking matrix): margin m = ΔG_offtarget − ΔG_NR4A3. ΔG is more negative
for tighter binding, so a POSITIVE margin means NR4A3 is favoured over that paralogue. A candidate must
beat BOTH paralogues to be selective, so the operative quantity is `min_margin` (the worst of the two).
"""

# Selectivity band (kcal/mol). Single-snapshot MM-GBSA without entropy/averaging is noisy; a margin within
# ±BAND of zero is "indistinct" (not a confident preference). Mirrors the docking SEL_MARGIN=1.0 triage bar
# but is deliberately a band, not a hard cutoff, to stay honest about MM-GBSA's uncertainty.
BAND = 1.0


def margins(dg3, dg1, dg2):
    """NR4A3-selectivity margins from the three endpoint ΔG (kcal/mol). Any ΔG may be None (failed leg).

    Returns margin_vs_NR4A1, margin_vs_NR4A2 (each = ΔG_paralogue − ΔG_NR4A3, +ve => NR4A3 favoured) and
    `min_margin` = the worse of the two present margins (None if NR4A3 itself is missing or no paralogue)."""
    m1 = None if (dg1 is None or dg3 is None) else round(dg1 - dg3, 2)
    m2 = None if (dg2 is None or dg3 is None) else round(dg2 - dg3, 2)
    present = [m for m in (m1, m2) if m is not None]
    mmin = min(present) if present else None
    return {"margin_vs_NR4A1": m1, "margin_vs_NR4A2": m2, "min_margin": mmin}


def verdict(dock_min_margin, mm_min_margin, band=BAND):
    """Compare docking selectivity to MM-GBSA selectivity for one candidate (both: +ve => NR4A3-selective).

    - confirmed_selective : docking called it NR4A3-selective AND MM-GBSA agrees (mm_min_margin > band)
    - reversed            : docking selective BUT MM-GBSA prefers a paralogue (mm_min_margin < −band)
    - weakened            : docking selective BUT MM-GBSA puts it inside the ±band (no confident preference)
    - rescued             : docking NOT selective BUT MM-GBSA now selective (mm_min_margin > band)
    - confirmed_nonselective : neither calls it NR4A3-selective
    - incomplete          : a required ΔG leg is missing
    """
    if dock_min_margin is None or mm_min_margin is None:
        return "incomplete"
    dock_sel = dock_min_margin > 0
    mm_sel = mm_min_margin > band
    mm_anti = mm_min_margin < -band
    if dock_sel and mm_sel:
        return "confirmed_selective"
    if dock_sel and mm_anti:
        return "reversed"
    if dock_sel:
        return "weakened"
    if mm_sel:
        return "rescued"
    return "confirmed_nonselective"


def rank_rows(rows):
    """Sort candidate rows (each a dict with 'mm_min_margin', possibly None) most-NR4A3-selective first.
    None margins sink to the bottom. Stable; does not mutate the input."""
    def key(r):
        m = r.get("mm_min_margin")
        return (m is None, -(m if m is not None else 0.0))
    return sorted(rows, key=key)


def census(rows):
    """Count rows by verdict (for the rescoring summary)."""
    out = {}
    for r in rows:
        v = r.get("verdict", "incomplete")
        out[v] = out.get(v, 0) + 1
    return out
