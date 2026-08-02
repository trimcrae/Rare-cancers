"""The SECOND instrument on the selcal co-fold finding — and the rules that make it worth having.

`selcal_cofold_validate` measured all 12 co-folds at 17.8-21.2 Å from the deposited ternaries with fnat 0.000.
It also had THREE defects before they were caught, each of which returned a plausible number rather than an
error: the ligand counted as an interface residue, a chimeric multi-copy reference, and contact-grouping
merging a lattice. Three silent defects is the argument for not trusting its fourth answer either.

So these tests pin what makes a cross-check real rather than decorative:
  1. it is a SEPARATE implementation — no shared parser, chain mapper, interface selector or superposition;
  2. only `fnat` is compared as a NUMBER, because only `fnat` is the same quantity in both;
  3. a DockQ that could not run reports a failure, never a zero;
  4. a DISAGREEMENT is reported as one and blocks citation — it is not averaged away.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import selcal_dockq_crosscheck as X  # noqa: E402
import selcal_cofold_validate as V  # noqa: E402
import test_selcal_cofold_validate as T  # noqa: E402

_dockq = pytest.mark.skipif(X.dockq_version().startswith("UNAVAILABLE"),
                            reason="the DockQ CLI is not installed on this runner")


# ---------- 1 · it really is a separate implementation ----------------------------------------------------


def test_the_crosscheck_shares_no_measurement_code_with_the_first_instrument():
    """A 'cross-check' that reuses the thing it checks is decorative. It may import the first instrument's
    ARTIFACT (to know which co-folds to score and which copy to pin), and nothing else."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "selcal_dockq_crosscheck.py")).read()
    assert "import selcal_cofold_validate" not in src
    assert "from selcal_cofold_validate" not in src
    for shared in ("_aligned_iface_rmsd", "interface_atom_indices", "nw_align", "parse_mmcif", "map_chains"):
        assert shared not in src, "the second instrument reuses %s from the first" % shared


def test_the_implementation_under_test_is_recorded_not_assumed():
    v = X.dockq_version()
    assert v and isinstance(v, str)


# ---------- 2 · only fnat is compared as a number ---------------------------------------------------------


def test_only_fnat_is_compared_numerically_and_the_rmsds_are_flagged_as_different_quantities():
    """The first instrument superposes on the WHOLE E3 Cα set (matching E1 on purpose); DockQ's iRMSD
    superposes on interface residues alone. Same name, different quantity. Subtracting them would be the
    one-fact-one-place bug in geometric form."""
    first = {"interface_rmsd_to_crystal_A": 19.7, "fnat": {"fnat": 0.0}}
    best = {"DockQ": 0.01, "fnat": 0.0, "iRMS": 11.2}
    c = X.compare(first, best)
    assert c["agree"] is True
    assert "fnat_abs_difference" in c
    assert "rmsds_are_NOT_directly_comparable" in c
    assert "iRMS_dockq_A" in c and "interface_rmsd_first_instrument_A" in c
    # the difference of the two RMSDs is never computed
    assert not any("rmsd" in k.lower() and "difference" in k.lower() for k in c)


def test_a_real_fnat_disagreement_is_reported_and_blocks_citation():
    first = {"interface_rmsd_to_crystal_A": 19.7, "fnat": {"fnat": 0.0}}
    best = {"DockQ": 0.62, "fnat": 0.71, "iRMS": 1.4}
    c = X.compare(first, best)
    assert c["agree"] is False
    assert "DISAGREES" in c["why"]
    assert "must not be cited" in c["why"]


def test_disagreement_is_never_averaged_into_a_range():
    doc = {"n_compared": 12, "n_agree": 9, "n_disagree": 3, "n_dockq_failed": 0, "records": []}
    v = X._overall(doc)
    assert v["instruments_agree"] is False
    assert "not a range to average" in v["sentence"]


# ---------- 3 · a failure is a failure, never a zero ------------------------------------------------------


def test_a_dockq_that_could_not_run_is_not_a_dockq_that_measured_zero(tmp_path):
    doc, err = X.run_dockq(str(tmp_path / "absent.cif"), str(tmp_path / "also_absent.cif"))
    assert doc is None and "not found" in err


def test_no_comparison_is_manufactured_when_dockq_produced_nothing():
    c = X.compare({"interface_rmsd_to_crystal_A": 19.7, "fnat": {"fnat": 0.0}}, None)
    assert c["agree"] is None
    assert "did not run is not an instrument that disagreed" in c["why"]


def test_overall_verdict_refuses_when_nothing_was_scored():
    v = X._overall({"n_compared": 0, "n_agree": 0, "n_disagree": 0, "n_dockq_failed": 12, "records": []})
    assert v["instruments_agree"] is None
    assert "did not run is not an instrument that agreed" in v["sentence"]


# ---------- 4 · the mapping pins the same copy in both instruments ----------------------------------------


def test_mapping_is_taken_from_the_first_instruments_derived_chain_map():
    """9DTY holds ~10 copies. Letting DockQ align freely would let it score a DIFFERENT copy, and a
    disagreement would then be ambiguous between 'the measurement differs' and 'they scored different
    copies' — a question not worth manufacturing."""
    rec = {"chain_map": {"matched": {"A": {"native_chain": "M"}, "E": {"native_chain": "R"},
                                     "F": {"native_chain": "S"}, "G": {"native_chain": "T"}}}}
    mapping, err = X.mapping_from_first_instrument(rec)
    assert err is None
    assert mapping == "AEFG:MRST"


