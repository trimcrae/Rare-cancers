#!/usr/bin/env python3
"""WHAT CUDA THE BAKED IMAGE ACTUALLY REQUIRES — run INSIDE the container, $0, no GPU needed.

★★ THE QUESTION, AND WHY IT MUST BE MEASURED RATHER THAN READ OFF A COMMENT (2026-07-31).
`gpu_backend.ResourceSpec.min_cuda` is **13.0**, and it is applied TWICE — once server-side in
`_vast_offer_query` (`cuda_max_good: {gte: min_cuda}`) and again client-side in
`rank_offers_by_usd_per_ns` — so it prunes the board harder than any other single filter. Its justification
is a comment: *"DIAG PROOF that the `cuda-version=12.6` env pin did NOT actually take — the baked env's PTX
is CUDA-13-class."*

Against that, `research/compute/Dockerfile.ternaryfep` is `FROM nvidia/cuda:12.6.3-runtime-ubuntu22.04` and
pins `cuda-version=12.6` in the conda env, and `Dockerfile.nr4a3fep` states its OpenMM *"runs on any >=12.6
host driver"*. Two documents, opposite claims, and the more expensive one is enforced. A 12.6 BASE image does
NOT settle it — conda-forge is free to resolve a newer CUDA runtime into the env, which is exactly what would
make the comment true. So: ask the ENV, not the Dockerfile.

★ THE DISCRIMINATING OBSERVATION. OpenMM's CUDA platform does not ship pre-compiled kernels for our systems —
it **JIT-compiles them at run time with NVRTC** (or, on older builds, by shelling out to `nvcc`). The PTX ISA
version NVRTC emits is fixed by the NVRTC library's own CUDA version, and the host DRIVER must support that
ISA or the load fails with `CUDA_ERROR_UNSUPPORTED_PTX_VERSION` — the precise error the 13.0 floor was raised
on. **So the version of `libnvrtc` inside the env IS the required host CUDA level**, and it is readable with
`ctypes` on a machine with no GPU at all.

Reported alongside it, because a single number with no corroboration is how the last wrong constant survived:
  * every CUDA-ish package the env actually resolved (`conda-meta`), so a `cuda-version=12.6` pin that did not
    take is visible as itself;
  * the CUDA *runtime* version (`libcudart`), which is what OpenMM links against;
  * OpenMM's own version and the CUDA plugin binaries it loads;
  * the embedded-fatbin architectures in the plugin, when `cuobjdump` is present — pre-compiled SASS/PTX would
    be a second, independent constraint.

⛔ WHAT THIS DOES NOT DO. It does not change a filter, does not rent anything and does not need a GPU. It
prints a verdict — the minimum `cuda_max_good` a host must advertise — and writes it as JSON. Acting on the
verdict is a separate, reviewed edit, because the whole point is that this constant should move only on
evidence.
"""
from __future__ import annotations

import ctypes
import glob
import json
import os
import subprocess
import sys


def _nvrtc_version():
    """(major, minor, libpath) from the env's own libnvrtc, or (None, None, reason).

    ctypes rather than a shell out: NVRTC's `nvrtcVersion` is the authoritative statement of which PTX ISA
    this env will emit, and reading it from the loaded library cannot disagree with what OpenMM will use."""
    cands = []
    for root in (os.environ.get("CONDA_PREFIX"), "/opt/mamba/envs/rbfe", sys.prefix):
        if root:
            cands += sorted(glob.glob(os.path.join(root, "lib", "libnvrtc.so*")))
    cands += sorted(glob.glob("/usr/local/cuda*/lib64/libnvrtc.so*"))
    cands += ["libnvrtc.so"]
    for p in cands:
        try:
            lib = ctypes.CDLL(p)
            maj, mnr = ctypes.c_int(), ctypes.c_int()
            if lib.nvrtcVersion(ctypes.byref(maj), ctypes.byref(mnr)) == 0:
                return maj.value, mnr.value, p
        except Exception:  # noqa: BLE001 — a candidate that will not load is simply not the answer
            continue
    return None, None, "no loadable libnvrtc found in the env"


