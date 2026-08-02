"""Unit tests for the PURE logic of nr4a3_covalent_handle_ensemble.

Everything here runs offline: no network, no RCSB, no numpy/biopython. The only I/O is reading PDB text
built inside the test. The network half (fetching 8XTT from files.rcsb.org) is CI-only and is not exercised
here — the sandbox's egress proxy 403s RCSB, which is exactly why that half is thin glue.
"""
import math
import os

import pytest

import nr4a_differential_atlas as atlas
import nr4a_paralogue_unique_residues as uniq
import nr4a3_covalent_handle_ensemble as che


# ------------------------------------------------------------------ helpers

def _atom(i, resid, name, elem, x, y, z, resname="CYS"):
    return {"resid": resid, "resname": resname, "name": name, "elem": elem,
            "x": float(x), "y": float(y), "z": float(z)}


def _tiny_cys(resid=1, origin=(0.0, 0.0, 0.0)):
    """A crude but geometrically sane CYS: N-CA-C-O backbone + CB-SG-HG side chain."""
    ox, oy, oz = origin
    spec = [("N", "N", 0, 0, 0), ("CA", "C", 1.46, 0, 0), ("C", "C", 2.2, 1.2, 0),
            ("O", "O", 3.4, 1.2, 0), ("CB", "C", 1.9, -0.8, -1.2), ("SG", "S", 3.6, -1.3, -1.4),
            ("HG", "H", 4.0, -2.0, -2.4)]
    return [_atom(i, resid, n, e, ox + x, oy + y, oz + z) for i, (n, e, x, y, z) in enumerate(spec)]


# ------------------------------------------------------------------ atom_sasa

def test_atom_sasa_matches_whole_structure_shrake_rupley():
    """THE equality that licenses the speed-up: evaluating only the atoms of interest, with every atom as an
    occluder, reproduces atlas.shrake_rupley for those residues EXACTLY at the same sphere count.

    If this ever drifts, every number in the artifact silently stops being comparable to the committed
    unique-residue map, which is the one thing the cross-check exists to prevent."""
    atoms = _tiny_cys(1) + _tiny_cys(2, origin=(4.5, 0.6, 0.3)) + _tiny_cys(3, origin=(20.0, 0.0, 0.0))
    whole = atlas.shrake_rupley(atoms, n_points=96)
    idx_by_res = {}
    for i, a in enumerate(atoms):
        idx_by_res.setdefault(a["resid"], []).append(i)
    subset = che.atom_sasa(atoms, idx_by_res[2], n_points=96)
    assert sum(subset.values()) == pytest.approx(whole[2], rel=1e-9, abs=1e-9)


def test_atom_sasa_buried_atom_is_zero_and_isolated_is_full_sphere():
    """Sanity at both extremes, so a silent geometry bug cannot hide behind plausible mid-range numbers."""
    lone = [_atom(0, 1, "SG", "S", 0, 0, 0)]
    r = atlas.VDW["S"] + atlas.PROBE
    got = che.atom_sasa(lone, [0], n_points=512)[0]
    assert got == pytest.approx(4.0 * math.pi * r * r, rel=0.01)

    # a sulfur completely enclosed by carbons at contact distance
    shell = [_atom(0, 1, "SG", "S", 0, 0, 0)]
    for dx, dy, dz in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
                       (0.7, 0.7, 0), (-0.7, -0.7, 0), (0.7, -0.7, 0), (-0.7, 0.7, 0),
                       (0, 0.7, 0.7), (0, -0.7, -0.7), (0.7, 0, 0.7), (-0.7, 0, -0.7)]:
        shell.append(_atom(len(shell), 2, "C", "C", dx * 1.5, dy * 1.5, dz * 1.5, resname="ALA"))
    assert che.atom_sasa(shell, [0], n_points=96)[0] < 1.0


# ------------------------------------------------------------------ numbering

