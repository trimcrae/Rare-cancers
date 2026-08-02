#!/usr/bin/env python3
"""Build DeepTernary's OWN unbound inputs for the selcal arms — the protocol, read off its shipped data.

★★ WHAT THIS REPLACES, AND WHY THE PREVIOUS READING WAS WRONG. Two CI runs (30753431082, 30754028742) died
inside the forward pass at

    predict_cpu.replace_to_unbound_coords ->  assert cdist.min(dim=1)[0][update_mask].max() < 1
    RuntimeError: max(): Expected reduction dim to be specified for input.numel() == 0

`update_mask = cdist.min(dim=1)[0] < 1` selects the degrader atoms lying within 1 Å of a supplied fragment
atom. Our `ligand.pdb` was the **CCD ideal conformer** in an arbitrary frame, so no degrader atom was near
any fragment atom, the mask was empty, and the reduction over it died. The empty tensor was never a bug in
the model — it was the model correctly reporting that nothing had been positioned.

The next guess was a constrained embed (pin the warhead onto `unbound_lig1`, the anchor onto `unbound_lig2`).
**DeepTernary's own released data refutes that guess**, which is why it is recorded here rather than tried:
`output.zip` ships the complete unbound inputs for all 22 benchmark cases, and in `6HAX_B_A_FWZ` —

  · `ligand.pdb` is byte-identical to the FWZ ligand of `gt_complex.pdb`: **max deviation 0.000 Å across all
    66 heavy atoms**. It is the NATIVE pose, not a generated conformer.
  · `unbound_protein1.pdb` is a different entry (chain I, 1150 atoms vs the native's 1201) yet sits at
    centroid (−21.6, 17.3, −20.3) against the native POI's (−21.3, 17.6, −20.7); `unbound_protein2.pdb`
    matches the native E3 the same way. Both have been **superposed into the native ternary frame**.
  · 33 of the 66 ligand atoms then fall within 1 Å of `unbound_lig1`, and 18 within 1 Å of `unbound_lig2` —
    exactly the two masks the assertion needs.

So the published UNBOUND protocol is: superpose each unbound binary into the native ternary frame, and hand
the model the native degrader pose. This module does that, from the same deposited references and the same
sequence-derived chain roles every other measurement in this lane uses.

⛔ THEREFORE THIS ARM IS NOT BLIND TO WHERE THE TWO LIGAND ENDS SIT, AND MUST NEVER BE WRITTEN UP AS IF IT
WERE. What the model is still genuinely asked for is the RELATIVE PLACEMENT OF THE TWO PROTEINS:
`predict_one_unbound` applies an independent random rotation+translation to protein 2 and to the ligand
before the forward pass, so the native arrangement is destroyed in the input and the architecture is an
output. `gt_complex.pdb` is read at exactly one place in that file — `cal_dockq(...)` — and never reaches
the model. What the model IS given is which pocket on each protein the ligand occupies. That is a **weaker
question** than our Boltz co-folds were asked (sequence + ligand, nothing else), and the two numbers must
never be set side by side as though they were the same test.

★ THE SUPERPOSITION IS ALSO A MEASUREMENT, NOT JUST PLUMBING. Transferring the warhead's pose from a binary
co-crystal into the ternary frame only works if the warhead binds the same way in both. This module reports
how many degrader atoms each transferred fragment lands within 1 Å of, and REFUSES the arm when either count
is zero — which is the honest outcome for a fragment whose binary pose does not transfer, not a reason to
loosen a threshold.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: Chain-level sequence identity required to call an unbound chain "the same protein as" a native chain.
#: Same bar as `selcal_cofold_validate.MIN_CHAIN_IDENTITY`, imported rather than retyped so the two cannot
#: drift apart; a paralogue pair at ~0.80 is precisely the confusion this lane exists to avoid.
def _min_identity():
    import selcal_cofold_validate as V
    return V.MIN_CHAIN_IDENTITY


#: Cα RMSD, in Å, above which a superposition is refused. An unbound binary of the same protein superposes
#: on its ternary counterpart at well under 2 Å; anything above this is a different protein, a different
#: domain, or a mis-mapped chain, and carrying it forward would silently place the fragment in open solvent.
MAX_SUPERPOSITION_RMSD_A = 5.0

#: The proximity window `replace_to_unbound_coords` uses, in Å. Read from its source, not chosen here:
#: `update_mask = cdist.min(dim=1)[0] < 1`.
SNAP_WINDOW_A = 1.0


# ---------- geometry --------------------------------------------------------------------------------------


def kabsch(mobile, target):
    """(R, t) minimising |R·mobile + t − target|, both (N,3) array-likes. Standard Kabsch with a reflection fix."""
    import numpy as np
    P = np.asarray(mobile, dtype=float)
    Q = np.asarray(target, dtype=float)
    pc, qc = P.mean(axis=0), Q.mean(axis=0)
    H = (P - pc).T @ (Q - qc)
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1.0, 1.0, d])
    R = Vt.T @ D @ U.T
    return R, qc - R @ pc


def copy_atom(a, **kw):
    """A new `selcal_cofold_validate.Atom` with selected fields replaced.

    `Atom` is a `__slots__` class, not a namedtuple, so there is no `_replace`; writing one here keeps this
    module from mutating structures another module parsed and may still be holding."""
    import selcal_cofold_validate as V
    f = {"chain": a.chain, "resseq": a.resseq, "icode": a.icode, "resname": a.resname, "name": a.name,
         "element": a.element, "x": a.x, "y": a.y, "z": a.z, "hetatm": a.hetatm}
    f.update(kw)
    return V.Atom(**f)


def apply_rt(atoms, R, t):
    """New Atom list with coordinates transformed. The originals are left untouched."""
    import numpy as np
    out = []
    for a in atoms:
        x, y, z = np.asarray(R @ np.array([a.x, a.y, a.z]) + t, dtype=float)
        out.append(copy_atom(a, x=float(x), y=float(y), z=float(z)))
    return out


def transform_pdb_coordinates(src, dest, R, t):
    """Copy a PDB byte-for-byte except the x/y/z columns, which are rigidly transformed.

    ★ WHY NOT JUST RE-WRITE IT. The unbound fragment files reaching this module were already checked
    RDKit-readable by the step before, and re-emitting them threw that away: the first attempt rebuilt them
    with `write_pdb` plus CCD-sourced CONECT records and `get_lig_coords` got `None` back —
        [rdkit] Explicit valence for atom # 7 C, 6, is greater than permitted
    because `MolFromPDBFile` bonds a real conformer BY PROXIMITY as well as by CONECT, and re-declaring a
    bond it had already inferred raises the bond order instead of being a no-op. Reproduced offline on
    DeepTernary's own `6HAX_B_A_FWZ/unbound_lig1.pdb`: readable as shipped (0 CONECT), readable through
    `write_pdb` with no CONECT, unreadable once CONECT is added. So a file that is already correct is
    MOVED, never rebuilt — a rigid transform cannot change any distance, so readability is preserved by
    construction."""
    import numpy as np
    n = 0
    with open(src) as fh, open(dest, "w") as out:
        for line in fh:
            if line.startswith(("ATOM  ", "HETATM")) and len(line) >= 54:
                x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                nx, ny, nz = np.asarray(R @ np.array([x, y, z]) + t, dtype=float)
                out.write("%s%8.3f%8.3f%8.3f%s" % (line[:30], nx, ny, nz, line[54:]))
                n += 1
            else:
                out.write(line)
    return n


def rdkit_readable(path):
    """(True, None) | (False, why). A ligand file the model cannot read is a refusal here, not a crash there."""
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        RDLogger.DisableLog("rdApp.*")
        m = Chem.MolFromPDBFile(path, removeHs=False, sanitize=True)
    except Exception as e:                                   # noqa: BLE001
        return False, "RDKit raised on %s: %s" % (os.path.basename(path), e)
    if m is None:
        return False, ("RDKit cannot sanitize %s — `get_lig_coords` would call .GetConformer() on None"
                       % os.path.basename(path))
    return True, None


def rmsd(a, b):
    import numpy as np
    A, B = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.sqrt(((A - B) ** 2).sum(axis=1).mean()))


def min_dist_counts(probe, reference, window=SNAP_WINDOW_A):
    """How many `probe` atoms lie within `window` of any `reference` atom — the mask the model builds."""
    import numpy as np
    if not probe or not reference:
        return 0, None
    P = np.array([[a.x, a.y, a.z] for a in probe], dtype=float)
    Q = np.array([[a.x, a.y, a.z] for a in reference], dtype=float)
    d = np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return int((d < window).sum()), round(float(d.min()), 3)


# ---------- native decomposition --------------------------------------------------------------------------


def native_copy(native_atoms, roles, degrader_comp):
    """(target chain atoms, E3 chain atoms, degrader atoms, error) for ONE copy of a multi-copy deposit.

    The chain ids come from `valb_frame_transfer_check.roles_from_selcal_artifact`, i.e. from the committed
    sequence-derived map that every other measurement in this lane already uses — 9DTY holds ~10 copies and
    picking a different one here would make the numbers incomparable for no gain. The degrader copy is then
    chosen as the one closest to THOSE two chains, because a deposit carries one degrader per copy and the
    nearest is the one bound in this copy."""
    tgt = [a for a in native_atoms if a.chain == roles["target"] and not a.hetatm and a.is_heavy]
    e3 = [a for a in native_atoms if a.chain == roles["e3"][0] and not a.hetatm and a.is_heavy]
    if not tgt:
        return None, None, None, "no polymer atoms on native target chain %s" % roles["target"]
    if not e3:
        return None, None, None, "no polymer atoms on native E3 chain %s" % roles["e3"][0]

    groups = {}
    for a in native_atoms:
        if a.resname.upper() != degrader_comp.upper() or not a.is_heavy:
            continue
        groups.setdefault(a.key, []).append(a)
    if not groups:
        return None, None, None, ("no %s residue in the deposit — the degrader cannot be located, and a "
                                  "substitute molecule would answer a different question" % degrader_comp)

    import numpy as np
    T = np.array([[a.x, a.y, a.z] for a in tgt])
    E = np.array([[a.x, a.y, a.z] for a in e3])
    best, best_score = None, None
    for key, ats in groups.items():
        L = np.array([[a.x, a.y, a.z] for a in ats])
        dt = np.sqrt(((L[:, None, :] - T[None, :, :]) ** 2).sum(axis=2)).min()
        de = np.sqrt(((L[:, None, :] - E[None, :, :]) ** 2).sum(axis=2)).min()
        score = max(dt, de)                       # the copy that is close to BOTH, not just to one
        if best_score is None or score < best_score:
            best, best_score = ats, score
    return tgt, e3, best, None


# ---------- superposition ---------------------------------------------------------------------------------


def superpose_onto(unbound_atoms, native_chain_atoms, label):
    """(R, t, detail, error) placing an unbound structure into the native frame by sequence-matched Cα.

    Matching is by SEQUENCE, never by chain letter: the unbound entry is a different deposit with its own
    lettering, and the identity floor is what stops a paralogue or a second copy being superposed instead."""
    import selcal_cofold_validate as V
    native_chain = native_chain_atoms[0].chain
    nseq, _ = V.chain_sequence(native_chain_atoms, native_chain)
    best = None
    for ch in V.polymer_chains(unbound_atoms):
        useq, _ = V.chain_sequence(unbound_atoms, ch)
        ident, pairs = V.align_identity(useq, nseq)
        if best is None or ident > best[1]:
            best = (ch, ident, pairs)
    if best is None:
        return None, None, None, "%s: the unbound file has no polymer chain to superpose" % label
    ch, ident, pairs = best
    if ident < _min_identity():
        return None, None, None, ("%s: best unbound chain %s matches the native chain at identity %.3f, "
                                  "below %.2f — that is a different protein, and superposing it would put "
                                  "the fragment in open solvent" % (label, ch, ident, _min_identity()))

    uca = V._ca_by_residue([a for a in unbound_atoms if a.chain == ch])
    nca = V._ca_by_residue(native_chain_atoms)
    ukeys = V.chain_sequence(unbound_atoms, ch)[1]
    nkeys = V.chain_sequence(native_chain_atoms, native_chain)[1]
    P, Q = [], []
    for ia, ib in pairs:
        if ia < len(ukeys) and ib < len(nkeys):
            ka, kb = ukeys[ia], nkeys[ib]
            if ka in uca and kb in nca:
                P.append(uca[ka]); Q.append(nca[kb])
    if len(P) < V.MIN_ALIGNED_RESIDUES:
        return None, None, None, ("%s: only %d Cα pairs survived the alignment, below %d — too few to define "
                                  "a frame" % (label, len(P), V.MIN_ALIGNED_RESIDUES))
    R, t = kabsch(P, Q)
    import numpy as np
    moved = [(R @ np.array(p) + t) for p in P]
    r = rmsd(moved, Q)
    detail = {"unbound_chain": ch, "native_chain": native_chain, "identity": round(ident, 4),
              "n_ca_pairs": len(P), "ca_rmsd_A": round(r, 3)}
    if r > MAX_SUPERPOSITION_RMSD_A:
        return None, None, detail, ("%s: superposition Cα RMSD %.2f Å exceeds %.1f Å — the two structures are "
                                    "not the same fold in the same conformation"
                                    % (label, r, MAX_SUPERPOSITION_RMSD_A))
    return R, t, detail, None


# ---------- one arm ---------------------------------------------------------------------------------------


def prepare_arm(cfg, base, native_dir, workdir, ideal_dir=None):
    """Write the eight files `predict_one_unbound` reads for one arm. Returns a status row."""
    import selcal_cofold_validate as V
    import selcal_deepternary_run as RUN
    import valb_frame_transfer_check as F

    name = cfg["name"]
    d = os.path.join(base, name)
    row = {"arm": name, "ok": True, "why": None, "native_pdb": cfg["native_pdb"],
           "degrader_comp": cfg["degrader_comp"], "detail": {}}

    native_path = os.path.join(native_dir, "%s.cif" % cfg["native_pdb"])
    if not os.path.exists(native_path):
        native_path = os.path.join(native_dir, "%s.pdb" % cfg["native_pdb"])
    if not os.path.exists(native_path):
        row.update(ok=False, why="native %s not found under %s" % (cfg["native_pdb"], native_dir))
        return row
    native_atoms = V.parse_structure(native_path)

    roles, rerr = F.roles_from_selcal_artifact(cfg["native_pdb"])
    if rerr:
        row.update(ok=False, why="native chain roles unresolved: %s" % rerr)
        return row
    row["detail"]["native_roles"] = roles

    tgt, e3, deg, err = native_copy(native_atoms, roles, cfg["degrader_comp"])
    if err:
        row.update(ok=False, why=err)
        return row
    row["detail"]["native_atom_counts"] = {"target": len(tgt), "e3": len(e3), "degrader": len(deg)}

    # The two unbound structures the blind prep already extracted, superposed into this native copy's frame.
    moved = {}
    for tag, fname, native_chain_atoms in (("p1", "unbound_protein1.pdb", tgt),
                                           ("p2", "unbound_protein2.pdb", e3)):
        p = os.path.join(d, fname)
        if not os.path.exists(p):
            row.update(ok=False, why="%s absent — the blind prep did not write it" % fname)
            return row
        ua = V.parse_structure(p)
        R, t, detail, serr = superpose_onto(ua, native_chain_atoms, tag)
        row["detail"]["superpose_%s" % tag] = detail
        if serr:
            row.update(ok=False, why=serr)
            return row
        lig_name = "unbound_lig%s.pdb" % tag[-1]
        lp = os.path.join(d, lig_name)
        if not os.path.exists(lp):
            row.update(ok=False, why="%s absent — the blind prep did not write it" % lig_name)
            return row
        moved[tag] = {"protein": apply_rt(ua, R, t), "lig": apply_rt(V.parse_structure(lp), R, t),
                      "protein_file": p, "lig_file": lp, "R": R, "t": t}

    # ★ THE MEASUREMENT. A transferred fragment is only usable if the warhead binds the binary and the ternary
    # the same way; the model's own 1 Å window is the test, so use it rather than inventing one.
    for tag, which in (("p1", "warhead"), ("p2", "anchor")):
        n_snap, closest = min_dist_counts(deg, [a for a in moved[tag]["lig"] if a.is_heavy])
        row["detail"]["snap_%s_%s" % (tag, which)] = {"n_degrader_atoms_within_1A": n_snap,
                                                      "closest_approach_A": closest}
        if n_snap == 0:
            row.update(ok=False, why=(
                "after superposing the %s binary onto the native frame, NO degrader atom lies within %.1f Å "
                "of the transferred %s fragment (closest approach %s Å). `replace_to_unbound_coords` would "
                "build an empty mask and die exactly as before. That is a real negative result about pose "
                "transfer for this fragment, not a threshold to relax."
                % (tag, SNAP_WINDOW_A, which, closest)))
            return row

    # ---- write the files predict_one_unbound reads ----
    #
    # ⚠ NO CONECT RECORDS ANYWHERE HERE, and that is the fix rather than an omission. See
    # `transform_pdb_coordinates` for the measured reason: RDKit bonds a real conformer by PROXIMITY as
    # well as by CONECT, so re-declaring a bond it already inferred raises the bond order and the molecule
    # fails sanitization. The four unbound files are MOVED in place, not rebuilt, so they keep exactly the
    # bytes the readability check upstream passed; the four native-derived files are written fresh, without
    # CONECT, and then verified.
    def _chain(atoms, ch):
        return [copy_atom(a, chain=ch) for a in atoms]

    n_p1, _ = RUN.write_pdb(_chain(tgt, "A"), os.path.join(d, "protein1.pdb"))
    n_p2, _ = RUN.write_pdb(_chain(e3, "B"), os.path.join(d, "protein2.pdb"))
    n_gt, _ = RUN.write_pdb(_chain(tgt, "A") + _chain(e3, "B") + _chain(deg, "A"),
                            os.path.join(d, "gt_complex.pdb"))
    n_lig, lig_alias = RUN.write_pdb(_chain(deg, "A"), os.path.join(d, "ligand.pdb"))
    moved_counts = {}
    for tag, fname in (("p1", "unbound_protein1.pdb"), ("p2", "unbound_protein2.pdb"),
                       ("p1", "unbound_lig1.pdb"), ("p2", "unbound_lig2.pdb")):
        key = "protein_file" if "protein" in fname else "lig_file"
        src = moved[tag][key]
        moved_counts[fname] = transform_pdb_coordinates(src, os.path.join(d, fname),
                                                        moved[tag]["R"], moved[tag]["t"])
    row["detail"]["written"] = {"protein1": n_p1, "protein2": n_p2, "gt_complex": n_gt, "ligand": n_lig,
                                "ligand_resname_alias": lig_alias.get(cfg["degrader_comp"].upper())
                                or lig_alias.get(cfg["degrader_comp"]),
                                "moved_in_place": moved_counts}

    # ★ THE MODEL READS THREE OF THESE WITH RDKit. Check here, where a failure is a legible refusal, rather
    # than five minutes later inside the forward pass as `'NoneType' object has no attribute 'GetConformer'`.
    unreadable = []
    for fname in ("ligand.pdb", "unbound_lig1.pdb", "unbound_lig2.pdb"):
        ok, why = rdkit_readable(os.path.join(d, fname))
        row["detail"].setdefault("rdkit_readable", {})[fname] = True if ok else why
        if not ok:
            unreadable.append(why)
    if unreadable:
        row.update(ok=False, why="; ".join(unreadable))
        return row

    # `ligand.sdf` is not read by predict_one_unbound (it reads ligand.pdb) but the blind prep's contract
    # check tests for it; leave whatever is there rather than deleting a file another module owns.
    #
    # ⚠ `predict_one_unbound` calls `auto_download_ideal_sdf(name.split('_')[-1])` EAGERLY, so an arm whose
    # name does not end in a CCD id fetches a 404 body and stores it under that key. It is only READ when
    # RDKit's own conformer generation fails, but when that happens the failure would be a confusing
    # `ideal_mol is None`. Pre-seed the key this arm will look up with the REAL degrader ideal SDF.
    ideal_dir = ideal_dir or os.path.join("data", "TernaryDB", "ligand_ideal")
    try:
        os.makedirs(ideal_dir, exist_ok=True)
        src = os.path.join(workdir, "%s_ideal.sdf" % cfg["degrader_comp"])
        if not os.path.exists(src):
            RUN._fetch(RUN.RCSB_IDEAL.format(c=cfg["degrader_comp"]), src)
        if os.path.exists(src):
            import shutil
            dest = os.path.join(ideal_dir, "%s_ideal.sdf" % name.split("_")[-1])
            shutil.copyfile(src, dest)
            row["detail"]["ideal_sdf_seeded"] = dest
    except Exception as e:                                   # noqa: BLE001
        row["detail"]["ideal_sdf_seeded"] = "failed: %s" % e

    return row


def reproduce_reference(ref_dir, target_chain="A", e3_chain="B", degrader_comp="FWZ"):
    """Does this builder reproduce DeepTernary's OWN unbound construction, on DeepTernary's OWN data?

    ★ THE CHECK THAT MAKES THE BUILDER TRUSTWORTHY, and it needs no pinned constant. `output.zip` ships the
    finished unbound inputs for `6HAX_B_A_FWZ`. Measure the two snap masks AS SHIPPED; then throw the shipped
    superposition away — displace each unbound structure by a large arbitrary rigid motion, re-derive the
    frame with `superpose_onto`, and measure the masks again. If this module's superposition is the same one
    the authors performed, the two counts are IDENTICAL. Nothing is compared against a number typed here, so
    the test cannot pass by having been tuned to a remembered figure.

    Returns a dict; `ok` is False if any count differs or the reference is unreadable."""
    import numpy as np
    import selcal_cofold_validate as V

    out = {"reference": ref_dir, "ok": True, "why": None, "arms": {}}
    try:
        native = V.parse_structure(os.path.join(ref_dir, "gt_complex.pdb"))
    except Exception as e:                                   # noqa: BLE001
        return {"reference": ref_dir, "ok": False, "why": "reference unreadable: %s" % e, "arms": {}}
    tgt, e3, deg, err = native_copy(native, {"target": target_chain, "e3": [e3_chain]}, degrader_comp)
    if err:
        return {"reference": ref_dir, "ok": False, "why": err, "arms": {}}

    theta = 1.1
    Rp = np.array([[np.cos(theta), -np.sin(theta), 0.0],
                   [np.sin(theta), np.cos(theta), 0.0], [0.0, 0.0, 1.0]])
    tp = np.array([37.0, -11.0, 5.0])
    for tag, protf, ligf, nat in (("p1", "unbound_protein1.pdb", "unbound_lig1.pdb", tgt),
                                  ("p2", "unbound_protein2.pdb", "unbound_lig2.pdb", e3)):
        rec = {}
        try:
            ua = V.parse_structure(os.path.join(ref_dir, protf))
            la = V.parse_structure(os.path.join(ref_dir, ligf))
        except Exception as e:                               # noqa: BLE001
            out.update(ok=False, why="%s unreadable: %s" % (protf, e))
            out["arms"][tag] = {"error": str(e)}
            continue
        rec["as_shipped"], rec["as_shipped_closest_A"] = min_dist_counts(deg, [a for a in la if a.is_heavy])
        R, t, detail, serr = superpose_onto(apply_rt(ua, Rp, tp), nat, tag)
        if serr:
            rec["error"] = serr
            out.update(ok=False, why=serr)
            out["arms"][tag] = rec
            continue
        moved = apply_rt(apply_rt(la, Rp, tp), R, t)
        rec["after_our_superposition"], rec["after_closest_A"] = \
            min_dist_counts(deg, [a for a in moved if a.is_heavy])
        rec["superposition"] = detail
        rec["agrees"] = (rec["as_shipped"] == rec["after_our_superposition"])
        if not rec["agrees"]:
            out.update(ok=False, why=("%s: this builder's superposition gives %d snap atoms where the shipped "
                                      "construction gives %d — it is not reproducing the published protocol"
                                      % (tag, rec["after_our_superposition"], rec["as_shipped"])))
        out["arms"][tag] = rec
    out["sentence"] = (
        "Builder reproduces DeepTernary's own unbound construction on %s: %s."
        % (os.path.basename(ref_dir.rstrip("/")),
           ", ".join("%s %s->%s" % (k, v.get("as_shipped"), v.get("after_our_superposition"))
                     for k, v in out["arms"].items()))
        if out["ok"] else "Builder does NOT reproduce the published construction: %s" % out["why"])
    return out


def run(configs, base, native_dir, workdir, ideal_dir=None):
    os.makedirs(workdir, exist_ok=True)
    return [prepare_arm(c, base, native_dir, workdir, ideal_dir) for c in configs]


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Build DeepTernary's own unbound inputs for the selcal arms.")
    ap.add_argument("--configs", default=None)
    ap.add_argument("--base", default="output/protac22")
    ap.add_argument("--native-dir", default="/tmp/selcal_dt")
    ap.add_argument("--workdir", default="/tmp/selcal_dt")
    ap.add_argument("--ideal-dir", default=None)
    ap.add_argument("--reproduce-reference", default=None,
                    help="a DeepTernary benchmark input dir (e.g. output/protac22/6HAX_B_A_FWZ); check this "
                         "builder reproduces the shipped construction, then exit")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-deepternary-frame.json"))
    args = ap.parse_args(argv)

    if args.reproduce_reference:
        rep = reproduce_reference(args.reproduce_reference)
        print(json.dumps(rep, indent=1), flush=True)
        return 0 if rep["ok"] else 7

    if not args.configs:
        ap.error("--configs is required unless --reproduce-reference is given")
    cfgs = json.load(open(args.configs))
    cfgs = cfgs["configs"] if isinstance(cfgs, dict) else cfgs
    rows = run(cfgs, args.base, args.native_dir, args.workdir, args.ideal_dir)
    json.dump(rows, open(args.out, "w"), indent=1)
    for r in rows:
        print("  %-18s %s" % (r["arm"], "READY" if r["ok"] else "REFUSED — " + (r["why"] or "")), flush=True)
        print("     %s" % json.dumps(r["detail"])[:600], flush=True)
    return 0 if any(r["ok"] for r in rows) else 6


if __name__ == "__main__":
    raise SystemExit(main())
