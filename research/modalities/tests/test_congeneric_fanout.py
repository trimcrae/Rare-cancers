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


# ================================================================= THE $/ns MARKET GUARD
# CLAUDE.md §6 (trimcrae, 2026-07-26): "A THIN, EXPENSIVE MARKET IS A REASON TO PAUSE, NOT TO PAY … I'd rather
# pause until availability opens than pay double per ns." Measured that night: 5 offers against a ~23 baseline,
# min_floor $0.200/hr, median_floor $0.333/hr, hours after this lane rented at $0.048-$0.139. The exposure is
# the 18-edge release, which fires AUTOMATICALLY on the shakeout's ddg.json — at the median floor the tranche
# prices at ~$87 against the $15-80 that was authorised.
def test_the_basis_is_derived_from_the_ladder_and_matches_what_good_hosts_actually_paid():
    """The basis is the rung's own plan rate converted to $/ns. Independent check: tonight's good hosts ran
    ~$0.0043/ns, and the scorer prices a $0.12 4090 at $0.004355 — the derivation is not free-floating."""
    import congeneric_fanout as cf
    basis = cf.basis_usd_per_ns()
    assert 0.004 < basis < 0.005, basis
    assert abs(basis - 0.0043) < 0.0006


def test_the_ceiling_is_the_rungs_own_authorised_band_top_not_a_typed_multiple():
    import congeneric_fanout as cf
    assert cf.market_ceiling_usd(19) == cf.cost_estimate(19)[1]
    # ...and it lands where trimcrae's "double per ns" phrasing does, which is a check, not a coincidence
    assert 2.0 <= cf.market_ceiling_usd(19) / cf.cost_plan(19) <= 2.5


def test_a_bad_market_HOLDS_and_reproduces_the_87_dollar_number():
    """Tonight's median floor, $0.333/hr on a 4090, is the case the rule was written for."""
    import congeneric_fanout as cf
    import vast_cost_model as vcm
    upn = 0.333 / vcm.REFERENCE_NS_PER_H
    ok, projected, ceiling, ratio = cf.market_verdict(upn, 19)
    assert ok is False
    assert 84 <= projected <= 90, projected          # the ~$87 in the rule's own evidence
    assert projected > ceiling
    assert ratio > 2.0, ratio


def test_a_good_market_LAUNCHES():
    """The guard must not be so tight that a normal board cannot clear it — a ceiling nobody can clear is
    one of the two failure modes the rule names."""
    import congeneric_fanout as cf
    ok, projected, ceiling, ratio = cf.market_verdict(0.0043, 19)
    assert ok is True and projected < ceiling and ratio < 1.05
    # the current (worse but authorised) host still passes: $63 < $80 is inside the band, so refusing it
    # would be the guard inventing an authorisation of its own
    ok2, proj2, _c, _r = cf.market_verdict(0.0077, 19)
    assert ok2 is True and 55 < proj2 < 70


def test_an_unpriceable_board_holds_rather_than_guessing():
    import congeneric_fanout as cf
    ok, projected, ceiling, ratio = cf.market_verdict(None, 19)
    assert ok is False and projected is None and ratio is None and ceiling > 0


def test_the_gate_scales_with_the_remaining_tranche_not_the_whole_map():
    """A partial tranche must be judged against its own share of the band, or the guard waves through
    nineteen expensive units one at a time."""
    import congeneric_fanout as cf
    import vast_cost_model as vcm
    bad = 0.333 / vcm.REFERENCE_NS_PER_H
    for n in (3, 8, 19):
        assert cf.market_verdict(bad, n)[0] is False, n
        assert cf.market_verdict(0.0043, n)[0] is True, n


