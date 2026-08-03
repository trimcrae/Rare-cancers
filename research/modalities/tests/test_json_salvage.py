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


def test_the_exact_committed_truncation_recovers_every_complete_value():
    """The real artifact, byte for byte: `nr4a3-5bt-frame.json` as run 30778084770 published it."""
    path = os.path.join(MOD, "nr4a3-5bt-frame.json")
    raw = open(path, encoding="utf-8").read()
    doc = json.loads(raw)                                        # repaired in place — it parses now
    assert "⛔_TRUNCATED_ARTIFACT" in doc, "the repaired artifact must carry its banner"
    b = doc["⛔_TRUNCATED_ARTIFACT"]
    assert b["dropped_tail_verbatim"] == ',\n  "_mol": '
    assert b["recovered_bytes"] + b["dropped_bytes"] == b["total_bytes"]
    # ⛔ the roll-up fields were never written and must NOT have been invented on repair
    for never in ("ready_arms", "refused_arms", "sentence", "exitvec_anchor", "c397_sg_xyz", "base"):
        assert never not in doc, "%s was never written by the run — repair must not synthesise it" % never
        assert never in b["keys_never_written"]


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
