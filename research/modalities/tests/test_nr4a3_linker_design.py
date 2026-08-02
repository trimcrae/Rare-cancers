"""Tests for the RUNG-5b design driver.

These sit alongside `test_linker_design.py` (which tests the geometry kernels) and cover the layer above it:
SMILES assembly, the backbone-index bookkeeping, and the preregistered filter. They exist because every one
of them corresponds to a defect that actually occurred:

  * the VHL handle ended at `NC(=O)` and the assembler added a second carbonyl -> an alpha-ketoamide;
  * a PEG segment after an amide nitrogen -> an N,O-acetal;
  * the branch residue abutting the warhead acyl -> an acylurea;
  * `k_warhead = n - k_E3` instead of `n + 1 - k_E3` -> every electrophile one atom out of place.

The k test is written as the IDENTITY `k_warhead + k_E3 = n + 1` rather than as the formula under test, so it
cannot be satisfied by the same arithmetic error twice.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_linker_design as LDD    # noqa: E402


def _acyl_segments():
    return [k for k, v in LDD.LINKER_SEGMENT.items() if v["n"] > 0 and not v.get("amine_only")]


def _amine_segments():
    return [k for k, v in LDD.LINKER_SEGMENT.items() if v["n"] > 0 and not v.get("acyl_only")]


def test_module_self_test_passes():
    assert LDD.self_test() == 0


@pytest.mark.parametrize("e3", ["vhl", "crbn"])
@pytest.mark.parametrize("wh", sorted(LDD.WARHEAD_HANDLE))
def test_unbranched_backbone_count_is_the_declared_sum(e3, wh):
    for s1 in _acyl_segments():
        smi, n, k = LDD.build_smiles(e3, wh, s1)
        assert n == 1 + LDD.LINKER_SEGMENT[s1]["n"] + LDD.WARHEAD_HANDLE[wh]["tail_atoms"]
        assert k is None
        assert smi.count("(") == smi.count(")")


@pytest.mark.parametrize("e3", ["vhl", "crbn"])
def test_branch_index_identity(e3):
    """★ k counted from the warhead plus k counted from the E3 must equal n + 1: the branch atom is counted
    once from each end, and there are n backbone atoms. Any off-by-one breaks this."""
    for wh in LDD.WARHEAD_HANDLE:
        for s1 in _acyl_segments():
            for s2 in _amine_segments():
                smi, n, k = LDD.build_smiles(e3, wh, s1, s2, "cyac_me")
                k_e3 = 1 + LDD.LINKER_SEGMENT[s1]["n"] + 1 + 2
                assert k + k_e3 == n + 1, (e3, wh, s1, s2, k, k_e3, n)
                assert 1 <= k <= n - 1


@pytest.mark.parametrize("motif", ["NC(=O)C(=O)", "C(=O)NCO", "C(=O)NC(=O)N"])
def test_no_forbidden_junction_motif_is_ever_emitted(motif):
    """alpha-ketoamide, N,O-acetal, acylurea — each was emitted by an earlier version."""
    for e3 in ("vhl", "crbn"):
        for wh in LDD.WARHEAD_HANDLE:
            for s1 in _acyl_segments():
                assert motif not in LDD.build_smiles(e3, wh, s1)[0]
                for s2 in _amine_segments():
                    for p in ("cyac_me", "pyr3", "ph", "cyanoprop"):
                        assert motif not in LDD.build_smiles(e3, wh, s1, s2, p)[0]


def test_assembler_refuses_the_three_known_bad_shapes():
    with pytest.raises(ValueError):          # branch residue with a bare N-terminus -> an amine, not an amide
        LDD.build_smiles("vhl", "5amide", "s0", "a2", "pyr3")
    with pytest.raises(ValueError):          # acyl-side PEG after an amide N -> N,O-acetal
        LDD.build_smiles("vhl", "5amide", "a2", "e2", "pyr3")
    with pytest.raises(ValueError):          # branch residue abutting the warhead acyl -> acylurea
        LDD.build_smiles("vhl", "5amide", "a2", "s0", "pyr3")


def test_ring_digit_renumbering_is_private_and_refuses_overflow():
    assert LDD._renumber("c1ccccc1", 7) == "c7ccccc7"
    assert LDD._renumber("Cc1cccnc1", 7) == "Cc7cccnc7"
    with pytest.raises(ValueError):
        LDD._renumber("c1ccc2ccccc2c1", 9)


def test_pendant_ring_digits_do_not_collide_with_the_scaffold():
    """The E3 handles use 1-3 and the warhead handles 4-6, so a pendant renumbered from 7 can never capture
    one of their ring bonds. Checked by counting each digit's occurrences: every ring closure must be even."""
    for e3 in ("vhl", "crbn"):
        for wh in LDD.WARHEAD_HANDLE:
            smi = LDD.build_smiles(e3, wh, "a3", "a2", "pyr3")[0]
            for d in "123456789":
                assert smi.count(d) % 2 == 0, (e3, wh, d, smi)


