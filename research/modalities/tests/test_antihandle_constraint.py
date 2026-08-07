"""`Q3` / `S15` — the anti-handle set as a DESIGN CONSTRAINT.

These tests exist because the roadmap's own instruction was *"implement it as an actual predicate in the
design/enumeration code with tests, not as prose"*. A prose constraint cannot reject anything and cannot
be regression-tested; these are the assertions that make it a constraint.

⚠ The most load-bearing tests here are NOT the ones that check the arithmetic. They are:
  * `test_the_antihandle_set_is_derived_and_not_typed` — an anti-handle list typed into a module is a
    memory, and this repository's rule 1 exists because memories drift.
  * `test_the_marginalisation_is_the_union_not_the_intersection` — taking the intersection is the
    false-negative direction and would certify a construct whose liability appears under 5 of 6 poses.
  * `test_the_target_is_never_counted_as_a_competitor` — an off-by-one here would make C397 look like
    the liability the filter exists to refuse.
"""
import json
import os

import pytest

import antihandle_constraint as AC

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "nr4a3-antihandle-constraint.json")


@pytest.fixture(scope="module")
def reach_doc():
    return json.load(open(AC.REACH, encoding="utf-8"))


@pytest.fixture(scope="module")
def doc():
    if not os.path.exists(ART):
        pytest.skip("artifact not built")
    return json.load(open(ART, encoding="utf-8"))


# ==========================================================================================================
# THE PREDICATE — pure arithmetic, no I/O
# ==========================================================================================================
def test_reach_is_monotone_in_length():
    atoms = {"NR4A1 C551": 20, "NR4A2 C534": 14, "NR4A1 C505": 12}
    prev = set()
    for n in range(0, 30):
        env = AC.reach_envelope(atoms, n)
        assert prev <= env, "reach envelope shrank at n=%d — reach must be monotone in chain length" % n
        prev = env
    assert AC.reach_envelope(atoms, 13) == {"NR4A1 C505"}
    assert AC.reach_envelope(atoms, 14) == {"NR4A1 C505", "NR4A2 C534"}
    assert AC.reach_envelope(atoms, 20) == {"NR4A1 C505", "NR4A2 C534", "NR4A1 C551"}


def test_a_cysteine_with_no_recorded_requirement_is_never_admitted():
    """`None` means the enumeration could not reach it at any length. ⛔ An ABSENT READING IS NOT A
    READING OF ABSENCE, but for a FILTER the safe direction is the same either way: not admitted."""
    assert AC.reach_envelope({"NR4A1 C551": None}, 10 ** 6) == set()


def test_an_unspecified_construct_length_admits_nothing_rather_than_everything():
    assert AC.reach_envelope({"NR4A1 C551": 5}, None) == set()
    assert AC.admits_antihandle({"NR4A1 C551": 5}, None, {"NR4A1 C551"}) == []


def test_the_target_is_never_counted_as_a_competitor():
    """⛔ The target's own requirement travels inside the same map. If it leaked into the envelope, C397
    would be scored as the liability the filter exists to refuse."""
    atoms = {AC.TARGET_KEY: 3, "NR4A1 C551": 40}
    assert AC.reach_envelope(atoms, 10) == set()
    assert AC.target_in_envelope(atoms, 10) is True
    assert AC.target_in_envelope(atoms, 2) is False


def test_admits_antihandle_returns_witnesses_not_a_bare_boolean():
    """A filter that says REJECTED without naming the residue cannot be argued with, and `S15`'s whole
    value is that the residue it names is a demonstrated liability (NR4A1 C551 / celastrol)."""
    hits = AC.admits_antihandle({"NR4A1 C551": 8, "NR4A1 C505": 8}, 10, {"NR4A1 C551", "NR4A1 C534"})
    assert hits == ["NR4A1 C551"]


# ==========================================================================================================
# THE MARGINALISATION — the rule R5 forces
# ==========================================================================================================
def _cells(*specs):
    return [("cell%d" % i, "corridor", a) for i, a in enumerate(specs)]


def test_the_marginalisation_is_the_union_not_the_intersection():
    """★ A liability under ANY committed cell is a liability, because `R5` is unresolved and the program
    cannot name which cell is the real one. Taking the intersection would certify this construct."""
    anti = {"NR4A1 C551"}
    cells = _cells({"NR4A1 C551": 5}, {"NR4A1 C551": 999}, {"NR4A1 C551": 999})
    v = AC.construct_verdict(cells, 10, anti, set())
    assert v["n_cells_admitting_an_antihandle"] == 1
    assert v["reject_any_pose"] is True
    assert v["reject_all_poses"] is False
    assert v["verdict"] == "REJECT", "one cell in three admitting the liability must REJECT"


