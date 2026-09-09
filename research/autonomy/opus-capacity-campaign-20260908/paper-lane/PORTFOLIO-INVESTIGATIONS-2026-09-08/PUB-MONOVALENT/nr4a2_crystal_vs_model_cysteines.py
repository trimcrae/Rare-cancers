#!/usr/bin/env python3
"""Does the MODELLED NR4A2 competitor-cysteine geometry reproduce in EXPERIMENTAL NR4A2 LBD structures?

WHY. The covalent axis of the monovalent/bivalent reach lane grades NR4A3 C397 against paralogue
competitor cysteines. Those competitor readings come from ONE modelled, pocket-opened NR4A2 structure
(results/nr4a3-matrix/nr4a2-opened.pdb). The owning artifact
research/modalities/nr4a3-covalent-handle-ensemble.json records verbatim:
  "There is no experimental NR4A1 or NR4A2 LBD ensemble in this repo".
That statement is FALSE AT THIS HEAD for NR4A2: two independent experimental NR4A2 (Nurr1) LBD crystal
structures are committed under research/modalities/_s4_lane_inputs/ (1OVL, 6 protein chains; 7WNH,
4 protein chains + DNA), and both resolve all five NR4A2 LBD cysteines including Cys534 -- the residue the
bivalent corridor tally names as the first-arriving closer in 34 of 60 cells.

WHAT THIS IS. A single-protein, single-measurement model-vs-experiment fidelity check on NR4A2 only.
It is NOT a validation of the opened pocket state, NOT a cross-paralogue claim, and NOT evidence about
NR4A3 C397. 1OVL/7WNH are COLLAPSED APO crystals; nr4a2-opened.pdb is biased open along a pocket CV, so a
systematic burial difference at pocket-lining positions is EXPECTED and is not a refutation of the model.
The load-bearing readout is therefore the RANK ORDER of the five cysteines by thiol exposure, plus the
per-residue experimental spread that the single modelled reading currently has no error bar against.

METHOD. Heavy-atom-only Shrake-Rupley (repo implementation, research/modalities/nr4a_differential_atlas.py
via nr4a3_covalent_handle_ensemble.atom_sasa, 96 sphere points for residue SASA and 960 for the single SG
atom -- the same conventions as the committed artifact). Crystals carry no hydrogens, so BOTH sides are
recomputed heavy-only from coordinates by ONE code path; the committed JSON's all-atom columns are never
compared against a crystal. Author numbering is never assumed: every chain is mapped to UniProt P43354 by
the repo's own global alignment (pdb_to_uniprot_map, identity >= 0.9 enforced).

$0. Pure CPU, pure stdlib + the repo's modules, no network, no GPU. Offline UniProt sequences come from the
committed research/modalities/nr4a-sequences-cache.json.
"""
import gzip
import json
import os
import statistics
import sys

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research/modalities")
sys.path.insert(0, MOD)

import nr4a_differential_atlas as atlas          # noqa: E402
import nr4a3_covalent_handle_ensemble as che     # noqa: E402

NR4A2_ACC = "P43354"
NR4A2_LBD_CYS = [465, 475, 505, 534, 566]
MODEL_PATH = os.path.join(REPO, "results/nr4a3-matrix/nr4a2-opened.pdb")
MODEL_UNIPROT_RANGE = (344, 598)          # from the committed artifact's opened_models.NR4A2
CRYSTALS = {
    "1OVL": os.path.join(MOD, "_s4_lane_inputs/1OVL.pdb.gz"),
    "7WNH": os.path.join(MOD, "_s4_lane_inputs/7WNH.pdb.gz"),
}
SEQ_CACHE = os.path.join(MOD, "nr4a-sequences-cache.json")
ARTIFACT = os.path.join(MOD, "nr4a3-covalent-handle-ensemble.json")


