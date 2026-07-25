"""Unit tests for the RUNG-5a mechanism-first orientation-basin search.

Scope discipline: these test the LOGIC that decides things — the exit-vector derivation that anchors the whole
linker-reach restraint, the multi-chain parse that a shared helper gets wrong, the transfer-zone set-membership
classifier, the matched superposition, and the Tier-2 gate's own truth table — each against a hand-constructed
fixture with a known answer. Several encode a specific bug that was found by reading a real run's output, so a
regression is caught by CI rather than by rereading a log.
"""
import json
import math
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import basin_geom as G                      # noqa: E402
import nr4a3_basin_search as B              # noqa: E402
import nr4a3_e3_stage as S                  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
STRUCT = os.path.join(REPO, "results", "nr4a3-matrix")


# --------------------------------------------------------------------- E3-side exit vector (staging)


def _fake_prot(chain, n, base):
    """n pseudo-residues on a line, so distances are trivially checkable."""
    return [{"name": "CA", "resname": "ALA", "chain": chain, "resid": i, "icode": " ",
             "xyz": (base[0] + i * 3.0, base[1], base[2]), "elem": "C"} for i in range(n)]


def test_exit_vector_splits_a_PROTAC_by_which_protein_each_atom_is_closer_to():
    """THE BUG THIS ENCODES. The verified ligand-bound recruiter entries are PROTAC ternaries (5T35 for VHL,
    6BOY for CRBN), so the bound 'ligand' spans E3 + linker + a SECOND warhead. Taking its most exposed atom
    as the E3 exit vector returns a point on the other warhead, tens of angstroms away, and would anchor the
    entire linker-reach restraint in the wrong place."""
    e3 = _fake_prot("A", 10, (0.0, 0.0, 0.0))           # CAs at x = 0,3,..27, y=z=0
    tgt = _fake_prot("B", 10, (0.0, 40.0, 0.0))         # a second protein, 40 A away in y
    # an E3-binding moiety hugging the E3 surface, then a linker climbing in +y toward the other protein
    lig = [{"name": f"W{i}", "resname": "LIG", "chain": "L", "resid": 1, "icode": " ",
            "xyz": (3.0 * i, 3.0, 0.0), "elem": "C"} for i in range(6)]
    lig += [{"name": f"X{i}", "resname": "LIG", "chain": "L", "resid": 1, "icode": " ",
             "xyz": (7.5, y, 0.0), "elem": "C"} for i, y in enumerate([8.0, 14.0, 20.0, 26.0, 32.0, 36.0])]
    got = S.pick_ligand(e3 + tgt, lig, {"A"})
    assert got is not None
    assert got["is_protac_ternary"] is True
    # atoms at y <= 20 are nearer the E3 (surface at y=0); the exit vector is the furthest of THOSE
    assert got["n_heavy_on_e3_side"] == 9                       # 6 warhead + 3 linker atoms
    assert got["exit_atom_name"] == "X2"                        # y = 20, the last E3-side atom
    assert got["exit_atom_dist_to_receptor_A"] == pytest.approx(20.06, abs=0.02)
    # and the far warhead is NOT chosen, which is the entire point
    assert got["exit_atom_dist_to_other_protein_A"] == pytest.approx(20.06, abs=0.02)


def test_exit_vector_distance_is_exact_and_not_clamped_by_the_grid():
    """THE SECOND BUG THIS ENCODES. The first staging run reported BOTH arms' exit exposure as exactly
    8.00 A — the distance field's clamp, not a distance. Past the clamp the argmax is degenerate, so the
    'most exposed atom' was being picked arbitrarily."""
    e3 = _fake_prot("A", 10, (0.0, 0.0, 0.0))
    lig = [{"name": f"W{i}", "resname": "LIG", "chain": "L", "resid": 1, "icode": " ",
            "xyz": (3.0 * i, 3.0, 0.0), "elem": "C"} for i in range(6)]
    lig += [{"name": f"X{i}", "resname": "LIG", "chain": "L", "resid": 1, "icode": " ",
             "xyz": (7.5, 6.0 + 4.0 * i, 0.0), "elem": "C"} for i in range(8)]
    got = S.pick_ligand(e3, lig, {"A"})
    assert got["exit_atom_dist_to_receptor_A"] > 8.0           # would be impossible if clamped
    assert got["exit_atom_dist_to_receptor_A"] == pytest.approx(34.0, abs=0.05)
    assert got["is_protac_ternary"] is False                   # no second protein -> nothing on the far side


