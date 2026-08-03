#!/usr/bin/env python3
"""RUNG `5b-T` — assemble the NR4A1/NR4A2/NR4A3 ternary INPUTS for DeepTernary, from recorded chemistry. ($0 CPU)

★★ WHAT THIS IS FOR, AND THE ONE TECHNICAL CONSTRAINT THAT SHAPES ALL OF IT.
`selcal_deepternary_frame.py` builds DeepTernary's published unbound inputs by superposing each unbound
binary **into the native ternary frame** — that is what the shipped `6HAX_B_A_FWZ` data shows the authors
doing, and it is why 33 of the degrader's 66 atoms land within 1 Å of `unbound_lig1`.

⛔ **THERE IS NO NATIVE NR4A3 TERNARY.** Not in this program, not in the PDB. So that step has *no reference
to superpose into*, and the module above cannot be pointed at these arms. This one supplies the missing
frame from the only thing that has ever been measured for it — the RUNG-5a orientation basin `crbn|M0`, whose
`term_a_union.C397.exemplar_placement` carries the 10 landmarks that recover its full rigid transform. The
arrangement is therefore a MODELLED one, and every result downstream is conditional on it.

★ IT DOES NOT LEAK INTO THE PREDICTION, and that is measured rather than assumed: `predict_one_unbound`
applies an independent random rotation+translation to protein 2 and to the ligand before the forward pass.
What the basin frame decides is whether the two-fragment embed is FEASIBLE AT ALL — which is exactly the
pre-flight this module exists to run.

WHAT EACH SLOT IS, AND WHERE IT COMES FROM
------------------------------------------
  unbound_protein1  the matched opened LBD, `results/nr4a3-matrix/nr4a{1,2,3}-opened.pdb`, each put into the
                    NR4A3 frame by `nr4a3_basin_search.superpose_paralogue`. ⛔ Using the SAME sampled E3
                    placement against all three superposed paralogues is what makes this comparison MATCHED;
                    three independent searches would find three different corners of orientation space.
  unbound_lig1      the DOCKED WARHEAD sub-pose (`--dock`, smina, the matched Pocket-5 box), moved by the same
                    superposition. ⛔ INHERITS `R5`, which is UNRESOLVED: `V3` returned INCONCLUSIVE because
                    the pipeline's SITE SELECTION missed on 6 of 6 pairs. Every geometry downstream of this
                    slot is conditional on a site that has not passed its own known-answer test.
  unbound_protein2  a CRBN chain from a DDB1–CRBN **binary** IMiD deposit, placed by (i) recovering the basin
                    exemplar's transform from its landmarks and applying it to the staged registry arm, then
                    (ii) sequence-superposing the binary's CRBN onto that placed copy. ★ The binary is used in
                    preference to the registry's own 6BOY conformer BECAUSE 6BOY IS A TERNARY (DDB1-CRBN-
                    BRD4/dBET6) and a ternary-derived E3 conformer imports that ternary's induced fit.
  unbound_lig2      the binary's own IMiD, in its crystal pose, carried by the same two transforms. CONECT is
                    sourced from the CCD `_chem_comp_bond` table, never from distances.
  ligand.pdb        a CONSTRAINED EMBED of the RECORDED degrader SMILES — warhead atoms pinned on the docked
                    warhead, IMiD atoms pinned on the placed IMiD, in the one common frame. The SMILES comes
                    from `nr4a3-linker-library-chem.json` and is NEVER perceived from coordinates.
  gt_complex.pdb    ⛔ A PLACEHOLDER, NOT A GROUND TRUTH. DeepTernary's script opens this path; there is no
                    native NR4A3 ternary to put in it, so it holds the ASSEMBLED INPUT arrangement and is
                    named `assembly_frame_placeholder_not_ground_truth` in the artifact. No DockQ, LRMSD or
                    fnat may be computed against it for a paralogue arm — the scorer refuses.

THE PRE-FLIGHT, AND THE TWO DEAD RUNS THAT PAID FOR IT
-----------------------------------------------------
Runs 30753431082 and 30754028742 died inside the forward pass at

    replace_to_unbound_coords ->  assert cdist.min(dim=1)[0][update_mask].max() < 1
    RuntimeError: max(): Expected reduction dim to be specified for input.numel() == 0

`update_mask` selects degrader atoms within 1 Å of a supplied fragment atom; the degrader was a CCD ideal
conformer in an arbitrary frame, so the mask was EMPTY. The reference construction gives 33 and 18. So this
module asserts both snap masks are non-empty BEFORE any prediction, and an arm that fails is **REFUSED, never
run "to see"** — its score would measure our input error and would be quoted as the generator's.

⛔ REFUSALS ARE NOT ZEROS. An empty snap mask or an infeasible two-fragment embed is a REFUSAL: the arm is
reported as unrun, with the measured reason, and never as a result of any magnitude.

⛔ SCOPE. Nothing here is a claim about binding, affinity, degradation, selectivity, efficacy or safety. It
writes input files and measures whether they are self-consistent.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))

#: The proximity window `replace_to_unbound_coords` builds its mask with, in Å. Read from its source
#: (`update_mask = cdist.min(dim=1)[0] < 1`), never chosen here.
SNAP_WINDOW_A = 1.0

#: Cα RMSD above which the binary→registry-arm CRBN superposition is refused, in Å. Same bar and the same
#: reasoning as `selcal_deepternary_frame.MAX_SUPERPOSITION_RMSD_A`: above this the two are not the same fold
#: in the same conformation, and carrying it forward would place the IMiD in open solvent.
MAX_SUPERPOSITION_RMSD_A = 5.0

#: The basin the whole C397 story rests on, and the field carrying the landmarks that recover its transform.
BASIN_ARM = "crbn"
BASIN_ID = "crbn|M0"
BASIN_CYSTEINE = "C397"

#: ⛔ ONE construct across all three arms, or the comparison is not matched. Chosen from the four CRBN
#: candidates the cost artifact names — they share the SAME 14-atom backbone and the same warhead/E3 cores —
#: because its electrophile is an ACRYLAMIDE, whose Michael-acceptor β-carbon is unambiguously identifiable by
#: substructure, and arm (C) of the gate has to measure a distance FROM that atom. The other three carry
#: cyanoacrylamide / cyanopropionamide warheads whose "electrophilic carbon" is a judgement call, and a gate
#: arm must not rest on one.
CONSTRUCT_ID = "crbnM0@ex_5amide_a2-a5_acrylamide"

#: Substructure queries. ⛔ Written as SMARTS against the RECORDED SMILES, so the mapping is a chemical fact
#: about the molecule rather than a perception from coordinates.
WARHEAD_SMARTS = "COC(=O)c1c[nH]c2ccc([#7])cc12"        # methyl indole-3-carboxylate + the C5 nitrogen
ELECTROPHILE_SMARTS = "[CH2]=[CH]C(=O)[NX3]"            # acrylamide; atom 0 is the β-carbon
GLUTARIMIDE_SMARTS = "O=C1CCC(N)C(=O)N1"                # the IMiD anchor both ends of the MCS must contain

#: The free warhead that is docked into each matched pocket. It is `cw_ev_5nh2`, the 5-amino member of the
#: staged congeneric series — i.e. the exact fragment the degrader's 5-amide is built from, so the docked pose
#: is a sub-pose of the degrader by construction rather than by resemblance.
WARHEAD_SMILES = "COC(=O)c1c[nH]c2ccc(N)cc12"
WARHEAD_SERIES_ID = "cw_ev_5nh2"

#: DDB1–CRBN **binary** IMiD deposits, in preference order. ⛔ Not remembered PDB IDs: every one of these is
#: already named in `nr4a3-e3-arm-registry.json` (as the staged receptor or in its own `rejected` list), so
#: they come from the E3 lane's UniProt-accession discovery rather than from anyone's memory. The first that
#: resolves to a CRBN chain matching the staged arm AND carries a glutarimide HET is used; if none does, the
#: build REFUSES rather than falling back to the ternary conformer silently.
E3_BINARY_CANDIDATES = ("4TZ4", "4CI3", "4CI1", "4CI2")

PARALOGUES = ("NR4A3", "NR4A1", "NR4A2")

#: Arm directory names. `predict_one_unbound` eagerly calls `auto_download_ideal_sdf(name.split('_')[-1])`,
#: so the last token is a CCD-shaped key we pre-seed with the real degrader; see `seed_ideal_sdf`.
ARM_SUFFIX = "5BT_LIG"


def arm_name(paralogue):
    return "%s_%s" % (paralogue.upper(), ARM_SUFFIX)


# ---------------------------------------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------------------------------------


def _rt_from_point_pair(src_pts, dst_pts):
    """(R, t, rmsd) mapping `src_pts` onto `dst_pts` — an EXACT recovery when the two are the same points
    before and after one rigid motion, which is how the paralogue superposition's transform is recovered
    without changing a function another lane owns."""
    import basin_geom as G
    return G.horn_superpose(list(src_pts), list(dst_pts))


def apply_rt(points, R, t):
    import basin_geom as G
    return G.apply_superpose([tuple(p) for p in points], R, t)


def write_pdb_atoms(rows, dest, conect=()):
    """Minimal PDB writer. `rows` = [(record, name, resname, chain, resseq, x, y, z, element)].

    ⚠ CONECT is written ONLY when asked. `selcal_deepternary_frame` measured why: `MolFromPDBFile` bonds a
    real conformer by PROXIMITY as well as by CONECT, so re-declaring a bond it already inferred raises the
    bond order and sanitization fails. Protein files never get CONECT; a ligand gets it only when its
    connectivity cannot be inferred (a novel HET), and the result is read back and checked either way.
    """
    n = 0
    with open(dest, "w") as fh:
        for i, (rec, name, resname, chain, resseq, x, y, z, elem) in enumerate(rows, start=1):
            nm = name if len(name) >= 4 else " %-3s" % name
            fh.write("%s%5d %-4s %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                     % (rec, i, nm[:4], (resname or "UNK")[:3], (chain or "A")[:1], resseq,
                        float(x), float(y), float(z), (elem or "")[:2].rjust(2)))
            n += 1
        for a, b in (conect or ()):
            fh.write("CONECT%5d%5d\n" % (a, b))
        fh.write("END\n")
    return n


def rdkit_readable(path):
    """(True, None) | (False, why) — a ligand file the model cannot read is a legible refusal here rather than
    `'NoneType' object has no attribute 'GetConformer'` five minutes into the forward pass."""
    try:
        from rdkit import Chem, RDLogger
        RDLogger.DisableLog("rdApp.*")
        m = Chem.MolFromPDBFile(path, removeHs=False, sanitize=True)
    except Exception as e:                                       # noqa: BLE001
        return False, "RDKit raised on %s: %s" % (os.path.basename(path), e)
    if m is None:
        return False, "RDKit cannot sanitize %s" % os.path.basename(path)
    return True, None


def snap_count(probe_xyz, reference_xyz, window=SNAP_WINDOW_A):
    """(n within `window`, closest approach) — the mask the model itself builds, not one invented here."""
    import numpy as np
    if len(probe_xyz) == 0 or len(reference_xyz) == 0:
        return 0, None
    P = np.asarray(probe_xyz, dtype=float)
    Q = np.asarray(reference_xyz, dtype=float)
    d = np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return int((d < window).sum()), round(float(d.min()), 3)


# ---------------------------------------------------------------------------------------------------------
# The chemistry: the recorded degrader, and the two fragments it must be pinned onto
# ---------------------------------------------------------------------------------------------------------


def recorded_degrader(construct_id=CONSTRUCT_ID, chem_path=None):
    """(record, error) for the construct, READ FROM THE COMMITTED LIBRARY.

    ⛔ The SMILES and InChIKey are taken from `nr4a3-linker-library-chem.json`, never perceived from
    coordinates. That is the whole reason this rung exists: the §2.5 ternaries are unusable as evidence
    because their molecule cannot be recovered from any model (`n_recovered = 0 of 3`), so no replicate can
    ever be matched to them."""
    path = chem_path or os.path.join(HERE, "nr4a3-linker-library-chem.json")
    if not os.path.exists(path):
        return None, "%s absent — the degrader has no recorded structure" % os.path.basename(path)
    doc = json.load(open(path))
    for c in doc.get("constructs", []):
        if c.get("construct_id") == construct_id:
            if not c.get("canonical_smiles") or not c.get("inchikey"):
                return None, "%s carries no canonical_smiles/inchikey" % construct_id
            return c, None
    return None, "%s is not in %s" % (construct_id, os.path.basename(path))


def degrader_mol(construct):
    """(mol with explicit Hs suppressed, {role: [atom idx]}, error). Substructure roles, from SMARTS."""
    from rdkit import Chem
    m = Chem.MolFromSmiles(construct["canonical_smiles"])
    if m is None:
        return None, None, "RDKit cannot parse the recorded SMILES of %s" % construct["construct_id"]
    roles = {}
    for key, smarts in (("warhead", WARHEAD_SMARTS), ("electrophile", ELECTROPHILE_SMARTS),
                        ("glutarimide", GLUTARIMIDE_SMARTS)):
        q = Chem.MolFromSmarts(smarts)
        hits = m.GetSubstructMatches(q)
        if len(hits) != 1:
            return None, None, ("the %s query matches %d times in %s — a mapping that is not unique cannot "
                                "pin an atom, and guessing which copy is meant is exactly the kind of silent "
                                "choice this rung exists to remove" % (key, len(hits), construct["construct_id"]))
        roles[key] = list(hits[0])
    return m, roles, None


# ---------------------------------------------------------------------------------------------------------
# Site 1 — the matched opened LBD and the docked warhead
# ---------------------------------------------------------------------------------------------------------


def matched_receptors(struct_dir=None):
    """{paralogue: model} with NR4A1/NR4A2 put into the NR4A3 frame, plus the recovered (R, t) for each.

    The superposition itself is `nr4a3_basin_search.superpose_paralogue` — the SAME function the basin search
    used, imported rather than reimplemented, so the frame these arms are built in is the frame the placement
    was sampled in. Its (R, t) is then recovered exactly by fitting the model's own Cα before and after."""
    import nr4a3_basin_search as BS
    struct_dir = struct_dir or os.path.join(REPO, "results", "nr4a3-matrix")
    ref = BS.load_paralogue(os.path.join(struct_dir, "nr4a3-opened.pdb"))
    out = {"NR4A3": {"model": ref, "R": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "t": (0.0, 0.0, 0.0),
                     "superposition": {"_note": "reference frame; identity transform"}}}
    for p in ("NR4A1", "NR4A2"):
        mob = BS.load_paralogue(os.path.join(struct_dir, "%s-opened.pdb" % p.lower()))
        moved = BS.superpose_paralogue(mob, ref)
        keys = list(mob["ca"].keys())
        R, t, rms = _rt_from_point_pair([mob["ca"][k] for k in keys], [moved["ca"][k] for k in keys])
        out[p] = {"model": moved, "R": R, "t": t, "superposition": moved["superposition"],
                  "transform_recovery_rms_A": round(rms, 6)}
    return out


