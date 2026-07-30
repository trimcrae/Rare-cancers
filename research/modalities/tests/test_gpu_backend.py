#!/usr/bin/env python3
"""
Tests for the provider-agnostic GPU harness + the auto-teardown guarantee (no idle GPUs on any provider).
Centerpiece: teardown fires EXACTLY ONCE on success, failure, exception, and watchdog-timeout.

Pure stdlib. Run: python -m pytest research/modalities/tests/test_gpu_backend.py
"""
import pytest
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autoteardown import make_subprocess_terminator, run_with_teardown  # noqa: E402
from gpu_backend import (  # noqa: E402
    JobSpec, MockBackend, ModalBackend, ResourceSpec, RunPodBackend, SageMakerBackend, SaladBackend,
    SlurmBackend, VastBackend, _object_store_env, _select_cheapest_offer, _vast_bid_price, _vast_offer_query,
    _vast_onstart, _vast_status, get_backend, pick_cheapest, s3_checkpoint_uri,
)
from object_store import checkpoint_key, completed_units, parse_uri  # noqa: E402


# ---- the anti-idle-GPU guarantee --------------------------------------------------------------------------

def _recorder():
    calls = []
    return calls, (lambda reason: calls.append(reason))


def test_teardown_fires_on_success():
    calls, term = _recorder()
    rc = run_with_teardown(lambda: 0, term, max_runtime_s=100)
    assert rc == 0 and calls == ["job-exit"]              # released on normal exit


def test_teardown_fires_on_nonzero_exit():
    calls, term = _recorder()
    rc = run_with_teardown(lambda: 1, term, max_runtime_s=100)
    assert rc == 1 and calls == ["job-exit"]              # released even when the job failed


def test_teardown_fires_on_exception_and_reraises():
    calls, term = _recorder()
    try:
        run_with_teardown(lambda: (_ for _ in ()).throw(RuntimeError("boom")), term, max_runtime_s=100)
        assert False, "should have re-raised"
    except RuntimeError:
        pass
    assert calls == ["job-exit"]                          # released even on a crash, exception still propagates


def test_teardown_fires_on_watchdog_timeout():
    calls, term = _recorder()

    def slow():
        time.sleep(0.3)                                   # runs past the 0.05s cap
        return 0
    run_with_teardown(slow, term, max_runtime_s=0.05)
    # watchdog fired first (timeout); the later job-exit is suppressed (idempotent) -> exactly one teardown
    assert calls == ["watchdog-timeout"]


def test_teardown_is_idempotent_single_release():
    calls, term = _recorder()
    run_with_teardown(lambda: 0, term, max_runtime_s=100)
    assert len(calls) == 1                                # GPU released once, never twice (no double-bill logic)


# ---- managed vs marketplace: who must self-terminate ------------------------------------------------------

def test_managed_backends_need_no_self_terminate():
    assert SageMakerBackend().self_terminate_cmd() == []  # SageMaker auto-releases
    assert SlurmBackend().self_terminate_cmd() == []      # scheduler releases the node


def test_marketplace_backends_must_self_terminate():
    assert RunPodBackend().self_terminate_cmd()[:2] == ["runpodctl", "remove"]
    # Vast self-terminate is KEY-FREE (2026-07-24): it exits the container to halt GPU billing without any API
    # key on the host (was `vastai destroy`, which needed the key on-host). CI reap does the actual destroy.
    vt = VastBackend().self_terminate_cmd()
    assert vt[:2] == ["bash", "-c"] and "poweroff" in vt[2]
    assert "vastai" not in " ".join(vt) and "VAST_API_KEY" not in " ".join(vt)


def test_managed_terminator_is_noop_marketplace_runs_cmd(capsys):
    make_subprocess_terminator([])("job-exit")            # empty cmd -> no subprocess, just a log line
    out = capsys.readouterr().out
    assert "auto-releases" in out
    # a marketplace terminator would attempt the argv; we only assert it's built (not run here to avoid a
    # real subprocess), covered by the mock-backend cmd shape above.


# ---- routing / cost ---------------------------------------------------------------------------------------

def test_pick_cheapest_prefers_free_hpc_then_marketplace():
    res = ResourceSpec(gpu="any", min_vram_gb=24)
    # with the free allocation available, ACCESS/Slurm win
    assert pick_cheapest(res, backends=["access", "vast", "runpod", "sagemaker"]) == "access"
    # without free HPC, the cheapest marketplace wins (vast rtx3090/4090 < sagemaker)
    assert pick_cheapest(res, backends=["vast", "runpod", "sagemaker"]) == "vast"


