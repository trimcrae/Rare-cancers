"""Regression tests: a superseded VALUE is asserted only where its NUMBER begins.

WHY THIS FILE EXISTS (2026-09-08). `check_superseded` matched each registry pattern with a
plain unanchored `re.search`, so a digit-initial pattern could match part-way into a longer
number or dotted identifier and be reported as a stated measurement. The measured case:
`card_ratio_4090_over_3090_2_10`'s alternative `2\\.102` matched inside the identifier
`10.1016/j.jbc.2022.102434` (...202`2.102`434) on a reference line and the linter reported
the manuscript as restating the retired 2.10x RTX 4090 / RTX 3090 card ratio.

⚠ THE IDENTIFIER BELOW IS A LEXICAL FIXTURE ONLY. Using the string
`10.1016/j.jbc.2022.102434` here asserts NOTHING about whether that publication exists, what
it contains, or whether it is the same work as any preprint. Its publisher-level and
cross-version status stays unconfirmed; this file only needs a string with those characters
in that order.

Both directions are pinned, because the way this linter dies is by being switched off:
over-tightening it (a real superseded value silently passing) is the worse failure, so every
suppression test here is paired with a positive one built from the REGISTRY'S OWN patterns.
"""

import json
import os
import sys

import pytest

_HERE = os.path.abspath(__file__)


def _lint_dir():
    """Locate lint_consistency.py: an explicit override, the repo layout, or beside this file."""
    env = os.environ.get("LINT_CONSISTENCY_DIR")
    if env and os.path.exists(os.path.join(env, "lint_consistency.py")):
        return env
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
    cand = os.path.join(repo, "research", "manuscripts")
    if os.path.exists(os.path.join(cand, "lint_consistency.py")):
        return cand
    return os.path.dirname(_HERE)


sys.path.insert(0, _lint_dir())

import lint_consistency as lc  # noqa: E402

# The live pattern of the entry this defect was found on. Read from the registry rather than
# retyped, so the tests follow the rule if its pattern is ever re-scoped.
_CARD_RATIO_ID = "card_ratio_4090_over_3090_2_10"


def _card_ratio_entry():
    for e in lc.load_registry()["superseded"]:
        if e["id"] == _CARD_RATIO_ID:
            return e
    pytest.skip(f"registry has no entry {_CARD_RATIO_ID}")


def _reg(tmp_path, entries):
    reg = {
        "targets": ["doc.md"],
        "supersession_markers": ["supersed", "retired", "previously"],
        "derivations": [],
        "table_completeness": [],
        "superseded": entries,
    }
    p = tmp_path / "reg.json"
    p.write_text(json.dumps(reg), encoding="utf-8")
    return json.loads(p.read_text(encoding="utf-8"))


def _run(tmp_path, text, entries):
    (tmp_path / "doc.md").write_text(text, encoding="utf-8")
    return lc.check_superseded(_reg(tmp_path, entries), repo=str(tmp_path))


# --------------------------------------------------------------------------
# NEGATIVE: digits inside an identifier are not an assertion of a value
# --------------------------------------------------------------------------
DOI_FIXTURE = "10.1016/j.jbc.2022.102434"   # lexical fixture; see the module docstring


def test_the_measured_case_a_doi_does_not_state_the_card_ratio(tmp_path):
    """THE BUG, in the shape it was found in: a bibliography line whose DOI happens to
    contain the characters `2.102`. `emc-mtap-prmt5-hypothesis.md:673` was reported as
    `superseded value '2.102' stated without marking it superseded`."""
    entry = _card_ratio_entry()
    text = (f"Journal of Biological Chemistry 2022;298(10):102434. doi {DOI_FIXTURE}. "
            "That record was identified from a search index and was not read here.\n")
    assert _run(tmp_path, text, [entry]) == []


def test_a_bare_identifier_alone_does_not_fire(tmp_path):
    assert _run(tmp_path, f"doi {DOI_FIXTURE}\n", [_card_ratio_entry()]) == []


def test_a_version_string_is_not_a_measurement(tmp_path):
    """`v1.2.102` — the digits follow a dot that itself follows a digit, so they continue an
    identifier rather than beginning a value."""
    assert _run(tmp_path, "pinned at openmm v1.2.102 in the rbfe env\n",
                [_card_ratio_entry()]) == []


def test_a_longer_number_ending_in_the_pattern_is_not_that_number(tmp_path):
    """`1442.102` is not `2.102`."""
    assert _run(tmp_path, "the checkpoint index reached 1442.102 steps\n",
                [_card_ratio_entry()]) == []