def dock_box(struct_dir=None, pad=6.0):
    """(centre, size) of the docking box, DERIVED from the poses already docked into these very receptors.

    ⛔ Not a box typed here. `results/nr4a3-matrix/docked_nr4a{1,2,3}.sdf` are 13 ligands docked into these
    three opened models through the harmonized Pocket-5 protocol; their own extent IS that box, so deriving
    it keeps the warhead in the same site as everything else this program measured — and inherits that site's
    unresolved `R5` along with it, which is stated wherever the result is."""
    from rdkit import Chem
    struct_dir = struct_dir or os.path.join(REPO, "results", "nr4a3-matrix")
    boxes = {}
    for p in PARALOGUES:
        path = os.path.join(struct_dir, "docked_%s.sdf" % p.lower())
        pts = []
        for m in Chem.SDMolSupplier(path, removeHs=True, sanitize=False):
            if m is None or m.GetNumConformers() == 0:
                continue
            c = m.GetConformer()
            pts.extend([tuple(c.GetAtomPosition(i)) for i in range(m.GetNumAtoms())])
        if not pts:
            boxes[p] = None
            continue
        lo = [min(q[i] for q in pts) for i in range(3)]
        hi = [max(q[i] for q in pts) for i in range(3)]
        boxes[p] = {"center": [round((lo[i] + hi[i]) / 2.0, 3) for i in range(3)],
                    "size": [round(hi[i] - lo[i] + 2 * pad, 3) for i in range(3)],
                    "n_reference_atoms": len(pts),
                    "_derived_from": "the extent of the poses already docked into this receptor"}
    return boxes