def test_salad_is_cheapest_marketplace_but_orchestrator_managed_teardown():
    res = ResourceSpec(gpu="any", min_vram_gb=24)
    # among paid marketplaces (no free HPC), Salad (crowd-sourced consumer GPUs) is the cheapest
    assert pick_cheapest(res, backends=["salad", "vast", "runpod", "sagemaker"]) == "salad"
    # Salad teardown is NOT in-pod self-destruct: self_terminate is empty; the anti-idle guard is
    # orchestrator stop() (scale the container group to 0), which is why stop() is defined for it.
    sb = SaladBackend()
    assert sb.self_terminate_cmd() == []
    try:
        sb.stop(None)                                     # defined (unlike the default) -> NotImplementedError stub
        assert False
    except NotImplementedError:
        pass


def test_supports_and_hourly_usd():
    be = get_backend("runpod")
    assert be.supports(ResourceSpec(gpu="rtx4090", min_vram_gb=24))
    assert be.hourly_usd(ResourceSpec(gpu="rtx4090", min_vram_gb=24)) is not None
    # a 40 GB requirement excludes a 24 GB-only class match on that gpu
    assert not be.supports(ResourceSpec(gpu="rtx4090", min_vram_gb=48))


def test_mock_backend_lifecycle_and_resume_flag():
    be = MockBackend()
    spec = JobSpec(name="edge1", command=["python", "rbfe.py"], resume=True, checkpoint_uri="s3://x/ckpt")
    h = be.submit(spec)
    assert be.status(h) == "running" and h.extra["resume"] is True
    be.complete(h, ok=True)
    assert be.status(h) == "completed"


def test_modal_is_managed_no_idle_by_design():
    # Modal is serverless: auto-scales to zero on return, so like SageMaker it needs no self-terminate.
    assert ModalBackend().self_terminate_cmd() == []
    assert ModalBackend().supports(ResourceSpec(gpu="a10g", min_vram_gb=24))


# ---- object store (stateless-provider checkpoint bridge) --------------------------------------------------

def test_object_store_uri_and_key_layout():
    assert parse_uri("s3://bkt/run/ckpt") == ("bkt", "run/ckpt")
    assert parse_uri("r2://bkt/x/y") == ("bkt", "x/y")            # any S3-compatible scheme
    assert checkpoint_key("run/ckpt", "window_03") == "run/ckpt/units/window_03.ckpt"


def test_completed_units_drives_resume():
    prefix = "run/ckpt"
    keys = [checkpoint_key(prefix, "w0"), checkpoint_key(prefix, "w1"), "run/ckpt/other.log"]
    assert completed_units(keys, prefix) == {"w0", "w1"}          # resume skips these; ignores non-unit objects


# ---- Vast marketplace: cheapest-offer selection + guaranteed self-destroy onstart -------------------------

def test_vast_selects_cheapest_capable_verified_offer():
    offers = [
        {"id": 1, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.45, "rentable": True},   # 24 GB, pricier
        {"id": 2, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.28, "rentable": True},   # 24 GB, CHEAPEST ok
        {"id": 3, "num_gpus": 1, "gpu_ram": 16384, "dph_total": 0.10, "rentable": True},   # too little VRAM
        {"id": 4, "num_gpus": 2, "gpu_ram": 49152, "dph_total": 0.20, "rentable": True},   # multi-GPU excluded
        {"id": 5, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.05, "rentable": False},  # not rentable
    ]
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24)
    chosen = _select_cheapest_offer(offers, res)
    assert chosen["id"] == 2                                       # cheapest that meets VRAM + single-GPU + rentable


def test_vast_bid_price_is_a_staleness_tick_above_the_floor_not_a_multiple():
    """The bid is the market floor plus a small tick — NOT a multiple of it.

    Measured 2026-07-25 (`vast-bid-semantics-probe-ladder.json`): renting one offer at three bid multiples gave
    charged = min(bid, the machine's on-demand price). x1.0 -> $0.00930 charged on a $0.00930 bid; x2.5 and
    x8.0 both -> $0.02133, matching that machine's on-demand dph_base to 17 significant figures. So every cent
    of premium below the cap is spent on every hour, and it buys only partial protection: Vast's docs say
    on-demand renters preempt interruptible ones regardless of bid. The tick exists solely so a quote that
    moves between the search call and the rent call still clears the floor."""
    from vast_cost_model import BID_STALENESS_EPS

    for floor in (0.10, 0.08, 0.24, 0.0147):
        bid = _vast_bid_price({"min_bid": floor, "dph_base": max(floor, 0.30)})
        assert bid > floor, "a bid at or below min_bid can leave the box created-but-stopped"
        assert bid <= floor * (1 + BID_STALENESS_EPS) + 0.0006
        for retired in (1.25, 1.5, 1.9):
            assert bid < floor * retired, f"policy must undercut the retired x{retired} rule"

    # no floor at all -> fall back to the base price, still a tick not a multiple
    assert _vast_bid_price({"min_bid": 0, "dph_base": 0.30}) == 0.306
    assert _vast_bid_price({}) is None                            # no pricing -> no bid