def _cudart_version():
    cands = []
    for root in (os.environ.get("CONDA_PREFIX"), "/opt/mamba/envs/rbfe", sys.prefix):
        if root:
            cands += sorted(glob.glob(os.path.join(root, "lib", "libcudart.so*")))
    cands += sorted(glob.glob("/usr/local/cuda*/lib64/libcudart.so*")) + ["libcudart.so"]
    for p in cands:
        try:
            lib = ctypes.CDLL(p)
            v = ctypes.c_int()
            if lib.cudaRuntimeGetVersion(ctypes.byref(v)) == 0 and v.value:
                return v.value // 1000, (v.value % 1000) // 10, p
        except Exception:  # noqa: BLE001
            continue
    return None, None, "no loadable libcudart found in the env"


def _conda_cuda_packages():
    """Every resolved package whose name mentions cuda/nvrtc/openmm, from conda-meta. The direct test of
    whether the Dockerfile's `cuda-version=12.6` pin actually took."""
    out = {}
    for root in (os.environ.get("CONDA_PREFIX"), "/opt/mamba/envs/rbfe", sys.prefix):
        if not root:
            continue
        for p in glob.glob(os.path.join(root, "conda-meta", "*.json")):
            name = os.path.basename(p)[:-5]
            low = name.lower()
            if not any(k in low for k in ("cuda", "nvrtc", "openmm", "cudnn", "nvidia")):
                continue
            try:
                with open(p) as fh:
                    d = json.load(fh)
                out[d.get("name", name)] = {"version": d.get("version"), "build": d.get("build"),
                                            "channel": (d.get("channel") or "").split("/")[-1]}
            except (OSError, ValueError):
                continue
        if out:
            break
    return out


def _openmm_info():
    info = {}
    try:
        import openmm  # noqa: PLC0415
        info["openmm_version"] = getattr(openmm.version, "version", None)
        info["openmm_git"] = getattr(openmm.version, "git_revision", None)
        info["openmm_dir"] = os.path.dirname(openmm.__file__)
        try:
            from openmm import Platform  # noqa: PLC0415
            info["platforms"] = [Platform.getPlatform(i).getName()
                                 for i in range(Platform.getNumPlatforms())]
            info["plugin_load_failures"] = list(Platform.getPluginLoadFailures())
        except Exception as e:  # noqa: BLE001 — no GPU on a CI runner; the version is still the answer
            info["platform_probe_error"] = f"{type(e).__name__}: {e}"
    except Exception as e:  # noqa: BLE001
        info["openmm_import_error"] = f"{type(e).__name__}: {e}"
    libs = []
    for root in (info.get("openmm_dir"), os.environ.get("CONDA_PREFIX"), "/opt/mamba/envs/rbfe"):
        if root:
            libs += glob.glob(os.path.join(root, "**", "*CUDA*.so*"), recursive=True)
    info["cuda_plugin_libs"] = sorted({p for p in libs})[:12]
    return info


def _fatbin_archs(libs):
    """Pre-compiled device code in the CUDA plugin, if `cuobjdump` exists. A SECOND constraint when present:
    embedded PTX carries its own ISA version independently of what NVRTC emits at run time."""
    out = {}
    for p in libs[:4]:
        try:
            r = subprocess.run(["cuobjdump", "-lelf", "-lptx", p], capture_output=True, text=True, timeout=60)
            txt = (r.stdout or "") + (r.stderr or "")
            archs = sorted({t for t in txt.replace(".", " ").split() if t.startswith(("sm_", "compute_"))})
            out[os.path.basename(p)] = archs or (txt.strip().splitlines()[:3] or ["(no device code listed)"])
        except Exception as e:  # noqa: BLE001 — cuobjdump is a bonus, never the load-bearing evidence
            out[os.path.basename(p)] = [f"(cuobjdump unavailable: {type(e).__name__})"]
            break
    return out


