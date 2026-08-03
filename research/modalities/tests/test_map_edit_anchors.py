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

def _write(text, _n=[0]):
    """Write `text` to a fresh temp file and return its path — `mea.verify` reads a PATH, not a string."""
    import tempfile, os
    _n[0] += 1
    fd, path = tempfile.mkstemp(prefix="mapedit_%d_" % _n[0], suffix=".md")
    with os.fdopen(fd, "w") as fh:
        fh.write(text)
    return path


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
    assert mea.verify([], doc)[1]["all_accounted"] is False


def test_an_applied_edit_is_a_success_not_a_dead_anchor(tmp_path):
    """⛔ THE REGRESSION THAT WAS RED ON `main`. Applying a routed edit REMOVES its `current_text` — so a
    guard that only looks for `current_text` goes red exactly when routing succeeds. Fifteen "dead"
    anchors on 2026-08-03 were all landed edits."""
    landed = "the replacement sentence that actually landed in the roadmap, verbatim and in full"
    p = tmp_path / "map.md"
    p.write_text("# T\n\n%s\n" % landed, encoding="utf-8")
    got, s = mea.verify([_edit(current_text="the old sentence, now replaced", proposed_text=landed)],
                        str(p))
    assert got[0]["anchor_status"] == "APPLIED"
    assert s["n_applied"] == 1 and s["not_found"] == []
    assert s["all_accounted"] is True, "an applied edit must not make the build red"
    assert s["all_applicable"] is False, "...but it is no longer APPLICABLE, and the two differ"


def test_a_short_proposed_text_cannot_manufacture_an_applied(tmp_path):
    p = tmp_path / "map.md"
    p.write_text("# T\n\nalpha\n", encoding="utf-8")
    got, _ = mea.verify([_edit(current_text="gone from the file", proposed_text="alpha")], str(p))
    assert got[0]["anchor_status"] == "NOT_FOUND"


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

def test_r14a_routed_edits_resolve_against_the_live_map():
    """⚠ AGAINST THE REAL ARTIFACT, NOT A SYNTHETIC VERDICT.

    An earlier version of this test built a fake doc (`panel_verdict([...PASS])`) and asserted its
    anchors resolved. That is unsound once the edits have been routed: several `proposed_text`s embed
    the MEASURED verdict, so a synthetic doc produces a different replacement string from the one in the
    document, and the test reports NOT_FOUND for edits that landed perfectly. It was asserting that the
    map had been edited from a doc that never existed.

    ⚠ AND IT ASSERTS AMBIGUITY, NOT LOCATABILITY. Whether an anchor is currently locatable is a property
    of the CHECKOUT — the artifact lands on `main` while a feature branch's roadmap has not been routed
    yet — so a NOT_FOUND here is as likely to mean "different ref" as "the map moved", and a test that
    cannot tell those apart is noise. The real guard against a dead anchor is the anchor check the module
    runs INSIDE the CI job, where the artifact and the map are the same checkout by construction. What is
    a genuine property of the code, on any ref, is that no anchor matches MORE than once.
    """
    p = os.path.join(MOD, "antitarget-selfcontrol.json")
    if not os.path.exists(p):
        pytest.skip("the panel has not been run on this ref")
    d = json.load(open(p))
    edits, s = mea.verify(sc.map_edits(d), LIVE_MAP)
    assert not s["ambiguous"], json.dumps(s["ambiguous"], indent=1)
    assert all(e["_schema_complete"] for e in edits)


def test_r14a_edit_shape_holds_for_either_verdict():
    """The SHAPE is verdict-independent even though the text is not — every edit is schema-complete and
    carries a non-empty anchor, whichever way the panel went."""
    for verdict in ("PASS", "FAIL"):
        d = {"selfcontrol": dict(sc.panel_verdict([{"name": "PXR", "verdict": verdict}]), targets=[])}
        edits = sc.map_edits(d)
        assert edits
        for e in edits:
            assert set(e) >= {"section", "anchor", "current_text", "proposed_text", "why", "artifact"}
            assert e["current_text"] and e["current_text"] != e["proposed_text"]


def test_r13a_routed_edits_resolve_against_the_live_map():
    audit = json.load(open(os.path.join(MOD, "nr4a3-exon-audit.json")))
    cache = json.load(open(os.path.join(MOD, "nr4a-sequences-cache.json")))
    d = fi.new_doc()
    fi.assemble(dict(audit["EWSR1"], protein=cache["EWSR1"]),
                dict(audit["NR4A3"], protein=cache["NR4A3"]), d)
    edits, s = mea.verify(fi.map_edits(d), LIVE_MAP)
    assert s["all_accounted"], json.dumps(
        {"not_found": s["not_found"], "ambiguous": s["ambiguous"]}, indent=1)
    assert all(e["_schema_complete"] for e in edits)
    # ⚠ NO ASSERTION ON `n_applied` HERE. Whether these have been ROUTED yet varies by checkout — the
    # edits land on `main` while a feature branch's copy of the roadmap has not received them — so an
    # "at least one is applied" assertion would pass or fail on which branch the suite runs from, which
    # is not a property of the code. `all_accounted` is the durable claim: every anchor is either
    # applicable or already applied, on any ref.


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