def test_pdb_to_uniprot_map_offset_construct():
    """A construct that is an exact interior slice of the UniProt sequence maps with the right offset —
    derived by alignment, never by an assumed constant."""
    uniprot = "MKVLTAACDEFGHIKLMNPQRSTVWYACDEFG"
    start = 8                                     # 1-based
    seq = uniprot[start - 1:start - 1 + 15]
    residues = [(i + 1, aa) for i, aa in enumerate(seq)]
    m, ident = che.pdb_to_uniprot_map(residues, uniprot)
    assert ident == pytest.approx(1.0)
    assert m[1] == start
    assert m[15] == start + 14


def test_pdb_to_uniprot_map_refuses_a_different_protein():
    """A model and its own UniProt sequence are the same protein. A low identity means the wrong chain or a
    corrupt file, and the module must REFUSE rather than emit a plausible-looking wrong map."""
    residues = [(i + 1, aa) for i, aa in enumerate("WWWWWWWWWWWWWWWWWWWW")]
    with pytest.raises(ValueError, match="alignment identity"):
        che.pdb_to_uniprot_map(residues, "ACDEFGHIKLMNPQRSTVYACDEFGHIKLMNPQRSTVY")


# ------------------------------------------------------------------ the label bug this module already hit

def test_model_label_is_unique_across_identically_named_frames():
    """REGRESSION. The NR4A1/NR4A2 metadynamics ensembles are 25 directories each holding a file called
    `frame.pdb`. Keying on the basename collapsed all 25 into one entry and reported an ensemble of ONE —
    a populated, plausible-looking field that had not been measured. Caught on the first real run."""
    paths = [f"/x/results/nr4a1-pocket-ensemble/metad/fp_{i}_metad/frame.pdb" for i in (0, 50, 100)]
    labels = [che.model_label(p) for p in paths]
    assert len(set(labels)) == 3
    assert all(l.endswith("/frame.pdb") for l in labels)


def test_analyse_models_refuses_duplicate_labels():
    """Belt-and-braces for the same failure: if a labelling scheme ever collides again, the run FAILS rather
    than silently dropping models."""
    with pytest.raises(ValueError, match="not unique"):
        che.analyse_models(["/a/frame.pdb", "/a/frame.pdb"], "ACDEF", (1,),
                           label_fn=lambda p: "same")


# ------------------------------------------------------------------ spread

def test_spread_counts_missing_and_never_invents_a_value():
    """An absent reading is not a reading of absence: Nones are dropped AND counted."""
    s = che.spread([1.0, None, 3.0, 2.0, None])
    assert s["n"] == 3 and s["n_missing"] == 2
    assert s["min"] == 1.0 and s["median"] == 2.0 and s["max"] == 3.0
    assert che.spread([])["n"] == 0
    assert che.spread([None, None]) == {"n": 0, "n_missing": 2}
    one = che.spread([5.0])
    assert one["min"] == one["median"] == one["max"] == 5.0 and one["iqr"] == 0.0


# ------------------------------------------------------------------ criteria are IMPORTED, not re-typed

def test_criteria_thresholds_are_the_repo_constants_not_local_copies():
    """★ The whole point of the positive control is that the thresholds were fixed BEFORE the question was
    asked. If this module ever grows its own copy of 0.25 or of the reach bands, the control stops being a
    control and every NR4A3 statement becomes circular."""
    assert che.EXPOSED_RSA is atlas.EXPOSED_RSA
    assert che.REACH_BANDS is uniq.REACH_BANDS
    assert che.CRYPTIC_POCKET_UNIPROT is uniq.CRYPTIC_POCKET_UNIPROT
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(che.__file__))),
                            "modalities", "nr4a3_covalent_handle_ensemble.py")).read()
    body = src.split('"""', 2)[-1]          # skip the module docstring, which quotes them on purpose
    assert "EXPOSED_RSA = 0.25" not in body
    assert "REACH_BANDS = (" not in body


def test_criteria_splits_accessible_from_reachable():
    assert che.criteria(0.4, 5.0) == {"accessible": True, "reach_class": "in_pocket",
                                      "reachable": True, "flagged": True}
    assert che.criteria(0.1, 5.0)["flagged"] is False          # fails accessibility only
    assert che.criteria(0.4, 100.0)["flagged"] is False         # fails reach only
    assert che.criteria(0.4, 100.0)["reach_class"] == "distal"
    assert che.criteria(None, None)["flagged"] is False


