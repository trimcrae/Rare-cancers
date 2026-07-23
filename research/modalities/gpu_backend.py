#!/usr/bin/env python3
"""
Provider-agnostic GPU compute backend for the NR4A3 MD/FEP jobs — so the SAME checkpointed job runs on AWS
SageMaker, RunPod, Vast.ai, or an HPC Slurm queue (ACCESS) without rewriting the science, and we can send work
to whichever is cheapest.

THE #1 GOTCHA THIS SOLVES (trimcrae, 2026-07-12): on rented-GPU providers (RunPod/Vast) you keep paying until
the instance is EXPLICITLY destroyed — a job that finishes but leaves its pod up bleeds money on an idle GPU.
SageMaker hides this (auto-releases on exit); a provider-agnostic harness must guarantee it. So every backend
exposes `self_terminate_cmd()` — the command the running job executes to destroy ITS OWN instance — and
`autoteardown.run_with_teardown` runs it in a finally-block + a watchdog, so the GPU is released on completion,
failure, OR timeout, on every provider. Managed backends (SageMaker, Slurm) return an empty command because the
platform already auto-releases.

Design goals: (1) per-unit checkpoint/resume to a provider-agnostic object store (already how our jobs work, so
a flaky-but-cheap marketplace is safe); (2) no idle GPUs anywhere; (3) pick-the-cheapest routing. The core +
MockBackend are pure-stdlib and unit-tested; the real adapters guard on missing SDK/creds so they fail loudly
off-provider rather than silently.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---- job / resource spec ----------------------------------------------------------------------------------

@dataclass
class ResourceSpec:
    gpu: str = "any"              # logical class: rtx4090 | rtx3090 | a10g | l4 | l40s | a100 | any
    min_vram_gb: int = 16         # MD complex legs fit comfortably in 16-24 GB (single-GPU)
    vcpus: int = 4
    ram_gb: int = 16              # host RAM floor (ternary setup/staging is RAM-bound: needs >=32 GB)
    disk_gb: int = 40             # host disk floor (container + trajectories/checkpoints)
    min_reliability: float = 0.90  # skip flaky hosts (Vast reliability2 in [0,1]); preemption we tolerate, crashes we don't
    interruptible: bool = True    # our per-unit checkpointing tolerates interruption -> take the cheap (bid) tier
    min_cuda: float = 12.6        # host DRIVER's cuda_max_good must be >= this. We PIN the conda env to
                                  # cuda-version=12.6 (fusion-cpu-extras build_env) so OpenMM's CUDA-plugin PTX is
                                  # 12.6 — backward-compatible with essentially every modern Vast host driver.
                                  # (Filtering for bleeding-edge drivers failed: even cuda_max_good>=13.0 hosts
                                  # PTX-crashed because the *unpinned* env pulled a too-new CUDA-13+ OpenMM, verified
                                  # 2026-07-23. Controlling OUR build is the robust fix; this floor just excludes the
                                  # rare <12.6 host.)


@dataclass
class JobSpec:
    name: str
    command: list                 # argv the container runs (the real MD/FEP driver)
    image: str = ""               # container image / provider template
    inputs: dict = field(default_factory=dict)      # name -> object-store URI (structures, prior ckpts)
    checkpoint_uri: str = ""      # object-store prefix; per-unit checkpoints upload here continuously
    resume: bool = True           # download prior checkpoints on start (re-dispatch or interruption resume)
    resources: ResourceSpec = field(default_factory=ResourceSpec)
    max_runtime_s: int = 72000    # hard cap; the watchdog tears the instance down if exceeded (anti-idle)
    env: dict = field(default_factory=dict)


@dataclass
class Handle:
    backend: str
    job_id: str
    extra: dict = field(default_factory=dict)


# ---- capability + (approximate) price tables --------------------------------------------------------------
# hourly_usd are ORDER-OF-MAGNITUDE 2026 estimates for right-sizing/routing decisions ONLY — live prices come
# from each provider's API at submit time. Marketplace prices float; treat these as "which tier is cheaper",
# not billing. Managed-HPC (access/slurm) is 0 because it runs on a granted allocation.
_CAPS = {  # backend -> {gpu -> (vram_gb, approx_usd_per_hr)}   (usd = interruptible/community tier where it exists)
    "sagemaker": {"a10g": (24, 0.40), "l4": (24, 0.30), "l40s": (48, 0.80)},   # + SageMaker mgmt premium
    "runpod":    {"rtx4090": (24, 0.44), "a10g": (24, 0.40), "l4": (24, 0.43),
                  "l40s": (48, 0.79), "a100": (80, 1.19)},
    "vast":      {"rtx4090": (24, 0.30), "rtx3090": (24, 0.22), "a10g": (24, 0.30), "a100": (80, 0.80)},
    "salad":     {"rtx4090": (24, 0.20), "rtx3090": (24, 0.12), "rtx4080": (16, 0.15)},  # crowd-sourced, cheapest
    "modal":     {"l4": (24, 0.80), "a10g": (24, 1.10), "a100": (40, 2.10)},  # serverless premium, but auto-scales
                 #                                                              to zero (no idle) + free monthly credits
    "gcp":       {"t4": (16, 0.11), "l4": (24, 0.20), "a100": (40, 1.10)},   # Compute Engine SPOT VMs; $300 trial
                 #                                                            credit funds these (see catch below)
    "oci":       {"a10": (24, 1.27), "a10g": (24, 1.27), "a100": (40, 4.00), "l40s": (48, 3.50)},  # $300 30-day
                 #   trial credit; A10 on-demand (no cheap GPU spot) -> a ONE-WINDOW burn, not a standing tier
    "access":    {"a100": (40, 0.0), "a10g": (24, 0.0), "l40s": (48, 0.0)},     # NSF allocation -> $0
    "slurm":     {"a100": (40, 0.0), "any": (24, 0.0)},                          # self-hosted / institutional
    "mock":      {"any": (24, 0.0)},
}


def _match_gpu(caps: dict, res: ResourceSpec):
    """Return (gpu_key, vram, usd) for the cheapest capable GPU on a backend, or None."""
    best = None
    for gpu, (vram, usd) in caps.items():
        if vram < res.min_vram_gb:
            continue
        if res.gpu not in ("any", gpu) and gpu != "any":
            continue
        if best is None or usd < best[2]:
            best = (gpu, vram, usd)
    return best


# ---- backend interface ------------------------------------------------------------------------------------

class Backend(ABC):
    name = "abstract"

    def supports(self, res: ResourceSpec) -> bool:
        return _match_gpu(_CAPS.get(self.name, {}), res) is not None

    def hourly_usd(self, res: ResourceSpec):
        m = _match_gpu(_CAPS.get(self.name, {}), res)
        return None if m is None else m[2]

    @abstractmethod
    def self_terminate_cmd(self) -> list:
        """argv the RUNNING JOB executes to destroy its OWN instance (the anti-idle-GPU guard). Empty list =>
        the platform auto-releases on exit (SageMaker, Slurm), so no self-termination is needed."""

    @abstractmethod
    def submit(self, spec: JobSpec) -> Handle: ...

    @abstractmethod
    def status(self, handle: Handle) -> str:  # queued | running | completed | failed | stopped
        ...

    def stop(self, handle: Handle) -> None:   # external stop (optional)
        raise NotImplementedError


# ---- managed backends: platform auto-releases (no self-terminate needed) -----------------------------------

class SageMakerBackend(Backend):
    name = "sagemaker"

    def self_terminate_cmd(self):
        return []                              # managed: instance auto-released when the training job exits

    def submit(self, spec: JobSpec) -> Handle:
        # reuse the existing sagemaker_submit.submit_spot path; guarded so it fails loudly off-AWS.
        try:
            import sagemaker  # noqa: F401
        except ImportError:
            raise RuntimeError("sagemaker backend needs the sagemaker SDK + AWS creds (run on AWS/CI).")
        raise NotImplementedError("wire to sagemaker_submit.submit_spot (existing infra) at integration time")

    def status(self, handle):
        raise NotImplementedError


class SlurmBackend(Backend):
    """HPC scheduler (e.g. an ACCESS resource: Anvil/Delta/Expanse). The scheduler releases the node when the
    batch job ends, so like SageMaker there is nothing to self-terminate — just respect the walltime."""
    name = "slurm"

    def self_terminate_cmd(self):
        return []                              # scheduler releases the node at job end / walltime

    def submit(self, spec: JobSpec) -> Handle:
        raise NotImplementedError("emit an sbatch script (walltime=max_runtime_s) + srun the command")

    def status(self, handle):
        raise NotImplementedError


# ---- rented-GPU marketplaces: MUST self-terminate or the GPU idles on the meter --------------------------

class RunPodBackend(Backend):
    name = "runpod"

    def self_terminate_cmd(self):
        # kill this pod from inside it; RUNPOD_POD_ID is injected by RunPod into the container env.
        return ["runpodctl", "remove", "pod", os.environ.get("RUNPOD_POD_ID", "$RUNPOD_POD_ID")]

    def submit(self, spec: JobSpec) -> Handle:
        if not os.environ.get("RUNPOD_API_KEY"):
            raise RuntimeError("runpod backend needs RUNPOD_API_KEY (create a RunPod account first).")
        raise NotImplementedError("POST pod-create via RunPod GraphQL API at integration time")

    def status(self, handle):
        raise NotImplementedError


# ---- Vast.ai marketplace helpers (pure logic + a thin urllib client) --------------------------------------
_VAST_HOST = "https://console.vast.ai"                             # version prefix added per-request (see below)


def _vast_url(path: str) -> str:
    """Resolve a request path against the host. An absolute '/api/vN/...' path (as returned in Vast's own
    deprecation redirects) is used verbatim; a bare '/instances/' defaults to the v0 prefix."""
    return _VAST_HOST + (path if path.startswith("/api/") else "/api/v0" + path)

# our logical GPU class -> a substring matched CLIENT-SIDE against the offer's gpu_name (spaces stripped,
# upper-cased). We do NOT filter the model server-side: Vast's `gpu_name` eq-token format is version-specific
# and a wrong token silently returns zero offers (confirmed by the smoke bisect: gpu_name=RTX_4090 -> 0 while
# the same query without it -> 55). Client-side substring match is robust and falls back to any capable card.
_VAST_GPU_SUBSTR = {
    "rtx4090": "4090", "rtx3090": "3090", "rtx4080": "4080",
    "a10g": "A10", "a100": "A100", "l40s": "L40S", "l4": "L4",
    "rtx8000": "8000", "a6000": "A6000", "a5000": "A5000",   # 24-48GB alternates for the $/ns bench
}


def _vast_request(method: str, path: str, api_key: str, params=None, body=None, _hops: int = 0):
    """Thin JSON client for the Vast REST API. Isolated so tests monkeypatch it; the callers' logic is pure.
    SELF-HEALING against Vast's v0->v1 migration: on a 410 `deprecated_endpoint` the body names the replacement
    ("Use /api/v1/instances/ instead"), so we follow it once instead of hard-failing (keeps the adapter working
    as endpoints move without hardcoding a version per route)."""
    url = _vast_url(path)
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:                            # surface the provider's error body, not a bare 4xx
        detail = e.read().decode()
        if e.code == 410 and _hops < 3:                           # follow the server's own "Use <path> instead"
            m = re.search(r"Use\s+(/api/\S+?)\s+instead", detail)
            if m:
                return _vast_request(method, m.group(1), api_key, params=params, body=body, _hops=_hops + 1)
        raise RuntimeError(f"vast API {method} {path} -> {e.code}: {detail[:400]}") from e


def _vast_offer_query(res: ResourceSpec) -> dict:
    """PURE: the Vast `/bundles/` search query for a single-GPU leg meeting `res` (shared by submit + the smoke,
    so they can't drift). Verified + rentable hosts only; interruptible => cheaper 'bid' tier (our per-unit
    checkpointing tolerates preemption)."""
    # NB: no server-side gpu_name filter (see _VAST_GPU_SUBSTR) — the model is chosen client-side. VRAM floor is
    # relaxed by ~1 GB because cards report just under the round number (a 4090 shows ~24564 MB, not 24576).
    # Host RAM/cores/disk/reliability ARE filtered (ternary setup is RAM-bound; flaky hosts crash, which — unlike
    # preemption — we do not tolerate). gpu_ram/cpu_ram are MB.
    return {
        "verified": {"eq": True},
        "rentable": {"eq": True},
        "num_gpus": {"eq": 1},
        "gpu_ram": {"gte": max(0, (res.min_vram_gb - 1)) * 1024},
        "cpu_ram": {"gte": res.ram_gb * 1024},
        "cpu_cores": {"gte": res.vcpus},
        "disk_space": {"gte": res.disk_gb},
        "reliability2": {"gte": res.min_reliability},
        "cuda_max_good": {"gte": res.min_cuda},   # host driver must support our OpenMM CUDA plugin's PTX (else PTX-version error)
        "order": [["dph_total", "asc"]],
        "type": "bid" if res.interruptible else "on-demand",
    }


# INTERRUPTIBLE BID = a small margin above the market FLOOR (min_bid), never above on-demand. On Vast you pay
# your bid, so bidding 1.25x the on-demand base (the old rule) meant paying MORE than on-demand — defeating the
# whole point of interruptible. That was an over-correction to mid-boot preemptions back when boot was the ~25-min
# conda solve; now the env is BAKED (~3-min boot) and every unit checkpoints, so a preemption costs only a short
# re-boot we absorb via re-dispatch/resume (the "spot preemptions are routine" rule). So bid low and, if a host
# preempts us, wait it out / re-dispatch — do NOT bid up toward on-demand. Tunable via env for a contested run.
_VAST_BID_FLOOR_MULT = float(os.environ.get("VAST_BID_FLOOR_MULT", "1.1"))   # small margin above min_bid to win+hold


def _vast_bid_price(offer: dict):
    """Interruptible bid $/hr = a small margin ABOVE the market floor (min_bid) so the box reliably wins a slot and
    holds. It MUST stay >= min_bid: a below-floor bid leaves the instance created-but-stopped (verified 2026-07-23
    — an 'always under on-demand' cap fell BELOW min_bid on cheap 3090 hosts where min_bid==dph_base, so the box
    never started). On Vast you pay your bid and min_bid IS the interruptible market price, so floor*1.1 is both
    cheap and reliable. (Selection already ranks by min_bid, so we never land on an expensive-floor host.) PURE."""
    try:
        floor = float(offer.get("min_bid") or 0.0)
        base = float(offer.get("dph_base") or offer.get("dph_total") or 0.0)
    except (TypeError, ValueError):
        return None
    ref = floor if floor > 0 else base
    if ref <= 0:
        return None
    return round(max(ref * _VAST_BID_FLOOR_MULT, 0.001), 4)


def _vast_gpu_ram_gb(offer: dict) -> float:
    """Vast reports per-GPU RAM in MB; be tolerant of an already-GB value on older payloads."""
    ram = float(offer.get("gpu_ram", 0) or 0)
    return ram / 1024.0 if ram > 1000 else ram


def _select_cheapest_offer(offers, res: ResourceSpec, max_hourly_usd=None):
    """PURE: cheapest single-GPU, rentable offer meeting the VRAM (and optional price) constraint, preferring the
    requested GPU model (client-side substring) but FALLING BACK to any capable card if that model isn't offered.
    Ranked by the price we'd actually PAY: the interruptible bid floor (min_bid) when res.interruptible, else the
    on-demand total. Returns the chosen offer dict, or None if nothing qualifies."""
    capable = []
    for o in offers:
        try:
            if res.interruptible and o.get("min_bid") is not None:
                price = float(o.get("min_bid"))                    # rank bid offers by their true interruptible cost
            else:
                price = float(o.get("dph_total", o.get("dph_base", 1e9)))
            ngpu = int(o.get("num_gpus", 1) or 1)
        except (TypeError, ValueError):
            continue
        if o.get("rentable") is False:
            continue
        if ngpu != 1:                                             # one GPU per leg (multi-GPU costs more, no gain)
            continue
        if _vast_gpu_ram_gb(o) + 0.5 < res.min_vram_gb:          # 0.5 GB slack for reporting rounding
            continue
        try:                                                     # host driver must run our OpenMM CUDA plugin's PTX
            cmg = float(o.get("cuda_max_good") or 0.0)
        except (TypeError, ValueError):
            cmg = 0.0
        if cmg and cmg + 1e-6 < res.min_cuda:                    # 0 = field absent -> don't over-filter, trust server query
            continue
        if max_hourly_usd is not None and price > max_hourly_usd:
            continue
        capable.append((price, o))
    if not capable:
        return None
    substr = _VAST_GPU_SUBSTR.get(res.gpu)                        # prefer the requested model, else any capable
    if substr:
        preferred = [(p, o) for p, o in capable
                     if substr in str(o.get("gpu_name", "")).replace(" ", "").upper()]
        capable = preferred or capable
    return min(capable, key=lambda po: po[0])[1]


def _vast_status(actual: str, cur_state: str = None) -> str:
    """Map Vast's instance status to our vocabulary: queued | running | completed | failed | stopped."""
    a = (actual or cur_state or "").lower()
    if a in ("running",):
        return "running"
    if a in ("loading", "created", "scheduling", "starting"):
        return "queued"
    if a in ("exited", "finished", "success"):
        return "completed"
    if a in ("error", "failed"):
        return "failed"
    return "stopped"                                             # offline/stopped/destroyed


