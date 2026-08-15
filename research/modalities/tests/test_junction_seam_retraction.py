#!/usr/bin/env python3
"""The retracted-seam guard must actually catch a retracted seam, and must actually be WIRED IN.

⛔ TWO CLASSES OF TEST HERE, AND THE SECOND IS THE ONE THIS REPOSITORY HAS BEEN BURNED BY.
The first class exercises `junction_seam_retraction` against real artifact SHAPES and asserts it
grades them right. The second asserts that the workflow which OWNS the `modalities-cache` branch
actually calls it -- because CLAUDE.md 6 records a guard that was documented in three places, wired
to a lane name no caller passed, and therefore protected nothing for 8.9 hours while reading as
safe: "a property asserted in prose about a value passed by a caller is not a property; it is a
hope." A banner sweep that no publish step invokes is exactly that shape.

⚠ No mocks of the module under test. The fixtures below are the REAL seam strings, and the
reference sets are the REAL ones re-derived from the committed exon audit and transcript cache.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MODALITIES))
sys.path.insert(0, MODALITIES)

import junction_seam_retraction as JSR  # noqa: E402

WORKFLOW = os.path.join(REPO, ".github", "workflows", "aso-offtarget.yml")


# ---------------------------------------------------------------------------------------------
# The reference sets, re-derived
# ---------------------------------------------------------------------------------------------

def test_the_retracted_seam_set_reproduces_the_documented_defect():
    """`TTGTCCGTACAG` at NR4A3 CDS nt 1081 must fall out of the arithmetic, not out of a constant.

    1081 // 3 + 1 == 361, which is one of the three resume residues
    `fusion-neoantigen-retraction.json` records as retracted. If this ever fails, either the exon
    audit moved or somebody typed the seam in -- both of which invalidate every grade below.
    """
    seams = JSR.retracted_acceptor_seams()
    assert 1081 in seams, seams
    assert seams[1081] == "TTGTCCGTACAG", seams[1081]
    assert sorted(q // 3 + 1 for q in seams) == [318, 361, 419], sorted(seams)
    src = open(os.path.join(MODALITIES, "junction_seam_retraction.py"), encoding="utf-8").read()
    # The seam may appear in prose in the module header; it must not appear in a code constant.
    code = "\n".join(l for l in src.split("\n") if not l.strip().startswith("#"))
    body = code.split('"""', 2)[-1]
    assert "TTGTCCGTACAG" not in body, (
        "the retracted seam is hard-coded in the module body -- it must be DERIVED, or the guard "
        "stops tracking the defect the moment the exon model changes")


def test_the_corrected_acceptor_seam_is_the_one_the_repository_already_recorded():
    """`ATATGCCCTGCG` -- two retained 5'UTR nt then NR4A3's ATG -- re-derived, not typed."""
    correct = JSR.correct_acceptor_seams()
    assert correct.get(3) == "ATATGCCCTGCG", correct
    assert set(correct.values()).isdisjoint(set(JSR.retracted_acceptor_seams().values())), (
        "a seam cannot be both corrected and retracted; the two reference sets overlap")


# ---------------------------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------------------------

_RETRACTED_DOC = {
    "_note": "Fusion-junction gapmer ASO designs.",
    "_breakpoint_model": {"assumption": False, "mode": "real_exon_junction",
                          "junction_label": "EWSR1_e10__NR4A3_e3",
                          "junction_context_mRNA": "ATCTTGATCTAG|TTGTCCGTACAG"},
}
_NESTED_RETRACTED_DOC = {
    "junction_label": "EWSR1_e9__NR4A3_e3",
    "breakpoint": {"mode": "real_exon_junction", "NR4A3_from_aa": 2,
                   "junction_context_mRNA": "ATAAGCCTGGTG|TTGTCCGTACAG"},
}
_CORRECT_DOC = {
    "_breakpoint_model": {"assumption": True, "mode": "real_exon_junction_mRNA",
                          "junction_context_mRNA": "ACGGGCAGCAGA|ATATGCCCTGCG"},
}
_MODELLED_DOC = {
    "_breakpoint_model": {"assumption": True, "mode": "modelled_reference_codon_space",
                          "junction_context_mRNA": "TACGGGCAGCAG|CCCTGCGTCCAA"},
}


