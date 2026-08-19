#!/usr/bin/env python3
"""No guard in the deposit suite may decline to run because an input or a parser is absent.

⛔⛔ WHY THIS EXISTS — THE SAME DEFECT, TWICE, IN TWO DIFFERENT DISGUISES, ON THE SAME DAY.

  2026-08-19  `.github/workflows/tests.yml` had never installed `pypdf` or `pymupdf`. Guards in the
              deposit suite imported them, took `pytest.skip("… is not installed in this sandbox")`
              on every CI run, and reported GREEN for checks that had never once executed on the
              machine that gates a commit. Among them: whether the deposit PDF's pages are nearly
              empty, whether its justification has degraded, and whether the three condemned
              sequences reach the built document at all.
  2026-08-19  An audit of the whole suite for the same class found the artifact-side twin:
              ~40 guards wrapped in `if not os.path.exists(<a COMMITTED artifact>): pytest.skip(…)`.
              Deleting the generated tables file, the canonical CSV, the figures, the coverage
              ladder or the manuscript itself made every assertion that depends on it evaporate,
              and the run still reported PASS. A guard that disappears with its input is
              indistinguishable from one that never ran.

★ THE PROPERTY, NOT THE INSTANCE. Both were fixed one call site at a time, and one call site at a
time is exactly how they came back. This asserts the SHAPE: in the deposit guard suite, a check may
fail and it may pass, but it may not quietly not-happen.

⚠ THE INSTALLED SET IS READ FROM THE WORKFLOW, NEVER TYPED HERE. If it were typed, this file would
be a second home for the pip line and would agree with itself while the runner installed something
else — the same one-fact-one-place failure it exists to catch.
"""
from __future__ import annotations

import ast
import glob
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "tests.yml")

#: ⭐ THE SCOPE IS A PATTERN, NOT A LIST, so a guard added tomorrow is covered without anybody
#: remembering to enrol it. The manuscript guards plus the ASO modality guards are the deposit's
#: own suite; the GPU/infra lanes under research/modalities have their own environments and their
#: own reasons to decline, and are deliberately out of scope.
SCOPE_PATTERNS = (
    "research/manuscripts/tests/test_*.py",
    "research/modalities/tests/test_aso_*.py",
    "research/modalities/tests/test_junction_aso_*.py",
    "research/modalities/tests/test_offtarget_chance_baseline.py",
)

#: distribution on the pip line -> the top-level module names importing it actually provides.
#: Needed because `pip install pyyaml` gives you `import yaml`. Deliberately small and explicit: a
#: distribution that appears on the pip line and NOT here fails `test_every_installed_distribution_
#: is_mapped_to_its_import_name`, so adding a package forces a decision instead of silently
#: widening what this file will tolerate.
DISTRIBUTION_PROVIDES = {
    "pytest": ("pytest", "_pytest", "pluggy", "iniconfig", "packaging"),
    "numpy": ("numpy",),
    "scipy": ("scipy",),
    "pymbar": ("pymbar",),
    "rdkit": ("rdkit", "PIL"),            # the rdkit wheel pulls Pillow
    "pyyaml": ("yaml",),
    "boto3": ("boto3", "botocore", "s3transfer", "jmespath", "dateutil", "urllib3"),
    "jsonschema": ("jsonschema", "attr", "attrs", "referencing", "rpds"),
    "biopython": ("Bio", "BioSQL"),
    "pdfminer.six": ("pdfminer", "cryptography", "cffi", "charset_normalizer"),
    "pypdf": ("pypdf",),
    # ⭐ ADDED 2026-08-19 WITH THE WORKFLOW LINE THAT INSTALLS IT, WHICH IS THE POINT OF THIS TABLE.
    # matplotlib was added to CI so the figure-RENDER guard could stop being a permanent skip, and
    # this file refused the change until the mapping was declared -- a distribution CI installs
    # whose import name nobody has written down still reads as "not available" to every guard that
    # imports it, which is the silent-skip failure in a new costume. The wheel brings its own
    # dependency set; naming them keeps a guard that imports `cycler` or `PIL` from reading as
    # uninstallable.
    "matplotlib": ("matplotlib", "pylab", "cycler", "kiwisolver", "pyparsing", "PIL",
                   "dateutil", "packaging", "numpy"),
}