def test_vast_bid_price_is_capped_at_the_machines_real_on_demand_price():
    """Vast enforces this ceiling itself (measured above), but we clamp on our side too: bidding INTO the cap
    still spends real money on every hour up to it, and a bid-type query cannot see the cap at all
    (`dph_base == min_bid` identically in a bid search, so it would be comparing the floor to itself)."""
    # cap binds
    assert _vast_bid_price({"min_bid": 0.2667, "dph_base": 0.2667}, ondemand_base=0.27) == 0.27
    # cap does not bind -> the tick stands
    assert _vast_bid_price({"min_bid": 0.1333, "dph_base": 0.1333}, ondemand_base=0.36) == 0.136


def test_vast_bid_cap_never_drops_the_bid_below_the_floor():
    """THE regression the cap must not reintroduce: an 'always under on-demand' rule once bid BELOW min_bid and
    left the instance created-but-stopped (verified 2026-07-23). Floor wins over the cap, always."""
    assert _vast_bid_price({"min_bid": 0.30, "dph_base": 0.30}, ondemand_base=0.20) == 0.30
    assert _vast_bid_price({"min_bid": 0.08, "dph_base": 0.08}, ondemand_base=0.05) == 0.08
    # a garbage cap is ignored rather than crashing the launch
    assert _vast_bid_price({"min_bid": 0.10, "dph_base": 0.10}, ondemand_base=None) == 0.102
    assert _vast_bid_price({"min_bid": 0.10, "dph_base": 0.10}, ondemand_base="oops") == 0.102


def test_vast_bid_floor_mult_env_var_is_an_escape_hatch_not_the_default():
    """A leg that genuinely cannot tolerate pauses may still want to buy retention, so the override survives —
    but it is OFF unless someone sets it, so the derived policy is what actually runs."""
    import importlib, os
    import gpu_backend
    assert gpu_backend._VAST_BID_FLOOR_MULT is None, "a multiple must not be the default policy"
    os.environ["VAST_BID_FLOOR_MULT"] = "1.9"
    try:
        gb = importlib.reload(gpu_backend)
        assert gb._vast_bid_price({"min_bid": 0.10, "dph_base": 0.30}) == 0.19
    finally:
        del os.environ["VAST_BID_FLOOR_MULT"]
        importlib.reload(gpu_backend)


def test_vast_selection_ranks_by_what_we_would_be_billed_when_interruptible():
    # A has lower on-demand but higher bid floor; B has higher on-demand but the cheaper bid we'd actually pay.
    # Same card, so this isolates the host-price effect — which on the live board spans 5.4x best-to-median and
    # is the single largest lever in the whole policy.
    a = {"id": 1, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.20, "min_bid": 0.18, "gpu_name": "RTX 4090"}
    b = {"id": 2, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.30, "min_bid": 0.09, "gpu_name": "RTX 4090"}
    res_bid = ResourceSpec(gpu="rtx4090", min_vram_gb=24, interruptible=True)
    assert _select_cheapest_offer([a, b], res_bid)["id"] == 2      # cheaper billed rate -> B
    res_od = ResourceSpec(gpu="rtx4090", min_vram_gb=24, interruptible=False)
    assert _select_cheapest_offer([a, b], res_od)["id"] == 1       # on-demand -> ranks by dph_total -> A


def test_vast_offer_query_shape():
    q = _vast_offer_query(ResourceSpec(gpu="rtx4090", min_vram_gb=24, interruptible=True))
    # model is NOT filtered server-side (brittle token -> silent 0 results); chosen client-side instead
    assert "gpu_name" not in q
    assert q["num_gpus"] == {"eq": 1}
    assert q["gpu_ram"] == {"gte": 23 * 1024}                      # 1 GB slack: cards report just under 24*1024
    assert q["type"] == "bid"                                      # interruptible -> cheaper bid tier
    # host constraints (ternary setup is RAM-bound; flaky hosts crash): default ram_gb=16, vcpus=4, disk=40, rel .90
    assert q["cpu_ram"] == {"gte": 16 * 1024} and q["cpu_cores"] == {"gte": 4}
    assert q["disk_space"] == {"gte": 40} and q["reliability2"] == {"gte": 0.90}
    # a ternary-sized spec raises the RAM/disk floors
    qt = _vast_offer_query(ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=80))
    assert qt["cpu_ram"] == {"gte": 32 * 1024} and qt["disk_space"] == {"gte": 80}
    q2 = _vast_offer_query(ResourceSpec(gpu="any", min_vram_gb=16, interruptible=False))
    assert q2["type"] == "on-demand" and q2["gpu_ram"] == {"gte": 15 * 1024}


