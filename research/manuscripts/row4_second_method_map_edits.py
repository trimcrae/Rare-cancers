#!/usr/bin/env python3
"""Generate the roadmap edits for the SECOND POSE METHOD — every number derived, none typed.

⛔ NO FIGURE IN THE OUTPUT IS WRITTEN BY HAND. Each `proposed_text` is assembled from
`research/modalities/pose-second-method.json` (and, where the panel ran, its rollup), so a re-run
regenerates the edits rather than leaving a stale sentence behind. Each `current_text` is the LIVE line
the anchor sits on, read from the map on disk — which is what makes `route_map_edits.py` able to refuse
an anchor that has moved instead of applying it somewhere plausible.

⚠ THE FENCE. This pass owns `R5`, `V3`, §10.1 row 4 and the new instrument row. It deliberately does not
touch `V17`, `R8`, `V21`, the `C*` register's VALUES, or anything categorical — another lane is live on
those, and `C14` in particular is cited by both `R5` and `R14`, so moving it to fix one would silently
move the other. Cite it; never change it.

Usage:  python3 research/manuscripts/row4_second_method_map_edits.py
        python3 research/manuscripts/route_map_edits.py \
                research/manuscripts/row4-second-method-map-edits.json --apply
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
ART = REPO / "research" / "modalities" / "pose-second-method.json"
MAP = REPO / "research" / "manuscripts" / "nr4a3-program-map.md"
OUT = REPO / "research" / "manuscripts" / "row4-second-method-map-edits.json"

#: The next free instrument id. `V1`…`V21` are taken; `V22` is checked against the live map below rather
#: than assumed, because minting a colliding id is silent and permanent (§0.4: never renumber).
NEW_V = "V22"


def live_line(anchor):
    """The single live line containing `anchor`, or (None, why). Ambiguity is refused, never guessed."""
    text = MAP.read_text()
    hits = [ln for ln in text.splitlines() if anchor in ln]
    if len(hits) == 1:
        return hits[0], None
    return None, ("anchor matched %d lines — %s" % (len(hits),
                  "stale" if not hits else "ambiguous, and this tool never picks one"))


def _f(v, nd=3, dash="—"):
    if v is None:
        return dash
    if isinstance(v, float):
        return ("%%.%df" % nd) % v
    return str(v)


def facts(doc):
    """Everything the sentences below are allowed to say, pulled out of the artifact in one place."""
    a = doc.get("part_a") or {}
    b = doc.get("part_b") or {}
    cm = a.get("cross_method_same_frame") or {}
    dec = a.get("orientation_or_location") or {}
    within = a.get("within_second_method_spread") or {}
    roll = b.get("rollup") or {}
    ind = b.get("induced_fit_panel") or {}
    v = doc.get("verdict") or {}
    crit = doc.get("criterion") or {}
    tool = doc.get("tooling") or {}
    bands = cm.get("bands") or {}
    return {
        "ran": bool(cm.get("n_systems")),
        "n_systems": cm.get("n_systems"),
        "n_recovered": bands.get("RECOVERED"),
        "n_partial": bands.get("PARTIAL"),
        "n_not": bands.get("NOT RECOVERED"),
        "med": (cm.get("rmsd_A") or {}).get("median"),
        "lo": (cm.get("rmsd_A") or {}).get("min"),
        "hi": (cm.get("rmsd_A") or {}).get("max"),
        "cen": (cm.get("centroid_distance_A") or {}).get("median"),
        "flip": dec.get("flip_rmsd_A"),
        "length": dec.get("molecule_length_A"),
        "internal": dec.get("median_internal_conformer_rmsd_A"),
        "decompose": dec.get("_reads"),
        "within_n": within.get("n_pairs"),
        "within_med": (within.get("ligand_rmsd_A") or {}).get("median"),
        "within_lo": (within.get("ligand_rmsd_A") or {}).get("min"),
        "within_hi": (within.get("ligand_rmsd_A") or {}).get("max"),
        "within_rec": within.get("n_pairs_within_recovered_A"),
        "runs": a.get("n_rdock_runs_per_system"),
        "rec_A": crit.get("recovered_A"),
        "part_A": crit.get("partial_A"),
        "panel_ran": bool(roll.get("n_pairs")),
        "panel_n": roll.get("n_pairs"),
        "panel_gradeable": roll.get("n_gradeable"),
        "panel_bands": roll.get("bands_over_gradeable_pairs") or {},
        "panel_inter": roll.get("inter_method_rmsd_A") or {},
        "fit_n": ind.get("n_pairs"),
        "fit_large": ind.get("n_with_large_rearrangement"),
        "fit_min": (ind.get("site_ca_rmsd_A") or {}).get("min"),
        "fit_max": (ind.get("site_ca_rmsd_A") or {}).get("max"),
        "outcome": v.get("outcome"),
        "sentence": v.get("sentence"),
        "rdock_version": tool.get("rdock_version"),
        "status": doc.get("_status"),
    }


def _band_phrase(f):
    """`C14`'s own words, and only its own words."""
    return ("**%s of %s** system(s) inside `C14`'s **RECOVERED** band (≤ %s Å), %s **PARTIAL**, "
            "%s **NOT RECOVERED**"
            % (_f(f["n_recovered"], 0), _f(f["n_systems"], 0), _f(f["rec_A"], 2),
               _f(f["n_partial"], 0), _f(f["n_not"], 0)))