def test_a_retracted_seam_under_breakpoint_model_is_caught():
    g, d = JSR.grade(_RETRACTED_DOC)
    assert g == JSR.GRADE_RETRACTED, (g, d)
    assert d["retracted_fields"][0]["nr4a3_resumes_at_residue"] == 361


def test_a_retracted_seam_NESTED_UNDER_A_DIFFERENT_KEY_IS_ALSO_CAUGHT():
    """⛔ Six of the thirteen real defects hide the seam under `breakpoint`, not `_breakpoint_model`.

    A grader that knew only one location would have passed exactly those six -- the same six that
    carry `NR4A3_from_aa: 2` beside a seam at residue 361, a file contradicting itself.
    """
    g, d = JSR.grade(_NESTED_RETRACTED_DOC)
    assert g == JSR.GRADE_RETRACTED, (g, d)
    assert d["retracted_fields"][0]["field"].endswith("breakpoint.junction_context_mRNA")


def test_a_corrected_panel_is_not_bannered():
    assert JSR.grade(_CORRECT_DOC)[0] == JSR.GRADE_CORRECT


def test_a_declared_codon_space_reference_is_not_bannered():
    """⛔ A gate that goes red on correctly-labelled files gets switched off, taking the real
    defects with it. Seven committed artifacts are the codon-space modelled reference."""
    assert JSR.grade(_MODELLED_DOC)[0] == JSR.GRADE_MODELLED


def test_the_real_or_modelled_call_is_read_from_mode_and_not_from_the_assumption_flag():
    """⛔ THE TRAP. `junction_aso.py` derived `assumption` by string-equality against
    "real_exon_junction"; the corrected builder renamed its mode to "real_exon_junction_mRNA" and
    the comparison was never updated, so RETRACTED artifacts carry `assumption: false` and
    CORRECTED ones carry `assumption: true`. Keying the grader on that flag would have inverted it.
    """
    assert JSR.declares_a_real_exon_junction(_RETRACTED_DOC) is True
    assert _RETRACTED_DOC["_breakpoint_model"]["assumption"] is False        # the trap, asserted
    assert JSR.declares_a_real_exon_junction(_CORRECT_DOC) is True
    assert _CORRECT_DOC["_breakpoint_model"]["assumption"] is True           # and its other half
    assert JSR.declares_a_real_exon_junction(_MODELLED_DOC) is False


def test_the_banner_names_the_corrected_seam_and_refuses_quotation():
    _, d = JSR.grade(_RETRACTED_DOC)
    b = JSR.banner(d, JSR.correct_acceptor_seams(), "2026-01-01T00:00:00Z", "2025-12-31 7:00 PM ET")
    assert b[JSR.STAMP_KEY] is True
    assert "DO NOT QUOTE" in b["status"]
    assert b["corrected_acceptor_seam"] == "ATATGCCCTGCG"
    assert "361" in b["one_line"]