def test_pick_ligand_refuses_a_crystallisation_additive_parked_away_from_the_receptor():
    e3 = _fake_prot("A", 10, (0.0, 0.0, 0.0))
    far = [{"name": f"X{i}", "resname": "LIG", "chain": "L", "resid": 1, "icode": " ",
            "xyz": (200.0 + i, 200.0, 200.0), "elem": "C"} for i in range(20)]
    assert S.pick_ligand(e3, far, {"A"}) is None
    tiny = [{"name": f"X{i}", "resname": "LIG", "chain": "L", "resid": 1, "icode": " ",
             "xyz": (3.0 * i, 3.0, 0.0), "elem": "C"} for i in range(5)]
    assert S.pick_ligand(e3, tiny, {"A"}) is None              # below MIN_LIGAND_HEAVY


def test_bridge_keys_by_protein_and_residue_so_two_chains_numbered_from_one_cannot_collide():
    """VHL and Elongin C both number from ~1. Keying the bridge on residue number alone would pair VHL 12
    with Elongin C 12 and produce a confident, meaningless superposition."""
    src = _fake_prot("X", 40, (0.0, 0.0, 0.0)) + _fake_prot("Y", 40, (0.0, 50.0, 0.0))
    dst = _fake_prot("P", 40, (100.0, 0.0, 0.0)) + _fake_prot("Q", 40, (100.0, 50.0, 0.0))
    tr, info = S.bridge_into_frame(src, {"VHL": {"X"}, "ELOC": {"Y"}},
                                   dst, {"VHL": {"P"}, "ELOC": {"Q"}})
    assert tr is not None
    assert info["n_bridge_ca"] == 80                            # both proteins contribute, jointly
    assert info["ca_per_bridge_protein"] == {"VHL": 40, "ELOC": 40}
    assert info["bridge_rmsd_A"] == pytest.approx(0.0, abs=1e-6)


def test_bridge_refuses_rather_than_producing_a_plausible_wrong_frame():
    src = _fake_prot("X", 40, (0.0, 0.0, 0.0))
    dst = _fake_prot("P", 10, (100.0, 0.0, 0.0))
    tr, info = S.bridge_into_frame(src, {"VHL": {"X"}}, dst, {"VHL": {"P"}})
    assert tr is None and "shared bridge residues" in info["reason"]
    # and a genuine geometric mismatch is refused on RMSD, not accepted quietly
    bent = [dict(a, xyz=(a["xyz"][0], a["xyz"][1] + (a["resid"] ** 2) * 0.6, a["xyz"][2]))
            for a in _fake_prot("P", 40, (100.0, 0.0, 0.0))]
    tr2, info2 = S.bridge_into_frame(src, {"VHL": {"X"}}, bent, {"VHL": {"P"}}, max_rmsd=1.0)
    assert tr2 is None and "RMSD" in info2["reason"]


# --------------------------------------------------------------------- multi-chain parsing


def test_multichain_parse_keeps_chains_apart(tmp_path):
    """The atlas's shared `parse_pdb` keys residues by NUMBER ALONE. That is right for a single-chain LBD and
    silently wrong for a multi-chain E3 arm, where VHL/EloB/EloC all number from ~1: two thirds of the
    recruiter would vanish into collided keys."""
    p = tmp_path / "two_chains.pdb"
    lines = []
    for ch, x in (("A", 0.0), ("B", 50.0)):
        for i in (1, 2, 3):
            for nm, dz in (("N", 0.0), ("CA", 1.0), ("C", 2.0), ("CB", 3.0)):
                lines.append("ATOM  %5d %-4s ALA %s%4d    %8.3f%8.3f%8.3f  1.00  0.00           C"
                             % (len(lines) + 1, nm, ch, i, x + i, 0.0, dz))
    p.write_text("\n".join(lines) + "\n")
    order, res = B.parse_multichain_pdb(str(p))
    assert len(order) == 6                                     # 3 residues x 2 chains, none collided
    assert {k[0] for k in order} == {"A", "B"}
    assert res[("A", 1, " ")]["aa"] == "A"


# --------------------------------------------------------------------- transfer-zone classification (term b)