# =========================================================================================================
# THE THIRD EDIT SHAPE — a MID-LINE REPLACEMENT, which the probe used to get silently wrong.
#
# Measured 2026-08-03 on live `C24` edits before they were routed: for a replacement the proposal neither
# starts nor ends with `current_text`, so the old code probed the first 120 characters of the WHOLE line.
# On a long table row the change sits far past character 120, so those 120 characters were byte-identical
# to the line already in the document — the probe matched, the status came back APPLIED, and the edit was
# SKIPPED while the router printed a clean run. Two `C24` edits (the `V17` and `R8` rows, the two places
# the roadmap says no percentile may be quoted for C397) hit exactly this.
# =========================================================================================================
LONG = ("| **V17** | The exposure criterion `EXPOSED_RSA = 0.25` is known-defective and fails its own "
        "positive control, and the rank is what survives, which is why the row reads the way it does, ")


def test_a_midline_replacement_is_NOT_reported_applied_before_it_lands():
    current = LONG + "the arm does not contain C397 | rank-only |"
    proposed = LONG + "the arm does not contain C397 *from that run*, and a second scope does | rank-only |"
    doc = "noise\n" + current + "\nmore noise\n"
    probe, discriminating = mea.build_probe(proposed, current)
    assert discriminating, "a real mid-line change must yield a usable probe"
    assert doc.count(probe) == 0, "the probe must be ABSENT before the edit lands"
    assert (doc.replace(current, proposed)).count(probe) == 1, "and PRESENT after"
    got, _s = mea.verify([{"section": "s", "anchor": "a", "current_text": current,
                           "proposed_text": proposed, "why": "w", "artifact": "x"}],
                         _write(doc))
    assert got[0]["anchor_status"] == "OK", "a mid-line edit that has not landed must be OK, not APPLIED"


def test_a_midline_replacement_is_reported_applied_once_it_has_landed():
    current = LONG + "the arm does not contain C397 | rank-only |"
    proposed = LONG + "the arm does not contain C397 *from that run*, and a second scope does | rank-only |"
    got, _s = mea.verify([{"section": "s", "anchor": "a", "current_text": current,
                           "proposed_text": proposed, "why": "w", "artifact": "x"}],
                         _write("noise\n" + proposed + "\n"))
    assert got[0]["anchor_status"] == "APPLIED"


def test_a_one_character_change_still_probes_because_the_window_widens():
    """`5b-T` flips an ORDERED-PLAN checkbox `[ ]` -> `[x]`. The introduced text is ONE character, which is
    meaningless as a probe in a 6,000-line document — so the window widens around it and still straddles
    the change, staying absent before and present after."""
    current = "`[ ]` 5b-T · Rebuild the NR4A1/2/3 ternaries by the ASSEMBLY route (structural only)"
    proposed = current.replace("`[ ]`", "`[x]`", 1)
    probe, discriminating = mea.build_probe(proposed, current)
    assert discriminating and len(probe) >= mea.MIN_PROBE_CHARS
    assert "[x]" in probe
    got, _s = mea.verify([{"section": "s", "anchor": "a", "current_text": current,
                           "proposed_text": proposed, "why": "w", "artifact": "x"}],
                         _write("noise\n" + proposed + "\n"))
    assert got[0]["anchor_status"] == "APPLIED"
    got, _s = mea.verify([{"section": "s", "anchor": "a", "current_text": current,
                           "proposed_text": proposed, "why": "w", "artifact": "x"}],
                         _write("noise\n" + current + "\n"))
    assert got[0]["anchor_status"] == "OK"


def test_append_and_prepend_shapes_are_unchanged_by_the_generalisation():
    current = "| **C16** | the decoy-null domain trim | pLDDT >= 70 | frozen |"
    for proposed in (current + " ⭑ a second scope now covers C397 — see C24, not a widening of this one.",
                     "⭑ PREFIXED NOTE ABOUT THE SECOND SCOPE, long enough to probe. " + current):
        probe, discriminating = mea.build_probe(proposed, current)
        assert discriminating
        assert ("noise\n" + current + "\n").count(probe) == 0
        assert ("noise\n" + proposed + "\n").count(probe) == 1


def test_a_probe_that_cannot_discriminate_is_reported_rather_than_guessed():
    """A change so small and so surrounded by its own text that no widened window escapes `current_text`
    must NOT be turned into an APPLIED. Absence of a usable probe is not evidence either way."""
    probe, discriminating = mea.build_probe("abc", "abc")     # a no-op proposal introduces nothing
    assert probe == "" and discriminating is False


def test_widening_measures_the_stripped_probe_so_a_landed_edit_is_not_called_dead():
    """Measured by routing the C24 edits twice. The §3b register's item count is `**23 items.**` ->
    `**24 items.**`: a ONE-character change whose widened window ended in whitespace, so a 25-character
    slice stripped to 23 — one below the floor — and the applied edit came back a DEAD ANCHOR."""
    current = "**23 items.** Status: ✅ **frozen** · ⚠ **CONTESTED** (a defensible alternative)"
    proposed = current.replace("**23 items.**", "**24 items.**", 1)
    probe, discriminating = mea.build_probe(proposed, current)
    assert discriminating, "a one-character count bump must still yield a usable probe"
    assert len(probe) >= mea.MIN_PROBE_CHARS, "the floor applies to the STRIPPED probe"
    assert "**24 items.**" in probe and "**23" not in probe
    got, _s = mea.verify([{"section": "s", "anchor": "a", "current_text": current,
                           "proposed_text": proposed, "why": "w", "artifact": "x"}],
                         _write("noise\n" + proposed + "\n"))
    assert got[0]["anchor_status"] == "APPLIED", "the landed edit must not read as dead"
