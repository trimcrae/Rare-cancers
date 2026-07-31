#!/usr/bin/env python3
"""A host that refuses to start must be answered in the SAME submit — and the answer must not be a price story.

★★ WHAT THESE TESTS PIN, AND THE MEASUREMENT THEY COME FROM (2026-07-29).

Between 9:25 and 10:01 AM ET the ternary lane rented four hosts — machines 29711, 28164, 12227, 41950 — and
every one answered `resources_unavailable` on start. Every board read was CHEAP (1.04x, 1.09x, 1.34x basis,
far under the $0.006539/ns buy line), so it was never price. The step-1 fan-out, renting from the same board
in the same window, ran for hours.

THE PRIME SUSPECT — disk — IS REFUTED, and `test_the_ternary_ask_is_not_narrower_than_the_fanouts` is that
refutation as an executable claim: the ONLY field on which the two lanes' `ResourceSpec` differ is `disk_gb`,
and the ternary lane asks for LESS (60 vs 80). Its `disk_space >= 60` board is a strict SUPERSET of the
fan-out's `>= 80`, and it requests the smaller `disk` at create. There is no filter on which the ternary lane
is stricter, so no difference in the ASK can explain the asymmetry. The hosts are refuted too: all four
machines appear in `step1-fanout-map.json` `realised_rentals` as hosts the fan-out rented and RAN on.

WHAT WAS ACTUALLY WRONG. `PUT /instances/<id>/ {"state": "running"}` answers a capacity refusal with an
ordinary HTTP 200 carrying `{"success": false, "error": "resources_unavailable", ...}`. `_vast_request`
returns that body rather than raising, and `_ensure_running` discarded it — printing `intended=stopped` eight
times and handing back a Handle. The launcher recorded `outcome: launched, n_rented: 1` and armed a watchdog
for a host that would never start; `collect` rediscovered the identical error 15-35 minutes later by making
the identical call. The fact was free at rental time and thrown away.

So the difference between the lanes is not what they ask for, it is how much a refusal costs them: a 19-unit
fan-out absorbs one, a 2-unit lane loses its whole tick. The fix is to answer it where it happens.
"""
import dataclasses
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gpu_backend as gb  # noqa: E402

# ⚠ EVERY REFERENCE GOES THROUGH `gb.`, NEVER `from gpu_backend import ...`. `test_gpu_backend.py` calls
# `importlib.reload(gpu_backend)` to exercise the env-driven constants, which REBINDS every class in the
# module — so a name bound here at import time becomes a stale class object, and `pytest.raises` then fails
# to catch an exception that is, by any reading of the log, exactly the one it asked for. Passing alone and
# failing in the full suite is the signature; it cost a debugging round, so it is written down.

MODS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _offer(oid, machine, dph=0.10, gpu="RTX 4090"):
    """One `/search/asks/` row, in the shapes `rank_offers_by_usd_per_ns` actually reads."""
    return {"id": oid, "machine_id": machine, "gpu_name": gpu, "num_gpus": 1, "rentable": True,
            "gpu_ram": 24564, "cpu_ram": 64 * 1024, "cpu_cores": 16, "disk_space": 200,
            "reliability2": 0.99, "cuda_max_good": 13.0, "dph_total": dph, "dph_base": dph,
            "min_bid": dph, "storage_cost": 0.10, "inet_down": 500}


def _spec(**kw):
    res = gb.ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=60,
                          interruptible=True, **kw)
    return gb.JobSpec(name="unit-x", command=["bash", "-lc", "true"], image="img", resources=res,
                      checkpoint_uri="s3://b/ckpt", env={"RESULT_S3": "s3://b/r"})


class _Vast:
    """A scripted Vast API. `refuse` = the set of machine_ids whose start answers resources_unavailable."""

    def __init__(self, offers, refuse=()):
        self.offers, self.refuse = offers, {str(m) for m in refuse}
        self.created, self.deleted, self.calls = [], [], []
        self._by_instance = {}
        self._n = 0

    def __call__(self, method, path, key, params=None, body=None, **kw):
        self.calls.append((method, path))
        if method == "GET" and path == "/search/asks/":
            return {"offers": list(self.offers)}
        if method == "GET" and path == "/instances/":
            return {"instances": [{"id": i, "intended_status": "stopped", "actual_status": "loading"}
                                  for i in self._by_instance]}
        if method == "PUT" and path.startswith("/asks/"):
            self._n += 1
            oid = int(path.split("/")[2])
            mid = str(next(o["machine_id"] for o in self.offers if o["id"] == oid))
            self._by_instance[self._n] = mid
            self.created.append((self._n, mid))
            return {"new_contract": self._n}
        if method == "PUT" and path.startswith("/instances/"):
            iid = int(path.split("/")[2])
            if self._by_instance.get(iid) in self.refuse:
                # THE EXACT BODY VAST RETURNS, copied from run 30458695218 (10:01 AM ET). HTTP 200.
                return {"success": False, "error": "resources_unavailable",
                        "msg": "Required resources are currently unavailable, state change queued."}
            return {"success": True}
        if method == "DELETE" and path.startswith("/instances/"):
            iid = int(path.split("/")[2])
            self._by_instance.pop(iid, None)
            self.deleted.append(iid)
            return {"success": True}
        raise AssertionError(f"unscripted call {method} {path}")