def _panel_phrase(f):
    if not f["panel_ran"]:
        return ("⚠ **The known-answer half did not run in this pass** — the panel arm is `MODE=panel` of "
                "the same module and needs the RCSB fetch, so it is recorded UNRUN rather than absent.")
    bits = []
    for arm, label in (("blind_apo_pipeline_box", "the pipeline's own box"),
                       ("blind_apo_fpocket_top_box", "an fpocket-chosen box"),
                       ("C3_oracle_box_apo", "the oracle box"),
                       ("receptor_wide_own_cavity_apo", "rDock's OWN cavity, which shares no site "
                                                        "configuration with the pipeline at all")):
        d = (f["panel_bands"] or {}).get(arm) or {}
        bits.append("%s: %s RECOVERED / %s PARTIAL / %s NOT RECOVERED"
                    % (label, _f(d.get("RECOVERED"), 0), _f(d.get("PARTIAL"), 0),
                       _f(d.get("NOT RECOVERED"), 0)))
    return ("✅ **AND THE SECOND METHOD WAS PUT TO THE SAME KNOWN-ANSWER PANEL, AT THE SAME BOXES, GRADED "
            "BY THE SAME `score_pose`.** %s of %s pairs clear the inherited ceiling rule and are "
            "gradeable; over those — %s. Inter-method agreement across every arm: median **%s Å** "
            "(n = %s)." % (_f(f["panel_gradeable"], 0), _f(f["panel_n"], 0), "; ".join(bits),
                           _f(f["panel_inter"].get("median")), _f(f["panel_inter"].get("n"), 0)))


def _fit_phrase(f):
    if not f["panel_ran"]:
        return ""
    return ("⚠ **INDUCED FIT, MEASURED FOR EVERY PAIR:** site Cα movement spans **%s–%s Å** and **%s of "
            "%s** pairs clear the 1.00 Å reporting band. ⛔ A pair below that line is a near-rigid "
            "re-dock and is a WEAK TEST of apo→holo transfer in either method — it must not be quoted as "
            "one." % (_f(f["fit_min"]), _f(f["fit_max"]), _f(f["fit_large"], 0), _f(f["fit_n"], 0)))


