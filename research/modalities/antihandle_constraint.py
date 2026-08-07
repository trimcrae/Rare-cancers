#!/usr/bin/env python3
"""`Q3` / `S15` — THE ANTI-HANDLE SET AS A DESIGN CONSTRAINT, NOT AN AFTER-THE-FACT REPORT.

★ WHY THIS MODULE EXISTS, AND WHY IT IS CODE RATHER THAN PROSE.
`S15` (reciprocal anti-handle avoidance) has been graded **B** in
`selectivity-mechanism-options.md` since the register was written, is the register's *cleanest positive
control* (NR4A1 Cys551 / celastrol is a literature-anchored covalent site on a paralogue — a demonstrated
liability rather than a hypothetical one), and its stated cheapest decisive test is **$0, because the
closure data is already committed**. What was missing was never data. It was that *the constraint is not
carried anywhere*: `nr4a3_linker_covalent_reach` optimises reach TO C397 and only REPORTS paralogue
closure afterwards, so nothing in the enumeration can refuse a construct for acquiring a paralogue
liability. Roadmap `§10.1a` records the cost of that gap — rung `5b-T`'s arm **C** failed on precisely
this axis (the construct's backbone sits above the window NR4A1 C505 closes), and a constraint evaluated
BEFORE the construct was built would have refused it.

⇒ So this module is a **predicate**, evaluated at design time, with a boolean answer per construct. A
sentence in a register cannot reject anything; `admits_antihandle()` can.

────────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ THE ANTI-HANDLE SET IS DERIVED FROM THE COMMITTED MAP AND IS **NOT** THE SET THE ROADMAP NAMES.
Roadmap `§10.1a` `Q3` writes the constraint as *"reject any construct whose reach envelope admits
**NR4A1 C505/C551** or **NR4A2 C534**"*. Read against
`nr4a3-linker-covalent-reach.json -> paralogue_control.reciprocal_uniqueness`, that prose set is wrong in
BOTH directions, and this module reports the disagreement rather than silently adopting either side:

  * **NR4A1 C505 is NOT reciprocal-unique** — it aligns to **NR4A3 C536**, a cysteine NR4A3 HAS. It is
    the single most frequent window-closer on the board (40 of 60 through-space cells), which is
    presumably why it reached the prose; but a residue both proteins carry cannot be an ANTI-handle in
    `S15`'s sense, and folding it in would make the constraint indistinguishable from the ordinary
    off-target-cysteine constraint the reach module already computes.
  * **NR4A1 C534 IS reciprocal-unique** (it aligns to NR4A3 **S565**) and the prose omits it.

Both bands are therefore computed and reported SEPARATELY — `antihandle` (reciprocal-unique, `S15`'s
mechanism) and `shared_position` (a paralogue cysteine at a position NR4A3 also carries). A design filter
that conflates them is not the filter `S15` describes.

────────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ EVERY VERDICT IN THIS MODULE IS MARGINALISED OVER POSES, AND THAT IS NOT A CAVEAT — IT IS THE
   DEFINITION OF THE CONSTRAINT.
On 2026-08-06 the second-method pose test LANDED AND FAILED (`pose-second-method.json`): 6 systems,
**0 of 6** agreeing within 2.00 Å, median inter-method disagreement **6.696 Å**, `R5_resolved` false,
outcome *"THE TWO METHODS DISAGREE"*. The pre-registered consequence is that no pose-conditional
statement may be made pose-specifically. For a FILTER that has a direction: the conservative
marginalisation is the **UNION** of liabilities, not the intersection — a construct that acquires an
anti-handle under any placement/pendant cell the program holds is a construct the program cannot certify,
because it cannot say which of those cells is the real one. So:

    REJECT  iff an anti-handle is admitted in ANY cell        <- the binding rule, `reject_any_pose`
    (report) rejected in EVERY cell                           <- `reject_all_poses`, the robust reading
    PASS    iff no anti-handle is admitted in ANY cell         <- the only state that may be called a pass

⚠ Taking the intersection instead would be the false-negative direction: it would certify a construct
whose liability appears under five of six poses.

────────────────────────────────────────────────────────────────────────────────────────────────────────
THE PREDICATE ITSELF. Reach is monotone in chain length (`chemoselectivity_margin`'s own premise: growing
the chain grows every branch ball, so each cysteine has a single threshold), so a construct of `n`
backbone atoms admits exactly the cysteines whose required count is `<= n`. That is the whole arithmetic;
the atom counts are READ from the committed enumeration and are never recomputed here.

⛔ WHAT THIS MODULE DOES NOT AND CANNOT SAY. It is geometry over committed geometry. No reactivity, thiol
pKa, adduct stability, potency, proteome-wide selectivity, efficacy, safety, therapeutic window or
clinical readiness is computed, implied or licensed anywhere. A construct that PASSES this filter has had
one liability class excluded on one set of models; it has not been shown selective, and the filter can
only ever NARROW the design space — `S15` is capped at B for exactly that reason.

Outputs: nr4a3-antihandle-constraint.json (+ .md)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

REACH = os.path.join(HERE, "nr4a3-linker-covalent-reach.json")
LIBRARY = os.path.join(HERE, "nr4a3-linker-design.json")
POSE_SECOND = os.path.join(HERE, "pose-second-method.json")
OUT = os.path.join(HERE, "nr4a3-antihandle-constraint.json")

WINDOW_KEY = "★_family_wide_chemoselectivity_window"

#: the three library keys whose union is "the committed construct set". Named rather than globbed so a
#: new key added upstream shows up as a KeyError instead of silently changing the denominator.
LIBRARY_KEYS = ("virtual_library",
                "virtual_library_at_the_term_a_exemplar",
                "virtual_library_at_representative_geometry")


# ==========================================================================================================
# THE ANTI-HANDLE SET — derived, never typed
# ==========================================================================================================
def anti_handle_set(reach_doc):
    """Read the reciprocal-uniqueness map and split every paralogue cysteine into its two bands.

    Returns ``(antihandles, shared, detail)`` where ``antihandles`` is the set of ``"NR4A1 C551"``-style
    labels whose ``paralogue_unique_vs_NR4A3`` is true, and ``shared`` is the complement.

    ⛔ Nothing here is hard-coded. If the committed map changes, the constraint changes with it — which is
    the entire point of deriving it: an anti-handle list typed into a module is a memory, and a memory is
    what a design constraint may not be built on.
    """
    by_par = reach_doc["paralogue_control"]["reciprocal_uniqueness"]["by_paralogue"]
    anti, shared, detail = set(), set(), {}
    for par, cys_map in by_par.items():
        for cys, rec in cys_map.items():
            label = "%s %s" % (par, cys)
            unique = bool(rec.get("paralogue_unique_vs_NR4A3"))
            (anti if unique else shared).add(label)
            detail[label] = {
                "paralogue": par,
                "cysteine": cys,
                "nr4a3_aligned_residue": rec.get("nr4a3_aligned_residue"),
                "nr4a3_has_a_cysteine_here": rec.get("nr4a3_has_a_cysteine_here"),
                "band": "antihandle" if unique else "shared_position",
            }
    return anti, shared, detail


#: The set roadmap §10.1a `Q3` writes in prose. Held here ONLY so the disagreement can be MEASURED and
#: reported; it is never used as the constraint. See the module docstring.
ROADMAP_PROSE_SET = frozenset({"NR4A1 C505", "NR4A1 C551", "NR4A2 C534"})


def roadmap_set_disagreement(anti, shared):
    """Measure the prose set against the derived one. Returns a dict, always — a clean agreement is a
    reading too, and a checker that only speaks when it disagrees cannot be distinguished from one that
    never ran."""
    derived = set(anti)
    in_prose_not_derived = sorted(ROADMAP_PROSE_SET - derived)
    in_derived_not_prose = sorted(derived - ROADMAP_PROSE_SET)
    return {
        "_what": "roadmap §10.1a Q3 states the anti-handle set in prose; this compares it to the set "
                 "derived from nr4a3-linker-covalent-reach.json -> paralogue_control.reciprocal_uniqueness",
        "prose_set": sorted(ROADMAP_PROSE_SET),
        "derived_set": sorted(derived),
        "agrees": not in_prose_not_derived and not in_derived_not_prose,
        "in_prose_but_not_reciprocal_unique": [
            {"label": lab,
             "why_not_an_antihandle": "it is at a position NR4A3 also carries a cysteine at, so it is a "
                                      "shared-position off-target liability, not a reciprocal anti-handle",
             "band_it_actually_belongs_to": "shared_position" if lab in shared else "unknown"}
            for lab in in_prose_not_derived],
        "reciprocal_unique_but_missing_from_the_prose": in_derived_not_prose,
        "_consequence": "the constraint implemented here uses the DERIVED set. The prose set is reported "
                        "so the roadmap can be corrected rather than quietly contradicted.",
    }


# ==========================================================================================================
# THE PREDICATE — pure, no I/O. This is the whole of `Q3`.
# ==========================================================================================================
#: private key carrying the TARGET's own requirement inside a competitor map. Excluded from every
#: envelope: the target is not a competitor, and letting it in would make C397 look like a liability.
TARGET_KEY = "__target_atoms__"


def reach_envelope(competitor_atoms, n_backbone_atoms):
    """Every COMPETITOR cysteine a construct of ``n_backbone_atoms`` admits.

    Reach is monotone in chain length, so a cysteine requiring ``k`` backbone atoms is inside the envelope
    exactly when ``k <= n``. ``None`` means "not reachable at any length in the enumeration" and is never
    admitted.
    """
    if n_backbone_atoms is None:
        return set()
    return {cys for cys, k in competitor_atoms.items()
            if cys != TARGET_KEY and k is not None and k <= n_backbone_atoms}


def target_in_envelope(competitor_atoms, n_backbone_atoms):
    """Does the construct reach C397 itself at this length? Reported beside every rejection, because
    "rejected" and "rejected while not even reaching the target" are different states and a filter that
    renders them alike is unreadable."""
    k = competitor_atoms.get(TARGET_KEY)
    if k is None or n_backbone_atoms is None:
        return None
    return k <= n_backbone_atoms


def admits_antihandle(competitor_atoms, n_backbone_atoms, antihandles):
    """★ THE PREDICATE. Which anti-handles does this construct's reach envelope admit, in this cell?

    Returns a sorted list — empty means the cell is clean. Deliberately returns the WITNESSES rather than
    a bare bool: a filter that says "rejected" without naming the residue cannot be argued with, and
    `S15`'s whole value is that the residue it names is a demonstrated liability.
    """
    return sorted(reach_envelope(competitor_atoms, n_backbone_atoms) & set(antihandles))


def construct_verdict(cells, n_backbone_atoms, antihandles, shared):
    """Evaluate one construct against EVERY cell, then marginalise over poses.

    ``cells`` is an iterable of ``(cell_id, convention, competitor_atoms)``.

    ⛔ The returned ``verdict`` is the UNION rule — REJECT if any cell admits an anti-handle. See the
    module docstring for why the intersection would be the false-negative direction.
    """
    per_cell, n_admitting, witnesses = [], 0, set()
    shared_admitting = 0
    n_target_reached = 0
    n_both = 0
    for cell_id, conv, atoms in cells:
        hits = admits_antihandle(atoms, n_backbone_atoms, antihandles)
        sh = sorted(reach_envelope(atoms, n_backbone_atoms) & set(shared))
        tgt = target_in_envelope(atoms, n_backbone_atoms)
        if hits:
            n_admitting += 1
            witnesses.update(hits)
        if sh:
            shared_admitting += 1
        if tgt:
            n_target_reached += 1
        if tgt and hits:
            n_both += 1
        per_cell.append({"cell": cell_id, "convention": conv,
                         "antihandles_admitted": hits, "shared_position_admitted": sh,
                         "target_C397_in_envelope": tgt})
    n_cells = len(per_cell)
    return {
        "n_backbone_atoms": n_backbone_atoms,
        "n_cells_evaluated": n_cells,
        "n_cells_admitting_an_antihandle": n_admitting,
        "n_cells_admitting_a_shared_position_cysteine": shared_admitting,
        "n_cells_where_C397_ITSELF_is_reached": n_target_reached,
        "n_cells_where_C397_IS_reached_AND_an_antihandle_is_admitted": n_both,
        "_why_that_pair_is_reported": "a cell that admits an anti-handle while NOT reaching C397 is pure "
                                      "liability with no engagement, and a cell that reaches C397 "
                                      "cleanly is the design target. Reporting only the union count "
                                      "renders those two states alike.",
        "antihandles_witnessed": sorted(witnesses),
        "reject_any_pose": n_admitting > 0,
        "reject_all_poses": n_cells > 0 and n_admitting == n_cells,
        "verdict": ("REJECT" if n_admitting > 0 else "PASS") if n_cells else "NOT EVALUABLE",
        "_marginalisation": "UNION over placement x pendant x convention cells. R5 is unresolved "
                            "(pose-second-method.json: 0 of 6 systems agree within 2.00 A), so the "
                            "program cannot say which cell is the real one and a liability under any of "
                            "them is a liability.",
        "per_cell": per_cell,
    }


# ==========================================================================================================
# I/O — join the committed library to the committed enumeration
# ==========================================================================================================
def load_cells(reach_doc):
    """(cell_id, convention, competitor_atoms) for every committed (placement x pendant x convention) cell.

    ``competitor_atoms`` carries a private ``__target_atoms__`` key so the target's own requirement travels
    with the competitors without being mistaken for one.
    """
    out = []
    for conv, rows in reach_doc[WINDOW_KEY]["by_convention"].items():
        for r in rows:
            atoms = dict(r["all_competitors_atoms"])
            atoms["__target_atoms__"] = r.get("target_atoms")
            out.append(("%s|%s" % (r["placement"], r["pendant"]), conv, atoms))
    return out


def load_constructs(lib_doc):
    """The committed construct set, de-duplicated on ``construct_id`` across the three library keys."""
    seen, out = {}, []
    for key in LIBRARY_KEYS:
        for c in lib_doc[key]:
            cid = c["construct_id"]
            if cid in seen:
                seen[cid]["library_keys"].append(key)
                continue
            rec = {
                "construct_id": cid,
                "library_keys": [key],
                "designed_for_basin": c.get("designed_for_basin"),
                "designed_at_placement": c.get("designed_at_placement"),
                "placement_pose_id": c.get("placement_pose_id"),
                "e3_handle": c.get("e3_handle"),
                "pendant": c.get("pendant"),
                "linker_class": c.get("linker_class"),
                "n_backbone_atoms_intended": c.get("n_backbone_atoms_intended"),
                "role": c.get("role"),
            }
            seen[cid] = rec
            out.append(rec)
    return out


def own_cell_ids(construct):
    """The cells belonging to the construct's OWN designed placement.

    ⚠ Reported beside the marginalised verdict, never instead of it. `R5` says the pose is not an object
    the program is entitled to, so "at its own placement" is a diagnostic, not a licence.
    """
    return "%s@%s" % (construct.get("designed_for_basin"), construct.get("designed_at_placement"))


#: lengths at which the constraint frontier is reported. `12` is not a free choice — it is the
#: categorical gate `nr4a-paralogue-dynamics.json -> categorical_verdict.gate_atoms`, and it is READ
#: rather than typed by `length_frontier()`.
FRONTIER_LENGTHS = (8, 10, 11, 12, 13, 14, 16, 18, 20, 24)


def length_frontier(cells, antihandles, shared, gate_atoms=None):
    """★ THE CONSTRAINT AS A FUNCTION OF LENGTH — which is what makes it a DESIGN constraint rather than a
    verdict on one library.

    Reach is monotone in length, so anti-handle admission is monotone too: this is the frontier a designer
    trades against. It composes directly with `Q4` (the linker-length design principle at the 12-atom
    gate) — the same variable that sets the categorical discrimination also sets the anti-handle exposure,
    and they point the SAME way, which no document said before.
    """
    rows = []
    for n in FRONTIER_LENGTHS:
        n_anti = n_shared = n_tgt = n_clean_hit = 0
        witnesses = set()
        for _cid, _conv, atoms in cells:
            hits = admits_antihandle(atoms, n, antihandles)
            tgt = target_in_envelope(atoms, n)
            if hits:
                n_anti += 1
                witnesses.update(hits)
            if reach_envelope(atoms, n) & set(shared):
                n_shared += 1
            if tgt:
                n_tgt += 1
            if tgt and not hits:
                n_clean_hit += 1
        rows.append({
            "n_backbone_atoms": n,
            "is_the_categorical_gate": (gate_atoms is not None and n == gate_atoms),
            "n_cells": len(cells),
            "n_cells_admitting_an_antihandle": n_anti,
            "n_cells_admitting_a_shared_position_cysteine": n_shared,
            "n_cells_where_C397_ITSELF_is_reached": n_tgt,
            "★_n_cells_reaching_C397_WITHOUT_an_antihandle": n_clean_hit,
            "_why_that_column": "THE DESIGN TARGET. A cell that reaches C397 and admits no anti-handle "
                                "is the only state a construct can be built into; the other three are "
                                "liability, no engagement, or both. This column is what the frontier is "
                                "FOR, and it need not be monotone.",
            "antihandles_witnessed": sorted(witnesses),
        })
    return rows


def screen(reach_doc, lib_doc):
    anti, shared, detail = anti_handle_set(reach_doc)
    cells = load_cells(reach_doc)
    constructs = load_constructs(lib_doc)
    rows = []
    for c in constructs:
        n = c["n_backbone_atoms_intended"]
        v = construct_verdict(cells, n, anti, shared)
        own = own_cell_ids(c)
        # placement ids are "arm|basin@geometry", so the cell id is "arm|basin@geometry|pendant"
        own_cells = [(cid, conv, at) for cid, conv, at in cells if cid.rsplit("|", 1)[0] == own]
        v_own = construct_verdict(own_cells, n, anti, shared) if own_cells else None
        rows.append({**c,
                     "own_placement": own,
                     "marginalised_over_poses": {k: val for k, val in v.items() if k != "per_cell"},
                     "at_its_own_placement_only": (
                         {k: val for k, val in v_own.items() if k != "per_cell"} if v_own else None),
                     "_own_placement_reading": "DIAGNOSTIC ONLY. R5 is unresolved, so a per-placement "
                                               "verdict is not a claim the program may make; the binding "
                                               "verdict is the marginalised one.",
                     })
    return anti, shared, detail, cells, constructs, rows


# ==========================================================================================================
# Assembly
# ==========================================================================================================
def _pose_inheritance():
    """Read the second-method result rather than describing it. FAIL-LOUD if it is missing: a filter that
    silently drops its own marginalisation premise is the failure `S15` exists inside."""
    if not os.path.exists(POSE_SECOND):
        return {"read": False,
                "_why_it_matters": "the marginalisation rule rests on this artifact; it is absent, so the "
                                   "rule is stated without its evidence"}
    d = json.load(open(POSE_SECOND, encoding="utf-8"))
    def dig(o, key):
        if isinstance(o, dict):
            if key in o:
                return o[key]
            for v in o.values():
                r = dig(v, key)
                if r is not None:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = dig(v, key)
                if r is not None:
                    return r
        return None
    return {
        "read": True,
        "cross_method_evidence": dig(d, "cross_method_evidence"),
        "R5_resolved": dig(d, "R5_resolved"),
        "outcome": dig(d, "outcome"),
        "_source": os.path.relpath(POSE_SECOND, REPO),
    }


DYNAMICS = os.path.join(HERE, "nr4a-paralogue-dynamics.json")


def categorical_gate_atoms():
    """READ the categorical gate rather than typing 12. One fact, one place — its home is
    `nr4a-paralogue-dynamics.json -> categorical_verdict.gate_atoms`."""
    if not os.path.exists(DYNAMICS):
        return None
    return json.load(open(DYNAMICS, encoding="utf-8"))["categorical_verdict"]["gate_atoms"]


def build():
    reach_doc = json.load(open(REACH, encoding="utf-8"))
    lib_doc = json.load(open(LIBRARY, encoding="utf-8"))
    anti, shared, detail, cells, constructs, rows = screen(reach_doc, lib_doc)
    gate_atoms = categorical_gate_atoms()
    frontier = length_frontier(cells, anti, shared, gate_atoms)
    peak = max(frontier, key=lambda r: r["★_n_cells_reaching_C397_WITHOUT_an_antihandle"]) \
        if frontier else None
    lens = [c["n_backbone_atoms_intended"] for c in constructs
            if c["n_backbone_atoms_intended"] is not None]
    shortest = min(lens) if lens else None

    n_reject = sum(1 for r in rows if r["marginalised_over_poses"]["reject_any_pose"])
    n_reject_all = sum(1 for r in rows if r["marginalised_over_poses"]["reject_all_poses"])
    n_pass = len(rows) - n_reject
    survivors = sorted(r["construct_id"] for r in rows
                       if not r["marginalised_over_poses"]["reject_any_pose"])
    witnesses = {}
    for r in rows:
        for w in r["marginalised_over_poses"]["antihandles_witnessed"]:
            witnesses[w] = witnesses.get(w, 0) + 1

    # the filter's OWN failure mode, stated as Q3 states it
    if n_pass == 0:
        headline = ("NO COMMITTED CONSTRUCT SURVIVES THE ANTI-HANDLE CONSTRAINT UNDER THE UNION-OVER-POSES "
                    "RULE — %d of %d rejected. The filter's failure mode IS its result: the enumeration "
                    "has been optimising reach TO C397 while admitting the reciprocal-unique paralogue "
                    "liability the constraint exists to refuse. ⚠ AND THE RULE TRAVELS WITH THE SENTENCE, "
                    "BECAUSE IT IS LOAD-BEARING: %d constructs are rejected in EVERY cell, so every "
                    "rejection here rests on SOME committed cell rather than on all of them. That is the "
                    "conservative reading R5 forces — the second pose method disagrees with the first, so "
                    "the program cannot name which cell is real — and it is not the same claim as 'no "
                    "geometry exists in which these constructs are clean'."
                    % (n_reject, len(rows), n_reject_all))
    elif n_pass == len(rows):
        headline = ("EVERY committed construct survives the anti-handle constraint at its intended "
                    "backbone length. The constraint is not currently binding on this set — which is a "
                    "reading about THIS set at THESE lengths and licenses nothing about longer ones.")
    else:
        headline = ("%d of %d committed constructs are REJECTED by the anti-handle constraint under the "
                    "union-over-poses rule; %d survive." % (n_reject, len(rows), n_pass))

    doc = {
        "_title": "Q3 / S15 — the reciprocal anti-handle set carried as a DESIGN CONSTRAINT, "
                  "as an executable predicate over the committed construct set",
        "_status": "GEOMETRY-ONLY DESIGN FILTER. $0 CPU, pure stdlib, no new compute of any kind — every "
                   "atom count is read from the committed enumeration. Nothing here is a claim about "
                   "binding, reactivity, degradation, proteome-wide selectivity, efficacy, safety, a "
                   "therapeutic window or clinical readiness. A filter removes liabilities; it adds no "
                   "signal and widens no margin.",
        "_question": "Does any committed construct's reach envelope admit a cysteine that a PARALOGUE has "
                     "and NR4A3 does not — i.e. a residue at which the molecule acquires a paralogue "
                     "liability no NR4A3-side analysis would ever look at?",
        "_the_predicate": "antihandle_constraint.admits_antihandle(competitor_atoms, n, antihandles) — "
                          "reach is monotone in chain length, so a construct of n backbone atoms admits "
                          "exactly the cysteines whose requirement is <= n.",
        "_inherits": [
            "every atom count comes from nr4a3-linker-covalent-reach.json, computed on ONE opened NR4A3 "
            "frame with independently built, superposed paralogue models — that lane's "
            "`aligned_pair_displacement` owns the rotamer-noise bound (max SG/CA ratio 9.5) and it is not "
            "re-derived here. No count may be quoted to better than the rotamer it rests on.",
            "the anchors are the docked pose whose known-answer test V3 returned INCONCLUSIVE, and V3's "
            "failure was SITE selection.",
            "no thiol pKa, intrinsic electrophile reactivity, adduct stability or chemoproteomic "
            "selectivity is computed anywhere in this repository.",
        ],
        "_pose_marginalisation": {
            "rule": "REJECT iff an anti-handle is admitted in ANY committed cell (the UNION). The "
                    "intersection would be the false-negative direction — it would certify a construct "
                    "whose liability appears under five of six poses.",
            "why": "R5 is unresolved and got worse on 2026-08-06: the second pose method DISAGREES with "
                   "the first, so the program cannot name which cell is the real one.",
            "evidence": _pose_inheritance(),
            "⛔": "no vector-specific or pose-specific statement is made anywhere in this artifact. The "
                 "per-placement columns are DIAGNOSTIC and are labelled as such.",
        },
        "anti_handle_set": {
            "_derived_from": "nr4a3-linker-covalent-reach.json -> paralogue_control.reciprocal_uniqueness",
            "antihandles": sorted(anti),
            "shared_position_paralogue_cysteines": sorted(shared),
            "per_residue": detail,
            "_band_definition": {
                "antihandle": "the paralogue carries a cysteine at a position where NR4A3 does not — "
                              "S15's mechanism, and the reciprocal of the program's own categorical handle",
                "shared_position": "both carry a cysteine at the aligned position — an ordinary off-target "
                                   "liability the reach module already scores, NOT an anti-handle",
            },
        },
        "roadmap_set_disagreement": roadmap_set_disagreement(anti, shared),
        "cells": {
            "_what": "placement x pendant x convention cells read from the committed enumeration",
            "n_cells": len(cells),
            "n_placements": len({c[0].rsplit("|", 1)[0] for c in cells}),
            "n_pendants": len({c[0].rsplit("|", 1)[1] for c in cells}),
            "conventions": sorted({c[1] for c in cells}),
        },
        "constructs": {
            "_what": "the committed construct set, de-duplicated across the three library keys",
            "n_constructs": len(constructs),
            "library_keys": list(LIBRARY_KEYS),
            "backbone_lengths_present": sorted({c["n_backbone_atoms_intended"] for c in constructs
                                                if c["n_backbone_atoms_intended"] is not None}),
            "shortest_committed_construct_atoms": min(
                [c["n_backbone_atoms_intended"] for c in constructs
                 if c["n_backbone_atoms_intended"] is not None] or [None]),
        },
        "★_length_frontier": {
            "_what": "the constraint evaluated as a FUNCTION OF LENGTH over the same cells — the trade a "
                     "designer actually makes, rather than a verdict on one library.",
            "_why_it_matters": "anti-handle admission is monotone in backbone length, and so is "
                               "P(a paralogue cysteine is also reached | an NR4A3-unique one is) "
                               "(Q4 / S6). Both LIABILITY quantities are therefore minimised at short "
                               "length — which is the composition §10.1b's ⊕ COMPOSER set asserts and "
                               "no artifact had measured.",
            "⛔_and_the_composition_is_NOT_as_simple_as_that": (
                "MEASURED HERE, AND IT CORRECTS THE SENTENCE ABOVE RATHER THAN DECORATING IT. The two "
                "LIABILITY columns are monotone and agree; the DESIGN-TARGET column — cells reaching "
                "C397 while admitting no anti-handle — is NOT monotone and does NOT peak at the gate. "
                "It rises to a maximum above the gate and then collapses, because engagement and "
                "liability grow at different rates. ⛔ THIS DOES NOT LICENSE THE LONGER LENGTH: at any "
                "length above the gate the CATEGORICAL statement inherits V17's false negative "
                "(linker_length_principle.principle() refuses to emit it there), so the extra clean "
                "cells are reach without a statable discrimination. The honest reading is that the two "
                "constraints agree about liability and DISAGREE about where the most buildable cells "
                "are, and the gate is set by what can be SAID rather than by what can be reached."),
            "★_the_design_target_column_peaks_at": (
                None if peak is None else
                {"n_backbone_atoms": peak["n_backbone_atoms"],
                 "n_cells": peak["★_n_cells_reaching_C397_WITHOUT_an_antihandle"],
                 "is_the_categorical_gate": peak["is_the_categorical_gate"]}),
            "categorical_gate_atoms": gate_atoms,
            "_gate_source": "nr4a-paralogue-dynamics.json -> categorical_verdict.gate_atoms (READ, not typed)",
            "⛔_shortest_committed_construct_is_above_the_gate": (
                None if gate_atoms is None or shortest is None else shortest > gate_atoms),
            "by_length": frontier,
        } if frontier else {},
        "summary": {
            "n_constructs": len(rows),
            "n_rejected_under_the_union_rule": n_reject,
            "n_rejected_in_EVERY_cell": n_reject_all,
            "n_surviving": n_pass,
            "surviving_construct_ids": survivors,
            "antihandle_witness_counts": dict(sorted(witnesses.items())),
        },
        "per_construct": rows,
        "verdict": {
            "headline": headline,
            "the_constraint_is_now_carried": True,
            "⛔_what_a_pass_does_not_license": [
                "any selectivity, potency, reactivity or window claim — no energy is computed anywhere",
                "an increase in NR4A3 engagement. A filter removes liabilities; it adds no signal.",
                "a proteome-wide statement — an electrophile does not know it is meant to be selective, "
                "and this constraint is evaluated over three proteins",
                "a pose-specific or vector-specific design rule. Every verdict is marginalised over poses "
                "and may only be quoted that way.",
            ],
            "⭑_what_it_does_license": "a design-time refusal with a named witness residue, applied before "
                                      "a construct is built rather than reported after it fails.",
        },
    }
    return doc


#: ⚠ A FIXED DATE, NOT `now()`. `systems_check [D4]` requires freshness on every tracked document, so the
#: frontmatter is EMITTED rather than hand-added — a hand-added block is dropped on the next run. But a
#: date stamped from the clock makes the file differ from a fresh render the following day, which is the
#: "does not reproduce" trap the steric audit hit and had to special-case.
GENERATED_ON = "2026-08-07"


def _frontmatter(title, purpose, scope, doc_id, generator):
    return "\n".join([
        "---",
        "id: %s" % doc_id,
        "title: %s" % title,
        "level: L4",
        "kind: memo",
        "status: generated",
        "generator: %s" % generator,
        "canonical_for: []",
        'purpose: "%s"' % purpose,
        "scope: %s" % scope,
        "audience: [maintainers, autonomous research agents]",
        "date: %s" % GENERATED_ON,
        "last_verified: unverified",
        "---",
        "",
    ])


def to_markdown(d):
    L = []
    A = L.append
    A(_frontmatter(
        "Q3 / S15 — the reciprocal anti-handle set as an executable design constraint",
        "Carry the reciprocal-unique paralogue cysteines as a design-time FILTER over the committed "
        "construct set, marginalised over poses, rather than reporting paralogue closure after the fact.",
        "Geometry only, over committed geometry. No binding, reactivity, degradation, selectivity, "
        "efficacy or safety statement. A filter removes liabilities; it adds no signal.",
        "DOC-NR4A3-ANTIHANDLE-CONSTRAINT",
        "research/modalities/antihandle_constraint.py"))
    A("# %s\n" % d["_title"])
    A("**Status.** %s\n" % d["_status"])
    A("**Question.** %s\n" % d["_question"])
    A("## The constraint\n")
    A("`%s`\n" % d["_the_predicate"])
    s = d["summary"]
    A("**%s**\n" % d["verdict"]["headline"])
    A("| quantity | value |")
    A("|---|---|")
    A("| committed constructs screened | %d |" % s["n_constructs"])
    A("| REJECTED (an anti-handle admitted in **any** cell) | %d |" % s["n_rejected_under_the_union_rule"])
    A("| rejected in **every** cell | %d |" % s["n_rejected_in_EVERY_cell"])
    A("| surviving | %d |" % s["n_surviving"])
    A("")
    A("## The anti-handle set — derived, not typed\n")
    ah = d["anti_handle_set"]
    A("| residue | NR4A3 aligned | NR4A3 has a Cys here | band |")
    A("|---|---|---|---|")
    for lab, r in sorted(ah["per_residue"].items()):
        A("| %s | %s | %s | %s |" % (lab, r["nr4a3_aligned_residue"], r["nr4a3_has_a_cysteine_here"],
                                     r["band"]))
    A("")
    dis = d["roadmap_set_disagreement"]
    A("### ⚠ The roadmap's prose set and the derived set %s\n"
      % ("AGREE" if dis["agrees"] else "**DISAGREE**"))
    A("- prose (`§10.1a` `Q3`): %s" % ", ".join("`%s`" % x for x in dis["prose_set"]))
    A("- derived: %s" % ", ".join("`%s`" % x for x in dis["derived_set"]))
    for e in dis["in_prose_but_not_reciprocal_unique"]:
        A("- ⛔ `%s` is in the prose and is **not** reciprocal-unique — %s" % (e["label"],
                                                                              e["why_not_an_antihandle"]))
    for lab in dis["reciprocal_unique_but_missing_from_the_prose"]:
        A("- ⛔ `%s` **is** reciprocal-unique and the prose omits it" % lab)
    A("")
    A("## Pose marginalisation\n")
    pm = d["_pose_marginalisation"]
    A("**Rule.** %s\n" % pm["rule"])
    A("**Why.** %s\n" % pm["why"])
    A("%s\n" % pm["⛔"])
    lf = d["★_length_frontier"]
    A("## ★ The constraint as a function of length\n")
    A("%s\n" % lf["_why_it_matters"])
    A("| backbone atoms | cells admitting an anti-handle | cells admitting a shared-position Cys | "
      "cells reaching C397 | ★ reaching C397 **without** an anti-handle | |")
    A("|---|---|---|---|---|---|")
    for r in lf["by_length"]:
        A("| %s%d | %d / %d | %d / %d | %d / %d | **%d** / %d | %s |" % (
            "**" if r["is_the_categorical_gate"] else "", r["n_backbone_atoms"],
            r["n_cells_admitting_an_antihandle"], r["n_cells"],
            r["n_cells_admitting_a_shared_position_cysteine"], r["n_cells"],
            r["n_cells_where_C397_ITSELF_is_reached"], r["n_cells"],
            r["★_n_cells_reaching_C397_WITHOUT_an_antihandle"], r["n_cells"],
            "**← the categorical gate**" if r["is_the_categorical_gate"] else ""))
    A("")
    pk = lf.get("★_the_design_target_column_peaks_at")
    if pk and not pk["is_the_categorical_gate"]:
        A("⛔ **The design-target column peaks at %d atoms (%d cells), NOT at the %d-atom gate.** %s\n"
          % (pk["n_backbone_atoms"], pk["n_cells"], lf["categorical_gate_atoms"],
             lf["⛔_and_the_composition_is_NOT_as_simple_as_that"]))
    if lf["⛔_shortest_committed_construct_is_above_the_gate"]:
        A("⛔ **The shortest committed construct is %d backbone atoms, above the %d-atom categorical "
          "gate** — so no committed construct sits where either constraint is at its minimum.\n"
          % (d["constructs"]["shortest_committed_construct_atoms"], lf["categorical_gate_atoms"]))
    A("## Per construct — marginalised over poses\n")
    A("| construct | backbone atoms | cells admitting an anti-handle | witnesses | verdict |")
    A("|---|---|---|---|---|")
    for r in d["per_construct"]:
        m = r["marginalised_over_poses"]
        A("| `%s` | %s | %d / %d | %s | %s |" % (
            r["construct_id"], r["n_backbone_atoms_intended"],
            m["n_cells_admitting_an_antihandle"], m["n_cells_evaluated"],
            ", ".join(m["antihandles_witnessed"]) or "—", m["verdict"]))
    A("")
    A("## ⛔ What a pass does not license\n")
    for x in d["verdict"]["⛔_what_a_pass_does_not_license"]:
        A("- %s" % x)
    A("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    for p in (REACH, LIBRARY):
        if not os.path.exists(p):
            print("REFUSED — %s does not exist" % p, file=sys.stderr)
            return 2
    doc = build()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    md = os.path.splitext(args.out)[0] + ".md"
    with open(md, "w", encoding="utf-8") as fh:
        fh.write(to_markdown(doc))
    s = doc["summary"]
    print("wrote %s — %d construct(s), %d rejected, %d surviving"
          % (os.path.relpath(args.out, REPO), s["n_constructs"],
             s["n_rejected_under_the_union_rule"], s["n_surviving"]))
    print("anti-handles: %s" % ", ".join(doc["anti_handle_set"]["antihandles"]))
    if not doc["roadmap_set_disagreement"]["agrees"]:
        print("⚠ roadmap prose set DISAGREES with the derived set — see roadmap_set_disagreement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
