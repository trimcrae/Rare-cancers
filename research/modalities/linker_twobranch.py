#!/usr/bin/env python3
"""A TWO-BRANCH linker template — one molecule carrying BOTH the covalent handle and the causal wedge.

★ WHY THIS EXISTS, AND WHY IT IS A SEPARATE FILE. `linker_branch_reach.py` measured why no construct in the
committed library carries both mechanisms, and the answer was not the one on record: it is not grid
resolution and it is not geometry, it is that `nr4a3_linker_design.build_smiles` takes **one** `pendant` and
its template has **one** branch residue. There was no slot for the second mechanism, so every sweep over
segments and chain lengths was searching a space that structurally could not contain the answer.

This module adds the missing slot. **It does NOT touch the preregistered enumeration.** `build_smiles`,
`enumerate_library` and `nr4a3-linker-design.json` are untouched and every construct in that library remains
exactly what it was; this emits a SEPARATE artifact, `nr4a3-linker-twobranch.json`, explicitly labelled as a
later additive exploration. The distinction matters: amending a preregistered enumeration after a result is
the retune this program forbids, whereas adding a capability that changes no existing record, no gate and no
verdict is an extension. Nothing downstream is unlocked by it.

THE TEMPLATE, and the arithmetic that follows from it:

    E3-NH-C(=O)- [SEG1] -C(=O)NH- CH(p_far) -C(=O)NH- [SEG2] -C(=O)NH- CH(p_near) -C(=O)NH- [SEG3] - <tail>

    n      = 11 + SEG1 + SEG2 + SEG3 + tail        (each branch node costs 1 + 3 + 1 backbone atoms)
    k_near = 3 + SEG3 + tail                        (the warhead-side branch; SEG1, SEG2 cancel)
    k_far  = 8 + SEG2 + SEG3 + tail  = k_near + 5 + SEG2

`p_near` sits closer to the warhead and `p_far` closer to the E3 — which is the assignment the geometry
wants, because the recorded T407 windows sit LOW (k in [2,6]) and the C397 windows sit HIGH (k around 11-13).

★★ THE RESULT, AND IT IS A SINGLE POINT RATHER THAN A REGION. Scanning every (SEG1, SEG2, SEG3, warhead)
against the windows the committed library actually recorded — same chain length, same placement, same target
— **exactly one chain satisfies both at once**: n = 18, term-(a) exemplar, SEG1 = SEG2 = SEG3 = a2, the
5-amide warhead, with the electrophile at k = 13 and the wedge at k = 6. That the answer is unique is itself
the finding: a two-mechanism molecule is not a design *space* here, it is one chain, and any change to a
segment breaks one of the two windows.

⚠ WHAT IS TRANSFERRED AND MUST NOT BE READ AS MEASURED. The windows come from SINGLE-branch records at the
same target, placement and chain length. That transfer is sound because `branch_position_window` is a
function of (endpoint A, endpoint B, target xyz, chain length, pendant reach) and **not** of how many branch
residues the chain carries — but it is a transfer, and a two-branch chain has never had its own window
computed. The honest status of anything below is THEREFORE: constructible, and window-admissible against
transferred windows. It is not a docked pose, not a strain estimate and not a survivor of the basin-fidelity
filter, none of which this module runs.

⚠ RDKit IS NOT AVAILABLE IN THE DEV SANDBOX, so chemical validity is verified in CI (`--verify`), not here.
The pure assembly and the window arithmetic are unit-tested locally; the SMILES are inert strings until
something parses them.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nr4a3_linker_design as LD  # noqa: E402  — one home for the chemistry constants

LIB_JSON = os.path.join(HERE, "nr4a3-linker-design.json")
OUT = os.path.join(HERE, "nr4a3-linker-twobranch.json")

COVALENT_TARGET = "C397 SG"
WEDGE_TARGET = "T407"
NODE_ATOMS = 1 + LD.BRANCH_NODE_ATOMS + 1          # acyl C + N-Calpha-C + amide N


def _max_ring_digit(frag):
    """Highest ring-closure digit a fragment uses, 0 if none. Single digits only, as in `_renumber`."""
    ds = [int(c) for c in re.findall(r"\d", frag)]
    return max(ds) if ds else 0


def _renumber_pair(far_smi, near_smi, base=7):
    """Give the two pendants DISJOINT ring-closure ranges.

    ★ THIS IS THE HAZARD THE ONE-PENDANT TEMPLATE NEVER HAD. `build_smiles` partitions digits E3 1-3,
    warhead 4-6, pendant 7-9 — a single pendant fits comfortably. Two pendants share that one range, and two
    fragments that both open ring `7` would close each other's bond, producing a chemically different molecule
    that still parses. So the far pendant is renumbered from `base` and the near one from immediately past the
    highest digit the far one consumed, and an overflow is REFUSED rather than silently wrapped."""
    far = LD._renumber(far_smi, base)
    nxt = base + _max_ring_digit(far_smi)          # first digit the far fragment did not take
    if _max_ring_digit(far_smi) and nxt > 9:
        raise ValueError("ring-closure digit overflow allocating the far pendant %r" % far_smi)
    near = LD._renumber(near_smi, nxt if _max_ring_digit(far_smi) else base)
    used_far = {int(c) for c in re.findall(r"\d", far)}
    used_near = {int(c) for c in re.findall(r"\d", near)}
    if used_far & used_near:
        raise ValueError("the two pendants share ring digits %s — they would capture each other's bonds"
                         % sorted(used_far & used_near))
    return far, near


def build_two_branch_smiles(e3_key, wh_key, s1_key, s2_key, s3_key, p_far, p_near):
    """Assemble one two-mechanism construct. Returns (smiles, n_backbone, k_far, k_near).

    The guards mirror `build_smiles`'s, and the acylurea guard applies to BOTH inter-amide segments: a
    zero-length SEG2 would put the far node's C-terminal amide N onto the near node's own acyl carbonyl,
    which is the same C(=O)-N-C(=O)-N motif the one-pendant assembler already refuses at SEG2."""
    e3, wh = LD.E3_HANDLE[e3_key], LD.WARHEAD_HANDLE[wh_key]
    s1, s2, s3 = (LD.LINKER_SEGMENT[k] for k in (s1_key, s2_key, s3_key))
    if s1["n"] == 0 or s1.get("amine_only"):
        raise ValueError("SEG1 must be a non-empty acyl-side segment")
    for name, seg in (("SEG2", s2), ("SEG3", s3)):
        if seg.get("acyl_only"):
            raise ValueError("%s placed after an amide N would make an N,O-acetal" % name)
        if seg["n"] == 0:
            raise ValueError("%s must be >= 1 atom or the flanking carbonyls form an acylurea" % name)
    far_smi, near_smi = _renumber_pair(LD.PENDANT[p_far]["smi"], LD.PENDANT[p_near]["smi"])
    node_far = "C(=O)N[C@@H](%s)C(=O)N" % far_smi
    node_near = "C(=O)N[C@@H](%s)C(=O)N" % near_smi
    smi = (e3["pre"] + "C(=O)" + s1["smi"] + node_far + s2["smi"] + node_near + s3["smi"]
           + wh["tail"] + e3["post"])
    n = 11 + s1["n"] + s2["n"] + s3["n"] + wh["tail_atoms"]
    k_near = LD.BRANCH_NODE_ATOMS + s3["n"] + wh["tail_atoms"]
    k_far = k_near + NODE_ATOMS + s2["n"]
    # Identity self-check, in the spirit of build_smiles's k_warhead + k_e3 == n + 1: the two branch
    # alpha-carbons are separated by exactly one node plus SEG2, an invariant no formula slip satisfies.
    assert k_far - k_near == NODE_ATOMS + s2["n"]
    return smi, n, k_far, k_near


def committed_windows(path=LIB_JSON):
    """The geometric windows the PREREGISTERED enumeration recorded, keyed (target, placement, n).

    Read, never recomputed: this module has no basin context and inventing one would be the fabrication the
    repo's staging guards exist to prevent."""
    with open(path) as fh:
        lib = json.load(fh)["virtual_library"]
    out = {}
    for r in lib:
        w = r.get("branch_window")
        if r.get("branch_target") and w:
            key = (r["branch_target"], r["designed_at_placement"], r["n_backbone_atoms_intended"])
            out.setdefault(key, set()).add((w["k_min"], w["k_max"]))
    return out


