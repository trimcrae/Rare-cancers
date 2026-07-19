#!/usr/bin/env python3
"""Free, CPU-only, per-edge TIMESTEP-CEILING scan for the congeneric warhead RBFE matrix (+ two anchors).

WHY: "does our designed warhead need 2 fs, or can the whole program run at OpenFE's 4 fs default?" is a per-EDGE
topology question, not a per-compound or per-project one. The stable timestep is capped at ~2 fs ONLY when the
hybrid system contains an UNCONSTRAINED alchemical X-H bond — and (in a constraints=HBonds system) the ONLY way to
get one is a morph that changes the hydrogen count on a MAPPED (core) atom: an element change (ring N -> CH) or a
hybridisation change (sp2 C=O -> sp3 CH2) AT a mapped position. A terminal-group swap or a chain
insertion/deletion, where the whole changed group and its H's are a unique/dummy block, leaves EVERY X-H
constrained -> the 4 fs default is stable. cf. research/modalities/ternary-rbfe-runbook.md section 1/1b.

WHAT: for each edge this builds the REAL OpenFE solvent-leg hybrid system via the production code path
(nr4a3_rbfe._mapping / _protocol / _chemical_systems -> proto.create -> HybridTopologySetupUnit) and reports the
count of unconstrained alchemical X-H bonds (nr4a3_rbfe.count_unconstrained_alchemical_xh). NO MD, NO GPU: it sets
RBFE_HMRDIAG_ONLY=1 so execute_hybrid_dag_spot_safe exits right after the constraint verdict. The verdict is
pose/environment-independent (the alchemical bonds are intramolecular to the ligand), so the binary solvent-leg
build gives the SAME answer the binary-complex OR ternary build would -- i.e. it also tells us the ceiling for the
ternary cooperativity edge that reuses the same warhead morph.

Charges: am1bcc (the env's guaranteed method; env tarball is named ...am1bcc...). The constraint/HMR assignment
does NOT depend on partial-charge VALUES, only on topology, so the charge method is irrelevant to the verdict --
am1bcc is chosen only because it is definitely present. NB: the runner must put the conda env's bin on PATH so the
OpenFF AmberTools wrapper finds sqm/antechamber (the workflow exports PATH); running the env python directly
without activation is what triggered ToolkitUnavailableException: AmberTools is not available.

ANCHORS (validate the check against known ground truth):
  * pilot  5-Br -> 5-NH2  (e_zaienne_cmpd19__cw_ev_5nh2): step1 RAN CLEAN at 4 fs  -> MUST report 0 unconstrained.
  * calib  Wurz cmpd1 -> cmpd4 (ring N -> CH):            NaN'd at 4 fs             -> MUST report >=1 unconstrained.
If both anchors come out as expected, the per-edge verdicts on the rest of the matrix are trustworthy.

Runs free on a CPU runner (openfe env). Writes congeneric-edge-timestep-table.json next to this file.
"""
import json
import os
import sys
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))

# Charges do not affect the constraint verdict (it depends only on topology/HMR/constraints), so use the env's
# guaranteed am1bcc. Requires the env's bin on PATH so the OpenFF AmberTools wrapper finds sqm (workflow exports it).
os.environ.setdefault("CHARGE_METHOD", "am1bcc")
# The verdict ASSUMES constraints=HBonds (so only the ALCHEMICAL X-H is unconstrained). The openfe build here did
# NOT constrain ligand X-H by default (run-1 diag: xh_total==xh_unconstrained for every edge, incl. the pilot that
# ran clean at 4 fs), which voided the premise. Force HBonds so the system matches the production system step1 ran
# stably at 4 fs. _protocol honors this and prints the effective setting.
os.environ.setdefault("RBFE_FORCE_CONSTRAINTS", "hbonds")

import openfe  # noqa: E402
from rdkit import Chem  # noqa: E402
from rdkit.Chem import AllChem  # noqa: E402

import nr4a3_rbfe as R  # noqa: E402  (reuse the REAL mapping/protocol/chemical-systems/verdict path)


def _embed(smiles):
    """SMILES -> a with-H, 3D RDKit mol. Coordinates are irrelevant to the constraint verdict (that depends only on
    topology/HMR/constraints), but a valid conformer is needed so openfe can parameterise + _align_pose can run."""
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError("unparseable SMILES: %s" % smiles)
    m = Chem.AddHs(m)
    params = AllChem.ETKDGv3()
    params.randomSeed = 0xC0FFEE
    if AllChem.EmbedMolecule(m, params) != 0:
        # fallback for the odd macrocyclic PROTAC that ETKDGv3 can't seed
        if AllChem.EmbedMolecule(m, AllChem.ETKDGv2()) != 0:
            AllChem.EmbedMolecule(m, useRandomCoords=True)
    try:
        AllChem.MMFFOptimizeMolecule(m, maxIters=400)
    except Exception:  # noqa: BLE001
        pass
    return m


