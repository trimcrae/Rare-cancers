"""`V20`'s refutation must stay readable end to end from committed files.

⛔ WHAT THIS PROTECTS. The decoy null is the headline of the recommended paper framings and the program's
most load-bearing negative, and until 2026-08-07 its primary run output existed only in S3 -- the audit's
own rule (*persist the primary artifact*) failed by the audit's own result. The output is now under
`results/nr4a3-decoy/`, and the thing that makes it an evidence CHAIN rather than a second place to look
is the check that it reproduces the committed constant the paper quotes.

⚠ EXACTLY ONE OF THE THREE ARCHIVED ARMS MAY REPRODUCE IT, and that is the assertion with teeth. Zero
would mean the constant has no committed primary output after all. More than one would mean the constant
does not identify a run -- and the two multi-snapshot arms return materially different margins from the
same docked poses, so ambiguity here would put an unresolvable question under every sentence citing it.
"""
from __future__ import annotations

import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MODALITIES))
MODULE = os.path.join(MODALITIES, "decoy_null_provenance.py")
ARTIFACT = os.path.join(MODALITIES, "decoy-null-provenance.json")

_spec = importlib.util.spec_from_file_location("decoy_null_provenance", MODULE)
dnp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dnp)


@pytest.fixture(scope="module")
def doc():
    return dnp.build()


def test_the_primary_output_is_committed_and_readable(doc):
    """The whole of `Q17`: not "an artifact exists" but "the three arms could be READ from git"."""
    unread = [a["arm"] for a in doc["arms"] if not a.get("read")]
    assert not unread, ("these MM-GBSA arms are not committed under results/nr4a3-decoy/ -- re-run "
                        "archive-results-aws.yml mode=archive prefixes=nr4a3-decoy: %r" % unread)


def test_exactly_one_arm_reproduces_the_committed_constant(doc):
    matching = doc["_derived"]["arms_reproducing_the_constant"]
    assert len(matching) == 1, (
        "the committed constant DECOY_2026_06_30 must identify EXACTLY ONE archived run. Got %r -- "
        "zero means the chain is broken again; more than one means every citation of the constant is "
        "ambiguous about which run it names." % (matching,))
    assert matching == ["-mmgbsa"], (
        "the canonical null is the SINGLE-snapshot arm; a multi-snapshot arm matching instead would mean "
        "the paper's §2.6 number and its §2.7 de-noising number have been conflated")
    assert doc["_derived"]["chain_is_end_to_end"] is True


def test_the_multi_snapshot_arms_are_kept_and_are_NOT_the_null(doc):
    """⚠ THEY ARE ARCHIVED ON PURPOSE. They are §2.7's de-noising evidence, and keeping them beside the
    null is what stops a future reader picking whichever file is nearest."""
    others = [a for a in doc["arms"] if a["arm"] != "-mmgbsa" and a.get("read")]
    assert others, "the multi-snapshot arms were dropped from the archive"
    for a in others:
        assert a["reproduces_DECOY_2026_06_30"] is False, a["arm"]
        assert a["scheme"], "%s carries no method scheme, so it cannot be told apart" % a["arm"]
        assert "MULTI-snapshot" in a["scheme"], a["scheme"]


def test_the_canonical_arm_holds_all_thirty_eight_drugs(doc):
    arm = next(a for a in doc["arms"] if a["arm"] == "-mmgbsa")
    assert arm["n_candidates"] == 38, arm["n_candidates"]
    assert arm["n_margins"] == 38, "a margin is missing from a drug record"
    # The roadmap owns the verdict and the percentage; this only asserts the record is complete enough
    # to reproduce them, and that the positive count is a majority (which is the refutation's shape).
    assert arm["n_positive_margin"] > arm["n_candidates"] / 2, arm


def test_the_committed_artifact_has_not_drifted():
    assert dnp.main(["--check"]) == 0


def test_the_artifact_states_no_grade():
    """⛔ ONE FACT, ONE PLACE. `V20`'s verdict lives in the roadmap; this artifact indexes files."""
    raw = open(ARTIFACT, encoding="utf-8").read()
    doc = json.loads(raw)
    assert "REFUTED" not in raw, "the verdict has been copied here; the roadmap owns it"
    assert "_rule" in doc and "adds no grade" in doc["_rule"]
