"""A CI gate must fail on the thing it guards — never on its own missing dependency.

★★ WHY THIS EXISTS: THE SAME DEFECT, ON THE SAME LINE, TWICE.

`step1-fanout-autoscale.yml` runs `pytest research/modalities/tests/test_congeneric_fanout.py` as the gate
that decides whether the fan-out may rent GPUs. The launcher reads `steps.costgate.outcome`; on `failure` it
records `decision: cost_model_red` and places nothing. So an *import* error in the gate reads, in the
committed readout, as **"the cost model is broken"** — and nothing about it points at a missing wheel.

  2026-07-27  PyYAML absent. The gate parses the workflow itself to prove `reap` is wired into the
              launcher's mode table, so it died on `import yaml`, blocked every tick, committed no readout,
              and the terminus release of the 18 held edges could not fire.
  2026-08-01  numpy absent. Two tests added on 07-31 03:05 UTC `import numpy as np` to assert what
              `_apply_seed` actually reaches. Every tick since has recorded `cost_model_red`. Measured
              across the two hours before the fix: 11 consecutive `cost_model_red` readouts.

Both passed in the dev sandbox, which carries far more than CI's `pip install -q boto3 pytest pyyaml`. The
2026-07-27 fix wrote a comment saying "pyyaml is NOT optional here… it passed locally only because the dev
sandbox happens to have PyYAML" — and the comment did not stop the identical thing happening to numpy,
because a comment cannot see an import somebody adds later. So the list is now DERIVED from what the gated
module imports (CLAUDE.md §1: a total is derived, never typed).

⚠ WHY NOT `pytest.importorskip`. Because that is the same bug wearing a nicer badge: the two numpy tests
assert the RNG seeding that makes a replicate independent, and a gate that silently skips them still reports
green while checking less than it claims. A gate whose coverage can quietly shrink is the "guard that cannot
fire" pattern this repo keeps re-learning. Install the dependency; do not weaken the gate.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

MODALITIES = Path(__file__).resolve().parents[1]
REPO = MODALITIES.parents[1]
WORKFLOWS = REPO / ".github" / "workflows"

#: pip name -> the module name it actually provides, for the few where they differ. Anything absent from
#: this map is assumed to install a module of the same name, which is true of every package in use here.
PROVIDES = {"pyyaml": "yaml", "pillow": "PIL", "scikit-learn": "sklearn", "python-dateutil": "dateutil",
            "beautifulsoup4": "bs4", "protobuf": "google"}

#: Modules a runner always has beyond the stdlib, or that pytest itself brings.
ALWAYS = {"pytest", "_pytest", "py", "pluggy", "packaging", "iniconfig"}

_PIP = re.compile(r"pip install\s+((?:-\w+\s+)*)([^\n|&;]+)")
_PYTEST_GATE = re.compile(r"pytest\s+((?:-\S+\s+)*)(\S*tests/\S+\.py)")


def _jobs(text: str) -> list[str]:
    """Each job's text, split on the two-space `job-name:` key, so one job's pip install is not credited
    to another job's gate — different jobs get different runners and different environments."""
    parts = re.split(r"\n  (?=[A-Za-z0-9_-]+:\n)", text)
    return parts if len(parts) > 1 else [text]


def _installed(job_text: str) -> set[str]:
    mods = set(ALWAYS)
    for m in _PIP.finditer(job_text):
        for tok in m.group(2).split():
            name = re.split(r"[<>=!\[]", tok.strip("'\"").lower())[0]
            if name and not name.startswith("-"):
                mods.add(PROVIDES.get(name, name))
    return mods


def _imports(path: Path) -> set[str]:
    """Every top-level module name imported ANYWHERE in the file — including inside functions.

    Function-level imports are the whole point: both incidents came from an `import` that a top-of-file
    scan would not have seen. `numpy` is imported inside two test bodies, `yaml` inside one.
    """
    tree = ast.parse(path.read_text())
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            out.add(node.module.split(".")[0])
    return out


def _third_party(mods: set[str]) -> set[str]:
    """Drop the stdlib and anything this repo supplies itself."""
    repo_local = {p.stem for p in MODALITIES.glob("*.py")} | {p.stem for p in MODALITIES.glob("tests/*.py")}
    return {m for m in mods
            if m not in sys.stdlib_module_names and m not in repo_local and not m.startswith("_")}


def _gates() -> list[tuple[Path, str, Path]]:
    """(workflow, job_text, gated test file) for every `pytest …/tests/*.py` run in a workflow."""
    out = []
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        text = wf.read_text()
        for job in _jobs(text):
            for m in _PYTEST_GATE.finditer(job):
                p = REPO / m.group(2)
                if p.is_file():
                    out.append((wf, job, p))
    return out


def test_the_scan_finds_the_gate_it_was_written_for():
    """A guard whose subject vanished must fail, not pass vacuously — the failure mode that let a dead
    tripwire sit green through the fix it claimed to police."""
    gates = _gates()
    assert gates, "no workflow appears to run a tests/*.py file as a gate; the scan has lost its subject"
    assert any(p.name == "test_congeneric_fanout.py" and w.name == "step1-fanout-autoscale.yml"
               for w, _j, p in gates), "the fan-out cost gate is no longer being seen by this guard"


@pytest.mark.parametrize(
    "wf,job,path", _gates(),
    ids=[f"{w.stem}:{p.name}" for w, _j, p in _gates()])
def test_a_gate_installs_everything_its_test_file_imports(wf, job, path):
    missing = sorted(_third_party(_imports(path)) - _installed(job))
    assert not missing, (
        f"{wf.name} runs `pytest {path.relative_to(REPO)}` as a gate but its job never installs "
        f"{', '.join(missing)}. The gate will die on ModuleNotFoundError, which is NOT a verdict about the "
        f"thing it guards — on this exact step it made the launcher record `decision: cost_model_red` and "
        f"refuse to place, twice (pyyaml 2026-07-27, numpy 2026-08-01). Add the package to that job's "
        f"`pip install`. Do NOT reach for `pytest.importorskip`: the gate would then report green while "
        f"silently checking less than it claims.")


def test_the_detector_actually_detects():
    """⚠ The two incidents were both invisible to a top-of-file import scan, so the property that matters
    is that FUNCTION-LEVEL imports are seen. Reconstructed from the real file rather than a synthetic one."""
    gated = MODALITIES / "tests" / "test_congeneric_fanout.py"
    found = _imports(gated)
    assert "numpy" in found, (
        "the numpy import this guard was written for is gone from the gated file — if it was removed on "
        "purpose, delete this assertion; if the parser stopped seeing function-level imports, that is the "
        "bug, because both incidents were function-level")
    src = gated.read_text()
    assert "    import numpy as np" in src, "…and it is indented, i.e. inside a function body"
    # And the installed-set parser must actually read the workflow's line, not silently return {}.
    wf = (WORKFLOWS / "step1-fanout-autoscale.yml").read_text()
    job = next(j for j in _jobs(wf) if "pytest research/modalities/tests/test_congeneric_fanout.py" in j)
    inst = _installed(job)
    assert {"boto3", "yaml", "numpy"} <= inst, inst
    assert "numpy" not in _installed(job.replace("pytest pyyaml numpy", "pytest pyyaml")), \
        "removing numpy from the install line must make this guard go red, or it proves nothing"
