#!/usr/bin/env python3
"""TRANSFER-ANCHOR DIAGNOSTIC — the discriminating observation RUNG 5a left unrun.

THE CONFLICT. Two *verified* VHL stagings put the OBSERVED E2~Ub transfer anchor (the catalytic cysteine of the
E2 in a solved CRL2^VHL ubiquitylation assembly, bridged into the recruiter's frame) at **30.9 A** and
**69.9 A** from the recruiter's ligand exit vector:

    registry A  receptor 5T35 (VHL-EloB-EloC + BRD4-BD2 + MZ1)   -> anchor->transfer 30.85 A
    registry B  receptor 6GMN (VHL-EloB-EloC + a 12-atom fragment) -> anchor->transfer 69.91 A

Both bridged the SAME intact assembly (8R5H) at good RMSD (0.98 A / 1.33 A). A 39 A disagreement about where
ubiquitin is delivered is decision-relevant: term (b) of the basin search is a set-membership question about a
zone hanging off that anchor, and the authoritative 12-pose run consumed registry A.

Lane 2 recorded two hypotheses and explicitly did not run the observation that discriminates them:
    H1  a different COPY was selected inside one of the source structures;
    H2  genuinely different CRL-arm CONFORMERS (the same class of effect as the measured 48.6 A composed-RING
        spread), in which case the transfer zone carries ~40 A of frame-to-frame variation and term (b) weakens.
This script adds the two hypotheses that a decomposition can actually separate them FROM:
    H3  the two EXIT VECTORS are in different places (one ligand is not in the VHL ligand site of the selected
        copy), i.e. the disagreement is about the recruiter anchor, not about the E2 at all;
    H4  the two mapped E2 positions differ (a bridge/copy problem on the 8R5H side).

THE DISCRIMINATING OBSERVATIONS, in order of decisiveness.

  (1) ZERO-COMPOSITION GROUND TRUTH. 8R5H is a solved, intact CRL2^VHL ubiquitylation assembly that contains,
      in ONE frame and with no superposition of any kind: VHL + EloB + EloC, the MZ1 degrader bound in the VHL
      site, and a trapped UBE2R2~ubiquitin. So the quantity in dispute -- "how far is the observed E2 catalytic
      cysteine from the VHL ligand exit vector?" -- can be MEASURED DIRECTLY inside that one structure. No
      bridge, no composition, no model. Whichever staging matches that number is the correct one. The same
      applies to CRBN in 9UUM (mezigdomide + UbcH5a~Ub), where the two registries disagree 12.87 vs 21.50 A.

  (2) COMMON-FRAME DECOMPOSITION. Superpose the two receptor copies onto each other and measure separately how
      far apart the two EXIT VECTORS are and how far apart the two MAPPED E2 CYSTEINES are. The 39 A has to
      live in one of them, and that is the difference between H3/H4 and H2.

  (3) PER-COPY LIGAND AUDIT. For a receptor entry deposited with several copies of the complex, compute the
      exit vector every candidate ligand would give and how far each sits from the ligand site that 8R5H
      OBSERVES, so "the ligand belongs to another copy" is measured rather than argued.

Pure stdlib; RCSB is 403'd at CONNECT by the dev sandbox's egress proxy, so this runs on a GitHub Actions
runner (CLAUDE.md section 6).

Usage
    python transfer_anchor_diag.py                      # full diagnostic, writes the JSON below
    python transfer_anchor_diag.py --out /tmp/x.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G            # noqa: E402
import nr4a3_e3_stage as S        # noqa: E402

OUT = os.path.join(HERE, "transfer-anchor-diagnostic.json")

# The two competing VHL stagings, named by the receptor entry each used. The intact assembly is DISCOVERED the
# same way the staging discovers it (accession set), never hard-coded -- but the two receptor entries are the
# subject of the diagnostic, so they are inputs by construction.
CASES = {
    "vhl": {
        "recruiter": "VHL",
        "receptor_needs": ["VHL", "ELOB", "ELOC"],
        "bridge": ["VHL", "ELOB", "ELOC"],
        "receptor_entries": {
            "registryA_5T35": "5T35",     # research/modalities/nr4a3-e3-arm-registry.json   -> 30.85 A
            "registryB_6GMN": "6GMN",     # research/modalities/nr4a3-e3-arm-registry-lane1.json -> 69.91 A
        },
        "e2_candidates": ["UBE2R2", "UBE2R1", "UBE2D1", "UBE2D2", "UBE2D3"],
    },
    "crbn": {
        "recruiter": "CRBN",
        "receptor_needs": ["CRBN", "DDB1"],
        "bridge": ["CRBN", "DDB1"],
        "receptor_entries": {
            "registryA_6BOY": "6BOY",     # -> 12.87 A
            "registryB_9FJX": "9FJX",     # -> 21.50 A
        },
        "e2_candidates": ["UBE2D1", "UBE2D2", "UBE2D3"],
    },
}


# ---------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------


def fetch(pdb):
    """(composition, protein atoms, het atoms) for one entry, from the legacy PDB file the staging uses."""
    comp = S.entry_composition(pdb)
    text = S._get(S.FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
    prot, het = S.parse_pdb_text(text)
    return comp, prot, het


def chains_of(comp, name):
    return set(comp["chains_by_accession"].get(S.ACC[name], []))


def copy_chains(prot, comp, names, log):
    """Reproduce the staging's own copy selection, so the diagnostic compares like with like."""
    by = {n: chains_of(comp, n) for n in names}
    by = {k: sorted(v) for k, v in by.items() if v}
    sel, info = S.select_assembly_copy(prot, by, log=None)
    return (sel or {n: sorted(v)[0] for n, v in by.items()}), info, by


