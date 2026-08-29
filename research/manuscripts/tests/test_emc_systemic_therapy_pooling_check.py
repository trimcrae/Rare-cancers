#!/usr/bin/env python3
"""`emc_systemic_therapy_pooling.py --check` must actually REFUSE a drifted artifact.

⛔ WHY THIS FILE EXISTS, AND WHY IT REFUSES TO MOCK ANYTHING.
Until 2026-08-08 that module parsed no arguments: `--check` was swallowed, the artifact was
overwritten, and the process exited 0. The module's own `_do_not_hand_edit` note promised that a
hand edit "will be silently overwritten" -- true only of a run somebody remembered to make, and
nothing in CI made one. So a hand edit to a POOLED CLINICAL PROPORTION persisted undetected, in the
one artifact in this repository whose numbers are patient-facing.

The repair is a verify mode; the repair's own failure mode is a verify mode that regenerates its
reference and therefore cannot fail. That is a broken guard that no-ops into the previous behaviour
and produces NO SYMPTOM -- CLAUDE.md 6 records exactly this shape (a census keep-alive whose every
test monkeypatched the seam, so a lookup that never worked looked fine for a full session).
**Mock the thing under test and you test the mock.** Therefore every test below:

  * calls the REAL `main(["--check"])` on the REAL committed artifact at its REAL path,
  * perturbs that file ON DISK and asserts a non-zero return,
  * restores the exact original bytes in a `finally`, and
  * asserts the restoration, so a crashed test cannot leave a corrupted clinical artifact behind.

The perturbations are chosen to be the edits that actually matter: a pooled proportion, a confidence
bound, an integer event count, and the `_do_not_hand_edit` promise itself.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, MANUSCRIPTS)

import emc_systemic_therapy_pooling as P  # noqa: E402

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
        json.dump(doc, fh, indent=1, ensure_ascii=True)
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


def test_check_refuses_a_hand_edited_pooled_proportion():
    """The exact edit that used to persist undetected: a pooled clinical proportion."""
    def mutate(doc):
        pool = doc["analyses"]["A1_objective_response_prospective"]["pool"]
        assert pool["proportion_pct"] != 99.9, "pick a value the artifact does not already carry"
        pool["proportion_pct"] = 99.9
    _perturb_and_assert_refusal(mutate, "A1's pooled objective-response proportion")


def test_check_refuses_a_hand_edited_confidence_bound():
    """A widened or narrowed interval is a claim about uncertainty and must not be hand-settable."""
    def mutate(doc):
        pool = doc["analyses"]["A4_disease_control"]["pool"]
        lo, hi = pool["wilson95_pct"]
        pool["wilson95_pct"] = [lo, hi + 10.0]
    _perturb_and_assert_refusal(mutate, "A4's Wilson 95% upper bound")


def test_check_refuses_a_hand_edited_integer_count():
    """The counts are the inputs the whole evidence contract rests on (POLICY-evidence 2.1)."""
    def mutate(doc):
        pool = doc["analyses"]["A2_objective_response_cytotoxic_chemotherapy"]["pool"]
        pool["events"] = pool["events"] + 1
    _perturb_and_assert_refusal(mutate, "A2's pooled event count")


def test_check_refuses_an_edit_to_the_do_not_hand_edit_promise_itself():
    """⛔ The note is part of the artifact and is compared like everything else.

    `_do_not_hand_edit` starts with an underscore, and the obvious way to write `_comparable()`
    -- skip underscore-prefixed keys as metadata -- would exempt the very sentence that tells a
    reader the file is generated. A guard that lets you quietly delete its own warning label is
    worse than none.
    """
    def mutate(doc):
        doc["_do_not_hand_edit"] = "edit freely"
    _perturb_and_assert_refusal(mutate, "the _do_not_hand_edit note")


def test_check_does_not_write_the_artifact():
    """`--check` must be read-only: a verify mode that regenerates cannot fail.

    This is the discriminating test between the repair and the defect it replaces. The old
    behaviour would REWRITE the perturbed file and return 0; if `--check` ever regains a write
    path, the mtime/bytes assertion below fires even when the return code happens to be right.
    """
    original = _original_bytes()
    try:
        doc = json.loads(original.decode("utf-8"))
        doc["analyses"]["A1_objective_response_prospective"]["pool"]["proportion_pct"] = 99.9
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
