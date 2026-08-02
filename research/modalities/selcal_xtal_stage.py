#!/usr/bin/env python3
"""The sensitivity control, re-run on DEPOSITED CRYSTAL COPIES instead of co-folds. ($0 to stage)

★★ WHY THIS EXISTS, AND WHY IT IS THE ONE EXPERIMENT THE SELECTIVITY CLAIMS ACTUALLY NEED.
`selcal_panel` asked the only question that can license a paralogue-selectivity claim: *given a pair whose
selectivity is measured and whose structures are solved on BOTH arms, can this program's endpoint tell them
apart?* It returned NULL on an adequately-powered design — and the null was then found to be
uninterpretable, because the twelve structures it ran on reproduce the degradation-target<->VHL interface at
**DockQ 0.023-0.046, fnat 0.000**: they score like the correct complex displaced ~32 A
(`selcal-dockq-decoy-scale.json`). The endpoint was never put to the test the null is read as.

This module removes the generation stage entirely. **9DTY and 9DTX ARE the two complexes whose selectivity
was measured** — same degrader, one paralogue each, both deposited. Running the identical endpoint on the
crystals themselves asks the readout question in isolation, with no predicted coordinates anywhere in the
chain.

★ THE UNIT OF INDEPENDENCE IS THE CRYSTALLOGRAPHIC COPY, and that is what makes this a real design rather
than a pair of numbers. 9DTY holds ~10 independent copies of the ternary in its asymmetric unit. Each is a
separate realisation of the same complex in a different lattice environment, so copies supply genuine
structural variation the way co-fold seeds were supposed to — but from crystallography rather than from a
predictor. The panel's shape, statistic, direction, alpha and sampling protocol are IMPORTED from
`selcal_panel` unchanged; only the source of the coordinates differs.

⛔ WHAT A PASS AND A FAIL EACH LICENSE, WRITTEN BEFORE THE RUN.
  · **PASS** (SMARCA2 copies plateau LOWER than SMARCA4 copies, one-sided, p < alpha) — the endpoint
    discriminates a known paralogue difference on correct inputs. That is the positive control this program
    has never had, and it is the precondition for treating any NR4A3 ternary readout as evidence. It does
    NOT make any NR4A3 prediction correct; it makes the instrument usable.
  · **FAIL / NULL** — the endpoint cannot resolve a known, structurally-explained paralogue difference even
    when handed the deposited complexes. Then **no NR4A3 selectivity case can be justified with E1**, and the
    paper must say so in those words rather than continuing to call the predictions merely unvalidated.
Both outcomes are decision-relevant, which is why this is worth its (small) spend.

⚠ WHAT THIS STILL CANNOT DO. It tests the READOUT, not the workflow: a prospective NR4A3 campaign has no
crystal, so a pass here licenses the endpoint and says nothing about the generation stage that feeds it —
which is separately measured, and separately failing, at DockQ 0.023-0.046. Both must work for a prospective
claim; this establishes at most one of them.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: The two deposits, READ from the frozen panel rather than typed here.
def deposits():
    import selcal_panel as P
    return dict(P.REFERENCE["deposited_ternaries"])          # {"SMARCA2": "9DTY", "SMARCA4": "9DTX"}


#: Arm id -> gene, from the panel's own ARMS tuple. One home for the mapping.
def arm_genes():
    import selcal_panel as P
    return {a.arm_id: a.gene for a in P.ARMS}


#: A copy is usable only if its degrader is actually bridging BOTH proteins — the thing being measured. The
#: window is the same 5.0 A contact distance `selcal_cofold_validate.fnat` uses for a native contact, imported
#: rather than chosen, so "bridging" means here exactly what it means in every other measurement in this lane.
def bridging_cutoff_a():
    import selcal_cofold_validate as V
    return V.FNAT_CONTACT_A


# =============================================================================================================
# 1 · CENSUS — how many independent copies does each deposit actually supply?
# =============================================================================================================


def reference_sequences_from_deposit(cif_path, pdb_id):
    """(target_seq, [e3 seqs], detail, error) taken from the DEPOSIT'S OWN chains, via the committed map.

    ⛔ THIS REPLACES `selcal_stage.construct_sequence` + `e3_sequences` AS THE REFERENCE, and the first census
    is why: run 30757393618 reported **0 copies on both arms**, against the ~10 that every other measurement
    in this lane sees in 9DTY. Those two helpers return the CO-FOLD CONSTRUCT sequences — what the panel asked
    Boltz to fold — and a construct is not obliged to align to a crystal chain above the 0.80 identity floor
    once expression tags, unresolved termini and a different domain boundary are in play.

    `valb_frame_transfer_check.roles_from_selcal_artifact` already names ONE copy's chains in this very
    deposit, derived by sequence in the committed map every other number here uses. Reading those chains'
    sequences OUT OF THE CRYSTAL gives references that are by construction crystal-like, so the sibling copies
    are found by matching a deposit against itself. It also keeps the copy convention identical to the DockQ
    measurements, which is the point of using the committed map rather than a fresh derivation."""
    import selcal_cofold_validate as V
    import valb_frame_transfer_check as F
    roles, rerr = F.roles_from_selcal_artifact(pdb_id)
    if rerr:
        return None, None, None, "roles unresolved for %s: %s" % (pdb_id, rerr)
    atoms = V.parse_structure(cif_path)
    tseq, _ = V.chain_sequence(atoms, roles["target"])
    e3 = []
    for c in roles["e3"]:
        s, _ = V.chain_sequence(atoms, c)
        if not s:
            return None, None, None, "E3 chain %s of %s carries no polymer sequence" % (c, pdb_id)
        e3.append(s)
    if not tseq:
        return None, None, None, "target chain %s of %s carries no polymer sequence" % (roles["target"], pdb_id)
    detail = {"_source": "chain sequences read out of the deposit, at the chains the committed selcal map "
                         "names — never the co-fold construct, which does not have to align to a crystal "
                         "chain above the identity floor",
              "seed_copy": {"target": roles["target"], "e3": roles["e3"]},
              "lengths": {"target": len(tseq), "e3": [len(s) for s in e3]}}
    return tseq, e3, detail, None


def chain_identity_table(cif_path, target_seq, e3_seqs, floor=0.5):
    """Every polymer chain's identity to each reference, for chains above `floor`. A DIAGNOSTIC, not a gate.

    Published beside the census because "0 copies" and "0 chains matched the target" are different findings
    with opposite remedies, and the first census could not tell them apart."""
    import selcal_cofold_validate as V
    atoms = V.parse_structure(cif_path)
    refs = [("target", target_seq)] + [("e3_%d" % i, s) for i, s in enumerate(e3_seqs)]
    out = {}
    for ch in V.polymer_chains(atoms):
        seq, _ = V.chain_sequence(atoms, ch)
        best = {}
        for name, ref in refs:
            ident, _ = V.align_identity(seq, ref)
            if ident >= floor:
                best[name] = round(ident, 4)
        if best:
            out[ch] = best
    return {"n_polymer_chains": len(V.polymer_chains(atoms)), "identity_floor_shown": floor,
            "min_identity_required": V.MIN_CHAIN_IDENTITY, "chains": out}


def copy_census(cif_path, target_seq, e3_seqs, degrader_comp):
    """[{copy_id, target_chain, e3_chains, ligand_key, bridges, min_dist_target_A, min_dist_e3_A}, ...].

    Copies come from `selcal_cofold_validate.target_anchored_assemblies`, which is the enumerator this lane
    already uses and which carries its own chimera check and its own measured limit — reused rather than
    re-derived so a copy means the same thing here as in the DockQ measurements.

    ⚠ EACH COPY IS THEN CHECKED FOR ITS OWN DEGRADER, not assumed to have one. A deposit can resolve the
    protein of a copy and leave its ligand unmodelled at that site, and a copy staged without the bridging
    molecule would run an apo interface while reporting as a ternary leg — a plausible-looking record of a
    thing that never happened, which is the failure mode this repo keeps paying for."""
    import selcal_cofold_validate as V
    atoms = V.parse_structure(cif_path)
    assemblies = V.target_anchored_assemblies(atoms, target_seq, e3_seqs)
    tgt_chains = {c for _, c in V.chains_matching(atoms, target_seq)}

    ligs = {}
    for a in atoms:
        if a.resname.upper() == degrader_comp.upper() and a.is_heavy:
            ligs.setdefault(a.key, []).append(a)

    cut = bridging_cutoff_a()
    out = []
    for i, chains in enumerate(assemblies):
        target = next((c for c in chains if c in tgt_chains), None)
        if target is None:
            continue
        e3 = [c for c in chains if c != target]
        tat = [a for a in atoms if a.chain == target and not a.hetatm and a.is_heavy]
        e3at = [a for a in atoms if a.chain in e3 and not a.hetatm and a.is_heavy]
        best = None
        for key, lat in ligs.items():
            dt = _min_dist(lat, tat)
            de = _min_dist(lat, e3at)
            score = max(dt, de)
            if best is None or score < best[0]:
                best = (score, key, dt, de)
        row = {"copy_id": "c%02d" % (i + 1), "target_chain": target, "e3_chains": e3,
               "ligand_key": None, "bridges": False,
               "min_dist_target_A": None, "min_dist_e3_A": None}
        if best is not None:
            _, key, dt, de = best
            row.update(ligand_key=list(key), min_dist_target_A=round(dt, 2), min_dist_e3_A=round(de, 2),
                       bridges=bool(dt <= cut and de <= cut))
        out.append(row)
    return out


def _min_dist(a_atoms, b_atoms):
    import numpy as np
    if not a_atoms or not b_atoms:
        return float("inf")
    A = np.array([[a.x, a.y, a.z] for a in a_atoms], dtype=float)
    B = np.array([[b.x, b.y, b.z] for b in b_atoms], dtype=float)
    return float(np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(axis=2)).min())


def census_both_arms(native_dir, out_path=None):
    """Census every arm's deposit. Pure read; no staging, no network beyond what the caller already fetched."""
    import selcal_stage as S
    import selcal_panel as P

    dep, genes = deposits(), arm_genes()
    lig = S.ligand_smiles()
    doc = {"_what": "independent crystallographic copies per arm — the unit of independence for the "
                    "crystal re-run of the sensitivity control",
           "degrader_ccd": lig["ccd"], "bridging_cutoff_A": bridging_cutoff_a(), "arms": {}}
    for arm_id, gene in genes.items():
        pdb = dep[gene]
        path = os.path.join(native_dir, "%s.cif" % pdb)
        if not os.path.exists(path):
            path = os.path.join(native_dir, "%s.pdb" % pdb)
        rec = {"gene": gene, "pdb": pdb, "path": path}
        if not os.path.exists(path):
            rec["error"] = ("%s not found under %s — an UNREAD deposit, not a deposit with no copies"
                            % (pdb, native_dir))
            doc["arms"][arm_id] = rec
            continue
        tseq, e3, detail, serr = reference_sequences_from_deposit(path, pdb)
        rec["reference_sequences"] = detail or {"error": serr}
        if serr:
            rec["error"] = serr
            doc["arms"][arm_id] = rec
            continue
        # ⚠ Published whether or not copies are found: "no chain matched the target" and "chains matched but
        # no copy survived the chimera check" are different findings with opposite remedies, and the first
        # census could not tell them apart.
        rec["chain_identities"] = chain_identity_table(path, tseq, e3)
        rows = copy_census(path, tseq, e3, lig["ccd"])
        rec["copies"] = rows
        rec["n_copies"] = len(rows)
        rec["n_bridging"] = sum(1 for r in rows if r["bridges"])
        doc["arms"][arm_id] = rec

    usable = [a.get("n_bridging", 0) for a in doc["arms"].values()]
    doc["n_usable_per_arm"] = {k: v.get("n_bridging", 0) for k, v in doc["arms"].items()}
    doc["design"] = design_from_census(doc)
    return doc


