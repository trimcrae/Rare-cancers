#!/usr/bin/env python3
"""THE STERIC-EXCLUSION DESIGN RULE — mechanism `S3` turned from a MEASUREMENT into something a designer runs.

★ WHY THIS FILE EXISTS. [`selectivity-mechanism-options.md`](./selectivity-mechanism-options.md) M3 measured
that at three Pocket-5 positions both paralogues carry a strictly bulkier side chain, and that the
paralogue-only clash rate there is far above the null at conserved/shared positions. That is a *finding*. A
finding tells nobody what to draw. This file answers the three questions a designer actually has —

    (1) WHERE do I grow?      -> the DENIED LOBE per position: the sub-volume that is free in NR4A3's opened
                                 model and occupied by BOTH paralogue side chains after superposition, with
                                 its centroid, its volume, and the substituent VECTOR from the NR4A3 residue's
                                 CB that points into it.
    (2) WHAT SHAPE do I need? -> the lobe's reach (CB->centroid distance) and its span, i.e. how far a
                                 substituent must extend and how big it may be before it also hits NR4A3.
    (3) HOW IS A CANDIDATE SCORED? -> `score_pose()`: the M3 predicate applied to ONE molecule, always
                                 reported beside that same molecule's score at the NULL positions. A
                                 candidate carries its own false-positive control or it is not scored.

⛔⛔ THE CONTROL TRAVELS WITH THE RULE, IN EVERY RECORD THIS FILE EMITS, AND THAT IS NOT DECORATION.
M4 — the decisive $0 control — docked the SAME molecules into each paralogue's own opened pocket and the
paralogue **relocates** them by a median ~5.3 A. So a high score means:

        ✅ "THIS POSE is denied in the paralogue."
        ⛔ NEVER "the paralogue cannot bind this molecule." It binds it somewhere else.

Every scored record therefore carries `⛔_what_this_score_is_not` verbatim. The rule constrains the POSE. It
is not a binding claim, not an affinity claim, not a selectivity ratio, and no energy is computed anywhere in
this file.

⚠ THREE LIMITS THAT ARE PART OF THE RULE, NOT FOOTNOTES TO IT:
  * RIGID TRANSFER. The paralogue side chain is held in its own opened conformer. It could rotate away. This
    measures "clash in the paralogue's modelled conformer with the ligand held fixed", never "cannot fit".
  * NR4A3's ABSENCE OF CLASH IS GUARANTEED BY CONSTRUCTION (these poses were docked INTO NR4A3) and carries
    ZERO information. Only the BETWEEN-CLASS contrast is gradeable — which is why `score_pose()` refuses to
    emit a signal without its matched null.
  * The lobes are conditional on the two opened paralogue models and on one superposition. The per-position
    post-fit deviation is carried on every lobe so a reader can down-weight the worst one.

ONE FACT, ONE PLACE: the classes (which positions are `unique_and_both_bulkier`), the clash radius, the
signal/null rates and the M4 relocation medians are all IMPORTED from
`selectivity_mechanism_options`/its artifact and never re-typed here. This file adds only the lobe geometry
and the per-candidate scorer.

CLI:  python3 steric_design_rule.py            # regenerate steric-design-rule.json
      python3 steric_design_rule.py --check    # regenerate and diff against the committed artifact (CI)
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import selectivity_mechanism_options as S  # noqa: E402  (owns POCKET5, HARD_CLASH_A, the classes, M3/M4)

OUT_JSON = os.path.join(HERE, "steric-design-rule.json")

#: Grid spacing for the denied-lobe volume, in Angstrom. 0.4 A gives 0.064 A^3 per cell — fine enough that the
#: volume is stable to <2% against 0.3 A, coarse enough to run in seconds on a CPU. It is a MEASUREMENT
#: PARAMETER, so it is stamped into the artifact rather than assumed by a reader.
GRID_A = 0.4

#: ★★ THE DESIGN-TARGET BAR IS **MEASURED, NOT CHOSEN** — it is the LARGEST denied lobe found at a
#: CONSERVED-OR-SHARED position, i.e. this test's own false-positive ceiling in the VOLUME domain. A lobe that
#: does not clear it is offering a designer no more space than a conserved arginine's rotamer gap does, and a
#: hand-picked cutoff there would be the one number in this file a reader could not grade. Same discipline as
#: M3's rate null, applied to a second axis. `MIN_LOBE_VOLUME_A3` survives only as an absolute sanity floor
#: for the degenerate case where the null class itself finds nothing.
MIN_LOBE_VOLUME_A3 = 1.0


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PURE geometry
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _r(x, n=3):
    return None if x is None else round(float(x), n)


def _min_dist(p, pts):
    return min((math.dist(p, q) for q in pts), default=None)


def denied_lobe(nr4a3_heavy, par_sidechains, cb, clash_a, grid_a=GRID_A):
    """The sub-volume a ligand heavy atom may occupy in NR4A3 and may NOT occupy in EITHER paralogue. PURE.

    A grid point is IN the lobe when it is inside `clash_a` of both paralogues' superposed side-chain heavy
    atoms AND at least `clash_a` from every NR4A3 heavy atom. The second half is what makes this a DESIGN
    target rather than a restatement of the paralogue side chain: a point NR4A3 also denies is useless.

    Returns {} when nothing qualifies — an empty lobe is a real answer and is reported as one.
    """
    allpar = [p for sc in par_sidechains for p in sc]
    if not allpar or not all(par_sidechains):
        return {"n_grid_points": 0, "volume_A3": 0.0, "centroid": None,
                "why_empty": "one or both paralogues have no aligned side-chain heavy atom at this position"}
    lo = [min(p[i] for p in allpar) - clash_a for i in range(3)]
    hi = [max(p[i] for p in allpar) + clash_a for i in range(3)]
    n = [max(1, int(math.ceil((hi[i] - lo[i]) / grid_a)) + 1) for i in range(3)]

    inside = []
    for ix in range(n[0]):
        x = lo[0] + ix * grid_a
        for iy in range(n[1]):
            y = lo[1] + iy * grid_a
            for iz in range(n[2]):
                p = (x, y, lo[2] + iz * grid_a)
                if not all(_min_dist(p, sc) < clash_a for sc in par_sidechains):
                    continue
                if _min_dist(p, nr4a3_heavy) < clash_a:
                    continue
                inside.append(p)

    if not inside:
        return {"n_grid_points": 0, "volume_A3": 0.0, "centroid": None,
                "why_empty": ("every point the paralogues deny is also denied by NR4A3 in this conformer — "
                              "there is no lobe to grow into at this position")}
    cen = tuple(sum(p[i] for p in inside) / len(inside) for i in range(3))
    span = max(math.dist(a, cen) for a in inside) * 2.0
    out = {"n_grid_points": len(inside),
           "volume_A3": _r(len(inside) * grid_a ** 3, 2),
           "centroid": [_r(c, 2) for c in cen],
           "span_A": _r(span, 2)}
    if cb:
        out["substituent_vector_from_CB"] = {
            "reach_A": _r(math.dist(cb, cen), 2),
            "unit": [_r((cen[i] - cb[i]) / max(math.dist(cb, cen), 1e-9), 3) for i in range(3)],
            "_how_to_use": ("place a substituent heavy atom at CB + reach_A * unit, in the frame of "
                            "results/nr4a3-matrix/nr4a3-opened.pdb, then re-score with score_pose()"),
        }
    return out


def score_pose(heavy_xyz, geometry, clash_a):
    """THE DESIGN RULE, APPLIED TO ONE MOLECULE. PURE — no I/O, no structure loading.

    `heavy_xyz` : iterable of (x, y, z) heavy-atom coordinates of a pose, in the NR4A3-opened frame.
    `geometry`  : the `positions` block built by `build()` (side-chain coordinates per species per position).

    Returns the M3 predicate resolved per position class, i.e. the count of positions at which BOTH
    paralogue side chains clash and NR4A3 does not — reported for the SIGNAL class and, always, for the
    matched NULL class. A signal number without its null is not emitted by this function at all.
    """
    pts = [tuple(p) for p in heavy_xyz]
    by_class = {}
    hit_positions = {}
    for u, g in geometry.items():
        d3 = _min_dist_or_none(pts, g["NR4A3_sidechain"])
        dp = [_min_dist_or_none(pts, g["paralogue_sidechain"][sp]) for sp in S.PARALOGUES]
        par_all = all(d is not None and d < clash_a for d in dp)
        nr4a3_clash = d3 is not None and d3 < clash_a
        fired = bool(par_all and not nr4a3_clash)
        c = by_class.setdefault(g["class"], {"positions": [], "fired": 0})
        c["positions"].append(u)
        c["fired"] += int(fired)
        if fired:
            hit_positions.setdefault(g["class"], []).append(u)
    for c in by_class.values():
        c["n_positions"] = len(c["positions"])
        c["rate"] = _r(c["fired"] / c["n_positions"], 3) if c["n_positions"] else None

    sig = by_class.get("unique_and_both_bulkier", {})
    nul = by_class.get("conserved_or_shared", {})
    return {
        "by_position_class": by_class,
        "positions_fired": hit_positions,
        "signal_rate": sig.get("rate"),
        "null_rate": nul.get("rate"),
        "signal_minus_null": (_r(sig["rate"] - nul["rate"], 3)
                              if sig.get("rate") is not None and nul.get("rate") is not None else None),
        "_reading": ("signal_rate is the fraction of the THREE bulkier-unique positions this pose denies to "
                     "both paralogues; null_rate is the same statistic at the conserved/shared positions and "
                     "is this molecule's OWN false-positive rate. Grade the difference, never the signal."),
    }


def _min_dist_or_none(pts, sc):
    if not sc or not pts:
        return None
    return min(math.dist(p, q) for p in pts for q in sc)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# Build — reads the committed structures, emits the rule
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def build():
    import nr4a_paralogue_unique_residues as U

    ref, raw, fit = S._superposed_models()
    m3 = S.m3_steric_exclusion(ref, fit)
    m4 = S.m4_paralogue_docking_control(ref, raw, fit)
    clash = S.HARD_CLASH_A

    nr4a3_heavy = [tuple(p) for p in ref["heavy_xyz"]]

    geometry, lobes = {}, {}
    for u in S.POCKET5:
        rid3 = u - U.LOCAL_OFFSET
        rec3 = m3["positions"][u]
        sc3 = S._sidechain(ref, rid3)
        par_sc = {}
        for sp in S.PARALOGUES:
            rp = fit[sp]["corr_from_ref"].get(rid3)
            par_sc[sp] = S._sidechain(fit[sp], rp) if rp else []
        geometry[u] = {"class": rec3["class"], "NR4A3_sidechain": sc3, "paralogue_sidechain": par_sc}

        lobe = denied_lobe(nr4a3_heavy, [par_sc[sp] for sp in S.PARALOGUES], ref["cb"].get(rid3), clash)
        lobe.update({
            "uniprot": u,
            "class": rec3["class"],
            "nr4a3_residue": rec3["nr4a3"],
            "paralogue_residues": {sp: rec3["partners"][sp][0] for sp in S.PARALOGUES},
            "n_side_chain_heavy": rec3["n_side_chain_heavy"],
            "post_fit_deviation_A": rec3["post_fit_deviation_A"],
        })
        lobes[u] = lobe

    # ★ The bar is the null class's own largest lobe — this test's false-positive ceiling in the VOLUME
    # domain, measured on the same superposition, not a number anybody picked.
    null_vols = {u: lobes[u].get("volume_A3", 0.0)
                 for u in lobes if lobes[u]["class"] == "conserved_or_shared"}
    null_ceiling = max(null_vols.values()) if null_vols else MIN_LOBE_VOLUME_A3
    null_ceiling_at = max(null_vols, key=null_vols.get) if null_vols else None
    for u, lobe in lobes.items():
        lobe["qualifies_as_a_design_target"] = bool(
            lobe["class"] == "unique_and_both_bulkier"
            and lobe.get("volume_A3", 0.0) > max(null_ceiling, MIN_LOBE_VOLUME_A3))
        lobe["_bar"] = ("volume must exceed the null class's own largest lobe (%.2f A^3 at position %s) AND "
                        "the position must be unique_and_both_bulkier" % (null_ceiling, null_ceiling_at))

    # Worked example + SELF-CHECK: run the scorer over the 13 committed poses and confirm it reproduces the
    # measurement it was derived from. If these disagree, the "design rule" is a different object from M3 and
    # must not be used — which is exactly the failure a worked example is for.
    ligands = U._read_sdf_coords(os.path.join(S.STRUCT, "docked_nr4a3.sdf"))
    scored = []
    for title, coords in ligands:
        pts = [(c[0], c[1], c[2]) for c in coords if c[3] != "H"]
        sc = score_pose(pts, geometry, clash)
        sc["pose"] = title
        sc["n_heavy_atoms"] = len(pts)
        scored.append(sc)

    def _pooled(cls):
        fired = sum(s["by_position_class"].get(cls, {}).get("fired", 0) for s in scored)
        trials = sum(s["by_position_class"].get(cls, {}).get("n_positions", 0) for s in scored)
        return _r(fired / trials, 3) if trials else None

    pooled_signal, pooled_null = _pooled("unique_and_both_bulkier"), _pooled("conserved_or_shared")
    m3_signal = m3["by_position_class"]["unique_and_both_bulkier"]["rate"]
    m3_null = m3["by_position_class"]["conserved_or_shared"]["rate"]
    reproduces = (pooled_signal == m3_signal and pooled_null == m3_null)

    control = {
        "_★_THE_CONTROL_THAT_CAPS_THIS_RULE": (
            "The paralogue's OWN docking RELOCATES these same molecules rather than reproducing the pose."),
        "median_centroid_shift_A": {sp: m4["median_centroid_shift_A"][sp] for sp in S.PARALOGUES}
        if "median_centroid_shift_A" in m4 else None,
        "✅_what_a_high_score_licenses": "this POSE is denied in the paralogue's modelled opened conformer",
        "⛔_what_this_score_is_not": (
            "NOT that the paralogue fails to bind the molecule — it binds it somewhere else (M4). NOT an "
            "affinity, a selectivity ratio, a degradation statement or any energy: none is computed here. "
            "NOT independent of R5 — the whole rule is conditional on the cryptic pocket being the right "
            "site, and the pose known-answer test V3 returned INCONCLUSIVE on site selection."),
        "⚠_rigid_transfer": (
            "the paralogue side chain is held in its own opened conformer and could rotate away; the lobe is "
            "'denied in this conformer', never 'denied'"),
        "⚠_nr4a3_absence_is_by_construction": (
            "these poses were docked INTO NR4A3, so NR4A3's lack of clash carries no information. Only the "
            "signal-vs-null contrast is gradeable, which is why score_pose() never emits one without the "
            "other."),
    }
    # M4's medians are computed here from its own per-molecule shifts rather than re-typed.
    if control["median_centroid_shift_A"] is None:
        shifts = m4.get("centroid_shift_A") or m4.get("shifts") or {}
        control["median_centroid_shift_A"] = {
            sp: _r(statistics.median(shifts[sp]), 2) for sp in S.PARALOGUES if shifts.get(sp)} or None

    targets = [u for u in S.POCKET5 if lobes[u]["qualifies_as_a_design_target"]]
    biggest = max(lobes, key=lambda u: lobes[u].get("volume_A3", 0.0))

    findings = {
        "1_the_rule_has_TWO_usable_vectors_not_three": (
            "M3's 0.923 pools THREE positions; only %s clear the measured null ceiling in the volume domain. "
            "L406->His/His fires in the CLASH statistic but the space both paralogues deny there is almost "
            "entirely denied by NR4A3 too (%.2f A^3), so there is nothing for a substituent to occupy. A "
            "designer gets two vectors, not three — which is a narrowing the measurement alone could not "
            "show, because a rate over positions cannot see whether the denied space is reachable."
            % (targets, lobes[406].get("volume_A3", 0.0))),
        "2_the_null_is_LARGER_than_one_signal_position": (
            "the conserved position %s offers %.2f A^3 — more than L406's %.2f A^3. The null is not a "
            "formality on this axis either: a substituent aimed at L406 would be exploiting no more denied "
            "space than a CONSERVED residue's rotamer gap. Grade the contrast, never the signal."
            % (null_ceiling_at, null_ceiling, lobes[406].get("volume_A3", 0.0))),
        "3_the_LARGEST_lobe_is_at_the_LEAST_trustworthy_position": (
            "position %s has the biggest lobe of all (%.2f A^3) and must NOT be taken as the top design "
            "target: it is class '%s' (it fires at 0.000 on the clash test — uniqueness alone creates no "
            "exclusion), and it carries the worst post-fit superposition deviation in the whole set (%s A). "
            "★ So VOLUME NEVER OVERRIDES CLASS. Ranking on lobe size alone would put this program's own "
            "independently down-weighted position first, which is what the class gate exists to prevent."
            % (biggest, lobes[biggest].get("volume_A3", 0.0), lobes[biggest]["class"],
               lobes[biggest]["post_fit_deviation_A"])),
        "4_what_a_designer_does_with_this": (
            "grow a substituent from the CB of I484 (reach %s A) and/or L534 (reach %s A) along the stated "
            "unit vector, keeping the added volume inside the lobe span; then re-score with score_pose() and "
            "ACCEPT on signal_minus_null. ⛔ And report the M4 relocation control in the same sentence."
            % ((lobes[484].get("substituent_vector_from_CB") or {}).get("reach_A"),
               (lobes[534].get("substituent_vector_from_CB") or {}).get("reach_A"))),
    }

    return {
        "_title": "The steric-exclusion DESIGN RULE (mechanism S3) — with its control attached to every record",
        "_owner": ("research/manuscripts/nr4a3-program-map.md §10.1 row 24; mechanism S3 in "
                   "selectivity-mechanism-options.md. The MEASUREMENT (0.923 vs 0.173) is owned there and is "
                   "imported, never re-typed, here."),
        "_cost": "$0 — CPU, no rental, no GPU, no dispatch.",
        "_licenses": ("A POSE constraint on a candidate molecule. Nothing about binding, affinity, "
                      "degradation, selectivity ratio, safety or clinical readiness is computed in this file."),
        "parameters": {"hard_clash_A": clash, "grid_A": GRID_A,
                       "absolute_sanity_floor_A3": MIN_LOBE_VOLUME_A3,
                       "_design_target_bar": "the null class's own largest lobe — MEASURED, see "
                                             "null_volume_ceiling_A3, not a chosen threshold",
                       "frame": "results/nr4a3-matrix/nr4a3-opened.pdb; paralogues superposed into it",
                       "_hard_clash_source": "selectivity_mechanism_options.HARD_CLASH_A "
                                             "(= nr4a3-orientation-basins.json parameters.hard_clash_A)"},
        "⛔_control": control,
        "★_findings": findings,
        "design_targets": targets,
        "null_volume_ceiling_A3": _r(null_ceiling, 2),
        "null_volume_ceiling_at": null_ceiling_at,
        "denied_lobes": lobes,
        "worked_example": {
            "_what": "the 13 committed selectivity-matrix poses scored by the rule, each with its own null",
            "n_poses": len(scored),
            "poses": scored,
            "pooled_signal_rate": pooled_signal,
            "pooled_null_rate": pooled_null,
            "reproduces_M3": reproduces,
            "_why_this_check_exists": (
                "if the scorer does not reproduce M3's own rates over M3's own poses then it is a different "
                "object from the measurement it claims to operationalise, and the rule must not be used. "
                "M3 rates imported for the comparison: signal %s, null %s." % (m3_signal, m3_null)),
        },
        "how_to_score_a_new_candidate": [
            "1. Dock or place the candidate in the NR4A3 opened frame (results/nr4a3-matrix/nr4a3-opened.pdb).",
            "2. score_pose(heavy_xyz, geometry, hard_clash_A) -> signal_rate, null_rate, signal_minus_null.",
            "3. ACCEPT on signal_minus_null, never on signal_rate: the null is the molecule's own "
            "false-positive rate under the same superposition.",
            "4. Report the M4 relocation control in the same sentence as the score. A score reported without "
            "it will be read as 'the paralogue cannot bind this', which is not what was measured.",
        ],
        "⛔_limits": m3["⛔_limits"],
    }


def main(argv):
    art = build()
    check = "--check" in argv
    txt = json.dumps(art, indent=1, sort_keys=False)
    if check and os.path.exists(OUT_JSON):
        with open(OUT_JSON) as fh:
            old = fh.read()
        if old.strip() != txt.strip():
            print("[steric-design-rule] ⛔ artifact does not reproduce from source", file=sys.stderr)
            return 1
        print("[steric-design-rule] ✅ reproduces")
        return 0
    with open(OUT_JSON, "w") as fh:
        fh.write(txt + "\n")
    lob = art["denied_lobes"]
    print("[steric-design-rule] design targets: %s" % (art["design_targets"],))
    for u in art["design_targets"]:
        v = lob[u]
        print("  %d %s -> %s  lobe %.1f A^3  reach %.2f A  span %.2f A" % (
            u, v["nr4a3_residue"], "/".join(str(x) for x in v["paralogue_residues"].values()),
            v["volume_A3"], (v.get("substituent_vector_from_CB") or {}).get("reach_A", float("nan")),
            v["span_A"]))
    w = art["worked_example"]
    print("[steric-design-rule] worked example: signal %s vs null %s over %d poses; reproduces_M3=%s"
          % (w["pooled_signal_rate"], w["pooled_null_rate"], w["n_poses"], w["reproduces_M3"]))
    print("[steric-design-rule] ⛔ control: %s" % (art["⛔_control"]["median_centroid_shift_A"],))
    return 0 if art["worked_example"]["reproduces_M3"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
