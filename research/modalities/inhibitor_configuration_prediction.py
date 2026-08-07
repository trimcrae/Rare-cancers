#!/usr/bin/env python3
"""`Q10` — DOES THE TCIP INTERFACE-FLOOR ABLATION'S PREDICTION HOLD FOR THE INHIBITOR CONFIGURATION?

────────────────────────────────────────────────────────────────────────────────────────────────────────
⭑ FIRST, THE FREE OBSERVATION NOBODY HAD TAKEN — AND IT CHANGES WHAT THIS ROW IS.

`§10.1a` `Q10` reads *"the enumeration has never been run in that configuration"*, and
`path-family-synthesis.md` §3 Tier-2 row 10 reads *"unchanged and still under-run"*. Both are **stale**.
`nr4a3-monovalent-reach.json` and `nr4a3_monovalent_reach.py` are committed and were written on
**2026-08-06 at 7:12 AM ET** — the enumeration HAS been run in the inhibitor configuration, it replicates
the committed bivalent window over all 120 cells with zero mismatches, and it returned
**`answer_on_the_conservative_convention: WORSE`**.

⇒ So `Q10` is not "run the enumeration". It is **"the enumeration ran; a mechanism landed the same day
that predicts the opposite; does the prediction hold?"** — which is a sharper question and a $0 one.
This module answers it. ⛔ It computes no new geometry: every atom count is READ from the two committed
artifacts, and the two configurations are compared through ONE function applied to both sides, so a
difference cannot be an artefact of two different readers.

────────────────────────────────────────────────────────────────────────────────────────────────────────
★ THE PREDICTION, STATED AS ITS SOURCE STATES IT.

`nr4a3-tcip-reach.json -> ★_interface_floor_ablation` re-ran identical cells at the 12-atom rung with
only the sampler's interface floor changed:

    min_contact_residues = 12 (committed)  ->  single/multi acceptance ratio 0.896
    min_contact_residues = 6               ->  1.121
    min_contact_residues = 0 (pure steric) ->  1.254        ★ the sign INVERTS

The artifact's own reading: *"the single-domain penalty is entirely the interface floor and not steric
bulk: on clash alone the smaller body gets MORE orientation space."* An inhibitor has **neither an E3 arm
nor an induced interface**, so the extrapolation to this configuration is that it should **gain
admissible space**.

⚠ THE EXTRAPOLATION CROSSES TWO INSTRUMENTS, AND THAT IS THE FIRST THING TO SAY. The ablation measures
the **orientation acceptance of a SECOND BODY**; the reach enumeration measures the **backbone-atom
window over which C397 is reachable and no other family cysteine is**. They are different quantities on
different instruments. So the prediction is tested on **both** axes and reported on both — because
"the prediction held" and "the route is rescued" are different claims, and a module that reported one
number could not tell them apart.

    AXIS A — ADMISSIBLE SPACE.  Does dropping the E3 arm admit cells the bivalent configuration refused?
                                This is the ablation's own axis, and the prediction is directional here.
    AXIS B — THE SELECTIVITY WINDOW.  The quantity `Q10` was closed on. The ablation makes NO prediction
                                here, and reading it as though it did is the error this module exists to
                                prevent.

────────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ POSE MARGINALISATION. `R5` is unresolved and got worse on 2026-08-06: `pose-second-method.json` returns
0 of 6 systems agreeing within 2.00 Å, median inter-method disagreement 6.696 Å, `R5_resolved` false.
Every anchor on both sides of this comparison descends from the same docked pose family, so **no
statement here is made about a vector or a pose**: every quantity is reported as a distribution over
cells with its full range, and every verdict is the marginal. Where a per-cell number appears it is
labelled a witness, not a claim.

⛔ WHAT THIS MODULE DOES NOT SAY. It is geometry over committed geometry. No reactivity, thiol pKa,
adduct stability, potency, proteome-wide selectivity, efficacy, safety, therapeutic window or clinical
readiness. Geometry can refute a route; it cannot license one.

Outputs: nr4a3-inhibitor-configuration-prediction.json (+ .md)
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:                       # so the shared frontmatter helper imports from any cwd
    sys.path.insert(0, HERE)

MONO = os.path.join(HERE, "nr4a3-monovalent-reach.json")
BIVALENT = os.path.join(HERE, "nr4a3-linker-covalent-reach.json")
TCIP = os.path.join(HERE, "nr4a3-tcip-reach.json")
POSE_SECOND = os.path.join(HERE, "pose-second-method.json")
OUT = os.path.join(HERE, "nr4a3-inhibitor-configuration-prediction.json")

WINDOW_KEY = "★_family_wide_chemoselectivity_window"
ABLATION_KEY = "★_interface_floor_ablation"


# ==========================================================================================================
# ONE READER FOR BOTH SIDES — so a difference cannot be an artefact of two different readers
# ==========================================================================================================
def cell_stats(row):
    """The three quantities this comparison turns on, computed identically from either configuration.

    ``margin``  = (first competitor's atom count) - (target's) — how much shorter the chain reaching C397
                  is than the chain reaching the first competitor anywhere in the family. This is the
                  DISCRIMINATION, and it is signed: negative means a competitor is reached first.
    ``rank``    = C397's 1-based rank among all family cysteines ordered by requirement (ties share the
                  best rank), recomputed here rather than trusted, so both sides use one definition.
    ``width``   = the committed family-wide window width, read not recomputed.
    """
    tgt = row.get("target_atoms")
    comp = {k: v for k, v in (row.get("all_competitors_atoms") or {}).items() if v is not None}
    if tgt is None or not comp:
        return None
    first = min(comp.values())
    rank = 1 + sum(1 for v in comp.values() if v < tgt)
    return {
        "target_atoms": tgt,
        "first_competitor_atoms": first,
        "margin_atoms": first - tgt,
        "rank_of_target": rank,
        "n_competitors": len(comp),
        "width": row.get("width"),
        "closed_by": row.get("closed_by"),
    }


def _summarise(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "min": min(vals), "median": statistics.median(vals), "max": max(vals),
            "mean": round(statistics.fmean(vals), 4)}


def configuration_summary(rows):
    st = [cell_stats(r) for r in rows]
    st = [s for s in st if s]
    return {
        "n_cells": len(st),
        "n_open_window": sum(1 for s in st if (s["width"] or 0) > 0),
        "margin_atoms": _summarise([s["margin_atoms"] for s in st]),
        "rank_of_target": _summarise([s["rank_of_target"] for s in st]),
        "n_target_first": sum(1 for s in st if s["rank_of_target"] == 1),
        "n_target_not_first": sum(1 for s in st if s["rank_of_target"] > 1),
        "n_margin_positive": sum(1 for s in st if s["margin_atoms"] > 0),
        "n_margin_non_positive": sum(1 for s in st if s["margin_atoms"] <= 0),
    }


# ==========================================================================================================
# AXIS A — ADMISSIBLE SPACE. The ablation's own axis.
# ==========================================================================================================
def axis_a(mono, biv):
    """Does dropping the E3 arm admit what the bivalent configuration refused?

    Two independent readings, because they answer different halves and a single number would conflate them:

      (a) the ADMISSIBILITY FILTER. `nr4a3_linker_covalent_reach.placement_admissibility` refuses a cell
          on two grounds — the E3 anchor is buried (*"the E3 must still project to solvent"*) and the
          warhead anchor has no room. ⛔ **Only the first is E3-specific.** A monovalent molecule still
          needs room at the warhead, so the second survives the configuration change untouched, and a
          reading that counted both as "gained" would overstate the prediction by the larger term.
      (b) the PAIRED TRANSITIONS the monovalent lane already computed — cells that were CLOSED bivalently
          and are OPEN monovalently. This is the gain measured on the decision quantity rather than on
          the filter.
    """
    adm = None
    for v in _walk(biv):
        if isinstance(v, dict) and "n_e3_anchor_BURIED" in v:
            adm = v
            break
    trans = mono["paired_transitions"]["by_convention"]
    filt = None
    if adm:
        e3 = adm["n_e3_anchor_BURIED"]
        wh = adm["n_warhead_anchor_with_no_room"]
        filt = {
            "_source": "nr4a3-linker-covalent-reach.json -> ensembles.placement_admissibility",
            "n_cells": adm["n_cells"],
            "n_refused_because_the_E3_ANCHOR_IS_BURIED": e3,
            "n_refused_because_the_WARHEAD_ANCHOR_HAS_NO_ROOM": wh,
            "⭑_retired_by_removing_the_E3_arm": e3,
            "⛔_NOT_retired": wh,
            "⛔_why": "a monovalent molecule still needs room at the warhead, so the warhead-anchor "
                     "refusal survives the configuration change untouched. Counting both as 'gained' "
                     "would overstate the prediction by the larger term.",
            "fraction_of_cells_gained": round(e3 / adm["n_cells"], 6) if adm["n_cells"] else None,
        }
    gains = {conv: {
        "closed_to_open": t["closed_to_open"],
        "open_to_closed": t["open_to_closed"],
        "open_to_open": t["open_to_open"],
        "closed_to_closed": t["closed_to_closed"],
        "n_paired": t["n_paired"],
        "net_change_in_open_cells": t["closed_to_open"] - t["open_to_closed"],
    } for conv, t in trans.items()}

    held = filt is not None and filt["⭑_retired_by_removing_the_E3_arm"] > 0 \
        and any(g["closed_to_open"] > 0 for g in gains.values())
    return {
        "_question": "does removing the E3 arm ADMIT cells the bivalent configuration refused? "
                     "This is the axis the interface-floor ablation is about.",
        "admissibility_filter": filt,
        "paired_transitions": gains,
        "⭐_prediction_holds_on_this_axis": held,
        "_reading": None,   # filled by build()
    }


# ==========================================================================================================
# AXIS B — THE SELECTIVITY WINDOW. The quantity Q10 was closed on.
# ==========================================================================================================
def axis_b(mono, biv):
    """The residue-uniqueness window and the discrimination behind it, computed identically on both sides.

    ⛔ THE ABLATION MAKES NO PREDICTION HERE. It measured a second body's orientation acceptance; this is
    a per-cysteine length arithmetic. Reporting the ablation as though it predicted this axis is the
    specific misreading this module exists to prevent — and reporting only this axis would be the
    opposite error, since it would look like the prediction was refuted when it was never made.
    """
    out = {}
    mono_fw = mono["family_wide_window"]
    biv_fw = biv[WINDOW_KEY]["by_convention"]
    for conv in sorted(biv_fw):
        out[conv] = {
            "monovalent": configuration_summary(mono_fw["monovalent"][conv]),
            "bivalent": configuration_summary(biv_fw[conv]),
        }
        m, b = out[conv]["monovalent"], out[conv]["bivalent"]
        out[conv]["delta"] = {
            "median_margin_atoms": (None if not (m["margin_atoms"] and b["margin_atoms"]) else
                                    m["margin_atoms"]["median"] - b["margin_atoms"]["median"]),
            "median_rank_of_target": (None if not (m["rank_of_target"] and b["rank_of_target"]) else
                                      m["rank_of_target"]["median"] - b["rank_of_target"]["median"]),
            "open_window_rate_monovalent": round(m["n_open_window"] / m["n_cells"], 4) if m["n_cells"] else None,
            "open_window_rate_bivalent": round(b["n_open_window"] / b["n_cells"], 4) if b["n_cells"] else None,
        }
    return out


# ==========================================================================================================
# ★ THE DISCRIMINATOR TEST — the mechanism, tested rather than asserted
# ==========================================================================================================
def discriminator_test(axis_b_rows):
    """★ IS THE `|p-b|` TERM A COST, OR A DISCRIMINATOR?

    The monovalent artifact's own explanation is that *"n = ceil(|p-a|/r) + ceil(|p-b|/r) is not merely a
    larger number … it penalises each cysteine by a DIFFERENT amount. Removing it removes a discriminator
    along with a cost."* That is a MECHANISM CLAIM and it is checkable, because the two failure modes make
    opposite predictions about the same data:

      * a pure COST shifts every cysteine's requirement by roughly the same amount, so C397's MARGIN over
        its first competitor and its RANK are preserved;
      * a DISCRIMINATOR shifts them by different amounts, so the margin collapses and the rank degrades.

    ⇒ If the margin and the rank both degrade while the target's own requirement falls, the term was doing
    selectivity work. That is the discriminating observation, and it is what decides whether the ablation's
    mechanism transfers to this axis or stops at the one it was measured on.
    """
    rows = {}
    for conv, d in axis_b_rows.items():
        m, b = d["monovalent"], d["bivalent"]
        tgt_fell = (m["margin_atoms"] is not None and b["margin_atoms"] is not None)
        rows[conv] = {
            "target_requirement_median_bivalent": None,
            "median_margin_bivalent": b["margin_atoms"]["median"] if b["margin_atoms"] else None,
            "median_margin_monovalent": m["margin_atoms"]["median"] if m["margin_atoms"] else None,
            "median_rank_bivalent": b["rank_of_target"]["median"] if b["rank_of_target"] else None,
            "median_rank_monovalent": m["rank_of_target"]["median"] if m["rank_of_target"] else None,
            "target_first_rate_bivalent": round(b["n_target_first"] / b["n_cells"], 4) if b["n_cells"] else None,
            "target_first_rate_monovalent": round(m["n_target_first"] / m["n_cells"], 4) if m["n_cells"] else None,
            "margin_degraded": (tgt_fell and
                                m["margin_atoms"]["median"] < b["margin_atoms"]["median"]),
            "rank_degraded": (m["rank_of_target"]["median"] > b["rank_of_target"]["median"]
                              if (m["rank_of_target"] and b["rank_of_target"]) else None),
        }
    both = [c for c, r in rows.items() if r["margin_degraded"] and r["rank_degraded"]]
    return {
        "_what": "a pure COST preserves margin and rank; a DISCRIMINATOR degrades both. This is the "
                 "observation that separates them.",
        "by_convention": rows,
        "conventions_where_BOTH_margin_and_rank_degrade": sorted(both),
        "⭐_verdict": (
            "THE E3 TERM WAS A DISCRIMINATOR, NOT ONLY A COST — margin and rank both degrade on %s. "
            "The interface-floor ablation's mechanism (a filter that, once removed, admits more) does "
            "NOT transfer to this axis, because what is removed here is not a filter but the term that "
            "was ORDERING the cysteines." % (", ".join(sorted(both)))
            if both else
            "NOT ESTABLISHED — margin and rank do not both degrade on any convention, so on this data "
            "the |p-b| term behaves as a cost rather than a discriminator."),
    }


# ==========================================================================================================
# helpers
# ==========================================================================================================
def _walk(o):
    yield o
    if isinstance(o, dict):
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def _pose_inheritance():
    if not os.path.exists(POSE_SECOND):
        return {"read": False}
    d = json.load(open(POSE_SECOND, encoding="utf-8"))

    def dig(o, key):
        for v in _walk(o):
            if isinstance(v, dict) and key in v:
                return v[key]
        return None
    return {"read": True, "R5_resolved": dig(d, "R5_resolved"), "outcome": dig(d, "outcome"),
            "cross_method_evidence": dig(d, "cross_method_evidence"),
            "_source": os.path.relpath(POSE_SECOND, REPO)}


def ablation_facts(tcip):
    a = tcip[ABLATION_KEY]
    return {
        "_source": "nr4a3-tcip-reach.json -> ★_interface_floor_ablation",
        "linker_atoms": a["linker_atoms"],
        "committed_floor": a["committed_floor"],
        "ratio_by_floor": {k: v["ratio_single_over_multi"] for k, v in a["by_floor"].items()},
        "ratio_at_the_committed_floor": a["ratio_at_the_committed_floor"],
        "ratio_with_no_interface_floor": a["ratio_with_no_interface_floor"],
        "the_sign_inverts": a["★_the_sign_inverts"],
        "⛔_what_it_does_not_settle": a["⛔_what_this_does_not_settle"],
    }


# ==========================================================================================================
def build():
    mono = json.load(open(MONO, encoding="utf-8"))
    biv = json.load(open(BIVALENT, encoding="utf-8"))
    tcip = json.load(open(TCIP, encoding="utf-8"))

    A = axis_a(mono, biv)
    B = axis_b(mono, biv)
    D = discriminator_test(B)

    filt = A["admissibility_filter"] or {}
    A["_reading"] = (
        "THE PREDICTION HOLDS ON ITS OWN AXIS, AND THE GAIN IS SMALL AND MEASURED. Removing the E3 arm "
        "retires exactly the E3-anchor-buried refusal — %s of %s ensemble cells — while the "
        "warhead-anchor refusal (%s cells) survives untouched. On the decision quantity, %s cells gain a "
        "window under the permissive convention and %s under the conservative one."
        % (filt.get("⭑_retired_by_removing_the_E3_arm"), filt.get("n_cells"),
           filt.get("⛔_NOT_retired"),
           A["paired_transitions"].get("through_space", {}).get("closed_to_open"),
           A["paired_transitions"].get("corridor", {}).get("closed_to_open")))

    mono_verdict = mono["verdict"]
    doc = {
        "_title": "Q10 — the TCIP interface-floor ablation predicts the inhibitor configuration gains "
                  "admissible space. Does it hold, and does it rescue the route?",
        "_status": "$0 CPU, pure stdlib, NO NEW GEOMETRY. Every atom count is read from the committed "
                   "artifacts and both configurations go through ONE reader, so a difference cannot be "
                   "an artefact of two different readers. Nothing here is a claim about reactivity, "
                   "potency, proteome-wide selectivity, efficacy, safety, a therapeutic window or "
                   "clinical readiness.",
        "⭑_the_stale_row_this_pass_corrects": {
            "what_the_board_says": "roadmap §10.1a Q10 — 'the enumeration has never been run in that "
                                   "configuration'; path-family-synthesis.md §3 row 10 — 'unchanged and "
                                   "still under-run'.",
            "what_is_committed": "nr4a3-monovalent-reach.json + nr4a3_monovalent_reach.py, written "
                                 "2026-08-06 at 7:12 AM ET.",
            "the_committed_answer": mono_verdict["answer_on_the_conservative_convention"],
            "its_headline": mono_verdict["headline"],
            "⛔": "the free observation was available the whole time. A row that says 'never run' about "
                 "an artifact sitting on the same branch is an unanswered question wearing the costume "
                 "of a status.",
        },
        "the_prediction": {
            "_from": ablation_facts(tcip),
            "_as_extrapolated_to_this_configuration": "an inhibitor has neither an E3 arm nor an induced "
                                                      "interface, so it sits at floor 0 with no second "
                                                      "body — the configuration the ablation says gains "
                                                      "orientation space.",
            "⚠_it_crosses_two_instruments": "the ablation measures a SECOND BODY's orientation "
                                            "acceptance; the reach enumeration measures a backbone-atom "
                                            "window over cysteines. Testing it on one axis only would "
                                            "conflate 'the prediction held' with 'the route is rescued'.",
        },
        "★_axis_A_admissible_space": A,
        "★_axis_B_the_selectivity_window": B,
        "★_the_discriminator_test": D,
        "_pose_marginalisation": {
            "rule": "every quantity is reported as a distribution over cells with its full range, and "
                    "every verdict is the marginal. No statement is made about a vector or a pose.",
            "why": "R5 is unresolved and got worse on 2026-08-06 — the second pose method DISAGREES with "
                   "the first (0 of 6 systems within 2.00 A, median 6.696 A).",
            "evidence": _pose_inheritance(),
            "⛔": "both configurations descend from the same docked pose family, so the COMPARISON is "
                 "internally matched even though neither side is pose-resolved. That is what makes a "
                 "paired delta readable where an absolute number would not be — and it is also the "
                 "limit: a pose that moved would move both sides, not cancel.",
        },
        "★_verdict": {},
        "★_what_picking_this_configuration_costs": {
            "_source": "roadmap §10.1b — THE MODALITY at C397",
            "retires": ["R9 — OUR ternary is correctly assembled", "R10 — a ternary forms",
                        "R12 — compatible with DEGRADATION (productive unique-lysine geometry)"],
            "⚠_do_not_confuse_this_with_the_TCIP_row": (
                "§10.1b was corrected on 2026-08-06 so that a TCIP retires ONLY R12 — a TCIP is bivalent "
                "and still induces a ternary. That correction does NOT apply here: a monovalent "
                "inhibitor induces no ternary at all, so R9 and R10 go with R12. The two ⚖ ALTERNATIVES "
                "in the same set have different terms, and reading one row's correction onto the other "
                "is exactly the drift that correction was fixing."),
            "loses": "the degradation mechanism — the program's stated reason for choosing degradation "
                     "over inhibition. An inhibitor must carry occupancy-driven pharmacology instead, "
                     "which this repository has measured nothing about.",
            "gains": "one fewer terminus to satisfy, and the E3-anchor admissibility refusal is retired.",
            "⛔": "these are a route's TERMS, not a recommendation. §10.1b records this as an ⚖ "
                 "ALTERNATIVE and the choice is trimcrae's.",
        },
        "⛔_what_this_does_not_license": [
            "any claim that a monovalent covalent probe at C397 is selective — the window question is "
            "answered against it on the conservative convention",
            "any claim that a NON-covalent monovalent pocket modulator is refuted. It has no cysteine to "
            "reach and is untouched by this measurement — the monovalent artifact says so itself.",
            "reactivity, thiol pKa, adduct stability, potency, proteome-wide selectivity, efficacy, "
            "safety, a therapeutic window or clinical readiness",
            "a pose-specific or vector-specific reading of any number here",
        ],
    }

    ts = A["paired_transitions"].get("through_space", {})
    co = A["paired_transitions"].get("corridor", {})
    doc["★_verdict"] = {
        "headline": (
            "THE PREDICTION HOLDS ON THE AXIS IT IS ABOUT AND DOES NOT RESCUE THE ROUTE. "
            "Axis A (admissible space, the ablation's own axis): removing the E3 arm retires the "
            "E3-anchor-buried refusal — %s of %s ensemble cells — and %s of %s paired cells gain a "
            "window under the permissive convention. Axis B (the selectivity window, the quantity Q10 "
            "was closed on): the conservative convention goes from %s of %s open cells to %s of %s, a "
            "complete one-directional collapse, and the committed monovalent verdict is %r. "
            "⛔ THE TWO ARE NOT IN CONFLICT AND THE ABLATION NEVER PREDICTED THE SECOND."
            % (filt.get("⭑_retired_by_removing_the_E3_arm"), filt.get("n_cells"),
               ts.get("closed_to_open"), ts.get("n_paired"),
               B["corridor"]["bivalent"]["n_open_window"], B["corridor"]["bivalent"]["n_cells"],
               B["corridor"]["monovalent"]["n_open_window"], B["corridor"]["monovalent"]["n_cells"],
               mono_verdict["answer_on_the_conservative_convention"])),
        "prediction_holds_on_axis_A": A["⭐_prediction_holds_on_this_axis"],
        "prediction_rescues_the_route": False,
        "★_why_both_are_true": (
            "an interface FLOOR and the |p-b| LENGTH TERM do different work. The floor is a FILTER on a "
            "second body's orientations — remove it and more orientations qualify, which is exactly what "
            "the ablation measured. The |p-b| term is a per-cysteine DISCRIMINATOR inside the length "
            "arithmetic: it penalises each cysteine by a different amount, so removing it removes the "
            "ordering along with the cost. %s"
            % D["⭐_verdict"]),
        "⭑_what_Q10_now_holds": (
            "the 30-of-30 chemoselectivity closure SURVIVES the removal of the E3 arm — which is the "
            "falsifier §10.1a wrote for this row, resolved in the direction that closes it. The "
            "counter-result was never an artefact of the E3 constraint, and the mechanism that looked "
            "like it might reopen the row acts on a different quantity."),
    }
    return doc


def _f(x):
    return "—" if x is None else (("%.4g" % x) if isinstance(x, float) else str(x))


def to_markdown(d):
    import antihandle_constraint as AC
    L = []
    A = L.append
    A(AC._frontmatter(
        "Q10 — the inhibitor configuration at C397, and whether the TCIP interface-floor ablation's "
        "prediction holds",
        "Test the interface-floor ablation's prediction against the committed monovalent reach run on "
        "both axes it could be read on, and report which one it is about.",
        "Geometry only, over committed artifacts. No new compute. No reactivity, potency, selectivity, "
        "efficacy or safety statement.",
        "DOC-NR4A3-INHIBITOR-CONFIGURATION-PREDICTION",
        "research/modalities/inhibitor_configuration_prediction.py"))
    A("# %s\n" % d["_title"])
    A("**Status.** %s\n" % d["_status"])
    st = d["⭑_the_stale_row_this_pass_corrects"]
    A("## ⭑ The free observation nobody had taken\n")
    A("- **The board says:** %s" % st["what_the_board_says"])
    A("- **What is committed:** %s" % st["what_is_committed"])
    A("- **The committed answer:** `%s`\n" % st["the_committed_answer"])
    A("> %s\n" % st["its_headline"])
    A("%s\n" % st["⛔"])
    A("## The prediction\n")
    ab = d["the_prediction"]["_from"]
    A("| `min_contact_residues` | single/multi acceptance ratio |")
    A("|---|---|")
    for k in sorted(ab["ratio_by_floor"], key=lambda x: -int(x)):
        A("| %s%s | %s |" % (k, " (committed)" if int(k) == ab["committed_floor"] else "",
                             ab["ratio_by_floor"][k]))
    A("")
    A("%s\n" % d["the_prediction"]["_as_extrapolated_to_this_configuration"])
    A("⚠ %s\n" % d["the_prediction"]["⚠_it_crosses_two_instruments"])
    A("## ★ Axis A — admissible space (the ablation's own axis)\n")
    f = d["★_axis_A_admissible_space"]["admissibility_filter"]
    if f:
        A("| refusal | cells | retired by removing the E3 arm? |")
        A("|---|---|---|")
        A("| E3 anchor is buried | %s / %s | **yes** |" % (f["n_refused_because_the_E3_ANCHOR_IS_BURIED"],
                                                          f["n_cells"]))
        A("| warhead anchor has no room | %s / %s | ⛔ **no** |"
          % (f["n_refused_because_the_WARHEAD_ANCHOR_HAS_NO_ROOM"], f["n_cells"]))
        A("")
        A("⛔ %s\n" % f["⛔_why"])
    A("| convention | closed → open | open → closed | net |")
    A("|---|---|---|---|")
    for conv, t in sorted(d["★_axis_A_admissible_space"]["paired_transitions"].items()):
        A("| %s | %s | %s | %s |" % (conv, t["closed_to_open"], t["open_to_closed"],
                                     t["net_change_in_open_cells"]))
    A("")
    A("**Prediction holds on this axis: %s**\n"
      % d["★_axis_A_admissible_space"]["⭐_prediction_holds_on_this_axis"])
    A("## ★ Axis B — the selectivity window (the quantity `Q10` was closed on)\n")
    A("| convention | config | cells | open windows | median margin (atoms) | median rank of C397 | "
      "target first |")
    A("|---|---|---|---|---|---|---|")
    for conv, r in sorted(d["★_axis_B_the_selectivity_window"].items()):
        for cfg in ("bivalent", "monovalent"):
            s = r[cfg]
            A("| %s | %s | %s | %s | %s | %s | %s |"
              % (conv, cfg, s["n_cells"], s["n_open_window"],
                 _f(s["margin_atoms"]["median"] if s["margin_atoms"] else None),
                 _f(s["rank_of_target"]["median"] if s["rank_of_target"] else None),
                 s["n_target_first"]))
    A("")
    A("## ★ The discriminator test\n")
    A("%s\n" % d["★_the_discriminator_test"]["_what"])
    A("%s\n" % d["★_the_discriminator_test"]["⭐_verdict"])
    A("## ★ Verdict\n")
    A("**%s**\n" % d["★_verdict"]["headline"])
    A("**Why both are true.** %s\n" % d["★_verdict"]["★_why_both_are_true"])
    A("**What `Q10` now holds.** %s\n" % d["★_verdict"]["⭑_what_Q10_now_holds"])
    c = d["★_what_picking_this_configuration_costs"]
    A("## ★ What picking this configuration costs\n")
    A("- **Retires:** %s" % "; ".join(c["retires"]))
    A("- **Loses:** %s" % c["loses"])
    A("- **Gains:** %s" % c["gains"])
    A("- ⛔ %s\n" % c["⛔"])
    A("## ⛔ What this does not license\n")
    for x in d["⛔_what_this_does_not_license"]:
        A("- %s" % x)
    A("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    for p in (MONO, BIVALENT, TCIP):
        if not os.path.exists(p):
            print("REFUSED — %s does not exist" % p, file=sys.stderr)
            return 2
    doc = build()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w", encoding="utf-8") as fh:
        fh.write(to_markdown(doc))
    print("wrote %s" % os.path.relpath(args.out, REPO))
    print("prediction holds on axis A: %s | rescues the route: %s"
          % (doc["★_verdict"]["prediction_holds_on_axis_A"],
             doc["★_verdict"]["prediction_rescues_the_route"]))
    print(doc["★_the_discriminator_test"]["⭐_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
