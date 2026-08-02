"""THE CATEGORICAL-AXIS AUDIT MUST NOT DRIFT FROM THE ARTIFACTS IT AUDITS.

WHY THIS TEST EXISTS. The audit's whole value is that it is a READING of committed artifacts rather than a
second home for their numbers — CLAUDE.md rule 1. An audit that is typed once and then left behind is worse
than no audit: it looks like a verification and is a stale copy. So the committed
`categorical-axis-audit.json` is regenerated here from the live artifacts and compared field-for-field.

★ AND THE COST OF GETTING THIS WRONG IS MEASURED, NOT HYPOTHETICAL. Writing this module, three figures were
typed by hand into proposed replacement prose and TWO of them were wrong (a tie count of `46 of 102` against
a derived 35 of 93; a `~2.4x` understatement factor against a derived ~1.6x). Both were caught only when the
sentence was changed to interpolate from the artifact. That is the same failure the audit is documenting,
committed by the audit, and it is why the generator interpolates every figure inside a proposed sentence.

The two facts the whole audit turns on are pinned separately below, because a regeneration that silently
started agreeing with a WRONG artifact would still pass the drift check.
"""
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import categorical_axis_audit as CAA  # noqa: E402


def _built():
    return CAA.build()


def test_committed_audit_matches_a_fresh_read_of_the_artifacts():
    """The committed JSON is what the generator produces today. `--check` is the CI-callable form."""
    rc = subprocess.call([sys.executable, os.path.join(MOD, "categorical_axis_audit.py"), "--check"])
    assert rc == 0, ("categorical-axis-audit.json has drifted from the artifacts it audits. "
                     "Regenerate: python3 research/modalities/categorical_axis_audit.py")


def test_C505_and_C534_are_different_sites_with_opposite_uniqueness_status():
    """★ THE RESIDUE-IDENTITY FINDING, pinned. This is the error the audit exists to fix, and a future
    edit that re-merges the two residues must fail here rather than in review."""
    sites = {s["label"]: s for s in _built()["residue_identity"]["sites"]}

    assert sites["C505"]["nr4a3_aligned_residue"] == "C536"
    assert sites["C505"]["nr4a3_has_a_cysteine_here"] is True
    assert sites["C505"]["paralogue_unique_vs_NR4A3"] is False
    assert sites["C505"]["present_in"] == ["NR4A1", "NR4A2"]

    assert sites["C534"]["nr4a3_aligned_residue"] == "S565"
    assert sites["C534"]["nr4a3_has_a_cysteine_here"] is False
    assert sites["C534"]["paralogue_unique_vs_NR4A3"] is True
    assert sites["C534"]["present_in"] == ["NR4A1", "NR4A2"]

    # C551 is NR4A1-only -- the asymmetry that makes it the celastrol confound
    assert sites["C551"]["present_in"] == ["NR4A1"]
    assert sites["C551"]["nr4a3_has_a_cysteine_here"] is False


def test_the_majority_through_space_closer_is_at_a_CONSERVED_position():
    """The reciprocal-uniqueness reading is carried by the CORRIDOR convention, not by both.

    If this ever flips, the roadmap sentence 'closed by a cysteine the paralogues have and NR4A3 lacks'
    becomes true as a general statement -- and it is not true today.
    """
    who = _built()["residue_identity"]["who_closes_the_window"]
    ts = who["through_space"]["graded_cells_term_a_exemplar"]["by_closer"]
    co = who["corridor"]["graded_cells_term_a_exemplar"]["by_closer"]
    assert max(ts, key=ts.get) == "NR4A1 C505", "through-space majority closer moved"
    assert max(co, key=co.get) == "NR4A2 C534", "corridor majority closer moved"


