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

import dataclasses
import functools
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

# ⛔⛔ THE NO-GPU BAN. `research/autonomy/gpu_ban.py` is the ONE gate; this module is one of its four call
# sites. Imported by path rather than copied, for the reason `vast_cost_model` is imported above: a second
# copy of a policy is a policy that drifts. `research/modalities/../autonomy` is `research/autonomy`.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "autonomy"))
import gpu_ban as _gpu_ban  # noqa: E402


class NoQualifyingOffer(RuntimeError):
    """The board was read successfully and had nothing this spec could buy.

    ★★ WHY THIS IS A TYPE AND NOT JUST A MESSAGE (2026-07-27). "The market had nothing under our price line"
    and "the provider API returned 403" both ended as a bare RuntimeError inside the launcher's per-unit
    `except`, so both printed `0/N unit(s) submitted` and failed the job identically. On the morning this was
    written that ambiguity was live in CI: the run list showed a red launch, and the only way to learn whether
    the price guard had worked correctly or the launcher was broken was to read the job log.

    They need OPPOSITE responses. Nothing affordable is the guard doing its job — wait for the board, the
    work is checkpointed, nothing is wrong. A provider fault is a real defect that costs a cleared window and
    must be loud. Subclassing RuntimeError keeps every existing `except RuntimeError` working unchanged."""


class CapacityRefusedAtStart(NoQualifyingOffer):
    """Every host we rented answered `resources_unavailable` on start, so nothing is running and $0 is billing.

    ★★ A SUBCLASS OF `NoQualifyingOffer`, DELIBERATELY (2026-07-29). Both callers of `submit` already sort
    exceptions into "the MARKET had nothing" and "the LAUNCHER is broken" by `isinstance(e, NoQualifyingOffer)`
    (`ternary_vast_launch.submit`, `congeneric_fanout_vast.mode_launch`). A host declining to schedule us is
    unambiguously the first: CLAUDE.md §6 records a capacity refusal as routine, not as an alarm, and
    `ternary-vast-watch.json._capacity_refusal` already says the answer is "pick another host". Filing it as a
    fault would make a normal market condition fail a build; giving it its OWN top-level type would silently
    reclassify it as a fault in both lanes, because neither has an `except` for it. So it inherits, and the
    lanes keep working with no edit.

    It carries `refusals` — one row per host that refused — so a caller with an object store can hand them to
    `capacity_refusal_trend.record`. That module is a READOUT and can never gate; nothing here consults it."""

    def __init__(self, message, refusals=()):
        super().__init__(message)
        self.refusals = list(refusals)


#: ★★ THE ACCOUNT-LEVEL VAST STAND-DOWN — ONE DOOR, ONE LOCK.
#: `VastBackend.submit` is the ONLY place in this repository that creates a Vast rental (`PUT /asks/{id}/`,
#: Vast's canonical create-instance endpoint). Six lanes call it: ternary, congeneric fan-out, protfep,
#: nrv04, bioemu and the ternary watchdog. A per-lane hold therefore has to be written six times and is
#: wrong the moment a seventh lane is added; a hold HERE cannot be routed around.
#:
#: ⚠ IT GATES CREATION ONLY. `destroy`, `stop`, `collect` and every reap path are untouched, because a lane
#: that is stood down must still tear down a host that somehow exists — otherwise "stood down" quietly
#: becomes "billing unwatched", which is this repository's most expensive recurring failure.
VAST_RENTAL_HOLD = "vast-RENTAL-HOLD.json"


def vast_rental_hold(root=None):
    """The account-level Vast rental hold, or None. UNREADABLE HOLDS — doubt never resolves to spend."""
    path = os.path.join(root or os.path.dirname(os.path.abspath(__file__)), VAST_RENTAL_HOLD)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return {"reason": f"the hold file exists but could not be parsed ({type(e).__name__}) — HOLDING, "
                          f"because an unreadable instruction to stop is not permission to spend"}
    return doc if isinstance(doc, dict) else {"reason": "hold file is not an object — HOLDING"}


class RentalHeldByOperator(NoQualifyingOffer):
    """A person stood the Vast account down. No rental may be created until the hold file is deleted.

    ★ A SUBCLASS OF `NoQualifyingOffer`, FOR THE SAME REASON `CapacityRefusedAtStart` IS. Every caller of
    `submit` already sorts that type into "a correct refusal, not a fault", so a stood-down account produces
    a QUIET, non-red lane without touching six call sites. The distinct type is what lets a caller that
    cares print "stood down" instead of "nothing affordable" — opposite meanings, and the ambiguity between
    a working guard and a broken launcher is exactly what typing these refusals exists to remove."""



# How many hosts a single `submit` will try before giving the unit up for this tick. See the retry loop in
# `VastBackend.submit` for why retrying at all is the fix and why it needs no extra price gate.
#
# WHY 3. A refusal costs one create + one destroy and ~50 s, and it is $0 (a Vast instance that never leaves
# `stopped` bills nothing but its disk, and the destroy is immediate). The cost of NOT retrying is a whole
# tick: the ternary lane's launches are dispatch-driven at ~30-35 min apart, so one undetected refusal idles
# the lane for half an hour. 3 keeps a pathological board (every top offer stale) from turning one unit's
# submit into a minutes-long burst against a shared key that has already answered an nginx HTML 403 to a
# four-unit launch — see `_vast_request`'s 403 note.
_VAST_START_REFUSAL_TRIES = max(1, int(os.environ.get("VAST_START_REFUSAL_TRIES", "3") or 3))


# =============================================================================================================
# ★★ THE HOST CUDA FLOOR — MEASURED PER IMAGE, WITH ONE HOME (2026-07-31)
# =============================================================================================================
# WHAT WAS WRONG. `ResourceSpec.min_cuda` was the constant **13.0**, applied TWICE per board read
# (`_vast_offer_query`'s `cuda_max_good: {gte: ...}` and again in `rank_offers_by_usd_per_ns`), on the strength
# of a COMMENT: *"DIAG PROOF that the `cuda-version=12.6` env pin did NOT actually take — the baked env's PTX
# is CUDA-13-class."* Against it, `Dockerfile.ternaryfep` is `FROM nvidia/cuda:12.6.3-runtime-ubuntu22.04` and
# pins `cuda-version=12.6`. Two documents, opposite claims, and the expensive one was enforced.
#
# WHAT IT COST, measured before it was changed (`vast-filter-ablation.json`, 2026-07-31 1:36 PM ET, bid tier,
# 1370 offers returned): the CUDA floor was the second most expensive filter in the whole spec —
#   13.0 -> 119 offers surviving, 52 priceable, best $0.003014/ns (0.883x basis)
#   12.6 -> 134 offers surviving, 58 priceable, best $0.002828/ns (0.829x basis)   = 6.2 % better per ns
# and the sweep is flat below 12.6, so 12.6 captures the whole gain. That is 6.2 % off every rental, forever.
#
# WHAT SETTLED IT — the diagnostic, not the Dockerfile line (`probe_image_cuda.py`, run INSIDE the image,
# $0, no GPU). OpenMM JIT-compiles its CUDA kernels with NVRTC, so the PTX ISA it emits — and therefore the
# minimum host driver — is fixed by the env's own `libnvrtc`, which `ctypes` can interrogate anywhere. The
# baked `triskit23/ternary-fep:latest` answered: **nvrtcVersion 12.6**, `libcudart` 12.6, conda
# `cuda-version 12.6`, `cuda-nvrtc 12.6.85`, openmm 8.4.0. The pin DID take. The comment was false for the
# image that is actually running.
#
# ⚠ AND IT MAY HAVE BEEN TRUE WHEN WRITTEN. The 13.0 raise was 2026-07-23 and the image has been re-baked
# since (`ternary-fep-bake.yml`). This measurement is of the CURRENT image, which is the only one selection
# can land on — which is exactly why the floor must be DERIVED from a probe artifact rather than remembered:
# a re-bake that moves the env now moves the filter with it, instead of leaving a stale constant behind.
# SUPERSEDED, RETAINED: `min_cuda = 13.0` as a standing constant, and the "the pin did NOT take" claim.
#
# ⚠ PER IMAGE, NEVER SHARED BLIND. `pmxfep`, `nrv04vast`, `nr4a3fep` and `bioemu` are different stacks. An
# image with no entry in the artifact keeps `CONSERVATIVE_MIN_CUDA`, because inheriting another image's
# measurement is the same error as inheriting a Dockerfile's claim.
CONSERVATIVE_MIN_CUDA = 13.0      # the fallback for an image nobody has probed — deliberately the old value
_CUDA_REQ_ARTIFACT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "image-cuda-requirements.json")