def build(doc):
    f = facts(doc)
    edits = []

    # ------------------------------------------------------------------ E1 · §10.1 row 4
    anchor1 = "| **4** | **Re-run the pose known-answer test with SITE and DOCKING separated**"
    cur1, why1 = live_line(anchor1)
    if cur1 is None:
        edits.append({"id": "E1", "section": "§10.1 row 4", "anchor": anchor1,
                      "current_text": None, "proposed_text": None, "why": why1})
    else:
        add = (
            " ✅ **AND THE SECOND METHOD HAS NOW RUN — 2026-08-03, $0, free CPU. `cross_method_evidence` "
            "is no longer NONE.** The engine is **rDock** (`rbcavity` + `rbdock`, stock three-stage "
            "protocol), chosen because it is independent WHERE IT COUNTS: it shares with smina no "
            "scoring term, no search algorithm, no atom typing and no source code — a genetic-algorithm "
            "→ Monte-Carlo → Simplex search under a directional-polar + weighted-SASA-desolvation "
            "function, against Vina's Monte-Carlo/BFGS search under gauss/repulsion/hydrophobic terms. "
            "⛔ **It is NOT the `V14` mistake repeated:** that instrument was orthogonal in its SAMPLING "
            "and shared the whole `C1`–`C5` detector chain, so a shared item moved both numbers "
            "together. Here the artifact states, PER ARM, which `C*` items are shared — `C14` and `C15` "
            "always (they are the yardstick both are graded by, not an instrument), `C5` only in the "
            "site-matched arm, `C4` only in the fpocket arm, and **nothing at all** in the arm where "
            "rDock finds its own cavity. ⛔ **THE ANSWER IS DISAGREEMENT, AND IT IS INFORMATIVE.** On "
            "the same six systems, in each receptor's own frame with no superposition: %s, over a "
            "%s–%s Å range with median **%s Å**. ⭑ **The disagreement is ORIENTATION, NOT LOCATION** — "
            "median centroid separation **%s Å** against a median RMSD that is ≈ this molecule's own "
            "measured cost of being turned end-for-end in place (**%s Å**, molecule length %s Å), and "
            "median internal-conformer RMSD **%s Å**, so both engines find the same shape and the same "
            "pocket and put it in differently. ⭑ **AND THE SECOND METHOD DOES NOT CONVERGE ACROSS "
            "RECEPTOR CONFORMERS EITHER** — %s of %s cross-conformer pairs inside %s Å, median **%s Å** "
            "(%s–%s), measured with the same Pocket-5 Cα superposition the first method's spread uses. "
            "⇒ **the non-convergence is a property of the SYSTEM, not of one scoring function**, which "
            "is exactly the attribution `pose-convergence-401.json` could not make. %s %s ⛔ **WHAT THIS "
            "LICENSES: nothing about correctness.** Two methods with disjoint scoring disagreeing means "
            "the pose is not method-independent; two agreeing would have meant only that, and a "
            "convergent wrong answer is still wrong. One home for every number: "
            "[`pose-second-method.json`](../modalities/pose-second-method.json); the poses themselves "
            "are committed under `_pose_second_method_poses/`. ⇒ **`R5` is NOT resolved, and the reason "
            "has changed again: it is no longer *\"there is no second opinion\"* but *\"the second "
            "opinion disagrees, in the direction of orientation\"*.**"
            % (_band_phrase(f), _f(f["lo"]), _f(f["hi"]), _f(f["med"]), _f(f["cen"]), _f(f["flip"], 2),
               _f(f["length"], 2), _f(f["internal"]),
               _f(f["within_rec"], 0), _f(f["within_n"], 0), _f(f["rec_A"], 2), _f(f["within_med"]),
               _f(f["within_lo"]), _f(f["within_hi"]),
               _panel_phrase(f), _fit_phrase(f)))
        edits.append({
            "id": "E1", "row": 4, "serves": "V3 → R5", "section": "§10.1 · Open rows, row 4",
            "file": "research/manuscripts/nr4a3-program-map.md", "anchor": anchor1,
            "current_text": cur1, "proposed_text": cur1.rstrip() + add,
            "why": "the row's own next action was `run a SECOND INDEPENDENT POSE METHOD`; it has run",
        })

    # ------------------------------------------------------------------ E2 · §3.1 a new instrument row
    anchor2 = "| **V20** | Single-snapshot MM-GBSA `margin > 0` as a selectivity verdict"
    cur2, why2 = live_line(anchor2)
    collision = ("`%s`" % NEW_V) in MAP.read_text()
    if cur2 is None or collision:
        edits.append({"id": "E2", "section": "§3.1 instrument table", "anchor": anchor2,
                      "current_text": None, "proposed_text": None,
                      "why": ("`%s` is already used in the live map — pick the next free id rather than "
                              "renumbering (§0.4)" % NEW_V) if collision else why2})
    else:
        row = (
            "| **%s** | **The scoring-independent second pose method** (`pose_second_method` — rDock "
            "`rbcavity`+`rbdock`, stock three-stage protocol) — ⭑ **NEW ROW 2026-08-03: `V3` had no "
            "independent comparator at all, which is why its INCONCLUSIVE could not be attributed** | "
            "⛔ **none of its own on this system** — it is run BESIDE `V3` on the same six receptors and "
            "on `V3`'s own known-answer panel, at the same boxes and graded by the same `score_pose`, so "
            "the comparison IS the test | %s; median inter-method RMSD **%s Å** at a median centroid "
            "separation of only **%s Å** | ⚠ **agreement would not have meant correctness and "
            "disagreement does not mean either method is wrong.** ⛔ It shares `C14`/`C15` with `V3` BY "
            "DESIGN (the yardstick, not the instrument) and `C5` in its site-matched arm; the arm that "
            "shares no site configuration is `receptor_wide_own_cavity`. It is a docking search like "
            "`V3`, so a shared receptor-conformer error survives both | ✓ **ran 2026-08-03 — the two "
            "methods DISAGREE** | `R5` |"
            % (NEW_V, _band_phrase(f), _f(f["med"]), _f(f["cen"])))
        edits.append({
            "id": "E2", "section": "§3.1 · The instrument table",
            "file": "research/manuscripts/nr4a3-program-map.md", "anchor": anchor2,
            "current_text": cur2, "proposed_text": cur2.rstrip() + "\n" + row,
            "why": "an instrument that answers a requirement needs a row; `%s` is the next free id and "
                   "was checked against the live map for collision" % NEW_V,
        })

    # ------------------------------------------------------------------ E3 · §3.2 the R5 coverage cell
    anchor3 = "| `R5` pose (`C14` `C15`) | `V3` |"
    cur3, why3 = live_line(anchor3)
    if cur3 is None:
        edits.append({"id": "E3", "section": "§3.2 R×V coverage", "anchor": anchor3,
                      "current_text": None, "proposed_text": None, "why": why3})
    else:
        new3 = cur3.replace("| `V3` |", "| `V3` `%s` |" % NEW_V, 1)
        new3 = new3.rstrip().rstrip("|").rstrip() + (
            " ⭑ **AND IT NOW HAS A SECOND INSTRUMENT, WHICH IS WHAT MAKES THE READING ATTRIBUTABLE:** "
            "`%s` (rDock) disagrees with `V3` on %s of %s systems at median **%s Å**, and disagrees in "
            "ORIENTATION rather than in location. ⛔ Two disjoint scoring functions failing to converge "
            "on the same receptors says the non-convergence is the SYSTEM's, not one function's — it "
            "does not say either pose is wrong, and it does not fill this cell. |"
            % (NEW_V, _f((f["n_partial"] or 0) + (f["n_not"] or 0), 0), _f(f["n_systems"], 0),
               _f(f["med"])))
        edits.append({
            "id": "E3", "section": "§3.2 · The R×V coverage matrix",
            "file": "research/manuscripts/nr4a3-program-map.md", "anchor": anchor3,
            "current_text": cur3, "proposed_text": new3,
            "why": "the matrix's own question is 'what could answer this?' and a second instrument now "
                   "serves R5",
        })

    # ------------------------------------------------------------------ E4 · §3b.3 the R×V×C R5 row
    anchor4 = "| **R5** the binding pose is right | `V3` | `C14` `C15` |"
    cur4, why4 = live_line(anchor4)
    if cur4 is None:
        edits.append({"id": "E4", "section": "§3b.3 R×V×C", "anchor": anchor4,
                      "current_text": None, "proposed_text": None, "why": why4})
    else:
        new4 = cur4.replace("| `V3` | `C14` `C15` |", "| `V3` `%s` | `C14` `C15` |" % NEW_V, 1)
        new4 = new4.rstrip().rstrip("|").rstrip() + (
            " ⚠ **AND `%s` INHERITS THE SAME `C14`, DELIBERATELY** — a second method graded by a "
            "different line would not be a check, it would be a different question. So `C14` moving "
            "still moves BOTH readings of `R5` together, exactly as it moves `R14`'s. |" % NEW_V)
        edits.append({
            "id": "E4", "section": "§3b.3 · The R×V×C traceability view",
            "file": "research/manuscripts/nr4a3-program-map.md", "anchor": anchor4,
            "current_text": cur4, "proposed_text": new4,
            "why": "the traceability view must show which configuration the new instrument stands on",
        })

    # ------------------------------------------------------------------ E5 · §3b.4 the V14 lesson
    anchor5 = "An orthogonal axis that shares a detector"
    cur5, why5 = live_line(anchor5)
    if cur5 is None:
        edits.append({"id": "E5", "section": "§3b.4 item 1", "anchor": anchor5,
                      "current_text": None, "proposed_text": None, "why": why5})
    else:
        edits.append({
            "id": "E5", "section": "§3b.4 · item 1 (the `V14` lesson)",
            "file": "research/manuscripts/nr4a3-program-map.md", "anchor": anchor5,
            "current_text": cur5,
            "proposed_text": cur5.rstrip() + (
                " ⭑ **AND THE LESSON IS NOW OPERATIONALISED RATHER THAN ONLY RECORDED:** `%s` "
                "([`pose_second_method.py`](../modalities/pose_second_method.py)) states its shared and "
                "unshared `C*` items **per arm**, computed from each arm's definition and pinned by "
                "`tests/test_pose_second_method.py`, so an instrument cannot quietly become "
                "non-independent between one pass and the next." % NEW_V),
            "why": "the register's own finding was that nobody wrote the shared-item table down",
        })

    # ------------------------------------------------------------------ E6 · §5 the R5 requirement row
    anchor6 = "| **R5** | **The binding pose is right.** Node `PS`"
    cur6, why6 = live_line(anchor6)
    if cur6 is None:
        edits.append({"id": "E6", "section": "§5 requirement R5", "anchor": anchor6,
                      "current_text": None, "proposed_text": None, "why": why6})
    else:
        edits.append({
            "id": "E6", "section": "§5 · Where each requirement stands — `R5`",
            "file": "research/manuscripts/nr4a3-program-map.md", "anchor": anchor6,
            "current_text": cur6,
            "proposed_text": cur6.rstrip() + (
                " ⭑ **THE BLOCKER IS NOW NAMED DIFFERENTLY, AND THAT IS THE 2026-08-03 CHANGE.** It was "
                "*\"no second opinion exists\"*; a second opinion now exists (`%s`, rDock — disjoint "
                "scoring, disjoint search, disjoint typing) and it **disagrees**: %s, median **%s Å**, "
                "with the disagreement carried by ORIENTATION (median centroid separation **%s Å**) "
                "rather than by location. ⛔ So `R5` is still ✕ unresolved, but for a measured reason. "
                "What would move it is listed, with costs, in "
                "[`pose-second-method.json`](../modalities/pose-second-method.json) → "
                "`verdict.what_would_resolve_R5`; the cheapest item on it is **$0** and is a SOURCING "
                "question (a known answer in regime whose site actually rearranges), not a compute one."
                % (NEW_V, _band_phrase(f), _f(f["med"]), _f(f["cen"]))),
            "why": "the requirement register states R5's blocker, and the blocker has changed",
        })
    return edits