def test_filter_thresholds_are_constants_not_derived_from_the_library():
    """The downselect is preregistered: its thresholds must be plain constants, so they cannot have been
    tuned to a result after the fact."""
    for key in ("min_member_fraction_comfortable", "max_strain_kT_at_placement", "max_backbone_atoms",
                "max_per_basin_per_kind"):
        assert isinstance(LDD.FILTER[key], (int, float))
    assert LDD.FILTER["max_strain_kT_at_placement"] == LDD.MAX_STRAIN_KT
    assert LDD.FILTER["max_backbone_atoms"] == LDD.CHEM_MAX_ATOMS


def test_every_pendant_declares_a_reach_that_exists():
    for name, p in LDD.PENDANT.items():
        assert p["reach_key"] in LDD.PENDANT_REACH, name
        assert p["kind"] in ("electrophile", "control", "wedge", "wedge_control"), name
        if p["kind"] == "electrophile":
            assert p["reversible"] in (True, False), name


def test_the_irreversible_comparator_is_present_and_labelled():
    """nr4a3-program-map.md prefers REVERSIBLE-covalent chemistry. That preference is only a tested choice if the
    irreversible comparator is in the library and marked as one."""
    assert LDD.PENDANT["acrylamide"]["reversible"] is False
    assert "IRREVERSIBLE" in LDD.PENDANT["acrylamide"]["name"]
    assert any(p.get("reversible") is True for p in LDD.PENDANT.values())


def test_controls_have_their_own_cap_bucket():
    """★ The regression this pins. Sharing the design bucket (basin x pendant_kind) let the two reversible
    electrophiles fill the 'electrophile' slot and filtered the IRREVERSIBLE comparator to zero — deleting
    the one construct that makes 'prefer reversible' falsifiable. Controls are capped per PENDANT."""
    assert "max_per_basin_per_control" in LDD.FILTER
    assert LDD.FILTER["max_per_basin_per_control"] >= 1


def test_emitted_library_keeps_the_comparator_and_the_controls():
    """Checked against the committed artifact rather than the code path, because the failure mode was a
    library that looked healthy while missing its comparator."""
    import json
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "nr4a3-linker-design.json")
    if not os.path.exists(path):
        pytest.skip("design artifact not present")
    s = json.load(open(path))["library_summary"]
    assert s["n_irreversible_comparator"] >= 1, "the irreversible comparator was filtered out of the library"
    assert s["n_reversible_covalent"] >= 1
    assert s["n_controls"] >= 1