def scan_edge(smi_a, smi_b, name_a, name_b, prefer_ec=False):
    """Build the real solvent-leg hybrid for A->B and return the constraint verdict dict (+ n_mapped)."""
    R.LEG = "solvent"
    R.LIGAND_A, R.LIGAND_B = name_a, name_b
    molA = _embed(smi_a)
    molB = _embed(smi_b)
    molB = R._align_pose(molB, molA, Chem)
    ligA = openfe.SmallMoleculeComponent.from_rdkit(molA, name=name_a)
    ligB = openfe.SmallMoleculeComponent.from_rdkit(molB, name=name_b)
    mapping = R._mapping(openfe, ligA, ligB, prefer_element_change=prefer_ec)
    A, B = R._chemical_systems(openfe, ligA, ligB, None)
    proto = R._protocol(openfe)
    dag = proto.create(stateA=A, stateB=B, mapping=mapping)
    ckpt = tempfile.mkdtemp(prefix="hmrscan_")
    os.environ["RBFE_HMRDIAG_ONLY"] = "1"
    # unset any inherited cache/commit envs so the scan never touches GCS/S3
    for k in ("RBFE_SETUP_CACHE_GCS", "RBFE_SPOT_COMMIT_GCS", "RBFE_SPOT_COMMIT_S3"):
        os.environ.pop(k, None)
    _, _, info = R.execute_hybrid_dag_spot_safe(proto, dag, ckpt, tag="scan_%s__%s" % (name_a, name_b))
    info = dict(info or {})
    info["n_mapped_atoms"] = len(mapping.componentA_to_componentB)
    return info


def _verdict(info):
    if info.get("error"):
        return "ERROR", None
    nu = info.get("xh_unconstrained")
    if nu is None:
        return "ERROR", None
    return ("2fs" if nu >= 1 else "4fs"), int(nu)


