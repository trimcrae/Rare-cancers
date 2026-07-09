"""Unit tests for fusion_cofold construct assembly — locks the canonical EMC breakpoint geometry, the
EWS/NR4A3 block split (which the reporter relies on to separate the two halves), and the apo YAML shape.

Sequence fetch is stubbed so the test is offline and deterministic: fetch_seq is replaced with a function
that returns a residue-range-length string, so the assertions check the residue arithmetic, not the
network. `X`-only sequences are fine — nothing here inspects residue identity.
"""
import json

import fusion_cofold as fc


def _stub_fetch(acc, lo=None, hi=None):
    return "X" * (hi - lo + 1) if (lo and hi) else "X" * 600


def _run_prep(monkeypatch, tmp_path):
    monkeypatch.setattr(fc, "fetch_seq", _stub_fetch)
    monkeypatch.setattr(fc, "OUT_DIR", str(tmp_path))
    monkeypatch.setattr(fc, "HERE", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["fusion_cofold.py"])   # prep only, no --run
    fc.main()
    return json.load(open(tmp_path / "fusion-cofold-prep.json"))["constructs"]


def test_seam_construct_ranges_and_boundary(monkeypatch, tmp_path):
    c = _run_prep(monkeypatch, tmp_path)["seam"]
    # EWS C-terminal 120 aa of the EAD (res 145..264) :: NR4A3 AF1 (res 2..260)
    assert c["ews_range"] == [145, 264] and c["ews_len"] == 120
    assert c["nr4a3_range"] == [2, 260] and c["nr4a3_len"] == 259
    # the block boundary the reporter splits on MUST equal the EWS length
    assert c["block_boundary"] == c["ews_len"] == 120
    assert c["total_len"] == 120 + 259


def test_composite_removes_af1_spacer(monkeypatch, tmp_path):
    c = _run_prep(monkeypatch, tmp_path)["composite"]
    # generous upper bound: same EWS tail :: NR4A3 folded core (261..626), AF1 deliberately dropped
    assert c["ews_range"] == [145, 264] and c["ews_len"] == 120
    assert c["nr4a3_range"] == [261, 626] and c["nr4a3_len"] == 366
    assert c["block_boundary"] == 120
    assert c["total_len"] == 120 + 366


def test_apo_yaml_has_no_ligand(monkeypatch, tmp_path):
    _run_prep(monkeypatch, tmp_path)
    y = open(tmp_path / "seam.yaml").read()
    assert "protein:" in y and "id: A" in y
    assert "ligand" not in y and "smiles" not in y   # apo — ligand-free
    # single chimeric chain of the expected length
    seq_line = [ln for ln in y.splitlines() if "sequence:" in ln][0]
    assert len(seq_line.split("sequence:")[1].strip()) == 120 + 259


def test_constructs_fit_g5xlarge(monkeypatch, tmp_path):
    # both single-chain constructs stay well under the ~700-residue Boltz job that ran on ml.g5.xlarge
    cons = _run_prep(monkeypatch, tmp_path)
    for name, c in cons.items():
        assert c["total_len"] < 600, f"{name} too large ({c['total_len']}) for the 16 GB A10G"