def test_every_confirmed_basin_has_a_published_patch_to_be_checked_against():
    """★ Meta-basin IDs are POSITIONAL — a rank in that run's clustering — so `CONFIRMED` alone cannot
    guarantee the artifact's `crbn|M0` is the basin that was confirmed. Re-running the same search at 250 000
    samples instead of 10^6 gave a `vhl|M2` whose interface patch matched the published one at Jaccard
    **0.176**, and RUNG 5b designed nine constructs against it and recommended a matched pair on it, with no
    symptom. Every id must therefore carry a patch to be checked against, and the threshold must be the SAME
    one the search uses to call two placements one meta-basin — not a looser number chosen here.
    """
    import nr4a3_basin_search as BS
    assert set(LDD.CONFIRMED) == set(LDD.CONFIRMED_PATCH)
    assert LDD.CONFIRMED_PATCH_MIN_JACCARD == BS.PARAMS["meta_basin_jaccard_cutoff"]
    for bid, patch in LDD.CONFIRMED_PATCH.items():
        assert patch == sorted(set(patch)), bid          # sorted, no duplicates
        assert len(patch) >= 5, bid                      # a real interface patch, not a stub


def test_construct_id_encodes_the_placement_it_was_designed_at():
    """★ Two placements, two libraries, one id space. The same basin, warhead and segments give a DIFFERENT
    molecule at the representative and at the term-(a) exemplar (different span floor, so different allowed
    lengths), and if the ids collided one would silently overwrite the other in any id-keyed consumer."""
    r_rep = {"meta_basin_id": "crbn|M0", "placement_label": "representative",
             "designed_on": {"basin_id": "crbn|p|b0", "pose_id": "p"}, "role": "design",
             "endpoint_distance": {"member_span_deciles_A": None, "member_span_A": {}},
             "accessibility": {"span_distribution_used": "x", "window_centre_A": 10.0},
             "wedge_element_sites": {"sites": []}}
    r_ex = dict(r_rep, placement_label="term_a_exemplar")
    ids = set()
    for r in (r_rep, r_ex):
        ids.add(LDD._record(r, "crbn", "5amide", "a2", None, "none", None, None, "C", 8, {},
                            {"P_reach_normalised": 0.0}, None)["construct_id"])
    assert len(ids) == 2, ids
    assert any("@ex_" in i for i in ids) and any("@rep_" in i for i in ids)


def test_the_preregistered_wedge_chemistry_rule_rejects_a_paralogue_donor():
    """★ THE RULE THAT REPLACED A GEOMETRY-ONLY PICK, and it is now binding on BOTH placements. An H-bond
    ACCEPTOR wedge can only discriminate if NR4A3 presents a donor and NEITHER paralogue does. Geometry alone
    selects Ile396 — the most E3-clear site — where the pyridyl nitrogen faces an isoleucine in every
    paralogue and `S` would be ~0 by construction."""
    ok = {"nr4a3": "T", "nr4a1": "L", "nr4a2": "V"}
    ile = {"nr4a3": "I", "nr4a1": "A", "nr4a2": "V"}          # no donor anywhere: the geometry-only pick
    par = {"nr4a3": "T", "nr4a1": "L", "nr4a2": "S"}          # NR4A2 also donates: not discriminating
    assert LDD._wedge_chemistry_ok(ok)
    assert not LDD._wedge_chemistry_ok(ile)
    assert not LDD._wedge_chemistry_ok(par)


def test_the_pendant_reach_table_is_the_shared_one():
    """One definition, shared with the RUNG-5a term-(a) gate — a local copy is how the two rungs drift."""
    import linker_design as LD
    assert LDD.PENDANT_REACH is LD.PENDANT_REACH_A


def test_saturated_control_matches_its_electrophile_in_everything_but_the_alkene():
    """The non-electrophilic control must be the cyanoacrylamide with the Michael acceptor reduced — same
    atoms, one bond order different — or it is not a matched control."""
    def skeleton(smi):
        return (smi.replace("/", "").replace("\\", "").replace("=", "")
                   .replace("[C@@H]", "C").replace("[C@H]", "C"))
    e, c = LDD.PENDANT["cyac_me"]["smi"], LDD.PENDANT["cyanoprop"]["smi"]
    # identical skeletons once bond orders and stereo tags are erased: the only constitutional difference
    # is the C=C. The STEREO difference is real and deliberate -- reducing the acceptor creates a centre the
    # electrophile does not have -- which is why the tags are stripped here and documented there.
    assert skeleton(e) == skeleton(c), (e, c)
    assert "@" in c and "@" not in e, "the saturated control must declare the centre reduction creates"
    assert "C#N" in c
    assert "=C" not in c.replace("C(=O)", "")        # no alkene survives in the control