@pytest.fixture
def vast(monkeypatch):
    monkeypatch.setenv("VAST_API_KEY", "k")
    monkeypatch.setattr(gb, "_vast_ondemand_base_by_machine", lambda *_a, **_k: {})
    monkeypatch.setattr(gb, "_object_store_env", lambda: {})
    import time as _t
    monkeypatch.setattr(_t, "sleep", lambda *_a: None)

    def _install(api):
        monkeypatch.setattr(gb, "_vast_request", api)
        return api
    return _install


# =============================================================================================================
# 1. THE DISCRIMINATOR — it is not the ask, and the disk hypothesis is refuted
# =============================================================================================================
def test_the_ternary_ask_is_not_narrower_than_the_fanouts():
    """The prime suspect, refuted as an executable claim rather than as a paragraph.

    If the ternary lane's host filter were stricter on ANY axis, that axis would be a live explanation for
    why it cannot keep a host while the fan-out can. It is stricter on none: the two specs differ in exactly
    one field, and on that field the ternary lane asks for LESS."""
    import congeneric_fanout_vast as cf
    import ternary_vast_launch as tv
    t, s = tv.resource_spec(), cf.FANOUT_RES
    differing = {f.name for f in dataclasses.fields(gb.ResourceSpec)
                 if getattr(t, f.name) != getattr(s, f.name)}
    # `min_cuda` JOINED `disk_gb` ON 2026-07-31, and it is the same shape of difference: the ternary lane
    # asks for LESS. `probe_image_cuda.py` measured `triskit23/ternary-fep` at nvrtc/cudart/cuda-version 12.6,
    # so that lane's floor is now its image's MEASURED requirement; `nr4a3fep` has not been probed yet, so the
    # fan-out keeps `CONSERVATIVE_MIN_CUDA`. The asymmetry is therefore evidence-based and TEMPORARY — it
    # closes the moment the probe runs inside the other image (see `test_image_cuda_floor.py`).
    assert differing == {"disk_gb", "min_cuda"}, (
        "a NEW difference between the two lanes' asks has appeared. Either it is the explanation for a "
        "capacity asymmetry, or it is an accidental divergence — but it must not arrive unremarked: %s"
        % {f: (getattr(t, f), getattr(s, f)) for f in differing})
    assert t.disk_gb < s.disk_gb, "the whole refutation is that ternary asks for LESS disk, not more"
    assert t.min_cuda <= s.min_cuda, "and less driver, never more"
    # ...and the derived Vast query says the same thing: a LOWER floor admits a SUPERSET of hosts.
    qt, qs = gb._vast_offer_query(t), gb._vast_offer_query(s)
    loose = {"disk_space", "cuda_max_good"}
    assert {k: v for k, v in qt.items() if k not in loose} == \
           {k: v for k, v in qs.items() if k not in loose}
    assert qt["disk_space"]["gte"] < qs["disk_space"]["gte"]
    assert qt["cuda_max_good"]["gte"] <= qs["cuda_max_good"]["gte"]


# =============================================================================================================
# 2. THE MECHANISM — the reply was there and was thrown away
# =============================================================================================================
def test_a_refused_start_is_read_from_the_reply_not_inferred_from_the_status(vast):
    """`{"success": false, "error": "resources_unavailable"}` arrives as an ordinary 200 body, so nothing
    raises and nothing in the instance record says `refused` — the status just sits at stopped/loading.
    Reading the reply is the ONLY way to know at rental time."""
    api = _Vast([_offer(1, 111)], refuse={111})
    api._by_instance[1] = "111"                      # a box we already hold, as after a create
    vast(api)
    assert gb.VastBackend()._ensure_running(1, "k", attempts=3, delay_s=0) == "refused"
    # It must not have burned all its attempts discovering something it was told on the first one.
    assert sum(1 for m, p in api.calls if m == "PUT" and p.startswith("/instances/")) == 1


def test_a_healthy_start_still_returns_without_extra_polling(vast):
    """The unchanged path: an accepted start must not become slower or noisier because of the refusal check."""
    api = _Vast([_offer(1, 111)])
    api._by_instance[1] = "111"

    def _patched(method, path, key, params=None, body=None, **kw):
        if method == "GET" and path == "/instances/":
            return {"instances": [{"id": 1, "intended_status": "running", "actual_status": "running"}]}
        return api(method, path, key, params=params, body=body, **kw)
    vast(_patched)
    assert gb.VastBackend()._ensure_running(1, "k", attempts=8, delay_s=0) == "running"


