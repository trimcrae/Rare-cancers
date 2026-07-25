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
import sys
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# THE VAST SPEND POLICY LIVES IN ONE PLACE. Bid level, throughput table and offer ranking all come from
# `vast_cost_model`, which derives them from a single cost function over measured inputs. This module used to
# carry its own copies of all three, and they drifted: the constant said x1.25 while its own docstring said
# x1.5, pricing.md said x1.5, bid-strategy.md said "keep x1.9", and a second throughput table in
# vast_bid_optimizer still held a withdrawn 669 ns/day. Importing is what makes that class of drift impossible.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vast_cost_model as _vcm  # noqa: E402


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
    min_cuda: float = 13.0        # host DRIVER's cuda_max_good must be >= this so OpenMM's CUDA-plugin PTX can JIT.
                                  # RAISED 12.6 -> 13.0 on 2026-07-23: DIAG PROOF that the `cuda-version=12.6` env
                                  # pin did NOT actually take — the baked env's PTX is CUDA-13-class, so legs that
                                  # landed on driver 560.35.03 (CUDA 12.6) / 565.57.01 (12.7) hosts crashed at
                                  # build_system with CUDA_ERROR_UNSUPPORTED_PTX_VERSION (and the mock teardown left
                                  # them idle-billing as "running"). The legs that completed all ran on newer-driver
                                  # hosts. Empirical fix: only take hosts whose cuda_max_good >= 13.0 (driver ~>=580),
                                  # which can JIT this env's PTX. Fewer hosts, but they don't crash. (The robust fix is
                                  # to genuinely rebuild the env at a lower CUDA; the pin has failed twice, so filter.)


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
        if e.code == 429 and _hops < 6:                           # rate limit (Vast DELETE threshold ~3 req/s): a
            import time                                           # burst teardown/collect 429s partway -> back off
            time.sleep(1.5 * (_hops + 1))                         # (1.5,3,4.5,...s) and retry so we drain the loop
            return _vast_request(method, path, api_key, params=params, body=body, _hops=_hops + 1)
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


# INTERRUPTIBLE BID — the policy now lives in `vast_cost_model.recommended_bid`, derived rather than tuned.
#
# The history this replaces: x1.1 -> x1.5 -> x1.9 -> x1.25, each a reaction to the last incident, with the
# docs never agreeing on which was in force. The x1.9 in particular was bought to avoid a ~20-minute image
# reload on every preemption — a cost that turned out to be SELF-INFLICTED (our reaper deleted paused
# instances instead of letting Vast resume them), so the premium was insuring against our own bug.
#
# What MEASUREMENT replaced it with (2026-07-25, `vast-bid-semantics-probe-ladder.json`): renting one offer at
# three bid multiples showed charged = min(bid, the machine's on-demand price) — x1.0 -> $0.00930 on a
# $0.00930 bid, x2.5 and x8.0 both -> $0.02133, which matched machine 142136's on-demand dph_base to 17
# significant figures. So every cent of premium below that cap is spent on every hour. Combined with Vast's
# documented rule that on-demand renters preempt interruptible ones regardless of bid, and a market where
# ~148 qualifying offers sat idle, the premium buys partial protection we can get for free by re-dispatching.
# `vast_cost_model.premium_breakeven_dlam_db` states the refutable version: a premium only pays if the hazard
# falls by >100 preemptions/hour per $/hr of premium.
#
# Kept only so existing callers and the ceiling arithmetic keep working; it is NO LONGER a policy knob.
_VAST_BID_FLOOR_MULT = float(os.environ.get("VAST_BID_FLOOR_MULT", "0") or 0) or None


