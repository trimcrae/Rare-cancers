#!/usr/bin/env python3
"""Does the census's word "covered" survive being TESTED? Ablation, not inspection.

⛔⛔ WHY THIS EXISTS — THE ROUND-16 DIAGNOSIS, WHICH IS ONE LEVEL ABOVE ROUND 15'S.

`claim_coverage.py` was written because fifteen review rounds would not converge: every blocker was
a surface with zero instruments, so the blocker rate tracked how many new LENSES a round introduced,
not how many defects the paper held. The fix was to stop sampling surfaces and enumerate them.

Round 16 pointed three seats at the enumerator and found the SAME defect one level up:

  seats 1/4/5  the census credited a guard's regexes to documents that guard never opens
               — 22 of 27 "covered" cover-letter sentences were false positives
  seat 5       `MAX_MATCH_SHARE = 0.10` on a 9-sentence document: the smallest representable
               non-zero share is 1/9 = 0.111 > 0.10, so EVERY pattern was discarded before the
               coverage loop ran. `journal-tables: 0 of 9` was integer arithmetic, not a reading
  seat 5       "matches few sentences" was implemented where "distinguishes this sentence" was
               meant, so bold spans, code spans and an ISO date all counted as coverage

★★ THE STRUCTURAL FINDING, AND IT IS WHY ITERATION ALONE CANNOT CONVERGE. Every fix ships a NEW
INSTRUMENT, and every new instrument is a new claim asserted in prose and measured nowhere. So each
round's fix REFILLS the pool the next round drains. Reviewing instruments by READING them can never
catch up with writing them — which is the same shape as CLAUDE.md's "a property asserted in prose
about a value passed by a caller is not a property; it is a hope."

★ WHAT CHANGES THE SHAPE: the census makes a per-sentence claim that is FALSIFIABLE IN ONE
OPERATION. "Sentence S is covered by witness W" predicts that if S changed, W would go red. So
change it and look. This module does that, and it is different in kind from every previous fix:

  · it adds NO new hand-written constant, so there is no new number to get wrong;
  · it derives its expectation from the census's OWN output, so it cannot drift from what the
    census claims;
  · it catches document-blindness, non-selective patterns AND the threshold bug with ONE
    mechanism, because all three make the census credit coverage that is not there.

TWO ERROR DIRECTIONS, BOTH FATAL, AND THE SECOND IS THE ONE INSPECTION NEVER FINDS:

  FALSE POSITIVE   census says COVERED, the named witness stays green when the sentence changes
                   -> the census is crediting a guard that binds nothing. Inflates `covered`,
                      shrinks the UNCOVERED list, and HIDES surfaces. The comfortable direction.
  FALSE NEGATIVE   census says UNCOVERED, some guard goes red when the sentence changes
                   -> the census under-reports. Wastes review budget, and (round 16) is what a
                      threshold that cannot represent a short document looks like from outside.

⚠ SCOPE, STATED HONESTLY, AND THE FIRST VERSION OF THIS PARAGRAPH WAS NOT (round 17 seat A). It
said the perturbation changes "the first digit-run", while `ablate`'s own docstring said EVERY digit
run is tried — the module documented two different behaviours, and the function implementing the one
described here had ZERO callers. It also disposed of predicate sentences as "out of scope", which is
false: 9 of the 44 covered numbered article sentences carry no claim number at all, only digits
inside identifiers ("RNase-H1", "5-6-5", "three of three"), so they are perturbed on something that
is not their claim and pass for the wrong reason.

WHAT IS ACTUALLY TRUE: every digit run in the sentence is tried and the FIRST one that trips any
guard wins. That answers "would anything notice a change here?", which is the question the census is
a proxy for. It does NOT answer "is this sentence's own claim watched?" — a sentence can pass on an
exon number while its rate goes unread. Reported, not hidden: `claim_coverage.json` records the
per-sentence witness list, and the gap between the two questions is the honest residue.
"""
from __future__ import annotations

import atexit
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

sys.path.insert(0, HERE)
import claim_coverage as cc  # noqa: E402

#: The witness kinds the census emits, and the command that re-runs each one.
_LINT_CONSISTENCY = [sys.executable, os.path.join(HERE, "lint_consistency.py")]


def _locate(text, sentence):
    r"""Find a censused sentence in the RAW file, tolerating the line wrapping the flattener removed.

    ⛔⛔ THE FIRST VERSION USED `sentence in text`, AND IT MATCHED NOTHING — NOT ONCE IN SEVEN TRIES
    (2026-08-22, caught by a positive control, not by a red run). `claim_coverage._prose` joins lines
    and collapses whitespace, so a censused sentence is the file's text with its LINE BREAKS REMOVED
    and almost never appears verbatim. Every ablation silently did nothing, reported "no witness went
    red", and would have been read as "these guards are blind" — a fabricated measurement about to be
    used to justify narrowing the census.
    ★ Matching with `\s+` between tokens is what makes the mutation actually land.
    """
    rx = re.compile(r"\s+".join(re.escape(tok) for tok in sentence.split()))
    return rx.search(text)