def design_from_census(doc, replicas=None):
    """The realised design and its exact-permutation floor, DERIVED from what the deposits actually supply.

    ⛔ THE PERMUTATION IS OVER MODELS, NOT LEGS, and getting that wrong would overstate the power by orders
    of magnitude. The parent design collapses velocity replicas to model means before the test — a leg is not
    an independent draw of the thing being compared — so the reference set is C(n_a + n_b, n_a) over MODELS.
    Here a model is a crystallographic COPY. The arithmetic is `selcal_gate.design_floor`, imported and
    called with the copy counts rather than re-derived, so this cannot drift from the gate that scores it."""
    import selcal_gate as G
    replicas = len(__import__("selcal_panel").MD_REPLICAS) if replicas is None else replicas
    per_arm = doc.get("n_usable_per_arm") or {}
    if len(per_arm) != 2 or min(per_arm.values()) < 1:
        return {"ok": False, "why": "fewer than one usable copy on an arm — no design is available",
                "per_arm": per_arm}
    n = min(per_arm.values())                      # matched arms; the smaller deposit sets the shape
    floor = G.design_floor(n, n)
    # ⚠ "CAN REACH ALPHA" IS NOT "ADEQUATELY POWERED", and at 3 copies per arm the two come apart: the floor
    # is exactly 0.05, so ONLY the single most extreme arrangement of 20 could ever reject, and one tied or
    # mildly out-of-order copy makes the test unable to fire at all. The parent panel's own wording is
    # "comfortably clear of alpha"; this makes that executable rather than a matter of reading. 4 copies per
    # arm (C = 70, floor 0.0143) is the smallest shape that clears it by the order of magnitude the parent
    # design was chosen for.
    comfortable = floor["min_attainable_p"] <= floor["alpha"] / 3.0
    return {"ok": bool(comfortable), "comfortably_clears_alpha": bool(comfortable),
            "_comfortable_rule": "min attainable p <= alpha/3; `can_reach_alpha` alone is satisfied at a floor "
                                 "of exactly alpha, where only one arrangement of the reference set can ever "
                                 "reject and the design is knife-edge rather than powered",
            "copies_per_arm": n, "replicas": replicas,
            "legs_per_arm": n * replicas, "total_legs": 2 * n * replicas,
            "reference_set": floor["n_arrangements"], "min_attainable_p": floor["min_attainable_p"],
            "alpha": floor["alpha"], "can_reach_alpha": floor["can_reach_alpha"],
            "why": ("matched arms at the smaller deposit's usable-copy count. The unit of independence is the "
                    "crystallographic COPY; replicas collapse to copy means before the test, exactly as the "
                    "parent panel collapses replicas to model means."),
            "_arithmetic": "selcal_gate.design_floor(copies, copies) — imported, not re-derived",
            "_parent_shape": "selcal_panel: 6 co-fold models x 2 replicas, C(12,6)=924, floor 1/924"}