def _vast_bid_price(offer: dict, ondemand_base: float = None):
    """Interruptible bid $/hr = the market floor plus a staleness tick, capped at the machine's real on-demand
    price and never at or below the floor. Delegates to `vast_cost_model.recommended_bid`; see the note above
    for why this is a tick and not a multiple.

    `VAST_BID_FLOOR_MULT` is still honoured as an ESCAPE HATCH if someone sets it explicitly — a specific leg
    that genuinely cannot tolerate pauses may want to buy retention — but it is unset by default, so the
    derived policy is what runs.

    WHY THE CAP NEEDS `ondemand_base` PASSED IN. The launch path queries `type: "bid"`, and in a bid-type
    search Vast reports `dph_base` as your rate AT the floor — so `dph_base == min_bid` identically and
    comparing against it compares the floor to itself. A genuine on-demand price only exists in a separate
    `type: "on-demand"` query joined by `machine_id` (see `_vast_ondemand_base_by_machine`). PURE."""
    try:
        floor = float(offer.get("min_bid") or 0.0)
        base = float(offer.get("dph_base") or offer.get("dph_total") or 0.0)
    except (TypeError, ValueError):
        return None
    ref = floor if floor > 0 else base
    if ref <= 0:
        return None
    if _VAST_BID_FLOOR_MULT:                       # explicit override only
        bid = ref * _VAST_BID_FLOOR_MULT
        try:
            cap = float(ondemand_base or 0.0)
        except (TypeError, ValueError):
            cap = 0.0
        if cap > 0:
            bid = max(ref, min(bid, cap))
        return round(max(bid, 0.001), 4)
    return _vcm.recommended_bid(ref, ondemand_base)


def _vast_ondemand_base_by_machine(key, res: ResourceSpec = None) -> dict:
    """machine_id -> on-demand `dph_base`, from a real `type: "on-demand"` query.

    The ONLY source of a true on-demand price. A bid-type query cannot provide one (see `_vast_bid_price`).
    Best-effort: any failure returns {} so the caller simply bids uncapped rather than failing to launch."""
    try:
        spec = ResourceSpec(**{**vars(res or ResourceSpec()), "interruptible": False})
        q = _vast_offer_query(spec)
        q["limit"] = 512
        data = _vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}) or {}
        out = {}
        for o in data.get("offers", []):
            try:
                out[str(o.get("machine_id"))] = float(o.get("dph_base"))
            except (TypeError, ValueError):
                continue
        return out
    except Exception as e:  # noqa: BLE001
        print(f"  [bid-cap] on-demand price lookup failed ({e}) -> bidding uncapped", flush=True)
        return {}


def _vast_gpu_ram_gb(offer: dict) -> float:
    """Vast reports per-GPU RAM in MB; be tolerant of an already-GB value on older payloads."""
    ram = float(offer.get("gpu_ram", 0) or 0)
    return ram / 1024.0 if ram > 1000 else ram


# MEASURED ns/day at 84,534 particles — SINGLE SOURCE OF TRUTH is `vast_cost_model.MEASURED_NS_PER_DAY_84K`
# (validated 2026-07-24 grid: 3 x ~20 s independent timed blocks per leg, physics-checked, CV < 1.4%, with a
# rejection gate that threw out a contended host and a mislabelled card). Re-exported here so existing callers
# keep working; do NOT add a card to this alias — add it to the cost model, or the two tables drift, which is
# exactly how a withdrawn 669 ns/day survived in a second table for a day.
_MEASURED_NS_PER_DAY_84K = _vcm.MEASURED_NS_PER_DAY_84K


def measured_ns_per_day(gpu_name):
    """Benched throughput for this card at the ternary size, or None if we have never measured it. PURE."""
    n = str(gpu_name or "").replace(" ", "").upper()
    for k in sorted(_MEASURED_NS_PER_DAY_84K, key=len, reverse=True):
        if k in n:
            return _MEASURED_NS_PER_DAY_84K[k]
    return None