def test_a_fleet_is_priced_over_the_N_CHEAPEST_offers_not_the_single_best():
    """Pricing a 19-host fleet off the one cheapest host would flatter a thin board exactly when thinness is
    what we are trying to detect. `market_snapshot` takes the mean over the N cheapest."""
    import gpu_backend as gb
    from gpu_backend import ResourceSpec
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=80, interruptible=True)

    def mk(name, bid):
        return {"gpu_name": name, "min_bid": bid, "num_gpus": 1, "gpu_ram": 24576, "rentable": True,
                "storage_cost": 0.1, "cuda_max_good": 13.0, "dph_total": 0.9}
    offers = [mk("RTX 4090", 0.05)] + [mk("RTX 3090", 0.30)] * 4
    measured, capable = gb.rank_offers_by_usd_per_ns(offers, res)
    assert len(capable) == 5 and len(measured) == 5
    assert measured[0][2]["gpu_name"] == "RTX 4090"          # ranking is by $/ns, cheapest first
    mean_of_all = sum(m[0] for m in measured) / len(measured)
    assert mean_of_all > measured[0][0] * 2, "the mean must not be flattered by the single best host"


def test_the_ranking_extraction_did_not_change_what_gets_rented():
    """rank_offers_by_usd_per_ns was extracted OUT of _select_cheapest_offer so the guard and the renting
    path share one filter. The renting path's answer must be unchanged."""
    import gpu_backend as gb
    from gpu_backend import ResourceSpec
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=80, interruptible=True)

    def mk(name, bid):
        return {"gpu_name": name, "min_bid": bid, "num_gpus": 1, "gpu_ram": 24576, "rentable": True,
                "storage_cost": 0.1, "cuda_max_good": 13.0, "dph_total": 0.9}
    offers = [mk("RTX 3090", 0.10), mk("RTX 4090", 0.12), mk("RTX 4080", 0.15)]
    chosen = gb._select_cheapest_offer(offers, res)
    measured, _c = gb.rank_offers_by_usd_per_ns(offers, res)
    assert chosen is measured[0][2] and chosen["gpu_name"] == "RTX 4090"
    assert gb._select_cheapest_offer([], res) is None
    assert gb.rank_offers_by_usd_per_ns([], res) == ([], [])


def test_a_hold_is_VISIBLE_and_never_silent():
    """The rule's first named failure mode: 'a fleet that never launches looks identical to one that
    finished'. Every hold must reach the readout, the S3 state and a committed file, each with the snapshot."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    i = src.index("def market_gate(")
    body = src[i:src.index("\ndef mode_launch(")]
    assert "_lprint" in body, "a hold must reach the committed launch readout"
    assert "step1-fanout-market-hold.json" in body, "a hold must leave a committed snapshot file"
    assert "put_object" in body, "a hold must persist state so the NEXT tick can time the escalation"
    for field in ("board_depth", "offers_priced", "spend_authorised_now_usd",
                  "ceiling_for_that_spend_usd", "unit_usd_per_ns_ceiling", "binding_gate"):
        assert field in body, f"the snapshot must carry {field}"
    # ★ A PARTIAL LAUNCH IS WHERE "never silent" is easiest to break: a tick that launches 5 of 19 and says
    # nothing about the 14 is exactly the failure §6 names. Both halves must always be reported.
    for field in ("n_launching_now", "n_held", "held_reason"):
        assert field in body, f"a partial launch must record {field}"
    assert "HELD" in body and "LAUNCHING NOW" in body, "both halves must reach the readout"


def test_the_hold_readout_is_committed_by_both_launching_workflows():
    """A file written into a runner and never committed is a silent hold with extra steps."""
    wf_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))), ".github/workflows")
    for name in ("step1-fanout-autoscale.yml", "fusion-cpu-extras.yml"):
        with open(os.path.join(wf_dir, name)) as fh:
            assert "step1-fanout-market-hold.json" in fh.read(), name


def test_an_indefinite_hold_escalates_rather_than_idling_forever():
    """The rule's second named failure mode: 'a ceiling nobody can clear turns into an idle night'. The guard
    never buys in on its own — it hands the decision over, via a job failure, which is the alert path that
    does not need an agent awake."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    assert "MARKET_HOLD_ESCALATE_H" in src
    body = src[src.index("def market_gate("):src.index("\ndef mode_launch(")]
    assert "::error title=" in body, "the escalation must be a GitHub error annotation"
    assert "first_held_utc" in body, "escalation must be timed from the FIRST hold, not this tick"
    assert "price_is_binding and held_h >=" in body, \
        "the escalation must fire ONLY when price is the binding constraint"
    # and the escalation must actually fail the process
    assert "raise SystemExit(2)" in src and "_MARKET_HOLD_ESCALATED" in src


