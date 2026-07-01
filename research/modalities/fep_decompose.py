#!/usr/bin/env python3
"""Per-residue selectivity attribution — the "WHY did it fail" map that must be captured BEFORE the early-stop
reclaims the fleet (pure, unit-tested).

If FEP is heading for a selectivity fail, we need to know *which receptor residues* explain it before we stop:
- residues where NR4A3 is stabilized MORE than the paralogue = selectivity DRIVERS (working as intended),
- residues where the PARALOGUE is stabilized as much/more = selectivity ERODERS (the culprits to redesign).
Input is per-receptor per-residue ligand-interaction energy (kcal/mol; more negative = more stabilizing),
computed at the coupled endpoint of the FEP pilot (nr4a3_fep per-residue decomposition). This module turns the
three maps into a ranked attribution + a redesign hint. No IO / no OpenMM.
"""

# NR4A3 orthosteric selectivity handles (paper §2.3) for cross-referencing the attribution.
HANDLES = {406: "L406", 407: "T407", 410: "T410", 412: "R412", 484: "I484", 531: "I531", 534: "L534"}


def selectivity_attribution(by_receptor, reference="nr4a3", top_n=8):
    """by_receptor: {receptor: {resid(int): contribution_kcal}}. For each paralogue, per-residue
    Δ = ref_contrib − paralogue_contrib (aligned by NR4A3 residue number).
      Δ < 0  → residue stabilizes NR4A3 MORE than the paralogue → selectivity DRIVER.
      Δ > 0  → residue stabilizes the PARALOGUE as much/more → selectivity ERODER (culprit).
    Returns per-paralogue ranked drivers/eroders + the net, with handle annotation."""
    ref = by_receptor.get(reference, {})
    out = {}
    for para, contrib in by_receptor.items():
        if para == reference:
            continue
        deltas = []
        for resid in sorted(set(ref) | set(contrib)):
            d = ref.get(resid, 0.0) - contrib.get(resid, 0.0)
            deltas.append({"resid": resid, "delta": round(d, 3),
                           "nr4a3": round(ref.get(resid, 0.0), 3),
                           "para": round(contrib.get(resid, 0.0), 3),
                           "handle": HANDLES.get(resid)})
        drivers = sorted([d for d in deltas if d["delta"] < 0], key=lambda x: x["delta"])[:top_n]
        eroders = sorted([d for d in deltas if d["delta"] > 0], key=lambda x: -x["delta"])[:top_n]
        out[para] = {"net_delta": round(sum(d["delta"] for d in deltas), 3),
                     "drivers": drivers, "eroders": eroders}
    return out


def redesign_hint(attribution):
    """One-line-per-paralogue design guidance from the attribution: the top selectivity-eroding residues are
    what a next candidate must engage differently. Flags whether eroders are pocket handles (engageable) or
    elsewhere (harder)."""
    hints = {}
    for para, a in attribution.items():
        if not a["eroders"]:
            hints[para] = f"{para}: no residue erodes selectivity (net Δ {a['net_delta']}) — selectivity-clean"
            continue
        top = a["eroders"][0]
        where = f"handle {top['handle']}" if top["handle"] else f"non-handle residue {top['resid']}"
        hints[para] = (f"{para}: selectivity eroded most at {where} (Δ +{top['delta']}); "
                       f"redesign to reduce {para} engagement there / exploit the drivers "
                       f"({', '.join(str(d['resid']) for d in a['drivers'][:3]) or 'none'})")
    return hints


def diagnostic_ready(by_receptor, reference="nr4a3", min_residues=5):
    """The early-stop must NOT fire a selectivity-fail until the WHY map exists. This returns True only when
    all three receptors have a per-residue map with >= min_residues entries — i.e. the attribution above will
    be meaningful. The monitor gates stop_fail on this."""
    needed = {reference, "nr4a1", "nr4a2"}
    return all(len(by_receptor.get(r, {})) >= min_residues for r in needed)