# ---------------------------------------------------------------------------------------------------------
# Site 2 — the E3, placed by the basin exemplar's own landmarks
# ---------------------------------------------------------------------------------------------------------


def exemplar_placement(basins_path=None, arm=BASIN_ARM, basin_id=BASIN_ID, cys=BASIN_CYSTEINE):
    """(placement, error) — the `term_a_union.<cys>.exemplar_placement` of the named meta-basin."""
    basins_path = basins_path or os.path.join(HERE, "nr4a3-orientation-basins.json")
    if not os.path.exists(basins_path):
        return None, "%s absent" % os.path.basename(basins_path)
    doc = json.load(open(basins_path))
    for mb in doc.get("arms", {}).get(arm, {}).get("meta_basins", []):
        if mb.get("meta_basin_id") != basin_id:
            continue
        ex = ((mb.get("term_a_union") or {}).get(cys) or {}).get("exemplar_placement")
        if not ex:
            return None, "%s carries no exemplar_placement for %s" % (basin_id, cys)
        return {"meta_basin_id": basin_id, "arm": arm, "cysteine": cys, **ex}, None
    return None, "%s not found under arms.%s.meta_basins" % (basin_id, arm)


def placed_registry_arm(placement, registry_path=None):
    """(all atoms of the staged E3 arm, moved into the target frame, detail, error).

    The transform is recovered by `nr4a3_linker_design.recover_transform`, which REFUSES unless the fit to the
    stored landmarks reproduces the placement's OWN recorded E3 anchor to 0.05 Å. That is an independent
    confirmation the recovered rotation is the one the search actually used, not a plausible one."""
    import nr4a3_basin_search as BS
    import nr4a3_linker_design as LD
    import basin_geom as G
    registry_path = registry_path or os.path.join(HERE, "nr4a3-e3-arm-registry.json")
    reg = json.load(open(registry_path))
    rec = (reg.get("arms") or {}).get(placement.get("arm") or BASIN_ARM)
    if rec is None:
        return None, None, "the registry has no %s arm" % (placement.get("arm") or BASIN_ARM)
    arm = BS.load_arm_from_registry(rec)
    arm["_landmarks"] = [arm["ca"][i] for i in G.farthest_point_sample(arm["ca"], 10)]
    try:
        R, t, rms, err = LD.recover_transform(arm, placement["landmarks"], placement["anchor_e3_xyz"])
    except ValueError as e:                                      # noqa: BLE001
        return None, None, str(e)

    order, res = BS.parse_multichain_pdb(os.path.join(REPO, rec["receptor_pdb"]))
    crbn_chain = (rec.get("_receptor_copy_chains") or {}).get(rec["recruiter"]) \
        or (rec.get("assembly_copy", {}).get("selected_chains", {}) or {}).get(rec["recruiter"])
    rows = []
    for key in order:
        if crbn_chain and key[0] != crbn_chain:
            continue
        r = res[key]
        for nm, xyz in r["atoms"]:
            rows.append({"chain": key[0], "resseq": key[1], "resname": r.get("resname") or r.get("aa"),
                         "name": nm, "xyz": xyz, "aa": r["aa"]})
    if not rows:
        return None, None, "no atoms on the staged %s chain %s" % (rec["recruiter"], crbn_chain)
    moved = apply_rt([q["xyz"] for q in rows], R, t)
    for q, p in zip(rows, moved):
        q["xyz"] = p
    detail = {"transform_recovery_rms_A": round(rms, 4), "anchor_reproduced_to_A": round(err, 4),
              "receptor_pdb": rec["receptor_pdb"], "chain": crbn_chain,
              "n_atoms": len(rows), "receptor_entry": (rec.get("provenance") or {}).get("receptor_entry"),
              "⛔_provenance": "6BOY is a TERNARY (DDB1-CRBN-BRD4/dBET6). This placed copy is used ONLY as the "
                              "frame onto which a BINARY IMiD deposit is superposed; its own conformer never "
                              "reaches the model, precisely because a ternary-derived E3 imports that "
                              "ternary's induced fit."}
    return rows, detail, None


