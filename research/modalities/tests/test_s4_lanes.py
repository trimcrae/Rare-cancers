"""Tests for the three §4 lanes of `emc-unexplored-treatment-lanes.md`.

⛔ THESE TESTS EXERCISE THE REAL MODULES AGAINST THE REAL COMMITTED INPUTS WHERE THEY CAN.
   `tests/test_fleet_armed.py::test_the_committed_census_lookup_works_against_the_real_repo` exists because
   every keep-alive test before it monkeypatched the seam and therefore tested the mock. The same discipline
   applies here: the alignment, the numbering offset and the SOFT parser are exercised on the real cached
   sequences, the real committed 8XTT benchmark artifact and the real committed GEO records, because those
   are exactly the joints where a silent mismatch would produce a plausible, wrong number.
"""
import gzip
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

INPUTS = os.path.join(HERE, "_s4_lane_inputs")


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ITEM 3 — the Nurr1 allosteric pocket vs Pocket-5
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_papers_residue_identities_match_uniprot_P43354():
    """If the paper were numbering a different isoform, every mapped residue would still LOOK fine."""
    import nurr1_allosteric_vs_pocket5 as M
    with open(M.SEQ_CACHE) as fh:
        seqs = json.load(fh)
    chk = M.paper_numbering_check(seqs)
    assert chk["status"] == "OK", [c for c in chk["checks"] if not c["ok"]]


def test_pocket5_is_imported_not_retyped():
    """Rule 1: the Pocket-5 definition has ONE home. A copy here would drift silently."""
    import nurr1_allosteric_vs_pocket5 as M
    import nr4a3_8xtt_benchmark as bm
    assert M.POCKET5_UNIPROT == list(bm.POCKET5)


def test_the_8xtt_numbering_offset_is_derived_from_the_committed_artifact():
    """A typed `-378` would survive a re-deposition that renumbered the entry."""
    import nurr1_allosteric_vs_pocket5 as M
    off, bench = M.xtt_offset()
    uni = bench["pocket5_residues_uniprot"]
    auth = bench["mapped_pocket5_8xtt"]
    assert sorted(u - off for u in uni) == sorted(auth)


def test_both_aligners_agree_on_every_site4_position():
    """The `alignment_robust` discipline: a position where two aligners disagree is not a mapping."""
    import nurr1_allosteric_vs_pocket5 as M
    with open(M.SEQ_CACHE) as fh:
        seqs = json.load(fh)
    rows = M.map_nr4a2_to_nr4a3([r["resnum"] for r in M.SITE4], seqs)
    assert all(r["aligners_agree"] for r in rows), [r for r in rows if not r["aligners_agree"]]


def test_M379_is_reported_as_a_gap_and_not_snapped_to_a_neighbour():
    """NR4A2 carries a 2-residue insertion there. Snapping it to a neighbour would invent an overlap."""
    import nurr1_allosteric_vs_pocket5 as M
    with open(M.SEQ_CACHE) as fh:
        seqs = json.load(fh)
    row = {r["nr4a2_resnum"]: r for r in M.map_nr4a2_to_nr4a3([379], seqs)}[379]
    assert row["mapped_nr4a3_resnum"] is None
    assert "gap" in (row["why_unmapped"] or "")


def test_the_control_epitopes_do_not_match_pocket5():
    """★ THE TEST THAT MAKES THE MATCH READABLE. If the same pipeline 'matched' the paper's OTHER sites,
    the finding would be an artifact of the mapping rather than a property of site 4."""
    d = _built()
    for label, v in d["control_other_epitopes_from_the_same_paper"]["sites"].items():
        assert v["accepted_by_frozen_gate"] is False, (label, v)
        assert v["n_overlap_with_pocket5"] == 0, (label, v)


def test_the_frozen_gate_is_used_not_reimplemented():
    import nurr1_allosteric_vs_pocket5 as M
    import pocket_tracking as pt
    m = pt.match_metrics([406, 407], [406, 407, 410])
    assert M.pt.match_metrics([406, 407], [406, 407, 410]) == m
    assert M.pt.JACCARD_MIN == pt.JACCARD_MIN


