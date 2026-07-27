"""THE PIN THAT STOPS A GATE BEING RE-TYPED AS A MULTIPLE OF A MOVING BASIS.

WHAT HAPPENED (2026-07-27). The ladder basis fell 22 % — $0.004359 -> $0.003412/ns — because the
throughput table was re-anchored and widened. No price moved; the yardstick did. Every guard written
as `1.5 * basis` or `x_basis >= 1.5` therefore meant a ~22 % STRICTER rule than the one agreed, and
boards that had been passing started failing. Nothing announced the change, because nothing had
changed on purpose.

The ruling (CLAUDE.md §1): the invariant is the ABSOLUTE approved rate, and the multiple is DERIVED
from it, so a future basis correction re-derives the multiple instead of silently rewriting the rule.

WHAT THIS FILE ASSERTS. That the checker still tells the two shapes apart:
  bad   `if upn >= 1.5 * basis:`                 - a literal against a correctable denominator
  good  `if upn >= unit_rate_line_usd_per_ns():` - the derivation, called
and that its exemptions (tolerances, round-trips, relative perturbations of a derived value) hold,
because a checker that fires on `abs(a - b) < 1e-12` is a checker someone deletes.
"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import lint_derived_thresholds as lint  # noqa: E402

MODALITIES = os.path.abspath(os.path.join(HERE, ".."))


def write_py(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def bugs(path, allowlist=()):
    return [
        f
        for f in lint.scan_file(path, allowlist=allowlist)
        if f.severity == lint.SEVERITY_BUG and not f.allowlisted
    ]


# ---------------------------------------------------------------------------------------
# The known-bad and known-good shapes, as the ruling states them
# ---------------------------------------------------------------------------------------

KNOWN_BAD = """
def gate(upn, basis):
    if upn >= 1.5 * basis:
        return "refused"
    return "ok"
"""

KNOWN_GOOD = """
from congeneric_fanout import unit_rate_line_usd_per_ns


def gate(upn):
    if upn >= unit_rate_line_usd_per_ns():
        return "refused"
    return "ok"
"""


def test_a_typed_multiple_of_the_basis_is_flagged(tmp_path):
    path = write_py(tmp_path, "gate_bad.py", KNOWN_BAD)
    found = bugs(path)
    assert len(found) == 1, [f.render() for f in found]
    assert found[0].expression == "1.5 * basis"
    assert found[0].literal == 1.5
    assert "22 %" in found[0].why
    assert "basis_usd_per_ns" in found[0].should_be


def test_calling_the_derived_accessor_is_not_flagged(tmp_path):
    path = write_py(tmp_path, "gate_good.py", KNOWN_GOOD)
    assert lint.scan_file(path) == []


def test_the_ratio_form_is_the_same_bug(tmp_path):
    """`x_basis >= 1.92` hides the same staleness as `>= 1.92 * basis`."""
    path = write_py(
        tmp_path,
        "ratio.py",
        "def gate(x_basis):\n    return x_basis >= 1.92\n",
    )
    found = bugs(path)
    assert len(found) == 1
    assert "drift_buy_line_x_basis" in found[0].should_be


def test_a_typed_module_constant_is_flagged(tmp_path):
    """The shape that actually ships: a frozen multiple at module scope."""
    path = write_py(tmp_path, "consts.py", "MARKET_MAX_RATIO_VS_BASIS = 2.25\n")
    found = bugs(path)
    assert len(found) == 1
    assert found[0].shape == "ASSIGN"


def test_a_constant_derived_from_the_accessor_is_not_flagged(tmp_path):
    """The live form in `ternary_vast_launch.py`: an env override falling back to the derivation."""
    path = write_py(
        tmp_path,
        "consts_ok.py",
        "import os\n"
        "from inflight_usd_per_ns import drift_multiple\n"
        "MARKET_MAX_RATIO_VS_BASIS = float(os.environ.get('X') or drift_multiple())\n",
    )
    assert lint.scan_file(path) == []


def test_a_typed_kwarg_rate_is_flagged(tmp_path):
    path = write_py(tmp_path, "kw.py", "spec(max_usd_per_ns=0.0065)\n")
    found = bugs(path)
    assert len(found) == 1
    assert found[0].shape == "KWARG"


# ---------------------------------------------------------------------------------------
# The exemptions — each one earned by a false positive
# ---------------------------------------------------------------------------------------


def test_a_tolerance_is_not_a_threshold(tmp_path):
    """`abs(a - b) < tol` bounds precision. Magnitude is irrelevant; the DIFFERENCE is the tell."""
    path = write_py(
        tmp_path,
        "tol.py",
        "def check(basis, expected):\n"
        "    assert abs(basis - expected) < 1e-12\n"
        "    assert abs(basis - expected) < 0.2\n",
    )
    assert lint.scan_file(path) == []


def test_abs_without_a_difference_is_still_a_threshold(tmp_path):
    """`abs(rate) < 0.0065` is a rule wearing a tolerance's clothes. Not exempt."""
    path = write_py(
        tmp_path,
        "fake_tol.py",
        "def check(usd_per_ns):\n    return abs(usd_per_ns) < 0.0065\n",
    )
    assert len(bugs(path)) == 1


