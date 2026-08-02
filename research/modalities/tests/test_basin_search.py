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


def test_pick_ligand_refuses_a_ligand_bound_to_an_OBLIGATE_PARTNER_rather_than_the_recruiter():
    """THE THIRD BUG THIS ENCODES, and the only one that reached a committed number.

    The receptor BODY is the recruiter plus its obligate partners (Elongin B/C for VHL, DDB1 for CRBN), and
    both of pick_ligand's tests were written against that body — so a fragment bound to a PARTNER passed,
    and produced an 'E3 exit vector' that is nowhere near the E3 ligand site. Staging VHL from 6GMN did
    exactly that: the chosen F4E fragment's entire 4.5 A lining is eight Elongin C residues and it lies
    6.87 A from the nearest VHL atom, giving an exit vector 51.4 A from the one MZ1 occupies in the intact
    assembly 8R5H and a transfer anchor at 69.9 A against a directly measured 30.8 A.

    Without `recruiter_chains` the old (permissive) behaviour is preserved, so this is additive."""
    recruiter = _fake_prot("A", 10, (0.0, 0.0, 0.0))            # CAs at x = 0..27, y = z = 0
    partner = _fake_prot("B", 10, (0.0, 60.0, 0.0))             # an obligate partner, 60 A away in y
    body = {"A", "B"}
    on_partner = [{"name": f"P{i}", "resname": "LIG", "chain": "B", "resid": 201, "icode": " ",
                   "xyz": (3.0 * i, 63.0, 0.0), "elem": "C"} for i in range(14)]
    # permissive (old) behaviour: eligible, because it touches the BODY
    assert S.pick_ligand(recruiter + partner, on_partner, body) is not None
    # with the recruiter named, it is refused — the whole point
    assert S.pick_ligand(recruiter + partner, on_partner, body, {"A"}) is None
    # and a genuine recruiter-bound ligand still passes, carrying the measured contact distance
    on_recruiter = [{"name": f"R{i}", "resname": "LIG", "chain": "A", "resid": 301, "icode": " ",
                     "xyz": (3.0 * i, 3.0, 0.0), "elem": "C"} for i in range(14)]
    got = S.pick_ligand(recruiter + partner, on_recruiter, body, {"A"})
    assert got is not None
    assert got["ligand_min_dist_to_recruiter_A"] == pytest.approx(3.0, abs=0.01)
    # a bigger partner-bound ligand must not outrank a smaller recruiter-bound one, because size is the
    # tie-break and the partner-bound group is now excluded before the comparison ever happens
    got2 = S.pick_ligand(recruiter + partner, on_recruiter + on_partner, body, {"A"})
    assert got2["chain"] == "A" and got2["resid"] == 301


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


def _meta(term_a=False, term_b_rank=0, nominal=0.0, reach_beyond_gate=False):
    if term_a:
        ta = {"C397": {"max_fraction_reachable": 1.0, "max_fraction_reachable_at_gate": 0.8,
                       "min_linker_atoms": 10, "n_poses_reachable": 3}}
    elif reach_beyond_gate:
        # reachable only at the permissive SAMPLING ceiling, not at a practical linker length
        ta = {"C397": {"max_fraction_reachable": 1.0, "max_fraction_reachable_at_gate": 0.0,
                       "min_linker_atoms": 19, "n_poses_reachable": 0}}
    else:
        ta = {"C397": {"max_fraction_reachable": 0.0, "max_fraction_reachable_at_gate": 0.0,
                       "min_linker_atoms": 99, "n_poses_reachable": 0}}
    return {"term_a_union": ta, "term_b_best_rank": term_b_rank,
            "stability_surrogate_nominal_delta_range": [nominal - 1.0, nominal]}


def test_term_a_limb_is_read_at_a_practical_linker_length_not_the_sampling_ceiling():
    """At the 20-atom sampling ceiling the focal-sum criterion admits almost any cysteine near the anchor
    midpoint, so 'reachable' would be nearly free and term (a) could not fail. A gate that cannot fail is not
    a gate, so the categorical limb is read at the practical linker length."""
    assert B.tier2_verdict([_meta(reach_beyond_gate=True)], 1)["basis"] == "NONE"
    assert B.tier2_verdict([_meta(term_a=True)], 1)["basis"] == "CATEGORICAL"