def registry_arm_chain_sequence(rows):
    """(sequence, {resseq: CA xyz}) for the placed registry arm, in its own residue order."""
    seq, ca, seen = [], {}, set()
    for r in rows:
        key = r["resseq"]
        if key not in seen:
            seen.add(key)
            seq.append(r["aa"])
        if r["name"] == "CA":
            ca[key] = r["xyz"]
    return "".join(seq), ca


def resolve_e3_binary(placed_rows, workdir, candidates=E3_BINARY_CANDIDATES, raw_dir=None):
    """(chain atoms, ligand atoms, detail, error) — a DDB1–CRBN BINARY's CRBN chain and its IMiD, both moved
    into the target frame by superposition onto the placed registry copy.

    ⛔ DISCOVERED, NOT ASSERTED. The deposit is accepted only when (a) one of its polymer chains matches the
    staged CRBN at or above the lane's own identity floor, (b) that chain carries a HET component whose
    CCD-sourced connectivity sanitizes in RDKit AND contains a glutarimide, and (c) the superposition onto the
    placed copy lands under `MAX_SUPERPOSITION_RMSD_A`. A deposit failing any of the three is skipped with its
    reason recorded; if every candidate fails the build REFUSES rather than falling back to the 6BOY TERNARY
    conformer, because a silent fallback is exactly the substitution the cost artifact warned about."""
    import numpy as np
    import basin_geom as G
    import selcal_cofold_validate as V
    import selcal_deepternary_run as RUN

    ref_seq, ref_ca = registry_arm_chain_sequence(placed_rows)
    tried = []
    for pid in candidates:
        rec = {"pdb_id": pid}
        try:
            path = RUN._fetch_structure(pid, workdir)
        except Exception as e:                                   # noqa: BLE001
            rec["error"] = "fetch failed: %s" % e
            tried.append(rec)
            continue
        if not path or not os.path.exists(path):
            rec["error"] = "fetch produced no file"
            tried.append(rec)
            continue
        atoms = V.parse_structure(path)

        best = None
        for ch in V.polymer_chains(atoms):
            useq, _ = V.chain_sequence(atoms, ch)
            ident, pairs = V.align_identity(useq, ref_seq)
            if best is None or ident > best[1]:
                best = (ch, ident, pairs)
        if best is None:
            rec["error"] = "no polymer chain"
            tried.append(rec)
            continue
        ch, ident, pairs = best
        rec.update(chain=ch, identity_to_staged_crbn=round(ident, 4))
        floor = V.MIN_CHAIN_IDENTITY
        if ident < floor:
            rec["error"] = ("best chain %s matches the staged CRBN at identity %.3f, below the lane's floor "
                            "%.2f — a different protein, or a non-human orthologue" % (ch, ident, floor))
            tried.append(rec)
            continue

        chain_atoms = [a for a in atoms if a.chain == ch and not a.hetatm and a.is_heavy]
        uca = V._ca_by_residue(chain_atoms)
        ukeys = V.chain_sequence(atoms, ch)[1]
        P, Q = [], []
        ref_keys = []
        seen = set()
        for r in placed_rows:
            if r["resseq"] not in seen:
                seen.add(r["resseq"])
                ref_keys.append(r["resseq"])
        for ia, ib in pairs:
            if ia < len(ukeys) and ib < len(ref_keys):
                ka, kb = ukeys[ia], ref_keys[ib]
                if ka in uca and kb in ref_ca:
                    P.append(tuple(uca[ka])); Q.append(tuple(ref_ca[kb]))
        rec["n_ca_pairs"] = len(P)
        if len(P) < V.MIN_ALIGNED_RESIDUES:
            rec["error"] = "only %d Cα pairs survived the alignment, below %d" % (len(P), V.MIN_ALIGNED_RESIDUES)
            tried.append(rec)
            continue
        R, t, rms = G.horn_superpose(P, Q)
        rec["ca_rmsd_A"] = round(rms, 3)
        if rms > MAX_SUPERPOSITION_RMSD_A:
            rec["error"] = ("superposition Cα RMSD %.2f Å exceeds %.1f Å — the binary and the staged copy are "
                            "not the same fold in the same conformation" % (rms, MAX_SUPERPOSITION_RMSD_A))
            tried.append(rec)
            continue

        # The IMiD: a HET on (or contacting) that chain, big enough to be a drug and small enough not to be a
        # second protein, whose CCD connectivity sanitizes and which contains a glutarimide.
        groups = {}
        for a in atoms:
            if not a.hetatm or not a.is_heavy or a.resname.upper() in ("HOH", "DOD"):
                continue
            groups.setdefault((a.resname.upper(), a.chain, a.resseq), []).append(a)
        chain_xyz = np.array([[a.x, a.y, a.z] for a in chain_atoms], dtype=float)
        lig, lig_detail, lig_err = None, None, "no HET component on chain %s sanitizes to a glutarimide" % ch
        for (comp, lch, rseq), ats in sorted(groups.items()):
            if not (12 <= len(ats) <= 60):
                continue
            L = np.array([[a.x, a.y, a.z] for a in ats], dtype=float)
            dmin = float(np.sqrt(((L[:, None, :] - chain_xyz[None, :, :]) ** 2).sum(axis=2)).min())
            if dmin > 5.0:
                continue
            bonds, berr = RUN.ccd_bonds(comp, workdir)
            if berr or not bonds:
                continue
            probe = os.path.join(workdir, "_probe_%s_%s%d.pdb" % (comp, lch, rseq))
            names = {}
            rows = []
            for i, a in enumerate(ats, start=1):
                names[a.name] = i
                rows.append(("HETATM", a.name, comp, "B", 1, a.x, a.y, a.z, a.element))
            con = [(names[b1], names[b2]) for (b1, b2) in bonds if b1 in names and b2 in names]
            write_pdb_atoms(rows, probe, conect=con)
            ok, why = rdkit_readable(probe)
            if not ok:
                continue
            from rdkit import Chem
            mol = Chem.MolFromPDBFile(probe, removeHs=False, sanitize=True)
            if mol is None or not mol.HasSubstructMatch(Chem.MolFromSmarts(GLUTARIMIDE_SMARTS)):
                continue
            lig, lig_err = ats, None
            lig_detail = {"het_code": comp, "chain": lch, "resseq": rseq, "n_heavy": len(ats),
                          "min_dist_to_crbn_A": round(dmin, 2), "n_ccd_bonds_applied": len(con),
                          "probe_pdb": probe}
            break
        if lig_err:
            rec["error"] = lig_err
            tried.append(rec)
            continue

        moved_chain = apply_rt([(a.x, a.y, a.z) for a in chain_atoms], R, t)
        moved_lig = apply_rt([(a.x, a.y, a.z) for a in lig], R, t)
        rec.update(ligand=lig_detail, ok=True)
        tried.append(rec)
        chain_out = [{"name": a.name, "resname": a.resname, "resseq": a.resseq, "element": a.element,
                      "xyz": p} for a, p in zip(chain_atoms, moved_chain)]
        lig_out = [{"name": a.name, "resname": a.resname, "resseq": a.resseq, "element": a.element,
                    "xyz": p} for a, p in zip(lig, moved_lig)]
        return chain_out, lig_out, {"selected": rec, "tried": tried}, None
    return None, None, {"tried": tried}, ("no DDB1–CRBN binary IMiD deposit could be resolved from %s; the "
                                          "6BOY TERNARY conformer is NOT substituted silently"
                                          % ", ".join(candidates))


