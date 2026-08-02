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


def test_signed_terms_label_each_edge_with_its_OWN_ddg():
    """The residual is order-independent, so a mislabelled `signed_terms` sums correctly while telling the
    reader the wrong edge carried the anomaly. That shipped: the walk reorders the loop and the values were
    zipped against the DECLARATION order. Pin the pairing, not just the sum."""
    ddg = _closed_ddg()
    ddg["e_cw_ev_5oh__cw_ev_5opropargyl"] += 4.0          # make one edge distinguishable
    res = {c["cycle_id"]: c for c in cf.cycle_closure(ddg)}
    edges = {e["edge_id"]: e for e in cf.load_map()["edges"]}
    for cyc in res.values():
        terms = cyc.get("signed_terms")
        if not terms:
            continue
        # every id is a real edge of that cycle, quoted at its own magnitude and no other edge's
        for eid, v in terms.items():
            assert eid in edges, eid
            assert abs(abs(v) - abs(round(ddg[eid], 3))) < 1e-6, (eid, v, ddg[eid])
        assert abs(sum(terms.values()) - cyc["sum_kcal"]) < 1e-6


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
    # nr4a3-program-map.md's ladder entry). plan() correctly reports the corrected band, so the TEST was the thing
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
    derived, so the ~$36 in nr4a3-program-map.md and the launcher's own print cannot disagree."""
    import vast_cost_model as vcm
    lo, hi = vcm.LADDER_REFERENCE_GPU_H[cf._FANOUT_LADDER_KEY]
    assert cf.UNIT_GPU_H == (lo / 19, hi / 19)
    # Re-derived 2026-07-27 when the throughput table was re-anchored and the ladder regenerated
    # (pricing.md Appendix T): the GPU-hours are unchanged, the $/reference-GPU-hour fell.
    assert 25 <= cf.cost_plan(19) <= 45
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
    # ⚠ SLICE FROM THE `if`, NOT FROM THE FIRST MENTION OF THE NAME. This used to start at the first
    # occurrence anywhere in the file — which is inside `market_gate`'s DOCSTRING — so the "exactly one
    # return" assertion below was really counting the returns of market_gate's tail, object_store_preflight,
    # _rented_usd_per_ns AND the first half of mode_launch. It passed by luck, and broke the moment a
    # placement decision was recorded before the gate. The gate is the `if`.
    gate = src[src.index('if os.environ.get("FANOUT_REQUIRE_PROVEN_TERMINUS")'):]
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
    """The basis is the rung's own plan rate converted to $/ns, and the check is that it is not free-floating:
    it must equal what the scorer charges for a representative reference-card offer at the plan rate.

    ⚠ The band was `0.004 < basis < 0.005`, anchored on "tonight's good hosts ran ~$0.0043/ns". That was an
    OBSERVATION of one night, and on 2026-07-27 the basis moved to ~$0.0034 for two reasons the observation
    cannot see: the reference card's throughput was re-measured, and the widened table admitted 97 more
    gradeable offers so the best-10 mean rate fell. Pinning a derived quantity against a stale observation
    would have forced the correction to be reverted. The IDENTITY below is what must hold."""
    import congeneric_fanout as cf
    import vast_cost_model as _vcm
    basis = cf.basis_usd_per_ns()
    assert basis == cf._usd_per_ref_gpu_h()[1] / _vcm.REFERENCE_NS_PER_H
    assert 0.001 < basis < 0.02, basis
    # The scorer must charge the same thing for a reference-card offer priced at the plan rate — that is the
    # non-free-floating check. (`abs(basis - 0.0043) < 0.0006` stood here, an observation of one night; the
    # 2026-07-27 re-anchoring moved the basis to ~$0.0034 and a stale observation must not veto a correction.)
    assert abs(basis - cf._usd_per_ref_gpu_h()[1] / _vcm.REFERENCE_NS_PER_H) < 1e-12


def test_the_ceiling_is_the_rungs_own_authorised_band_top_not_a_typed_multiple():
    import congeneric_fanout as cf
    assert cf.market_ceiling_usd(19) == cf.cost_estimate(19)[1]
    # ...and it lands where trimcrae's "double per ns" phrasing does, which is a check, not a coincidence
    # The band top / plan ratio is itself derived from the market snapshot's best-to-median spread, so it
    # drifts a little on each repricing; 2.52 after the 2026-07-27 reprice. What matters is that the ceiling
    # is meaningfully above the plan and nowhere near a typed multiple.
    assert 2.0 <= cf.market_ceiling_usd(19) / cf.cost_plan(19) <= 2.7


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
    # Expressed RELATIVE TO THE BASIS rather than as a typed $/ns: a "good market" is one at the plan rate,
    # and a typed 0.0043 silently became 1.26x basis when the basis was re-anchored on 2026-07-27.
    good = cf.basis_usd_per_ns()
    ok, projected, ceiling, ratio = cf.market_verdict(good, 19)
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
    # ★ THE WRITE MOVED TO ONE WRITER (2026-07-27) — assert the writer is REACHED and that the writer does
    # both halves. This used to look for `put_object` literally inside `market_gate`, which forbade exactly
    # the refactor the staleness incident required: `market_gate` was the ONLY writer of the snapshot, so
    # every launcher path that never reached pricing left the artifact carrying an old timestamp.
    assert "_write_market_hold(" in body, "a hold must be routed through the single snapshot writer"
    writer = src[src.index("def _write_market_hold("):src.index("def record_no_placement(")]
    assert "step1-fanout-market-hold.json" in writer, "a hold must leave a committed snapshot file"
    assert "put_object" in writer, "a hold must persist state so the NEXT tick can time the escalation"
    for field in ("board_depth", "offers_priced", "spend_authorised_now_usd",
                  "ceiling_for_that_spend_usd", "unit_usd_per_ns_ceiling", "binding_gate"):
        assert field in body, f"the snapshot must carry {field}"
    # ★ A PARTIAL LAUNCH IS WHERE "never silent" is easiest to break: a tick that launches 5 of 19 and says
    # nothing about the 14 is exactly the failure §6 names. Both halves must always be reported.
    for field in ("n_launching_now", "n_held", "held_reason"):
        assert field in body, f"a partial launch must record {field}"
    assert "HELD" in body and "LAUNCHING NOW" in body, "both halves must reach the readout"


def test_every_exit_from_mode_launch_records_a_named_placement_decision():
    """★★ THE 1 H 47 M REGRESSION GUARD (2026-07-27, 12:44 PM -> 2:31 PM ET).

    `step1-fanout-market-hold.json` kept a 12:43 PM timestamp through SEVEN green ticks while the fleet
    decayed 11 -> 5 and ten checkpointed units sat with no host, because the artifact's only writer was the
    price gate — a code path most no-op ticks never reach. "We held on price", "there was nothing to place",
    "placement was switched off" and "the launch step never ran" were therefore indistinguishable, and the
    last of those was the truth for 1 h 47 m.

    So the invariant is not "holds are logged" but the strictly stronger *every* exit from `mode_launch`
    leaves a NAMED decision behind, and a stale `utc` can only ever mean the tick itself did not run.
    """
    import congeneric_fanout_vast as cfv
    src = open(cfv.__file__).read()
    body = src[src.index("def mode_launch("):src.index("\ndef mode_monitor(")]
    lines = body.splitlines()
    # Every `return`/`SystemExit` that leaves the launcher WITHOUT having rented must be preceded by a
    # decision record. Walk backwards from each exit to the nearest recorder or submit loop.
    unguarded = []
    for n, ln in enumerate(lines):
        s = ln.strip()
        if s != "return" and not s.startswith("raise SystemExit"):
            continue
        window = "\n".join(lines[max(0, n - 30):n])
        if "record_no_placement(" in window or "market_gate(" in window or "backend.submit" in window \
                or "rmg.gate(" in window:
            continue
        unguarded.append((n + 1, s))
    assert not unguarded, ("these exits from mode_launch leave no placement decision behind, so the "
                          f"snapshot goes stale and nobody can tell why nothing was placed: {unguarded}")
    for code in ("placement_disabled", "nothing_pending", "fleet_at_width", "terminus_hold",
                 "credential_hold", "cost_model_red", "measurement_failed", "price_hold", "placed"):
        assert code in cfv.PLACEMENT_DECISIONS, f"{code} must be a documented decision"
        assert code in src, f"{code} is documented but never actually recorded"


