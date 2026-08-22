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
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "research", "modalities")
TESTS = os.path.join(MOD, "tests")
#: The other suite. Nothing here is ever SELECTED -- preflight runs this whole directory unscoped --
#: but a document guarded from it is not unguarded, and the verdict below has to know that.
MANUSCRIPT_TESTS = os.path.join(ROOT, "research", "manuscripts", "tests")


def _named_by_manuscript_tests(base):
    """How many modules in the manuscripts suite name `base`. 0 if the directory is absent."""
    if not os.path.isdir(MANUSCRIPT_TESTS):
        return 0
    n = 0
    for t in sorted(os.listdir(MANUSCRIPT_TESTS)):
        if not (t.startswith("test_") and t.endswith(".py")):
            continue
        try:
            if base in open(os.path.join(MANUSCRIPT_TESTS, t), encoding="utf-8").read():
                n += 1
        except OSError:
            continue
    return n

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


#: Where the validated content of the gatekeeping files is recorded. See `_unvalidated_gatekeepers`.
VALIDATION_RECORD = os.path.join(ROOT, "scripts", "selector-validation.json")


def _unvalidated_gatekeepers():
    """Which of `ALWAYS_FULL_PATHS` differ from the content a full run validated.

    Returns a (possibly empty) set, or None if the record cannot be read — which the caller treats
    as FULL, because an unreadable record is an unanswered question and uncertainty is FULL.
    """
    try:
        rec = json.load(open(VALIDATION_RECORD, encoding="utf-8")).get("validated") or {}
    except Exception:  # noqa: BLE001 — unreadable or absent record is an uncertainty
        return None
    out = set()
    for rel in ALWAYS_FULL_PATHS:
        want = rec.get(rel)
        path = os.path.join(ROOT, rel)
        if want is None or not os.path.exists(path):
            return None
        if hashlib.sha256(open(path, "rb").read()).hexdigest() != want:
            out.add(rel)
    return out


def uncommitted_files():
    """Only what is not yet committed: the dirty tree, the index and untracked files.

    ⛔⛔ THIS EXISTS BECAUSE `ALWAYS_FULL` WAS STICKY FOR THE LIFE OF A BRANCH (2026-08-22, trimcrae:
    *"if it's looking at a ton of stuff not related to ASO, we should either not be running it at all
    or only running a subset of it"*). `changed_files()` deliberately spans the whole branch, so once
    ANY commit on the branch touched `scripts/affected_tests.py` or `scripts/preflight.sh`, every
    later run resolved to FULL no matter what it was changing. Measured that morning: a prose-only
    edit to one manuscript ran all 398 modality modules — 7,800 tests over docking, ABFE and GPU
    fleet management, none of which a manuscript can reach — for 19m38s, and passed every one.

    ⭐ THE SAFETY PROPERTY IS UNCHANGED, because it was never about the branch. The rule is "if the
    selector is untrustworthy, do not trust it", and a selector change is ALWAYS dirty at the moment
    of its own commit, so it is always FULL-gated there. Once that commit has passed, the selector on
    disk is the one that FULL run validated. Keeping it a permanent tripwire re-gates a question that
    was already answered, and the cost is the scoped fast path for the rest of the branch.

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
    return out


def changed_files():
    """Everything this commit would carry that the default branch does not, plus the dirty tree.

    Returns None if git cannot answer, which the caller treats as FULL.
    """
    out = uncommitted_files()
    if out is None:
        return None
    out = set(out)

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

    # ⛔⛔ THE SELECTOR AND PREFLIGHT ARE GATED ON CONTENT, NOT ON HOW THE CONTENT ARRIVED
    # (2026-08-22, round 14 seat 4, reproduced exploit). The previous rule asked whether the file
    # was UNCOMMITTED, on the premise that a selector edit is always dirty at the moment of its own
    # commit and therefore FULL-gated there. `git cherry-pick` falsifies that premise outright: it
    # auto-commits, so the change lands with a zero-width dirty window and the new selector
    # immediately scopes itself. Measured by that seat: after a cherry-pick the new selector picks 0
    # modality modules while the old selector on the identical git state says FULL. merge, revert
    # and rebase behave the same way, and CLAUDE.md §7 mandates them.
    # ⭐ So the question is whether THIS CONTENT has passed a full run, which scripts/
    # selector-validation.json records as a hash. A file that matches its record is one a
    # PREFLIGHT_FULL run has already validated, however it got here; anything else is FULL.
    stale = _unvalidated_gatekeepers()
    if stale is None:
        say("the selector validation record could not be read — FULL")
        return None
    for f in sorted(stale):
        say(f"{f} does not match its validated hash — FULL")
        return None
    for f in sorted(files):
        if os.path.basename(f) in ALWAYS_FULL_BASENAMES:
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
                #
                # ⛔⛔ BUT "UNGUARDED" IS A CLAIM, AND THIS SAID IT ABOUT A GUARDED DOCUMENT
                # (2026-08-22, round-13 seat 4). This selector only ever SELECTS from the modalities
                # suite, so it only ever LOOKED there -- and preflight runs
                # `research/manuscripts/tests` wholesale, unscoped, on every commit. So a document
                # guarded from that directory was reported as guarded by nothing at all. The journal
                # article was in exactly that state the moment its numbers guard was written.
                # An instrument that reports a false absence is the failure this repository keeps
                # paying for: an absent reading is not a reading of absence. The selection contract
                # is unchanged -- only modalities modules are ever returned -- but the verdict now
                # looks where the other guards actually live before calling a document unguarded.
                elsewhere = _named_by_manuscript_tests(base)
                if elsewhere:
                    say(f"{f} -> no modalities test names it; guarded by {elsewhere} "
                        "manuscripts test module(s), which preflight runs unscoped")
                else:
                    say(f"{f} -> NO test names it, in either suite; this document is unguarded")
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