# Env forwarded into a rented instance so its job container can read/write the checkpoint bucket. For "reuse
# S3" this carries the AWS keys + region; if OBJECT_STORE_ENDPOINT is set (R2/B2) it rides along too, so the
# same code path serves any S3-compatible store. SECURITY: a rented community host is UNTRUSTED — set these
# from a **bucket-scoped IAM key** (s3:GetObject/PutObject/ListBucket on just the checkpoint prefix), never a
# broad/admin AWS key. See cheap-gpu-plan.md.
_OBJECT_STORE_ENV_KEYS = (
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_DEFAULT_REGION",
    "OBJECT_STORE_ENDPOINT", "OBJECT_STORE_REGION",
)


def _object_store_env(source_env=None) -> dict:
    """Collect the checkpoint-store credentials/config present in the environment, to forward into the instance
    so its job container can reach the bucket (reuse-S3 = the AWS keys). PURE (reads a dict) -> unit-tested."""
    env = source_env if source_env is not None else os.environ
    return {k: env[k] for k in _OBJECT_STORE_ENV_KEYS if env.get(k)}


def s3_checkpoint_uri(job_name: str, bucket: str = None, prefix: str = "vast") -> str:
    """Build a per-job checkpoint prefix on the REUSED S3 bucket (the one the AWS jobs already use). `bucket`
    defaults to $VAST_CKPT_BUCKET (e.g. the SageMaker default bucket, sagemaker-us-east-2-<acct>). A campaign
    launcher sets JobSpec.checkpoint_uri to this so each leg checkpoints per-unit and resumes after preemption."""
    bucket = bucket or os.environ.get("VAST_CKPT_BUCKET")
    if not bucket:
        raise ValueError("s3_checkpoint_uri needs a bucket (arg or $VAST_CKPT_BUCKET)")
    return f"s3://{bucket}/{prefix}/{job_name}/ckpt"


