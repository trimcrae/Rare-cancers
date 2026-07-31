#!/usr/bin/env python3
"""The stage probe measures the PRODUCTION build path, and its boundary is the physical one.

Context: the inter-chain-distance gate this replaced was refuted by its own first run
(nrv04_cofold_audit.CLASH_MIN_INTERCHAIN_A). The lesson pinned here is that the replacement must not be a
re-implementation of the builder — a probe that rebuilds the stages itself can drift from the real pipeline
and then answer confidently about something nobody runs.
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import nrv04_pe_stage_probe as probe  # noqa: E402


def test_the_probe_hooks_the_real_builder_rather_than_reimplementing_it():
    import nrv04_covalent_md as md
    assert "stage_probe" in inspect.signature(md.build_system).parameters
    src = inspect.getsource(md.build_system)
    # The three stages the diagnosis turns on, in the production builder itself.
    for stage in ("protein_after_pdbfixer", "protein_plus_ligand", "solvated"):
        assert stage in src, f"{stage} is not probed in the real build path"
    assert "build_system(" in inspect.getsource(probe.probe_unit)


def test_the_probe_is_inert_for_a_real_leg():
    """Every production leg passes stage_probe=None, so this costs nothing and cannot change a result."""
    import nrv04_covalent_md as md
    assert inspect.signature(md.build_system).parameters["stage_probe"].default is None
    src = inspect.getsource(md.build_system)
    assert src.count("if stage_probe:") == 3, "each stage must be guarded, so None does no work"


def test_the_boundary_is_zero_and_agrees_with_the_quarantine():
    """Both use the physical boundary, not a tuned cut — a MINIMISED solvated system is always negative."""
    import nrv04_vast_launch as vl
    assert probe.NONPHYSICAL_PE_KJ == 0.0
    assert vl._NONPHYSICAL_PE_KJ == probe.NONPHYSICAL_PE_KJ, (
        "the quarantine and the probe must not disagree about what counts as non-physical")


#: The measured stage energies, 2026-07-31 4:20 PM ET. Held here so the classifier is exercised against the
#: real observation rather than invented numbers — an invariance claim about made-up data proves nothing.
_MEASURED_SUBJECT = {"system": "nr4a3", "seed": 3, "stages": [
    {"stage": "protein_after_pdbfixer", "n_atoms": 10914, "pe_kj_per_mol": 2.109005036357692e+15},
    {"stage": "protein_plus_ligand", "n_atoms": 11080, "pe_kj_per_mol": 2.109005036360151e+15},
    {"stage": "solvated", "n_atoms": 316243, "pe_kj_per_mol": 2.108844375741770e+15}]}
_MEASURED_CONTROL = {"system": "nr4a3", "seed": 1, "stages": [
    {"stage": "protein_after_pdbfixer", "n_atoms": 10914, "pe_kj_per_mol": 2.522674e+05},
    {"stage": "protein_plus_ligand", "n_atoms": 11080, "pe_kj_per_mol": 2.606874e+05},
    {"stage": "solvated", "n_atoms": 329820, "pe_kj_per_mol": -3.740431e+06}]}


def test_no_per_stage_physical_verdict_survives_anywhere():
    """⛔ THE ZERO BOUNDARY CALLED THE HEALTHY CONTROL BROKEN, and that must not come back.

    `PE <= 0` is meaningful only for a MINIMISED SOLVATED system. No probe stage is minimised and two are not
    solvated, so the control's perfectly ordinary +2.5e5 at `protein_after_pdbfixer` was reported as the
    stage where its energy 'first goes non-physical'. Same class of error as reporting `solvated` off two
    stages that had RAISED: a summary line that contradicted the table above it.
    """
    src = inspect.getsource(probe.probe_unit)
    assert '"physical"' not in src, "a probe stage records a MEASUREMENT, not a verdict"
    assert "NONPHYSICAL_PE_KJ" not in src, "the post-minimisation boundary must not be applied to a stage"
    assert not hasattr(probe, "first_nonphysical_stage")


def test_the_verdict_is_comparative_and_names_the_measured_stage():
    got = probe.compare_to_control(_MEASURED_SUBJECT, _MEASURED_CONTROL)
    assert got["first_divergent_stage"] == "protein_after_pdbfixer", (
        "the energy is already 1e15 before the ligand exists and before one water is placed")
    rows = {r["stage"]: r for r in got["stages"]}
    assert round(rows["protein_after_pdbfixer"]["decades_above_control"], 1) == 9.9
    # Ligand placement and solvation are EXONERATED: they do not introduce the divergence, they inherit it.
    assert rows["protein_plus_ligand"]["status"] == "DIVERGENT"
    assert rows["solvated"]["status"] == "DIVERGENT"
    assert rows["solvated"]["sign_flip"] is True, "control goes negative on solvation; the subject does not"
    # ★ THE READING THAT DECIDES THE LANE: the divergence is in the earliest thing built, so it is the INPUT.
    assert "property of the INPUT, not of the build" in got["verdict"], got["verdict"]


def test_the_verdict_is_invariant_across_the_threshold():
    """★★ WHAT MAKES THIS A SEPARATOR AND NOT THE RETIRED GEOMETRY CUT.

    The 1.5 A inter-chain gate was refuted because ground truth straddled it. Here the separation is ~10
    decades, so the answer does not move across four orders of magnitude of the threshold's own value. If a
    future observation ever makes the verdict threshold-sensitive, this fails and the measure needs the same
    scrutiny the geometry one got — rather than a quiet re-tune.
    """
    answers = {probe.compare_to_control(_MEASURED_SUBJECT, _MEASURED_CONTROL,
                                        decades=float(d))["first_divergent_stage"]
               for d in range(1, 9)}
    assert answers == {"protein_after_pdbfixer"}, answers
    assert 1.0 < probe.DIVERGENCE_DECADES < 9.0


#: The nr4a2 measurement, 5:16 PM ET (run 30665640363). Both breaker-blocked units' co-folds, against the
#: seed-1 control whose BOTH replicas landed complete production legs.
_NR4A2_S2 = {"system": "nr4a2", "seed": 2, "stages": [
    {"stage": "protein_after_pdbfixer", "n_atoms": 10911, "pe_kj_per_mol": 385775.29882575397},
    {"stage": "protein_plus_ligand", "n_atoms": 11077, "pe_kj_per_mol": 395188.7538965884},
    {"stage": "solvated", "n_atoms": 346135, "pe_kj_per_mol": -3847881.648498424}]}
_NR4A2_S1 = {"system": "nr4a2", "seed": 1, "stages": [
    {"stage": "protein_after_pdbfixer", "n_atoms": 10911, "pe_kj_per_mol": 881959.6142306231},
    {"stage": "protein_plus_ligand", "n_atoms": 11077, "pe_kj_per_mol": 2783972101.010649},
    {"stage": "solvated", "n_atoms": 345000, "pe_kj_per_mol": 2781196768.2754927}]}


def test_the_blocked_units_cofold_is_NOT_an_input_fault():
    """★★ THE ANSWER THAT KEEPS THE PANEL AT 16/18 RATHER THAN 14/18.

    nr4a2 m2 r0 and m3 r0 are breaker-blocked. If their co-folds were clashed like nr4a3/seed_3, they would
    be unrecoverable and the reachable ceiling would drop by two more units. They are not: seed 2 reaches a
    strongly NEGATIVE solvated energy, no stage diverges, and separately its sibling replica m2-r1 landed a
    complete production leg off the same co-fold (MD_REPLICAS are velocity seeds, not inputs).
    """
    got = probe.compare_to_control(_NR4A2_S2, _NR4A2_S1)
    assert got["first_divergent_stage"] is None
    assert probe.owner_of_the_fault(_NR4A2_S2, got)["owner"] == probe.OWNER_UNKNOWN
    # The seed-3 signature for contrast — 21 orders of magnitude apart at the solvated stage.
    assert probe.compare_to_control(_MEASURED_SUBJECT, _MEASURED_CONTROL)["first_divergent_stage"] is not None


def test_a_subject_BELOW_its_control_is_not_merely_consistent_with_it():
    """⚠ THE TEST IS ONE-SIDED. `d = log10|subj| - log10|ctrl|` can only flag a subject WORSE than its
    control, so nr4a2:2 (solvated -3.85e6, healthy) against nr4a2:1 (+2.78e9) printed "consistent with the
    control" at every stage — which reads as "as good as" when the subject is orders BETTER."""
    rows = {r["stage"]: r for r in probe.compare_to_control(_NR4A2_S2, _NR4A2_S1)["stages"]}
    assert "BELOW the control" in rows["protein_plus_ligand"]["status"], "-3.85 decades"
    assert rows["protein_after_pdbfixer"]["status"] == "consistent with the control", (
        "-0.36 decades is genuinely consistent; only an ORDERS-apart gap earns the stronger wording")
    # ★ The solvated row is only -2.86 decades — UNDER the threshold — but the subject is NEGATIVE and the
    # control POSITIVE. Sign is the qualitative fact at this stage and must not be buried by the magnitude
    # test failing to clear its own bar.
    assert "NEGATIVE solvated energy" in rows["solvated"]["status"]
    assert "runnable signature" in rows["solvated"]["status"]
    assert abs(rows["solvated"]["decades_above_control"]) < 3.0, (
        "this is precisely the case the decade test does NOT catch, which is why sign is checked separately")


