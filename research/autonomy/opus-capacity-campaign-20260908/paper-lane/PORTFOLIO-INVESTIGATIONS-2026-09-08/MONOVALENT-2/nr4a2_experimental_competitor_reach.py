#!/usr/bin/env python3
"""Does the corridor closure verdict survive replacing the MODELLED NR4A2 competitor with EXPERIMENTAL ones?

WHY. `research/modalities/nr4a3-linker-covalent-reach.json` carries a 20-conformer EXPERIMENTAL spread
(8XTT) on the TARGET side (NR4A3 C397) but the COMPETITOR side is a single modelled conformer per
paralogue (`results/nr4a3-matrix/nr4a2-opened.pdb`, `nr4a1-opened.pdb`). The corridor tally that closes
the window names `NR4A2 C534` as the first-arriving competitor in 34 of 60 cells. Ten experimental NR4A2
LBD chains ARE committed (1OVL x6, 7WNH x4; established by the PUB-MONOVALENT lane). This script puts
each experimental chain through the SAME superposition + reach path the artifact uses for the modelled
paralogue, and recomputes the closure decision per corridor cell with the modelled NR4A2 competitor set
replaced by each experimental chain's.

BASELINE FIRST. The modelled NR4A2 rows are recomputed here by the same path and asserted, cell by cell,
against the committed `all_competitors_atoms["NR4A2 C*"]` in the artifact. If that does not reproduce,
nothing downstream is interpretable and the script exits non-zero without reporting a sensitivity.

SCOPE. Geometry only, corridor convention, primary clash cutoff 3.0 A. NR4A2 competitors only; NR4A3 and
NR4A1 competitor atoms and the target atoms are taken UNCHANGED from the committed artifact. No
reactivity, potency, selectivity, efficacy, safety or therapeutic-window claim is made or implied.
$0: pure CPU, repo modules, no network, no GPU.
"""
import gzip
import json
import os
import statistics
import sys

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research/modalities")
sys.path.insert(0, MOD)

import basin_geom as G                        # noqa: E402
import nr4a_differential_atlas as atlas       # noqa: E402
import nr4a3_basin_search as BS               # noqa: E402
import nr4a3_linker_covalent_reach as LCR     # noqa: E402
import nr4a3_covalent_handle_ensemble as COV  # noqa: E402

ARTIFACT = os.path.join(MOD, "nr4a3-linker-covalent-reach.json")
SEQ_CACHE = os.path.join(MOD, "nr4a-sequences-cache.json")
NR4A2_MODEL = os.path.join(REPO, "results/nr4a3-matrix/nr4a2-opened.pdb")
CRYSTALS = {"1OVL": os.path.join(MOD, "_s4_lane_inputs/1OVL.pdb.gz"),
            "7WNH": os.path.join(MOD, "_s4_lane_inputs/7WNH.pdb.gz")}
CUTOFF = LCR.CLASH_PRIMARY_A          # 3.0
CUTOFFS = (CUTOFF,)
CUT_KEY = "%.1f" % CUTOFF
HEAVY = BS.HEAVY
BACKBONE = BS.BACKBONE


