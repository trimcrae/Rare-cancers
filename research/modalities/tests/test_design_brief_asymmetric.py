"""`Q16` — the design brief restated asymmetrically, in its harder measured form.

⚠ The two tests that matter are the ones guarding the two ways this brief can be misquoted:

  * `test_the_word_SEPARATED_is_never_carried_unqualified` — the source artifact's own `lead_status` is
    *"LIVE BUT DEMOTED — the asymmetry is real, the word SEPARATED is not carryable"*. A brief that
    carried the word would be quoting a verdict that does not survive the contested `C2` rule.
  * `test_the_exposure_lever_is_withdrawn_in_both_directions` — the HPA table removes the lever AND must
    never be read as evidence against the dopaminergic requirement. Both halves, or neither.
"""
import json
import os

import pytest

import design_brief_asymmetric as B

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "nr4a3-design-brief-asymmetric.json")


@pytest.fixture(scope="module")
def doc():
    if not os.path.exists(ART):
        pytest.skip("artifact not built")
    return json.load(open(ART, encoding="utf-8"))


# ==========================================================================================================
# THE SHAPE OF THE BRIEF
# ==========================================================================================================
def test_the_brief_is_asymmetric_and_both_halves_are_molecular(doc):
    one = doc["★_the_brief"]["one_line"]
    assert "HARD vs NR4A1" in one
    assert "HARD-BUT-LOWER-PRIORITY vs NR4A2" in one
    assert "BOTH MOLECULAR" in one


def test_NR4A2_is_never_called_a_soft_constraint(doc):
    """⛔ The bound is cited (MP:0011087, complete-penetrance neonatal lethality). 'Soft' is the framing
    the measurement retired, and it survives ONLY inside the superseded list."""
    live = json.dumps({k: v for k, v in doc["★_the_brief"].items()
                       if k != "⛔_superseded_retained"}, ensure_ascii=False)
    low = live.lower()
    for i in [j for j in range(len(low)) if low.startswith("soft constraint", j)]:
        ctx = low[max(0, i - 60):i]
        assert "not a" in ctx or "⛔" in ctx, (
            "'soft constraint' appears in the live brief without an explicit refusal: ...%r"
            % live[max(0, i - 60):i + 20])
    assert any("SOFT constraint" in s for s in doc["★_the_brief"]["⛔_superseded_retained"]), \
        "the retired framing must be RETAINED as superseded, not silently dropped"


def test_the_NR4A2_clause_cites_its_floor(doc):
    c = next(c for c in doc["★_the_brief"]["clauses"] if c["id"] == "B2")
    f = doc["the_NR4A2_bound"]["the_floor"]
    assert f["mp_id"] in c["text"]
    for pmid in f["pubmed_ids"]:
        assert pmid in c["text"], "a cited floor must carry its PubMed IDs into the clause"
    assert "complete penetrance" in c["text"]


def test_every_clause_carries_its_own_sensitivity(doc):
    for c in doc["★_the_brief"]["clauses"]:
        assert c.get("⚠_sensitivity"), "%s has no sensitivity attached" % c["id"]
        assert len(c["⚠_sensitivity"]) > 40


# ==========================================================================================================
# ★ THE WORD
# ==========================================================================================================
def test_the_word_SEPARATED_is_never_carried_unqualified(doc):
    """★ THE LOAD-BEARING TEST. Wherever `SEPARATED` appears in a clause, the same clause must say it is
    not carryable and name what breaks it."""
    for c in doc["★_the_brief"]["clauses"]:
        blob = json.dumps(c, ensure_ascii=False)
        if "SEPARATED" not in blob:
            continue
        s = c["⚠_sensitivity"]
        assert "do not carry the word SEPARATED" in s, c["id"]
        assert "C2" in s, "the sensitivity must name the contested rule that breaks it"


def test_the_lead_status_is_read_from_the_source_and_not_paraphrased(doc):
    src = json.load(open(B.ASYM, encoding="utf-8"))
    assert doc["★_the_asymmetry_read"]["lead_status"] == src["verdict"]["lead_status"]
    assert "not carryable" in doc["★_the_asymmetry_read"]["lead_status"]


