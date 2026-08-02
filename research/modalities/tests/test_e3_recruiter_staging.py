"""Unit tests for e3_recruiter_staging — RUNG 5a's E3 staging + ligandability downselect.

Every test here is offline and synthetic. The point is not to re-check RCSB (that is fetched provenance) but
to pin the three things that could silently corrupt the deliverable:

  1. the GEOMETRY means what the JSON says it means — a ligand in a synthetic pocket with one open mouth must
     report high burial and an exit vector pointing OUT of the mouth, not into the wall;
  2. the DOWNSELECT is the preregistered rule — gates are hard, the Pareto front is a real dominance test,
     and the cap drops the rest with a recorded reason;
  3. no recruiter can be dropped on availability, which nr4a3-program-map.md forbids explicitly.
"""
import json
import math

import pytest

import e3_recruiter_staging as st


# ---------------------------------------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------------------------------------
def _atom(x, y, z, elem="C", name="C", chain="A", resid=1, resname="ALA"):
    return {"chain": chain, "resid": resid, "resname": resname, "name": name, "elem": elem,
            "x": float(x), "y": float(y), "z": float(z)}


def _shell_pocket(open_axis="+z", radius=5.0, n=700, mouth_cos=0.55):
    """A hollow protein shell around the origin with ONE opening along `open_axis`. The inner layer sits in
    van-der-Waals contact with a ligand at the origin, so burial is meaningful; the outer layers stop rays
    leaking through the shell. Anything at the origin is enclosed except along that axis, so the correct
    exit vector is unambiguous."""
    atoms, pts = [], st._fib_sphere(n)
    ax = {"+z": (0, 0, 1), "-z": (0, 0, -1), "+x": (1, 0, 0)}[open_axis]
    for i, (dx, dy, dz) in enumerate(pts):
        if dx * ax[0] + dy * ax[1] + dz * ax[2] > mouth_cos:      # carve the mouth
            continue
        for r in (radius, radius + 2.2, radius + 4.4):            # layers, so rays cannot leak through
            atoms.append(_atom(dx * r, dy * r, dz * r, resid=1 + i % 40))
    return atoms


def test_exit_vector_points_out_of_the_pocket_mouth():
    prot = _shell_pocket("+z")
    lig = [_atom(0, 0, 0), _atom(1.4, 0, 0), _atom(0, 1.4, 0), _atom(0, 0, 1.4)]
    res = st.analyse_site(prot, lig)
    ev = res["exit_vector"]
    # the maximum-clearance direction must be the open axis
    assert ev["direction"][2] > 0.85, ev["direction"]
    assert ev["clearance_A"] >= 15.0
    assert ev["cone_openness_30deg"] > 0.5
    # and the site must read as enclosed, not as a flat surface
    assert res["site_enclosure"]["blocked_fraction"] > 0.6


def test_exit_vector_follows_the_mouth_when_it_moves():
    """The same ligand in a shell opening along -z must give the opposite vector — i.e. the geometry is
    reading the protein, not a coordinate convention."""
    res = st.analyse_site(_shell_pocket("-z"), [_atom(0, 0, 0), _atom(1.4, 0, 0)])
    assert res["exit_vector"]["direction"][2] < -0.85


def test_burial_discriminates_pocket_from_flat_surface():
    lig = [_atom(0, 0, 0), _atom(1.4, 0, 0), _atom(0, 1.4, 0)]
    buried = st.analyse_site(_shell_pocket("+z"), lig)["ligand_burial"]["buried_fraction"]
    # a flat slab well below the ligand: contact, but no pocket
    slab = [_atom(i * 2.0 - 20, j * 2.0 - 20, -5.0) for i in range(21) for j in range(21)]
    flat = st.analyse_site(slab, lig)["ligand_burial"]["buried_fraction"]
    assert buried > 0.6 > flat
    assert flat < st.GATES["G2_ligand_is_pocket_bound"]["threshold"] <= buried


def test_open_solid_angle_fraction_is_larger_on_an_exposed_site():
    lig = [_atom(0, 0, 0), _atom(1.4, 0, 0)]
    slab = [_atom(i * 2.0 - 20, j * 2.0 - 20, -5.0) for i in range(21) for j in range(21)]
    enclosed = st.analyse_site(_shell_pocket("+z"), lig)["exit_vector"]["open_solid_angle_fraction_15A"]
    exposed = st.analyse_site(slab, lig)["exit_vector"]["open_solid_angle_fraction_15A"]
    assert exposed > enclosed


