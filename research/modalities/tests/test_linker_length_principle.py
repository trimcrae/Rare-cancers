"""`Q4` / `S6` — the linker-length design principle, stated at the 12-atom gate AND ONLY THERE.

⚠ The point of this suite is not that the arithmetic is right. It is that **the principle cannot escape
its gate**. `Q4`'s falsifier is written into the roadmap as *"stated at 16–20 atoms it inherits `V17`'s
false negative … The gate IS the falsifier"* — so the tests that matter are the ones asserting that no
code path emits a selectivity statement above the gate, and that every rendering of the statement carries
its own gate inside it.
"""
import json
import os

import pytest

import linker_length_principle as P

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "nr4a3-linker-length-principle.json")


@pytest.fixture(scope="module")
def cv():
    return P.load_dynamics()


@pytest.fixture(scope="module")
def doc():
    if not os.path.exists(ART):
        pytest.skip("artifact not built")
    return json.load(open(ART, encoding="utf-8"))


# ==========================================================================================================
# THE GATE — read, never typed
# ==========================================================================================================
def test_the_gate_is_read_from_its_one_home(cv):
    """⛔ This module must never contain the literal gate. Its home is
    `nr4a-paralogue-dynamics.json -> categorical_verdict.gate_atoms`."""
    assert P.gate_atoms(cv) == cv["gate_atoms"]


def test_the_module_does_not_type_the_gate_value():
    import inspect
    src = inspect.getsource(P)
    # the gate appears only via gate_atoms(); a bare `12` as a threshold would be the drift rule 1 exists
    # to stop. Titles/docstrings may mention it — the assertion is about executable comparisons.
    code = [ln for ln in src.splitlines()
            if not ln.lstrip().startswith(("#", '"', "'"))]
    for ln in code:
        assert "n > 12" not in ln and "n <= 12" not in ln and "== 12" not in ln, \
            "the gate is typed as a literal in %r" % ln.strip()


# ==========================================================================================================
# ★ THE REFUSAL — the whole of "and only there"
# ==========================================================================================================
def test_the_principle_is_STATED_at_the_gate(cv):
    r = P.principle(P.gate_atoms(cv), cv)
    assert r["status"] == "STATED" and r["statement"]
    assert r["at_the_gate"] is True


def test_the_principle_is_REFUSED_above_the_gate_and_emits_no_statement(cv):
    """★ THE LOAD-BEARING TEST. Above the gate there is no hedged statement — there is no statement."""
    g = P.gate_atoms(cv)
    lengths = sorted({b["n_backbone_atoms"] for b in P.bands(cv)})
    above = [n for n in lengths if n > g]
    assert above, "the fixture has no above-gate length, so this test proves nothing"
    for n in above:
        r = P.principle(n, cv)
        assert r["status"] == "REFUSED", "a statement was emitted at %d atoms" % n
        assert r["statement"] is None
        assert P.FAILED_EXPOSURE_INSTRUMENT in r["reason"], (
            "a refusal that does not name the failed instrument is a refusal nobody can act on")


def test_an_unmeasured_length_is_REFUSED_rather_than_interpolated(cv):
    r = P.principle(13, cv)
    assert r["status"] == "REFUSED" and r["statement"] is None
    assert "NO MEASUREMENT" in r["reason"]


def test_the_default_is_the_gate_not_the_caller_s_convenience(cv):
    assert P.principle(cv=cv)["requested_atoms"] == P.gate_atoms(cv)


# ==========================================================================================================
# THE STATEMENT CARRIES ITS OWN GATE
# ==========================================================================================================
def test_every_rendering_of_the_statement_contains_its_gate_and_its_qualifier(cv):
    """A copy-pasted sentence must arrive with its gate. This is mechanism (2) of the three."""
    g = P.gate_atoms(cv)
    s = P.principle(g, cv)["statement"]
    assert str(g) in s
    assert "ONLY THERE" in s
    assert "REACH ALONE" in s
    assert P.FAILED_EXPOSURE_INSTRUMENT in s
    assert "may not be quoted" in s


def test_the_statement_makes_no_selectivity_efficacy_or_readiness_claim(cv):
    s = P.principle(cv=cv)["statement"].lower()
    assert "discrimination is geometry; it is not selectivity" in s
    for banned in ("therapeutic window", "clinical readiness", "proteome-wide selectivity", "efficacy"):
        i = s.find(banned)
        assert i >= 0, "the statement must explicitly refuse %r, not merely omit it" % banned
        assert "does not" in s[max(0, i - 300):i] or "not" in s[max(0, i - 300):i]