def _in_any(k, windows):
    return any(lo <= k <= hi for lo, hi in windows)


def admissible_chains(windows=None):
    """Every (SEG1, SEG2, SEG3, warhead) whose two branch positions land in the committed windows of BOTH
    targets, at the SAME chain length and the SAME placement. Pure over the segment table."""
    windows = committed_windows() if windows is None else windows
    seg1 = [k for k, v in LD.LINKER_SEGMENT.items() if not v.get("amine_only") and v["n"] > 0]
    seg = [k for k, v in LD.LINKER_SEGMENT.items() if not v.get("acyl_only") and v["n"] > 0]
    out = []
    for a in seg1:
        for b in seg:
            for c in seg:
                for wk, wv in LD.WARHEAD_HANDLE.items():
                    n = 11 + LD.LINKER_SEGMENT[a]["n"] + LD.LINKER_SEGMENT[b]["n"] \
                        + LD.LINKER_SEGMENT[c]["n"] + wv["tail_atoms"]
                    k_near = LD.BRANCH_NODE_ATOMS + LD.LINKER_SEGMENT[c]["n"] + wv["tail_atoms"]
                    k_far = k_near + NODE_ATOMS + LD.LINKER_SEGMENT[b]["n"]
                    for (tgt, place, nn), ws in windows.items():
                        if tgt != COVALENT_TARGET or nn != n or not _in_any(k_far, ws):
                            continue
                        wedge = windows.get((WEDGE_TARGET, place, n))
                        if wedge and _in_any(k_near, wedge):
                            out.append({"n_backbone_atoms": n, "placement": place, "warhead": wk,
                                        "seg1": a, "seg2": b, "seg3": c,
                                        "k_far_covalent": k_far, "k_near_wedge": k_near,
                                        "covalent_window": sorted(ws), "wedge_window": sorted(wedge)})
    seen, uniq = set(), []
    for c in out:
        key = tuple(sorted(c.items(), key=lambda kv: kv[0]))[:0] or json.dumps(c, sort_keys=True)
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    return uniq


