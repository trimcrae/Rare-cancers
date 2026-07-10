#!/usr/bin/env python3
"""Stage a RELATIVE / SELECTIVITY ABFE benchmark for the custom ABFE engine (nr4a3_abfe.py).

WHY THIS EXISTS
---------------
The engine's only prior benchmarks test ABSOLUTE ΔG on ONE receptor: methane hydration (passes) and
T4-lysozyme/benzene absolute binding (fails by +7.1 kcal/mol). Neither tests the observable we actually
USE for decisions — a receptor-to-receptor ΔΔG (a SELECTIVITY contrast) for ONE ligand. A per-engine
additive offset cancels in that difference, so a selectivity benchmark can pass even where the absolute
number is badly offset. This module builds the two receptor input files the modern ABFE pipeline consumes
(`<receptor>-opened.pdb` + `docked_<receptor>.sdf`) for a DOCUMENTED one-ligand / two-related-protein
selectivity system, so `gpu-abfe-aws.yml` can run it UNCHANGED and we can ask the reviewer's question:
does the protocol recover the experimental selectivity DIRECTION?

THE SYSTEM (see selectivity-benchmark.json for the cited ground truth)
----------------------------------------------------------------------
Ligand   : SGC-CBP30 (a 3,5-dimethylisoxazole acetyl-lysine-mimetic chemical probe), C28H33ClN4O3.
Protein A: CREBBP bromodomain  — holo PDB 4NR7 (CREBBP + SGC-CBP30). ITC Kd = 21 nM.
Protein B: BRD4 bromodomain 1  — holo PDB 5BT4 (BRD4(1) + SGC-CBP30). ITC Kd ~ 850 nM (40x weaker).
Both bromodomains are close structural homologs (same reader fold / Kac pocket) and BOTH crystallise HOLO
with the SAME ligand, so each pose is lifted from a real crystal complex (no docking). Experimental
selectivity: ~40-fold for CREBBP over BRD4(1) => ΔΔG_exp ≈ RT·ln(40) ≈ 2.2 kcal/mol favouring CREBBP
(Hay et al., J. Am. Chem. Soc. 2014, 136:9308). The benchmark PASSES if the engine returns
ΔG_bind(CREBBP) < ΔG_bind(BRD4(1)) (CREBBP the tighter binder).

DESIGN (mirrors .github/workflows/stage-t4l-benchmark.yml)
----------------------------------------------------------
Per receptor we emit:
  <receptor>-opened.pdb  — apo protein: standard-AA ATOM records of ONE chain; ligand/waters/ions
                           stripped; alt-locs resolved. prepare_leg() runs PDBFixer on this (adds missing
                           atoms + H), so we deliberately keep it a bare-protein parse.
  docked_<receptor>.sdf  — SGC-CBP30 at its CRYSTAL pose: heavy-atom coordinates lifted straight from the
                           holo HETATM records onto an RDKit molecule whose bond orders come from the
                           published SMILES (RDKit AssignBondOrdersFromTemplate), Hs added, _Name set to
                           the pose label the ABFE engine selects on.

The PARSING / POSE-INPUT logic in this file is PURE PYTHON (no rdkit / no network) and is unit-tested in
tests/test_selectivity_benchmark.py. The chemistry step (build_docked_sdf) imports rdkit lazily and runs
only inside the staging GitHub Action, exactly like the T4L staging job.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict

# ---------------------------------------------------------------- pure-python parsing (unit-tested)

STD_AA = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET",
          "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "HID", "HIE", "HIP", "SEC", "PYL", "MSE"}

# HETATM residue names that are NEVER the ligand of interest: water, buffer, cryoprotectant, common ions.
SOLVENT_HET = {
    "HOH", "WAT", "DOD", "H2O",
    "SO4", "PO4", "PGE", "PEG", "P6G", "1PE", "2PE", "EDO", "GOL", "MPD", "BME", "DMS", "DMSO",
    "ACT", "ACY", "FMT", "EPE", "TRS", "MES", "IMD", "NO3", "NH4", "CIT", "FLC", "TLA", "MLI",
    "NA", "K", "MG", "CA", "ZN", "MN", "FE", "CU", "NI", "CO", "CD", "HG", "CL", "BR", "IOD", "F",
    "CS", "RB", "SR", "BA", "LI", "PB", "AU", "PT", "XE", "KR", "AR",
}


def apo_protein(pdb_text):
    """Apo protein PDB: standard-AA ATOM records of the FIRST protein chain only; HETATM/water/ions
    stripped; alt-locs resolved (blank/'A' kept, altLoc column blanked); duplicate atom keys dropped.
    Returns (apo_pdb_text, chain_id, n_atoms). Mirrors stage-t4l-benchmark's apo_protein()."""
    out, chain, seen = [], None, set()
    for ln in pdb_text.splitlines():
        if ln[:6] != "ATOM  ":
            continue
        if ln[17:20].strip() not in STD_AA:
            continue
        cid = ln[21]
        if chain is None:
            chain = cid
        if cid != chain:
            continue
        if ln[16] not in (" ", "A"):            # keep altLoc blank or 'A' only
            continue
        key = (ln[12:16], ln[17:27])            # atom name + resName/chain/resSeq/iCode
        if key in seen:
            continue
        seen.add(key)
        out.append(ln[:16] + " " + ln[17:])     # blank the altLoc column
    out += ["TER", "END"]
    return "\n".join(out) + "\n", chain, len(seen)


