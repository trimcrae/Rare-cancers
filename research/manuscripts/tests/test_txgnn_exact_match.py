"""The TxGNN query matcher must resolve an agent to ITSELF, never to a name containing it.

⛔ WHY. `txgnn_predict.relevant_ranks` used a substring test against a descending-sorted ranking,
so it returned the highest-scoring compound whose name CONTAINED the query. Three of 33 queried
agents were reported against a different molecule, and the highest-ranked "hit" of the whole
exercise — reported in the manuscript and in `txgnn-emc-findings.md` as doxorubicin at the 74.7th
percentile — was 13-deoxydoxorubicin. The sibling script in the same directory,
`enumerate-drugs.mjs`, had guarded the identical collision since it was written. A guard described
in a docstring is not a guard; these are the collisions that actually occurred, asserted.
"""
import importlib.util
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PREDICT = os.path.join(ROOT, "research", "hypotheses", "txgnn_predict.py")
REANALYSIS = os.path.join(ROOT, "research", "hypotheses", "txgnn_exact_match_reanalysis.py")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


predict = _load(PREDICT, "txgnn_predict_under_test")
reanalysis = _load(REANALYSIS, "txgnn_exact_match_reanalysis_under_test")


@pytest.mark.parametrize("wrong_name,query", [
    ("13-deoxydoxorubicin", "doxorubicin"),      # EMC and soft-tissue-sarcoma nodes
    ("Zoptarelin doxorubicin", "doxorubicin"),   # chondrosarcoma node
    ("Lapatinib", "apatinib"),                   # the collision enumerate-drugs.mjs already guards
    ("Palifosfamide", "ifosfamide"),
])
def test_a_name_that_merely_contains_the_query_is_not_a_match(wrong_name, query):
    assert not predict.name_matches_query(wrong_name, query)


@pytest.mark.parametrize("name,query", [
    ("Doxorubicin", "doxorubicin"),
    ("Sunitinib Malate", "sunitinib"),
    ("Tivozanib hydrochloride", "tivozanib"),
    ("Pazopanib", "pazopanib"),
])
def test_the_agent_itself_and_its_salt_forms_do_match(name, query):
    assert predict.name_matches_query(name, query)


def test_the_matcher_takes_the_agent_not_the_higher_scoring_lookalike():
    """The whole defect in one assertion: the lookalike outranks the agent and must lose."""
    ranked = [
        {"drug": "13-deoxydoxorubicin", "score": 1.0},
        {"drug": "Zoptarelin doxorubicin", "score": 0.9},
        {"drug": "Doxorubicin", "score": -3.0},
    ]
    predict.RELEVANT = ["doxorubicin"]
    (row,) = predict.relevant_ranks(ranked, len(ranked))
    assert row["matched"] == "Doxorubicin"
    assert row["rank"] == 3


def test_an_agent_absent_from_the_vocabulary_is_absent_and_not_a_low_rank():
    ranked = [{"drug": "Pazopanib", "score": 1.0}]
    predict.RELEVANT = ["fruquintinib"]
    (row,) = predict.relevant_ranks(ranked, 1)
    assert row["matched"] is None and row["rank"] is None
    assert row["match"] == "absent_from_vocabulary"


def test_the_committed_reanalysis_matches_a_fresh_derivation():
    """The manuscript quotes these medians; a hand-edit of the artifact must fail the build."""
    assert reanalysis.main(["--check"]) == 0


def test_the_three_misresolved_queries_carry_no_invented_rank():
    built = reanalysis.build()
    seen = set()
    for disease in built["diseases"]:
        for row in disease["misresolved_by_the_substring_matcher"]:
            seen.add(row["query"])
            assert row["true_rank_of_the_query"] is None
    assert seen == {"doxorubicin", "apatinib", "ifosfamide"}
