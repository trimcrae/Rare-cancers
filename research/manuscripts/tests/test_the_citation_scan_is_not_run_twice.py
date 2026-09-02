"""Gate 6 must walk the corpus ONCE, and its redaction must still blind a failed fetch.

⛔⛔ WHY THIS FILE EXISTS: THE COMMIT LOOP'S SECOND-BIGGEST COST WAS A FUNCTION CALLED TWICE.
Measured 2026-09-02 with cProfile over one `lint_citations.py` run: 101.6 s, of which
`_scan` — the regex walk of every tracked prose and artifact file — accounted for 95.4 s in **two
disjoint halves of 47.6 s each**. `lint_citations.check()` computed `survey()`, then handed off to
`lint_citation_types.check()`, whose `retraction_sweep()` computed the identical `survey()` again.
Wall clock on this box: **72.4 s before, 37.7 s after**, with byte-identical output.

⛔ AND THE REASON A GUARD IS NEEDED RATHER THAN A COMMENT: NOTHING ABOUT THE SLOW SHAPE WAS VISIBLE.
Both spellings are green, both print the same numbers, and the only symptom is minutes of wall clock
that CLAUDE.md §6 records this repository paying for over and over. `_types.check()` and
`_types.check(prose=prose)` differ by one keyword; a future edit that drops it regresses the loop by
half a gate and no existing test notices. That is the `subagent_width` shape — a rule governed by
nothing — which this repository has already paid for twice.

⛔ THE SECOND HALF IS A CORRECTNESS OBLIGATION, NOT A SPEED ONE. `_redact_failed_fetches` used to
return a freshly-built copy of everything it walked; it now returns the INPUT NODE when nothing
needed redacting. That is only sound while (a) the value is equal to what a full rebuild produces
and (b) a failed fetch is still blinded. AUT-PD-038 is what (b) is for: a DOI once anchored on three
straight 403s, a gate meant to establish that somebody retrieved a paper satisfied by three records
saying nobody could. Both are asserted here against a reference implementation rather than trusted.
"""
import copy
import importlib.util
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MANUSCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lc = _load("lint_citations")


# --------------------------------------------------------------------------------------------
# one scan per gate run
# --------------------------------------------------------------------------------------------


def test_the_type_guard_is_handed_the_scan_instead_of_repeating_it(monkeypatch):
    """`lint_citations.check()` must reach `survey()` exactly once, not once per guard.

    ⭐ THE CORPUS IS EMPTIED RATHER THAN SCANNED, SO THIS COSTS MILLISECONDS. `_tracked()` is the
    one place both linters ask what files exist, so stubbing it to `[]` makes every scan trivial
    while leaving the CALL GRAPH — which is the entire property under test — untouched.
    ⛔ AND `sys.modules` IS SEEDED DELIBERATELY. `lint_citation_types` does `import lint_citations
    as LC` at module level, and `check()` loads it by path at call time; without this line that
    import builds a SECOND, uninstrumented copy of this module and the counter would read 1 whether
    or not the duplicate scan happened — a test that passes for the wrong reason.
    """
    monkeypatch.setattr(lc, "_tracked", lambda: [])
    monkeypatch.setitem(sys.modules, "lint_citations", lc)
    calls = []
    real = lc.survey
    monkeypatch.setattr(lc, "survey", lambda: (calls.append(1), real())[1])

    assert lc.check() == 0, "an empty corpus must be green; a red here means the stub, not the gate"
    assert len(calls) == 1, (
        "gate 6 walked the corpus %d times. `lint_citations.check()` must pass the prose half it "
        "already holds into `lint_citation_types.check(prose=...)`; recomputing it is 21 s of every "
        "commit for an answer already in hand." % len(calls))


def test_the_sweep_still_computes_the_scan_when_nobody_hands_it_one(monkeypatch):
    """⛔ `prose=None` IS THE STANDALONE PATH AND IT MUST NOT HAVE BECOME A SILENT EMPTY SWEEP.

    `python3 research/manuscripts/lint_citation_types.py` and every test that drives that module
    directly pass nothing. If the parameter's default ever stopped meaning "compute it yourself",
    the repository-wide retraction sweep would report `0 prose identifier(s)` — a coverage number
    that reads like a clean tree and measures nothing, which is the exact defect `retraction_sweep`
    was written to replace.
    """
    lct = _load("lint_citation_types")
    calls = []
    real = lct.LC.survey
    monkeypatch.setattr(lct.LC, "survey", lambda: (calls.append(1), real())[1])
    monkeypatch.setattr(lct.LC, "_tracked", lambda: [])

    hits, not_swept, cov = lct.retraction_sweep()
    assert calls, "with no prose handed in, the sweep must go and get it"
    assert cov is not None, "the sweep artifact must be readable, or this asserts nothing"