# =============================================================================================================
# 3. THE FIX — pick another host, in the same submit, and destroy the one that refused
# =============================================================================================================
def test_submit_moves_to_another_host_instead_of_returning_a_dead_one(vast):
    """CLAUDE.md §6: a capacity refusal means pick another host — do not queue, do not raise the bid. Before
    this, `submit` returned a Handle for the refused box and the lane discovered it a tick (15-35 min) later."""
    api = vast(_Vast([_offer(1, 111, dph=0.05), _offer(2, 222, dph=0.09)], refuse={111}))
    h = gb.VastBackend().submit(_spec())
    assert str(h.extra["machine_id"]) == "222", "it must land on the host that did NOT refuse"
    assert [m for _i, m in api.created] == ["111", "222"], "cheapest first, then the fallback"
    assert api.deleted == [1], "the refused instance must be destroyed, not left to a later reap"
    assert [r["machine_id"] for r in h.extra["start_refusals"]] == ["111"]


def test_the_refused_machine_is_excluded_only_for_this_submit(vast):
    """A capacity refusal is 'a claim about a MOMENT, not about the host' (trimcrae, 2026-07-27). The
    exclusion must therefore die with the call: the caller's own spec must come back unmutated, so the next
    tick is free to rent the same machine."""
    spec = _spec()
    before = spec.resources.exclude_machine_ids
    vast(_Vast([_offer(1, 111, dph=0.05), _offer(2, 222, dph=0.09)], refuse={111}))
    gb.VastBackend().submit(spec)
    assert spec.resources.exclude_machine_ids == before, \
        "submit mutated the caller's ResourceSpec — that is how a moment becomes a permanent blacklist"


def test_the_retry_is_bounded_and_ends_with_nothing_billing(vast):
    """A board whose every top offer is stale must not turn one unit's submit into an unbounded burst against
    a shared API key (see `_vast_request`'s HTML-403 note). It stops, and every box it touched is destroyed."""
    offers = [_offer(i, 100 + i, dph=0.05 + 0.01 * i) for i in range(1, 7)]
    api = vast(_Vast(offers, refuse={100 + i for i in range(1, 7)}))
    with pytest.raises(gb.CapacityRefusedAtStart) as e:
        gb.VastBackend().submit(_spec())
    assert len(api.created) == gb._VAST_START_REFUSAL_TRIES
    assert sorted(api.deleted) == sorted(i for i, _m in api.created), \
        "every rented box must be destroyed — a refused instance still bills its disk"
    assert len(e.value.refusals) == gb._VAST_START_REFUSAL_TRIES


def test_running_out_of_qualifying_offers_is_also_capacity_not_a_fault(vast):
    """Two hosts, both refuse, `_VAST_START_REFUSAL_TRIES` not yet reached: the loop runs out of BOARD rather
    than of tries. Still nothing running, still $0, still not a defect."""
    api = vast(_Vast([_offer(1, 111), _offer(2, 222)], refuse={111, 222}))
    with pytest.raises(gb.CapacityRefusedAtStart):
        gb.VastBackend().submit(_spec())
    assert sorted(api.deleted) == [1, 2]


# =============================================================================================================
# 4. THE CEILING — a retry is bounded by the SAME approved rate, and nothing here loosens it
# =============================================================================================================
def test_a_replacement_over_the_ceiling_is_refused_rather_than_bought(vast):
    """⚠ THE LOAD-BEARING SAFETY PROPERTY. The gate clears a price and `ResourceSpec.max_usd_per_ns` carries
    it into selection; its own docstring says this must bind 'every fallback after a capacity refusal'. So a
    retry may only ever buy at or under the approved rate — a launcher that answered a refusal by reaching
    for the next-cheapest thing REGARDLESS of price would be a hole straight through the buy line."""
    cheap, dear = _offer(1, 111, dph=0.05), _offer(2, 222, dph=9.99)
    api = vast(_Vast([cheap, dear], refuse={111}))
    ceiling = gb.rank_offers_by_usd_per_ns([cheap], _spec().resources)[0][0][0] * 1.05
    with pytest.raises(gb.NoQualifyingOffer):
        gb.VastBackend().submit(_spec(max_usd_per_ns=ceiling))
    assert [m for _i, m in api.created] == ["111"], "it must not have bought the over-ceiling replacement"
    assert api.deleted == [1]