def measured_min_cuda(image=None, default=None, path=None):
    """The MEASURED minimum host `cuda_max_good` for `image`, or the conservative fallback.

    `image` may be a bare key (`ternary-fep`) or a full reference (`docker.io/triskit23/ternary-fep:latest`) —
    the repo writes both forms in different places and a lookup that only accepted one would silently return
    the fallback and look like a measurement nobody had taken.

    None/unknown image => `CONSERVATIVE_MIN_CUDA`, deliberately: a caller that has not said which stack it
    runs must not inherit another stack's floor."""
    fallback = CONSERVATIVE_MIN_CUDA if default is None else float(default)
    if not image:
        return fallback
    key = str(image).rsplit("/", 1)[-1].split(":")[0]
    try:
        with open(path or _CUDA_REQ_ARTIFACT) as fh:
            got = (json.load(fh).get("images") or {}).get(key) or {}
        v = got.get("required_host_cuda")
        return float(v) if v else fallback
    except (OSError, ValueError, TypeError):
        return fallback


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
    # Machines to skip regardless of price. On Vast a start can be refused with
    # {"error": "resources_unavailable"} because that host's GPU is already taken — and no bid fixes
    # it (verified 2026-07-25: raising a stuck leg's bid 26% to its value ceiling changed nothing).
    # Such a host has INFINITE realised $/ns, which the $/ns ranking cannot see, so it will keep
    # winning selection and keep failing to start. This is the availability term the ranking lacks.
    # Vast is ~23 independently-priced hosts visible at once, so the answer is to pick another one
    # rather than to queue — see the 2026-07-24 reservation-price retraction, "you do not wait for a
    # price, you pick a host".
    exclude_machine_ids: tuple = ()
    # ★★ THE PRICE THE GATE CLEARED, MADE BINDING ON THE OFFER ACTUALLY BOUGHT (2026-07-27).
    #
    # The defect this closes: a launcher's market gate takes its OWN board snapshot, decides, and then
    # `submit` calls `_select_cheapest_offer` against a SECOND, independently-fetched board. Two reads,
    # two different objects — so the figure in front of the decision is not the figure we pay. Measured on
    # the step 1 lane at 8:00 AM ET: the gate cleared on machine 11892 at 1.388x basis and the launcher
    # rented machine 55559 at 1.479x. Harmless there (both under the line), unbounded in principle.
    #
    # It bites hardest exactly where a per-unit gate lives, because such a gate's whole premise is "buy from
    # the top of the ranking" — and the top is where offers evaporate. A `resources_unavailable` on the best
    # host is routine on Vast, and the fallback is BY DEFINITION worse than what was approved.
    #
    # So the ceiling travels WITH the spec into the selection, rather than being re-checked beside it. A
    # non-clearing offer is then never selected in the first place — including on every fallback after a
    # capacity refusal — which is strictly stronger than re-checking one chosen offer, and it cannot drift
    # from the gate because both sides call `rank_offers_by_usd_per_ns`.
    #
    # None = unset, which is what every gate/reporting caller wants: the gate must SEE the expensive offers
    # in order to report them and to say how far above the line the cheapest one sits. Only the spec handed
    # to `submit` carries the cap.
    max_usd_per_ns: float = None
    # ★ `gpu` AS A HARD CONSTRAINT, NOT A PREFERENCE (2026-07-27). Normally the model is a hint: selection
    # ranks by $/ns and takes whatever wins, because "the card is not the decision — the offer is". But a
    # THROUGHPUT BENCH is the one job whose entire output is "how fast is card X", and for it the default
    # behaviour is actively wrong: `_select_cheapest_offer` returns the best MEASURED offer first, so a request
    # to bench an RTX 5090 lands on a 4090 or 3090 and the result is filed under the card we asked for. That is
    # not hypothetical — it is the 2026-07-24 incident in which a leg fell back to a Quadro RTX 8000 and was
    # tabulated as an A10, which is part of why that whole grid was withdrawn. With this set, an unavailable
    # card fails the submit cleanly instead of quietly measuring something else.
    require_gpu: bool = False
    # ★★ A DEADLINE IS A SPEED FLOOR, AND NAMING A CARD IS NOT ONE (trimcrae, 2026-07-29: "Can we get T2
    # ternary on a faster chip so that they're all done by tomorrow morning... At this point, I just want
    # them all done by the morning. Don't worry about the price of the rest of these specific legs.")
    #
    # WHAT FAILED. The lane already had a `gpu_class` input that sets `ResourceSpec.gpu`. It could not
    # deliver, and the reason is structural rather than a bug: with `require_gpu` False, `gpu` is consulted
    # ONLY by `_select_cheapest_offer`'s unmeasured fallback, so the moment any benched offer qualifies the
    # $/ns ranking decides and the requested class is never looked at. T2 ternary was re-placed on an RTX
    # 3090 at $0.068/hr — the cheapest $/ns on the board, correctly — and its measured 34 s/iter put its ETA
    # at 5:59 PM the NEXT DAY against ~3:30 AM for its siblings. Selection was working; it was optimising
    # the wrong thing, because nothing in the spec expressed a deadline.
    #
    # WHY NOT JUST SET `require_gpu` AND NAME A 5090. Because the constraint is not "this card", it is "fast
    # enough to land by morning", and a card name is a lossy encoding of it: it excludes every equally-fast
    # card we have benched, it silently expires when the table gains an entry, and it invites the 2026-07-24
    # failure of filing a result under a card that never ran. A floor in ns/hr says the actual requirement,
    # is checked against the SAME validated throughput table the $/ns ranking already uses (CLAUDE.md §1 —
    # one home for card speed), and needs no maintenance when a card is added.
    #
    # ⚠ AN UNBENCHED CARD CANNOT CLEAR A FLOOR. `ns_per_hour` returns None for a card we have never measured,
    # and taking one would wave through exactly the slowness this exists to refuse — the same reasoning that
    # empties `capable` when `max_usd_per_ns` admits nothing. So unbenched offers are excluded whenever this
    # is set, and only then.
    #
    # 0.0 = UNSET, which is what every ordinary leg and every gate wants: this is a per-launch override for a
    # unit that has become the critical path, not a standing policy. Leaving it on would quietly convert the
    # lane's cost discipline into a speed preference nobody voted for.
    min_ns_per_h: float = 0.0
    # ★★ THE HOST DRIVER FLOOR — NOW MEASURED PER IMAGE, NOT ASSERTED (2026-07-31). See
    # `measured_min_cuda` above for the whole argument; the short version is that this default is the
    # CONSERVATIVE fallback for a caller who has not said which image it runs, and any lane that knows its
    # image should pass `measured_min_cuda(<image>)` instead of inheriting it.
    min_cuda: float = CONSERVATIVE_MIN_CUDA


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

    #: ⛔⛔ THE NO-GPU BAN, APPLIED TO EVERY BACKEND AT CLASS-DEFINITION TIME.
    #: Seven real adapters implement `submit` (SageMaker, Slurm, RunPod, Vast, Salad, GCP, Modal) and each
    #: one starts a billable machine. Checking the ban in each of them would be seven copies of a policy —
    #: and, exactly as `vast-RENTAL-HOLD.json` records of per-lane holds, "wrong the moment a seventh is
    #: added". Wrapping here means an EIGHTH backend is gated on the day it is written, with no edit to
    #: this file and none to `gpu_ban`.
    #: ⚠ `mock` IS EXEMPT AND THAT IS NOT A BYPASS: `MockBackend` creates nothing, contacts nothing and
    #: bills nothing — it is the dry-run/test double. A caller reaches it only by asking for it BY NAME,
    #: and what it then returns is a fake handle, not a machine.
    _GPU_BAN_EXEMPT_BACKENDS = frozenset({"mock", "abstract"})

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        fn = cls.__dict__.get("submit")
        if fn is None or getattr(fn, "_gpu_ban_wrapped", False):
            return

        @functools.wraps(fn)
        def _submit(self, *a, **kw):
            if getattr(self, "name", "abstract") not in Backend._GPU_BAN_EXEMPT_BACKENDS:
                _gpu_ban.assert_permitted(
                    f"{type(self).__name__}.submit — starting a billable GPU on the {getattr(self, 'name', '?')} backend")
            return fn(self, *a, **kw)

        _submit._gpu_ban_wrapped = True
        cls.submit = _submit

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

# NB: this map is the SOFT preference only (`_select_cheapest_offer`, used when nothing measured qualifies).
# The HARD `require_gpu` constraint deliberately does NOT consult it: its entries are loose substrings ("4090"
# matches the cut-down `RTX 4090D` too), and a bench that lands on a near-miss produces a number for a card
# that never ran. That path uses the same suffix rule as `vast_cost_model._model_key`, so any card the census
# shortlists is benchable without anyone remembering to add a map entry first.


# ★★ ONE BOARD READ SERVES A WHOLE WAVE (2026-07-27, added for the ramp trimcrae asked for).
#
# THE PROBLEM THE RAMP CREATES. `/search/asks/` is read once per unit inside `VastBackend.submit`, and AGAIN
# per unit inside `_vast_ondemand_base_by_machine` (the bid cap). That is 2 reads per unit, on top of the
# market gate's 1. A 5-unit tick is 11 board reads in a burst; the 18-wide fleet this ramp is for would be
# **37**. One Vast API key drives every lane in this repo, and this file's own 403 handler records the
# consequence measured at 11:08-11:10 AM ET today: an nginx HTML 403 — a proxy/WAF throttle verdict, not an
# auth failure — hit the board read, `/instances/` and all four `/search/asks/` of a FOUR-unit launch, which
# rented 0/4. Bursting is the documented trigger. Scaling placement 4x while leaving the read pattern
# per-unit would scale the trigger with it, and the ramp would throttle itself exactly when it got wide.
#
# WHY A CACHE IS THE *CORRECT* ANSWER HERE AND NOT MERELY THE CHEAP ONE. Every unit in a wave issues the
# IDENTICAL query: `_vast_offer_query(res)` is a pure function of the ResourceSpec's hard filters, and the
# two things that differ per unit — `exclude_machine_ids` (the launcher widens it as it goes so the wave
# lands on distinct hosts) and `max_usd_per_ns` — are applied CLIENT-SIDE in `rank_offers_by_usd_per_ns`,
# never sent to Vast. So the per-unit reads were already fetching the same rows and throwing away 17 copies
# of them. Serving one snapshot to the whole wave also makes the wave INTERNALLY CONSISTENT: unit 1 and unit
# 18 now choose from the same board, which is what the gate priced. Reading fresh per unit gave each unit a
# different market and no two of them what the gate approved.
#
# ⚠ OPT-IN, SHORT-LIVED, AND IT NEVER SERVES A STALE ROW. Off unless a caller opens the context manager, so
# nothing else in the repo changes behaviour; bounded by an explicit TTL checked against a MONOTONIC clock;
# emptied on exit so a cache can never outlive the wave that wanted it. Errors are never cached — a failed
# read raises exactly as before, which keeps §6's fail-closed discipline intact (an unreadable board is not
# a cheap one, and it must not be a remembered one either).
#
# ⚠ READS ONLY, AND ONLY THIS ENDPOINT. `/instances/` reflects state we are mutating and must never be
# remembered; a mutation is never cached at all, for the same reason the 403/timeout retries are GET-only.
_BOARD_CACHE: dict = {}
_BOARD_CACHE_TTL_S = 0.0
_BOARD_CACHE_STATS = {"hits": 0, "misses": 0, "saved_calls": 0}
_BOARD_CACHE_PATH = "/search/asks"


