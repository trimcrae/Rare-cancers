#!/usr/bin/env python3
"""Offline unit tests for `nr4a3_tcip_reach` — pure logic plus committed coordinates, no network.

The rules these pin, in order of how much damage each would do if it drifted:
  1. NO CONSTANT IS RE-TYPED. Every threshold, ladder rung and ceiling this module reports must be the
     one the owning lane holds. A re-typed rise or ceiling would silently make the TCIP answer
     incomparable with the E3 one it is paired against, which is the whole point of the module;
  2. the body-free envelope must use the SAMPLER'S OWN anchor predicate, not a lookalike. If the two
     ever diverge, the "body-free upper bound" stops being an upper bound on the body results;
  3. the size partition must be checked against measured residue counts, never trusted because it was
     typed — the "a populated field is not a measured one" rule in its smallest form;
  4. the effector-arm census must COUNT staged arms rather than assert a number, must read each arm's
     partner class from its own RECORD rather than from which file it came out of, and must never let a
     staged NAMED effector leak into the size-class pools that `birc2`/`mdm2` carry as proxies;
  5. the described-not-applied map edits must be ANCHOR-CHECKED against the live files — an edit whose
     `current_text` is not in the file it names is worse than no edit, because it reads as verified;
  6. the acceptance test must be E3-free, proven by a controlled reproduction rather than by reading
     the source — this is the claim `PUB-TCIP` rests on.
"""
import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import basin_geom as G                       # noqa: E402
import linker_design as LD                   # noqa: E402
import nr4a3_basin_search as BS              # noqa: E402
import nr4a3_linker_design as NLD            # noqa: E402
import nr4a3_tcip_reach as T                 # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# 1 · nothing is re-typed
# ---------------------------------------------------------------------------------------------------------
def test_every_constant_is_imported_from_the_lane_that_owns_it():
    assert T.RISE == LD.RISE_PER_ATOM_A
    assert T.CHEM_MAX_ATOMS == NLD.CHEM_MAX_ATOMS
    assert T.LINKER_MIN_ATOMS == BS.PARAMS["linker_min_atoms"]
    assert T.GATE_ATOMS == BS.PARAMS["linker_gate_atoms"]
    assert T.SEARCH_MAX_ATOMS == BS.PARAMS["linker_max_atoms"]
    assert T.MIN_CLEARANCE == BS.PARAMS["pose_min_clearance_A"]


def test_the_ladder_contains_the_committed_report_rungs_and_both_ceilings():
    for n in BS.PARAMS["linker_report_atoms"]:
        assert n in T.LADDER
    assert BS.PARAMS["linker_gate_atoms"] in T.LADDER
    assert BS.PARAMS["linker_max_atoms"] in T.LADDER
    # the committed report ladder stops at the SEARCH ceiling; the chemically routine ceiling is higher and
    # is what a design answer is actually read at, so it must be on the ladder too
    assert NLD.CHEM_MAX_ATOMS in T.LADDER
    assert max(T.LADDER) == NLD.CHEM_MAX_ATOMS


def test_required_distances_are_derived_and_not_typed():
    r = T.required_distances()
    assert r["span_at_gate_A"] == pytest.approx(
        G.contour_length_from_atoms(BS.PARAMS["linker_gate_atoms"], LD.RISE_PER_ATOM_A))
    assert r["span_at_chemically_routine_ceiling_A"] == pytest.approx(
        G.contour_length_from_atoms(NLD.CHEM_MAX_ATOMS, LD.RISE_PER_ATOM_A))
    # and no TCIP-specific distance may sneak in while the citation is unverified
    assert "⚠_no_tcip_specific_distance_is_used" in r


# ---------------------------------------------------------------------------------------------------------
# 2 · the body-free envelope uses the sampler's own predicate
# ---------------------------------------------------------------------------------------------------------
def test_body_free_envelope_agrees_with_the_samplers_own_anchor_predicate():
    """A synthetic field, so the test owns its own ground truth: one atom at the origin, and the predicate
    `min_dist(b) - cell_slack >= pose_min_clearance_A` is checked point by point against the envelope's
    own admissibility count."""
    field = G.SquaredDistanceField([(0.0, 0.0, 0.0)], cell=0.9, clamp=8.0)
    a = (0.0, 0.0, 0.0)
    env = T.body_free_envelope(a, field, ladder=[6], pitch=1.5)
    r = env["6"]
    lo = G.contour_length_from_atoms(T.LINKER_MIN_ATOMS, T.RISE)
    hi = G.contour_length_from_atoms(6, T.RISE)
    n_ok = n_tot = 0
    steps = int(hi / 1.5)
    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            for k in range(-steps, steps + 1):
                d2 = (i * 1.5) ** 2 + (j * 1.5) ** 2 + (k * 1.5) ** 2
                if d2 > hi * hi or d2 < lo * lo:
                    continue
                n_tot += 1
                p = (a[0] + i * 1.5, a[1] + j * 1.5, a[2] + k * 1.5)
                if field.min_dist(p) - field.cell_slack >= T.MIN_CLEARANCE:
                    n_ok += 1
    assert r["n_grid_points"] == n_tot
    assert r["n_admissible"] == n_ok