def select_docked_pose(sdf_path, R, t, anchor_xyz, warhead_smarts=WARHEAD_SMARTS):
    """(coords of the chosen pose's warhead-match atoms in the target frame, detail, error).

    ⛔ THE SELECTION RULE IS FIXED BEFORE THE RUN AND IS NOT AN OUTCOME RULE: take the smina pose whose C5
    nitrogen — the atom the linker leaves from — lands nearest the exit-vector anchor **the E3 placement was
    sampled conditional on**. Any other pose is not the geometry that placement was derived under, so picking
    the best-scoring pose instead would silently change the question. Every pose's score and anchor distance
    is published so the choice is visible."""
    import numpy as np
    from rdkit import Chem
    if not os.path.exists(sdf_path):
        return None, None, "%s absent — the warhead was not docked" % os.path.basename(sdf_path)
    q = Chem.MolFromSmarts(warhead_smarts)
    rows, best = [], None
    for i, mol in enumerate(Chem.SDMolSupplier(sdf_path, removeHs=True, sanitize=True)):
        if mol is None or mol.GetNumConformers() == 0:
            rows.append({"pose": i, "error": "unreadable"})
            continue
        match = mol.GetSubstructMatch(q)
        if len(match) != len(q.GetAtoms()):
            rows.append({"pose": i, "error": "the docked molecule does not carry the warhead substructure"})
            continue
        conf = mol.GetConformer()
        pts = apply_rt([tuple(conf.GetAtomPosition(int(a))) for a in match], R, t)
        d = float(np.linalg.norm(np.array(pts[11]) - np.array(anchor_xyz, dtype=float)))
        score = mol.GetProp("minimizedAffinity") if mol.HasProp("minimizedAffinity") else None
        rows.append({"pose": i, "c5n_to_exitvec_anchor_A": round(d, 2),
                     "smina_affinity_kcal_per_mol": float(score) if score else None})
        if best is None or d < best[0]:
            best = (d, i, pts)
    if best is None:
        return None, {"poses": rows}, "no docked pose carried the warhead substructure"
    return best[2], {"poses": rows, "chosen_pose": best[1], "chosen_c5n_to_anchor_A": round(best[0], 2),
                     "_rule": "nearest C5 nitrogen to the exit-vector anchor the E3 placement was sampled at; "
                              "fixed before the run, not chosen on the outcome"}, None


def restrained_two_end_embed(mol_noH, warhead_idx, warhead_targets, imid_pairs,
                             n_confs=200, seed=20260803):
    """(mol with a chosen conformer, detail, error) — the degrader pinned on BOTH fragments at once.

    ★ WHY A RESTRAINED MINIMISATION RATHER THAN A HARD `coordMap` ON BOTH ENDS. A hard two-end coordMap either
    embeds or raises, and a raise says only "infeasible" — it cannot say *how far off* the second end was, and
    that distance is the pre-flight's whole content. So the warhead is pinned by `coordMap` (it is a rigid
    sub-pose that must be reproduced), the IMiD is pulled by distance restraints, and what is REPORTED is how
    close the pulled end actually got. An arm whose IMiD cannot reach its target is refused on the measured
    snap mask below, not on an exception."""
    import numpy as np
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Geometry import Point3D

    mol = Chem.AddHs(mol_noH)
    cmap = {int(i): Point3D(*[float(x) for x in p]) for i, p in zip(warhead_idx, warhead_targets)}
    cids = AllChem.EmbedMultipleConfs(mol, numConfs=n_confs, coordMap=cmap, randomSeed=seed,
                                      useRandomCoords=True, maxAttempts=40, numThreads=0)
    if not len(cids):
        return None, {"n_conformers": 0}, ("the constrained embed produced no conformer: with the warhead "
                                           "pinned on its docked sub-pose the molecule cannot be built at "
                                           "all. REFUSED — this is not a zero.")
    props = AllChem.MMFFGetMoleculeProperties(mol)
    W = np.asarray(warhead_targets, dtype=float)
    best = None
    for cid in cids:
        ff = AllChem.MMFFGetMoleculeForceField(mol, props, confId=cid)
        pids = [ff.AddExtraPoint(*[float(x) for x in tgt], fixed=True) - 1 for _, tgt in imid_pairs]
        ff.Initialize()
        for i in warhead_idx:
            ff.MMFFAddPositionConstraint(int(i), 0.25, 500.0)
        for pid, (idx, _tgt) in zip(pids, imid_pairs):
            ff.AddDistanceConstraint(pid, int(idx), 0.0, 0.5, 100.0)
        ff.Minimize(maxIts=1000)
        conf = mol.GetConformer(cid)
        Q = np.array([list(conf.GetAtomPosition(int(i))) for i in warhead_idx], dtype=float)
        war = float(np.sqrt(((Q - W) ** 2).sum(axis=1).mean()))
        I = np.array([list(conf.GetAtomPosition(int(i))) for i, _ in imid_pairs], dtype=float)
        T = np.array([t for _, t in imid_pairs], dtype=float)
        imid = float(np.sqrt(((I - T) ** 2).sum(axis=1).mean()))
        if best is None or (war + imid) < best[0]:
            best = (war + imid, cid, war, imid)
    _, cid, war, imid = best
    keep = Chem.Mol(mol)
    keep.RemoveAllConformers()
    keep.AddConformer(mol.GetConformer(cid), assignId=True)
    return keep, {"n_conformers": len(cids), "chosen_conf": int(cid),
                  "warhead_rmsd_to_docked_pose_A": round(war, 3),
                  "imid_rmsd_to_placed_fragment_A": round(imid, 3),
                  "_reading": "both are RMSDs to the two supplied fragment poses, not to anything measured. "
                              "They say how well the recorded molecule can bridge the modelled arrangement — "
                              "nothing about affinity, and nothing about whether the arrangement is right."}, None


def _receptor_rows(model, chain="A"):
    rows = []
    for rid in sorted(model["atoms_by_res"]):
        for a in model["atoms_by_res"][rid]:
            rows.append(("ATOM  ", a["name"], a.get("resname") or "UNK", chain, rid,
                         a["x"], a["y"], a["z"], a["elem"]))
    return rows


