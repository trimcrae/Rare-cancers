import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fep_decision as fd  # noqa: E402


def _b(n3, se3, n1, se1, n2, se2):
    return {"nr4a3": {"dg": n3, "se": se3}, "nr4a1": {"dg": n1, "se": se1}, "nr4a2": {"dg": n2, "se": se2}}


def test_provisional_ddg_sign_and_error():
    ddg = fd.provisional_ddg(_b(-12, 0.3, -8, 0.4, -7, 0.0))
    assert ddg["nr4a1"]["ddg"] == -4.0
    assert abs(ddg["nr4a1"]["se"] - 0.5) < 1e-9      # sqrt(0.3^2+0.4^2)
    assert all(v["ddg"] < 0 for v in ddg.values())   # NR4A3-selective


def test_stop_fail_when_optimistic_bound_still_nonselective():
    # NR4A3 NOT tighter than NR4A1 (ddg ~ +3), tiny se -> even optimistic bound > target -> stop_fail
    d = fd.early_stop(_b(-8.0, 0.2, -11.0, 0.2, -12.0, 0.2), target_ddg=-1.0, z=1.0)
    assert d["action"] == "stop_fail"
    assert "not selective" in d["reason"].lower() or "aborting" in d["reason"].lower()


def test_continue_when_ambiguous():
    # ddg ~ -1.5 but large se -> optimistic bound below target, pessimistic above -> keep sampling
    d = fd.early_stop(_b(-11.5, 2.0, -10.0, 2.0, -10.0, 2.0), target_ddg=-1.0, z=1.0)
    assert d["action"] == "continue"


def test_stop_success_optional():
    # confidently selective vs both, small se
    b = _b(-14.0, 0.2, -8.0, 0.2, -8.0, 0.2)
    assert fd.early_stop(b, target_ddg=-1.0, z=1.0, allow_success_stop=True)["action"] == "stop_success"
    # but not when success-stop disabled
    assert fd.early_stop(b, target_ddg=-1.0, z=1.0, allow_success_stop=False)["action"] == "continue"


def test_stop_fail_takes_priority_only_when_confident():
    # one paralogue clearly fails (nr4a2 far tighter than nr4a3) -> stop_fail regardless of the other
    d = fd.early_stop(_b(-9.0, 0.1, -20.0, 0.1, -9.5, 0.1), target_ddg=-1.0, z=1.0)
    assert d["action"] == "stop_fail"


def test_convergence_flag():
    assert fd.convergence_flag([0.1, 0.2, 0.05, 0.15])["ok"] is True
    bad = fd.convergence_flag([0.001, 0.0, 0.002, 0.2], min_overlap=0.03, min_frac_ok=0.5)
    assert bad["ok"] is False and "stop_unconverged" in bad["reason"]
    assert fd.convergence_flag([])["ok"] is True     # no data yet != failure


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