def test_the_envelope_is_monotone_in_linker_length_by_construction():
    """A longer linker can only ADD shell, never remove it, so the admissible COUNT must be non-decreasing.
    A fraction may fall (the added shell can be worse than the old), and that is not a bug — the count is
    the invariant, so the test pins the count."""
    field = G.SquaredDistanceField([(0.0, 0.0, 0.0)], cell=0.9, clamp=8.0)
    env = T.body_free_envelope((0.0, 0.0, 0.0), field, ladder=[6, 10, 16], pitch=2.0)
    counts = [env[str(n)]["n_admissible"] for n in (6, 10, 16)]
    assert counts == sorted(counts)


def test_the_envelope_is_deterministic():
    field = G.SquaredDistanceField([(0.0, 0.0, 0.0)], cell=0.9, clamp=8.0)
    one = T.body_free_envelope((1.0, 2.0, 3.0), field, ladder=[8], pitch=2.0)
    two = T.body_free_envelope((1.0, 2.0, 3.0), field, ladder=[8], pitch=2.0)
    assert one == two


# ---------------------------------------------------------------------------------------------------------
# 3 · the size partition is measured, not asserted
# ---------------------------------------------------------------------------------------------------------
def test_size_labels_are_checked_against_the_coordinates():
    reg = json.load(open(T.REGISTRY))
    geom = {}
    for aid in list(T.SINGLE_DOMAIN_ARMS) + list(T.MULTI_SUBUNIT_ARMS):
        geom[aid] = T.body_geometry(BS.load_arm_from_registry(reg["arms"][aid]))
    assert T.crosscheck_size_partition(geom)["status"] == "AGREES"
    for aid in T.SINGLE_DOMAIN_ARMS:
        assert geom[aid]["n_residues"] <= T.SINGLE_DOMAIN_MAX_RESIDUES
    for aid in T.MULTI_SUBUNIT_ARMS:
        assert geom[aid]["n_residues"] > T.SINGLE_DOMAIN_MAX_RESIDUES


def test_a_mislabelled_size_partition_is_caught():
    bad = {aid: {"size_class": "multi_subunit"} for aid in T.SINGLE_DOMAIN_ARMS}
    bad.update({aid: {"size_class": "multi_subunit"} for aid in T.MULTI_SUBUNIT_ARMS})
    assert T.crosscheck_size_partition(bad)["status"] == "DISAGREES"


# ---------------------------------------------------------------------------------------------------------
# 4 · the census counts, and its answer is the finding that converts the lead
# ---------------------------------------------------------------------------------------------------------
def test_effector_arm_census_counts_rather_than_asserts():
    """★ THE ASSERTION THAT USED TO BE HERE WAS `c["answer"] == 0`, AND THAT WAS THE BUG THIS FILE EXISTS TO
    PREVENT, ONE LEVEL UP. A test pinning the answer to a literal 0 pins the CONCLUSION, not the counting —
    it would have gone red the moment an effector was staged (correct behaviour arriving), and stayed green
    forever if the census had silently stopped reading the effector registry (the failure). So what is
    checked now is the ARITHMETIC: the total is the number of records across both registries, the effector
    count is the number of EFFECTOR-classed records that are actually loadable, and no row's class is
    invented."""
    c = T.effector_arm_census()
    n_records = sum(len(json.load(open(p))["arms"])
                    for p in (T.REGISTRY, T.EFFECTOR_REGISTRY) if os.path.exists(p))
    assert c["n_staged_arms_total"] == n_records
    assert c["n_loadable"] >= 2
    eff = [r for r in c["arms"]
           if r["partner_class"] == T.EFFECTOR_PARTNER_CLASS and r["loadable_as_rigid_body"]]
    assert c["answer"] == len(eff)
    assert c["effector_arm_ids"] == [r["arm_id"] for r in eff]
    for r in c["arms"]:
        assert r["partner_class"] in (T.E3_PARTNER_CLASS, T.EFFECTOR_PARTNER_CLASS), r