def test_the_sign_rule_is_scoped_to_the_solvated_stage_only():
    """An unsolvated stage has no such expectation — a normal unminimised protein is positive, and treating a
    negative one there as a health signal would be inventing physics the calibration does not support."""
    subj = {"system": "x", "seed": 1, "stages": [
        {"stage": "protein_after_pdbfixer", "pe_kj_per_mol": -1.0e5}]}
    ctl = {"system": "x", "seed": 2, "stages": [
        {"stage": "protein_after_pdbfixer", "pe_kj_per_mol": 2.0e5}]}
    got = probe.compare_to_control(subj, ctl)
    assert got["stages"][0]["status"] == "consistent with the control"


def test_a_sick_control_cannot_silently_launder_a_sick_subject():
    """⛔ THE DANGEROUS DIRECTION. Two inputs BOTH at 1e15 would print "consistent" at every stage and return
    OWNER_UNDETERMINED — a clean bill of health for two broken structures. The guard must be ABSOLUTE."""
    got = probe.compare_to_control(_NR4A2_S2, _NR4A2_S1)
    assert got["control_solvated_kj"] > 0
    assert "not a pristine yardstick" in got["control_caveat"]
    assert "RELATIVE to it" in got["control_caveat"]
    # ...and a genuinely clean control raises no caveat.
    assert probe.compare_to_control(_MEASURED_SUBJECT, _MEASURED_CONTROL)["control_caveat"] is None