def test_vast_selection_prefers_requested_model_with_fallback():
    o4090 = {"id": 1, "num_gpus": 1, "gpu_ram": 24564, "dph_total": 0.40, "gpu_name": "RTX 4090"}
    o3090 = {"id": 2, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.20, "gpu_name": "RTX 3090"}
    # cheaper 3090 exists, but a 4090 was requested -> pick the 4090 (soft preference)
    assert _select_cheapest_offer([o4090, o3090], ResourceSpec(gpu="rtx4090", min_vram_gb=24))["id"] == 1
    # no 4090 in the pool -> fall back to the cheapest capable card (the 3090)
    assert _select_cheapest_offer([o3090], ResourceSpec(gpu="rtx4090", min_vram_gb=24))["id"] == 2


def test_vast_offer_selection_respects_price_ceiling_and_none():
    offers = [{"id": 9, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.90, "rentable": True}]
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24)
    assert _select_cheapest_offer(offers, res, max_hourly_usd=0.50) is None   # only offer is over the cap
    assert _select_cheapest_offer([], res) is None                           # empty marketplace


def test_vast_onstart_always_self_destroys():
    spec = JobSpec(name="edgeA", command=["python", "rbfe.py", "--edge", "A"],
                   checkpoint_uri="r2://ckpt/edgeA", resume=True, env={"MODE": "real"})
    script = _vast_onstart(spec, VastBackend().self_terminate_cmd())
    assert "python rbfe.py --edge A" in script
    assert "export RESUME=1" in script and "r2://ckpt/edgeA" in script
    assert "export MODE=real" in script
    # the anti-idle guard: an EXIT trap self-STOPS the instance on completion/crash/stop (not just a trailing
    # line that a `set -e` abort would skip), KEY-FREE — it exits the container (poweroff / kill PID 1) to halt
    # the GPU meter, with NO API key on the host. The guaranteed destroy is control-plane (CI reap).
    assert "trap ct_selfstop EXIT" in script
    assert "ct_selfstop()" in script and "poweroff" in script
    # SECURITY: the account API key must NEVER reach a community host (trimcrae, 2026-07-24). The onstart script
    # must not carry VAST_API_KEY or call the Vast API to self-destroy.
    assert "VAST_API_KEY" not in script
    assert "DELETE" not in script and "/api/v0/instances/" not in script


def test_object_store_env_forwards_only_present_keys():
    src = {"AWS_ACCESS_KEY_ID": "AKIA", "AWS_SECRET_ACCESS_KEY": "sek", "AWS_DEFAULT_REGION": "us-east-2",
           "IRRELEVANT": "x"}
    fwd = _object_store_env(src)
    assert fwd == {"AWS_ACCESS_KEY_ID": "AKIA", "AWS_SECRET_ACCESS_KEY": "sek", "AWS_DEFAULT_REGION": "us-east-2"}
    assert _object_store_env({}) == {}                             # nothing to forward -> empty (no crash)


def test_vast_onstart_forwards_s3_creds_for_reuse():
    spec = JobSpec(name="edgeB", command=["python", "rbfe.py"], checkpoint_uri="s3://bkt/vast/edgeB/ckpt",
                   env={"MODE": "real"})
    creds = {"AWS_ACCESS_KEY_ID": "AKIA", "AWS_SECRET_ACCESS_KEY": "sek", "AWS_DEFAULT_REGION": "us-east-2"}
    script = _vast_onstart(spec, VastBackend().self_terminate_cmd(), extra_env=creds)
    assert "export AWS_ACCESS_KEY_ID=AKIA" in script               # the rented host can now reach the S3 bucket
    assert "export AWS_SECRET_ACCESS_KEY=sek" in script
    assert "export CHECKPOINT_URI=s3://bkt/vast/edgeB/ckpt" in script
    assert "export MODE=real" in script
    assert "trap ct_selfstop EXIT" in script                    # still arms the best-effort self-stop, on ANY exit


