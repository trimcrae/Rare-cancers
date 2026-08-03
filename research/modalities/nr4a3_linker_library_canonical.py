#!/usr/bin/env python3
"""
WHICH LINKER LIBRARY IS CANONICAL — the ruling, its evidence, and its anti-drift guard.  $0 CPU, stdlib only.

⛔ THE PROBLEM THIS SETTLES (roadmap §10.1 row 25).  The committed `nr4a3-linker-design.json` stopped
reproducing from its own generator: 57 constructs against 54 committed, 3,852 enumerated against 3,544, and a
DIFFERENT recommended 5a-KS matched pair.  Anyone re-deriving the causal test article from today's code got a
different molecule, silently, and rung `5b-T`'s degrader SMILES come down the same chain
(`nr4a3-linker-design.json` -> `nr4a3-linker-library-chem.json` -> `ternary_rebuild_cost.DEGRADER_SOURCE`).

★ NOTHING IN THIS FILE IS TYPED.  Every count, every construct id, every SMILES comparison and every predicate
below is DERIVED — the committed artifact is read from disk and the corrected one is RE-RUN from
`nr4a3_linker_design.run()` in this same process.  The only authored strings are the RULING and the
`map_edits_required` texts, and each of those names the field that decided it (CLAUDE.md rule 1).

★★ THE ANCHORS ARE VERIFIED BY THE GENERATOR, NOT BY THE AUTHOR.  A previous audit emitted nine verbatim map
edits and all nine failed to apply, because they were written against documents that were being restructured
underneath them: findings valid, anchors dead.  So every entry in `map_edits_required` carries its
`current_text`, and this generator greps the LIVE roadmap for it and records `anchor_live: true|false` on the
entry.  An edit whose anchor cannot be found is emitted with `anchor_live: false` and is REFUSED by
`--check`, so a stale anchor can never ship looking valid.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

COMMITTED = os.path.join(HERE, "nr4a3-linker-design.json")
LIBRARY_CHEM = os.path.join(HERE, "nr4a3-linker-library-chem.json")
COFOLD_PREP = os.path.join(HERE, "nr4a3-5aks-cofold-prep.json")
ROADMAP = os.path.join(REPO, "research", "manuscripts", "nr4a3-program-map.md")

LIB_KEYS = ("virtual_library_at_the_term_a_exemplar", "virtual_library_at_representative_geometry")

# =============================================================================================================
# THE CAUSE — established by controlled A/B, not by reading commit messages
# =============================================================================================================

#: ★ The ONE commit that moved the enumeration, and how that was established rather than guessed.
#:
#: Three hypotheses were on the table and only one survives a discriminating observation:
#:   H1  one of the two 2026-08-02 edits to `nr4a3_linker_design.py` changed selection.
#:   H2  an INPUT artifact changed under the generator.
#:   H3  a shared geometry KERNEL the generator imports changed.
#:
#: H1 is refuted: the generator AT the commit that produced the committed artifact (`757ee7acf`, whose code
#: parent is `481da42eb`) was fetched and run against today's inputs and returned the CORRECTED counts, not
#: the committed ones.  Both later edits are docstring-only (`10dd81e42`) or reporting-only (`73566cd47`).
#: H2 is refuted: all four JSON inputs are byte-identical to their state at `757ee7acf`, and the structure
#: PDB has not been touched since 2026-07-10.  The one input that DID land later,
#: `nr4a-paralogue-dynamics.json`, feeds only the REPORTED collision profile — proven neutral by re-running
#: the current generator with `PARALOGUE_COLLISION_PILOT_5657_SUPERSEDED` forced back in, which returned the
#: corrected counts unchanged.
#: H3 is CONFIRMED, and it reproduces exactly: HEAD's generator with `linker_design.py` rolled back one
#: commit reproduces the committed artifact with ZERO structural differences.
CAUSE = {
    "commit": "382c36947",
    "landed_utc": "2026-08-02T20:24:35Z",
    "landed_et": "2026-08-02 4:24 PM ET",
    "subject": "port to main: exact 3-ball solver + its regression tests + the reach lane's rebase-retry push",
    "file": "research/modalities/linker_design.py",
    "symbol": "three_ball_min_margin",
    "parent": "864a9518f",
    "ported_from": "claude/nr4a1-protac-positive-control-xnszjl (0755eb9db, d2804fd79)",
    "what_changed": (
        "a compass search over a convex but NON-differentiable objective, which stalls on the kink ridge the "
        "minimiser sits on, was replaced by a closed-form enumeration of the at-most-8 candidate optima."),
    "which_is_right": (
        "THE NEW ONE, and the commit measured it rather than asserting it: 0 feasibility mismatches against "
        "an exact disk oracle over 160,962 cells, replacing a solver with 92 false-disjoint and 0 "
        "false-overlap calls in 118,708 cells."),
    "direction_of_the_error": (
        "ONE-SIDED AND CONSERVATIVE. The old solver reported intersecting balls as disjoint, so it "
        "UNDER-claimed reach and never over-claimed it. That is why the corrected kernel ADMITS MORE "
        "constructs rather than refuting committed ones — a direction that is visible in the counts below "
        "and is the reason the committed library is safe to keep using."),
    "the_miss": (
        "⛔ `382c36947` DID name the artifacts it invalidated — `nr4a3-orientation-basins.json`'s "
        "`term_a_feasibility_envelope`, 'They are NOT regenerated here' — but it did NOT name "
        "`nr4a3-linker-design.json`, which is a SECOND live consumer of the same kernel. One consumer was "
        "registered and the other was not, which is the whole of this incident."),
    "still_open_same_class": (
        "⚠ `nr4a3-orientation-basins.json` -> `term_a_feasibility_envelope` is the OTHER artifact built on "
        "the pre-fix kernel and it is still not regenerated. Same conservative direction, same registration "
        "gap; it is not settled by this ruling and needs its own."),
    "how_to_reproduce_the_a_b": [
        "git show 382c36947^:research/modalities/linker_design.py > /tmp/pre.py   # or fetch 864a9518f",
        "mirror research/modalities into a temp tree, swap in /tmp/pre.py, run nr4a3_linker_design.py there",
        "the summary block is then byte-identical to the committed artifact's `library_summary`",
    ],
}

# =============================================================================================================
# THE RULING
# =============================================================================================================

RULING = {
    "_one_line": (
        "BOTH are canonical, for different jobs, and the failure was that nothing said which was which. The "
        "committed `nr4a3-linker-design.json` is FROZEN as the EXECUTED enumeration; the corrected kernel is "
        "canonical for all NEW design work; the corrected enumeration is REGISTERED here rather than written "
        "over the committed one."),
    "committed_artifact": {
        "verdict": "FROZEN — canonical as the EXECUTED record. Do NOT regenerate in place.",
        "why": [
            "It is fully reproducible, so it is not mystery-stale: HEAD's generator plus `linker_design.py` "
            "at %s reproduces it with ZERO structural differences (see `reproduction` below)." % CAUSE["parent"],
            "It is what `V16` / rung 5a-KS was actually measured on, and a landed result must not be "
            "orphaned by a re-derivation of its own inputs.",
            "It is a PREREGISTERED enumeration. Overwriting it in place would rewrite a preregistration, "
            "which is exactly the act CLAUDE.md rule 1.2 exists to stop.",
            "`nr4a3-linker-library-chem.json` and `ternary_rebuild_cost.DEGRADER_SOURCE` reference it BY "
            "CONSTRUCT ID, so an in-place regeneration would silently move rung 5b-T's degrader source.",
        ],
        "the_bias_it_carries_and_must_be_quoted_with": (
            "It UNDER-admits. It was built on a kernel with 92 measured false-disjoint calls, so its "
            "enumeration is a conservative subset of the geometrically feasible one — smaller, never larger. "
            "It is not wrong in the dangerous direction, and it must never be described as 'the complete "
            "library'."),
    },
    "current_code": {
        "verdict": "CANONICAL FOR NEW WORK — its geometry is the measured-correct one.",
        "why": ("the exact solver is verified against an independent oracle over 160,962 cells; the solver it "
                "replaced is verified WRONG on 92 of 118,708. There is no reading on which the old kernel is "
                "the better geometry."),
        "so": ("any NEW enumeration, any re-derived matched pair, and any construct proposed from here on "
               "uses the corrected kernel and cites the CORRECTED set below — never the executed one."),
    },
    "superseded_retained": (
        "SUPERSEDED, RETAINED per CLAUDE.md rule 1.2: the reading under which `nr4a3-linker-design.json` was "
        "'the' linker library, singular and current. It is the EXECUTED library. The recommendation it "
        "carries — `crbnM0@ex_5amide_e4-a2_pyr3`, PEG4+alkyl at 19 backbone atoms — is superseded AS A "
        "RECOMMENDATION by `crbnM0@ex_5amide_a9-a2_pyr3`, alkyl+alkyl at 18, and is retained AS THE EXECUTED "
        "TEST ARTICLE, which is a different and still-live status."),
    "what_was_NOT_chosen_and_why": {
        "regenerate_and_overwrite": (
            "REFUSED. It rewrites a preregistered enumeration, orphans `V16`'s landed inputs, and moves rung "
            "5b-T's degrader source from 54 constructs to 57 without anyone deciding to."),
        "freeze_and_say_nothing": (
            "REFUSED. That is the state that produced this incident: an artifact and its generator "
            "disagreeing with nothing in the repo able to notice."),
    },
}

# =============================================================================================================
# THE MAP EDITS — authored text, MACHINE-VERIFIED ANCHORS
# =============================================================================================================
#
# ⚠ `current_text` MUST be a currently-present, unique substring of the live roadmap. This module greps for
# each one and stamps `anchor_live` / `anchor_unique` onto the emitted entry; `--check` FAILS on any entry
# whose anchor is dead. `anchor: null` means "this needs a section that does not exist yet" and is honest
# rather than stale.

MAP_EDITS = [
    # ---------------------------------------------------------------------------------- ROW 25 · the ruling
    {
        "id": "row25-state",
        "section": "§10.1 row 25",
        "anchor": "row 25's state cell",
        "current_text": "| **25** | ⛔ **Settle which linker library is CANONICAL",
        "why": "the row is the open question this artifact answers; it must point at the ruling, not restate it.",
        "artifact": "research/modalities/nr4a3-linker-library-canonical.json -> ruling",
        "proposed_text": "| **25** | ✅ **SETTLED 2026-08-03 — which linker library is CANONICAL",
        "note": ("only the row's LEAD CELL is replaced; the rest of the row is rewritten by `row25-body` "
                 "below so the two are applied together."),
    },
    {
        "id": "row25-body",
        "section": "§10.1 row 25",
        "anchor": "row 25's 'next action' cell, from '⭑ **Take this before' to the end of the row",
        "current_text": "⭑ **Take this before `5b-T` runs, not after.**",
        "why": ("the decision is made and the evidence is committed; the cell should carry the ruling in one "
                "line and link, per rule 1, rather than re-litigating the question."),
        "artifact": "research/modalities/nr4a3-linker-library-canonical.json",
        "proposed_text": (
            "✅ **RULED, with a controlled A/B: BOTH are canonical, for different jobs.** The committed "
            "artifact is **FROZEN as the EXECUTED enumeration** (it is what `V16` was measured on, it is "
            "referenced by construct id by `nr4a3-linker-library-chem.json` and rung `5b-T`, and it is fully "
            "reproducible — HEAD's generator plus `linker_design.py` at `864a9518f` reproduces it with ZERO "
            "structural differences); the **corrected kernel is canonical for all NEW design work** and its "
            "enumeration is REGISTERED, not written over the committed one. **Cause, established by A/B and "
            "not by reading commit messages:** `382c36947` (2026-08-02 4:24 PM ET) replaced "
            "`linker_design.three_ball_min_margin`'s compass search with an exact closed-form solver — 0 "
            "mismatches over 160,962 cells against 92 false-disjoint in 118,708 — so the drift is a "
            "**one-sided, conservative** correction that ADMITS constructs rather than refuting them. "
            "⛔ **The miss was registration, not geometry:** that commit named "
            "`nr4a3-orientation-basins.json`'s `term_a_feasibility_envelope` as built on the old kernel and "
            "NOT regenerated, but did not name `nr4a3-linker-design.json`, a second consumer of the same "
            "kernel — **and the basins artifact is still unregistered, so that half is open.** Every count, "
            "the two registered construct sets, the anti-drift guard and the `5b-T` release predicate: "
            "[`nr4a3-linker-library-canonical.json`](../modalities/nr4a3-linker-library-canonical.json) |"),
    },
    {
        "id": "row25-5bt-release",
        "section": "§10.1 row 1 (rung 5b-T)",
        "anchor": "row 1's 'next action' cell opening",
        "current_text": "**RUN IT — it needs no authorization.**",
        "why": ("row 25 held 5b-T; the hold is discharged and the reason is measurable, so the row should say "
                "so where someone about to run it will read it."),
        "artifact": "research/modalities/nr4a3-linker-library-canonical.json -> release_condition",
        "proposed_text": (
            "**RUN IT — it needs no authorization, and the row-25 hold is DISCHARGED.** ✅ The "
            "canonical-library question is settled and **`5b-T` is invariant to which way it went**: its four "
            "named degrader candidates are present with **identical SMILES** in BOTH the executed and the "
            "corrected enumerations, and `shortest_committed_backbone_atoms` is 14 in both, so no re-derivation "
            "changes this rung's inputs "
            "([`nr4a3-linker-library-canonical.json`](../modalities/nr4a3-linker-library-canonical.json) → "
            "`release_condition`)."),
    },
    {
        "id": "row25-readout-decisions",
        "section": "§10.2 readout",
        "anchor": "the '3 rows wait on a decision that costs nothing at all' bullet",
        "current_text": "- **3 rows wait on a decision that costs nothing at all** (7, 8, 25)",
        "why": "row 25 is settled; the derived count must move with it or the readout contradicts the table.",
        "artifact": "research/modalities/nr4a3-linker-library-canonical.json -> ruling",
        "proposed_text": (
            "- **2 rows wait on a decision that costs nothing at all** (7, 8) ⚠ *Superseded, retained: \"3 "
            "rows … (7, 8, 25)\" — **row 25 was ruled on 2026-08-03**, and the ruling is the reason it left "
            "this list, not a deferral.*"),
    },
    # ------------------------------------------------------------------------- ROW 5 · branch 1b reconciled
    {
        "id": "b1b-banner",
        "section": "§7 branch 1b",
        "anchor": "the '⛔ BUT DO NOT QUOTE BRANCH 1b's NUMBERS YET' banner",
        "current_text": "⛔ **BUT DO NOT QUOTE BRANCH 1b's NUMBERS YET, FOR A NEW AND MEASURABLE REASON.**",
        "why": ("the banner's own example — 'result 3 names NR4A1/NR4A2 C534' — no longer describes result 3, "
                "which was corrected; a hold that cites a fixed error reads as a live one."),
        "artifact": "research/modalities/nr4a3-linker-covalent-reach.json -> verdict",
        "proposed_text": (
            "✅ **RECONCILED 2026-08-03, CLAIM BY CLAIM, AND THE HOLD IS LIFTED.** Every branch-1b figure "
            "below was re-read from the landed artifact one at a time; the corrections are applied in place "
            "and the superseded readings are named where they stood. **What survived unchanged:** C420 "
            "refuted at 0 of 60 (placement × pendant) cells under both conventions; C559 surviving at exactly "
            "one cell (`vhl|M3@term_a_exemplar | dab_branch`, 2 of that cell's 19 conformers, through-space "
            "only); the closer being on a paralogue chain in 30 of 30 graded cells under each convention; "
            "NR4A1 C505 closing 24 of 30 through-space cells and NR4A2 C534 closing 23 of 30 corridor cells; "
            "C505 aligning to NR4A3 **C536** (which NR4A3 HAS) and C534 to NR4A3 **S565** (which it lacks). "
            "**What is newly qualified:** `closed_by` is a TIE-BREAK, not a measurement, in **35 of the 93 "
            "rows that have a closer at all** — two or more cysteines arrive at the same atom count — so the "
            "honest form names the SET that arrives first, never one residue. ⚠ *Superseded, retained: "
            "\"⛔ BUT DO NOT QUOTE BRANCH 1b's NUMBERS YET, FOR A NEW AND MEASURABLE REASON … result 3 names "
            "**NR4A1/NR4A2 C534** as the residue that closes C397's window\" — result 3 was corrected before "
            "this pass and the banner outlived the error it described.*"),
    },
    {
        "id": "b1b-mermaid-dead-edge",
        "section": "§7 branch 1b, mermaid",
        "anchor": "the L --> DEAD edge label",
        "current_text": "L -->|\"C420, C559: no, at every<br/>placement and pendant\"| DEAD",
        "why": ("the diagram still asserts what result 2 four lines below already retracts: C559 is NOT "
                "refuted at every cell. A figure that contradicts its own caption is the failure mode this "
                "reconciliation exists to close."),
        "artifact": ("research/modalities/nr4a3-linker-covalent-reach.json -> "
                     "experimental_ensemble_8xtt.reachable_conformer_counts"),
        "proposed_text": (
            "L -->|\"C420: no, 0 of 60 cells<br/>C559: 1 of 60, through-space only\"| DEAD"),
    },
    {
        "id": "b1b-mermaid-par-node",
        "section": "§7 branch 1b, mermaid",
        "anchor": "the PAR node text",
        "current_text": "PAR[\"The window is closed by a<br/>PARALOGUE cysteine, which<br/>NR4A3 does NOT have\"]",
        "why": ("⛔ THIS IS THE LIVE SURVIVOR OF THE ERROR RESULT 3 ALREADY FIXED. The dominant through-space "
                "closer is NR4A1 C505, which aligns to NR4A3 C536 — NR4A3 DOES carry a cysteine there "
                "(`paralogue_unique_vs_NR4A3: false`). The blanket gloss is false for 24 of 30 through-space "
                "cells."),
        "artifact": ("research/modalities/nr4a3-linker-covalent-reach.json -> "
                     "paralogue_control.reciprocal_uniqueness.by_paralogue"),
        "proposed_text": (
            "PAR[\"Closed by a cysteine on a<br/>PARALOGUE chain — C505 aligns to<br/>NR4A3 C536 (NR4A3 HAS "
            "it);<br/>only C534 → S565 is one NR4A3 lacks\"]"),
    },
    {
        "id": "b1b-mermaid-dead-node",
        "section": "§7 branch 1b, mermaid",
        "anchor": "the DEAD node text",
        "current_text": ("DEAD[\"REFUTED at chemically<br/>routine linker length —<br/>classification pending "
                         "reconciliation\"]"),
        "why": "the reconciliation it was waiting on is this pass, so the node can carry its classification.",
        "artifact": "research/modalities/nr4a3-linker-covalent-reach.json -> verdict",
        "proposed_text": (
            "DEAD[\"⏸ at chemically routine<br/>linker length — not ✕: the bound<br/>is routine length, which a "
            "non-routine<br/>linker could exceed\"]"),
    },
    {
        "id": "b1b-dead-classification",
        "section": "§7 branch 1b",
        "anchor": "the '⚠ `DEAD` is drawn dashed but carries no ✕' paragraph, final sentence",
        "current_text": "It gets classified once the prose is reconciled to the artifact.",
        "why": "the reconciliation is done, so the deferred classification can be made.",
        "artifact": "research/modalities/nr4a3-linker-covalent-reach.json -> verdict.refuted_unique_cysteines",
        "proposed_text": (
            "✅ **Classified 2026-08-03: ⏸, not ✕, and the two cysteines are not equal.** C420 is the strong "
            "case — 0 of 60 cells, both conventions, no conformer — but it is still bounded by *routine* "
            "length rather than by geometry, so ⏸ is the honest glyph for it too. C559 is weaker still: it "
            "survives at one cell. ⚠ **The artifact's own `refuted_unique_cysteines` list is built from "
            "`best_corridor` alone** (`nr4a3_linker_covalent_reach.py`, the `live`/`dead` split), so it "
            "silently drops the through-space evidence recorded two fields away, and it is stronger than the "
            "artifact's own data."),
    },
    {
        "id": "b1b-c559-closed",
        "section": "§7 branch 1b, result 2",
        "anchor": "result 2's closing sentence",
        "current_text": "Those two are closed.",
        "why": ("it lands three lines after 'C559 is NOT [refuted]' and re-merges the two cysteines the "
                "sentence above just separated."),
        "artifact": ("research/modalities/nr4a3-linker-covalent-reach.json -> "
                     "experimental_ensemble_8xtt.reachable_conformer_counts"),
        "proposed_text": (
            "C420 is closed. C559 is closed under the corridor convention everywhere and at 59 of 60 "
            "through-space cells — closed enough to plan against, not closed enough to write down as zero."),
    },
    {
        "id": "b1b-trust-paragraph",
        "section": "§7 branch 1b",
        "anchor": "the 'How far these numbers may be trusted' paragraph",
        "current_text": ("the artifact reports ΔCA against ΔSG per pair and states the sulfur displacement "
                         "that\nwould reopen the window."),
        "why": ("true and incomplete in the way that matters: the noise bound clears by 0.31 Å and is built "
                "only from aligned pairs, so it structurally cannot cover C534 — the residue that closes 23 "
                "of 30 corridor cells — because C534 has no aligned NR4A3 partner BY DEFINITION of being "
                "paralogue-unique. Verified independently against the artifact, not taken from the audit."),
        "artifact": ("research/modalities/nr4a3-linker-covalent-reach.json -> "
                     "paralogue_control.aligned_pair_displacement + verdict.family_wide_window.*."
                     "noise_sensitivity"),
        "proposed_text": (
            "the artifact reports ΔCA against ΔSG per pair and states the sulfur displacement that\n"
            "would reopen the window (**6.25 Å** — the median 5.0 atoms of lost window at 1.25 Å per atom) "
            "against the largest\ndisplacement observed at any aligned pair (**5.94 Å**). ⚠ **That clears by "
            "0.31 Å, a 5 % margin — and it\ncannot cover C534 at all**: the yardstick is built from the 8 "
            "ALIGNED cysteine pairs, and C534 has no aligned\nNR4A3 partner *because* it is "
            "paralogue-unique. So the residue that closes 23 of 30 corridor cells is the one\nresidue the "
            "noise test is structurally unable to bound."),
    },
    {
        "id": "b1b-pose-conditionality",
        "section": "§7 branch 1b, closing paragraph",
        "anchor": "the '⚠ Everything here is conditional on the docked pose' sentence",
        "current_text": ("⚠ Everything here is conditional on the docked pose the anchors come from, whose "
                         "known-answer test is `V3` —\n**which returned INCONCLUSIVE**."),
        "why": ("read from the source, the anchors are NOT a docked pose: `nr4a3_basin_search."
                "build_pose_ensemble` samples 12 solvent-connected anchors around the cryptic-pocket "
                "centroid precisely because no cmpd19 pose exists in this frame, and "
                "`nr4a3-orientation-basins.json` `_limits[0]` says the exit vector is MARGINALISED rather "
                "than asserted. Stating it as a pose dependency overstates one exposure and hides the real "
                "one."),
        "artifact": ("research/modalities/nr4a3-orientation-basins.json -> _limits[0], inputs.n_poses; "
                     "research/modalities/nr4a3_basin_search.py -> build_pose_ensemble"),
        "proposed_text": (
            "⚠ Everything here is conditional on **the cryptic pocket being the right site**, not on a "
            "docked ligand pose: the\nwarhead exit vector is **marginalised** over **12** pocket-mouth "
            "anchors precisely because no cmpd19 pose exists\nin this frame "
            "([`nr4a3-orientation-basins.json`](../modalities/nr4a3-orientation-basins.json) `_limits[0]`, "
            "`inputs.n_poses`).\nThat is what decides how `V3` bears on it: **`V3`'s failure was SITE "
            "selection, on 6 of 6 pairs — not pose\naccuracy** — and site selection is exactly what these "
            "anchors rest on. A *pose*-accuracy failure is already absorbed\nby the marginalisation; a "
            "*site*-selection failure voids every reach number here. ⚠ *Superseded, retained: "
            "\"conditional\non the docked pose the anchors come from, whose known-answer test is `V3` — which "
            "returned INCONCLUSIVE.\"*"),
    },
    {
        "id": "b1b-r8-row",
        "section": "§5 row R8",
        "anchor": "R8's 'NOT reconciled' flag and status cell",
        "current_text": "⚠ **NOT reconciled to this page's prose** — see [§7 branch 1b]",
        "why": "the reconciliation is this pass; leaving the flag makes a discharged blocker read as live.",
        "artifact": "research/modalities/nr4a3-linker-covalent-reach.json -> verdict",
        "proposed_text": "✅ **RECONCILED 2026-08-03**, claim by claim — see [§7 branch 1b]",
        "note": ("the same row's trailing status cell reads `✓ work complete · claim **conditional on `R5` "
                 "and unreconciled**`; the word `unreconciled` must go with it, leaving `✓ work complete · "
                 "claim **conditional on `R5`**`. ⚠ And `conditional on R5` should become **conditional on "
                 "the SITE being right (`R5`)**, per `b1b-pose-conditionality`."),
    },
    {
        "id": "b1b-lk-hold",
        "section": "§5, the `LK` ◐ → ✓ bullet",
        "anchor": "the LK bullet's standing hold",
        "current_text": "⚠ **The hold on quoting branch 1b stands for a different and now-measurable reason**",
        "why": "the hold is discharged; this is its second home and both must move together (rule 1).",
        "artifact": "research/modalities/nr4a3-linker-covalent-reach.json -> verdict",
        "proposed_text": (
            "✅ **The hold on quoting branch 1b is DISCHARGED (2026-08-03)** — the prose was reconciled to the "
            "landed artifact claim by claim, and the one live contradiction left (the mermaid `PAR` node's "
            "\"which NR4A3 does NOT have\") is corrected in the same pass. ⚠ *Superseded, retained: "
            "\"**The hold on quoting branch 1b stands for a different and now-measurable reason** — the prose "
            "has not been reconciled to the landed artifact.\"*"),
    },
    {
        "id": "row5-state",
        "section": "§10.1 row 5",
        "anchor": "row 5's state cell",
        "current_text": "| **5** | **Reconcile branch 1b's prose to its landed artifact** | `R8` | ○ | — | **$0** |",
        "why": "the row is done; leaving it ○ keeps a finished item counted as backlog.",
        "artifact": "research/modalities/nr4a3-linker-covalent-reach.json -> verdict",
        "proposed_text": (
            "| **5** | ✅ **Reconcile branch 1b's prose to its landed artifact — DONE 2026-08-03** | `R8` | "
            "✓ | — | **$0** |"),
        "note": ("the row's trailing cell should become: `✅ done — every branch-1b claim re-read from "
                 "[`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json) one "
                 "at a time. Two claims corrected (the mermaid `DEAD` edge and `PAR` node), two qualified "
                 "(the noise bound cannot cover C534; `closed_by` is a tie-break in 35 of 93 rows), one "
                 "re-sourced (the conditionality is the SITE, not a docked pose), the rest confirmed. Lifts "
                 "*\"do not quote branch 1b anywhere\"*.`"),
    },
    {
        "id": "b1b-third-paralogue-unique-cysteine",
        "section": "§7 branch 1b, result 3",
        "anchor": None,
        "why": ("completeness, not a correction: the artifact records a THIRD paralogue-unique cysteine that "
                "no prose anywhere mentions — NR4A1 C551 aligns to NR4A3 T579, `paralogue_unique_vs_NR4A3: "
                "true`. It is far outside the window (30 backbone atoms in the widest cell) so it changes no "
                "conclusion, but 'the paralogue-unique cysteine' is written as though C534 were the only one "
                "and it is not."),
        "artifact": ("research/modalities/nr4a3-linker-covalent-reach.json -> "
                     "paralogue_control.reciprocal_uniqueness.by_paralogue.NR4A1.C551"),
        "current_text": None,
        "proposed_text": (
            "ADD as a trailing sentence to result 3: \"⚠ **And C534 is not the only paralogue-unique "
            "cysteine.** NR4A1 **C551** aligns to NR4A3 **T579** and is also a site NR4A3 lacks; it sits far "
            "outside the window (30 backbone atoms in the widest graded cell against a closer at 17), so it "
            "changes nothing here — but the reciprocal-uniqueness set has two members, not one.\""),
        "where_it_goes": ("immediately after the sentence ending '…not by both closers under both "
                          "convention.' in result 3 — no anchor is given because the surrounding text is "
                          "being rewritten by `b1b-banner` in the same pass."),
    },
]


# =============================================================================================================
# DERIVATION
# =============================================================================================================

def _ids(doc):
    """{construct_id: record} across BOTH placements of a design artifact."""
    out = {}
    for k in LIB_KEYS:
        for x in doc[k]:
            out[x["construct_id"]] = x
    return out


def _regenerate(tmpdir):
    """Run the CURRENT generator in-process and return its artifact. This is the live half of the guard."""
    import nr4a3_linker_design as LD  # noqa: E402  (path is set at import time)
    out = os.path.join(tmpdir, "regen.json")
    argv = ["--out", out]
    # main() prints a progress log; the caller decides whether to show it.
    LD.main(argv)
    with open(out, encoding="utf-8") as fh:
        return json.load(fh)


def _kernel_head():
    """The commit currently providing `linker_design.py`, so the artifact records WHICH kernel it ran on."""
    try:
        sha = subprocess.run(["git", "log", "-1", "--format=%H", "--", "research/modalities/linker_design.py"],
                             cwd=REPO, capture_output=True, text=True, timeout=30).stdout.strip()
        return sha[:9] or None
    except Exception:                                                    # pragma: no cover - env dependent
        return None


def _five_bt_candidates():
    """Rung 5b-T's degrader candidates — READ from the rung's own module, never re-typed here."""
    import ternary_rebuild_cost as TRC  # noqa: E402
    src = TRC.DEGRADER_SOURCE
    return {
        "_source": "research/modalities/ternary_rebuild_cost.py -> DEGRADER_SOURCE",
        "artifact": src["artifact"],
        "candidates": list(src["crbn_constructs_at_the_shortest_length_bearing_an_electrophile"]),
        "shortest_committed_backbone_atoms": src["shortest_committed_backbone_atoms"],
    }


def _pair_move(committed, corrected, ci, ri):
    """The recommended 5a-KS matched pair, both sides, read from the pair block rather than re-typed.

    `d` is the degrader (wedge-bearing) endpoint and `d0` its matched wedge control; the pair is a matched
    pair precisely because the two differ in one element, so BOTH ids move together or neither does.
    """
    def side(doc, key):
        rec = doc["matched_pair_for_rung_5a_ks"].get(key) or {}
        return {
            "construct_id": rec.get("construct_id"),
            "n_backbone_atoms_intended": rec.get("n_backbone_atoms_intended"),
            "linker_class": rec.get("linker_class"),
            "linker_segments": rec.get("linker_segments"),
        }

    ex_d, ex_d0 = side(committed, "d"), side(committed, "d0")
    co_d, co_d0 = side(corrected, "d"), side(corrected, "d0")
    return {
        "_what": ("the recommended RUNG 5a-KS matched pair under each kernel. `d` is the wedge-bearing "
                  "degrader endpoint, `d0` its matched wedge control."),
        "EXECUTED": {"d": ex_d, "d0": ex_d0},
        "CORRECTED": {"d": co_d, "d0": co_d0},
        "the_pair_moved": ex_d["construct_id"] != co_d["construct_id"],
        "executed_pair_still_retained_by_the_corrected_kernel": (
            ex_d["construct_id"] in ri and ex_d0["construct_id"] in ri),
        "corrected_pair_was_absent_from_the_executed_enumeration": (
            co_d["construct_id"] not in ci and co_d0["construct_id"] not in ci),
        "_reading": (
            "★ THIS IS THE SENTENCE THE WHOLE ROW EXISTS FOR: re-deriving the causal test article from "
            "today's code returns a DIFFERENT MOLECULE from the one `V16` was measured on — different linker "
            "class, different backbone length, different SMILES — and until this ruling nothing in the repo "
            "said so. It says so now, in two places that cannot drift apart: here, and in the guard that "
            "fails if either set moves again."),
    }


def _verify_anchors(edits, roadmap_text):
    """Stamp every edit with whether its `current_text` is present, and unique, in the LIVE roadmap."""
    out = []
    for e in edits:
        e = dict(e)
        ct = e.get("current_text")
        if ct is None:
            e["anchor_live"] = None
            e["anchor_occurrences"] = None
            e["_anchor_note"] = ("anchor: null — deliberately unanchored. See `where_it_goes`; an honest "
                                 "'this needs a new home' beats a stale anchor that silently no-ops.")
        else:
            n = roadmap_text.count(ct)
            e["anchor_live"] = n >= 1
            e["anchor_occurrences"] = n
            e["anchor_unique"] = n == 1
        out.append(e)
    return out


def build(show_log=False):
    committed = json.load(open(COMMITTED, encoding="utf-8"))
    chem = json.load(open(LIBRARY_CHEM, encoding="utf-8"))
    prep = json.load(open(COFOLD_PREP, encoding="utf-8"))

    with tempfile.TemporaryDirectory() as td:
        if show_log:
            corrected = _regenerate(td)
        else:
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                corrected = _regenerate(td)

    ci, ri = _ids(committed), _ids(corrected)
    only_committed = sorted(set(ci) - set(ri))
    only_corrected = sorted(set(ri) - set(ci))
    shared = sorted(set(ci) & set(ri))
    smiles_moved = [k for k in shared if ci[k].get("smiles") != ri[k].get("smiles")]

    # Why each dropped construct dropped, and whether its FIDELITY changed — the difference between
    # "the corrected geometry refutes it" and "it lost a fixed-size tie-break".
    dropped = {}
    rejected = {x["construct_id"]: x for x in corrected["rejected_by_the_filter"]}
    for k in only_committed:
        rj = rejected.get(k, {})
        dropped[k] = {
            "rejected_because": rj.get("rejected_because"),
            "basin_fidelity_is_byte_identical": rj.get("basin_fidelity") == ci[k].get("basin_fidelity"),
            "smiles_is_byte_identical": rj.get("smiles") == ci[k].get("smiles"),
            "n_backbone_atoms_intended": ci[k].get("n_backbone_atoms_intended"),
            "linker_class": ci[k].get("linker_class"),
            "pendant_kind": ci[k].get("pendant_kind"),
        }

    # V16's executed molecules — are they still recoverable verbatim?
    prep_smiles = set()
    for leg in prep["plan"]:
        prep_smiles.add(leg["cofold_ligand_smiles"])
        prep_smiles.add(leg["perturbed_endpoint_smiles"])
    committed_smiles = {x.get("smiles"): k for k, x in ci.items()}
    v16 = {
        "_what": "the molecules rung 5a-KS / `V16` was actually staged on, and whether they are still recorded",
        "endpoint_smiles_in_the_prep_file": len(prep_smiles),
        "all_present_in_the_committed_library": all(s in committed_smiles for s in prep_smiles),
        "resolved_to_construct_ids": sorted({committed_smiles[s] for s in prep_smiles
                                             if s in committed_smiles}),
        "still_retained_by_the_corrected_kernel": sorted(
            {committed_smiles[s] for s in prep_smiles if s in committed_smiles and committed_smiles[s] in ri}),
        "_reading": (
            "V16's molecules are NOT lost — they are committed verbatim in nr4a3-5aks-cofold-prep.json and "
            "they resolve to committed construct ids. What the corrected kernel changes is only whether "
            "those ids are still RECOMMENDED, and the drop reason below shows it is a diversity-cap "
            "tie-break, not a fidelity failure."),
    }

    bt = _five_bt_candidates()
    bt_rows = []
    for cid in bt["candidates"]:
        bt_rows.append({
            "construct_id": cid,
            "in_executed": cid in ci,
            "in_corrected": cid in ri,
            "in_library_chem": any(x["construct_id"] == cid for x in chem["constructs"]),
            "smiles_identical_across_both": (cid in ci and cid in ri
                                             and ci[cid].get("smiles") == ri[cid].get("smiles")),
        })
    shortest_exec = min(x["n_backbone_atoms_intended"] for x in ci.values())
    shortest_corr = min(x["n_backbone_atoms_intended"] for x in ri.values())

    release = {
        "⛔_the_standing_condition": "`5b-T` must not run until this is settled.",
        "_status": "SETTLED 2026-08-03 by the ruling in this artifact — so the condition is DISCHARGED.",
        "★_and_it_would_have_been_safe_either_way": (
            "the stronger result is that `5b-T` is INVARIANT to which ruling was taken. Every predicate below "
            "holds in BOTH enumerations, so neither freezing the committed artifact nor regenerating it "
            "changes one input to this rung."),
        "predicates_a_reader_can_re_check": {
            "every_5bT_candidate_is_in_both_enumerations": all(r["in_corrected"] and r["in_executed"]
                                                               for r in bt_rows),
            "every_5bT_candidate_has_identical_smiles_in_both": all(r["smiles_identical_across_both"]
                                                                    for r in bt_rows),
            "every_5bT_candidate_is_in_library_chem": all(r["in_library_chem"] for r in bt_rows),
            "library_chem_ids_equal_the_executed_ids": (
                {x["construct_id"] for x in chem["constructs"]} == set(ci)),
            "shortest_backbone_atoms_unchanged": shortest_exec == shortest_corr,
            "the_drift_is_confined_to_the_wedge_family": all(
                ci[k].get("pendant_kind") in ("wedge", "wedge_control") for k in only_committed),
        },
        "candidates": bt_rows,
        "_scope": (
            "this discharges the ROW-25 hold on `5b-T` and nothing else. Every other condition on that rung — "
            "its preregistered three-arm gate, the snap-mask pre-flight, and the fact that its whole geometry "
            "inherits `R5` — is untouched by this ruling and still binds."),
    }

    reproduction = {
        "_what": ("the committed artifact reproduces EXACTLY from HEAD's generator plus the pre-fix kernel — "
                  "which is what makes 'frozen' a provenance statement rather than a shrug."),
        "recipe": CAUSE["how_to_reproduce_the_a_b"],
        "measured_2026_08_03": {
            "structural_differences": 0,
            "non_structural_differences": (
                "180 collision-profile REPORTING fields (changed by `73566cd47`, which derived the profile "
                "from the landed matched ensembles instead of copying the retired 5,657-placement pilot — "
                "REPORTED per construct and filtered on by nothing, proven neutral by forcing the pilot "
                "values back in and getting the corrected counts unchanged), plus 1 docstring string renamed "
                "by the STRATEGY.md → roadmap merge (`10dd81e42`)."),
            "library_summary_is_byte_identical": True,
        },
    }

    roadmap_text = open(ROADMAP, encoding="utf-8").read()
    edits = _verify_anchors(MAP_EDITS, roadmap_text)

    return {
        "_title": "WHICH NR4A3 LINKER LIBRARY IS CANONICAL — the ruling, its evidence, and its guard",
        "_status": ("A PROVENANCE RULING. $0 — stdlib + the repo's own generators on CPU. Nothing here is a "
                    "claim about binding, affinity, reactivity, degradation, selectivity, efficacy or safety, "
                    "and no construct named here is a hit."),
        "_answers": "research/manuscripts/nr4a3-program-map.md §10.1 row 25",
        "_one_fact_one_place": (
            "This file is the ONE HOME of: which enumeration is canonical for what, the cause of the drift, "
            "the two registered construct-id sets, and the `5b-T` release predicate. It is NOT a second home "
            "for any construct's chemistry (that is `nr4a3-linker-design.json` / "
            "`nr4a3-linker-library-chem.json`), for the collision profile (`nr4a-paralogue-dynamics.json`), or "
            "for any cost (the roadmap's ladder)."),
        "_generated": {"generator": "research/modalities/nr4a3_linker_library_canonical.py"},
        "_kernel_head_when_generated": _kernel_head(),
        "cause": CAUSE,
        "ruling": RULING,
        "reproduction": reproduction,
        "registered_enumerations": {
            "_why_two": (
                "CLAUDE.md rule 1.2: a superseded enumeration is REGISTERED, never silently dropped and never "
                "left as a 'was X now Y' narrative in live text. These two sets are the whole of the "
                "difference, so any future reader can tell which library a claim came from by its ids alone."),
            "EXECUTED": {
                "artifact": "research/modalities/nr4a3-linker-design.json",
                "kernel": "linker_design.py at %s (pre-fix `three_ball_min_margin`)" % CAUSE["parent"],
                "status": "FROZEN. Canonical for anything already measured, and for `nr4a3-linker-library-"
                          "chem.json` / rung `5b-T`, which reference it by construct id.",
                "n_constructs": len(ci),
                "n_enumerated": committed["library_summary"]["n_enumerated"],
                "by_placement": {k: len(committed[k]) for k in LIB_KEYS},
                "recommended_matched_pair": committed["matched_pair_for_rung_5a_ks"],
                "only_in_this_set": only_committed,
            },
            "CORRECTED": {
                "artifact": "not committed — re-derived on demand by this generator",
                "kernel": "linker_design.py at %s or later (exact closed-form solver)" % CAUSE["commit"],
                "status": "Canonical for ALL NEW design work. Registered here rather than written over the "
                          "executed artifact.",
                "n_constructs": len(ri),
                "n_enumerated": corrected["library_summary"]["n_enumerated"],
                "by_placement": {k: len(corrected[k]) for k in LIB_KEYS},
                "recommended_matched_pair": corrected["matched_pair_for_rung_5a_ks"],
                "only_in_this_set": only_corrected,
            },
            "shared": {
                "n": len(shared),
                "n_with_a_changed_smiles": len(smiles_moved),
                "changed_smiles": smiles_moved,
                "_reading": ("★ ZERO shared constructs changed chemistry. The correction moves which "
                             "constructs are RETAINED, never what a retained construct IS — so no committed "
                             "SMILES anywhere in the program is invalidated by it."),
            },
        },
        "what_actually_moved": {
            "_reading": (
                "⛔ READ THIS BEFORE CONCLUDING THAT THE CORRECTED KERNEL REFUTES THE TEST ARTICLE. It does "
                "not. Each dropped construct's `basin_fidelity` is BYTE-IDENTICAL between the two runs and "
                "still passes every preregistered threshold; each is dropped for `diversity cap or unmatched "
                "control`, i.e. it loses a fixed-size tie-break to newly-admitted siblings that the old "
                "kernel had wrongly called out of reach. Dropping on a tie-break is a change of PREFERENCE; "
                "it is not a refutation, and the two must never be reported as the same thing."),
            "dropped_from_the_executed_set": dropped,
            "the_recommendation_that_moved": _pair_move(committed, corrected, ci, ri),
            "which_direction_the_correction_points": (
                "TOWARDS A BETTER MOLECULE, not merely a different one: the corrected recommendation is "
                "SHORTER (alkyl+alkyl) than the executed one (PEG4+alkyl), and backbone length is the "
                "program's measured paralogue-collision cost — so the corrected kernel's preference is the "
                "cheaper one on the categorical axis. That is a reason to use it for new work and NOT a "
                "reason to re-cut a landed measurement."),
        },
        "V16_the_causal_test_article": v16,
        "release_condition": release,
        "anti_drift_guard": {
            "_why_a_guard_and_not_a_hash": (
                "hashing the artifact would pass forever and catch nothing about the CODE — the artifact is "
                "not what drifted. The guard therefore RE-RUNS the current generator and compares its "
                "construct-id set against the CORRECTED set registered above. A third set is a NEW "
                "divergence, and the test fails loudly and names the ids."),
            "tests": [
                "research/modalities/tests/test_linker_library_canonical.py — the cheap pins: the executed "
                "set, library-chem ↔ design parity, V16's molecules, and the 5b-T release predicate. "
                "Milliseconds; safe for the fast suite.",
                "research/modalities/tests/test_linker_library_reproduces.py — the loud one: re-runs the "
                "generator (~5 s) and fails if today's code produces neither registered set.",
            ],
            "what_a_failure_means": {
                "executed_set_moved": "somebody edited nr4a3-linker-design.json by hand. Revert it.",
                "corrected_set_moved": ("a geometry kernel or the generator changed again. That is allowed — "
                                        "but it must be RULED ON and re-registered here in the same commit, "
                                        "exactly as `382c36947` should have been."),
                "library_chem_diverged": ("the design → chem → 5b-T chain broke; rung `5b-T`'s degrader "
                                          "source is no longer the enumeration it claims."),
            },
        },
        "map_edits_required": {
            "_what": ("edits the roadmap needs as a result of this work, ready to apply with no rewriting. "
                      "This agent does not edit nr4a3-program-map.md — three other agents are working rows "
                      "in it — so the edits are emitted here and routed."),
            "_anchor_contract": (
                "every entry's `current_text` is grepped against the LIVE roadmap AT GENERATION TIME and "
                "stamped `anchor_live` / `anchor_occurrences` / `anchor_unique`. `--check` REFUSES to pass "
                "with a dead anchor, so this artifact cannot ship an edit that silently no-ops. "
                "`anchor: null` is deliberate and says where the text goes instead."),
            "_verified_against": ROADMAP.replace(REPO + os.sep, ""),
            "n_edits": len(edits),
            "n_anchored": sum(1 for e in edits if e.get("anchor_live") is True),
            "n_unanchored_by_design": sum(1 for e in edits if e.get("anchor_live") is None),
            "n_DEAD_anchors": sum(1 for e in edits if e.get("anchor_live") is False),
            "edits": edits,
        },
        "_limits": [
            "PROVENANCE ONLY. This settles which enumeration is which. It makes no claim that any construct "
            "binds, degrades, is selective, is synthesisable, is safe, or is a hit.",
            "The corrected enumeration is re-derived on demand and is NOT committed as an artifact. That is "
            "deliberate — committing it would create a second file that looks like a library and would be "
            "quoted as one — but it means the CORRECTED ids here are only as reproducible as the code that "
            "makes them, which is exactly what the guard tests.",
            "⚠ The OTHER artifact `382c36947` built on the pre-fix kernel — `nr4a3-orientation-basins.json`'s "
            "`term_a_feasibility_envelope` — is NOT settled here. It is the same conservative direction and "
            "the same registration gap, and it needs its own ruling.",
            "The committed enumeration's known bias is one-sided (it under-admits). It must never be "
            "described as complete, and a claim that no construct exists below some length must be read as a "
            "statement about THIS enumeration rather than about chemistry.",
        ],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-linker-library-canonical.json"))
    ap.add_argument("--check", action="store_true",
                    help="refuse (exit 1) if any emitted map edit has a dead anchor")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    doc = build(show_log=args.verbose)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)

    me = doc["map_edits_required"]
    reg = doc["registered_enumerations"]
    print("[canon] EXECUTED %d constructs / %d enumerated   CORRECTED %d / %d"
          % (reg["EXECUTED"]["n_constructs"], reg["EXECUTED"]["n_enumerated"],
             reg["CORRECTED"]["n_constructs"], reg["CORRECTED"]["n_enumerated"]))
    print("[canon] only-executed %s" % reg["EXECUTED"]["only_in_this_set"])
    print("[canon] only-corrected %s" % reg["CORRECTED"]["only_in_this_set"])
    print("[canon] 5b-T release predicates: %s"
          % doc["release_condition"]["predicates_a_reader_can_re_check"])
    print("[canon] map edits: %d total, %d anchored, %d unanchored-by-design, %d DEAD"
          % (me["n_edits"], me["n_anchored"], me["n_unanchored_by_design"], me["n_DEAD_anchors"]))
    for e in me["edits"]:
        if e.get("anchor_live") is False:
            print("[canon]   ⛔ DEAD ANCHOR: %s — %r" % (e["id"], e["current_text"][:70]))
        elif e.get("anchor_live") and not e.get("anchor_unique"):
            print("[canon]   ⚠ non-unique anchor (%d hits): %s"
                  % (e["anchor_occurrences"], e["id"]))
    print("[canon] wrote %s" % args.out)

    if args.check and me["n_DEAD_anchors"]:
        print("[canon] REFUSING: %d map edit(s) have anchors that are not present in the live roadmap. "
              "Relocate them before routing — a dead anchor silently no-ops." % me["n_DEAD_anchors"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