def test_the_caveat_does_not_invent_a_cut_the_data_cannot_support():
    """A positive pre-min solvated energy is NOT disqualifying: nr4a2 seed 1 read +2.78e9 and BOTH its
    replicas landed. The caveat must inform, never gate — inventing a threshold between 2.8e9 and 2.1e15 is
    exactly the retired inter-chain gate's mistake."""
    got = probe.compare_to_control(_NR4A2_S2, _NR4A2_S1)
    assert got["first_divergent_stage"] is None, "the caveat must not turn into a verdict"
    assert "both of its replicas landed" in got["control_caveat"]


def test_a_stage_missing_from_either_side_is_unknown_not_a_verdict():
    """CLAUDE.md §4b — an absent reading is not a reading of absence, in the classifier too."""
    subj = {"system": "x", "seed": 1, "stages": [
        {"stage": "protein_after_pdbfixer", "pe_kj_per_mol": None, "error": "boom"},
        {"stage": "solvated", "pe_kj_per_mol": 1e15}]}
    ctl = {"system": "x", "seed": 2, "stages": [{"stage": "solvated", "pe_kj_per_mol": -4e6}]}
    got = probe.compare_to_control(subj, ctl)
    rows = {r["stage"]: r for r in got["stages"]}
    assert rows["protein_after_pdbfixer"]["decades_above_control"] is None
    assert rows["protein_after_pdbfixer"]["status"].startswith("unknown")
    # An unreadable EARLIER stage must not let a later one claim to be where divergence STARTED.
    assert got["first_divergent_stage"] == "solvated"
    assert "an EARLIER origin is not excluded" in got["verdict"], got["verdict"]
    assert "every stage BEFORE it is consistent" not in got["verdict"]
    assert probe.compare_to_control({"stages": []}, ctl)["verdict"].startswith("NO COMPARISON POSSIBLE")