def test_cavity_volume_is_positive_in_a_pocket_and_small_on_a_slab():
    lig = [_atom(0, 0, 0), _atom(1.4, 0, 0)]
    vp = st.analyse_site(_shell_pocket("+z"), lig)["cavity"]["volume_A3"]
    slab = [_atom(i * 2.0 - 20, j * 2.0 - 20, -5.0) for i in range(21) for j in range(21)]
    vs = st.analyse_site(slab, lig)["cavity"]["volume_A3"]
    assert vp > 0
    assert vp > vs


def test_clearance_is_capped_and_monotone():
    prot = [_atom(0, 0, 10.0)]
    g = st.Grid(prot)
    blocked = st._clearance(0, 0, 0, 0, 0, 1, g, prot)
    open_ = st._clearance(0, 0, 0, 0, 0, -1, g, prot)
    assert 6.0 < blocked < 9.0                     # stops just short of the atom + linker radius
    assert open_ == pytest.approx(st.GEOM["ray_max_A"])


def test_a_vdw_contacted_anchor_with_one_open_side_is_not_reported_as_sealed():
    """Regression for the bug that dropped FEM1B at G3.

    Rays used to start 0.25 A from the anchor — INSIDE the anchor atom's own van-der-Waals sphere — so any
    protein atom merely in CONTACT with the anchor (~3.3 A) fell inside the 3.40 A clash radius of that first
    sample in nearly every direction, and a wide-open site reported clearance 0.0. A linker's first atom is
    bonded at ~1.5 A. Controlled reproduction: an atom contacted on five of six sides, wide open on the
    sixth, gave 0.0 A from the centre and 25.0 A from a bond length out.

    The tell in the real data was an internal contradiction: FEM1B's anchor had 14.56 A^2 of solvent-accessible
    surface while max_ray_clearance_A read 0.0."""
    prot = [_atom(3.3, 0, 0), _atom(-3.3, 0, 0), _atom(0, 3.3, 0), _atom(0, -3.3, 0), _atom(0, 0, -3.3)]
    g = st.Grid(prot)
    up = st._clearance(0, 0, 0, 0, 0, 1, g, prot)
    assert up == pytest.approx(st.GEOM["ray_max_A"]), up
    # and starting from the anchor centre still reports it sealed — i.e. the fix is what changes the answer
    assert st._clearance(0, 0, 0, 0, 0, 1, g, prot, t0=st.GEOM["ray_step_A"]) == 0.0


def test_a_genuinely_sealed_site_is_still_sealed_after_the_bond_length_offset():
    """The fix must not open a site that is truly enclosed — otherwise it trades a false negative for a
    false positive, which is worse here because a false positive advances a recruiter."""
    sealed = _shell_pocket("+z", radius=3.3, n=900, mouth_cos=2.0)
    res = st.analyse_site(sealed, [_atom(0, 0, 0)])
    assert res["exit_vector"]["no_exit_path"] is True
    assert res["exit_vector"]["clearance_A"] == 0.0


# ---------------------------------------------------------------------------------------------------------
# structure parsing
# ---------------------------------------------------------------------------------------------------------
PDB = """\
ATOM      1  N   ALA A   1      11.104   6.134  -6.504  1.00 20.00           N
ATOM      2  CA  ALA A   1      11.639   6.055  -5.147  1.00 20.00           C
HETATM    3  C1  LIG A 501      10.000   5.000  -5.000  1.00 20.00           C
HETATM    4  O1  LIG A 501       9.000   5.000  -5.000  1.00 20.00           O
HETATM    5  O   HOH A 601       1.000   1.000   1.000  1.00 20.00           O
ATOM      6  CA  MSE B   7      20.000  20.000  20.000  1.00 20.00           C
END
"""