def test_transfer_classification_follows_the_strategy_ordering_exactly():
    uniq = {200, 146}                                          # local ids of K572 / K518
    assert B.classify_transfer({"NR4A3": [200], "NR4A1": [], "NR4A2": []}, uniq)[0] \
        == "unique_only_paralogues_bare"
    assert B.classify_transfer({"NR4A3": [200, 7], "NR4A1": [], "NR4A2": []}, uniq)[0] \
        == "unique_plus_conserved_paralogues_bare"
    assert B.classify_transfer({"NR4A3": [200], "NR4A1": [9], "NR4A2": []}, uniq)[0] == "unique_only"
    assert B.classify_transfer({"NR4A3": [200, 7], "NR4A1": [9], "NR4A2": []}, uniq)[0] \
        == "unique_plus_conserved"
    assert B.classify_transfer({"NR4A3": [7], "NR4A1": [9], "NR4A2": []}, uniq)[0] == "conserved_only"
    assert B.classify_transfer({"NR4A3": [], "NR4A1": [9], "NR4A2": []}, uniq)[0] == "none"
    # and the ordering is strictly monotone, because the gate reads the RANK
    ranks = [B.classify_transfer(c, uniq)[1] for c in (
        {"NR4A3": [], "NR4A1": [], "NR4A2": []},
        {"NR4A3": [7], "NR4A1": [9], "NR4A2": []},
        {"NR4A3": [200, 7], "NR4A1": [9], "NR4A2": []},
        {"NR4A3": [200], "NR4A1": [9], "NR4A2": []},
        {"NR4A3": [200, 7], "NR4A1": [], "NR4A2": []},
        {"NR4A3": [200], "NR4A1": [], "NR4A2": []})]
    assert ranks == sorted(ranks) and len(set(ranks)) == 6


def test_transfer_zone_needs_ring_geometry_and_flags_unreliably_placed_paralogue_lysines():
    rng = random.Random(4)
    pl = {"ring": None, "cullin": None}
    assert B.transfer_zone(pl, {"NR4A3": []}, rng) is None
    pl = {"ring": (0.0, 0.0, 0.0), "cullin": (0.0, 0.0, -40.0)}
    lys = {"NR4A3": [{"local_resid": 200, "xyz": (0.0, 0.0, 25.0), "position_reliable": True}],
           "NR4A1": [{"local_resid": 11, "xyz": (0.0, 0.0, 25.0), "position_reliable": False}]}
    got = B.transfer_zone(pl, lys, rng, ring_r=25.0, transfer_d=10.0, n_e2=32)
    assert got["covered"]["NR4A3"] == [200]
    assert got["covered"]["NR4A1"] == [11]
    assert got["covered_but_unreliably_placed"]["NR4A1"] == [11]


# --------------------------------------------------------------------- accessibility (piece 4)


def test_accessibility_is_zero_for_linkers_shorter_than_the_basin_span():
    """A basin the linker physically cannot span must score exactly zero accessibility, whatever its
    interface looks like — that separation is the whole point of load-bearing piece 4."""
    acc = B.basin_accessibility([15.0, 16.0, 17.0])
    assert acc["density_by_linker_atoms"][5] == 0.0             # 5 atoms = 6.25 A contour: unreachable
    assert acc["best_density"] > 0.0
    assert acc["best_linker_atoms"] >= 15                       # needs a long linker to reach at all
    near = B.basin_accessibility([8.0, 9.0, 10.0])
    assert near["best_linker_atoms"] < acc["best_linker_atoms"]
    # A basin sitting at 22-24 A is essentially inaccessible even to the 20-atom (25 A) ceiling: a chain
    # spans its own contour length only in an exponentially rare fully-extended state. That is a real result
    # about long-span basins, not a numerical artefact, so it is asserted rather than papered over.
    stretched = B.basin_accessibility([22.0, 23.0, 24.0])
    assert stretched["best_density"] < 1e-6 * acc["best_density"]


# --------------------------------------------------------------------- the Tier-2 gate truth table


def _meta(term_a=False, term_b_rank=0, nominal=0.0):
    return {"term_a_union": ({"C397": {"max_fraction_reachable": 1.0, "min_linker_atoms": 10,
                                       "n_poses_reachable": 3}} if term_a else
                             {"C397": {"max_fraction_reachable": 0.0, "min_linker_atoms": 99,
                                       "n_poses_reachable": 0}}),
            "term_b_best_rank": term_b_rank,
            "stability_surrogate_nominal_delta_range": [nominal - 1.0, nominal]}