def test_the_two_axes_are_split_and_labelled(doc):
    per = doc["★_the_asymmetry_read"]["by_paralogue"]
    assert per["NR4A1"]["axis"] == "mandatory"
    assert per["NR4A2"]["axis"] == "best_effort"
    assert per["NR4A1"]["verdict_under_the_frozen_rule"] != per["NR4A2"]["verdict_under_the_frozen_rule"], \
        "the whole point of the split is that the two axes got different answers"


def test_all_three_cautions_travel_with_the_mandatory_axis(doc):
    t = doc["★_the_asymmetry_read"]["by_paralogue"]["NR4A1"]["★_three_cautions"]
    assert t["contested_C2_rule"]["survives_the_rule_change"] is False
    assert t["design_effect_corrected_wilson"]["intervals_overlap"] is True
    assert t["design_floor"]["p_one_sided"] == t["design_floor"]["p_one_sided_FLOOR"], (
        "the exact test is at its design floor; if it ever is not, the 'ceiling of the design' reading "
        "must be revisited deliberately")


def test_the_design_floor_caution_says_the_p_is_a_ceiling_not_a_significance(doc):
    for par, r in doc["★_the_asymmetry_read"]["by_paralogue"].items():
        w = r["★_three_cautions"]["design_floor"]["⚠"]
        assert "never 'just significant'" in w


# ==========================================================================================================
# ★ THE EXPOSURE LEVER
# ==========================================================================================================
def test_the_exposure_lever_is_withdrawn_in_both_directions(doc):
    lv = doc["the_NR4A2_bound"]["the_exposure_lever"]
    c = lv["counts"]
    assert c["nr4a2_dominant"] == 0 and c["nr4a2_unbuffered"] == 0
    assert c["nr4a2_and_nr4a3_co_expressed"] > 0
    assert "MOLECULAR" in lv["⛔_reading"]
    warn = doc["the_NR4A2_bound"]["⚠_what_the_table_may_NOT_be_quoted_for"]
    assert "NOT EVIDENCE AGAINST A DOPAMINERGIC REQUIREMENT" in warn
    assert "substantia nigra" in warn


def test_the_expression_counts_are_read_from_their_one_home(doc):
    src = json.load(open(B.SPARING, encoding="utf-8"))
    b3 = src["verdict"]["gates"]["B3_tissue_overlap_measured"]
    assert doc["the_NR4A2_bound"]["the_exposure_lever"]["counts"] == b3["counts"]
    assert doc["the_NR4A2_bound"]["the_exposure_lever"]["n_tissues"] == b3["n_tissues"]


def test_the_developmental_vs_adult_ceiling_is_stated_as_a_clause_not_a_footnote(doc):
    c = next(c for c in doc["★_the_brief"]["clauses"] if c["id"] == "B4")
    assert "CEILING OF CONCERN" in c["text"]
    assert "absence of evidence" in c["text"]


# ==========================================================================================================
# LANGUAGE DISCIPLINE AND POSE MARGINALISATION
# ==========================================================================================================
def test_the_brief_declares_what_it_does_not_contain(doc):
    none = " ".join(doc["★_the_brief"]["⛔_this_brief_contains_no"]).lower()
    for x in ("free energy", "margin", "window", "therapeutic window", "clinical readiness",
              "pose-"):
        assert x in none


def test_no_clause_names_a_pose_a_vector_or_a_construct(doc):
    blob = json.dumps(doc["★_the_brief"], ensure_ascii=False).lower()
    for token in ("exitvec", "denovo_401", "vhl|", "crbn|", "docked pose"):
        assert token not in blob, "the brief re-specialises to %r" % token


def test_the_pose_marginalisation_states_why_the_brief_is_statable_today(doc):
    pm = doc["_pose_marginalisation"]
    assert "NEITHER R3 NOR R5" in pm["why_it_is_nonetheless_statable_today"]
    assert pm["evidence"]["read"] is True
    assert pm["evidence"]["R5_resolved"] is False


def test_every_superseded_framing_is_retained_rather_than_deleted(doc):
    sup = doc["★_the_brief"]["⛔_superseded_retained"]
    assert len(sup) >= 4
    joined = " ".join(sup)
    for phrase in ("UNBOUNDED", "exposure question", "conjoined verdict", "SEPARATED"):
        assert phrase in joined
