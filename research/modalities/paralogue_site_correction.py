#!/usr/bin/env python3
"""Correct the PARALOGUE docking site — the step `apo-pose-regime-dock.json` showed is the whole failure.

★★ WHY THIS EXISTS (trimcrae, 2026-08-03: *"Ok I guess do the $0 fix then and document it everywhere"*).

`nr4a3_warhead.py:314` builds NR4A1's and NR4A2's docking boxes by **copying NR4A3's pocket onto them** —
`map_pocket_to_paralogue()` carries the Pocket-5 residues across a BLOSUM62 alignment and `pocket_box()`
centres a 24 A box on their CA centroid. NR4A3's own box is NOT built that way; it is found directly on
the NR4A3 structure. So the two halves of every selectivity statement rest on different methods, and
`MODE=regime_dock` measured what those methods are worth on the NR4A fold, against 11 deposited
crystallographic answers:

    box drawn by                blind-from-apo dock, MINUS this protocol's own best on the SAME pair
    the receptor's own cavity   median  +0.39 A   — and it beats the holo oracle outright on 3 of 11
    the Pocket-5 transfer       median +16.05 A   — worse on 11 of 11

⇒ **The transfer is the failure, and it is the step that places every ANTI-TARGET box in the program.**

⛔ WHAT THAT DOES TO THE SELECTIVITY NUMBERS, STATED PLAINLY. A selectivity result is a COMPARISON. If the
NR4A3 arm is docked in a real pocket and the paralogue arms are docked 16-19 A from theirs, then a
"paralogue-selective" margin is the difference between a real pocket and two misplaced ones — which any
molecule would show. That is not a selectivity measurement, and it would explain the implausible size of
the one the program holds (ABFE ddG ~ -4.8 / -5.0 kcal/mol, i.e. ~3,000x).

★ THE FIX IS AVAILABLE AND COSTS NOTHING, AND IT IS BETTER THAN "USE A CAVITY DETECTOR INSTEAD."
NR4A1 and NR4A2 have **deposited holo structures**. We do not have to infer where a ligand binds on them;
crystallography already answered. So this module defines each paralogue's site from the ligand positions in
its own deposited structures, superposed into the frame of the AF2 model the pipeline actually docks into.

    1. fetch the AF2 model `nr4a3_warhead` docks into (the same alphafold.ebi.ac.uk call it makes)
    2. rebuild the pipeline's TRANSFERRED box on that model, through the pipeline's own two functions
    3. for each deposited holo entry: CE-superpose it onto the AF2 model, carry its crystallographic
       ligand into the AF2 frame  (CE is sequence-independent, so it cannot inherit the alignment defect
       being measured)
    4. the CORRECTED site is the consensus of those ligand positions
    5. report the displacement between (2) and (4), and whether the pipeline's own 24 A box contains the
       crystallographic ligand at all

⚠ SCOPE, AND IT IS NARROW ON PURPOSE.
  - This RE-SCORES NOTHING. It moves no ddG, re-runs no leg, and overturns no verdict. It emits a corrected
    site and a measured displacement; consuming them is a separate, explicit step per artifact.
  - The holo entry list is READ from `apo-pose-site-in-regime.json`, never typed here — one fact, one place,
    and it is the same in-regime set the docking panel graded.
  - NR4A3's own site is NOT touched. It was never built by the transfer, and nothing here re-derives it.
  - A paralogue with no readable deposited ligand is REFUSED, not guessed. An absent reading is not a
    reading of absence (CLAUDE.md SS4).

Output: paralogue-site-correction.json. Network (AlphaFold API + RCSB) and Bio.PDB; no smina, no fpocket,
no GPU, no rental. $0.
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "paralogue-site-correction.json")
SITE_PANEL = os.path.join(HERE, "apo-pose-site-in-regime.json")
WORK = os.environ.get("PARA_SITE_WORK", os.path.join(HERE, "_paralogue_site_work"))

#: The pipeline's own box edge, read from `nr4a3_warhead.dock_into`'s smina call rather than retyped.
#: A containment test against a different size would be a test of a box the pipeline never draws.
BOX_EDGE_A = 24.0


def _pipeline_box_edge():
    """Read `--size_x` out of `dock_into`'s source. ONE HOME: if the pipeline's box changes, this follows."""
    import inspect
    import nr4a3_warhead as wh
    src = inspect.getsource(wh.dock_into)
    for tok in ('"--size_x", "', "'--size_x', '"):
        if tok in src:
            rest = src.split(tok, 1)[1]
            return float(rest.split(rest[0] if rest[0] in "\"'" else '"', 1)[0] or BOX_EDGE_A)
    return BOX_EDGE_A


def in_regime_holo_entries():
    """The deposited holo entries per paralogue, READ from the committed site panel rather than typed.

    ⚠ It carries COVALENT entries too, and they are kept here on purpose. `R2b` excludes a covalent ligand
    from a DOCKING panel because a non-covalent dock cannot reproduce a covalent pose — but this module
    runs no dock. It asks only WHERE the ligand sits, which crystallography answered either way, and both
    NR4A2 entries in that panel are covalent. Dropping them would leave NR4A3's closest paralogue with no
    correction at all, for a reason that does not apply.
    """
    with open(SITE_PANEL) as fh:
        panel = json.load(fh)["site_panel_in_regime"]
    out = {}
    for row in panel["pairs"]:
        acc = row.get("accession")
        if not acc or not row.get("holo") or not row.get("ligand"):
            continue
        out.setdefault(acc, {"protein": row.get("protein"), "entries": []})
        out[acc]["entries"].append({"holo": row["holo"], "ligand": row["ligand"],
                                    "covalent": bool(row.get("covalent"))})
    return out


def fetch_af2(acc, dest):
    """The SAME AlphaFold call `nr4a3_warhead` makes — this must be the model the pipeline docks into,
    not a re-prediction, or the displacement would be measured against a receptor nobody uses."""
    import nr4a3_dock as dock
    url = json.loads(dock._get("https://alphafold.ebi.ac.uk/api/prediction/%s" % acc))[0]["pdbUrl"]
    with open(dest, "wb") as fh:
        fh.write(dock._get(url, timeout=120))
    return dest


def pipeline_transferred_box(nr4a3_pdb, para_pdb, pocket_resnums):
    """The box the pipeline ACTUALLY draws on this paralogue — through its own two functions, not a
    reimplementation. A hand-rolled copy could differ from the shipping code in exactly the way that
    would make this measurement wrong."""
    import nr4a3_warhead as wh
    try:
        para_res = wh.map_pocket_to_paralogue(nr4a3_pdb, para_pdb, pocket_resnums)
    except Exception as e:                                     # noqa: BLE001
        return None, "map_pocket_to_paralogue failed: %s: %s" % (type(e).__name__, e)
    if not para_res:
        return None, ("0 pocket residues mapped — the pipeline itself raises here and records "
                      "`selectivity_evaluated: false`")
    try:
        center, n_ca = wh.pocket_box(para_pdb, para_res)
    except Exception as e:                                     # noqa: BLE001
        return None, "pocket_box failed: %s: %s" % (type(e).__name__, e)
    return {"center": [round(c, 3) for c in center], "n_pocket_ca": n_ca,
            "n_residues_mapped": len(para_res)}, None


def crystal_site_in_af2_frame(holo_pdb_path, comp_id, af2_pdb_path):
    """Carry a deposited ligand into the AF2 model's frame by CE structural superposition.

    ⛔ CE, NOT SEQUENCE ALIGNMENT — and that is the whole point rather than a preference. The defect being
    measured lives in a BLOSUM62 residue mapping; validating it with another sequence alignment could
    inherit the same error and agree with it. `Bio.PDB.cealign` matches the two folds without reading the
    sequence at all, so agreement or disagreement here is independent evidence.
    """
    import apo_pose_recovery as apr
    try:
        from Bio.PDB import PDBParser
        from Bio.PDB.cealign import CEAligner
    except Exception as e:                                     # noqa: BLE001
        return None, "Bio.PDB.cealign unavailable: %s: %s" % (type(e).__name__, e)

    holo_txt = apr._read(holo_pdb_path)
    lines, _key = apr.ligand_hetatms(holo_txt, comp_id)
    if not lines:
        return None, "no HETATM copy of %s in %s" % (comp_id, os.path.basename(holo_pdb_path))
    lig = apr.het_coords(lines)

    try:
        parser = PDBParser(QUIET=True)
        af2 = parser.get_structure("af2", af2_pdb_path)
        holo = parser.get_structure("holo", holo_pdb_path)
        aligner = CEAligner()
        aligner.set_reference(af2)
        aligner.align(holo)                                     # moves `holo` into the AF2 frame
    except Exception as e:                                      # noqa: BLE001
        return None, "CE structural alignment failed: %s: %s" % (type(e).__name__, e)

    # The aligner moved the STRUCTURE object; recover the rigid transform from paired CA before/after and
    # apply it to the ligand, which is a HETATM and therefore not carried by the superposition itself.
    import nr4a3_8xtt_benchmark as bm
    before, after = [], []
    for res in holo.get_residues():
        if "CA" in res:
            after.append(tuple(float(v) for v in res["CA"].coord))
    holo2 = PDBParser(QUIET=True).get_structure("holo2", holo_pdb_path)
    for res in holo2.get_residues():
        if "CA" in res:
            before.append(tuple(float(v) for v in res["CA"].coord))
    n = min(len(before), len(after))
    if n < 3:
        return None, "fewer than 3 CA atoms to recover the superposition transform"
    try:
        R, t = bm.kabsch_transform(before[:n], after[:n])
        moved = bm.apply_transform(lig, R, t)
    except Exception as e:                                      # noqa: BLE001
        return None, "could not recover the CE transform: %s: %s" % (type(e).__name__, e)
    return {"ligand_centroid_af2_frame": [round(c, 3) for c in bm.centroid(moved)],
            "n_ligand_heavy_atoms": len(moved),
            "ce_rms_A": round(float(getattr(aligner, "rms", float("nan"))), 3),
            "n_ca_superposed": n}, None


def _centroid(points):
    return [round(sum(p[i] for p in points) / len(points), 3) for i in range(3)]


def _spread(points, c):
    return sorted(round(math.dist(p, c), 3) for p in points)


def run():
    import nr4a3_warhead as wh
    import apo_pose_recovery as apr
    os.makedirs(WORK, exist_ok=True)
    edge = _pipeline_box_edge()
    doc = {
        "_module": "paralogue_site_correction",
        "_asks": ("On the AF2 receptor the pipeline ACTUALLY docks each paralogue into: how far is the box "
                  "the pipeline draws from where crystallography says ligands bind on that protein?"),
        "_why": ("`apo-pose-regime-dock.json` showed the Pocket-5 transfer docks a median +16.05 A worse "
                 "than this protocol's own ceiling, on 11 of 11 in-regime pairs, while the receptor's own "
                 "cavity sits at +0.39 A. That transfer is the step that places every ANTI-TARGET box, so "
                 "every selectivity margin in the program is a comparison whose paralogue arms it drew."),
        "_scope": ("re-scores nothing, moves no ddG, overturns no verdict. Emits a corrected site and a "
                   "measured displacement; consuming them is a separate, explicit step per artifact."),
        "_no_dock": "geometric only — no smina, no fpocket, no seed, deterministic given the deposits",
        "pipeline_box_edge_A": edge,
        "nr4a3_site_untouched": ("NR4A3's own box is built directly on the NR4A3 structure, NOT by "
                                 "`map_pocket_to_paralogue`, so it is not what this corrects and nothing "
                                 "here re-derives it."),
        "paralogues": {},
        "refusals": [],
    }

    try:
        by_acc = in_regime_holo_entries()
    except Exception as e:                                      # noqa: BLE001
        doc["refusals"].append({"stage": "read_site_panel", "evidence": "%s: %s" % (type(e).__name__, e)})
        _emit(doc)
        return doc

    # NR4A3's AF2 model is the SOURCE of the transfer, so it is what the pipeline aligns from.
    nr4a3_pdb = os.path.join(WORK, "AF-Q92570.pdb")
    if not os.path.exists(nr4a3_pdb):
        try:
            fetch_af2("Q92570", nr4a3_pdb)
        except Exception as e:                                  # noqa: BLE001
            doc["refusals"].append({"stage": "fetch_nr4a3_af2",
                                    "evidence": "%s: %s" % (type(e).__name__, e)})
            _emit(doc)
            return doc

    for acc, info in sorted(by_acc.items()):
        row = {"protein": info["protein"], "accession": acc, "entries": [], "refusals": []}
        para_pdb = os.path.join(WORK, "AF-%s.pdb" % acc)
        try:
            if not os.path.exists(para_pdb):
                fetch_af2(acc, para_pdb)
        except Exception as e:                                  # noqa: BLE001
            row["refusals"].append({"stage": "fetch_af2", "evidence": "%s: %s" % (type(e).__name__, e)})
            doc["paralogues"][acc] = row
            continue

        box, why = pipeline_transferred_box(nr4a3_pdb, para_pdb, wh.POCKET_RESIDUES)
        row["pipeline_transferred_box"] = box or {"refused": why}

        sites = []
        for ent in info["entries"]:
            e_row = dict(ent)
            try:
                holo_path = apr.fetch_pdb(ent["holo"], os.path.join(WORK, ent["holo"] + ".pdb"))
            except Exception as e:                              # noqa: BLE001
                e_row["refused"] = "fetch: %s: %s" % (type(e).__name__, e)
                row["entries"].append(e_row)
                continue
            got, why2 = crystal_site_in_af2_frame(holo_path, ent["ligand"], para_pdb)
            if got is None:
                e_row["refused"] = why2
            else:
                e_row.update(got)
                sites.append(got["ligand_centroid_af2_frame"])
            row["entries"].append(e_row)

        row["n_entries"] = len(info["entries"])
        row["n_usable"] = len(sites)
        if not sites:
            row["corrected_site"] = None
            row["_reads"] = ("REFUSED — no deposited ligand could be carried into this receptor's frame. "
                             "An absent reading is not a reading of absence: this is unmeasured, NOT "
                             "evidence that the pipeline's box is right.")
            doc["paralogues"][acc] = row
            continue

        c = _centroid(sites)
        row["corrected_site"] = {
            "center": c,
            "n_deposited_ligands": len(sites),
            "agreement_A": {"spread_from_consensus": _spread(sites, c)},
            "_reads": ("where crystallography says ligands bind on this protein, expressed in the frame of "
                       "the AF2 model the pipeline docks into. Consensus of %d deposited ligand(s)."
                       % len(sites)),
        }
        if box:
            d = round(math.dist(box["center"], c), 3)
            half = edge / 2.0
            inside = all(abs(box["center"][i] - c[i]) <= half for i in range(3))
            row["displacement"] = {
                "pipeline_box_center_to_crystallographic_site_A": d,
                "crystallographic_site_inside_the_pipeline_box": inside,
                "box_edge_A": edge,
                "_reads": ("the pipeline docks this anti-target %s A from where its ligands actually bind. "
                           "%s" % (d, "The site IS inside the box it draws." if inside else
                                   "The site is OUTSIDE the box it draws, so no amount of searching "
                                   "inside that box can find it.")),
            }
        doc["paralogues"][acc] = row

    doc["summary"] = _summary(doc)
    _emit(doc)
    return doc


def _summary(doc):
    rows = [(a, r) for a, r in doc["paralogues"].items() if r.get("displacement")]
    if not rows:
        return {"measured": False,
                "_reads": ("no paralogue could be measured. UNMEASURED, not 'the box is fine' — see each "
                           "paralogue's `refusals`.")}
    ds = [r["displacement"]["pipeline_box_center_to_crystallographic_site_A"] for _a, r in rows]
    out_of_box = [a for a, r in rows
                  if not r["displacement"]["crystallographic_site_inside_the_pipeline_box"]]
    return {
        "measured": True,
        "n_paralogues_measured": len(rows),
        "displacement_A": {"min": min(ds), "max": max(ds)},
        "n_with_the_crystallographic_site_OUTSIDE_the_pipeline_box": len(out_of_box),
        "paralogues_docked_outside_their_own_ligand_site": sorted(out_of_box),
        "corrected_sites": {a: r["corrected_site"]["center"] for a, r in rows},
        "_licenses": ("a corrected anti-target site, and a measured displacement for the one currently "
                      "used. It does NOT re-score anything, and it does not make the NR4A3 arm correct — "
                      "NR4A3's own box was never built by this step."),
        "_does_not_license": ("any statement that a selectivity margin is now valid. The margin must be "
                              "RECOMPUTED at the corrected site before it means anything, and the pose "
                              "resolution bound from `apo-pose-regime-dock.json` (protocol ceiling median "
                              "3.147 A) still sits above the differences those margins try to resolve."),
    }


def _emit(doc):
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=2)
    print(json.dumps(doc.get("summary") or {"refusals": doc.get("refusals")}, indent=2))
    print("[paralogue-site-correction] wrote %s" % OUT)


if __name__ == "__main__":
    run()
