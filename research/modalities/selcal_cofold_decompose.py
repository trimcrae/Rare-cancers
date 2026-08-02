#!/usr/bin/env python3
"""WHICH PART of the co-folds is wrong? Per-protein pocket placement vs assembly. ($0 CPU)

★★ WHY THIS IS ON THE CRITICAL PATH TO ANY NR4A3 SELECTIVITY CLAIM, and not a curiosity.
The co-folds score **DockQ 0.023-0.046** against the deposited ternaries — the ~32 A rung of the decoy
ladder. The NR4A3 ternaries this program reasons about came from the SAME co-folding route, so a validated
readout applied to them would still be reading suspect structures. The question that decides what to do next
is therefore not "how bad" but **WHERE**:

  · **Assembly-only failure** — each protein's own ligand pocket is correctly occupied, and only the two
    halves are misplaced relative to each other. Then the missing information is the ASSEMBLY, which is
    exactly what a ternary generator supplies when it is given each end's pocket (measured today: DockQ
    0.839 on 9DTY). A route to credible NR4A3 ternaries exists, and its precondition is nameable.
  · **Pocket failure** — the warhead is not even in the right site on the target. Then supplying an assembly
    would not help, because the thing to assemble is wrong, and no NR4A3 ternary from this route can be
    trusted regardless of what the readout does.

⚠ ⛔ THE ANSWER IS PUBLISHED WHICHEVER WAY IT LANDS, and the second branch is the one that costs this
program more. A measurement that can only support the plan is not a measurement.

★ HOW IT SEPARATES THEM, using only native-derived selections so nothing is chosen to flatter the model.
For one (co-fold, native copy) pair, twice — once per protein:
  1. superpose the co-fold's chain for that protein onto the native's, by sequence-matched Ca Kabsch;
  2. apply that transform to the co-fold's DEGRADER;
  3. select the native degrader atoms **within 5 A of that protein in the NATIVE** — its warhead-contacting
     set on the target, its anchor-contacting set on VHL — and report the deviation of the corresponding
     co-fold atoms.
A small deviation in BOTH frames with a near-zero whole-interface DockQ is the assembly-only signature; a
large deviation in the target frame is the pocket signature.

⛔ CORRESPONDENCE IS CHEMICAL, NEVER BY PROXIMITY — and the first attempt got the chemistry wrong.
Matching by CCD atom NAME failed on every one of the 12 co-folds ("no atom NAME is shared", run 30757725008):
the crystal carries the CCD's names, while the co-fold was folded from a SMILES and names its ligand atoms in
its own scheme, under its own residue name. So the correspondence now goes through the TEMPLATE MOLECULE that
both sides are copies of: each side's heavy atoms are posed onto the reference SMILES by
`nrv04_covalent_assemble.ligand_mol_from_coords`, whose skeleton substructure match returns atoms in TEMPLATE
order, so index i means the same chemical atom on both sides. That is a graph match, not a distance one — a
molecule that is flipped, threaded backwards, or in the wrong pocket still maps correctly and therefore still
reports a large deviation, which is precisely the class of error being tested for.

⛔ This re-scores no leg, moves no verdict and amends no preregistration.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: Native contact window used to select each protein's ligand-contacting atom set. The lane's own contact
#: distance, imported so "contacting" means here what it means in every other measurement.
def contact_a():
    import selcal_cofold_validate as V
    return V.FNAT_CONTACT_A


#: Deviation, in A, at or below which a pocket is called "occupied as in the crystal". DERIVED rather than
#: chosen: it is the CAPRI "High" interface-RMSD boundary (1.0 A) doubled, so it is looser than the criterion
#: the field applies to a whole interface and cannot be accused of being tuned to pass. A value between this
#: and the ladder's own scale is reported as-is, without a label.
POCKET_OK_A = 2.0


def template_ordered_coords(heavy_atoms, template_smiles):
    """(N,3) coordinates in TEMPLATE atom order, or (None, why).

    The posing kernel is `nrv04_covalent_assemble.ligand_mol_from_coords` — the same one that writes every
    staged ligand.sdf in this lane — so the ordering here is the ordering the rest of the program uses."""
    from nrv04_covalent_assemble import ligand_mol_from_coords
    from rdkit import Chem
    if not heavy_atoms:
        return None, "no heavy atoms selected"
    els = [(a.element or a.name[:1]).upper().capitalize() for a in heavy_atoms]
    xyz = [(a.x, a.y, a.z) for a in heavy_atoms]
    try:
        mol = ligand_mol_from_coords(els, xyz, template_smiles)
    except Exception as e:                                   # noqa: BLE001
        return None, "template match failed (%d heavy atoms): %s" % (len(heavy_atoms), e)
    mol = Chem.RemoveHs(mol)
    conf = mol.GetConformer()
    return [tuple(conf.GetAtomPosition(i)) for i in range(mol.GetNumAtoms())], None


def model_ligand_atoms(atoms):
    """The co-fold's degrader heavy atoms — selected by SIZE, not by residue name.

    A co-fold folded from SMILES does not have to reuse the CCD's residue name, and requiring it is what made
    the first decomposition read zero atoms on the model side."""
    import selcal_cofold_validate as V
    return V.ligand_atoms(atoms)


def native_ligand_atoms(native_atoms, native_lig_key, comp):
    """The native degrader's heavy atoms for ONE copy, in file order."""
    return [a for a in native_atoms
            if a.resname.upper() == comp.upper() and a.is_heavy and
            (native_lig_key is None or a.key == native_lig_key)]