def read_text(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rt") as fh:
            return fh.read()
    with open(path) as fh:
        return fh.read()


def parse_chain(text, chain):
    """(residues, atoms) for ONE protein chain, first MODEL only, heavy atoms, altloc blank/A."""
    residues, order, atoms = {}, [], []
    for ln in text.splitlines():
        if ln.startswith("ENDMDL"):
            break
        if not ln.startswith("ATOM") or ln[21] != chain:
            continue
        if ln[16] not in (" ", "A"):
            continue
        resn = ln[17:20].strip()
        if resn not in atlas.THREE2ONE:
            continue
        name = ln[12:16].strip()
        elem = (ln[76:78].strip() or name[0]).upper()
        if elem not in HEAVY:
            continue
        if ln[26] != " ":
            raise ValueError("insertion code at %r in chain %s" % (ln[22:27], chain))
        rid = int(ln[22:26])
        atoms.append({"resid": rid, "resname": resn, "name": name, "elem": elem,
                      "x": float(ln[30:38]), "y": float(ln[38:46]), "z": float(ln[46:54])})
        if rid not in residues:
            residues[rid] = atlas.THREE2ONE[resn]
            order.append(rid)
    return [(r, residues[r]) for r in order], atoms


def model_from_chain(residues, atoms, path):
    """The dict shape `BS.load_paralogue` returns, built from one already-parsed chain."""
    by_res = {}
    for a in atoms:
        by_res.setdefault(a["resid"], []).append(a)
    ca, cb = {}, {}
    for rid, alist in by_res.items():
        for a in alist:
            if a["name"] == "CA":
                ca[rid] = (a["x"], a["y"], a["z"])
        side = [a for a in alist if a["name"] not in BACKBONE]
        cb[rid] = G.centroid([(a["x"], a["y"], a["z"]) for a in side]) if side else ca.get(rid)
    return {"path": path, "residues": residues, "seq": "".join(aa for _, aa in residues),
            "ids": [r for r, _ in residues],
            "heavy_xyz": [(a["x"], a["y"], a["z"]) for a in atoms],
            "atoms_by_res": by_res, "ca": ca, "cb": cb,
            "aa_of": {rid: aa for rid, aa in residues}}


def protein_chains(text):
    out = []
    for ln in text.splitlines():
        if ln.startswith("ENDMDL"):
            break
        if ln.startswith("ATOM") and ln[17:20].strip() in atlas.THREE2ONE and ln[21] not in out:
            out.append(ln[21])
    return out


def nr4a2_atoms_by_cell(rows):
    """{(placement, pendant): {"NR4A2 C###": corridor_atoms}} from reach_one_frame rows."""
    out = {}
    for r in rows:
        for pname, e in r["by_pendant"].items():
            out.setdefault((r["placement"], pname), {})["NR4A2 %s" % r["cysteine"]] = \
                e["corridor_atoms"][CUT_KEY]
    return out


def main():
    art = json.load(open(ARTIFACT))
    cells = art["★_family_wide_chemoselectivity_window"]["by_convention"]["corridor"]
    seqs = json.load(open(SEQ_CACHE))
    nr4a2_seq = seqs["P43354"] if "P43354" in seqs else seqs["NR4A2"]
    if isinstance(nr4a2_seq, dict):
        nr4a2_seq = nr4a2_seq.get("sequence") or nr4a2_seq.get("seq")

    placements, _basins = LCR.load_placements()
    nr4a3 = BS.load_paralogue(LCR.OPENED["NR4A3"])

    frames = {}   # label -> {"rows":..., "fit":..., "identity":...}

    # ---------- BASELINE: the modelled NR4A2, recomputed by this same path ----------
    mob = BS.load_paralogue(LCR.OPENED["NR4A2"])
    res_m, _ = atlas.parse_pdb(LCR.OPENED["NR4A2"])
    uni_m, ident_m = COV.pdb_to_uniprot_map(res_m, nr4a2_seq, LCR.MIN_ALIGN_IDENTITY)
    moved_m = BS.superpose_paralogue(mob, nr4a3)
    r_m = LCR.reach_one_frame(moved_m, placements, set(), uni_m, CUTOFFS, label="NR4A2-opened")
    base = nr4a2_atoms_by_cell(r_m["rows"])

    mismatches, n_checked = [], 0
    for c in cells:
        key = (c["placement"], c["pendant"])
        committed = {k: v for k, v in c["all_competitors_atoms"].items() if k.startswith("NR4A2 ")}
        mine = {k: v for k, v in base.get(key, {}).items() if v is not None}
        for k in sorted(set(committed) | set(mine)):
            n_checked += 1
            if committed.get(k) != mine.get(k):
                mismatches.append({"cell": "%s|%s" % key, "competitor": k,
                                   "committed": committed.get(k), "recomputed": mine.get(k)})
    baseline = {"n_quantities_checked": n_checked, "n_mismatched": len(mismatches),
                "mismatches": mismatches[:40],
                "alignment_identity": round(ident_m, 4),
                "superposition": moved_m["superposition"]}
    print("BASELINE: %d/%d modelled-NR4A2 competitor atom counts reproduce"
          % (n_checked - len(mismatches), n_checked))
    if mismatches:
        print("BASELINE FAILED — first mismatches:")
        for m in mismatches[:10]:
            print("  ", m)
        json.dump({"baseline": baseline, "_status": "BASELINE FAILED — no sensitivity reported"},
                  open(OUT, "w"), indent=1)
        return 2

    # ---------- the experimental chains ----------
    for pdb, path in sorted(CRYSTALS.items()):
        text = read_text(path)
        for ch in protein_chains(text):
            lab = "%s_%s" % (pdb, ch)
            residues, atoms = parse_chain(text, ch)
            uni_map, ident = COV.pdb_to_uniprot_map(residues, nr4a2_seq, LCR.MIN_ALIGN_IDENTITY)
            m = model_from_chain(residues, atoms, path)
            moved = BS.superpose_paralogue(m, nr4a3)
            r = LCR.reach_one_frame(moved, placements, set(), uni_map, CUTOFFS, label=lab)
            frames[lab] = {
                "pdb": pdb, "chain": ch, "n_residues": len(residues),
                "alignment_identity": round(ident, 4),
                "superposition": moved["superposition"],
                "cysteines": sorted(r["cysteines"]),
                "atoms_by_cell": nr4a2_atoms_by_cell(r["rows"]),
                "invariant_violations": r["invariant_violations"],
            }
            print("frame %s: %d res, ident %.3f, core_rmsd %.2f A, cys %s"
                  % (lab, len(residues), ident, moved["superposition"]["core_rmsd_A"],
                     ",".join(sorted(r["cysteines"]))))

    # ---------- recompute the closure decision per corridor cell ----------
    per_cell = []
    for c in cells:
        key = (c["placement"], c["pendant"])
        others = {k: v for k, v in c["all_competitors_atoms"].items() if not k.startswith("NR4A2 ")}
        variants = {}
        for lab, f in frames.items():
            comp = dict(others)
            for k, v in f["atoms_by_cell"].get(key, {}).items():
                if v is not None:
                    comp[k] = v
            m = LCR.chemoselectivity_margin(c["target_atoms"], comp)
            variants[lab] = {"closed_by": m["blocked_by"], "closed_at_atoms": m["blocked_at_atoms"],
                             "width": m["width"],
                             "nr4a2_c534_atoms": f["atoms_by_cell"].get(key, {}).get("NR4A2 C534")}
        c534 = [v["nr4a2_c534_atoms"] for v in variants.values() if v["nr4a2_c534_atoms"] is not None]
        closers = sorted({v["closed_by"] for v in variants.values()}, key=lambda x: (x is None, x))
        per_cell.append({
            "placement": c["placement"], "pendant": c["pendant"],
            "target_atoms": c["target_atoms"],
            "committed": {"closed_by": c["closed_by"], "closed_at_atoms": c["closed_at_atoms"],
                          "width": c["width"],
                          "nr4a2_c534_atoms": c["all_competitors_atoms"].get("NR4A2 C534")},
            "experimental": {
                "n_frames": len(variants),
                "closers_seen": closers,
                "closer_unchanged_in_all_frames": closers == [c["closed_by"]],
                "widths_seen": sorted({v["width"] for v in variants.values()}),
                "any_window_opens": any(v["width"] > 0 for v in variants.values()),
                "nr4a2_c534_atoms": LCR.spread(c534),
                "by_frame": variants,
            }})

    n_open_committed = sum(1 for c in cells if c["width"] > 0)
    n_open_any = sum(1 for c in per_cell if c["experimental"]["any_window_opens"])
    n_closer_changed = sum(1 for c in per_cell if not c["experimental"]["closer_unchanged_in_all_frames"])
    c534_all = [v for c in per_cell for v in
                [c["experimental"]["nr4a2_c534_atoms"]["min"], c["experimental"]["nr4a2_c534_atoms"]["max"]]
                if v is not None]
    delta = [c["experimental"]["nr4a2_c534_atoms"]["max"] - c["experimental"]["nr4a2_c534_atoms"]["min"]
             for c in per_cell if c["experimental"]["nr4a2_c534_atoms"]["n"]]

    out = {
        "_title": "Corridor closure under EXPERIMENTAL NR4A2 competitor geometry (10 crystal chains)",
        "_question": ("The committed corridor tally closes the chemoselectivity window using ONE modelled "
                      "NR4A2 conformer. Does the closure verdict — and the 'NR4A2 C534 closes 34/60 cells' "
                      "reading — survive substituting each of the ten committed experimental NR4A2 LBD "
                      "chains through the same superposition and reach path?"),
        "_scope": ("Corridor convention, clash cutoff %.1f A, NR4A2 competitors substituted only. NR4A3 "
                   "and NR4A1 competitor atoms and the NR4A3 C397 target atoms are taken UNCHANGED from "
                   "the committed artifact. Geometry only." % CUTOFF),
        "_provenance": {
            "reach_engine": "research/modalities/nr4a3_linker_covalent_reach.py (imported unmodified: "
                            "reach_one_frame, chemoselectivity_margin, load_placements, spread)",
            "superposition": "nr4a3_basin_search.superpose_paralogue (unmodified)",
            "numbering": "nr4a3_covalent_handle_ensemble.pdb_to_uniprot_map, identity >= %.2f"
                         % LCR.MIN_ALIGN_IDENTITY,
            "committed_cells": "research/modalities/nr4a3-linker-covalent-reach.json -> "
                               "★_family_wide_chemoselectivity_window.by_convention.corridor",
            "experimental_structures": {k: os.path.relpath(v, REPO) for k, v in CRYSTALS.items()},
            "modelled_reference": os.path.relpath(NR4A2_MODEL, REPO),
        },
        "baseline_modelled_nr4a2_reproduces": baseline,
        "frames": {k: {kk: vv for kk, vv in v.items() if kk != "atoms_by_cell"}
                   for k, v in frames.items()},
        "summary": {
            "n_corridor_cells": len(per_cell),
            "n_cells_with_open_window_committed": n_open_committed,
            "n_cells_where_any_experimental_frame_opens_a_window": n_open_any,
            "n_cells_where_the_closer_identity_changes_in_at_least_one_frame": n_closer_changed,
            "nr4a2_c534_corridor_atoms_over_all_cells_and_frames": LCR.spread(c534_all),
            "per_cell_max_minus_min_c534_atoms": LCR.spread(delta),
        },
        "per_cell": per_cell,
        "_limits": [
            "1OVL and 7WNH are collapsed apo crystals; the modelled paralogue is biased open along a "
            "pocket CV. A systematic competitor-distance difference is EXPECTED and is not a refutation "
            "of either structure.",
            "Chains within one crystal are not independent measurements; 1OVL contributes 6 and 7WNH 4.",
            "Only the NR4A2 competitor set is varied. The NR4A3 target reach, the NR4A3 conserved "
            "competitors and ALL NR4A1 competitors remain single-conformer modelled readings, and NR4A1 "
            "has no experimental coordinates in this checkout at all.",
            "Corridor convention at one clash cutoff (3.0 A); the committed sweep 2.0/2.6/3.0/3.4 is not "
            "reproduced here.",
            "Geometry only: no thiol pKa, reactivity, adduct, potency, selectivity, safety, therapeutic "
            "window or clinical readiness is computed, claimed or implied.",
        ],
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("\nSUMMARY")
    print(json.dumps(out["summary"], indent=1))
    return 0


OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "nr4a2-experimental-competitor-reach.json")

if __name__ == "__main__":
    sys.exit(main())