def board_read_cache(ttl_s: float = 180.0):
    """Context manager: serve repeated identical `/search/asks/` GETs from one read for `ttl_s` seconds.

    Use around a FAN-OUT, not around a whole program. `stats()` on the yielded object reports hits and the
    calls saved, so the reduction in API pressure is measured rather than asserted.
    """
    import contextlib

    @contextlib.contextmanager
    def _cm():
        global _BOARD_CACHE_TTL_S
        prev_ttl, prev_cache = _BOARD_CACHE_TTL_S, dict(_BOARD_CACHE)
        _BOARD_CACHE.clear()
        _BOARD_CACHE_STATS.update({"hits": 0, "misses": 0, "saved_calls": 0})
        _BOARD_CACHE_TTL_S = float(ttl_s)
        try:
            yield _BOARD_CACHE_STATS
        finally:
            _BOARD_CACHE_TTL_S = prev_ttl
            _BOARD_CACHE.clear()
            _BOARD_CACHE.update(prev_cache)

    return _cm()


def _board_cache_key(path, params):
    return (path, json.dumps(params or {}, sort_keys=True))


def _vast_request(method: str, path: str, api_key: str, params=None, body=None, _hops: int = 0,
                  no_cache: bool = False):
    """Thin JSON client for the Vast REST API. Isolated so tests monkeypatch it; the callers' logic is pure.
    SELF-HEALING against Vast's v0->v1 migration: on a 410 `deprecated_endpoint` the body names the replacement
    ("Use /api/v1/instances/ instead"), so we follow it once instead of hard-failing (keeps the adapter working
    as endpoints move without hardcoding a version per route)."""
    # ⛔⛔ THE NO-GPU BAN, AT THE ONE DOOR EVERY VAST RENTAL GOES THROUGH.
    # `PUT /asks/{id}/` is Vast's canonical create-instance call and the ONLY mutating call this repository
    # makes against `/asks/`. Three call sites reach it — `VastBackend.submit` and `vast_bid_semantics_probe`
    # twice — and the probe does NOT go through `VastBackend.submit`, so a gate on `submit` alone would have
    # left a real rental path open. Gating the HTTP verb instead covers every present caller and every future
    # one, and it is BELOW the retry loop, so a relaunch faces it again: CLAUDE.md §6, a relaunch is a NEW
    # PURCHASE.
    # ⚠ CREATION ONLY, and the shape of the test is what guarantees that: board reads are `GET`, teardown is
    # `DELETE /instances/{id}/`, stop and reap are `PUT /instances/{id}/`. None of them match, so a stood-down
    # account still tears down a host that somehow exists — the failure `vast_rental_hold` names, where
    # "stood down" quietly becomes "billing unwatched".
    if method in ("PUT", "POST", "PATCH") and path.startswith("/asks/"):
        _gpu_ban.assert_permitted(f"vast {method} {path} — creating a rental (Vast create-instance)")
    # ---- the wave-scoped board cache (see `board_read_cache`) ------------------------------------------
    # GET + `/search/asks/` + cache open, or this is a no-op. `_hops` is deliberately NOT part of the key:
    # a retry of the same query is the same query, and the entry it writes is what a later hop would fetch.
    #
    # ⚠⚠ `no_cache` IS NOT A CONVENIENCE — IT EXISTS BECAUSE `/search/asks/` IS A ROTATING SAMPLE.
    # `sample_board` measured it (2026-07-27): even at `limit=512` one read returns ~225 offers, two
    # identical reads 20 s apart share only ~174 machines, P(present, then absent) = 0.245, and the
    # cumulative distinct machines across 30 reads reached 591 and was still climbing. So a caller that
    # issues the SAME query N times is not being wasteful — it is deliberately deepening a ~38 % sample,
    # and merging two reads measurably improves what we can buy at (best-4 -5.8 %). A cache that collapsed
    # those N reads to one would silently turn `samples=2` back into `samples=1` and delete that gain while
    # reporting a cache hit. Re-samplers MUST opt out, and this flag is how.
    _ck = None
    if not no_cache and _BOARD_CACHE_TTL_S > 0 and method == "GET" and path.startswith(_BOARD_CACHE_PATH):
        import time as _time
        _ck = _board_cache_key(path, params)
        _hit = _BOARD_CACHE.get(_ck)
        if _hit is not None and _hit[0] > _time.monotonic():
            _BOARD_CACHE_STATS["hits"] += 1
            _BOARD_CACHE_STATS["saved_calls"] += 1
            return _hit[1]
        _BOARD_CACHE_STATS["misses"] += 1
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
            _payload = json.loads(r.read().decode() or "{}")
            if _ck is not None:
                # ⚠ ONLY A SUCCESSFUL READ IS REMEMBERED. An exception leaves the cache untouched, so a
                # throttled or timed-out board read is re-attempted by the next unit instead of being
                # frozen in for the rest of the wave — §6's "an unreadable market is not a cheap one".
                import time as _time
                _BOARD_CACHE[_ck] = (_time.monotonic() + _BOARD_CACHE_TTL_S, _payload)
            return _payload
    except urllib.error.HTTPError as e:                            # surface the provider's error body, not a bare 4xx
        detail = e.read().decode()
        if e.code == 410 and _hops < 3:                           # follow the server's own "Use <path> instead"
            m = re.search(r"Use\s+(/api/\S+?)\s+instead", detail)
            if m:
                return _vast_request(method, m.group(1), api_key, params=params, body=body, _hops=_hops + 1,
                                     no_cache=no_cache)
        if e.code == 429 and _hops < 6:                           # rate limit (Vast DELETE threshold ~3 req/s): a
            import time                                           # burst teardown/collect 429s partway -> back off
            time.sleep(1.5 * (_hops + 1))                         # (1.5,3,4.5,...s) and retry so we drain the loop
            return _vast_request(method, path, api_key, params=params, body=body, _hops=_hops + 1,
                                 no_cache=no_cache)
        # ★★ A BARE 403 FROM THE EDGE IS TRANSIENT, AND NOT RETRYING IT COST A CLEARED WINDOW
        #    (2026-07-27, 11:08-11:10 AM ET, run 30278451510).
        #
        # WHAT HAPPENED. The market gate read the board fine at 11:06 AM ET (54 offers, 1.483x basis, CLEAR)
        # and dispatched. Two minutes later the launch's every call answered `403 Forbidden` — the board
        # read, `/instances/`, and all four `/search/asks/` inside submit — so it rented 0/4. Three minutes
        # after THAT, a `collect` on the same key listed instances normally. Same key, same endpoints, works
        # either side of the failure: transient, not an authorisation problem.
        #
        # HOW WE KNOW IT IS THE EDGE AND NOT VAST'S APP. The body is nginx's HTML error page
        # (`<html><head><title>403 Forbidden</title></head>`). Vast's own errors are JSON envelopes
        # (`{"success": false, "error": "resources_unavailable"}`), and a revoked key answers in JSON too. An
        # HTML 403 is a proxy/WAF verdict, which is a throttle in every case we have observed.
        #
        # WHY IT FIRES AT ALL: this account drives several lanes from ONE key, and a single 4-unit launch
        # alone issues ~8 `/search/asks/` calls in a burst (one per unit in `submit`, plus one per unit in
        # `_vast_ondemand_base_by_machine`) on top of the gate's. Bursting is the trigger, so backing off is
        # the remedy.
        #
        # ⚠ GET ONLY — NEVER A MUTATION. Retrying a POST that created an instance would double-rent, and a
        # 403 arriving AFTER the create was accepted is exactly the case where that happens. A read is
        # idempotent, so this is safe; a write is not, so it still fails fast and loudly.
        if e.code in (403, 500, 502, 503, 504) and method == "GET" and _hops < 5:
            import time
            time.sleep(2.0 * (_hops + 1))                         # 2,4,6,8,10 s -> ~30 s of patience total
            return _vast_request(method, path, api_key, params=params, body=body, _hops=_hops + 1,
                                 no_cache=no_cache)
        raise RuntimeError(f"vast API {method} {path} -> {e.code}: {detail[:400]}") from e
    # ★★ A CONNECTION THAT NEVER COMPLETED GOT **NO** RETRY AT ALL, WHICH IS BACKWARDS
    #    (2026-07-27, 2:20 PM ET, run 30292566268).
    #
    # The handler above retries a 403/5xx — an answer we did not like — but it only catches `HTTPError`. A
    # TIMEOUT or a refused/reset connection raises `URLError` (or a bare `TimeoutError`), which is NOT an
    # HTTPError, so it fell straight through and killed the caller on the FIRST attempt. That is exactly
    # inverted: a request that got no answer at all is MORE obviously transient than one that got a 403.
    #
    # It cost the collect step of the 2:20 PM tick: `mode_collect` -> `_live_instances` -> here ->
    # `urllib.error.URLError: <urlopen error timed out>`, so the reap did not run. Same shape as the 1:21 PM
    # incident, different transport — the board was slow rather than forbidden (the same tick's S3 listing
    # took 5 minutes, so the runner's egress was degraded generally).
    #
    # ⚠ GET ONLY, for the identical reason as above: retrying a POST that already created an instance would
    # double-rent, and a timeout is precisely the case where the request may have succeeded server-side while
    # the response was lost. A read is idempotent; a write is not, so a write still fails fast and loudly.
    # `URLError` must be caught AFTER `HTTPError` — HTTPError SUBCLASSES URLError, so the reverse order would
    # silently swallow every HTTP status and lose the provider's error body.
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        if method == "GET" and _hops < 5:
            import time
            time.sleep(2.0 * (_hops + 1))                         # same 2,4,6,8,10 s ladder as the 403 path
            return _vast_request(method, path, api_key, params=params, body=body, _hops=_hops + 1,
                                 no_cache=no_cache)
        raise RuntimeError(f"vast API {method} {path} -> unreachable: {type(e).__name__}: {e}") from e