def test_the_statement_names_no_pose_basin_or_exit_vector(cv):
    """`R5` is unresolved. A length principle that named a vector would be a pose-conditional claim
    wearing a length label."""
    s = P.principle(cv=cv)["statement"].lower()
    for token in ("exitvec", "basin", "pose ", "vhl|", "crbn|"):
        assert token not in s, "the statement re-specialises to %r" % token


# ==========================================================================================================
# ★ THE QUOTATION GUARD — mechanism (3)
# ==========================================================================================================
def test_the_guard_flags_an_above_gate_band_quoted_without_the_disclosure(cv):
    n = max(b["n_backbone_atoms"] for b in P.bands(cv))
    lo, hi = P._band_patterns(cv)[n]
    r = P.quotation_guard("the design principle gives %s at long linkers, so prefer them" % hi, cv)
    assert r["n_above_gate_quotations"] >= 1
    assert r["n_undisclosed"] >= 1


def test_the_guard_clears_the_same_band_when_the_disclosure_travels_with_it(cv):
    n = max(b["n_backbone_atoms"] for b in P.bands(cv))
    lo, hi = P._band_patterns(cv)[n]
    r = P.quotation_guard("%s — but this column inherits V17's false negative and is not a "
                          "selectivity statement" % hi, cv)
    assert r["n_above_gate_quotations"] >= 1
    assert r["n_undisclosed"] == 0


def test_the_guard_does_not_fire_on_the_gate_band_itself(cv):
    g = P.gate_atoms(cv)
    lo, hi = P._band_patterns(cv)[g]
    r = P.quotation_guard("at the gate the band is %s–%s" % (lo, hi), cv)
    assert r["n_above_gate_quotations"] == 0, (
        "the guard fired on the gate's own band — it would then fire on every correct use")


def test_the_committed_principle_artifact_passes_its_own_guard(cv):
    """⛔ The artifact quotes every band, including the above-gate ones. It must therefore carry the
    disclosure beside each — a guard whose own output fails it is a guard nobody will keep."""
    md = os.path.join(HERE, "..", "nr4a3-linker-length-principle.md")
    if not os.path.exists(md):
        pytest.skip("markdown not built")
    r = P.quotation_guard(open(md, encoding="utf-8").read(), cv)
    assert r["n_undisclosed"] == 0, r["findings"]


# ==========================================================================================================
# THE NUMBERS — derived from their one home
# ==========================================================================================================
def test_every_band_reproduces_the_committed_source(cv):
    for b in P.bands(cv):
        for scope, v in b["reach_only_by_scope"].items():
            src = cv["by_scope"][scope]["by_linker_atoms"][str(b["n_backbone_atoms"])]
            assert v == src["P_paralogue_also_labelled_given_nr4a3"]
        assert b["reach_only_band"][0] == min(b["reach_only_by_scope"].values())
        assert b["reach_only_band"][1] == max(b["reach_only_by_scope"].values())


def test_the_reach_only_dependence_is_monotone_in_length(cv):
    rows = P.bands(cv)
    for a, b in zip(rows, rows[1:]):
        assert b["reach_only_band"][1] >= a["reach_only_band"][1], (
            "the length dependence is not monotone — the principle's premise is that it is")


def test_the_S6_phrasing_correction_is_measured_not_asserted(doc, cv):
    """`S6` says P(categorical | exposed) is 1.000 at EVERY length. The artifact must report the per-scope
    reading rather than repeat the rounded one."""
    per = doc["★_why_only_at_the_gate"]["P_categorical_given_exposed_by_scope_over_all_lengths"]
    assert per, "the per-scope reading is absent, so the correction is an assertion"
    assert any(v != [1.0, 1.0] for v in per.values()), (
        "every scope is exactly 1.0 — if that is now true, S6's phrasing is correct and this "
        "correction must be withdrawn deliberately rather than left standing")


def test_the_composition_with_Q3_is_read_not_described(doc):
    c = doc["★_composition_with_Q3"]
    if not c.get("read"):
        pytest.skip("Q3 artifact not built")
    assert c["gate_atoms"] == doc["gate_atoms"], "the two artifacts disagree about the gate"
    assert c["at_the_gate"]["is_the_categorical_gate"] is True


def test_the_artifact_records_a_refusal_for_every_above_gate_length(doc):
    g = doc["gate_atoms"]
    for n, r in doc["★_refused_above_the_gate"].items():
        assert r["status"] == "REFUSED" and r["statement"] is None
        assert int(n) != g