def test_capacity_refused_is_a_market_condition_not_a_launcher_fault():
    """Both lanes sort exceptions with `isinstance(e, NoQualifyingOffer)` -> 'market' else 'fault'. A host
    declining to schedule us is routine (CLAUDE.md §6), so it must land on the market side without either
    lane needing a new `except` — which is exactly what subclassing buys."""
    assert issubclass(gb.CapacityRefusedAtStart, gb.NoQualifyingOffer)
    e = gb.CapacityRefusedAtStart("x", [{"machine_id": "1"}])
    assert isinstance(e, gb.NoQualifyingOffer) and e.refusals == [{"machine_id": "1"}]


# =============================================================================================================
# 5. THE READOUT — a capacity refusal must never render as a price hold
# =============================================================================================================
def test_the_ledger_has_a_word_for_it_that_is_neither_a_hold_nor_a_fault(tmp_path):
    """The 2026-07-29 morning had two words available and both were false. `refused-on-price` would point a
    reader at a market that read 1.04x basis; `submit-failed` calls a clean provider answer a FAULT."""
    import ternary_launch_ledger as tll
    p = str(tmp_path / "l.json")
    receipt = {"n_requested": 2, "n_rented": 0,
               "failed": [{"unit_id": "u1", "kind": "capacity"}, {"unit_id": "u2", "kind": "capacity"}]}
    tll.record("launched", path=p, receipt=receipt)
    row = tll.last(p)
    assert row["outcome"] == "capacity-refused"
    assert not tll.is_fault(p), "a clean provider answer is not a defect"
    line = tll.summary_line(p)
    assert "⏸ held" not in line and "⛔ FAULT" not in line and "✅" not in line, line
    assert "NOT a price hold" in row["what_that_means"]


def test_one_fault_among_the_refusals_still_dominates(tmp_path):
    """Unchanged precedence: if any unit died on a provider/code error we never got a clean answer from the
    market, so we cannot claim capacity refused us."""
    import ternary_launch_ledger as tll
    p = str(tmp_path / "l.json")
    tll.record("launched", path=p, receipt={"n_requested": 2, "n_rented": 0,
                                            "failed": [{"kind": "capacity"}, {"kind": "fault"}]})
    assert tll.last(p)["outcome"] == "submit-failed" and tll.is_fault(p)


def test_the_launcher_reports_capacity_with_its_own_sentence():
    """Source-level, because the sentence is what a reader at 3 AM acts on: the capacity branch must exist,
    must be green (a `::warning::`, like the price hold — §6 calls this routine), and must NOT reuse the
    price hold's title, which is the misdiagnosis this whole change exists to stop."""
    src = open(os.path.join(MODS, "ternary_vast_launch.py")).read()
    assert 'kind == "capacity"' in src
    assert "TVAST NO CAPACITY" in src
    i, j = src.index("TVAST NO CAPACITY"), src.index("TVAST HELD ON PRICE")
    assert src[min(i, j):max(i, j)].count("::error") == 0, \
        "a capacity refusal must not be red — it is the most routine failure Vast has"


# =============================================================================================================
# 6. THE TREND STAYS A READOUT
# =============================================================================================================
def test_the_launcher_records_the_trend_but_never_consults_it():
    """`capacity_refusal_trend` exists because `vast_machine_blacklist` correctly refuses CLASS_CAPACITY, so
    a sustained availability failure left no durable trace. It may never gate. The launcher now feeds it from
    the rent path as well as from collect — and must still never read a decision back out of it."""
    src = open(os.path.join(MODS, "ternary_vast_launch.py")).read()
    assert "capacity_refusal_trend" in src
    for banned in ("crt.decide", "_crt.decide", "_crt.summarize(", "if _crt", "if crt"):
        assert banned not in src, f"{banned!r}: the trend must not be able to influence a rental"
    # gpu_backend, which owns the retry, must not IMPORT or CALL it — the exclusion there is per-call and
    # dies with the submit. (It may name the module in a comment; a comment cannot gate anything.)
    import ast
    tree = ast.parse(open(os.path.join(MODS, "gpu_backend.py")).read())
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert "capacity_refusal_trend" not in imported, \
        "the retry must not be able to consult a refusal history — that is the durable blacklist that was " \
        "struck down, wearing a different name"


def test_the_refusals_reach_the_caller_so_the_trend_can_see_them(vast):
    """A trend that only counts refusals we FAILED to recover from would under-report exactly when the fix is
    working. The successful path carries its casualties out on the Handle."""
    vast(_Vast([_offer(1, 111, dph=0.05), _offer(2, 222, dph=0.09)], refuse={111}))
    h = gb.VastBackend().submit(_spec())
    assert h.extra["start_refusals"] and h.extra["start_refusals"][0]["why"].startswith("resources_unavailable")
    assert json.dumps(h.extra["start_refusals"])  # must stay JSON-serialisable for the receipt


def test_a_clean_launch_carries_an_empty_refusal_list(vast):
    vast(_Vast([_offer(1, 111)]))
    assert gb.VastBackend().submit(_spec()).extra["start_refusals"] == []
