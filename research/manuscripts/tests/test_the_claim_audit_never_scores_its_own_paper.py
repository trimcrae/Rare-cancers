"""The claim-audit sampler must never emit a support verdict, and its draw must be reproducible.

⛔⛔ WHY THIS FILE EXISTS. `claim_audit.py` implements the SAMPLING half of Kosmos's stratified audit
protocol (research/method-watch-autonomy-prior-art-2.md §4.1, §4.2) and deliberately stops there.
The Supported/Refuted/Unverifiable classification is the human or blind-seat step, because the whole
value of Kosmos's 57.9% is that expert scientists OUTSIDE the system went and reproduced the
analysis. A tool that scored its own paper would be the author's own model grading the author's own
sentences on the axis where that model is measured least reliable, and it would return a comfortable
number carrying no information.

★ THAT INVARIANT IS ONE LINE OF PROSE IN A DOCSTRING, WHICH IS THE SAME THING AS A HOPE. A future
edit that adds a heuristic verdict — "this row has a matching pin, call it supported" — would look
like an improvement, pass every other gate in this repository, and silently destroy the only reason
the measurement is worth having. So the invariant is measured here instead.

⚠ WHAT THIS DOES NOT ASSERT. Not that any type assignment is correct — the classification is a
documented heuristic and every row carries its `signals` so a reader can dispute it per sentence.
Not that the manifest's evidence handles SUPPORT the sentences they hang on. Only that the tool
refuses to grade, and that the draw is a function of the seed and the sentence text.
"""
from __future__ import annotations

import importlib.util
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(HERE, "..", "claim_audit.py")
MANUSCRIPT = os.path.join(
    HERE, "..", "aso", "fusion-junction-aso-journal-article.md"
)


def _load():
    spec = importlib.util.spec_from_file_location("claim_audit_under_test", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def manifest():
    mod = _load()
    return mod.build_manifest(os.path.abspath(MANUSCRIPT), 20260828, 6)


def test_every_emitted_verdict_is_null(manifest):
    """The tool grades nothing. Every sampled row leaves `verdict` for a verifier to fill in."""
    graded = [r for r in manifest["sample"] if r.get("verdict") is not None]
    assert graded == [], (
        "claim_audit.py emitted %d verdict(s). It must not classify support — that is the "
        "human/blind-seat step, and a tool that scores its own paper is the failure mode the "
        "audit exists to catch. Offending claim ids: %s"
        % (len(graded), [r["claim_id"] for r in graded])
    )


def test_the_verdict_fields_are_present_and_empty(manifest):
    """Present so a verifier has somewhere to write; empty so nothing pretends to be graded."""
    for row in manifest["sample"]:
        for field in ("verdict", "verdict_evidence", "verdict_by"):
            assert field in row, "row %s has no %s field to fill in" % (row["claim_id"], field)
            assert row[field] is None, (
                "row %s pre-fills %s — the sampler must leave the verification to a verifier"
                % (row["claim_id"], field)
            )


def test_the_module_defines_no_support_vocabulary_of_its_own():
    """SUPPORTED/REFUTED may appear only as the TALLY's input vocabulary, never as an output.

    `tally()` does arithmetic over verdicts somebody else wrote, so it has to name them. What must
    not exist is an assignment that gives a row one of those values.
    """
    mod = _load()
    assert set(mod.VERDICTS) == {"SUPPORTED", "REFUTED", "UNVERIFIABLE"}
    with open(MODULE, encoding="utf-8") as fh:
        source = fh.read()
    for verdict in mod.VERDICTS:
        bad = '"verdict": "%s"' % verdict
        assert bad not in source, (
            "claim_audit.py assigns %s to a row. The sampler must not grade." % verdict
        )


def test_the_draw_is_reproducible_from_the_seed(manifest):
    """Same manuscript, same seed, same sample — otherwise an audit cannot be re-run or disputed."""
    mod = _load()
    again = mod.build_manifest(os.path.abspath(MANUSCRIPT), 20260828, 6)
    assert [r["claim_id"] for r in again["sample"]] == [
        r["claim_id"] for r in manifest["sample"]
    ]


def test_a_different_seed_draws_a_different_sample(manifest):
    """A seed that changes nothing would make `--seed` a decoration and the sample unfalsifiable."""
    mod = _load()
    other = mod.build_manifest(os.path.abspath(MANUSCRIPT), 20260829, 6)
    assert [r["claim_id"] for r in other["sample"]] != [
        r["claim_id"] for r in manifest["sample"]
    ]


def test_all_three_strata_are_populated(manifest):
    """A stratified audit with an empty stratum is not stratified; it is a silent single sample."""
    for claim_type in ("DATA-ANALYSIS", "LITERATURE", "INTERPRETATION"):
        assert manifest["strata"][claim_type]["population"] > 0, (
            "%s stratum is empty on the ASO journal article — the classifier has stopped "
            "distinguishing claim types, and every rate computed from it would be meaningless"
            % claim_type
        )
        assert manifest["strata"][claim_type]["sampled"] > 0


def test_the_tally_refuses_to_invent_a_verdict():
    """A row still holding null counts as UNSCORED. It must never be folded into `supported`."""
    mod = _load()
    fake = {
        "sample": [
            {"type": "INTERPRETATION", "verdict": "SUPPORTED"},
            {"type": "INTERPRETATION", "verdict": None},
            {"type": "INTERPRETATION", "verdict": "REFUTED"},
        ]
    }
    got = mod.tally(fake)["INTERPRETATION"]
    assert got["n_sampled"] == 3
    assert got["n_scored"] == 2
    assert got["n_unscored"] == 1
    assert got["supported"] == 1 and got["refuted"] == 1
    assert got["supported_rate_of_scored"] == 0.5
    assert got["supported_rate_of_sampled"] == pytest.approx(1 / 3, abs=1e-4)