# ------------------------------------------------------------------ rank test

def test_control_rank_orders_and_finds_the_control():
    opened = {
        "NR4A1": {"cysteines": {551: {"rsa": 0.20, "rsa_heavy": 0.3, "sg_sasa_A2": 5.0,
                                      "sg_sasa_heavy_A2": 20.0, "sg_rel": 0.3}}},
        "NR4A3": {"cysteines": {397: {"rsa": 0.40, "rsa_heavy": 0.5, "sg_sasa_A2": 9.0,
                                      "sg_sasa_heavy_A2": 30.0, "sg_rel": 0.5},
                                496: {"rsa": 0.01, "rsa_heavy": 0.02, "sg_sasa_A2": 0.0,
                                      "sg_sasa_heavy_A2": 0.0, "sg_rel": 0.0}}},
    }
    r = che.control_rank(opened)
    assert r["status"] == "OK" and r["n_cysteines_pooled"] == 3
    assert r["observables"]["rsa"]["rank"] == 2 and r["observables"]["rsa"]["of"] == 3
    assert r["observables"]["sg_rel"]["rank"] == 2


def test_control_rank_reports_unread_when_the_control_is_not_modelled():
    """A control that could not be run is UNREAD — never silently 'passed'."""
    opened = {"NR4A3": {"cysteines": {397: {"rsa": 0.4}}}}
    assert che.control_rank(opened)["status"] == "UNREAD"


# ------------------------------------------------------------------ cysteine_geometry end-to-end (synthetic)

def test_cysteine_geometry_reports_both_sasa_conventions_and_pocket_distance():
    atoms = _tiny_cys(1) + [_atom(99, 5, "CA", "C", 12.0, 0.0, 0.0, resname="ALA")]
    residues = [(1, "C"), (5, "A")]
    uni_map = {1: 401, 5: 405}
    out = che.cysteine_geometry(residues, atoms, uni_map, pocket_uniprot=(405,), n_points=96)
    row = out[401]
    assert row["sg_present"] is True
    # hydrogens present must occlude the SG relative to hydrogens deleted
    assert row["sg_sasa_A2"] < row["sg_sasa_heavy_A2"]
    assert 0.0 <= row["sg_rel"] <= 1.0
    assert row["dist_to_pocket_A"] == pytest.approx(
        math.dist((3.6, -1.3, -1.4), (12.0, 0.0, 0.0)), abs=0.01)
    assert row["reach_class"] in ("in_pocket", "exit_vector", "linker_borne", "distal")


def test_sg_sphere_count_does_not_disturb_the_residue_rsa_crosscheck():
    """★ The two-sphere-count invariant. `sg_n_points` refines the single-ATOM SG measures; it must leave
    the RESIDUE RSA untouched, because that number is what `crosscheck_committed` reproduces against the
    committed unique-residue artifact. If refining SG precision ever moved RSA, the cross-check would start
    failing for a reason that has nothing to do with the data."""
    atoms = _tiny_cys(1) + [_atom(99, 5, "CA", "C", 12.0, 0.0, 0.0, resname="ALA")]
    residues, uni_map = [(1, "C"), (5, "A")], {1: 401, 5: 405}
    coarse = che.cysteine_geometry(residues, atoms, uni_map, (405,), n_points=96, sg_n_points=96)
    fine = che.cysteine_geometry(residues, atoms, uni_map, (405,), n_points=96, sg_n_points=960)
    assert coarse[401]["rsa"] == fine[401]["rsa"]
    assert coarse[401]["residue_sasa_A2"] == fine[401]["residue_sasa_A2"]
    assert coarse[401]["dist_to_pocket_A"] == fine[401]["dist_to_pocket_A"]