def test_mapping_refuses_on_a_multi_character_chain_id():
    rec = {"chain_map": {"matched": {"A": {"native_chain": "AA"}}}}
    mapping, err = X.mapping_from_first_instrument(rec)
    assert mapping is None and "single character" in err


def test_mapping_refuses_when_the_first_instrument_recorded_none():
    mapping, err = X.mapping_from_first_instrument({})
    assert mapping is None and "no chain map" in err


# ---------- 5 · end-to-end against known displacements ----------------------------------------------------


@_dockq
@pytest.mark.parametrize("dx,expect_class", [(0.0, "High"), (3.0, "Medium"), (20.0, "Incorrect"),
                                             (60.0, "Incorrect")])
def test_both_instruments_agree_across_known_displacements(tmp_path, dx, expect_class):
    """The check that makes the cross-check meaningful: on inputs whose answer we KNOW, do the two
    independent implementations agree on the quantity that is genuinely shared?"""
    pytest.importorskip("numpy")
    native = T._write_cif(T._complex(), str(tmp_path / "n.cif"))
    model = T._write_cif(T._complex(target_dx=dx), str(tmp_path / "m.cif"))
    mine = V.validate_one(model, native)
    doc, err = X.run_dockq(model, native, mapping="AEFG:AEFG")
    assert err is None, err
    best, ierr = X.target_e3_interface(doc, "A", "E")     # target chain A vs VHL chain E, BY ROLE
    assert ierr is None, ierr
    assert X.quality_class(best["DockQ"]) == expect_class
    c = X.compare(mine, best)
    assert c["agree"] is True, c
    assert abs(mine["fnat"]["fnat"] - best["fnat"]) <= X.FNAT_AGREEMENT_TOL


@_dockq
def test_dockq_key_spelling_change_degrades_to_missing_not_to_zero():
    """DockQ 2.x spells them `iRMSD`/`LRMSD`; the first draft of this module read `iRMS` and silently got
    None, which a formatter then rendered as a number. Both spellings are accepted, and an unknown one
    yields None rather than 0.0."""
    mk = lambda v: {"best_result": {"AE": dict(v, chain1="A", chain2="E")}}   # noqa: E731
    assert X.target_e3_interface(mk({"DockQ": 0.5, "fnat": 0.4, "iRMSD": 3.3}), "A", "E")[0]["iRMS"] == 3.3
    assert X.target_e3_interface(mk({"DockQ": 0.5, "fnat": 0.4, "iRMS": 3.3}), "A", "E")[0]["iRMS"] == 3.3
    assert X.target_e3_interface(mk({"DockQ": 0.5, "fnat": 0.4}), "A", "E")[0]["iRMS"] is None


def test_the_interface_is_selected_BY_ROLE_never_by_score():
    """⛔ THE DEFECT THAT MADE THIS CROSS-CHECK REPORT THE WRONG ANSWER, pinned so it cannot return.

    The first version took the highest-scoring interface. On the real run that was `TS` (SMARCA2 arm) and
    `AB` (SMARCA4 arm) — native chains mapping from model F and G, i.e. **Elongin B <-> Elongin C**, the
    internal VCB heterodimer every co-fold reproduces. It scored 0.95-0.97, and the cross-check declared the
    first instrument overturned on the strength of an interface that was never in question."""
    doc = {"best_result": {
        "MR": {"DockQ": 0.02, "fnat": 0.0, "iRMSD": 12.0, "chain1": "M", "chain2": "R"},   # target <-> VHL
        "TS": {"DockQ": 0.96, "fnat": 0.97, "iRMSD": 0.5, "chain1": "T", "chain2": "S"},   # EloB <-> EloC
    }}
    picked, err = X.target_e3_interface(doc, "M", "R")
    assert err is None
    assert picked["interface"] == "MR", "the interface must be chosen by ROLE, not by score"
    assert picked["DockQ"] == 0.02
    assert X._legacy_best_interface(doc)["interface"] == "TS"      # the defect, reproduced
    assert [c["interface"] for c in X.other_interfaces(doc, "M", "R")] == ["TS"]


def test_an_unscored_target_interface_refuses_rather_than_falling_back():
    """An interface DockQ did not score is not an interface that scored well."""
    doc = {"best_result": {"TS": {"DockQ": 0.96, "fnat": 0.97, "iRMSD": 0.5, "chain1": "T", "chain2": "S"}}}
    picked, err = X.target_e3_interface(doc, "M", "R")
    assert picked is None
    assert "NOT the target" in err


# ---------- 6 · scope -------------------------------------------------------------------------------------


def test_the_artifact_does_not_overwrite_the_first_instruments_record():
    assert os.path.basename(X.OUT_JSON) != os.path.basename(X.FIRST_INSTRUMENT_JSON)
    assert X.OUT_JSON.endswith("selcal-cofold-dockq.json")


def test_the_module_licenses_nothing(tmp_path):
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "selcal_dockq_crosscheck.py")).read()
    assert "re-scores no leg" in src
    assert "selcal-verdict.json remains" in src