def build_arm(paralogue, ctx, base, workdir):
    """Write the eight files `predict_one_unbound` reads for one paralogue arm. Returns a status row."""
    import numpy as np
    from rdkit import Chem
    from rdkit.Chem import rdFMCS

    name = arm_name(paralogue)
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    row = {"arm": name, "paralogue": paralogue, "ok": True, "why": None, "detail": {}}

    rec = ctx["receptors"][paralogue]
    R, t = rec["R"], rec["t"]
    row["detail"]["matched_superposition"] = rec["superposition"]

    # ---- site 1: the docked warhead sub-pose, moved into the matched frame
    sdf = os.path.join(ctx["docked_dir"], "docked_%s_warhead.sdf" % paralogue.lower())
    war_pts, war_detail, err = select_docked_pose(sdf, R, t, ctx["exitvec_anchor"])
    row["detail"]["docked_warhead"] = war_detail
    if err:
        row.update(ok=False, why="site 1 REFUSED — %s" % err)
        return row

    # ---- site 2: the placed binary CRBN and its IMiD (identical for all three arms, by construction)
    imid_xyz = [a["xyz"] for a in ctx["e3_ligand"]]

    # ---- the degrader: MCS between the recorded molecule and the placed IMiD, then the two-end embed
    imid_probe = ctx["e3_ligand_detail"]["selected"]["ligand"]["probe_pdb"]
    imid_mol = Chem.MolFromPDBFile(imid_probe, removeHs=False, sanitize=True)
    deg = ctx["degrader_mol"]
    mcs = rdFMCS.FindMCS([deg, imid_mol], ringMatchesRingOnly=True, completeRingsOnly=True,
                         timeout=60)
    q = Chem.MolFromSmarts(mcs.smartsString) if mcs.smartsString else None
    dmatch = deg.GetSubstructMatch(q) if q else ()
    imatch = imid_mol.GetSubstructMatch(q) if q else ()
    glut = set(ctx["roles"]["glutarimide"])
    row["detail"]["imid_mcs"] = {"n_atoms": len(dmatch), "smarts": mcs.smartsString if q else None,
                                 "n_overlapping_the_glutarimide": len(glut & set(dmatch))}
    if len(dmatch) < 8 or len(glut & set(dmatch)) < 4:
        row.update(ok=False, why=("site 2 REFUSED — the maximum common substructure between the recorded "
                                  "degrader and the deposited IMiD covers %d atoms, %d of them on the "
                                  "glutarimide; that is too little to pin the E3 end, and a looser match "
                                  "would be pinning the wrong part of the molecule"
                                  % (len(dmatch), len(glut & set(dmatch)))))
        return row
    # ⚠ THE TARGET COORDINATES ARE THE **PLACED** ONES, NOT THE PROBE'S. `imid_mol` was read from the probe
    # PDB, which is written in the DEPOSIT's own frame; `imid_xyz` is the same atom list after the two
    # transforms that put it in the target frame. The probe rows and `ctx["e3_ligand"]` are built from one
    # ordered atom list, so index i is the same atom in both — pinning to the probe's coordinates instead
    # would place the IMiD tens of Å away and the snap mask would (correctly) refuse the arm.
    if imid_mol.GetNumAtoms() != len(imid_xyz):
        row.update(ok=False, why=("site 2 REFUSED — the IMiD probe has %d atoms against %d placed atoms, so "
                                  "the index correspondence that carries the placement is not established"
                                  % (imid_mol.GetNumAtoms(), len(imid_xyz))))
        return row
    imid_pairs = [(int(di), list(imid_xyz[int(ii)])) for di, ii in zip(dmatch, imatch)]

    ligmol, embed_detail, err = restrained_two_end_embed(
        deg, ctx["roles"]["warhead"], war_pts, imid_pairs,
        n_confs=ctx["n_confs"], seed=ctx["seed"])
    row["detail"]["embed"] = embed_detail
    if err:
        row.update(ok=False, why="REFUSED — %s" % err)
        return row

    conf = ligmol.GetConformer()
    deg_heavy = [(a.GetIdx(), a.GetSymbol()) for a in ligmol.GetAtoms() if a.GetAtomicNum() > 1]
    deg_xyz = [[conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z]
               for i, _ in deg_heavy]

    # ---- ★ THE PRE-FLIGHT. Both masks non-empty, or the arm is REFUSED before any prediction.
    n1, c1 = snap_count(deg_xyz, war_pts)
    n2, c2 = snap_count(deg_xyz, imid_xyz)
    row["detail"]["snap_masks"] = {
        "unbound_lig1_warhead": {"n_degrader_atoms_within_1A": n1, "closest_approach_A": c1},
        "unbound_lig2_imid": {"n_degrader_atoms_within_1A": n2, "closest_approach_A": c2},
        "reference_construction": {"unbound_lig1": 33, "unbound_lig2": 18, "on": "6HAX_B_A_FWZ"},
        "_why": "`replace_to_unbound_coords` builds `cdist.min(dim=1)[0] < 1` and reduces over it; an empty "
                "mask is the RuntimeError that killed runs 30753431082 and 30754028742."}
    if n1 == 0 or n2 == 0:
        row.update(ok=False, why=(
            "PRE-FLIGHT REFUSAL — snap mask empty (warhead %d, IMiD %d; closest approaches %s / %s Å). "
            "`replace_to_unbound_coords` would reduce over an empty tensor and die exactly as before. This is "
            "a measured negative about whether the recorded degrader can bridge this modelled arrangement, "
            "and it is NOT a zero score." % (n1, n2, c1, c2)))
        return row

    # ---- write the eight files
    lig_rows = [("HETATM", "%s%d" % (sym, k + 1), "LIG", "A", 1, p[0], p[1], p[2], sym)
                for k, ((_, sym), p) in enumerate(zip(deg_heavy, deg_xyz))]
    p1 = _receptor_rows(rec["model"], "A")
    p2 = [("ATOM  ", a["name"], a["resname"], "B", a["resseq"], a["xyz"][0], a["xyz"][1], a["xyz"][2],
           a["element"]) for a in ctx["e3_chain"]]
    ul1 = [("HETATM", "W%d" % (k + 1), "WAR", "A", 1, p[0], p[1], p[2], sym)
           for k, (p, sym) in enumerate(zip(war_pts, ctx["warhead_elements"]))]
    ul2 = [("HETATM", a["name"], a["resname"], "B", 1, a["xyz"][0], a["xyz"][1], a["xyz"][2], a["element"])
           for a in ctx["e3_ligand"]]
    written = {
        "protein1.pdb": write_pdb_atoms(p1, os.path.join(d, "protein1.pdb")),
        "unbound_protein1.pdb": write_pdb_atoms(p1, os.path.join(d, "unbound_protein1.pdb")),
        "protein2.pdb": write_pdb_atoms(p2, os.path.join(d, "protein2.pdb")),
        "unbound_protein2.pdb": write_pdb_atoms(p2, os.path.join(d, "unbound_protein2.pdb")),
        "unbound_lig1.pdb": write_pdb_atoms(ul1, os.path.join(d, "unbound_lig1.pdb")),
        "unbound_lig2.pdb": write_pdb_atoms(ul2, os.path.join(d, "unbound_lig2.pdb")),
        "ligand.pdb": write_pdb_atoms(lig_rows, os.path.join(d, "ligand.pdb")),
        "gt_complex.pdb": write_pdb_atoms(p1 + p2 + lig_rows, os.path.join(d, "gt_complex.pdb")),
    }
    from rdkit import Chem as _C
    _C.MolToMolFile(ligmol, os.path.join(d, "ligand.sdf"))
    row["detail"]["written"] = written
    row["detail"]["gt_complex_is"] = ("assembly_frame_placeholder_not_ground_truth — there is NO native NR4A3 "
                                      "ternary. DockQ/LRMSD/fnat against this file are meaningless and the "
                                      "scorer refuses to compute them for a paralogue arm.")
    row["detail"]["protein1_is_also_unbound_protein1"] = (
        "the same matched opened LBD serves both slots, because there is no native ternary to take a bound "
        "conformer from. Stated rather than hidden: this arm supplies NO induced fit on the target side.")

    unreadable = []
    for f in ("ligand.pdb", "unbound_lig1.pdb", "unbound_lig2.pdb"):
        ok, why = rdkit_readable(os.path.join(d, f))
        row["detail"].setdefault("rdkit_readable", {})[f] = True if ok else why
        if not ok:
            unreadable.append(why)
    if unreadable:
        row.update(ok=False, why="REFUSED — %s" % "; ".join(unreadable))
        return row

    # arm (C) needs the electrophile carbon and, on the NR4A3 arm only, the C397 SG it must reach.
    ele_beta = ctx["roles"]["electrophile"][0]
    heavy_order = [i for i, _ in deg_heavy]
    row["detail"]["arm_C_inputs"] = {
        "electrophile_beta_carbon_ligand_atom": "%s%d" % (ligmol.GetAtomWithIdx(ele_beta).GetSymbol(),
                                                          heavy_order.index(ele_beta) + 1),
        "electrophile_beta_carbon_index_in_ligand_pdb": heavy_order.index(ele_beta) + 1,
        "n_backbone_atoms_measured": ctx["construct"]["n_backbone_atoms_measured"],
        "c397_sg_xyz": ctx["c397_sg"] if paralogue == "NR4A3" else None,
        "_note": ("C397 is NR4A3-unique; the comparator arms have no such cysteine, which is the categorical "
                  "handle itself. Arm (C) is therefore measured on the NR4A3 arm only.")}
    return row


