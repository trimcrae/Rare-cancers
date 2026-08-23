"""Guards for the threshold-agnostic coverage curve, and for its agreement with the manuscript.

⛔ WHAT THIS EXISTS TO CATCH. The vaccine manuscript's §2.3 states coverage at three thresholds in
prose (0.45 -> 23.2%, 0.40 -> 8.5%, 0.37 -> 0%) and now also publishes the whole function as an
artifact. Two copies of the same fact is exactly the drift CLAUDE.md rule 1 is about, and nothing
else compares them: `lint_consistency.py` sees prose, not JSON. So the first test below reads the
numbers OUT OF THE MANUSCRIPT and asserts the artifact reproduces them.

⚠ NONE OF THESE RE-IMPLEMENT THE CURVE. The one way to fake this suite would be to recompute
`1 - prod(1-af)^2` here and assert it matches itself; the assertions are instead structural
(monotonicity, the declared ceiling) or cross-artifact (the manuscript, `coverage-curve.json`).
"""
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
CURVE = os.path.join(MOD, "coverage-threshold-curve.json")
ALLELE_CURVE = os.path.join(MOD, "coverage-curve.json")
MS = os.path.join(REPO, "research", "manuscripts", "neoantigen",
                  "emc-vaccine-development-path.md")

pytestmark = pytest.mark.skipif(not os.path.exists(CURVE),
                                reason="coverage-threshold-curve.json not yet generated")


def _curve():
    with open(CURVE) as fh:
        return json.load(fh)


def _at(d, t):
    return next((r for r in d["curve"] if abs(r["threshold"] - t) < 1e-9), None)


@pytest.mark.committed_artifact
def test_the_artifact_reproduces_every_threshold_the_manuscript_states_in_prose():
    """⛔ The prose and the JSON are two homes for one fact; this is the only thing joining them."""
    with open(MS) as fh:
        text = fh.read()
    # §2.3's sentence, whatever its current wording: "to <cut> leaves <n> allele(s) and <pct>%".
    stated = re.findall(r"to\s+(0\.\d+)\s+leaves\s+(\w+)(?:\s+alleles?)?\s+and\s+([\d.]+)%",
                        text)
    assert stated, "§2.3 no longer states threshold points in the form this test reads"
    words = {"none": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    d = _curve()
    for cut, n_word, pct in stated:
        row = _at(d, float(cut))
        assert row, f"the curve has no point at the threshold {cut} the manuscript states"
        n = words.get(n_word.lower(), None)
        assert n is not None, f"unparsed allele count {n_word!r}"
        assert row["n_presenting_alleles"] == n, f"at {cut}: prose says {n}, artifact says {row}"
        assert abs(row["coverage"] * 100 - float(pct)) < 0.05, (
            f"at {cut}: prose says {pct}%, artifact says {row['coverage'] * 100}%")


@pytest.mark.committed_artifact
def test_every_step_the_artifact_finds_is_named_in_the_manuscript_with_its_own_numbers():
    """§2.3 now walks the staircase step by step; a step the prose does not carry has drifted.

    ⚠ Containment, not a parse. Asserting the prose PARSES into the artifact would make this test a
    second reader of the sentence, and it would then break on rewording rather than on drift. What
    it asserts is that each step's threshold, its coverage and its allele all appear in the text.
    """
    with open(MS) as fh:
        text = fh.read()
    d = _curve()
    # ⚠ SCOPED TO THE STEPS BELOW THE CONVENTIONAL CUT, which is what §2.3 walks one by one. The
    # curve now runs well above that cut and its steps there are reported in aggregate, not named
    # individually; requiring all of them in prose would force a 28-item list into the manuscript.
    steps = [st for st in d.get("steps") or [] if st["threshold"] <= d["conventional_threshold"]]
    assert steps, "the artifact reports no steps at or below the conventional cut"
    for st in steps:
        assert f"{st['threshold']:.4f}".rstrip("0") in text or str(st["threshold"]) in text, (
            f"the manuscript never states the step at {st['threshold']}")
        pct = f"{st['coverage_after'] * 100:.1f}%"
        assert pct in text, f"the manuscript never states {pct}, the coverage after {st['threshold']}"
        for allele in st["alleles_added"]:
            # the manuscript escapes the asterisk for markdown; compare on the unescaped form
            assert allele.replace("*", r"\*") in text or allele in text, (
                f"the manuscript never names {allele}, which causes the step at {st['threshold']}")


@pytest.mark.committed_artifact
def test_the_conventional_cut_agrees_with_the_allele_curves_headline():
    """The two curves sweep different axes and must meet at the point they share.

    `coverage-curve.json` sweeps allele COUNT at threshold 0.5; this one sweeps THRESHOLD over the
    full panel. Its value at 0.5 is that curve's maximum, or one of them is wrong.
    """
    if not os.path.exists(ALLELE_CURVE):
        pytest.skip("coverage-curve.json absent")
    with open(ALLELE_CURVE) as fh:
        allele_curve = json.load(fh)
    conv = _curve()["at_conventional_threshold"]
    assert conv is not None
    assert abs(conv["coverage"] - allele_curve["global_max_coverage"]) < 1e-9
    assert conv["n_presenting_alleles"] == allele_curve["n_presenting_alleles"]


def test_coverage_never_falls_as_the_cut_loosens():
    """A looser cut can only ADD presenting alleles; a dip means the calls or the pooling drifted."""
    d = _curve()
    prev_cov, prev_n = -1.0, -1
    for row in d["curve"]:
        assert row["coverage"] >= prev_cov - 1e-12, f"coverage fell at {row['threshold']}"
        assert row["n_presenting_alleles"] >= prev_n, f"alleles fell at {row['threshold']}"
        prev_cov, prev_n = row["coverage"], row["n_presenting_alleles"]


def test_no_point_is_drawn_above_the_ceiling_the_artifact_declares():
    """⛔ AN ABSENT READING IS NOT A READING OF ABSENCE. Above the ceiling an allele's absence means
    it was never predicted; a point drawn there would publish "no more alleles" as a finding."""
    d = _curve()
    ceiling = d["_ceiling"]["value"]
    assert d["curve"], "empty curve"
    assert max(r["threshold"] for r in d["curve"]) <= ceiling + 1e-12
    assert d["_ceiling"]["above_the_conventional_cut"] == (ceiling > d["conventional_threshold"])


def test_the_artifact_says_which_run_produced_it():
    """A curve off the strict matrix and a curve off a fresh MHCflurry sweep are different claims."""
    assert _curve()["_provenance"].strip()


def test_the_artifact_refuses_to_read_as_a_case_for_a_looser_threshold():
    """⛔ The disclaimer is load-bearing: this analysis is quoted in a paper about its own limits."""
    d = _curve()
    disclaimer = d["⛔_what_this_is_not"].lower()
    assert "not a better coverage number" in disclaimer
    assert "screen" in disclaimer