def test_the_launch_step_is_not_gated_on_a_null_prone_inputs_expression():
    """★★ THE ROOT CAUSE, PINNED (2026-07-27).

    Both money-spending steps were guarded by `if: ${{ github.event.inputs.release_fanout != '0' }}`. A
    `schedule:` event carries NO `inputs` context, so that operand is `null`; GitHub Actions casts both
    operands to a NUMBER when their types differ and `null` casts to `0`, making the condition `0 != 0` —
    FALSE. Every scheduled tick silently skipped the launch (3 of 3 that day, jobs API runs 30273407468,
    30285319719, 30292476003), while the SAME runs resolved `${{ …fleet_branch || '…' }}` to its fallback
    correctly — the observation that discriminates.

    The repair is not a better expression. A YAML `if:` decides with implicit coercion and leaves `skipped`
    as its only trace; the switch belongs in the launcher, which names and records what it decided.
    """
    import yaml
    wf = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))), ".github/workflows/step1-fanout-autoscale.yml")
    with open(wf) as fh:
        raw = fh.read()
    doc = yaml.safe_load(raw)
    steps = doc["jobs"]["tick"]["steps"]
    launch = [s for s in steps if s.get("env", {}).get("LAUNCH") == "1"]
    assert launch, "the tick must still have a launch step"
    for s in launch:
        cond = str(s.get("if", ""))
        assert "github.event.inputs" not in cond, (
            "the launch step must NOT be gated on the inputs context — it is null on a schedule and null "
            f"casts to 0, so `!= '0'` is FALSE and the step silently skips. Found: {cond!r}")
        assert "always()" in cond, ("the launch step must run on every tick so the market snapshot cannot "
                                    "go stale; the DECISION is the launcher's, not the YAML's")
        assert s["env"].get("FANOUT_PLACEMENT_ENABLED"), \
            "the resolved flag must be handed to the launcher rather than decided in YAML"


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
    assert "price_blocks_every_unit and held_h >=" in body, \
        "the escalation must fire ONLY when price is blocking EVERY unit"
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
    assert why and "cheapest offer" in why and "refused on the" in why, why


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


def test_the_DOLLAR_ceiling_is_derived_from_the_tranche_ceiling_not_typed():
    """★ The identity that makes per-unit placement a re-expression of the authorisation rather than a
    loosening of it: both sides of market_verdict are linear in n, so the tranche test WAS a per-unit test.
    Retained after trimcrae's 1.5x ruling because it is still what the DOLLAR ceiling means — the rate line
    binds on top of it, it does not replace it."""
    import congeneric_fanout as cf
    dollar = cf._unit_dollar_ceiling_usd_per_ns()
    assert abs(dollar - cf.market_ceiling_usd(1) / cf.reference_ns_per_unit()) < 1e-12
    for n in (1, 3, 5, 18, 19):
        # a unit priced just under the DOLLAR ceiling keeps ANY tranche size inside its own dollar band
        ok, projected, ceiling, _r = cf.market_verdict(dollar * 0.99, n)
        assert ok, (n, projected, ceiling)
        assert not cf.market_verdict(dollar * 1.05, n)[0], n
    src = open(cf.__file__).read()
    fn = src[src.index("def _unit_dollar_ceiling_usd_per_ns("):src.index("# ★★ THE DRIFT LINE IS THE BUY")]
    assert "market_ceiling_usd(1)" in fn, "must be DERIVED from the rung's own band, never typed"


def test_the_drift_line_IS_the_buy_line_and_binds_on_top_of_the_dollar_ceiling():
    """★ trimcrae, 2026-07-27: *"What's the point of tracking that if we don't act on it?"* A unit must clear
    BOTH. Today the rate line is the lower, so nothing that prints ⚠ DRIFT can be bought."""
    import congeneric_fanout as cf
    b = cf.basis_usd_per_ns()
    dollar, rate, eff, which = cf.unit_ceiling_components()
    # The rate line is the APPROVED ABSOLUTE $/ns (trimcrae, 2026-07-27 re-expression). It was
    # `1.5 * basis`; when the basis was corrected that expression silently changed the rule, so the invariant
    # is now the rate and the multiple is derived from it. Both forms must agree exactly.
    import inflight_usd_per_ns as _iu
    assert rate == _iu.APPROVED_USD_PER_NS, "the rate line IS the approved absolute rate"
    assert abs(rate - cf.drift_buy_line_x_basis() * b) < 1e-12, "and the multiple reproduces it"
    assert eff == min(dollar, rate), "a unit must clear BOTH constraints"
    assert cf.unit_usd_per_ns_ceiling() == eff
    # at today's basis the rate line is the binding one, and the readout must say so
    assert rate < dollar and "rate line" in which, (rate, dollar, which)
    # nothing at or above the LINE can be placed any more — expressed against the derived multiple, because
    # a typed 1.5x stopped being the line when the basis was corrected (2026-07-27 re-expression).
    x = cf.drift_buy_line_x_basis()
    assert cf.place_units([(x - 0.01) * b, (x + 0.01) * b, (x + 0.5) * b], 5)[0] == 1
    # and the refusal names which constraint it hit
    assert "rate line" in cf.place_units([(x + 0.1) * b], 5)[2]


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
    assert "price_blocks_every_unit = (blocking is None)" in body
    assert 'else (_utcnow() if price_blocks_every_unit else None)' in body, \
        "first_held_utc must be cleared while price is not blocking every unit, not left ticking"
    # ★ AND THE RECORD MUST NOT READ AS A SELF-CONTRADICTION (2026-07-27). A snapshot carrying
    # `binding_gate: "price"` beside `price_is_binding: false` was two DIFFERENT questions answered
    # correctly under names that claimed to be one question. The scope field is what disambiguates them.
    assert "binding_gate_scope" in body, \
        "binding_gate must say how many units its verdict covers, or it reads as contradicting the " \
        "fleet-level escalation flag"
    # The superseded key must not be WRITTEN again (reading a previous tick's copy is how the hold clock
    # survives the rename, so `prev.get("price_is_binding")` is legitimate and deliberately still allowed).
    assert 'doc["price_is_binding"]' not in body, \
        "the superseded key must not be emitted into the snapshot again"
    assert 'prev.get("price_is_binding")' in body, \
        "a rename must not silently restart the hold clock — read the old key as a fallback"
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