def test_vast_onstart_spec_env_overrides_forwarded():
    spec = JobSpec(name="e", command=["true"], env={"AWS_DEFAULT_REGION": "us-west-2"})
    script = _vast_onstart(spec, [], extra_env={"AWS_DEFAULT_REGION": "us-east-2"})
    assert "export AWS_DEFAULT_REGION=us-west-2" in script         # spec.env wins over the forwarded default
    assert "export AWS_DEFAULT_REGION=us-east-2" not in script


def test_s3_checkpoint_uri_builds_prefix(monkeypatch):
    assert s3_checkpoint_uri("valA", bucket="sagemaker-us-east-2-123") == \
        "s3://sagemaker-us-east-2-123/vast/valA/ckpt"
    monkeypatch.setenv("VAST_CKPT_BUCKET", "sagemaker-us-east-2-123")
    assert s3_checkpoint_uri("nrv04").startswith("s3://sagemaker-us-east-2-123/vast/nrv04/")
    monkeypatch.delenv("VAST_CKPT_BUCKET", raising=False)
    try:
        s3_checkpoint_uri("x")
        assert False
    except ValueError:
        pass


def test_vast_status_mapping():
    assert _vast_status("running") == "running"
    assert _vast_status("loading") == "queued"
    assert _vast_status("exited") == "completed"
    assert _vast_status("error") == "failed"
    assert _vast_status(None) == "stopped"


def test_vast_request_follows_deprecation_redirect(monkeypatch):
    import io
    import urllib.error
    import gpu_backend as gb
    calls = []

    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=60):
        calls.append(req.full_url)
        if "/api/v0/instances/" in req.full_url:                   # server says v0 is gone -> names the v1 path
            raise urllib.error.HTTPError(
                req.full_url, 410, "gone", {},
                io.BytesIO(b'{"error":"deprecated_endpoint",'
                           b'"msg":"/api/v0/instances/ is deprecated. Use /api/v1/instances/ instead."}'))
        return _Resp(b'{"instances":[]}')

    monkeypatch.setattr(gb.urllib.request, "urlopen", fake_urlopen)
    out = gb._vast_request("GET", "/instances/", "k", params={"owner": "me"})
    assert out == {"instances": []}                                # transparently succeeded after the follow
    assert any("/api/v1/instances/" in u for u in calls)           # it actually retried the v1 path


def test_vast_submit_needs_key(monkeypatch):
    monkeypatch.delenv("VAST_API_KEY", raising=False)
    try:
        VastBackend().submit(JobSpec(name="x", command=["true"]))
        assert False
    except RuntimeError as e:
        assert "VAST_API_KEY" in str(e)


def test_get_backend_unknown_raises():
    try:
        get_backend("nope")
        assert False
    except KeyError:
        pass


if __name__ == "__main__":
    calls, term = _recorder()
    run_with_teardown(lambda: 0, term, 100)
    print("teardown on success:", calls)


def test_offer_usd_per_ns_uses_measured_throughput_only():
    """$/hr cannot rank hosts carrying different cards — a cheap slow card and a dear fast one look the same.

    Reads the throughput from the table rather than re-typing it: the values were re-anchored 2026-07-27 onto
    a median over N>=3 hosts (pricing.md Appendix T), and this test is about the ARITHMETIC, not the constants
    (which tests/test_throughput_provenance.py pins against their evidence)."""
    import vast_cost_model as _vcm
    from gpu_backend import measured_ns_per_day, offer_usd_per_ns
    assert measured_ns_per_day("NVIDIA GeForce RTX 4090") == _vcm.MEASURED_NS_PER_DAY_84K["RTX4090"]
    assert measured_ns_per_day("NVIDIA GeForce RTX 4080 SUPER") == _vcm.MEASURED_NS_PER_DAY_84K["RTX4080"]
    # never benched -> no number is invented for it
    assert measured_ns_per_day("NVIDIA L4") is None
    assert measured_ns_per_day("Quadro RTX 8000") is None
    assert offer_usd_per_ns("NVIDIA L4", 0.10) is None

    a = offer_usd_per_ns("NVIDIA GeForce RTX 4090", 0.148889)
    b = offer_usd_per_ns("NVIDIA GeForce RTX 3090", 0.102963)
    # Derived from the table, not typed: `$/hr ÷ (ns_day/24)`.
    assert a == pytest.approx(0.148889 / (_vcm.MEASURED_NS_PER_DAY_84K["RTX4090"] / 24.0))
    assert b == pytest.approx(0.102963 / (_vcm.MEASURED_NS_PER_DAY_84K["RTX3090"] / 24.0))
    assert b > a                      # the cheaper $/hr host is still the dearer one per ns