def test_the_enumerator_and_the_pair_selector_choose_the_wedge_site_by_ONE_rule():
    """★★ THE DEFECT THIS PINS (LANE 14, 2026-07-26): the preregistered wedge chemistry rule was binding in
    `matched_pair` but NOT in `enumerate_library`, which went on taking the site with the most E3 clearance.
    The emitted pair then reported `wedge_target_residue: T407` while its own d/d0 molecules had been built
    with the pyridyl aimed at C397 — Asn in NR4A1, Ser in NR4A2, i.e. both paralogues keep an H-bond partner,
    which is precisely the "S is ~0 by construction" trap the rule exists to prevent. Measured over the
    corrected artifact the two selections disagreed on 8 of 10 (basin x placement) records.

    The pin is that there is ONE selector. A second call site re-deriving "max clearance among clean sites"
    is the bug, not an equivalent spelling of it.
    """
    sites = [
        # the geometry winner, and the wrong chemistry: Cys397 (Asn/Ser) — both paralogues can H-bond
        {"uniprot_resid": 397, "nr4a3": "C", "nr4a1": "N", "nr4a2": "S",
         "e3_clearance_A": 14.29, "e3_clear_enough_for_a_matched_pair": True},
        # the most-clear NON-397 site, still the wrong chemistry: Ile (Ala/Val) — no donor anywhere
        {"uniprot_resid": 396, "nr4a3": "I", "nr4a1": "A", "nr4a2": "V",
         "e3_clearance_A": 12.63, "e3_clear_enough_for_a_matched_pair": True},
        # the chemistry winner, and the least clear of the three: Thr (Leu/Val)
        {"uniprot_resid": 407, "nr4a3": "T", "nr4a1": "L", "nr4a2": "V",
         "e3_clearance_A": 8.6, "e3_clear_enough_for_a_matched_pair": True},
        # right chemistry but touching the E3: excluded regardless
        {"uniprot_resid": 412, "nr4a3": "R", "nr4a1": "A", "nr4a2": "T",
         "e3_clearance_A": 2.0, "e3_clear_enough_for_a_matched_pair": False},
    ]
    picked = LDD.select_wedge_site(sites)
    assert picked is not None and picked["uniprot_resid"] == 407, picked
    # ... and a basin with no chemistry-valid site gets NO wedge site, rather than the most E3-clear one
    assert LDD.select_wedge_site([s for s in sites if s["uniprot_resid"] in (396, 397)]) is None
    assert LDD.select_wedge_site([]) is None


def test_c397_is_never_the_wedge_site_even_if_it_somehow_passed_the_chemistry_rule():
    """The categorical handle's cysteine must not host the MARGINAL wedge — putting both mechanisms on one
    residue would make a null from 5a-KS unreadable. Cys is not an H-bond donor so the chemistry rule already
    excludes it; this pins the intent rather than the coincidence."""
    cys_as_if_a_donor = {"uniprot_resid": 397, "nr4a3": "T", "nr4a1": "L", "nr4a2": "V",
                         "e3_clearance_A": 99.0, "e3_clear_enough_for_a_matched_pair": True}
    other = {"uniprot_resid": 407, "nr4a3": "S", "nr4a1": "L", "nr4a2": "V",
             "e3_clearance_A": 6.1, "e3_clear_enough_for_a_matched_pair": True}
    assert LDD.select_wedge_site([cys_as_if_a_donor, other])["uniprot_resid"] == 407


