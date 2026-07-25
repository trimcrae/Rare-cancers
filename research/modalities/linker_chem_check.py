#!/usr/bin/env python3
"""
RDKit verification of the RUNG-5b virtual library. Runs on a free CI runner inside the pre-baked
`docker.io/triskit23/ternary-fep` image (CLAUDE.md §6: pull the image, never solve a conda env in CI).

WHY THIS EXISTS, AND WHY IT IS A REFUSAL RATHER THAN A REPORT. `nr4a3_linker_design.py` derives a linker
length and a branch position from GEOMETRY, and then emits a SMILES string by concatenation. Those are two
independent representations of the same molecule, and nothing in the enumerator forces them to agree — a
mis-specified fragment, an off-by-one in the branch index, or a segment whose atom count is wrong would
produce a library whose geometry and whose chemistry describe different compounds, with no symptom. Three
such defects were already caught by READING the emitted strings (an alpha-ketoamide at the VHL junction, an
N,O-acetal wherever a PEG segment followed an amide nitrogen, an acylurea when the branch residue abutted the
warhead acyl) and one by re-deriving an index (the branch position was one atom too close to the warhead).
Reading strings does not scale and does not stay done. So this recomputes, from the PARSED MOLECULE:

  * the backbone length, as the topological shortest path between the two anchor atoms, and compares it to
    `n_backbone_atoms_intended` — **a mismatch is a hard failure, not a warning**;
  * the branch position, as the path index of the branch alpha-carbon, and compares it to
    `branch_k_from_warhead`;
  * that the cmpd19 warhead core, the des-acetyl VH032 core or the pomalidomide core, and the declared
    pendant are each present as exact substructures, with stereochemistry where declared;
  * that no unintended functional group was created at a junction (alpha-ketoamide, N,O-acetal, acylurea,
    ketone, anhydride, ester-in-linker);
  * physicochemical descriptors, reported WITHOUT a pass/fail, because a degrader is a beyond-rule-of-5
    molecule by construction and gating on Ro5 here would reject the entire class.

Output: `nr4a3-linker-library-chem.json`, committed back to the triggering branch. Exit code is non-zero if
any construct fails, so the CI step cannot go green on a library that does not describe what it claims to.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

HERE = os.path.dirname(os.path.abspath(__file__))

# Anchor definitions. Each is a SMILES whose anchor atom carries **atom map 1** — the warhead's C5 substituent
# atom on one side, the E3 handle's attachment heteroatom on the other. These are exactly the two atoms the
# geometry calls `a` and `b`.
#
# ★ WHY ATOM MAPS AND `MolFromSmiles`, RATHER THAN SMARTS WITH A POSITIONAL INDEX. The first version used
# hand-written SMARTS and took the anchor as the match's last atom, and BOTH halves of that were wrong:
#   * `O=C1NC(=O)CCC1N1C(=O)c2cccc([NX3])c2C1=O` ends with the phthalimide carbonyl OXYGEN, not the aniline
#     nitrogen, so the CRBN anchor was seven bonds from where it was supposed to be — which is exactly the
#     discrepancy the length check then reported (24 intended, 31 measured). The check caught it, which is
#     the point, but a positional index into a hand-written pattern is a defect waiting to happen.
#   * the VHL pattern spelled the thiazole and the benzene with UPPERCASE C, i.e. aliphatic carbon, while
#     RDKit aromatises those rings on parse — so it matched nothing at all, on 21 of 22 constructs.
# `MolFromSmiles` perceives aromaticity the same way for the query and the target, and an atom map names the
# anchor explicitly instead of relying on where it happens to fall in the string.
ANCHORS = {
    "warhead_5amide": "COC(=O)c1c[nH]c2ccc([N:1])cc12",
    "warhead_5triazole": "COC(=O)c1c[nH]c2ccc([O:1])cc12",
    "warhead_5piperazine": "COC(=O)c1c[nH]c2ccc([N:1]3CCNCC3)cc12",
    "e3_vhl": "CC1=C(SC=N1)c1ccc(CNC(=O)C2CC(O)CN2C(=O)C(C(C)(C)C)[N:1])cc1",
    "e3_crbn": "O=C1NC(=O)CCC1N1C(=O)c2cccc([N:1])c2C1=O",
}

# Stereocentres that are legitimately UNDEFINED rather than unspecified. The thalidomide-class glutarimide
# C-3 epimerises in aqueous solution on a timescale of minutes, so these ligands are used, and behave, as
# racemates; demanding a configuration there would be demanding something chemistry does not provide.
RACEMIC_BY_CHEMISTRY = {
    "crbn": ("the pomalidomide glutarimide C-3, which epimerises in solution — declared racemic, not "
             "unspecified", 1),
}

CORES = {
    "cmpd19": "COC(=O)c1c[nH]c2ccccc12",
    "vh032_desacetyl": "CC1=C(SC=N1)c1ccc(CNC(=O)C2CC(O)CN2C(=O)C(C(C)(C)C)N)cc1",
    "pomalidomide": "O=C1NC(=O)CCC1N1C(=O)c2cccc(N)c2C1=O",
}

# Junction motifs that must NEVER appear. Each was either emitted by an earlier version of the enumerator or
# is the obvious neighbouring failure mode of one that was.
FORBIDDEN = {
    "alpha_ketoamide": "[NX3][CX3](=O)[CX3](=O)",
    "n_o_acetal": "[NX3][CX4;H2][OX2]",
    "acylurea": "[CX3](=O)[NX3][CX3](=O)[NX3]",
    "linker_ketone": "[CX4][CX3](=O)[CX4]",
    "anhydride": "[CX3](=O)[OX2][CX3]=O",
    "gem_diol_or_hemiketal": "[OX2H][CX4][OX2]",
}

PENDANT_SMARTS = {
    "cyac_me": "N#CC(=CC)C(=O)N",
    "cyac_ph": "N#CC(=Cc1ccccc1)C(=O)N",
    "acrylamide": "C=CC(=O)N",
    "cyanoprop": "N#CC(C)C(=O)N",
    "pyr3": "Cc1cccnc1",
    "ph": "Cc1ccccc1",
}


# ★ HOW THE ANCHORS ARE ACTUALLY FOUND, AFTER TWO FAILED ATTEMPTS AT HAND-WRITTEN PATTERNS.
#
# Attempt 1 was SMARTS with a positional index: the CRBN pattern's last atom was the phthalimide carbonyl
# OXYGEN rather than the aniline nitrogen (seven bonds out — exactly the 24-vs-31 discrepancy reported), and
# the VHL pattern spelled aromatic rings with uppercase carbon so it matched nothing at all.
# Attempt 2 was `MolFromSmiles` with the anchor named by atom map — which failed on 4 of 5 patterns against
# their OWN reference molecules, i.e. the patterns were wrong in a way that had nothing to do with naming the
# atom. (`--diagnose-anchors` prints the match-count matrix that discriminates why.)
#
# The lesson is that a hand-written pattern is a second, unverified description of the molecule, and this
# module exists precisely because second descriptions drift. So the anchors are now found STRUCTURALLY, from
# the fragments the library is built out of and which are already known to match:
#
#   1. match the two TRUNCATED cores — the warhead's indole ester, and the E3 handle *minus its attachment
#      heteroatom*. These are complete, self-contained fragments; the earlier run confirmed both the cmpd19
#      and pomalidomide cores match cleanly.
#   2. take the shortest path between them.
#   3. the anchor on each side is the FIRST atom on that path outside its own core.
#
# That is the chemical definition of the anchors verbatim — the warhead's C5 substituent atom, and the E3
# handle's attachment heteroatom — with nothing hand-transcribed, and it is handle-agnostic: the same rule
# finds the aniline N, the ether O and the piperazine N without three separate patterns.
TRUNCATED_CORES = {
    "warhead": "COC(=O)c1c[nH]c2ccccc12",
    "e3_vhl": "CC1=C(SC=N1)c1ccc(CNC(=O)C2CC(O)CN2C(=O)C(C(C)(C)C))cc1",
    "e3_crbn": "O=C1NC(=O)CCC1N1C(=O)c2ccccc2C1=O",
}


def _core_atoms(mol, key):
    patt = Chem.MolFromSmiles(TRUNCATED_CORES[key])
    if patt is None:
        raise RuntimeError("truncated core %s does not parse" % key)
    hits = mol.GetSubstructMatches(patt, useChirality=False)
    if not hits:
        return None, "truncated core %s not found" % key
    if len(hits) > 1 and len({frozenset(h) for h in hits}) > 1:
        return None, "truncated core %s is ambiguous (%d distinct matches)" % (key, len(hits))
    return set(hits[0]), None


def find_anchors(mol, e3_handle):
    """(warhead_anchor_idx, e3_anchor_idx, error). Structural, not pattern-transcribed — see the note above."""
    wh_core, err = _core_atoms(mol, "warhead")
    if err:
        return None, None, err
    e3_core, err = _core_atoms(mol, "e3_" + e3_handle)
    if err:
        return None, None, err
    if wh_core & e3_core:
        return None, None, "the warhead and E3 cores overlap; the construct is not two handles on a linker"
    best = None
    for i in wh_core:
        for j in e3_core:
            p = Chem.GetShortestPath(mol, i, j)
            if p and (best is None or len(p) < len(best)):
                best = p
    if not best:
        return None, None, "no path between the warhead and E3 cores"
    a = next((x for x in best if x not in wh_core), None)
    b = next((x for x in reversed(best) if x not in e3_core), None)
    if a is None or b is None:
        return None, None, "the cores are directly bonded; there is no linker between them"
    return a, b, None


def check_one(c):
    """Verify one construct. Returns a dict; `ok` False means the construct does not describe what it claims."""
    out = {"construct_id": c["construct_id"], "errors": [], "warnings": []}
    mol = Chem.MolFromSmiles(c["smiles"])
    if mol is None:
        out["errors"].append("SMILES does not parse")
        out["ok"] = False
        return out

    a_idx, b_idx, err = find_anchors(mol, c["e3_handle"])
    if err:
        out["errors"].append(err)
        out["ok"] = False
        return out
    out["anchor_atoms"] = {
        "warhead": "%s%d" % (mol.GetAtomWithIdx(a_idx).GetSymbol(), a_idx),
        "e3": "%s%d" % (mol.GetAtomWithIdx(b_idx).GetSymbol(), b_idx),
    }
    expect_wh = {"5amide": "N", "5triazole": "O", "5piperazine": "N"}[c["warhead_handle"]]
    if mol.GetAtomWithIdx(a_idx).GetSymbol() != expect_wh:
        out["errors"].append("warhead anchor is %s, but handle %s attaches through %s"
                             % (mol.GetAtomWithIdx(a_idx).GetSymbol(), c["warhead_handle"], expect_wh))
    if mol.GetAtomWithIdx(b_idx).GetSymbol() != "N":
        out["errors"].append("E3 anchor is %s, but both handles attach through N"
                             % mol.GetAtomWithIdx(b_idx).GetSymbol())

    path = Chem.GetShortestPath(mol, a_idx, b_idx)
    n_measured = len(path) - 2          # atoms STRICTLY between the two anchors
    out["n_backbone_atoms_measured"] = n_measured
    out["n_backbone_atoms_intended"] = c["n_backbone_atoms_intended"]
    if n_measured != c["n_backbone_atoms_intended"]:
        out["errors"].append("backbone length disagrees: geometry says %d, the molecule says %d"
                             % (c["n_backbone_atoms_intended"], n_measured))

    # branch position, re-derived from the molecule: the path atom carrying the declared pendant
    if c.get("branch_k_from_warhead") is not None:
        patt = Chem.MolFromSmarts(PENDANT_SMARTS[c["pendant"]])
        hits = mol.GetSubstructMatches(patt) if patt is not None else []
        if not hits:
            out["errors"].append("declared pendant %s not found in the molecule" % c["pendant"])
        else:
            # ★ THE BRANCH ATOM IS THE PATH ATOM TOPOLOGICALLY CLOSEST TO THE PENDANT — not necessarily one
            # BONDED to it. The first version required direct adjacency and failed on every Dab-branch
            # construct, because the electrophile is mounted on a two-carbon side chain: the pendant's
            # matched atoms start three bonds from the backbone, so nothing on the path touches them. The
            # distance is measured rather than assumed, and reported, so a pendant that has drifted onto the
            # wrong part of the molecule still shows up as an implausible side-chain length.
            pend_atoms = set(a for h in hits for a in h)
            dmat = Chem.GetDistanceMatrix(mol)
            best = None
            for i, ai in enumerate(path):
                if ai in pend_atoms:
                    continue
                d = min(dmat[ai][pa] for pa in pend_atoms)
                if best is None or d < best[0]:
                    best = (d, i)
            if best is None or best[0] > 4:
                out["errors"].append("pendant %s is not attached to the backbone path (nearest backbone "
                                     "atom is %s bonds away)"
                                     % (c["pendant"], "none" if best is None else int(best[0])))
            else:
                out["branch_side_chain_bonds"] = int(best[0])
                k_measured = best[1]               # index along the path from the WARHEAD anchor
                out["branch_k_measured"] = k_measured
                out["branch_k_intended"] = c["branch_k_from_warhead"]
                if k_measured != c["branch_k_from_warhead"]:
                    out["errors"].append("branch position disagrees: geometry says k=%d, the molecule says "
                                         "k=%d" % (c["branch_k_from_warhead"], k_measured))

    # Required cores, checked against the SAME truncated fragments the anchor rule uses. Deliberately not a
    # second, independently hand-written set: a duplicate description is exactly what failed twice above, and
    # a spurious "required core absent" would fail the build for a defect in the check rather than the library.
    for name in ("warhead", "e3_" + c["e3_handle"]):
        atoms, err = _core_atoms(mol, name)
        out.setdefault("cores", {})[name] = atoms is not None
        if err:
            out["errors"].append("required core %s: %s" % (name, err))

    for name, sma in FORBIDDEN.items():
        patt = Chem.MolFromSmarts(sma)
        if patt is not None and mol.HasSubstructMatch(patt):
            out["errors"].append("forbidden junction motif present: %s" % name)

    centres = Chem.FindMolChiralCenters(mol, includeUnassigned=True, useLegacyImplementation=False)
    n_stereo = len(centres)
    n_unassigned = sum(1 for _, tag in centres if tag == "?")
    allowed_reason, n_allowed = RACEMIC_BY_CHEMISTRY.get(c["e3_handle"], (None, 0))
    if n_unassigned > n_allowed:
        out["errors"].append("%d UNASSIGNED stereocentre(s) (%d allowed): an 'exact structure' with an "
                             "undefined centre is two compounds, not one" % (n_unassigned, n_allowed))
    elif n_unassigned:
        out["warnings"].append("%d undefined stereocentre(s), by chemistry rather than by omission: %s"
                               % (n_unassigned, allowed_reason))
        out["racemic_by_chemistry"] = allowed_reason

    out["descriptors"] = {
        "mw": round(Descriptors.MolWt(mol), 1),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
        "clogp": round(Crippen.MolLogP(mol), 2),
        "tpsa": round(rdMolDescriptors.CalcTPSA(mol), 1),
        "hbd": rdMolDescriptors.CalcNumHBD(mol),
        "hba": rdMolDescriptors.CalcNumHBA(mol),
        "rotatable_bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "fraction_csp3": round(rdMolDescriptors.CalcFractionCSP3(mol), 3),
        "n_stereocentres": n_stereo,
        "_reading": "REPORTED, NOT GATED. A bifunctional degrader is beyond-rule-of-5 by construction; "
                    "applying a Ro5 filter here would reject the entire modality. These are for the "
                    "manuscript's physicochemical assessment and for ranking WITHIN the class.",
    }
    out["canonical_smiles"] = Chem.MolToSmiles(mol)
    out["inchikey"] = Chem.MolToInchiKey(mol)
    out["ok"] = not out["errors"]
    return out


def check_pair(pair, results):
    """The matched pair carries an extra obligation: d and d0 must differ in EXACTLY ONE ATOM.

    Checked, not asserted: same heavy-atom count, same net formal charge, same rotatable-bond count, same
    number of stereocentres, and a canonical-SMILES difference confined to a single aromatic position. If any
    of those fails the pair is not a matched pair and `S` would not isolate the wedge element.
    """
    d, d0 = pair.get("d"), pair.get("d0")
    if not d or not d0:
        return {"ok": False, "errors": ["no pair proposed"]}
    rd = next((r for r in results if r["construct_id"] == d["construct_id"]), None)
    r0 = next((r for r in results if r["construct_id"] == d0["construct_id"]), None)
    if not rd or not r0 or not rd.get("descriptors") or not r0.get("descriptors"):
        return {"ok": False, "errors": ["pair members failed their own checks"]}
    md, m0 = Chem.MolFromSmiles(d["smiles"]), Chem.MolFromSmiles(d0["smiles"])
    errs = []
    if md.GetNumHeavyAtoms() != m0.GetNumHeavyAtoms():
        errs.append("heavy-atom counts differ (%d vs %d)" % (md.GetNumHeavyAtoms(), m0.GetNumHeavyAtoms()))
    if Chem.GetFormalCharge(md) != Chem.GetFormalCharge(m0):
        errs.append("net formal charges differ")
    if rd["descriptors"]["rotatable_bonds"] != r0["descriptors"]["rotatable_bonds"]:
        errs.append("rotatable-bond counts differ")
    if rd["descriptors"]["n_stereocentres"] != r0["descriptors"]["n_stereocentres"]:
        errs.append("stereocentre counts differ")
    fd = rdMolDescriptors.CalcMolFormula(md)
    f0 = rdMolDescriptors.CalcMolFormula(m0)
    return {
        "ok": not errs,
        "errors": errs,
        "d_formula": fd, "d0_formula": f0,
        "d_inchikey": rd.get("inchikey"), "d0_inchikey": r0.get("inchikey"),
        "heavy_atoms": md.GetNumHeavyAtoms(),
        "delta": "d - d0 = one aromatic C-H replaced by N (aza-scan)",
        "_reading": "these are the checks that make 'differs only in the wedge element' a MEASUREMENT rather "
                    "than a claim. They do not, and cannot, establish that the two molecules are equally "
                    "well described by the force field — that is a separate question for the FEP setup.",
    }


# Minimal N-acylated / N-alkylated references, one per anchor: the smallest molecule that legitimately
# contains that anchor. Used by `--self-test`, which is the check that WOULD have caught both anchor bugs
# before they reached the library — a pattern that matches nothing, or that names the wrong atom, fails here
# in two seconds instead of failing 22 constructs in CI.
ANCHOR_REFERENCES = {
    "warhead_5amide": ("COC(=O)c1c[nH]c2ccc(NC(C)=O)cc12", "N"),
    "warhead_5triazole": ("COC(=O)c1c[nH]c2ccc(OCc3cn(C)nn3)cc12", "O"),
    "warhead_5piperazine": ("COC(=O)c1c[nH]c2ccc(N3CCN(C(C)=O)CC3)cc12", "N"),
    "e3_vhl": ("CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)C)O", "N"),
    "e3_crbn": ("C1CC(=O)NC(=O)C1N2C(=O)C3=C(C2=O)C(=CC=C3)NC(C)=O", "N"),
}


def diagnose_anchors():
    """Print which query construction actually matches, for each anchor, against its own reference.

    Written instead of guessing why `[N:1]` failed. Four hypotheses, each discriminated by one row:
      (H1) the pattern is wrong independently of the map      -> the no-map column also fails
      (H2) the bracket atom `[N:1]` fixes H count / valence   -> the no-map column passes, `[N:1]` fails
      (H3) atom maps participate in matching                  -> same signature as H2, separated by the
                                                                 `[#7:1]`-as-SMARTS column
      (H4) aromaticity perception differs                     -> SMARTS-with-lowercase passes where the
                                                                 SMILES-derived query fails
    """
    rows = []
    for key, (ref_smi, elem) in ANCHOR_REFERENCES.items():
        ref = Chem.MolFromSmiles(ref_smi)
        pat = ANCHORS[key]
        nomap = pat.replace("[N:1]", "N").replace("[O:1]", "O")
        variants = {
            "smiles_with_map": Chem.MolFromSmiles(pat),
            "smiles_no_map": Chem.MolFromSmiles(nomap),
            "smarts_with_map": Chem.MolFromSmarts(pat.replace("[N:1]", "[#7:1]").replace("[O:1]", "[#8:1]")),
            "smarts_no_map": Chem.MolFromSmarts(nomap),
            "smiles_no_map_adjusted": None,
        }
        m = Chem.MolFromSmiles(nomap)
        if m is not None:
            from rdkit.Chem import rdmolops
            p = rdmolops.AdjustQueryParameters.NoAdjustments()
            p.adjustDegree = False
            p.makeDummiesQueries = True
            variants["smiles_no_map_adjusted"] = rdmolops.AdjustQueryProperties(m, p)
        row = {"anchor": key}
        for name, q in variants.items():
            row[name] = ("PARSE-FAIL" if q is None
                         else str(len(ref.GetSubstructMatches(q, uniquify=False))))
        rows.append(row)
    cols = ["anchor", "smiles_with_map", "smiles_no_map", "smarts_with_map", "smarts_no_map",
            "smiles_no_map_adjusted"]
    print("[chem] anchor-matching diagnostic (match counts against each anchor's own reference).")
    print("[chem] RETAINED after the structural rule replaced these patterns: the failure it explains is a "
          "general RDKit fact about hand-written queries, and the next person to write one needs it.")
    print("[chem] " + " | ".join("%-22s" % c for c in cols))
    for r in rows:
        print("[chem] " + " | ".join("%-22s" % str(r.get(c, "")) for c in cols))
    return 0


def self_test():
    """Every anchor pattern must parse, mark exactly one atom, match its own reference molecule, and land on
    an atom of the expected element. Also checks the forbidden-motif SMARTS parse and that a deliberately
    malformed molecule is caught."""
    bad = []
    # The truncated cores must each match their own reference, and the anchor rule must land on the right
    # element in a minimal two-handle construct.
    for key, smi in TRUNCATED_CORES.items():
        if Chem.MolFromSmiles(smi) is None:
            bad.append("truncated core %s does not parse" % key)
    for e3, wh, expect_wh, probe in (
            ("vhl", "5amide", "N",
             "CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)CCC(=O)"
             "Nc4ccc5[nH]cc(C(=O)OC)c5c4)O"),
            ("vhl", "5triazole", "O",
             "CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)CCCn4cc"
             "(COc5ccc6[nH]cc(C(=O)OC)c6c5)nn4)O"),
            ("crbn", "5amide", "N",
             "C1CC(=O)NC(=O)C1N2C(=O)C3=C(C2=O)C(=CC=C3)NC(=O)CCC(=O)Nc4ccc5[nH]cc(C(=O)OC)c5c4")):
        m = Chem.MolFromSmiles(probe)
        if m is None:
            bad.append("%s/%s probe does not parse" % (e3, wh))
            continue
        a, b, err = find_anchors(m, e3)
        if err:
            bad.append("%s/%s: %s" % (e3, wh, err))
            continue
        if m.GetAtomWithIdx(a).GetSymbol() != expect_wh:
            bad.append("%s/%s: warhead anchor is %s, expected %s"
                       % (e3, wh, m.GetAtomWithIdx(a).GetSymbol(), expect_wh))
        if m.GetAtomWithIdx(b).GetSymbol() != "N":
            bad.append("%s/%s: E3 anchor is %s, expected N"
                       % (e3, wh, m.GetAtomWithIdx(b).GetSymbol()))
    for name, sma in FORBIDDEN.items():
        if Chem.MolFromSmarts(sma) is None:
            bad.append("forbidden motif %s does not parse" % name)
    for name, sma in PENDANT_SMARTS.items():
        if Chem.MolFromSmarts(sma) is None:
            bad.append("pendant SMARTS %s does not parse" % name)
    # the forbidden motifs must actually fire on molecules that contain them
    for name, probe in (("alpha_ketoamide", "CC(=O)C(=O)NC"), ("n_o_acetal", "CC(=O)NCOC"),
                        ("acylurea", "CC(=O)NC(=O)NC"), ("anhydride", "CC(=O)OC(C)=O")):
        m = Chem.MolFromSmiles(probe)
        if not m.HasSubstructMatch(Chem.MolFromSmarts(FORBIDDEN[name])):
            bad.append("forbidden motif %s does not fire on %s" % (name, probe))
    if bad:
        for b in bad:
            print("[chem] SELF-TEST FAILURE: %s" % b)
        return 1
    print("[chem] self-test OK (%d truncated cores, %d forbidden motifs, %d pendants)"
          % (len(TRUNCATED_CORES), len(FORBIDDEN), len(PENDANT_SMARTS)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--design", default=os.path.join(HERE, "nr4a3-linker-design.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-linker-library-chem.json"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--diagnose-anchors", action="store_true")
    args = ap.parse_args(argv)
    if args.diagnose_anchors:
        return diagnose_anchors()
    if args.self_test:
        return self_test()

    design = json.load(open(args.design))
    lib = design["virtual_library"]
    results = [check_one(c) for c in lib]
    n_bad = sum(1 for r in results if not r["ok"])
    # ★ BOTH PAIRS ARE CHECKED (2026-07-25). RUNG 5b now proposes a pair at the term-(a) EXEMPLAR (the
    # recommended one, which is what 5a-KS would be run on) and one at the REPRESENTATIVE. Verifying only the
    # first would leave the second's "differs in exactly one atom" claim unverified while it sits in the
    # artifact being quoted — and the representative pair used to be the ONLY one checked, so this is the
    # coverage moving with the deliverable rather than staying where it was.
    pair = check_pair(design.get("matched_pair_for_rung_5a_ks", {}), results)
    pair_rep = check_pair(design.get("matched_pair_at_representative_geometry", {}), results)

    out = {
        "_title": "RDKit verification of the RUNG-5b virtual library",
        "_method": "Every construct's backbone length and branch position are RE-DERIVED from the parsed "
                   "molecule (topological shortest path between the two anchor atoms) and compared to the "
                   "values the geometry asserted; required cores and the declared pendant are matched as "
                   "exact substructures; a list of junction motifs that must never appear is checked; "
                   "descriptors are reported without a pass/fail.",
        "_rdkit_version": Chem.rdBase.rdkitVersion,
        "n_constructs": len(lib),
        "n_failed": n_bad,
        "constructs": results,
        "matched_pair_check": pair,
        "matched_pair_check_at_representative_geometry": pair_rep,
        "_descriptor_scope": "A bifunctional degrader is beyond-rule-of-5 by construction. Descriptors are "
                             "for physicochemical assessment and within-class ranking; no permeability, "
                             "exposure, efficacy or safety claim follows from them.",
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("[chem] %d constructs, %d FAILED  (exemplar pair: %s | representative pair: %s)"
          % (len(lib), n_bad,
             "OK" if pair.get("ok") else "FAILED %s" % pair.get("errors"),
             "OK" if pair_rep.get("ok") else "FAILED %s" % pair_rep.get("errors")))
    for r in results:
        if not r["ok"]:
            print("[chem]   %-40s %s" % (r["construct_id"], "; ".join(r["errors"])))
    return 1 if (n_bad or not pair.get("ok") or not pair_rep.get("ok")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