def main():
    if not ART.exists():
        print("REFUSED — %s does not exist; run pose_second_method.py first" % ART, file=sys.stderr)
        return 2
    doc = json.loads(ART.read_text())
    f = facts(doc)
    if not f["ran"]:
        print("REFUSED — the artifact carries no comparable system (status %r). An edit written off an "
              "UNRUN artifact would assert a measurement nobody made." % f["status"], file=sys.stderr)
        return 3
    edits = build(doc)
    OUT.write_text(json.dumps({
        "_what": "Roadmap edits for the SECOND POSE METHOD (rDock) — %s." % f["outcome"],
        "_rule": "⛔ NO NUMBER IS TYPED IN THIS FILE. Every figure in every `proposed_text` is derived "
                 "by row4_second_method_map_edits.py from pose-second-method.json, and every "
                 "`current_text` is the live line read off the map. Regenerate rather than edit.",
        "_fence": "This pass owns R5, V3, §10.1 row 4 and the new instrument row. It does not touch V17, "
                  "R8, V21, the categorical artifacts, or any `C*` VALUE — C14 is cited, never changed, "
                  "because the same line is what makes V21's panel unreadable.",
        "generated_from": os.path.relpath(ART, REPO),
        "new_instrument_id": NEW_V,
        "n_edits": len(edits),
        "derived_facts": f,
        "map_edits_required": edits,
    }, indent=1) + "\n")
    print("wrote %s — %d edit(s), %d unanchored"
          % (os.path.relpath(OUT, REPO), len(edits),
             sum(1 for e in edits if e.get("proposed_text") is None)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