# Self-destroy on ANY exit: a bash EXIT trap that finds THIS instance by its unique label via the Vast REST API
# (key forwarded in $VAST_API_KEY) and DELETEs it. The trap fires on success, on a crash, AND on a `set -e`
# abort — so a job that FAILS or STOPS kills its own GPU immediately instead of idling on the meter (the earlier
# `vastai destroy`/mock path silently no-op'd, leaving crashed VMs bleeding). Uses curl + python3, both present
# on the baked image. SECURITY: forwarding VAST_API_KEY to a community host is a real exposure (it can spend the
# account's credit) — accepted here for guaranteed teardown; rotate the key after a campaign. The CI-side
# collect backstop (key stays on CI) is the second layer.
_VAST_SELFDESTROY = (
    'ct_selfdestroy(){ rc=$?; [ -n "$VAST_API_KEY" ] || return $rc; '
    'mid=$(curl -s -H "Authorization: Bearer $VAST_API_KEY" "https://console.vast.ai/api/v0/instances/?owner=me" '
    "| python3 -c 'import sys,json,os"
    "\nd=json.load(sys.stdin)"
    "\nprint(next((str(i[\"id\"]) for i in d.get(\"instances\",[]) if i.get(\"label\")==os.environ.get(\"SELF_LABEL\")),\"\"))' 2>/dev/null); "
    '[ -n "$mid" ] && curl -s -X DELETE -H "Authorization: Bearer $VAST_API_KEY" '
    '"https://console.vast.ai/api/v0/instances/$mid/" >/dev/null 2>&1; return $rc; }'
)


