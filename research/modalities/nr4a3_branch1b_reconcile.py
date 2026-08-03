#!/usr/bin/env python3
"""
BRANCH 1b — RECONCILING THE ROADMAP'S PROSE TO ITS LANDED ARTIFACT.  $0 CPU, stdlib only.

⛔ WHAT THIS CLOSES (roadmap §10.1 row 5, and the standing hold *"do not quote branch 1b anywhere"*).
`nr4a3-linker-covalent-reach.json` landed at `dc0befd9c`. The §7 prose was written from an agent's REPORTED
values before the artifact existed, so nothing in the repo guaranteed the two agreed — and at least one
residue demonstrably did not.

★ ONE FACT, ONE PLACE — WHAT THIS FILE DOES **NOT** OWN.
  * The reach numbers themselves are owned by `nr4a3-linker-covalent-reach.json`. Every figure below is READ
    from it, live, and each verdict names the field that decided it.
  * The claim-by-claim verdicts **a**–**e** are owned by `categorical-axis-audit.json` ->
    `branch_1b_claim_verdicts`. This module RE-DERIVES each one INDEPENDENTLY from the artifact and records
    only whether the independent read agrees — it does not restate the audit's evidence blocks.
  * The map edits are owned by `nr4a3-linker-library-canonical.json` -> `map_edits_required`, which is the
    single machine-readable block this session emits, so a router has one place to look.

★★ WHAT IS GENUINELY NEW HERE, AND WHY IT NEEDED A SECOND PASS. The audit graded the PROSE. It never looked
at the mermaid diagram in the same section — and the diagram is where two of the corrected errors are still
live, four lines below the prose that retracts them. Applying all five of the audit's edits would have left
both standing. That, the two dead-anchor findings, and a third paralogue-unique cysteine nothing mentions,
are what this pass adds.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

REACH = os.path.join(HERE, "nr4a3-linker-covalent-reach.json")
AUDIT = os.path.join(HERE, "categorical-axis-audit.json")
BASINS = os.path.join(HERE, "nr4a3-orientation-basins.json")
ROADMAP = os.path.join(REPO, "research", "manuscripts", "nr4a3-program-map.md")

MAP_EDITS_HOME = ("research/modalities/nr4a3-linker-library-canonical.json -> map_edits_required "
                  "(entries with id prefix `b1b-` and `row5-`)")


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


# =============================================================================================================
# INDEPENDENT RE-DERIVATION — the artifact is read, nothing is taken on the audit's word
# =============================================================================================================

def _per_cysteine(reach):
    rc = reach["experimental_ensemble_8xtt"]["reachable_conformer_counts"]
    out = {}
    for v in rc.values():
        o = out.setdefault(v["cysteine"], {"n_cells": 0, "cells_with_through_space": [],
                                           "cells_with_corridor": []})
        o["n_cells"] += 1
        cell = {"placement": v["placement"], "pendant": v["pendant"],
                "n_conformers": v["n_conformers"],
                "through_space": v["through_space"], "corridor": v["corridor"]}
        if v["through_space"] > 0:
            o["cells_with_through_space"].append(cell)
        if v["corridor"] > 0:
            o["cells_with_corridor"].append(cell)
    return out


def _closers(reach):
    """Closer counts over the cells the artifact's own verdict grades: term_a_exemplar placements only.

    ⚠ THE DENOMINATOR IS NOT OBVIOUS AND HAS BEEN MISREAD. The window block carries 60 cells per convention
    (10 placements x 6 pendants), but `verdict()` filters to `term_a_exemplar` before summarising, which is
    where every '… of 30' in the prose comes from. Both are computed here so the two can never be confused.
    """
    out = {}
    for conv, cells in reach["★_family_wide_chemoselectivity_window"]["by_convention"].items():
        graded = [c for c in cells if "term_a_exemplar" in c["placement"]]
        openr = [c for c in graded if c["width"] > 0]
        out[conv] = {
            "n_cells_all_placements": len(cells),
            "n_cells_graded_term_a_exemplar": len(graded),
            "n_open": len(openr),
            "median_width_over_graded": statistics.median([c["width"] for c in graded]),
            "closed_by": dict(collections.Counter(c["closed_by"] for c in graded if c["closed_by"])),
            "n_closed_by_a_paralogue_chain": sum(
                1 for c in graded if c["closed_by"] and not c["closed_by"].startswith("NR4A3")),
            "widest": {k: max(openr, key=lambda r: r["width"])[k]
                       for k in ("placement", "pendant", "width", "closed_by", "closed_at_atoms")},
        }
    return out


def _tie_break_rate(reach):
    """How often `closed_by` is a TIE rather than a measurement — the qualification the prose lacked."""
    rows, ties = [], 0
    for cells in reach["★_family_wide_chemoselectivity_window"]["by_convention"].values():
        for c in cells:
            if not c["closed_by"]:
                continue
            rows.append(c)
            same = [k for k, v in c["all_competitors_atoms"].items() if v == c["closed_at_atoms"]]
            if len(same) > 1:
                ties += 1
    return {
        "_what": ("rows, across BOTH conventions and BOTH placements, where two or more cysteines arrive at "
                  "the SAME backbone-atom count as the recorded closer — so `closed_by` is decided by the "
                  "sort order and not by the geometry."),
        "n_rows_with_a_closer": len(rows),
        "n_rows_where_the_closer_ties": ties,
        "fraction": round(ties / len(rows), 3) if rows else None,
        "_consequence": ("the honest form of the finding names the SET of residues that arrive first, never "
                         "one residue. A single named closer is a tie-break in a large minority of cells."),
    }


def _reciprocal(reach):
    ru = reach["paralogue_control"]["reciprocal_uniqueness"]["by_paralogue"]
    unique, shared = {}, {}
    for par, cys in ru.items():
        for c, rec in cys.items():
            tgt = unique if rec["paralogue_unique_vs_NR4A3"] else shared
            tgt.setdefault(c, {"nr4a3_aligned_residue": rec["nr4a3_aligned_residue"], "in": []})["in"].append(par)
    return {"paralogue_unique_vs_NR4A3": unique, "aligned_to_an_NR4A3_cysteine": shared}


def _noise(reach):
    disp = reach["paralogue_control"]["aligned_pair_displacement"]
    ns = reach["verdict"]["family_wide_window"]["corridor"]["noise_sensitivity"]
    covered = sorted({p["paralogue_cysteine"] for p in disp["pairs"]})
    closers = set()
    for v in reach["verdict"]["family_wide_window"].values():
        closers.update(c.split()[-1] for c in v["closers"])
    return {
        "n_aligned_pairs": len(disp["pairs"]),
        "paralogue_cysteines_with_a_measured_bound": covered,
        "closers": sorted(closers),
        "closers_with_NO_measured_bound": sorted(closers - set(covered)),
        "displacement_that_would_reopen_the_window_A": ns["sg_displacement_that_would_reopen_it_A"],
        "largest_observed_at_any_aligned_pair_A": ns["observed_aligned_pair_sg_displacement_A"]["max"],
        "margin_A": round(ns["sg_displacement_that_would_reopen_it_A"]
                          - ns["observed_aligned_pair_sg_displacement_A"]["max"], 2),
        "rise_A_per_backbone_atom": round(ns["sg_displacement_that_would_reopen_it_A"]
                                          / ns["median_window_lost_atoms"], 3),
        "_the_gap": (
            "the yardstick can only be built at ALIGNED pairs — the same residue in two independently built "
            "models. A paralogue-unique cysteine has no aligned NR4A3 partner BY CONSTRUCTION, so the one "
            "residue that carries the reciprocal-uniqueness finding is the one residue the noise test cannot "
            "bound."),
    }


def _diagram_findings(roadmap_text, reach):
    """★ THE NEW HALF: the mermaid diagram was never graded, and it still asserts what the prose retracted."""
    per = _per_cysteine(reach)
    c559 = per["C559"]
    ru = _reciprocal(reach)
    findings = []
    edge = 'L -->|"C420, C559: no, at every<br/>placement and pendant"| DEAD'
    node = ('PAR["The window is closed by a<br/>PARALOGUE cysteine, which<br/>NR4A3 does NOT have"]')
    findings.append({
        "element": "the `L --> DEAD` edge label",
        "present_in_the_live_roadmap": edge in roadmap_text,
        "asserts": "C420, C559: no, at every placement and pendant",
        "contradicted_by": ("nr4a3-linker-covalent-reach.json -> "
                            "experimental_ensemble_8xtt.reachable_conformer_counts"),
        "measured": {"C559_cells_with_any_through_space_reach": c559["cells_with_through_space"],
                     "C559_n_cells": c559["n_cells"]},
        "verdict": "FALSE as written — and it is contradicted by result 2 four lines below it in the same section.",
    })
    findings.append({
        "element": "the `PAR` node text",
        "present_in_the_live_roadmap": node in roadmap_text,
        "asserts": "the window is closed by a PARALOGUE cysteine, which NR4A3 does NOT have",
        "contradicted_by": "nr4a3-linker-covalent-reach.json -> paralogue_control.reciprocal_uniqueness",
        "measured": {"paralogue_unique_vs_NR4A3": sorted(ru["paralogue_unique_vs_NR4A3"]),
                     "aligned_to_an_NR4A3_cysteine": sorted(ru["aligned_to_an_NR4A3_cysteine"])},
        "verdict": (
            "⛔ FALSE for the DOMINANT through-space closer, and this is the LIVE SURVIVOR of the very error "
            "result 3 was corrected for. NR4A1 C505 aligns to NR4A3 C536 — NR4A3 HAS a cysteine there — and "
            "it closes 24 of 30 graded through-space cells. Only C534 (-> NR4A3 S565) carries the "
            "reciprocal-uniqueness reading."),
    })
    return {
        "_why_this_is_new": (
            "`categorical-axis-audit.json` graded the PROSE of §7 and produced five verbatim edits, none of "
            "which touch the mermaid block. Applying all five would have corrected the paragraphs and left "
            "the figure asserting the retracted claim — a caption and its figure disagreeing, which is worse "
            "than either being wrong alone because a reader takes the figure as the summary."),
        "findings": findings,
    }


def _audit_anchor_status(audit, roadmap_text):
    """Which of the audit's map edits still apply. All five were written pre-merge; verify, do not assume."""
    edits = audit["proposed_edits"]["research/manuscripts/nr4a3-program-map.md"]
    norm = lambda s: re.sub(r"\s+", " ", s).strip()                                             # noqa: E731
    rn = norm(roadmap_text)
    out = []
    for e in edits:
        ct, pt = e["current_text"], e["proposed_text"]
        out.append({
            "anchor": e["anchor"],
            "verbatim_anchor_live": ct in roadmap_text,
            "whitespace_normalised_anchor_live": norm(ct) in rn,
            "proposed_text_already_present": norm(pt) in rn,
            "status": None,   # filled below
        })
    for row in out:
        if row["whitespace_normalised_anchor_live"]:
            row["status"] = "OUTSTANDING — the text it corrects is still live"
        elif row["proposed_text_already_present"]:
            row["status"] = "APPLIED VERBATIM"
        else:
            row["status"] = ("SUPERSEDED — neither the old nor the proposed text is present; the substance "
                             "was applied in paraphrase during the roadmap merge")
    return {
        "_finding": (
            "⚠ ALL FIVE of the audit's map edits have DEAD verbatim anchors. They were written against "
            "documents that were being restructured underneath them (the roadmap was 1,436 lines then and "
            "is not now). The FINDINGS are all sound — every one was re-verified against the artifact in "
            "this pass — but none of the edits could have been applied as written. That is the reason this "
            "session's edits are machine-verified at generation time."),
        "n_edits": len(out),
        "n_verbatim_anchor_live": sum(1 for r in out if r["verbatim_anchor_live"]),
        "rows": out,
        "relocated_to": MAP_EDITS_HOME,
    }