def test_tier2_gate_is_a_conjunction_and_labels_a_nominal_only_pass_as_weaker():
    """nr4a3-program-map.md's rule is 'no categorical handle AND no nominal discrimination => STOP', so a GO needs only
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


def test_assembly_copy_selection_picks_one_coherent_copy_not_both():
    """THE BUG THIS ENCODES. 5T35 deposits TWO copies of VHL-EloB-EloC. Taking every chain annotated as one
    of those three proteins gives a 'receptor body' that is literally two complexes with a void between them,
    and it also lets the bridge pair VHL from one copy with Elongin C from the other — which is exactly what
    drove the joint superposition RMSDs to 5.2-7.3 A and rejected every VHL scaffold candidate. Neither
    symptom announces itself as a chain-selection problem."""
    prot = []
    for i in range(40):
        prot.append({"name": "CA", "resname": "ALA", "chain": "A", "resid": i, "icode": " ",
                     "xyz": (i * 1.0, 0.0, 0.0), "elem": "C"})
        prot.append({"name": "CA", "resname": "ALA", "chain": "B", "resid": i, "icode": " ",
                     "xyz": (i * 1.0, 4.0, 0.0), "elem": "C"})
    for i in range(40):                                       # a second copy, 300 A away
        prot.append({"name": "CA", "resname": "ALA", "chain": "C", "resid": i, "icode": " ",
                     "xyz": (300.0 + i * 1.0, 0.0, 0.0), "elem": "C"})
        prot.append({"name": "CA", "resname": "ALA", "chain": "D", "resid": i, "icode": " ",
                     "xyz": (300.0 + i * 1.0, 4.0, 0.0), "elem": "C"})
    sel, info = S.select_assembly_copy(prot, {"VHL": {"A", "C"}, "ELOC": {"B", "D"}})
    assert sel is not None and info["ok"]
    assert (sel["VHL"], sel["ELOC"]) in (("A", "B"), ("C", "D"))       # never A with D
    assert info["n_contacting_pairs"] == 1


def test_assembly_copy_selection_refuses_a_real_choice_but_flags_a_forced_one():
    """Two different situations that must NOT be conflated. When there are several copies to choose between
    and none is coherent, refusing is right. When there is only ONE chain combination available, refusing
    gains nothing — there is no alternative to fall back to — so it is accepted and its incoherence is
    FLAGGED instead of hidden."""
    prot = []
    for ch, x in (("A", 0.0), ("B", 500.0), ("C", 1000.0), ("D", 1500.0)):
        for i in range(30):
            prot.append({"name": "CA", "resname": "ALA", "chain": ch, "resid": i, "icode": " ",
                         "xyz": (x + i, 0.0, 0.0), "elem": "C"})
    sel, info = S.select_assembly_copy(prot, {"VHL": {"A", "C"}, "ELOC": {"B", "D"}})
    assert sel is None and "mutually-contacting" in info["reason"]
    forced, finfo = S.select_assembly_copy(prot, {"VHL": {"A"}, "ELOC": {"B"}})
    assert forced == {"VHL": "A", "ELOC": "B"}
    assert finfo["single_copy"] is True and finfo["coherent"] is False
    assert "WARNING" in finfo["_note"]
    lone, linfo = S.select_assembly_copy(prot, {"VHL": {"A"}})
    assert lone == {"VHL": "A"} and linfo["coherent"] is True           # nothing to contact, trivially fine


def test_both_sensitivity_standards_are_reported_and_the_strict_one_stays_the_default():
    """One swept transfer distance (10.0 A) is this file's own SUPERSEDED assumption — the solved assembly
    measured 17.1 A — so requiring the term-(b) category to survive it is requiring it to survive a refuted
    parameter. Narrowing the sweep after a basin failed it would be moving the goalpost, so BOTH standards
    are reported and `sensitivity_robust` keeps pointing at the STRICTER one."""
    sens = {"d10.0_r18.0": 1, "d10.0_r32.0": 5, "d14.0_r18.0": 5, "d14.0_r32.0": 5,
            "d17.0_r18.0": 5, "d17.0_r32.0": 3, "d21.0_r18.0": 5, "d21.0_r32.0": 3}
    cal = {k: v for k, v in sens.items() if 14.0 <= float(k.split("_")[0][1:]) <= 21.0}
    assert min(sens.values()) < 3                       # fails the full sweep, because of the refuted value
    assert min(cal.values()) >= 3                       # holds across the calibrated range
    assert set(cal) == {"d14.0_r18.0", "d14.0_r32.0", "d17.0_r18.0", "d17.0_r32.0",
                        "d21.0_r18.0", "d21.0_r32.0"}
    assert 10.0 in B.PARAMS["lysine_transfer_sweep_A"]   # the superseded value stays IN the reported sweep


def test_monomeric_ring_arms_survive_the_accession_gather(tmp_path):
    """THE BUG THIS ENCODES. A monomeric RING E3 has no cullin scaffold and no bridge, so both fields are
    legitimately None — and the very first line of stage_arm concatenated them into a list. BIRC2 and MDM2,
    the two recruiters the E3 lane's downselect actually ADVANCED, both died on `list + None` before ever
    reaching the guard written to handle them."""
    reg = {"recruiters": {
        "BIRC2": {"uniprot": {"accession": "Q13490"}, "e3_class": "monomeric RING E3 (BIR/RING)",
                  "arm": "RING_BIRC2", "staged_structures": [{"pdb_id": "4HY4", "is_primary": True}]},
        "VHL": {"uniprot": {"accession": "P40337"}, "e3_class": "CRL2 substrate receptor (BC-box)",
                "arm": "CRL2_VHL", "staged_structures": [{"pdb_id": "5T35", "is_primary": True}]},
        "NOACC": {"uniprot": {"accession": None}, "e3_class": "monomeric RING E3"},
    }}
    p = tmp_path / "lane1.json"
    p.write_text(json.dumps(reg))
    arms = S.arms_from_lane1(str(p))
    assert set(arms) == {"birc2", "vhl"}                       # the unresolved accession is REFUSED, not guessed
    assert arms["birc2"]["e3_architecture"] == "MONOMERIC_RING"
    assert arms["birc2"]["self_ring"] is True
    assert arms["birc2"]["scaffold_needs"] is None and arms["birc2"]["bridge"] is None
    assert arms["vhl"]["e3_architecture"] == "CRL2"
    assert "CUL2" in arms["vhl"]["scaffold_needs"] and "RBX1" in arms["vhl"]["scaffold_needs"]
    # the exact expression that crashed: gathering accessions across all three (possibly-None) fields
    for spec in arms.values():
        keys = set((spec.get("receptor_needs") or []) + (spec.get("scaffold_needs") or [])
                   + (spec.get("bridge") or []))
        assert all(k in S.ACC for k in keys)


def test_zero_hit_search_is_an_answer_not_a_network_failure(monkeypatch):
    """RCSB answers a zero-hit search with 204 No Content and an EMPTY BODY, which urllib treats as SUCCESS —
    so it never reaches the HTTPError branch and json.loads('') raises. That made five legitimately-empty
    'is there a VHL + E2 + ubiquitin structure?' probes each report 'POST failed after 4 tries', turning a
    real negative answer into a fake infrastructure problem."""
    class _Empty:
        def read(self):
            return b""

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    monkeypatch.setattr(S.urllib.request, "urlopen", lambda *a, **k: _Empty())
    assert S._post_json(S.SEARCH_URL, {"query": {}}) == {"result_set": []}
    assert S.search_entries(["P40337", "P51668"]) == []


def test_feasibility_envelope_separates_a_closed_target_from_an_unlucky_recruiter():
    """The distinction a negative result has to make. If term (a) comes back empty it is either because no E3
    body happened to dock where the linker could reach the cysteine — fixable by trying another recruiter —
    or because no credible linker can reach it at all, which no recruiter choice can fix. The envelope is
    E3-independent, so it is an UPPER BOUND no basin can exceed."""
    rng = random.Random(31)
    field = G.SquaredDistanceField([(0.0, 0.0, -50.0)], cell=1.0, clamp=8.0)   # a distant dummy: nothing blocks
    poses = [{"anchor_xyz": [0.0, 0.0, 0.0]}]
    near = {"uniprot_resid": 397, "xyz": (8.0, 0.0, 0.0)}
    far = {"uniprot_resid": 559, "xyz": (300.0, 0.0, 0.0)}
    env = B.term_a_feasibility_envelope(poses, [near, far], field, rng, n_mc=3000)
    n, f = env["per_cysteine"]["C397"], env["per_cysteine"]["C559"]
    assert n["geometrically_closed"] is False
    assert n["shortest_linker_with_any_feasible_anchor"] is not None
    assert f["geometrically_closed"] is True                  # 300 A is beyond any linker: CLOSED, not unlucky
    assert f["shortest_linker_with_any_feasible_anchor"] is None
    # and the bound is monotone in linker length — more linker never reaches less
    fr = [n["by_linker_atoms"][k]["max_over_poses"] for k in sorted(n["by_linker_atoms"])]
    assert fr == sorted(fr)


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


def test_reach_never_reports_a_linker_shorter_than_the_span_it_must_bridge():
    """★ THE 2026-07-25 CORRECTION, pinned on the geometry that exposed it. The published rule was the
    prolate-spheroid RELAXATION |q-a| + |q-b| <= n*rise + 2e; for a nucleophile ON the anchor-anchor segment
    that reduces to `span <= n*rise + 2e`, i.e. it credits the pendant with shortening the SPAN. It cannot —
    the backbone still has to connect a to b.

    Closed form, no fitting: span 20 A, cysteine at its midpoint. The relaxed rule sees focal sum 20, deducts
    2e = 6 and returns ceil(14/1.25) = 12 atoms. The span alone needs ceil(20/1.25) = 16. So the published
    figure was low by 4 atoms on exactly this record, and the corrected one must never sit below the floor.
    """
    pose = {"anchor_xyz": [0.0, 0.0, 0.0]}
    pl = {"anchor_e3": (20.0, 0.0, 0.0)}
    cys = [{"uniprot_resid": 397, "xyz": (10.0, 0.0, 0.0), "unique": True}]
    r = B.electrophile_reach(pl, pose, cys)[0]
    assert r["min_linker_atoms_relaxed_superseded"] == 12          # what RUNG 5a published
    assert r["span_floor_atoms"] == 16
    assert r["min_linker_atoms"] >= r["span_floor_atoms"]          # the constraint no pendant can buy off
    assert r["min_linker_atoms"] >= r["min_linker_atoms_relaxed_superseded"]


def test_reach_is_never_shorter_than_either_published_bound_over_a_grid():
    """Both inequalities are provable (see `linker_design.min_linker_atoms_exact`), so they hold for EVERY
    record the search emits, not just the demonstration geometry. A regression that reintroduced the relaxed
    rule anywhere in the aggregation would break this."""
    pose = {"anchor_xyz": [0.0, 0.0, 0.0]}
    for bx in (6.0, 13.0, 21.0):
        pl = {"anchor_e3": (bx, 0.0, 0.0)}
        cys = [{"uniprot_resid": 397 + i, "xyz": xyz, "unique": True}
               for i, xyz in enumerate([(3.0, 4.0, 0.0), (10.0, 2.0, 1.0), (5.0, 9.0, -2.0),
                                        (bx / 2.0, 0.0, 0.0), (-4.0, 3.0, 2.0)])]
        for r in B.electrophile_reach(pl, pose, cys):
            assert r["min_linker_atoms"] is not None
            assert r["min_linker_atoms"] >= r["span_floor_atoms"]
            assert r["min_linker_atoms"] >= r["min_linker_atoms_relaxed_superseded"]


def test_reach_reports_unreachable_as_null_rather_than_as_a_number():
    """Out of range must read as absent, not as `reach_scan_max_atoms` — a number would be quoted."""
    pose = {"anchor_xyz": [0.0, 0.0, 0.0]}
    pl = {"anchor_e3": (12.0, 0.0, 0.0)}
    cys = [{"uniprot_resid": 559, "xyz": (400.0, 0.0, 0.0), "unique": True}]
    r = B.electrophile_reach(pl, pose, cys)[0]
    assert r["min_linker_atoms"] is None and r["reachable"] is False


def test_term_b_limb_requires_beating_the_null_not_merely_covering_a_unique_lysine():
    """Without a null, 'this basin's transfer zone covers K572' is uninterpretable. If ANY linker-feasible,
    clash-free placement covers a unique lysine at the same rate, the term carries no information and a
    basin that scores well is just a placement that exists — so the gate requires the basin to EXCEED the
    background rate, not merely to reach rank 3."""
    at_background = _meta(term_b_rank=5)
    at_background["term_b_exceeds_background"] = False
    assert B.tier2_verdict([at_background], 1)["basis"] == "NONE"
    above = _meta(term_b_rank=5)
    above["term_b_exceeds_background"] = True
    assert B.tier2_verdict([above], 1)["basis"] == "CATEGORICAL"