def test_a_clean_construct_passes_and_a_pass_requires_every_cell_clean():
    anti = {"NR4A1 C551"}
    v = AC.construct_verdict(_cells({"NR4A1 C551": 999}, {"NR4A1 C551": 999}), 10, anti, set())
    assert v["verdict"] == "PASS" and v["reject_any_pose"] is False


def test_no_cells_is_NOT_EVALUABLE_rather_than_a_pass():
    """⛔ A filter with nothing to evaluate must not report a pass. An empty run that renders as green is
    the exact failure `preflight.sh`'s own header records."""
    v = AC.construct_verdict([], 12, {"NR4A1 C551"}, set())
    assert v["verdict"] == "NOT EVALUABLE"


# ==========================================================================================================
# THE SET — derived, never typed
# ==========================================================================================================
def test_the_antihandle_set_is_derived_and_not_typed(reach_doc):
    """Every member must be `paralogue_unique_vs_NR4A3` in the COMMITTED map, and every such member must
    be in the set. If the map changes, the constraint changes with it."""
    anti, shared, detail = AC.anti_handle_set(reach_doc)
    by_par = reach_doc["paralogue_control"]["reciprocal_uniqueness"]["by_paralogue"]
    expected = {"%s %s" % (p, c) for p, m in by_par.items() for c, r in m.items()
                if r.get("paralogue_unique_vs_NR4A3")}
    assert anti == expected
    assert anti and not (anti & shared)
    for lab in anti:
        assert detail[lab]["nr4a3_has_a_cysteine_here"] is False, (
            "%s is called an anti-handle while NR4A3 carries a cysteine at the aligned position" % lab)
    for lab in shared:
        assert detail[lab]["nr4a3_has_a_cysteine_here"] is True


def test_a_shared_position_paralogue_cysteine_is_not_an_antihandle(reach_doc):
    """⛔ NR4A1 C505 aligns to NR4A3 C536, a cysteine NR4A3 HAS. It is the most frequent window-closer on
    the board, which is why it reached the roadmap's prose — but a residue both proteins carry cannot be
    a RECIPROCAL anti-handle, and folding it in would make `S15` indistinguishable from the ordinary
    off-target-cysteine constraint the reach module already computes."""
    anti, shared, _ = AC.anti_handle_set(reach_doc)
    assert "NR4A1 C505" in shared and "NR4A1 C505" not in anti


def test_the_roadmap_prose_set_disagreement_is_reported_rather_than_absorbed(reach_doc):
    """The predicate must never silently adopt the prose set, and must never silently drop it either."""
    anti, shared, _ = AC.anti_handle_set(reach_doc)
    dis = AC.roadmap_set_disagreement(anti, shared)
    assert set(dis["derived_set"]) == anti
    assert dis["agrees"] == (set(dis["prose_set"]) == anti)
    if not dis["agrees"]:
        assert dis["in_prose_but_not_reciprocal_unique"] or \
               dis["reciprocal_unique_but_missing_from_the_prose"], \
            "a disagreement was flagged and neither direction was named"


def test_the_prose_set_is_never_used_as_the_constraint():
    """Held as a literal so the disagreement is MEASURABLE — but a grep-level guarantee that it is not
    wired into the predicate. `admits_antihandle` takes its set as an argument and has no default."""
    import inspect
    src = inspect.getsource(AC.admits_antihandle) + inspect.getsource(AC.construct_verdict) + \
        inspect.getsource(AC.screen)
    assert "ROADMAP_PROSE_SET" not in src


# ==========================================================================================================
# THE ARTIFACT
# ==========================================================================================================
def test_the_gate_is_read_from_its_one_home_and_not_typed(doc):
    dyn = json.load(open(AC.DYNAMICS, encoding="utf-8"))
    assert doc["★_length_frontier"]["categorical_gate_atoms"] == \
        dyn["categorical_verdict"]["gate_atoms"]


def test_the_length_frontier_is_monotone(doc):
    """Reach is monotone in length, so anti-handle admission must be too. A non-monotone frontier would
    mean the arithmetic is wrong, not that the protein is interesting."""
    rows = doc["★_length_frontier"]["by_length"]
    for a, b in zip(rows, rows[1:]):
        assert b["n_backbone_atoms"] > a["n_backbone_atoms"]
        assert b["n_cells_admitting_an_antihandle"] >= a["n_cells_admitting_an_antihandle"]
        assert b["n_cells_where_C397_ITSELF_is_reached"] >= a["n_cells_where_C397_ITSELF_is_reached"]