# =============================================================================================================
# 2 · STAGE — one MD unit per (arm, copy)
# =============================================================================================================


def extract_copy_ligand(cif_path, comp, target_chain, e3_chains, template_smiles, out_sdf):
    """(atom count, detail) for THIS copy's degrader only.

    ⛔ `nrv04_covalent_assemble.extract_ligand_from_cif` cannot be used unchanged here and the reason is
    arithmetic: it concatenates EVERY non-polymer heavy atom in the file. On a co-fold that is one degrader;
    on 9DTY it is ~10 degraders plus the zincs and the cryoprotectant, and the template match would fail on a
    count that means nothing. So the copy's own ligand is selected first — by the same rule the census used,
    the residue closest to BOTH this copy's proteins — and only then handed to the SAME posing kernel
    (`ligand_mol_from_coords`), so the SDF is produced by identical code to the co-fold path."""
    import gemmi
    from rdkit import Chem
    from nrv04_covalent_assemble import ligand_mol_from_coords

    st = gemmi.read_structure(cif_path)
    model = st[0]
    prot = {"target": [], "e3": []}
    cands = []
    for chain in model:
        for res in chain:
            info = gemmi.find_tabulated_residue(res.name)
            if bool(info) and (info.is_amino_acid() or info.is_nucleic_acid()):
                if chain.name == target_chain:
                    prot["target"] += [(a.pos.x, a.pos.y, a.pos.z) for a in res if a.element.name != "H"]
                elif chain.name in e3_chains:
                    prot["e3"] += [(a.pos.x, a.pos.y, a.pos.z) for a in res if a.element.name != "H"]
            elif res.name.upper() == comp.upper():
                ats = [(a.element.name, (a.pos.x, a.pos.y, a.pos.z)) for a in res if a.element.name != "H"]
                if ats:
                    cands.append((chain.name, res.seqid.num, ats))
    if not cands:
        return 0, "no %s residue in %s" % (comp, os.path.basename(cif_path))
    if not prot["target"] or not prot["e3"]:
        return 0, "copy %s/%s has no protein atoms to anchor the ligand choice" % (target_chain, e3_chains)

    import numpy as np
    T = np.array(prot["target"], dtype=float)
    E = np.array(prot["e3"], dtype=float)

    def _worst(ats):
        L = np.array([p for _, p in ats], dtype=float)
        dt = np.sqrt(((L[:, None, :] - T[None, :, :]) ** 2).sum(axis=2)).min()
        de = np.sqrt(((L[:, None, :] - E[None, :, :]) ** 2).sum(axis=2)).min()
        return max(dt, de), dt, de

    ch, num, ats = min(cands, key=lambda c: _worst(c[2])[0])
    worst, dt, de = _worst(ats)
    mol = ligand_mol_from_coords([e for e, _ in ats], [p for _, p in ats], template_smiles)
    w = Chem.SDWriter(out_sdf); w.write(mol); w.close()
    return len(ats), {"chain": ch, "resseq": num, "n_candidates": len(cands),
                      "min_dist_target_A": round(float(dt), 2), "min_dist_e3_A": round(float(de), 2)}