def test_a_prose_dict_handed_in_is_the_corpus_the_sweep_reports(monkeypatch):
    """The coverage line must describe the corpus actually swept, whatever was passed.

    ⚠ This is the guard on the parameter's one abuse: handing the sweep a NARROWED dict would shrink
    its reach while the printed total went on sounding repository-wide. It cannot be prevented by
    typing, so it is made visible — `cov["total"]` is derived from the argument, so a caller that
    narrows the corpus also narrows the number a reader sees.
    """
    lct = _load("lint_citation_types")
    hits, not_swept, cov = lct.retraction_sweep({"PMID": {"36062197": {"a.md"}}})
    assert cov["total"] == 1, "the coverage total must count the corpus it was given, not a memory"
    assert [h[1] for h in hits] == ["36062197"], (
        "the sweep must still find a retraction in a corpus handed to it — otherwise passing prose "
        "in disabled the guard rather than speeding it up")


# --------------------------------------------------------------------------------------------
# the redaction still redacts
# --------------------------------------------------------------------------------------------


def _rebuild(node):
    """The pre-optimisation implementation: always allocate. The reference, kept deliberately dumb."""
    if lc._is_fetch_record(node) and not lc._fetch_succeeded(node):
        return {"url": None, "status": node.get("status")}
    if isinstance(node, dict):
        return {k: _rebuild(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_rebuild(v) for v in node]
    return node


_FAILED = {"url": "https://doi.org/10.1000/x", "status": 403,
           "attempts": [{"n": 1, "status": 403}],
           "text": "Access denied. PMID 36062197 DOI 10.1000/fabricated"}
_OK = {"url": "https://doi.org/10.1000/y", "status": 200,
       "attempts": [{"n": 1, "status": 200}],
       "text": "PMID 40646688 was retrieved"}


def test_a_failed_fetch_is_still_blinded():
    """⛔ AUT-PD-038, and it is the whole reason this function exists. A 403's body must not anchor."""
    out = lc._redact_failed_fetches({"records": [_FAILED]})
    text = json.dumps(out)
    assert "36062197" not in text and "10.1000/fabricated" not in text, (
        "a failed fetch's body reached the scanner — an identifier nobody retrieved would now count "
        "as anchored, which is the 2026-08-27 defect")
    assert out is not {"records": [_FAILED]}
    assert out["records"][0] == {"url": None, "status": 403}


def test_a_successful_fetch_is_untouched_and_still_anchors():
    out = lc._redact_failed_fetches({"records": [_OK]})
    assert "40646688" in json.dumps(out), "a real retrieval must go on anchoring what it retrieved"


@pytest.mark.parametrize("doc", [
    {"records": [_FAILED, _OK]},
    {"a": {"b": {"c": [_FAILED]}}, "d": [1, 2, {"e": _OK}]},
    {"nothing": "to redact", "n": [1, 2, 3], "deep": {"deeper": {"deepest": None}}},
    [],
    {},
    {"attempts": 4, "url": "not a record — status missing"},
])
def test_the_fast_path_returns_exactly_what_a_full_rebuild_would(doc):
    """Equality against the reference, on documents with and without anything to redact."""
    assert lc._redact_failed_fetches(copy.deepcopy(doc)) == _rebuild(copy.deepcopy(doc))


def test_a_document_with_nothing_to_redact_is_returned_unchanged_by_identity():
    """⭐ THE OPTIMISATION ITSELF, PINNED. Without this, a rewrite could go back to copying 13 M
    nodes per gate run and every other test here would stay green."""
    doc = {"a": [1, {"b": "c"}], "d": _OK}
    assert lc._redact_failed_fetches(doc) is doc, (
        "an untouched document must come back as the same object; rebuilding it was 17.6 s of a "
        "101.6 s profiled gate-6 run")


def test_a_document_with_something_to_redact_is_not_the_same_object():
    """⛔ THE DANGEROUS DIRECTION: returning the input when a redaction WAS needed would hand the
    scanner the unredacted document while every equality test above still passed on other inputs."""
    doc = {"a": [1, {"b": "c"}], "d": _FAILED}
    out = lc._redact_failed_fetches(doc)
    assert out is not doc
    assert doc["d"]["text"], "the input must not be mutated in place — it is a caller's document"
    assert "36062197" not in json.dumps(out)


def test_the_real_corpus_scans_identically_either_way(tmp_path):
    """The equality holds on the repository's own artifacts, not only on fixtures.

    ⚠ Sampled rather than exhaustive, and named as such: the tracked `.json` corpus is thousands of
    files and this runs in the commit loop. The fixtures above carry the shapes; this carries the
    evidence that real documents contain no shape they missed.
    """
    import subprocess
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "*.json"], capture_output=True, text=True)
    rels = [p for p in r.stdout.split("\n") if p][:120]
    assert rels, "no tracked .json found — this test would assert nothing"
    for rel in rels:
        try:
            parsed = json.loads(open(os.path.join(ROOT, rel), encoding="utf-8").read())
        except (ValueError, OSError):
            continue
        assert (json.dumps(lc._redact_failed_fetches(copy.deepcopy(parsed)), ensure_ascii=False)
                == json.dumps(_rebuild(copy.deepcopy(parsed)), ensure_ascii=False)), rel