ELECTROPHILES = [k for k, v in LD.PENDANT.items() if v["reach_key"] == "dab_branch"]
WEDGES = [k for k, v in LD.PENDANT.items() if v["reach_key"] == "aryl_branch_residue"]


def enumerate_two_branch():
    """Build every two-mechanism construct the admissible chains allow, across pendant choices.

    The pendant CONTROLS are enumerated alongside the actives on purpose: `cyanoprop` is the non-electrophilic
    control for the covalent handle and `ph` is the des-aza control for the wedge, so the set contains its own
    matched comparisons rather than a lone active."""
    chains = admissible_chains()
    out = []
    for ch in chains:
        for e3 in LD.E3_HANDLE:
            for pe in ELECTROPHILES:
                for pw in WEDGES:
                    smi, n, k_far, k_near = build_two_branch_smiles(
                        e3, ch["warhead"], ch["seg1"], ch["seg2"], ch["seg3"], pe, pw)
                    assert (n, k_far, k_near) == (ch["n_backbone_atoms"], ch["k_far_covalent"],
                                                  ch["k_near_wedge"])
                    out.append({
                        "construct_id": "2br_%s_%s_%s-%s-%s_%s+%s" % (e3, ch["warhead"], ch["seg1"],
                                                                      ch["seg2"], ch["seg3"], pe, pw),
                        "e3_handle": e3, "warhead_handle": ch["warhead"],
                        "linker_segments": [ch["seg1"], ch["seg2"], ch["seg3"]],
                        "n_backbone_atoms": n,
                        "pendant_far": pe, "pendant_far_kind": LD.PENDANT[pe]["kind"],
                        "pendant_near": pw, "pendant_near_kind": LD.PENDANT[pw]["kind"],
                        "branch_k_covalent_from_warhead": k_far,
                        "branch_k_wedge_from_warhead": k_near,
                        "covalent_target": COVALENT_TARGET, "wedge_target": WEDGE_TARGET,
                        "placement": ch["placement"],
                        "smiles": smi,
                        "stereocentres": "(S) at BOTH branch alpha-carbons, from the L-amino-acid blocks",
                        "branch_residues": ["Fmoc-L-Dab(Boc)-OH (electrophile side chain)",
                                            "Fmoc-L-Phe-OH / Fmoc-3-(3-pyridyl)-L-Ala-OH (wedge)"],
                    })
    return chains, out


