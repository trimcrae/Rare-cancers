"""parse_pdb() must REFUSE multi-chain input rather than silently discarding half of it.

WHY. nr4a_differential_atlas.parse_pdb keys residues by number alone, so a two-chain complex numbered
from 1 collapses onto itself and roughly half the residues vanish with no error. That is correct and
intended for the matched single-chain NR4A LBD models it was written for, and it is a silent wrong
answer for anything else -- the one failure mode this program keeps paying for (a positional chain
split that scored Elongin C; a watchdog unparseable so its cron never fired; a diagnostic returning
True when its report was absent).

Verified before adding the guard: all three committed models are single-chain A, so refusing
multi-chain moves no published number. This test pins both halves of that contract.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from nr4a_differential_atlas import parse_pdb  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
MODELS = os.path.join(REPO, "results", "nr4a3-matrix")


def test_single_chain_models_still_parse():
    """The committed matched models must keep working -- this guard must not move any result."""
    for name in ("nr4a3-opened.pdb", "nr4a1-opened.pdb", "nr4a2-opened.pdb"):
        path = os.path.join(MODELS, name)
        if not os.path.exists(path):
            pytest.skip(f"{name} not present")
        residues, atoms = parse_pdb(path)
        assert residues, f"{name} parsed to zero residues"
        assert atoms, f"{name} parsed to zero atoms"


def test_multichain_input_raises_rather_than_silently_halving(tmp_path):
    """Two chains both numbered from 1: without the guard, chain B vanishes and nothing says so."""
    pdb = tmp_path / "twochain.pdb"
    lines = []
    for chain in ("A", "B"):
        for i, (resn, atom) in enumerate([("ALA", "CA"), ("GLY", "CA")], start=1):
            lines.append(
                f"ATOM  {i:5d}  {atom:<3s} {resn} {chain}{i:4d}    "
                f"{1.0 * i:8.3f}{2.0:8.3f}{3.0:8.3f}  1.00  0.00           C"
            )
    pdb.write_text("\n".join(lines) + "\n")

    with pytest.raises(ValueError) as exc:
        parse_pdb(str(pdb))
    msg = str(exc.value)
    assert "SINGLE-CHAIN ONLY" in msg
    assert "2 chains" in msg
    assert "parse_multichain_pdb" in msg, "the error must name the correct alternative"