def read_text(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rt") as fh:
            return fh.read()
    with open(path) as fh:
        return fh.read()


def parse_chain(text, chain, first_model_only=True, heavy_only=True):
    """(residues, atoms) for ONE chain, in the dict shape atlas/che expect. Skips altloc B+, HETATM,
    non-standard residues and (by default) hydrogens. Chain-aware, unlike atlas.parse_pdb."""
    residues, order, atoms = {}, [], []
    for ln in text.splitlines():
        if first_model_only and ln.startswith("ENDMDL"):
            break
        if not ln.startswith("ATOM"):
            continue
        if ln[21] != chain:
            continue
        if ln[16] not in (" ", "A"):
            continue
        resn = ln[17:20].strip()
        if resn not in atlas.THREE2ONE:
            continue
        name = ln[12:16].strip()
        elem = (ln[76:78].strip() or name[0]).upper()
        if heavy_only and elem == "H":
            continue
        if ln[26] != " ":            # insertion codes: none expected here, refuse rather than mis-number
            raise ValueError(f"insertion code at {ln[22:27]!r} in chain {chain}")
        rid = int(ln[22:26])
        atoms.append({"resid": rid, "resname": resn, "name": name, "elem": elem,
                      "x": float(ln[30:38]), "y": float(ln[38:46]), "z": float(ln[46:54])})
        if rid not in residues:
            residues[rid] = atlas.THREE2ONE[resn]
            order.append(rid)
    return [(r, residues[r]) for r in order], atoms


def protein_chains(text):
    out = []
    for ln in text.splitlines():
        if ln.startswith("ENDMDL"):
            break
        if ln.startswith("ATOM") and ln[17:20].strip() in atlas.THREE2ONE:
            if ln[21] not in out:
                out.append(ln[21])
    return out


def measure(residues, atoms, uni_map, targets):
    """Heavy-atom-only residue SASA, SG SASA and isolated-SG SASA for each UniProt target residue."""
    rev = {}
    for pdb_res, uni in uni_map.items():
        rev[uni] = pdb_res
    idx_by_res = {}
    for i, a in enumerate(atoms):
        idx_by_res.setdefault(a["resid"], []).append(i)
    out = {}
    for uni in targets:
        pdb_res = rev.get(uni)
        if pdb_res is None:
            out[uni] = {"present": False, "why": "position not modelled/resolved in this chain"}
            continue
        idxs = idx_by_res[pdb_res]
        resname = atoms[idxs[0]]["resname"]
        sg = [i for i in idxs if atoms[i]["name"] == "SG"]
        res_sasa = sum(che.atom_sasa(atoms, idxs, n_points=96).values())
        rec = {"present": True, "pdb_resnum": pdb_res, "resname": resname,
               "residue_sasa_heavy_A2": round(res_sasa, 2)}
        one = atlas.THREE2ONE.get(resname)
        maxasa = atlas.MAXASA.get(one)
        rec["rsa_heavy"] = round(res_sasa / maxasa, 4) if maxasa else None
        if resname != "CYS" or not sg:
            rec["sg_present"] = False
            out[uni] = rec
            continue
        i = sg[0]
        rec["sg_present"] = True
        rec["sg_sasa_heavy_A2"] = round(che.atom_sasa(atoms, [i], n_points=960)[i], 2)
        iso_atoms = [atoms[j] for j in idxs]
        iso_i = idxs.index(i)
        rec["sg_sasa_isolated_A2"] = round(che.atom_sasa(iso_atoms, [iso_i], n_points=960)[iso_i], 2)
        rec["sg_rel"] = round(rec["sg_sasa_heavy_A2"] / rec["sg_sasa_isolated_A2"], 4) \
            if rec["sg_sasa_isolated_A2"] else None
        out[uni] = rec
    return out


def spread(vals):
    v = sorted(x for x in vals if x is not None)
    if not v:
        return {"n": 0}
    return {"n": len(v), "min": round(v[0], 4), "median": round(statistics.median(v), 4),
            "max": round(v[-1], 4),
            "mean": round(statistics.fmean(v), 4)}


def main():
    seqs = json.load(open(SEQ_CACHE))
    nr4a2_seq = seqs[NR4A2_ACC] if NR4A2_ACC in seqs else seqs["NR4A2"]
    if isinstance(nr4a2_seq, dict):
        nr4a2_seq = nr4a2_seq.get("sequence") or nr4a2_seq.get("seq")

    result = {
        "_title": "NR4A2 LBD competitor cysteines: modelled opened structure vs two experimental crystals",
        "_question": ("The covalent reach lane's paralogue competitor readings come from one modelled "
                      "NR4A2 structure. Two experimental NR4A2 LBD crystals are committed in this repo. "
                      "Does the modelled thiol-exposure ordering of the five NR4A2 LBD cysteines "
                      "reproduce in the experimental structures, and what is the experimental spread the "
                      "single modelled reading has no error bar against?"),
        "_scope": ("NR4A2 only; one measurement (heavy-atom Shrake-Rupley thiol exposure) recomputed by "
                   "one code path on both sides. NOT a pocket-state validation, NOT a cross-paralogue "
                   "claim, NOT evidence about NR4A3 C397, NOT any efficacy/selectivity/therapeutic claim."),
        "_provenance": {
            "sasa_implementation": "research/modalities/nr4a_differential_atlas.py (via "
                                   "nr4a3_covalent_handle_ensemble.atom_sasa), unmodified",
            "numbering": "global BLOSUM62 alignment to UniProt P43354 "
                         "(nr4a3_covalent_handle_ensemble.pdb_to_uniprot_map, identity >= 0.9)",
            "sequences": "research/modalities/nr4a-sequences-cache.json (committed, offline)",
            "model": "results/nr4a3-matrix/nr4a2-opened.pdb",
            "crystals": {k: os.path.relpath(v, REPO) for k, v in CRYSTALS.items()},
        },
        "_limits": [
            "1OVL and 7WNH are COLLAPSED APO crystals; nr4a2-opened.pdb is biased open along a "
            "pocket-opening CV. A systematic burial difference is EXPECTED and is not a refutation.",
            "Crystal chains carry no hydrogens, so every number here is heavy-atom-only on BOTH sides. "
            "The committed artifact's all-atom columns are not comparable and are not compared.",
            "Crystallographic packing and, in 7WNH, bound DNA and the DBD, are not present in the model; "
            "chains are measured in isolation (protein chain only) to keep the occluder set comparable.",
            "Chains within one crystal are not independent measurements of the protein.",
            "No thiol pKa, reaction rate, adduct or selectivity is computed. Exposure is not reactivity.",
        ],
        "model": {},
        "crystals": {},
        "comparison": {},
    }

    # ---- model side, recomputed heavy-only from coordinates
    residues, atoms = parse_chain(read_text(MODEL_PATH), protein_chains(read_text(MODEL_PATH))[0])
    uni_map, ident = che.pdb_to_uniprot_map(residues, nr4a2_seq)
    result["model"] = {"path": os.path.relpath(MODEL_PATH, REPO), "alignment_identity": round(ident, 4),
                       "n_residues": len(residues),
                       "cysteines": measure(residues, atoms, uni_map, NR4A2_LBD_CYS)}

    # ---- crystal side
    per_chain_vals = {u: [] for u in NR4A2_LBD_CYS}
    for pdb_id, path in CRYSTALS.items():
        text = read_text(path)
        entry = {"path": os.path.relpath(path, REPO), "chains": {}}
        for ch in protein_chains(text):
            residues, atoms = parse_chain(text, ch)
            try:
                uni_map, ident = che.pdb_to_uniprot_map(residues, nr4a2_seq)
            except ValueError as e:
                entry["chains"][ch] = {"refused": str(e)}
                continue
            # restrict the occluder set to the modelled UniProt span so the two sides see the same object
            keep = {p for p, u in uni_map.items() if MODEL_UNIPROT_RANGE[0] <= u <= MODEL_UNIPROT_RANGE[1]}
            atoms_lbd = [a for a in atoms if a["resid"] in keep]
            res_lbd = [(r, aa) for r, aa in residues if r in keep]
            m = measure(res_lbd, atoms_lbd, uni_map, NR4A2_LBD_CYS)
            entry["chains"][ch] = {"alignment_identity": round(ident, 4),
                                   "n_residues_in_model_span": len(res_lbd),
                                   "uniprot_span_resolved": [min(uni_map[r] for r, _ in res_lbd),
                                                             max(uni_map[r] for r, _ in res_lbd)],
                                   "cysteines": m}
            for u in NR4A2_LBD_CYS:
                per_chain_vals[u].append(m[u].get("sg_rel") if m[u].get("present") else None)
        result["crystals"][pdb_id] = entry

    # ---- comparison
    model_cys = result["model"]["cysteines"]
    rows = {}
    for u in NR4A2_LBD_CYS:
        rows[u] = {"model_sg_rel": model_cys[u].get("sg_rel"),
                   "model_rsa_heavy": model_cys[u].get("rsa_heavy"),
                   "crystal_sg_rel": spread(per_chain_vals[u])}
    def order_by(getter, keys):
        return [k for k in sorted(keys, key=lambda k: (-(getter(k) if getter(k) is not None else -1)))]
    model_rank = order_by(lambda u: rows[u]["model_sg_rel"], NR4A2_LBD_CYS)
    xtal_rank = order_by(lambda u: rows[u]["crystal_sg_rel"].get("median"), NR4A2_LBD_CYS)
    result["comparison"] = {
        "per_cysteine": rows,
        "rank_most_to_least_exposed_thiol": {"model": model_rank, "crystal_median": xtal_rank,
                                             "identical": model_rank == xtal_rank},
        "n_crystal_chains": sum(len(v["chains"]) for v in result["crystals"].values()),
    }

    # ---- the provenance claim this run tests, stated as a checkable fact
    art = json.load(open(ARTIFACT))
    result["absent_input_statement_under_test"] = {
        "artifact": os.path.relpath(ARTIFACT, REPO),
        "field": "comparison_validity.absent_input",
        "verbatim": art["comparison_validity"]["absent_input"],
        "checked_against": [os.path.relpath(p, REPO) for p in CRYSTALS.values()],
    }
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
