"""THE `$/ns` IS A REFERENCE-GPU **INDEX**, AND EVERY GATE DECISION IS INVARIANT TO SYSTEM SIZE.

★★ THE ALARM THIS ANSWERS (2026-07-31). `vast_cost_model.MEASURED_NS_PER_DAY_84K` is annotated "THIS IS THE
ONLY THROUGHPUT TABLE", and `vast_bench_sweep` records what it benches: *"TIP3P/PME 84,534 particles, 4 fs
HMR, 3 timed blocks"* — plain, single-replica MD on a pure WATER BOX. Every 5a-KS board row is priced through
it (`RTX 3090 $0.00554/ns · 1.62x basis`), and 5a-KS is a 147,788-particle ternary assembly run as a 12-window
HREX RBFE. The worry was that the buy gate had been clearing purchases all day on a throughput figure
belonging to a different assembly, and that rows reading 1.21-1.62x might really be over the 1.9166x line.

★ THE ANSWER IS NO, AND IT IS ARITHMETIC RATHER THAN LUCK. `REFERENCE_NS_PER_H` appears in the NUMERATOR of
`rung_ns_per_unit` (`ref_gpu_h * REFERENCE_NS_PER_H`) and in the DENOMINATOR of `basis_usd_per_ns`
(`plan_$/ref-GPU-h / REFERENCE_NS_PER_H`), so it cancels out of BOTH gate tests. These tests re-derive the
whole chain under a uniform slowdown and assert the decisions do not move.

⚠ WHAT THEY DELIBERATELY DO NOT CLAIM: that the index is a physical `$/ns` for any lane (it is not — see
`ns_per_hour`), or that card-to-card RATIOS transfer from the water box to a real assembly. The cancellation
is exact only for a UNIFORM factor, and non-uniformity is untested — one production point per card, no two
cards sharing a leg. That assumption is stated in `vast_cost_model`, not hidden here.
"""
import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vast_cost_model as vcm  # noqa: E402


@pytest.fixture
def scaled(monkeypatch):
    """Re-derive the whole chain with the table scaled by `k` — i.e. 'the real system is k times slower on
    every card'. Restores the table afterwards, because it is module state every other test reads."""
    orig = dict(vcm.MEASURED_NS_PER_DAY_84K)
    orig_ref = vcm.REFERENCE_NS_PER_H

    def _apply(k):
        for c in orig:
            vcm.MEASURED_NS_PER_DAY_84K[c] = orig[c] / k
        vcm.REFERENCE_NS_PER_H = vcm.MEASURED_NS_PER_DAY_84K[vcm.REFERENCE_CARD] / 24.0
        import congeneric_fanout as cf
        importlib.reload(cf)
        cf._vcm = vcm
        basis = cf.basis_usd_per_ns()
        nsh = vcm.ns_per_hour("RTX 3090")
        pn = vcm.usd_per_ns(0.0963, 0.0196, nsh)          # a real board row's rate
        ns_unit = (7.0 / 3.0) * vcm.REFERENCE_NS_PER_H     # rung_ns_per_unit's shape
        return {"ratio_vs_basis": pn / basis, "projected_usd": pn * ns_unit}

    yield _apply
    for c in orig:
        vcm.MEASURED_NS_PER_DAY_84K[c] = orig[c]
    vcm.REFERENCE_NS_PER_H = orig_ref
    import congeneric_fanout as cf
    importlib.reload(cf)
    cf._vcm = vcm


@pytest.mark.parametrize("k", [1.748, 3.37, 10.0, 0.5])
def test_both_gate_tests_are_invariant_to_a_uniform_system_size_change(scaled, k):
    """1.748 is the REAL ratio (147,788 / 84,534); 3.37 was the figure alarmed about; 10 and 0.5 are there to
    show the invariance is structural rather than a coincidence at one value."""
    base = scaled(1.0)
    got = scaled(k)
    assert abs(got["ratio_vs_basis"] - base["ratio_vs_basis"]) < 1e-9, (
        "the RATE ceiling moved with system size — REFERENCE_NS_PER_H stopped cancelling")
    assert abs(got["projected_usd"] - base["projected_usd"]) < 1e-9, (
        "the DOLLAR ceiling moved with system size — REFERENCE_NS_PER_H stopped cancelling")


def test_the_cancellation_is_named_where_someone_would_look_to_break_it():
    """The invariance is load-bearing and non-obvious. If a future edit makes `rung_ns_per_unit` use a leg's
    REAL nanosecond target while `basis_usd_per_ns` stays in reference units, the dollar ceiling silently
    becomes wrong by the system-size factor — and nothing else in the repo would notice."""
    import inspect

    import ternary_vast_launch as tv
    assert "REFERENCE_NS_PER_H" in inspect.getsource(tv.rung_ns_per_unit)
    import congeneric_fanout as cf
    assert "REFERENCE_NS_PER_H" in inspect.getsource(cf.basis_usd_per_ns)


def test_the_bench_provenance_has_one_home_and_says_water_box():
    assert vcm.BENCH_PARTICLES == 84534
    assert "TIP3P" in vcm.BENCH_PROTOCOL and "84,534" in vcm.BENCH_PROTOCOL


def test_ns_per_hour_no_longer_claims_to_be_the_ternary_system_size():
    """It said "ns/hr for this card at the ternary system size". No caller passes a system and none ever has;
    the figure is a water-box bench. A false provenance in a docstring is how a confident wrong number gets
    quoted into a report."""
    doc = vcm.ns_per_hour.__doc__ or ""
    # The SUMMARY LINE is the claim; the old phrase must still appear further down, because §1 requires a
    # corrected value to be registered rather than silently dropped. So this checks where it appears, not
    # whether it appears.
    summary = doc.strip().splitlines()[0]
    assert "at the ternary system size" not in summary, summary
    assert "84,534" in summary and "water-box" in summary
    assert "USED TO SAY" in doc and "FALSE" in doc, "the correction must be registered, not just applied"
    assert "index" in doc.lower()
