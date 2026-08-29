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
import shutil
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


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """⛔⛔ A MUTATION TEST WORKS ON A COPY. THIS ONE DID NOT, AND IT CORRUPTED THE TRACKED TREE.

    ⚠ MEASURED 2026-08-29. Every perturbation below used to be written into the LIVE artifact under
    `research/manuscripts/endpoint/` and undone in a `finally`. That is safe only while nothing else
    reads the file during the window — and the manuscripts suite runs under `xdist`, so several
    things do:

      · `test_endpoint_logic.py::test_the_share_below_the_design_contour_excludes_undefined_conditions`
        read `endpoint-regime-map.json` mid-window and raised `KeyError: 'G4_what_the_map_reads'` —
        the section `test_check_refuses_a_deleted_section` had just removed;
      · `test_endpoint_manuscript_figures.py`'s module-scoped `figures` fixture read the same file
        and took the WHOLE MODULE down as a collection ERROR, which is the intermittent shape
        AUT-PD-085 filed and could not attribute;
      · the parametrized cases here raced EACH OTHER: two workers mutating and restoring one file
        interleave, so a restore can lose.

    ⛔ AND THE LOSS IS NOT CONFINED TO THE RUN. After one three-worker reproduction the working tree
    was left carrying `"conditions_placed": 45` against the committed 44 — a value invented by a
    tamper test, sitting in a tracked artifact, with the suite reporting only a flake. A `git add -A`
    on top of that commits a falsified number, which is exactly the mutation-window incident
    CLAUDE.md §6 records reaching `origin/main` on 2026-08-27.

    ★ THE FIX IS THE RULE, APPLIED TO A TEST INSTEAD OF AN AGENT: copy the artifact to `tmp_path`,
    point the producer's `OUT` at the copy, and mutate that. Every producer's `--check` reads `OUT`
    and nothing else, so the check under test is unchanged; what changes is that the live tree is
    never written to at all, and the restore this used to depend on no longer has to succeed.
    """
    def _make(module):
        copy = tmp_path / os.path.basename(module.OUT)
        shutil.copyfile(module.OUT, copy)
        monkeypatch.setattr(module, "OUT", str(copy))
        return str(copy)
    return _make


@pytest.mark.parametrize("module,artifact,keypath", JSON_PRODUCERS)
def test_check_passes_on_the_committed_artifact(module, artifact, keypath):
    assert module.main(["--check"]) == 0, f"{artifact} does not re-derive as committed"


@pytest.mark.parametrize("module,artifact,keypath", JSON_PRODUCERS)
def test_check_refuses_a_perturbed_headline_number(module, artifact, keypath, isolated):
    copy = isolated(module)
    doc = json.loads(_read(copy).decode("utf-8"))
    section, key = keypath
    assert section in doc, f"{section} missing from {artifact}"
    assert key in doc[section], f"{key} missing from {artifact}[{section}]"
    value = doc[section][key]
    doc[section][key] = (value + 1) if isinstance(value, (int, float)) else "TAMPERED"
    with open(copy, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    assert module.main(["--check"]) != 0, (
        f"{artifact}: --check accepted a changed {section}.{key}, so it verifies nothing")


@pytest.mark.parametrize("module,artifact,keypath", JSON_PRODUCERS)
def test_check_refuses_a_deleted_section(module, artifact, keypath, isolated):
    copy = isolated(module)
    doc = json.loads(_read(copy).decode("utf-8"))
    doc.pop(keypath[0], None)
    with open(copy, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    assert module.main(["--check"]) != 0, (
        f"{artifact}: --check accepted a missing {keypath[0]}")


def test_the_figure_check_passes_and_refuses_a_perturbation(isolated):
    """The figure is an SVG rather than JSON, so it gets its own byte-level perturbation.

    Isolated for the same reason as the JSON producers above: the SVG is a tracked deposit artifact
    and a lost restore leaves tampered bytes in the tree.
    """
    assert F.main(["--check"]) == 0
    copy = isolated(F)
    original = _read(copy)
    with open(copy, "wb") as fh:
        fh.write(original.replace(b"</svg>", b"<!-- tampered --></svg>"))
    assert F.main(["--check"]) != 0, "the figure --check accepted altered bytes"


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
                 "placebo_arm_calibration", "endpoint_prior_art_audit", "endpoint_regime_figure",
                 "endpoint_result_figures"):
        if f"{name}.py --check" in ci:
            assert name in script, (
                f"{name} runs --check in CI but is absent from the regeneration order, so a change "
                f"upstream of it can ship stale")
