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

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---- job / resource spec ----------------------------------------------------------------------------------

@dataclass
class ResourceSpec:
    gpu: str = "any"              # logical class: rtx4090 | rtx3090 | a10g | l4 | l40s | a100 | any
    min_vram_gb: int = 16         # MD complex legs fit comfortably in 16-24 GB (single-GPU)
    vcpus: int = 4
    ram_gb: int = 16
    interruptible: bool = True    # our per-unit checkpointing tolerates interruption -> take the cheap tier


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


class VastBackend(Backend):
    name = "vast"

    def self_terminate_cmd(self):
        # destroy this instance from inside it; the instance id is in the env Vast injects.
        return ["vastai", "destroy", "instance", os.environ.get("VAST_INSTANCE_ID", "$VAST_INSTANCE_ID")]

    def submit(self, spec: JobSpec) -> Handle:
        if not os.environ.get("VAST_API_KEY"):
            raise RuntimeError("vast backend needs VAST_API_KEY (create a Vast.ai account first).")
        raise NotImplementedError("vastai create instance ... at integration time")

    def status(self, handle):
        raise NotImplementedError


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
