#!/usr/bin/env python3
"""The ablation cache may skip work; it may never change an answer.

⛔⛔ A CACHE IN FRONT OF A CORRECTNESS GATE IS THE MOST DANGEROUS OBJECT IN THIS REPOSITORY, because
its failure mode is silence. The sweep it fronts is the only instrument that checks whether
`covered` is TRUE rather than merely recorded — on 2026-09-02 it found eleven sentences whose
credited witnesses never went red. A cache that turned one of those into a hit would hide exactly
the finding the gate exists for, and would do it without a symptom.

★ SO EVERY TEST HERE IS A WAY THE CACHE COULD LIE, DRIVEN RATHER THAN DESCRIBED. The key must move
when the sentence moves, when the witness set moves, and when a witness's SOURCE moves; anything it
cannot key on must be a MISS; and a malformed or unreadable entry must re-run rather than pass.

⚠ THE ONE INPUT NOT IN THE KEY IS THE ARTIFACT CORPUS, deliberately, and the argument is in the
module: a guard that stops binding because an artifact moved fails in the ordinary manuscripts
suite, which runs on every commit ahead of this. `test_an_artifact_change_is_caught_by_the_guards_own_
suite_not_by_this_cache` pins that reasoning to something executable rather than leaving it in prose.
"""

from __future__ import annotations

import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MANUSCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = _load("claim_ablation_cache")


def _tmpdir():
    import tempfile
    return tempfile.mkdtemp(prefix="ablation-cache-test-")

PAPER = "research/manuscripts/aso/fusion-junction-aso-journal-article.md"
W = ["test:test_a_quantity_written_as_a_word_is_bound_too.py"]


def test_the_key_moves_when_the_sentence_moves():
    a = C.key_for(PAPER, "the parent arm reads six transcripts", W)
    b = C.key_for(PAPER, "the parent arm reads ten transcripts", W)
    assert a and b and a != b, (
        "the key is blind to the sentence, so a perturbed sentence would hit the cache entry of the "
        "sentence it replaced — the cache answering a question it was not asked")


def test_the_key_moves_when_the_PAPER_moves():
    """⛔ FOUND BY MUTATION, NOT BY DESIGN — the first pass of this file did not assert it, and
    deleting the paper from the key left all sixteen tests green.

    ★ AND THE COLLISION IS REACHABLE RATHER THAN THEORETICAL. A witness set is usually per-document,
    which is what made the omission feel safe — but `test_a_quantity_written_as_a_word_is_bound_too`
    reads the ASO journal article AND the fusion-partner manuscript, so those two papers genuinely
    share a witness. An identical sentence under a shared witness set would then share one cache
    entry, and one paper's verdict would answer for the other's.
    """
    a = C.key_for(PAPER, "All five screens address hybridisation rather than cleavage", W)
    b = C.key_for("research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md",
                  "All five screens address hybridisation rather than cleavage", W)
    assert a and b and a != b, (
        "two papers sharing a witness and a sentence share a cache entry. The witness that makes "
        "this reachable is the one this cache's own soundness argument leans on.")


def test_the_key_moves_when_the_witness_set_moves():
    a = C.key_for(PAPER, "s", W)
    b = C.key_for(PAPER, "s", W + ["test:test_journal_article_numbers.py"])
    assert a and b and a != b, (
        "adding or losing a witness must be a miss: the recorded verdict was about a different set "
        "of guards, and a sentence that lost its only binding witness would keep its green")


def test_the_key_moves_when_a_witness_SOURCE_moves(tmp_path, monkeypatch):
    """⛔ THE ONE THAT MATTERS MOST. A guard can be widened, narrowed or broken without its NAME
    changing. Keying on the witness list alone would let a rewritten guard inherit the verdict of
    the guard it replaced — a cache certifying work that was never done."""
    src = tmp_path / "test_fake_guard.py"
    src.write_text("assert True\n", encoding="utf-8")
    monkeypatch.setattr(C, "_witness_sources_for", lambda w: [str(src)])
    a = C.key_for(PAPER, "s", ["test:test_fake_guard.py"])
    src.write_text("assert True  # widened\n", encoding="utf-8")
    b = C.key_for(PAPER, "s", ["test:test_fake_guard.py"])
    assert a and b and a != b, "the guard's source changed and the key did not"