def test_a_relative_perturbation_of_a_derived_rate_is_not_flagged(tmp_path):
    """`APPROVED_USD_PER_NS * 1.001` moves WITH the basis — it is anchored, not typed."""
    path = write_py(
        tmp_path,
        "perturb.py",
        "from inflight_usd_per_ns import APPROVED_USD_PER_NS\n"
        "just_under = APPROVED_USD_PER_NS * 0.999\n"
        "just_over = APPROVED_USD_PER_NS * 1.001\n",
    )
    assert lint.scan_file(path) == []


def test_a_round_tripped_fixture_value_is_not_flagged(tmp_path):
    """A literal written in and asserted back out tests plumbing, not the basis."""
    path = write_py(
        tmp_path,
        "test_roundtrip_fixture.py",
        "def test_ledger(record, load):\n"
        "    record(gate={'ratio_vs_basis': 1.261})\n"
        "    assert load()[0]['gate_ratio_vs_basis'] == 1.261\n",
    )
    assert lint.scan_file(path) == []


def test_identities_are_never_thresholds(tmp_path):
    path = write_py(tmp_path, "ident.py", "x = 1 * basis_usd_per_ns()\ny = 0 * basis_usd_per_ns()\n")
    assert lint.scan_file(path) == []


def test_unrelated_domain_constants_are_out_of_vocabulary(tmp_path):
    """The false positives that forced the vocabulary to be narrowed. None of these are dollars.

    An earlier draft matched any name containing `threshold`, `drift`, `ceiling` or `per_ns`.
    A checker that flags a gnomAD constraint constant is a checker nobody keeps.
    """
    path = write_py(
        tmp_path,
        "domain.py",
        "LOEUF_THRESHOLD = 0.35\n"
        "PS_PER_NS = 1000.0\n"
        "ENDPOINT_DRIFT_SIGMA = 4.0\n"
        "pct = paralogue_ceiling * 100\n",
    )
    assert lint.scan_file(path) == []


# ---------------------------------------------------------------------------------------
# Severity, allowlist, and the live tree
# ---------------------------------------------------------------------------------------


def test_a_test_file_is_a_note_not_a_failure(tmp_path):
    """A literal in a test is usually a deliberate pin. Listed, never red."""
    path = write_py(tmp_path, "test_pinned.py", KNOWN_BAD)
    findings = lint.scan_file(path)
    assert len(findings) == 1
    assert findings[0].severity == lint.SEVERITY_NOTE
    assert bugs(path) == []


def test_an_allowlist_entry_without_a_reason_cannot_be_constructed():
    with pytest.raises(ValueError):
        lint.Allow(path="x.py", expression="1.5 * basis", reason="")
    with pytest.raises(ValueError):
        lint.Allow(path="x.py", expression="1.5 * basis", reason="fine")


def test_the_shipped_allowlist_keeps_the_historical_identity_typed():
    """`1.5 * old_basis` must stay typed: deriving it would make the proof circular."""
    assert len(lint.ALLOWLIST) == 1
    entry = lint.ALLOWLIST[0]
    assert entry.path.endswith("test_buy_line_invariant.py")
    assert entry.expression == "1.5 * old_basis"
    assert "HISTORICAL IDENTITY" in entry.reason


def test_an_allowlisted_finding_is_reported_but_does_not_fail(tmp_path):
    path = write_py(tmp_path, "gate_bad.py", KNOWN_BAD)
    allow = (
        lint.Allow(
            path="gate_bad.py",
            expression="1.5 * basis",
            reason="Synthetic fixture for the checker's own tests; it gates no real spend.",
        ),
    )
    assert bugs(path, allowlist=allow) == []
    assert lint.scan_file(path, allowlist=allow)[0].allowlisted


@pytest.mark.skipif(not os.path.isdir(MODALITIES), reason="modalities not checked out")
def test_no_production_module_types_a_multiple_of_the_basis():
    """The sweep as CI runs it. A new typed threshold in a shipping module turns this red."""
    assert lint.main(["lint_derived_thresholds.py", MODALITIES]) == 0
