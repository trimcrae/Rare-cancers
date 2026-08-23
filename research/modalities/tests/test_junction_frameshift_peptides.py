"""Guards for the out-of-frame (frameshift) antigen screen.

⛔ THE ONE THAT MATTERS IS THE UNSCREENED-BINDING GUARD. The script runs anywhere, but MHCflurry is
CI-only. If the binder list defaulted to `[]` the artifact would serialise "0 strong binders" from a
run that never asked a predictor anything — an absent reading printed as a reading of absence, which
is the substitution this repository has paid for more than once. The count must be null until a
predictor actually ran, and these tests hold it there.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "junction-frameshift-peptides.json")

_spec = importlib.util.spec_from_file_location(
    "junction_frameshift_peptides", os.path.join(MOD, "junction_frameshift_peptides.py"))
jf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jf)

pytestmark = pytest.mark.skipif(not os.path.exists(ART),
                               reason="junction-frameshift-peptides.json not yet generated")


def _art():
    with open(ART) as fh:
        return json.load(fh)


def test_novel_kmers_excludes_anything_present_in_either_parent():
    parent_a, parent_b = "AAAAWWWWAAAA", "CCCCYYYYCCCC"
    got = jf.novel_kmers("WWWWAAAAQ", parent_a, parent_b)
    assert all(k not in parent_a and k not in parent_b for k in got)
    assert "WWWWAAAA" not in got, "an 8-mer of parent A survived the filter"


@pytest.mark.committed_artifact
def test_an_unscreened_binder_count_is_null_and_never_zero():
    """⛔ 'not screened' and 'screened, found none' are different claims."""
    d = _art()
    n = d["n_predicted_strong_binders"]
    if n is None:
        assert "NOT SCREENED" in d["⚠_binding_scope"]
        assert d["strong_binders"] is None
    else:
        assert "measured zero" in d["⚠_binding_scope"]


@pytest.mark.committed_artifact
def test_convergent_tracts_are_reported_so_the_peptide_count_is_not_summed():
    """Junctions frameshifting into the same exon share a tract; adding them would inflate it."""
    d = _art()
    conv = d["convergent_tracts"]["shared_tract_after_the_seam_residue"]
    assert isinstance(conv, dict)
    for tract, labels in conv.items():
        assert len(labels) > 1
        for lab in labels:
            row = next(r for r in d["junctions"] if r["junction_label"] == lab)
            assert row["novel_tract"].endswith(tract)


@pytest.mark.committed_artifact
def test_every_junction_carries_an_nmd_reading_that_says_it_is_positional():
    d = _art()
    assert d["junctions"], "no out-of-frame junctions screened"
    for r in d["junctions"]:
        nmd = r["nmd"]
        assert "nmd_predicted" in nmd
        assert any("positional" in k or "positional" in str(v) for k, v in nmd.items()), (
            f"{r['junction_label']}: the NMD reading does not say it is a prediction")


@pytest.mark.committed_artifact
def test_the_artifact_refuses_to_read_as_a_list_of_emc_targets():
    """⛔ These are combinatorial exon pairs, not observed breakpoints."""
    t = _art()["⛔_what_this_is_not"].lower()
    assert "not a set of emc vaccine targets" in t
    assert "combinatorial window" in t