def first_protein_chain(pdb_text):
    """The chain id of the first standard-AA ATOM record (the chain apo_protein keeps)."""
    for ln in pdb_text.splitlines():
        if ln[:6] == "ATOM  " and ln[17:20].strip() in STD_AA:
            return ln[21]
    return None


def _elem(ln):
    """Element symbol from a PDB ATOM/HETATM line: columns 77-78 if present, else first alpha of the name."""
    e = ln[76:78].strip()
    if e:
        return e[0].upper() + e[1:].lower()
    nm = ln[12:16].strip()
    return (nm[0:1] or "?").upper()


def hetatm_residues(pdb_text):
    """Group HETATM records into candidate ligand residues.

    Returns a dict keyed by (resName, chainId, resSeq, iCode) -> list of raw HETATM line strings
    (one entry per atom record, alt-locs included). Water/ion/buffer residues (SOLVENT_HET) are excluded.
    """
    groups = defaultdict(list)
    for ln in pdb_text.splitlines():
        if ln[:6] != "HETATM":
            continue
        resn = ln[17:20].strip()
        if resn in SOLVENT_HET:
            continue
        key = (resn, ln[21], ln[22:26].strip(), ln[26].strip())
        groups[key].append(ln)
    return dict(groups)


def _distinct_heavy_atom_count(lines):
    """Number of DISTINCT heavy (non-H) atoms in a residue's lines, collapsing alt-locs by atom name."""
    names = set()
    for ln in lines:
        if _elem(ln) in ("H", "D"):
            continue
        names.add(ln[12:16].strip())
    return len(names)


def select_ligand_residue(pdb_text, het_code=None, prefer_chain=None):
    """Pick the ligand residue to lift the pose from.

    - If het_code is given, restrict to residues with that resName.
    - Otherwise consider every non-solvent HETATM residue.
    - Prefer a copy in `prefer_chain` (so the pose sits in the SAME protein copy we emit as the apo PDB);
      among the remaining, choose the one with the most distinct heavy atoms (the real drug-like ligand,
      not a stray buffer molecule), tie-broken by (chain, resSeq) for determinism.

    Returns (reskey, lines) or raises ValueError if nothing qualifies.
    """
    groups = hetatm_residues(pdb_text)
    if het_code:
        code = het_code.strip().upper()
        groups = {k: v for k, v in groups.items() if k[0] == code}
        if not groups:
            raise ValueError(f"no non-solvent HETATM residue named {code!r} found")
    if not groups:
        raise ValueError("no non-solvent HETATM residue found (structure may be apo)")

    def rank(item):
        (resn, chain, resseq, icode), lines = item
        in_chain = 1 if (prefer_chain is not None and chain == prefer_chain) else 0
        try:
            seq = int(resseq)
        except ValueError:
            seq = 10**9
        # sort key: chain-match first, then more heavy atoms, then deterministic (chain, resSeq)
        return (in_chain, _distinct_heavy_atom_count(lines), -ord(chain[:1] or "Z"), -seq)

    reskey, lines = max(groups.items(), key=rank)
    return reskey, lines