# How many offers to ask Vast for. See the note on `limit` in `_vast_offer_query` — the default of 64 was
# hiding ~72 % of the board from every purchase decision. ONE home for the number (CLAUDE.md rule 1).
_VAST_SEARCH_LIMIT = 512


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
        # ★★ THE LIMIT IS LOAD-BEARING, AND ITS ABSENCE WAS COSTING ~26 % ON EVERY PURCHASE
        #    (measured 2026-07-27, run 30294964932, `vast_board_volatility.py`).
        #
        # Vast's `/search/asks/` defaults to **64 rows**. This query set no `limit`, so every market gate and
        # every `submit` in this repo has been deciding on the first 64 offers. Measured against the same
        # board in the same second: `limit=512` returns **225** offers, the default returns **64** — we were
        # seeing 28 % of the market.
        #
        # WHY THAT IS NOT MERELY "A SMALLER SAMPLE". The truncation is not random: this query is ORDERED BY
        # `dph_total asc` while `rank_offers_by_usd_per_ns` ranks by **$/ns**. Those are different orderings,
        # and the benched cards that can be priced at all are not the cheapest per HOUR. So chopping the list
        # at 64 removes gradeable offers preferentially — priceable fell 143-147 (full) to 28-29 (default) —
        # and the surviving best-4 mean was **+26.3 % more expensive** on every single paired read
        # (full $0.003050/ns = 0.89x basis; truncated $0.003853/ns = 1.13x basis).
        #
        # ★ IT ALSO MANUFACTURED THE "MARKET" VOLATILITY THAT PROMPTED THIS. trimcrae asked whether hourly
        # polling was too slow, because the gate read 1.261x basis at 9:13:04 AM ET and 2.436x at 9:16:28 AM.
        # Across the 24 committed snapshots the decision is perfectly predicted by how many rows came back:
        # every 64-row read cleared (8/8), and in the morning — same bench table, so no confounder — every
        # read shorter than 64 held (0/10 cleared). The board had not moved; the page had.
        #
        # 512 covers the ~225-offer board with room to grow, and costs ~0.3 s of extra latency (0.68 s vs
        # 0.39 s). It is nowhere near a rate concern: the response carries `x-ratelimit-limit: 500` per a
        # 60-second window and this repo's entire usage sat at 3-4.
        #
        # `_vast_ondemand_base_by_machine` already passed `limit: 512` for exactly this reason; it simply was
        # never applied to the query that decides what we BUY.
        "limit": _VAST_SEARCH_LIMIT,
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


def sample_board(key, res: ResourceSpec, samples: int = 1, gap_s: float = 1.0):
    """Read `/search/asks/` `samples` times and MERGE, keeping each machine's cheapest sighting.

    ★★ WHY MERGING IS NOT PARANOIA: THE ENDPOINT RETURNS A ROTATING SAMPLE, NOT THE BOARD
       (measured 2026-07-27, `vast_board_volatility.py`, run 30295566972).

    Even with an explicit `limit=512`, one read returns ~225 offers — but two identical reads 20 s apart share
    only ~174 machines, and the cumulative distinct machines seen across 30 reads reached **591 and was still
    climbing**. The measured probability that a machine present in one read is absent from the next is
    **0.245**. So a single read is a ~38 % sample of the qualifying board, drawn afresh each time.

    Merging two reads measurably improves the price we can buy at, because it deepens the sample rather than
    waiting for the market to change: best-1 **-5.6 %**, best-4 **-5.8 %**, best-19 **-3.9 %**.

    ⚠ DEFAULT `samples=1`, i.e. NO behaviour change, and that default is deliberate rather than timid. The
    Vast edge throttle that has taken down this repo's launches twice fires on BURSTS — a single 4-unit
    `submit` already issues ~8 `/search/asks/` calls in seconds, and blindly doubling that is a good way to
    trade a 5 % price gain for a launch that rents nothing. Sustained RATE is not the constraint (the route
    reports `x-ratelimit-limit: 500` per 60 s against our 3-4), so a GATE — which makes one read and one
    decision — can afford `samples=2` cheaply. Callers opt in where the burst maths says it is safe.

    Merging keeps the CHEAPEST sighting per machine, never the latest, so a merged board can only be better
    than either read alone, and every hard filter still applies downstream in `rank_offers_by_usd_per_ns`.
    """
    import time as _t
    merged, n_reads = {}, 0
    for i in range(max(1, int(samples))):
        if i:
            _t.sleep(max(0.0, gap_s))
        try:
            # `no_cache=True`: these N reads are the WHOLE POINT — `/search/asks/` returns a rotating
            # sample, so identical queries return different machines. A wave-scoped board cache
            # (`board_read_cache`) would collapse them to one and silently undo the merge.
            offers = (_vast_request("GET", "/search/asks/", key, no_cache=True,
                                    params={"q": json.dumps(_vast_offer_query(res))}) or {}).get("offers", [])
        except Exception as e:  # noqa: BLE001
            # A failed EXTRA read must never lose the reads we already have — returning fewer samples is a
            # smaller error than failing a gate that had a perfectly good board in hand.
            print(f"  [board] sample {i + 1}/{samples} failed ({type(e).__name__}: {e})", flush=True)
            if not merged:
                raise
            break
        n_reads += 1
        for o in offers:
            mid = str(o.get("machine_id"))
            prev = merged.get(mid)
            try:
                price = float(o.get("min_bid") if res.interruptible and o.get("min_bid") is not None
                              else o.get("dph_total", 1e9))
            except (TypeError, ValueError):
                continue
            if prev is None or price < prev[0]:
                merged[mid] = (price, o)
    return [o for _p, o in merged.values()], n_reads


def _vast_ondemand_base_by_machine(key, res: ResourceSpec = None) -> dict:
    """machine_id -> on-demand `dph_base`, from a real `type: "on-demand"` query.

    The ONLY source of a true on-demand price. A bid-type query cannot provide one (see `_vast_bid_price`).
    Best-effort: any failure returns {} so the caller simply bids uncapped rather than failing to launch."""
    try:
        spec = ResourceSpec(**{**vars(res or ResourceSpec()), "interruptible": False})
        q = _vast_offer_query(spec)
        # The query now carries `_VAST_SEARCH_LIMIT` itself. This line stays only so the intent is explicit at
        # the call site, and it references the CONSTANT rather than repeating the literal 512 that used to sit
        # here — a second copy of the number is how the two reads drift apart, and for a year this was the
        # only caller that asked for the whole board while the one that decides purchases did not.
        q["limit"] = _VAST_SEARCH_LIMIT
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
    """Throughput this card may use at the ternary size, or None if it may not borrow a benched figure. PURE.

    ★ THE NAME-MATCHING NOW LIVES IN ONE PLACE (`vast_cost_model.card_of`), 2026-07-27. This function used to
    carry its OWN longest-first substring sweep — a second implementation of the very thing the shared table
    exists to prevent. Both copies gave `RTX 4090D`, a cut-down SKU, the full RTX 4090 figure. Deferring means
    the allow-list argument (and the refusal of anti-conservative aliases) cannot be true in one file and
    false in the other. For an alias entry the value is a LOWER BOUND; ask `_vcm.throughput_provenance`."""
    c = _vcm.card_of(gpu_name)
    return None if c is None else _MEASURED_NS_PER_DAY_84K[c]


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


def rank_offers_by_usd_per_ns(offers, res: ResourceSpec, max_hourly_usd=None):
    """PURE: (measured, capable) where `measured` is every qualifying offer SORTED by expected $/ns.

    Extracted from `_select_cheapest_offer` — which now calls it — so that "which offers qualify and what do
    they cost per ns" has exactly ONE implementation. The market guard needs the whole ranked list (a fleet
    of N units buys the N best offers, not the single best one N times), and a second copy of this filter
    would be free to disagree with the one that actually rents.

    `measured` is [(usd_per_ns, price, offer)] ascending; `capable` is [(price, offer)] for everything that
    passed the hard filters, including cards that were never benched and therefore have no $/ns."""
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
        if res.exclude_machine_ids and str(o.get("machine_id")) in {
                str(m) for m in res.exclude_machine_ids}:
            continue                                              # host known to refuse starts (see ResourceSpec)
        if res.require_gpu:
            # A HARD card constraint, applied with the other hard filters rather than as a ranking preference.
            # Only a throughput bench sets it (ResourceSpec.require_gpu): for that job, landing on a different
            # card does not make the run cheaper, it makes the RESULT WRONG and files it under the card we
            # asked for.
            # SUFFIX-anchored, the same rule `vast_cost_model._model_key` uses, so "give me an rtx4090" cannot
            # be satisfied by the cut-down `RTX 4090D` and "rtxpro6000s" cannot be satisfied by the
            # workstation `RTX PRO 6000 WS`. A vendor prefix is still free.
            want = _vcm.normalise_gpu_name(res.gpu)
            if want and not _vcm.normalise_gpu_name(o.get("gpu_name")).endswith(want):
                continue
        if res.min_ns_per_h:
            # THE DEADLINE FILTER — hard, and applied here beside the other hard filters rather than as a
            # ranking preference, for the reason in `ResourceSpec.min_ns_per_h`: a preference loses to $/ns
            # every time a cheap slow card is on the board, which is the case it exists for. An unbenched
            # card has no throughput to check and therefore cannot be shown to clear.
            _nsph = _vcm.ns_per_hour(o.get("gpu_name"))
            if not _nsph or _nsph < float(res.min_ns_per_h):
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
        return [], []
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
    # ★★ SCORE AT THE RATE WE WILL ACTUALLY BID — NOT AT THE ONE THE POLICY WOULD HAVE CHOSEN
    #    (measured 2026-07-31; this is how a 2.61x rental cleared a 1.92x ceiling).
    #
    # WHAT HAPPENED. `collect`'s self-heal dispatches every re-placement with `bid_floor_mult=2.0` — the
    # retention bid trimcrae authorised for churning legs — which sets `VAST_BID_FLOOR_MULT` and makes
    # `_vast_bid_price` return TWICE the market floor. But this line passed `billed_usd_h=None` for an
    # interruptible offer, so `score_offer` re-derived a bid from `vast_cost_model.recommended_bid` (floor
    # plus a small staleness tick) and never saw the multiplier. The ceiling was therefore evaluated against
    # a price we were never going to pay.
    #
    # THE CONTROLLED REPRODUCTION, on the exact offer from `ternary-vast-rental-receipt.json`
    # (machine 34345, RTX 3090, `min_bid`/`dph_total` $0.08148):
    #     VAST_BID_FLOOR_MULT unset -> scored $0.005338/ns, bid $0.0831/hr, SELECTED
    #     VAST_BID_FLOOR_MULT=2.0   -> scored $0.005338/ns, bid $0.1630/hr, SELECTED   <- identical score
    # and the instance then billed `dph_base` $0.16 + storage = $0.1711/hr = **$0.00891/ns, 2.612x basis**,
    # against a $0.006539/ns cap. The score did not move because it could not see the multiplier.
    #
    # ⚠ THIS IS THE §1 RULING'S OWN CASE: "the flag and the refusal are the same number". The board flagged
    # `⚠ PAYING OVER THE 1.92x LINE` on a rental this function had just approved. One number, one decision.
    #
    # `_vast_bid_price(o)` is the one home of "what will this offer cost per hour", multiplier included and
    # capped at the machine's on-demand price exactly as Vast charges it. Passing it makes the cap bind on
    # the real rate for BOTH tiers, so the on-demand branch is unchanged (it already passed its own price).
    # ⚠ ONLY FOR AN OFFER THAT ACTUALLY CARRIES `min_bid`. A real bid-tier offer always does; one that does
    # not is either an on-demand row or a synthetic fixture, and for those the previous `None` (let
    # `score_offer` derive it) is preserved EXACTLY. Widening it would change which offers are priceable at
    # all — and that silently moved a model-preference fallback in `_select_cheapest_offer`, which is a
    # different decision from the one being fixed here.
    def _billed(p, o):
        if not res.interruptible:
            return p
        return _vast_bid_price(o) if o.get("min_bid") is not None else None

    scored = [(_vcm.score_offer(o, job, billed_usd_h=_billed(p, o)), p, o) for p, o in capable]
    measured = sorted(((s.usd_per_ns, p, o) for s, p, o in scored if s is not None),
                      key=lambda t: (t[0], t[1]))
    # THE BINDING CEILING (see ResourceSpec.max_usd_per_ns). Applied to the SCORED figure — storage priced at
    # the job's real disk, on the rate we are actually billed — never to the quote, which the rate forensics
    # measured as understating the true rate by 9.05-26.41 % with no constant offset (it scales with each
    # machine's own storage_cost, which varies ~4.5x across a single board).
    if res.max_usd_per_ns is not None:
        cap = float(res.max_usd_per_ns)
        measured = [t for t in measured if t[0] <= cap]
        # And an UNPRICEABLE offer cannot be shown to clear, so once a cap is set the unmeasured fallback in
        # `_select_cheapest_offer` must not be reachable: taking a card we have never benched would wave
        # through exactly the spend the cap exists to refuse. Emptying `capable` makes that structural.
        if not measured:
            capable = []
    return measured, capable