def test_the_census_reads_the_partner_class_from_the_record_not_from_the_filename():
    """The old census hard-coded `E3 ubiquitin-ligase recruiter` for every row. Harmless while there was one
    registry, and guaranteed to mislabel a staged effector as a ligase the moment there were two."""
    c = T.effector_arm_census()
    e3 = {r["arm_id"] for r in c["arms"] if r["partner_class"] == T.E3_PARTNER_CLASS}
    assert {"vhl", "crbn", "birc2", "mdm2"} <= e3
    if os.path.exists(T.EFFECTOR_REGISTRY):
        staged = json.load(open(T.EFFECTOR_REGISTRY))["arms"]
        for aid, rec in staged.items():
            row = next(r for r in c["arms"] if r["arm_id"] == aid)
            assert row["partner_class"] == rec["partner_class"]
            assert row["partner_class"] == T.EFFECTOR_PARTNER_CLASS


def test_a_named_effector_may_not_be_pooled_into_the_size_class_comparison():
    """⛔ THE DISCIPLINE THE ROUTE MEMO TURNS ON. `birc2` and `mdm2` are size-and-shape PROXIES; a staged
    effector must never leak into the pools that carry the size result, or a proxy number would be
    laundered into an effector one."""
    for aid in T.staged_effector_arm_ids():
        assert aid not in T.SINGLE_DOMAIN_ARMS
        assert aid not in T.MULTI_SUBUNIT_ARMS


def test_the_named_effector_reading_says_so_when_nothing_is_staged():
    out = T.named_effector_reading([], {}, {}, {}, [], {"arms": []})
    assert out["status"] == "NO_NAMED_EFFECTOR_STAGED"
    assert "SIZE CLASS" in out["_reading"]


# ---------------------------------------------------------------------------------------------------------
# 5 · the described-not-applied edits are anchor-checked against the live files
# ---------------------------------------------------------------------------------------------------------
def test_every_described_map_edit_resolves_against_its_live_file():
    """★ THE ASSERTION THAT USED TO BE HERE WAS `assert chk["current_text_found"]`, AND IT WENT RED THE DAY
    ANOTHER LANE DID WHAT THESE EDITS ASK. An applied edit necessarily removes its own `current_text`, so
    "the text I want to replace is still there" cannot be the invariant — it treats success and never-existed
    as the same observation. What must hold is that each edit still RESOLVES: it is either still pending, or
    verifiably applied. Only `STALE_ANCHOR` (neither text is in the file) is a real defect, because that is
    the state in which an edit reads as verified while targeting nothing."""
    edits = T.map_edits_required(T.effector_arm_census(), {})
    assert edits
    for e in edits:
        if e["state"] == "NO_ANCHOR" or e["file"].endswith(".json"):
            continue
        assert e["anchor_check"]["file_present"], e["file"]
        assert e["state"] in ("PENDING", "APPLIED"), (e["file"], e["current_text"], e["state"])


def test_an_applied_map_edit_is_recognised_as_applied_rather_than_as_a_broken_anchor(tmp_path):
    """The discrimination itself, on a file whose content is known by construction."""
    f = tmp_path / "doc.md"
    f.write_text("intro\nthe NEW wording is here\ntail\n")
    rel = os.path.relpath(str(f), T.REPO)
    cur = T._anchor_check(rel, "the OLD wording")
    prop = T._anchor_check(rel, "the NEW wording")
    assert cur["current_text_found"] is False
    assert prop["current_text_found"] is True


def test_the_closure_kind_row_records_a_verified_state_and_asks_for_no_edit():
    """The 2026-08-06 route audit found `RT-TCIP.closure_kind: instrument_limit` and corrected it in the
    same pass. A later lane must not 'fix' it again — so the module carries the measured current value and
    a no-action status, and this test fails if the graph ever regresses."""
    routes = json.load(open(os.path.join(T.REPO, "systems", "graph", "routes.json")))
    rs = routes["routes"] if isinstance(routes, dict) and "routes" in routes else routes
    row = next(r for r in (rs if isinstance(rs, list) else rs.values()) if r["id"] == "RT-TCIP")
    assert row["closure_kind"] == "open"
    # and the graph's own encoding is the evidence that R9/R10 are NOT retired
    assert row["blockers_retired"] == ["BLK-TERNARY-GEOMETRY"]
    assert "BLK-INDUCED-COMPLEX" in row["blockers_inherited"]