def test_a_witness_whose_source_cannot_be_read_is_a_miss(monkeypatch):
    """Unreadable buys nothing — the direction every cap in this loop fails."""
    monkeypatch.setattr(C, "_witness_sources_for", lambda w: ["/nonexistent/guard.py"])
    assert C.key_for(PAPER, "s", W) is None
    assert C.witness_sources(W) is None


def test_a_partial_witness_set_never_yields_a_key(tmp_path, monkeypatch):
    """⛔ ONE UNREADABLE WITNESS POISONS THE WHOLE KEY, RATHER THAN BEING DROPPED FROM IT. A key
    built over the readable subset would hit whenever the unreadable guard changed — the cache
    silently narrowing what it is keyed on, which is the defect this repository met three times in
    one night at other levels."""
    good = tmp_path / "test_good.py"
    good.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(C, "_witness_path",
                        lambda w: str(good) if "good" in w else "/nonexistent/x.py")
    assert C.key_for(PAPER, "s", ["test:test_good.py", "test:test_missing.py"]) is None


def test_a_none_key_is_never_stored_and_never_hits():
    entries = {}
    C.record(entries, None, red=True, reason="r", witnesses=W)
    assert entries == {}, "a keyless result must not be stored under any key at all"
    assert C.lookup(entries, None) is None


@pytest.mark.parametrize("bad", [{}, {"red": "yes"}, {"red": None}, [], "green", 3, None])
def test_a_malformed_entry_is_a_miss_not_a_pass(bad):
    """⛔ THE FAIL-CLOSED DIRECTION. A corrupt cache must cost time, never correctness."""
    assert C.lookup({"k": bad}, "k") is None


def test_an_unreadable_cache_file_is_an_empty_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "CACHE", str(tmp_path / "does-not-exist.json"))
    assert C.load() == {}
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(C, "CACHE", str(p))
    assert C.load() == {}


def test_a_cache_written_under_another_schema_is_ignored(tmp_path, monkeypatch):
    """A future format change must not be read as the current one."""
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"_schema": "something-else/9", "entries": {"k": {"red": False}}}),
                 encoding="utf-8")
    monkeypatch.setattr(C, "CACHE", str(p))
    assert C.load() == {}


def test_a_recorded_red_stays_red_on_the_way_back():
    """The cache carries the verdict it was given, both ways. It has no opinion of its own."""
    entries = {}
    k = C.key_for(PAPER, "s", W)
    C.record(entries, k, red=False, reason="no guard noticed six->ten", witnesses=W,
             status="applied", quantity_kind="words")
    got = C.lookup(entries, k)
    assert got["red"] is False and "six->ten" in got["reason"], (
        "a BLIND sentence's verdict must survive the round trip — if the cache dropped or inverted "
        "it, the eleven blind sentences of 2026-09-02 would have come back covered")
    assert got["status"] == "applied" and got["quantity_kind"] == "words", (
        "the verdict's status rides with it; a caller reading `red` alone cannot tell a watched "
        "perturbation from one that never applied")
    C.record(entries, k, red=True, reason="went red", witnesses=W, status="applied")
    assert C.lookup(entries, k)["red"] is True


def test_a_verdict_recorded_without_a_status_is_a_miss():
    """⛔ ABSENCE READ AS EVIDENCE, ONE LAYER DOWN. `ablate` returns APPLIED — the sentence was
    perturbed and the witnesses watched — or NOT_APPLIED, meaning it could not be perturbed at all
    and the run measured NOTHING. Both come back with `red` False. An entry carrying `red` alone is
    therefore ambiguous, and the ambiguity resolves the dangerous way: a NOT_APPLIED returning as a
    hit reads as a clean, watched green. Entries from before the field existed are exactly that
    shape, so the miss is not defensive tidiness — it is the only reading that cannot invent a
    measurement.
    """
    k = C.key_for(PAPER, "s", W)
    legacy = {k: {"red": False, "reason": "recorded before `status` existed", "witnesses": sorted(W)}}
    assert C.lookup(legacy, k) is None, (
        "an entry with no recorded status must re-ablate, never come back as a watched green")
    C.record(legacy, k, red=False, reason="re-run", witnesses=W, status="not-applied")
    assert C.lookup(legacy, k)["status"] == "not-applied", (
        "and once a status IS recorded, NOT_APPLIED must survive as itself rather than flattening "
        "into the green it superficially resembles")