def _select_cheapest_offer(offers, res: ResourceSpec, max_hourly_usd=None):
    """PURE: cheapest single-GPU, rentable offer meeting the VRAM (and optional price) constraint, preferring the
    requested GPU model (client-side substring) but FALLING BACK to any capable card if that model isn't offered.
    Ranked by the price we'd actually PAY: the interruptible bid floor (min_bid) when res.interruptible, else the
    on-demand total. Returns the chosen offer dict, or None if nothing qualifies."""
    measured, capable = rank_offers_by_usd_per_ns(offers, res, max_hourly_usd)
    if not capable:
        return None
    if measured:
        return measured[0][2]
    substr = _VAST_GPU_SUBSTR.get(res.gpu)                        # nothing benched -> prefer the requested model
    if substr:
        preferred = [(p, o) for p, o in capable
                     if substr in str(o.get("gpu_name", "")).replace(" ", "").upper()]
        capable = preferred or capable
    return min(capable, key=lambda po: po[0])[1]


# ★★ THE STATUSES IN WHICH AN INSTANCE STILL HOLDS ITS UNIT'S SLOT — the ONE home for that question
# (CLAUDE.md §1), because at least three call sites need it and each one that re-typed a status comparison
# has been wrong in a different way.
#
#   * `running` — obviously occupied.
#   * `queued`  — a FRESH RENTAL whose image is still pulling reads `actual_status=loading` /
#                 `cur_state=stopped` for as long as 2 h 57 min on this account. Counting that as free is
#                 how a launcher rents a SECOND GPU for work it has already paid to start, so `queued`
#                 counts as occupied and the conservative direction is preserved exactly where it belongs.
#
# Everything else — `completed` (Vast's `exited`/`finished`), `failed`, `stopped` (offline/destroyed) — is a
# box that will never do more work. It is still an instance RECORD, and still billing for its volume, but it
# is not a host: the unit it was rented for has nobody working on it.
VAST_OCCUPYING_STATUSES = ("running", "queued")


def vast_instance_occupies_slot(inst) -> bool:
    """Does this instance record still hold its unit's slot — i.e. is a host actually working on that unit?

    ★★ WHY THIS EXISTS: "EXISTS" AND "RUNNING" ARE DIFFERENT QUESTIONS AND THE LANE KEPT ANSWERING THE FIRST
    (measured 2026-07-27, twice in one day). `ternary_vast_watchdog.classify` was handed
    `instance_alive = inst is not None` and reassured about four hosts whose GPUs had already been reclaimed,
    for 85 minutes. Hours later `ternary_vast_launch.live_unit_hosts` — a different file, the same mistake —
    counted three `exited` boxes as occupied slots, so `gate_for_mode` reported "4 already running" over a
    cohort with ONE live leg, declined to price the market at all, and left three RUNG 2b replicates dead
    indefinitely. Both sites had a comment explaining why the conservative reading was safe; neither had a
    predicate, so neither could be corrected once.

    PURE, and `None` (no record at all) is FALSE — a unit with no instance is unambiguously unhosted.
    """
    if not inst:
        return False
    return _vast_status(inst.get("actual_status"), inst.get("cur_state")) in VAST_OCCUPYING_STATUSES


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
# same code path serves any S3-compatible store.
#
# SECURITY — THIS IS THE ONE PLACE THE CREDENTIAL IS CHOSEN. A rented community host is UNTRUSTED and the
# credential goes into its onstart script in PLAINTEXT (there is no secret-injection mechanism on Vast), so
# the host's operator can read it. Until 2026-07-27 what went out was the repo's general CI key, which can
# write anywhere in sagemaker-us-east-2-<acct> — every leg's checkpoints and results, i.e. the evidence base
# for the whole program. See research/compute/credential-exposure-2026-07-27.md and the runbook it links.
#
# The fix is a DEDICATED credential whose IAM policy allows only the six S3 actions a leg performs, on only
# the lane prefixes it touches (rendered from s3_scoped_policy.py). It arrives in its own env vars so that
# CI keeps its broad key for SageMaker/analysis and the host gets only the narrow one:
#
#     VAST_S3_ACCESS_KEY_ID / VAST_S3_SECRET_ACCESS_KEY [/ VAST_S3_SESSION_TOKEN]
#
# TRANSITION-SAFE, DELIBERATELY. If those are unset the old AWS_* pair is forwarded exactly as before, so
# lanes in flight when this landed keep running and trimcrae can create the scoped user whenever he gets to
# it. If they ARE set, the broad AWS_* credential is NOT forwarded at all — the point is exclusivity, not
# preference. The host still sees standard AWS_* names, so no pipeline changes.
_OBJECT_STORE_ENV_KEYS = (
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_DEFAULT_REGION",
    "OBJECT_STORE_ENDPOINT", "OBJECT_STORE_REGION",
)
# The credential triple, and where the scoped credential supplies each member. Anything not in this map
# (region, endpoint) is plain configuration, carries no secret, and passes through in either mode.
_SCOPED_CRED_ALIASES = {
    "AWS_ACCESS_KEY_ID": "VAST_S3_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY": "VAST_S3_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN": "VAST_S3_SESSION_TOKEN",
}


def object_store_cred_mode(source_env=None) -> str:
    """'scoped' if the dedicated leg credential is configured, else 'inherited' (the broad CI key).

    Reported by the launchers so the readout says which credential a rental was given WITHOUT printing any
    part of it — the whole incident began with a diagnostic that printed values it had not named."""
    env = source_env if source_env is not None else os.environ
    return "scoped" if (env.get("VAST_S3_ACCESS_KEY_ID") and env.get("VAST_S3_SECRET_ACCESS_KEY")) \
        else "inherited"


def _object_store_env(source_env=None) -> dict:
    """Collect the checkpoint-store credential/config to forward into a rented instance.

    Prefers the DEDICATED leg credential (VAST_S3_*) and, when it is present, forwards ONLY that — the broad
    CI key must never ride along beside it. Falls back to the AWS_* pair when no scoped credential is
    configured, so nothing breaks before trimcrae creates the IAM user. Shape-agnostic: a long-lived scoped
    key and an STS triple both work, because the session token is just another member of the same map.
    PURE (reads a dict) -> unit-tested."""
    env = source_env if source_env is not None else os.environ
    scoped = object_store_cred_mode(env) == "scoped"
    out = {}
    for k in _OBJECT_STORE_ENV_KEYS:
        alias = _SCOPED_CRED_ALIASES.get(k)
        if alias is None:                                   # region/endpoint: configuration, not a secret
            v = env.get(k)
        elif scoped:
            v = env.get(alias)                              # scoped mode: the CI value is NOT a fallback
        else:
            v = env.get(k)
        if v:
            out[k] = v
    return out


def s3_checkpoint_uri(job_name: str, bucket: str = None, prefix: str = "vast") -> str:
    """Build a per-job checkpoint prefix on the REUSED S3 bucket (the one the AWS jobs already use). `bucket`
    defaults to $VAST_CKPT_BUCKET (e.g. the SageMaker default bucket, sagemaker-us-east-2-<acct>). A campaign
    launcher sets JobSpec.checkpoint_uri to this so each leg checkpoints per-unit and resumes after preemption."""
    bucket = bucket or os.environ.get("VAST_CKPT_BUCKET")
    if not bucket:
        raise ValueError("s3_checkpoint_uri needs a bucket (arg or $VAST_CKPT_BUCKET)")
    return f"s3://{bucket}/{prefix}/{job_name}/ckpt"


