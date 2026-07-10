"""Unit tests for the PURE logic of nr4a3_8xtt_redock + nr4a3_8xtt_seed_md.

No smina / openmm / rdkit / biopython / network — protein_only_model (PDB text), summarize_selectivity
(the selectivity aggregate), and pick_seed_model are dependency-free. The dock/MM-GBSA/MD glue is validated
only in the AWS jobs.
"""
import pytest

import nr4a3_8xtt_redock as rd
import nr4a3_8xtt_seed_md as smd


# ------------------------------------------------------------------ protein_only_model

_MODEL = """\
ATOM      1  N   MET A 373      0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  MET A 373      1.000   0.000   0.000  1.00  0.00           C
ATOM      3  CB  MET A 373      1.500   0.000   0.000  1.00  0.00           C
ATOM      4  CA  LYS A 374      2.000   0.000   0.000  1.00  0.00           C
HETATM    5  O   HOH A 500      9.000   9.000   9.000  1.00  0.00           O
ATOM      6  CA  LEU B 999      8.000   0.000   0.000  1.00  0.00           C
"""


def test_protein_only_keeps_biggest_chain_atoms_drops_het_and_other_chain():
    out = rd.protein_only_model(_MODEL)
    lines = [l for l in out.splitlines() if l.startswith("ATOM")]
    # chain A has 4 ATOM records, chain B has 1 -> A wins; HETATM dropped
    assert len(lines) == 4
    assert all(l[21] == "A" for l in lines)
    assert "HOH" not in out
    assert out.rstrip().endswith("END")


def test_protein_only_altloc_filtered():
    text = ("ATOM      1  CA AMET A 373      0.000   0.000   0.000  1.00  0.00           C\n"
            "ATOM      2  CA BMET A 373      0.100   0.000   0.000  1.00  0.00           C\n"
            "ATOM      3  CA  LYS A 374      2.000   0.000   0.000  1.00  0.00           C\n")
    out = rd.protein_only_model(text)
    # the 'B' altloc is dropped; 'A' altloc + blank kept
    ats = [l for l in out.splitlines() if l.startswith("ATOM")]
    assert len(ats) == 2


def test_protein_only_no_atoms_raises():
    with pytest.raises(ValueError, match="no ATOM records"):
        rd.protein_only_model("HETATM    5  O   HOH A 500      9.000   9.000   9.000\n")


# ------------------------------------------------------------------ summarize_selectivity

def _conf(model, margin):
    return {"model": model, "mm_min_margin": margin}


def test_summary_survives_majority_selective():
    per = [_conf(2, 2.0), _conf(8, 1.5), _conf(20, 0.2), _conf(6, 3.0)]  # 3/4 > band(1.0)
    s = rd.summarize_selectivity(per, band=1.0)
    assert s["verdict"] == "survives"
    assert s["n_selective"] == 3
    assert s["n_conformers_scored"] == 4


def test_summary_mixed():
    per = [_conf(2, 2.0), _conf(8, 0.1), _conf(20, -0.5), _conf(6, 0.3)]  # 1/4 selective
    s = rd.summarize_selectivity(per, band=1.0)
    assert s["verdict"] == "mixed"
    assert s["n_selective"] == 1


def test_summary_fails_none_selective():
    per = [_conf(2, -1.0), _conf(8, 0.2), _conf(20, 0.5)]
    s = rd.summarize_selectivity(per, band=1.0)
    assert s["verdict"] == "fails"
    assert s["n_selective"] == 0


def test_summary_no_data_when_all_none():
    per = [{"model": 2, "error": "boom"}, {"model": 8, "mm_min_margin": None}]
    s = rd.summarize_selectivity(per, band=1.0)
    assert s["verdict"] == "no-data"
    assert s["n_conformers_scored"] == 0


def test_summary_frac_matches_threshold():
    """distribution_stats threshold == band, so frac_ge_threshold reflects the selective fraction."""
    per = [_conf(2, 2.0), _conf(8, 0.0)]
    s = rd.summarize_selectivity(per, band=1.0)
    assert s["min_margin_distribution"]["frac_ge_threshold"] == pytest.approx(0.5)


# ------------------------------------------------------------------ pick_seed_model

def test_pick_seed_model_default_single():
    assert smd.pick_seed_model(20, "8") == 8


def test_pick_seed_model_all_takes_first():
    assert smd.pick_seed_model(20, "all") == 1


def test_pick_seed_model_absent_raises():
    with pytest.raises(ValueError, match="none of the requested"):
        smd.pick_seed_model(5, "8")