def test_the_committed_artifact_verified_the_literature_cache_bytes_themselves():
    """★ NOT 'a file at some path was checked'. The recorded git blob id must be the blob id of the copy on
    `literature-cache`, so the quote check is provably against the CI-retrieved text and not a re-typed or
    re-downloaded variant of it. Compare with:
        git ls-tree origin/literature-cache -- literature/nr4a-ligand-chemistry/PMC12095788.txt
    """
    p = os.path.join(HERE, "nurr1-allosteric-vs-pocket5.json")
    if not os.path.exists(p):
        pytest.skip("artifact not generated in this checkout")
    with open(p) as fh:
        d = json.load(fh)
    v = d["source_quote_verification"]
    assert v["status"] == "OK", v
    assert v["n_found_verbatim"] == v["n_quotes"]
    assert v["git_blob_sha1_of_the_verified_text"] == "b542818379d6aedada98ab9600d4b081a65bbaef", (
        "the verified text is not the literature-cache copy this result was built on")


def test_the_verdict_carries_its_own_ceiling():
    d = _built()
    v = d["verdict"]
    joined = " ".join(v["⛔_what_this_does_not_say"]).lower()
    for word in ("efficacy", "safety", "selectivity", "affinity"):
        assert word in joined
    assert "STARTING POINT" in v["_what_it_does_license"] or "documented negative" in v["_what_it_does_license"]


_CACHE = {}


def _built():
    if "d" not in _CACHE:
        import nurr1_allosteric_vs_pocket5 as M
        _CACHE["d"] = M.build()
    return _CACHE["d"]


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ITEM 1 — GSE11185
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _has_geo():
    return os.path.exists(os.path.join(INPUTS, "GSE11185_series.soft.txt"))


geo = pytest.mark.skipif(not _has_geo(), reason="raw GEO reads not present (they are a CI fetch)")


@geo
def test_the_arms_are_read_from_the_sample_titles_not_declared():
    import gse11185_wt_vs_fusion as M
    c = M.characterise(INPUTS)
    for s in c["samples"]:
        assert s["arm"] in ("wild_type", "fusion"), s
        assert s["arm_matched_on"] in s["title"], s
        assert s["dox"] in ("plus_dox", "minus_dox"), s


@geo
def test_ews_nor1_does_not_get_labelled_wild_type_by_a_substring_match():
    """'NOR1' is a substring of 'EWS/NOR1'. Longest-match-first is the whole reason ARM_RULES is ordered,
    and an unordered dict would silently label every fusion sample wild-type."""
    import gse11185_wt_vs_fusion as M
    assert M.arm_of("293-tet-On-EWS/NOR1 with doxycycline")[0] == "fusion"
    assert M.arm_of("293-tet-On-NOR1 with doxycycline")[0] == "wild_type"


@geo
def test_n_per_design_cell_is_one_and_the_artifact_says_so():
    """The single most important fact about this series. A version of this module that lost it would still
    produce a full, plausible table of fold changes."""
    import gse11185_wt_vs_fusion as M
    c = M.characterise(INPUTS)
    assert c["n_samples_per_design_cell"] == [1]
    assert "n = 1" in c["★_replication"]


@geo
def test_no_p_value_is_emitted_anywhere():
    """With one array per cell there is nothing to compute a p-value from, and the artifact must not
    contain one under any key."""
    import gse11185_wt_vs_fusion as M
    d = M.build(INPUTS)
    blob = json.dumps(d).lower()
    for forbidden in ('"p_value"', '"pvalue"', '"p_val"', '"q_value"', '"fdr"'):
        assert forbidden not in blob, forbidden


@geo
def test_the_selection_artifact_is_kept_and_labelled_rather_than_deleted():
    """The union-selected correlation is strongly negative and WRONG. Deleting it leaves the next session
    free to recompute it and believe it."""
    import gse11185_wt_vs_fusion as M
    d = M.build(INPUTS)
    art = (d["read"]["induction_response"]["★_correlation_of_induction_magnitude"]
           ["⛔_selection_artifact_do_not_read_as_a_finding"])
    unbiased = d["read"]["induction_response"]["★_correlation_of_induction_magnitude"]["pearson_r"]
    assert art["pearson_r"] < 0 < unbiased, (art["pearson_r"], unbiased)


@geo
def test_the_construct_expression_control_is_reported_as_unavailable_not_as_a_pass():
    """All three NR4A3 probesets are ABSENT-called. An artifact that reported that as 'no induction' would
    be reading an absent reading as a reading of absence."""
    import gse11185_wt_vs_fusion as M
    d = M.build(INPUTS)
    chk = d["instrument_controls"]["★_construct_expression_check"]
    assert chk["status"] == "CONTROL_UNAVAILABLE"
    assert chk["n_nr4a3_probesets_present_on_all_four_arrays"] == 0