# Best-effort self-STOP on ANY exit, KEY-FREE (2026-07-24, trimcrae: never share VAST_API_KEY with community
# hosts). VAST_API_KEY is deliberately NOT forwarded to a rented host (a real exposure: the key can spend the
# account's credit), so the host's only lever is to end its own container — Vast bills the GPU while the
# container runs.
#
# ⛔ CORRECTED 2026-07-27 — THIS IS BEST-EFFORT, NOT A GUARANTEE, AND THE OLD TEXT SAID OTHERWISE.
# The previous version of this comment (and CLAUDE.md §6) claimed "the auto-teardown wrapper guarantees no
# idle-GPU billing anywhere". It does not, and the failure is silent. MEASURED by controlled reproduction in
# a private PID namespace (`unshare -fp --mount-proc`, a child shell playing the onstart script exactly as
# Vast runs it — see `tests/test_vast_idle_guard.py::test_the_selfstop_chain_cannot_end_a_container`):
#
#     poweroff        -> "System has not been booted with systemd as init system (PID 1). Can't operate."
#     shutdown -h now -> the same
#     kill -9 1       -> returns SUCCESS and PID 1 SURVIVES. A PID-namespace init ignores any signal it has
#                        no handler for, and SIGKILL cannot be handled (kernel SIGNAL_UNKILLABLE). This is
#                        why the failure was invisible: the chain's `||` never advanced past a "success".
#     kill -9 -1      -> kills every other process AND the caller, and PID 1 SURVIVES
#                        (`man 2 kill`: pid == -1 signals every permitted process "except for process 1")
#
# So on an unprivileged container the chain kills the JOB and leaves the CONTAINER up: `actual_status`
# stays `running` and the GPU keeps billing. Observed exactly that on 2026-07-27, both 5a-KS legs, for
# ~53 min. `kill -9 1` is dropped here because it is provably a no-op that returns 0.
# ⇒ THE GUARANTEE IS CONTROL-PLANE ONLY: `ternary_vast_launch.collect` (result-in-S3 / recorded-failure /
#   runtime backstop / `vast_idle_guard` verdict) + stop_all, where the key never leaves CI. What the host
#   can still usefully do is stop DOING the work and say, loudly and in the log the control plane reads,
#   that it could not stop the meter.
_VAST_SELFSTOP = (
    'ct_selfstop(){ rc=$?; '
    'echo "[selfstop] job exited rc=$rc; attempting container self-stop"; '
    'poweroff 2>/dev/null; shutdown -h now 2>/dev/null; sleep 2; '
    'echo "[selfstop] STILL UP: poweroff/shutdown need privileges this container does not have, and no '
    'signal can reach PID 1 from inside its own namespace. THE GPU IS STILL BILLING until the CI reap '
    'destroys this instance (vast_idle_guard). Killing the job now so it at least stops working."; '
    'kill -9 -1 2>/dev/null; '
    'return $rc; }'
)

# ★ THE CRASH-LOOP BRAKE, and why it is a COUNTER rather than a flag. When the onstart script exits, Vast
# re-runs it; if whatever killed it is a property of the RENTAL rather than of the attempt (a dead
# credential, a missing stage cache, a host with no CUDA), the next attempt dies the same way and the box
# spins. Measured 2026-07-27: a ~13-30 s loop — stage cache MISS -> `FAILED at staging` -> `Killed` -> repeat
# — on two instances at once, billing throughout; and on 2026-07-26 the same shape left seventeen 168-byte
# archived attempts on the first 5a-KS smoke.
#
# A one-shot "already ran, refuse" FLAG would be wrong and would cost a whole leg: a spot preemption stops
# the instance, `collect` nudges it back to `running`, the container restarts and the leg is SUPPOSED to
# resume from its checkpoint. That legitimate restart and a crash-loop differ only in RATE, so the brake
# counts starts in a window: three inside CT_WIN is not something a healthy leg does, while a resume hours
# later starts from an empty window. Holding idle (rather than exiting) is deliberate — an exit just gets
# re-fired, whereas a quiet hold stops the churn, stops re-doing the same failing work, and lets the log go
# silent, which is exactly the WEDGED signal `vast_idle_guard` reaps on.
_VAST_CRASHLOOP_BRAKE = (
    'CT_STARTS=${CT_STARTS:-/root/.vast_starts}; CT_WIN=${CT_WIN:-900}; CT_MAX=${CT_MAX:-3}\n'
    'ct_t=$(date +%s); echo "$ct_t" >> "$CT_STARTS" 2>/dev/null || true\n'
    'ct_n=$(awk -v t=$((ct_t-CT_WIN)) \'$1+0>=t\' "$CT_STARTS" 2>/dev/null | wc -l)\n'
    'echo "[selfstop] container start ${ct_n:-?} within the last ${CT_WIN}s"\n'
    'if [ "${ct_n:-0}" -ge "$CT_MAX" ]; then\n'
    '  echo "[selfstop] CRASH-LOOP BRAKE: ${ct_n} container starts in ${CT_WIN}s. This rental keeps '
    'restarting into the same failure, so re-running the job would burn GPU and produce nothing. Holding '
    'idle and letting the log go silent so the CI idle guard reaps this instance."\n'
    '  while true; do sleep 3600; done\n'
    'fi'
)


def _vast_onstart(spec: JobSpec, self_terminate_argv, extra_env=None) -> str:
    """Build the instance onstart script: arm the crash-loop brake, arm the KEY-FREE best-effort self-stop
    EXIT trap, then run the job command. `extra_env` is merged UNDER spec.env (spec.env wins). PURE (no I/O)
    -> unit-tested.

    ⛔ WHAT THE TRAP DOES AND DOES NOT DO. This docstring used to say the trap "halts its GPU billing (exits
    its container) ... never idles on the meter". That was measured false on 2026-07-27 — an unprivileged
    container cannot end itself, `kill -9 1` returns 0 while doing nothing, and two 5a-KS legs billed for
    ~53 min in a crash-loop with `actual_status: running` and `gpu_util: 0.0`. See the comment above
    `_VAST_SELFSTOP` for the controlled reproduction. The trap stops the JOB and says loudly that it could
    not stop the METER; the brake stops a rental re-running a job that keeps failing the same way; **the
    destroy is control-plane only** (`ternary_vast_launch.collect` + `vast_idle_guard`).

    ⚠ WHAT THIS SCRIPT EXPOSES, STATED PLAINLY. Everything below is written into the rental's onstart field
    IN CLEARTEXT and is readable by the host's operator, by anyone who can see the Vast instance record, and
    by anything that prints that record (which is exactly how the 2026-07-27 leak happened). Vast has no
    secret-injection mechanism, so this is not a bug to fix but a boundary to scope. What crosses it:

      * the object-store credential from `_object_store_env()` — the ONLY secret here, and the reason that
        function exists as the single choke point. It must be the DEDICATED, prefix-scoped `vast-leg-s3`
        credential (VAST_S3_* -> the policy in `s3_scoped_policy.py`), NOT the broad CI key. Until the
        scoped secret exists it falls back to AWS_*, and while it does, every rented host sees a key that
        can write any bucket in the account and launch SageMaker jobs — see the module comment above
        `_OBJECT_STORE_ENV_KEYS` and `research/compute/scoped-s3-credential-runbook.md`.
      * `spec.env` — lane configuration (bucket/prefix URIs, sampling parameters, git branch). Launchers
        must never put a secret in it; a presigned URL (short-lived, one object) is the right way to hand a
        host something private, as `nrv04_vast_launch` does for the packed MD env.
      * CHECKPOINT_URI / RESUME / SELF_LABEL, and the job command itself.

    WHAT IS WITHHELD: `VAST_API_KEY` — never on a community host, because it can spend the account's credit;
    teardown is key-free (the trap below) with the control-plane destroy staying in CI. The earlier version
    of this docstring named that withholding and nothing else, which read as reassurance while the AWS key
    went out in the clear. It is one item on the list, not the list.

    ★ ORDER IS LOAD-BEARING. The brake runs BEFORE the trap is armed and before the job: its whole job is to
    decide whether this rental should run the command at all, and once the trap is armed any exit tries to
    kill the shell that would have made that decision. And the trap is armed BEFORE the command so a
    `set -e`/signal death on the very first line is still covered.
    """
    cmd = " ".join(shlex.quote(a) for a in spec.command)
    env = {**(extra_env or {}), **spec.env}
    lines = ["#!/bin/bash", "set -o pipefail",
             f"export CHECKPOINT_URI={shlex.quote(spec.checkpoint_uri)}",
             f"export RESUME={'1' if spec.resume else '0'}",
             f"export SELF_LABEL={shlex.quote(spec.name)}"]      # the trap finds this instance by its label
    lines += [f"export {k}={shlex.quote(str(v))}" for k, v in env.items()]
    lines += [_VAST_CRASHLOOP_BRAKE, _VAST_SELFSTOP, "trap ct_selfstop EXIT", cmd]
    return "\n".join(lines)