def test_a_single_unit_launch_is_gated_too_just_on_a_different_ceiling():
    """★ RETIRED AND REPLACED (2026-07-27). This test used to assert the OPPOSITE — that only a fleet is
    gated — pinning CLAUDE.md §6's original last line, "a single unit already running is not affected".

    That exemption was cut on the wrong axis and trimcrae caught it: *"Why are there so many high $/ns rows
    that are flagged but you're still paying for them?"* A resume onto a NEW HOST is a NEW PURCHASE — the old
    host is gone and the market is quoted afresh — so the shakeout unit's overnight relaunches all went
    unpriced at 1.76x the ladder basis, `⚠ DRIFT` on the board, while the fan-out at 2.05x was refused.

    The right axis is "would waiting lose work?", and for a checkpointed unit it would not. So BOTH paths are
    gated; only the CEILING differs — a tranche gets its authorised dollar band, a single host gets the rate
    (the drift line), because a resume re-enters a leg at an unknown fraction of its work and any dollar
    projection for it would be the whole unit's cost."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    launch = src[src.index("def mode_launch("):]
    assert "relaunch_market_gate" in launch, "the single-host path must consult the $/ns gate"
    assert "elif len(batch) > 1:" in launch, "the FLEET keeps its own dollar-band ceiling"
    # No path may reach the rent loop unpriced: the belt now covers every non-empty batch, not just a fleet.
    assert "if batch and not _MARKET_GUARD_RAN:" in launch


def test_the_guard_cannot_be_skipped_by_a_future_refactor():
    """Belt as well as braces: a multi-unit batch that reaches the rent path without having been priced must
    HOLD, not rent. By CLAUDE.md §6 an unpriced fan-out is a bug, and the safe failure is to refuse."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    launch = src[src.index("def mode_launch("):]
    i_belt = launch.index("not _MARKET_GUARD_RAN")
    i_rent = launch.index("backend.submit(spec)")
    assert i_belt < i_rent, "the belt must sit before anything is rented"


# ================================================================= THE CREDENTIAL PRE-FLIGHT
# 2026-07-27: instance 45996071 was rented healthy and cheap, resumed the shakeout unit's complex leg to
# production@2000, and then spent over an hour boot -> openfe import -> nvidia-smi -> `InvalidAccessKeyId` on
# the staging copy -> `Killed`, on a ~15-60 s loop, at $0.2497/hr with 0 % GPU. Every existing guard passed
# it: the $/ns gate prices the board (the board was fine), the starved-host exclusion needs commits to compare
# (a host that dies before `s3 cp` produces none), and `phase.txt` still read `leg-solvent-running` because
# the phase marker is only written forward. A rental whose credential cannot read the staged inputs is
# worthless at any price, so the launcher asks that question FIRST.

def test_credential_preflight_fails_closed_on_every_unusable_outcome():
    """No credential, a rejected credential, and an empty staging prefix must ALL hold — and a resolver that
    itself blows up must hold too, because "we could not check" is not "it works"."""
    import congeneric_fanout_vast as cfv

    class _Boom:
        def list_objects_v2(self, **kw):
            err = Exception("nope")
            err.response = {"Error": {"Code": "InvalidAccessKeyId"}}
            raise err

    class _Empty:
        def list_objects_v2(self, **kw):
            return {"KeyCount": 0}

    class _Ok:
        def list_objects_v2(self, **kw):
            return {"KeyCount": 1}

    import gpu_backend
    real_env, real_mode = gpu_backend._object_store_env, gpu_backend.object_store_cred_mode
    import boto3
    real_client = boto3.client
    try:
        gpu_backend.object_store_cred_mode = lambda *a, **k: "inherited"

        gpu_backend._object_store_env = lambda *a, **k: {}
        ok, why = cfv.object_store_preflight(bucket="b", prefix="p")
        assert not ok and "no object-store credential" in why, why

        gpu_backend._object_store_env = lambda *a, **k: {"AWS_ACCESS_KEY_ID": "AKIA_FAKE",
                                                         "AWS_SECRET_ACCESS_KEY": "sekrit"}
        boto3.client = lambda *a, **k: _Boom()
        ok, why = cfv.object_store_preflight(bucket="b", prefix="p")
        assert not ok and "InvalidAccessKeyId" in why, why
        # The probe must never leak the credential it was handed into the reason string.
        assert "AKIA_FAKE" not in why and "sekrit" not in why, why

        boto3.client = lambda *a, **k: _Empty()
        ok, why = cfv.object_store_preflight(bucket="b", prefix="p")
        assert not ok and "EMPTY" in why, why

        boto3.client = lambda *a, **k: _Ok()
        ok, why = cfv.object_store_preflight(bucket="b", prefix="p")
        assert ok, why
    finally:
        gpu_backend._object_store_env, gpu_backend.object_store_cred_mode = real_env, real_mode
        boto3.client = real_client


def test_credential_preflight_tests_the_FORWARDED_credential_not_the_runners():
    """The whole point: on the day this was written the CI runner's own key listed the bucket fine minutes
    either side of the host's rejection, so a probe built on `os.environ` would have passed while every
    rental crash-looped. It must resolve through `gpu_backend._object_store_env`."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    fn = src[src.index("def object_store_preflight("):src.index("def mode_launch(")]
    assert "_object_store_env" in fn, "the probe must test the credential the HOST is given"
    assert "os.environ.get(\"AWS_ACCESS_KEY_ID\")" not in fn, "must not fall back to the runner's own key"


def test_credential_preflight_runs_before_anything_is_rented():
    """Ordering is the guarantee. It must sit before the price gate (cheaper question, decided first) and,
    above all, before the rent call."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    launch = src[src.index("def mode_launch("):]
    i_pre = launch.index("object_store_preflight()")
    i_price = launch.index("THE $/ns MARKET GUARD")
    i_rent = launch.index("backend.submit(spec)")
    assert i_pre < i_price < i_rent, "pre-flight -> price gate -> rent"


# ================================================================= PER-UNIT PLACEMENT
# trimcrae, 2026-07-27: *"The fanout fleet doesn't all have to run at the same time. If 5 GPUs are cheap
# enough and the rest aren't, only run 5."* The gate used to take a MEAN over the N cheapest offers and hold
# all-or-nothing, so cheap capacity was refused because expensive capacity existed beside it.

def _mult(u):
    import congeneric_fanout as cf
    return u / cf.basis_usd_per_ns()


def test_two_cheap_among_eight_expensive_launches_two_and_holds_the_rest():
    """The board that prompted the redesign, in miniature. The old mean would have refused all ten."""
    import congeneric_fanout as cf
    ceil = cf.unit_usd_per_ns_ceiling()
    cheap = [ceil * 0.75, ceil * 0.8]
    dear = [ceil * m for m in (1.5, 1.6, 1.9, 2.0, 2.1, 2.4, 2.7, 3.1)]
    n, placed, why = cf.place_units(sorted(cheap + dear), 18)
    assert n == 2, (n, placed)
    assert placed == sorted(cheap)
    assert why is None
    # and the mean over all ten would have failed, which is the whole point
    mean = sum(cheap + dear) / 10
    assert mean > ceil, "the fixture must reproduce the mean-drags-it-over failure"


def test_a_board_where_nothing_clears_launches_zero_and_still_says_why():
    import congeneric_fanout as cf
    ceil = cf.unit_usd_per_ns_ceiling()
    n, placed, why = cf.place_units([ceil * 1.2, ceil * 5], 18)
    assert n == 0 and placed == []
    assert why and "cheapest offer" in why and "authorised" in why, why


def test_a_board_where_everything_clears_launches_everything():
    import congeneric_fanout as cf
    ceil = cf.unit_usd_per_ns_ceiling()
    n, placed, why = cf.place_units([ceil * 0.5] * 6, 6)
    assert n == 6 and why is None
    # never more units than offers: one unit per host, because two on one host contend for its GPU
    assert cf.place_units([ceil * 0.5] * 3, 19)[0] == 3


def test_an_empty_or_unpriceable_board_is_a_hold_not_a_guess():
    import congeneric_fanout as cf
    n, placed, why = cf.place_units([], 5)
    assert n == 0 and why and "unpriceable" in why


def test_the_per_unit_ceiling_is_derived_from_the_tranche_ceiling_not_typed():
    """★ The identity that makes per-unit placement a re-expression of the authorisation rather than a
    loosening of it: both sides of market_verdict are linear in n, so the tranche test WAS a per-unit test."""
    import congeneric_fanout as cf
    ceil = cf.unit_usd_per_ns_ceiling()
    assert abs(ceil - cf.market_ceiling_usd(1) / cf.reference_ns_per_unit()) < 1e-12
    for n in (1, 3, 5, 18, 19):
        # a unit priced just under the per-unit ceiling keeps ANY tranche size inside its own dollar band
        ok, projected, ceiling, _r = cf.market_verdict(ceil * 0.99, n)
        assert ok, (n, projected, ceiling)
        assert not cf.market_verdict(ceil * 1.05, n)[0], n
    src = open(cf.__file__).read()
    fn = src[src.index("def unit_usd_per_ns_ceiling("):src.index("def place_units(")]
    assert "market_ceiling_usd(1)" in fn, "must be DERIVED from the rung's own band, never typed"


def test_a_terminus_blocked_hold_does_not_escalate_on_price():
    """★ THE CRY-WOLF FIX (2026-07-27). This escalated 'held 9.9 h on a bad market' while the terminus was
    unmet — a window in which the 18 units could not have launched at any price, so price was never what
    stopped them. An alert that fires on a hold price did not cause trains everyone to ignore the alerts
    that matter."""
    import congeneric_fanout_vast as cfv
    # the pure half: which gate is binding
    assert cfv.binding_gate((("terminus", False, "no ddg.json"),)) == ("terminus", "no ddg.json")
    assert cfv.binding_gate((("terminus", True, "ok"), ("pre-flight", True, "ok"))) is None
    assert cfv.binding_gate(())is None
    # first shut gate wins the name, and a later clear one cannot mask it
    assert cfv.binding_gate((("terminus", False, "a"), ("pre-flight", True, "b")))[0] == "terminus"

    src = open(cfv.__file__).read()
    body = src[src.index("def market_gate("):src.index("\ndef object_store_preflight(")]
    # the clock must be CLEARED, not merely unread, while another gate is shut
    assert "price_is_binding = (blocking is None)" in body
    assert 'else (_utcnow() if price_is_binding else None)' in body, \
        "first_held_utc must be cleared while price is not binding, not left ticking"
    # with per-unit launching, 'price is binding' means NOT ONE unit could be placed
    assert "n_place == 0" in body, "a tick that placed some units is not a price-bound tick"


def test_the_terminus_is_passed_to_the_price_gate_from_the_launcher():
    """The false alarm was possible because the terminus is enforced only under
    FANOUT_REQUIRE_PROVEN_TERMINUS=1 while the hold clock in S3 is shared by every entry point."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    launch = src[src.index("def mode_launch("):]
    assert "terminus_proven = done > 0" in launch, "computed unconditionally, at zero extra S3 cost"
    i_term = launch.index("terminus_proven = done > 0")
    i_gate = launch.index("market_gate(")
    assert i_term < i_gate, "the terminus must be known before the price gate is consulted"
    assert '("terminus", terminus_proven' in launch, "and actually handed to it"


# ================================================================= THE GATE MUST BIND ON WHAT IS BOUGHT
# 2026-07-27, rate-forensics lane: the market gate takes its OWN board snapshot and decides; `submit` then
# calls `_select_cheapest_offer` against a SECOND, independently-fetched board. Measured that morning: the
# gate cleared on machine 11892 at 1.388x basis and the launcher rented machine 55559 at 1.479x. Both were
# under the line so nothing was lost, but the number in front of the decision was not the number paid — the
# same class as the quote-vs-billed defect. It bites hardest under a PER-UNIT gate, whose whole premise is
# "buy from the top of the ranking", because the top is exactly where a resources_unavailable sends us to a
# fallback that is by definition worse than what was approved.

def _capped_res(cap):
    import gpu_backend as gb
    return gb.ResourceSpec(gpu="rtx4090", min_vram_gb=16, min_cuda=13.0, max_usd_per_ns=cap)


def _offer(name, bid, mid, storage=0.1):
    return {"gpu_name": name, "min_bid": bid, "num_gpus": 1, "gpu_ram": 24576, "rentable": True,
            "storage_cost": storage, "cuda_max_good": 13.0, "dph_total": bid, "machine_id": mid,
            "id": mid, "reliability2": 0.99}


def test_the_price_ceiling_travels_with_the_spec_into_selection():
    """A cap on the spec must remove non-clearing offers from the RANKING, so the launcher cannot buy what
    the gate refused — including on the fallback after a capacity refusal."""
    import gpu_backend as gb
    offers = [_offer("RTX 4090", 0.12, 1), _offer("RTX 4090", 0.90, 2)]
    uncapped, _c = gb.rank_offers_by_usd_per_ns(offers, _capped_res(None))
    assert len(uncapped) == 2, "with no cap the gate must SEE the expensive offer in order to report it"
    cap = uncapped[0][0] * 1.05                      # admits the cheap one only
    capped, _c2 = gb.rank_offers_by_usd_per_ns(offers, _capped_res(cap))
    assert [o["machine_id"] for _u, _p, o in capped] == [1]
    assert gb._select_cheapest_offer(offers, _capped_res(cap))["machine_id"] == 1


def test_a_cap_that_nothing_clears_refuses_rather_than_falling_back():
    """The fallback exists for a board where nothing is benched. Under a cap it must be unreachable: taking
    an unpriceable card would wave through exactly the spend the cap refuses."""
    import gpu_backend as gb
    offers = [_offer("RTX 4090", 0.90, 1), _offer("RTX 4090", 1.20, 2)]
    assert gb._select_cheapest_offer(offers, _capped_res(1e-9)) is None
    # unbenched cards must not sneak through the cap either
    assert gb._select_cheapest_offer([_offer("Totally Unknown GPU", 0.01, 3)], _capped_res(1e-9)) is None
    # ...but with NO cap the unbenched fallback still works, which is the behaviour it is there for
    assert gb._select_cheapest_offer([_offer("Totally Unknown GPU", 0.01, 3)], _capped_res(None)) is not None


def test_the_fanout_actually_sets_the_cap_on_every_job_it_submits():
    import congeneric_fanout as cf
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    fn = src[src.index("def build_jobspec("):src.index("# ---- S3 helpers")]
    assert "max_usd_per_ns=_cf.unit_usd_per_ns_ceiling()" in fn, \
        "every submitted spec must carry the same ceiling the gate cleared on"
    assert cf.unit_usd_per_ns_ceiling() > 0


def test_the_readout_reports_the_rate_ACTUALLY_rented_not_the_one_that_cleared():
    """A readout quoting the cleared figure describes a purchase that did not happen. And it must be priced
    off dph_total (what Vast bills, storage included), never the quote — forensics measured quotes as
    understating the true rate by 9.05-26.41 % with no constant offset."""
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    fn = src[src.index("def _rented_usd_per_ns("):src.index("def mode_launch(")]
    assert 'handle.extra.get("dph")' in fn, "must price the offer we got, off the billed rate"
    assert 'handle.extra.get("min_bid")' not in fn and 'extra["min_bid"]' not in fn, \
        "must NOT be derived from the quote"
    loop = src[src.index("for u in batch:"):]
    assert "_rented_usd_per_ns(h)" in loop and "RENTED AT" in loop

    class _H:
        extra = {"dph": 0.1384, "gpu_name": "RTX 4090"}
    upn, cell = cfv._rented_usd_per_ns(_H())
    assert upn and "x basis" in cell and "ABOVE THE" not in cell, cell

    class _Unknown:
        extra = {"dph": 0.5, "gpu_name": "Totally Unknown GPU"}
    upn2, cell2 = cfv._rented_usd_per_ns(_Unknown())
    assert upn2 is None and "UNKNOWN" in cell2, "an ungradeable rental must say so, not invent a figure"