def test_the_default_units_pair_the_failing_input_with_a_working_control():
    """A probe run on the broken input alone cannot say which stage is ABNORMAL."""
    import argparse
    ap = argparse.ArgumentParser()
    src = inspect.getsource(probe.main)
    assert "nr4a3:3,nr4a3:1" in src, "the failing seed and its working sibling must both be the default"
    del ap, argparse


def test_a_stage_that_cannot_be_priced_records_no_energy_and_says_why():
    src = inspect.getsource(probe.probe_unit)
    assert '"pe_kj_per_mol": None' in src, "an unreadable stage must never carry a fabricated energy"
    assert '"error":' in src, "and it must say what stopped it"


def test_pre_solvation_stages_are_priced_without_a_cutoff():
    """The probe's own first run measured NOTHING before solvation, and that is not a result.

    `sysgen.create_system` applies the production PME + 0.9 nm cutoff, which needs a periodic box at least
    twice the cutoff. An unsolvated topology has none, so both pre-solvation stages raised
    "cutoff distance cannot be greater than half the periodic box size" for the FAILING unit and the CONTROL
    alike — making `first_nonphysical_stage=solvated` an artifact of unmeasurability, not evidence about
    solvation. CLAUDE.md §4b: an absent reading is not a reading of absence.
    """
    src = inspect.getsource(probe.single_point_kj)
    assert "NoCutoff" in src
    assert 'periodic=(name == "solvated")' in inspect.getsource(probe.probe_unit), (
        "only the solvated stage may be priced periodically")


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# LOCALISATION — the stage has TWO OWNERS, and choosing between them is the point.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
_CMP = {"first_divergent_stage": "protein_after_pdbfixer"}


def _loc(forces, contacts):
    return {"localised": {"protein_after_pdbfixer": {"energy_by_force_kj": forces,
                                                     "worst_contacts": contacts}}}


def test_two_cofold_heavy_atoms_in_contact_is_trimcraes_decision():
    got = probe.owner_of_the_fault(
        _loc({"NonbondedForce[3]": 2.1e15, "HarmonicBondForce[0]": 1.0e4},
             [{"distance_a": 0.02, "atom_1": "A:LEU10:CB", "atom_2": "B:VAL9:CG1",
               "both_from_cofold": True, "under_clash_cutoff": True}]), _CMP)
    assert got["owner"] == probe.OWNER_INPUT
    assert "preregistration" in got["action"]


def test_a_contact_involving_an_atom_OUR_PREP_ADDED_is_mine_to_fix():
    """The predicted structure is not exonerated, but a code fix must be tried before a re-seed decision."""
    got = probe.owner_of_the_fault(
        _loc({"NonbondedForce[3]": 2.1e15},
             [{"distance_a": 0.02, "atom_1": "A:LEU10:HB2", "atom_2": "B:VAL9:CG1",
               "both_from_cofold": False, "under_clash_cutoff": True}]), _CMP)
    assert got["owner"] == probe.OWNER_CODE


