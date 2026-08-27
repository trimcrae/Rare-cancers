"""Mutation tests for the single-slot artifact identity guard.

⛔⛔ A GUARD IS WORTH WHAT ITS MUTATION TEST PROVES, AND THE FIRST MUTATION HERE IS THE INCIDENT.
`atr-hrd-sarcoma-series.json` held GSE28866's data under GSE299349's name from 2026-08-07 (commit
325258cb8) to 2026-08-27 (a8caba9) — twenty days — while `atr_hrd_sarcoma_series.py --check` printed
OK on every run, because that check only asks whether the artifact re-derives from the cache sitting
beside it and both had been replaced together. Test 1 below puts GSE28866 back in the slot on a COPY
and requires the guard to go red, attributed to the artifact rather than to anything else.

⛔ EVERY MUTATION RUNS ON A COPY OF THE TREE, NEVER ON THE TREE (research-loop §3, 2026-08-27: a
seat's mutation window let thirteen inverted claims reach origin/main; and 2026-08-27 again, when
mutating this module's own refusal made an earlier test run the real fetch half and rewrite the
committed artifact). Nothing here opens a file under the repository for writing.

⛔ AND EVERY MUTATION ASSERTS IT LANDED BEFORE ANY RESULT IS READ. A `replace()` that matched
nothing produces a green run over unmutated data, which proves the opposite of what it appears to
prove — so `_mutate` fails the test on the wrong occurrence count rather than on the guard's verdict.
"""

import copy
import json
import os
import shutil
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import single_slot_identity as G          # noqa: E402
import atr_hrd_sarcoma_series as M        # noqa: E402


SLOT = G.SLOTS[0]
ARTIFACT = SLOT["artifact"]
INPUTS = SLOT["caches"][0]["path"]
QUANT = SLOT["caches"][1]["path"]
PRODUCER = SLOT["producer"]
SMAP = SLOT["systems_map"]
DOC = SLOT["declared_by"][0]
FIXTURE = [PRODUCER, ARTIFACT, INPUTS, QUANT, SMAP, DOC]


@pytest.fixture
def tree(tmp_path):
    """A COPY of exactly the files the guard reads, at their real relative paths."""
    root = tmp_path / "repo"
    for rel in FIXTURE:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(os.path.join(G.REPO, rel), dst)
    return root


def run(root):
    return G.check_slot(copy.deepcopy(SLOT), str(root))


def _mutate(root, rel, old, new, expect=1):
    """Text mutation that FAILS THE TEST unless it actually applied `expect` times."""
    p = root / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == expect, (
        f"mutation did not land: {old!r} occurs {s.count(old)} times in {rel}, expected {expect}. "
        f"A mutation that silently fails to apply produces a green run that proves nothing.")
    p.write_text(s.replace(old, new), encoding="utf-8")


def _mutate_json(root, rel, fn):
    """JSON mutation. `fn(obj)` must return a truthy 'this changed something' witness."""
    p = root / rel
    obj = json.loads(p.read_text(encoding="utf-8"))
    landed = fn(obj)
    assert landed, f"mutation did not land in {rel}"
    p.write_text(json.dumps(obj, indent=1, sort_keys=True), encoding="utf-8")


def kinds(fails):
    return {f.split(":", 1)[0] for f in fails}


# =============================================================================================
# 0 — the control. If this is not green, every red below proves nothing about the mutation.
# =============================================================================================
def test_the_unmutated_copy_is_green(tree):
    assert run(tree) == []


def test_the_real_tree_is_green():
    """The guard must be green on the repository as committed, or it is not a gate, it is noise."""
    assert G.check_slot(SLOT) == []


# =============================================================================================
# 1-2 — THE INCIDENT, in both of the places it lived.
# =============================================================================================
def test_1_the_original_incident_the_slot_holds_another_series(tree):
    """325258cb8: `--series GSE28866` wrote another series into this artifact's fixed path."""
    _mutate(tree, ARTIFACT, '"series": "GSE299349"', '"series": "GSE28866"')
    fails = run(tree)
    assert "B/artifact" in kinds(fails), fails
    assert any("GSE28866" in f and "GSE299349" in f for f in fails), fails


def test_2_the_inputs_cache_is_for_another_series(tree):
    """The upstream half, and the one a re-derive check structurally cannot see: `--check`
    reproduces the artifact FROM this file, so a cache for GSE28866 makes a GSE28866 artifact
    reproduce byte-identically and report OK."""
    _mutate(tree, INPUTS, '"series": "GSE299349"', '"series": "GSE28866"')
    fails = run(tree)
    assert "C/cache" in kinds(fails), fails


def test_3_the_producer_constant_drifts_away_from_everything_else(tree):
    """The other direction: the module is re-pointed and the committed records are not."""
    _mutate(tree, PRODUCER, 'SERIES = "GSE299349"', 'SERIES = "GSE28866"')
    fails = run(tree)
    assert {"B/artifact", "C/cache"} <= kinds(fails), fails


def test_4_a_quant_cache_fetched_for_a_different_series(tree):
    """The quant cache names no accession at all — it is keyed by GSM — so it is bound by
    membership. A cache from another series shares no sample with this artifact."""
    def swap(obj):
        old = obj["per_sample"]
        obj["per_sample"] = {f"GSM00000{i}": v for i, v in enumerate(old.values())}
        return set(obj["per_sample"]) != set(old)
    _mutate_json(tree, QUANT, swap)
    fails = run(tree)
    assert "D/members" in kinds(fails), fails