def catalytic_cys(prot, comp, e2_name):
    """The E2 catalytic cysteine, identified the way the staging identifies it: the SG bearing ubiquitin's
    C-terminal glycine as a thioester, i.e. the one nearest ubiquitin's C-terminus. Unique answer, no heuristic."""
    e2c = chains_of(comp, e2_name)
    ubc = set()
    for a in S.UBIQUITIN_ACC:
        ubc.update(comp["chains_by_accession"].get(a, []))
    if not e2c or not ubc:
        return None
    sgs = [a for a in prot if a["chain"] in e2c and a["resname"] == "CYS" and a["name"] == "SG"]
    ub_res = sorted({a["resid"] for a in prot if a["chain"] in ubc})
    if not sgs or not ub_res:
        return None
    ub_ct = [a["xyz"] for a in prot
             if a["chain"] in ubc and a["resid"] == ub_res[-1] and a["name"] in ("C", "CA")]
    if not ub_ct:
        return None
    ranked = sorted(((min(G.dist(a["xyz"], u) for u in ub_ct), a) for a in sgs), key=lambda t: t[0])
    d, cat = ranked[0]
    return {"resid": cat["resid"], "chain": cat["chain"], "xyz": list(cat["xyz"]),
            "to_ubiquitin_cterm_A": round(d, 2),
            "runner_up_A": [round(x[0], 2) for x in ranked[1:4]]}