def contacting_indices(native_coords, native_atoms, protein_chains, cutoff=None):
    """Indices (in TEMPLATE order) of the native degrader atoms within `cutoff` of the given chains."""
    import numpy as np
    cutoff = contact_a() if cutoff is None else cutoff
    prot = [a for a in native_atoms if a.chain in protein_chains and not a.hetatm and a.is_heavy]
    if not native_coords or not prot:
        return []
    L = np.array(native_coords, dtype=float)
    P = np.array([[a.x, a.y, a.z] for a in prot], dtype=float)
    d = np.sqrt(((L[:, None, :] - P[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return [i for i, dist in enumerate(d) if dist <= cutoff]


def superpose_chain(model_atoms, native_atoms, model_chain, native_chain):
    """(R, t, detail, error) aligning ONE model chain onto ONE native chain by sequence-matched Ca."""
    import selcal_cofold_validate as V
    import selcal_deepternary_frame as FR
    mseq, mkeys = V.chain_sequence(model_atoms, model_chain)
    nseq, nkeys = V.chain_sequence(native_atoms, native_chain)
    ident, pairs = V.align_identity(mseq, nseq)
    mca = V._ca_by_residue([a for a in model_atoms if a.chain == model_chain])
    nca = V._ca_by_residue([a for a in native_atoms if a.chain == native_chain])
    P, Q = [], []
    for ia, ib in pairs:
        if ia < len(mkeys) and ib < len(nkeys) and mkeys[ia] in mca and nkeys[ib] in nca:
            P.append(mca[mkeys[ia]]); Q.append(nca[nkeys[ib]])
    if len(P) < V.MIN_ALIGNED_RESIDUES:
        return None, None, {"identity": round(ident, 4), "n_ca_pairs": len(P)}, \
            "only %d Ca pairs for %s->%s" % (len(P), model_chain, native_chain)
    R, t = FR.kabsch(P, Q)
    import numpy as np
    r = FR.rmsd([(R @ np.array(p) + t) for p in P], Q)
    return R, t, {"identity": round(ident, 4), "n_ca_pairs": len(P), "ca_rmsd_A": round(r, 3)}, None


def frame_deviation(model_atoms, native_atoms, model_chain, native_chain, comp,
                    native_lig_key, protein_chains, template_smiles,
                    model_coords=None, native_coords=None):
    """Deviation of the co-fold degrader from the native, in ONE protein's frame. Returns a record.

    `model_coords` / `native_coords` are the two ligands already posed in TEMPLATE order; they are passed in
    rather than recomputed per frame because the match is the expensive part and is frame-independent."""
    import numpy as np
    R, t, detail, err = superpose_chain(model_atoms, native_atoms, model_chain, native_chain)
    rec = {"model_chain": model_chain, "native_chain": native_chain, "superposition": detail}
    if err:
        rec["error"] = err
        return rec
    if model_coords is None or native_coords is None:
        rec["error"] = "one or both degraders could not be posed onto the reference template"
        return rec
    if len(model_coords) != len(native_coords):
        rec["error"] = ("template-ordered atom counts differ (%d model vs %d native) — the two are not the "
                        "same molecule and no correspondence exists"
                        % (len(model_coords), len(native_coords)))
        return rec

    idx = contacting_indices(native_coords, native_atoms, protein_chains)
    rec["n_native_contacting_atoms"] = len(idx)
    if not idx:
        rec["error"] = "no native degrader atom contacts this protein — nothing to compare in this frame"
        return rec

    dev = []
    for i in idx:
        p = np.asarray(R @ np.array(model_coords[i], dtype=float) + t, dtype=float)
        dev.append(float(np.sqrt(((p - np.array(native_coords[i], dtype=float)) ** 2).sum())))
    dev.sort()
    rec.update({
        "n_compared": len(dev),
        "rmsd_A": round(float(np.sqrt(np.mean(np.square(dev)))), 3),
        "median_A": round(dev[len(dev) // 2], 3),
        "min_A": round(dev[0], 3), "max_A": round(dev[-1], 3),
        "pocket_occupied_as_in_crystal": bool(np.sqrt(np.mean(np.square(dev))) <= POCKET_OK_A),
        "_correspondence": "template-ordered graph match, never proximity",
    })
    return rec


def decompose_one(model_path, native_path, record):
    """Both frames for one co-fold, using the FIRST instrument's committed chain map for this co-fold.

    ⛔ THE CHAIN MAP IS READ, NEVER RE-DERIVED. `selcal-cofold-vs-crystal.json` already records, per co-fold,
    the sequence-derived model->native chain correspondence AND which copy of a multi-copy deposit it scored.
    Re-deriving it here would risk this measurement landing on a different copy from the DockQ it is meant to
    explain, and a disagreement would then be ambiguous between 'the placement differs' and 'they looked at
    different copies' — a question not worth manufacturing."""
    import selcal_cofold_validate as V
    import selcal_stage as S

    matched = ((record.get("chain_map") or {}).get("matched")) or {}
    tgt_model = record.get("target_model_chain") or S.CHAIN_TARGET
    e3_model = record.get("e3_model_chains") or [S.CHAIN_VHL, S.CHAIN_ELOB, S.CHAIN_ELOC]
    out = {"model": os.path.basename(model_path), "arm_id": record.get("arm_id"),
           "native_pdb_id": record.get("native_pdb_id"), "seed": record.get("seed")}
    if tgt_model not in matched or e3_model[0] not in matched:
        out["error"] = "the committed chain map does not carry both roles for this co-fold"
        return out

    lig_ref = S.ligand_smiles()
    comp, smiles = lig_ref["ccd"], lig_ref["smiles"]
    model_atoms = V.parse_structure(model_path)
    native_atoms = V.parse_structure(native_path)
    tgt_native = matched[tgt_model]["native_chain"]
    vhl_native = matched[e3_model[0]]["native_chain"]

    # The native degrader copy belonging to THIS scored copy of the deposit.
    import selcal_deepternary_frame as FR
    _, _, deg, err = FR.native_copy(native_atoms, {"target": tgt_native, "e3": [vhl_native]}, comp)
    lig_key = deg[0].key if (deg and not err) else None
    out["native_ligand_key"] = list(lig_key) if lig_key else None
    if err:
        out["native_ligand_note"] = err

    # Pose BOTH degraders onto the reference template once: the graph match is frame-independent, and the
    # two results then share TEMPLATE atom ordering, which is the correspondence.
    mod_heavy = model_ligand_atoms(model_atoms)
    nat_heavy = native_ligand_atoms(native_atoms, lig_key, comp)
    out["ligand_heavy_atoms"] = {"model": len(mod_heavy), "native": len(nat_heavy)}
    mcoords, merr = template_ordered_coords(mod_heavy, smiles)
    ncoords, nerr = template_ordered_coords(nat_heavy, smiles)
    out["template_match"] = {"model": merr or "ok", "native": nerr or "ok"}

    out["target_frame"] = frame_deviation(model_atoms, native_atoms, tgt_model, tgt_native, comp,
                                          lig_key, {tgt_native}, smiles, mcoords, ncoords)
    out["e3_frame"] = frame_deviation(model_atoms, native_atoms, e3_model[0], vhl_native, comp,
                                      lig_key, {vhl_native}, smiles, mcoords, ncoords)
    out["dockq_whole_interface"] = (record.get("dockq") or {}).get("DockQ")
    return out


def verdict(rows):
    """The one sentence this artifact licenses, or an honest refusal."""
    ok = [r for r in rows if r.get("target_frame", {}).get("rmsd_A") is not None
          and r.get("e3_frame", {}).get("rmsd_A") is not None]
    doc = {"n_rows": len(rows), "n_decomposed": len(ok)}
    if not ok:
        doc["sentence"] = ("No co-fold could be decomposed, so WHERE the failure sits is UNMEASURED — which "
                           "is not a statement about the co-folds.")
        return doc
    t = sorted(r["target_frame"]["rmsd_A"] for r in ok)
    e = sorted(r["e3_frame"]["rmsd_A"] for r in ok)
    doc["target_frame_rmsd_A"] = {"min": t[0], "median": t[len(t) // 2], "max": t[-1]}
    doc["e3_frame_rmsd_A"] = {"min": e[0], "median": e[len(e) // 2], "max": e[-1]}
    n_t = sum(1 for r in ok if r["target_frame"]["pocket_occupied_as_in_crystal"])
    n_e = sum(1 for r in ok if r["e3_frame"]["pocket_occupied_as_in_crystal"])
    doc["n_target_pocket_ok"] = n_t
    doc["n_e3_pocket_ok"] = n_e
    doc["pocket_ok_bar_A"] = POCKET_OK_A
    if n_t == len(ok) and n_e == len(ok):
        doc["failure_locus"] = "assembly"
        doc["sentence"] = (
            "All %d co-folds place the degrader in BOTH pockets as the crystal does (target-frame RMSD "
            "median %.2f A, E3-frame median %.2f A, both within %.1f A) while the whole interface scores "
            "0.023-0.046. The failure is the ASSEMBLY of two correctly-occupied halves, not the pockets — so "
            "the missing information is the one a ternary generator supplies when given each end's site."
            % (len(ok), doc["target_frame_rmsd_A"]["median"], doc["e3_frame_rmsd_A"]["median"], POCKET_OK_A))
    elif n_e == len(ok) and n_t == 0:
        doc["failure_locus"] = "target_pocket"
        doc["sentence"] = (
            "The E3 half is placed as in the crystal on all %d co-folds (median %.2f A) but the target half "
            "is NOT (median %.2f A). The degrader is not occupying the target site the crystal shows, so "
            "supplying an assembly would not rescue these structures — the thing to assemble is wrong."
            % (len(ok), doc["e3_frame_rmsd_A"]["median"], doc["target_frame_rmsd_A"]["median"]))
    else:
        doc["failure_locus"] = "mixed"
        doc["sentence"] = (
            "Mixed: %d of %d co-folds occupy the target pocket as in the crystal and %d of %d the E3 pocket "
            "(target median %.2f A, E3 median %.2f A). Neither the assembly-only nor the pocket reading holds "
            "across the panel, and the per-co-fold rows are the result rather than any summary of them."
            % (n_t, len(ok), n_e, len(ok), doc["target_frame_rmsd_A"]["median"],
               doc["e3_frame_rmsd_A"]["median"]))
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Decompose the co-fold failure into pocket vs assembly ($0).")
    ap.add_argument("--cofold-root", default="/tmp/selcal_cofolds")
    ap.add_argument("--native-dir", default="/tmp/selcal_cofolds/_native")
    ap.add_argument("--first-json", default=os.path.join(HERE, "selcal-cofold-vs-crystal.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-cofold-decompose.json"))
    args = ap.parse_args(argv)

    if not os.path.exists(args.first_json):
        json.dump({"error": "%s absent — the chain map this reads has not been produced"
                            % os.path.basename(args.first_json)}, open(args.out, "w"), indent=1)
        print("[decompose] REFUSED: no committed chain map", flush=True)
        return 3
    first = json.load(open(args.first_json))
    rows = []
    for rec in first.get("records", []):
        if not rec.get("graded"):
            continue
        model = rec.get("model_path") or os.path.join(args.cofold_root, rec.get("model") or "")
        if not os.path.exists(model):
            rows.append({"model": rec.get("model"), "error": "co-fold file not present on this runner"})
            continue
        native = os.path.join(args.native_dir, "%s.cif" % (rec.get("native_pdb_id") or ""))
        if not os.path.exists(native):
            native = os.path.join(args.native_dir, "%s.pdb" % (rec.get("native_pdb_id") or ""))
        if not os.path.exists(native):
            rows.append({"model": rec.get("model"), "error": "native not present on this runner"})
            continue
        try:
            rows.append(decompose_one(model, native, rec))
        except Exception as e:                               # noqa: BLE001
            rows.append({"model": rec.get("model"), "error": "%s: %s" % (type(e).__name__, e)})

    doc = {"_what": "where the co-fold failure sits: per-protein pocket placement vs the assembly of the two",
           "pocket_ok_bar_A": POCKET_OK_A, "contact_A": contact_a(), "rows": rows}
    doc.update(verdict(rows))
    json.dump(doc, open(args.out, "w"), indent=1)
    for r in rows[:14]:
        if r.get("error"):
            print("  %-40s ERROR %s" % (str(r.get("model"))[:40], r["error"][:80]), flush=True)
            continue
        print("  %-40s target %-7s E3 %-7s DockQ %s"
              % (str(r.get("model"))[:40], r["target_frame"].get("rmsd_A"), r["e3_frame"].get("rmsd_A"),
                 r.get("dockq_whole_interface")), flush=True)
    print(doc["sentence"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
