#!/usr/bin/env python3
"""Why no ONE construct carries both the covalent electrophile and the causal wedge — the measured answer.

★ WHAT THIS SETTLES, AND WHY IT IS NOT WHAT WAS WRITTEN DOWN. nr4a3-program-map.md and the RUNG 5b block record the
blocker as: *"the covalent series sits at 14 backbone atoms and the wedge pair at 19; a single chain carrying
BOTH needs 16, and the segment grid cannot build it (branch floor k=6 against T407's k in [2,3] at n=16)"* —
i.e. a GRID-RESOLUTION limit at one chain length. Run against the committed enumeration, **every clause of
that except the branch floor is wrong**, and the real blocker is a different kind of thing entirely.

THE THREE MEASURED FACTS (all read from `nr4a3-linker-design.json` -> `virtual_library`, never typed):

  1. **T407 constructs at n = 16 EXIST.** Three of them, at the representative placement, inside a recorded
     window of k in [4, 13]. So "the grid cannot build it at 16" is false.
  2. **C397 constructs at n = 16 also exist**, at the term-(a) exemplar placement, at k = 11 and k = 6.
     So at n = 16 the grid builds an electrophile branch AND a wedge branch — just never on one molecule.
  3. **No recorded T407 window is k in [2, 3].** The exemplar windows are k in [2, 6] (n = 18, 19) and the
     representative's is k in [4, 13] (n = 16); the enumerator builds at k = 6, 7 and 11, all INSIDE them.
     The [2,3] figure is not reproduced by any committed record.

★ THE ACTUAL BLOCKER IS THE CHAIN TEMPLATE, AND IT IS ONE LINE OF `build_smiles`. That function's signature
carries exactly one `pendant`, and its template

    E3-NH-C(=O)- [SEG1] -C(=O)NH- CH(pendant) -C(=O)NH- [SEG2] - <warhead tail>

has exactly ONE branch residue. A molecule carrying the electrophile (-> C397) *and* the wedge (-> T407)
needs TWO. **No choice of SEG1, SEG2, chain length or placement can produce one, because there is no slot** —
which is why sweeping the grid finds nothing and why the failure looked like a length problem.

★ AND THE BRANCH FLOOR IS REAL BUT IT IS ARCHITECTURAL, NOT A GRID ARTEFACT. `build_smiles` returns
`k_warhead = n + 1 - k_e3`, which reduces to **`k = 3 + SEG2 + tail`** — INDEPENDENT of SEG1 and of the chain
length. So the branch alpha-carbon's distance from the warhead is set entirely by what follows it. The floor
is `3 + min(SEG2) + min(tail)`, and the 3 is the branch residue's own N-C(alpha)-C. Adding finer segments
moves it by exactly the amount they are shorter, and SEG2 = 0 is refused for a chemical reason that is not
negotiable (it would put two carbonyls together as an ACYLUREA). So no grid can push k below 4.

WHAT WOULD ACTUALLY WORK, with the arithmetic rather than a hope: a second branch node costs `1 + 3 + 1 = 5`
backbone atoms plus its own following segment. With the grid's existing segments (smallest admissible SEG2 is
2) a two-pendant chain first becomes constructible at **n = 18**, not 16. So the fix is a TWO-BRANCH TEMPLATE,
not a finer grid — and at 18 atoms the grid already has every segment it needs.

⚠ THIS MODULE DIAGNOSES; IT DOES NOT RE-ENUMERATE. Emitting a two-pendant construct would edit a
PREREGISTERED enumeration, and this repo's standard for that is a dated, recorded amendment — not a drive-by
from a diagnostic. It is also a DESIGN change (a new architecture), not a defect fix, so it does not even
qualify under the amendment standard that covers a statistic shown to lack discriminating power. The existing
library is untouched and every construct in it remains exactly what it was.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LIB_JSON = os.path.join(HERE, "nr4a3-linker-design.json")
OUT = os.path.join(HERE, "linker-branch-reach.json")

# The two mechanisms a single chain would have to carry at once. One home: nr4a3-program-map.md section MECHANISM-FIRST.
COVALENT_TARGET = "C397 SG"
WEDGE_TARGET = "T407"


def load_library(path=LIB_JSON):
    with open(path) as fh:
        return json.load(fh)["virtual_library"]


def branched_records(lib):
    """Every construct that carries a pendant, i.e. every one with a branch node."""
    return [r for r in lib if r.get("branch_target")]


def reach_table(lib):
    """Per (target, n_backbone), the branch positions the enumeration ACTUALLY produced and the geometric
    window it produced them inside. Pure aggregation of committed records -- fabricates nothing."""
    out = {}
    for r in branched_records(lib):
        key = "%s@n%d" % (r["branch_target"], r["n_backbone_atoms_intended"])
        w = r.get("branch_window") or {}
        e = out.setdefault(key, {"target": r["branch_target"], "n_backbone": r["n_backbone_atoms_intended"],
                                 "k_built": set(), "window_k_min": set(), "window_k_max": set(),
                                 "placements": set(), "pendants": set(), "n_constructs": 0})
        e["k_built"].add(r.get("branch_k_from_warhead"))
        if w:
            e["window_k_min"].add(w.get("k_min"))
            e["window_k_max"].add(w.get("k_max"))
        e["placements"].add(r.get("designed_at_placement"))
        e["pendants"].add(r.get("pendant"))
        e["n_constructs"] += 1
    for e in out.values():
        for f in ("k_built", "window_k_min", "window_k_max", "placements", "pendants"):
            e[f] = sorted(x for x in e[f] if x is not None)
    return out


def branch_floor():
    """The architectural floor on k, DERIVED from the assembler rather than remembered.

    `build_smiles` returns k_warhead = n + 1 - k_e3 with k_e3 = 4 + SEG1, and n = 6 + SEG1 + SEG2 + tail, so
    k = 3 + SEG2 + tail. SEG1 and the chain length cancel out exactly. The 3 is the branch residue's own
    N-C(alpha)-C, which no grid change can remove."""
    import nr4a3_linker_design as LD
    seg2 = {k: v["n"] for k, v in LD.LINKER_SEGMENT.items()
            if not v.get("acyl_only") and v["n"] > 0}          # SEG2 admissibility, from the assembler's guards
    tails = {k: v["tail_atoms"] for k, v in LD.WARHEAD_HANDLE.items()}
    per_warhead = {wk: sorted({LD.BRANCH_NODE_ATOMS + n + t for n in seg2.values()})
                   for wk, t in tails.items()}
    floor = min(min(v) for v in per_warhead.values())
    return {
        "formula": "k_warhead = BRANCH_NODE_ATOMS + SEG2 + warhead_tail  (SEG1 and chain length cancel)",
        "branch_node_atoms": LD.BRANCH_NODE_ATOMS,
        "admissible_seg2_lengths": seg2,
        "warhead_tail_atoms": tails,
        "achievable_k_per_warhead": per_warhead,
        "floor_k": floor,
        "_why_seg2_cannot_be_zero": ("build_smiles REFUSES SEG2 = 0: the branch residue's C-terminal amide N "
                                     "would sit on the warhead tail's own carbonyl, making an ACYLUREA rather "
                                     "than two amides. That is a chemistry guard, not a grid choice."),
        "_floor_is_architectural": ("the 3 is the branch residue's own N-C(alpha)-C. A finer grid moves the "
                                    "floor by exactly the amount the new segment is shorter and no further, "
                                    "so no grid change reaches k < 4."),
    }


def two_pendant_minimum_length():
    """The chain length at which a construct could carry BOTH pendants, if the template allowed two.

    Each branch node costs 1 (acyl C) + BRANCH_NODE_ATOMS + 1 (amide N) = 5 backbone atoms, and every segment
    between two amides must be >= 1 for the acylurea reason above."""
    import nr4a3_linker_design as LD
    node = 1 + LD.BRANCH_NODE_ATOMS + 1
    seg2 = [v["n"] for k, v in LD.LINKER_SEGMENT.items() if not v.get("acyl_only") and v["n"] > 0]
    seg1 = [v["n"] for k, v in LD.LINKER_SEGMENT.items() if not v.get("amine_only") and v["n"] > 0]
    tail = min(v["tail_atoms"] for v in LD.WARHEAD_HANDLE.values())
    with_grid = 1 + min(seg1) + node + min(seg2) + node + min(seg2) + tail
    in_principle = 1 + 1 + node + 1 + node + 1 + tail          # if 1-atom segments existed
    return {
        "backbone_atoms_per_branch_node": node,
        "min_n_with_the_EXISTING_grid": with_grid,
        "min_n_if_1_atom_segments_existed": in_principle,
        "reading": ("A two-pendant chain is constructible at n = %d with the segments the grid ALREADY has. "
                    "The '16' in the superseded framing is close to the in-principle floor (%d), which is why "
                    "the limit looked like grid resolution -- but at 18 atoms no new segment is needed at all, "
                    "so the missing piece is the TEMPLATE, not the grid." % (with_grid, in_principle)),
    }


def build_report():
    lib = load_library()
    table = reach_table(lib)
    cov = {k: v for k, v in table.items() if v["target"] == COVALENT_TARGET}
    wed = {k: v for k, v in table.items() if v["target"] == WEDGE_TARGET}
    shared_n = sorted({v["n_backbone"] for v in cov.values()} & {v["n_backbone"] for v in wed.values()})
    return {
        "_what": ("Why no single construct carries both the covalent electrophile and the causal wedge. "
                  "Diagnostic only -- it re-enumerates nothing."),
        "_reads": "nr4a3-linker-design.json -> virtual_library (the committed enumeration)",
        "n_branched_constructs": len(branched_records(lib)),
        "reach_table": table,
        "chain_lengths_carrying_BOTH_targets_separately": shared_n,
        "branch_floor": branch_floor(),
        "two_pendant_minimum_length": two_pendant_minimum_length(),
        "verdict": {
            "blocker": "THE CHAIN TEMPLATE CARRIES ONE PENDANT. build_smiles takes a single `pendant` and its "
                       "template has a single branch residue, so no (SEG1, SEG2, length, placement) can emit a "
                       "two-mechanism molecule -- there is no slot for the second one.",
            "not_the_blocker": ["grid resolution at n = 16 (the grid builds BOTH targets at 16, separately)",
                                "a T407 window of k in [2,3] (no committed record shows one; the windows are "
                                "k in [2,6] and k in [4,13], and the enumerator builds inside them)"],
            "real_but_secondary": "the k floor of %d, which is architectural (the branch residue's own "
                                  "N-C(alpha)-C) and not fixable by any grid change" % branch_floor()["floor_k"],
            "what_would_work": "a TWO-BRANCH template; constructible at n = %d with existing segments"
                               % two_pendant_minimum_length()["min_n_with_the_EXISTING_grid"],
        },
        "_not_done_here": ("Emitting a two-pendant construct edits a PREREGISTERED enumeration and is a DESIGN "
                           "change rather than a defect fix, so it needs a dated recorded amendment, not a "
                           "drive-by from a diagnostic. The existing library is untouched."),
    }


def main():
    rep = build_report()
    with open(OUT, "w") as fh:
        json.dump(rep, fh, indent=1)
        fh.write("\n")
    v = rep["verdict"]
    print("[branch-reach] %d branched constructs; both targets built separately at n = %s"
          % (rep["n_branched_constructs"], rep["chain_lengths_carrying_BOTH_targets_separately"]))
    print("[branch-reach] BLOCKER: %s" % v["blocker"])
    print("[branch-reach] k floor = %d (architectural); two-branch template constructible at n = %d"
          % (rep["branch_floor"]["floor_k"], rep["two_pendant_minimum_length"]["min_n_with_the_EXISTING_grid"]))
    print("[branch-reach] wrote %s" % OUT)


if __name__ == "__main__":
    main()
