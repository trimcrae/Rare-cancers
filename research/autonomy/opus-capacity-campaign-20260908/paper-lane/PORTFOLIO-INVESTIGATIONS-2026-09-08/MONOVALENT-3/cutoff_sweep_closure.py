#!/usr/bin/env python3
"""Is the corridor closure that survived experimental NR4A2 geometry a STRUCTURAL fact, or an artifact
of the PRIMARY clash cutoff?

WHY. MONOVALENT-2 substituted ten experimental NR4A2 LBD chains into the committed corridor decision and
found the open/closed verdict identical on all 60 cells -- but it did so at ONE clash cutoff (3.0 A). The
committed engine declares a whole sweep, `CLASH_SWEEP_A = (2.0, 2.6, 3.0, 3.4)` (line 136 of
`research/modalities/nr4a3_linker_covalent_reach.py`), precisely so that no single value is load-bearing.
This script crosses the two dimensions: four cutoffs x ten experimental chains x 60 corridor cells.

NOTHING IS RE-RULED. `cutoffs` is already threaded through `reach_one_frame`; the sweep values are read
from the committed module and never redefined here. No cutoff is adjusted to preserve any verdict.

GATES, IN ORDER.
  A. Before ANY experimental chain is read: the modelled NR4A2 competitor atom counts must reproduce
     end-to-end by this same code path against the committed artifact -- 300/300, hard exit 2 otherwise.
  B. At the PRIMARY cutoff the recomputed corridor tally must be MONOVALENT-2's published
     34 (NR4A2 C534) / 8 (NR4A1 C505) / 18 (none) of 60, EXACTLY -- hard exit 3 otherwise.
A gate failure IS the result and is reported digit for digit.

SCOPE. Geometry only. Only the NR4A2 competitor set is substituted; NR4A3 target reach, NR4A3 conserved
competitors and ALL NR4A1 competitors are taken UNCHANGED from the committed artifact at each cutoff (the
committed artifact carries all four cutoffs for every opened frame). NR4A1 has NO experimental coordinates
in this checkout and none may be fetched, so every NR4A1-side statement here is un-error-barred and says
so. No reactivity, potency, selectivity, efficacy, safety, therapeutic-window or clinical-readiness claim
is made or implied. $0: repo modules, CPU only, no network, no GPU. Conformer/structure trees are read
IN PLACE, never copied.
"""
import gzip
import json
import os
import sys
import time

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
CRYSTALS = {"1OVL": os.path.join(MOD, "_s4_lane_inputs/1OVL.pdb.gz"),
            "7WNH": os.path.join(MOD, "_s4_lane_inputs/7WNH.pdb.gz")}

CUTOFFS = LCR.CLASH_SWEEP_A            # (2.0, 2.6, 3.0, 3.4) -- imported, never retyped
PRIMARY = LCR.CLASH_PRIMARY_A          # 3.0
PRIMARY_KEY = "%.1f" % PRIMARY
HEAVY = BS.HEAVY
BACKBONE = BS.BACKBONE

# MONOVALENT-2's published primary-cutoff corridor tally. This is the control, not a target.
GATE_B_EXPECTED = {"NR4A2 C534": 34, "NR4A1 C505": 8, None: 18}
GATE_B_N_CELLS = 60

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cutoff-sweep-closure.json")