def test_write_is_idempotent_and_check_agrees_with_it(tmp_path=None):
    """`--write` then `--check` must agree, and a second `--write` must change nothing.

    Runs against a REAL temporary directory of REAL artifact shapes -- no monkeypatching of the
    sweep, because the seam being tested is the file I/O.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for name, doc in (("junction-aso-designs-eXn3.json", _RETRACTED_DOC),
                          ("junction-sirna-designs-eYn3.json", _NESTED_RETRACTED_DOC),
                          ("junction-aso-offtarget-eZn3.json", _CORRECT_DOC)):
            with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                json.dump(doc, fh, ensure_ascii=False)

        assert JSR.main(["--check", "--dir", d]) == 1, "--check passed an unbannered retracted seam"
        assert JSR.main(["--write", "--dir", d]) == 0
        assert JSR.main(["--check", "--dir", d]) == 0, "--check still fails after --write"
        rows = JSR.sweep(d, write=True)
        assert not any(r["changed"] for r in rows), "--write is not idempotent; it rewrites every run"
        first = json.load(open(os.path.join(d, "junction-aso-designs-eXn3.json"), encoding="utf-8"))
        assert next(iter(first)) == JSR.BANNER_KEY, (
            "the banner is not the first key -- a retraction a reader must scroll to is one half "
            "the readers will miss")


# ---------------------------------------------------------------------------------------------
# ⛔ THE WIRING. Everything above is worth nothing if no publish step calls it.
# ---------------------------------------------------------------------------------------------

def test_the_workflow_that_owns_modalities_cache_runs_the_sweep_before_it_pushes():
    """The publish step of `aso-offtarget.yml` must `--write`, then `--check`, then push.

    ⛔ ORDER IS ASSERTED, NOT JUST PRESENCE. A `--check` after the push, or a `--write` with no
    `--check`, would both leave the branch exactly as unprotected as it was while reading as fixed.
    """
    text = open(WORKFLOW, encoding="utf-8").read()
    assert 'junction_seam_retraction.py" --write' in text, (
        "the workflow that owns modalities-cache does not run the seam sweep; any banner it "
        "publishes over will be silently dropped on the next run")
    i_write = text.index('junction_seam_retraction.py" --write')
    i_check = text.index('junction_seam_retraction.py" --check', i_write)
    i_push = text.index("git push origin modalities-cache")
    assert i_write < i_check < i_push, (i_write, i_check, i_push)


def test_the_sweep_tool_is_staged_before_the_branch_switch_because_the_branch_has_no_code():
    """⛔ `modalities-cache` carries ZERO `.py` files, so the tool must be copied out first.

    Invoking it from `research/modalities` AFTER `git checkout -B modalities-cache` would fail with
    a missing file on every publish — and since the sweep is a hard gate, that would block all
    publishing from this workflow, turning a data-integrity guard into an outage. Asserted rather
    than described, because "the file will be there" is a hope about a checkout, not a property.
    """
    text = open(WORKFLOW, encoding="utf-8").read()
    i_stage = text.index('cp research/modalities/junction_seam_retraction.py')
    i_switch = text.index("git checkout -B modalities-cache")
    assert i_stage < i_switch, "the sweep tool is staged after the branch switch, where it does not exist"
    # every input the tool resolves relative to its own directory must travel with it
    staged = text[i_stage:i_switch]
    for dep in ("junction_aso.py", "fusion_breakpoints.py", "nr4a3-exon-audit.json",
                "emc-construct-inputs.json"):
        assert dep in staged, "%s is not staged with the sweep tool" % dep
    i_run = text.index('junction_seam_retraction.py" --write')
    assert i_run > i_switch, "sanity: the sweep should run on the checked-out cache tree"
    assert '--dir research/modalities' in text[i_run:i_run + 200], (
        "the staged tool must be pointed at the checked-out artifact tree with --dir")


def test_the_staged_tool_actually_RUNS_from_the_files_the_workflow_stages(tmp_path=None):
    """⛔ STAGE WHAT THE WORKFLOW STAGES, AND RUN IT. The list above is a HAND-MAINTAINED IMPORT
    CLOSURE, and naming the files a test remembers is exactly how it went stale.

    MEASURED 2026-08-15. `junction_seam_retraction` gained `import aso_screen_sets` on 2026-08-14
    (commit 538d2ec4) and the workflow's `cp` list was not updated with it. Copying the six files
    that list named to a temp directory and running `--check --dir <empty>` — which is precisely
    what the publish step does three lines later, as its self-test — died with
    `ModuleNotFoundError: No module named 'aso_screen_sets'`. That self-test is a HARD GATE, so
    every publish from the workflow that owns `modalities-cache` would have refused; it went
    unnoticed only because no run had been dispatched in the intervening day.

    The test above could not have caught it: it asserts that four remembered dependencies appear in
    the staged block, and all four still did. So this one does not read the list at all — it parses
    the paths OUT of the workflow, copies exactly those, and executes the tool. A dependency added
    to the module and forgotten here now fails the build instead of the next publish.
    """
    import re  # noqa: PLC0415
    import shutil  # noqa: PLC0415
    import subprocess  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    text = open(WORKFLOW, encoding="utf-8").read()
    i_stage = text.index('cp research/modalities/junction_seam_retraction.py')
    block = text[i_stage:text.index('"$RUNNER_TEMP/tool/"', i_stage)]
    paths = re.findall(r'research/modalities/[A-Za-z0-9._-]+', block)
    assert paths, "no staged paths parsed out of the workflow"

    with tempfile.TemporaryDirectory() as tmp:
        tool, empty = os.path.join(tmp, "tool"), os.path.join(tmp, "empty")
        os.makedirs(tool)
        os.makedirs(empty)
        for rel in paths:
            src = os.path.join(REPO, rel)
            assert os.path.exists(src), f"the workflow stages {rel}, which does not exist"
            shutil.copy(src, tool)
        # `--check` over an empty directory grades nothing: this is a pure import/derivation check
        # of the staged copy, which is the same thing the publish step's self-test is.
        r = subprocess.run([sys.executable, os.path.join(tool, "junction_seam_retraction.py"),
                            "--check", "--dir", empty],
                           capture_output=True, text=True,
                           env={**os.environ, "TRANSCRIPT_SOURCE": "cache"})
        assert r.returncode == 0, (
            "the staged sweep tool cannot run from the files the workflow copies — every publish "
            f"from aso-offtarget.yml would refuse.\nstdout: {r.stdout[-800:]}\n"
            f"stderr: {r.stderr[-800:]}")


def test_a_sweep_dispatch_stages_nothing_from_the_checkout():
    """⛔ THIS ONE COST DATA BEFORE IT EXISTED, WHICH IS WHY IT IS ASSERTED AND NOT DESCRIBED.

    Run 31277458528 (2026-08-08), the first seam-sweep dispatch: no science step ran, so the
    publish step's unconditional `cp research/modalities/<globs> $RUNNER_TEMP/res/` staged the
    REPOSITORY's committed copies and wrote them over the branch's own. `hybrid-intron-model.json`
    went from 134,817 bytes on `modalities-cache` to the repo's 16,934-byte copy — a 3,130-line
    deletion inside a commit whose subject said it was bannering seams.

    A mode that runs no producer has no outputs; copying a checked-in file is not a result. The
    branch is the accumulating home for these artifacts and the checkout is not, so a sweep must
    stage nothing at all.

    ⛔⛔ THIS TEST WAS DEAD FOR A DAY AND FAILED LOUDLY RATHER THAN SILENTLY, WHICH IS THE ONLY REASON
    IT IS BEING FIXED AND NOT MOURNED (2026-08-13). It located the guard by `text.index` on the literal
    `cp research/modalities/junction-aso-designs*.json "$RUNNER_TEMP/res/"` — and the 2026-08-12
    rewrite replaced that unconditional `cp` with mtime-scoped `find … -newer "$RUNNER_TEMP/job-start"
    -exec cp` staging, so the literal stopped existing and `index` raised ValueError on `main`. The
    property it guards is MORE true than before, and nothing was checking it.
    ⚠ THE LESSON IS THE ANCHOR, NOT THE STRING. A test that finds the code it guards by pasting a
    line of that code has a lifetime equal to the next refactor of that line. This looks for the
    guard CONDITION and the staging BLOCK instead, so a change to how files are copied cannot
    silently retire it.
    """
    text = open(WORKFLOW, encoding="utf-8").read()
    guard = '[ "${{ inputs.seam_retraction_sweep }}" != "true" ]; then'
    assert guard in text, (
        "the publish step no longer guards staging on the sweep input; a seam-sweep dispatch will "
        "overwrite modalities-cache artifacts with whatever is committed in the repo")
    i_stage = text.index(guard)
    i_else = text.index("\n          else", i_stage)
    staged = text[i_stage:i_else]

    # Everything the publish stages must sit inside that guard, however it is copied.
    for glob_ in ("junction-aso-designs*.json", "junction-aso-offtarget*.json",
                  "aso-insilico-evaluation*.json", "junction-sirna-designs*.json",
                  "hybrid-intron-model.json", "aso-premrna-*.json"):
        assert glob_ in staged, "%s is staged outside the sweep guard" % glob_

    # ⛔ AND THE SWEEP BRANCH MUST STAGE NOTHING AT ALL, which is the actual property. An `else` that
    # quietly copied one glob would satisfy every assertion above.
    i_fi = text.index("\n          fi", i_else)
    sweep_branch = text[i_else:i_fi]
    assert "cp research/modalities" not in sweep_branch and "-exec cp" not in sweep_branch, (
        "the seam-sweep branch stages something from the checkout: %r" % sweep_branch[:300])


def test_the_sweep_failure_actually_blocks_the_push():
    """A guard whose failure is swallowed by `|| true` is a report, not a guard.

    This repository has the incident on record: `|| echo` on a fetch step let a swallowed failure
    exit 0 and the publish then republished stale artifacts under a fresh-screen commit message
    (junction_aso.py's `_env_int` block, run 31130625823).
    """
    text = open(WORKFLOW, encoding="utf-8").read()
    start = text.index("git checkout -B modalities-cache")
    for flag in ("--write", "--check"):
        i = text.index('junction_seam_retraction.py" %s' % flag, start)
        tail = text[i:i + 400]
        assert "exit 1" in tail, "%s does not fail the job: %r" % (flag, tail[:200])
        line_end = text.index("\n", i)
        assert "|| true" not in text[i:line_end], "%s swallows its own failure" % flag


if __name__ == "__main__":                                        # pragma: no cover
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS %s" % name)
            except AssertionError as exc:
                failures += 1
                print("FAIL %s: %s" % (name, exc))
    sys.exit(1 if failures else 0)


def test_the_publish_refuses_to_delete_an_artifact():
    """⛔ RUN 31696283722 DELETED 39 ARTIFACTS FROM modalities-cache AND EVERY EXISTING GUARD PASSED.

    Mechanism, and it is a shell bug rather than a git one: the publish `rm -f
    research/modalities/*.json` deletes the FEATURE-BRANCH copies, `git checkout -B modalities-cache`
    carries those working-tree deletions across (for a file identical in both refs the deletion is an
    uncommitted change git can preserve), and then `git add research/modalities/junction-aso-designs
    *.json` — with the glob matching nothing in the working tree — is passed to git LITERALLY, expanded
    as a pathspec against the INDEX, and stages all 39 deletions.

    ⚠ WHY NOTHING CAUGHT IT. Every other guard in that step reasons about what the run PRODUCED: the
    mtime baseline, the sweep-staging rule above, the commit-message check. This loss came from what
    the checkout carried IN, which no producer-shaped guard can see. The sibling off-target glob
    escaped only because it happened to match one `-graded.json` file that exists on that branch
    alone, so whether a family survived depended on an unrelated file existing.

    Two assertions, because the fix has two halves and either alone leaves a hole: the tree is
    restored from HEAD after the branch switch, and the commit is refused outright if the staged diff
    contains a deletion. This workflow adds and updates artifacts; it never removes one.
    """
    text = open(WORKFLOW, encoding="utf-8").read()
    i_switch = text.index("git checkout -B modalities-cache")
    i_commit = text.index('git commit -m "$MSG"', i_switch)
    window = text[i_switch:i_commit]
    assert "git checkout HEAD -- research/modalities" in window, (
        "the publish does not restore the branch's own tree after switching, so working-tree "
        "deletions carried across the checkout can be staged")
    assert "git diff --cached --diff-filter=D --name-only" in window, (
        "the publish does not check the staged diff for deletions")
    i_guard = window.index("git diff --cached --diff-filter=D --name-only")
    assert "exit 1" in window[i_guard:i_guard + 600], (
        "the deletion check does not fail the job; a guard that reports and continues is not a guard")
