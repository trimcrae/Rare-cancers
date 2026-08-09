"""Every endpoint producer's `--check` must actually REFUSE a drifted artifact.

WHY THIS FILE EXISTS. This repository has already shipped a `--check` that swallowed its argument,
regenerated its own reference, and exited 0 -- so a hand edit to a pooled clinical proportion
persisted undetected. `test_emc_systemic_therapy_pooling_check.py` was written for that incident and
states the principle: the repair's own failure mode is a verify mode that cannot fail. Six new
producers shipped with `--check` wired into CI and nothing testing that the check is real.

So every test here calls the REAL `main(["--check"])` on the REAL committed artifact at its REAL
path, perturbs that file on disk, asserts a non-zero return, restores the exact original bytes in a
`finally`, and asserts the restoration -- so a crashed test cannot leave a corrupted artifact behind.
Nothing is monkeypatched. Mock the thing under test and you test the mock.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, MANUSCRIPTS)

import endpoint_corpus as C  # noqa: E402
import endpoint_prior_art_audit as A  # noqa: E402
import endpoint_regime_figure as F  # noqa: E402
import endpoint_regime_map as M  # noqa: E402
import orr_dcr_reread as R  # noqa: E402
import placebo_arm_calibration as P  # noqa: E402

#: (module, artifact path, a mutation that must be detected)
JSON_PRODUCERS = [
    pytest.param(C, C.OUT, ("C6_counts", "distinct_trials"), id="endpoint_corpus"),
    pytest.param(R, R.OUT, ("R5_reporting_census", "arms_recovered"), id="orr_dcr_reread"),
    pytest.param(M, M.OUT, ("G4_what_the_map_reads", "conditions_placed"), id="endpoint_regime_map"),
    pytest.param(P, P.OUT, ("P3_classification", "control_arms_found"),
                 id="placebo_arm_calibration"),
    pytest.param(A, A.OUT, ("A5_the_gap", "conditions_in_the_low_response_regime"),
                 id="endpoint_prior_art_audit"),
]


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


def _restore(path, original):
    with open(path, "wb") as fh:
        fh.write(original)
    assert _read(path) == original, f"failed to restore {path}"


@pytest.mark.parametrize("module,artifact,keypath", JSON_PRODUCERS)
def test_check_passes_on_the_committed_artifact(module, artifact, keypath):
    assert module.main(["--check"]) == 0, f"{artifact} does not re-derive as committed"


@pytest.mark.parametrize("module,artifact,keypath", JSON_PRODUCERS)
def test_check_refuses_a_perturbed_headline_number(module, artifact, keypath):
    original = _read(artifact)
    try:
        doc = json.loads(original.decode("utf-8"))
        section, key = keypath
        assert section in doc, f"{section} missing from {artifact}"
        assert key in doc[section], f"{key} missing from {artifact}[{section}]"
        value = doc[section][key]
        doc[section][key] = (value + 1) if isinstance(value, (int, float)) else "TAMPERED"
        with open(artifact, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        assert module.main(["--check"]) != 0, (
            f"{artifact}: --check accepted a changed {section}.{key}, so it verifies nothing")
    finally:
        _restore(artifact, original)


@pytest.mark.parametrize("module,artifact,keypath", JSON_PRODUCERS)
def test_check_refuses_a_deleted_section(module, artifact, keypath):
    original = _read(artifact)
    try:
        doc = json.loads(original.decode("utf-8"))
        doc.pop(keypath[0], None)
        with open(artifact, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        assert module.main(["--check"]) != 0, (
            f"{artifact}: --check accepted a missing {keypath[0]}")
    finally:
        _restore(artifact, original)


def test_the_figure_check_passes_and_refuses_a_perturbation():
    """The figure is an SVG rather than JSON, so it gets its own byte-level perturbation."""
    assert F.main(["--check"]) == 0
    original = _read(F.OUT)
    try:
        with open(F.OUT, "wb") as fh:
            fh.write(original.replace(b"</svg>", b"<!-- tampered --></svg>"))
        assert F.main(["--check"]) != 0, "the figure --check accepted altered bytes"
    finally:
        _restore(F.OUT, original)


def test_every_producer_with_a_ci_check_is_in_the_regeneration_script():
    """A seventh producer must not be added to CI and silently omitted from the dependency order.

    The regeneration script exists because a corpus change once shipped without regenerating what
    reads it, and only CI noticed -- after a push.
    """
    root = os.path.dirname(MANUSCRIPTS)
    root = os.path.dirname(root)
    with open(os.path.join(root, ".github/workflows/tests.yml")) as fh:
        ci = fh.read()
    with open(os.path.join(root, "scripts/regenerate_endpoint_chain.sh")) as fh:
        script = fh.read()
    for name in ("endpoint_corpus", "orr_dcr_reread", "endpoint_regime_map",
                 "placebo_arm_calibration", "endpoint_prior_art_audit", "endpoint_regime_figure"):
        if f"{name}.py --check" in ci:
            assert name in script, (
                f"{name} runs --check in CI but is absent from the regeneration order, so a change "
                f"upstream of it can ship stale")