def test_the_dollar_ceiling_branch_is_REACHABLE_not_just_written():
    """★ `unit_ceiling_components()` returns the derived dollar ceiling as binding whenever it is the lower
    of the two. Today the rate line is lower, so that branch is dormant — and a dormant branch in the gate
    that decides purchases is not somewhere to discover a bug. A repricing that pushed the rung's band top
    below 1.5x basis would make it live, so it is exercised here against a stubbed band."""
    import congeneric_fanout as cf
    b = cf.basis_usd_per_ns()
    real = cf.market_ceiling_usd
    try:
        # a band top low enough that the DOLLAR ceiling bites first (0.5x basis per unit)
        cf.market_ceiling_usd = lambda n: 0.5 * b * cf.reference_ns_per_unit() * n
        dollar, rate, eff, which = cf.unit_ceiling_components()
        assert dollar < rate, (dollar, rate)
        assert eff == dollar and "dollar ceiling" in which, which
        assert cf.unit_usd_per_ns_ceiling() == dollar
        # a unit under the 1.5x rate line but OVER the squeezed dollar ceiling must be refused, and the
        # refusal must name the dollar ceiling rather than the rate line
        n, _placed, why = cf.place_units([1.2 * b], 5)
        assert n == 0 and "dollar ceiling" in why and "rate line" not in why, why
        # ...and one under both still places
        assert cf.place_units([0.4 * b], 5)[0] == 1
    finally:
        cf.market_ceiling_usd = real
    # restored: the rate line binds again
    assert "rate line" in cf.unit_ceiling_components()[3]


# ---- the stopped-host adjudication: never-started vs preempted, and the machine that took several down ------
# Added 2026-07-27 after five of fifteen hosts sat stopped and NO committed artifact carried `machine_id`,
# so "five bad hosts" and "one bad machine rented five times" were indistinguishable. The two readings have
# opposite remedies, so a classifier that cannot separate them is not a classifier.

def _inst(iid, label, machine, msg, cur="stopped", age_h=0.5):
    import time
    return {"id": iid, "label": label, "machine_id": machine, "status_msg": msg, "cur_state": cur,
            "gpu_name": "RTX 5090", "start_date": time.time() - age_h * 3600}


def test_never_started_and_preempted_are_separated_by_the_status_msg_signature():
    """A container that never executed is HOST-scoped (destroy + share the machine). A box that ran and
    exited is a routine preemption (resume; excluding its machine retires healthy cheap supply)."""
    import congeneric_fanout_vast as fv
    live = [_inst(1, "s1f-00-a", "7001", ""),
            _inst(2, "s1f-01-b", "7002", "success, running docker.io/triskit23/nr4a3fep_latest/ssh"),
            _inst(3, "s1f-02-c", "7003", "", cur="running")]      # running: not stopped, not adjudicated
    c = fv.never_started_cohort(live)
    assert [r["label"] for r in c["never_started"]] == ["s1f-00-a"]
    assert [r["label"] for r in c["preempted"]] == ["s1f-01-b"]
    assert c["n_never_started"] == 1 and c["n_preempted"] == 1
    assert c["never_started"][0]["klass"] == "host_fault"        # sole rental on 7001


def test_a_duplicate_on_a_machine_we_already_hold_is_NOT_a_bad_host():
    """★ THE MEASUREMENT (2026-07-27): 0 of 7 double-booked instances started, 8 of 10 single-booked ones
    did. A Vast machine rents a fixed number of GPUs, so a second container on a box whose GPU we already
    hold sits stopped with an empty status_msg — the SAME signature as a genuine create/start race. Host
    exclusions are PERMANENT and CROSS-LANE, so misfiling this class retires healthy machines that are
    running our own work."""
    import congeneric_fanout_vast as fv
    live = [_inst(1, "s1f-05-incumbent", "19492", "success, running img", cur="running", age_h=1.0),
            _inst(2, "s1f-01-dupe", "19492", "", age_h=0.25)]
    c = fv.never_started_cohort(live)
    (dupe,) = c["never_started"]
    assert dupe["klass"] == "double_booked" and dupe["double_booked_behind"] == 1
    assert "NOT be excluded" in dupe["remedy"]
    assert c["n_double_booked"] == 1 and c["n_host_fault"] == 0
    # and the machine must NOT appear in the set that earns a permanent cross-lane exclusion
    assert c["host_fault_machines"] == []


def test_the_OLDEST_instance_on_a_bad_machine_is_the_host_fault_and_the_rest_are_duplicates():
    """Machine 19499 took three never-starts. The first was a real refusal (nothing of ours was on it); the
    two placed after it are our own duplicates. One exclusion, not three — and the exclusion must come from
    the instance that actually evidences a host fault."""
    import congeneric_fanout_vast as fv
    live = [_inst(1, "s1f-08-a", "19499", "", age_h=0.82),
            _inst(2, "s1f-14-b", "19499", "", age_h=0.73),
            _inst(3, "s1f-01-c", "19499", "", age_h=0.15)]
    c = fv.never_started_cohort(live)
    klass = {r["instance"]: r["klass"] for r in c["never_started"]}
    assert klass == {1: "host_fault", 2: "double_booked", 3: "double_booked"}
    assert c["host_fault_machines"] == ["19499"]
    assert c["max_units_on_one_machine"] == 3


def test_the_headline_is_how_many_units_ONE_machine_took_down():
    """N never-starts on N machines is a thin board; N on ONE machine is a 1569-class box that won selection
    N times and needs exactly one exclusion. Only this number tells them apart."""
    import congeneric_fanout_vast as fv
    spread = [_inst(i, f"s1f-{i:02d}-x", str(8000 + i), "") for i in range(5)]
    assert fv.never_started_cohort(spread)["max_units_on_one_machine"] == 1
    stacked = [_inst(i, f"s1f-{i:02d}-x", "1569", "") for i in range(5)]
    c = fv.never_started_cohort(stacked)
    assert c["max_units_on_one_machine"] == 5
    assert c["never_started_by_machine"] == {"1569": sorted(f"s1f-{i:02d}-x" for i in range(5))}


def test_an_exclusion_added_AFTER_we_rented_is_corroboration_not_a_selector_bug():
    """Machine 144071 entered the shared set between two ticks, minutes after this lane rented it. Reading
    that as 'the selector ignored the exclusion set' would accuse our own code on evidence that cannot
    support it — the only thing that can is the `excluding N machine(s)` line of the wave that placed it."""
    import congeneric_fanout_vast as fv
    live = [_inst(1, "s1f-03-a", "144071", "")]
    c = fv.never_started_cohort(live, excluded={"144071"})
    assert c["machines_excluded_since"] == ["144071"]
    assert "rented_despite_exclusion" not in c, "must not make a claim the data cannot support"
    assert fv.never_started_cohort(live)["machines_excluded_since"] == []