def _vast_onstart(spec: JobSpec, self_terminate_argv, extra_env=None) -> str:
    """Build the instance onstart script: export the resume/checkpoint context (+ forwarded object-store creds +
    VAST_API_KEY), arm a self-destroy EXIT trap so the instance is torn down on completion/crash/stop (never
    idles on the meter — the #1 gotcha), then run the job command. `extra_env` is merged UNDER spec.env (spec.env
    wins). PURE (no I/O) -> unit-tested."""
    cmd = " ".join(shlex.quote(a) for a in spec.command)
    env = {**(extra_env or {}), **spec.env}
    lines = ["#!/bin/bash", "set -o pipefail",
             f"export CHECKPOINT_URI={shlex.quote(spec.checkpoint_uri)}",
             f"export RESUME={'1' if spec.resume else '0'}",
             f"export SELF_LABEL={shlex.quote(spec.name)}"]      # the trap finds this instance by its label
    lines += [f"export {k}={shlex.quote(str(v))}" for k, v in env.items()]
    lines += [_VAST_SELFDESTROY, "trap ct_selfdestroy EXIT", cmd]
    return "\n".join(lines)


class VastBackend(Backend):
    """Vast.ai — a MARKETPLACE of independent, individually-rentable GPU hosts (each rental is its OWN machine),
    which is exactly why it breaks the single-shared-pool wall-clock ceiling that a single-region cloud (GCP
    us-central1 Spot L4 pool) hits: N legs = N independent instances, genuinely N-wide with no shared-quota
    bottleneck. On our MD/FEP workload (memory-bandwidth-bound PME) the marketplace's RTX 4090s (1008 GB/s) are
    the a-priori cheapest $/ns. The catch is the PROVIDER not the card: community hosts are interruptible and can
    vanish, and — the #1 gotcha — a finished job that leaves its instance UP bleeds money on an idle GPU, so the
    instance MUST self-destroy. Two guards: (1) autoteardown's finally+watchdog runs `self_terminate_cmd()` on
    success/failure/timeout; (2) the onstart script appends the same destroy as a belt-and-braces backstop.

    NOTE (must smoke before a fleet): the exact Vast REST endpoints/query schema drift between API versions; the
    LOAD-BEARING logic — cheapest-verified-offer selection and the guaranteed-self-destroy onstart — is factored
    into pure, unit-tested helpers (`_select_cheapest_offer`, `_vast_onstart`), so a one-instance smoke only has
    to confirm the HTTP shapes, not the science."""
    name = "vast"

    def self_terminate_cmd(self):
        # destroy this instance from inside it; the instance id is in the env Vast injects.
        return ["vastai", "destroy", "instance", os.environ.get("VAST_INSTANCE_ID", "$VAST_INSTANCE_ID")]

    def submit(self, spec: JobSpec) -> Handle:
        key = os.environ.get("VAST_API_KEY")
        if not key:
            raise RuntimeError("vast backend needs VAST_API_KEY (create a Vast.ai account first).")
        res = spec.resources
        q = _vast_offer_query(res)
        offers = _vast_request("GET", "/search/asks/", key,
                               params={"q": json.dumps(q)}).get("offers", [])
        max_hr = self.hourly_usd(res)                              # cap at our routing estimate + headroom
        offer = _select_cheapest_offer(offers, res,
                                       max_hourly_usd=(max_hr * 2.0 if max_hr else None))
        if offer is None:
            raise RuntimeError(f"vast: no rentable verified offer for {res} (of {len(offers)} offers)")
        # Forward the checkpoint-store creds (reuse-S3 = the AWS keys) AND VAST_API_KEY (so the self-destroy EXIT
        # trap can DELETE this instance on completion/crash/stop) into the rented host.
        extra = dict(_object_store_env())
        extra["VAST_API_KEY"] = key
        onstart = _vast_onstart(spec, self.self_terminate_cmd(), extra_env=extra)
        # Rent the chosen ask: PUT /asks/{id}/ is Vast's canonical create-instance endpoint (POST /instances/
        # 404s). On success the body carries new_contract = the instance id.
        body = {
            "client_id": "me",
            "image": spec.image or "nvidia/cuda:12.4.1-base-ubuntu22.04",
            "disk": max(40, res.disk_gb),
            "onstart": onstart,
            "runtype": "ssh",
            "label": spec.name,
            "target_state": "running",
        }
        if res.interruptible:                                     # interruptible => set an optimized bid $/hr
            bid = _vast_bid_price(offer)
            if bid is not None:
                body["price"] = bid
        created = _vast_request("PUT", f"/asks/{offer['id']}/", key, body=body)
        inst_id = created.get("new_contract") or created.get("id")
        if inst_id is None:
            raise RuntimeError(f"vast: instance create returned no id: {created}")
        # ROBUST EXPLICIT START: creating the ask does NOT reliably launch the container — diag showed 3/4 created
        # instances stuck at intended_status="stopped" (cpu 0%, no capacity msg) while a 4th ran, SAME code: the
        # start PUT races Vast finishing the create, so on some hosts it's lost and the box sits stopped forever.
        # Poll and re-issue the start until Vast reports it running (intended_status flips), bounded.
        self._ensure_running(inst_id, key)
        return Handle(backend=self.name, job_id=str(inst_id),
                      extra={"offer": offer["id"], "dph": offer.get("dph_total"), "resume": spec.resume})

    def _ensure_running(self, inst_id, key, attempts=8, delay_s=6):
        """Re-issue PUT state=running until the instance's intended_status/actual_status is 'running' (fixes the
        create/start race that leaves bid instances stuck 'stopped'). Bounded; logs the final state."""
        import time
        for i in range(attempts):
            try:
                _vast_request("PUT", f"/instances/{inst_id}/", key, body={"state": "running"})
            except Exception as e:  # noqa: BLE001 — a transient error shouldn't abort the retry loop
                print(f"[vast] start {inst_id} attempt {i + 1}: {e}", flush=True)
            inst = next((x for x in _vast_request("GET", "/instances/", key, params={"owner": "me"})
                         .get("instances", []) if str(x.get("id")) == str(inst_id)), None)
            intended, actual = (inst or {}).get("intended_status"), (inst or {}).get("actual_status")
            print(f"[vast] start {inst_id} attempt {i + 1}: intended={intended} actual={actual}", flush=True)
            if intended == "running" or actual == "running":
                return
            time.sleep(delay_s)
        print(f"[vast] WARN {inst_id} did not reach intended=running after {attempts} attempts", flush=True)

    def status(self, handle: Handle) -> str:
        key = os.environ.get("VAST_API_KEY")
        if not key:
            raise RuntimeError("vast backend needs VAST_API_KEY.")
        resp = _vast_request("GET", "/instances/", key, params={"owner": "me"})
        for inst in resp.get("instances", []):
            if str(inst.get("id")) == str(handle.job_id):
                return _vast_status(inst.get("actual_status"), inst.get("cur_state"))
        return "stopped"                                           # gone from the list => destroyed/terminated

    def stop(self, handle: Handle) -> None:
        key = os.environ.get("VAST_API_KEY")
        if not key:
            raise RuntimeError("vast backend needs VAST_API_KEY.")
        _vast_request("DELETE", f"/instances/{handle.job_id}/", key)