def test_5_an_emptied_quant_cache_binds_nothing_and_says_so(tree):
    """⛔ An empty member set must not read as 'no mismatch found'. A guard whose subject vanished
    reports UNMEASURED, never OK (CLAUDE.md §4)."""
    def empty(obj):
        obj["per_sample"] = {}
        return True
    _mutate_json(tree, QUANT, empty)
    fails = run(tree)
    assert "D/members" in kinds(fails), fails


# =============================================================================================
# 6-7 — the machine-readable map `systems/` and the manuscripts both read.
# =============================================================================================
def test_6_the_systems_map_records_a_different_series_for_this_path(tree):
    _mutate(tree, SMAP,
            "The sample-level characterisation of GSE299349",
            "The sample-level characterisation of GSE28866")
    fails = run(tree)
    assert "E/systems-map" in kinds(fails), fails


def test_7_the_systems_map_entry_disappears(tree):
    def drop(obj):
        before = len(obj["artifacts"])
        obj["artifacts"] = [r for r in obj["artifacts"] if r.get("path") != ARTIFACT]
        return len(obj["artifacts"]) == before - 1
    _mutate_json(tree, SMAP, drop)
    fails = run(tree)
    assert "E/systems-map" in kinds(fails), fails


# =============================================================================================
# 8-9 — THE HALF THAT MAKES THIS WORTH MORE THAN THE INSTANCE: the citing prose.
# =============================================================================================
def test_8_the_declaring_manuscript_section_names_another_series(tree):
    """§8 of the assessment declares this artifact as its producer. If the slot is re-pointed and
    the prose is not — or the prose is edited and the slot is not — the manuscript is making claims
    about one series from another's data, which is exactly what happened for twenty days."""
    _mutate(tree, DOC, "**§3.0a flagged `GSE299349`", "**§3.0a flagged `GSE28866`")
    fails = run(tree)
    assert "F/producer" in kinds(fails), fails
    assert any(DOC in f for f in fails), fails


def test_9_the_producer_declaration_is_removed_from_the_manuscript(tree):
    """⛔ THE VACUITY FAILURE, AND IT IS THE ONE THAT LOOKS MOST LIKE A PASS. A rule over 'every
    declaring document' is satisfied by zero documents. The registry names the documents that MUST
    declare this artifact, so losing the declaration is a finding rather than silence."""
    _mutate(tree, DOC,
            "> **Producer:** [`atr_hrd_sarcoma_series.py`]",
            "> Source: [`atr_hrd_sarcoma_series.py`]")
    fails = run(tree)
    assert "F/producer" in kinds(fails), fails
    assert any("DISAPPEARED" in f for f in fails), fails


# =============================================================================================
# 10-11 — absent inputs must fail closed, never skip.
# =============================================================================================
def test_10_a_missing_artifact_fails_rather_than_skips(tree):
    (tree / ARTIFACT).unlink()
    fails = run(tree)
    assert "B/artifact" in kinds(fails), fails


def test_11_a_producer_that_declares_no_identity_stops_the_whole_check(tree):
    """With no declared identity there is nothing to compare anything to, so the guard must say
    that and fail — not compare the remaining records to each other and call them consistent."""
    _mutate(tree, PRODUCER, 'SERIES = "GSE299349"', 'SERIES_NAME = "GSE299349"')
    fails = run(tree)
    assert kinds(fails) == {"A/declared"}, fails


# =============================================================================================
# WIRING — a guard nothing executes is the defect this repository keeps paying for.
# =============================================================================================
def test_the_producers_check_mode_runs_the_identity_guard(monkeypatch, capsys):
    """`--check` must FAIL on an unbound slot, not merely mention it. Stubbed rather than mutated
    because `--check` reads the real committed paths."""
    monkeypatch.setattr(G, "check_slot", lambda slot, root=G.REPO: ["B/artifact: stubbed failure"])
    assert M.main(["--check"]) == 1
    err = capsys.readouterr().err
    assert "IDENTITY UNBOUND" in err and "stubbed failure" in err


def test_an_unregistered_producer_is_reported_rather_than_skipped(monkeypatch, capsys):
    """If the slot is dropped from the registry, the producer's `--check` must go red. Silently
    passing is how the fixed output path became unbound in the first place."""
    monkeypatch.setattr(G, "SLOTS", [])
    assert M.main(["--check"]) == 1
    assert "IDENTITY UNCHECKED" in capsys.readouterr().err


def test_the_commit_loop_actually_runs_this_guard():
    """⛔ THE ROW IN preflight.sh IS PART OF THE GUARD. The modalities suite is opt-in behind
    PREFLIGHT_MODALITIES=1 and CI runs it on push — i.e. after the commit that would ship the wrong
    artifact. The gate row is what fires BEFORE the mistake is shared, so its absence is a test
    failure here rather than a silent loss of coverage."""
    with open(os.path.join(G.REPO, "scripts", "preflight.sh"), encoding="utf-8") as fh:
        sh = fh.read()
    assert "research/modalities/single_slot_identity.py" in sh
    assert "research/modalities/atr_hrd_sarcoma_series.py" in sh


def test_an_empty_registry_is_a_failure_not_a_pass(monkeypatch, capsys):
    monkeypatch.setattr(G, "SLOTS", [])
    assert G.main(["--check"]) == 1
    assert "REGISTRY EMPTY" in capsys.readouterr().err