class VastBackend(Backend):
    """Vast.ai — a MARKETPLACE of independent, individually-rentable GPU hosts (each rental is its OWN machine),
    which is exactly why it breaks the single-shared-pool wall-clock ceiling that a single-region cloud (GCP
    us-central1 Spot L4 pool) hits: N legs = N independent instances, genuinely N-wide with no shared-quota
    bottleneck. On our MD/FEP workload (memory-bandwidth-bound PME) the marketplace's RTX 4090s (1008 GB/s) are
    the a-priori cheapest $/ns. The catch is the PROVIDER not the card: community hosts are interruptible and can
    vanish, and — the #1 gotcha — a finished job that leaves its instance UP bleeds money on an idle GPU, so the
    instance MUST stop billing.

    ⛔ WHO CAN ACTUALLY STOP THE METER (corrected 2026-07-27; this said "two-layer" and the first layer does
    not work). VAST_API_KEY is NEVER put on a community host, so the host has no way to destroy anything, and
    — measured, not assumed — an UNPRIVILEGED CONTAINER CANNOT END ITSELF EITHER: `poweroff`/`shutdown` need
    an init this container does not have, `kill -9 -1` excludes PID 1 by definition and kills the caller, and
    `kill -9 1` RETURNS SUCCESS while being ignored. So:
      (1) HOST, BEST-EFFORT — the onstart EXIT trap and autoteardown's finally+watchdog stop the JOB (no more
          GPU work, no more churn) and record that they could not stop the BILLING; the crash-loop brake
          stops a rental re-running a job that keeps failing. None of this ends the rental.
      (2) CONTROL-PLANE, THE ONLY GUARANTEE — the CI collect reap (result-in-S3 / recorded-failure / runtime
          backstop / the `vast_idle_guard` verdict on a box that is up and doing nothing) + stop_all, with
          the key staying in CI.
    Anything that claims the host halts its own billing is wrong, and cost ~53 min of billed idle on two
    5a-KS legs on 2026-07-27 before it was measured.

    NOTE (must smoke before a fleet): the exact Vast REST endpoints/query schema drift between API versions; the
    LOAD-BEARING logic — cheapest-verified-offer selection and the key-free-self-stop onstart — is factored
    into pure, unit-tested helpers (`_select_cheapest_offer`, `_vast_onstart`), so a one-instance smoke only has
    to confirm the HTTP shapes, not the science."""
    name = "vast"

    def self_terminate_cmd(self):
        # KEY-FREE, BEST-EFFORT self-stop: try to exit this container, with NO API key on the host. On an
        # unprivileged container none of this can succeed (see the class docstring and the comment above
        # `_VAST_SELFSTOP`) — it is kept because it costs nothing and DOES work where the container is
        # privileged, and because `kill -9 -1` at least stops the job from doing more GPU work. The
        # guaranteed DESTROY is control-plane — the CI collect reap + stop_all, key never leaving CI.
        # (`kill -9 1` removed: measured to return 0 while doing nothing, which is worse than useless
        # because it makes an `||` chain report success.)
        return ["bash", "-c", "poweroff 2>/dev/null; shutdown -h now 2>/dev/null; kill -9 -1 2>/dev/null; true"]

    def submit(self, spec: JobSpec) -> Handle:
        # ⛔ THE OPERATOR HOLD IS CHECKED BEFORE THE BOARD IS EVEN READ. Not after pricing, not after a
        # qualify pass: a stood-down account must not spend an API call deciding what it is not allowed to
        # buy, and reading the board first would let a market verdict be reported for a decision that is not
        # the market's. Creation only — destroy/stop/collect never reach here.
        _hold = vast_rental_hold()
        if _hold:
            raise RentalHeldByOperator(
                f"⏸ VAST IS STOOD DOWN — no rental may be created until {VAST_RENTAL_HOLD} is deleted. "
                f"Reason on record: {_hold.get('reason', '(none given)')}"
                + (f" · paused {_hold['paused_utc']}" if _hold.get("paused_utc") else "")
                + ". Teardown, collect and reap are unaffected; banked checkpoints are untouched.")

        key = os.environ.get("VAST_API_KEY")
        if not key:
            raise RuntimeError("vast backend needs VAST_API_KEY (create a Vast.ai account first).")
        res = spec.resources
        q = _vast_offer_query(res)
        offers = _vast_request("GET", "/search/asks/", key,
                               params={"q": json.dumps(q)}).get("offers", [])
        max_hr = self.hourly_usd(res)                              # cap at our routing estimate + headroom
        max_hourly = (max_hr * 2.0 if max_hr else None)
        offer = _select_cheapest_offer(offers, res, max_hourly_usd=max_hourly)
        if offer is None:
            # TYPED, because the caller must tell this apart from a fault (see `NoQualifyingOffer`). The board
            # was READ — `len(offers)` proves it — and simply had nothing buyable within the spec. That is the
            # price guard working, not a broken launcher, and the two must not produce the same CI signal.
            raise NoQualifyingOffer(
                f"vast: no rentable verified offer for {res} (of {len(offers)} offers)")
        # Forward ONLY the checkpoint-store credential into the rented host — the science needs S3, not Vast.
        # VAST_API_KEY is deliberately NOT forwarded (never expose the account key to a community host); the host
        # tears down key-free by exiting its container, and CI destroys it (2026-07-24). Which credential that is
        # gets decided in ONE place, `_object_store_env` — scoped `vast-leg-s3` when configured, else the broad
        # CI key with the exposure that implies. Say which, on the record, without printing any part of it.
        extra = dict(_object_store_env())
        # WHAT THE MARKETPLACE SAID WE RENTED, forwarded so the container can record it next to its own result.
        # The throughput tables are keyed on `gpu_name`, but a leg can only see the CUDA DEVICE name, and the
        # two differ ("RTX 4090" vs "NVIDIA GeForce RTX 4090"; "RTX PRO 6000 WS" vs the full Blackwell string).
        # Without this a bench result cannot be matched back to the offer that produced it except by string
        # guessing — which is precisely how a leg that fell back to a Quadro RTX 8000 was tabulated as an A10
        # and helped get the 2026-07-24 grid withdrawn.
        mode = object_store_cred_mode()
        print(f"  [cred] object-store credential: {mode}"
              + ("" if mode == "scoped" else "  ** BROAD CI KEY — see research/compute/"
                                             "scoped-s3-credential-runbook.md **"), flush=True)
        if mode == "scoped":
            # A scoped key that does not cover this lane's prefix produces a leg that runs for hours and then
            # 403s on upload — the one outcome worse than the exposure. Warn at LAUNCH, where it is cheap to
            # see. Both targets are checked because they diverge: on the NR-V04 lanes `checkpoint_uri` is the
            # `vast/<name>/ckpt` default that nothing reads, while every real write goes to `RESULT_S3`.
            # Non-fatal on purpose: a wrong guess here must never be able to stop a fleet.
            try:
                from s3_scoped_policy import covers            # local import: keeps gpu_backend dependency-free
                for target in {spec.checkpoint_uri, (spec.env or {}).get("RESULT_S3")}:
                    if target and not covers(target):
                        print(f"  [cred] WARNING: {target} is not covered by the scoped policy — register "
                              f"its prefix in s3_scoped_policy.LANE_PREFIXES or this leg cannot upload",
                              flush=True)
            except Exception:  # noqa: BLE001 — an advisory check must not be able to abort a launch
                pass
        # ★★ A CAPACITY REFUSAL AT START IS ANSWERED HERE, IN THE SAME SUBMIT — NOT A TICK LATER
        #    (measured 2026-07-29; this used to create once, ignore the answer, and hand back a Handle).
        #
        # WHAT THE EVIDENCE SHOWED. The ternary lane and the step-1 fan-out ask the SAME market for the same
        # thing: a field-by-field diff of `ternary_vast_launch.resource_spec()` against
        # `congeneric_fanout_vast.FANOUT_RES` differs in exactly ONE field — `disk_gb` 60 vs 80 — so the
        # ternary lane's `disk_space >= 60` board is a strict SUPERSET of the fan-out's `>= 80`, and ternary
        # asks the smaller `disk` at create. Nor is it the hosts: every machine that refused ternary that
        # morning (29711, 28164, 12227, 41950) appears in `step1-fanout-map.json` `realised_rentals` as a
        # host the fan-out rented and RAN on — 29711 four times up to 2.32 h, 12227 five times up to 1.92 h.
        # The two lanes are refused by the same mechanism at similar rates; the difference is only that a
        # 19-unit fan-out absorbs a refusal and a 2-unit lane loses its whole tick to one.
        #
        # SO THE FIX IS NOT IN THE ASK, IT IS IN THE RESPONSE. CLAUDE.md §6 already rules that a capacity
        # refusal means "destroy and pick another host — do not queue, do not raise the bid", and that is
        # what this loop does at the one moment the fact is knowable for free.
        #
        # ⚠ THIS ADDS NO NEW PRICE GATE AND WEAKENS NONE, and that is structural rather than a promise: every
        # retry re-enters `_select_cheapest_offer` with the SAME `ResourceSpec`, so `res.max_usd_per_ns` —
        # the ceiling the launcher's market gate cleared on — filters each replacement exactly as it filtered
        # the first. `ResourceSpec.max_usd_per_ns`'s own docstring names this case: the ceiling travels with
        # the spec so that a non-clearing offer "is never selected in the first place — INCLUDING ON EVERY
        # FALLBACK AFTER A CAPACITY REFUSAL". A retry can therefore only ever be at or under the approved
        # rate; if nothing under it survives the widened exclusion, this raises instead of buying.
        #
        # ⚠ AND IT RE-RANKS THE BOARD WE ALREADY HAVE — no second `/search/asks/` read. That keeps the API
        # burst identical to before (the shared key answers an HTML 403 to bursts) and keeps the replacement
        # priced off the same snapshot the gate saw.
        refusals = []
        while True:
            # Rebuilt per offer: `VAST_OFFER_GPU_NAME` is the card the marketplace SAID we rented, and filing
            # a leg under the previous candidate's card is the 2026-07-24 mislabelling incident.
            extra["VAST_OFFER_GPU_NAME"] = str(offer.get("gpu_name") or "")
            onstart = _vast_onstart(spec, self.self_terminate_cmd(), extra_env=extra)
            # Rent the chosen ask: PUT /asks/{id}/ is Vast's canonical create-instance endpoint (POST
            # /instances/ 404s). On success the body carries new_contract = the instance id.
            body = {
                "client_id": "me",
                "image": spec.image or "nvidia/cuda:12.4.1-base-ubuntu22.04",
                "disk": max(40, res.disk_gb),
                "onstart": onstart,
                "runtype": "ssh",
                "label": spec.name,
                "target_state": "running",
            }
            if res.interruptible:                                 # interruptible => set an optimized bid $/hr
                # Cap the bid at THIS machine's real on-demand price. Requires a separate on-demand query: the
                # offer in hand came from a bid-type search, whose dph_base is the floor by definition, so it
                # cannot bound anything. Best-effort — an empty map just means we bid uncapped, as before.
                od = _vast_ondemand_base_by_machine(key, res).get(str(offer.get("machine_id")))
                bid = _vast_bid_price(offer, ondemand_base=od)
                if bid is not None:
                    body["price"] = bid
                    if od:
                        print(f"  [bid] ${bid}/hr (floor ${offer.get('min_bid')}, on-demand cap ${od:.4f})",
                              flush=True)
            created = _vast_request("PUT", f"/asks/{offer['id']}/", key, body=body)
            inst_id = created.get("new_contract") or created.get("id")
            if inst_id is None:
                raise RuntimeError(f"vast: instance create returned no id: {created}")
            # ROBUST EXPLICIT START: creating the ask does NOT reliably launch the container — diag showed 3/4
            # created instances stuck at intended_status="stopped" (cpu 0%, no capacity msg) while a 4th ran,
            # SAME code: the start PUT races Vast finishing the create, so on some hosts it's lost and the box
            # sits stopped forever. Poll and re-issue the start until Vast reports it running, bounded.
            if self._ensure_running(inst_id, key) != "refused":
                break
            # REFUSED. Destroy FIRST, so the meter and the disk stop before we do anything else — an
            # unprivileged container cannot end itself, so the control plane doing it here is the only thing
            # that can (see the class docstring). Best-effort: a failed destroy must not swallow the refusal,
            # because `collect`'s reap is the backstop and it needs to still see the instance.
            mid = str(offer.get("machine_id"))
            refusals.append({"machine_id": mid, "instance": str(inst_id),
                             "offer": offer.get("id"), "gpu_name": offer.get("gpu_name"),
                             "why": "resources_unavailable on start"})
            try:
                _vast_request("DELETE", f"/instances/{inst_id}/", key)
                print(f"  [capacity] machine {mid} refused the start — instance {inst_id} DESTROYED, "
                      f"$0 further. Picking another host (CLAUDE.md §6: do not queue, do not raise the bid).",
                      flush=True)
            except Exception as e:  # noqa: BLE001 — collect's reap is the backstop; never hide the refusal
                print(f"  [capacity] machine {mid} refused the start and destroying instance {inst_id} "
                      f"failed ({type(e).__name__}: {e}) — collect's reap will take it.", flush=True)
            if len(refusals) >= _VAST_START_REFUSAL_TRIES:
                raise CapacityRefusedAtStart(
                    f"vast: {len(refusals)} host(s) refused the start with resources_unavailable "
                    f"(machines {', '.join(r['machine_id'] for r in refusals)}); nothing is running and "
                    f"$0 is billing. Not a price problem — the board was read and priced.", refusals)
            # Widen the exclusion on a COPY: `res` is the caller's object and other units may hold a
            # reference to it (`ResourceSpec.exclude_machine_ids` documents the same hazard for the fleet
            # loop). The ceiling rides along untouched, so the replacement is bounded by the approved rate.
            res = dataclasses.replace(
                res, exclude_machine_ids=tuple(sorted(set(map(str, res.exclude_machine_ids)) |
                                                      {r["machine_id"] for r in refusals})))
            offer = _select_cheapest_offer(offers, res, max_hourly_usd=max_hourly)
            if offer is None:
                raise CapacityRefusedAtStart(
                    f"vast: {len(refusals)} host(s) refused the start with resources_unavailable "
                    f"(machines {', '.join(r['machine_id'] for r in refusals)}) and no remaining offer of "
                    f"{len(offers)} clears this spec's ceiling. Nothing is running, $0 is billing.", refusals)
        return Handle(backend=self.name, job_id=str(inst_id),
                      # min_bid is carried so a launcher can report the market FLOOR alongside what we bid —
                      # the premium is otherwise invisible and gets baked into the next cost estimate.
                      # machine_id is carried so a FLEET launcher can avoid stacking several legs on
                      # one machine. Offers are per GPU slot, but a host advertising slots it cannot
                      # actually schedule will accept both rentals and refuse both starts — observed
                      # 2026-07-25, machine 53989 took two legs of the same fleet and answered
                      # resources_unavailable for each.
                      extra={"offer": offer["id"], "dph": offer.get("dph_total"),
                             "machine_id": offer.get("machine_id"),
                             # Carried so a caller can price the offer it ACTUALLY got: $/ns needs the card,
                             # and without it a launcher can only report the quote it was shown.
                             "gpu_name": offer.get("gpu_name"),
                             "min_bid": offer.get("min_bid"), "bid": body.get("price"),
                             # Hosts that refused BEFORE this one, already destroyed and $0. Carried so a
                             # caller with an object store can put them in the perishable
                             # `capacity_refusal_trend` window — which is a READOUT and may never gate, so
                             # nothing here reads it back. Empty on the normal path.
                             "start_refusals": refusals,
                             "resume": spec.resume})

    def _ensure_running(self, inst_id, key, attempts=8, delay_s=6):
        """Re-issue PUT state=running until the instance's intended_status/actual_status is 'running' (fixes the
        create/start race that leaves bid instances stuck 'stopped'). Bounded; logs the final state.

        ⚠ **THIS DOES NOT ACTUALLY CLOSE THE RACE — MEASURED 2026-07-27, NOT INFERRED.** Instance 46003951
        (`bench-rtx5090-9p5nm`) exited this loop on ATTEMPT 1 with `intended=running actual=None`, ~2 s after
        the create. Two `diag` reads afterwards:

            12:55 ET  actual=loading  cur_state=stopped  intended=stopped  msg="#7 Building dependency tree..."
            13:00 ET  actual=created  cur_state=stopped  intended=stopped  msg="Successfully loaded ...:latest"

        The image pull SUCCEEDED and the box still never ran: Vast reports `intended_status=running`
        optimistically on a fresh create, this loop takes that as done, and Vast settles the instance to
        `intended_status=stopped` once provisioning finishes. So the exit condition is satisfied by a value
        that has not converged yet, and the "ROBUST EXPLICIT START" comment above overstates what this does.

        JUDGED BY THE STEP-1 LANE, 2026-07-27, and the census lane's instinct not to fix it here was right —
        but for a sharper reason than submit latency. The observed settle-back to `intended_status=stopped`
        happens AFTER provisioning finishes, i.e. MINUTES after create (12:55 -> 13:00 ET above). **No
        bounded submit-time loop can observe it at all**, so "poll to a terminal state" does not close this
        race either — it just adds minutes per unit across a fleet and still returns before the settle-back.
        The race is not closeable at submit time; it is only detectable later.

        So what is fixed here is the HONESTY of the exit, at zero latency cost: `actual == "running"` is
        evidence and returns silently; `intended == "running"` alone is an echo of the PUT we just issued and
        now returns with an explicit "ACCEPTED, not yet confirmed" line, so a caller can no longer read an
        optimistic echo as a live box. Recovery stays where it already works — the per-tick collector nudge
        (`PUT /instances/{id}/ {"state":"running"}`), which `relaunch_market_gate.EXEMPTIONS` correctly
        treats as restarting a host we already hold rather than as a new purchase.

        THE REAL FIX, and it belongs with the idle-guard work: a host that never reaches `actual=running`
        after N nudges must be DESTROYED AND ITS MACHINE EXCLUDED. It bills while producing no throughput,
        which is infinite realised $/ns — precisely the case `exclude_machine_ids` exists for and precisely
        the case $/ns ranking is structurally blind to, so without an explicit exclusion such a host keeps
        winning selection and keeps failing. The recovery in the meantime is the nudge the collectors already do
        (`PUT /instances/{id}/ {"state":"running"}`), which `relaunch_market_gate.EXEMPTIONS` correctly treats
        as restarting a host we already hold rather than as a new purchase.

        ★★ AND IT NOW READS THE REPLY, WHICH IT USED TO THROW AWAY (measured 2026-07-29).

        `PUT /instances/<id>/ {"state": "running"}` is the SAME call the per-tick collector makes, and when
        the machine cannot schedule us Vast answers it — HTTP 200, JSON body — with

            {"success": false, "error": "resources_unavailable",
             "msg": "Required resources are currently unavailable, state change queued."}

        `_vast_request` returns that body rather than raising (only an HTTP error status raises), so the old
        loop discarded the provider's own verdict, printed `intended=stopped` eight times, warned, and handed
        back a Handle. The launcher then recorded `outcome: launched, n_rented: 1` and armed a watchdog for a
        host that was never going to start. The refusal was rediscovered 15-35 minutes later by `collect`,
        which issues the identical PUT and prints the identical error — i.e. **the fact was available at
        rental time and thrown away**. Verbatim, run 30455581714 (9:25 AM ET) vs run 30458695218 (10:01 AM
        ET), same instance class:

            [vast] start 46197224 attempt 1..8: intended=stopped actual=None -> loading
            [vast] WARN 46197224 did not reach intended=running after 8 attempts     <- the reply was RIGHT THERE
            ...35 min later...
            -> NUDGED 46199407: vast replied {'success': False, 'error': 'resources_unavailable', ...}

        So this returns a VERDICT instead of None:
          * `"running"`      — `actual == "running"`: evidence, the container is up.
          * `"accepted"`     — `intended == "running"` only: an optimistic echo, unchanged behaviour.
          * `"refused"`      — Vast said `resources_unavailable`. The host is declining, and CLAUDE.md §6's
                               standing rule for that is "destroy and pick another host, do not wait it out".
          * `"unconfirmed"`  — the attempts ran out with no answer either way (the pre-existing WARN case).
        `submit` acts on `"refused"`; every other value keeps the previous behaviour exactly.
        """
        import time
        verdict = "unconfirmed"
        for i in range(attempts):
            try:
                resp = _vast_request("PUT", f"/instances/{inst_id}/", key, body={"state": "running"})
                # THE ONE LINE THIS DOCSTRING IS ABOUT. `success: false` with an error string is a normal
                # 200 response on Vast, so it never raised and never got looked at.
                if str((resp or {}).get("error") or "") == "resources_unavailable":
                    print(f"[vast] start {inst_id} attempt {i + 1}: REFUSED — vast replied {str(resp)[:240]}",
                          flush=True)
                    return "refused"
            except Exception as e:  # noqa: BLE001 — a transient error shouldn't abort the retry loop
                print(f"[vast] start {inst_id} attempt {i + 1}: {e}", flush=True)
            inst = next((x for x in _vast_request("GET", "/instances/", key, params={"owner": "me"})
                         .get("instances", []) if str(x.get("id")) == str(inst_id)), None)
            intended, actual = (inst or {}).get("intended_status"), (inst or {}).get("actual_status")
            print(f"[vast] start {inst_id} attempt {i + 1}: intended={intended} actual={actual}", flush=True)
            if actual == "running":
                return "running"                                  # EVIDENCE: the container is up.
            if intended == "running":
                # NOT evidence — an echo of the request we just made. Returning here is still correct
                # (see the judgement in the docstring: the settle-back to intended=stopped happens MINUTES
                # later, so no bounded submit-time loop can observe it, and polling to a terminal state
                # would add minutes per unit across a fleet). What was wrong is that the caller could not
                # TELL the two apart, so a rental with an optimistic echo read exactly like a live box.
                print(f"[vast] start {inst_id}: intended=running but actual={actual!r} — start ACCEPTED, "
                      f"not yet confirmed running. Vast reports intended optimistically on a fresh create "
                      f"and may settle it back to 'stopped' after provisioning; the per-tick collector nudge "
                      f"is what recovers that, and a host that never reaches actual=running should be "
                      f"destroyed and excluded (infinite realised $/ns is invisible to $/ns ranking).",
                      flush=True)
                return "accepted"
            time.sleep(delay_s)
        print(f"[vast] WARN {inst_id} did not reach intended=running after {attempts} attempts", flush=True)
        return verdict

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