def _witness_cmd(witness):
    """The command that re-runs one witness, or None if this witness is not runnable.

    The census emits two witness kinds: `test:<file>.py`, re-run as that pytest module, and
    `pin:<id>`, whose enforcement lives in `lint_consistency.py`.
    """
    if witness.startswith("test:"):
        return [sys.executable, "-m", "pytest", os.path.join(cc.TESTS, witness[len("test:"):]),
                "-q", "--no-header", "-p", "no:cacheprovider", "-p", "no:randomly"]
    if witness.startswith("pin:"):
        return list(_LINT_CONSISTENCY)
    if witness.startswith("generator:"):
        # A generated document's binding is REPRODUCTION: `--check` exits non-zero when the committed
        # file no longer matches what its generator produces.
        return [sys.executable, os.path.join(REPO, witness[len("generator:"):]), "--check"]
    return None


def _run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True).returncode != 0


#: The distinct outcomes of one ablation. ⛔ `NOT_APPLIED` MUST NEVER BE COLLAPSED INTO "no witness
#: went red": that conflation is what produced the fabricated reading above, and it is the same
#: early-exit-reports-a-pass defect this module exists to detect in other guards.
APPLIED, NOT_APPLIED = "applied", "not-applied"

#: One hard-linked clone of the repository, made once per process and reused.
_WORKSPACE = None


def _workspace():
    """A disposable clone of the repo that mutations happen in, so the REAL tree is never touched.

    ⛔⛔ THE FIRST VERSION MUTATED THE REAL MANUSCRIPT IN PLACE, AND IT CORRUPTED A PREFLIGHT RUN
    (measured 2026-08-22). A `finally` plus a digest check makes the mutation window SHORT; it does
    not make it SAFE, because safety here is about everything ELSE reading the repo during that
    window. Proven, not inferred: perturbing a pinned figure and running
    `research/modalities/tests/test_lint_consistency.py::test_the_real_repo_is_consistent`
    concurrently reproduces exactly the failure a preflight reported —
    `lint_consistency` reads the same file and sees a pin that disagrees with its artifact.
    ⚠ AND THE `finally` IS NOT EVEN RELIABLE: a process killed with SIGTERM (or its orphaned
    grandchild, which `pkill -P` does not reach) skips it and leaves a DEPOSIT ARTIFACT corrupted on
    disk. A gate that can lose a manuscript is not a gate.

    ★ `cp -al` COSTS 0.03 s FOR 3,326 FILES, so there was never a reason to accept the risk. The
    clone shares inodes, which means an IN-PLACE write would still reach the original — measured, it
    does — so every mutation is written to a new file and `os.replace`d into position, which breaks
    the link instead of following it.
    """
    global _WORKSPACE
    if _WORKSPACE and os.path.isdir(_WORKSPACE):
        return _WORKSPACE
    root = tempfile.mkdtemp(prefix="claim-ablation-")
    for entry in os.listdir(REPO):
        if entry == ".git":
            continue  # nothing under test reads it, and it is the bulk of the tree
        subprocess.run(["cp", "-al", os.path.join(REPO, entry), os.path.join(root, entry)],
                       check=True, capture_output=True)
    _WORKSPACE = root
    atexit.register(shutil.rmtree, root, True)
    return root


def _mirror(path, workspace):
    """The clone's copy of a repo path."""
    return os.path.join(workspace, os.path.relpath(path, REPO))


