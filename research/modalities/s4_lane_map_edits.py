#!/usr/bin/env python3
"""
ROUTE THE THREE §4-LANE RESULTS INTO THE MAP AND THE GRAPH — as EDITS, never as hand-edits.

The roadmap ([`nr4a3-program-map.md`](../manuscripts/nr4a3-program-map.md)) and `systems/graph/*.json` are
not hand-edited by this work. This module emits (a) roadmap edits through `map_edits.py`, whose
`current_text` is READ out of the live map at generation time so an anchor cannot go stale silently, and
(b) a declarative list of graph records for the systems maintainer to apply, each pointing at the artifact
that OWNS its numbers so the graph links rather than restates them (CLAUDE.md rule 1).

⛔ NOTHING HERE APPLIES AN EDIT. It describes edits and checks that each one still targets a real line.

Output: s4-lane-map-edits.json
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import map_edits as ME                                      # noqa: E402

OUT = os.path.join(HERE, "s4-lane-map-edits.json")
A_GSE = "research/modalities/gse11185-wt-vs-fusion.json"
A_RE = "research/modalities/nr4a3-re-reach.json"
A_P5 = "research/modalities/nurr1-allosteric-vs-pocket5.json"


def _load(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return json.load(fh)


def roadmap_edits(text):
    gse, re_, p5 = _load(A_GSE), _load(A_RE), _load(A_P5)
    edits = []

    # ── §9, the result-lane table: three lanes that have no node, row or mention on the page ─────────────
    anchor = "**The linker library + matched pair** — 54 constructs, RDKit 54/54"
    rows = []
    if p5:
        c = p5["comparison_full_site"]
        rows.append(
            "| **The published Nurr1 allosteric site vs Pocket-5** — n_overlap %s, Jaccard %s, centroid "
            "%s–%s Å over %d 8XTT conformers | the first external, independently-published site definition "
            "this program's target site has ever been compared against | `R1` `R5` `R7` | ⭑ **A MATCH under "
            "the frozen composite gate**, and the paper's three OTHER epitopes, mapped by the identical "
            "pipeline, land 14.8–24.3 Å away with zero overlap — so it is a property of that site, not of "
            "the mapping. ⛔ **A GEOMETRY STATEMENT ONLY**: it says nothing about whether vidofludimus binds "
            "NR4A3, and 3 of the 9 site residues do not carry the same type in NR4A3, which is where a "
            "selectivity argument would START. What it changes is that the site has published SAR attached "
            "to it for the first time ([`nurr1-allosteric-vs-pocket5.json`](../modalities/nurr1-allosteric-vs-pocket5.json)) |"
            % (c["n_overlap"], c["jaccard"], c["centroid_dist_ang_min"], c["centroid_dist_ang_max"],
               c["n_conformers_ok"]))
    if gse:
        t = gse["read"]["induction_response"]["at_2x"]
        rows.append(
            "| **GSE11185 — the direct wild-type-vs-fusion expression experiment** — %d / %d probes up ≥2×, "
            "%d shared (%s× chance) | the only deposited NOR1-vs-EWS/NOR1 comparison that exists, in this "
            "repo's own GEO census and never opened until 2026-08-07 | `R13` | ⛔ **n = 1 per design cell, "
            "HEK293 overexpression, and NO vector-only control**, so no p-value is computable and a shared "
            "response is construct-driven OR doxycycline-driven. The construct-expression control is "
            "UNAVAILABLE — all three NR4A3 probesets are absent on all four arrays. ⭑ It does **NOT** bear "
            "on the retired AF-1 premise in either direction, and that refusal is the point: the premise "
            "stands on `nr4a3-exon-audit.json` alone ([`gse11185-wt-vs-fusion.json`](../modalities/gse11185-wt-vs-fusion.json)) |"
            % (t["n_up_wild_type"], t["n_up_fusion"], t["n_up_both"],
               t["overlap_enrichment_over_chance"]))
    if re_:
        v = re_["verdict"]
        rows.append(
            "| **Response-element reach enumeration (PDB 7WNH)** — %s | the first anchor this program has "
            "enumerated that is NOT in an NR4A3 pocket | `R5` `R7` | ⛔ **`ADMITS` is an excluded-volume "
            "statement that no tested body has ever failed** — it removes a way the route could have been "
            "dead and licenses nothing further. What carries information is the naked-DNA ablation (does "
            "the receptor shape the geometry at all?) and the interface-floor ablation. ⛔ It does not "
            "touch the route's real blocker: an NBRE-directed warhead is selective for a sequence NR4A1, "
            "NR4A2 and wild-type NR4A3 all read, and none exists "
            "([`nr4a3-re-reach.json`](../modalities/nr4a3-re-reach.json)) |" % v["answer"])
    if rows:
        edits.append(ME.edit(
            text, section="§9 · Result lanes the graph could not express", anchor=anchor,
            why=("three §4 lanes of emc-unexplored-treatment-lanes.md ran on 2026-08-07 at $0 and have no "
                 "node, row or mention on this page"),
            artifact="%s ; %s ; %s" % (A_P5, A_GSE, A_RE),
            transform=ME.append_after_line("\n".join(rows)), kind="append_rows"))

    return edits


def graph_edits():
    """Declarative records for `systems/graph/*.json`. NOT applied here — the graph is generated-and-checked
    and a hand-edit fails the build; these are handed to the systems maintainer."""
    p5, re_, gse = _load(A_P5), _load(A_RE), _load(A_GSE)
    out = []
    out.append({
        "file": "systems/graph/artifacts.json",
        "action": "add",
        "record": {
            "id": "ART-NURR1-P5-SITE-MATCH",
            "path": A_P5,
            "what": ("residue-overlap and centroid comparison of the published Nurr1 H1/H5/H7/H8 allosteric "
                     "surface pocket against NR4A3 Pocket-5, in pocket_tracking's frozen vocabulary"),
            "owns": ["the site correspondence and its three-control refutation"],
            "cost": "$0",
        },
    })
    out.append({
        "file": "systems/graph/evidence.json",
        "action": "add",
        "record": {
            "id": "EV-LOPEZGARCIA-2025",
            "citation": (p5 or {}).get("source", {}).get("citation"),
            "doi": (p5 or {}).get("source", {}).get("doi"),
            "pmc": (p5 or {}).get("source", {}).get("pmc"),
            "verification_level": "[FT]",
            "what_it_supplies": ("the ONLY published, mutagenesis-anchored ligand site on an NR4A LBD, plus "
                                 "a clinical-stage scaffold (vidofludimus) and its SAR"),
            "⚠": "it is an NR4A2 result; nothing about NR4A3 binding follows from it",
        },
    })
    out.append({
        "file": "systems/graph/artifacts.json",
        "action": "add",
        "record": {"id": "ART-RE-REACH", "path": A_RE,
                   "what": ("linker-reach enumeration anchored on the NBRE response element (PDB 7WNH) "
                            "rather than on an NR4A3 pocket"),
                   "owns": ["the response-element anchor's admissibility and its two ablations"],
                   "cost": "$0"},
    })
    out.append({
        "file": "systems/graph/routes.json",
        "action": "add",
        "⚠_this_is_a_NEW_route_and_needs_trimcraes_grade": True,
        "record": {
            "id": "RT-RESPONSE-ELEMENT",
            "display_name": "Response-element-anchored degrader — bind the NBRE, recruit the E3",
            "purpose": ("Can the target-side terminus bind the DNA the receptor sits on instead of a pocket "
                        "on the receptor, so the route stops depending on NR4A3 being ligandable?"),
            "distinct_from": [
                {"route": "RT-DBD", "axis": "what the warhead binds",
                 "why": ("RT-DBD is closed on zinc-finger PARALOGUE IDENTITY — it targets the DBD PROTEIN. "
                         "This route targets the DNA, so that arithmetic does not reach it. The blocker it "
                         "does inherit is different and is stated: the NBRE is read by NR4A1, NR4A2 and "
                         "wild-type NR4A3 alike.")},
                {"route": "RT-DEGRADER", "axis": "where the target-side terminus binds",
                 "why": "identical E3 half; the anchor moves off the LBD entirely"},
            ],
            "blockers_inherited": ["BLK-NOT-FUSION-SELECTIVE", "BLK-INDUCED-COMPLEX", "BLK-NO-WET-LAB"],
            "blockers_retired": [],
            "artifacts": ["ART-RE-REACH"],
            "state": {"work_state": "registered", "maturity": "computed", "confidence": "low"},
            "closure_kind": "open",
            "closure_note": ((re_ or {}).get("verdict", {}).get("_what_it_licenses")),
            "⛔_what_is_NOT_claimed": ((re_ or {}).get("verdict", {})
                                      .get("⛔_and_this_is_the_sentence_that_must_travel_with_it")),
        },
    })
    out.append({
        "file": "systems/graph/artifacts.json",
        "action": "add",
        "record": {"id": "ART-GSE11185", "path": A_GSE,
                   "what": "first read of GEO GSE11185, the direct NOR1-vs-EWS/NOR1 expression experiment",
                   "owns": ["what the deposited values say about shared vs divergent target programmes"],
                   "cost": "$0",
                   "⚠": ((gse or {}).get("verdict", {}).get("⛔_ceiling") or [None])[0]},
    })
    out.append({
        "file": "systems/graph/routes.json",
        "action": "amend",
        "target": "RT-6MP",
        "field": "closure_note",
        "append": ("⚠ 2026-08-07: GSE11185 — the only deposited wild-type-vs-fusion expression experiment — "
                   "was read at $0 and does NOT bear on the AF-1 premise in either direction "
                   "(gse11185-wt-vs-fusion.json `af1_premise_bearing`). The corrected premise still stands "
                   "on nr4a3-exon-audit.json alone. Recorded so this dataset is not recruited to the "
                   "question later."),
    })
    return out


def build():
    text = ME.load_map()
    edits = roadmap_edits(text)
    return {
        "_title": "Routed edits for the three §4 lanes of emc-unexplored-treatment-lanes.md",
        "_status": "DESCRIBES edits; applies none. The roadmap and systems/graph are not hand-edited here.",
        "_generated_against": os.path.relpath(ME.MAP, REPO),
        "map_edits_required": edits,
        "map_edit_anchor_check": ME.verify(edits, text),
        "graph_edits_required": graph_edits(),
        "⚠_the_new_route_needs_a_human": ("RT-RESPONSE-ELEMENT is a NEW route with no grade. Grading a route "
                                          "is trimcrae's call, not this module's, and the record above "
                                          "deliberately carries no `grade` key."),
    }


def main(argv=None):
    d = build()
    with open(OUT, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")
    print(json.dumps(d["map_edit_anchor_check"], indent=1))
    print("graph edits: %d" % len(d["graph_edits_required"]))
    return 0 if d["map_edit_anchor_check"]["n_stale"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
