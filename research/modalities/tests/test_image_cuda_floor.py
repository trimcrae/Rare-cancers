"""THE HOST CUDA FLOOR IS MEASURED PER IMAGE — pinned so it cannot drift back to a remembered constant.

WHAT THIS EXISTS TO STOP (2026-07-31). `ResourceSpec.min_cuda` was the constant 13.0, justified by a comment
asserting the baked env's PTX was CUDA-13-class. It was the second most expensive filter in the whole spec —
`vast-filter-ablation.json` measured 119 offers surviving at 13.0 against 134 at 12.6, and 6.2 % better $/ns —
and `probe_image_cuda.py`, run inside the image itself, showed the claim was false for the image that
actually runs: nvrtc 12.6, cudart 12.6, `cuda-version` 12.6, `cuda-nvrtc` 12.6.85.

The lesson is not "12.6 is the right number". It is that a filter whose bound is a CLAIM ABOUT OUR CONTAINER
must be derived from a probe of that container, so a re-bake moves the filter with it.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gpu_backend as gb  # noqa: E402

ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "image-cuda-requirements.json")


def test_the_artifact_exists_and_carries_its_evidence():
    with open(ART) as fh:
        doc = json.load(fh)
    t = doc["images"]["ternary-fep"]
    assert t["required_host_cuda"] == 12.6
    # The corroborating readings must travel with the number, or the next reader has a bare constant again.
    assert t["nvrtc"] == "12.6" and t["cudart"] == "12.6"
    assert t["cuda_version_pkg"] == "12.6" and t["cuda_nvrtc_pkg"].startswith("12.6")


def test_an_unprobed_image_keeps_the_conservative_fallback():
    """The whole safety argument. `pmxfep`, `nrv04vast` and `bioemu` are different stacks; inheriting the
    ternary image's floor would be the same error as inheriting a Dockerfile's claim."""
    assert gb.measured_min_cuda(None) == gb.CONSERVATIVE_MIN_CUDA
    assert gb.measured_min_cuda("docker.io/triskit23/an-image-nobody-probed:latest") == gb.CONSERVATIVE_MIN_CUDA
    assert gb.ResourceSpec().min_cuda == gb.CONSERVATIVE_MIN_CUDA


@pytest.mark.parametrize("ref", ["ternary-fep", "triskit23/ternary-fep",
                                 "docker.io/triskit23/ternary-fep:latest"])
def test_every_reference_form_resolves(ref):
    """The repo writes the image three ways in three places; a lookup that accepted one would silently return
    the fallback and look exactly like a measurement nobody had taken."""
    assert gb.measured_min_cuda(ref) == 12.6


def test_a_missing_or_broken_artifact_fails_SAFE(tmp_path):
    """Degrading to the LOOSE floor on an unreadable artifact would quietly buy hosts that cannot run the
    kernels — a crash, not a preemption, and this repo does not tolerate crashes."""
    assert gb.measured_min_cuda("ternary-fep", path=str(tmp_path / "nope.json")) == gb.CONSERVATIVE_MIN_CUDA
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert gb.measured_min_cuda("ternary-fep", path=str(bad)) == gb.CONSERVATIVE_MIN_CUDA


def test_each_lane_asks_for_its_OWN_image():
    import congeneric_fanout_vast as cfv
    import protfep_vast_launch as pv
    import ternary_vast_launch as tv
    assert tv.resource_spec().min_cuda == 12.6, "the ternary lane runs the image that was probed"
    assert cfv.FANOUT_RES.min_cuda == gb.measured_min_cuda(cfv.FEP_IMAGE)
    assert pv.RES.min_cuda == gb.measured_min_cuda(pv.VAST_IMAGE)


def test_the_floor_is_not_typed_anywhere_it_could_drift():
    """Rule 1. A second copy of the number is a second thing to forget when the image is re-baked."""
    import inspect
    for mod in (gb,):
        src = inspect.getsource(mod)
        assert src.count("min_cuda: float = CONSERVATIVE_MIN_CUDA") == 1
    import ternary_vast_launch as tv
    assert "min_cuda=float(os.environ.get(\"TVAST_MIN_CUDA\") or measured_min_cuda(VAST_IMAGE))" \
        in inspect.getsource(tv.resource_spec)