def probe():
    nmaj, nmin, npath = _nvrtc_version()
    cmaj, cmin, cpath = _cudart_version()
    omm = _openmm_info()
    doc = {
        "_what": __doc__.split("\n")[0],
        "nvrtc": {"major": nmaj, "minor": nmin, "lib": npath,
                  "_why": "OpenMM JITs its CUDA kernels with NVRTC, so the PTX ISA it emits — and therefore "
                          "the minimum host driver — is set by THIS library's version, not by the base "
                          "image tag."},
        "cudart": {"major": cmaj, "minor": cmin, "lib": cpath},
        "conda_cuda_packages": _conda_cuda_packages(),
        "openmm": omm,
        "fatbin_archs": _fatbin_archs(omm.get("cuda_plugin_libs") or []),
    }
    req = None
    if nmaj is not None:
        req = float("%d.%d" % (nmaj, nmin))
    elif cmaj is not None:
        req = float("%d.%d" % (cmaj, cmin))
    doc["required_host_cuda"] = req
    doc["verdict"] = (
        "UNDETERMINED — neither libnvrtc nor libcudart could be loaded from the env; do NOT move min_cuda "
        "on this run." if req is None else
        "the env JITs against CUDA %s, so a host advertising cuda_max_good >= %s can run it. "
        "ResourceSpec.min_cuda should be %s." % (req, req, req))
    return doc


def _main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out, image, merge = None, os.environ.get("PROBE_IMAGE") or "", None
    for i, a in enumerate(argv):
        if a == "--json-out" and i + 1 < len(argv):
            out = argv[i + 1]
        if a == "--image" and i + 1 < len(argv):
            image = argv[i + 1]
        # The ONE HOME of the floor, merged across images: `gpu_backend.measured_min_cuda` reads it, and a
        # per-image key is what stops one image's measurement being applied to another's lane.
        if a == "--merge-into" and i + 1 < len(argv):
            merge = argv[i + 1]
    doc = probe()
    doc["image"] = image
    print(json.dumps(doc, indent=1))
    print("\n=== VERDICT ===\n" + doc["verdict"])
    if out:
        with open(out, "w") as fh:
            json.dump(doc, fh, indent=1)
        print("wrote %s" % out)
    if merge and image:
        try:
            with open(merge) as fh:
                agg = json.load(fh)
        except (OSError, ValueError):
            agg = {}
        agg.setdefault("_what", "MEASURED minimum host `cuda_max_good` per container image — the one home of "
                                "`ResourceSpec.min_cuda`. Written by probe_image_cuda.py from INSIDE each "
                                "image; never typed by hand.")
        agg.setdefault("_how", "OpenMM JITs its CUDA kernels with NVRTC, so the PTX ISA it emits — and hence "
                               "the minimum host driver — is set by the env's own libnvrtc, read with ctypes "
                               "on a runner with no GPU. Corroborated by the env's cuda-version / "
                               "cuda-nvrtc / libcudart.")
        agg.setdefault("images", {})
        agg["images"][image] = {
            "required_host_cuda": doc["required_host_cuda"],
            "nvrtc": "%s.%s" % (doc["nvrtc"]["major"], doc["nvrtc"]["minor"]),
            "cudart": "%s.%s" % (doc["cudart"]["major"], doc["cudart"]["minor"]),
            "cuda_version_pkg": (doc["conda_cuda_packages"].get("cuda-version") or {}).get("version"),
            "cuda_nvrtc_pkg": (doc["conda_cuda_packages"].get("cuda-nvrtc") or {}).get("version"),
            "openmm": (doc["conda_cuda_packages"].get("openmm") or {}).get("version"),
            "measured_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        }
        with open(merge, "w") as fh:
            json.dump(agg, fh, indent=1, sort_keys=True)
        print("merged %s into %s" % (image, merge))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