def test_the_condemn_path_excludes_a_host_fault_and_never_a_duplicate():
    """The safety property with the money on it: a permanent, cross-lane exclusion must be reachable ONLY
    from the host-fault branch. Pinned as source because the branch sits inside `mode_monitor`, behind a
    Vast key, an S3 client and a live board."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_monitor)
    assert 'if stuck_sig and i.get("id") in _dupes:' in src, "the duplicate branch must be tested FIRST"
    assert "_scope = None" in src and "if _scope is None:" in src, \
        "a duplicate must reach a branch that writes NO exclusion"
    # the host-scoped publish must still exist for the genuine case
    assert '_scope = "host"' in src


def test_the_launch_wave_avoids_machines_the_lane_is_ALREADY_renting():
    """The wave-local `used_machines` only remembered THIS process's submissions, so a second wave minutes
    later could stack a unit onto a machine the first wave had just rented — two units contending for one
    GPU, and one bad machine taking both down together. Pinned as source, because the seeding happens deep
    inside `mode_launch` (Vast key, S3 and a live board) and the property is a one-line invariant."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_launch)
    assert "_already_on" in src and "used_machines |= _already_on" in src, \
        "mode_launch must seed host-distinctness with the machines it is already renting"
    # and it must NOT write them to the durable exclusion set — a machine we are happily running on is good
    assert "_record_exclusion(s3, bucket, _already_on" not in src

def test_the_double_booked_floor_is_DERIVED_from_the_one_home_and_is_shorter():
    """`STUCK_START_MIN` buys image-pull protection and nothing else, and a container with no GPU to pull
    onto has none to protect. The floor must be a FRACTION of that single home so the two cannot drift, and
    the two-strike rule must not move for either class."""
    import congeneric_fanout_vast as fv
    assert fv.stuck_start_min_for(False) == fv.STUCK_START_MIN
    assert fv.stuck_start_min_for(True) == fv.STUCK_START_MIN / 3.0
    assert fv.stuck_start_min_for(True) < fv.stuck_start_min_for(False)
    assert fv.STUCK_START_STRIKES >= 2, "consecutive-observation discipline is never relaxed (CLAUDE.md §4)"
    import inspect
    src = inspect.getsource(fv.mode_monitor)
    assert "_floor = stuck_start_min_for(" in src and "age >= _floor" in src, \
        "the condemn test must use the derived per-class floor, not the bare constant"

def test_a_machine_that_HAS_run_our_container_can_never_be_condemned_as_never_starting():
    """★ THE VERDICT MUST NOT DEPEND ON WHAT WAS CLEANED UP (2026-07-27, observed within 7 minutes).
    46031788 was correctly `double_booked` behind our own 46031535 on machine 53989. The collect reaped
    46031535 for being terminal, 46031788 became the oldest thing we held there, and the SAME instance
    re-classified as `host_fault` — one strike from publishing 53989 cross-lane and permanently, though it
    had just run two of this lane's containers to 94-99 % GPU."""
    import congeneric_fanout_vast as fv
    incumbent = _inst(1, "s1f-12-x", "53989", "success, running img", age_h=0.75)
    dupe = _inst(2, "s1f-15-y", "53989", "", age_h=0.7)
    assert fv.never_started_cohort([incumbent, dupe])["never_started"][0]["klass"] == "double_booked"
    # incumbent reaped, nothing else changed, and WITHOUT the durable set it would flip to host_fault
    assert fv.never_started_cohort([dupe])["never_started"][0]["klass"] == "host_fault"
    # ...with it, the machine is proven and cannot be condemned
    c = fv.never_started_cohort([dupe], known_good={"53989"})
    (row,) = c["never_started"]
    assert row["klass"] == "stopped_on_a_proven_machine" and row["machine_has_run_our_container"]
    assert c["host_fault_machines"] == [] and c["n_host_fault"] == 0
    assert c["n_stopped_on_a_proven_machine"] == 1


def test_the_proven_set_is_read_off_a_non_empty_status_msg():
    """Whatever the message says, the box got as far as running our image — which is the exact claim a
    'never starts' verdict denies."""
    import congeneric_fanout_vast as fv
    live = [_inst(1, "s1f-a", "111", "success, running docker.io/triskit23/nr4a3fep_latest/ssh"),
            _inst(2, "s1f-b", "222", "#7 5.55 Get:5 http://archive.ubuntu.com/ubuntu jammy/main"),
            _inst(3, "s1f-c", "333", ""), _inst(4, "s1f-d", "444", "   ")]
    assert fv.observed_started_machines(live) == ["111", "222"]


def test_the_condemn_path_never_publishes_a_proven_machine():
    """The safety property, pinned as source: a cross-lane exclusion must be unreachable from both the
    duplicate branch and the proven-machine branch."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_monitor)
    i_proven = src.index('if stuck_sig and i.get("id") in _proven:')
    i_dupe = src.index('elif stuck_sig and i.get("id") in _dupes:')
    i_host = src.index('_scope = "host"')
    assert i_proven < i_dupe < i_host, "both no-exclusion branches must be tested before the host verdict"
    # the proven set must be built from the DURABLE store, not only from the current listing
    assert "_load_started_machines(s3, bucket)" in src and "_save_started_machines(s3, bucket, _good)" in src

# ---- withdrawing an exclusion that the evidence refutes -----------------------------------------------------
# Added 2026-07-27 after three machines that had run this lane's legs at 94-99 % GPU were condemned
# host-scoped by the unstable verdict, and the very next tick excluded 38 machines against a 152-offer board
# and lost 4 of 5 authorised placements to `no rentable verified offer`.

class _DictS3:
    """S3 stand-in over a dict of key -> bytes, with just get_object/put_object."""

    def __init__(self, objs=None):
        self.objs = dict(objs or {})

    def get_object(self, Bucket=None, Key=None):  # noqa: N803
        import io
        if Key not in self.objs:
            raise KeyError(Key)
        return {"Body": io.BytesIO(self.objs[Key])}

    def put_object(self, Bucket=None, Key=None, Body=None):  # noqa: N803
        self.objs[Key] = Body


def _excl_doc(entries):
    import json
    return json.dumps({"machine_ids": sorted({m for m, _ in entries}),
                       "history": [{"machine_id": m, "why": w} for m, w in entries]}).encode()


def test_a_never_starts_exclusion_is_withdrawn_by_evidence_that_it_started():
    import json
    import congeneric_fanout_vast as fv
    s3 = _DictS3({f"{fv.RESULT_PREFIX}/_excluded_machines.json":
                  _excl_doc([("53989", "never started: cur_state=stopped with an empty status_msg"),
                             ("1569", "never started: create/start race")])})
    assert fv.withdraw_wrong_exclusions(s3, "bkt", {"53989"}) == ["53989"]
    doc = json.loads(s3.objs[f"{fv.RESULT_PREFIX}/_excluded_machines.json"])
    assert doc["machine_ids"] == ["1569"], "only the refuted entry goes; the unrefuted one stays"
    assert any(h.get("action") == "withdraw" for h in doc["history"]), "the withdrawal must be recorded"


def test_an_exclusion_for_a_DIFFERENT_reason_survives_evidence_that_it_started():
    """The lane-scoped throughput verdict is about the machine PAIRED WITH THIS WORKLOAD. A host that starts
    fine and then sustains 12 % GPU is exactly what it describes, so starting refutes nothing."""
    import congeneric_fanout_vast as fv
    s3 = _DictS3({f"{fv.RESULT_PREFIX}/_excluded_machines.json":
                  _excl_doc([("777", "gpu_util 12.0% for 2 checks on a plain-RBFE leg (healthy band 70-95%)")])})
    assert fv.withdraw_wrong_exclusions(s3, "bkt", {"777"}) == []


def test_withdrawal_is_not_an_ageing_policy():
    """Nothing is withdrawn for being old — only for positive contrary evidence. A machine never observed
    running must survive untouched however long it has sat in the set."""
    import congeneric_fanout_vast as fv
    s3 = _DictS3({f"{fv.RESULT_PREFIX}/_excluded_machines.json":
                  _excl_doc([("1569", "never started: create/start race")])})
    assert fv.withdraw_wrong_exclusions(s3, "bkt", set()) == []
    assert fv.withdraw_wrong_exclusions(s3, "bkt", {"999"}) == []


def test_the_shared_set_refuses_to_overrule_another_lanes_entry():
    import json
    import vast_machine_blacklist as vmb
    s3 = _DictS3({vmb.SHARED_KEY: json.dumps(
        {"machine_ids": ["46392"],
         "history": [{"machine_id": "46392", "why": "never started", "lane": "rung5aks"}]}).encode()})
    assert vmb.withdraw(s3, "bkt", "46392", "we saw it run", lane="step1_fanout") is False
    assert json.loads(s3.objs[vmb.SHARED_KEY])["machine_ids"] == ["46392"]
    # ...but its own entry it may withdraw
    assert vmb.withdraw(s3, "bkt", "46392", "we saw it run", lane="rung5aks") is True
    assert json.loads(s3.objs[vmb.SHARED_KEY])["machine_ids"] == []


def test_the_repair_runs_before_the_condemn_block():
    """Otherwise a machine could be withdrawn and re-condemned inside a single tick, which is a loop, not a
    repair."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_monitor)
    assert src.index("withdraw_wrong_exclusions(s3, bucket, _good)") < src.index("_cohort_now =")

