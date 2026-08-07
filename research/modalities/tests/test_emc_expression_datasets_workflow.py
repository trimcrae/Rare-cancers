"""The part-B guard in `emc-expression-datasets.yml` must be resolved ONCE, not restated per step.

⛔ WHY THIS TEST EXISTS — measured 2026-08-07, run 31199787306.
Part B's step and its summary were each gated on a hand-written exclusion list:

    if: inputs.mode != 'gse-series' && inputs.mode != 'aso-junction' && inputs.mode != 'panels'

so every new mode had to be added to both, and the fourth one (`hypoxia-confounds`) was not. A
dispatch of that mode started the 75-minute PART B step — the one that rewrites the 7 MB committed
grading artifact this workflow's own header says a new mode must not be able to perturb. It was
caught at step 5 of 23 and cancelled. The mode list was correct in three places and stale in two.

That is CLAUDE.md §1 exactly: a restated list falls behind, and it falls behind silently, because
the stale copy is still valid YAML and still a valid boolean. The guard now lives in ONE step whose
output every consumer reads, and this test fails the build if any step goes back to restating it.

⚠ THE NEGATIVE FORM IS NOT THE BUG AND MUST SURVIVE. A dispatch that sends no inputs at all has to
fall through to part B, so the predicate is still "mode is not one of the named non-part-b modes",
never `mode == 'part-b'`. The bug was the DUPLICATION, not the polarity — so this test also asserts
the polarity is still negative and that every declared mode is accounted for by the one guard.

Stdlib + PyYAML if available; falls back to a text scan so it can never be skipped into silence.
"""

import os
import re

import pytest

# tests/ -> modalities/ -> research/ -> repo root. Four levels, and the assertion below is what
# stops a miscount from turning every check in this file into a fabricated pass.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
WF = os.path.join(REPO, ".github", "workflows", "emc-expression-datasets.yml")
assert os.path.isdir(os.path.join(REPO, ".github")), (
    f"REPO resolved to {REPO}, which has no .github/ — the path arithmetic is wrong and every "
    f"test in this file would be testing a missing file")


@pytest.fixture(scope="module")
def text():
    if not os.path.exists(WF):
        pytest.fail(f"{WF} is missing — the workflow this test guards does not exist")
    with open(WF, "r", encoding="utf-8") as fh:
        return fh.read()


def test_no_step_restates_the_mode_exclusion_list():
    """The exact shape that cost run 31199787306: two or more `inputs.mode != ...` in one `if:`."""
    with open(WF, "r", encoding="utf-8") as fh:
        offenders = [(n, ln.strip()) for n, ln in enumerate(fh, 1)
                     if ln.lstrip().startswith("if:") and ln.count("inputs.mode !=") >= 2]
    assert not offenders, (
        "a step gates on a restated mode-exclusion list; use `steps.guard.outputs.part_b` "
        "instead — a restated list already ran part B under the wrong mode:\n  " +
        "\n  ".join(f"line {n}: {ln}" for n, ln in offenders))


def test_the_guard_step_exists_and_is_the_only_place_the_excluded_modes_are_listed(text):
    assert "id: guard" in text, "the resolved-once guard step is gone"
    # the case arm is the single home of the exclusion list
    arms = re.findall(r"^\s*([a-z|-]+)\)\s*PART_B=false", text, re.M)
    assert len(arms) == 1, f"expected exactly one `PART_B=false` case arm, found {arms}"
    excluded = set(arms[0].split("|"))
    assert excluded, "the exclusion list is empty — every mode would run part B"
    # ...and it must cover every declared mode except part-b itself
    m = re.search(r"options:\s*\[([^\]]+)\]", text)
    assert m, "the mode `options:` list could not be read"
    declared = {o.strip().strip('"\'') for o in m.group(1).split(",")}
    missing = declared - excluded - {"part-b"}
    assert not missing, (
        f"mode(s) {sorted(missing)} are dispatchable but not in the part-B exclusion arm, so "
        f"dispatching them would ALSO run part B — which is the run-31199787306 defect returning")


def test_every_consumer_reads_the_resolved_guard_rather_than_recomputing_it(text):
    n = text.count("steps.guard.outputs.part_b")
    assert n >= 3, (
        f"only {n} step(s) read the resolved guard; part B's step, its reproduce check and its "
        f"summary must all read it, or one of them will drift again")


def _if_lines():
    """Only the `if:` CONDITIONS. ⚠ Scanning whole-file text is what this test got wrong first:
    the comment explaining why the guard is not the positive form CONTAINS the positive form, so a
    whole-file scan failed on the sentence that states the rule. Same failure shape as the
    `_is_substitution_lhs` exception in `lint_claims.py` — a rule must not fire on its own name."""
    with open(WF, "r", encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.lstrip().startswith("if:")]


def test_the_guard_is_still_the_negative_form_so_an_empty_dispatch_falls_through_to_part_b(text):
    """`== 'part-b'` would turn a no-inputs dispatch into a no-op that reports success."""
    assert re.search(r"\*\)\s*PART_B=true", text), (
        "the default case arm is gone; an empty `inputs.mode` must fall through to part B")
    offenders = [ln for ln in _if_lines() if "inputs.mode == 'part-b'" in ln]
    assert not offenders, (
        "the guard was flipped to the positive form — a dispatch sending no inputs would then "
        f"silently skip part B and report success: {offenders}")


def _publish_arm(mode):
    """The PATHS block of one arm of the publish step's `case`-style if/elif chain.

    ⚠ Anchored on the `MSG=`/`PATHS=` assignment, not on the `elif` token. The first attempt split
    on `elif [ ... = "hypoxia-confounds" ]` and landed on the UNIT-TEST step's identical `elif`
    a hundred lines earlier, so the "block" it checked was most of the file and the assertion was
    meaningless. A test scoped to the wrong region passes or fails for the wrong reason."""
    with open(WF, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    start = None
    for i, ln in enumerate(lines):
        if f'= "{mode}" ]; then' in ln and "MSG=" in "\n".join(lines[i + 1:i + 3]):
            start = i
            break
    assert start is not None, f"no publish arm found for mode {mode!r}"
    out = []
    for ln in lines[start + 1:]:
        if re.match(r"\s*(elif|else|fi)\b", ln):
            break
        out.append(ln)
    return "\n".join(out)


def test_the_hypoxia_confounds_mode_publishes_its_own_artifacts_and_nothing_part_b_owns():
    """A new mode must not be able to perturb — or publish over — the committed grading artifact."""
    paths = _publish_arm("hypoxia-confounds")
    assert "emc-hypoxia-confounds.json" in paths, paths
    assert "emc-atr-vulnerability" not in paths, (
        "the hypoxia-confounds mode would publish part B's grading artifact")
    assert "emc-expression-panels" not in paths, (
        "the hypoxia-confounds mode would publish the panels artifacts it only READS")
