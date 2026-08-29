"""`claim_coverage.py --check` must refuse a census artifact the guard corpus has invalidated.

⛔⛔ WHY THIS FILE EXISTS (AUT-PD-130, measured 2026-08-28). `83aede1` closed AUT-PD-119 by widening
three guards' regex patterns. Two of those guards witness a censused manuscript, and the census
HARVESTS ITS PATTERNS FROM THE TEST CORPUS — so `covered` moved 99 -> 101 with no manuscript byte
touched, the committed census artifact went stale, and `main` was red on a clean tree for about 35
minutes. The pairing that normally catches a stale artifact did not apply: the manuscript and the
artifact had last been written by the SAME commit, so a doc-touches-artifact rule saw nothing, and
the invalidating edit lived in a different DIRECTORY from the artifact it staled.

⚠ AND THE RED WAS NOT COSMETIC. `claim_ablation._baseline_reds` correctly subtracts a witness that
is already red on the unmutated clone, so while that guard was red every sentence whose only witness
is that module scored BLIND — a false BLIND pointing a reader at the paper rather than at the
instrument.

★ THE REPAIR IS A RECOMPUTATION, NOT A PATH RULE, and the tests below hold both halves of it: the
check is REAL (it refuses every way the artifact can disagree with a live census, including the way
the incident produced), and the check is WIRED (commit loop, CI, regeneration chain). A verify mode
nothing calls protects exactly as much as one that cannot fail.

⛔⛔ EVERY MUTATION RUNS AGAINST A CLONE, AND THAT IS NOT FASTIDIOUSNESS. Both suites run under
`-n <cores> --dist loadfile`, which distributes by FILE: while this module ran, a sibling worker
would be running `test_claim_coverage_has_not_regressed`, which reads the same artifact and runs the
same census. Perturbing the real `claim-coverage.json` — or dropping a fixture into the real test
corpus — would redden that test on another worker at a rate near a coin flip, and a
non-deterministic red gets a guard deleted, not fixed. The clone is a tree of symlinks built in
pytest's `tmp_path`; only the files a test perturbs are materialised, so the mutation is invisible
to every other worker and to the working tree the commit is made from.

⚠ THIS MODULE DELIBERATELY NAMES NO CENSUSED DOCUMENT — see the last test. `_test_patterns` credits
a module's literals to any document whose basename appears anywhere in its source, so a guard for
the census that typed a manuscript filename would change the number it is guarding.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
sys.path.insert(0, MANUSCRIPTS)

import claim_coverage  # noqa: E402

#: Directories a symlink clone must not descend into: git's object store is large and irrelevant,
#: and a node_modules tree is neither read by the census nor cheap to walk.
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache"}


@pytest.fixture(scope="module")
def live_report():
    """One live census for every artifact-level test — it is ~1.7 s and its result is a constant."""
    return claim_coverage.build_report()


@pytest.fixture(scope="module")
def committed_text():
    return io.open(claim_coverage.ARTIFACT, encoding="utf-8").read()


@pytest.fixture(scope="module")
def clone(tmp_path_factory):
    """A whole-repository mirror: real directories, symlinked files.

    ⛔ SYMLINKS RATHER THAN COPIES because the census reads 32 manuscripts, three records, the pins
    and every module in the test corpus, and a real copy of the repository per test module is a cost
    with no matching benefit. `claim_coverage` derives its own REPO from `__file__`, which Python
    does not resolve through a symlink, so a run inside the clone reads the clone.
    """
    root = str(tmp_path_factory.mktemp("census-clone") / "repo")
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)
        rel = os.path.relpath(dirpath, REPO)
        target_dir = root if rel == "." else os.path.join(root, rel)
        os.makedirs(target_dir, exist_ok=True)
        for name in filenames:
            src, dst = os.path.join(dirpath, name), os.path.join(target_dir, name)
            if not os.path.lexists(dst) and os.path.exists(src):
                os.symlink(src, dst)
    #: The clone must reproduce before any test perturbs it, or every red below is the clone's.
    proc = _check(root)
    assert proc.returncode == 0, (
        f"the clone does not reproduce before any mutation, so nothing below measures a mutation:\n"
        f"{proc.stdout}{proc.stderr}")
    return root


def _check(root, *args):
    """Run the REAL command line preflight runs, inside `root`."""
    return subprocess.run(
        [sys.executable, os.path.join(root, "research", "manuscripts", "claim_coverage.py"),
         "--check", *args], capture_output=True, text=True)


def _materialise(root, rel):
    """Replace one symlink in the clone with a real file, so a test can edit it in isolation."""
    path = os.path.join(root, rel)
    if os.path.islink(path):
        real = os.path.realpath(path)
        os.remove(path)
        shutil.copyfile(real, path)
    return path


def _mutated_artifact(root, mutate):
    """Apply `mutate` to the clone's committed census and return the check's completed process."""
    path = _materialise(root, "research/manuscripts/claim-coverage.json")
    doc = json.loads(io.open(path, encoding="utf-8").read())
    mutate(doc)
    io.open(path, "w", encoding="utf-8").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    try:
        return _check(root)
    finally:
        _materialise(root, "research/manuscripts/claim-coverage.json")
        shutil.copyfile(claim_coverage.ARTIFACT, path)


def _a_censused_paper():
    """The censused document with the most sentences — the widest target for a fixture pattern."""
    papers = json.loads(io.open(claim_coverage.ARTIFACT, encoding="utf-8").read())["papers"]
    return max(papers, key=lambda p: papers[p]["sentences"])


# --------------------------------------------------------------------------------------
# The committed artifact, and the comparison that decides it.
# --------------------------------------------------------------------------------------


def test_check_passes_on_the_committed_artifact():
    """⛔ FIRST, because every refusal below is meaningless if the green case is not green."""
    assert claim_coverage.main(["--check"]) == 0, (
        "the committed census does not reproduce from a live run — regenerate it with "
        "`python3 research/manuscripts/claim_coverage.py --write` and commit the result")


def test_a_perturbed_count_is_named_field_by_field(live_report, committed_text):
    """⚠ A DIFF, NOT A BOOLEAN. A reader of a red gate who is told only "stale" can act only by
    regenerating, and a regeneration is what makes a real regression disappear into a green run."""
    doc = json.loads(committed_text)
    paper = _a_censused_paper()
    doc["papers"][paper]["covered"] += 1
    bad = claim_coverage.disagreements(
        live_report, json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    assert bad, "a changed `covered` was accepted, so the comparison verifies nothing"
    assert any(paper in line and "covered" in line for line in bad), bad


def test_a_dropped_document_is_refused(live_report, committed_text):
    paper = _a_censused_paper()
    doc = json.loads(committed_text)
    doc["papers"].pop(paper)
    bad = claim_coverage.disagreements(
        live_report, json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    assert any(paper in line for line in bad), bad


def test_counts_for_a_document_nothing_censuses_are_refused(live_report, committed_text):
    """⛔ THE OTHER DIRECTION, AND IT IS ASSERTED ON THE MESSAGE FOR A MEASURED REASON. Counts left
    behind for a retired endpoint read as a live measurement of a document nothing measures.

    ⚠ MUTATION-TESTED 2026-08-28: deleting the reverse-direction loop outright left this test GREEN
    while it asserted only that some disagreement was reported, because the byte backstop below
    catches the same file — the specific finding was masked by a general one, and the reader would
    have been told "the bytes differ" about a retired endpoint. Binding the sentence the loop
    produces is what makes the deletion visible.
    """
    orphan = "research/manuscripts/a-document-that-is-not-on-disk.md"
    doc = json.loads(committed_text)
    doc["papers"][orphan] = {
        "sentences": 1, "covered": 1, "with_a_number": 1, "with_a_number_covered": 1,
        "uncovered": 0, "uncovered_with_a_number": 0}
    bad = claim_coverage.disagreements(
        live_report, json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    assert any(orphan in line and "no longer censused" in line for line in bad), bad


def test_a_rewritten_record_of_which_record_named_each_document_is_refused(live_report,
                                                                          committed_text):
    """⚠ THIS FIELD MOVES NO COUNT, and it is the one that says the predicate was used at all.

    The freshness assertion in `test_the_paper_states_what_its_own_claims_depend_on.py` compares the
    six per-paper counts and nothing else, so this half of the artifact could drift while every
    number agreed. A populated field is not a measured one (CLAUDE.md §4).
    ⚠ AND THE ASSERTION IS ON THE MESSAGE, for the reason the test above records: deleting the
    metadata comparison outright left an existence-only assertion green, because the byte backstop
    reports the same file in words that name nothing.
    """
    doc = json.loads(committed_text)
    doc["named_by"][sorted(doc["named_by"])[0]] = "a record that did not name it"
    bad = claim_coverage.disagreements(
        live_report, json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    assert any(line.startswith("named_by:") for line in bad), bad


def test_bytes_that_write_would_not_produce_are_refused(live_report, committed_text):
    """Every field agrees and the file is still not the one `--write` makes."""
    reformatted = json.dumps(json.loads(committed_text), indent=4, ensure_ascii=False) + "\n"
    assert claim_coverage.disagreements(live_report, reformatted)


def test_an_unreadable_artifact_is_refused(live_report):
    assert claim_coverage.disagreements(live_report, "{ not json")


def test_an_unrecognised_mode_is_an_error_rather_than_a_silent_pass():
    """⛔ THE FAILURE MODE OF WIRING A GATE: the flag is misspelled and the row is green forever.

    Before AUT-PD-130 this module ignored every argument it did not recognise and exited 0, so
    `claim_coverage.py --verify` in a workflow would have been a row that measured nothing — the
    defect `.github/workflows/tests.yml` records against `emc_systemic_therapy_pooling.py`.
    """
    assert claim_coverage.main(["--verify"]) != 0
    assert claim_coverage.main(["--check-archive"]) != 0


def test_write_and_check_together_are_refused():
    """A verify that regenerates its own reference passes unconditionally, whatever went wrong."""
    assert claim_coverage.main(["--write", "--check"]) != 0


# --------------------------------------------------------------------------------------
# The command line, and the incident itself — both inside the clone.
# --------------------------------------------------------------------------------------


def test_the_command_line_exits_non_zero_and_says_which_document_moved(clone):
    """⛔ THE EXIT CODE IS WHAT PREFLIGHT READS. A comparison that returns a list of disagreements
    and a process that reports them are different claims, and only the second one gates a commit."""
    paper = _a_censused_paper()
    proc = _mutated_artifact(clone, lambda doc: doc["papers"][paper].__setitem__(
        "covered", doc["papers"][paper]["covered"] + 1))
    assert proc.returncode != 0, "the command line accepted a stale artifact"
    assert paper in proc.stderr, proc.stderr
    assert "--write" in proc.stderr, "the remedy is not in the message a reader sees"


def test_a_missing_artifact_is_refused(clone):
    """⛔ AN ABSENT ARTIFACT IS NOT A REPRODUCING ONE, AND ONLY THE PROCESS CAN SAY SO.

    `disagreements()` never sees this case — it is handed the file's text — so the branch that
    decides it lives in `main()` alone, and nothing bound it until now. It is the cheapest way to
    make this gate green while measuring nothing: delete the file the check compares against and a
    check that returns 0 on absence reports "no disagreement" for a census nobody can read.
    ⚠ FOUND BY MUTATION, NOT BY READING (2026-08-29, seat s4): flipping that one `return 1` to
    `return 0` left all 17 tests of this module green, the only survivor of thirteen single-site
    mutations. The other twelve — each half of the comparison, the byte backstop, the unreadable
    JSON branch, the unknown-flag error, the `--write --check` refusal, the document name in the
    message, and the wiring in each of preflight, CI and the regeneration chain — were caught.
    """
    path = os.path.join(clone, "research/manuscripts/claim-coverage.json")
    saved = os.readlink(path) if os.path.islink(path) else None
    os.remove(path)
    try:
        proc = _check(clone)
        assert proc.returncode != 0, "the check accepted a census artifact that is not there"
        assert "--write" in proc.stderr, "the remedy is not in the message a reader sees"
    finally:
        if saved is not None:
            os.symlink(saved, path)
        else:
            shutil.copyfile(claim_coverage.ARTIFACT, path)


def _selective_excerpt(paper):
    """A literal from one of `paper`'s own sentences that binds exactly that sentence.

    ⚠ DERIVED AT RUN TIME, NEVER TYPED. A typed pattern would be a second copy of a manuscript's
    prose, stale the moment the paper is edited — and the document's basename would have to be typed
    beside it, which is the one thing this module must not contain.
    """
    sents = claim_coverage.sentences(os.path.join(REPO, paper))
    for sentence in sents:
        excerpt = sentence[10:70].strip()
        if len(excerpt) < 24:
            continue
        pattern = "(?:" + re.escape(excerpt) + ")"
        if claim_coverage.is_selective(pattern, sents):
            return pattern
    pytest.skip(f"no sentence of {paper} yields a selective excerpt")


def test_a_widened_guard_pattern_alone_turns_the_check_red(clone):
    """⛔⛔ THE REPRODUCTION. No manuscript byte moves; only a file in the guard corpus appears.

    This is `83aede1` in miniature: a guard gains a pattern that binds a sentence of a censused
    document, the census credits it, and the committed artifact is stale from that moment. Nothing
    in the commit loop could see it before this change — the freshness comparison lived in the
    manuscripts suite, which is opt-in locally and reached in CI only after the push that shares the
    mistake.
    """
    paper = _a_censused_paper()
    pattern = _selective_excerpt(paper)
    fixture = os.path.join(clone, "research", "manuscripts", "tests",
                           "test_zz_a_widened_guard_pattern.py")
    try:
        io.open(fixture, "w", encoding="utf-8").write(
            f"DOCUMENT = {os.path.basename(paper)!r}\nPATTERN = {pattern!r}\n")
        proc = _check(clone)
        assert proc.returncode != 0, (
            "a new guard pattern binding a censused sentence left --check green: the census "
            "artifact and the guard corpus are not paired, which is AUT-PD-130 reopening")
        assert paper in proc.stderr, proc.stderr
    finally:
        os.remove(fixture)
    assert _check(clone).returncode == 0, "the check did not go green again once the guard was gone"


def test_a_guard_that_names_no_censused_document_leaves_the_check_green(clone):
    """⛔ THE NEGATIVE CONTROL, AND IT IS WHAT KEEPS THIS FROM BEING A PATH RULE.

    Most edits under the guard corpus move no pattern that binds any censused sentence, and a gate
    that reddened on all of them would be relaxed within a week — the census recomputation reddens
    on the census OUTPUT changing, which is the question actually at issue.
    """
    fixture = os.path.join(clone, "research", "manuscripts", "tests",
                           "test_zz_a_guard_that_binds_nothing_censused.py")
    try:
        io.open(fixture, "w", encoding="utf-8").write(
            'PATTERN = "(?:a phrase that appears in no publication endpoint at all)"\n')
        assert _check(clone).returncode == 0, (
            "a guard naming no censused document moved the census — the check is reddening on the "
            "presence of a file rather than on the census output")
    finally:
        os.remove(fixture)


def test_the_clone_left_the_working_tree_alone(clone):
    """⛔ THE MUTATION-WINDOW RULE, ASSERTED RATHER THAN INTENDED (CLAUDE.md §6, 2026-08-27: a
    mutation window that overlapped a `git add -A` put 13 inverted claims on `origin/main`)."""
    assert claim_coverage.main(["--check"]) == 0, (
        "a test in this module perturbed the real tree instead of the clone")
    for name in os.listdir(HERE):
        assert not name.startswith("test_zz_"), f"a fixture escaped the clone: {name}"


# --------------------------------------------------------------------------------------
# The check is wired.
# --------------------------------------------------------------------------------------


def _text(rel):
    return io.open(os.path.join(REPO, rel), encoding="utf-8").read()


def test_the_commit_loop_runs_the_census_check():
    """⛔ THE HALF THAT WAS MISSING. The comparison has existed since 2026-08-22 and ran nowhere a
    commit could see it: the manuscripts suite is opt-in behind PREFLIGHT_TESTS=1, and CI reaches it
    only after the push that ships the stale artifact."""
    assert ("research/manuscripts/claim_coverage.py|claim coverage census|--check"
            in _text("scripts/preflight.sh")), (
        "the census is not a row in preflight's generated-artifact gate, so a guard-pattern "
        "widening can again reach `main` and redden it on a clean tree")


def test_ci_runs_the_census_check():
    assert "research/manuscripts/claim_coverage.py --check" in _text(".github/workflows/tests.yml")


def test_the_regeneration_chain_verifies_the_census():
    """With a real `--check` the chain's verify mode prints a verdict instead of NOT VERIFIED."""
    chain = _text("scripts/regenerate_aso_chain.sh")
    assert "claim_coverage.py --check" in chain
    assert "claim_coverage.py --write" in chain


def test_this_module_names_no_censused_document():
    """⛔⛔ REFLEXIVE, AND NOT DECORATION. `_test_patterns` credits a test module's string literals
    to every document whose basename appears anywhere in its source — a constant, a comment,
    anywhere. A guard for the census that typed a manuscript filename would change the very counts
    it exists to hold, exactly as the four floor-table keys did on 2026-08-26 (the cover letter read
    16 covered instead of 10). Deriving the document at run time is what keeps this file inert.
    """
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    named = sorted({os.path.basename(p) for p in claim_coverage.PAPERS
                    if os.path.basename(p) in src})
    assert not named, (
        f"this module names {named}, so its own literals are now credited as coverage of those "
        f"documents — derive the name at run time instead")
