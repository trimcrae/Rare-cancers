"""Every ASO figure whose provenance is pinned must be redrawn by the chain that pins it.

⛔ WHY. `aso_figure_provenance.py` records the content hash of every artifact each ASO figure was
drawn from, and `--check` goes red when an artifact has moved since. That instrument only means
anything if the figure was actually redrawn before the hash was re-pinned. On 2026-08-17 it was not:
`scripts/regenerate_aso_chain.sh` ran three of the four drawing scripts and then ran the provenance
step, which re-pinned the sources of ALL FOUR. `aso-gap-length-tradeoff` — the paper's Figure 3,
which draws the gap-length identity across three geometries — was pinned to atlases it had not been
redrawn from. The recipe printed inside `aso-figure-provenance.json` named the same three scripts,
so a person following the file's own instructions reproduced the defect exactly.

★ WHAT THIS ASSERTS. Not that the figures are correct — a staleness instrument cannot do that (see
that module's docstring, which is explicit about it). This asserts the three lists that have to
agree actually agree: the figures with pinned provenance, the generators declared for them, and the
steps the regeneration chain runs. When they disagree, the disagreement is silent in every other
check, because every other check is downstream of the pin.
"""
from __future__ import annotations

import importlib.util
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIGDIR = os.path.join(REPO, "research", "manuscripts", "figures")
CHAIN = os.path.join(REPO, "scripts", "regenerate_aso_chain.sh")
PROVENANCE = os.path.join(FIGDIR, "aso_figure_provenance.py")


def _module():
    spec = importlib.util.spec_from_file_location("aso_figure_provenance", PROVENANCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PROV = _module()


def _chain_text():
    if not os.path.exists(CHAIN):
        pytest.fail(f"the regeneration chain is missing: {CHAIN}")
    return open(CHAIN, encoding="utf-8").read()


def _scripts_the_chain_runs():
    """Filenames the chain actually invokes, taken from `run_step` command strings only.

    ⚠ COMMAND STRINGS, NOT THE WHOLE FILE. The chain's comments name scripts too — including, at
    the time this test was written, the very script that had been omitted from the steps. Matching
    anywhere in the file would have let the comment about the bug satisfy the test about the bug.
    """
    runs = re.findall(r'^\s*run_step\s+".*?"\s+"(.*?)"', _chain_text(), flags=re.M)
    return {os.path.basename(tok) for cmd in runs for tok in cmd.split() if tok.endswith(".py")}


def test_every_pinned_figure_has_a_declared_generator():
    missing = sorted(set(PROV.FIGURES) - set(PROV.GENERATORS))
    assert not missing, (
        "these figures have provenance pinned but no generator declared, so the provenance step "
        "would re-pin a figure nothing redraws: " + ", ".join(missing))


def test_no_generator_is_declared_for_a_figure_that_is_not_pinned():
    strays = sorted(set(PROV.GENERATORS) - set(PROV.FIGURES))
    assert not strays, "GENERATORS names figures with no provenance entry: " + ", ".join(strays)


@pytest.mark.parametrize("stem", sorted(PROV.GENERATORS))
def test_the_declared_generator_exists_on_disk(stem):
    script = PROV.GENERATORS[stem]
    assert os.path.exists(os.path.join(FIGDIR, script)), (
        f"{stem} declares generator {script}, which is not in {FIGDIR}")


@pytest.mark.parametrize("stem", sorted(PROV.GENERATORS))
def test_the_regeneration_chain_runs_every_figure_generator(stem):
    script = PROV.GENERATORS[stem]
    assert script in _scripts_the_chain_runs(), (
        f"scripts/regenerate_aso_chain.sh never runs {script}, but it does run the provenance "
        f"step, which re-pins {stem}'s source hashes. That combination certifies a stale figure "
        f"as current. Add a `run_step` for it before the provenance step.")


def _step_order():
    """Script filename -> index of the `run_step` that first invokes it.

    ⚠ Ordered over the STEPS, not over the file, for the same reason `_scripts_the_chain_runs`
    reads command strings only: a comment sits at a character offset too, and comparing offsets
    inside the whole text lets prose about a step stand in for the step.
    """
    order = {}
    for i, cmd in enumerate(re.findall(r'^\s*run_step\s+".*?"\s+"(.*?)"', _chain_text(), flags=re.M)):
        for tok in cmd.split():
            if tok.endswith(".py"):
                order.setdefault(os.path.basename(tok), i)
    return order


def test_the_chain_runs_the_provenance_step_after_every_drawing_step():
    """The pin has to be the last word, or it pins a figure the next step is about to change."""
    order = _step_order()
    pin_at = order.get("aso_figure_provenance.py")
    assert pin_at is not None, "the chain no longer runs the provenance step at all"
    for stem, script in sorted(PROV.GENERATORS.items()):
        at = order.get(script)
        assert at is not None, f"the chain has no run_step invoking {script}"
        assert at < pin_at, (
            f"{script} runs after the provenance pin, so {stem}'s recorded hashes describe the "
            "state before it was redrawn")


def test_the_recipe_the_provenance_file_prints_rebuilds_every_figure():
    """The `_regenerate` line is what a human follows; it must not name a subset."""
    recipe = PROV.regenerate_recipe()
    for stem, script in sorted(PROV.GENERATORS.items()):
        assert script in recipe, (
            f"the _regenerate recipe omits {script}, so following it redraws every figure except "
            f"{stem} and then re-pins {stem} anyway")
    for post in PROV.FIGURE_POSTSTEPS:
        assert post in recipe, f"the _regenerate recipe omits the {post} step"


def test_the_committed_provenance_record_carries_the_derived_recipe():
    """A committed record written before the recipe was derived would still name three scripts."""
    import json
    out = os.path.join(FIGDIR, "aso-figure-provenance.json")
    assert os.path.exists(out), "aso-figure-provenance.json is missing — run the module"
    assert json.load(open(out, encoding="utf-8")).get("_regenerate") == PROV.regenerate_recipe(), (
        "the committed provenance record's _regenerate line is stale — regenerate it with "
        "python3 research/manuscripts/figures/aso_figure_provenance.py")