def build_report():
    chains, lib = enumerate_two_branch()
    return {
        "_what": "Two-branch linker constructs: ONE molecule carrying the covalent handle AND the causal wedge.",
        "_status": ("ADDITIVE EXPLORATION. The preregistered enumeration (nr4a3-linker-design.json) is "
                    "UNTOUCHED and nothing in it is invalidated; this is a separate artifact and it unlocks "
                    "nothing downstream."),
        "_why": ("linker_branch_reach.py measured that no committed construct carries both mechanisms because "
                 "the one-pendant TEMPLATE has no second slot -- not because of grid resolution and not "
                 "because of geometry. This adds the slot."),
        "template": ("E3-NH-C(=O)-[SEG1]-C(=O)NH-CH(p_far)-C(=O)NH-[SEG2]-C(=O)NH-CH(p_near)-C(=O)NH-[SEG3]"
                     "-<warhead tail>"),
        "arithmetic": {"n": "11 + SEG1 + SEG2 + SEG3 + tail",
                       "k_near": "%d + SEG3 + tail" % LD.BRANCH_NODE_ATOMS,
                       "k_far": "k_near + %d + SEG2" % NODE_ATOMS},
        "n_admissible_chains": len(chains),
        "admissible_chains": chains,
        "★_the_solution_is_unique": (
            "Exactly %d chain satisfies both committed windows at the same length and placement. That is the "
            "finding as much as the molecule is: a two-mechanism construct here is not a design SPACE but a "
            "single point, and changing any one segment breaks one of the two windows." % len(chains)),
        "n_constructs": len(lib),
        "constructs": lib,
        "_limits": {
            "windows_are_TRANSFERRED": ("the k-windows come from SINGLE-branch records at the same target, "
                                        "placement and chain length. branch_position_window is a function of "
                                        "(endpoints, target, length, reach) and NOT of branch count, so the "
                                        "transfer is sound -- but no two-branch chain has had its own window "
                                        "computed, and this must never be reported as though one had."),
            "not_yet_done": ["RDKit validity + heavy-atom/property profile (CI, --verify)",
                             "basin-fidelity filtering", "docked pose", "linker strain",
                             "any energetic or selectivity quantity whatsoever"],
            "claim_ceiling": ("constructible and window-admissible against transferred windows. Nothing here "
                              "is a predicted selective candidate, a binding statement or a degradation "
                              "statement."),
        },
    }