# --------------------------------------------------------------------------
# POSITIVE: every real restatement of a superseded value still fires
# --------------------------------------------------------------------------
def test_the_card_ratio_this_rule_exists_to_catch_still_fires(tmp_path):
    """THE TRUE POSITIVE. Current value 1.745x; 2.102 is retired by the 2026-07-27
    median-of-N re-anchoring. Stated flat, with no supersession marker, it is an ERROR."""
    out = _run(tmp_path, "A 4090 does 2.102 times the work of a 3090 on this workload.\n",
               [_card_ratio_entry()])
    assert len(out) == 1 and out[0]["rule"] == "S-" + _CARD_RATIO_ID
    assert "2.102" in out[0]["message"]


@pytest.mark.parametrize("text", [
    "the card ratio is 2.10x on the current estimator\n",       # first alternative, bare x
    "the card ratio is 2.10 × the 3090\n",                      # unicode multiplication sign
    "| RTX 4090 / RTX 3090 | 2.102 | median |\n",               # inside a table row
    "**2.102**\n",                                              # markdown emphasis around it
    "(2.102)\n",                                                # parenthesised
    "ratio 2.102, measured on six hosts\n",                     # trailing comma
    "the ratio is 2.102.\n",                                    # sentence-final full stop
])
def test_real_statements_of_the_retired_ratio_all_fire(tmp_path, text):
    """The formats the registry's targets actually use. A value adjacent to punctuation,
    emphasis or a table pipe still BEGINS its own number, so the left-edge rule leaves it
    alone."""
    assert len(_run(tmp_path, text, [_card_ratio_entry()])) == 1


def test_a_marked_retraction_of_the_ratio_still_clears(tmp_path):
    """The other direction, unchanged: a correctly-written retraction must not be flagged."""
    assert _run(tmp_path, "The 4090/3090 ratio previously stood at 2.102; superseded "
                          "2026-07-27 by the median-of-N re-anchoring to 1.745x.\n",
                [_card_ratio_entry()]) == []


def test_a_genuine_value_later_on_the_same_line_as_an_identifier_still_fires(tmp_path):
    """★ THE FIX MUST NOT INTRODUCE A FALSE NEGATIVE. The scan continues past a fragment
    instead of stopping at it, so a real restatement sharing a line with a DOI is caught."""
    text = (f"See doi {DOI_FIXTURE}; on that basis the card ratio is 2.102 and we plan "
            "around it.\n")
    out = _run(tmp_path, text, [_card_ratio_entry()])
    assert len(out) == 1 and "2.102" in out[0]["message"]


def test_the_registrys_truncating_digit_idiom_is_preserved(tmp_path):
    """`ladder_basis_0_004359`'s pattern is `0\\.00435\\d|0\\.00436\\b|\\$0\\.0043593` — the first
    alternative deliberately matches the LEADING digits of a longer figure. The rule is
    left-edge only precisely so this keeps firing."""
    entry = next((e for e in lc.load_registry()["superseded"]
                  if e["id"] == "ladder_basis_0_004359"), None)
    if entry is None:
        pytest.skip("registry has no entry ladder_basis_0_004359")
    assert len(_run(tmp_path, "the ladder basis is 0.0043593 per ns\n", [entry])) == 1


def test_non_digit_initial_patterns_are_untouched(tmp_path):
    """`$128`, `4080 is within 7 %` and friends do not begin with a digit at all, so the rule
    never looks at them."""
    entries = [{"id": "t", "pattern": r"\$128\b", "current": "$194", "retired_by": "a missing row"}]
    assert len(_run(tmp_path, "the whole gated ladder is $128 for the priceable stages\n",
                    entries)) == 1


# --------------------------------------------------------------------------
# unit-level pins on the predicate itself
# --------------------------------------------------------------------------
@pytest.mark.parametrize("line,start,matched,expected", [
    ("10.1016/j.jbc.2022.102434", 17, "2.102", True),    # interior of an identifier
    ("1442.102", 3, "2.102", True),                      # suffix of a longer number
    ("v1.2.102", 3, "2.102", True),                      # after a digit-preceded dot
    ("ratio 2.102 here", 6, "2.102", False),             # begins its own number
    ("(2.102)", 1, "2.102", False),                      # punctuation is not a digit
    ("**2.102**", 2, "2.102", False),
    ("2.102 leads the line", 0, "2.102", False),         # start of line
    ("was $128 once", 4, "$128", False),                 # non-digit-initial: never suppressed
])
def test_begins_mid_number_predicate(line, start, matched, expected):
    assert line[start:start + len(matched)] == matched, "fixture offset is wrong"
    assert lc._begins_mid_number(line, start, matched) is expected