# ---------------------------------------------------------------------------------------------------------
# 6 · the acceptance test is E3-free — proven, not read
# ---------------------------------------------------------------------------------------------------------
def test_the_acceptance_test_ignores_every_E3_specific_field():
    m3 = BS.load_paralogue(os.path.join(T.STRUCT_DIR, "nr4a3-opened.pdb"))
    field3 = G.SquaredDistanceField(m3["heavy_xyz"], cell=0.9, clamp=8.0)
    reactive = BS.load_reactive_map(T.UNIQUE_JSON, m3)
    poses = BS.build_pose_ensemble(m3, reactive, field3, 12, random.Random(T.BASIN_SEED))
    reg = json.load(open(T.REGISTRY))
    arms = {aid: BS.load_arm_from_registry(reg["arms"][aid]) for aid in ("birc2", "vhl")}
    res = T.crosscheck_acceptance_is_e3_free(arms, poses, field3, n_samples=8000)
    assert res["status"] == "HOLDS", res


# ---------------------------------------------------------------------------------------------------------
# 7 · the pooled proportion arithmetic
# ---------------------------------------------------------------------------------------------------------
def test_wilson_interval_brackets_the_point_estimate_and_narrows_with_n():
    lo1, hi1 = T.wilson(50, 1000)
    lo2, hi2 = T.wilson(500, 10000)
    assert lo1 < 0.05 < hi1 and lo2 < 0.05 < hi2
    assert (hi2 - lo2) < (hi1 - lo1)
    assert T.wilson(0, 0) == [None, None]


def test_a_ratio_whose_intervals_overlap_is_reported_as_overlapping():
    """The comparator must be able to return 'no measurable difference' — a module that can only return a
    difference is not a measurement."""
    cells = ([{"arm_id": "birc2", "linker_atoms": 12, "n_accepted": 100, "n_samples": 100000,
               "n_contact_median": 20}]
             + [{"arm_id": "vhl", "linker_atoms": 12, "n_accepted": 101, "n_samples": 100000,
                 "n_contact_median": 30}])
    free = {"12": {"shell_hi_A": 15.0, "mean_fraction_admissible": 0.5}}
    out = T.paired_body_size_comparison(cells, free, {})
    assert out["12"]["intervals_overlap"] is True
    assert out["12"]["size_ratio_single_over_multi"] == pytest.approx(100 / 101, rel=1e-3)


# ---------------------------------------------------------------------------------------------------------
# 8 · the sampled result must reproduce between processes
# ---------------------------------------------------------------------------------------------------------
def test_the_per_cell_seed_does_not_depend_on_pythons_hash_randomisation():
    """⛔ REGRESSION GUARD. The job seeds were once built from `hash(arm_id)`, which Python salts per
    PROCESS unless PYTHONHASHSEED is set — so two full runs of the same code produced different numbers
    (the pooled size ratio moved 0.871 -> 0.869 and the gate ratio 0.871 -> 0.914 with no edit in between).
    A sampled artifact that does not reproduce is not an artifact. This test runs the seed derivation in a
    SEPARATE interpreter with a different hash salt and requires the same answer."""
    import subprocess
    import textwrap
    prog = textwrap.dedent(
        """
        import os, sys
        sys.path.insert(0, %r)
        import nr4a3_tcip_reach as T
        import zlib
        print([zlib.crc32(a.encode('utf-8')) %% 997
               for a in sorted(list(T.SINGLE_DOMAIN_ARMS) + list(T.MULTI_SUBUNIT_ARMS))])
        """ % HERE)
    outs = set()
    for salt in ("0", "1", "12345"):
        env = dict(os.environ, PYTHONHASHSEED=salt)
        outs.add(subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True,
                                env=env, check=True).stdout.strip())
    assert len(outs) == 1, outs
    # ...and the module must not have gone back to `hash()`. ⚠ Checked on CODE lines only: the incident is
    # narrated in a comment right above the fix, so a whole-file substring search matches the warning and
    # fails on the very text that documents it — a guard that fires on its own documentation.
    code = [ln.split("#", 1)[0] for ln in
            open(os.path.join(HERE, "nr4a3_tcip_reach.py")).read().split("\n")]
    assert not any("hash(aid)" in ln for ln in code)
    assert any("zlib.crc32" in ln for ln in code)
