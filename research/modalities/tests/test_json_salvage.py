#!/usr/bin/env python3
"""Guards for `json_salvage` — the recovery half of the truncated-artifact defect.

⛔ The salvager is only ever allowed to RECOVER and DROP. If it ever completes, infers or defaults a value it
has manufactured a record no run produced, which is the failure CLAUDE.md §4(b) calls more dangerous than an
empty one. These tests are what hold that line.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, MOD)

import pytest                                                    # noqa: E402

import json_salvage as JS                                        # noqa: E402


#: The roll-up fields the truncated run never reached. Present together in a COMPLETE artifact;
#: absent together in a SALVAGED one. Any mixture is the state this test exists to refuse.
ROLLUP_FIELDS = ("ready_arms", "refused_arms", "sentence", "exitvec_anchor", "c397_sg_xyz", "base")


def test_the_committed_frame_artifact_is_either_salvaged_or_genuinely_complete():
    """`nr4a3-5bt-frame.json` — SALVAGED (as run 30778084770 published it) or COMPLETE, never between.

    ⚠ THIS TEST USED TO ASSERT ONLY THE SALVAGED STATE, and it went red when a later run legitimately
    produced a complete artifact and overwrote the truncated one. That is a real weakness rather than
    bad luck: a guard pinned to one state of a LIVE artifact reports a correct world as broken, and the
    fix is not to relax it but to make it express both states — and refuse the third.

    ⛔ THE THIRD STATE IS THE WHOLE POINT. A document with no banner AND no roll-up fields is a
    truncation that lost its banner: it parses, it looks like a normal artifact, and a reader has no way
    to know keys are missing rather than false. A document WITH a banner AND roll-up fields is a
    salvage that synthesised them — the "populated field is not a measured one" failure. Both are
    invisible to a schema check and both are refused here.

    Provenance is checked the way CLAUDE.md §4(b) requires — on the thing only a real run can produce.
    A full-precision float and a real working path cannot come from a default; `[]` and `0.0` can.
    """
    path = os.path.join(MOD, "nr4a3-5bt-frame.json")
    raw = open(path, encoding="utf-8").read()
    doc = json.loads(raw)                                        # repaired in place — it parses now
    banner = doc.get("⛔_TRUNCATED_ARTIFACT")
    present = [k for k in ROLLUP_FIELDS if k in doc]

    if banner is not None:
        # SALVAGED. Recovery is exact and the salvager invented nothing.
        assert banner["dropped_tail_verbatim"] == ',\n  "_mol": '
        assert banner["recovered_bytes"] + banner["dropped_bytes"] == banner["total_bytes"]
        for never in ROLLUP_FIELDS:
            assert never not in doc, \
                "%s was never written by the run — repair must not synthesise it" % never
            assert never in banner["keys_never_written"]
        return

    # COMPLETE. It must say so, and it must look like something a run actually produced.
    assert doc.get("_artifact_state", "").startswith("COMPLETE"), (
        "the frame artifact carries no truncation banner and does not declare itself COMPLETE — that "
        "is a truncation whose banner was lost, which parses cleanly and hides its own missing keys")
    assert not present or len(present) == len(ROLLUP_FIELDS), (
        "the artifact is part-way: roll-up fields %s are present and %s are not. A complete run writes "
        "all of them and a salvaged one writes none; a mixture means something filled in a subset"
        % (present, [k for k in ROLLUP_FIELDS if k not in doc]))
    assert len(doc.get("arms") or []) == 3, "a complete frame attempts all three paralogue arms"
    # ⛔ Provenance, not presence: a defaulted field cannot carry these.
    assert isinstance(doc.get("base"), str) and doc["base"], "no working path — nothing ran"
    ev = doc.get("exitvec_anchor")
    assert isinstance(ev, list) and len(ev) == 3, "the exit-vector anchor is missing or malformed"
    assert any(isinstance(v, float) and abs(v - round(v, 3)) > 0 for v in ev), (
        "every exit-vector component is round to 3dp — a computed anchor carries full float precision, "
        "so this reads as a value written in rather than measured")


def test_a_truncated_document_recovers_its_prefix_and_names_what_it_dropped():
    text = '{"a": 1, "b": [1, 2, 3], "c": {"d": "x"}, "e": '
    doc, rep = JS.salvage(text)
    assert doc == {"a": 1, "b": [1, 2, 3], "c": {"d": "x"}}
    assert rep["dropped_tail_verbatim"] == ', "e": '
    assert rep["closers_added"] == "}"
    assert rep["recovered_bytes"] + rep["dropped_bytes"] == rep["total_bytes"] == len(text)


def test_truncation_inside_a_nested_array_closes_every_open_container():
    """⚠ THE RECOVERED UNIT IS THE COMPLETE KEY/VALUE, NOT THE WHOLE ENCLOSING OBJECT — deliberately.

    That is exactly what the real repair needed: `e3_binary` kept its finished `selected` and `tried` and
    lost only the mid-write `_mol`. The consequence is that a container caught mid-write comes back with the
    keys that completed and WITHOUT the one that did not — never with a default in its place. A reader must
    therefore treat a missing key as missing, which is why the artifact carries the banner naming the tail.
    """
    text = '{"arms": [{"arm": "NR4A3", "ok": true}, {"arm": "NR4A1", "ok": '
    doc, rep = JS.salvage(text)
    assert doc == {"arms": [{"arm": "NR4A3", "ok": True}, {"arm": "NR4A1"}]}
    assert "ok" not in doc["arms"][1], "the incomplete key must be ABSENT, never defaulted"
    assert rep["dropped_tail_verbatim"] == ', "ok": '
    assert rep["closers_added"] == "}]}"


def test_a_brace_inside_a_string_is_not_a_cut_point():
    """A regex-based salvager cuts here and silently loses the rest — hence the character scan."""
    text = '{"note": "a } inside a string", "n": 7, "x": '
    doc, _rep = JS.salvage(text)
    assert doc == {"note": "a } inside a string", "n": 7}


def test_an_escaped_quote_does_not_end_the_string():
    text = '{"note": "he said \\"hi\\" and }", "n": 1, "x": '
    doc, _rep = JS.salvage(text)
    assert doc["note"] == 'he said "hi" and }' and doc["n"] == 1


def test_a_healthy_document_is_refused_rather_than_rewritten():
    with pytest.raises(ValueError, match="already parses"):
        JS.salvage('{"a": 1}')


def test_nothing_recoverable_is_a_refusal_not_an_empty_document():
    """⛔ An unrecoverable file must never come back as `{}` — that is a reading of absence invented out of
    an absent reading."""
    with pytest.raises(ValueError, match="nothing is recoverable"):
        JS.salvage('{"a": ')


def test_the_salvager_never_adds_a_key():
    text = '{"a": 1, "b": 2, "c": '
    doc, _ = JS.salvage(text)
    assert set(doc) == {"a", "b"}, "salvage may only drop, never add"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