def test_parse_pdb_splits_polymer_from_ligand_and_drops_water(tmp_path):
    p = tmp_path / "x.pdb"
    p.write_text(PDB)
    prot, het = st.parse_structure(str(p))
    assert len(prot) == 3                                     # 2 ALA + 1 MSE (selenomethionine is polymer)
    assert list(het) == [("A", "LIG", 501)]                   # water excluded
    assert len(het[("A", "LIG", 501)]) == 2


CIF = """\
data_TEST
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.auth_seq_id
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.auth_comp_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM   1 N N   . ALA A 1 11.104 6.134 -6.504 ALA A 1
HETATM 2 C C1  . LIG A 501 10.000 5.000 -5.000 LIG A 1
HETATM 3 O O   . HOH A 601 1.000 1.000 1.000 HOH A 1
ATOM   4 C CA  . ALA A 2 12.000 6.000 -5.000 ALA A 2
#
"""


def test_parse_cif_reads_atom_site(tmp_path):
    p = tmp_path / "x.cif"
    p.write_text(CIF)
    prot, het = st.parse_structure(str(p))
    assert len(prot) == 1                                     # model 2 row is excluded
    assert list(het) == [("A", "LIG", 501)]


# ---------------------------------------------------------------------------------------------------------
# linker-bearing-analogue classification
# ---------------------------------------------------------------------------------------------------------
def _entry(pdb_id, mw, others=()):
    return {"pdb_id": pdb_id, "distinct_uniprot_accessions": ["P1"] + list(others),
            "candidate_ligands": [{"ccd": "LIG", "formula_weight": mw}]}


def test_linker_analogue_tiers():
    assert st.classify_linker_analogue([], "P1")["label"] == "none"
    assert st.classify_linker_analogue([_entry("1AAA", 300.0)], "P1")["label"] == "handle_only"
    assert st.classify_linker_analogue([_entry("1AAA", 700.0)], "P1")["label"] == "bivalent_binary"
    t = st.classify_linker_analogue([_entry("1AAA", 700.0), _entry("2BBB", 900.0, ["P2"])], "P1")
    assert t["label"] == "solved_ternary" and t["tier"] == 3
    assert t["evidence_pdb_ids_ternary"] == ["2BBB"]


# ---------------------------------------------------------------------------------------------------------
# the preregistered downselect
# ---------------------------------------------------------------------------------------------------------
def _rec(tier=2, clearance=20.0, cone=0.9, burial=0.8, res=1.5, open15=0.5):
    return {
        "staged_structures": [{"pdb_id": "1XXX", "resolution_A": res, "experimental_methods": ["X-RAY"],
                               "is_primary": True, "ligand": {"ccd": "LIG"}}],
        "linker_bearing_analogue": {"tier": tier, "label": "t"},
        "ligandability": {"ligand_burial": {"buried_fraction": burial},
                          "exit_vector": {"clearance_A": clearance, "cone_openness_30deg": cone,
                                          "open_solid_angle_fraction_15A": open15}},
    }


def test_gate_failures_are_recorded_with_the_gate_that_failed():
    recs = {"A": _rec(), "NOSTRUCT": {"staged_structures": [], "linker_bearing_analogue": {"tier": 0},
                                      "ligandability": {}},
            "FLAT": _rec(burial=0.2), "SEALED": _rec(clearance=3.0, cone=0.0)}
    ds = st.downselect(recs)
    failed = {d["recruiter"]: d.get("gate_failed") for d in ds["dropped"] if d["stage"] == "gate"}
    assert failed["NOSTRUCT"] == "G1_public_ligand_bound_structure"
    assert failed["FLAT"] == "G2_ligand_is_pocket_bound"
    assert failed["SEALED"] == "G3_linker_can_leave"
    assert recs["A"]["decision"] == "ADVANCE"


def test_low_resolution_fails_G1_but_nmr_does_not():
    recs = {"LOWRES": _rec(res=3.6)}
    st.downselect(recs)
    assert recs["LOWRES"]["gates"]["G1_public_ligand_bound_structure"]["pass"] is False
    nmr = _rec(res=None)
    nmr["staged_structures"][0]["experimental_methods"] = ["SOLUTION NMR"]
    recs = {"NMR": nmr}
    st.downselect(recs)
    assert recs["NMR"]["gates"]["G1_public_ligand_bound_structure"]["pass"] is True


