"""Unit tests for the PURE logic of nr4a3_8xtt_benchmark (the AF2-vs-8XTT benchmark).

Everything here runs WITHOUT 8XTT, numpy, biopython, or fpocket — the numbering map, the
superposition/RMSD, the distribution stats, and the verdict are all dependency-free pure functions, so
they are fully testable locally (the I/O glue that touches RCSB/AFDB/fpocket/biopython is exercised only
in the AWS job). The single fpocket-plumbing test skips when the fpocket binary is absent (as noted in
TESTING.md), which is the case in the dev container.
"""
import math
import shutil

import pytest

import nr4a3_8xtt_benchmark as bm


# ==================================================================================================
# numbering map (align 8XTT author numbering <-> Q92570 UniProt numbering)
# ==================================================================================================

def test_positions_from_blocks_simple_offset():
    """UniProt residues 373..377 aligned to 8XTT author residues 1..5 (a constant -372 offset)."""
    resnums_a = [373, 374, 375, 376, 377]          # UniProt
    resnums_b = [1, 2, 3, 4, 5]                     # 8XTT author numbering
    blocks_a = [(0, 5)]
    blocks_b = [(0, 5)]
    m = bm.positions_from_blocks(blocks_a, blocks_b, resnums_a, resnums_b)
    assert m == {373: 1, 374: 2, 375: 3, 376: 4, 377: 5}


def test_positions_from_blocks_with_gap():
    """A gap in B (missing residue) splits the alignment into two blocks; the map must skip the gapped
    UniProt residue and keep the numbering consistent on both sides."""
    resnums_a = [373, 374, 375, 376, 377]          # A has 5 residues
    resnums_b = [10, 11, 13, 14]                    # B is missing the residue aligned to A index 2
    blocks_a = [(0, 2), (3, 5)]                     # A indices 0,1  then 3,4  (index 2 unaligned)
    blocks_b = [(0, 2), (2, 4)]                     # B indices 0,1  then 2,3
    m = bm.positions_from_blocks(blocks_a, blocks_b, resnums_a, resnums_b)
    assert m == {373: 10, 374: 11, 376: 13, 377: 14}
    assert 375 not in m                              # gapped -> unmapped


def test_positions_from_blocks_bad_span_raises():
    with pytest.raises(ValueError, match="block spans differ"):
        bm.positions_from_blocks([(0, 3)], [(0, 2)], [1, 2, 3], [1, 2])


def test_identity_from_blocks():
    seq_a = "ACDEF"
    seq_b = "AXDEF"                                  # one mismatch at column 1
    ident = bm.identity_from_blocks([(0, 5)], [(0, 5)], seq_a, seq_b)
    assert ident == pytest.approx(4 / 5)


def test_map_uniprot_to_pdb_with_injected_aligner():
    """End-to-end map on a synthetic sequence pair, injecting a trivial identity aligner (no biopython).
    Same-length, identical sequences -> a single full-length block, identity 1.0, and the constant
    UniProt->author offset preserved."""
    uni_seq = "MKLTPQR"
    uni_res = [400, 401, 402, 403, 404, 405, 406]
    pdb_seq = "MKLTPQR"
    pdb_res = [1, 2, 3, 4, 5, 6, 7]

    def fake_align(a, b):
        assert a == uni_seq and b == pdb_seq
        return [(0, len(a))], [(0, len(b))]

    mapping, identity = bm.map_uniprot_to_pdb(uni_seq, uni_res, pdb_seq, pdb_res, align_fn=fake_align)
    assert identity == pytest.approx(1.0)
    assert mapping == {400: 1, 401: 2, 402: 3, 403: 4, 404: 5, 405: 6, 406: 7}


def test_map_uniprot_to_pdb_low_identity_fails_loud():
    """8XTT and Q92570 are the same protein — an implausibly low alignment identity must RAISE, never
    silently produce a garbage map."""
    def junk_align(a, b):
        return [(0, len(a))], [(0, len(b))]

    with pytest.raises(ValueError, match="implausibly low"):
        bm.map_uniprot_to_pdb("AAAAAA", [1, 2, 3, 4, 5, 6], "CCCCCC", [1, 2, 3, 4, 5, 6],
                              align_fn=junk_align)