def test_tier2_gate_is_a_conjunction_and_labels_a_nominal_only_pass_as_weaker():
    """STRATEGY.md's rule is 'no categorical handle AND no nominal discrimination => STOP', so a GO needs only
    one limb — but a categorical GO and a nominal-only GO are NOT the same evidence, and the gate must say so
    rather than laundering a cheap contact-score difference into a mechanism."""
    assert B.tier2_verdict([_meta(term_a=True)], 1)["basis"] == "CATEGORICAL"
    assert B.tier2_verdict([_meta(term_b_rank=5)], 1)["basis"] == "CATEGORICAL"
    assert B.tier2_verdict([_meta(term_b_rank=2)], 1)["basis"] == "NONE"        # rank<3 = no unique lysine
    weak = B.tier2_verdict([_meta(nominal=5.0)], 1)
    assert weak["basis"] == "NOMINAL_ONLY" and weak["pass"] is True
    assert "expect a negative" in weak["verdict"]
    stop = B.tier2_verdict([_meta(nominal=-3.0)], 1)
    assert stop["pass"] is False and stop["basis"] == "NONE" and "NO-GO" in stop["verdict"]
    assert B.tier2_verdict([], 0)["pass"] is False


def test_tier2_gate_prefers_categorical_even_when_a_nominal_basin_also_exists():
    v = B.tier2_verdict([_meta(nominal=9.0), _meta(term_a=True)], 2)
    assert v["basis"] == "CATEGORICAL"
    assert v["n_nominally_discriminating"] == 1 and v["n_exploiting_term_a_electrophile_reach"] == 1


# --------------------------------------------------------------------- matched superposition (real models)


@pytest.mark.skipif(not os.path.exists(os.path.join(STRUCT, "nr4a3-opened.pdb")),
                    reason="matched opened models not present")
def test_matched_superposition_reports_core_and_global_separately_on_the_real_models():
    """The real numbers: a single global fit of all 244 aligned CA pairs gives 6.38 A for NR4A1, which would
    make any paralogue comparison meaningless; the structured core is 203 pairs at 1.73 A. Both must be
    reported, because one says 'the frame is shared' and the other says 'these loops are not comparable'."""
    m3 = B.load_paralogue(os.path.join(STRUCT, "nr4a3-opened.pdb"))
    m1 = B.superpose_paralogue(B.load_paralogue(os.path.join(STRUCT, "nr4a1-opened.pdb")), m3)
    sp = m1["superposition"]
    assert sp["global_all_pair_rmsd_A"] > sp["core_rmsd_A"]
    assert sp["core_rmsd_A"] < 2.5
    assert 0.7 < sp["core_fraction"] < 1.0
    assert sp["post_fit_deviation_A"]["max"] > 10.0            # the discarded loops really are far off
    lys = B.paralogue_lysines(m1)
    assert lys and all("position_reliable" in k for k in lys)
    assert any(k["position_reliable"] for k in lys)


@pytest.mark.skipif(not os.path.exists(os.path.join(STRUCT, "nr4a3-opened.pdb")),
                    reason="matched opened models not present")
