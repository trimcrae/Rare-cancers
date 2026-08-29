#!/usr/bin/env python3
"""`emc_fusion_partner_pooling.py --check` must actually REFUSE a drifted artifact.

⛔ WHY THIS FILE EXISTS, AND WHY IT REFUSES TO MOCK ANYTHING.
Until 2026-08-08 that module parsed no arguments at all: `--check` was accepted by the shell,
ignored by the script, and the artifact was regenerated and OVERWRITTEN whatever you passed, with
an unconditional exit 0. So `emc-fusion-partner-pooling.json`'s own `_do_not_hand_edit` banner --
which tells every reader that the numbers in it are computed rather than typed -- was unenforced,
and **a hand edit to a pooled clinical event count persisted with nothing able to say so.** That
artifact is nothing but clinical event counts: partner-stratified deaths, recurrences and
metastases pooled under `systems/POLICY-evidence.md`. ⚠ This is the SECOND instance of the same
defect found on the same day; the first was `emc_systemic_therapy_pooling.py`, and both the repair
and this test deliberately follow that file's idiom rather than inventing a second one.

The repair is a verify mode; a verify mode's own failure mode is regenerating its reference and
therefore being unable to fail. That is a broken guard which no-ops into the previous behaviour and
produces NO SYMPTOM -- CLAUDE.md §6 records exactly this shape (a census keep-alive whose every
test monkeypatched the seam, so a lookup that never worked looked fine for a full session).
**Mock the thing under test and you test the mock.** Therefore every test below:

  * calls the REAL `main(["--check"])` on the REAL committed artifact at its REAL path,
  * perturbs that file ON DISK and asserts a non-zero return,
  * restores the exact original bytes in a `finally`, and
  * asserts the restoration, so a crashed test cannot leave a corrupted clinical artifact behind.

The perturbations are the edits that would actually matter: a pooled event count, a Wilson bound,
a per-cohort stratum, the size defeater that every prognostic figure must travel with, and the
`_do_not_hand_edit` promise itself.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, MANUSCRIPTS)

import emc_fusion_partner_pooling as P  # noqa: E402

import pytest

#: ⛔⛔ THE PERTURBATIONS BELOW RUN ON A COPY, NEVER ON THE COMMITTED ARTIFACT.
#:
#: ⚠ MEASURED 2026-08-29, on the sibling `test_endpoint_producers_check.py`, which had this exact
#: shape: mutate the LIVE tracked artifact, restore it in a `finally`. That is safe only while
#: nothing else reads the file, and the manuscripts suite runs under `xdist`. Reproduced 3 of 3
#: runs at `-n 3`: another worker read the artifact mid-window and raised `KeyError` on the section
#: a tamper test had just deleted, and a module-scoped fixture reading the same file took its WHOLE
#: module down as a collection ERROR. The parametrized cases also raced each other, so a restore
#: can lose — and one reproduction left `"conditions_placed": 45` against the committed 44 in the
#: working tree, a value invented by a tamper test, with the suite reporting only a flake. A
#: `git add -A` on top of that commits a falsified number.
#:
#: ★ `_artifact` copies the committed file to `tmp_path` and points the producer's `OUT` at the
#: copy. Every producer's `--check` reads `OUT` and nothing else, so what is under test does not
#: change; what changes is that the live tree is never written to, and no restore has to win a race.
#: The redirection is self-verifying: `--check` on an unmutated artifact returns 0, and every
#: assertion below demands non-zero.


@pytest.fixture(autouse=True)
def _artifact(tmp_path, monkeypatch):
    """Redirect the producer's OUT at a private copy for the duration of each test."""
    copy = tmp_path / os.path.basename(P.OUT)
    shutil.copyfile(P.OUT, copy)
    monkeypatch.setattr(P, "OUT", str(copy))
    return str(copy)


def _original_bytes():
    with open(P.OUT, "rb") as fh:
        return fh.read()


def _write(doc):
    with open(P.OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=True)
        fh.write("\n")


def _perturb_and_assert_refusal(mutate, what):
    """Apply `mutate` to the committed artifact, assert `--check` returns non-zero, restore."""
    original = _original_bytes()
    try:
        doc = json.loads(original.decode("utf-8"))
        mutate(doc)
        _write(doc)
        rc = P.main(["--check"])
        assert rc != 0, (
            "--check returned %r after %s was perturbed. A verify mode that accepts a drifted "
            "clinical artifact is the defect it was written to remove." % (rc, what))
    finally:
        with open(P.OUT, "wb") as fh:
            fh.write(original)
    assert _original_bytes() == original, "the artifact was not restored byte-for-byte"


def test_the_committed_artifact_currently_reproduces():
    """The precondition. If this fails, every refusal below proves nothing."""
    assert P.main(["--check"]) == 0, (
        "the committed artifact does not re-derive from the generator's counts -- regenerate it "
        "before reading anything else in this file as a result")