def find_intact_assembly(spec, log):
    """Discover the intact ubiquitylation assembly by ACCESSION SET, exactly as the staging does."""
    for e2 in spec["e2_candidates"]:
        try:
            hits = S.search_entries([S.ACC[spec["recruiter"]], S.ACC[e2]], rows=10)
        except Exception as exc:                                          # noqa: BLE001
            log(f"[diag] search failed for {e2}: {exc}")
            continue
        for pdb in hits:
            try:
                comp = S.entry_composition(pdb)
            except Exception:                                             # noqa: BLE001
                continue
            if not all(chains_of(comp, n) for n in spec["receptor_needs"]):
                continue
            if not any(a in comp["chains_by_accession"] for a in S.UBIQUITIN_ACC):
                continue
            try:
                text = S._get(S.FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
            except S.NotAvailable:
                log(f"[diag] {pdb}: no legacy PDB file (404) — skipped, as the staging skips it")
                continue
            prot, het = S.parse_pdb_text(text)
            cat = catalytic_cys(prot, comp, e2)
            if cat is None:
                continue
            log(f"[diag] intact assembly for {spec['recruiter']}: {pdb} with E2 {e2}")
            return {"pdb_id": pdb, "e2": e2, "comp": comp, "prot": prot, "het": het, "cat": cat}
    return None


def ligand_report(prot, het, body_chains, comp, tag):
    """pick_ligand's answer PLUS the per-chain breakdown it does not report: which subunit the exit atom is
    actually next to. An exit vector 4 A from *some* body atom can still be nowhere near the recruiter."""
    lig = S.pick_ligand(prot, het, body_chains)
    if lig is None:
        return None
    exit_xyz = tuple(lig["exit_atom_xyz"])
    per_chain = {}
    for ch in sorted({a["chain"] for a in prot}):
        pts = [a["xyz"] for a in prot if a["chain"] == ch]
        if pts:
            per_chain[ch] = round(min(G.dist(exit_xyz, p) for p in pts), 2)
    acc_of = {}
    for acc, chs in comp["chains_by_accession"].items():
        for c in chs:
            acc_of[c] = acc
    named = {}
    for name, acc in S.ACC.items():
        for c in comp["chains_by_accession"].get(acc, []):
            named.setdefault(c, name)
    return {
        "tag": tag,
        "het_code": lig["het_code"], "ligand_chain": lig["chain"], "ligand_resid": lig["resid"],
        "n_heavy": lig["n_heavy"], "n_heavy_on_e3_side": lig["n_heavy_on_e3_side"],
        "is_protac_ternary": lig["is_protac_ternary"],
        "exit_atom_name": lig["exit_atom_name"], "exit_atom_xyz": list(exit_xyz),
        "exit_dist_to_body_A": lig["exit_atom_dist_to_receptor_A"],
        "nearest_atom_per_chain_A": per_chain,
        "chain_identity": {c: named.get(c, acc_of.get(c, "?")) for c in per_chain},
        "nearest_chain": min(per_chain, key=per_chain.get) if per_chain else None,
        "_ligand": lig,
    }


def all_candidate_ligands(prot, het, body_chains):
    """Every HET group this entry offers that could have been chosen, with the exit vector each would give.
    pick_ligand takes the LARGEST group with >=4 atoms within 4.5 A of the body, and ties break on file order —
    so on a multi-copy entry the audit has to show what the alternatives were."""
    body = [a["xyz"] for a in prot if a["chain"] in body_chains]
    field = G.SquaredDistanceField(body, cell=1.0, clamp=8.0)
    groups = {}
    for a in het:
        if a["resname"] in S.EXCLUDE_HET:
            continue
        groups.setdefault((a["resname"], a["chain"], a["resid"], a["icode"]), []).append(a)
    rows = []
    for key, atoms in groups.items():
        if len(atoms) < S.MIN_LIGAND_HEAVY:
            continue
        near = sum(1 for a in atoms if field.min_dist(a["xyz"]) <= 4.5)
        cen = G.centroid([a["xyz"] for a in atoms])
        rows.append({"het": key[0], "chain": key[1], "resid": key[2], "n_heavy": len(atoms),
                     "n_atoms_within_4.5A_of_selected_body": near,
                     "eligible": near >= 4, "centroid": [round(c, 2) for c in cen]})
    rows.sort(key=lambda r: (-r["n_heavy"], r["chain"], r["resid"]))
    return rows


def superpose_map(src_prot, src_chain_map, dst_prot, dst_chain_map):
    return S.bridge_into_frame(src_prot, src_chain_map, dst_prot, dst_chain_map)


def run_case(case_id, spec, log):
    out = {"case": case_id, "recruiter": spec["recruiter"]}

    # ---- (1) ZERO-COMPOSITION GROUND TRUTH -----------------------------------------------------------
    intact = find_intact_assembly(spec, log)
    if intact is None:
        out["error"] = "no intact ubiquitylation assembly with a legacy PDB file was found"
        return out
    icomp, iprot, ihet = intact["comp"], intact["prot"], intact["het"]
    isel, iinfo, iby = copy_chains(iprot, icomp, spec["receptor_needs"], log)
    ibody = set(isel.values())
    ilig = ligand_report(iprot, ihet, ibody, icomp, f"{intact['pdb_id']} (intact assembly)")
    cat = intact["cat"]
    gt = {
        "pdb_id": intact["pdb_id"], "title": icomp.get("title"), "method": icomp.get("method"),
        "resolution_A": icomp.get("resolution_A"), "e2": intact["e2"],
        "receptor_copy": isel, "copy_selection": iinfo,
        "catalytic_cys": cat,
        "ligand": ilig,
    }
    if ilig is not None:
        gt["OBSERVED_exit_to_catalytic_cys_A"] = round(G.dist(tuple(ilig["exit_atom_xyz"]), tuple(cat["xyz"])), 2)
        gt["OBSERVED_ligand_centroid_to_catalytic_cys_A"] = round(
            G.dist(tuple(ilig["_ligand"]["ligand_centroid"]), tuple(cat["xyz"])), 2)
        gt["OBSERVED_e3_moiety_centroid_to_catalytic_cys_A"] = round(
            G.dist(tuple(ilig["_ligand"]["e3_moiety_centroid"]), tuple(cat["xyz"])), 2)
        rbx = chains_of(icomp, "RBX1")
        if rbx:
            cen, rng = S.ring_domain_centroid(iprot, rbx)
            if cen:
                gt["OBSERVED_exit_to_RING_A"] = round(G.dist(tuple(ilig["exit_atom_xyz"]), cen), 2)
                gt["OBSERVED_RING_to_catalytic_cys_A"] = round(G.dist(cen, tuple(cat["xyz"])), 2)
                gt["ring_residue_range"] = list(rng)
        log(f"[diag] *** GROUND TRUTH ({intact['pdb_id']}, no composition): ligand exit atom "
            f"{ilig['het_code']}.{ilig['exit_atom_name']} -> {intact['e2']} catalytic Cys{cat['resid']} = "
            f"{gt['OBSERVED_exit_to_catalytic_cys_A']} A")
    out["ground_truth"] = gt

    # ---- (2) reproduce each staging, then decompose in a common frame ---------------------------------
    frames = {}
    for label, pdb in spec["receptor_entries"].items():
        try:
            comp, prot, het = fetch(pdb)
        except Exception as exc:                                          # noqa: BLE001
            frames[label] = {"error": f"{type(exc).__name__}: {exc}"}
            log(f"[diag] {label}: {exc}")
            continue
        sel, info, by = copy_chains(prot, comp, spec["receptor_needs"], log)
        body = set(sel.values())
        lig = ligand_report(prot, het, body, comp, f"{pdb} ({label})")
        rec = {"pdb_id": pdb, "title": comp.get("title"), "resolution_A": comp.get("resolution_A"),
               "chains_by_accession": comp["chains_by_accession"],
               "receptor_copy": sel, "copy_selection": info,
               "candidate_ligands": all_candidate_ligands(prot, het, body),
               "ligand": lig}
        # bridge the intact assembly into this receptor's frame, exactly as stage_intact_assembly does
        src_map = {n: {isel[n]} for n in spec["receptor_needs"] if n in isel}
        dst_map = {n: {sel[n]} for n in spec["receptor_needs"] if n in sel}
        tr, binfo = superpose_map(iprot, src_map, prot, dst_map)
        if tr is None:
            rec["bridge"] = binfo
        else:
            R, t = tr
            cys_f = G.apply_superpose([tuple(cat["xyz"])], R, t)[0]
            rec["bridge"] = binfo
            rec["mapped_catalytic_cys_xyz"] = [round(c, 3) for c in cys_f]
            if ilig is not None:
                obs_exit_f = G.apply_superpose([tuple(ilig["exit_atom_xyz"])], R, t)[0]
                obs_cen_f = G.apply_superpose([tuple(ilig["_ligand"]["e3_moiety_centroid"])], R, t)[0]
                rec["mapped_observed_exit_xyz"] = [round(c, 3) for c in obs_exit_f]
                rec["mapped_observed_e3_moiety_centroid_xyz"] = [round(c, 3) for c in obs_cen_f]
                if lig is not None:
                    rec["THIS_STAGING_exit_vs_OBSERVED_exit_A"] = round(
                        G.dist(tuple(lig["exit_atom_xyz"]), obs_exit_f), 2)
                    rec["THIS_STAGING_exit_vs_OBSERVED_e3_moiety_centroid_A"] = round(
                        G.dist(tuple(lig["exit_atom_xyz"]), obs_cen_f), 2)
            if lig is not None:
                rec["REPRODUCED_anchor_to_transfer_A"] = round(
                    G.dist(tuple(lig["exit_atom_xyz"]), cys_f), 2)
                log(f"[diag] {label}: reproduced anchor->transfer = "
                    f"{rec['REPRODUCED_anchor_to_transfer_A']} A "
                    f"(bridge {binfo['n_bridge_ca']} CA @ {binfo['bridge_rmsd_A']} A); this staging's exit atom "
                    f"is {rec.get('THIS_STAGING_exit_vs_OBSERVED_exit_A')} A from the exit atom OBSERVED in "
                    f"{intact['pdb_id']}")
        rec["_prot"] = prot
        rec["_comp"] = comp
        rec["_sel"] = sel
        frames[label] = rec

    labels = [l for l in spec["receptor_entries"] if l in frames and "_prot" in frames[l]]
    if len(labels) == 2:
        a, b = labels
        fa, fb = frames[a], frames[b]
        src_map = {n: {fb["_sel"][n]} for n in spec["receptor_needs"] if n in fb["_sel"]}
        dst_map = {n: {fa["_sel"][n]} for n in spec["receptor_needs"] if n in fa["_sel"]}
        tr, binfo = superpose_map(fb["_prot"], src_map, fa["_prot"], dst_map)
        dec = {"common_frame": a, "moved": b, "receptor_superposition": binfo}
        if tr is not None:
            R, t = tr
            if fb.get("ligand") and fa.get("ligand"):
                eb = G.apply_superpose([tuple(fb["ligand"]["exit_atom_xyz"])], R, t)[0]
                dec["delta_exit_vector_A"] = round(G.dist(tuple(fa["ligand"]["exit_atom_xyz"]), eb), 2)
            if fb.get("mapped_catalytic_cys_xyz") and fa.get("mapped_catalytic_cys_xyz"):
                cb = G.apply_superpose([tuple(fb["mapped_catalytic_cys_xyz"])], R, t)[0]
                dec["delta_mapped_E2_catalytic_cys_A"] = round(
                    G.dist(tuple(fa["mapped_catalytic_cys_xyz"]), cb), 2)
            dec["_reading"] = (
                "The two stagings disagree by |d_A - d_B| angstroms about the anchor-to-transfer distance. "
                "Placed in one frame, this says how much of that lives in the EXIT VECTOR and how much in the "
                "mapped E2 position. A small E2 delta with a large exit delta means the disagreement is about "
                "the recruiter anchor (H3), not about CRL conformation (H2).")
        out["common_frame_decomposition"] = dec

    for lab in list(frames):
        for k in ("_prot", "_comp", "_sel"):
            frames[lab].pop(k, None)
        if frames[lab].get("ligand"):
            frames[lab]["ligand"].pop("_ligand", None)
    if out.get("ground_truth", {}).get("ligand"):
        out["ground_truth"]["ligand"].pop("_ligand", None)
    out["stagings"] = frames

    # ---- verdict ---------------------------------------------------------------------------------------
    gtd = out.get("ground_truth", {}).get("OBSERVED_exit_to_catalytic_cys_A")
    if gtd is not None:
        scored = []
        for lab, rec in frames.items():
            d = rec.get("REPRODUCED_anchor_to_transfer_A")
            if d is not None:
                scored.append((abs(d - gtd), lab, d))
        scored.sort()
        if scored:
            out["verdict"] = {
                "observed_no_composition_A": gtd,
                "per_staging_A": {lab: d for _, lab, d in scored},
                "closest_to_observed": scored[0][1],
                "miss_A": {lab: round(m, 2) for m, lab, _ in scored},
            }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--cases", default="vhl,crbn")
    args = ap.parse_args(argv)
    lines = []

    def log(m):
        print(m, flush=True)
        lines.append(m)

    res = {"_title": "Transfer-anchor diagnostic — which VHL staging places the observed E2~Ub transfer "
                     "anchor correctly?",
           "_method": "Direct, composition-free measurement inside a solved intact ubiquitylation assembly, "
                      "plus a common-frame decomposition of the two stagings' disagreement into an "
                      "exit-vector component and a mapped-E2 component, plus a per-copy ligand audit.",
           "cases": {}}
    for cid in [c.strip() for c in args.cases.split(",") if c.strip()]:
        spec = CASES.get(cid)
        if not spec:
            continue
        log(f"[diag] ===== case {cid} =====")
        res["cases"][cid] = run_case(cid, spec, log)
    res["log"] = lines
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=False)
    print(f"[diag] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