#: A site may reach a module CI does not install only if it says so, at the site, in these words.
#: The marker is what turns "this cannot run in CI" from an accident into a recorded decision.
NOT_IN_CI_MARKER = "NOT IN CI"
#: …and the same idea for a skip keyed on anything else: a guard may decline to run, but somebody
#: has to have decided that it may, in writing, next to the skip.
DELIBERATE_SKIP_MARKER = "SKIP IS DELIBERATE"
MARKER_WINDOW_LINES = 12

_PIP_LINE = re.compile(r"^\s*-\s*run:\s*pip install\s+(.+?)\s*$", re.M)


def _scope_files():
    out = []
    for pattern in SCOPE_PATTERNS:
        out += glob.glob(os.path.join(REPO, pattern))
    out = sorted(set(out))
    #: a scope that has silently emptied is the same failure as a guard that silently stopped
    assert len(out) >= 40, (
        f"only {len(out)} guard file(s) matched {SCOPE_PATTERNS}; the deposit suite is far larger "
        "than that, so these patterns have stopped matching and this whole file is asserting "
        "nothing. Re-derive the scope rather than lowering the floor.")
    return out


def _installed_distributions():
    if not os.path.exists(WORKFLOW):
        pytest.fail(f"the test workflow is missing at {WORKFLOW}; it is committed, and it is the "
                    "only record of what the machine that gates a commit installs.")
    found = _PIP_LINE.findall(open(WORKFLOW, encoding="utf-8").read())
    assert found, (
        "no `- run: pip install …` line was found in .github/workflows/tests.yml. Either the "
        "workflow stopped installing anything — in which case every guard needing a package is "
        "silently skipping — or the install moved to a form this cannot read, and the rules below "
        "would pass by finding nothing. Re-anchor rather than deleting.")
    dists = []
    for line in found:
        dists += [tok for tok in line.split() if not tok.startswith("-")]
    return sorted(set(dists))


def _importable_in_ci():
    mods = set()
    for dist in _installed_distributions():
        mods.update(DISTRIBUTION_PROVIDES.get(dist, ()))
    return mods


def _marked_not_in_ci(lines, lineno):
    lo = max(0, lineno - 1 - MARKER_WINDOW_LINES)
    hi = min(len(lines), lineno + MARKER_WINDOW_LINES)
    return any(NOT_IN_CI_MARKER in ln for ln in lines[lo:hi])


def test_every_installed_distribution_is_mapped_to_its_import_name():
    """The mapping above must cover the pip line, or a rule below silently stops covering a package."""
    unmapped = [d for d in _installed_distributions() if d not in DISTRIBUTION_PROVIDES]
    assert not unmapped, (
        f"the workflow installs {unmapped} and DISTRIBUTION_PROVIDES does not say what module name "
        "each gives you. Until it does, a guard importing that module reads as 'not installed in "
        "CI' here and this file will refuse it — add the mapping deliberately.")


def test_no_deposit_guard_depends_on_a_module_ci_does_not_install():
    """⛔ THE pypdf/pymupdf CLASS. An importorskip on an absent package is a permanent skip."""
    have, offenders = _importable_in_ci(), []
    import sys  # noqa: PLC0415
    stdlib = set(sys.stdlib_module_names)
    repo_modules = {os.path.splitext(os.path.basename(p))[0]
                    for p in glob.glob(os.path.join(REPO, "research", "*", "*.py"))
                    + glob.glob(os.path.join(REPO, "research", "*", "*", "*.py"))}
    for path in _scope_files():
        src = open(path, encoding="utf-8").read()
        lines = src.splitlines()
        tree = ast.parse(src)
        reached = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "importorskip" and node.args \
                    and isinstance(node.args[0], ast.Constant):
                reached.append((node.args[0].value, node.lineno))
            if isinstance(node, ast.Try) and any(
                    (isinstance(h.type, ast.Name) and h.type.id in ("ImportError",
                                                                    "ModuleNotFoundError"))
                    or (isinstance(h.type, ast.Tuple)
                        and any(getattr(e, "id", None) in ("ImportError", "ModuleNotFoundError")
                                for e in h.type.elts))
                    for h in node.handlers):
                swallows = any(
                    isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                    and c.func.attr == "skip"
                    for h in node.handlers for c in ast.walk(h))
                if not swallows:
                    continue                      # an ImportError that FAILS is the desired shape
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Import):
                        reached += [(a.name, sub.lineno) for a in sub.names]
                    elif isinstance(sub, ast.ImportFrom) and sub.module and not sub.level:
                        reached.append((sub.module, sub.lineno))
        for module, lineno in reached:
            top = module.split(".")[0]
            if top in stdlib or top in have or top in repo_modules:
                continue
            if _marked_not_in_ci(lines, lineno):
                continue
            offenders.append(f"{os.path.relpath(path, REPO)}:{lineno} -> {module}")
    assert not offenders, (
        "these guards decline to run when a module is absent, and the machine that gates a commit "
        "never installs it — so they have never run there and report green for a check nobody "
        "performed:\n  " + "\n  ".join(offenders)
        + f"\n\nEither add the distribution to the pip line in .github/workflows/tests.yml, or "
          f"re-express the check against a module CI does install, or — if the check genuinely "
          f"cannot run there — say so at the site with the words {NOT_IN_CI_MARKER!r} so the gap "
          "is a recorded decision instead of a green tick.")


