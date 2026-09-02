#!/usr/bin/env python3
"""Which modality tests a PAPER's publication actually depends on.

⛔⛔ THE MEASUREMENT THAT FORCED THIS. `PREFLIGHT_FULL=1` is the gate between this repository and an
outside reader, and it is defined as "every gate, both suites UNSCOPED". Measured 2026-09-02 on a
green run of it:

    modalities   8,212 tests   423.6 s   72 % of the whole publication gate
    manuscripts  1,851 tests    67.6 s
    pure-logic   1,498 tests    55.1 s
    fast gates       —          ~37 s

★ AND THE 8,212 ARE ALMOST ENTIRELY ABOUT OTHER WORK. `affected_tests.select()` for a change to the
ASO journal article returns **0 of 429** modality test files. Of the 429, **39** name an artifact
that paper actually deposits — 727 tests. The other 390 are docking, ABFE, GPU-fleet, vaccine and
degrader suites, run in full to publish a six-page ASO paper. trimcrae, 2026-09-02: "10 minutes is
still too long for checking 6 pages."

★★ THE SCOPE IS DERIVED FROM THE PAPER'S OWN DEPOSIT, NEVER HAND-LISTED. `aso_archive_manifest.py`
already records every file the paper ships; this reads that manifest, keeps the paths under
`research/modalities/`, and returns every test module that names one of them. Add a file to the
deposit and its guards enter the scope on the next run, with nobody remembering to do anything —
which is the property a hand-kept list cannot have and this repository has lost twice to lists.

⛔ WHAT THIS DOES NOT NARROW, AND THE DISTINCTION IS THE WHOLE SAFETY ARGUMENT. The manuscripts
suite, the pure-logic suites, and every fast gate still run IN FULL. This scopes the ONE suite whose
subject is other routes' science. A claim in the paper is bound by a manuscripts guard; a deposited
artifact is bound by whichever modality test names it; neither is dropped.

⛔ AND IT FAILS TO FULL, ALWAYS. An unreadable manifest, a manifest naming no modality path, a
missing tests directory — each returns None, and the caller must then run everything. A scope that
cannot be derived is not a small scope.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MOD_TESTS = os.path.join(ROOT, "research", "modalities", "tests")

#: The papers this can scope, and the manifest that records what each one ships. One entry per
#: paper that HAS a deposit; a paper without one cannot be scoped and must run FULL.
MANIFESTS = {
    "PUB-ASO": os.path.join(HERE, "aso", "fusion-junction-aso-archive-manifest.json"),
}


def _paths_in(node, out):
    if isinstance(node, dict):
        for value in node.values():
            _paths_in(value, out)
    elif isinstance(node, list):
        for value in node:
            _paths_in(value, out)
    elif isinstance(node, str) and "/" in node and node.endswith(
            (".json", ".csv", ".tsv", ".py", ".md", ".txt", ".fa", ".bed")):
        out.add(node)


def deposited_modality_files(paper):
    """Basenames of every `research/modalities/` file the paper's manifest records, or None."""
    manifest = MANIFESTS.get(paper)
    if not manifest or not os.path.exists(manifest):
        return None
    try:
        with open(manifest, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    paths = set()
    _paths_in(doc, paths)
    modality = {p for p in paths if p.startswith("research/modalities/")}
    if not modality:
        return None
    return {os.path.basename(p) for p in modality}


def scoped_tests(paper):
    """Repo-relative modality test modules guarding this paper's deposit, or None to mean FULL.

    ⛔ A SUBSTRING MATCH ON THE BASENAME, DELIBERATELY WIDE. A test that merely MENTIONS a deposited
    artifact is included; the cost of a false include is one extra test file, and the cost of a
    false exclude is an unguarded artifact in a published deposit. The asymmetry decides the rule.
    """
    names = deposited_modality_files(paper)
    if not names or not os.path.isdir(MOD_TESTS):
        return None
    out = []
    for entry in sorted(os.listdir(MOD_TESTS)):
        if not (entry.startswith("test_") and entry.endswith(".py")):
            continue
        try:
            with open(os.path.join(MOD_TESTS, entry), encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except OSError:
            return None          # cannot read one -> cannot claim a scope
        if any(name in src for name in names):
            out.append(os.path.join("research", "modalities", "tests", entry))
    return out or None           # an empty scope is not a scope; run FULL


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", default="PUB-ASO")
    ap.add_argument("--count", action="store_true", help="print the counts rather than the paths")
    a = ap.parse_args(argv)
    sel = scoped_tests(a.paper)
    if sel is None:
        print("FULL", file=sys.stdout)
        return 0
    if a.count:
        total = len([f for f in os.listdir(MOD_TESTS)
                     if f.startswith("test_") and f.endswith(".py")])
        print("%d of %d modality test module(s) guard %s's deposit" % (len(sel), total, a.paper))
        return 0
    print("\n".join(sel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