def ligand_heavy_atoms(lines):
    """Heavy-atom (name, element, (x,y,z)) list for ONE alt-loc copy of a ligand residue.

    Alt-locs are resolved to blank/'A'; duplicate atom names are dropped (first wins); hydrogens skipped.
    This is exactly the coordinate set lifted onto the RDKit template in build_docked_sdf().
    """
    atoms, seen = [], set()
    for ln in lines:
        if ln[16] not in (" ", "A"):            # single alt-loc
            continue
        el = _elem(ln)
        if el in ("H", "D"):
            continue
        name = ln[12:16].strip()
        if name in seen:
            continue
        seen.add(name)
        xyz = (float(ln[30:38]), float(ln[38:46]), float(ln[46:54]))
        atoms.append((name, el, xyz))
    return atoms


def single_altloc_pdb_block(lines):
    """A PDB block of ONE alt-loc copy of the ligand, alt-loc column blanked, for RDKit MolFromPDBBlock.

    Keeps heavy atoms + any explicit hydrogens of the blank/'A' alt-loc, deduped by atom name.
    """
    out, seen = [], set()
    for ln in lines:
        if ln[16] not in (" ", "A"):
            continue
        name = ln[12:16].strip()
        if name in seen:
            continue
        seen.add(name)
        out.append(ln[:16] + " " + ln[17:])
    out.append("END")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- rdkit chemistry (runs in the Action)