def test_an_artifact_change_is_caught_by_the_guards_own_suite_not_by_this_cache():
    """⛔ THE SOUNDNESS ARGUMENT FOR THE ONE INPUT LEFT OUT OF THE KEY, MADE EXECUTABLE.

    The corpus is deliberately absent from the key. That is only safe while a guard which stops
    binding because an artifact moved FAILS ON ITS OWN, in the manuscripts suite, ahead of the
    sweep. This asserts the guard used above is in that suite's directory and is collected by it —
    if guards ever moved somewhere the ordinary commit loop does not run, the omission would stop
    being sound and this goes red.
    """
    guard = os.path.join(HERE, "test_a_quantity_written_as_a_word_is_bound_too.py")
    assert os.path.exists(guard), (
        "the witness this cache's soundness argument leans on is not in research/manuscripts/tests, "
        "which is the directory the manuscripts suite runs. If guards move, re-argue the key.")
    src = open(guard, encoding="utf-8").read()
    assert "def test_" in src, "the witness must be collectable by pytest, or it never runs at all"


def test_the_cache_does_not_write_itself_while_a_suite_is_grading(tmp_path, monkeypatch):
    """⛔⛔ THE FILE IS TRACKED AND THE GATE THAT READS IT RUNS UNDER PYTEST, WHICH FORBIDS BOTH.

    `tracked_tree_guard.assert_tree_unchanged()` fails any pytest run that modifies a tracked file
    (AUT-PD-186). The ablation gate lives in the manuscripts suite, so a cache that recorded its
    verdicts while grading would redden every suite in which it missed — the accelerator failing the
    gate it accelerates, which is the least legible red this repository could produce.
    ★ So a write is an act somebody performs deliberately, and the default is to read.
    """
    p = tmp_path / "c.json"
    monkeypatch.setattr(C, "CACHE", str(p))
    monkeypatch.delenv(C.WRITE_ENV, raising=False)
    assert C.save({"k": {"red": True, "reason": "r", "witnesses": [], "status": "applied"}}) is False
    assert not p.exists(), (
        "an ungated save touched the tracked cache; under pytest that is a tracked-tree failure and "
        "under a grader it is a record editing itself")


def test_a_populate_run_does_write(tmp_path, monkeypatch):
    """⛔ AND THE GATE MUST NOT BE A SILENT REFUSAL EITHER — a cache that can never be filled is a
    57-minute sweep with extra machinery in front of it. The populate path is real and this drives
    it end to end, so a typo in the env name shows up here rather than as a permanently empty file
    nobody can explain."""
    p = tmp_path / "c.json"
    monkeypatch.setattr(C, "CACHE", str(p))
    monkeypatch.setenv(C.WRITE_ENV, "1")
    entries = {}
    k = C.key_for(PAPER, "s", W)
    C.record(entries, k, red=True, reason="six -> ten", witnesses=W, status="applied",
             quantity_kind="words")
    assert C.save(entries) is True
    assert C.lookup(C.load(), k)["red"] is True, (
        "a populated verdict must survive the file round trip, or the sweep re-runs everything "
        "forever while appearing to cache")


def test_only_the_exact_opt_in_enables_a_write(tmp_path, monkeypatch):
    """⚠ A truthy-looking value is not the opt-in. `CLAIM_ABLATION_CACHE_WRITE=0` and `=false` are
    the shapes a shell leaves lying around, and reading either as "yes" would put writes back inside
    grading runs by accident — the precise failure the gate above exists to prevent."""
    p = tmp_path / "c.json"
    monkeypatch.setattr(C, "CACHE", str(p))
    for value in ("0", "", "false", "no", "true", "yes"):
        monkeypatch.setenv(C.WRITE_ENV, value)
        assert C.writes_enabled() is (value == "1"), (
            "%r must not be read as the opt-in; only the literal '1' is" % (value,))