def test_coarse_sg_sasa_is_quantised_and_finer_sphere_relieves_it():
    """The reason `sg_n_points` exists at all: at 96 points a sulfur's SASA lands on multiples of ~1.34 A^2,
    coarse enough that distinct cysteines read as identical numbers. Documented as a measured property, not
    an assumption."""
    lone = [_atom(0, 1, "SG", "S", 0, 0, 0)]
    r = atlas.VDW["S"] + atlas.PROBE
    quantum = 4.0 * math.pi * r * r / 96
    assert quantum == pytest.approx(1.34, abs=0.02)
    coarse = che.atom_sasa(lone, [0], n_points=96)[0]
    fine = che.atom_sasa(lone, [0], n_points=960)[0]
    assert coarse / quantum == pytest.approx(round(coarse / quantum), abs=1e-6)
    assert fine == pytest.approx(4.0 * math.pi * r * r, rel=0.005)


def test_cysteine_geometry_skips_residues_with_no_uniprot_counterpart():
    """A modelled residue that aligns to nothing is omitted, not assigned a guessed number."""
    atoms = _tiny_cys(1)
    out = che.cysteine_geometry([(1, "C")], atoms, {}, pocket_uniprot=(405,), n_points=96)
    assert out == {}


# ------------------------------------------------------------------ pocket mapping

def test_map_pocket_to_reports_unmappable_positions():
    a = "ACDEFGHIKLMNPQRSTVWY"
    b = "ACDEFGHIKLMNPQRSTVWY"
    mapped, missing = che.map_pocket_to(a, b, (3, 7, 999))
    assert mapped == [3, 7] and missing == [999]


# ------------------------------------------------------------------ the artifact must not assert feasibility

BANNED = ("is feasible", "feasibility is established", "druggable target", "will degrade",
          "therapeutic window", "covalent route is open")
NEGATIONS = ("no claim", "not ", "never", "is a judgement", "cannot", "does not", "no efficacy")


def _assert_only_negated(text, where):
    """Every banned phrase must sit inside an explicit negation.

    Scoped to a CHARACTER WINDOW, not to a line: the first version of this test scanned line by line and
    fired on `...that a covalent NR4A3 degrader\\nis feasible...`, where the negation was real but had been
    pushed onto the previous line by wrapping. A guard that fails on line breaks trains people to weaken it,
    which is worse than no guard.
    """
    low = text.lower()
    for banned in BANNED:
        start = 0
        while True:
            i = low.find(banned, start)
            if i < 0:
                break
            window = low[max(0, i - 200):i + len(banned) + 60]
            assert any(neg in window for neg in NEGATIONS), f"{where}: unnegated {banned!r} near {window!r}"
            start = i + len(banned)


def test_module_never_claims_a_covalent_nr4a3_degrader_is_feasible():
    """Hard constraint on this deliverable. Accessibility + spread + control recovery are reportable;
    feasibility is a judgement, not a measurement, and must not appear as a conclusion."""
    _assert_only_negated(open(che.__file__).read(), "source")


def test_rendered_markdown_never_claims_feasibility():
    """The guard that actually matters: the SOURCE is read by maintainers, but the MARKDOWN is what gets
    quoted into a manuscript. Rendered from a minimal synthetic artifact so it needs no structures."""
    d = {
        "_title": "t", "_question": "q", "_method": "m",
        "_criteria": {"note": "n", "accessible": "a", "reachable": "r", "flagged": "f"},
        "_limits": ["No claim is made that a covalent NR4A3 degrader is feasible."],
        "positive_control": {"protein": "NR4A1", "resnum": 551, "residue": "C",
                             "attribution": "proposed, not structurally confirmed",
                             "paralogue_partners": {"NR4A3": {"residue": "T", "resnum": 579,
                                                              "is_cysteine": False}}},
        "control_recovery": {"status": "NOT_RECOVERED", "reading": "criteria do not flag it"},
        "nr4a3_lbd_cysteines": [], "nr4a3_unique_lbd_cysteines": [], "ensembles": {},
        "cross_checks": {}, "unread_inputs": [], "refusals": [],
    }
    _assert_only_negated(che.to_markdown(d), "markdown")