def main():
    mp = json.load(open(os.path.join(HERE, "congeneric-rbfe-map.json")))
    smiles = {n["id"]: n["smiles"] for n in mp["nodes"]}
    edges = mp["edges"]

    # anchors from repo ground truth
    wurz = json.load(open(os.path.join(HERE, "wurz-calib-frozen.json")))
    anchors = [
        {"edge_id": "ANCHOR_pilot_5Br_to_5NH2", "kind": "anchor",
         "perturbation": "5-Br -> 5-NH2 (== step1 pilot; RAN CLEAN at 4 fs -> expect 0 unconstrained)",
         "smi_a": smiles["zaienne_cmpd19"], "smi_b": smiles["cw_ev_5nh2"],
         "name_a": "zaienne_cmpd19", "name_b": "cw_ev_5nh2", "prefer_ec": False, "expect": "4fs"},
        {"edge_id": "ANCHOR_calib_wurz_N_to_CH", "kind": "anchor",
         "perturbation": wurz["morph"] + " (NaN'd at 4 fs -> expect >=1 unconstrained)",
         "smi_a": wurz["calib_hi"]["smiles"], "smi_b": wurz["calib_lo"]["smiles"],
         "name_a": "Wurz_cmpd1", "name_b": "Wurz_cmpd4", "prefer_ec": True, "expect": "2fs"},
    ]

    designed_rows = [{
        "edge_id": e["edge_id"], "kind": e["class"], "perturbation": e["perturbation"],
        "smi_a": smiles[e["node_a"]], "smi_b": smiles[e["node_b"]],
        "name_a": e["node_a"], "name_b": e["node_b"],
        # a ring/element change wants prefer_element_change; harmless elsewhere. Trigger on the known
        # element-change-ish classes so a degenerate strict map doesn't hide an edge's true topology.
        "prefer_ec": e["class"] in ("bioisostere", "microstate_variant"), "expect": None} for e in edges]

    results = []

    def _run(s, src):
        print("\n" + "=" * 100, flush=True)
        print("[scan] %-32s %s" % (s["edge_id"], s["perturbation"]), flush=True)
        try:
            info = scan_edge(s["smi_a"], s["smi_b"], s["name_a"], s["name_b"], s.get("prefer_ec", False))
        except Exception as ex:  # noqa: BLE001
            print("[scan] FAILED: %s" % ex, flush=True)
            traceback.print_exc()
            info = {"error": "%s: %s" % (type(ex).__name__, ex)}
        v, nu = _verdict(info)
        results.append({
            "edge_id": s["edge_id"], "src": src, "kind": s["kind"], "perturbation": s["perturbation"],
            "node_a": s["name_a"], "node_b": s["name_b"],
            "xh_total": info.get("xh_total"), "xh_unconstrained": info.get("xh_unconstrained"),
            "total_constraints": info.get("total_constraints"),
            "constraints_setting": info.get("constraints_setting"),
            "hydrogen_mass_setting": info.get("hydrogen_mass_setting"),
            "constrain_diag": info.get("constrain_diag"),
            "unconstrained_atoms": info.get("unconstrained"), "n_mapped_atoms": info.get("n_mapped_atoms"),
            "max_stable_timestep_fs": {"4fs": 4.0, "2fs": 2.0, "ERROR": None}[v],
            "verdict": v, "expect": s.get("expect"), "error": info.get("error"),
        })
        print("[scan] -> verdict %s (unconstrained X-H = %s)" % (v, nu), flush=True)

    # ANCHORS FIRST as a GATE: the two known-answer edges validate the whole method. Only spend on the 19 designed
    # edges if the anchors come out as expected (pilot->4fs, calib->2fs); otherwise the harness is still wrong and
    # running 19 more would just produce 19 more meaningless rows.
    # SCAN_ANCHORS=pilot runs ONLY the small fast pilot (fast constraint diagnostic; calib am1bcc is ~14 min).
    _which = os.environ.get("SCAN_ANCHORS", "both").lower()
    run_anchors = [a for a in anchors if _which == "both"
                   or (_which == "pilot" and "pilot" in a["edge_id"].lower())
                   or (_which == "calib" and "calib" in a["edge_id"].lower())]
    for a in run_anchors:
        _run(a, "anchor")
    anchors_ok = all(r["verdict"] == r["expect"] for r in results if r["src"] == "anchor")
    for r in results:
        if r["src"] == "anchor":
            print("[scan] anchor %s: total_constraints=%s constraints_setting=%s hmass=%s xh_total=%s xh_unc=%s"
                  % (r["edge_id"], r.get("total_constraints"), r.get("constraints_setting"),
                     r.get("hydrogen_mass_setting"), r.get("xh_total"), r.get("xh_unconstrained")), flush=True)
    proceed = anchors_ok and _which == "both"
    print("\n[scan] ANCHOR GATE: %s" % (
        "PASS — proceeding to the 19 designed edges" if proceed else
        ("PASS (diagnostic %s-only run — not running designed edges)" % _which if anchors_ok else
         "FAIL — NOT running the designed edges (harness still wrong; fix before trusting any verdict)")), flush=True)
    if proceed:
        for s in designed_rows:
            _run(s, "designed")

    out = {
        "_schema": "congeneric_edge_timestep_ceiling_scan",
        "_method": ("real OpenFE solvent-leg hybrid build (constraints=HBonds, HMR default) per edge; count of "
                    "unconstrained alchemical X-H bonds = timestep ceiling (>=1 -> ~2 fs, 0 -> 4 fs). No MD/GPU."),
        "charge_method": os.environ.get("CHARGE_METHOD"),
        "results": results,
    }
    # anchor self-check
    checks = {}
    for row in results:
        if row["src"] == "anchor":
            checks[row["edge_id"]] = {"expect": row["expect"], "got": row["verdict"],
                                      "ok": row["expect"] == row["verdict"]}
    out["anchor_check"] = checks
    out["anchor_check_passed"] = all(c["ok"] for c in checks.values()) if checks else False

    designed = [r for r in results if r["src"] == "designed"]
    out["summary"] = {
        "n_designed_edges": len(designed),
        "n_designed_4fs": sum(1 for r in designed if r["verdict"] == "4fs"),
        "n_designed_2fs": sum(1 for r in designed if r["verdict"] == "2fs"),
        "n_designed_error": sum(1 for r in designed if r["verdict"] == "ERROR"),
        "designed_2fs_edges": [r["edge_id"] for r in designed if r["verdict"] == "2fs"],
    }

    path = os.path.join(HERE, "congeneric-edge-timestep-table.json")
    json.dump(out, open(path, "w"), indent=2)
    print("\n" + "#" * 100, flush=True)
    print("[scan] anchor_check_passed = %s : %s" % (out["anchor_check_passed"], out["anchor_check"]), flush=True)
    print("[scan] DESIGNED edges: %d total | %d run at 4 fs | %d need 2 fs | %d error"
          % (out["summary"]["n_designed_edges"], out["summary"]["n_designed_4fs"],
             out["summary"]["n_designed_2fs"], out["summary"]["n_designed_error"]), flush=True)
    print("[scan] designed edges needing 2 fs: %s" % out["summary"]["designed_2fs_edges"], flush=True)
    print("[scan] wrote %s" % path, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