def test_a_submit_starved_by_OUR_OWN_filters_does_not_read_as_a_capacity_refusal():
    """`no rentable verified offer` is emitted both when the market has nothing and when our exclusion set
    plus host-distinctness have eaten the board. Opposite remedies — withdraw a wrong exclusion vs wait for
    prices — so the readout must name which. Measured: 38 machines excluded against 152 offers lost 4 of 5
    authorised placements, every one printing as if the market had refused us."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_launch)
    assert '"no rentable verified offer" in str(e)' in src
    assert "NOT a capacity refusal" in src
    # and it must break the count down into the two causes, since only one of them is actionable here
    assert "_n_excl, _n_held = len(excluded), len(used_machines) - len(excluded)" in src


# ---- host distinctness vs the SLOT rule: they disagree ON PURPOSE (2026-07-27, 6:32 -> 6:53 PM ET) --------

def test_a_terminal_instance_still_makes_its_machine_off_limits():
    """THE TRAP, PINNED SO IT IS NOT "FIXED" AGAIN. `live_labels` deliberately does not let an `exited`
    instance hold its unit's SLOT, so the seed here — which avoids every machine in the listing — reads like
    the 6c996cca defect ("the gate counted corpses as hosts"). It is not, and the repo has the measurement:
    the three machines the 6:32 PM tick called corpses (43159, 50143, 28904) were all `running` again 21 min
    later, and the committed-iteration census proves they never stopped working (cw_ev_5oh went warmup@380 ->
    production@40; cw_ev_5alkyne added 80 iterations). `exited` is routinely a TRANSIENT status.

    The two rules ask different questions with different costs of being wrong: re-submitting a unit needlessly
    costs one rental against an S3 checkpoint, while double-booking a machine lands a second unit on a GPU our
    own leg is still using — measured today at 0 of 7 double-booked instances ever starting."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_launch)
    seed = '_already_on = {str(i.get("machine_id")) for i in live if i.get("machine_id") is not None}'
    assert seed in src, "the distinctness seed must span the WHOLE listing, terminal instances included"
    # and it must not have been narrowed by the terminal-state test the SLOT rule uses
    assert '_already_on = {str(i.get("machine_id")) for i in live\n' not in src
    assert "_TERMINAL" not in src.split(seed)[1].split("used_machines |= _already_on")[0]


def test_the_launcher_says_out_loud_that_a_terminal_status_does_not_free_a_machine():
    """A reader comparing the two lines in one readout will otherwise conclude the launcher contradicts
    itself — which is exactly the wrong conclusion that got acted on once already."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_launch)
    assert "A TERMINAL status does not free a" in src
    assert "`exited` is routinely transient" in src


def test_the_reaper_still_requires_two_consecutive_terminal_observations():
    """This is the same fact from the other side, and it is what makes the distinctness rule above correct:
    the lane does not believe a single terminal reading anywhere. If this ever became a one-shot reap, the
    transient-`exited` argument would need re-measuring rather than assuming."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_collect) if hasattr(fv, "mode_collect") else ""
    if not src:
        import pytest
        pytest.skip("mode_collect not present under this name")
    assert "if seen < 2:" in src


# ================================================================= THE REPLICATE AXIS (TRANCHE 1R)
# 2026-07-31. The lane could not run a replicate at all: `unit_id` had no repeat component, `result_key` and
# therefore `_pending` keyed done-detection off it, so a "replicate" request for an already-computed edge was
# SILENTLY SKIPPED — and `FANOUT_ONLY`, which filters the pending set and hard-fails on an empty match, could
# not rescue it. These tests gate the two halves of the fix that can go wrong expensively: the ids that must
# NOT change (18 landed ddG results are content-addressed by them, ~$74 to re-buy) and the isolation that
# makes a replicate an independent draw rather than a longer one.

# ★ THE 19 UNIT IDS AS THEY EXISTED BEFORE THE REPLICATE AXIS. Generated by running the pre-change
# `congeneric_fanout.py` out of `git show HEAD:` — i.e. these are transcribed from the code that produced
# the keys now sitting in S3, not re-derived from the code under test.
PRE_REPLICATE_UNIT_IDS = [
    "e_zaienne_cmpd19__cw_ev_5nh2__neutral__neutral",
    "e_zaienne_cmpd19__cw_ev_5oh__neutral__neutral",
    "e_zaienne_cmpd19__cw_ev_5cooh__neutral__neutral_acid",
    "e_zaienne_cmpd19__cw_ev_5alkyne__neutral__neutral",
    "e_zaienne_cmpd19__cw_ev_5ch2nh2__neutral__neutral_amine",
    "e_zaienne_cmpd19__cw_ev_5opropargyl__neutral__neutral",
    "e_zaienne_cmpd19__cw_ev_5piperazine__neutral__neutral",
    "e_zaienne_cmpd19__cw_ev_5pegamine__neutral__neutral_amine",
    "e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral",
    "e_zaienne_cmpd19__cw_bio_nmethyl_amide__neutral__neutral",
    "e_zaienne_cmpd19__cw_bio_tetrazole__neutral__neutral",
    "e_zaienne_cmpd19__cw_bio_acylsulfonamide__neutral__neutral",
    "e_zaienne_cmpd19__cw_bio_hydroxamic__neutral__neutral",
    "e_zaienne_cmpd19__cw_ms_free_acid__neutral__neutral_acid",
    "e_zaienne_cmpd19__cw_ms_carbinol__neutral__neutral",
    "e_zaienne_cmpd19__cw_ms_5acetamido_ester__neutral__neutral",
    "e_cw_ev_5nh2__cw_ms_5acetamido_ester__neutral__neutral",
    "e_cw_ev_5oh__cw_ev_5opropargyl__neutral__neutral",
    "e_cw_ms_free_acid__cw_bio_primary_amide__neutral_acid__neutral",
]


