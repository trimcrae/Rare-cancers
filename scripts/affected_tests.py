#!/usr/bin/env python3
"""Select the tests a change can actually affect, or say FULL and mean it.

⛔ WHY: PREFLIGHT WAS 15 MINUTES AND 87 % OF IT WAS ONE STEP (measured 2026-08-12). The modalities
suite ran 745.9 s of a ~15-minute gate — ~7,000 tests, single-threaded, on every commit including
one that edited only prose. The doc, systems-model and medical-integrity gates that have ACTUALLY
caught things in this repository cost about a minute between them.

⚠ AND THE EXPENSIVE COPY IS THE WEAKER ONE. This sandbox has no numpy, rdkit, boto3, scipy, pymbar
or netCDF4, so 48 of those tests fail as missing imports and five modules do not import at all.
`tests.yml` runs `on: push` with the real dependencies installed, so the version of this suite that
means something runs in CI on every push regardless. Paying twelve local minutes for a degraded
rerun of a check that is about to run properly is poor value, and it is why this selector exists.

HOW IT CHOOSES. Static import graph, pure stdlib, no execution:

  1. Every `research/modalities/*.py` is parsed for the repo modules it imports, giving a
     module -> module edge set; the closure of that is which modules a change can reach.
  2. Every `tests/test_*.py` is parsed the same way, giving test -> modules.
  3. A changed module selects every test whose reachable-module set contains it.
  4. A changed ARTIFACT (`.json`) selects every test whose source text names that file, which is
     how the `committed_artifact` tests bind to the files they assert against.

⛔ AND EVERY UNCERTAINTY RESOLVES TO FULL, WHICH IS THE ONLY PROPERTY THAT MAKES THIS SAFE. A test
selector that under-selects is precisely the failure this repository keeps paying for — a check that
reports while measuring nothing (CLAUDE.md §4). So: a changed `conftest.py`, a changed test HELPER
that is not itself a test, a change to pytest configuration, a change to THIS FILE or to
`preflight.sh`, or any git command that does not answer, all return FULL rather than a subset. The
selector is allowed to be wrong in the direction of running too much and never in the other.

⚠ WHAT THIS IS NOT: a replacement for the full suite. It is the pre-commit filter. Before a
publication, a release, or anything outward-facing, run `PREFLIGHT_FULL=1 ./scripts/preflight.sh`.

Usage:
    python3 scripts/affected_tests.py            # prints test paths, or the single token FULL
    python3 scripts/affected_tests.py --explain  # and why, to stderr
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "research", "modalities")
TESTS = os.path.join(MOD, "tests")

#: A change to any of these cannot be scoped, so it takes the whole suite. Paths are repo-relative
#: prefixes or exact names; the test is "startswith" for directories and "endswith" for basenames.
ALWAYS_FULL_BASENAMES = ("conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini")
ALWAYS_FULL_PATHS = ("scripts/affected_tests.py", "scripts/preflight.sh")


def _git(*args):
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001 — an unanswered git is an uncertainty, and uncertainty is FULL
        return None
    return r.stdout if r.returncode == 0 else None


def changed_files():
    """Everything this commit would carry that the default branch does not, plus the dirty tree.

    Returns None if git cannot answer, which the caller treats as FULL.
    """
    out = set()
    dirty = _git("diff", "--name-only", "HEAD")
    staged = _git("diff", "--name-only", "--cached")
    untracked = _git("ls-files", "--others", "--exclude-standard")
    if dirty is None or staged is None or untracked is None:
        return None
    for blob in (dirty, staged, untracked):
        out.update(x.strip() for x in blob.splitlines() if x.strip())

    # committed-but-unmerged work on this branch, so a preflight run after several commits still
    # covers everything the branch introduces rather than only the last commit
    base = _git("merge-base", "HEAD", "origin/main")
    if base:
        blob = _git("diff", "--name-only", f"{base.strip()}...HEAD")
        if blob is None:
            return None
        out.update(x.strip() for x in blob.splitlines() if x.strip())
    return out


def _module_imports(path, known):
    """Repo modules imported by `path`, by static parse. Never imports anything itself."""
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception:  # noqa: BLE001 — an unparseable file is an uncertainty; caller goes FULL
        return None
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return {n for n in names if n in known}


def build_graph():
    """(module -> modules it imports, test -> modules it imports). None on any parse failure."""
    known = {f[:-3] for f in os.listdir(MOD) if f.endswith(".py")}
    mod_edges, test_edges = {}, {}
    for name in sorted(known):
        got = _module_imports(os.path.join(MOD, f"{name}.py"), known)
        if got is None:
            return None, None
        mod_edges[name] = got
    for f in sorted(os.listdir(TESTS)):
        if not (f.startswith("test_") and f.endswith(".py")):
            continue
        got = _module_imports(os.path.join(TESTS, f), known)
        if got is None:
            return None, None
        test_edges[f] = got
    return mod_edges, test_edges


def _reachable(seed, mod_edges):
    """Transitive closure, so a change to a leaf module still selects tests that reach it."""
    seen, stack = set(seed), list(seed)
    while stack:
        cur = stack.pop()
        for nxt in mod_edges.get(cur, ()):  # noqa: SIM118
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def select(explain=False):
    def say(msg):
        if explain:
            print(f"  {msg}", file=sys.stderr)

    files = changed_files()
    if files is None:
        say("git did not answer — FULL")
        return None
    if not files:
        say("no changed files — nothing to run")
        return []

    for f in sorted(files):
        if os.path.basename(f) in ALWAYS_FULL_BASENAMES or f in ALWAYS_FULL_PATHS:
            say(f"{f} cannot be scoped — FULL")
            return None
        # a non-test .py inside tests/ is a shared helper; its blast radius is the whole suite
        if f.startswith("research/modalities/tests/") and f.endswith(".py") \
                and not os.path.basename(f).startswith("test_"):
            say(f"{f} is a test helper, not a test — FULL")
            return None

    mod_edges, test_edges = build_graph()
    if mod_edges is None:
        say("a source file did not parse — FULL")
        return None

    reach = {t: _reachable(m, mod_edges) for t, m in test_edges.items()}
    chosen, unmapped = set(), []

    for f in sorted(files):
        base = os.path.basename(f)
        if f.startswith("research/modalities/tests/") and base.startswith("test_"):
            if base in test_edges:
                chosen.add(base)
                say(f"{f} is itself a test")
            continue
        if f.startswith("research/modalities/") and f.endswith(".py"):
            name = base[:-3]
            hits = {t for t, r in reach.items() if name in r}
            if hits:
                chosen |= hits
                say(f"{f} -> {len(hits)} test module(s)")
            else:
                unmapped.append(f)
                say(f"{f} -> no test imports it")
            continue
        if f.endswith((".json", ".jsonl")):
            # artifacts bind to tests by NAME, which is how committed_artifact tests find them
            hits = set()
            for t in test_edges:
                try:
                    if base in open(os.path.join(TESTS, t), encoding="utf-8").read():
                        hits.add(t)
                except Exception:  # noqa: BLE001
                    return None
            if hits:
                chosen |= hits
                say(f"{f} -> {len(hits)} test module(s) name it")
            continue
        # ⛔ A MANUSCRIPT IS AN INPUT TO THE MODALITIES SUITE, AND THIS SELECTOR USED TO SAY IT WAS
        # NOT (found 2026-08-16, round-7 Phase 3.4). `research/manuscripts/**/*.md` fell through to
        # the "outside the modalities test domain" line below, so a MANUSCRIPT-ONLY commit selected
        # ZERO modality tests -- and `test_aso_submission_numbers.py`, the 35-assertion guard whose
        # entire job is to pin the manuscript's numbers to the artifacts, lives in that suite. The
        # gate that exists to catch a number drifting out of the paper was the one guaranteed not to
        # run when only the paper changed.
        # ⚠ THIS IS THE SECOND INSTANCE OF THE BUG COMMIT 233783c1a FIXED. That commit closed the
        # dead-selector case (a selector that answered "nothing to run" and was believed); this is
        # the same failure reached by a different route -- a real answer, computed over a file class
        # the selector declined to map. Bound BY NAME, exactly as the .json branch above binds
        # artifacts, because that is already how these tests find what they read.
        if f.startswith("research/manuscripts/") and f.endswith(".md"):
            hits = set()
            for t in test_edges:
                try:
                    if base in open(os.path.join(TESTS, t), encoding="utf-8").read():
                        hits.add(t)
                except Exception:  # noqa: BLE001
                    return None
            if hits:
                chosen |= hits
                say(f"{f} -> {len(hits)} test module(s) name it")
            else:
                # ⚠ NOT "ignored". A submission-bound document that no test names is UNGUARDED, and
                # saying so is the point -- a silent skip here is what let the SI ship outside every
                # instrument.
                say(f"{f} -> NO test names it; this document is unguarded")
            continue
        say(f"{f} — outside the modalities test domain, ignored")

    if unmapped and explain:
        print(f"  ⚠ {len(unmapped)} changed module(s) are imported by no test — they are "
              f"UNCOVERED, not safe: {unmapped[:5]}", file=sys.stderr)
    return sorted(f"research/modalities/tests/{t}" for t in chosen)


def main():
    explain = "--explain" in sys.argv
    sel = select(explain=explain)
    if sel is None:
        print("FULL")
    else:
        for p in sel:
            print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