def test_selection_prefers_cheaper_per_ns_over_cheaper_per_hour():
    from gpu_backend import ResourceSpec, _select_cheapest_offer
    cheap_slow = {"id": 1, "num_gpus": 1, "gpu_ram": 24576, "min_bid": 0.103,
                  "dph_total": 0.103, "gpu_name": "NVIDIA GeForce RTX 3090"}
    dearer_fast = {"id": 2, "num_gpus": 1, "gpu_ram": 24576, "min_bid": 0.149,
                   "dph_total": 0.149, "gpu_name": "NVIDIA GeForce RTX 4090"}
    res = ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0)
    assert _select_cheapest_offer([cheap_slow, dearer_fast], res)["id"] == 2


def test_selection_still_captures_the_host_spread_within_one_card():
    """The 2.7x spread across 4090 hosts is the biggest single lever; ranking by $/ns must not lose it."""
    from gpu_backend import ResourceSpec, _select_cheapest_offer
    offers = [{"id": i, "num_gpus": 1, "gpu_ram": 24576, "min_bid": mb, "dph_total": mb,
               "gpu_name": "NVIDIA GeForce RTX 4090"}
              for i, mb in enumerate([0.3550, 0.1333, 0.6000], start=1)]
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24, min_cuda=0.0)
    assert _select_cheapest_offer(offers, res)["min_bid"] == 0.1333


def test_an_unbenched_card_is_taken_only_when_nothing_measured_qualifies():
    from gpu_backend import ResourceSpec, _select_cheapest_offer
    res = ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0)
    l4 = {"id": 9, "num_gpus": 1, "gpu_ram": 24576, "min_bid": 0.01, "dph_total": 0.01, "gpu_name": "NVIDIA L4"}
    m4090 = {"id": 8, "num_gpus": 1, "gpu_ram": 24576, "min_bid": 0.60, "dph_total": 0.60,
             "gpu_name": "NVIDIA GeForce RTX 4090"}
    # a measured card wins even at 60x the $/hr, because the L4 has no trustworthy throughput to rank on
    assert _select_cheapest_offer([l4, m4090], res)["id"] == 8
    assert _select_cheapest_offer([l4], res)["id"] == 9      # ...but it is still usable if it is all there is


def test_price_ceiling_governs_the_billed_rate_not_the_floor():
    """The cost ceiling must be checked against what we are BILLED, not the floor we bid above.

    Measured 2026-07-25: the charge is min(bid, on-demand), so the billed rate is exactly what
    `_vast_bid_price` returns. Comparing max_hourly_usd to min_bid alone let the effective rate run past the
    cap before any offer was rejected — at the old x1.9 with a $0.60 cap that is $1.14/hr, i.e. no ceiling at
    all. That is how the step1 fan-out ran at ~$0.37/hr against a routing estimate of $0.30 with nothing
    complaining. Thresholds here are DERIVED from `_vast_bid_price` so the test survives a policy change and
    only fails if the ceiling genuinely stops governing the billed rate."""
    from gpu_backend import ResourceSpec, _select_cheapest_offer, _vast_bid_price

    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24, interruptible=True)
    cap = 0.60

    def billed(floor):
        return _vast_bid_price({"min_bid": floor, "dph_base": floor})

    # a floor whose BILLED rate lands above the cap must be rejected
    over = 0.75
    assert billed(over) > cap
    pricey = {"id": 1, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.50, "min_bid": over,
              "gpu_name": "RTX 4090"}
    assert _select_cheapest_offer([pricey], res, max_hourly_usd=cap) is None

    # ...and one comfortably under the same ceiling is still selectable
    under = 0.30
    assert billed(under) < cap
    ok = {"id": 2, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.25, "min_bid": under,
          "gpu_name": "RTX 4090"}
    assert _select_cheapest_offer([ok], res, max_hourly_usd=cap)["id"] == 2

    # the boundary sits where the BILLED rate crosses the ceiling, wherever the policy puts that
    lo, hi = 0.30, 0.75
    for _ in range(40):
        mid = (lo + hi) / 2
        if billed(mid) <= cap:
            lo = mid
        else:
            hi = mid
    just_under = {"id": 3, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.40,
                  "min_bid": round(lo - 0.002, 4), "gpu_name": "RTX 4090"}
    just_over = {"id": 4, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.40,
                 "min_bid": round(hi + 0.002, 4), "gpu_name": "RTX 4090"}
    assert _select_cheapest_offer([just_under], res, max_hourly_usd=cap)["id"] == 3
    assert _select_cheapest_offer([just_over], res, max_hourly_usd=cap) is None

    # on-demand offers are billed at dph_total, so their ceiling check is unchanged
    od = ResourceSpec(gpu="rtx4090", min_vram_gb=24, interruptible=False)
    assert _select_cheapest_offer([{"id": 5, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.55,
                                    "gpu_name": "RTX 4090"}], od, max_hourly_usd=cap)["id"] == 5


