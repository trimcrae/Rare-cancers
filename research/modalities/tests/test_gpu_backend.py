#!/usr/bin/env python3
"""
Tests for the provider-agnostic GPU harness + the auto-teardown guarantee (no idle GPUs on any provider).
Centerpiece: teardown fires EXACTLY ONCE on success, failure, exception, and watchdog-timeout.

Pure stdlib. Run: python -m pytest research/modalities/tests/test_gpu_backend.py
"""
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
    assert VastBackend().self_terminate_cmd()[:2] == ["vastai", "destroy"]


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


def test_vast_bid_price_is_small_margin_above_floor():
    # bid a small margin ABOVE the floor (min_bid) — cheap, and always runnable
    assert _vast_bid_price({"min_bid": 0.10, "dph_base": 0.30}) == 0.11   # 0.10 * 1.1
    # cheap 3090 host where min_bid == dph_base (no interruptible discount): bid must stay ABOVE min_bid, NOT be
    # capped below it (the below-floor cap left the box created-but-stopped, verified 2026-07-23)
    assert _vast_bid_price({"min_bid": 0.08, "dph_base": 0.08}) == 0.088  # 0.08 * 1.1 >= floor, runnable
    assert _vast_bid_price({"min_bid": 0.24, "dph_base": 0.2933}) == 0.264  # 0.24 * 1.1
    assert _vast_bid_price({"min_bid": 0, "dph_base": 0.30}) == 0.33      # no floor -> fall back to base*1.1
    assert _vast_bid_price({}) is None                            # no pricing -> no bid


def test_vast_selection_ranks_by_min_bid_when_interruptible():
    # A has lower on-demand but higher bid floor; B has higher on-demand but the cheaper bid we'd actually pay
    a = {"id": 1, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.20, "min_bid": 0.18, "gpu_name": "RTX 4090"}
    b = {"id": 2, "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.30, "min_bid": 0.09, "gpu_name": "RTX 4090"}
    res_bid = ResourceSpec(gpu="rtx4090", min_vram_gb=24, interruptible=True)
    assert _select_cheapest_offer([a, b], res_bid)["id"] == 2      # ranks by min_bid -> B is cheaper to run
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
    # the anti-idle guard: an EXIT trap self-destroys the instance on completion/crash/stop (not just a trailing
    # line that a `set -e` abort would skip). It finds THIS instance by its label and DELETEs it via the API.
    assert "trap ct_selfdestroy EXIT" in script
    assert "ct_selfdestroy()" in script and "DELETE" in script and "/api/v0/instances/" in script
    assert "export SELF_LABEL=edgeA" in script


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
    assert "trap ct_selfdestroy EXIT" in script                    # still self-destroys, now on ANY exit


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