def test_every_witness_kind_the_sweep_emits_can_be_keyed():
    """⛔⛔ THE FAILURE THAT MADE THIS CACHE A NO-OP, AND IT WAS SILENT.

    `claim_ablation.guards_reading` emits three kinds of witness — `test:`, `pin:*` and
    `generator:` — and it appends `pin:*` to EVERY document. The first version of this module knew
    only `test:` and failed closed on everything else, so `witness_sources` returned None for every
    sentence in the repository, `key_for` returned None, and `record` dropped each verdict on the
    floor. Measured 2026-09-02: an 18-minute sweep ablated all 184 covered sentences correctly and
    wrote a cache holding ZERO entries. Nothing failed, nothing was empty in a way anyone would
    notice, and the only tell was the run printing its own entry count.

    ★ SO THE TWO MODULES ARE CHECKED AGAINST EACH OTHER RATHER THAN AGREED IN PROSE. This asks the
    real emitter for the real witness set of every floored document and requires that every one of
    them can be hashed. A new witness kind added to `guards_reading` reds this until the key knows
    how to read it — which is the correct direction: an unknown kind must make the cache COLDER,
    never blinder.
    """
    ca = _load("claim_ablation")
    cc = _load("claim_coverage")
    for paper in cc.COVERAGE_FLOOR:
        witnesses = ca.guards_reading(os.path.basename(paper))
        assert witnesses, "%s has no witnesses at all — the emitter, not the cache, is broken" % paper
        srcs = C.witness_sources(witnesses)
        assert srcs is not None, (
            "%s: at least one of its %d witnesses cannot be keyed, so EVERY sentence in that "
            "document is a permanent cache miss and the sweep pays full price forever. The "
            "unkeyable ones are %r" % (paper, len(witnesses),
                                       [w for w in witnesses if not C._witness_sources_for(w)]))
        assert len(srcs) == len(set(witnesses))


def test_repinning_a_figure_busts_the_key_even_though_no_guard_changed(monkeypatch):
    """⛔ `pin:*` IS TWO FILES AND THE SECOND ONE IS THE POINT. `lint_consistency.py` enforces the
    pins; `pinned-figures.json` IS the pins. Re-pinning a figure changes what that witness would say
    without changing a line of its code, and CLAUDE.md rule 1.3 makes re-pinning a routine act — so
    a key over the enforcer alone would hit across exactly the edit the pins exist to catch."""
    pins = os.path.join(MANUSCRIPTS, "pinned-figures.json")
    assert os.path.exists(pins), "the pins file moved; re-derive what `pin:*` is a function of"
    srcs = C._witness_sources_for("pin:*")
    assert pins in srcs and any(p.endswith("lint_consistency.py") for p in srcs), (
        "`pin:*` must be keyed on the pins AND their enforcer: %r" % (srcs,))
    # ⛔ THE PINS ARE MUTATED ON A COPY, NEVER IN THE TREE (AUT-PD-186 and CLAUDE.md §6). A test that
    # writes `pinned-figures.json` is one xdist worker away from another test reading an invented
    # figure, and a restore that loses leaves that value committed with the suite reporting a flake.
    import shutil
    tmp = _tmpdir()
    enforcer = os.path.join(tmp, "lint_consistency.py")
    copy = os.path.join(tmp, "pinned-figures.json")
    shutil.copyfile(os.path.join(MANUSCRIPTS, "lint_consistency.py"), enforcer)
    shutil.copyfile(pins, copy)
    monkeypatch.setattr(C, "_witness_sources_for", lambda w: [enforcer, copy])
    before = C.key_for(PAPER, "s", ["pin:*"])
    with open(copy, "ab") as fh:
        fh.write(b"\n")
    assert C.key_for(PAPER, "s", ["pin:*"]) != before, (
        "re-pinning a figure left the key unchanged — a cached verdict would then survive the one "
        "edit `pinned-figures.json` exists to make visible")
    # ⛔ AND THE ENFORCER'S OWN SOURCE COUNTS TOO, or a rewritten `lint_consistency` inherits the
    # verdicts of the one it replaced.
    mid = C.key_for(PAPER, "s", ["pin:*"])
    with open(enforcer, "ab") as fh:
        fh.write(b"\n")
    assert C.key_for(PAPER, "s", ["pin:*"]) != mid


def test_an_unknown_witness_kind_is_a_miss_rather_than_a_guess():
    """A kind nobody has taught this module about must not be keyed on nothing and hit forever."""
    assert C._witness_sources_for("oracle:something") is None
    assert C._witness_sources_for("") is None
    assert C._witness_sources_for(None) is None
    assert C.witness_sources(["test:test_the_ablation_cache_cannot_launder_a_red.py",
                              "oracle:something"]) is None, (
        "one unkeyable witness must poison the whole set — a key over the readable subset would hit "
        "whenever the unreadable one changed")
