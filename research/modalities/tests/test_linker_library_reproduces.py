#!/usr/bin/env python3
"""
THE LOUD HALF OF THE ANTI-DRIFT GUARD — it RE-RUNS the linker generator and refuses a third enumeration.

⛔ THE FAILURE THIS EXISTS TO MAKE IMPOSSIBLE. On 2026-08-02 a shared geometry kernel was corrected
(`382c36947`, `linker_design.three_ball_min_margin`). The correction was right and its own commit named one
downstream artifact it invalidated — and missed a second, `nr4a3-linker-design.json`. For a day the committed
library and its generator disagreed by three constructs, including the molecule the causal test article is
built from, and **nothing in the repo could notice**, because the artifact had not changed. A test that pins
the artifact alone would have passed throughout.

So this test pins the CODE's output instead. It re-runs the generator (~5 s) and asserts its construct-id set
is exactly the CORRECTED set registered in `nr4a3-linker-library-canonical.json`. Any third set means a kernel
or the generator moved again — which is ALLOWED, and must be ruled on and re-registered in the same commit,
exactly as `382c36947` should have been.

⚠ This is deliberately NOT in the fast suite: it costs ~5 s and writes a ~18 MB artifact to a temp dir.
"""

import contextlib
import io
import json
import os
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

RULING = os.path.join(MOD, "nr4a3-linker-library-canonical.json")
DESIGN = os.path.join(MOD, "nr4a3-linker-design.json")
LIB_KEYS = ("virtual_library_at_the_term_a_exemplar", "virtual_library_at_representative_geometry")


def _ids(doc):
    out = {}
    for k in LIB_KEYS:
        for x in doc[k]:
            out[x["construct_id"]] = x
    return out


@pytest.fixture(scope="module")
def regenerated():
    """Run today's generator, exactly as a person re-deriving the test article would."""
    import nr4a3_linker_design as LD
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "regen.json")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = LD.main(["--out", out])
        assert rc == 0, "the linker generator refused to run; that is a failure in its own right"
        with open(out, encoding="utf-8") as fh:
            return json.load(fh)


@pytest.fixture(scope="module")
def ruling():
    with open(RULING, encoding="utf-8") as fh:
        return json.load(fh)


def test_todays_code_still_produces_the_registered_CORRECTED_enumeration(regenerated, ruling):
    reg = ruling["registered_enumerations"]["CORRECTED"]
    got = set(_ids(regenerated))
    exec_ids = set(_ids(json.load(open(DESIGN, encoding="utf-8"))))
    want = (exec_ids - set(ruling["registered_enumerations"]["EXECUTED"]["only_in_this_set"])
            ) | set(reg["only_in_this_set"])
    assert got == want, (
        "⛔ THE LINKER GENERATOR NOW PRODUCES A THIRD ENUMERATION.\n"
        "  new constructs, in neither registered set: %s\n"
        "  registered-corrected constructs it no longer produces: %s\n"
        "This is not necessarily wrong — the last time it happened the change was a genuine geometry fix. "
        "But it MUST be ruled on and re-registered in `nr4a3-linker-library-canonical.json` in the same "
        "commit, naming the cause, or the program is back in the state row 25 was opened for: an artifact "
        "and its generator disagreeing with nothing able to see it. Regenerate with "
        "`python3 research/modalities/nr4a3_linker_library_canonical.py --check`."
        % (sorted(got - want), sorted(want - got)))
    assert len(got) == reg["n_constructs"]
    assert regenerated["library_summary"]["n_enumerated"] == reg["n_enumerated"]


def test_the_committed_artifact_still_does_NOT_reproduce_and_the_ruling_says_why(regenerated):
    """The divergence is REGISTERED, not repaired. If it silently closed, the registration is now a lie."""
    committed = json.load(open(DESIGN, encoding="utf-8"))
    if set(_ids(committed)) == set(_ids(regenerated)):
        pytest.fail(
            "the committed linker library now reproduces from today's code. That is a GOOD state, but it "
            "means either the artifact was regenerated (which the ruling forbids without a new decision) or "
            "the kernel was reverted. Update `nr4a3-linker-library-canonical.json` — leaving a registered "
            "divergence in place when there is none is the same one-fact-two-places failure in reverse.")


def test_the_recommended_matched_pair_still_moves_and_the_ruling_records_both_sides(regenerated, ruling):
    """The single most decision-relevant consequence: re-deriving the test article gives a DIFFERENT molecule."""
    move = ruling["what_actually_moved"]["the_recommendation_that_moved"]
    assert move["the_pair_moved"] is True, (
        "the ruling records the 5a-KS matched pair as unmoved. That is the whole reason row 25 was opened — "
        "if it is now true, re-rule and re-register.")
    got_d = regenerated["matched_pair_for_rung_5a_ks"]["d"]["construct_id"]
    assert got_d == move["CORRECTED"]["d"]["construct_id"], (
        "today's code recommends %r; the ruling registers the corrected recommendation as %r."
        % (got_d, move["CORRECTED"]["d"]["construct_id"]))
    assert move["EXECUTED"]["d"]["construct_id"] != got_d


def test_no_construct_shared_by_the_two_enumerations_changed_its_smiles(regenerated):
    """Independent of the ruling artifact: read both libraries and compare."""
    committed = _ids(json.load(open(DESIGN, encoding="utf-8")))
    now = _ids(regenerated)
    moved = [k for k in set(committed) & set(now) if committed[k].get("smiles") != now[k].get("smiles")]
    assert not moved, (
        "these constructs exist in both enumerations with DIFFERENT SMILES: %s. Every committed molecule "
        "downstream — the 5a-KS endpoints, library-chem's canonical_smiles and InChIKeys, rung 5b-T's "
        "degrader — would need re-checking." % moved)