# ---------------------------------------------------------------------------------------------------
# parsing helpers -- identical to MONOVALENT-2's (reused, not re-derived)
# ---------------------------------------------------------------------------------------------------
def read_text(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rt") as fh:
            return fh.read()
    with open(path) as fh:
        return fh.read()


def parse_chain(text, chain):
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


def nr4a2_atoms_by_cell(rows, cut_key):
    """{(placement, pendant): {"NR4A2 C###": corridor_atoms at cut_key}}"""
    out = {}
    for r in rows:
        for pname, e in r["by_pendant"].items():
            out.setdefault((r["placement"], pname), {})["NR4A2 %s" % r["cysteine"]] = \
                e["corridor_atoms"][cut_key]
    return out


def cells_at_cutoff(nr4a3_rows, nr4a1_rows, nr4a2_rows, cutoff):
    """The committed engine's own corridor cell builder, at one cutoff, with a given NR4A2 row set."""
    par = {"opened": {"NR4A1": {"rows": nr4a1_rows}, "NR4A2": {"rows": nr4a2_rows}}}
    return LCR.paralogue_inclusive_window(nr4a3_rows, par, convention="corridor", cutoff=cutoff)


def tally(cells):
    t = {}
    for c in cells:
        t[c["closed_by"]] = t.get(c["closed_by"], 0) + 1
    return t


def tkey(k):
    return "none" if k is None else k


def main():
    t0 = time.time()
    art = json.load(open(ARTIFACT))
    committed_cells = art["★_family_wide_chemoselectivity_window"]["by_convention"]["corridor"]
    nr4a3_rows = art["designed_frame"]["rows"]
    nr4a1_rows = art["paralogue_control"]["opened"]["NR4A1"]["rows"]
    nr4a2_rows_committed = art["paralogue_control"]["opened"]["NR4A2"]["rows"]

    seqs = json.load(open(SEQ_CACHE))
    nr4a2_seq = seqs["P43354"] if "P43354" in seqs else seqs["NR4A2"]
    if isinstance(nr4a2_seq, dict):
        nr4a2_seq = nr4a2_seq.get("sequence") or nr4a2_seq.get("seq")

    placements, _basins = LCR.load_placements()
    nr4a3 = BS.load_paralogue(LCR.OPENED["NR4A3"])

    # ===============================================================================================
    # GATE A -- modelled NR4A2 competitor atom counts, recomputed end to end. BEFORE any experimental
    # chain is read. 300/300 or hard exit 2.
    # ===============================================================================================
    mob = BS.load_paralogue(LCR.OPENED["NR4A2"])
    res_m, _ = atlas.parse_pdb(LCR.OPENED["NR4A2"])
    uni_m, ident_m = COV.pdb_to_uniprot_map(res_m, nr4a2_seq, LCR.MIN_ALIGN_IDENTITY)
    moved_m = BS.superpose_paralogue(mob, nr4a3)
    r_m = LCR.reach_one_frame(moved_m, placements, set(), uni_m, CUTOFFS, label="NR4A2-opened")
    base = nr4a2_atoms_by_cell(r_m["rows"], PRIMARY_KEY)

    mismatches, n_checked = [], 0
    for c in committed_cells:
        key = (c["placement"], c["pendant"])
        committed = {k: v for k, v in c["all_competitors_atoms"].items() if k.startswith("NR4A2 ")}
        mine = {k: v for k, v in base.get(key, {}).items() if v is not None}
        for k in sorted(set(committed) | set(mine)):
            n_checked += 1
            if committed.get(k) != mine.get(k):
                mismatches.append({"cell": "%s|%s" % key, "competitor": k,
                                   "committed": committed.get(k), "recomputed": mine.get(k)})
    gate_a = {"gate": "A -- modelled NR4A2 competitor atom counts reproduce at the primary cutoff "
                      "%.1f A, before any experimental chain is read" % PRIMARY,
              "n_quantities_checked": n_checked, "n_reproduced": n_checked - len(mismatches),
              "n_mismatched": len(mismatches), "mismatches": mismatches[:40],
              "alignment_identity": round(ident_m, 4),
              "superposition": moved_m["superposition"],
              "passed": not mismatches and n_checked == 300}
    print("GATE A: %d/%d modelled-NR4A2 competitor atom counts reproduce (expected 300/300)"
          % (n_checked - len(mismatches), n_checked))
    if mismatches or n_checked != 300:
        print("GATE A FAILED — the gate failure IS the result. First mismatches:")
        for m in mismatches[:10]:
            print("  ", m)
        json.dump({"_status": "GATE A FAILED — no sensitivity reported", "gate_a": gate_a},
                  open(OUT, "w"), indent=1)
        return 2

    # Supplementary (non-gating, reported): does the recomputed modelled frame also reproduce the
    # committed NR4A2-opened rows at the OTHER three cutoffs? Reported, never used to license anything.
    mine_by_cut = {("%.1f" % cut): nr4a2_atoms_by_cell(r_m["rows"], "%.1f" % cut) for cut in CUTOFFS}
    comm_by_cut = {("%.1f" % cut): nr4a2_atoms_by_cell(nr4a2_rows_committed, "%.1f" % cut)
                   for cut in CUTOFFS}
    sweep_recheck = {}
    for cut in CUTOFFS:
        k = "%.1f" % cut
        n_ok = n_bad = 0
        bad = []
        for cell, d in comm_by_cut[k].items():
            for comp, v in d.items():
                if mine_by_cut[k].get(cell, {}).get(comp) == v:
                    n_ok += 1
                else:
                    n_bad += 1
                    bad.append({"cell": "%s|%s" % cell, "competitor": comp, "committed": v,
                                "recomputed": mine_by_cut[k].get(cell, {}).get(comp)})
        sweep_recheck[k] = {"n_reproduced": n_ok, "n_mismatched": n_bad, "mismatches": bad[:20]}
    print("supplementary: committed NR4A2-opened rows reproduce per cutoff: " +
          ", ".join("%s A %d/%d" % (k, v["n_reproduced"], v["n_reproduced"] + v["n_mismatched"])
                    for k, v in sweep_recheck.items()))

    # ===============================================================================================
    # GATE B -- at the PRIMARY cutoff the sweep must return 34 / 8 / 18 of 60, exactly.
    # ===============================================================================================
    committed_sweep = {}
    for cut in CUTOFFS:
        cells = cells_at_cutoff(nr4a3_rows, nr4a1_rows, nr4a2_rows_committed, cut)
        committed_sweep["%.1f" % cut] = cells
    prim_cells = committed_sweep[PRIMARY_KEY]
    prim_tally = tally(prim_cells)
    gate_b_obs = {tkey(k): v for k, v in prim_tally.items()}
    gate_b_exp = {tkey(k): v for k, v in GATE_B_EXPECTED.items()}
    gate_b_ok = (len(prim_cells) == GATE_B_N_CELLS and gate_b_obs == gate_b_exp)
    gate_b = {"gate": "B -- at the primary cutoff %.1f A the sweep returns MONOVALENT-2's published "
                      "corridor tally exactly" % PRIMARY,
              "expected": gate_b_exp, "expected_n_cells": GATE_B_N_CELLS,
              "observed": gate_b_obs, "observed_n_cells": len(prim_cells),
              "passed": gate_b_ok}
    print("GATE B: observed %s over %d cells; expected %s over %d"
          % (json.dumps(gate_b_obs, sort_keys=True), len(prim_cells),
             json.dumps(gate_b_exp, sort_keys=True), GATE_B_N_CELLS))
    if not gate_b_ok:
        print("GATE B FAILED — the gate failure IS the result.")
        json.dump({"_status": "GATE B FAILED — no sensitivity reported",
                   "gate_a": gate_a, "gate_b": gate_b}, open(OUT, "w"), indent=1)
        return 3

    # Extra control (reported): the recomputed primary cells must equal the committed corridor cells
    # field for field on the decision quantities.
    cell_identity = {"n_cells": len(prim_cells), "n_field_mismatches": 0, "mismatches": []}
    cmap = {(c["placement"], c["pendant"]): c for c in committed_cells}
    for c in prim_cells:
        k = (c["placement"], c["pendant"])
        o = cmap.get(k)
        if o is None:
            cell_identity["n_field_mismatches"] += 1
            cell_identity["mismatches"].append({"cell": "%s|%s" % k, "field": "MISSING_IN_COMMITTED"})
            continue
        for f in ("target_atoms", "window_lo", "window_hi", "width", "closed_by", "closed_at_atoms"):
            if c[f] != o[f]:
                cell_identity["n_field_mismatches"] += 1
                cell_identity["mismatches"].append({"cell": "%s|%s" % k, "field": f,
                                                   "recomputed": c[f], "committed": o[f]})
    print("control: recomputed primary cells vs committed corridor cells — %d field mismatches"
          % cell_identity["n_field_mismatches"])

    # ===============================================================================================
    # THE SWEEP -- ten experimental chains x four cutoffs
    # ===============================================================================================
    frames = {}
    for pdb, path in sorted(CRYSTALS.items()):
        text = read_text(path)                      # read IN PLACE, no copy
        for ch in protein_chains(text):
            lab = "%s_%s" % (pdb, ch)
            residues, atoms = parse_chain(text, ch)
            uni_map, ident = COV.pdb_to_uniprot_map(residues, nr4a2_seq, LCR.MIN_ALIGN_IDENTITY)
            m = model_from_chain(residues, atoms, path)
            moved = BS.superpose_paralogue(m, nr4a3)
            r = LCR.reach_one_frame(moved, placements, set(), uni_map, CUTOFFS, label=lab)
            frames[lab] = {"pdb": pdb, "chain": ch, "n_residues": len(residues),
                           "alignment_identity": round(ident, 4),
                           "superposition": moved["superposition"],
                           "cysteines": sorted(r["cysteines"]),
                           "invariant_violations": r["invariant_violations"],
                           "rows": r["rows"]}
            print("frame %s: %d res, ident %.3f, core_rmsd %.2f A, cys %s  [%.0fs]"
                  % (lab, len(residues), ident, moved["superposition"]["core_rmsd_A"],
                     ",".join(sorted(r["cysteines"])), time.time() - t0))

    # per (cutoff, frame) corridor cells
    exp_cells = {}   # cut_key -> frame -> {(pl,pen): cell}
    for cut in CUTOFFS:
        k = "%.1f" % cut
        exp_cells[k] = {}
        for lab, f in frames.items():
            cells = cells_at_cutoff(nr4a3_rows, nr4a1_rows, f["rows"], cut)
            exp_cells[k][lab] = {(c["placement"], c["pendant"]): c for c in cells}

    order = [(c["placement"], c["pendant"]) for c in prim_cells]
    per_cell = []
    for key in order:
        rec = {"placement": key[0], "pendant": key[1], "by_cutoff": {}}
        for cut in CUTOFFS:
            k = "%.1f" % cut
            comm = {(c["placement"], c["pendant"]): c for c in committed_sweep[k]}[key]
            byframe = {}
            for lab in sorted(frames):
                c = exp_cells[k][lab][key]
                byframe[lab] = {"closed_by": c["closed_by"], "closed_at_atoms": c["closed_at_atoms"],
                                "width": c["width"], "open": c["width"] > 0,
                                "nr4a2_c534_atoms": c["all_competitors_atoms"].get("NR4A2 C534")}
            closers = sorted({v["closed_by"] for v in byframe.values()},
                             key=lambda x: (x is None, x))
            rec["by_cutoff"][k] = {
                "target_atoms": comm["target_atoms"],
                "committed_modelled": {"closed_by": comm["closed_by"], "width": comm["width"],
                                       "closed_at_atoms": comm["closed_at_atoms"],
                                       "open": comm["width"] > 0,
                                       "nr4a2_c534_atoms":
                                           comm["all_competitors_atoms"].get("NR4A2 C534")},
                "experimental": {
                    "n_frames": len(byframe),
                    "open_in_any_frame": any(v["open"] for v in byframe.values()),
                    "open_in_all_frames": all(v["open"] for v in byframe.values()),
                    "closers_seen": [tkey(x) for x in closers],
                    "closer_unchanged_in_all_frames": closers == [comm["closed_by"]],
                    "widths_seen": sorted({v["width"] for v in byframe.values()}),
                    "nr4a2_c534_atoms": LCR.spread(
                        [v["nr4a2_c534_atoms"] for v in byframe.values()]),
                    "by_frame": byframe,
                },
            }
        # ---- where does a decision FLIP along the cutoff axis? ----
        opencl = {k: rec["by_cutoff"][k]["committed_modelled"]["open"] for k in rec["by_cutoff"]}
        exp_open_any = {k: rec["by_cutoff"][k]["experimental"]["open_in_any_frame"]
                        for k in rec["by_cutoff"]}
        clsr = {k: rec["by_cutoff"][k]["committed_modelled"]["closed_by"] for k in rec["by_cutoff"]}
        ks = ["%.1f" % c for c in CUTOFFS]
        rec["flips"] = {
            "committed_open_closed_flips_at": [ks[i] for i in range(1, len(ks))
                                               if opencl[ks[i]] != opencl[ks[i - 1]]],
            "experimental_open_in_any_frame_flips_at": [ks[i] for i in range(1, len(ks))
                                                        if exp_open_any[ks[i]] != exp_open_any[ks[i - 1]]],
            "committed_closer_identity_changes_at": [ks[i] for i in range(1, len(ks))
                                                     if clsr[ks[i]] != clsr[ks[i - 1]]],
            "open_closed_agrees_with_primary_at_all_cutoffs":
                all(opencl[k] == opencl[PRIMARY_KEY] for k in ks) and
                all(exp_open_any[k] == exp_open_any[PRIMARY_KEY] for k in ks),
        }
        per_cell.append(rec)

    # ---- tallies per cutoff ----
    tallies = {}
    for cut in CUTOFFS:
        k = "%.1f" % cut
        cells = committed_sweep[k]
        tallies[k] = {
            "n_cells": len(cells),
            "committed_modelled_tally": {tkey(a): b for a, b in
                                         sorted(tally(cells).items(), key=lambda kv: tkey(kv[0]))},
            "n_open_committed": sum(1 for c in cells if c["width"] > 0),
            "per_experimental_frame": {},
        }
        for lab in sorted(frames):
            fc = [exp_cells[k][lab][key] for key in order]
            tallies[k]["per_experimental_frame"][lab] = {
                "tally": {tkey(a): b for a, b in sorted(tally(fc).items(), key=lambda kv: tkey(kv[0]))},
                "n_open": sum(1 for c in fc if c["width"] > 0),
            }
        opens = [tallies[k]["per_experimental_frame"][l]["n_open"] for l in sorted(frames)]
        c534 = [tallies[k]["per_experimental_frame"][l]["tally"].get("NR4A2 C534", 0)
                for l in sorted(frames)]
        tallies[k]["experimental_n_open_range"] = [min(opens), max(opens)]
        tallies[k]["experimental_nr4a2_c534_closer_count_range"] = [min(c534), max(c534)]
        _comm_open = {(c["placement"], c["pendant"]): (c["width"] > 0) for c in cells}
        tallies[k]["open_closed_set_identical_to_committed_in_every_frame"] = all(
            (exp_cells[k][l][key]["width"] > 0) == _comm_open[key]
            for l in sorted(frames) for key in order)

    # exact per-cell open/closed set comparison (independent of the count above)
    setcmp = {}
    for cut in CUTOFFS:
        k = "%.1f" % cut
        comm = {(c["placement"], c["pendant"]): (c["width"] > 0) for c in committed_sweep[k]}
        diffs = []
        for lab in sorted(frames):
            for key in order:
                if (exp_cells[k][lab][key]["width"] > 0) != comm[key]:
                    diffs.append({"frame": lab, "cell": "%s|%s" % key,
                                  "committed_open": comm[key],
                                  "experimental_open": exp_cells[k][lab][key]["width"] > 0})
        setcmp[k] = {"n_cell_frame_open_closed_differences": len(diffs), "differences": diffs[:60]}

    # where along the cutoff axis does ANY decision flip?
    flip_cells_open = [("%s|%s" % (c["placement"], c["pendant"]), c["flips"])
                       for c in per_cell
                       if c["flips"]["committed_open_closed_flips_at"] or
                       c["flips"]["experimental_open_in_any_frame_flips_at"]]
    flip_cells_closer = [("%s|%s" % (c["placement"], c["pendant"]),
                          c["flips"]["committed_closer_identity_changes_at"])
                         for c in per_cell if c["flips"]["committed_closer_identity_changes_at"]]

    out = {
        "_title": "Clash-cutoff sweep of the corridor closure under experimental NR4A2 competitor geometry",
        "_question": ("Is the corridor closure that survived experimental NR4A2 competitor geometry "
                      "(MONOVALENT-2, primary cutoff only) a structural fact, or an artifact of the "
                      "primary clash cutoff? Four committed cutoffs x ten experimental NR4A2 LBD chains "
                      "x 60 corridor cells."),
        "_scope": ("Corridor convention. Only the NR4A2 competitor set is substituted; the NR4A3 C397 "
                   "target reach, the NR4A3 conserved competitors and ALL NR4A1 competitors are taken "
                   "UNCHANGED from the committed artifact AT EACH CUTOFF. Geometry only: no reactivity, "
                   "pKa, potency, selectivity, efficacy, safety, therapeutic window or clinical "
                   "readiness is computed, claimed or implied."),
        "_cutoffs_A": list(CUTOFFS),
        "_primary_cutoff_A": PRIMARY,
        "_cutoffs_source": ("research/modalities/nr4a3_linker_covalent_reach.py line 136, "
                            "CLASH_SWEEP_A — imported, never redefined here. No cutoff was adjusted."),
        "_nr4a1_caveat": ("NR4A1 has NO experimental coordinates in this checkout and none may be "
                          "fetched. Every NR4A1-side reading below — including every cell whose closer "
                          "is NR4A1 C505 — rests on a SINGLE modelled conformer and is un-error-barred."),
        "_provenance": {
            "reach_engine": ("research/modalities/nr4a3_linker_covalent_reach.py imported unmodified: "
                             "reach_one_frame, paralogue_inclusive_window, chemoselectivity_margin, "
                             "load_placements, spread, CLASH_SWEEP_A, CLASH_PRIMARY_A"),
            "superposition": "nr4a3_basin_search.superpose_paralogue (unmodified)",
            "numbering": ("nr4a3_covalent_handle_ensemble.pdb_to_uniprot_map, identity >= %.2f"
                          % LCR.MIN_ALIGN_IDENTITY),
            "committed_artifact": "research/modalities/nr4a3-linker-covalent-reach.json",
            "committed_rows_used_unchanged": ["designed_frame.rows (NR4A3, all four cutoffs)",
                                              "paralogue_control.opened.NR4A1.rows (all four cutoffs)"],
            "experimental_structures": {k: os.path.relpath(v, REPO) for k, v in CRYSTALS.items()},
            "chain_parser": ("reused unmodified from "
                             "MONOVALENT-2/nr4a2_experimental_competitor_reach.py"),
            "read_in_place": True,
        },
        "gate_a_modelled_baseline": gate_a,
        "gate_b_primary_cutoff_tally": gate_b,
        "control_recomputed_primary_cells_vs_committed": cell_identity,
        "supplementary_committed_nr4a2_rows_reproduce_per_cutoff": sweep_recheck,
        "frames": {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in frames.items()},
        "tally_per_cutoff": tallies,
        "open_closed_set_vs_committed_per_cutoff": setcmp,
        "flips": {
            "_definition": ("A flip is a change in a cell's decision BETWEEN ADJACENT CUTOFFS along "
                            "(2.0, 2.6, 3.0, 3.4). 'open_closed' is the load-bearing verdict "
                            "(width > 0 means a chemoselective window exists); 'closer identity' is "
                            "the residue attribution."),
            "n_cells_whose_open_closed_decision_flips_along_the_cutoff_axis": len(flip_cells_open),
            "cells_with_an_open_closed_flip": flip_cells_open[:60],
            "n_cells_whose_closer_identity_changes_along_the_cutoff_axis": len(flip_cells_closer),
            "cells_with_a_closer_identity_change": flip_cells_closer[:60],
        },
        "per_cell": per_cell,
        "_limits": [
            "1OVL and 7WNH are collapsed apo crystals; the modelled paralogue is biased open along a "
            "pocket CV. A systematic competitor-distance difference is EXPECTED and refutes neither.",
            "Chains within one crystal are not independent measurements; 1OVL contributes 6 and 7WNH 4.",
            "Only the NR4A2 competitor set varies. NR4A1 has no experimental coordinates in this "
            "checkout, so the NR4A1 side of every closer swap is un-error-barred.",
            "The four cutoffs are not independent either: the corridor candidate set is nested, so a "
            "larger cutoff can only ever lengthen or remove a corridor, never shorten one.",
            "Geometry only: no thiol pKa, reactivity, adduct, potency, selectivity, safety, "
            "therapeutic window or clinical readiness is computed, claimed or implied. A geometric "
            "corridor result is NEVER an EMC efficacy, safety, selectivity, therapeutic-window or "
            "clinical-readiness claim.",
        ],
        "_runtime_s": round(time.time() - t0, 1),
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("\nTALLY PER CUTOFF")
    for cut in CUTOFFS:
        k = "%.1f" % cut
        t = tallies[k]
        print(" %s A: committed %s | n_open %d | exp n_open range %s | exp C534-closer range %s"
              % (k, json.dumps(t["committed_modelled_tally"], sort_keys=True), t["n_open_committed"],
                 t["experimental_n_open_range"], t["experimental_nr4a2_c534_closer_count_range"]))
        print("       cell-frame open/closed differences vs committed: %d"
              % setcmp[k]["n_cell_frame_open_closed_differences"])
    print("\nFLIPS along the cutoff axis: open/closed in %d cells; closer identity in %d cells"
          % (len(flip_cells_open), len(flip_cells_closer)))
    print("runtime %.1f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
