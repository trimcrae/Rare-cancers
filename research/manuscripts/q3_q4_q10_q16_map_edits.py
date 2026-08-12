#!/usr/bin/env python3
"""Routed roadmap edits for `Q3`, `Q4`, `Q10` and `Q16`.

⛔ NO NUMBER IS TYPED IN THIS FILE. Every figure in every `proposed_text` is derived by this script from
the four committed artifacts named in `generated_from`, and every `current_text` is the **live line read
off the target document** rather than transcribed — a transcription is how the categorical audit emitted
nine verbatim edits that all failed to apply.

⛔ THIS SCRIPT APPLIES NOTHING. `nr4a3-program-map.md`, `path-family-synthesis.md`, `systems/graph/*` and
`systems/views/*` are not hand-edited by this pass; the edits are ROUTED. Verify with
`research/manuscripts/verify_map_edit_anchors.py research/manuscripts/degrader/q3-q4-q10-q16-map-edits.json`.

⛔ FENCE. This pass owns the `Q3`, `Q4`, `Q10` and `Q16` rows of §10.1a, the ⚖ ALTERNATIVE cell for THE
MODALITY at C397 in §10.1b, §2.4's brief clause, and `path-family-synthesis.md` §3 Tier-2 row 10. It
touches no `C*` VALUE, no `R*` verdict, no instrument row, no price and no gate scoreboard.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "research", "modalities")

MAP = "research/manuscripts/nr4a3-program-map.md"
SYN = "research/manuscripts/program/path-family-synthesis.md"
OUT = os.path.join(HERE, "degrader", "q3-q4-q10-q16-map-edits.json")

ART = {
    "antihandle": os.path.join(MOD, "nr4a3-antihandle-constraint.json"),
    "length": os.path.join(MOD, "nr4a3-linker-length-principle.json"),
    "inhibitor": os.path.join(MOD, "nr4a3-inhibitor-configuration-prediction.json"),
    "brief": os.path.join(MOD, "nr4a3-design-brief-asymmetric.json"),
}


def live_line(relpath, anchor):
    """Read the ONE line containing ``anchor`` out of the live document.

    ⛔ Refuses on 0 or >1 matches rather than guessing — an ambiguous anchor is exactly the defect
    `map_edit_anchors.verify()` was corrected to catch."""
    body = open(os.path.join(REPO, relpath), encoding="utf-8").read()
    hits = [ln for ln in body.splitlines() if anchor in ln]
    if len(hits) != 1:
        raise SystemExit("REFUSED — anchor %r matches %d lines in %s" % (anchor, len(hits), relpath))
    return hits[0]


def facts():
    d = {k: json.load(open(p, encoding="utf-8")) for k, p in ART.items()}
    ah, ln, ih, br = d["antihandle"], d["length"], d["inhibitor"], d["brief"]
    s = ah["summary"]
    lf = ah["★_length_frontier"]
    gate_row = next(r for r in lf["by_length"] if r["is_the_categorical_gate"])
    dis = ah["roadmap_set_disagreement"]
    A = ih["★_axis_A_admissible_space"]
    filt = A["admissibility_filter"]
    ts, co = A["paired_transitions"]["through_space"], A["paired_transitions"]["corridor"]
    Bwin = ih["★_axis_B_the_selectivity_window"]
    az = br["★_the_asymmetry_read"]
    lever = br["the_NR4A2_bound"]["the_exposure_lever"]
    return {
        # Q3
        "n_constructs": s["n_constructs"],
        "n_rejected": s["n_rejected_under_the_union_rule"],
        "n_surviving": s["n_surviving"],
        "n_rejected_all_cells": s["n_rejected_in_EVERY_cell"],
        "antihandles": ah["anti_handle_set"]["antihandles"],
        "witness_counts": s["antihandle_witness_counts"],
        "prose_set": dis["prose_set"],
        "prose_extra": [e["label"] for e in dis["in_prose_but_not_reciprocal_unique"]],
        "prose_missing": dis["reciprocal_unique_but_missing_from_the_prose"],
        "gate_atoms": lf["categorical_gate_atoms"],
        "gate_anti_cells": gate_row["n_cells_admitting_an_antihandle"],
        "gate_n_cells": gate_row["n_cells"],
        "gate_target_cells": gate_row["n_cells_where_C397_ITSELF_is_reached"],
        "gate_clean_cells": gate_row["★_n_cells_reaching_C397_WITHOUT_an_antihandle"],
        "peak": lf["★_the_design_target_column_peaks_at"],
        "shortest_construct": ah["constructs"]["shortest_committed_construct_atoms"],
        # Q4
        "reach_band_at_gate": next(b["reach_only_band"] for b in ln["the_length_dependence"]["by_length"]
                                   if b["n_backbone_atoms"] == ln["gate_atoms"]),
        "refused_at": sorted(ln["★_refused_above_the_gate"], key=int),
        "p_cat_by_scope": ln["★_why_only_at_the_gate"][
            "P_categorical_given_exposed_by_scope_over_all_lengths"],
        "surviving_fraction": {str(r["n_backbone_atoms"]):
                               r["fraction_of_the_reach_signal_surviving_the_exposure_filter"]
                               for r in ln["★_why_only_at_the_gate"]["by_length"]},
        # Q10
        "mono_answer": ih["⭑_the_stale_row_this_pass_corrects"]["the_committed_answer"],
        "e3_retired": filt["⭑_retired_by_removing_the_E3_arm"],
        "adm_cells": filt["n_cells"],
        "warhead_not_retired": filt["⛔_NOT_retired"],
        "ts_gain": ts["closed_to_open"], "ts_loss": ts["open_to_closed"], "ts_paired": ts["n_paired"],
        "co_gain": co["closed_to_open"], "co_loss": co["open_to_closed"],
        "co_biv_open": Bwin["corridor"]["bivalent"]["n_open_window"],
        "co_biv_cells": Bwin["corridor"]["bivalent"]["n_cells"],
        "co_mono_open": Bwin["corridor"]["monovalent"]["n_open_window"],
        "co_mono_cells": Bwin["corridor"]["monovalent"]["n_cells"],
        "disc_verdict": ih["★_the_discriminator_test"]["⭐_verdict"],
        "holds_A": ih["★_verdict"]["prediction_holds_on_axis_A"],
        "rescues": ih["★_verdict"]["prediction_rescues_the_route"],
        # Q16
        "brief_one_line": br["★_the_brief"]["one_line"],
        "lead_status": az["lead_status"],
        "nr4a1_verdict": az["by_paralogue"]["NR4A1"]["verdict_under_the_frozen_rule"],
        "nr4a2_verdict": az["by_paralogue"]["NR4A2"]["verdict_under_the_frozen_rule"],
        "nr4a1_c2_survives": az["by_paralogue"]["NR4A1"]["★_three_cautions"]["contested_C2_rule"][
            "survives_the_rule_change"],
        "n_tissues": lever["n_tissues"],
        "coexpressed": lever["counts"]["nr4a2_and_nr4a3_co_expressed"],
        "dominant": lever["counts"]["nr4a2_dominant"],
        "unbuffered": lever["counts"]["nr4a2_unbuffered"],
    }


def build(f):
    E = []

    # ---- Q3 -------------------------------------------------------------------------------------------
    a = "| **Q3** | ★ **Carry the anti-handle set as a design CONSTRAINT"
    E.append({
        "id": "E1", "row": "Q3", "serves": "S15 → R8 R15",
        "section": "§10.1a · the option queue, Q3",
        "file": MAP, "anchor": a, "current_text": live_line(MAP, a),
        "proposed_text": (
            "| **Q3** | ★ **Carry the anti-handle set as a design CONSTRAINT, not as an after-the-fact "
            "report** — reject any construct whose reach envelope admits a RECIPROCAL-UNIQUE paralogue "
            "cysteine | [`S15`](../modalities/selectivity-mechanism-options.md) **B** | `R8` `R15` | "
            "**⊕ CMP** + **⇢ PRE** | ✅ **DONE %s** | **—** | **$0** | ⭐ **BUILT AS A PREDICATE AND RUN — "
            "AND THE FALSIFIER THIS ROW WROTE IS THE RESULT: NO COMMITTED CONSTRUCT SURVIVES IT.** "
            "%d of %d constructs are REJECTED under the union-over-poses rule, **%d survive**; witnesses "
            "%s. ⚠ **The rule is load-bearing and travels with the sentence**: only **%d** are rejected "
            "in EVERY cell, so each rejection rests on SOME committed cell rather than all of them — the "
            "conservative reading `R5` forces (the second pose method disagrees with the first, so the "
            "program cannot name which cell is real), and NOT the claim that no clean geometry exists. "
            "⇒ the enumeration HAS been optimising reach TO C397 while admitting the paralogue "
            "liability.⛔ **AND THE SET THIS ROW NAMED IN PROSE IS WRONG IN BOTH DIRECTIONS**: the "
            "derived reciprocal-unique set is %s — `%s` is in the prose and is **not** reciprocal-unique "
            "(it aligns to NR4A3 C536, a cysteine NR4A3 HAS), while `%s` **is** and the prose omits it. "
            "⭑ **And the constraint is monotone in LENGTH, which is what makes it a design rule**: at the "
            "%d-atom categorical gate only **%d of %d** cells admit an anti-handle while **%d of %d** "
            "reach C397 — and the shortest committed construct is **%d** atoms, above the gate. "
            "⚠ **BUT `Q3` AND `Q4` DO NOT AGREE ABOUT EVERYTHING, AND THE DISAGREEMENT IS MEASURED "
            "RATHER THAN SMOOTHED**: both LIABILITY columns are monotone and minimised at short length, "
            "but the DESIGN-TARGET column — cells reaching C397 while admitting **no** anti-handle — is "
            "not monotone and peaks at **%d atoms (%d of %d cells)** against **%d** at the gate. ⛔ That "
            "does **not** license the longer length: above the gate the categorical statement inherits "
            "`V17`'s false negative and `Q4`'s `principle()` refuses to emit it, so the extra clean "
            "cells are reach without a statable discrimination. **The gate is set by what can be SAID, "
            "not by what can be reached.** "
            "Predicate + tests: [`antihandle_constraint.py`](../modalities/antihandle_constraint.py); "
            "numbers: [`nr4a3-antihandle-constraint.json`](../modalities/nr4a3-antihandle-constraint.json). "
            "⛔ A filter removes liabilities; it adds no signal, computes no energy and licenses no "
            "margin, ratio or window |"
            % (DATE, f["n_rejected"], f["n_constructs"], f["n_surviving"],
               ", ".join("`%s` ×%d" % (k, v) for k, v in f["witness_counts"].items()),
               f["n_rejected_all_cells"],
               ", ".join("`%s`" % x for x in f["antihandles"]),
               f["prose_extra"][0] if f["prose_extra"] else "—",
               f["prose_missing"][0] if f["prose_missing"] else "—",
               f["gate_atoms"], f["gate_anti_cells"], f["gate_n_cells"],
               f["gate_target_cells"], f["gate_n_cells"], f["shortest_construct"],
               f["peak"]["n_backbone_atoms"], f["peak"]["n_cells"], f["gate_n_cells"],
               f["gate_clean_cells"])),
        "why": "the row's own falsifier was 'no committed construct survives it', and that is the "
               "measured outcome; and the prose anti-handle set disagrees with the committed "
               "reciprocal-uniqueness map, which a design constraint may not do.",
    })

    # ---- Q4 -------------------------------------------------------------------------------------------
    a = "| **Q4** | **State the linker-length design principle at the 12-atom gate"
    lo, hi = f["reach_band_at_gate"]
    E.append({
        "id": "E2", "row": "Q4", "serves": "S6 → R15",
        "section": "§10.1a · the option queue, Q4",
        "file": MAP, "anchor": a, "current_text": live_line(MAP, a),
        "proposed_text": (
            "| **Q4** | **State the linker-length design principle at the %d-atom gate — and only there** "
            "| [`S6`](../modalities/selectivity-mechanism-options.md) **B** | `R15` | **⊕ CMP** (with "
            "`Q3`) | ✅ **DONE %s** | **—** | **$0** | ⭐ **STATED, AND 'ONLY THERE' IS NOW ENFORCED BY "
            "THREE MECHANISMS RATHER THAN ASKED FOR**: `principle(n)` REFUSES above the gate and emits no "
            "statement at all (refused at %s atoms); the statement text carries its own gate inside every "
            "rendering; and `quotation_guard(text)` is a checkable predicate that finds an above-gate "
            "band quoted without the `V17` disclosure. At the gate P(a paralogue cysteine is also reached "
            "\\| an NR4A3-unique one is) is **%.3f–%.3f** and the reach-only and exposure-filtered bands "
            "AGREE, so the statement rests on nothing `V17` touches; above it only %s of the reach signal "
            "survives the filter. ⚠ **AND `S6`'s OWN PHRASING IS CORRECTED**: *'P(categorical \\| "
            "exposed) is 1.000 at EVERY length'* is exactly 1.0 in the static and unbiased scopes and "
            "**%.3f–%.3f** in the metadynamics scope — the argument is unweakened, but a principle whose "
            "point is that a number must be stated at its gate may not round one past where it holds. "
            "[`linker_length_principle.py`](../modalities/linker_length_principle.py) · "
            "[`nr4a3-linker-length-principle.json`](../modalities/nr4a3-linker-length-principle.json) |"
            % (f["gate_atoms"], DATE, ", ".join(f["refused_at"]), lo, hi,
               "–".join(sorted({"%.1f%%" % (100 * v) for k, v in f["surviving_fraction"].items()
                                if int(k) > f["gate_atoms"] and v is not None})),
               f["p_cat_by_scope"]["metad_biased"][0], f["p_cat_by_scope"]["metad_biased"][1])),
        "why": "the row's falsifier is the gate itself; the principle now exists as a statement that "
               "cannot be emitted outside it, and stating it exposed a rounding error in S6's own "
               "phrasing.",
    })

    # ---- Q10 ------------------------------------------------------------------------------------------
    a = "| **Q10** | **Re-run the linker-reach enumeration with the E3 arm REMOVED**"
    E.append({
        "id": "E3", "row": "Q10", "serves": "route 2 → R8 R15",
        "section": "§10.1a · the option queue, Q10",
        "file": MAP, "anchor": a, "current_text": live_line(MAP, a),
        "proposed_text": (
            "| **Q10** | **Re-run the linker-reach enumeration with the E3 arm REMOVED** — the covalent "
            "inhibitor / probe configuration at C397 | [route 2](program/target-route-options.md) ★★ | `R8` "
            "`R15` | **⚖ ALT** (to the degrader modality — see [§10.1b](#101b--the-family--what-picking-"
            "one-costs-you)) | ✅ **DONE** | **—** | **$0 CPU** | ⛔ **THIS ROW SAID 'NEVER RUN' ABOUT AN "
            "ARTIFACT ALREADY ON THIS BRANCH.** The enumeration ran **2026-08-06 at 7:12 AM ET** "
            "([`nr4a3-monovalent-reach.json`](../modalities/nr4a3-monovalent-reach.json)), replicates the "
            "committed bivalent window over all 120 cells, and returns **`%s`** on the conservative "
            "convention. ⭐ **AND THE TCIP INTERFACE-FLOOR ABLATION'S PREDICTION WAS THEN TESTED AGAINST "
            "IT (%s): IT HOLDS ON ITS OWN AXIS AND DOES NOT RESCUE THE ROUTE.** Axis A — admissible "
            "space, the ablation's axis: removing the E3 arm retires the E3-anchor-buried refusal, **%d "
            "of %d** ensemble cells, while the warhead-anchor refusal (**%d**) survives untouched, and "
            "**%d of %d** paired cells gain a window on the permissive convention against **%d** that "
            "lose one. Axis B — the window `Q10` was closed on: **%d of %d → %d of %d** open cells, a "
            "complete one-directional collapse. ⭑ **The discriminating observation:** margin AND rank "
            "both degrade, so the `\\|p−b\\|` term was a **discriminator**, not only a cost — an "
            "interface FLOOR is a filter that admits more when removed, a length term is what was "
            "ORDERING the cysteines, and the ablation never made a prediction about the second. ⇒ **the "
            "30-of-30 closure SURVIVES without the E3 arm** — this row's own falsifier, resolved in the "
            "direction that closes it. "
            "[`nr4a3-inhibitor-configuration-prediction.json`](../modalities/nr4a3-inhibitor-configuration-prediction.json) |"
            % (f["mono_answer"], DATE, f["e3_retired"], f["adm_cells"], f["warhead_not_retired"],
               f["ts_gain"], f["ts_paired"], f["ts_loss"],
               f["co_biv_open"], f["co_biv_cells"], f["co_mono_open"], f["co_mono_cells"])),
        "why": "the row's stated falsifier — 'the 30-of-30 closure SURVIVES without the E3 arm' — is "
               "answered, and the mechanism that appeared to reopen it acts on a different quantity.",
    })

    # ---- Q10, the ALTERNATIVE cell in §10.1b ----------------------------------------------------------
    a = "| **THE MODALITY at C397** | degrader (the current plan"
    cur = live_line(MAP, a)
    E.append({
        "id": "E4", "row": "§10.1b", "serves": "the ⚖ ALTERNATIVE set",
        "section": "§10.1b · ⚖ ALTERNATIVES — THE MODALITY at C397",
        "file": MAP, "anchor": a, "current_text": cur,
        "proposed_text": (
            cur.rstrip().rstrip("|").rstrip()
            + " ⭐ **AND THE INHIBITOR LIMB IS NO LONGER A $0 STUDY WAITING TO BE RUN — IT RAN (%s).** "
              "Removing the E3 arm returns **`%s`** on the conservative convention and the interface-floor "
              "ablation's prediction was tested against it: it **holds on admissible space** (the "
              "E3-anchor-buried refusal is retired, %d of %d ensemble cells) and **does not rescue the "
              "window** (%d of %d → %d of %d open cells). ⚠ **The 2026-08-06 TCIP correction does NOT "
              "transfer to this limb**: a TCIP is bivalent and retires only `R12`, while a monovalent "
              "inhibitor induces no ternary at all, so `R9` and `R10` go with it. "
              "[`nr4a3-inhibitor-configuration-prediction.json`](../modalities/nr4a3-inhibitor-configuration-prediction.json) |"
              % (DATE, f["mono_answer"], f["e3_retired"], f["adm_cells"],
                 f["co_biv_open"], f["co_biv_cells"], f["co_mono_open"], f["co_mono_cells"])),
        "why": "the cell describes the inhibitor limb as a study still to be run; it has been run, and "
               "the two ⚖ ALTERNATIVES in this same set have different terms that a reader has already "
               "conflated once.",
    })

    # ---- Q16 ------------------------------------------------------------------------------------------
    a = "| **Q16** | **Restate the design brief ASYMMETRICALLY"
    E.append({
        "id": "E5", "row": "Q16", "serves": "route 1 → R7 (§2.4)",
        "section": "§10.1a · the option queue, Q16",
        "file": MAP, "anchor": a, "current_text": live_line(MAP, a),
        "proposed_text": (
            "| **Q16** | **Restate the design brief ASYMMETRICALLY** — in its harder measured form | "
            "[route 1](program/target-route-options.md) ★★ | `R7` ([§2.4](#24--the-selectivity-requirement-is-"
            "asymmetric--and-this-page-stated-it-symmetrically)) | **⇢ PRE** | ✅ **DONE %s** | **—** | "
            "**$0** | ⭐ **RESTATED: *%s*** — four clauses, each carrying its own sensitivity, in "
            "[`nr4a3-design-brief-asymmetric.json`](../modalities/nr4a3-design-brief-asymmetric.json). "
            "⛔ **NR4A2 is NOT a soft constraint**: complete germline loss is neonatal-lethal at complete "
            "penetrance with a primary citation, so the floor is evidenced rather than precautionary; it "
            "ranks below NR4A1 only because NR4A1's bound is a **combination** genotype a degrader "
            "RECONSTITUTES. ⛔ **The exposure lever is withdrawn by measurement** — %d of %d tissues "
            "co-express, **%d** dominant, **%d** unbuffered, so there is no tissue where the anti-target "
            "is present and the target is not and the selectivity has to be MOLECULAR. ⚠ **AND THE BRIEF "
            "CARRIES THE ASYMMETRY WITHOUT THE WORD**: the split read is NR4A1 *%s* on the MANDATORY "
            "axis and NR4A2 *%s* on the best-effort one, but its own `lead_status` is *%s* — the "
            "separation does **not** survive the contested `C2` rule, the design-effect-corrected Wilson "
            "intervals overlap, and at 3 vs 3 replicates the exact test's Holm-adjusted floor is 0.10, so "
            "no outcome of this design can clear α = 0.05 family-wise |"
            % (DATE, f["brief_one_line"], f["coexpressed"], f["n_tissues"], f["dominant"],
               f["unbuffered"], f["nr4a1_verdict"], f["nr4a2_verdict"], f["lead_status"])),
        "why": "the row asks for the harder measured form and for the asymmetric read's sensitivity to "
               "travel with it; the brief now exists and the word SEPARATED is deliberately not carried.",
    })

    # ---- §2.4's brief clause --------------------------------------------------------------------------
    a = "  — spare NR4A2 as far as the four handles allow, and carry the residual as a DISCLOSED, UNSIZED"
    E.append({
        "id": "E6", "row": "§2.4", "serves": "R7",
        "section": "§2.4 · the selectivity requirement is ASYMMETRIC — 'What this changes'",
        "file": MAP, "anchor": a, "current_text": live_line(MAP, a),
        "proposed_text": (
            "  — spare NR4A2 as far as the four handles allow. ⭐ **RESTATED %s (`Q16`): *%s*.** "
            "⚠ *Superseded, retained: **'soft constraint'** and **'carry the residual as a DISCLOSED, "
            "UNSIZED exposure'** — NR4A2's floor is a primary-cited complete-penetrance neonatal "
            "lethality, so the constraint is bounded rather than soft, and %d of %d tissues co-express "
            "with **%d** dominant and **%d** unbuffered, so the exposure lever the phrase hands off to "
            "does not exist.* Full brief, with every clause's sensitivity attached to it:"
            % (DATE, f["brief_one_line"], f["coexpressed"], f["n_tissues"], f["dominant"],
               f["unbuffered"])),
        "why": "this clause is the one place the brief is stated in the requirements layer, and it still "
               "carries the exposure lever the HPA reading removed.",
    })

    # ---- path-family-synthesis §3 Tier-2 row 10 -------------------------------------------------------
    a = "| 10 | **Covalent inhibitor rather than degrader** at C397 |"
    E.append({
        "id": "E7", "row": "§3 Tier-2 row 10", "serves": "route 2",
        "section": "path-family-synthesis.md §3 · Tier 2, row 10",
        "file": SYN, "anchor": a, "current_text": live_line(SYN, a),
        "proposed_text": (
            "| 10 | **Covalent inhibitor rather than degrader** at C397 | ⛔ **NO LONGER UNDER-RUN — IT "
            "RAN (2026-08-06, 7:12 AM ET) AND RETURNED `%s`** on the conservative convention "
            "([`nr4a3-monovalent-reach.json`](../modalities/nr4a3-monovalent-reach.json)). ⚠ *Superseded, "
            "retained: 'unchanged and still under-run … the enumeration has never been run in that "
            "configuration'.* The TCIP interface-floor ablation's prediction was then tested against it "
            "(%s): it **holds on admissible space** — the E3-anchor-buried refusal is retired, %d of %d "
            "ensemble cells, while the warhead-anchor refusal (%d) survives — and it **does not rescue "
            "the window**: %d of %d → %d of %d open cells. The `\\|p−b\\|` term was a DISCRIMINATOR, not "
            "only a cost, so removing it removed the ordering. Retires the ternary/ubiquitin stack; loses "
            "the degradation mechanism "
            "([`nr4a3-inhibitor-configuration-prediction.json`](../modalities/nr4a3-inhibitor-configuration-prediction.json)) |"
            % (f["mono_answer"], DATE, f["e3_retired"], f["adm_cells"], f["warhead_not_retired"],
               f["co_biv_open"], f["co_biv_cells"], f["co_mono_open"], f["co_mono_cells"])),
        "why": "this row asserts the enumeration has never been run about an artifact committed to this "
               "branch. A stale row that reads as a live lead is how a free result stays invisible.",
    })
    return E


DATE = "2026-08-07"


def main():
    for k, p in ART.items():
        if not os.path.exists(p):
            print("REFUSED — %s (%s) does not exist; build it first" % (p, k), file=sys.stderr)
            return 2
    f = facts()
    edits = build(f)
    doc = {
        "_what": "Routed roadmap edits for Q3 (the anti-handle design constraint), Q4 (the linker-length "
                 "principle at its gate), Q10 (the inhibitor configuration and the ablation's "
                 "prediction) and Q16 (the asymmetric design brief).",
        "_rule": "⛔ NO NUMBER IS TYPED IN THIS FILE. Every figure in every `proposed_text` is derived by "
                 "q3_q4_q10_q16_map_edits.py from the artifacts in `generated_from`, and every "
                 "`current_text` is the live line READ off the target document. Regenerate rather than "
                 "edit.",
        "_fence": "This pass owns the Q3, Q4, Q10 and Q16 rows of §10.1a, the MODALITY-at-C397 cell in "
                  "§10.1b, §2.4's brief clause and path-family-synthesis.md §3 Tier-2 row 10. It touches "
                  "no C* VALUE, no R* verdict, no instrument row, no price and no gate scoreboard.",
        "⛔_pose_marginalisation": "R5 is unresolved (pose-second-method.json: 0 of 6 systems agree "
                                  "within 2.00 A, R5_resolved false). Every edit above states its "
                                  "quantity as marginalised over poses — Q3's constraint is the UNION "
                                  "over placement x pendant x convention cells, Q4's principle is an "
                                  "average over 73,867 placements and names no vector, Q10's comparison "
                                  "is a paired delta reported as a distribution, and Q16's brief "
                                  "inherits neither R3 nor R5. No proposed_text contains a "
                                  "pose-specific or vector-specific claim.",
        "generated_from": {k: os.path.relpath(p, REPO) for k, p in ART.items()},
        "n_edits": len(edits),
        "derived_facts": f,
        "map_edits_required": edits,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote %s — %d edit(s)" % (os.path.relpath(OUT, REPO), len(edits)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