def test_the_design_target_column_is_reported_and_its_peak_is_derived(doc):
    """★ The column that decides whether a length is BUILDABLE — reaching C397 while admitting no
    anti-handle. It need not be monotone, and its peak must be derived from the rows rather than typed."""
    lf = doc["★_length_frontier"]
    rows = lf["by_length"]
    key = "★_n_cells_reaching_C397_WITHOUT_an_antihandle"
    for r in rows:
        assert 0 <= r[key] <= r["n_cells_where_C397_ITSELF_is_reached"], (
            "clean hits cannot exceed cells that reach the target at all")
    peak = lf["★_the_design_target_column_peaks_at"]
    best = max(rows, key=lambda r: r[key])
    assert peak["n_backbone_atoms"] == best["n_backbone_atoms"]
    assert peak["n_cells"] == best[key]


def test_the_composition_claim_does_not_outrun_its_own_column(doc):
    """⛔ THE GUARD ON MY OWN SENTENCE. If the design-target column does NOT peak at the gate, the
    artifact must say so explicitly — a composition claim that hid the disagreement would be exactly the
    drift Q4 exists to stop."""
    lf = doc["★_length_frontier"]
    peak = lf["★_the_design_target_column_peaks_at"]
    if peak["is_the_categorical_gate"]:
        return
    txt = lf["⛔_and_the_composition_is_NOT_as_simple_as_that"]
    assert "does NOT peak at the gate" in txt
    assert "DOES NOT LICENSE THE LONGER LENGTH" in txt
    assert "V17" in txt, "the reason the longer length is refused must be named"


def test_every_construct_carries_a_marginalised_verdict_and_the_own_placement_column_is_labelled(doc):
    for r in doc["per_construct"]:
        m = r["marginalised_over_poses"]
        assert m["verdict"] in ("REJECT", "PASS", "NOT EVALUABLE")
        assert "UNION" in m["_marginalisation"]
        assert "DIAGNOSTIC ONLY" in r["_own_placement_reading"], (
            "a per-placement column that is not labelled DIAGNOSTIC is a pose-specific claim, which R5 "
            "does not permit")


def test_the_summary_counts_are_derived_from_the_rows_not_typed(doc):
    rows = doc["per_construct"]
    s = doc["summary"]
    assert s["n_constructs"] == len(rows)
    assert s["n_rejected_under_the_union_rule"] == sum(
        1 for r in rows if r["marginalised_over_poses"]["reject_any_pose"])
    assert s["n_surviving"] == s["n_constructs"] - s["n_rejected_under_the_union_rule"]
    assert sorted(s["surviving_construct_ids"]) == sorted(
        r["construct_id"] for r in rows if not r["marginalised_over_poses"]["reject_any_pose"])


def test_the_headline_carries_the_marginalisation_rule_it_depends_on(doc):
    """★ A headline is the sentence that gets quoted alone. 'No committed construct survives' is true
    under the UNION rule and would be an overstatement without it — especially while the intersection
    count is 0, i.e. every rejection rests on SOME cell rather than all of them."""
    h = doc["verdict"]["headline"]
    s = doc["summary"]
    if s["n_surviving"] == 0:
        assert "UNION-OVER-POSES" in h
        assert str(s["n_rejected_in_EVERY_cell"]) in h
        assert "R5" in h


def test_the_artifact_makes_no_licensing_claim(doc):
    """Language discipline. The claim ceiling binds inside artifacts as well as in the manuscript."""
    blob = json.dumps(doc, ensure_ascii=False).lower()
    for banned in ("therapeutic window", "clinically", "clinical readiness", "is safe", "efficacious"):
        # the phrases appear ONLY inside explicit refusals, which all begin with a refusal marker
        for hit in [i for i in range(len(blob)) if blob.startswith(banned, i)]:
            ctx = blob[max(0, hit - 300):hit]
            assert any(m in ctx for m in ("not", "no ", "never", "⛔", "does not", "nothing here")), \
                "%r appears without a refusal in context" % banned


def test_the_pose_marginalisation_cites_the_second_method_result(doc):
    ev = doc["_pose_marginalisation"]["evidence"]
    assert ev["read"] is True, "the marginalisation premise must be READ, not described"
    assert ev["R5_resolved"] is False, (
        "R5 is recorded as resolved — if the second pose method now agrees, this constraint's "
        "marginalisation rule must be revisited deliberately rather than left standing")