def offer_usd_per_ns(gpu_name, usd_per_hour):
    """$ per ns of MD — the quantity that actually decides cost, unlike $/hr.

    A $0.103/hr RTX 3090 looks cheaper than a $0.149/hr RTX 4090 and is not: 359 vs 755 ns/day makes it
    $0.00688 vs $0.00473 per ns, 45% worse. Ranking offers by $/hr cannot see that. Returns None for an
    unmeasured card so the caller can rank it last instead of inventing a throughput for it. PURE."""
    ns = measured_ns_per_day(gpu_name)
    try:
        p = float(usd_per_hour)
    except (TypeError, ValueError):
        return None
    if not ns or p <= 0:
        return None
    return p / (ns / 24.0)


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
                # ...but the CEILING must be checked against what we will actually be BILLED. Measured
                # 2026-07-25: on Vast the charge is min(your bid, the machine's on-demand price), so the
                # billed rate is exactly what `_vast_bid_price` returns — ask it rather than re-deriving a
                # multiple here. Comparing the ceiling to min_bid alone let the effective rate run past the
                # cap before any offer was rejected (at the old x1.9 and a $0.60 cap, $1.14/hr — no ceiling
                # at all), which is how the step1 fan-out ran at ~$0.37/hr against a $0.30 estimate.
                effective = _vast_bid_price(o) or price
            else:
                price = float(o.get("dph_total", o.get("dph_base", 1e9)))
                effective = price
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
        if max_hourly_usd is not None and effective > max_hourly_usd:
            continue
        capable.append((price, o))
    if not capable:
        return None
    # RANK BY $/ns, NOT $/hr — and on the price we will actually be BILLED, storage included.
    #
    # Measured on the live board (2026-07-25, 148 qualifying offers): the spread from the best offer to the
    # median is 5.4x, and 2.3x within the RTX 4090 class alone. That dwarfs both the 2.10x card gap and the
    # 1.48x that the retired x1.9 bid multiple was worth — SELECTION IS THE LEVER, by roughly an order of
    # magnitude. Ranking by $/hr picks a $0.103/hr 3090 over a $0.149/hr 4090 and pays 45% more per ns for it;
    # ranking by the floor rather than the bid ignores the tick we actually pay; ignoring storage misprices
    # hosts whose $/GB/month differs by 20x on an otherwise identical box.
    #
    # Cards we have never benched have no $/ns, so they sort AFTER every measured offer and are taken only when
    # nothing measured qualifies. That is deliberate: substituting a spec-sheet proxy for a measurement is what
    # produced the retracted 2026-07-24 rankings.
    job = _vcm.JobProfile(disk_gb=max(40, res.disk_gb), min_vram_gb=res.min_vram_gb,
                          min_reliability=res.min_reliability, min_cuda=res.min_cuda)
    # On-demand offers are billed at dph_total and carry no meaningful min_bid, so hand the scorer the rate we
    # would actually be charged rather than letting it derive a bid that nobody would pay.
    scored = [(_vcm.score_offer(o, job, billed_usd_h=(None if res.interruptible else p)), p, o)
              for p, o in capable]
    measured = [(s.usd_per_ns, p, o) for s, p, o in scored if s is not None]
    if measured:
        return min(measured, key=lambda t: (t[0], t[1]))[2]
    substr = _VAST_GPU_SUBSTR.get(res.gpu)                        # nothing benched -> prefer the requested model
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


# Self-STOP on ANY exit, KEY-FREE (2026-07-24, trimcrae: never share VAST_API_KEY with community hosts): a bash
# EXIT trap that halts THIS instance's GPU billing WITHOUT any API key on the host, by exiting its own container
# — Vast bills the GPU only while the container runs, so powering the container off / killing its init (PID 1)
# stops the GPU meter immediately on completion, crash, or `set -e` abort. We deliberately do NOT forward
# VAST_API_KEY to the rented host (a real exposure: the key can spend the account's credit). Stopping billing is
# not the same as DESTROYING the instance (an exited instance still holds cheap disk); the guaranteed DESTROY is
# CONTROL-PLANE only — the CI-side collect reap (result-in-S3 / terminal-state / 240-min backstop) + stop_all,
# where the key never leaves CI. So: host self-stops the GPU key-free, CI destroys the exited instance.
_VAST_SELFDESTROY = (
    'ct_selfdestroy(){ rc=$?; '
    'poweroff 2>/dev/null || shutdown -h now 2>/dev/null || kill -9 -1 2>/dev/null || kill -9 1 2>/dev/null || true; '
    'return $rc; }'
)


