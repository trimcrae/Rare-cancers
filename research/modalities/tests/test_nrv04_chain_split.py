#!/usr/bin/env python3
"""Offline tests for the E3/degradation-target chain split (nrv04_covalent_assemble.identify_chains).

This is the regression suite for the 2026-07-24 finding: the MD driver derived the split POSITIONALLY ("target
= the last protein chain") while the co-fold YAML builder writes the target FIRST, so a 112-residue Elongin C
was scored as the degradation target and every interface readout described the wrong interface. The identifier
below replaces the guess, and these tests pin the two things that must never regress: it selects the NR4A LBD
in a real-shaped assembly, and it FAILS CLOSED rather than picking something plausible when the assembly is
wrong.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nrv04_covalent_assemble as asm  # noqa: E402


def _pdb(chains):
    """Minimal PDB text with `chains` = [(chain_id, n_residues)] — enough for the identifier, which only reads
    the chain column and the residue-sequence column."""
    lines = []
    serial = 1
    for ch, n in chains:
        for res in range(1, n + 1):
            lines.append(f"ATOM  {serial:5d}  CA  ALA {ch}{res:4d}    "
                         f"{0.0:8.3f}{0.0:8.3f}{0.0:8.3f}  1.00  0.00           C")
            serial += 1
    return "\n".join(lines) + "\n"


def _write(tmp_path, chains, name="complex.pdb"):
    p = tmp_path / name
    p.write_text(_pdb(chains))
    return str(p)


# the real co-fold layout, measured 2026-07-24: A = NR4A LBD (254), E = VHL (213), F = EloB (118), G = EloC (112)
REAL_LAYOUT = [("A", 254), ("E", 213), ("F", 118), ("G", 112)]


def test_identifies_the_nr4a_lbd_not_the_last_chain(tmp_path):
    got = asm.identify_chains(_write(tmp_path, REAL_LAYOUT))
    assert got["target_chain"] == "A", "the target is the NR4A LBD, which is the FIRST chain in these co-folds"
    assert got["e3_chains"] == ["E", "F", "G"]
    assert got["e3_roles"] == {"E": "VHL", "F": "ElonginB", "G": "ElonginC"}


def test_the_old_positional_rule_would_have_picked_elongin_c(tmp_path):
    """The bug, stated as a test: sorted-last is G (Elongin C, 112 residues), not the target."""
    got = asm.identify_chains(_write(tmp_path, REAL_LAYOUT))
    positional = sorted(c["chain"] for c in got["census"])[-1]
    assert positional == "G" and got["e3_roles"][positional] == "ElonginC"
    assert positional != got["target_chain"]


def test_chain_order_does_not_change_the_answer(tmp_path):
    """Identification is by composition, not position — so a co-fold that emits the target last is fine too."""
    reordered = [("E", 213), ("F", 118), ("G", 112), ("A", 254)]
    assert asm.identify_chains(_write(tmp_path, reordered))["target_chain"] == "A"


def test_contaminated_cofold_is_rejected_not_silently_used(tmp_path):
    """A 255-residue chain is 14-3-3 epsilon (the pre-2026-07-17 ElonginB accession error). It is within one
    residue of the 254-residue NR4A LBD, so a naive largest-chain rule could mistake one for the other — this
    must fail loudly instead."""
    contaminated = [("A", 254), ("E", 213), ("F", 255), ("G", 112)]
    with pytest.raises(ValueError, match="contaminant"):
        asm.identify_chains(_write(tmp_path, contaminated))


def test_missing_e3_subunit_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="unique degradation-target chain"):
        asm.identify_chains(_write(tmp_path, [("A", 254), ("X", 300), ("E", 213)]))


def test_wrong_sized_target_fails_closed(tmp_path):
    """The LBD construct is frozen at 254 residues; a different length means a different construct."""
    with pytest.raises(ValueError, match="expected the frozen"):
        asm.identify_chains(_write(tmp_path, [("A", 300), ("E", 213), ("F", 118), ("G", 112)]))


def test_e3_lengths_match_the_audited_uniprot_values():
    """Verified against UniProt on a CI runner, 2026-07-24 (nrv04_cofold_audit.fetch_lengths)."""
    assert asm.E3_CHAIN_RESIDUES == {213: "VHL", 118: "ElonginB", 112: "ElonginC"}
    assert 255 in asm.CONTAMINANT_CHAIN_RESIDUES
    assert asm.NR4A_LBD_RESIDUES == 254