def build_docked_sdf(smiles, ligand_pdb_block, name, out_path):
    """Lift the crystal pose onto an RDKit molecule with correct bond orders and write docked_<r>.sdf.

    rdkit is imported HERE (lazily) so the pure-python parsing above stays importable/testable without it.
    Recipe: perceive the ligand's heavy-atom geometry from the holo HETATM block, then assign bond
    orders / aromaticity from the published SMILES template (RDKit's standard AssignBondOrdersFromTemplate),
    which preserves the crystal conformer. Hs are added with coordinates; _Name is set to the ABFE pose
    label. Returns a stats dict; raises on any mismatch (so the Action fails loudly rather than staging a
    wrong molecule).
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdMolDescriptors

    template = Chem.MolFromSmiles(smiles)
    if template is None:
        raise ValueError(f"could not parse ligand SMILES: {smiles!r}")
    raw = Chem.MolFromPDBBlock(ligand_pdb_block, removeHs=True, proximityBonding=True, sanitize=False)
    if raw is None:
        raise ValueError("RDKit could not read the ligand HETATM block")
    # AssignBondOrdersFromTemplate matches the template's heavy-atom graph onto the PDB geometry and
    # transfers bond orders + aromaticity, keeping the crystal conformer.
    mol = AllChem.AssignBondOrdersFromTemplate(template, raw)
    Chem.SanitizeMol(mol)
    mol = Chem.AddHs(mol, addCoords=True)
    mol.SetProp("_Name", name)
    w = Chem.SDWriter(out_path)
    w.write(mol)
    w.close()

    # readback the way prepare_leg loads it
    rb = Chem.SDMolSupplier(out_path, removeHs=False, sanitize=True)[0]
    if rb is None or rb.GetProp("_Name") != name:
        raise ValueError("SDF readback / _Name check failed")
    f_rb = rdMolDescriptors.CalcMolFormula(rb)
    f_tm = rdMolDescriptors.CalcMolFormula(Chem.AddHs(template))
    if f_rb != f_tm:
        raise ValueError(f"formula mismatch: SDF {f_rb} vs template {f_tm}")
    return {"formula": f_rb, "n_atoms": rb.GetNumAtoms(),
            "n_heavy": rb.GetNumHeavyAtoms(), "name": name}


# ---------------------------------------------------------------- staging driver (network + boto3 lazy)

def _fetch_pdb(pdb_id):
    import requests
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    print(f"# fetching {url}", flush=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.text


def _parse_entries(spec):
    """'crebbp:4NR7,brd4bd1:5BT4' -> [('crebbp','4NR7'), ('brd4bd1','5BT4')]."""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        tok, _, pid = part.partition(":")
        tok, pid = tok.strip(), pid.strip()
        if not tok or not pid:
            raise ValueError(f"bad entry {part!r}; expected token:PDBID")
        out.append((tok, pid))
    return out


def stage_one(pdb_text, receptor, smiles, ligand_name, het_code, out_dir):
    """Build <receptor>-opened.pdb + docked_<receptor>.sdf from a holo PDB text. Returns (pdb_path, sdf_path)."""
    apo_pdb, chain, n_atoms = apo_protein(pdb_text)
    resids = sorted({int(l[22:26]) for l in apo_pdb.splitlines()
                     if l[:6] == "ATOM  " and l[22:26].strip().lstrip("-").isdigit()})
    print(f"# {receptor}: apo chain {chain}, {n_atoms} atoms, {len(resids)} residues "
          f"(range {resids[0]}..{resids[-1]})", flush=True)
    reskey, lines = select_ligand_residue(pdb_text, het_code=het_code or None, prefer_chain=chain)
    heavy = ligand_heavy_atoms(lines)
    print(f"# {receptor}: ligand residue {reskey[0]} (chain {reskey[1]} resSeq {reskey[2]}), "
          f"{len(heavy)} heavy atoms", flush=True)
    pdb_path = os.path.join(out_dir, f"{receptor}-opened.pdb")
    sdf_path = os.path.join(out_dir, f"docked_{receptor}.sdf")
    with open(pdb_path, "w") as f:
        f.write(apo_pdb)
    stats = build_docked_sdf(smiles, single_altloc_pdb_block(lines), ligand_name, sdf_path)
    print(f"# {receptor}: wrote {pdb_path} and {sdf_path} — {stats}", flush=True)
    return pdb_path, sdf_path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage the SGC-CBP30 CREBBP-vs-BRD4(1) selectivity ABFE benchmark")
    ap.add_argument("--entries", default="crebbp:4NR7,brd4bd1:5BT4",
                    help="comma-sep receptorToken:PDBID pairs (both holo with the ligand)")
    ap.add_argument("--ligand-smiles",
                    default="COC1=CC=C(CCC2=NC3=CC(C4=C(C)ON=C4C)=CC=C3N2C[C@H](C)N2CCOCC2)C=C1Cl",
                    help="isomeric SMILES of the shared ligand (bond-order template for the pose lift)")
    ap.add_argument("--ligand-name", default="sgc_cbp30",
                    help="pose label written as SDF _Name (the ABFE 'ligand' selector)")
    ap.add_argument("--het-code", default="",
                    help="PDB 3-letter HET code of the ligand; empty = auto-detect the largest non-solvent HETATM residue")
    ap.add_argument("--pdb-dir", default="", help="dir of pre-fetched <PDBID>.pdb (skip network)")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--upload-prefix", default="", help="S3 receptor_prefix to upload under; empty = no upload")
    ap.add_argument("--region", default="us-east-2")
    a = ap.parse_args(argv)

    os.makedirs(a.out_dir, exist_ok=True)
    entries = _parse_entries(a.entries)
    produced = []
    for receptor, pdb_id in entries:
        if a.pdb_dir:
            with open(os.path.join(a.pdb_dir, f"{pdb_id}.pdb")) as f:
                pdb_text = f.read()
        else:
            pdb_text = _fetch_pdb(pdb_id)
        produced += list(stage_one(pdb_text, receptor, a.ligand_smiles, a.ligand_name,
                                   a.het_code, a.out_dir))

    if a.upload_prefix:
        import boto3
        acct = boto3.client("sts").get_caller_identity()["Account"]
        bucket = f"sagemaker-{a.region}-{acct}"
        s3 = boto3.client("s3")
        prefix = a.upload_prefix.strip().strip("/")
        for fn in produced:
            key = f"{prefix}/{os.path.basename(fn)}"
            s3.upload_file(fn, bucket, key)
            print(f"# uploaded s3://{bucket}/{key} ({os.path.getsize(fn)} B)", flush=True)
        print("\n=== STAGED — dispatch gpu-abfe-aws.yml (mode=run) with: ===")
        print(f"    receptor_prefix = {prefix}")
        print(f"    receptors       = {','.join(t for t, _ in entries)}")
        print(f"    ligand          = {a.ligand_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
