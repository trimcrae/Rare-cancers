"""The instrument census must stay DERIVED from the roadmap, and must go red rather than empty.

⛔ THE FAILURE THIS GUARDS IS THE ONE THAT MADE THE CENSUS NECESSARY. The program's instrument record
lived as two markdown tables inside a 5,000-line document, so every statement of "how many instruments,
how many have a known-answer test, how many requirements have no usable answer" was narrated. A collector
that silently returns zero rows when a heading is reworded would be strictly worse than the prose it
replaced, because a census reading "no instruments have problems" is a positive claim.

So: the parser raises on a missing table and on a wrong-shaped row (asserted below against a mutated
copy), the committed artifacts are checked for drift, and no state may be silently defaulted.

⚠ THIS TEST DOES NOT GRADE AN INSTRUMENT. It never asserts that `V7` fails or that `R4` is a hole -- the
roadmap owns those and would then have two homes. It asserts that whatever the roadmap says is carried
across verbatim and classified from a string a reader can see.
"""
from __future__ import annotations

import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MODALITIES))
MODULE = os.path.join(MODALITIES, "instrument_census.py")

_spec = importlib.util.spec_from_file_location("instrument_census", MODULE)
ic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ic)


@pytest.fixture(scope="module")
def census():
    return ic.build()


def test_the_committed_artifacts_have_not_drifted_from_the_roadmap():
    """A generated view that drifts is a stale fact that reads as a current one -- the same class as the
    branch-drift incident in CLAUDE.md §7. Regenerate with
    `python3 research/modalities/instrument_census.py`."""
    assert ic.main(["--check"]) == 0


def test_the_census_is_not_empty_and_covers_every_instrument_row(census):
    """A parse of zero rows is an ERROR, not an empty census."""
    assert census["_derived"]["n_instruments"] >= 20, census["_derived"]
    assert census["_derived"]["n_requirements"] >= 15, census["_derived"]
    ids = [r["id"] for r in census["instruments"]]
    assert len(ids) == len(set(ids)), "duplicate instrument id in the census"
    assert all(i.startswith("V") for i in ids), ids


def test_no_state_is_silently_defaulted(census):
    """⛔ AN UNREADABLE STATE MUST NOT BECOME A PASSING ONE. `UNCLASSIFIED` is reported rather than
    defaulted, and this test is what makes reporting it consequential -- otherwise a reworded state cell
    would quietly drop an instrument out of every count that matters."""
    assert not census["_derived"]["unclassified_instrument_states"], (
        "these §3.1 state cells match no rule in STATE_RULES -- add the rule (with the reading it "
        "encodes), do not widen an existing one: %r"
        % census["_derived"]["unclassified_instrument_states"])
    assert not census["_derived"]["unclassified_hole_cells"], (
        "these §3.2 hole cells match no rule in HOLE_RULES: %r"
        % census["_derived"]["unclassified_hole_cells"])


def test_every_row_carries_the_string_its_class_was_read_from(census):
    """A classification that cannot be checked against its input is an unhomed opinion."""
    for r in census["instruments"]:
        assert r["state_verbatim"], "%s has a class but no state string" % r["id"]
        assert r["known_answer_test"], "%s names no known-answer test cell at all" % r["id"]
        assert r["scope_limit"], "%s carries no scope limit -- §3.1's whole point" % r["id"]
    for c in census["coverage"]:
        assert c["hole_verbatim"], "%s has a hole class but no hole string" % c["requirement"]


def test_an_instrument_with_no_known_answer_test_is_recorded_as_such(census):
    """⭐ THE FIELD THE CENSUS EXISTS FOR. "Has a known-answer test" and "passed its known-answer test"
    have been collapsed in prose before; they are different objects and the paper framing (`P1`) turns on
    the difference."""
    n_no = census["_derived"]["n_without_a_known_answer_test"]
    assert n_no >= 1, ("§3.1 records instruments whose known-answer-test cell says none exists; if this "
                       "is now zero the detector has broken, not the program improved")
    assert (census["_derived"]["n_with_a_known_answer_test"] + n_no
            == census["_derived"]["n_instruments"])
    listed = set(census["_derived"]["instruments_without_a_known_answer_test"])
    assert listed == {r["id"] for r in census["instruments"] if not r["has_known_answer_test"]}


def test_the_coverage_matrix_only_cites_instruments_that_exist(census):
    """A requirement resting on an instrument with no row is a pointer to nothing -- and §3.2 is where a
    reader goes to find out what a claim stands on."""
    known = {r["id"] for r in census["instruments"]}
    for c in census["coverage"]:
        missing = [i for i in c["instruments"] if i not in known]
        assert not missing, "%s cites instruments with no §3.1 row: %r" % (c["requirement"], missing)


def test_a_missing_table_raises_rather_than_returning_an_empty_census(tmp_path):
    """⛔ THE MOST IMPORTANT ASSERTION IN THIS FILE. A heading reword must be loud."""
    p = tmp_path / "map.md"
    p.write_text("# a roadmap with no instrument table\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        ic.build(str(p))
    assert "table" in str(e.value).lower()


def test_a_wrong_shaped_row_raises_rather_than_shifting_the_columns(tmp_path):
    """⚠ THE `V16` HAZARD, MADE A TEST. Its cells contain `\\|S\\|`; a naive pipe split gives nine cells
    and silently shifts `state` and `serves` by two columns."""
    src = open(os.path.join(ROOT, "research", "manuscripts", "nr4a3-program-map.md"),
               encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(src) if l.startswith(ic.INSTRUMENT_HEADER))
    src[start + 2] = src[start + 2] + " an extra | cell |"
    p = tmp_path / "map.md"
    p.write_text("\n".join(src), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        ic.build(str(p))
    assert "cells" in str(e.value)


def test_the_escaped_pipe_row_is_parsed_with_its_columns_intact(census):
    """The positive half of the test above: `V16` really is read with seven columns, so its `serves` and
    its state are the roadmap's and not the two cells to their left."""
    v16 = next((r for r in census["instruments"] if r["id"] == "V16"), None)
    if v16 is None:
        pytest.skip("V16 is no longer a row in §3.1")
    assert "|S|" in v16["result"] or "\\|S\\|" in v16["result"] or "S = " in v16["result"], v16["result"]
    assert v16["verdict_class"] != "UNCLASSIFIED"


def test_the_json_and_the_md_agree_on_the_counts():
    """Two views, one number. The MD table is rendered from `_derived`, so a disagreement means the
    renderer has started typing figures instead of reading them."""
    js = json.load(open(os.path.join(MODALITIES, "instrument-census.json"), encoding="utf-8"))
    md = open(os.path.join(MODALITIES, "instrument-census.md"), encoding="utf-8").read()
    assert "| instruments in §3.1 | **%d** |" % js["_derived"]["n_instruments"] in md
    assert "| requirements in the §3.2 matrix | **%d** |" % js["_derived"]["n_requirements"] in md