def _vast_onstart(spec: JobSpec, self_terminate_argv, extra_env=None) -> str:
    """Build the instance onstart script: export the resume/checkpoint context (+ forwarded object-store creds;
    NO VAST_API_KEY — never on a community host), arm a KEY-FREE self-stop EXIT trap so the instance halts its GPU
    billing (exits its container) on completion/crash/stop (never idles on the meter — the #1 gotcha), then run
    the job command. The guaranteed DESTROY is control-plane (CI reap). `extra_env` is merged UNDER spec.env
    (spec.env wins). PURE (no I/O) -> unit-tested."""
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
    instance MUST stop billing. Teardown is KEY-FREE + two-layer (VAST_API_KEY is NEVER put on a community host):
    (1) HOST self-STOP — autoteardown's finally+watchdog + the onstart EXIT trap exit the container (poweroff /
    kill PID 1), halting the GPU meter with no API key; (2) CONTROL-PLANE DESTROY — the CI collect reap
    (result-in-S3 / terminal / 240-min backstop) + stop_all fully remove the exited instance, key staying in CI.
    The host can stop its own GPU billing but only CI (the key-holder) can destroy the instance.

    NOTE (must smoke before a fleet): the exact Vast REST endpoints/query schema drift between API versions; the
    LOAD-BEARING logic — cheapest-verified-offer selection and the key-free-self-stop onstart — is factored
    into pure, unit-tested helpers (`_select_cheapest_offer`, `_vast_onstart`), so a one-instance smoke only has
    to confirm the HTTP shapes, not the science."""
    name = "vast"

    def self_terminate_cmd(self):
        # KEY-FREE self-stop: exit this container so Vast halts GPU billing, with NO API key on the host.
        # The guaranteed DESTROY of the (now-exited) instance is control-plane — the CI collect reap + stop_all,
        # where VAST_API_KEY never leaves CI. (Was `vastai destroy` — needed the key on the host; removed.)
        return ["bash", "-c", "poweroff 2>/dev/null || shutdown -h now 2>/dev/null || kill -9 1 2>/dev/null || true"]

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
        # Forward ONLY the checkpoint-store creds (reuse-S3 = bucket-scoped AWS keys) into the rented host — the
        # science needs S3, not Vast. VAST_API_KEY is deliberately NOT forwarded (never expose the account key to a
        # community host); the host tears down key-free by exiting its container, and CI destroys it (2026-07-24).
        extra = dict(_object_store_env())
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
            # Cap the bid at THIS machine's real on-demand price. Requires a separate on-demand query: the offer
            # in hand came from a bid-type search, whose dph_base is the floor by definition, so it cannot bound
            # anything. Best-effort — an empty map just means we bid uncapped, exactly as before.
            od = _vast_ondemand_base_by_machine(key, res).get(str(offer.get("machine_id")))
            bid = _vast_bid_price(offer, ondemand_base=od)
            if bid is not None:
                body["price"] = bid
                if od:
                    print(f"  [bid] ${bid}/hr (floor ${offer.get('min_bid')}, on-demand cap ${od:.4f})", flush=True)
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
                      # min_bid is carried so a launcher can report the market FLOOR alongside what we bid —
                      # the premium is otherwise invisible and gets baked into the next cost estimate.
                      extra={"offer": offer["id"], "dph": offer.get("dph_total"),
                             "min_bid": offer.get("min_bid"), "bid": body.get("price"),
                             "resume": spec.resume})

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
                                 SaladBackend(), ModalBackend(), GCPBackend()]}


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
