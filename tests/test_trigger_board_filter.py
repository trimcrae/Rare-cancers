"""The scan BOARD must show only what a trigger's CURRENT criterion admits.

Why this test exists (measured, 2026-08-05). `research/method-watch-trigger-hits.json`
is a CUMULATIVE ledger -- that is its job, it makes the scan idempotent. But a trigger's
query can be REVISED, and `write_board` rendered "most recent matches" straight out of
that ledger. So a hit admitted only by a SUPERSEDED query kept rendering as a current
match forever.

The real case: `TRG-E3-RECRUITER-STRUCTURE`'s first query admitted `TITLE:KEAP1` and
`TITLE:ligand`. Three KEAP1 redox-pharmacology papers (acute lung injury, coenzyme A,
heart failure) entered the ledger under a row whose criterion is *a partner-free liganded
structure for RNF114/DCAF16/DCAF15*. The query was revised on 2026-08-03, which stopped
them being INGESTED -- and did nothing about the four already stored. The board is what a
reader consults, so the row went on advertising "Keap1 ligand for acute lung injury" as
evidence for a structural-stageability criterion.

Revising a query is therefore only half a fix. This test pins the other half.
"""
import collections
import importlib.util
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "trigger_scan", os.path.join(_ROOT, "scripts", "trigger_scan.py"))
ts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ts)


def _render(tmp_path, trigger, hits):
    """Render a one-trigger board against a hand-built ledger, return the text."""
    cfg = {"triggers": [trigger]}
    ledger = {"runs": [{"date": "2026-08-05", "mode": "scan", "triggers": 1,
                        "queries": 1, "new_hits": 0, "appended": 0, "errors": []}],
              "hits": {trigger["id"]: hits}}
    run = ledger["runs"][-1]
    per = {trigger["id"]: dict(queries=1, seen=len(hits), in_window=0, new=0, appended=0)}
    board = tmp_path / "board.md"
    orig = ts.BOARD
    try:
        ts.BOARD = str(board)
        ts.write_board(cfg, ledger, run, per)
    finally:
        ts.BOARD = orig
    return board.read_text(encoding="utf-8")


_TRIGGER = {
    "id": "TRG-TEST-ROW",
    "title": "A deposited PARTNER-FREE LIGANDED structure",
    "status": "watching",
    "trigger_kind": "external_capability",
    "scan_enabled": True,
    "reopens": {"roadmap_rows": ["R9"]},
    # The REVISED criterion: one of the three blocked genes AND a structural word.
    "search": {
        "must_match": ["rnf114", "dcaf16", "dcaf15"],
        "also_match": ["structure", "crystal", "cryo-em"],
        "exclude_match": ["molecular glue", "review"],
    },
}

# Admitted only by the SUPERSEDED query (it allowed TITLE:KEAP1 and TITLE:ligand).
_STALE = {
    "id": "MED/42224961",
    "title": "Discovery of a novel covalent allosteric site CYS434 in Keap1 and its ligand "
             "for the treatment of acute lung injury",
    "date": "2026-05-30", "venue": "Bioorg Med Chem", "url": "https://example.invalid/a",
}
# Satisfies the CURRENT criterion.
_LIVE = {
    "id": "MED/00000001",
    "title": "Crystal structure of DCAF16 bound to a fragment",
    "date": "2026-08-01", "venue": "Test J", "url": "https://example.invalid/b",
}


def test_hit_from_a_superseded_query_is_not_rendered_as_a_current_match(tmp_path):
    """The KEAP1 case. A stale hit must not appear in 'most recent matches'."""
    out = _render(tmp_path, _TRIGGER, {_STALE["id"]: _STALE})
    assert "acute lung injury" not in out, (
        "a hit the CURRENT query would not return is being advertised as a match; "
        "revising the query did not clean the cumulative ledger's rendering"
    )
    assert "no matches recorded" in out


def test_withheld_hits_are_counted_not_silently_swallowed(tmp_path):
    """Filtering the view is fine; hiding that you filtered is not."""
    out = _render(tmp_path, _TRIGGER, {_STALE["id"]: _STALE})
    assert "1 earlier ledger hit(s) withheld" in out
    assert "SUPERSEDED" in out
    # It must point at where the history still lives -- the ledger is not edited.
    assert "method-watch-trigger-hits.json" in out


def test_a_hit_meeting_the_current_criterion_still_renders(tmp_path):
    """The filter must not be so aggressive it hides real hits."""
    out = _render(tmp_path, _TRIGGER, {_LIVE["id"]: _LIVE})
    assert "Crystal structure of DCAF16" in out
    assert "withheld" not in out


def test_mixed_ledger_shows_the_live_hit_and_withholds_the_stale_one(tmp_path):
    out = _render(tmp_path, _TRIGGER, {_STALE["id"]: _STALE, _LIVE["id"]: _LIVE})
    assert "Crystal structure of DCAF16" in out
    assert "acute lung injury" not in out
    assert "1 earlier ledger hit(s) withheld" in out


def test_the_ledger_itself_is_never_mutated_by_rendering(tmp_path):
    """History is retained. The VIEW is filtered, the record is not."""
    hits = {_STALE["id"]: dict(_STALE)}
    before = json.dumps(hits, sort_keys=True)
    _render(tmp_path, _TRIGGER, hits)
    assert json.dumps(hits, sort_keys=True) == before


def test_the_real_e3_row_advertises_no_keap1_paper():
    """Guards the live artifact, not just the logic.

    The board is regenerated by CI, so this asserts the shipped file is consistent
    with the shipped trigger config -- if a future query revision re-admits KEAP1
    pharmacology under a structural-stageability row, this fails.
    """
    with open(os.path.join(_ROOT, "research", "method-watch-triggers.json"),
              encoding="utf-8") as fh:
        cfg = json.load(fh, object_pairs_hook=collections.OrderedDict)
    trg = next(t for t in cfg["triggers"] if t["id"] == "TRG-E3-RECRUITER-STRUCTURE")
    s = trg["search"]
    for bad in ("Keap1 and its ligand for the treatment of acute lung injury",
                "Covalent Modification of Keap1 by the Key Metabolic Cofactor Coenzyme A"):
        assert not ts._matches(bad, s.get("must_match") or [], s.get("also_match") or [],
                               s.get("exclude_match") or []), (
            f"the E3 recruiter row's query admits KEAP1 pharmacology again: {bad!r}. "
            "Its criterion is a partner-free liganded structure for RNF114/DCAF16/DCAF15."
        )