# ==================================================================================================
# superposition / RMSD (pure Python quaternion Kabsch)
# ==================================================================================================

def test_centroid():
    assert bm.centroid([(0, 0, 0), (2, 4, 6)]) == (1.0, 2.0, 3.0)


def test_plain_rmsd_known_value():
    # each atom displaced by (1,0,0) -> per-atom sq dist 1 -> rmsd 1
    a = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    b = [(1, 0, 0), (2, 1, 1), (3, 2, 2)]
    assert bm.rmsd(a, b) == pytest.approx(1.0)


def test_plain_rmsd_length_mismatch_raises():
    with pytest.raises(ValueError, match="coordinate-count mismatch"):
        bm.rmsd([(0, 0, 0)], [(0, 0, 0), (1, 1, 1)])


def test_kabsch_identical_is_zero():
    pts = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]
    R, t = bm.kabsch_transform(pts, pts)
    fit = bm.apply_transform(pts, R, t)
    assert bm.rmsd(fit, pts) == pytest.approx(0.0, abs=1e-9)


def test_kabsch_pure_translation_recovered():
    pts = [(0, 0, 0), (1, 0, 0), (0, 2, 0), (0, 0, 3), (1, 1, 1)]
    target = [(x + 5, y - 3, z + 2) for (x, y, z) in pts]
    R, t = bm.kabsch_transform(pts, target)
    fit = bm.apply_transform(pts, R, t)
    assert bm.rmsd(fit, target) == pytest.approx(0.0, abs=1e-9)


def test_kabsch_known_rotation_recovered():
    """target = R_true @ mobile + translation; kabsch must recover a transform that maps mobile onto
    target with ~zero RMSD (rigid, exact)."""
    mobile = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (2, -1, 3), (-1, 2, 1)]
    # 90 deg about z: (x,y,z) -> (-y, x, z); then translate
    target = [(-y + 2, x - 1, z + 4) for (x, y, z) in mobile]
    R, t = bm.kabsch_transform(mobile, target)
    fit = bm.apply_transform(mobile, R, t)
    assert bm.rmsd(fit, target) == pytest.approx(0.0, abs=1e-6)


def test_kabsch_too_few_points_raises():
    with pytest.raises(ValueError, match="need >= 3"):
        bm.kabsch_transform([(0, 0, 0), (1, 1, 1)], [(0, 0, 0), (1, 1, 1)])


def test_superpose_and_score_identical():
    coords = {r: (r * 1.0, (r % 3) * 1.0, (r % 5) * 1.0) for r in range(400, 420)}
    out = bm.superpose_and_score(coords, coords, fit_residues=list(coords),
                                 pocket_residues=[406, 407, 410], handle_residues=[406, 410])
    assert out["global_rmsd"] == pytest.approx(0.0, abs=1e-9)
    assert out["pocket_rmsd"] == pytest.approx(0.0, abs=1e-9)
    assert out["handle_rmsd"] == pytest.approx(0.0, abs=1e-9)
    assert out["n_fit"] == 20
    assert out["n_pocket"] == 3
    assert set(out["handle_displacements"]) == {406, 410}


def test_superpose_and_score_rigid_translation_is_zero():
    mobile = {r: (r * 1.0, 0.0, 0.0) for r in range(400, 410)}
    # curve it so points aren't colinear (needed for a well-defined 3D fit)
    for r in mobile:
        mobile[r] = (r * 1.0, (r - 405) ** 2 * 0.1, (r % 2) * 1.0)
    target = {r: (x + 10, y - 4, z + 7) for r, (x, y, z) in mobile.items()}
    out = bm.superpose_and_score(mobile, target, fit_residues=list(mobile),
                                 pocket_residues=[406, 407], handle_residues=[406])
    assert out["global_rmsd"] == pytest.approx(0.0, abs=1e-6)
    assert out["pocket_rmsd"] == pytest.approx(0.0, abs=1e-6)


def test_superpose_and_score_missing_residues_skipped():
    mobile = {r: (r * 1.0, 1.0, 2.0) for r in [400, 401, 402, 403]}
    target = {r: (r * 1.0, 1.0, 2.0) for r in [400, 401, 402]}   # 403 absent in target
    out = bm.superpose_and_score(mobile, target, fit_residues=[400, 401, 402, 403],
                                 pocket_residues=[400, 403], handle_residues=[403])
    assert out["n_fit"] == 3                        # only 3 common residues fit
    assert out["n_pocket"] == 1                     # only 400 present (403 skipped)
    assert out["handle_rmsd"] is None               # 403 not in fit set -> no handle disp