def test_cap_is_two_and_the_overflow_is_logged_not_silent():
    """Four recruiters on the front (each best on a different axis) -> exactly 2 advance and the other 2
    are dropped WITH a reason. A silent top-N is the failure mode nr4a3-program-map.md names explicitly."""
    recs = {"A": _rec(tier=3, clearance=20.0, cone=0.9, open15=0.2),     # best analogue tier
            "B": _rec(tier=2, clearance=20.0, cone=0.9, open15=0.9),     # best openness
            "C": _rec(tier=1, clearance=20.0, cone=0.95, open15=0.5),    # best exit quality
            "D": _rec(tier=0, clearance=20.0, cone=0.8, open15=0.6)}
    del recs["D"]["linker_bearing_analogue"]
    recs["D"]["linker_bearing_analogue"] = {"tier": 0, "label": "none"}
    ds = st.downselect(recs)
    assert len(ds["advanced"]) == 2
    non_advanced = set(recs) - set(ds["advanced"])
    assert {d["recruiter"] for d in ds["dropped"]} == non_advanced
    assert all(d["reason"] for d in ds["dropped"])


def test_a_single_front_member_is_backfilled_so_the_e3_is_a_controlled_variable():
    """When one recruiter dominates outright the front is a singleton. Advancing only it would leave the E3
    an uncontrolled variable downstream, so the second slot is backfilled AND labelled as backfilled."""
    recs = {n: _rec(tier=t, open15=o) for n, t, o in
            [("A", 3, 0.9), ("B", 3, 0.8), ("C", 3, 0.7)]}
    ds = st.downselect(recs)
    assert ds["pareto_front"] == ["A"]
    assert ds["advanced"] == ["A", "B"]
    assert ds["backfilled_for_e3_choice_sensitivity"] == ["B"]
    assert "advance_note" in recs["B"] and recs["B"]["decision"] == "ADVANCE"
    assert {d["recruiter"] for d in ds["dropped"]} == {"C"}


def test_pareto_front_excludes_a_dominated_recruiter():
    recs = {"GOOD": _rec(tier=3, clearance=20.0, cone=0.9, open15=0.9),
            "WORSE": _rec(tier=1, clearance=9.0, cone=0.35, open15=0.1)}
    recs["ALSO"] = _rec(tier=1, clearance=9.0, cone=0.35, open15=0.05)
    ds = st.downselect(recs)
    assert ds["pareto_front"] == ["GOOD"]
    # WORSE is Pareto-dominated but backfills the second slot (E3-choice sensitivity); ALSO, dominated by
    # BOTH, is dropped at the pareto stage with a reason.
    assert ds["backfilled_for_e3_choice_sensitivity"] == ["WORSE"]
    assert [d["stage"] for d in ds["dropped"] if d["recruiter"] == "ALSO"] == ["pareto"]


def test_availability_is_never_a_drop_reason():
    """nr4a3-program-map.md RUNG 5a: all widened arms are broadly expressed, so no recruiter may be dropped with
    'not expressed'. Assert it structurally rather than trusting the prose."""
    recs = {"A": _rec(), "B": _rec(tier=1, open15=0.1), "C": _rec(burial=0.1)}
    ds = st.downselect(recs)
    assert ds["availability_assertion"]["verified"] is True
    for d in ds["dropped"]:
        assert d["availability_was_not_a_factor"] is True
        assert "express" not in d["reason"].lower()


def test_no_tunable_scalar_in_the_rule():
    """The rule must be gates + Pareto + a fixed lexicographic tiebreak (STRATEGY validation requirement 5),
    never a weighted sum whose weights could be tuned to the answer."""
    ds = st.downselect({"A": _rec()})
    assert set(ds["rule"]) == {"gates", "pareto_axes", "tiebreak_lexicographic", "cap", "backfill",
                               "preregistered"}
    assert "weight" not in json_dumps_lower(ds["rule"])


def json_dumps_lower(obj):
    import json
    return json.dumps(obj).lower()


