#!/usr/bin/env python3
"""The routed-edit anchor verifier — and the two rungs that use it.

⛔ THE FAILURE THIS GUARDS IS SILENT. A routed roadmap edit whose `current_text` has been reworded is not
an error anybody sees: it simply never gets applied, and the lane that produced it reports success. Nine
verbatim edits died that way on 2026-08-03. So the direction every test below protects is the same one:
`all_applicable` must never be True on evidence that does not support it.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import map_edit_anchors as mea            # noqa: E402
import antitarget_selfcontrol as sc       # noqa: E402
import fusion_object_inventory as fi      # noqa: E402

LIVE_MAP = os.path.join(MOD, "..", "manuscripts", "nr4a3-program-map.md")


def test_self_check():
    assert mea.check() == 0


@pytest.fixture()
def doc(tmp_path):
    p = tmp_path / "map.md"
    p.write_text("# T\n\nalpha unique line\n\ntwice\n\ntwice\n", encoding="utf-8")
    return str(p)


def _edit(**kw):
    base = {"section": "s", "anchor": "a", "current_text": "alpha unique line",
            "proposed_text": "p", "why": "w", "artifact": "x.json"}
    base.update(kw)
    return base


def test_exactly_once_is_the_only_pass(doc):
    got, s = mea.verify([_edit()], doc)
    assert got[0]["anchor_status"] == "OK" and s["all_applicable"] is True


def test_two_occurrences_is_a_defect_in_the_edit_not_a_warning(doc):
    got, s = mea.verify([_edit(current_text="twice")], doc)
    assert got[0]["anchor_status"] == "AMBIGUOUS"
    assert s["all_applicable"] is False, "a mechanical apply would hit the wrong one"


def test_a_reworded_anchor_is_dead_and_says_so(doc):
    got, s = mea.verify([_edit(current_text="this text was reworded away")], doc)
    assert got[0]["anchor_status"] == "NOT_FOUND"
    assert s["not_found"] == ["s"]


def test_an_unreadable_map_can_never_report_applicable(doc):
    got, s = mea.verify([_edit()], doc + ".gone")
    assert got[0]["anchor_status"] == "UNREAD"
    assert s["all_applicable"] is False
    assert s["map_read"] is False and s["map_read_why"]


def test_no_edits_is_not_all_applicable(doc):
    assert mea.verify([], doc)[1]["all_applicable"] is False


def test_schema_completeness_is_reported_separately(doc):
    got, _ = mea.verify([{"anchor": "a", "current_text": "alpha unique line"}], doc)
    assert got[0]["_schema_complete"] is False
    assert set(got[0]["_schema_missing"]) == {"section", "proposed_text", "why", "artifact"}
    # a complete-looking status must not paper over a malformed edit
    assert got[0]["anchor_status"] == "OK"


def test_the_verifier_cannot_write(doc):
    before = open(doc, encoding="utf-8").read()
    mea.verify([_edit(proposed_text="SOMETHING NEW")], doc)
    assert open(doc, encoding="utf-8").read() == before
    # ...and `verify` itself contains no write. Scoped to that function on purpose: the module's own
    # `check()` writes a TEMP fixture, and a module-wide grep would fail on it — a false positive that
    # would make this guard look broken and get deleted.
    import inspect
    src = inspect.getsource(mea.verify)
    assert ".write(" not in src
    assert 'open(' in src and '"w"' not in src and "'w'" not in src


# ------------------------------------------------------------------ the two rungs' live anchors

@pytest.mark.parametrize("verdict", ["PASS", "FAIL"])
def test_r14a_routed_edits_resolve_against_the_live_map(verdict):
    d = {"selfcontrol": dict(sc.panel_verdict([{"name": "PXR", "verdict": verdict}]), targets=[])}
    edits, s = mea.verify(sc.map_edits(d), LIVE_MAP)
    assert s["all_applicable"], json.dumps(
        {"not_found": s["not_found"], "ambiguous": s["ambiguous"]}, indent=1)
    assert all(e["_schema_complete"] for e in edits)


def test_r13a_routed_edits_resolve_against_the_live_map():
    audit = json.load(open(os.path.join(MOD, "nr4a3-exon-audit.json")))
    cache = json.load(open(os.path.join(MOD, "nr4a-sequences-cache.json")))
    d = fi.new_doc()
    fi.assemble(dict(audit["EWSR1"], protein=cache["EWSR1"]),
                dict(audit["NR4A3"], protein=cache["NR4A3"]), d)
    edits, s = mea.verify(fi.map_edits(d), LIVE_MAP)
    assert s["all_applicable"], json.dumps(
        {"not_found": s["not_found"], "ambiguous": s["ambiguous"]}, indent=1)
    assert all(e["_schema_complete"] for e in edits)


def test_r13a_does_not_give_the_stale_neoantigen_fact_a_second_home():
    """The map already carries the 26-binder consequence. A routed edit that RESTATES it would be the
    one-fact-one-place violation; the edit must POINT at the re-derivation instead."""
    audit = json.load(open(os.path.join(MOD, "nr4a3-exon-audit.json")))
    cache = json.load(open(os.path.join(MOD, "nr4a-sequences-cache.json")))
    d = fi.new_doc()
    fi.assemble(dict(audit["EWSR1"], protein=cache["EWSR1"]),
                dict(audit["NR4A3"], protein=cache["NR4A3"]), d)
    neo = [e for e in fi.map_edits(d) if "neoantigen" in e["section"]]
    assert len(neo) == 1
    assert "26 predicted binders" not in neo[0]["proposed_text"], \
        "the map already states this; the edit must confirm and point, not copy"
    assert "fusion-object-inventory.json" in neo[0]["proposed_text"]