class SaladBackend(Backend):
    """SaladCloud — crowd-sourced consumer GPUs (gamers' idle PCs); typically the CHEAPEST tier, but the
    HIGHEST churn (a node drops the instant its owner uses the PC). Lifecycle is ORCHESTRATOR-MANAGED: you run
    a Container Group of N replicas and Salad reclaims/replaces nodes; a node cannot meaningfully self-destruct,
    so self_terminate_cmd is EMPTY. The anti-idle-GPU guard therefore lives at the CONTROL PLANE — the
    orchestrator MUST stop() the container group (scale to 0 / delete via the Salad API) when the work queue
    drains, else the group keeps billing replicas. Best fit: the many SHORT triage rungs, where high preemption
    + our per-unit checkpointing cancel out; NOT ideal for the few long full-sampling terminal legs, where
    frequent preemption forces repeated MD-env/system reloads that can eat the price advantage (see the
    env-load economics, design doc 7b)."""
    name = "salad"

    def self_terminate_cmd(self):
        return []                              # node can't self-destroy; teardown = orchestrator stop() below

    def submit(self, spec: JobSpec) -> Handle:
        if not os.environ.get("SALAD_API_KEY"):
            raise RuntimeError("salad backend needs SALAD_API_KEY + org/project (create a SaladCloud account).")
        raise NotImplementedError("create a Container Group via the Salad API at integration time")

    def stop(self, handle: Handle) -> None:
        # THE anti-idle guard for Salad: the orchestrator scales the group to 0 / deletes it when done.
        raise NotImplementedError("DELETE/scale the Salad container group to 0 via the Salad API")

    def status(self, handle):
        raise NotImplementedError