def stage_copy(cif_path, leg_id, target_chain, e3_chains, out_dir, ligand_key=None):
    """`<out_dir>/<leg_id>/{complex.pdb, ligand.sdf, chains.json}` for ONE crystallographic copy.

    The chain surgery and the ligand posing kernel are `nrv04_covalent_assemble`'s, the same ones
    `selcal_stage.assemble_unit` uses — which is the scientific content of the word `control` here: if this
    staged differently, a pass would be about THIS path and silent about the one the program ran."""
    from nrv04_covalent_assemble import write_complex_pdb
    import selcal_stage as S

    chains = [target_chain] + list(e3_chains)
    leg_out = os.path.join(out_dir, leg_id)
    os.makedirs(leg_out, exist_ok=True)
    complex_pdb = os.path.join(leg_out, "complex.pdb")
    write_complex_pdb(cif_path, sorted(chains), complex_pdb)
    lig = S.ligand_smiles()
    n_lig, lig_detail = extract_copy_ligand(cif_path, lig["ccd"], target_chain, list(e3_chains),
                                            lig["smiles"], os.path.join(leg_out, "ligand.sdf"))
    rec = {"leg": leg_id, "source": "DEPOSITED CRYSTAL COPY", "cif": os.path.basename(cif_path),
           "target_chain": target_chain, "e3_chains": list(e3_chains), "ligand_key": ligand_key,
           "ligand_atoms": n_lig, "ligand_detail": lig_detail, "out": leg_out}
    # ⛔ A UNIT WITH NO LIGAND IS NOT A TERNARY LEG. Refuse rather than stage an apo interface that would
    # report as one — the exact shape of the smoke-leg incident (STRATEGY Appendix A 57).
    if not n_lig:
        rec["error"] = ("no degrader atoms extracted for %s — this copy would run an apo interface while "
                        "recording as a ternary leg" % leg_id)
        return rec
    audit = S.cofold_input_audit(complex_pdb)
    rec["input_audit"] = audit
    with open(os.path.join(leg_out, "chains.json"), "w") as fh:
        json.dump({"target": target_chain, "e3": list(e3_chains),
                   "ligand": {k: lig[k] for k in ("ccd", "name", "smiles_program")},
                   "_source": "deposited crystal copy"}, fh, indent=2)
    return rec


