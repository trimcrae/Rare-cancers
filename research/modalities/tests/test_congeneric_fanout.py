"""Unit tests for the STEP 1 fan-out core (congeneric_fanout.py) + the Vast launcher's pure jobspec build.

These gate the decisions that a fan-out cannot get wrong silently: which units are launched, which are
deliberately excluded (and why), that no map edge is dropped, that the ligand SMILES the engine parameterizes
match the frozen map, and that the thermodynamic-cycle bookkeeping signs edges correctly.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import congeneric_fanout as cf  # noqa: E402


# ---- unit enumeration -------------------------------------------------------------------------------------

def test_tranche1_covers_every_map_edge_exactly_once():
    units = cf.default_units()
    edges = [e["edge_id"] for e in cf.load_map()["edges"]]
    assert [u["edge_id"] for u in units] == edges
    assert len(units) == len(set(u["unit_id"] for u in units)) == 19


def test_tranche1_is_charge_conserving_only():
    assert all(not u["charge_changing"] for u in cf.default_units())


def test_charge_changing_legs_are_enumerated_but_disjoint_from_tranche1():
    t1 = {u["unit_id"] for u in cf.default_units()}
    t2 = {u["unit_id"] for u in cf.charge_changing_units()}
    assert t2 and not (t1 & t2)
    assert all(u["charge_changing"] for u in cf.charge_changing_units())
    # the map declares 27 microstate legs in total; tranche 1 + tranche 2 must account for all of them
    total = sum(len(e.get("microstate_legs") or []) for e in cf.load_map()["edges"])
    assert len(t1) + len(t2) == total == 27


def test_no_edge_is_silently_dropped(tmp_path):
    """An edge with only charge-changing legs must ABORT enumeration, not vanish from the fan-out."""
    m = cf.load_map()
    m["edges"][0]["microstate_legs"] = [{"leg_id": "neutral__anionic", "state_a": "neutral",
                                         "state_b": "anionic_x", "net_charge_change": -1,
                                         "charge_change": True}]
    p = tmp_path / "map.json"
    p.write_text(json.dumps(m))
    with pytest.raises(ValueError, match="NO charge-conserving"):
        cf.default_units(map_path=str(p))


def test_smiles_registry_fails_closed_on_drift(tmp_path):
    s = cf.load_series()
    s["compounds"][0]["smiles"] = "CCO"
    p = tmp_path / "series.json"
    p.write_text(json.dumps(s))
    with pytest.raises(ValueError, match="SMILES drift"):
        cf.smiles_registry(series_path=str(p))


def test_comparator_scaffolds_are_not_in_the_rbfe_registry():
    """denovo_401 and its analogues are a DIFFERENT scaffold — the common-mode assumption is invalid across
    scaffolds, so they get ABFE, never an RBFE edge into the indole series."""
    reg = cf.smiles_registry()
    assert not [k for k in reg if k.startswith("cw_cmp_")]
    units = cf.default_units()
    assert not [u for u in units if "denovo" in u["ligand_a"] or "denovo" in u["ligand_b"]]


def test_is_charge_changing_detects_charge_from_any_signal():
    assert cf.is_charge_changing({"charge_change": True})
    assert cf.is_charge_changing({"net_charge_change": -1})
    assert cf.is_charge_changing({"state_a": "neutral", "state_b": "cationic_ammonium"})
    assert not cf.is_charge_changing({"state_a": "neutral", "state_b": "neutral_acid",
                                      "net_charge_change": 0, "charge_change": False})


def test_unit_ids_are_stable_for_the_primary_frame_and_qualified_otherwise():
    assert cf.unit_id("e_x", "neutral__neutral") == "e_x__neutral__neutral"
    other = cf.unit_id("e_x", "neutral__neutral", "nr4a1", "nr4a1_antitarget:matched_open_frame")
    assert other == "e_x__neutral__neutral__nr4a1_matched_open_frame"


def test_frame_units_reuse_tranche1_edges_on_another_receptor():
    fu = cf.frame_units("nr4a1", "nr4a1_antitarget:matched_open_frame")
    assert len(fu) == len(cf.default_units())
    assert all(u["receptor"] == "nr4a1" for u in fu)
    assert not ({u["unit_id"] for u in fu} & {u["unit_id"] for u in cf.default_units()})


# ---- engine wiring ----------------------------------------------------------------------------------------

def test_unit_env_shapes_the_two_alchemical_legs():
    u = cf.default_units()[0]
    cx = cf.unit_env(u, "complex")
    assert cx["MODE"] == "splittest" and cx["RBFE_TINY"] == "0" and cx["OPENMM_REQUIRE_CUDA"] == "1"
    assert cx["LIGAND_A"] == u["ligand_a"] and cx["LIGAND_B"] == u["ligand_b"]
    assert cf.unit_env(u, "reduce")["MODE"] == "reduce"
    assert cf.unit_env(u, "reduce")["OPENMM_REQUIRE_CUDA"] == "0"
    with pytest.raises(ValueError):
        cf.unit_env(u, "bogus")


def test_result_and_checkpoint_keys_are_per_unit_and_disjoint():
    units = cf.default_units()
    rk = [cf.result_key(u, "p") for u in units]
    ck = [cf.checkpoint_prefix(u, "p") for u in units]
    assert len(set(rk)) == len(set(ck)) == len(units)
    assert not set(rk) & set(ck)


# ---- cycle bookkeeping ------------------------------------------------------------------------------------

def _closed_ddg():
    """A ddG set in which every declared cycle closes exactly, built from a per-node potential (so the signs
    are right by construction, whichever direction each edge is written in)."""
    pot = {"zaienne_cmpd19": 0.0, "cw_ev_5nh2": 1.5, "cw_ms_5acetamido_ester": -0.4, "cw_ev_5oh": 0.8,
           "cw_ev_5opropargyl": -1.1, "cw_ms_free_acid": 2.2, "cw_bio_primary_amide": 0.3}
    out = {}
    for e in cf.load_map()["edges"]:
        if e["node_a"] in pot and e["node_b"] in pot:
            out[e["edge_id"]] = pot[e["node_b"]] - pot[e["node_a"]]
    return out


def test_cycles_close_for_a_self_consistent_ddg_set():
    res = cf.cycle_closure(_closed_ddg())
    assert len(res) == 3
    for c in res:
        assert c["status"] == "ok", c
        assert abs(c["sum_kcal"]) < 1e-6


def test_a_broken_edge_is_reported_as_a_violation():
    ddg = _closed_ddg()
    ddg["e_cw_ev_5oh__cw_ev_5opropargyl"] += 4.0
    res = {c["cycle_id"]: c for c in cf.cycle_closure(ddg)}
    assert res["cycle_exitvector_ether"]["status"] == "VIOLATION"
    assert res["cycle_3carbonyl"]["status"] == "ok"


def test_missing_edges_report_incomplete_rather_than_a_fabricated_closure():
    ddg = _closed_ddg()
    del ddg["e_zaienne_cmpd19__cw_ev_5oh"]
    res = {c["cycle_id"]: c for c in cf.cycle_closure(ddg)}
    assert res["cycle_exitvector_ether"]["status"] == "incomplete"
    assert res["cycle_exitvector_ether"]["missing"] == ["e_zaienne_cmpd19__cw_ev_5oh"]
    assert "sum_kcal" not in res["cycle_exitvector_ether"]


def test_ranking_uses_anchor_rooted_edges_only_and_sorts_tightest_first():
    rows = cf.rank_by_ddg({"e_zaienne_cmpd19__cw_ev_5nh2": 1.84,
                           "e_zaienne_cmpd19__cw_ev_5oh": -0.5,
                           "e_cw_ev_5oh__cw_ev_5opropargyl": -9.9})
    assert [r["node"] for r in rows] == ["cw_ev_5oh", "cw_ev_5nh2"]      # closure edge excluded
    assert rows[0]["ddg_bind_kcal"] < rows[1]["ddg_bind_kcal"]


# ---- planning ---------------------------------------------------------------------------------------------

def test_plan_states_what_it_does_not_run():
    p = cf.plan()
    assert p["n_units"] == 19
    assert len(p["excluded_tranche_2_charge_changing"]) == 8
    assert p["excluded_tranche_3_frames"]
    assert "not selectivity" in p["claim_ceiling"].lower() or "NOT a selectivity" in p["claim_ceiling"]
    lo, hi = p["cost_usd_est"]
    # ⚠ THIS BOUND WAS A STALE COPY OF A RETIRED NUMBER. It read `5 < lo < hi < 60`, commented "the pinned
    # ~$12-26 band, with measurement slack" — but that band was repriced to **~$36 ($15-80)** when the ~4x
    # cost error was found (wrong molecule 2.6x, wrong bid basis 3x; see step1-fanout-lane.md §5 and
    # STRATEGY.md's ladder entry). plan() correctly reports the corrected band, so the TEST was the thing
    # holding the retired figure, and it went red the moment anyone touched this lane. That is precisely the
    # one-fact-one-place failure the repo's own linter exists for — a number living in two places while a
    # correction reached only one.
    # Assert the SHAPE (ordered, positive, finite) and a generous ceiling that no longer encodes a specific
    # estimate; the band itself has one home, and it is not here.
    assert 0 < lo < hi < 200


def test_wave_plan_matches_the_requested_width():
    assert cf.wave_plan(19, 8)["waves"] == 3
    assert cf.wave_plan(8, 8)["waves"] == 1
    assert cf.wave_plan(1, 8)["waves"] == 1


# ---- launcher jobspec (pure part) -------------------------------------------------------------------------

def test_jobspec_is_resumable_checkpointed_and_per_unit_scoped():
    import congeneric_fanout_vast as fv
    u = cf.default_units()[3]
    spec = fv.build_jobspec(u, "my-branch", "bkt", 3)
    assert spec.resume is True
    assert spec.checkpoint_uri.startswith("s3://bkt/") and u["unit_id"] in spec.checkpoint_uri
    assert spec.name.startswith("s1f-03-") and len(spec.name) <= 64
    assert spec.env["LIGAND_A"] == u["ligand_a"] and spec.env["LIGAND_B"] == u["ligand_b"]
    assert spec.env["GIT_BRANCH"] == "my-branch"
    body = spec.command[-1]
    # both alchemical legs run, each spot-safe, and the branch's own code is what executes
    assert "run_leg complex" in body and "run_leg solvent" in body
    assert "RBFE_SPOT_SAFE=1" in body and "RBFE_SPOT_COMMIT_S3" in body
    assert "$GIT_BRANCH.tar.gz" in body
    # the engine's 401-anchored reduce is deliberately NOT used
    assert "MODE=reduce" not in body
    assert "ddg_bind" in body


def test_every_unit_gets_a_distinct_instance_label():
    import congeneric_fanout_vast as fv
    names = [fv.build_jobspec(u, "b", "bkt", i).name for i, u in enumerate(cf.default_units())]
    assert len(set(names)) == len(names)


# ---- progress census, host exclusion and the cost ledger ---------------------------------------------------
# These gate the RESUME half of the lane, which is where it has actually failed. Wave 1 proved the lane
# SAMPLES; 0 of 19 units ever reached a ddG. So what needs testing now is not "does a jobspec build" but
# "can the driver tell an advancing unit from a wedged one, does it spend on distinct hosts, and does the
# realised-cost arithmetic hold" — the three things whose absence let a ~4x cost error stand unnoticed.


class _FakeS3:
    """Minimal stand-in for the two S3 calls the census makes. Not a mock of boto3 — just enough shape that
    the KEY PARSING and the SCALAR ORDERING are exercised on real key strings."""

    def __init__(self, keys, raise_on_list=False):
        self._keys, self._raise = list(keys), raise_on_list

    def get_paginator(self, _op):
        outer = self

        class _P:
            @staticmethod
            def paginate(Bucket=None, Prefix=""):  # noqa: N803 — boto3's kwarg names
                if outer._raise:
                    raise RuntimeError("listing blew up")
                yield {"Contents": [{"Key": k} for k in outer._keys if k.startswith(Prefix)]}
        return _P()


def _ckpt_key(unit, leg, phase, it, gen="g0", leaf="COMMITTED.json"):
    import congeneric_fanout_vast as fv
    return f"{cf.checkpoint_prefix(unit, fv.RESULT_PREFIX)}/{leg}/{phase}/iter-{it:08d}/{gen}/{leaf}"


def test_committed_progress_reads_the_furthest_commit():
    import congeneric_fanout_vast as fv
    u = cf.default_units()[0]
    s3 = _FakeS3([_ckpt_key(u, "complex", "warmup", 20), _ckpt_key(u, "complex", "warmup", 40),
                  _ckpt_key(u, "complex", "production", 80)])
    scalar, detail = fv.committed_progress(s3, "bkt", u)
    assert detail == "complex/production@80" and scalar > 0


def test_committed_progress_scalar_is_monotone_across_both_transitions():
    """The two places a naive iteration counter REGRESSES on a healthy unit: warmup->production (the counter
    restarts) and complex-leg->solvent-leg (it restarts again). Either would read as a stall."""
    import congeneric_fanout_vast as fv
    u = cf.default_units()[0]
    seq = [[_ckpt_key(u, "complex", "warmup", 200)],
           [_ckpt_key(u, "complex", "warmup", 200), _ckpt_key(u, "complex", "production", 1)],
           [_ckpt_key(u, "complex", "production", 2000)],
           [_ckpt_key(u, "complex", "production", 2000), _ckpt_key(u, "solvent", "warmup", 1)],
           [_ckpt_key(u, "solvent", "production", 1)]]
    scalars = [fv.committed_progress(_FakeS3(k), "bkt", u)[0] for k in seq]
    assert scalars == sorted(scalars) and len(set(scalars)) == len(scalars), scalars


def test_committed_progress_distinguishes_unreadable_from_zero():
    """A listing failure must NOT read as 'no progress' — that manufactures a stall out of a network blip."""
    import congeneric_fanout_vast as fv
    u = cf.default_units()[0]
    assert fv.committed_progress(_FakeS3([], raise_on_list=True), "bkt", u)[0] == -1
    assert fv.committed_progress(_FakeS3([]), "bkt", u)[0] == 0


def test_committed_progress_ignores_keys_it_cannot_interpret():
    import congeneric_fanout_vast as fv
    u = cf.default_units()[0]
    junk = [_ckpt_key(u, "complex", "warmup", 10).replace("iter-00000010", "iter-oops"),
            _ckpt_key(u, "sidecar", "warmup", 10), _ckpt_key(u, "complex", "cooldown", 10),
            f"{cf.checkpoint_prefix(u, fv.RESULT_PREFIX)}/stray.json"]
    assert fv.committed_progress(_FakeS3(junk), "bkt", u)[0] == 0
    assert fv.committed_progress(_FakeS3(junk + [_ckpt_key(u, "complex", "warmup", 10)]),
                                 "bkt", u)[1] == "complex/warmup@10"


def test_ledger_cost_prices_on_the_bid_and_admits_its_holes():
    """Vast charges the BID (up to the machine's on-demand price), not dph_total, so the bid is what the
    realised number must use. A rental with no usable rate contributes 0 and is COUNTED — a total that hides
    holes is worse than one that admits them."""
    import congeneric_fanout_vast as fv
    doc = {"rentals": {"1": {"bid": 0.20, "dph": 0.9, "billed_min": 60},
                       "2": {"dph": 0.10, "billed_min": 30},
                       "3": {"billed_min": 600}}}
    total, n, rows, unpriced = fv.ledger_cost(doc)
    assert total == 0.25 and n == 3 and unpriced == 1
    assert [r["usd"] for r in rows] == [0.2, 0.05, 0.0]


def test_jobspec_exclusions_do_not_leak_between_units():
    """The fleet loop widens the exclusion set as it goes so 18 units land on 18 hosts. If that were applied
    to the shared module-level ResourceSpec, every already-built spec would change under it."""
    import congeneric_fanout_vast as fv
    units = cf.default_units()
    a = fv.build_jobspec(units[0], "b", "bkt", 0, exclude_machine_ids={"111"})
    b = fv.build_jobspec(units[1], "b", "bkt", 1, exclude_machine_ids={"111", "222"})
    assert a.resources.exclude_machine_ids == ("111",)
    assert b.resources.exclude_machine_ids == ("111", "222")
    assert fv.FANOUT_RES.exclude_machine_ids == ()


def test_cost_plan_and_band_are_derived_from_the_repriced_ladder():
    """The stale hand-typed constants (5-6 GPU-h at $0.12-0.25/hr) understated this tranche ~4x. Both are now
    derived, so the ~$36 in STRATEGY.md and the launcher's own print cannot disagree."""
    import vast_cost_model as vcm
    lo, hi = vcm.LADDER_REFERENCE_GPU_H[cf._FANOUT_LADDER_KEY]
    assert cf.UNIT_GPU_H == (lo / 19, hi / 19)
    assert 30 <= cf.cost_plan(19) <= 45
    band = cf.cost_estimate(19)
    assert band[0] <= cf.cost_plan(19) <= band[1]


def test_expected_iteration_rate_matches_the_measured_seconds_per_iteration():
    """The slow-host threshold has to be anchored to the MEASURED cmpd19/NR4A3 rate (three wave-1 hosts at
    12.76 / 13.70 / 14.42 s per HREX iteration), not to a round number. Wave 2's own host reproduced it:
    160 -> 260 committed iterations across ~23 min of sampling is ~261 iter/h."""
    import congeneric_fanout_vast as fv
    assert 250 <= fv.EXPECTED_ITER_PER_H <= 285


def test_terminus_gate_holds_until_a_ddg_exists():
    """The gate is what lets a cron fan out safely. If it could release with no result in S3 it would be
    launching 18 units into the unproven terminus it exists to guard."""
    import congeneric_fanout_vast as fv
    units = cf.default_units()

    class _S3:
        def __init__(self, have): self.have = set(have)
        def head_object(self, Bucket=None, Key=None):
            if Key not in self.have:
                raise KeyError(Key)
            return {}

    assert len(fv._pending(_S3([]), "bkt", units)) == 19
    assert len(fv._pending(_S3([cf.result_key(units[2], fv.RESULT_PREFIX)]), "bkt", units)) == 18


def test_an_exited_instance_does_not_hold_its_units_slot():
    """Vast teardown is two-layer: the container's EXIT trap halts GPU billing key-free, but only CI can
    DESTROY the instance, so an exited box lingers in the listing doing nothing. If the launcher counted it as
    occupying the unit, every relaunch would be a silent no-op — which is precisely what a preemption produces
    (container gone, checkpoint banked, corpse still carrying the label)."""
    import congeneric_fanout_vast as fv
    src = open(fv.__file__).read()
    assert '_TERMINAL = ("exited", "offline", "error")' in src
    # the slot count and the label set must BOTH filter, or one of them re-introduces the bug alone
    assert 'live_labels = {i.get("label") for i in live if (i.get("actual_status") or "") not in _TERMINAL}' \
        in src
    assert '_busy = [i for i in live if (i.get("actual_status") or "") not in _TERMINAL]' in src


def test_the_terminus_gate_cannot_deadlock_the_shakeout_unit():
    """THE GATE HOLDS BACK THE FAN-OUT, NOT THE UNIT THAT PROVES THE TERMINUS. A gate that returns outright
    while no ddg.json exists can never restart the one unit whose whole job is to produce that ddg.json — a
    cron would tick all night launching nothing. It must NARROW to the shakeout unit instead of returning."""
    import congeneric_fanout_vast as fv
    src = open(fv.__file__).read()
    gate = src[src.index("FANOUT_REQUIRE_PROVEN_TERMINUS"):]
    gate = gate[:gate.index("slots = max(")]
    assert "FANOUT_SHAKEOUT_UNIT" in gate, "the gate has no way to keep the shakeout unit alive"
    assert "todo = keep" in gate, "the gate discards rather than narrows"
    # Exactly ONE executable `return` may remain in the gate, and it is the one guarded by a MISSING
    # shakeout name. Comments are stripped first: the block explains the deadlock in prose, and matching
    # those words would make this assertion pass or fail on the wording rather than on the code.
    code = [ln for ln in gate.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert sum(1 for ln in code if ln.strip() == "return") == 1


# ================================================================= INTERNAL CALL ARITY
# LANE 21, 2026-07-26. `mode_launch` called `_lprint(msg, flush=True)`. `_lprint` is not `print` — it takes
# one argument — so the call raised TypeError on the FIRST SUCCESSFUL SUBMISSION and nowhere else: the smoke
# path, the dry path and every no-op tick sail past it. Autoscale run 30226203566 rented Vast instance
# 45951628 and died on that line before the rental ledger entry, before `_save_ledger`, before
# `_arm_watchdog` and before the launch readout — a box billing while invisible to realised spend and to the
# watch list. Fanned 19 wide it would have submitted one unit per tick, none ledgered, none watched.
#
# The general defect is a call to a MODULE-LOCAL helper that does not match its signature and is only
# reachable when money is being spent. That is statically decidable, so it is decided here rather than in
# production: every call in these modules to a function they define themselves is bound against the real
# signature. Positional arguments are only counted (values are irrelevant to arity); *args/**kwargs callees
# accept anything, as they should.
def _arity_violations(mod):
    import ast
    import inspect
    src = inspect.getsource(mod)
    tree = ast.parse(src)
    defs = {n.name: n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    bad = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        target = getattr(mod, node.func.id, None)
        if node.func.id not in defs or not callable(target):
            continue
        if any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords):
            continue                                   # f(*a) / f(**kw) — arity is not static
        try:
            sig = inspect.signature(target)
        except (TypeError, ValueError):
            continue
        try:
            sig.bind(*[None] * len(node.args), **{k.arg: None for k in node.keywords})
        except TypeError as e:
            bad.append(f"line {node.lineno}: {node.func.id}(...) does not match {node.func.id}{sig} — {e}")
    return bad


def test_every_internal_call_in_the_vast_launcher_matches_its_signature():
    import congeneric_fanout_vast as cfv
    bad = _arity_violations(cfv)
    assert not bad, "congeneric_fanout_vast.py:\n  " + "\n  ".join(bad)


def test_every_internal_call_in_the_pure_core_matches_its_signature():
    import congeneric_fanout as cf
    bad = _arity_violations(cf)
    assert not bad, "congeneric_fanout.py:\n  " + "\n  ".join(bad)


def test_the_arity_check_actually_catches_the_bug_it_was_written_for():
    """A guard that cannot fail is not a guard. Reproduce the exact 2026-07-26 defect in a throwaway module
    and assert the checker names it."""
    import ast
    import inspect
    import types
    mod = types.ModuleType("shim")
    src = ("def _lprint(msg):\n    print(msg, flush=True)\n\n"
           "def mode_launch():\n    _lprint('x', flush=True)\n")
    exec(compile(src, "shim", "exec"), mod.__dict__)
    mod.__dict__["__source__"] = src
    orig = inspect.getsource
    try:
        inspect.getsource = lambda m: src if m is mod else orig(m)
        ast.parse(src)                                   # sanity: the shim is valid python
        bad = _arity_violations(mod)
    finally:
        inspect.getsource = orig
    assert len(bad) == 1 and "_lprint" in bad[0] and "flush" in bad[0], bad


# ================================================================= THE REAP MODE'S REFUSALS
# `reap` destroys a host AND writes a permanent machine blacklist. `stop`'s blank-means-everything default is
# already a documented footgun on a shared Vast account; a mode that also blacklists must not inherit it.
def _reap_env(**kw):
    import os
    keep = {k: os.environ.get(k) for k in
            ("REAP", "DIAG_UNIT", "FANOUT_ONLY", "REAP_REASON", "VAST_API_KEY", "VAST_CKPT_BUCKET")}
    for k, v in kw.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    return keep


def _reap_restore(keep):
    import os
    for k, v in keep.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_reap_refuses_a_blank_selector_because_blank_would_condemn_the_whole_fleet():
    import pytest
    import congeneric_fanout_vast as cfv
    keep = _reap_env(VAST_API_KEY="x", DIAG_UNIT="", FANOUT_ONLY="", REAP_REASON="anything")
    try:
        with pytest.raises(SystemExit) as e:
            cfv.mode_reap()
        assert "blank selector" in str(e.value)
    finally:
        _reap_restore(keep)


def test_reap_refuses_without_a_recorded_reason():
    """An exclusion with no cause is a machine nobody can ever justify un-excluding."""
    import pytest
    import congeneric_fanout_vast as cfv
    keep = _reap_env(VAST_API_KEY="x", DIAG_UNIT="45938720", FANOUT_ONLY=None, REAP_REASON="")
    try:
        with pytest.raises(SystemExit) as e:
            cfv.mode_reap()
        assert "REAP_REASON is required" in str(e.value)
    finally:
        _reap_restore(keep)


def test_reap_refuses_without_a_vast_key_rather_than_reporting_success():
    import pytest
    import congeneric_fanout_vast as cfv
    keep = _reap_env(VAST_API_KEY=None, DIAG_UNIT="45938720", REAP_REASON="why")
    try:
        with pytest.raises(SystemExit) as e:
            cfv.mode_reap()
        assert "VAST_API_KEY required" in str(e.value)
    finally:
        _reap_restore(keep)


def test_reap_is_wired_into_the_launcher_mode_table_and_the_workflow():
    import yaml
    import congeneric_fanout_vast as cfv
    assert "REAP" in [flag for flag, _fn in cfv._MODES]
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))), ".github/workflows/fusion-cpu-extras.yml")) as fh:
        wf = yaml.safe_load(fh)
    # PyYAML resolves a bare `on:` key to the BOOLEAN True (YAML 1.1 truthy), not the string "on".
    trig = wf.get("on", wf.get(True))
    opts = trig["workflow_dispatch"]["inputs"]["fanout_mode"]["options"]
    assert "reap" in opts, opts
    env = wf["jobs"]["step1_fanout"]["env"]
    assert "REAP" in env and "REAP_REASON" in env