def test_reactive_map_reproduces_the_tier0_geometry_from_the_committed_json():
    """Cross-check against the Tier-0 artifact rather than trusting this file's own parse: the unique-cysteine
    and unique-lysine distances to the cryptic pocket must land where nr4a-paralogue-unique-residues.json says
    they do."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uj = os.path.join(here, "nr4a-paralogue-unique-residues.json")
    m3 = B.load_paralogue(os.path.join(STRUCT, "nr4a3-opened.pdb"))
    r = B.load_reactive_map(uj, m3)
    assert {c["uniprot_resid"] for c in r["unique_cysteines"]} == {397, 420, 559}
    assert {k["uniprot_resid"] for k in r["unique_lysines"]} == {518, 572, 592}
    ref = json.load(open(uj))
    ref_d = {c["resnum"]: c["geometry"]["dist_to_cryptic_pocket_A"]
             for c in ref["nr4a3_unique_cysteines"] + ref["nr4a3_unique_lysines"]
             if "local_resid" in (c.get("geometry") or {})}
    for entry in r["unique_cysteines"] + r["unique_lysines"]:
        d = min(G.dist(entry["xyz"], p) for p in r["pocket_points"])
        # Tier-0 measured to the pocket residues' atoms INCLUDING hydrogens (the models carry them); this
        # file measures heavy-atom-only, so its distances are systematically a few tenths larger. Same
        # residues, same pocket, same ordering — the tolerance covers the H difference and nothing more.
        assert -0.01 <= d - ref_d[entry["uniprot_resid"]] < 1.5
    # K572 is the most exposed unique lysine, which is what makes it the term-(b) lead
    k572 = next(k for k in r["unique_lysines"] if k["uniprot_resid"] == 572)
    assert k572["rsa"] > 0.8 and k572["exposed"]


# --------------------------------------------------------------------- pose ensemble (term d)


@pytest.mark.skipif(not os.path.exists(os.path.join(STRUCT, "nr4a3-opened.pdb")),
                    reason="matched opened models not present")
def test_pose_ensemble_anchors_are_outside_the_protein_and_solvent_connected():
    """An 'exit vector' buried in the protein core is not one: no linker leaves from there. Every ensemble
    member must clear the protein AND still clear it 8 A further along its own outward ray."""
    m3 = B.load_paralogue(os.path.join(STRUCT, "nr4a3-opened.pdb"))
    f3 = G.SquaredDistanceField(m3["heavy_xyz"], cell=0.9, clamp=8.0)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = B.load_reactive_map(os.path.join(here, "nr4a-paralogue-unique-residues.json"), m3)
    poses = B.build_pose_ensemble(m3, r, f3, 8, random.Random(3))
    assert len(poses) == 8
    lo, hi = B.PARAMS["pose_anchor_shell_A"]
    for p in poses:
        a = tuple(p["anchor_xyz"])
        assert lo - 0.01 <= p["dist_to_pocket_centroid_A"] <= hi + 0.01
        assert f3.min_dist(a) >= B.PARAMS["pose_min_clearance_A"]
        v = tuple(p["exit_direction"])
        out = (a[0] + v[0] * 8.0, a[1] + v[1] * 8.0, a[2] + v[2] * 8.0)
        assert f3.min_dist(out) >= B.PARAMS["pose_min_clearance_A"]
    # ... and they are spread, not stacked on one spot
    for i in range(len(poses)):
        for j in range(i + 1, len(poses)):
            assert G.dist(tuple(poses[i]["anchor_xyz"]), tuple(poses[j]["anchor_xyz"])) \
                >= B.PARAMS["pose_min_separation_A"] - 1e-6


# --------------------------------------------------------------------- end-to-end on the synthetic arm


@pytest.mark.skipif(not os.path.exists(os.path.join(STRUCT, "nr4a3-opened.pdb")),
                    reason="matched opened models not present")
def test_placements_respect_the_linker_restraint_and_never_clash():
    """The two invariants the whole search rests on: every accepted placement is within linker reach, and
    none of them puts the E3 inside NR4A3."""
    rng = random.Random(9)
    m3 = B.load_paralogue(os.path.join(STRUCT, "nr4a3-opened.pdb"))
    f3 = G.SquaredDistanceField(m3["heavy_xyz"], cell=0.9, clamp=8.0)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = B.load_reactive_map(os.path.join(here, "nr4a-paralogue-unique-residues.json"), m3)
    pose = B.build_pose_ensemble(m3, r, f3, 1, rng)[0]
    arm = B.synthetic_arm(random.Random(1))
    pls, stats = B.sample_placements(arm, pose, f3, rng, 20000)
    assert stats["n_accepted"] > 0
    lmax = G.contour_length_from_atoms(B.PARAMS["linker_max_atoms"], B.PARAMS["linker_rise_per_atom_A"])
    lmin = G.contour_length_from_atoms(B.PARAMS["linker_min_atoms"], B.PARAMS["linker_rise_per_atom_A"])
    for p in pls:
        assert lmin - 1e-6 <= p["span_A"] <= lmax + 1e-6
        assert G.dist(p["anchor_e3"], tuple(pose["anchor_xyz"])) == pytest.approx(p["span_A"], abs=1e-6)
        for q in p["cb"]:
            assert not f3.is_clash(q, B.PARAMS["hard_clash_A"])
        assert p["n_contact"] >= B.PARAMS["min_contact_residues"]
        assert p["n_soft"] <= B.PARAMS["max_soft_clashes"]


def test_electrophile_reach_couples_the_two_tethers_through_one_contour_length():
    """The electrophile rides ON the linker, so reaching a cysteine and spanning to the E3 are paid for out of
    the SAME contour length. That coupling is what makes term (a) a real constraint rather than a free wish."""
    pose = {"anchor_xyz": [0.0, 0.0, 0.0]}
    pl = {"anchor_e3": (20.0, 0.0, 0.0)}
    cys = [{"uniprot_resid": 397, "xyz": (10.0, 0.0, 0.0), "unique": True},      # on the segment
           {"uniprot_resid": 559, "xyz": (10.0, 30.0, 0.0), "unique": True}]     # a big detour
    got = B.electrophile_reach(pl, pose, cys)
    on, off = got[0], got[1]
    assert on["detour_A"] == pytest.approx(0.0)
    assert on["min_linker_atoms"] < off["min_linker_atoms"]
    assert off["detour_A"] > 40.0
    assert on["reachable"] is True and off["reachable"] is False
