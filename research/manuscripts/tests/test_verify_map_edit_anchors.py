"""`three-row-audit-map-edits.json` must stay routable, and its verifier must not be the retired predicate.

⛔ WHY THIS FILE EXISTS (2026-08-07). `research/manuscripts/verify_map_edit_anchors.py` had been red for
days -- 13 edits x 2 refs, 26 FAILs -- and **no test and no workflow ran it**, so nothing in the repository
could say so. It asserted `count(anchor) == 1 and count(current_text) == 1`, the predicate the roadmap
records being retired twice already (`test_linker_library_canonical` and `test_nr4a3_5bt`, both 2026-08-03):
that shape goes red at the moment a routed edit is APPLIED, because applying an edit is what removes its
`current_text`. Twelve of the thirteen edits had landed. Its only stable green state was "nobody applied
anything".

Two properties are asserted here, and the second is the one that would have caught the rot:

  1. every edit in the block resolves to an ACCOUNTED state (`OK`, `APPLIED` or `UNANCHORED`) against the
     file it actually names -- `NOT_FOUND` and `AMBIGUOUS` stay failures;
  2. the verifier SCRIPT reaches the same verdict, exercised end to end rather than reimplemented here.
     Mock the thing under test and you test the mock.
"""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))
ARTIFACT = os.path.join(MANUSCRIPTS, "degrader", "three-row-audit-map-edits.json")
SCRIPT = os.path.join(MANUSCRIPTS, "verify_map_edit_anchors.py")

sys.path.insert(0, os.path.join(ROOT, "research", "modalities"))
import map_edit_anchors as mea  # noqa: E402

ACCOUNTED = {"OK", "APPLIED", "UNANCHORED"}


@pytest.fixture(scope="module")
def edits():
    return json.load(open(ARTIFACT, encoding="utf-8"))["map_edits_required"]


def test_every_edit_resolves_against_the_file_it_names(edits):
    """⚠ AGAINST ITS OWN `file`, WHICH IS HALF THE POINT. Three of the thirteen edits target
    `map-merge-inventory.md` and `nr4a3-degrader-paper.md`; resolving the block against the roadmap alone
    reports all three as dead anchors when all three have landed."""
    dead = []
    for e in edits:
        path = os.path.join(ROOT, e["file"])
        assert os.path.exists(path), "%s names a file that does not exist: %s" % (e["id"], e["file"])
        got, _ = mea.verify([e], path)
        st = got[0]["anchor_status"]
        if st not in ACCOUNTED:
            dead.append((e["id"], st, e.get("section")))
    assert not dead, (
        "these routed edits are neither applicable nor landed -- relocate the anchor to text that "
        "exists, do not delete the edit and do not loosen this check: %r" % (dead,))


def test_an_unanchored_edit_still_says_where_it_goes(edits):
    """⛔ `current_text: null` IS A CONTRACT, NOT AN ESCAPE HATCH. It means the value must be REGENERATED
    rather than applied (a derived total may never be typed -- CLAUDE.md rule 1). An edit that claims it
    and then does not say where it lands is unroutable, and would let this check be satisfied by deleting
    anchors rather than repairing them."""
    for e in edits:
        if e.get("current_text") is None:
            assert e.get("where_it_goes"), (
                "%s is unanchored by contract but does not say where it goes" % e["id"])
            assert e.get("anchor"), "%s is unanchored but carries no human locator either" % e["id"]


def test_a_relocated_anchor_actually_locates_something(edits):
    """A relocated anchor that matches nothing is the original defect wearing a fresh string, and a
    relocated anchor that matches twice sends a mechanical apply to the wrong place."""
    bodies = {}
    for e in edits:
        path = os.path.join(ROOT, e["file"])
        body = bodies.setdefault(path, open(path, encoding="utf-8").read())
        anchor = e.get("anchor")
        if not isinstance(anchor, str) or not anchor:
            continue
        n = body.count(anchor)
        # An anchor is a human locator; several emitters write it as a description rather than as
        # searchable text, so 0 is tolerated ONLY when `current_text` is present to locate the edit.
        if e.get("current_text") is None:
            assert n == 1, ("%s is unanchored, so its `anchor` is the ONLY locator it has, and it "
                            "occurs %d times in %s" % (e["id"], n, e["file"]))
        else:
            assert n <= 1, "%s: anchor is ambiguous (%d occurrences) in %s" % (e["id"], n, e["file"])


def test_the_verifier_script_itself_is_green_and_is_not_the_retired_predicate():
    """⛔ THE SCRIPT, NOT A REIMPLEMENTATION OF IT. This is the assertion that would have caught the rot:
    the module was correct in the tests that never imported it and wrong in the file that shipped."""
    src = open(SCRIPT, encoding="utf-8").read()
    assert "map_edit_anchors" in src, (
        "the verifier must use the shared discriminator, not reimplement an anchor check -- "
        "`map_edit_anchors.verify()` is its one home")
    r = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, "verify_map_edit_anchors.py is RED:\n%s\n%s" % (r.stdout[-3000:], r.stderr[-2000:])
    assert "0 unresolved" in r.stdout, r.stdout[-2000:]


def test_the_retired_predicate_is_not_reintroduced():
    """`count(current_text) == 1` as a health check is the defect, by name. It has been fixed three times
    in this repository; this is what stops a fourth."""
    src = open(SCRIPT, encoding="utf-8").read()
    for banned in ("n_anchor == 1 and n_cur == 1", "n_cur == 1 and n_anchor == 1"):
        assert banned not in src, (
            "the retired predicate is back: a guard shaped this way goes red the moment routing "
            "SUCCEEDS, so its only stable green state is 'nobody applied anything'")


def test_the_module_import_is_real():
    """Guards the path plumbing above: if `map_edit_anchors` ever stops importing from here, every
    assertion in this file would collapse into a collection error rather than a diagnosis."""
    assert importlib.util.find_spec("map_edit_anchors") is not None
    assert hasattr(mea, "verify")