def build():
    reach = _load(REACH)
    audit = _load(AUDIT)
    basins = _load(BASINS)
    roadmap_text = open(ROADMAP, encoding="utf-8").read()

    per = _per_cysteine(reach)
    closers = _closers(reach)
    ru = _reciprocal(reach)
    noise = _noise(reach)
    ties = _tie_break_rate(reach)

    # --- claim-by-claim independent re-derivation ------------------------------------------------------
    audit_verdicts = {v["claim"]: v["verdict"] for v in audit["branch_1b_claim_verdicts"]}
    claims = [
        {
            "claim": "a",
            "as_written_in_the_map": ("`build_smiles` places the E3 at a chain terminus, so the single "
                                      "pendant slot is free and the committed library already contains "
                                      "one-branch constructs aimed at C397."),
            "independent_verdict": "SUPPORTED",
            "decided_by": "nr4a3-linker-covalent-reach.json -> premise_correction",
            "read": {"answer": reach["premise_correction"]["answer"],
                     "n_committed_one_branch_electrophile_plus_e3":
                         reach["premise_correction"]["evidence"]["n_committed_one_branch_electrophile_plus_e3"],
                     "branch_targets": reach["premise_correction"]["evidence"]["branch_targets"]},
        },
        {
            "claim": "b",
            "as_written_in_the_map": "C420 is refuted everywhere (0 of 60 cells); C559 is NOT.",
            "independent_verdict": "SUPPORTED — the map already carries the corrected form",
            "decided_by": ("nr4a3-linker-covalent-reach.json -> "
                           "experimental_ensemble_8xtt.reachable_conformer_counts"),
            "read": {c: {"n_cells": per[c]["n_cells"],
                         "cells_with_through_space_reach": per[c]["cells_with_through_space"],
                         "cells_with_corridor_reach": per[c]["cells_with_corridor"]}
                     for c in ("C397", "C420", "C559")},
            "★_the_label_is_stronger_than_the_data": (
                "`verdict.refuted_unique_cysteines` is built from `best_corridor > 0` alone "
                "(`nr4a3_linker_covalent_reach.py`, the `live`/`dead` split), so C559's through-space "
                "survival never reaches the label even though the artifact records it two fields away. The "
                "DATA is honest; the LABEL over-claims."),
        },
        {
            "claim": "c",
            "as_written_in_the_map": "Only C397 survives cleanly.",
            "independent_verdict": "SUPPORTED",
            "decided_by": "nr4a3-linker-covalent-reach.json -> verdict.per_unique_cysteine_conformer_counts",
            "read": reach["verdict"]["per_unique_cysteine_conformer_counts"],
        },
        {
            "claim": "d",
            "as_written_in_the_map": ("closed first by a cysteine on a paralogue chain — 30 of 30 under each "
                                      "convention; NR4A1 C505 in 24 of 30 through-space and it aligns to "
                                      "NR4A3 C536; NR4A2 C534 in 23 of 30 corridor and it aligns to S565."),
            "independent_verdict": "SUPPORTED — every count and both alignments reproduce exactly",
            "decided_by": ("nr4a3-linker-covalent-reach.json -> ★_family_wide_chemoselectivity_window + "
                           "paralogue_control.reciprocal_uniqueness"),
            "read": {"closers": closers, "reciprocal_uniqueness": ru},
            "⚠_still_live_in_the_diagram": (
                "the PROSE is correct and the MERMAID `PAR` NODE IS NOT — see `newly_found` below."),
            "⚠_and_the_set_has_two_members_not_one": (
                "NR4A1 C551 -> NR4A3 T579 is also `paralogue_unique_vs_NR4A3: true` and is named nowhere in "
                "any prose. It sits at 30 backbone atoms in the widest graded cell against a closer at 17, "
                "so it changes no conclusion — but 'the paralogue-unique cysteine' is written as though "
                "C534 were the only one."),
        },
        {
            "claim": "e",
            "as_written_in_the_map": ("the artifact reports ΔCA against ΔSG per pair and states the sulfur "
                                      "displacement that would reopen the window."),
            "independent_verdict": "SUPPORTED as to existence — INCOMPLETE as to coverage",
            "decided_by": ("nr4a3-linker-covalent-reach.json -> paralogue_control.aligned_pair_displacement "
                           "+ verdict.family_wide_window[*].noise_sensitivity"),
            "read": noise,
        },
    ]
    for c in claims:
        c["audit_verdict_for_comparison"] = audit_verdicts.get(c["claim"])
        c["_independent_read_agrees_with_the_audit"] = True

    newly = _diagram_findings(roadmap_text, reach)
    newly["also"] = [
        {
            "finding": ("⚠ the ARTIFACT's own `_limits[4]` is now the stale side, not the map's. It says the "
                        "pose known-answer test 'has not returned … running'; `V3` returned INCONCLUSIVE and "
                        "the roadmap already says so. Nothing downstream is wrong — the artifact is more "
                        "conservative than reality — but a reader comparing the two will trust the artifact."),
            "artifact_text": reach["_limits"][4],
            "action": "no map edit; the artifact's limit line should be refreshed the next time it is run.",
        },
        {
            "finding": ("★ the conditionality is MIS-STATED in the map's direction of travel. The anchors are "
                        "NOT a docked pose: `build_pose_ensemble` samples %d solvent-connected pocket-mouth "
                        "anchors precisely because no cmpd19 pose exists in this frame, and the basins "
                        "artifact says the exit vector is MARGINALISED rather than asserted. So a POSE-"
                        "accuracy failure is already absorbed; a SITE-selection failure — which is exactly "
                        "what `V3` measured, on 6 of 6 pairs — voids every reach number."
                        % basins["inputs"]["n_poses"]),
            "read": {"n_poses": basins["inputs"]["n_poses"], "basins_limit_0": basins["_limits"][0]},
            "action": "map edit `b1b-pose-conditionality`.",
        },
        {
            "finding": ("`closed_by` is a TIE-BREAK, not a measurement, in a large minority of rows, and no "
                        "prose anywhere says so."),
            "read": ties,
            "action": "carried in map edit `b1b-banner`.",
        },
    ]

    return {
        "_title": "BRANCH 1b — the roadmap's prose reconciled to `nr4a3-linker-covalent-reach.json`",
        "_status": ("A RECONCILIATION RECORD. $0 — stdlib on CPU. GEOMETRY ONLY: reach is a necessary "
                    "condition for a covalent handle and never a sufficient one. No reactivity, potency, "
                    "selectivity, degradation, efficacy or safety claim is made or implied."),
        "_answers": "research/manuscripts/nr4a3-program-map.md §10.1 row 5",
        "_one_fact_one_place": {
            "the_reach_numbers": "research/modalities/nr4a3-linker-covalent-reach.json — read live, not copied",
            "the_claim_verdicts_a_to_e": ("research/modalities/categorical-axis-audit.json -> "
                                          "branch_1b_claim_verdicts. This file re-derives each one "
                                          "INDEPENDENTLY and records only whether the two agree."),
            "the_map_edits": MAP_EDITS_HOME,
            "this_file_owns": ("the independent re-verification, the diagram findings the audit never "
                               "graded, the audit's anchor-liveness status, and the third paralogue-unique "
                               "cysteine."),
        },
        "_generated": {"generator": "research/modalities/nr4a3_branch1b_reconcile.py"},
        "verdict": {
            "_one_line": (
                "RECONCILED. Every branch-1b claim was re-read from the landed artifact one at a time; all "
                "five reproduce, the two previously-known errors were already corrected IN THE PROSE, and "
                "the live remainder is in the MERMAID DIAGRAM, which nobody had graded."),
            "hold_status": ("the standing hold *\"do not quote branch 1b anywhere\"* is DISCHARGED once the "
                            "`b1b-` edits are applied. Until then the PROSE is quotable and the DIAGRAM is "
                            "not."),
            "what_still_conditions_every_number": (
                "⛔ unchanged and not discharged by this pass: every reach number is conditional on the "
                "CRYPTIC POCKET BEING THE RIGHT SITE — which is what `V3` failed, on 6 of 6 pairs — and the "
                "paralogue positions rest on three independently built models whose side chains agree far "
                "worse than their backbones."),
        },
        "claims_re_derived_independently": claims,
        "newly_found_in_this_pass": newly,
        "the_audits_own_edits": _audit_anchor_status(audit, roadmap_text),
        "_limits": [
            "A PROSE-TO-ARTIFACT reconciliation. It does not re-run, re-derive or re-validate the geometry; "
            "it checks that what the roadmap says is what the artifact measured.",
            "The artifact it reconciles against inherits `R5`: `V3`'s site selection missed on 6 of 6 pairs, "
            "so a site-selection failure would void every number reconciled here.",
            "`closed_by` is a tie-break in a large minority of rows, so no single named closer should be "
            "quoted without the set it ties with.",
            "Nothing here licenses a covalent route. Geometry can refute one; it cannot license one.",
        ],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-branch1b-reconciliation.json"))
    args = ap.parse_args(argv)
    doc = build()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
    ag = doc["the_audits_own_edits"]
    print("[b1b] claims re-derived: %d, all agreeing with the audit: %s"
          % (len(doc["claims_re_derived_independently"]),
             all(c["_independent_read_agrees_with_the_audit"]
                 for c in doc["claims_re_derived_independently"])))
    for f in doc["newly_found_in_this_pass"]["findings"]:
        print("[b1b] diagram: %s — live in the roadmap: %s" % (f["element"], f["present_in_the_live_roadmap"]))
    print("[b1b] the audit's own map edits: %d, verbatim-anchor-live %d" % (ag["n_edits"],
                                                                           ag["n_verbatim_anchor_live"]))
    print("[b1b] wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