@geo
def test_the_af1_answer_is_a_refusal_and_says_why():
    import gse11185_wt_vs_fusion as M
    d = M.build(INPUTS)
    a = d["af1_premise_bearing"]
    assert a["does_this_dataset_speak_to_it"].startswith("NO")
    assert a["why_not"] and len(a["why_not"]) >= 3


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ITEM 2 — the response-element reach enumeration
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _has_7wnh():
    return os.path.exists(os.path.join(INPUTS, "7WNH.pdb.gz"))


pdb = pytest.mark.skipif(not _has_7wnh(), reason="7WNH not present (it is a CI fetch)")


@pdb
def test_the_biological_unit_is_measured_from_contacts_not_read_off_the_header():
    """7WNH's ASU holds 4 protein chains and 8 DNA chains. A body assembled from the wrong pairing would
    produce an excluded volume that looks entirely reasonable and is wrong."""
    import nr4a3_re_reach as M
    atoms = M.parse_pdb(M.PDB_GZ)
    unit = M.pick_biological_unit(atoms)
    assert unit["protein_chain"] in {"A", "B", "C", "D"}
    assert len(unit["dna_chains"]) == 2, unit
    assert "contacts" in unit["_method"]


@pdb
def test_the_nbre_is_found_in_the_coordinates_rather_than_assumed():
    import nr4a3_re_reach as M
    atoms = M.parse_pdb(M.PDB_GZ)
    unit = M.pick_biological_unit(atoms)
    keep = set(unit["dna_chains"]) | {unit["protein_chain"]}
    body = [a for a in atoms if a["chain"] in keep]
    n = M.locate_nbre(body, unit["dna_chains"])
    assert n["matched"] in (M.NBRE_CONSENSUS, M.revcomp(M.NBRE_CONSENSUS))
    assert len(n["core_nucleotides"]) == len(M.NBRE_CONSENSUS)
    assert n["paired_partner_nucleotides"], "no base-paired partner strand found"


@pdb
def test_locate_nbre_refuses_rather_than_guessing_when_the_element_is_absent():
    import nr4a3_re_reach as M
    atoms = [a for a in M.parse_pdb(M.PDB_GZ) if a["chain"] == "A"]      # protein only, no DNA
    with pytest.raises(SystemExit):
        M.locate_nbre(atoms, ["E", "F"])


@pdb
def test_the_ladder_and_gate_are_imported_not_retyped():
    import nr4a3_re_reach as M
    import nr4a3_tcip_reach as T
    import nr4a3_basin_search as BS
    assert M.LADDER == list(T.LADDER)
    assert M.GATE_ATOMS == BS.PARAMS["linker_gate_atoms"]
    assert M.MIN_CLEARANCE == BS.PARAMS["pose_min_clearance_A"]


def test_the_committed_reach_artifact_carries_the_admits_ceiling():
    """An `admits` answer that travelled without its ceiling would read as a result."""
    p = os.path.join(HERE, "nr4a3-re-reach.json")
    if not os.path.exists(p):
        pytest.skip("artifact not generated in this checkout")
    with open(p) as fh:
        d = json.load(fh)
    s = d["verdict"]["⛔_and_this_is_the_sentence_that_must_travel_with_it"]
    assert "EXCLUDED-VOLUME" in s and "NOT evidence" in s
    assert d["verdict"]["⛔_the_blocker_this_does_not_touch"]


def test_the_reach_artifact_makes_no_selectivity_or_efficacy_claim():
    p = os.path.join(HERE, "nr4a3-re-reach.json")
    if not os.path.exists(p):
        pytest.skip("artifact not generated in this checkout")
    with open(p) as fh:
        blob = json.load(fh)
    v = json.dumps(blob["verdict"])
    assert "not of sequence selectivity" in v
    assert "not of degradation" in v
    assert "Nothing here is a selectivity claim of any kind." in v


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# The raw inputs themselves
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
@geo
def test_the_fetch_manifest_distinguishes_a_read_failure_from_an_absence():
    with open(os.path.join(INPUTS, "_manifest.json")) as fh:
        m = json.load(fh)
    assert "READ FAILURE" in m["_reading_discipline"]
    for r in m["reads"]:
        assert "http" in r and "error" in r


@geo
def test_the_platform_annotation_was_parsed_and_not_truncated():
    p = os.path.join(INPUTS, "GPL570_id2gene.json.gz")
    if not os.path.exists(p):
        pytest.skip("platform annotation not present")
    with gzip.open(p, "rt") as fh:
        a = json.load(fh)
    assert a["n_probes"] == len(a["id2gene"])
    assert a["n_probes"] > 50000
