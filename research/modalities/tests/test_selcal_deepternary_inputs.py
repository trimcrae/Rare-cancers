"""The curated blind inputs for the DeepTernary head-to-head — and the asymmetry that must stay visible."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(HERE, "selcal-deepternary-inputs-curated.json")


def _d():
    return json.load(open(ART))


def test_the_sealed_reference_is_never_used_as_an_input():
    """The whole point of a blind control: the native ternary supplies the ANSWER, never the question."""
    d = _d()
    for arm, v in d["arms"].items():
        sealed = v["native_ternary_sealed"]
        assert v["poi_binary"]["pdb"] != sealed, arm
        assert v["e3_binary"]["pdb"] != sealed, arm
        assert sealed not in v["alternates"]["poi"] + v["alternates"]["e3"], arm


def test_both_arms_are_scored_against_our_own_cofold_on_the_same_arm():
    """The valid comparison is each arm vs OUR co-fold on that arm, so the number to beat is carried in the
    config rather than looked up later from memory."""
    for v in _d()["arms"].values():
        assert v["our_cofold_score_to_beat"]["fnat"] == 0.0
        assert v["our_cofold_score_to_beat"]["source"] == "selcal-cofold-dockq.json"


def test_the_arm_asymmetry_is_stated_and_says_the_arms_are_not_comparable():
    """⚠ SMARCA2 gets a binary from the degrader's own CCD series; SMARCA4 gets an unrelated chemotype nine
    years older. A worse SMARCA4 result would be partly an input artifact. If that ever stops being said out
    loud, the two arms will get read against each other and the reading will be wrong."""
    note = _d()["⚠_asymmetry_between_the_arms"]
    assert "NOT equally well supplied".lower() in note.lower()
    assert "arms are NOT comparable to each other" in note
    assert "input-quality artifact" in note


def test_what_is_still_unverified_is_listed_rather_than_assumed():
    """Ligand identity came from an RCSB name and molecular weight, not from a substructure match. The prep
    step has to confirm it and refuse otherwise — recorded before the run, not after it disappoints."""
    open_items = " ".join(_d()["_open_before_running"])
    assert "not verified as a substructure" in open_items
    assert "REFUSE rather than proceed" in open_items
    assert "chain ids for each binary are not yet resolved" in open_items


def test_the_blindness_guarantee_is_stated_at_its_real_strength():
    """Binaries would not appear in a ternary database regardless of date, so 'not in the exclusion set' is a
    weak guarantee here. Saying so is the difference between a caveat and a claim."""
    d = _d()
    assert "weak guarantee and is stated as one" in d["_none_of_these_are_in_the_exclusion_set"]
    assert "Only the native ternary POSE stays sealed" in d["_blindness_rule"]