def test_schema_documents_every_top_level_recruiter_field():
    """Lane 2 builds against _schema; a field that exists in the data but not in the schema is a silent
    contract break."""
    documented = set(st.SCHEMA_DOC["recruiters.<GENE>"])
    produced = {"gene", "aliases", "e3_class", "arm", "incumbent_recruiter", "uniprot", "rcsb_search",
                "n_entries_screened", "staged_structures", "linker_bearing_analogue", "ligandability",
                "gates", "axes", "decision", "_status"}
    undocumented = produced - documented - {"aliases", "incumbent_recruiter", "rcsb_search",
                                            "n_entries_screened", "_status"}
    assert not undocumented, f"undocumented in SCHEMA_DOC: {sorted(undocumented)}"


def test_exit_quality_is_zero_when_geometry_is_missing():
    assert st._exit_quality({}) == 0.0
    assert st._exit_quality({"exit_vector": {}}) == 0.0


def test_fib_sphere_is_unit_length():
    for (x, y, z) in st._fib_sphere(64):
        assert math.isclose(math.sqrt(x * x + y * y + z * z), 1.0, abs_tol=1e-9)


def test_fully_enclosed_site_reports_no_exit_path_not_an_arbitrary_vector():
    """A ligand with no route to solvent must be FLAGGED, not handed a meaningless direction.

    Regression for a real degeneracy found 2026-07-25 by running the geometry on the repo's own AF2 NR4A3
    model with a pseudo-ligand at the (closed) cryptic pocket: with max clearance 0.0, the near-maximal tie
    test `c >= 0.95 * cmax` accepted ALL 512 directions, whose solid-angle centroid is ~the zero vector, and
    the code then fell back to an arbitrary argmax — reporting a confident-looking unit vector next to a 0.0
    clearance. A meaningless vector wearing the same field name as a real one is the failure mode."""
    # mouth_cos > 1 carves nothing, and a 3.3 A shell radius leaves no room for a 1.7 A linker atom in ANY
    # direction: max clearance is exactly 0.0, which is the degenerate case.
    sealed = _shell_pocket("+z", radius=3.3, n=900, mouth_cos=2.0)
    res = st.analyse_site(sealed, [_atom(0, 0, 0)])
    ev = res["exit_vector"]
    assert ev["no_exit_path"] is True
    assert ev["clearance_A"] <= st.GEOM["ray_step_A"]
    assert ev["n_near_maximal_directions"] == 0
    assert abs(sum(c * c for c in ev["direction"]) - 1.0) < 1e-6      # still a unit vector, but declared
    recs = {"SEALED": {"staged_structures": [{"pdb_id": "1XXX", "resolution_A": 1.5,
                                              "experimental_methods": ["X-RAY"], "is_primary": True,
                                              "ligand": {"ccd": "LIG"}}],
                       "linker_bearing_analogue": {"tier": 3},
                       "ligandability": {"ligand_burial": {"buried_fraction": 0.99},
                                         "exit_vector": ev}}}
    ds = st.downselect(recs)
    assert [d["gate_failed"] for d in ds["dropped"]] == ["G3_linker_can_leave"]


def _full_entry(pdb_id, res, mw, uniprots, ccd="LIG"):
    return {"pdb_id": pdb_id, "resolution_A": res, "distinct_uniprot_accessions": list(uniprots),
            "candidate_ligands": [{"ccd": ccd, "formula_weight": mw}]}


def test_geometry_frame_prefers_a_partner_free_structure_even_at_worse_resolution():
    """A ternary/glue entry is the wrong frame for burial and the exit vector: the PROTAC would be scored
    against half the protein that buries it, and the partner occupies the orientation space being measured.
    So a partner-free entry wins even when a ternary entry has better resolution and a bigger ligand."""
    arm = {"P_RECRUITER", "P_ADAPTOR"}
    entries = [_full_entry("TERN", 1.5, 900.0, ["P_RECRUITER", "P_ADAPTOR", "P_TARGET"]),
               _full_entry("BINARY", 2.4, 350.0, ["P_RECRUITER", "P_ADAPTOR"])]
    staged = st.select_staged(entries, arm)
    assert staged[0]["pdb_id"] == "BINARY" and staged[0]["is_primary"] is True
    assert staged[1]["pdb_id"] == "TERN" and staged[1].get("is_primary") is False
    assert staged[1]["partner_uniprots"] == ["P_TARGET"]
    # an obligate arm subunit is NOT a partner
    assert staged[0]["has_partner_protein"] is False