def test_superpose_too_few_common_raises():
    mobile = {400: (0, 0, 0), 401: (1, 1, 1)}
    target = {400: (0, 0, 0), 401: (1, 1, 1)}
    with pytest.raises(ValueError, match="need >= 3"):
        bm.superpose_and_score(mobile, target, fit_residues=[400, 401],
                               pocket_residues=[400], handle_residues=[400])


# ==================================================================================================
# distribution statistics
# ==================================================================================================

def test_distribution_stats_known_values():
    vals = [0.1, 0.2, 0.3, 0.4, 0.5]                 # median 0.3, mean 0.3
    d = bm.distribution_stats(vals, threshold=0.3)
    assert d["n"] == 5
    assert d["min"] == pytest.approx(0.1)
    assert d["max"] == pytest.approx(0.5)
    assert d["median"] == pytest.approx(0.3)
    assert d["mean"] == pytest.approx(0.3)
    assert d["q1"] == pytest.approx(0.2)            # numpy 'linear' quantile
    assert d["q3"] == pytest.approx(0.4)
    assert d["iqr"] == pytest.approx(0.2)
    assert d["frac_ge_threshold"] == pytest.approx(3 / 5)   # 0.3,0.4,0.5 >= 0.3


def test_distribution_stats_drops_none_and_handles_empty():
    d = bm.distribution_stats([None, 0.6, None, 0.4], threshold=0.53)
    assert d["n"] == 2
    assert d["frac_ge_threshold"] == pytest.approx(0.5)     # only 0.6 >= 0.53
    empty = bm.distribution_stats([], threshold=0.53)
    assert empty["n"] == 0 and empty["median"] is None and empty["frac_ge_threshold"] is None


def test_quantile_interpolates():
    assert bm._quantile([0.0, 1.0], 0.5) == pytest.approx(0.5)
    assert bm._quantile([0.0, 1.0, 2.0, 3.0], 0.25) == pytest.approx(0.75)


# ==================================================================================================
# verdict
# ==================================================================================================

def _dist(vals):
    return bm.distribution_stats(vals, threshold=bm.DRUGGABLE_REF)


def test_verdict_agree():
    """Distribution brackets AF2 0.495, reaches 0.53; tight pocket + handle RMSD -> agree."""
    drug = _dist([0.40, 0.48, 0.52, 0.55, 0.60])    # min<=0.495<=max, some >=0.53
    v = bm.verdict(drug, bm.AF2_STATIC_DRUGGABILITY, global_rmsd_median=1.5,
                   pocket_rmsd_median=1.8, handle_rmsd_median=2.0)
    assert v["verdict"] == "agree"
    assert v["pocket_ok"] and v["fold_ok"] and v["handle_ok"]


def test_verdict_partial():
    """Pocket consistent but backbone moderately divergent (pocket RMSD 3.2 > 2.5) -> partial."""
    drug = _dist([0.45, 0.50, 0.54, 0.58])
    v = bm.verdict(drug, bm.AF2_STATIC_DRUGGABILITY, global_rmsd_median=2.5,
                   pocket_rmsd_median=3.2, handle_rmsd_median=2.5)
    assert v["verdict"] == "partial"
    assert v["pocket_ok"] and not v["fold_ok"]


def test_verdict_disagree_broken_fold():
    """A grossly divergent backbone (pocket RMSD > 5 A) forces disagree regardless of pocket score."""
    drug = _dist([0.50, 0.55])
    v = bm.verdict(drug, bm.AF2_STATIC_DRUGGABILITY, global_rmsd_median=8.0,
                   pocket_rmsd_median=6.5, handle_rmsd_median=7.0)
    assert v["verdict"] == "disagree"


def test_verdict_disagree_nothing_ok():
    drug = _dist([0.10, 0.12, 0.15])                # far below AF2, none reach 0.53
    v = bm.verdict(drug, bm.AF2_STATIC_DRUGGABILITY, global_rmsd_median=4.0,
                   pocket_rmsd_median=4.0, handle_rmsd_median=4.0)
    assert v["verdict"] == "disagree"
    assert not v["pocket_ok"] and not v["fold_ok"] and not v["handle_ok"]