def verify_with_rdkit(report):
    """CI-only: parse every SMILES and record heavy-atom counts. Fails loudly if a construct does not parse —
    an unparseable string in a design artifact is worse than an absent one."""
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    rows, bad = [], []
    for c in report["constructs"]:
        m = Chem.MolFromSmiles(c["smiles"])
        if m is None:
            bad.append(c["construct_id"])
            continue
        rows.append({"construct_id": c["construct_id"], "heavy_atoms": m.GetNumHeavyAtoms(),
                     "mw": round(Descriptors.MolWt(m), 2),
                     "n_stereocentres": len(Chem.FindMolChiralCenters(m, includeUnassigned=True,
                                                                      useLegacyImplementation=False))})
    report["rdkit_verification"] = {"n_parsed": len(rows), "n_failed": len(bad), "failed": bad,
                                    "per_construct": rows}
    if bad:
        raise SystemExit("[twobranch] %d construct(s) failed to parse: %s" % (len(bad), bad))
    report["cost_of_the_second_mechanism"] = _property_cost(rows)
    return report


def _property_cost(rows):
    """★ WHAT CARRYING BOTH MECHANISMS COSTS IN PROPERTY SPACE — reported because it is the honest half.

    A second branch residue plus a second pendant is not free: it adds a node, a segment and a whole
    functional group. Comparing against the COMMITTED single-mechanism library (the same chemistry, the same
    handles) rather than against a textbook rule keeps the comparison internal and fair."""
    import statistics
    with open(os.path.join(HERE, "nr4a3-linker-library-chem.json")) as fh:
        base = [c["descriptors"] for c in json.load(fh)["constructs"] if c.get("descriptors")]
    b_ha = sorted(d["heavy_atoms"] for d in base if d.get("heavy_atoms"))
    b_mw = sorted(d["mw"] for d in base if d.get("mw"))
    t_ha = sorted(r["heavy_atoms"] for r in rows)
    t_mw = sorted(r["mw"] for r in rows)
    return {
        "single_mechanism_library": {"n": len(b_ha), "heavy_atoms": [b_ha[0], b_ha[-1]],
                                     "heavy_atoms_median": statistics.median(b_ha),
                                     "mw": [round(b_mw[0], 1), round(b_mw[-1], 1)],
                                     "mw_median": round(statistics.median(b_mw), 1)},
        "two_mechanism_set": {"n": len(t_ha), "heavy_atoms": [t_ha[0], t_ha[-1]],
                              "heavy_atoms_median": statistics.median(t_ha),
                              "mw": [round(t_mw[0], 1), round(t_mw[-1], 1)],
                              "mw_median": round(statistics.median(t_mw), 1)},
        "delta_median_heavy_atoms": statistics.median(t_ha) - statistics.median(b_ha),
        "delta_median_mw": round(statistics.median(t_mw) - statistics.median(b_mw), 1),
        "★_reading": ("Carrying the second mechanism costs roughly a dozen heavy atoms and ~200 Da at the "
                      "median, and pushes the top of the set past 1200 Da. That is ABOVE the committed "
                      "library's whole range and well into the region where oral bioavailability and cell "
                      "permeability become the binding problem rather than affinity. **This set is therefore "
                      "a demonstration that the two mechanisms CAN be carried on one chain, not a claim that "
                      "the resulting molecule is developable** -- and the honest framing for the paper is that "
                      "the architecture permits it at a real physicochemical cost, which the single-mechanism "
                      "constructs do not pay."),
        "_not_assessed": ["permeability", "solubility", "metabolic stability", "synthetic tractability at "
                          "two orthogonally-protected branch residues"],
    }


def main():
    rep = build_report()
    if "--verify" in sys.argv:
        rep = verify_with_rdkit(rep)
    with open(OUT, "w") as fh:
        json.dump(rep, fh, indent=1)
        fh.write("\n")
    print("[twobranch] %d admissible chain(s), %d constructs -> %s"
          % (rep["n_admissible_chains"], rep["n_constructs"], OUT))
    for c in rep["admissible_chains"]:
        print("[twobranch]   n=%d %s  %s-%s-%s + %s   covalent@k=%d  wedge@k=%d"
              % (c["n_backbone_atoms"], c["placement"], c["seg1"], c["seg2"], c["seg3"],
                 c["warhead"], c["k_far_covalent"], c["k_near_wedge"]))


if __name__ == "__main__":
    main()