def seed_ideal_sdf(base, dt_root, arms):
    """Pre-seed the CCD key `predict_one_unbound` eagerly fetches, with the REAL degrader.

    `auto_download_ideal_sdf(name.split('_')[-1])` runs before anything else and stores a 404 body under that
    key when the token is not a CCD id. It is only read when RDKit's own conformer generation fails, but when
    it does the failure is a confusing `ideal_mol is None`."""
    import shutil
    out = os.path.join(dt_root, "data", "TernaryDB", "ligand_ideal")
    os.makedirs(out, exist_ok=True)
    done = []
    for a in arms:
        src = os.path.join(base, a, "ligand.sdf")
        if os.path.exists(src):
            dest = os.path.join(out, "%s_ideal.sdf" % a.split("_")[-1])
            shutil.copyfile(src, dest)
            done.append(dest)
    return sorted(set(done))


# ---------------------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------------------


def mode_dock_inputs(args):
    """Write the receptor PDB + warhead SDF + box smina needs, one per paralogue, in each receptor's OWN frame."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    import nr4a3_basin_search as BS
    os.makedirs(args.workdir, exist_ok=True)
    struct_dir = os.path.join(REPO, "results", "nr4a3-matrix")
    boxes = dock_box(struct_dir)
    w = Chem.AddHs(Chem.MolFromSmiles(WARHEAD_SMILES))
    AllChem.EmbedMolecule(w, randomSeed=20260803)
    AllChem.MMFFOptimizeMolecule(w)
    Chem.MolToMolFile(w, os.path.join(args.workdir, "warhead.sdf"))
    out = {"_what": "inputs for the $0 smina dock of the warhead into each matched opened pocket",
           "warhead": {"series_id": WARHEAD_SERIES_ID, "smiles": WARHEAD_SMILES,
                       "sdf": os.path.join(args.workdir, "warhead.sdf")},
           "boxes": boxes, "receptors": {}}
    for p in PARALOGUES:
        src = os.path.join(struct_dir, "%s-opened.pdb" % p.lower())
        model = BS.load_paralogue(src)
        dest = os.path.join(args.workdir, "%s_receptor.pdb" % p.lower())
        write_pdb_atoms(_receptor_rows(model, "A"), dest)
        out["receptors"][p] = {"source": os.path.relpath(src, REPO), "prepared": dest,
                               "n_heavy_atoms": len(model["heavy_xyz"])}
    json.dump(out, open(args.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "receptors"}, indent=1), flush=True)
    return 0


def mode_plan(args):
    """Resolve every COMMITTED input and refuse loudly if one is missing. No network, no smina, no model."""
    doc = {"_what": "RUNG 5b-T pre-flight over the committed inputs only", "ok": True, "problems": []}
    c, err = recorded_degrader()
    doc["degrader"] = {"construct_id": CONSTRUCT_ID,
                       "canonical_smiles": c["canonical_smiles"] if c else None,
                       "inchikey": c["inchikey"] if c else None,
                       "n_backbone_atoms_measured": c.get("n_backbone_atoms_measured") if c else None,
                       "source": "research/modalities/nr4a3-linker-library-chem.json",
                       "_never": "perceived from coordinates"}
    if err:
        doc["problems"].append(err)
    else:
        m, roles, rerr = degrader_mol(c)
        doc["degrader"]["substructure_roles"] = {k: len(v) for k, v in (roles or {}).items()}
        if rerr:
            doc["problems"].append(rerr)
    pl, perr = exemplar_placement()
    doc["placement"] = pl and {k: pl[k] for k in ("meta_basin_id", "basin_id", "pose_id", "exact_atoms",
                                                  "span_A", "anchor_e3_xyz")}
    if perr:
        doc["problems"].append(perr)
    else:
        rows, det, aerr = placed_registry_arm(pl)
        doc["e3_placement"] = det
        if aerr:
            doc["problems"].append(aerr)
    doc["boxes"] = dock_box()
    for p in PARALOGUES:
        f = os.path.join(REPO, "results", "nr4a3-matrix", "%s-opened.pdb" % p.lower())
        if not os.path.exists(f):
            doc["problems"].append("%s absent" % f)
    doc["ok"] = not doc["problems"]
    doc["sentence"] = ("Every committed input for RUNG 5b-T resolves." if doc["ok"]
                       else "REFUSED before any compute: %s" % "; ".join(doc["problems"]))
    json.dump(doc, open(args.out, "w"), indent=1)
    print(doc["sentence"], flush=True)
    return 0 if doc["ok"] else 6


def mode_build(args):
    import basin_geom as G
    import nr4a3_basin_search as BS
    os.makedirs(args.workdir, exist_ok=True)
    base = args.base or os.path.join(args.workdir, "protac22")
    os.makedirs(base, exist_ok=True)

    doc = {"_what": "RUNG 5b-T — the assembled inputs for the three paralogue arms",
           "_status": "INPUT CONSTRUCTION AND ITS PRE-FLIGHT. No prediction, no score, no claim.",
           "construct_id": CONSTRUCT_ID, "arms": []}

    c, err = recorded_degrader()
    if err:
        doc["error"] = err
        json.dump(doc, open(args.out, "w"), indent=1)
        print("REFUSED —", err, flush=True)
        return 6
    deg, roles, err = degrader_mol(c)
    if err:
        doc["error"] = err
        json.dump(doc, open(args.out, "w"), indent=1)
        print("REFUSED —", err, flush=True)
        return 6
    doc["degrader"] = {"construct_id": c["construct_id"], "canonical_smiles": c["canonical_smiles"],
                       "inchikey": c["inchikey"],
                       "n_backbone_atoms_measured": c.get("n_backbone_atoms_measured"),
                       "_source": "nr4a3-linker-library-chem.json — recorded, never perceived"}

    pl, err = exemplar_placement()
    if err:
        doc["error"] = err
        json.dump(doc, open(args.out, "w"), indent=1)
        print("REFUSED —", err, flush=True)
        return 6
    placed, e3det, err = placed_registry_arm(pl)
    if err:
        doc["error"] = err
        json.dump(doc, open(args.out, "w"), indent=1)
        print("REFUSED —", err, flush=True)
        return 6
    doc["placement"] = {k: pl[k] for k in ("meta_basin_id", "basin_id", "pose_id", "exact_atoms", "span_A",
                                           "anchor_e3_xyz")}
    doc["placement"]["_the_constraint"] = (
        "⛔ THERE IS NO NATIVE NR4A3 TERNARY, so DeepTernary's published 'superpose both binaries into the "
        "native frame' step has no reference. This RUNG-5a orientation basin supplies the arrangement "
        "instead, and every result downstream is conditional on it. It does not leak into the prediction — "
        "`predict_one_unbound` randomly rotates and translates protein 2 and the ligand — but it decides "
        "whether the two-fragment embed is feasible at all.")
    doc["e3_placement"] = e3det

    chain, lig, seldet, err = resolve_e3_binary(placed, args.workdir,
                                                (args.e3_binary,) if args.e3_binary else E3_BINARY_CANDIDATES)
    doc["e3_binary"] = seldet
    if err:
        doc["error"] = err
        json.dump(doc, open(args.out, "w"), indent=1)
        print("REFUSED —", err, flush=True)
        return 6

    basins = json.load(open(os.path.join(HERE, "nr4a3-orientation-basins.json")))
    anchor = next(q["anchor_xyz"] for q in basins["pose_ensemble"] if q["pose_id"] == pl["pose_id"])
    receptors = matched_receptors()
    sg = BS.atom_xyz(receptors["NR4A3"]["model"],
                     basins["target_frame"]["unique_cysteines"][0]["local_resid"], "SG")

    from rdkit import Chem
    wq = Chem.MolFromSmarts(WARHEAD_SMARTS)
    wmol = Chem.MolFromSmiles(WARHEAD_SMILES)
    warhead_elements = [wmol.GetAtomWithIdx(int(i)).GetSymbol() for i in wmol.GetSubstructMatch(wq)]

    ctx = {"receptors": receptors, "degrader_mol": deg, "roles": roles, "construct": c,
           "e3_chain": chain, "e3_ligand": lig, "e3_ligand_detail": seldet,
           "exitvec_anchor": anchor, "c397_sg": list(sg) if sg else None,
           "docked_dir": args.docked_dir or args.workdir, "warhead_elements": warhead_elements,
           "n_confs": args.n_confs, "seed": args.seed}
    doc["exitvec_anchor"] = anchor
    doc["c397_sg_xyz"] = ctx["c397_sg"]

    for p in PARALOGUES:
        r = build_arm(p, ctx, base, args.workdir)
        doc["arms"].append(r)
        print("  %-16s %s" % (r["arm"], "READY" if r["ok"] else "REFUSED — " + (r["why"] or "")), flush=True)

    ready = [r["arm"] for r in doc["arms"] if r["ok"]]
    doc["ready_arms"] = ready
    doc["refused_arms"] = [{"arm": r["arm"], "why": r["why"]} for r in doc["arms"] if not r["ok"]]
    doc["base"] = base
    doc["sentence"] = (
        "%d of %d paralogue arms passed the pre-flight and are built (%s)."
        % (len(ready), len(PARALOGUES), ", ".join(ready) or "none")
        + (" REFUSED: %s." % "; ".join("%s (%s)" % (r["arm"], r["why"]) for r in doc["refused_arms"])
           if doc["refused_arms"] else "")
        + " ⛔ A refusal is not a zero, and an arm that is not built is not a result of any magnitude.")
    json.dump(doc, open(args.out, "w"), indent=1)
    print(doc["sentence"], flush=True)
    # ⛔ ALL THREE OR NONE. A comparison missing an arm is not a comparison — the same rule
    # `nr4a_ternary_signature` already enforces, applied one stage earlier so nothing is predicted for a
    # panel that cannot be read.
    return 0 if len(ready) == len(PARALOGUES) else 6


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="RUNG 5b-T — assemble the three paralogue ternary inputs ($0).")
    ap.add_argument("--mode", required=True, choices=("plan", "dock-inputs", "build"),
                    help="plan: resolve every committed input and REFUSE loudly if one is missing (no "
                         "network, no smina, no model). dock-inputs: emit what smina needs. "
                         "build: the full assembly and its pre-flight.")
    ap.add_argument("--workdir", default="/tmp/nr4a3_5bt")
    ap.add_argument("--base", default=None, help="DeepTernary's output/protac22 directory")
    ap.add_argument("--docked-dir", default=None, help="directory holding docked_<paralogue>_warhead.sdf")
    ap.add_argument("--e3-binary", default=None, help="pin the E3 binary deposit id")
    ap.add_argument("--n-confs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260803)
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-5bt-frame.json"))
    args = ap.parse_args(argv)
    return {"plan": mode_plan, "dock-inputs": mode_dock_inputs, "build": mode_build}[args.mode](args)


if __name__ == "__main__":
    raise SystemExit(main())