# ==================================================================================================
# I/O text helpers that are pure enough to test without network/fpocket
# ==================================================================================================

_MULTIMODEL_PDB = """\
HEADER    NUCLEAR RECEPTOR
MODEL        1
ATOM      1  N   MET A 373      0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  MET A 373      1.000   0.000   0.000  1.00  0.00           C
ATOM      3  CA  LYS A 374      2.000   0.000   0.000  1.00  0.00           C
ATOM      4  CA  LEU A 375      3.000   0.000   0.000  1.00  0.00           C
TER
ENDMDL
MODEL        2
ATOM      1  CA  MET A 373      0.000   1.000   0.000  1.00  0.00           C
ATOM      2  CA  LYS A 374      0.000   2.000   0.000  1.00  0.00           C
ATOM      3  CA  LEU A 375      0.000   3.000   0.000  1.00  0.00           C
ENDMDL
END
"""


def test_split_models_counts_and_bodies():
    models = bm.split_models(_MULTIMODEL_PDB)
    assert len(models) == 2
    assert "MODEL" not in models[0] and models[0].rstrip().endswith("END")
    # model 1 has 4 ATOM records (incl. the N), model 2 has 3
    assert models[0].count("ATOM") == 4
    assert models[1].count("ATOM") == 3


def test_split_models_no_model_records_single_block():
    plain = ("ATOM      2  CA  MET A 373      1.000   0.000   0.000  1.00  0.00           C\n"
             "ATOM      3  CA  LYS A 374      2.000   0.000   0.000  1.00  0.00           C\n")
    models = bm.split_models(plain)
    assert len(models) == 1
    assert models[0].count("ATOM") == 2


def test_chain_ca_picks_biggest_chain_and_reads_coords():
    chain, resnums, seq, ca = bm.chain_ca(bm.split_models(_MULTIMODEL_PDB)[0])
    assert chain == "A"
    assert resnums == [373, 374, 375]
    assert seq == "MKL"                             # MET, LYS, LEU
    assert ca[373] == (1.0, 0.0, 0.0)


def test_pocket_overlapping_site_picks_max_overlap():
    pockets = [
        {"pocket": 1, "druggability": 0.9, "residues": [100, 101, 102]},       # no overlap
        {"pocket": 5, "druggability": 0.50, "residues": [406, 407, 410, 999]},  # 3 overlap
        {"pocket": 3, "druggability": 0.30, "residues": [406, 500]},            # 1 overlap
    ]
    site, n = bm.pocket_overlapping_site(pockets, [406, 407, 410, 412])
    assert site["pocket"] == 5 and n == 3
    none, zero = bm.pocket_overlapping_site(pockets, [700, 800])
    assert none is None and zero == 0


@pytest.mark.skipif(shutil.which("fpocket") is None,
                    reason="fpocket binary not installed locally; the per-model fpocket plumbing is "
                           "validated in the AWS job (entry_8xtt.py builds a conda env with fpocket). "
                           "Use AF-Q92570 as a single stand-in conformer where fpocket IS present.")
def test_fpocket_plumbing_on_stand_in(tmp_path):
    """Plumbing smoke test for fpocket_pockets_with_residues: runs fpocket on a small real structure and
    asserts the parse+map path returns well-formed pocket dicts. Skipped when fpocket is absent."""
    import os
    import urllib.request
    pdb = tmp_path / "stand_in.pdb"
    # Prefer a locally-mounted AF-Q92570 stand-in; else fetch (only works where egress is allowed).
    local = os.path.join(os.path.dirname(bm.__file__), "AF-Q92570.pdb")
    if os.path.exists(local):
        pdb.write_bytes(open(local, "rb").read())
    else:
        urllib.request.urlretrieve(
            "https://alphafold.ebi.ac.uk/files/AF-Q92570-F1-model_v4.pdb", str(pdb))
    pockets = bm.fpocket_pockets_with_residues(str(pdb))
    assert isinstance(pockets, list) and pockets
    for p in pockets:
        assert "druggability" in p and "residues" in p and isinstance(p["residues"], list)