# ============================================================ transient-network retry on the Vast board read
# 2026-07-27, 2:20 PM ET, run 30292566268. `_vast_request` retried a 403/5xx — an answer we did not like —
# but its only handler was `except HTTPError`. A TIMEOUT raises `URLError`, which is NOT an HTTPError, so it
# fell through and killed the caller on the FIRST attempt. Inverted: a request that got no answer at all is
# more obviously transient than one that got a 403. It cost that tick its collect, hence its reap.

def test_a_timed_out_GET_is_retried_not_fatal(monkeypatch):
    """The board read must survive a transient timeout the same way it survives a transient 403."""
    import io
    import urllib.error
    import gpu_backend as gb
    calls = []

    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=60):
        calls.append(req.full_url)
        if len(calls) < 3:                                          # two timeouts, then the board answers
            raise urllib.error.URLError(TimeoutError("timed out"))
        return _Resp(b'{"instances":[]}')

    monkeypatch.setattr(gb.urllib.request, "urlopen", fake_urlopen)
    import time as _t
    monkeypatch.setattr(_t, "sleep", lambda *_a: None)
    assert gb._vast_request("GET", "/instances/", "k", params={"owner": "me"}) == {"instances": []}
    assert len(calls) == 3, "it must actually have retried, not swallowed the error"


def test_a_timed_out_WRITE_is_NEVER_retried(monkeypatch):
    """A create may have succeeded server-side with only the RESPONSE lost — retrying would double-rent.

    This is the whole reason the retry is GET-only, and it is the expensive direction to get wrong.
    """
    import urllib.error
    import gpu_backend as gb
    calls = []

    def fake_urlopen(req, timeout=60):
        calls.append(req.full_url)
        raise urllib.error.URLError(TimeoutError("timed out"))

    monkeypatch.setattr(gb.urllib.request, "urlopen", fake_urlopen)
    import time as _t
    monkeypatch.setattr(_t, "sleep", lambda *_a: None)
    try:
        gb._vast_request("PUT", "/asks/123/", "k", body={"price": 1})
        raise AssertionError("a timed-out write must fail loudly, never retry")
    except RuntimeError as e:
        assert "unreachable" in str(e)
    assert len(calls) == 1, "a write must be attempted exactly once"


# ── the deadline floor (trimcrae, 2026-07-29: "I just want them all done by the morning") ────────────
# `gpu_class` could not deliver this and the reason is structural: with `require_gpu` unset, `ResourceSpec.gpu`
# is read ONLY by `_select_cheapest_offer`'s unmeasured fallback, so any benched offer sends the decision back
# to the $/ns ranking. T2 ternary was correctly re-placed on the board's best $/ns — an RTX 3090 — whose
# measured 34 s/iter put its ETA ~14 h past its siblings'. The requirement was speed; nothing in the spec
# could say so.

def _o(i, gpu, bid):
    return {"id": i, "num_gpus": 1, "gpu_ram": 24576, "min_bid": bid, "dph_total": bid, "gpu_name": gpu}


def test_a_speed_floor_refuses_the_best_dollar_per_ns_when_it_is_too_slow():
    """The exact 2026-07-29 board shape: the cheap 3090 wins on $/ns and must still be refused."""
    from gpu_backend import ResourceSpec, _select_cheapest_offer
    cheap_slow = _o(1, "NVIDIA GeForce RTX 3090", 0.068)
    dearer_fast = _o(2, "NVIDIA GeForce RTX 5090", 0.229)
    no_floor = ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0)
    assert _select_cheapest_offer([cheap_slow, dearer_fast], no_floor)["id"] == 1, (
        "precondition: without a floor the cheap slow card is correctly the best $/ns")
    floored = ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0, min_ns_per_h=40.0)
    assert _select_cheapest_offer([cheap_slow, dearer_fast], floored)["id"] == 2


def test_the_floor_is_checked_against_the_validated_table_not_a_card_name():
    """One home for card speed (CLAUDE.md §1): the admitted set must follow MEASURED_NS_PER_DAY_84K."""
    import vast_cost_model as _vcm
    from gpu_backend import ResourceSpec, rank_offers_by_usd_per_ns
    names = {"RTX5090": "NVIDIA GeForce RTX 5090", "RTX4090": "NVIDIA GeForce RTX 4090",
             "RTX3090": "NVIDIA GeForce RTX 3090", "RTXA4000": "NVIDIA RTX A4000"}
    offers = [_o(i, n, 0.20) for i, n in enumerate(names.values(), start=1)]
    res = ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0, min_ns_per_h=31.0)
    _, capable = rank_offers_by_usd_per_ns(offers, res)
    got = {o.get("gpu_name") for _, o in capable}
    want = {v for k, v in names.items() if _vcm.MEASURED_NS_PER_DAY_84K[k] / 24.0 >= 31.0}
    assert got == want and want, (got, want)