class GCPBackend(Backend):
    """Google Compute Engine GPU VMs — funded by the $300 free-trial credit. NOT serverless: a raw GCE VM
    **bills every second it is up**, so like the marketplaces it MUST self-terminate or it idles on the meter.
    The guard is a VM that deletes ITSELF at job end: `gcloud compute instances delete <name> --zone <zone>`.
    Name+zone come from the instance metadata server; a startup script exports them as GCP_INSTANCE_NAME/GCP_ZONE
    so this static argv resolves. Auth is a SERVICE-ACCOUNT JSON key (NOT a Gemini/AI-Studio API key — a
    different product) via GOOGLE_APPLICATION_CREDENTIALS. Two real catches (documented in cheap-gpu-plan.md):
    (1) new accounts have GPU quota = 0 and Google blocks GPU-quota grants while on the free trial, so you must
    upgrade to a paid (still credit-funded) account and request quota before any GPU VM launches; (2) use SPOT
    (preemptible) VMs for the price in _CAPS — our per-unit checkpointing makes preemption safe. Best fit: the
    $300 credit is the reserve for the few long terminal MD legs where L4/A100 pricing beats Modal's serverless
    premium; keep Modal for free validation/triage."""
    name = "gcp"

    def self_terminate_cmd(self):
        # delete THIS VM from inside it; startup script exports name/zone from the metadata server.
        return ["gcloud", "compute", "instances", "delete",
                os.environ.get("GCP_INSTANCE_NAME", "$GCP_INSTANCE_NAME"),
                "--zone", os.environ.get("GCP_ZONE", "$GCP_ZONE"), "--quiet"]

    def submit(self, spec: JobSpec) -> Handle:
        if not (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GCP_SA_KEY")):
            raise RuntimeError("gcp backend needs a service-account JSON key "
                               "(GOOGLE_APPLICATION_CREDENTIALS or GCP_SA_KEY) + a project with GPU quota.")
        raise NotImplementedError(
            "create a Spot GCE VM (accelerator + startup script running the command, then self_terminate_cmd) "
            "via the Compute Engine API at integration time")

    def status(self, handle):
        raise NotImplementedError


# ---- Oracle Cloud (OCI) GPU VMs — $300 credit-burn, MUST self-terminate ----------------------------------
# OCI has NO cheap GPU spot for the entry A10 shape, so this is a ONE-WINDOW burn of the 30-day $300 trial, not
# a standing provider (cheap-gpu-plan.md § Oracle). Like a raw GCE VM, an OCI compute instance bills every second
# it is up, so it MUST self-destroy on job exit or it idles on the meter. The LOAD-BEARING logic (config from env,
# cloud-init user_data with a guaranteed self-destroy EXIT trap, launch-details shape, lifecycle-state mapping) is
# factored into PURE, unit-tested helpers; the thin SDK calls in submit/status/stop are guarded so they fail
# loudly off-OCI. Self-termination is KEYLESS via INSTANCE PRINCIPALS (no signing key on the VM) — this needs a
# one-time tenancy setup: a Dynamic Group matching the instance + a policy
#   `allow dynamic-group <dg> to manage instance-family in compartment <c>`
# so the running VM may `oci --auth instance_principal compute instance terminate` ITSELF. autoteardown's
# finally+watchdog runs self_terminate_cmd() (belt); the cloud-init EXIT trap is the braces backstop.

_OCI_SHAPE = {                                                # logical gpu class -> OCI shape (single-GPU MD = A10.1)
    "a10": "VM.GPU.A10.1", "a10g": "VM.GPU.A10.1", "any": "VM.GPU.A10.1",
    "a10x2": "VM.GPU.A10.2",
    "a100": "BM.GPU.A100-v2.8", "l40s": "BM.GPU.L40S.4", "h100": "BM.GPU.H100.8",
}


def _oci_shape_for(res: ResourceSpec) -> str:
    """PURE: OCI shape name for a logical GPU class. Defaults to the entry VM.GPU.A10.1 (1× A10, 24 GB) — the
    only OCI GPU shape that's both single-GPU and usually launch-able on a trial tenancy."""
    return _OCI_SHAPE.get(res.gpu, "VM.GPU.A10.1")


def _oci_config_from_env(src=None) -> dict:
    """PURE: assemble the `oci` SDK config dict from OCI_* env. Key material comes from OCI_KEY_PEM (the inline PEM
    body — the CI-secret path) or OCI_KEY_FILE (a path). Raises a loud, itemised error if a required field is
    missing so an off-OCI/mis-secreted run fails at the door, not deep in the SDK."""
    env = src if src is not None else os.environ
    missing = [k for k in ("OCI_USER_OCID", "OCI_TENANCY_OCID", "OCI_FINGERPRINT", "OCI_REGION") if not env.get(k)]
    if not (env.get("OCI_KEY_PEM") or env.get("OCI_KEY_FILE")):
        missing.append("OCI_KEY_PEM|OCI_KEY_FILE")
    if missing:
        raise RuntimeError("oci backend needs " + ", ".join(missing) + " (create an OCI API signing key: "
                           "Console -> Profile -> API keys -> Add API key).")
    cfg = {"user": env["OCI_USER_OCID"], "tenancy": env["OCI_TENANCY_OCID"],
           "fingerprint": env["OCI_FINGERPRINT"], "region": env["OCI_REGION"]}
    if env.get("OCI_KEY_FILE"):
        cfg["key_file"] = env["OCI_KEY_FILE"]
    else:
        cfg["key_content"] = env["OCI_KEY_PEM"]                # oci SDK accepts an inline PEM body here
    return cfg


def _oci_launch_ctx_from_env(src=None) -> dict:
    """PURE: the placement OCIDs OCI requires to put a VM somewhere — compartment, availability domain, subnet,
    and boot image (a GPU-driver image, e.g. an Oracle-Linux-GPU or your baked image OCID). Read from OCI_* env."""
    env = src if src is not None else os.environ
    return {
        "compartment_id": env.get("OCI_COMPARTMENT_OCID") or env.get("OCI_TENANCY_OCID", ""),  # root compartment ok
        "availability_domain": env.get("OCI_AD", ""),
        "subnet_id": env.get("OCI_SUBNET_OCID", ""),
        "image_id": env.get("OCI_IMAGE_OCID", ""),
        "shape": env.get("OCI_SHAPE", ""),
    }


# Self-destroy on ANY exit via INSTANCE PRINCIPALS (keyless): find THIS instance's OCID from the OCI metadata
# service (169.254.169.254, the Bearer-Oracle IMDS) and terminate it. Fires on success, crash, AND `set -e`
# abort, so a failed/stopped job kills its own GPU immediately instead of idling on the meter. Needs the one-time
# dynamic-group + policy (see class docstring) so instance-principal auth is allowed to terminate self.
_OCI_SELFDESTROY = (
    'oci_selfdestroy(){ rc=$?; '
    'iid="${OCI_INSTANCE_ID:-$(curl -s -H \'Authorization: Bearer Oracle\' '
    'http://169.254.169.254/opc/v2/instance/id 2>/dev/null)}"; '
    '[ -n "$iid" ] && oci --auth instance_principal compute instance terminate '
    '--instance-id "$iid" --force >/dev/null 2>&1 || true; return $rc; }'
)


def _oci_user_data(spec: JobSpec, extra_env=None) -> str:
    """PURE: the cloud-init `user_data` bash — export the resume/checkpoint context (+ forwarded object-store
    creds), resolve this instance's OCID from IMDS, arm a self-destroy EXIT trap so the VM is torn down on
    completion/crash/stop (never idles — the #1 gotcha), then run the job command. `extra_env` merges UNDER
    spec.env (spec.env wins). Mirrors _vast_onstart so both providers share the same anti-idle contract."""
    cmd = " ".join(shlex.quote(a) for a in spec.command)
    env = {**(extra_env or {}), **spec.env}
    lines = ["#!/bin/bash", "set -o pipefail",
             'export OCI_INSTANCE_ID=$(curl -s -H "Authorization: Bearer Oracle" '
             'http://169.254.169.254/opc/v2/instance/id 2>/dev/null)',
             f"export CHECKPOINT_URI={shlex.quote(spec.checkpoint_uri)}",
             f"export RESUME={'1' if spec.resume else '0'}",
             f"export SELF_LABEL={shlex.quote(spec.name)}"]
    lines += [f"export {k}={shlex.quote(str(v))}" for k, v in env.items()]
    lines += [_OCI_SELFDESTROY, "trap oci_selfdestroy EXIT", cmd]
    return "\n".join(lines)


def _oci_launch_details(spec: JobSpec, ctx: dict, user_data_b64: str) -> dict:
    """PURE: a LaunchInstanceDetails-shaped dict (submit maps it onto SDK model objects). Validates that the
    placement OCIDs OCI demands are present, so a missing OCI_SUBNET_OCID/OCI_IMAGE_OCID fails clearly here."""
    need = [k for k in ("compartment_id", "availability_domain", "subnet_id", "image_id") if not ctx.get(k)]
    if need:
        raise RuntimeError("oci launch needs " + ", ".join("OCI_" + k.upper() for k in need)
                           + " (Console -> the resource's Details page has each OCID).")
    return {
        "compartment_id": ctx["compartment_id"],
        "availability_domain": ctx["availability_domain"],
        "shape": ctx.get("shape") or "VM.GPU.A10.1",
        "display_name": spec.name,
        "create_vnic_details": {"subnet_id": ctx["subnet_id"], "assign_public_ip": True},
        "source_details": {"source_type": "image", "image_id": ctx["image_id"]},
        "metadata": {"user_data": user_data_b64},             # base64 cloud-init (OCI decodes + runs it at boot)
    }


def _oci_status(lifecycle_state: str) -> str:
    """PURE: map an OCI instance lifecycle_state to our vocabulary. Because the VM self-terminates at job end,
    TERMINATING/TERMINATED reads as 'completed' (the job's real pass/fail lives in the checkpoint/reduce, same as
    every other backend); STOPPING/STOPPED is an externally halted box."""
    s = (lifecycle_state or "").upper()
    if s == "RUNNING":
        return "running"
    if s in ("PROVISIONING", "STARTING", "CREATING_IMAGE", "MOVING"):
        return "queued"
    if s in ("TERMINATING", "TERMINATED"):
        return "completed"                                    # self-destroyed on job exit
    return "stopped"                                          # STOPPING/STOPPED/unknown -> externally halted


class OCIBackend(Backend):
    """Oracle Cloud Infrastructure GPU VM — funded by the $300 / 30-day free-trial credit. NOT serverless and NO
    cheap GPU spot for the A10, so it is a ONE-WINDOW credit burn (cheap-gpu-plan.md § Oracle), not a standing
    provider. Like the GCE backend it MUST self-terminate or it idles on the meter; the guard is KEYLESS via
    instance principals (see module note above) + autoteardown's finally/watchdog. Best fit: burn the ~230 free
    A10-GPU-hours on triage-tier legs during the window, then stop. The load-bearing logic is pure + unit-tested;
    submit/status/stop guard on the `oci` SDK + OCI_* env so they fail loudly off-OCI."""
    name = "oci"

    def self_terminate_cmd(self):
        # KEYLESS self-destroy via instance principals; OCI_INSTANCE_ID is exported by the cloud-init from IMDS,
        # with an inline IMDS fallback so this argv resolves even if the export was skipped.
        return ["bash", "-lc",
                'oci --auth instance_principal compute instance terminate --instance-id '
                '"${OCI_INSTANCE_ID:-$(curl -s -H \'Authorization: Bearer Oracle\' '
                'http://169.254.169.254/opc/v2/instance/id)}" --force']

    def submit(self, spec: JobSpec) -> Handle:
        try:
            import oci                                          # noqa: F401
        except ImportError:
            raise RuntimeError("oci backend needs the oci SDK (`pip install oci`) + OCI_* API-key env.")
        import base64
        cfg = _oci_config_from_env()                           # raises if creds missing
        ctx = _oci_launch_ctx_from_env()
        if not ctx.get("shape"):
            ctx["shape"] = _oci_shape_for(spec.resources)
        # forward the checkpoint-store creds (reuse-S3 = the AWS keys) so the VM can read/write the bucket
        ud = _oci_user_data(spec, extra_env=dict(_object_store_env()))
        ud_b64 = base64.b64encode(ud.encode()).decode()
        details = _oci_launch_details(spec, ctx, ud_b64)       # validates placement OCIDs
        models = oci.core.models
        launch = models.LaunchInstanceDetails(
            compartment_id=details["compartment_id"],
            availability_domain=details["availability_domain"],
            shape=details["shape"],
            display_name=details["display_name"],
            create_vnic_details=models.CreateVnicDetails(
                subnet_id=details["create_vnic_details"]["subnet_id"], assign_public_ip=True),
            source_details=models.InstanceSourceViaImageDetails(image_id=details["source_details"]["image_id"]),
            metadata=details["metadata"],
        )
        client = oci.core.ComputeClient(cfg)
        try:
            resp = client.launch_instance(launch)
        except Exception as e:                                 # noqa: BLE001 — classify the common trial failure
            msg = str(e)
            if "capacity" in msg.lower() or "out of host" in msg.lower():
                raise RuntimeError(
                    f"oci: Out of host capacity for {ctx['shape']} — try another OCI_AD in-region, another "
                    f"A10-stocked region, or a Capacity Reservation (trial GPU capacity is thin). ({msg})")
            raise
        return Handle(backend=self.name, job_id=resp.data.id, extra={"shape": ctx["shape"]})

    def status(self, handle: Handle) -> str:
        try:
            import oci                                          # noqa: F401
        except ImportError:
            raise RuntimeError("oci backend needs the oci SDK (`pip install oci`).")
        client = oci.core.ComputeClient(_oci_config_from_env())
        try:
            inst = client.get_instance(handle.job_id).data
        except Exception:                                      # noqa: BLE001 — gone/terminated -> off the meter
            return "stopped"
        return _oci_status(getattr(inst, "lifecycle_state", None))

    def stop(self, handle: Handle) -> None:
        try:
            import oci                                          # noqa: F401
        except ImportError:
            raise RuntimeError("oci backend needs the oci SDK (`pip install oci`).")
        client = oci.core.ComputeClient(_oci_config_from_env())
        client.terminate_instance(handle.job_id, preserve_boot_volume=False)


class ModalBackend(Backend):
    """Modal — SERVERLESS GPU (Python-native: decorate a function, .map() it over the work units). Per-second
    billing and it **auto-scales to zero the instant a call returns**, so there is NO idle-GPU risk by design —
    self_terminate_cmd is empty (managed). Per-GPU-hour price carries a serverless premium (higher than
    Salad/Vast), but the combination of **free monthly credits + zero-idle + zero-ops + native fan-out** makes
    it the best 'start here / run triage for free' option, and an excellent fit for our many-independent-window
    FEP pattern. Submit is via the Modal SDK (a deployed function), not a VM."""
    name = "modal"

    def self_terminate_cmd(self):
        return []                              # serverless: auto-scales to zero on return (no idle billing)

    def submit(self, spec: JobSpec) -> Handle:
        try:
            import modal  # noqa: F401
        except ImportError:
            raise RuntimeError("modal backend needs the modal SDK + `modal token new` (create a Modal account).")
        raise NotImplementedError("define a @app.function(gpu=...) and .spawn()/.map() the units at integration time")

    def status(self, handle):
        raise NotImplementedError


# ---- mock backend (fully functional; for tests + dry runs) ------------------------------------------------

class MockBackend(Backend):
    name = "mock"

    def __init__(self):
        self._jobs = {}                         # job_id -> state
        self.terminated = []                    # records self_terminate_cmd executions (idle-GPU guard test)

    def self_terminate_cmd(self):
        return ["mock-terminate", "self"]       # non-empty: a marketplace-like backend that MUST self-kill

    def submit(self, spec: JobSpec) -> Handle:
        jid = f"mock-{spec.name}-{len(self._jobs)}"
        self._jobs[jid] = "running"
        return Handle(backend=self.name, job_id=jid, extra={"resume": spec.resume})

    def status(self, handle):
        return self._jobs.get(handle.job_id, "unknown")

    def complete(self, handle, ok=True):
        self._jobs[handle.job_id] = "completed" if ok else "failed"


_REGISTRY = {b.name: b for b in [SageMakerBackend(), SlurmBackend(), RunPodBackend(), VastBackend(),
                                 SaladBackend(), ModalBackend(), GCPBackend(), OCIBackend()]}


def get_backend(name: str) -> Backend:
    if name == "mock":
        return MockBackend()
    if name not in _REGISTRY:
        raise KeyError(f"unknown backend {name!r}; known: {sorted(_REGISTRY) + ['mock']}")
    return _REGISTRY[name]


def pick_cheapest(res: ResourceSpec, backends=None) -> str:
    """Return the name of the cheapest backend that can satisfy `res`. Free managed-HPC (access/slurm) wins
    when eligible; otherwise the cheapest marketplace. Ties broken by registration order."""
    names = backends or ["access", "slurm", "salad", "gcp", "vast", "runpod", "sagemaker"]
    priced = []
    for n in names:
        caps = _CAPS.get(n, {})
        m = _match_gpu(caps, res)
        if m is not None:
            priced.append((m[2], n))
    if not priced:
        raise ValueError(f"no backend satisfies {res}")
    priced.sort()
    return priced[0][1]
