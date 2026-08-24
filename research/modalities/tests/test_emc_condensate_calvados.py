"""The CALVADOS single-chain arm's frozen contract, asserted in CI.

⛔ These tests are the prespecification's enforcement, not a smoke test. The prespecification
(`emc-condensate-calvados-prespecification.md`) is frozen; if a construct boundary, a scoring rule or
a negative definition moves, that is an amendment and these fail until the amendment is written.

Pure stdlib: nothing here imports calvados, openmm or numpy, so it runs in the sandbox and in CI.
"""

import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(os.path.dirname(HERE), "emc_condensate_calvados.py")
PRESPEC = os.path.join(os.path.dirname(HERE),
                       "emc-condensate-calvados-prespecification.md")


def _mod():
    spec = importlib.util.spec_from_file_location("emc_condensate_calvados", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_selftest_passes_every_guard():
    assert _mod().selftest() == 0


def test_the_prespecification_exists_and_is_frozen():
    text = open(PRESPEC).read()
    assert "status: immutable" in text
    assert "Frozen 2026-08-24, before any construct in section 3 was simulated" in text
    assert "## 11 · Amendment log" in text


def test_every_negative_named_in_the_prespecification_is_reachable_in_the_scorer():
    """A negative the prose promises but the code cannot emit is a promise, not a rule."""
    m = _mod()
    text = open(PRESPEC).read()
    src = open(MOD).read()
    for name in ("NEGATIVE_COMPOSITION_ONLY", "NEGATIVE_NO_STRATIFICATION",
                 "NEGATIVE_WILDTYPE_NOT_SEPARATED", "NEGATIVE_FET_NOT_SPECIAL"):
        assert name in text, f"{name} missing from the prespecification"
        assert name in src, f"{name} is promised in prose but the scorer cannot emit it"
    assert m.score([])["verdict"] == "INCOMPLETE"


def test_no_verdict_about_a_partner_can_come_from_an_incomplete_run_set():
    m = _mod()
    for runs in ([], [{"run_id": "x", "construct": "E264", "nu": 0.5}]):
        r = m.score(runs)
        assert r["verdict"] in ("INCOMPLETE", "INSTRUMENT_FAILED")
        assert "negatives" not in r


def test_boundaries_are_read_from_committed_artifacts_not_typed():
    """If a committed artifact moves a boundary, the construct set must move with it."""
    m = _mod()
    b = m._boundaries()
    designs = json.load(open(os.path.join(os.path.dirname(HERE),
                                          "emc-fet-construct-designs.json")))
    t2 = next(c for c in designs["constructs"] if c["id"] == "EWSR1_NR4A3_type2")
    assert t2["domains_retained_and_lost"]["five_prime_FET_half"]["residues_retained"] \
        == f"EWSR1(1-{b['EWSR1_type2_retained']})"
    cons = {c["id"]: c for c in m.build_constructs()}
    assert cons["E264"]["length"] == b["EWSR1_type2_retained"]
    assert cons["E360"]["length"] == b["EWSR1_RRM_start"] - 1


def test_no_simulated_window_reaches_into_the_folded_rrm():
    """The commonest reported junction retains EWSR1 1-431 and the RRM starts at 361, so an
    all-disordered model may not be pointed at the untruncated type-1 segment."""
    m = _mod()
    b = m._boundaries()
    assert b["EWSR1_type1_retained"] > b["EWSR1_RRM_start"]  # the conflict is real
    for c in m.build_constructs():
        if c["window"].startswith("EWSR1") and c["role"] in ("TEST", "CONTROL"):
            assert c["length"] < b["EWSR1_RRM_start"]


def test_tcf12_windows_are_isoform_independent():
    m = _mod()
    s = m._sequences()
    ens, uni = s["TCF12"], s["TCF12_uniprot"]
    cons = {c["id"]: c for c in m.build_constructs()}
    for cid in ("C161", "C264", "C360"):
        n = cons[cid]["length"]
        assert ens[:n] == uni[:n], f"{cid} differs between the two committed TCF12 isoforms"


def test_length_matching_is_exact():
    m = _mod()
    cons = {c["id"]: c for c in m.build_constructs()}
    for fet, non in m.PRIMARY_FAMILY:
        assert cons[fet]["length"] == cons[non]["length"]


def test_the_primary_permutation_design_is_powered_and_three_versus_three_is_not():
    m = _mod()
    assert m.permutation_p([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])["powered"]
    assert not m.permutation_p([1, 2, 3], [4, 5, 6])["powered"]


def test_the_manifest_on_disk_matches_the_frozen_construct_set():
    m = _mod()
    path = os.path.join(os.path.dirname(HERE), "emc-condensate-constructs.json")
    if not os.path.exists(path):
        return
    disk = json.load(open(path))
    live = m.build_constructs()
    assert disk["n_constructs"] == len(live)
    assert disk["n_runs"] == sum(c["n_replicates"] for c in live)
    for a, b in zip(disk["constructs"], live):
        assert a["id"] == b["id"] and a["sha256"] == b["sha256"], a["id"]


def test_claim_ceiling_words_never_appear_in_the_scorer_output():
    m = _mod()
    banned = ("efficacy", "therapeutic window", "clinically", "patient-selective", "safe ")
    text = json.dumps(m.score([]))
    for w in banned:
        assert w not in text.lower()
