"""Unit tests for ternary_fep_stage.py — the PURE input-staging planner (no gemmi/co-fold/network).

Verifies the exact input contract each pilot leg needs: which environment legs require a complex.pdb, which
protein chain roles it must contain (E3 machinery always; target only in ternary; binary DROPS the target),
the two ligand endpoints, and that all three env legs of a morph derive from one co-fold. The heavy
stage_from_cofold() assembler is SHAKEOUT-PENDING (gemmi/CI) and not exercised here."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_fep_stage as stg     # noqa: E402
import nr4a3_ternary_fep as eng      # noqa: E402


def test_solvent_leg_needs_no_protein():
    r = stg.required_inputs_for_leg("nrv04_active_to_epimer__solvent")
    assert r["environment"] == "solvent"
    assert r["needs_complex_pdb"] is False and r["chain_roles"] == []


def test_binary_leg_has_e3_only_no_target():
    r = stg.required_inputs_for_leg("nrv04_active_to_epimer__binary_vhl")
    assert r["needs_complex_pdb"] is True
    assert r["chain_roles"] == ["VHL", "ElonginB", "ElonginC"]      # target DROPPED
    assert stg.target_role("nrv04_active_to_epimer__binary_vhl") is None


def test_ternary_leg_adds_the_target_chain():
    r = stg.required_inputs_for_leg("nrv04_active_to_epimer__ternary_nr4a1")
    assert r["chain_roles"] == ["VHL", "ElonginB", "ElonginC", "NR4A1"]
    assert stg.target_role("nrv04_active_to_epimer__ternary_nr4a1") == "NR4A1"


def test_calib_ternary_target_is_smarca2():
    assert stg.target_role("calib_hi_to_lo__ternary_vhl") == "SMARCA2"
    r = stg.required_inputs_for_leg("calib_hi_to_lo__ternary_vhl")
    assert r["chain_roles"][-1] == "SMARCA2"


def test_endpoints_carried_for_every_leg():
    for lid in eng.expand_pilot_legs():
        r = stg.required_inputs_for_leg(lid)
        assert len(r["ligand_endpoints"]) == 2 and all(r["ligand_endpoints"])


def test_manifest_covers_all_legs_and_two_cofold_morphs():
    m = stg.staging_manifest()
    assert {l["leg_id"] for l in m["legs"]} == set(eng.expand_pilot_legs())
    # one ternary co-fold per morph feeds all three of its environment legs → exactly 2 source co-folds
    assert set(m["source_cofold_morphs"]) == {"calib_hi_to_lo", "nrv04_active_to_epimer"}


def test_three_env_legs_share_one_source_cofold():
    m = {l["leg_id"]: l for l in stg.staging_manifest()["legs"]}
    for morph in ("nrv04_active_to_epimer", "calib_hi_to_lo"):
        srcs = {m[lid]["source_cofold_morph"] for lid in m if lid.startswith(morph)}
        assert srcs == {morph}          # binary, ternary, solvent all derive from the same co-fold
