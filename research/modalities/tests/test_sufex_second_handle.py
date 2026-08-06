#!/usr/bin/env python3
"""Guards on the Y419 second-handle finding.

⛔ THE FAILURES THESE PROTECT AGAINST, in the order they would actually happen:

  1. The mandate quietly reverting — the artifact going back to presenting the `V17` cutoff and the
     threshold-free rank as co-equal readings. That is the exact thing path-family-synthesis §2 row 6 says
     to stop doing, and it is a prose-shaped regression that no numeric check would catch.
  2. M398/M399 being dropped SILENTLY instead of by name — the difference between an enumeration and an
     advertisement.
  3. A REAGENT-level statement drifting into an engagement or a therapeutic one. `lint_claims.py` runs only
     in CI; this is the local half.
  4. A roadmap edit whose anchor has been reworded — it would simply never apply, and the generator would
     still report success. Same failure `test_map_edit_anchors.py` exists for, applied to this generator.
  5. The competitor census being read as the chemoselectivity window it is NOT.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import sufex_second_handle as S           # noqa: E402

ART = os.path.join(MOD, "sufex-second-handle.json")


@pytest.fixture(scope="module")
def art():
    if not os.path.exists(ART):
        pytest.skip("artifact not generated in this checkout")
    with open(ART, encoding="utf-8") as fh:
        return json.load(fh)


# ----------------------------------------------------------------------------------------------------------
# 1 · the ruling
# ----------------------------------------------------------------------------------------------------------
def test_the_ruler_is_the_rank_not_the_cutoff(art):
    r = art["the_reported_ruler"]
    assert "RANK" in r["THE_RULER"].upper()
    assert "cutoff" not in r["THE_RULER"].lower()


def test_the_cutoff_reading_is_labelled_superseded_and_not_offered_as_an_alternative(art):
    """The cutoff reading MUST still be present — registering it is how the sweep stays gradeable — but it
    may never be presented as a co-equal choice."""
    sup = art["the_reported_ruler"]["under_the_superseded_cutoff"]
    assert sup["chemically_credible_set"], "the superseded reading was dropped, not registered"
    assert "SUPERSEDED" in sup["_reading"].upper()
    # ⚠ SCOPED TO WHAT THIS FILE REPORTS. `map_edits_required` legitimately QUOTES the retired sentence —
    # as the anchor it targets and as the reason for the edit — and a test that fired on that would be
    # firing on the fix. Everything else may not carry it.
    reported = {k: v for k, v in art.items() if k != "map_edits_required"}
    assert "neither reading is chosen" not in json.dumps(reported, ensure_ascii=False).lower(), \
        "the co-equal framing the mandate retires has come back into what this file reports"


def test_y419_clears_the_reference_and_fails_the_cutoff_and_both_are_stated(art):
    y = art["the_reported_ruler"]["Y419"]
    assert y["clears_the_reference"] is True
    assert y["clears_the_V17_cutoff"] is False, \
        "if this ever flips, the finding no longer depends on which ruler is used and the framing must change"
    assert y["rsa"] > art["the_reported_ruler"]["reference_rsa"]
    assert 1 <= y["rank_among_tetherable_unique_handles"] <= y["n_tetherable_unique_handles_ranked"]


def test_every_cited_M2_number_matches_the_artifact_that_owns_it():
    """⛔ RULE 1. This file may not be a second home. Every quoted figure is re-read from
    selectivity-mechanism-options.json and must still agree."""
    m2 = S._load(S.SELMECH)["measurements"]["M2"]
    res = S.build()
    owner = {h["class"] + str(h["uniprot"]): h for h in m2["lbd_unique_handles"]}
    assert res["the_reported_ruler"]["Y419"]["rsa"] == owner["Y419"]["rsa"]
    assert res["the_reported_ruler"]["reference_rsa"] == m2[
        "read_against_the_V17_positive_control_instead_of_the_cutoff"]["reference_rsa"]
    for d in res["explicitly_dropped"]["dropped"]:
        assert d["rsa"] == owner[d["label"]]["rsa"]


# ----------------------------------------------------------------------------------------------------------
# 2 · the drops
# ----------------------------------------------------------------------------------------------------------
def test_m398_and_m399_are_dropped_BY_NAME_with_their_numbers(art):
    d = art["explicitly_dropped"]
    assert set(d["not_carried_forward"]) == {"M398", "M399"}
    for row in d["dropped"]:
        assert row.get("status") != "NOT_IN_ARTIFACT", "the drop could not be targeted"
        assert row["clears_the_reference"] is False
        assert row["clears_the_V17_cutoff"] is False
        assert isinstance(row["rsa"], (int, float))
        assert "DROPPED" in row["VERDICT"]


def test_a_dropped_handle_is_never_in_the_admitted_set(art):
    admitted = " ".join(art["the_reported_ruler"]["NEW_handles_the_ruling_admits"])
    for lab in art["explicitly_dropped"]["not_carried_forward"]:
        assert lab not in admitted


# ----------------------------------------------------------------------------------------------------------
# 3 · language discipline — REAGENT level only
# ----------------------------------------------------------------------------------------------------------
FORBIDDEN = ("therapeutic window", "clinically ready", "clinical readiness", "proteome-wide selectivity of",
             "is safe", "efficacious", "will degrade", "drug candidate")


def test_no_claim_above_reagent_level(art):
    blob = json.dumps(art, ensure_ascii=False).lower()
    for phrase in FORBIDDEN:
        # ⚠ Several of these appear inside the artifact's OWN disclaimers ("no ... therapeutic window").
        # A bare substring test would fail on the disclaimer that exists to prevent the claim. So the test
        # is that every occurrence is negated.
        i = 0
        while True:
            i = blob.find(phrase, i)
            if i < 0:
                break
            # 220 chars, because the artifact's own disclaimer lists six forbidden claims after one "no
            # claim about", so the negation can be a long way in front of the last item in the list.
            window = blob[max(0, i - 220):i]
            assert any(n in window for n in ("no ", "not ", "never", "nothing", "does not", "cannot")), \
                "un-negated occurrence of %r" % phrase
            i += len(phrase)


def test_the_limits_block_names_the_things_that_are_not_modelled(art):
    lim = " ".join(art["⛔_limits"]).lower()
    assert "pka" in lim
    assert "one static opened conformer" in lim
    assert "two paralogues" in lim
    assert "r5" in lim, "a second handle does not unblock Route B and the artifact must say so"


# ----------------------------------------------------------------------------------------------------------
# 4 · roadmap edits — described, never applied
# ----------------------------------------------------------------------------------------------------------
def test_the_generator_does_not_write_any_locked_file():
    src = open(os.path.join(MOD, "sufex_second_handle.py"), encoding="utf-8").read()
    # The only `open(..., "w")` in this module is the artifact write.
    assert src.count('"w"') == 1
    for locked in S.LOCKED:
        assert ('open(%r, "w"' % locked) not in src


def test_every_described_edit_resolved_against_the_live_map(art):
    v = art["map_edits_required"]["verification"]
    assert v["n_entries"] == v["n_applicable"], \
        "an edit could not be targeted — retarget it, do not lower the bar (see test_map_edit_anchors.py)"
    assert v["n_stale"] == 0 and v["n_unlocatable"] == 0


def test_current_text_is_byte_exact_in_the_live_map(art):
    """The `grep -F` a consumer would run, run here."""
    import map_edits as ME
    text = ME.load_map()
    if text is None:
        pytest.skip("roadmap not present in this checkout")
    for e in art["map_edits_required"]["entries"]:
        if e.get("status") != "OK":
            continue
        assert text.count(e["current_text"]) == 1, "anchor %r no longer unique/exact" % e["anchor"]
        assert e["proposed_text"] != e["current_text"], "a no-op edit is not an edit"


def test_the_10_1_row_is_anchored_inside_the_table_not_under_the_heading(art):
    """⛔ A `|`-row appended under the §10.1 HEADING lands before the table header and renders broken —
    the heading is followed by a prose paragraph. It must anchor on the last existing table row."""
    for e in art["map_edits_required"]["entries"]:
        if "10.1" in e["section"]:
            assert e["current_text"].lstrip().startswith("|"), \
                "the §10.1 row edit is anchored on a non-table line"


# ----------------------------------------------------------------------------------------------------------
# 5 · the competitor census
# ----------------------------------------------------------------------------------------------------------
def test_the_census_says_plainly_that_it_is_not_the_window(art):
    c = art["sufex_competitor_census"]
    assert "NOT the chemoselectivity window" in c["_what_this_is_NOT"]
    assert "cysteine" in c["_S1_window_citations"]["competitor_set_is_cysteine_only"].lower()


def test_the_sufex_competitor_set_is_larger_than_the_cysteine_one_on_both_residue_sets(art):
    c = art["sufex_competitor_census"]
    wide = c["sufex_warhead"]["n_at_or_inside_Y419_distance_shell"]
    narrow = c["sufex_warhead_narrow_set_sensitivity"]["n_at_or_inside_Y419_distance_shell"]
    cys = c["cysteine_warhead"]["n_at_or_inside_Y419_distance_shell"]
    assert cys > 0
    assert wide > cys and narrow > cys, \
        "the whole consequence rests on this direction; if it inverts the finding must be rewritten"
    assert wide >= narrow


def test_unreliable_paralogue_positions_are_excluded_and_counted_not_dropped(art):
    for key in ("sufex_warhead", "cysteine_warhead"):
        b = art["sufex_competitor_census"][key]
        assert b["n_reliable"] + b["n_excluded_unreliable"] == b["n_reactive_atoms_all_three_models"]


def test_nr4a3_rows_are_never_marked_unreliable(art):
    """NR4A3 is the reference frame — it is not superposed, so nothing about it can be off-core. A row that
    says otherwise means the reliability rule leaked across models."""
    for key in ("rows_sufex", "rows_cysteine"):
        for r in art["sufex_competitor_census"][key]:
            if r["protein"] == "NR4A3":
                assert r["position_reliable_in_nr4a3_frame"] is True
                assert r["post_fit_deviation_A"] == 0.0


def test_pocket_residues_are_self_excluded_so_no_distance_is_a_tautology(art):
    """A pocket-LINING residue is ~0 A from 'the pocket' by construction. M2 excluded its own atoms before
    taking the minimum and so does this; a 0.0 A row would be that tautology coming back."""
    for r in art["sufex_competitor_census"]["rows_sufex"]:
        assert r["dist_to_cryptic_pocket_A"] > 0.0


def test_the_pocket_mirror_matches_its_owner():
    import nr4a_paralogue_unique_residues as U
    S._assert_pocket_matches_owner(U.CRYPTIC_POCKET_UNIPROT)


# ----------------------------------------------------------------------------------------------------------
# 6 · the literature record
# ----------------------------------------------------------------------------------------------------------
def test_every_citation_carries_a_verification_level(art):
    for e in art["literature_record"]["entries"]:
        assert e["verification"], "a citation with no verification level is an unfalsifiable citation"
        assert e["url"].startswith("https://")
        assert e["what_it_does_NOT_establish"], \
            "a citation with no stated limit is a citation being used as an argument"


def test_no_citation_asserts_an_identifier_it_could_not_see(art):
    """⛔ THE GOLDEN RULE. Where a DOI or PMID was not visible in a returned URL, the field is null — never
    a plausible-looking guess. This asserts the fields that ARE populated look like real identifiers."""
    for e in art["literature_record"]["entries"]:
        if e.get("doi") is not None:
            assert e["doi"].startswith("10."), e["doi"]
        if e.get("pmid") is not None:
            assert e["pmid"].isdigit(), e["pmid"]


def test_the_verdict_does_not_upgrade_precedented_to_routine(art):
    v = art["literature_record"]["★_verdict"].lower()
    assert "not routine" in v or "not be routine" in v
    assert "binding-site" in v, "the precedent/site mismatch is the load-bearing part and must be stated"


def test_regenerates_without_drift():
    """The artifact is generated, not typed. If this fails, the committed copy is stale."""
    if not os.path.exists(ART):
        pytest.skip("artifact not generated in this checkout")
    old = json.load(open(ART, encoding="utf-8"))
    old.pop("_generated", None)
    new = json.loads(json.dumps(S.build()))
    new.pop("_generated", None)
    assert old == new