def test_a_BONDED_term_carrying_the_energy_is_connectivity_and_a_reseed_would_not_help():
    got = probe.owner_of_the_fault(
        _loc({"HarmonicBondForce[0]": 2.1e15, "NonbondedForce[3]": 1.0e4},
             [{"distance_a": 0.02, "atom_1": "A:LEU10:CB", "atom_2": "B:VAL9:CG1",
               "both_from_cofold": True, "under_clash_cutoff": True}]), _CMP)
    assert got["owner"] == probe.OWNER_CODE
    assert "connectivity" in got["why"]


def test_an_unlocalised_divergence_never_assigns_an_owner():
    """⛔ THE FAILURE THIS GUARDS. `protein_after_pdbfixer` is the output of Boltz AND of our repair; naming
    it without the force/atom evidence would be a coin-flip wearing a diagnosis."""
    got = probe.owner_of_the_fault({"localised": None}, _CMP)
    assert got["owner"] == probe.OWNER_UNKNOWN
    assert probe.owner_of_the_fault({}, {"first_divergent_stage": None})["owner"] == probe.OWNER_UNKNOWN


def test_the_localiser_is_on_by_default():
    """Stopping one measurement short of the discriminator is the habit CLAUDE.md §2 exists to break."""
    src = inspect.getsource(probe.main)
    assert '"--no-localise"' in src and "default=True" in src
    assert inspect.signature(probe.probe_unit).parameters["localise"].default is False, (
        "the library default stays off — main() opts in, so an unrelated caller pays nothing")


# ── the contact finder, exercised without openmm (numpy + duck-typed topology) ─────────────────────────────
class _FakeElem:
    def __init__(self, symbol):
        self.symbol = symbol


class _FakeAtom:
    def __init__(self, index, name, resname, resid, chain, symbol):
        self.index, self.name = index, name
        self.element = _FakeElem(symbol) if symbol else None
        self.residue = type("R", (), {"name": resname, "id": resid,
                                      "chain": type("C", (), {"id": chain})()})()


class _FakeTop:
    def __init__(self, atoms, bonds):
        self._a, self._b = atoms, bonds

    def atoms(self):
        return list(self._a)

    def bonds(self):
        return [(self._a[i], self._a[j]) for i, j in self._b]


class _FakePos:
    def __init__(self, arr):
        self.arr = arr

    def value_in_unit(self, _u):
        return self.arr


def _stub_openmm(monkeypatch):
    import types
    monkeypatch.setitem(sys.modules, "openmm",
                        types.SimpleNamespace(unit=types.SimpleNamespace(angstrom="A")))