def test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took():
    """⛔ THE EXISTENCE RULE BELOW DOES NOT SEE A TRUTHINESS ONE, AND FOUR HID FROM IT.

    `if not m["n_junctions"]: pytest.skip("no matched junctions in this checkout")` names a
    checkout state, keys on an artifact's CONTENT, and tests no path — so an existence-shaped rule
    walks straight past it while the guard still evaporates. Rather than enumerate every shape a
    condition can take, this requires the OUTCOME to be recorded: a skip that survives in this
    suite carries, at the site, either {NOT_IN_CI_MARKER!r} (the package is genuinely absent from
    the runner) or {DELIBERATE_SKIP_MARKER!r} (the condition is a real property of the data, and
    somebody decided the guard may decline). Anything else is a guard quietly not running.
    """
    offenders = []
    for path in _scope_files():
        src = open(path, encoding="utf-8").read()
        lines = src.splitlines()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "skip" \
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest":
                lo = max(0, node.lineno - 1 - MARKER_WINDOW_LINES)
                hi = min(len(lines), node.lineno + MARKER_WINDOW_LINES)
                window = lines[lo:hi]
                if any(NOT_IN_CI_MARKER in ln or DELIBERATE_SKIP_MARKER in ln for ln in window):
                    continue
                offenders.append(f"{os.path.relpath(path, REPO)}:{node.lineno}")
    assert not offenders, (
        "these guards can decline to run and nothing at the site records that anyone decided they "
        "may:\n  " + "\n  ".join(offenders)
        + f"\n\nEvery artifact this suite reads is committed and every module it needs is on the "
          f"pip line, so a skip is almost always a check evaporating with its input. Turn it into "
          f"a pytest.fail or an assert; if it genuinely must stay, write {NOT_IN_CI_MARKER!r} or "
          f"{DELIBERATE_SKIP_MARKER!r} beside it with the reason.")


def test_no_deposit_guard_skips_itself_because_an_input_is_missing():
    """⛔ THE ARTIFACT-SIDE TWIN. A guard wrapped in `if not exists(...): skip` vanishes with its input.

    Every artifact these guards read is committed, so an absence is a broken tree — a finding, and
    the loudest moment there is. `pytest.fail` is the right verb; so is a plain `assert`.
    """
    offenders = []
    for path in _scope_files():
        tree = ast.parse(open(path, encoding="utf-8").read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            tests_existence = any(
                isinstance(x, ast.Attribute)
                and x.attr in ("exists", "isdir", "isfile", "is_file", "is_dir")
                for x in ast.walk(node.test))
            if not tests_existence:
                continue
            if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                   and c.func.attr == "skip"
                   and isinstance(c.func.value, ast.Name) and c.func.value.id == "pytest"
                   for c in ast.walk(node)):
                offenders.append(f"{os.path.relpath(path, REPO)}:{node.lineno}")
    assert not offenders, (
        "these guards skip themselves when a file is missing, and every file the deposit suite "
        "reads is committed — so the skip can only ever fire on a broken tree, which is exactly "
        "when the guard has to speak:\n  " + "\n  ".join(offenders)
        + "\n\nUse pytest.fail (or a plain assert) and name the artifact.")