def stage_all(census, native_dir, out_dir):
    """Stage every bridging copy of every arm. Returns [record, ...]; refusals are records, not omissions."""
    rows = []
    for arm_id, arm in sorted((census.get("arms") or {}).items()):
        if arm.get("error"):
            rows.append({"leg": arm_id, "error": arm["error"]})
            continue
        for c in arm.get("copies", []):
            if not c["bridges"]:
                rows.append({"leg": "%s__%s" % (arm_id, c["copy_id"]),
                             "error": ("degrader does not bridge in this copy (target %s A, E3 %s A against "
                                       "a %.1f A contact cutoff) — excluded as a MEASURED INPUT FAULT, "
                                       "before any outcome is known"
                                       % (c["min_dist_target_A"], c["min_dist_e3_A"],
                                          census["bridging_cutoff_A"]))})
                continue
            rows.append(stage_copy(arm["path"], "%s__%s" % (arm_id, c["copy_id"]),
                                   c["target_chain"], c["e3_chains"], out_dir, c.get("ligand_key")))
    return rows


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Census / stage the crystal re-run of the sensitivity control.")
    ap.add_argument("--native-dir", default="/tmp/selcal_cofolds/_native")
    ap.add_argument("--stage-to", default=None, help="also stage MD units into this directory")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-xtal-census.json"))
    args = ap.parse_args(argv)

    doc = census_both_arms(args.native_dir)
    if args.stage_to:
        doc["staged"] = stage_all(doc, args.native_dir, args.stage_to)
        doc["n_staged"] = sum(1 for r in doc["staged"] if not r.get("error"))
    json.dump(doc, open(args.out, "w"), indent=1)

    for arm_id, arm in sorted((doc.get("arms") or {}).items()):
        if arm.get("error"):
            print("  %-18s REFUSED — %s" % (arm_id, arm["error"]), flush=True)
            continue
        print("  %-18s %s: %d copies, %d with a bridging degrader"
              % (arm_id, arm["pdb"], arm["n_copies"], arm["n_bridging"]), flush=True)
    print("  design: %s" % json.dumps(doc.get("design")), flush=True)
    if "n_staged" in doc:
        print("  staged %d unit(s)" % doc["n_staged"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