def test_close_contacts_finds_the_clash_excludes_bonded_and_names_who_placed_it(monkeypatch):
    import numpy as np
    _stub_openmm(monkeypatch)
    atoms = [_FakeAtom(0, "CB", "LEU", "10", "A", "C"),     # co-fold heavy atom
             _FakeAtom(1, "CG1", "VAL", "9", "B", "C"),     # co-fold heavy atom, 0.4 A away -> the clash
             _FakeAtom(2, "CA", "LEU", "10", "A", "C"),     # bonded 1-2 to CB and CLOSE — must be excluded
             _FakeAtom(3, "HB2", "LEU", "10", "A", "H")]    # a PDBFixer hydrogen, 0.5 A from atom 1
    pos = _FakePos(np.array([[0.0, 0, 0], [0.4, 0, 0], [0.1, 0, 0], [0.9, 0, 0]]))
    top = _FakeTop(atoms, [(0, 2)])
    keys = {("A", "10", "CB"), ("B", "9", "CG1"), ("A", "10", "CA")}
    hits, n = close_or_skip(top, pos, keys)
    pairs = {(h["atom_1"], h["atom_2"]) for h in hits}
    assert ("A:LEU10:CB", "B:VAL9:CG1") in pairs, "the real clash must be found"
    assert not any("LEU10:CA" in a and "LEU10:CB" in b for a, b in pairs), "a 1-2 bonded pair is not a clash"
    worst = [h for h in hits if h["atom_2"] == "B:VAL9:CG1" and h["atom_1"] == "A:LEU10:CB"][0]
    assert worst["both_from_cofold"] is True
    # ⛔ THE REGRESSION THIS PINS. The first implementation derived `both_from_cofold` by testing whether the
    # PROSE contained "co-fold" — and the hydrogen's prose reads "...the co-fold is heavy-atoms-only", so
    # every PDBFixer hydrogen was attributed to Boltz. That boolean is what `owner_of_the_fault` uses to
    # choose between a code fix and a preregistration decision for trimcrae.
    h_pair = [h for h in hits if "HB2" in h["atom_1"] or "HB2" in h["atom_2"]]
    assert h_pair and h_pair[0]["both_from_cofold"] is False, "a hydrogen is ours — the co-fold has none"
    assert "prep" in (h_pair[0]["source_1"], h_pair[0]["source_2"])
    assert "PDBFixer" in (h_pair[0]["placed_by_1"] + h_pair[0]["placed_by_2"])
    assert n >= len(hits)


def test_with_no_raw_cofold_nothing_may_be_attributed_to_boltz(monkeypatch):
    """UNKNOWN is not co-fold. Attributing to Boltz is the attribution that ends in trimcrae's inbox."""
    import numpy as np
    _stub_openmm(monkeypatch)
    atoms = [_FakeAtom(0, "CB", "LEU", "10", "A", "C"), _FakeAtom(1, "CG1", "VAL", "9", "B", "C")]
    pos = _FakePos(np.array([[0.0, 0, 0], [0.3, 0, 0]]))
    hits, _ = probe.close_contacts(_FakeTop(atoms, []), pos, cofold_keys=None, cutoff_a=1.0)
    assert hits[0]["both_from_cofold"] is False
    assert hits[0]["source_1"] == "unknown"
    # ...and an unknown-provenance contact must not be sold as a preregistration decision.
    got = probe.owner_of_the_fault(_loc({"NonbondedForce[3]": 2.1e15}, hits), _CMP)
    assert got["owner"] != probe.OWNER_INPUT


def test_a_heavy_atom_absent_from_the_raw_cofold_is_attributed_to_our_prep(monkeypatch):
    import numpy as np
    _stub_openmm(monkeypatch)
    atoms = [_FakeAtom(0, "CB", "LEU", "10", "A", "C"), _FakeAtom(1, "OXT", "VAL", "9", "B", "O")]
    pos = _FakePos(np.array([[0.0, 0, 0], [0.3, 0, 0]]))
    hits, _ = close_or_skip(_FakeTop(atoms, []), pos, {("A", "10", "CB")})   # OXT is NOT in the co-fold
    assert hits[0]["both_from_cofold"] is False
    assert "heavy atom added by PDBFixer" in hits[0]["placed_by_2"]


def test_cofold_atom_keys_reads_the_raw_heavy_atom_record(tmp_path):
    p = tmp_path / "complex.pdb"
    p.write_text("ATOM      1  CB  LEU A  10      11.000  2.000  3.000  1.00  0.00           C\n"
                 "HETATM    2  C1  LIG B   1       1.000  2.000  3.000  1.00  0.00           C\n"
                 "TER\n")
    keys = probe.cofold_atom_keys(str(p))
    assert ("A", "10", "CB") in keys and ("B", "1", "C1") in keys


def close_or_skip(top, pos, keys):
    return probe.close_contacts(top, pos, cofold_keys=keys, cutoff_a=1.0)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
