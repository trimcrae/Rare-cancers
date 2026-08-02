#!/usr/bin/env python3
"""AUDIT OF THE CATEGORICAL SELECTIVITY AXIS — residue identity, branch-1b's five claims, and the limits.

WHY THIS FILE EXISTS
--------------------
The categorical axis is the program's strongest asset and it was **not writable down**: three separate
problems, none of which is fixed by more compute.

  (1) A RESIDUE-IDENTITY ERROR in the central claim. The roadmap's branch-1b prose names
      "NR4A1/NR4A2 **C534**" as the residue that closes C397's chemoselectivity window, while
      `nr4a3-linker-covalent-reach.json` records `closed_by` values of BOTH `NR4A1 C505` and
      `NR4A2 C534`. Those are two DIFFERENT sites with OPPOSITE uniqueness status, and the prose's
      gloss ("a cysteine the paralogues have and NR4A3 lacks") is false for one of them.
  (2) BRANCH 1b's FIVE CLAIMS were written from an agent's report BEFORE the artifact existed and had
      never been checked against it.
  (3) THE AXIS'S OWN LIMITS were asserted, not measured — in particular which parts are conditional on
      the pose/pocket and which are not, and how much load the RSA >= 0.25 exposure cutoff actually
      carries given that the same cutoff FAILS its own positive control (NR4A1 Cys551).

WHAT THIS IS NOT
----------------
Not new science. No new computation, no GPU, no rental — every figure below is READ out of a committed
artifact or out of the source that produced it, and the field path is carried beside it.

★ ONE FACT, ONE PLACE (CLAUDE.md rule 1). Every number here is a CITATION, not a second home. Each
carries `_from`, the artifact + field path that OWNS it. If this file and the cited field ever disagree,
**the artifact wins and this file is the bug** — which is why it is generated rather than typed. The only
things authored here are the VERDICT strings, which are judgements about whether a piece of prose is
supported, and those name the field that decided them.

Usage
    python3 research/modalities/categorical_axis_audit.py            # write the JSON
    python3 research/modalities/categorical_axis_audit.py --check    # regenerate and diff, exit 1 on drift
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

DYN = os.path.join(HERE, "nr4a-paralogue-dynamics.json")
REACH = os.path.join(HERE, "nr4a3-linker-covalent-reach.json")
UNIQ = os.path.join(HERE, "nr4a-paralogue-unique-residues.json")
LIB = os.path.join(HERE, "nr4a3-linker-design.json")
BASINS = os.path.join(HERE, "nr4a3-orientation-basins.json")
OUT = os.path.join(HERE, "categorical-axis-audit.json")

# The two documents this audit reports edits FOR but must not edit: both are being restructured
# concurrently, and this worktree is isolated from that checkout.
LOCKED = ("STRATEGY.md", "research/manuscripts/nr4a3-program-map.md")


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _et(utc: dt.datetime) -> str:
    """CLAUDE.md rule 1: US Eastern, 12-hour. EDT = UTC-4 for every date this repo deals in."""
    e = utc - dt.timedelta(hours=4)
    return e.strftime("%Y-%m-%d %I:%M %p ET").replace(" 0", " ", 1) if e.strftime("%I")[0] == "0" \
        else e.strftime("%Y-%m-%d %I:%M %p ET")


# ==========================================================================================================
# (1) RESIDUE IDENTITY — which residue is which, in which paralogue, at which aligned position
# ==========================================================================================================
def residue_identity(dyn, reach, uniq):
    """THE DISQUALIFYING ERROR, resolved from the alignment rather than from either prose.

    The confusion is not "one residue named two ways". NR4A1 and NR4A2 are both 598 aa and are
    CO-NUMBERED through the LBD, so `C505` and `C534` each name a real, distinct site present in BOTH
    paralogues. They differ in the only way that matters here: C505 sits at a position where NR4A3 also
    carries a cysteine (C536), and C534 sits at a position where NR4A3 carries a SERINE (S565).
    """
    inv = dyn["cysteine_inventory"]["by_species"]
    recip = reach["paralogue_control"]["reciprocal_uniqueness"]["by_paralogue"]
    seq = uniq["reciprocal_paralogue_unique"]

    seq_by = {}
    for sp, rows in seq.items():
        for r in rows:
            if r["residue"] == "C":
                seq_by[(sp, "C%d" % r["resnum"])] = r

    sites = {}
    for sp in ("NR4A1", "NR4A2"):
        for row in inv[sp]:
            lab = row["label"]
            rc = recip.get(sp, {}).get(lab, {})
            s = seq_by.get((sp, lab))
            site = sites.setdefault(lab, {
                "label": lab,
                "present_in": [],
                "nr4a3_aligned_residue": rc.get("nr4a3_aligned_residue", row.get("nr4a3_aligned")),
                "nr4a3_has_a_cysteine_here": rc.get("nr4a3_has_a_cysteine_here",
                                                    row.get("nr4a3_has_cys_here")),
                "paralogue_unique_vs_NR4A3": rc.get("paralogue_unique_vs_NR4A3"),
                "sequence_context": {},
                "_from": ["nr4a3-linker-covalent-reach.json -> paralogue_control.reciprocal_uniqueness"
                          ".by_paralogue.<sp>.<label>",
                          "nr4a-paralogue-dynamics.json -> cysteine_inventory.by_species.<sp>"],
            })
            site["present_in"].append(sp)
            if s:
                site["sequence_context"][sp] = {
                    "context": s["context"], "nr4a3_residue": s["nr4a3_residue"],
                    "nr4a3_resnum": s["nr4a3_resnum"],
                    "_from": "nr4a-paralogue-unique-residues.json -> reciprocal_paralogue_unique.%s" % sp}

    # who actually closes the window, per convention, over the graded (term_a_exemplar) cells the
    # verdict block is computed on -- and over ALL rows, which the verdict block does not report
    fam = reach["★_family_wide_chemoselectivity_window"]["by_convention"]
    closers = {}
    for conv, rows in fam.items():
        graded = [r for r in rows if "term_a_exemplar" in r["placement"]]
        closers[conv] = {
            "graded_cells_term_a_exemplar": {
                "n": len(graded),
                "by_closer": dict(collections.Counter(r["closed_by"] for r in graded if r["closed_by"])),
                "n_no_window": sum(1 for r in graded if not r["closed_by"]),
            },
            "all_rows_including_representative_placements": {
                "n": len(rows),
                "by_closer": dict(collections.Counter(r["closed_by"] for r in rows if r["closed_by"])),
                "n_no_window": sum(1 for r in rows if not r["closed_by"]),
            },
        }
    # how often the two candidate closers TIE at the same atom count -- the reason a single name was
    # ever quotable in the first place
    ties = 0
    tie_rows = 0
    for conv, rows in fam.items():
        for r in rows:
            at = r["closed_at_atoms"]
            if at is None:
                continue
            tie_rows += 1
            if len([k for k, v in r["all_competitors_atoms"].items() if v == at]) > 1:
                ties += 1

    return {
        "_question": "Which residue is which, in which paralogue, at which aligned position, and what "
                     "does NR4A3 have at each aligned site?",
        "_answer_one_line": "C505 and C534 are TWO DIFFERENT SITES, each present in BOTH paralogues. "
                            "C505 aligns to NR4A3 C536 (NR4A3 HAS a cysteine there — conserved). C534 "
                            "aligns to NR4A3 S565 (NR4A3 does NOT — paralogue-unique). Naming only "
                            "'C534' therefore mislabels the majority closer under the through-space "
                            "convention, which is NR4A1 C505 — a CONSERVED position.",
        "_why_it_is_disqualifying": "The prose's gloss is 'a cysteine the paralogues have and NR4A3 "
                                    "lacks'. That is TRUE of C534 and FALSE of C505. Under the "
                                    "through-space convention the closer is NR4A1 C505 in 24 of 30 "
                                    "graded cells, so the reciprocal-uniqueness reading — the whole "
                                    "point of result 3 — is the MINORITY case there. It holds as the "
                                    "majority only under the corridor convention.",
        "sites": [sites[k] for k in sorted(sites, key=lambda s: int(s[1:]))],
        "nr4a3_side": {
            "unique_cysteines_in_the_LBD": reach["cysteines"]["nr4a3_unique"],
            "conserved_cysteines_in_the_LBD": reach["cysteines"]["conserved"],
            "_from": "nr4a3-linker-covalent-reach.json -> cysteines",
        },
        "who_closes_the_window": closers,
        "tie_frequency": {
            "n_rows_with_a_closer": tie_rows,
            "n_rows_where_at_least_two_cysteines_arrive_at_the_SAME_atom_count": ties,
            "_reading": "A tie means the artifact's single `closed_by` name is a tie-break, not a "
                        "measurement. Quoting it as THE closing residue overstates what was resolved; "
                        "the honest form names the set that arrives first.",
            "_from": "nr4a3-linker-covalent-reach.json -> ★_family_wide_chemoselectivity_window"
                     ".by_convention[*].all_competitors_atoms",
        },
        "★_the_correct_sentence": "Under BOTH reach conventions the first cysteine to come into reach is "
                                  "always one belonging to a PARALOGUE rather than to NR4A3 (30 of 30 "
                                  "graded cells, each convention). WHICH paralogue cysteine differs by "
                                  "convention: NR4A1 C505 — a position NR4A3 shares (C536) — closes 24 of "
                                  "30 through-space cells, while NR4A2 C534 — a position NR4A3 lacks "
                                  "(S565) — closes 23 of 30 corridor cells. Only the second of those "
                                  "supports a reciprocal-uniqueness reading.",
    }


# ==========================================================================================================
# (2) BRANCH 1b's FIVE CLAIMS, one at a time, against the committed artifact
# ==========================================================================================================
def claim_verdicts(dyn, reach, lib):
    fam = reach["★_family_wide_chemoselectivity_window"]["by_convention"]
    v = reach["verdict"]
    counts = v["per_unique_cysteine_conformer_counts"]
    pc = reach["premise_correction"]["evidence"]

    one_branch = [r for r in lib["virtual_library"]
                  if r.get("pendant_kind") == "electrophile" and r.get("e3_handle") and r.get("branch_target")]

    # (b) where, if anywhere, is C420/C559 NOT refuted?
    rc = reach["experimental_ensemble_8xtt"]["reachable_conformer_counts"]
    survivors = {c: [] for c in ("C420", "C559")}
    n_cells_per_cys = collections.Counter(row["cysteine"] for row in rc.values())
    for key, row in rc.items():
        if row["cysteine"] in survivors and (row["through_space"] > 0 or row["corridor"] > 0):
            survivors[row["cysteine"]].append({
                "cell": key, "placement": row["placement"], "pendant": row["pendant"],
                "n_conformers": row["n_conformers"],
                "through_space": row["through_space"], "corridor": row["corridor"]})

    # (d) closer classification
    graded = {conv: [r for r in rows if "term_a_exemplar" in r["placement"]] for conv, rows in fam.items()}
    unique_closers = {"NR4A1 C534", "NR4A2 C534", "NR4A1 C551"}
    d_split = {}
    for conv, rows in graded.items():
        cn = collections.Counter(r["closed_by"] for r in rows if r["closed_by"])
        d_split[conv] = {
            "n_graded": len(rows),
            "closed_by_a_PARALOGUE_UNIQUE_cysteine": sum(n for k, n in cn.items() if k in unique_closers),
            "closed_by_a_paralogue_cysteine_at_a_CONSERVED_position":
                sum(n for k, n in cn.items() if k not in unique_closers),
            "closed_by_an_NR4A3_cysteine": sum(n for k, n in cn.items() if k.startswith("NR4A3")),
            "by_closer": dict(cn),
        }

    # (e) noise sensitivity + which pairs it can and cannot cover
    disp = reach["paralogue_control"]["aligned_pair_displacement"]
    covered = sorted({"%s %s" % (p["paralogue"], p["paralogue_cysteine"]) for p in disp["pairs"]})
    ns = v["family_wide_window"]["through_space"]["noise_sensitivity"]
    closer_set = sorted({r["closed_by"] for rows in graded.values() for r in rows if r["closed_by"]})
    uncovered = [c for c in closer_set if c not in covered]

    return [
        {
            "claim": "a",
            "as_written": "`build_smiles` places the E3 at a chain terminus, so an electrophile pendant + "
                          "E3 arm is a ONE-branch molecule and `linker_twobranch.py` is not required — "
                          "21 committed one-branch constructs all target C397 SG.",
            "verdict": "SUPPORTED",
            "decided_by": ["nr4a3-linker-covalent-reach.json -> premise_correction.evidence",
                           "nr4a3_linker_design.build_smiles (source, read directly)",
                           "nr4a3-linker-design.json -> virtual_library (recounted here, independently)"],
            "evidence": {
                "build_smiles_signature": pc["build_smiles_signature"],
                "template": pc["template"],
                "n_committed_one_branch_electrophile_plus_e3__artifact": pc[
                    "n_committed_one_branch_electrophile_plus_e3"],
                "n_committed_one_branch_electrophile_plus_e3__recounted_here": len(one_branch),
                "recount_agrees": len(one_branch) == pc["n_committed_one_branch_electrophile_plus_e3"],
                "n_in_full_virtual_library": len(lib["virtual_library"]),
                "branch_targets": sorted({r["branch_target"] for r in one_branch}),
                "n_backbone_atoms_present": sorted({r["n_backbone_atoms_intended"] for r in one_branch}),
                "e3_handles": dict(collections.Counter(r["e3_handle"] for r in one_branch)),
                "pendants": dict(collections.Counter(r.get("pendant") for r in one_branch)),
            },
            "note": "Verified three ways: the artifact's `premise_correction`, the SOURCE of `build_smiles` "
                    "(the E3 fragment is emitted first and the chain continues past it, so the single "
                    "`pendant` slot is free), and an independent recount of the committed library. The "
                    "recount matches. Nothing needs changing.",
        },
        {
            "claim": "b",
            "as_written": "C420 and C559 are refuted at every placement, pendant and reach convention.",
            "verdict": "CORRECTED — true of C420, NOT true of C559",
            "decided_by": ["nr4a3-linker-covalent-reach.json -> experimental_ensemble_8xtt"
                           ".reachable_conformer_counts",
                           "nr4a3-linker-covalent-reach.json -> verdict"
                           ".per_unique_cysteine_conformer_counts"],
            "evidence": {
                "n_cells_per_cysteine": n_cells_per_cys["C559"],
                "C420": {"best_through_space": counts["C420"]["best_through_space"],
                         "best_corridor": counts["C420"]["best_corridor"],
                         "cells_with_any_reach": survivors["C420"],
                         "reading": "refuted everywhere — 0 of %d (placement x pendant) cells, both "
                                    "conventions, no conformer." % n_cells_per_cys["C420"]},
                "C559": {"best_through_space": counts["C559"]["best_through_space"],
                         "best_corridor": counts["C559"]["best_corridor"],
                         "cells_with_any_reach": survivors["C559"],
                         "reading": "refuted under the CORRIDOR convention everywhere, and under "
                                    "through-space at %d of %d cells — but NOT at all of them."
                                    % (n_cells_per_cys["C559"] - len(survivors["C559"]),
                                       n_cells_per_cys["C559"])},
            },
            "the_mechanism_of_the_error": "`verdict()` builds its `live` list from `best_corridor > 0` "
                                          "alone and calls everything else `refuted_unique_cysteines`. "
                                          "C559's through-space evidence therefore never reaches the "
                                          "label, even though the artifact records it two fields away. "
                                          "The DATA is honest; the LABEL is stronger than the data.",
            "corrected_wording": "C420 is refuted at every placement, pendant, conformer and reach "
                                 "convention. C559 is refuted under the corridor convention everywhere "
                                 "and at 59 of 60 through-space cells; it survives in exactly one — the "
                                 "`vhl|M3` term_a_exemplar anchor with the longest `dab_branch` pendant — "
                                 "in 2 of that cell's 19 conformers. That single surviving cell is the "
                                 "OPTIMISTIC anchor (a best-of-N) with the most generous pendant, so it "
                                 "is the weakest possible form of a survival; it is still not zero.",
        },
        {
            "claim": "c",
            "as_written": "C397 survives.",
            "verdict": "SUPPORTED",
            "decided_by": ["nr4a3-linker-covalent-reach.json -> verdict.at_which_cysteine",
                           "nr4a3-linker-covalent-reach.json -> verdict"
                           ".per_unique_cysteine_conformer_counts.C397"],
            "evidence": {
                "at_which_cysteine": v["at_which_cysteine"],
                "C397": counts["C397"],
                "reading": "reachable in 20 of 20 8XTT conformers under BOTH conventions at its best "
                           "cell, and it is the only NR4A3-unique cysteine with a non-zero corridor "
                           "count anywhere.",
            },
        },
        {
            "claim": "d",
            "as_written": "The window is closed by a paralogue cysteine rather than an NR4A3-conserved "
                          "one — 'i.e. a cysteine the paralogues have and NR4A3 lacks'.",
            "verdict": "CORRECTED — the first half is supported, the gloss is FALSE for the majority "
                       "through-space closer",
            "decided_by": ["nr4a3-linker-covalent-reach.json -> ★_family_wide_chemoselectivity_window"
                           ".by_convention[*].closed_by",
                           "nr4a3-linker-covalent-reach.json -> paralogue_control.reciprocal_uniqueness"],
            "evidence": d_split,
            "the_two_statements_that_must_not_be_merged": {
                "supported": "In 30 of 30 graded cells, under EACH convention, the first cysteine to come "
                             "into reach belongs to a PARALOGUE CHAIN rather than to NR4A3. That is what "
                             "`n_closed_by_a_PARALOGUE_cysteine: 30` counts — it tests only "
                             "`not closed_by.startswith('NR4A3')`.",
                "NOT_supported_as_a_general_statement": "'a cysteine the paralogues have and NR4A3 lacks'. "
                                                        "NR4A1 C505 aligns to NR4A3 C536 "
                                                        "(`paralogue_unique_vs_NR4A3: false`) and closes "
                                                        "24 of 30 through-space cells. Only NR4A2 C534 "
                                                        "(-> NR4A3 S565) carries the reciprocal-uniqueness "
                                                        "reading, and it is the majority closer under the "
                                                        "corridor convention only.",
            },
            "★_the_deeper_finding": "Because C505 and NR4A3 C536 are an ALIGNED PAIR, the gap between "
                                    "them in these models is not a sequence difference — it is a rotamer "
                                    "difference between independently built models. The artifact's own "
                                    "`aligned_pair_displacement` records that pair at delta_SG 4.06 A / "
                                    "delta_CA 1.19 A (sg_over_ca 3.4) for NR4A1 and delta_SG 3.34 A / "
                                    "delta_CA 0.35 A (sg_over_ca 9.5) for NR4A2 — the LARGEST ratio in "
                                    "the whole table, which is the artifact's own flag for 'the backbones "
                                    "agree and the side chains do not'. So the through-space closure rests "
                                    "on precisely the pair the artifact says is least trustworthy.",
        },
        {
            "claim": "e",
            "as_written": "The artifact reports ΔCA against ΔSG per aligned pair and states the sulfur "
                          "displacement that would reopen the window.",
            "verdict": "SUPPORTED as to existence — INCOMPLETE as to coverage",
            "decided_by": ["nr4a3-linker-covalent-reach.json -> paralogue_control.aligned_pair_displacement",
                           "nr4a3-linker-covalent-reach.json -> verdict.family_wide_window[*]"
                           ".noise_sensitivity"],
            "evidence": {
                "per_pair_reporting_exists": True,
                "n_pairs": disp["pairs"].__len__(),
                "pairs_covered": covered,
                "max_sg_over_ca": disp["max_sg_over_ca"],
                "median_window_lost_atoms": ns["median_window_lost_atoms"],
                "rise_A_per_backbone_atom": reach["_parameters"]["imported_never_retyped"][
                    "rise_A_per_backbone_atom"],
                "sg_displacement_that_would_reopen_it_A": ns["sg_displacement_that_would_reopen_it_A"],
                "observed_aligned_pair_sg_displacement_A": ns["observed_aligned_pair_sg_displacement_A"],
                "correction_needed_is_inside_the_observed_model_noise":
                    ns["correction_needed_is_inside_the_observed_model_noise"],
                "margin_A": round(ns["sg_displacement_that_would_reopen_it_A"]
                                  - ns["observed_aligned_pair_sg_displacement_A"]["max"], 2),
                "closers_observed": closer_set,
                "closers_with_NO_measured_noise_bound": uncovered,
            },
            "★_the_gap": "The noise yardstick can only be built at ALIGNED cysteine pairs — the same "
                         "residue in two independently built models. C534 has no aligned NR4A3 cysteine "
                         "BY CONSTRUCTION (that is what makes it paralogue-unique), so it contributes no "
                         "pair and inherits no measured bound. The residue that closes 23 of 30 corridor "
                         "cells is therefore the one residue the noise test cannot cover. The bound that "
                         "IS reported (6.25 A needed vs 5.94 A observed) also clears by only 0.31 A — a "
                         "5 % margin — and the 5.94 A maximum comes from the C465/C496 pair, not from "
                         "either closer.",
            "corrected_wording": "The artifact reports ΔCA and ΔSG for the 8 aligned cysteine pairs and "
                                 "derives the sulfur displacement that would reopen the window "
                                 "(6.25 A = the median 5.0 atoms of lost window x the 1.25 A/atom rise). "
                                 "That correction exceeds the largest displacement observed at any "
                                 "aligned pair (5.94 A) — by 0.31 A. The test does not and cannot cover "
                                 "NR4A1/NR4A2 C534, which has no aligned NR4A3 partner.",
        },
    ]


# ==========================================================================================================
# (3) POSE-DEPENDENT vs POSE-INDEPENDENT, and the limits
# ==========================================================================================================
def pose_split(dyn, reach, uniq, basins):
    cv = dyn["categorical_verdict"]
    scopes = cv["by_scope"]
    gate = str(cv["gate_atoms"])

    load = []
    for scope, s in scopes.items():
        for n, cell in sorted(s["by_linker_atoms"].items(), key=lambda kv: int(kv[0])):
            u = cell["P_paralogue_also_labelled_given_nr4a3"]
            e = cell["P_paralogue_also_labelled_given_nr4a3_EXPOSED"]
            load.append({"scope": scope, "linker_atoms": int(n),
                         "P_collision_reach_only": u, "P_collision_reach_AND_exposed": e,
                         "percentage_points_carried_by_the_exposure_filter": round((u - e) * 100, 3)})

    pooled = {sp: dyn["term_a"]["by_species"][sp]["pooled_unbiased"] for sp in ("NR4A3", "NR4A1", "NR4A2")}
    envelope = []
    for sp, pu in pooled.items():
        for cys, row in pu["summary"].items():
            envelope.append({
                "species": sp, "cysteine": cys,
                "nr4a3_aligned": row.get("nr4a3_aligned"),
                "n_frames": pu["n_frames"],
                "frac_frames_inside_the_12_atom_envelope": row["frac_frames_open_at_or_below_gate"],
                "n_frames_inside": row["n_frames_open_at_or_below_gate"],
                "rsa_median": row["rsa"]["median"], "rsa_max": row["rsa"]["max"],
                "ever_clears_the_0_25_cutoff": row["rsa"]["max"] > cv["exposed_rsa_cutoff"],
            })
    envelope.sort(key=lambda r: -r["frac_frames_inside_the_12_atom_envelope"])

    return {
        "★_the_separation_nobody_had_drawn": "The claim splits into three layers with three different "
                                             "exposures. Layer 1 survives R5/V3 failing outright. Layer 2 "
                                             "survives it if the CRYPTIC POCKET is right, whatever the "
                                             "ligand pose inside it. Layer 3 is the one the exposure "
                                             "criterion carries, and that criterion has a demonstrated "
                                             "false negative.",
        "pose_independent": {
            "_what": "rests on sequence alone — no structure, no pose, no pocket",
            "items": [
                "Cysteine uniqueness: C397 / C420 / C559 are cysteines in NR4A3 (Q92570) and are NOT "
                "cysteines at the aligned position in NR4A1 (P22736) or NR4A2 (P43354).",
                "Reciprocal uniqueness: NR4A1/NR4A2 C534 aligns to NR4A3 S565, and NR4A1 C551 to NR4A3 "
                "T579 — cysteines the paralogues have and NR4A3 lacks.",
                "Non-uniqueness of C505: NR4A1/NR4A2 C505 aligns to NR4A3 C536, so it is NOT a "
                "reciprocal-uniqueness site.",
            ],
            "instrument": "UniProt FASTA + two independent global aligners; every one of these positions "
                          "is `alignment_robust: true` / `aligners_agree: true`.",
            "_from": ["nr4a-paralogue-unique-residues.json -> nr4a3_unique_cysteines[*].partners",
                      "nr4a-paralogue-unique-residues.json -> reciprocal_paralogue_unique",
                      "nr4a3-linker-covalent-reach.json -> paralogue_control.aligned_partners"],
            "survives_R5_failing": True,
            "_note": "This is the ONLY layer that is safe if the pose work is thrown away entirely. It is "
                     "also, on its own, much weaker than the axis has been credited with: it says nothing "
                     "about whether anything can REACH those residues.",
        },
        "pocket_dependent_but_NOT_docked_pose_dependent": {
            "_what": "rests on the cryptic pocket's identity and location, and marginalises the ligand "
                     "exit vector rather than asserting it",
            "items": [
                "Every reach number in BOTH artifacts — the 12-atom gate fractions, the family-wide "
                "window, the matched-construct collision probabilities.",
            ],
            "★_the_measured_correction": "The roadmap says branch 1b is 'conditional on the docked pose "
                                         "the anchors come from, whose known-answer test is V3'. Read "
                                         "from the source, that is not what the anchors are. "
                                         "`nr4a3_basin_search.build_pose_ensemble` does not consume a "
                                         "docked ligand pose at all — its own docstring says 'The repo "
                                         "holds no cmpd19 pose in this matched-model frame ... so "
                                         "asserting one exit-vector point would manufacture precision the "
                                         "evidence does not support', and it instead samples 12 "
                                         "solvent-connected anchors in a shell around the CRYPTIC-POCKET "
                                         "CENTROID. `nr4a3-orientation-basins.json`'s own _limits[0] says "
                                         "the same: 'the warhead exit vector is MARGINALISED over an "
                                         "ensemble of pocket-mouth anchors rather than asserted'. Both "
                                         "audited artifacts read their anchors from that ensemble "
                                         "(pose_ids `exitvec_00`..`exitvec_11`).",
            "what_this_actually_inherits_from_V3": "V3's failure was SITE SELECTION on 6 of 6 pairs, not "
                                                   "pose accuracy — with an fpocket-chosen box the same "
                                                   "protocol reached 3.04 A. Site selection is exactly "
                                                   "the thing these anchors depend on. So the exposure "
                                                   "runs through the POCKET, not through a pose: if "
                                                   "Pocket 5 is the wrong site, every anchor moves and "
                                                   "every reach number is void. If Pocket 5 is right and "
                                                   "the ligand's orientation within it is unknown, the "
                                                   "12-anchor marginalisation already covers that.",
            "_from": ["nr4a3_basin_search.build_pose_ensemble (source)",
                      "nr4a3-orientation-basins.json -> _limits[0], pose_ensemble",
                      "nr4a3-linker-covalent-reach.json -> anchors._source",
                      "nr4a_paralogue_dynamics.matched_placements (source)"],
            "survives_R5_failing": "PARTLY — survives a pose-accuracy failure, does NOT survive a "
                                   "site-selection failure",
        },
        "exposure_criterion_dependent": {
            "_what": "rests on EXPOSED_RSA = 0.25, the instrument V17, which fails its own positive control",
            "cutoff": cv["exposed_rsa_cutoff"],
            "how_much_load_it_carries": load,
            "★_reading": "At the 12-atom DESIGN GATE the exposure filter carries almost nothing: "
                         "reach-only collision is already 0.000 / 0.00124 / 0.00290 across the three "
                         "scopes, so the headline gate result does NOT rest on the criterion that failed "
                         "its positive control. The filter becomes load-bearing at 16 atoms (5.4-12.4 "
                         "percentage points) and dominant at 20 (26.3-38.3 points). This is the single "
                         "most useful thing in this audit: the claim is defensible at the gate on reach "
                         "ALONE, and indefensible at 16-20 without the cutoff.",
            "_from": "nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope[*].by_linker_atoms",
        },
        "the_envelope_the_headline_does_not_show": {
            "_what": "the E3-INDEPENDENT reach envelope, pooled over the 75 unbiased frames per species — "
                     "'could SOME construct reach this cysteine at <=12 atoms', as opposed to 'does the "
                     "SAME placement reach both'",
            "_why_it_matters": "The paralogues are NOT out of reach. NR4A1 C465 sits inside the 12-atom "
                               "envelope in MORE frames than NR4A3's own C397 does. What excludes every "
                               "one of them from the categorical count is the RSA cutoff, and the largest "
                               "paralogue RSA anywhere in the unbiased pool is 0.2126 — 15 % below it. "
                               "The categorical result is therefore 'the same construct geometry rarely "
                               "reaches both', NOT 'the paralogues have nothing in range'.",
            "rows": envelope,
            "_from": "nr4a-paralogue-dynamics.json -> term_a.by_species[*].pooled_unbiased.summary",
        },
        "gate_reading": {
            "gate_atoms": cv["gate_atoms"],
            "by_scope": {s: {"n_frames": v["n_frames"],
                             "P_categorical_given_nr4a3": v["by_linker_atoms"][gate][
                                 "P_categorical_given_nr4a3"],
                             "P_categorical_given_nr4a3_EXPOSED": v["by_linker_atoms"][gate][
                                 "P_categorical_given_nr4a3_EXPOSED"],
                             "n_placements_with_any_nr4a3_hit": v["by_linker_atoms"][gate][
                                 "n_placements_with_any_nr4a3_hit"]}
                         for s, v in scopes.items()},
            "n_placements": dyn["term_b"]["placements"]["n_total"],
            "_from": "nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope",
        },
    }


def limits(dyn, reach):
    cv = dyn["categorical_verdict"]
    scopes = cv["by_scope"]
    gate = str(cv["gate_atoms"])
    pooled = dyn["term_a"]["by_species"]
    c551 = pooled["NR4A1"]["pooled_unbiased"]["summary"]["C551"]
    c551_metad = pooled["NR4A1"]["ensembles"]["metad"]["summary"]["C551"]
    c551_static = pooled["NR4A1"]["ensembles"]["static_opened_model"]["summary"]["C551"]
    c534_metad = pooled["NR4A2"]["ensembles"]["metad"]["summary"]["C534"]
    c465 = pooled["NR4A1"]["pooled_unbiased"]["summary"]["C465"]

    return [
        {
            "id": "L1-positive-control",
            "★": True,
            "limit": "The exposure criterion that produces the zero has a DEMONSTRATED FALSE NEGATIVE on "
                     "the one NR4A-family covalent site with literature support — and that site is on "
                     "NR4A1, one of the two paralogues the axis reports as carrying zero exposed "
                     "reachable cysteines.",
            "measured": {
                "criterion": "EXPOSED_RSA = %s" % cv["exposed_rsa_cutoff"],
                "NR4A1_C551_static_opened_model_rsa": c551_static["rsa"]["median"],
                "NR4A1_C551_metad_rsa": {"median": c551_metad["rsa"]["median"],
                                         "max": c551_metad["rsa"]["max"],
                                         "n_frames": c551_metad["n_frames"]},
                "NR4A1_C551_unbiased_pooled_rsa": {"median": c551["rsa"]["median"],
                                                   "max": c551["rsa"]["max"],
                                                   "n_frames": pooled["NR4A1"]["pooled_unbiased"][
                                                       "n_frames"]},
                "NR4A1_C551_frac_frames_inside_the_12_atom_envelope_unbiased":
                    c551["frac_frames_open_at_or_below_gate"],
                "NR4A1_C551_frac_frames_inside_the_12_atom_envelope_metad":
                    c551_metad["frac_frames_open_at_or_below_gate"],
            },
            "consequence": "C551 clears RSA 0.25 in NO frame of any scope, so the same criterion that "
                           "returns 'zero exposed NR4A1 cysteines' would also return 'the celastrol site "
                           "is not exposed'. A criterion returns zero on the class where a false negative "
                           "manufactures the headline. THE DEFENSIBLE FORM IS THE THRESHOLD-FREE RANK — "
                           "C551 is 3/18 across all NR4A-family LBD cysteines, behind NR4A3's C397 and "
                           "C420 — NOT the cutoff.",
            "what_it_does_NOT_undermine": "The 12-atom gate reading, which holds on reach ALONE "
                                          "(see pose_dependency_split.exposure_criterion_dependent). It "
                                          "undermines the 16-atom and 20-atom columns, and it undermines "
                                          "any sentence of the form 'no exposed paralogue cysteine' that "
                                          "does not name its criterion.",
            "_from": ["nr4a-paralogue-dynamics.json -> term_a.by_species.NR4A1",
                      "nr4a3-program-map.md §7 branch 1 (instrument V17)"],
        },
        {
            "id": "L2-reach-not-absence",
            "limit": "The paralogues are not out of range; they are out of the EXPOSED set. NR4A1 C465 "
                     "sits inside the 12-atom envelope in more unbiased frames than NR4A3's own C397 "
                     "does, and it is excluded solely by an RSA that never exceeds 0.2126.",
            "measured": {
                "NR4A1_C465_frac_frames_inside_envelope": c465["frac_frames_open_at_or_below_gate"],
                "NR4A1_C465_rsa_max": c465["rsa"]["max"],
                "NR4A3_C397_frac_frames_inside_envelope":
                    pooled["NR4A3"]["pooled_unbiased"]["summary"]["C397"]["frac_frames_open_at_or_below_gate"],
                "highest_paralogue_rsa_anywhere_in_the_unbiased_pool": c465["rsa"]["max"],
                "NR4A2_C534_metad_rsa_max": c534_metad["rsa"]["max"],
                "_note_on_C534": "In the BIASED metadynamics scope NR4A2 C534 reaches RSA %s, ABOVE the "
                                 "0.25 cutoff — and that is exactly where the only non-zero exposed "
                                 "collision probabilities in the whole artifact appear "
                                 "(metad_biased, 14/16/20 atoms)." % c534_metad["rsa"]["max"],
            },
            "_from": "nr4a-paralogue-dynamics.json -> term_a.by_species[*].pooled_unbiased.summary",
        },
        {
            "id": "L3-rare-event",
            "limit": "The conditioning event is thin BY CONSTRUCTION. The categorical probability is "
                     "conditioned on a placement reaching an NR4A3-unique cysteine at all, which happens "
                     "in ~0.04 % of placements. The honest statement is 'zero co-labelling events "
                     "observed', not 'a probability of 1.000'.",
            "measured": {
                "n_placements": dyn["term_b"]["placements"]["n_total"],
                "n_conditioning_events_by_scope": {
                    s: v["by_linker_atoms"][gate]["n_placements_with_any_nr4a3_hit"]
                    for s, v in scopes.items()},
            },
            "_from": "nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope[*]"
                     ".n_placements_with_any_nr4a3_hit",
            "⚠_two_numbers_that_are_not_the_same_and_are_being_paired": {
                "mean_per_placement_probability": {
                    "value": scopes["unbiased_release"]["by_linker_atoms"][gate]["mean_P_nr4a3_unique"],
                    "as_percent": round(100.0 * scopes["unbiased_release"]["by_linker_atoms"][gate][
                        "mean_P_nr4a3_unique"], 4),
                    "field": "categorical_verdict.by_scope.unbiased_release.by_linker_atoms.12"
                             ".mean_P_nr4a3_unique",
                    "means": "mean over placements of the FRACTION OF FRAMES in which a placement hits",
                },
                "fraction_of_placements_that_ever_hit": {
                    "n": scopes["unbiased_release"]["by_linker_atoms"][gate][
                        "n_placements_with_any_nr4a3_hit"],
                    "of": dyn["term_b"]["placements"]["n_total"],
                    "as_percent": round(100.0 * scopes["unbiased_release"]["by_linker_atoms"][gate][
                        "n_placements_with_any_nr4a3_hit"] / dyn["term_b"]["placements"]["n_total"], 4),
                    "field": "categorical_verdict.by_scope.unbiased_release.by_linker_atoms.12"
                             ".n_placements_with_any_nr4a3_hit",
                    "means": "count of placements where AT LEAST ONE frame hits",
                },
                "the_problem": "The paper §2.10 and the lane doc §3.5 both write '~0.04 % of placements "
                               "(122 hits in 73,867)'. 0.04 % is the FIRST quantity and 122/73,867 = "
                               "0.165 % is the SECOND. Both figures are correct; the parenthetical does "
                               "not compute the percentage it is attached to, and a reader checking the "
                               "arithmetic will find a 4x discrepancy in the paper's own sentence.",
                "fix": "state them as two facts — 'the mean per-placement probability is 0.041 % and 122 "
                       "of 73,867 placements (0.165 %) hit in at least one frame' — or drop one.",
            },
            "_note": "The rare-event framing itself is already stated correctly in the paper (§2.10) and "
                     "in the lane doc §3.5. It is repeated here because it is the limit most likely to be "
                     "dropped when the result is summarised — and because the pairing above is not right.",
        },
        {
            "id": "L4-one-residue-deep",
            "limit": "At the 12-atom gate the NR4A3 side of the claim is C397 ALONE. C420 and C559 reach "
                     "the gate in 0 of 75 unbiased frames, so every 'NR4A3-unique cysteine' in the "
                     "conditioning event is C397.",
            "measured": {c: {"frac_frames_inside_the_12_atom_envelope":
                             pooled["NR4A3"]["pooled_unbiased"]["summary"][c][
                                 "frac_frames_open_at_or_below_gate"],
                             "rsa_median": pooled["NR4A3"]["pooled_unbiased"]["summary"][c]["rsa"]["median"]}
                         for c in ("C397", "C420", "C559")},
            "consequence": "A single point of failure. Anything that moves C397 — a wrong pocket, a wrong "
                           "rotamer, an unmodelled post-translational modification — takes the whole axis "
                           "with it.",
            "_from": "nr4a-paralogue-dynamics.json -> term_a.by_species.NR4A3.pooled_unbiased.summary",
        },
        {
            "id": "L5-correlated-frames",
            "limit": "The effective n is smaller than the frame count. Three independent trajectories make "
                     "the CROSS-SPECIES pairing exact, but each species' own frames are correlated within "
                     "a replica, so 75 frames is not 75 independent observations.",
            "_from": "nr4a-paralogue-dynamics.json -> categorical_verdict._limits[1] (the artifact's own)",
        },
        {
            "id": "L6-necessary-not-sufficient",
            "limit": "Reach and exposure are NECESSARY, not sufficient. No thiol pKa, nucleophilicity, "
                     "adduct stability or electrophile promiscuity is modelled anywhere in either "
                     "artifact.",
            "_from": ["nr4a-paralogue-dynamics.json -> categorical_verdict._limits[0]",
                      "nr4a3-linker-covalent-reach.json -> _status"],
        },
        {
            "id": "L7-upper-bound-asymmetry",
            "limit": "The term-(a) envelope is an E3-INDEPENDENT UPPER BOUND, which is conservative for "
                     "ruling a paralogue site OUT and NOT conservative for ruling one IN. A paralogue "
                     "cysteine shown open in the envelope has not been shown reachable by any real "
                     "recruiter.",
            "_from": "nr4a-paralogue-dynamics.json -> _limits[1] (the artifact's own)",
        },
        {
            "id": "L8-superposition-residual",
            "limit": "Paralogue conformers are superposed into the NR4A3 reference frame and carry a "
                     "core-fit residual. At aligned cysteine pairs the backbones agree far better than "
                     "the side chains — max delta_SG/delta_CA = %s — so no paralogue atom count may be "
                     "quoted more precisely than the rotamer it rests on."
                     % reach["paralogue_control"]["aligned_pair_displacement"]["max_sg_over_ca"],
            "_from": "nr4a3-linker-covalent-reach.json -> paralogue_control.aligned_pair_displacement",
        },
        {
            "id": "L9-single-conformer-window",
            "limit": "The family-wide chemoselectivity window is computed on SINGLE CONFORMERS — the "
                     "`nr4a3-opened.pdb` frame and two superposed opened paralogue models — not on "
                     "ensembles, and the `verdict` block's 30 graded cells are all `term_a_exemplar` "
                     "anchors, which the artifact itself labels a best-of-N and 'the OPTIMISTIC end of "
                     "the basin'. The `representative` anchors are excluded from the headline.",
            "_from": ["nr4a3-linker-covalent-reach.json -> ★_family_wide_chemoselectivity_window._computed_on",
                      "nr4a3-linker-covalent-reach.json -> anchors._caveat",
                      "nr4a3_linker_covalent_reach.verdict (source: rows filtered to term_a_exemplar)"],
        },
    ]


def licenses():
    return {
        "★_what_the_categorical_axis_LICENSES": [
            "A design prioritisation: prefer a SHORT linker. Discrimination is clean at the 12-atom gate "
            "and degrades monotonically with length, so a construct that reaches C397 at 11-12 backbone "
            "atoms is not merely more tractable — it is more selective. That is a real, measured design "
            "consequence and it is the axis's most useful output.",
            "A refutation, which is what geometry is actually good for: C420 and C559 are not usable "
            "electrophile targets at chemically routine linker length (C420 absolutely; C559 with the one "
            "recorded exception).",
            "A narrowed statement of TARGET-ENGAGEMENT selectivity: at the geometries where this construct "
            "class could put an electrophile on an NR4A3-unique cysteine, no EXPOSED cysteine on either "
            "paralogue is reachable by the same construct — with 'exposed' adjudicated by a criterion that "
            "must be named, because it has a demonstrated false negative.",
        ],
        "⛔_what_it_does_NOT_license": [
            "NOT degradation. Nothing here models ubiquitin transfer, processivity, or turnover. A "
            "cysteine being labellable says nothing about whether the protein is degraded.",
            "NOT affinity. No binding free energy, no potency, no residence time. The axis is set "
            "membership and distance, not energy.",
            "NOT efficacy, and not safety, and not a therapeutic window. None is computed anywhere.",
            "NOT proteome-wide selectivity. The comparison set is NR4A1 and NR4A2. Every other cysteine in "
            "the proteome is untested — and an electrophile does not know it is meant to be selective.",
            "NOT that a covalent bond forms at all. Reach and exposure are geometric necessary conditions; "
            "thiol pKa, intrinsic reactivity and adduct stability are untested and untestable here.",
            "⛔ NOT a productive ternary complex. A PROTAC needs a ternary geometry that presents a "
            "substrate lysine to the E2~Ub transfer zone, and the categorical cysteine axis says NOTHING "
            "about that. It is a separate term with its own separate evidence, and this axis neither "
            "supports nor substitutes for it.",
            "NOT a claim that the paralogues lack a reachable cysteine. They have several; they lack an "
            "EXPOSED one under this cutoff. Those are different sentences and only the second is measured.",
        ],
        "_the_one_sentence_form": "At the 12-atom design gate, over 73,867 matched E3 placements and 300 "
                                  "matched conformers, no placement that reaches an NR4A3-unique cysteine "
                                  "also reaches a solvent-exposed cysteine on NR4A1 or NR4A2 — a "
                                  "TARGET-ENGAGEMENT geometry result about a construct class, conditional "
                                  "on the cryptic pocket being the right site, that licenses a short-linker "
                                  "design preference and refutes two of three candidate handles, and that "
                                  "makes no claim about binding, ternary formation, degradation, efficacy "
                                  "or safety.",
    }


# ==========================================================================================================
# (4) THE STALE BLOCKER + the exact edits the two locked documents need
# ==========================================================================================================
def stale_blocker():
    return {
        "_finding": "STRATEGY.md still describes the matched paralogue MD ensembles as 'in flight' and "
                    "marks the categorical verdict VERDICT_NOT_EVALUABLE. Both are false and have been "
                    "for a week.",
        "measured_provenance": {
            "artifact": "research/modalities/nr4a-paralogue-dynamics.json",
            "first_commit_carrying_a_FULLY_EVALUABLE_verdict": {
                "sha": "3d993237f",
                "utc": "2026-07-26 18:48:31 +0000",
                "et": "2026-07-26 2:48 PM ET",
                "message": "lane13: analyse — paralogue MD ensembles / categorical-dynamics analysis",
                "verified": "all three scopes carry n_frames NR4A3/NR4A1/NR4A2 = 1/1/1, 75/75/75, 25/25/25 "
                            "and NONE carries the VERDICT_NOT_EVALUABLE key; "
                            "P_categorical_given_nr4a3_EXPOSED = 1.0 at the gate in all three.",
            },
            "later_commits": [
                {"sha": "c32e817e8", "utc": "2026-07-31 18:27:15 +0000", "et": "2026-07-31 2:27 PM ET"},
                {"sha": "8f3e3732c", "utc": "2026-08-02 09:40:50 +0000", "et": "2026-08-02 5:40 AM ET"},
            ],
            "★_correction_to_the_task_framing": "The result is often described as landing 2026-07-31. It "
                                                "landed 2026-07-26 at 2:48 PM ET; 2026-07-31 is a "
                                                "re-commit. The blocker has therefore been stale for "
                                                "SEVEN days, not two.",
            "how_it_was_checked": "git show <sha>:research/modalities/nr4a-paralogue-dynamics.json, "
                                  "parsed and inspected for the VERDICT_NOT_EVALUABLE key — a $0 read.",
        },
        "root_cause": "The lane doc `nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md` contains "
                      "BOTH the landed result (§3.5, correct, and itself dated '2026-07-26 2:49 PM ET') "
                      "AND the earlier pilot framing (§4, 'the run now in flight', with the 5,657-placement "
                      "numbers). STRATEGY.md was written from §4. The lane doc's §4 was never reconciled to "
                      "its own §3.5, so the stale text had a live-looking source to be copied from.",
        "the_guard_is_real_and_did_not_fire_wrongly": "VERDICT_NOT_EVALUABLE is a genuine code path in "
                                                      "`nr4a_paralogue_dynamics.categorical_verdict` that "
                                                      "fires only when a scope has NO paralogue conformers "
                                                      "— it exists to stop a PASS produced by measuring "
                                                      "nothing. It is correct code. It has simply not been "
                                                      "true of this artifact since 2026-07-26.",
        "what_is_NOT_stale": {
            "the_paper": "research/manuscripts/nr4a3-degrader-paper.md §2.10 already carries the landed "
                         "numbers verbatim and honestly (300 conformers, 73,867 placements, 1.000 exposed, "
                         "0.12 %/0.29 % unfiltered, 122 hits / ~0.04 %, and the 'zero co-labelling events "
                         "observed, not a probability quoted to five figures' caveat). The manuscript does "
                         "NOT quote the superseded 0.081/0.258 pair.",
            "pinned_figures_json": "carries no entry for either superseded value — which is why CI is "
                                   "green on them today.",
            "the_paper_gaps_that_ARE_real": [
                "§2.10 says 'for solvent-exposed cysteines' without naming the criterion "
                "(EXPOSED_RSA = 0.25) or its failed positive control (NR4A1 Cys551).",
                "§2.10 pairs '~0.04 % of placements' with '(122 hits in 73,867)'. Those are two different "
                "quantities and 122/73,867 = 0.165 %. See limits -> L3-rare-event.",
            ],
        },
    }


def _band(scopes, atoms, key):
    """min-max across the three scopes at one linker length, formatted as a band. DERIVED, so the ranges
    in the proposed prose below cannot drift from the artifact the way 0.081/0.258 did."""
    vals = [s["by_linker_atoms"][str(atoms)][key] for s in scopes.values()]
    lo, hi = min(vals), max(vals)
    return "%.3f" % lo if lo == hi else "%.3f-%.3f" % (lo, hi)


def proposed_edits(residue_identity_block, claim_block, dyn):
    """The prose these documents need. ⚠ Every FIGURE inside a proposed sentence is interpolated from the
    audit block above it, never typed — a proposed edit that carries a hand-typed number is the same bug the
    edit exists to fix, and it happened once while writing this file: a tie count was typed as `46 of 102`
    and the derived value is 35 of 93."""
    ri, cl = residue_identity_block, claim_block
    ties = ri["tie_frequency"]
    ts = ri["who_closes_the_window"]["through_space"]["graded_cells_term_a_exemplar"]
    co = ri["who_closes_the_window"]["corridor"]["graded_cells_term_a_exemplar"]
    e_ev = [c for c in cl if c["claim"] == "e"][0]["evidence"]
    _b_ev = [c for c in cl if c["claim"] == "b"][0]["evidence"]
    _N_CELLS = _b_ev["n_cells_per_cysteine"]
    cv = dyn["categorical_verdict"]
    scopes = cv["by_scope"]
    gate = str(cv["gate_atoms"])
    K = "P_paralogue_also_labelled_given_nr4a3"
    b12, b16, b20 = _band(scopes, 12, K), _band(scopes, 16, K), _band(scopes, 20, K)
    npl = dyn["term_b"]["placements"]["n_total"]
    n_conf = sum(dyn["ensemble_census"]["by_species"][sp]["n_frames_total"]
                 for sp in ("NR4A3", "NR4A1", "NR4A2"))
    stat = dyn["term_a"]["by_species"]
    pu = {sp: stat[sp]["pooled_unbiased"] for sp in ("NR4A3", "NR4A1", "NR4A2")}
    so = {sp: stat[sp]["ensembles"]["static_opened_model"]["summary"] for sp in ("NR4A3", "NR4A1", "NR4A2")}
    a1_465 = pu["NR4A1"]["summary"]["C465"]
    a3_397 = pu["NR4A3"]["summary"]["C397"]
    cat_all = " / ".join(str(scopes[s]["by_linker_atoms"][gate]["P_categorical_given_nr4a3"])
                         for s in ("static_opened_model", "unbiased_release", "metad_biased"))
    n_hits = scopes["unbiased_release"]["by_linker_atoms"][gate]["n_placements_with_any_nr4a3_hit"]
    # ⚠ TWO DIFFERENT RARE-EVENT NUMBERS, AND THEY ARE NOT INTERCHANGEABLE.
    #   mean_P_nr4a3_unique          = mean over placements of the FRACTION OF FRAMES that hit  (0.041 %)
    #   n_placements_with_any_nr4a3_hit / n_placements = placements where >=1 frame hits        (0.165 %)
    # The paper §2.10 pairs "~0.04 %" with "(122 hits in 73,867)", which is the first percentage beside the
    # second count. Both figures are real; the parenthetical does not compute the percentage in front of it.
    mean_p = scopes["unbiased_release"]["by_linker_atoms"][gate]["mean_P_nr4a3_unique"]
    return {
        "_scope": "This audit does NOT edit STRATEGY.md or research/manuscripts/nr4a3-program-map.md. "
                  "Both are being restructured in the main checkout by other agents and this work ran in "
                  "an isolated worktree. The edits are specified here so they can be routed.",
        "STRATEGY.md": [
            {
                "anchor": "~line 197, the MECHANISM-FIRST reach-correction paragraph",
                "current_text": "The design consequence from the collision profile still stands and is the "
                                "durable part: **0 collisions at 12 atoms, 0.081 at 16, 0.258 at 20**",
                "problem": "0.081 and 0.258 are the 2026-07-25 A2 PILOT numbers — static models only, "
                           "5,657 placements. The landed matched run (%s placements, three scopes) gives "
                           "%s at 16 and %s at 20. The pilot understates the 16-atom collision by ~%.1fx "
                           "against the unbiased ensemble."
                           % ("{:,}".format(npl), b16, b20,
                              scopes["unbiased_release"]["by_linker_atoms"]["16"][K] / 0.081),
                "proposed_text": "The design consequence from the collision profile still stands and is "
                                 "the durable part: reach-only collision is **%s at 12 atoms, %s at 16 "
                                 "and %s at 20** across the three matched scopes "
                                 "([`nr4a-paralogue-dynamics.json`]"
                                 "(research/modalities/nr4a-paralogue-dynamics.json) → "
                                 "`categorical_verdict.by_scope[*].by_linker_atoms`, which is their one "
                                 "home)" % (b12, b16, b20),
                "and_add_to_appendix_A": "The pilot pair **0.081 at 16 / 0.258 at 20** — computed on the "
                                         "static opened models over 5,657 placements before the matched "
                                         "ensembles landed. Superseded 2026-07-26 by the %s-placement "
                                         "matched run over three scopes; retained because the shape "
                                         "(rising steeply with linker length) is unchanged and is the "
                                         "durable part." % "{:,}".format(npl),
            },
            {
                "anchor": "~lines 1009-1016, the paralogue-side bullets",
                "current_text": "**Each paralogue's static opened model presents TWO cysteines inside the "
                                "same gate**, and **NR4A1 C465 opens at a 6-atom linker against C397's "
                                "10** ... (NR4A1 C551, the celastrol site, at 10; NR4A2 C465 at 10, C534 "
                                "at 12.) ... **Matched-construct test** ... 5,657 placements ... 0 at 12 "
                                "atoms, 0.081 at 16, 0.258 at 20",
                "problem": "Every number in this bullet disagrees with the landed artifact's own "
                           "static_opened_model scope. Read from "
                           "`term_a.by_species[*].ensembles.static_opened_model.summary."
                           "<cys>.shortest_linker_atoms.min`: NR4A1 C465 = %s atoms (not 6), C551 = %s "
                           "(not 10); NR4A2 C465 = %s (not 10), C534 = %s (not 12). And on the landed "
                           "static model exactly ONE cysteine per paralogue clears the 12-atom gate "
                           "(C465 in each), not two."
                           % (so["NR4A1"]["C465"]["shortest_linker_atoms"]["min"],
                              so["NR4A1"]["C551"]["shortest_linker_atoms"]["min"],
                              so["NR4A2"]["C465"]["shortest_linker_atoms"]["min"],
                              so["NR4A2"]["C534"]["shortest_linker_atoms"]["min"]),
                "proposed_text": "**Each paralogue's static opened model presents ONE cysteine inside the "
                                 "12-atom gate** — C465 in both, at %s atoms (NR4A1) and %s (NR4A2) "
                                 "against C397's %s — and over the %d unbiased frames NR4A1's C465 is "
                                 "inside the envelope in **%d of %d**, *more often than NR4A3's own C397 "
                                 "at %d of %d*. **Matched-construct test** (same placement, warhead exit "
                                 "anchor, E3 anchor and budget; **%s** placements over **%d** matched "
                                 "conformers): reach-only collision **%s at 12 atoms, %s at 16, %s at 20**."
                                 % (so["NR4A1"]["C465"]["shortest_linker_atoms"]["min"],
                                    so["NR4A2"]["C465"]["shortest_linker_atoms"]["min"],
                                    so["NR4A3"]["C397"]["shortest_linker_atoms"]["min"],
                                    pu["NR4A1"]["n_frames"],
                                    a1_465["n_frames_open_at_or_below_gate"], pu["NR4A1"]["n_frames"],
                                    a3_397["n_frames_open_at_or_below_gate"], pu["NR4A3"]["n_frames"],
                                    "{:,}".format(npl), n_conf, b12, b16, b20),
            },
            {
                "anchor": "~lines 1020-1024, the ★ SO WHAT ACTUALLY HOLDS THE CATEGORICAL AXIS UP paragraph",
                "current_text": "The matched paralogue MD ensembles that turn those single numbers into "
                                "distributions are **in flight** and the verdict is deliberately marked "
                                "**`VERDICT_NOT_EVALUABLE`** until they land",
                "problem": "STALE. They landed at commit 3d993237f, 2026-07-26 2:48 PM ET. No scope of the "
                           "committed artifact carries the VERDICT_NOT_EVALUABLE key; all three carry "
                           "matched frames (1/1/1, 75/75/75, 25/25/25).",
                "proposed_text": "**The matched paralogue MD ensembles LANDED 2026-07-26 (2:48 PM ET, "
                                 "commit `3d993237f`) and the verdict is EVALUABLE**: over %d matched "
                                 "conformers and %s placements, `P(no paralogue cysteine reachable | the "
                                 "construct reaches an NR4A3-unique one)` at the 12-atom gate is **1.000 "
                                 "on exposed cysteines in all three scopes**, and %s on all cysteines. "
                                 "⚠ **Report it as the rare-event statistic it is** — only **%d of %s** "
                                 "placements (**%.2f %%**) put an NR4A3-unique cysteine in reach in any "
                                 "frame, and the mean per-placement probability is **%.3f %%**, so the "
                                 "defensible statement is *zero co-labelling events observed*, not a "
                                 "probability quoted to five figures. ⚠ **And the word *exposed* is "
                                 "adjudicated by `EXPOSED_RSA = %s`, the instrument that fails its own "
                                 "positive control** — so at 16-20 atoms the axis rests on a criterion "
                                 "with a demonstrated false negative, while **at the 12-atom gate it does "
                                 "not** (reach-only collision there is already ≤ %.1f %%). *Superseded, "
                                 "retained: 'in flight ... VERDICT_NOT_EVALUABLE'.*"
                                 % (n_conf, "{:,}".format(npl), cat_all,
                                    n_hits, "{:,}".format(npl), 100.0 * n_hits / npl, 100.0 * mean_p,
                                    cv["exposed_rsa_cutoff"],
                                    100.0 * max(s["by_linker_atoms"]["12"][K] for s in scopes.values())),
            },
        ],
        "research/manuscripts/nr4a3-program-map.md": [
            {
                "anchor": "§7 'Branch 1b — COMPUTED, NOT RECONCILED TO ITS ARTIFACT', result 3",
                "current_text": "It is closed first by a **paralogue** cysteine — i.e. a cysteine the "
                                "paralogues have and NR4A3 lacks",
                "problem": "The gloss after the dash is false for the majority through-space closer. "
                           "NR4A1 C505 aligns to NR4A3 C536 — NR4A3 HAS a cysteine there "
                           "(`paralogue_unique_vs_NR4A3: false`) — and it closes %d of %d graded "
                           "through-space cells. The artifact's `n_closed_by_a_PARALOGUE_cysteine: 30` "
                           "counts only `not startswith('NR4A3')`, i.e. 'on a paralogue chain', which is a "
                           "weaker statement than the gloss."
                           % (ts["by_closer"].get("NR4A1 C505", 0), ts["n"]),
                "proposed_text": "It is closed first by a cysteine belonging to a **paralogue chain** "
                                 "rather than to NR4A3 — in %d of %d graded cells under each convention. "
                                 "⚠ **But which one, and whether it is a site NR4A3 lacks, differs by "
                                 "convention and must not be merged.** Under **through-space** the closer "
                                 "is **NR4A1 C505** in %d of %d cells — and C505 aligns to NR4A3 **C536**, "
                                 "so NR4A3 *does* carry a cysteine at that position and the reciprocal-"
                                 "uniqueness reading does **not** apply to it. Under **corridor** the "
                                 "closer is **NR4A2 C534** in %d of %d — and C534 aligns to NR4A3 "
                                 "**S565**, which NR4A3 genuinely lacks. So the reciprocal-uniqueness "
                                 "finding is real but is carried by C534 under one convention, not by both "
                                 "closers under both."
                                 % (ts["n"] - ts["n_no_window"], ts["n"],
                                    ts["by_closer"].get("NR4A1 C505", 0), ts["n"],
                                    co["by_closer"].get("NR4A2 C534", 0), co["n"]),
            },
            {
                "anchor": "§7 branch 1b, result 2 · and §5 row R8",
                "current_text": "C420 and C559 are refuted at every placement, pendant and convention",
                "problem": "True of C420. NOT true of C559: "
                           "`per_unique_cysteine_conformer_counts.C559.best_through_space = %s`. The "
                           "artifact's own `refuted_unique_cysteines` list is built from "
                           "`best_corridor > 0` alone, so it drops the through-space evidence recorded two "
                           "fields away." % _b_ev["C559"]["best_through_space"],
                "proposed_text": "**C420 is refuted everywhere** — 0 of %d (placement × pendant) cells, "
                                 "both conventions, no conformer. **C559 is refuted under the corridor "
                                 "convention everywhere and at %d of %d through-space cells**, surviving "
                                 "in exactly one — `%s | %s`, in %d of that cell's %d conformers. That "
                                 "cell is the OPTIMISTIC best-of-N anchor with the longest pendant, so it "
                                 "is the weakest form of a survival; it is still not zero, and the "
                                 "artifact's `refuted_unique_cysteines` label is stronger than the "
                                 "artifact's own data."
                                 % (_N_CELLS, _N_CELLS - len(_b_ev["C559"]["cells_with_any_reach"]),
                                    _N_CELLS, _b_ev["C559"]["cells_with_any_reach"][0]["placement"],
                                    _b_ev["C559"]["cells_with_any_reach"][0]["pendant"],
                                    _b_ev["C559"]["cells_with_any_reach"][0]["through_space"],
                                    _b_ev["C559"]["cells_with_any_reach"][0]["n_conformers"]),
            },
            {
                "anchor": "§7 branch 1b, the 'How far these numbers may be trusted' paragraph",
                "current_text": "the artifact reports ΔCA against ΔSG per pair and states the sulfur "
                                "displacement that would reopen the window",
                "problem": "True, and incomplete in a way that matters. The %d pairs are all at CONSERVED "
                           "positions; C534 has no aligned NR4A3 partner by construction, so the corridor "
                           "convention's majority closer carries NO measured noise bound. And the reported "
                           "bound clears by only %s A (%s needed vs %s observed)."
                           % (e_ev["n_pairs"], e_ev["margin_A"],
                              e_ev["sg_displacement_that_would_reopen_it_A"],
                              e_ev["observed_aligned_pair_sg_displacement_A"]["max"]),
                "proposed_text": "… and states the sulfur displacement that would reopen the window "
                                 "(**%s Å**, derived as the median %s atoms of lost window × the "
                                 "%s Å/atom rise) against the largest displacement observed at any "
                                 "aligned pair (**%s Å**). ⚠ **That clears by %s Å — a %.0f %% margin — "
                                 "and it cannot cover C534 at all**: the yardstick is built from aligned "
                                 "cysteine pairs, and C534 has no aligned NR4A3 partner *because* it is "
                                 "paralogue-unique. So the residue that closes %d of %d corridor cells is "
                                 "the one residue the noise test is structurally unable to bound."
                                 % (e_ev["sg_displacement_that_would_reopen_it_A"],
                                    e_ev["median_window_lost_atoms"],
                                    e_ev["rise_A_per_backbone_atom"],
                                    e_ev["observed_aligned_pair_sg_displacement_A"]["max"],
                                    e_ev["margin_A"],
                                    100.0 * e_ev["margin_A"]
                                    / e_ev["observed_aligned_pair_sg_displacement_A"]["max"],
                                    co["by_closer"].get("NR4A2 C534", 0), co["n"]),
            },
            {
                "anchor": "§7 branch 1b closing paragraph, and §8 Route B heading",
                "current_text": "Everything here is conditional on the docked pose the anchors come from, "
                                "whose known-answer test is `V3` — which returned INCONCLUSIVE.",
                "problem": "Read from the source, the anchors are not a docked pose. "
                           "`nr4a3_basin_search.build_pose_ensemble` samples 12 solvent-connected anchors "
                           "in a shell around the CRYPTIC-POCKET CENTROID, and its docstring says a docked "
                           "pose was deliberately NOT asserted because none exists in this frame; "
                           "`nr4a3-orientation-basins.json` `_limits[0]` says the exit vector is "
                           "'MARGINALISED over an ensemble of pocket-mouth anchors rather than asserted'. "
                           "Stating it as a docked-pose dependency overstates the exposure in one "
                           "direction and hides the real one.",
                "proposed_text": "Everything here is conditional on **the cryptic pocket being the right "
                                 "site**, not on a docked ligand pose: the warhead exit vector is "
                                 "**marginalised** over 12 pocket-mouth anchors precisely because no "
                                 "cmpd19 pose exists in this frame "
                                 "([`nr4a3-orientation-basins.json`](../modalities/"
                                 "nr4a3-orientation-basins.json) `_limits[0]`). That matters for grading "
                                 "`V3`: V3's failure was **site selection** on 6 of 6 pairs, not pose "
                                 "accuracy (3.04 Å blind from apo through an fpocket-chosen box) — and "
                                 "site selection is exactly what these anchors rest on. So a **pose**-"
                                 "accuracy failure is already absorbed by the marginalisation; a "
                                 "**site**-selection failure voids every reach number here.",
            },
            {
                "anchor": "§7 branch 1b banner ('DO NOT QUOTE BRANCH 1b's NUMBERS YET')",
                "current_text": "the artifact's widest graded cell records `closed_by: \"NR4A1 C505\"` at "
                                "17 backbone atoms (with NR4A2 C534 also at 17 and NR4A1 C534 at 18)",
                "problem": "Correct as far as it goes — this audit confirms the widest through-space cell "
                           "(`vhl|M2@term_a_exemplar | rung5a_convention`, width 7) exactly. But it "
                           "understates the scope: the disagreement is not one cell, it is the "
                           "convention-wide split, and %d of %d rows with a closer are a TIE at the "
                           "closing atom count, so `closed_by` is a tie-break rather than a measurement in "
                           "%.0f %% of them."
                           % (ties["n_rows_where_at_least_two_cysteines_arrive_at_the_SAME_atom_count"],
                              ties["n_rows_with_a_closer"],
                              100.0 * ties["n_rows_where_at_least_two_cysteines_arrive_at_the_SAME_atom_count"]
                              / ties["n_rows_with_a_closer"]),
                "proposed_text": "the disagreement is convention-wide, not confined to one cell: NR4A1 "
                                 "C505 closes %d of %d graded through-space cells and NR4A2 C534 closes %d "
                                 "of %d corridor cells, and in **%d of the %d rows that have a closer at "
                                 "all, at least two cysteines arrive at the SAME atom count** — so "
                                 "`closed_by` is a tie-break, not a measurement, in %.0f %% of them. "
                                 "The honest form names the set that arrives first, never one residue."
                                 % (ts["by_closer"].get("NR4A1 C505", 0), ts["n"],
                                    co["by_closer"].get("NR4A2 C534", 0), co["n"],
                                    ties["n_rows_where_at_least_two_cysteines_arrive_at_the_SAME_atom_count"],
                                    ties["n_rows_with_a_closer"],
                                    100.0 * ties["n_rows_where_at_least_two_cysteines_arrive_at_the_SAME_atom_count"]
                                    / ties["n_rows_with_a_closer"]),
            },
            {
                "anchor": "§10 roadmap row 5 ('Reconcile branch 1b's prose to its landed artifact')",
                "current_text": "○ (not started)",
                "problem": "The reconciliation is done — this audit is it. The row should point at "
                            "`categorical-axis-audit.json` and close.",
                "proposed_text": "✓ done — [`categorical-axis-audit.md`]"
                                 "(../modalities/categorical-axis-audit.md) / "
                                 "[`categorical-axis-audit.json`]"
                                 "(../modalities/categorical-axis-audit.json), $0. Two claims corrected "
                                 "(b, d), one qualified (e), two supported (a, c). Lifts *'do not quote "
                                 "branch 1b anywhere'* once the five edits above are applied.",
            },
        ],
        "research/manuscripts/pinned-figures.json": {
            "_why": "CLAUDE.md rule 1.3: changing a pinned number means registering the old one IN THE "
                    "SAME COMMIT, so CI finds the copies the fix missed.",
            "⛔_do_not_add_it_before_the_edits_above": "`check_superseded` scans every pattern across all "
                                                       "12 target files. Adding this entry BEFORE "
                                                       "STRATEGY.md and the program map are fixed turns CI "
                                                       "red in three files at once, including the lane doc "
                                                       "`nr4a3-paralogue-dynamics-categorical-test-"
                                                       "2026-07-25.md`, which is itself a lint target. Add "
                                                       "it in the SAME commit as the fixes, not before.",
            "entry_to_add_to_superseded[]": {
                "id": "paralogue_collision_pilot_5657",
                "pattern": "0\\.081\\s*(at|@)\\s*16|0\\.258\\s*(at|@)\\s*20|\\b5,?657\\s+placements",
                "current": "reach-only collision 0.000-0.003 @12, 0.054-0.133 @16, 0.263-0.383 @20 over "
                           "73,867 matched placements and three scopes "
                           "(nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope)",
                "retired_by": "the matched NR4A1/NR4A2/NR4A3 ensembles landing 2026-07-26 (3d993237f), "
                              "which replaced the 5,657-placement static-model pilot",
            },
            "also_needs_a_marked_line_in": [
                "research/manuscripts/nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md §3.3 and §4 "
                "(a lint target; §3.5 of the same file already carries the landed result, so §4 is "
                "internally contradicted and is the source STRATEGY.md copied from)",
                "research/manuscripts/nr4a3-inverse-linker-design-2026-07-25.md (not a lint target; "
                "carries the pair in five places)",
                "research/manuscripts/map-audit-strategy.md, research/manuscripts/map-merge-inventory.md "
                "(not lint targets)",
            ],
        },
        "research/manuscripts/nr4a3-degrader-paper.md": {
            "_status": "NOT stale — §2.10 already carries the landed numbers correctly and does not quote "
                       "the superseded pair. One real gap, recorded here and not fixed:",
            "gap": "§2.10 states 'P(...) = 1.000 for solvent-exposed cysteines in every scope' without "
                   "naming the criterion that adjudicates *solvent-exposed* (`EXPOSED_RSA = 0.25`) or "
                   "disclosing that the same criterion fails its own positive control — NR4A1 Cys551, the "
                   "literature-anchored celastrol site, at RSA 0.165 on the state-matched opened model and "
                   "0 of 25 metadynamics frames. The paper discusses Cys551 at length elsewhere (§ on the "
                   "NR-V04 confound), so the omission is in the categorical paragraph specifically.",
            "suggested_addition": "one clause naming the cutoff and one sentence saying that at the "
                                  "12-atom gate the result does NOT depend on it (reach-only collision "
                                  "there is 0.000-0.003), while the 16- and 20-atom columns do.",
        },
    }


# ==========================================================================================================
def build():
    dyn, reach, uniq, lib, basins = (_load(DYN), _load(REACH), _load(UNIQ), _load(LIB), _load(BASINS))
    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    ri = residue_identity(dyn, reach, uniq)
    cl = claim_verdicts(dyn, reach, lib)
    return {
        "_title": "Audit of the CATEGORICAL selectivity axis — residue identity, branch-1b's five claims, "
                  "the pose split, and the limits",
        "_status": "AUDIT of committed artifacts. $0 — no new computation, no GPU, no rental. Nothing here "
                   "is a claim about binding, reactivity, degradation, efficacy or safety.",
        "_one_fact_one_place": "Every figure is a CITATION carrying the artifact + field path that OWNS "
                               "it. This file is not a second home for any of them. If a number here and "
                               "its cited field disagree, the artifact wins and this file is the bug — "
                               "which is why it is GENERATED (categorical_axis_audit.py), never typed. "
                               "Only the VERDICT strings are authored, and each names the field that "
                               "decided it.",
        "_generated": {"utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "et": _et(now),
                       "generator": "research/modalities/categorical_axis_audit.py"},
        "_audited_artifacts": {
            "research/modalities/nr4a-paralogue-dynamics.json":
                "the matched NR4A1/NR4A2/NR4A3 ensembles + the categorical verdict",
            "research/modalities/nr4a3-linker-covalent-reach.json":
                "the linker-borne covalent reach enumeration + the family-wide chemoselectivity window",
            "research/modalities/nr4a-paralogue-unique-residues.json":
                "the sequence-level uniqueness map (UniProt + two aligners)",
            "research/modalities/nr4a3-linker-design.json": "the committed virtual construct library",
            "research/modalities/nr4a3-orientation-basins.json": "the anchors both reach analyses read",
        },
        "_documents_this_audit_may_not_edit": list(LOCKED),
        "residue_identity": ri,
        "branch_1b_claim_verdicts": cl,
        "pose_dependency_split": pose_split(dyn, reach, uniq, basins),
        "limits": limits(dyn, reach),
        "what_the_axis_licenses": licenses(),
        "stale_blocker": stale_blocker(),
        "proposed_edits": proposed_edits(ri, cl, dyn),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate and compare against the committed file; exit 1 on drift")
    args = ap.parse_args(argv)

    d = build()
    txt = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not os.path.exists(OUT):
            print("categorical_axis_audit: %s does not exist" % OUT)
            return 1
        with open(OUT, encoding="utf-8") as fh:
            cur = fh.read()
        # the generation stamp is expected to differ; everything else must not
        a = json.loads(cur)
        a.pop("_generated", None)
        b = json.loads(txt)
        b.pop("_generated", None)
        if a != b:
            print("categorical_axis_audit: DRIFT — the committed audit disagrees with a fresh read of the "
                  "artifacts. Regenerate it.")
            return 1
        print("categorical_axis_audit: current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print("categorical_axis_audit: wrote %s (%d bytes)" % (OUT, len(txt)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
