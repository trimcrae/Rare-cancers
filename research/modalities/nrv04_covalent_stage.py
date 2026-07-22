#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — staging helpers (prereg legs 3 + the covalent restraint pair).

Pure-stdlib PDB text edits (no gemmi/rdkit needed for these), so they unit-test offline. Two pieces:

  1. mutate_cys_to_ala(pdb_text, chain, resnum) — the C551A control (prereg leg 3). Truncates the target Cys to
     Ala by keeping only the Ala heavy atoms {N,CA,C,O,CB}, dropping Sγ (and all H), and renaming CYS->ALA. The
     existing pdbfixer hydrogenation step (ternary_pdb_stage._hydrogenate_pdb) re-adds H afterward.

  2. find_covalent_pair(pdb_text, cys_chain, cys_resnum, lig_resname, lig_atom) — locate the (Cys-Sγ, ligand
     electrophilic-C) atom-serial pair used by the MD driver to impose the restrained-covalent bond
     (celastrol C6 -> Cys551 Sγ, ~1.81 A). Returns 1-based PDB serials so the driver can map them to OpenMM
     particle indices.

These operate on the already-assembled complex.pdb (E3 + target LBD + ligand) that ternary staging produces.
"""
from __future__ import annotations

# PDB fixed-column fields (0-based slices)
_REC = slice(0, 6)
_SERIAL = slice(6, 11)
_NAME = slice(12, 16)
_RESNAME = slice(17, 20)
_CHAIN = slice(21, 22)
_RESSEQ = slice(22, 26)

_ALA_HEAVY = {"N", "CA", "C", "O", "CB"}     # atoms an alanine keeps; a Cys->Ala truncation drops SG (+ all H)


def _atom_name(line: str) -> str:
    return line[_NAME].strip()


def mutate_cys_to_ala(pdb_text: str, chain: str, resnum: int) -> str:
    """Return `pdb_text` with the CYS at (chain, resnum) truncated to ALA. Drops Sγ and every hydrogen on that
    residue (re-added later by the hydrogenation step), renames CYS->ALA. Raises if the target isn't a CYS."""
    out, seen_cys, kept = [], False, False
    for line in pdb_text.splitlines():
        rec = line[_REC].strip()
        if rec in ("ATOM", "HETATM") and line[_CHAIN] == chain and _safe_int(line[_RESSEQ]) == resnum:
            resname = line[_RESNAME].strip()
            if resname != "CYS":
                raise ValueError(f"residue {chain}{resnum} is {resname}, not CYS — refusing to mutate")
            seen_cys = True
            if _atom_name(line) not in _ALA_HEAVY:          # drop SG + all H
                continue
            kept = True
            line = line[:17] + "ALA" + line[20:]            # rename CYS -> ALA (cols 18-20)
        out.append(line)
    if not seen_cys:
        raise ValueError(f"no residue found at {chain}{resnum}")
    if not kept:
        raise ValueError(f"{chain}{resnum} had no backbone/CB atoms to keep — malformed input")
    return "\n".join(out) + "\n"


def find_covalent_pair(pdb_text: str, cys_chain: str, cys_resnum: int,
                       lig_resname: str, lig_atom: str) -> dict:
    """Locate the covalent-restraint atom pair: the Cys Sγ and the ligand electrophilic carbon. Returns their
    1-based PDB serials + (x,y,z) so the driver can (a) map to OpenMM indices and (b) sanity-check the starting
    distance. Raises if either atom is missing."""
    sg = _find_atom(pdb_text, cys_chain, cys_resnum, "SG", resname="CYS")
    lig = _find_ligand_atom(pdb_text, lig_resname, lig_atom)
    d = _dist(sg["xyz"], lig["xyz"])
    return {"cys_sg": sg, "lig_c": lig, "start_distance_A": round(d, 3),
            "target_bond_A": 1.81}                          # C(sp3)-S covalent length


# ---- helpers (pure) ---------------------------------------------------------------------------------------

def _safe_int(s: str):
    try:
        return int(s.strip())
    except ValueError:
        return None


def _xyz(line: str):
    return (float(line[30:38]), float(line[38:46]), float(line[46:54]))


def _dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def _find_atom(pdb_text, chain, resnum, atom, resname=None):
    for line in pdb_text.splitlines():
        if line[_REC].strip() in ("ATOM", "HETATM") and line[_CHAIN] == chain \
                and _safe_int(line[_RESSEQ]) == resnum and _atom_name(line) == atom:
            if resname and line[_RESNAME].strip() != resname:
                raise ValueError(f"{chain}{resnum} is {line[_RESNAME].strip()}, expected {resname}")
            return {"serial": _safe_int(line[_SERIAL]), "xyz": _xyz(line)}
    raise ValueError(f"atom {atom} not found at {chain}{resnum}")


def _find_ligand_atom(pdb_text, lig_resname, lig_atom):
    for line in pdb_text.splitlines():
        if line[_REC].strip() in ("ATOM", "HETATM") and line[_RESNAME].strip() == lig_resname \
                and _atom_name(line) == lig_atom:
            return {"serial": _safe_int(line[_SERIAL]), "xyz": _xyz(line)}
    raise ValueError(f"ligand atom {lig_resname}/{lig_atom} not found")