def test_a_peptide_fragment_entity_is_not_chosen_as_the_geometry_frame():
    """A pocket and an exit vector measured on a 20-residue degron peptide describe nothing. But full-length
    coverage must NOT be ranked on: a WD40/Kelch domain construct is the correct object at low coverage."""
    arm = {"P_RECRUITER"}
    pep = _full_entry("PEPT", 1.2, 400.0, ["P_RECRUITER"])
    pep["recruiter_entity_length"] = 18
    dom = _full_entry("DOMAIN", 2.6, 400.0, ["P_RECRUITER"])
    dom["recruiter_entity_length"] = 320
    staged = st.select_staged([pep, dom], arm, uniprot_length=1500)
    assert staged[0]["pdb_id"] == "DOMAIN"                       # despite worse resolution
    assert staged[0]["recruiter_uniprot_coverage_fraction"] == 0.213   # low coverage, still correct
    assert staged[0]["recruiter_entity_is_peptide_fragment"] is False
    assert staged[1]["recruiter_entity_is_peptide_fragment"] is True


def test_a_glue_recruiter_with_only_ternary_structures_still_stages_and_is_flagged():
    arm = {"P_RECRUITER", "P_ADAPTOR"}
    entries = [_full_entry("GLUE", 2.0, 400.0, ["P_RECRUITER", "P_ADAPTOR", "P_SUBSTRATE"])]
    staged = st.select_staged(entries, arm)
    assert staged[0]["pdb_id"] == "GLUE" and staged[0]["has_partner_protein"] is True


def test_g1_distinguishes_no_structure_at_all_from_no_liganded_structure():
    """Two different findings that would otherwise read identically in the dropped-set log: a recruiter
    nobody has crystallised, versus one that is well characterised but never with a ligand."""
    bare = {"staged_structures": [], "linker_bearing_analogue": {"tier": 0}, "ligandability": {},
            "rcsb_search": {"n_hits_any_structure": 0, "total_count_any_structure": 0}}
    apo = {"staged_structures": [], "linker_bearing_analogue": {"tier": 0}, "ligandability": {},
           "rcsb_search": {"n_hits_any_structure": 4, "example_apo_entries": ["1AAA", "2BBB"]}}
    g_bare, _ = st.evaluate_gates(bare)
    g_apo, _ = st.evaluate_gates(apo)
    assert "no deposited structure of this protein at all" in \
        g_bare["G1_public_ligand_bound_structure"]["observed"]
    assert "none carries a usable" in g_apo["G1_public_ligand_bound_structure"]["observed"]
    assert "1AAA" in g_apo["G1_public_ligand_bound_structure"]["observed"]


