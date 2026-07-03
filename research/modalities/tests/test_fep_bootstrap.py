import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_fep as fep  # noqa: E402


def _stub_setup(monkeypatch, tmp_path, captured):
    """Mock the heavy setup helpers so run_real's phase logic can be tested without Yank/LEaP."""
    monkeypatch.setattr(fep, "CKPT_DIR", str(tmp_path))
    monkeypatch.setattr(fep, "RECEPTOR_DIR", str(tmp_path))
    (tmp_path / "nr4a3-opened.pdb").write_text("ATOM\n")            # rec pdb existence check
    monkeypatch.setattr(fep, "_extract_ligand_sdf", lambda r, o: "lig.sdf")
    monkeypatch.setattr(fep, "_sdf_to_mol2", lambda s, o: "lig.mol2")
    monkeypatch.setattr(fep, "_prep_receptor", lambda p, o: p)
    monkeypatch.setattr(fep, "_yank_yaml",
                        lambda receptor, n_iter, out_dir, lig, rec: captured.__setitem__("n_iter", n_iter) or "y")
    monkeypatch.setattr(fep, "_run_yank_resilient", lambda *a, **k: 0)


def test_bootstrap_uses_bootstrap_iter_and_skips_dg(tmp_path, monkeypatch):
    captured = {}
    _stub_setup(monkeypatch, tmp_path, captured)
    monkeypatch.setattr(fep, "BOOTSTRAP_ITER", 60)

    def no_parse(*a, **k):
        raise AssertionError("_parse_dg must NOT run for the bootstrap phase")
    monkeypatch.setattr(fep, "_parse_dg", no_parse)

    fep.run_real({"id": "nr4a3", "receptor": "nr4a3"}, phase="bootstrap")

    assert captured["n_iter"] == 60                                 # ran at BOOTSTRAP_ITER, not PILOT/PROD
    marker = json.load(open(tmp_path / "nr4a3.json"))
    assert marker["phase"] == "bootstrap"                           # marker so the spot 'sample' phase resumes it
    assert "dg_bind_kcal" not in marker                             # no (meaningless) ΔG at this iteration count


def test_sample_phases_use_full_iters_and_parse_dg(tmp_path, monkeypatch):
    captured = {}
    _stub_setup(monkeypatch, tmp_path, captured)
    monkeypatch.setattr(fep, "PILOT_ITER", 500)
    monkeypatch.setattr(fep, "PROD_ITER", 3000)
    monkeypatch.setattr(fep, "_parse_dg", lambda out_dir: (-9.1, 0.4))

    fep.run_real({"id": "nr4a3", "receptor": "nr4a3"}, phase="pilot")
    assert captured["n_iter"] == 500
    assert json.load(open(tmp_path / "nr4a3.json"))["dg_bind_kcal"] == -9.1

    fep.run_real({"id": "nr4a3", "receptor": "nr4a3"}, phase="prod")
    assert captured["n_iter"] == 3000                              # prod extends to the full count