def test_check_refuses_a_hand_edited_pooled_event_count():
    """The exact edit that used to persist undetected, on the headline prognostic contrast."""
    def mutate(doc):
        arm = doc["analyses"]["B_outcome_by_partner"]["disease_specific_death"]["taf15_arm"]
        arm["events"] = arm["events"] - 1
    _perturb_and_assert_refusal(mutate, "the pooled TAF15 disease-specific-death event count")


def test_check_refuses_a_hand_edited_confidence_bound():
    """A widened or narrowed interval is a claim about uncertainty and must not be hand-settable."""
    def mutate(doc):
        arm = doc["analyses"]["B_outcome_by_partner"]["disease_specific_death"]["comparator_arm"]
        arm["ci95_hi_percent"] = arm["ci95_hi_percent"] + 10.0
    _perturb_and_assert_refusal(mutate, "the pooled EWSR1 arm's Wilson 95% upper bound")


def test_check_refuses_a_hand_edited_per_cohort_stratum():
    """The INPUT counts, not only the pooled outputs -- POLICY-evidence.md §2.1 rests on these."""
    def mutate(doc):
        for c in doc["cohorts"]:
            if c["id"] == "huang-2023-outcome":
                c["strata"]["TAF15::NR4A3"]["disease_specific_death"]["events"] = 2
                return
        raise AssertionError("huang-2023-outcome is not in the artifact's cohorts")
    _perturb_and_assert_refusal(mutate, "Huang 2023's TAF15 disease-specific-death stratum")


def test_check_refuses_deletion_of_the_size_defeater():
    """⛔ The defeater is not decoration: the crude prognostic magnitude may not be quoted without it.

    Huang 2023's own multivariable analysis says the partner is NOT independent of tumour size, and
    every pooled contrast in this artifact carries that sentence in its `defeater` field. Silently
    dropping it would leave a quotable magnitude with its refutation removed, which is the single
    most damaging hand edit available in this file.
    """
    def mutate(doc):
        doc["analyses"]["B_outcome_by_partner"]["disease_specific_death"].pop("defeater")
    _perturb_and_assert_refusal(mutate, "the size defeater on the pooled death contrast")


def test_check_refuses_an_edit_to_the_do_not_hand_edit_promise_itself():
    """⛔ The note is part of the artifact and is compared like everything else.

    `_do_not_hand_edit` starts with an underscore, and the obvious way to write `_comparable()` --
    skip underscore-prefixed keys as metadata -- would exempt the very sentence that tells a reader
    the file is generated. A guard that lets you quietly delete its own warning label is worse than
    none.
    """
    def mutate(doc):
        doc["_do_not_hand_edit"] = "edit freely"
    _perturb_and_assert_refusal(mutate, "the _do_not_hand_edit note")


def test_check_does_not_write_the_artifact():
    """`--check` must be read-only: a verify mode that regenerates cannot fail.

    ⭐ THIS IS THE TEST THAT DISCRIMINATES AGAINST THE DEFECT BEING REPLACED. The old behaviour
    would REWRITE the perturbed file and return 0. Return code alone does not separate the two --
    a regenerating check returns 0 because it just made the file match. Only the bytes do.
    """
    original = _original_bytes()
    try:
        doc = json.loads(original.decode("utf-8"))
        doc["analyses"]["B_outcome_by_partner"]["disease_specific_death"]["taf15_arm"]["events"] = 1
        _write(doc)
        perturbed = _original_bytes()
        rc = P.main(["--check"])
        assert rc != 0
        assert _original_bytes() == perturbed, (
            "--check MODIFIED the artifact. A verify mode that regenerates its own reference "
            "compares the generator against itself and can never fail.")
    finally:
        with open(P.OUT, "wb") as fh:
            fh.write(original)


def test_check_reports_a_missing_artifact_rather_than_creating_one():
    """An absent artifact is a failure, never a silent regeneration."""
    original = _original_bytes()
    try:
        os.remove(P.OUT)
        assert P.main(["--check"]) != 0
        assert not os.path.exists(P.OUT), "--check created the artifact it was asked to verify"
    finally:
        with open(P.OUT, "wb") as fh:
            fh.write(original)


def test_the_entrypoint_propagates_the_exit_code():
    """⛔ A verify mode whose failure cannot reach the shell is wired into nothing.

    The module's `__main__` block must be `sys.exit(main())`, not a bare `main()`. The bare form is
    exactly what the defect had, and it is invisible to every test that calls `main()` directly --
    so this reads the source, which is the only place the difference exists.
    """
    src = open(P.__file__, encoding="utf-8").read()
    tail = src[src.index('if __name__ == "__main__":'):]
    assert "sys.exit(main())" in tail, (
        "the entrypoint does not propagate main()'s return code; a --check that returns 1 would "
        "still exit 0 and no CI step could fail on it")


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