def test_every_existing_unit_id_is_byte_identical_after_the_replicate_axis():
    """THE EXPENSIVE ONE. Every landed ddG is content-addressed by its unit_id: `_pending` calls a unit
    finished iff `<prefix>/<unit_id>/ddg.json` exists. Rename one and the lane does not "relabel" it — it
    stops seeing it, and the next unattended tick re-rents that edge. Order is pinned too, because the Vast
    label carries the unit's INDEX in this list and `mode_collect` matches a live host back to its unit
    through that label."""
    units = cf.default_units()
    assert [u["unit_id"] for u in units] == PRE_REPLICATE_UNIT_IDS
    assert [u["replicate"] for u in units] == [0] * 19
    # and the two keys derived from the id, which are the actual S3 objects
    assert [cf.result_key(u, "pfx") for u in units] == [f"pfx/{i}/ddg.json" for i in PRE_REPLICATE_UNIT_IDS]
    assert [cf.checkpoint_prefix(u, "pfx") for u in units] == [f"pfx/{i}/ckpt" for i in PRE_REPLICATE_UNIT_IDS]


@pytest.mark.committed_artifact
def test_the_pinned_ids_still_cover_every_result_this_lane_has_bought():
    """Cross-check the pin against the committed map artifact rather than against the code that produced it:
    if a future edit changed BOTH the function and the pin, this still fails."""
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "step1-fanout-map.json")) as fh:
        landed = {r["unit_id"] for r in json.load(fh)["results"]}
    assert landed and landed <= set(PRE_REPLICATE_UNIT_IDS)


def test_replicate_0_renders_no_suffix_and_a_replicate_renders_one():
    assert cf.unit_id("e_x", "neutral__neutral") == "e_x__neutral__neutral"
    assert cf.unit_id("e_x", "neutral__neutral", replicate=0) == "e_x__neutral__neutral"
    assert cf.unit_id("e_x", "neutral__neutral", replicate=2) == "e_x__neutral__neutral__r2"
    # the frame qualifier keeps its place; the repeat index goes last
    assert (cf.unit_id("e_x", "neutral__neutral", "nr4a1", "nr4a1_antitarget:matched_open_frame", 3)
            == "e_x__neutral__neutral__nr4a1_matched_open_frame__r3")
    with pytest.raises(ValueError):
        cf.unit_id("e_x", "l", replicate=-1)


def test_the_open_cycles_edges_resolve_from_the_map_not_from_a_typed_list():
    """`cycle_3carbonyl` is the cycle that does not close; the replicate request names IT, and the three
    edge ids come from the frozen map. Typing them here (or in a workflow) is the transcription error this
    resolution exists to prevent."""
    ids = cf.resolve_edge_ids(["cycle_3carbonyl"])
    cyc = [c for c in cf.load_map()["cycles"] if c["cycle_id"] == "cycle_3carbonyl"][0]
    assert set(ids) == set(cyc["edge_ids"]) and len(ids) == 3
    # an unknown name fails closed rather than silently selecting nothing
    with pytest.raises(ValueError, match="not an edge id or a cycle id"):
        cf.resolve_edge_ids(["cycle_3"])


def test_a_replicate_is_a_distinct_unit_with_its_own_result_and_checkpoint_keys():
    base = {u["edge_id"]: u for u in cf.default_units()}
    reps = cf.replicate_units(["cycle_3carbonyl"], (1, 2))
    assert len(reps) == 6 and {r["replicate"] for r in reps} == {1, 2}
    for r in reps:
        b = base[r["edge_id"]]
        assert r["unit_id"] != b["unit_id"] and r["unit_id"].startswith(b["unit_id"] + "__r")
        # the two S3 objects done-detection and resume are keyed on
        assert cf.result_key(r, "p") != cf.result_key(b, "p")
        assert cf.checkpoint_prefix(r, "p") != cf.checkpoint_prefix(b, "p")
        # same chemistry, same leg, same frame — a replicate differs by the draw and nothing else
        for k in ("edge_id", "leg_id", "ligand_a", "ligand_b", "smiles_a", "smiles_b", "receptor", "frame"):
            assert r[k] == b[k]
    assert len({r["unit_id"] for r in reps}) == 6


def test_replicate_0_is_refused_because_it_is_the_original_not_a_repeat():
    with pytest.raises(ValueError, match="must be >= 1"):
        cf.replicate_units(["cycle_3carbonyl"], (0,))
    with pytest.raises(ValueError):
        cf.replicate_units(["cycle_3carbonyl"], ())


def test_lane_units_is_exactly_the_map_when_no_replicate_is_requested(monkeypatch):
    monkeypatch.delenv("FANOUT_REPLICATE_EDGES", raising=False)
    monkeypatch.delenv("FANOUT_REPLICATES", raising=False)
    assert [u["unit_id"] for u in cf.lane_units()] == PRE_REPLICATE_UNIT_IDS
    assert cf.requested_replicates() == ([], [])


def test_lane_units_appends_replicates_without_disturbing_the_map_order(monkeypatch):
    monkeypatch.setenv("FANOUT_REPLICATE_EDGES", "cycle_3carbonyl")
    monkeypatch.setenv("FANOUT_REPLICATES", "2")
    lane = cf.lane_units()
    assert [u["unit_id"] for u in lane[:19]] == PRE_REPLICATE_UNIT_IDS   # indices -> Vast labels: unmoved
    assert len(lane) == 25 and all(u["replicate"] for u in lane[19:])
    assert cf.fanout_width() == 25


# ---- SEED: emitted for a replicate, ABSENT at n=0, and consumed by the engine ------------------------------

def test_unit_env_emits_no_SEED_at_n0_because_the_resume_fingerprint_hashes_it():
    """`rbfe_spot_checkpoint.SYSTEM_FINGERPRINT_ENV` lists SEED and hashes `str(env.get(k, ""))`, so unset
    and "" collide but "0" does NOT. Every generation this lane has committed was written with SEED unset;
    emitting SEED=0 would give all of them a fingerprint mismatch and every in-flight leg would refuse to
    resume after a preemption. The absence is the feature."""
    u0 = cf.default_units()[0]
    assert "SEED" not in cf.unit_env(u0, "complex")
    assert "RBFE_STRICT_PROVENANCE" not in cf.unit_env(u0, "complex")
    r1 = cf.replicate_units([u0["edge_id"]], (1,))[0]
    assert cf.unit_env(r1, "complex")["SEED"] == "1"
    assert cf.unit_env(r1, "complex")["RBFE_STRICT_PROVENANCE"] == "1"
    # SEED == the replicate index, on every leg kind
    r3 = cf.replicate_units([u0["edge_id"]], (3,))[0]
    for leg in ("complex", "solvent", "reduce"):
        assert cf.unit_env(r3, leg)["SEED"] == "3"