def test_an_unbenched_card_cannot_clear_a_floor_it_has_no_throughput_for():
    """Same reasoning as max_usd_per_ns: an offer that cannot be shown to clear must not be taken."""
    from gpu_backend import ResourceSpec, _select_cheapest_offer
    l4 = _o(9, "NVIDIA L4", 0.01)
    assert _select_cheapest_offer([l4], ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0))["id"] == 9
    floored = ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0, min_ns_per_h=31.0)
    assert _select_cheapest_offer([l4], floored) is None


def test_the_floor_is_off_by_default_so_no_ordinary_leg_pays_for_speed_it_did_not_ask_for():
    from gpu_backend import ResourceSpec, _select_cheapest_offer
    assert ResourceSpec().min_ns_per_h == 0.0
    cheap_slow = _o(1, "NVIDIA GeForce RTX 3090", 0.068)
    res = ResourceSpec(gpu="any", min_vram_gb=24, min_cuda=0.0)
    assert _select_cheapest_offer([cheap_slow], res)["id"] == 1


def test_the_ternary_lane_reads_the_floor_from_its_env():
    import importlib
    import os
    import ternary_vast_launch as tv
    old = os.environ.get("TVAST_MIN_NS_PER_H")
    try:
        os.environ["TVAST_MIN_NS_PER_H"] = "40"
        assert tv.resource_spec().min_ns_per_h == 40.0
        del os.environ["TVAST_MIN_NS_PER_H"]
        assert tv.resource_spec().min_ns_per_h == 0.0
    finally:
        if old is None:
            os.environ.pop("TVAST_MIN_NS_PER_H", None)
        else:
            os.environ["TVAST_MIN_NS_PER_H"] = old
        importlib.reload(tv)


# ── buying host retention on a churning leg (trimcrae, 2026-07-30) ───────────────────────────────────
# T3 ternary lost hosts repeatedly at ~90% done: ~24-minute host lifetimes delivering ~40 iterations each,
# against 280 iterations remaining — each cold start costing more wall-clock than the MD it bought. The bid
# override is the documented lever ("a specific leg that genuinely cannot tolerate pauses may want to buy
# retention"), and it must stay bounded on both sides.

def test_the_bid_override_is_capped_by_the_real_ondemand_price():
    """On Vast the charge is min(bid, on-demand), so the cap is what stops a raise running away."""
    import importlib
    import os
    import gpu_backend as gb
    old = os.environ.get("VAST_BID_FLOOR_MULT")
    try:
        os.environ["VAST_BID_FLOOR_MULT"] = "1.25"
        importlib.reload(gb)
        offer = {"min_bid": 0.200, "dph_base": 0.200}
        assert gb._vast_bid_price(offer, ondemand_base=0.210) == pytest.approx(0.210), "must cap at on-demand"
        assert gb._vast_bid_price(offer, ondemand_base=0.400) == pytest.approx(0.250), "1.25x under the cap"
        # and never below the floor, whatever the cap says
        assert gb._vast_bid_price(offer, ondemand_base=0.150) == pytest.approx(0.200)
    finally:
        if old is None:
            os.environ.pop("VAST_BID_FLOOR_MULT", None)
        else:
            os.environ["VAST_BID_FLOOR_MULT"] = old
        importlib.reload(gb)


def test_unset_leaves_the_derived_tick_policy_alone():
    import gpu_backend as gb
    assert gb._VAST_BID_FLOOR_MULT is None, "the override must be OFF by default — it is a per-launch lever"


def test_the_chosen_multiple_keeps_both_live_host_classes_under_the_buy_line():
    """1.25x is the largest round multiple that does; 1.35x puts a 1.50x-basis host at 2.03x."""
    import inflight_usd_per_ns as f
    line, basis = f.APPROVED_USD_PER_NS, f.APPROVED_USD_PER_NS / f.drift_multiple()
    for cur in (0.004557, 0.005119):          # T3 ternary's actual 1.34x and 1.50x rentals
        assert cur * 1.25 <= line, "1.25x must stay under the buy line"
        assert (0.005119 * 1.35) > line, "1.35x must NOT — pinning why 1.25 was chosen"
        assert cur / basis < f.drift_multiple()
