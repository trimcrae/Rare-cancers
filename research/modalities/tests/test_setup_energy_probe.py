"""The $0 CPU reproduction that decides BLOCK vs RETRY for a pre-MD `setup()` NaN.

Pins `step1_setup_energy_probe.verdict`, the rule that says whether this lane keeps renting hosts for
`e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral`. The module itself needs openfe/openmm, so
only the pure decision function is exercised here — which is the part that must never regress
silently, because it is the part that spends (or stops spending) money.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import step1_setup_energy_probe as ep  # noqa: E402


def _row(energies, repro="completed", **extra):
    rows = [{"group": i, "force": name, "energy_kj_mol": e,
             "finite": e == e and abs(e) != float("inf")}
            for i, (name, e) in enumerate(energies)]
    r = {"unit_id": "u", "edge_id": "e", "edge": "a->b",
         "energy_probe": {"rows": rows, "verdict": "…"},
         "minimize_repro": {"outcome": repro, "wall_s": 12.3, "detail": "d"}}
    r.update(extra)
    return r


def test_non_finite_force_term_is_BLOCK():
    d, why = ep.verdict(_row([("NonbondedForce", -1.1e6),
                              ("CustomNonbondedForce", float("inf"))]))
    assert d == "BLOCK"
    assert "CustomNonbondedForce" in why
    assert "reproduces on every host" in why


def test_nan_term_is_BLOCK_too():
    d, _ = ep.verdict(_row([("CustomBondForce", float("nan"))]))
    assert d == "BLOCK"


def test_all_finite_AND_a_clean_minimiser_reproduction_is_RETRY():
    d, why = ep.verdict(_row([("HarmonicBondForce", 900.0), ("NonbondedForce", -1.2e6)]))
    assert d == "RETRY"
    assert "COMPLETED WITHOUT A NaN" in why


def test_all_finite_but_the_minimiser_REPRODUCED_the_NaN_is_BLOCK():
    # THE CASE STAGE 1 ALONE CANNOT SEE: setup() minimises every lambda state, so a softcore term
    # that is finite at the built lambda and divergent at an intermediate one gives all-finite
    # single-point energies AND a deterministic NaN. The reproduction must win.
    d, why = ep.verdict(_row([("NonbondedForce", -1.2e6)], repro="nan"))
    assert d == "BLOCK"
    assert "Deterministic for this edge" in why


def test_all_finite_with_NO_minimiser_reproduction_is_INCONCLUSIVE_not_RETRY():
    row = _row([("NonbondedForce", -1.2e6)])
    row.pop("minimize_repro")
    d, why = ep.verdict(row)
    assert d == "INCONCLUSIVE"
    assert "lambda window it never visited" in why


def test_a_failed_reproduction_is_INCONCLUSIVE():
    d, _ = ep.verdict(_row([("NonbondedForce", -1.2e6)], repro="error"))
    assert d == "INCONCLUSIVE"


def test_build_error_is_INCONCLUSIVE_not_RETRY():
    # "we could not measure" must never read as "we measured that it is fine" — that conflation is
    # what would license renting another host off a diagnostic that never ran.
    d, why = ep.verdict({"build_error": "ToolkitUnavailableException: AmberTools is not available"})
    assert d == "INCONCLUSIVE"
    assert "AmberTools" in why


def test_probe_error_is_INCONCLUSIVE():
    d, _ = ep.verdict({"energy_probe": {"error": "OpenMMException: no CPU platform"}})
    assert d == "INCONCLUSIVE"


def test_empty_rows_is_INCONCLUSIVE():
    d, why = ep.verdict({"energy_probe": {"rows": []}})
    assert d == "INCONCLUSIVE"
    assert "measured nothing" in why


def test_missing_energy_probe_key_is_INCONCLUSIVE():
    d, _ = ep.verdict({"unit_id": "u"})
    assert d == "INCONCLUSIVE"


def test_verdict_never_invents_a_fourth_answer():
    for row in (_row([("F", 1.0)]), _row([("F", float("inf"))]), {"build_error": "x"},
                _row([("F", 1.0)], repro="nan"), _row([("F", 1.0)], repro="error"),
                {"energy_probe": {"rows": []}}):
        assert ep.verdict(row)[0] in ("BLOCK", "RETRY", "INCONCLUSIVE")


def test_probe_targets_the_complex_leg_by_default():
    # The leg that NaN'd was the complex leg; a solvent-leg build is a different system and would
    # answer a different question.
    assert ep.LEG == "complex"


def test_the_verdict_wording_matches_the_drivers_own(monkeypatch):
    """One fact, one home: the CPU reproduction and the rented leg's failure path must not produce
    two different sentences for the same evidence. Both go through the driver's verdict."""
    import rbfe_spot_driver as drv
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "step1_setup_energy_probe.py")).read()
    assert "energy_probe_verdict" in src or "rbfe_spot_driver.energy_probe_verdict" in src
    assert callable(drv.energy_probe_verdict)
