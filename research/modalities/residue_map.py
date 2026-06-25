"""
Pure, unit-tested residue-number mapping shared by the MD analysis (nr4a3_mdpocket.py) and the
metadynamics CV (nr4a3_metad.py).

WHY THIS EXISTS. OpenMM/PDBFixer may renumber the solvated PDB residues from 1, while our target
residues (Pocket-5, the CV set) use the AF2/UniProt numbering. Assuming one scheme silently matched
zero residues once already. This resolves target residues to positional indices for BOTH schemes and
is unit-tested (tests/test_residue_map.py), so the assumption can't regress silently.
"""


def resolve_positions(resseqs, target_residues, lbd_first):
    """Positional indices (0-based, into the ordered protein-residue list `resseqs`) of the target
    residues, plus a label describing how they were mapped.

    `resseqs`: residue sequence numbers of the protein residues, in chain order.
    `target_residues`: residue numbers in the ORIGINAL AF2 numbering.
    `lbd_first`: first residue of the contiguously-trimmed LBD (e.g. 373).

    If the trajectory still carries the original numbering (resSeq spans the targets) we match by
    resSeq. Otherwise the residues were renumbered from 1, and since the LBD was trimmed contiguously
    from `lbd_first`, original residue r sits at ordinal (r - lbd_first)."""
    if not resseqs:
        return [], "empty"
    target = set(target_residues)
    if not target:
        return [], "no-targets"
    lo, hi = min(target), max(target)
    if min(resseqs) <= lo and hi <= max(resseqs):
        return [i for i, rs in enumerate(resseqs) if rs in target], "resSeq-preserved"
    return ([i for i in range(len(resseqs)) if (lbd_first + i) in target],
            f"renumbered-from-{lbd_first}")