def _write_without_following_the_link(path, text):
    """⛔ `open(path, "w")` TRUNCATES THE SHARED INODE and reaches the original. Replace, never write."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    with io.open(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def guards_reading(document_basename):
    """Every guard that OPENS this document, whether or not the census could credit it.

    ⛔⛔ THE CENSUS CAN ONLY CREDIT A GUARD WHOSE LOGIC IS A HARVESTED STRING LITERAL, AND THE BEST
    GUARDS IN THIS SUITE ARE NOT (2026-08-22). `claim_coverage._test_patterns` scrapes regex-shaped
    literals out of test source; a guard that COMPUTES — the gene-identifier attestation set, the
    polarity table's span/require/forbid rows, seat 1's artifact bindings — exposes no such literal
    and is therefore invisible to it. Ablating only the census's `read_by` then reports those
    sentences BLIND when the paper is in fact well guarded: a false negative manufactured by the
    proxy rather than by the guards.
    ★ THE QUESTION THE GATE IS ACTUALLY ASKING IS "would anything notice?", so it runs everything
    that opens the file. The census stays a cheap SCREEN; this is the ASSAY.
    """
    out = []
    for name in sorted(os.listdir(cc.TESTS)):
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        try:
            if document_basename in io.open(os.path.join(cc.TESTS, name), encoding="utf-8").read():
                out.append(f"test:{name}")
        except OSError:
            continue

    # ⛔⛔ THE PINS ARE THE PRIMARY BINDING MECHANISM AND THE FIRST VERSION OF THIS FUNCTION DROPPED
    # THEM (2026-08-22). Scanning only `tests/` fixed the computed-guard blind spot and opened a new
    # one in the same edit: `lint_consistency.py` is what enforces every `must_appear_in` pin, and it
    # lives outside `tests/`, so three pins added to the cover letter minutes earlier changed nothing
    # and the sentence still read BLIND. ⚠ A fix that swaps one blind spot for another looks like
    # progress in the report and is not.
    out.append("pin:*")
    for key, path in cc.PAPERS.items():
        if os.path.basename(path) == document_basename:
            gen = cc._generator(path)
            if gen:
                out.append(f"generator:{gen}")
    return out


def _witness_cmds(witnesses, workspace):
    """One command per TOOL, not per witness — every pytest module in a single invocation.

    A sentence can carry a dozen witnesses; starting a dozen interpreters to ask one question is the
    difference between a gate that runs per commit and one that gets disabled.
    """
    manuscripts = _mirror(HERE, workspace)
    modules = [os.path.join(manuscripts, "tests", w[len("test:"):])
               for w in witnesses if w.startswith("test:")]
    cmds = []
    if modules:
        cmds.append([sys.executable, "-m", "pytest", *modules,
                     "-q", "--no-header", "-p", "no:cacheprovider", "-p", "no:randomly"])
    if any(w.startswith("pin:") for w in witnesses):
        cmds.append([sys.executable, os.path.join(manuscripts, "lint_consistency.py")])
    for w in witnesses:
        if w.startswith("generator:"):
            cmds.append([sys.executable, os.path.join(workspace, w[len("generator:"):]), "--check"])
    return cmds


def _run(cmd, workspace):
    return subprocess.run(cmd, cwd=workspace, capture_output=True, text=True).returncode != 0


def ablate(paper_key, row, witnesses=None):
    """Perturb the sentence IN A CLONE, run its guards there, and report whether anything noticed.

    Returns `{"status", "red", "witnesses", "reason"}`. A caller reading `red` without first checking
    `status == APPLIED` is reading absence as evidence.

    ⛔⛔ EVERY DIGIT RUN IS TRIED, NOT JUST THE FIRST (2026-08-22). Perturbing only the first one
    manufactured false BLIND verdicts wherever a sentence opens with an incidental number — a
    `5-6-5` gapmer motif, a "Table 1" cross-reference, a figure number. Those are not the claim, so
    nothing SHOULD go red for them, and scoring the sentence unwatched on that basis is the same
    "absent reading read as a reading of absence" this module was written to stop.
    ★ A sentence is bound if ANY perturbation of it trips a guard, which is what "would anything
    notice if this changed?" actually means. The first trip wins and the rest are not run.
    """
    path = cc.PAPERS[paper_key]
    original = io.open(path, encoding="utf-8").read()
    ws = list(witnesses) if witnesses is not None else guards_reading(os.path.basename(path))

    hit = _locate(original, row["sentence"])
    if hit is None:
        return {"status": NOT_APPLIED, "red": [], "witnesses": ws,
                "reason": "the censused sentence has no home in the raw file even allowing for line "
                          "wrapping — the flattener and the file have diverged"}
    span = original[hit.start():hit.end()]
    runs = list(re.finditer(r"\d+", span))
    if not runs:
        return {"status": NOT_APPLIED, "red": [], "witnesses": ws,
                "reason": "the sentence states no number, so this module defines no perturbation"}

    workspace = _workspace()
    mirror = _mirror(path, workspace)
    before = hashlib.sha256(original.encode()).hexdigest()
    cmds = _witness_cmds(ws, workspace)
    tried = []
    try:
        for m in runs:
            run = m.group(0)
            new_run = run[:-1] + ("7" if run[-1] != "7" else "4")
            tried.append(f"{run}->{new_run}")
            _write_without_following_the_link(
                mirror,
                original[:hit.start() + m.start()] + new_run + original[hit.start() + m.end():])
            if any(_run(cmd, workspace) for cmd in cmds):
                return {"status": APPLIED, "red": ws, "witnesses": ws,
                        "reason": f"{run} -> {new_run}"}
    finally:
        _write_without_following_the_link(mirror, original)
        after = hashlib.sha256(io.open(path, encoding="utf-8").read().encode()).hexdigest()
        if after != before:
            raise SystemExit(
                f"FATAL: the REAL {os.path.basename(path)} changed during an ablation "
                f"({before[:12]} -> {after[:12]}). Recover it from git before doing anything else.")
    return {"status": APPLIED, "red": [], "witnesses": ws,
            "reason": "no guard reading this file noticed any of: " + ", ".join(tried)}
