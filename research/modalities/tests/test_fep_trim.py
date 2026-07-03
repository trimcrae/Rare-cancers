import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_fep as fep  # noqa: E402


def _atom(i, resseq, x, y, z):
    return (f"ATOM  {i:>5}  CA  ALA A{resseq:>4}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n")


def _write_pdb(path, n_tail_n, n_core, n_tail_c):
    """Compact core near origin (~within 15 Å) + floppy N/C tails marching out along +z far past the core."""
    lines, idx, res = [], 1, 1
    # N-terminal floppy tail: residues marching out to large -z (far from core)
    for k in range(n_tail_n):
        z = -100.0 + k * 3.8            # from -100 up toward the core
        lines.append(_atom(idx, res, 0.0, 0.0, z)); idx += 1; res += 1
    # compact core: a tight cluster near origin
    import math
    for k in range(n_core):
        a = k * 0.9
        lines.append(_atom(idx, res, 10 * math.cos(a), 10 * math.sin(a), (k % 7) - 3)); idx += 1; res += 1
    # C-terminal floppy tail marching out to large +z
    for k in range(n_tail_c):
        z = 30.0 + k * 3.8
        lines.append(_atom(idx, res, 0.0, 0.0, z)); idx += 1; res += 1
    open(path, "w").write("".join(lines))


def test_trims_both_floppy_tails(tmp_path):
    p = str(tmp_path / "rec.pdb")
    _write_pdb(p, n_tail_n=15, n_core=60, n_tail_c=10)
    out = fep._trim_floppy_termini(p, str(tmp_path))
    assert out != p                                    # something was trimmed
    order, atoms, ca = fep._residues_in_order(out)
    # the compact core (60 residues) should survive; the ~25 floppy tail residues should be gone
    assert 55 <= len(order) <= 66
    # every surviving CA is near the core (no far-flung tail residue left)
    import math
    xs = [c for c in ca.values()]
    cz = sum(p[2] for p in xs) / len(xs)
    assert all(abs(p[2] - cz) < 30 for p in xs)


def test_guard_keeps_untrimmed_when_all_compact(tmp_path):
    p = str(tmp_path / "compact.pdb")
    _write_pdb(p, n_tail_n=0, n_core=80, n_tail_c=0)   # no floppy tails
    out = fep._trim_floppy_termini(p, str(tmp_path))
    assert out == p                                    # nothing to trim → returns input unchanged


def test_guard_refuses_excessive_trim(tmp_path):
    # mostly tail, tiny core → trimming would remove >35% → guard falls back to untrimmed
    p = str(tmp_path / "mostlytail.pdb")
    _write_pdb(p, n_tail_n=40, n_core=20, n_tail_c=40)
    out = fep._trim_floppy_termini(p, str(tmp_path))
    assert out == p