def test_a_differing_seed_REFUSES_to_resume_a_committed_generation():
    """The resume guard, exercised end to end on the real fingerprint code: a generation committed by the
    n=0 unit may not be restored into a replicate, and vice versa. Without this a replicate could extend
    another draw's trajectory and report it as an independent sample."""
    import rbfe_spot_checkpoint as spot
    u0 = cf.default_units()[0]
    r2 = cf.replicate_units([u0["edge_id"]], (2,))[0]
    base_env = {"LEG_ID": "complex", "CHARGE_METHOD": "am1bcc", "N_WINDOWS": "12"}
    env0 = {**base_env, **cf.unit_env(u0, "complex")}
    env2 = {**base_env, **cf.unit_env(r2, "complex")}
    fp0, f0 = spot.system_fingerprint(env0)
    fp2, _ = spot.system_fingerprint(env2)
    assert fp0 != fp2, "n=0 and r2 must not share a resume fingerprint"
    manifest0 = {"system_fingerprint": fp0, "system_fingerprint_fields": f0}
    assert spot.fingerprint_mismatch_reason(manifest0, env0) is None          # its own generation: fine
    why = spot.fingerprint_mismatch_reason(manifest0, env2)                   # the other draw's: refused
    assert why and "MISMATCH" in why and "SEED" in why
    # and the refusal is symmetric
    fp2_fields = spot.system_fingerprint(env2)[1]
    assert spot.fingerprint_mismatch_reason(
        {"system_fingerprint": fp2, "system_fingerprint_fields": fp2_fields}, env0)


def test_the_n0_fingerprint_is_unchanged_by_the_replicate_axis():
    """The other half of the same guard: adding the axis must not move the hash of a configuration that
    existed before it, or every already-committed generation becomes unrestorable."""
    import rbfe_spot_checkpoint as spot
    u0 = cf.default_units()[0]
    env = {"LEG_ID": "complex", "CHARGE_METHOD": "am1bcc", "N_WINDOWS": "12"}
    assert spot.system_fingerprint(env)[0] == spot.system_fingerprint({**env, **cf.unit_env(u0, "complex")})[0]
    assert spot.system_fingerprint(env)[0] != spot.system_fingerprint({**env, "SEED": "0"})[0]


def test_SEED_is_listed_in_the_resume_fingerprint_at_all():
    """If SEED were ever dropped from SYSTEM_FINGERPRINT_ENV the two tests above would still pass through
    the checkpoint-prefix separation alone, and the belt would be gone without anything saying so."""
    import rbfe_spot_checkpoint as spot
    assert "SEED" in spot.SYSTEM_FINGERPRINT_ENV


def test_the_engine_parses_an_empty_SEED_rather_than_crashing_on_a_rented_GPU(monkeypatch):
    """`env SEED="$SEED"` in a launcher whose SEED is unset exports the EMPTY STRING, and `int("")` raises.
    That would be a crash in the setup phase of a billed leg, for a variable the engine never used before."""
    import importlib
    import nr4a3_rbfe
    for raw, want in (("", 0), (None, 0), ("2", 2), (" 3 ", 3)):
        if raw is None:
            monkeypatch.delenv("SEED", raising=False)
        else:
            monkeypatch.setenv("SEED", raw)
        m = importlib.reload(nr4a3_rbfe)
        assert m.SEED == want
        assert m.SEED_ENV_RAW == raw
    monkeypatch.delenv("SEED", raising=False)
    importlib.reload(nr4a3_rbfe)


class _FakeGroup:
    pass


class _FakeSettings:
    def __init__(self, with_seed_field):
        self.simulation_settings = _FakeGroup()
        self.integrator_settings = _FakeGroup()
        if with_seed_field:
            self.simulation_settings.random_seed = None


def test_the_engine_applies_the_seed_to_every_stream_it_can_actually_reach(monkeypatch):
    """★ MEASURED, NOT ASSUMED (2026-07-31). OpenFE's settings expose NO seed field — `grep -i seed` over
    `src/openfe/protocols/openmm_utils/omm_settings.py` returns nothing, `_get_integrator` builds an
    `openmmtools.mcmc.LangevinDynamicsMove` with no seed argument, and openmmtools never calls
    `setRandomNumberSeed`, so the thermostat seed is OpenMM's default 0 = OS-drawn per Context. What IS
    reachable is the global NumPy RNG that openmmtools' replica mixing draws from
    (`multistate/replicaexchange.py` uses `np.random`). So `_apply_seed` must seed that, must use a settings
    seed field IF one ever appears, and must never silently do nothing."""
    import importlib
    import numpy as np
    import nr4a3_rbfe
    monkeypatch.setenv("SEED", "7")
    m = importlib.reload(nr4a3_rbfe)

    rep = m._apply_seed(_FakeSettings(with_seed_field=False))
    assert rep["seed"] == 7
    assert any("numpy.random.seed(7)" in a for a in rep["applied"])
    # the absence of a settings hook is REPORTED, never swallowed
    assert "simulation_settings.random_seed" in rep["not_available"]
    # and it is a real seeding, not a log line: the stream is reproducible from the index
    m._apply_seed(_FakeSettings(with_seed_field=False))
    a = np.random.rand(3).tolist()
    m._apply_seed(_FakeSettings(with_seed_field=False))
    assert np.random.rand(3).tolist() == a
    monkeypatch.setenv("SEED", "8")
    m8 = importlib.reload(nr4a3_rbfe)
    m8._apply_seed(_FakeSettings(with_seed_field=False))
    assert np.random.rand(3).tolist() != a          # a different index is a different stream

    # if a future openfe grows the field, it is used
    s = _FakeSettings(with_seed_field=True)
    rep2 = m8._apply_seed(s)
    assert s.simulation_settings.random_seed == 8
    assert "simulation_settings.random_seed=8" in rep2["applied"]

    monkeypatch.delenv("SEED", raising=False)
    importlib.reload(nr4a3_rbfe)


def test_SEED_0_leaves_the_rng_exactly_as_the_18_landed_edges_had_it(monkeypatch):
    """A replicate must not retroactively change how the map's own draw was computed. At SEED=0 nothing is
    seeded — same choice, same reason, as nr4a3_metad.py."""
    import importlib
    import numpy as np
    import nr4a3_rbfe
    monkeypatch.delenv("SEED", raising=False)
    m = importlib.reload(nr4a3_rbfe)
    np.random.seed(12345)
    before = np.random.rand(3).tolist()
    np.random.seed(12345)
    rep = m._apply_seed(_FakeSettings(with_seed_field=False))
    assert np.random.rand(3).tolist() == before, "SEED=0 must not touch the global RNG"
    assert not [a for a in rep["applied"] if "numpy" in a]


def test_the_protocol_builder_actually_calls_the_seeder():
    """A seeding function nothing calls is the failure this whole change is about."""
    import inspect
    import nr4a3_rbfe
    assert "_apply_seed(s)" in inspect.getsource(nr4a3_rbfe._protocol)


# ---- placement: a replicate is genuinely PENDING while the n=0 edge stays DONE -----------------------------

def test_pending_treats_a_replicate_as_a_separate_unit(monkeypatch):
    """The defect in one assertion. `_pending` skips any unit whose ddg.json exists; all three cycle edges
    have one, so before the axis a replicate request was silently skipped and `FANOUT_ONLY` — which filters
    the PENDING set and hard-fails on an empty match — could not rescue it."""
    import congeneric_fanout_vast as fv
    monkeypatch.setenv("FANOUT_REPLICATE_EDGES", "cycle_3carbonyl")
    monkeypatch.setenv("FANOUT_REPLICATES", "2")
    lane = cf.lane_units()
    done = set(PRE_REPLICATE_UNIT_IDS)          # pretend the whole map has landed

    class _S3:
        def head_object(self, Bucket, Key):     # noqa: N803 — boto3's signature
            uid = Key.split("/")[-2]
            if uid in done:
                return {}
            raise KeyError(Key)

    pending = fv._pending(_S3(), "bkt", lane, blocked={})
    assert [u["unit_id"] for u in pending] == [u["unit_id"] for u in lane if u["replicate"]]
    assert len(pending) == 6
    # and the finished map units are still counted as done, not as unrun
    n_done, n_blocked, n_out = fv.counts(lane, done, {})
    assert (n_done, n_blocked, n_out) == (19, 0, 6)