def test_the_exposure_filter_is_not_load_bearing_at_the_12_atom_gate():
    """★ THE MOST USEFUL SEPARATION IN THE AUDIT.

    At the design gate the categorical result holds on REACH ALONE, so it does not inherit the demonstrated
    false negative of the RSA >= 0.25 criterion (instrument V17, which misses NR4A1 Cys551). At 16-20 atoms
    it does. A regeneration that lost this distinction would let the paper claim the gate result on an
    instrument it does not actually need -- and would let a reader dismiss the gate result along with the
    instrument.
    """
    rows = _built()["pose_dependency_split"]["exposure_criterion_dependent"]["how_much_load_it_carries"]
    at12 = [r for r in rows if r["linker_atoms"] == 12]
    at20 = [r for r in rows if r["linker_atoms"] == 20]
    assert at12 and at20
    assert max(r["percentage_points_carried_by_the_exposure_filter"] for r in at12) < 1.0, \
        "the exposure filter has become load-bearing at the gate -- the gate claim now inherits V17"
    assert min(r["percentage_points_carried_by_the_exposure_filter"] for r in at20) > 20.0, \
        "the 20-atom column no longer depends on the exposure filter -- re-read the artifact"


def test_C420_is_refuted_everywhere_and_C559_is_not():
    """Claim (b). `refuted_unique_cysteines` is built from best_corridor alone and so drops C559's
    through-space evidence; the audit must keep recording the number that contradicts the label."""
    ev = {c["claim"]: c for c in _built()["branch_1b_claim_verdicts"]}["b"]["evidence"]
    assert ev["C420"]["best_through_space"] == 0
    assert ev["C420"]["best_corridor"] == 0
    assert ev["C420"]["cells_with_any_reach"] == []
    assert ev["C559"]["best_corridor"] == 0
    assert ev["C559"]["best_through_space"] > 0, \
        "C559 is now refuted through-space too -- update claim (b), do not leave it CORRECTED"
    assert len(ev["C559"]["cells_with_any_reach"]) == 1


def test_the_noise_yardstick_cannot_cover_the_corridor_closer():
    """Claim (e). The bound is built from ALIGNED pairs, and C534 has no aligned NR4A3 partner by
    construction -- so the residue closing most corridor cells carries no measured bound."""
    ev = {c["claim"]: c for c in _built()["branch_1b_claim_verdicts"]}["e"]["evidence"]
    assert "NR4A2 C534" in ev["closers_with_NO_measured_noise_bound"]
    assert "NR4A2 C534" not in ev["pairs_covered"]
    assert ev["correction_needed_is_inside_the_observed_model_noise"] is False
    assert 0 < ev["margin_A"] < 1.0, "the noise margin is no longer thin -- re-read and re-word the limit"


def test_every_proposed_edit_names_the_document_and_the_problem():
    """A routed edit that does not say WHAT is wrong is unactionable by whoever applies it."""
    pe = _built()["proposed_edits"]
    for doc in CAA.LOCKED:
        assert doc in pe, "%s lost its proposed-edit block" % doc
        for e in pe[doc]:
            assert e["anchor"] and e["problem"] and e["proposed_text"]


def test_the_audit_does_not_edit_the_locked_documents():
    """This work ran in an isolated worktree while both files were being restructured elsewhere. The audit
    reports their edits; it must never contain them."""
    repo = os.path.abspath(os.path.join(MOD, "..", ".."))
    out = subprocess.run(["git", "-C", repo, "log", "--name-only", "--format=", "-1", "--",
                          "research/modalities/categorical-axis-audit.json"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    touched = {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}
    for doc in CAA.LOCKED:
        assert doc not in touched, "the audit's commit touched %s, which it must not" % doc


def test_the_licence_block_refuses_the_five_things_it_must_refuse():
    """Language discipline is the point of this section, so it is asserted rather than trusted."""
    txt = json.dumps(_built()["what_the_axis_licenses"]["⛔_what_it_does_NOT_license"]).lower()
    for must in ("degradation", "affinity", "efficacy", "safety", "ternary", "proteome"):
        assert must in txt, "the licence block stopped refusing %r" % must