def test_the_collision_bracket_is_a_bracket_and_never_an_interpolation():
    """★ FOUR measured points. A construct at 18 atoms sits between the 16- and 20-atom points and that is the
    whole honest statement — a curve through four points quoting a value at 18 is not. Above the longest
    measured point the upper end is OPEN, because the measurement stops there and the trend is rising."""
    src = LDD.PARALOGUE_COLLISION_BY_LINKER_ATOMS
    for n in (12, 14, 16, 20):
        b = LDD.collision_bracket(n)
        assert b["lo"] == b["hi"] == src[n]["reach_only"], n     # each is itself a measured point
    mid = LDD.collision_bracket(18)
    assert (mid["lo"], mid["hi"]) == (src[16]["reach_only"], src[20]["reach_only"])
    assert mid["at"] == [16, 20] and "NOT interpolated" in mid["reading"]
    beyond = LDD.collision_bracket(24)
    assert beyond["lo"] == src[20]["reach_only"] and beyond["hi"] is None, \
        "above the last measured point the bracket is open"
    # monotone non-decreasing in the lower end, which is the only shape the measurement supports
    los = [LDD.collision_bracket(n)["lo"] for n in range(8, 30)]
    assert all(b >= a for a, b in zip(los, los[1:])), los


def test_the_collision_profile_is_read_from_the_landed_artifact_not_copied():
    """★★ REGRESSION, 2026-08-02. This table WAS a hard-coded copy of the 5,657-placement static-model pilot
    while the matched ensembles that superseded it sat committed two directories away — the one-fact-two-places
    failure CLAUDE.md rule 1 exists to stop. It is now DERIVED, and this test compares it to its one home
    field by field so a re-hard-coding cannot pass."""
    with open(os.path.join(os.path.dirname(__file__), "..", "nr4a-paralogue-dynamics.json"),
              encoding="utf-8") as fh:
        scopes = json.load(fh)["categorical_verdict"]["by_scope"]
    p = LDD.PARALOGUE_COLLISION_BY_LINKER_ATOMS
    assert sorted(p) == [12, 14, 16, 20]
    assert len(p[12]["by_scope"]) == 3, "all three conformer scopes must be carried, not just the static one"
    for n in p:
        for scope, sv in scopes.items():
            row = sv["by_linker_atoms"][str(n)]
            assert p[n]["by_scope"][scope]["reach_only"] == \
                row["P_paralogue_also_labelled_given_nr4a3"], (n, scope)
        assert p[n]["reach_only"] == max(v["reach_only"] for v in p[n]["by_scope"].values()), \
            "the headline value is the WIDEST reading across scopes, so a bracket cannot understate"


def test_the_superseded_pilot_is_retained_and_never_read():
    """CLAUDE.md rule 1.2: never silently drop a superseded number. It is kept under its own name — the
    committed library's brackets were written from it — and nothing reads it."""
    old = LDD.PARALOGUE_COLLISION_PILOT_5657_SUPERSEDED
    assert [old[n]["reach_only"] for n in (12, 14, 16, 20)] == [0.0, 0.0, 0.081, 0.258]
    assert old is not LDD.PARALOGUE_COLLISION_BY_LINKER_ATOMS
    assert LDD.PARALOGUE_COLLISION_BY_LINKER_ATOMS[16]["reach_only"] != old[16]["reach_only"], \
        "if these agreed the supersession would not have been applied"


def test_no_length_is_a_measured_zero_under_the_landed_ensembles():
    """★ The reading that changed. Under the pilot, 14 atoms was 'the longest length at which reach-only
    collision is still a MEASURED zero', and that sentence propagated into four documents. It is false under
    the matched ensembles: only the static-model scope reads a zero, and only at 12."""
    p = LDD.PARALOGUE_COLLISION_BY_LINKER_ATOMS
    assert p[14]["reach_only"] > 0.0
    assert p[12]["reach_only"] > 0.0, "the widest-across-scopes reading at the gate is not zero either"
    assert p[12]["by_scope"]["static_opened_model"]["reach_only"] == 0.0, \
        "the static model alone still reads a zero at 12 — which is exactly why the scope must be named"