def test_the_launcher_enumerates_the_lane_and_not_just_the_map():
    """`_pending` can only hide or reveal units it is HANDED. If mode_launch went back to `default_units()`
    a replicate would not be held, it would be invisible — no hold artifact, no readout, nothing."""
    import inspect
    import congeneric_fanout_vast as fv
    for fn in (fv.mode_launch, fv.mode_monitor, fv.mode_diag):
        src = inspect.getsource(fn)
        assert "lane_units()" in src, f"{fn.__name__} must enumerate lane_units()"
        assert "= default_units()" not in src, f"{fn.__name__} must not fall back to the map alone"


def test_collect_keeps_the_map_scoped_to_19_but_reaps_over_the_whole_lane():
    """Two lists, deliberately: the artifact's denominator must not move when a replicate is requested, and
    a replicate host that finished must still be recognised and destroyed."""
    import inspect
    import congeneric_fanout_vast as fv
    src = inspect.getsource(fv.mode_collect)
    assert "units = default_units()" in src and "lane = lane_units()" in src
    assert "for i, u in enumerate(lane)" in src            # labels/reaping run off the lane
    assert "for u in lane}" in src


def test_a_replicate_jobspec_carries_its_seed_and_an_n0_one_does_not():
    import congeneric_fanout_vast as fv
    u0 = cf.default_units()[0]
    r1 = cf.replicate_units([u0["edge_id"]], (1,))[0]
    s0, s1 = fv.build_jobspec(u0, "b", "bkt", 0), fv.build_jobspec(r1, "b", "bkt", 19)
    assert "SEED" not in s0.env and "REPLICATE" not in s0.env
    assert s1.env["SEED"] == "1" and s1.env["REPLICATE"] == "1"
    assert s1.env["RBFE_STRICT_PROVENANCE"] == "1"
    # separate checkpoint URI is what stops the two sharing a commit store
    assert s0.checkpoint_uri != s1.checkpoint_uri and s1.checkpoint_uri.endswith("__r1/ckpt")
    assert s0.name != s1.name and len(s1.name) <= 64


def test_replicate_stats_reports_a_sample_SD_across_draws_and_none_below_n2():
    rows = [{"edge_id": "e_a", "replicate": 0, "ddg_bind_kcal": 1.0},
            {"edge_id": "e_a", "replicate": 1, "ddg_bind_kcal": 2.0},
            {"edge_id": "e_a", "replicate": 2, "ddg_bind_kcal": 3.0},
            {"edge_id": "e_b", "replicate": 0, "ddg_bind_kcal": 5.0}]
    st = cf.replicate_stats(rows)
    assert st["e_a"]["n"] == 3 and st["e_a"]["mean_kcal"] == 2.0 and st["e_a"]["sd_kcal"] == 1.0
    assert st["e_a"]["draws"] == {"r0": 1.0, "r1": 2.0, "r2": 3.0}
    assert st["e_b"]["n"] == 1 and st["e_b"]["sd_kcal"] is None
    assert cf.replicate_stats([]) == {}


def test_the_plan_shows_the_replicate_request_and_says_what_it_does_not_buy(monkeypatch):
    monkeypatch.setenv("FANOUT_REPLICATE_EDGES", "cycle_3carbonyl")
    monkeypatch.setenv("FANOUT_REPLICATES", "2")
    p = cf.plan(env=os.environ)
    r = p["replicates"]
    assert p["n_units"] == 19                     # the tranche-1 headline is untouched
    assert r["n_units"] == 6 and r["replicate_indices"] == [1, 2] and len(r["edges"]) == 3
    assert set(r["seed_per_unit"].values()) == {"1", "2"}
    assert "not" in r["what_it_buys"].lower() and "accuracy" in r["what_it_buys"].lower()
    monkeypatch.delenv("FANOUT_REPLICATE_EDGES")
    assert "replicates" not in cf.plan(env=os.environ)


def test_the_launchers_pending_filter_IS_the_pure_one_a_dry_run_uses():
    """The dry run's whole value is that it exercises the launcher's own filter. If `_pending` grew a
    private copy of the rule, `PLAN` would be reporting on that copy."""
    import inspect
    import congeneric_fanout_vast as fv
    assert "pending_given(" in inspect.getsource(fv._pending)
    units = cf.default_units()
    done = {units[0]["unit_id"], units[5]["unit_id"]}
    blk = {units[9]["unit_id"]: {"why": "x"}}
    assert [u["unit_id"] for u in cf.pending_given(units, done, blk)] == [
        u["unit_id"] for u in units if u["unit_id"] not in done and u["unit_id"] not in blk]


def test_the_plan_dry_run_places_only_the_replicates_and_leaves_the_18_done(tmp_path, monkeypatch):
    """The question this whole change had to answer without spending a cent: would a replicate request for
    the open cycle actually be placed, and would the finished edges stay finished?"""
    import congeneric_fanout_vast as fv
    monkeypatch.setenv("FANOUT_REPLICATE_EDGES", "cycle_3carbonyl")
    monkeypatch.setenv("FANOUT_REPLICATES", "2")
    snap = tmp_path / "map.json"
    snap.write_text(json.dumps({
        "results": [{"unit_id": u} for u in PRE_REPLICATE_UNIT_IDS
                    if u != "e_zaienne_cmpd19__cw_bio_nmethyl_amide__neutral__neutral"],
        "blocked_units": {"e_zaienne_cmpd19__cw_bio_nmethyl_amide__neutral__neutral": {"why": "no mapper"}}}))
    dr = fv._plan_placement_dry_run(cf.lane_units(), map_path=str(snap))
    assert dr["n_lane_units"] == 25 and dr["n_done"] == 18 and dr["n_blocked"] == 1
    assert dr["n_would_place"] == 6
    assert all(u.endswith(("__r1", "__r2")) for u in dr["would_place"])
    assert set(dr["would_place_seeds"].values()) == {"1", "2"}
    # nothing already computed is re-placed — this is the ~$74 assertion
    assert not set(dr["would_place"]) & set(PRE_REPLICATE_UNIT_IDS)
    # and with no replicate requested the same snapshot places NOTHING
    monkeypatch.delenv("FANOUT_REPLICATE_EDGES")
    dr0 = fv._plan_placement_dry_run(cf.lane_units(), map_path=str(snap))
    assert dr0["n_lane_units"] == 19 and dr0["n_would_place"] == 0


def test_a_missing_snapshot_reads_as_unknown_not_as_finished(tmp_path):
    """Failing the other way — an absent artifact silently meaning 'all done' — would make a dry run say
    'nothing to place' on a fresh checkout, which is the reassuring-but-wrong answer."""
    import congeneric_fanout_vast as fv
    dr = fv._plan_placement_dry_run(cf.default_units(), map_path=str(tmp_path / "absent.json"))
    assert dr["n_done"] == 0 and dr["n_would_place"] == 19
    assert "NONE FOUND" in dr["_done_set_source"]