def test_bridging_demotes_tier3_when_the_ligand_touches_only_one_protein(monkeypatch, tmp_path):
    """Entry-level co-presence of a second protein is NOT bridging. A crystallisation partner, or a ligand
    bound to only one of the two chains, would pass the entry-level tier-3 screen; the coordinates must say
    the ligand actually contacts both."""
    # chain A = recruiter, chain B = partner 30 A away; the ligand sits on A only.
    lines = []
    n = 0
    for i in range(6):
        n += 1
        lines.append("ATOM  {:5d}  CA  ALA A{:4d}    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i + 1, 0.0, i * 2.0, 0.0))
    for i in range(6):
        n += 1
        lines.append("ATOM  {:5d}  CA  ALA B{:4d}    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i + 1, 40.0, i * 2.0, 0.0))
    for i in range(3):
        n += 1
        lines.append("HETATM{:5d}  C{:d}  BIG A 900    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i, 3.0, i * 1.5, 0.0))
    p = tmp_path / "1TST.pdb"
    p.write_text("\n".join(lines) + "\nEND\n")
    monkeypatch.setattr(st, "download_structure", lambda pid, out_dir=None: (str(p), "test"))

    rec = {"arm_component_accessions": ["P_REC"],
           "linker_bearing_analogue": {"tier": 3, "label": "solved_ternary",
                                       "evidence_pdb_ids_ternary": ["1TST"]},
           "staged_structures": [{"pdb_id": "1TST", "recruiter_auth_asym_ids": ["A"],
                                  "polymer_entities": [{"uniprot_ids": ["P_REC"], "auth_asym_ids": ["A"]},
                                                       {"uniprot_ids": ["P_OTHER"],
                                                        "auth_asym_ids": ["B"]}],
                                  "candidate_ligands": [{"ccd": "BIG", "formula_weight": 900.0}]}]}
    st.verify_bridging(rec, {"P_REC"})
    lb = rec["linker_bearing_analogue"]
    assert lb["tier"] == 2 and lb["label"] == "bivalent_binary"
    assert "tier_demoted" in lb
    assert lb["bridging_check"][0]["contacts_recruiter"] > 0
    assert lb["bridging_check"][0]["contacts_partner"] == 0


def test_bridging_keeps_tier3_when_the_ligand_touches_both(monkeypatch, tmp_path):
    lines, n = [], 0
    for i in range(4):
        n += 1
        lines.append("ATOM  {:5d}  CA  ALA A{:4d}    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i + 1, 0.0, i * 2.0, 0.0))
    for i in range(4):
        n += 1
        lines.append("ATOM  {:5d}  CA  ALA B{:4d}    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i + 1, 9.0, i * 2.0, 0.0))
    for i in range(4):        # a ligand spanning the 9 A gap, in contact with both chains
        n += 1
        lines.append("HETATM{:5d}  C{:d}  BIG A 900    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i, 2.0 + i * 1.7, 0.0, 0.0))
    p = tmp_path / "2TST.pdb"
    p.write_text("\n".join(lines) + "\nEND\n")
    monkeypatch.setattr(st, "download_structure", lambda pid, out_dir=None: (str(p), "test"))
    rec = {"arm_component_accessions": ["P_REC"],
           "linker_bearing_analogue": {"tier": 3, "label": "solved_ternary",
                                       "evidence_pdb_ids_ternary": ["2TST"]},
           "staged_structures": [{"pdb_id": "2TST", "recruiter_auth_asym_ids": ["A"],
                                  "polymer_entities": [{"uniprot_ids": ["P_REC"], "auth_asym_ids": ["A"]},
                                                       {"uniprot_ids": ["P_OTHER"],
                                                        "auth_asym_ids": ["B"]}],
                                  "candidate_ligands": [{"ccd": "BIG", "formula_weight": 900.0}]}]}
    st.verify_bridging(rec, {"P_REC"})
    lb = rec["linker_bearing_analogue"]
    assert lb["tier"] == 3 and "tier_demoted" not in lb
    assert lb["bridging_check"][0]["bridges"] is True


def test_load_advanced_is_a_stable_consumer_contract_that_carries_caveats(tmp_path):
    """Lane 2 builds against load_advanced(). Two things it must guarantee: the exit-vector frame is present
    under stable keys, and a recruiter measured on a compromised frame arrives WITH the caveat attached
    rather than looking clean."""
    doc = {
        "downselect": {"advanced": ["GOOD", "MEH"], "backfilled_for_e3_choice_sensitivity": ["MEH"]},
        "recruiters": {
            "GOOD": {"uniprot": {"accession": "P1"}, "e3_class": "cls",
                     "linker_bearing_analogue": {"tier": 3},
                     "staged_structures": [{"pdb_id": "1AAA", "resolution_A": 1.5, "is_primary": True,
                                            "ligand": {"ccd": "LIG"}, "recruiter_auth_asym_ids": ["A"]}],
                     "ligandability": {"coordinate_source": "biological assembly 1 (mmCIF)",
                                       "ligand_burial": {"buried_fraction": 0.8},
                                       "occluder_set": {"chains_present_in_frame": ["A", "B"]},
                                       "exit_vector": {"anchor_xyz": [1.0, 2.0, 3.0],
                                                       "direction": [0, 0, 1], "clearance_A": 20.0,
                                                       "cone_openness_30deg": 0.9,
                                                       "open_solid_angle_fraction_15A": 0.4,
                                                       "no_exit_path": False}}},
            "MEH": {"uniprot": {"accession": "P2"}, "e3_class": "cls",
                    "linker_bearing_analogue": {"tier": 1},
                    "staged_structures": [{"pdb_id": "2BBB", "resolution_A": 2.9, "is_primary": True,
                                           "ligand": {"ccd": "LG2"}, "recruiter_auth_asym_ids": ["C"]}],
                    "ligandability": {"coordinate_source": "asymmetric unit (mmCIF)",
                                      "measured_with_partner_protein_removed": True,
                                      "ligand_burial": {"buried_fraction": 0.6},
                                      "occluder_set": {"chains_present_in_frame": ["C"]},
                                      "exit_vector": {"anchor_xyz": [0, 0, 0], "direction": [1, 0, 0],
                                                      "clearance_A": 12.0, "cone_openness_30deg": 0.5,
                                                      "open_solid_angle_fraction_15A": 0.2,
                                                      "no_exit_path": False}}}},
    }
    p = tmp_path / "staging.json"
    p.write_text(json.dumps(doc))
    rows = st.load_advanced(str(p))
    assert [r["gene"] for r in rows] == ["GOOD", "MEH"]           # ranked order preserved
    assert rows[0]["anchor_xyz"] == [1.0, 2.0, 3.0] and rows[0]["exit_direction"] == [0, 0, 1]
    assert rows[0]["caveats"] == []                               # a clean frame carries none
    assert rows[1]["backfilled"] is True
    assert any("partly formed by the partner" in c for c in rows[1]["caveats"])
    assert any("not a biological assembly" in c for c in rows[1]["caveats"])


def test_bridging_reaches_evidence_entries_that_are_not_in_the_staged_set(monkeypatch, tmp_path):
    """Once staging began preferring partner-free frames, the tier-3 evidence entry stopped being in the
    staged top-8 for exactly the recruiters that have many binary structures — so bridging silently went
    unverified for VHL, CRBN, BIRC2 and DCAF1 while still deciding the top lexicographic key. The evidence
    entries' metadata is now carried on the record so verification does not depend on staging."""
    lines, n = [], 0
    for i in range(4):
        n += 1
        lines.append("ATOM  {:5d}  CA  ALA A{:4d}    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i + 1, 0.0, i * 2.0, 0.0))
    for i in range(4):
        n += 1
        lines.append("ATOM  {:5d}  CA  ALA B{:4d}    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i + 1, 9.0, i * 2.0, 0.0))
    for i in range(4):
        n += 1
        lines.append("HETATM{:5d}  C{:d}  BIG A 900    {:8.3f}{:8.3f}{:8.3f}  1.00  0.00           C"
                     .format(n, i, 2.0 + i * 1.7, 0.0, 0.0))
    p = tmp_path / "3TST.pdb"
    p.write_text("\n".join(lines) + "\nEND\n")
    monkeypatch.setattr(st, "download_structure", lambda pid, out_dir=None: (str(p), "test"))
    rec = {"arm_component_accessions": ["P_REC"],
           # note: staged_structures deliberately does NOT contain 3TST
           "staged_structures": [{"pdb_id": "9BIN", "is_primary": True}],
           "linker_bearing_analogue": {
               "tier": 3, "label": "solved_ternary", "evidence_pdb_ids_ternary": ["3TST"],
               "_evidence_entries": [{"pdb_id": "3TST", "recruiter_auth_asym_ids": ["A"],
                                      "polymer_entities": [{"uniprot_ids": ["P_REC"],
                                                            "auth_asym_ids": ["A"]},
                                                           {"uniprot_ids": ["P_OTHER"],
                                                            "auth_asym_ids": ["B"]}],
                                      "candidate_ligands": [{"ccd": "BIG", "formula_weight": 900.0}]}]}}
    st.verify_bridging(rec, {"P_REC"})
    lb = rec["linker_bearing_analogue"]
    assert lb["bridging_check"], "evidence entry outside the staged set must still be checked"
    assert lb["bridging_check"][0]["bridges"] is True
    assert lb["tier"] == 3


def test_base_chain_matches_assembly_symmetry_copies_to_their_entity():
    assert st.base_chain("A") == "A"
    assert st.base_chain("A-2") == "A"
    assert st.base_chain("") == ""


def test_an_open_site_is_not_flagged_no_exit_path():
    res = st.analyse_site(_shell_pocket("+z"), [_atom(0, 0, 0), _atom(1.4, 0, 0)])
    assert res["exit_vector"]["no_exit_path"] is False
