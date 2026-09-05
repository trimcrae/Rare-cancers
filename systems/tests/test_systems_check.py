#!/usr/bin/env python3
"""Tests for the systems model's checker and guard. ($0, pure stdlib + pytest)

Every test here guards a rule that exists because of a measured failure, and each says which.
"""
from __future__ import annotations

import copy
import inspect
import json
import shutil
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
REPO = os.path.dirname(SYS)
sys.path.insert(0, SYS)

import systems_check as sc  # noqa: E402
import parser_guard as pg  # noqa: E402


@pytest.fixture(scope="module")
def graph():
    return sc.derive(sc.load_graph())


# ───────────────────────── the model is internally consistent ─────────────────────────

def test_repo_state_is_clean(graph):
    """The committed graph passes every invariant. A red build here is a real inconsistency."""
    f = sc.Findings()
    sc.run_checks(graph, f)
    assert f.errors == [], "\n".join(f.errors)


@pytest.mark.parametrize("path_sep", ["/", "\\"])
def test_views_match_the_graph(graph, monkeypatch, path_sep):
    """A generated view that has been hand-edited, or has drifted, is a defect.

    This is the whole reason the views are generated: prose drifts and cannot be checked.
    """
    f = sc.Findings()
    native_relpath = os.path.relpath
    with monkeypatch.context() as paths:
        paths.setattr(sc.os, "sep", path_sep)
        paths.setattr(sc.os.path, "relpath", lambda *args: native_relpath(*args).replace("\\", "/").replace("/", path_sep))
        sc.check_views(graph, f)
    assert f.errors == [], "\n".join(f.errors) + "\n\nRun: python3 systems/systems_check.py --write-views"


def test_every_route_lands_in_exactly_one_family(graph):
    fams = {s["id"]: set(s["routes"]) for s in graph["strategies"]}
    seen = {}
    for f, rs in fams.items():
        for r in rs:
            assert r not in seen, f"{r} is in both {seen[r]} and {f}"
            seen[r] = f
    assert len(seen) == len(graph["routes"])


# ───────────────────────── the taxonomies do their job ─────────────────────────

def test_permanent_blocker_carries_no_technology(graph):
    """A fact about what the objects ARE is not waiting on a capability.

    Putting one on a watch list wastes the watch, and — worse — implies the route might come back.
    """
    for b in graph["blockers"]:
        if b["permanent"]:
            assert not b["retired_by_technology"], \
                f"{b['id']} is permanent ({b['kind']}) but claims a technology would retire it"


def test_non_permanent_blocker_names_a_way_out(graph):
    """Either a technology or an action. A blocker with neither is mis-typed or under-analysed."""
    for b in graph["blockers"]:
        if not b["permanent"]:
            assert b["retired_by_technology"] or b.get("retired_by_action"), \
                f"{b['id']} ({b['kind']}) names no technology and no action that would retire it"


def test_every_forecast_declares_its_basis(graph):
    """An unlabelled forecast is indistinguishable from a measurement."""
    for c in graph["forecasts"]:
        assert c.get("basis") in ("evidence_based", "extrapolated", "speculative"), \
            f"{c['id']} has no usable basis"
        assert c.get("last_reviewed"), f"{c['id']} has no last_reviewed date"


def test_technology_and_forecast_reference_each_other(graph):
    fc = {c["id"]: c for c in graph["forecasts"]}
    for t in graph["technologies"]:
        assert t["forecast"] in fc, f"{t['id']} names a forecast that does not exist"
        assert fc[t["forecast"]]["tech_ref"] == t["id"], f"{t['id']} back-reference disagrees"


def test_blocker_kinds_are_from_the_closed_enum(graph):
    schema = json.load(open(os.path.join(SYS, "schema", "blocker.schema.json")))
    allowed = set(schema["properties"]["kind"]["enum"])
    for b in graph["blockers"]:
        assert b["kind"] in allowed, f"{b['id']} has kind {b['kind']!r}, which is outside the enum"


# ───────────────────────── the claim ceiling is enforced ─────────────────────────

def test_a_failing_instrument_cannot_be_cited_as_support(graph):
    """A claim can never be stronger than the instrument underneath it.

    Selectivity results in this program have had to be withdrawn; this is the structural version
    of the rule that exists because of that.
    """
    g = copy.deepcopy(graph)
    failing = next(i["id"] for i in g["instruments"]
                   if (i.get("known_answer_control") or {}).get("state") in sc.NON_SUPPORTING_CONTROL)
    g["routes"][0].setdefault("instruments", {}).setdefault("support", []).append(failing)
    f = sc.Findings()
    sc.check_instrument_support(g, f)
    assert any("[V2]" in e for e in f.errors), \
        "citing an instrument whose known-answer control failed as SUPPORT must be an error"


def test_no_control_and_a_failed_control_are_both_non_supporting():
    """Different facts, and neither is support. `none` is in the set deliberately."""
    assert "none" in sc.NON_SUPPORTING_CONTROL
    assert "fails" in sc.NON_SUPPORTING_CONTROL


def test_compute_needs_a_case(graph):
    g = copy.deepcopy(graph)
    g["routes"][0]["recommends_compute"] = True
    g["routes"][0].pop("compute_case", None)
    f = sc.Findings()
    sc.check_compute_case(g, f)
    assert any("[C1]" in e for e in f.errors), \
        "recommending compute with no case must fail — reasoning must be shown exhausted first"


# ───────────────────────── pointers resolve ─────────────────────────

def test_every_owner_anchor_resolves(graph):
    f = sc.Findings()
    sc.check_pointers(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_slugify_matches_github_for_a_heading_with_glyphs():
    """The one broken anchor this check found had gained a glyph after being registered.

    Glyphs are stripped and the surrounding spaces each become a hyphen, so adding one to a
    heading silently changes its anchor. That is exactly the drift this check exists to catch.
    """
    assert sc.slugify("## Route 1 — ⭐ ATR-inhibitor synthetic lethality") == \
        "route-1---atr-inhibitor-synthetic-lethality"
    assert sc.slugify("## Route 1 — ATR-inhibitor synthetic lethality") == \
        "route-1--atr-inhibitor-synthetic-lethality"


# ───────────────────────── the fail-red guard ─────────────────────────

@pytest.mark.parametrize("path_sep", ["/", "\\"])
def test_parser_guard_passes_on_the_committed_tree(monkeypatch, path_sep):
    native_relpath = os.path.relpath
    with monkeypatch.context() as paths:
        paths.setattr(pg.os, "sep", path_sep)
        paths.setattr(pg.os.path, "relpath", lambda *args: native_relpath(*args).replace("\\", "/").replace("/", path_sep))
        result = pg.main([])
    assert result == 0


def test_parser_guard_catches_a_renamed_plan_heading(tmp_path, monkeypatch):
    """The failure this guard exists for: a heading moves, the scanner reports blindness, CI stays green."""
    src = open(os.path.join(REPO, pg.PLAN_DOC), encoding="utf-8").read()
    broken = src.replace("THE ORDERED PLAN", "THE SEQUENCED PLAN")
    monkeypatch.setattr(pg, "read", lambda rel: broken if rel == pg.PLAN_DOC else
                        (open(os.path.join(REPO, rel), encoding="utf-8").read()
                         if os.path.exists(os.path.join(REPO, rel)) else None))
    problems = []
    pg.check_plan_heading(lambda p, w, y: problems.append((p, w, y)))
    assert problems and problems[0][0] == "work_ledger"


def test_parser_guard_catches_a_plan_section_with_no_items(monkeypatch):
    """A heading that has drifted away from the checkboxes is as blinding as a missing heading."""
    text = "# doc\n\n## THE ORDERED PLAN (spend-gated)\n\nprose only, no items\n\n## next section\n"
    monkeypatch.setattr(pg, "read", lambda rel: text if rel == pg.PLAN_DOC else None)
    problems = []
    pg.check_plan_heading(lambda p, w, y: problems.append((p, w, y)))
    assert problems and "no checklist items" in problems[0][1]


# ───────────────────────── cli ─────────────────────────

def test_cli_check_exits_zero():
    r = subprocess.run([sys.executable, os.path.join(SYS, "systems_check.py"), "--check"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


# ───────────────────────── the requirement register (Phase 3) ─────────────────────────

def test_requirement_extraction_is_lossless(graph):
    """Every claim-ceiling cell in the roadmap is stored verbatim in the graph.

    This is what makes the decomposition safe rather than a summarisation. A cap here would silently
    drop the nuance the roadmap's narrative carries, and a lossy migration is a regression.
    """
    f = sc.Findings()
    sc.check_requirement_source_agreement(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_a_hand_edit_to_either_side_fails(graph):
    g = copy.deepcopy(graph)
    g["requirements"][0]["claim_ceiling_raw"] = "tampered"
    f = sc.Findings()
    sc.check_requirement_source_agreement(g, f)
    assert any("[M4]" in e for e in f.errors)


def test_every_requirement_states_a_claim_ceiling(graph):
    """A requirement with no ceiling cannot bound what may be claimed from it, which is its whole job."""
    for r in graph["requirements"]:
        assert r.get("claim_ceiling"), f"{r['id']} states no claim ceiling"


def test_the_kinds_of_gap_are_distinguished(graph):
    """'Nothing built', 'needs a bench' and 'every instrument failed' are three different work items.

    The first needs something BUILT, the second cannot be answered in this program at all, the third
    needs a better METHOD. Filing them under one word is how the cheap one stays invisible — the same
    failure the technology taxonomy found on the watch list.

    ⭐ THE MIDDLE ONE WAS ADDED 2026-08-05 AND IS THE POINT. [Q3] reported R6 (a computable term nobody
    has computed) and R4 ('⛔ none — needs a bench', against a program CLAUDE.md §5 says has no wet lab)
    with the identical sentence. A permanent warning for a decision already taken is how a reader learns
    to skim the warning list.
    """
    inst = sc.by_id(graph["instruments"])
    holes, unusable = [], []
    for r in graph["requirements"]:
        vb = r.get("verified_by", [])
        if not vb:
            holes.append(r["id"])
        elif not [v for v in vb if inst.get(v, {}).get("usable")]:
            unusable.append(r["id"])
    assert holes and unusable, "both categories should be populated in the current state"
    assert not set(holes) & set(unusable), "a requirement cannot be in both categories"

    # Every hole says WHY it is a hole, and the three answers license different actions.
    by_gap = {}
    for r in graph["requirements"]:
        if r["id"] in holes and r["state"]["work_state"] != "dead":
            gap = r.get("coverage_gap")
            assert gap in sc.COVERAGE_GAPS, f"{r['id']} has no instrument and no coverage_gap"
            assert len(r.get("coverage_gap_why", "")) > 20, f"{r['id']} states a gap with no reason"
            by_gap.setdefault(gap, []).append(r["id"])
    assert {"WARN", "INFO"} <= {sc.COVERAGE_GAPS[g][0] for g in by_gap}, \
        "the split is inert unless at least one gap warns and at least one is a stated boundary"


def test_a_requirement_with_no_instrument_and_no_reason_is_an_error(graph):
    """⛔ Omitting `coverage_gap` must not be the quiet way to avoid answering.

    Sabotage: strip the field from R4 and the check must ERROR, not fall silent. A field that is only
    read when present is a field nobody has to write.
    """
    import copy
    g = copy.deepcopy(graph)
    for r in g["requirements"]:
        if r["id"] == "R4":
            r.pop("coverage_gap", None)
            r.pop("coverage_gap_why", None)
    f = sc.Findings()
    sc.check_requirements(g, f)
    assert any("[Q3]" in e and "R4" in e for e in f.errors), \
        "an uninstrumented requirement that will not say why must fail the build"


def test_a_passing_control_does_not_by_itself_make_an_instrument_usable(graph):
    """⭐ INS-MONOVALENT-REACH passes its own control and cannot license a claim.

    Its own note: the bivalent replication 'is what makes the monovalent half readable; it inherits
    V3's INCONCLUSIVE site question and V17's defective exposure cutoff, so it can refute a route and
    cannot license one.' A usability test reading only `known_answer_control.state` calls it supporting
    and silently clears R8's [Q4] — which is exactly what the 2026-08-05 reconciliation nearly did.
    """
    inst = sc.by_id(graph["instruments"])
    reach = inst["INS-MONOVALENT-REACH"]
    assert reach["known_answer_control"]["state"] == "passes"
    assert reach["inherits_limits_from"] == ["V3", "V17"]
    assert reach["usable"] is False, "a passing control must not override an inherited limit"
    r8 = sc.by_id(graph["requirements"])["R8"]
    assert "INS-MONOVALENT-REACH" in r8["verified_by"]
    assert not [v for v in r8["verified_by"] if inst[v]["usable"]], "R8 must keep its [Q4]"


def test_mixed_is_not_a_pass(graph):
    """⛔ NO VAGUE STATES — and `mixed` was the one that was never enumerated anywhere.

    It was in use on two instruments and in no schema, so it silently counted as SUPPORTING. V19's own
    note reads 'PARTIAL — the arm that addresses the GENERATIVE step is unrun' and V15's reads 'one of
    the five nulls does not support it'. Closing the enum ADDED a warning (R1); that is the direction a
    correction should move a count.
    """
    assert "mixed" in sc.NON_SUPPORTING_CONTROL
    inst = sc.by_id(graph["instruments"])
    mixed = [i["id"] for i in graph["instruments"]
             if (i.get("known_answer_control") or {}).get("state") == "mixed"]
    assert mixed, "the test is inert if nothing is `mixed`"
    assert not any(inst[m]["usable"] for m in mixed)
    f = sc.Findings()
    sc.check_requirements(graph, f)
    assert any("[Q4]" in w and "R1" in w for w in f.warns), \
        "R1 (V13 fails, V14 none, V15 mixed) must warn now that `mixed` is not a pass"


# ───────────────────────── the plan move (§1) ─────────────────────────

def test_plan_render_round_trips(graph):
    """The generated plan reproduces every stored block exactly.

    Only `marker` is a field; everything else is verbatim. The extractor refuses to write unless the
    render matches the source byte for byte, and this keeps that true as the graph is edited.
    """
    plan = graph.get("plan") or {}
    assert plan.get("blocks"), "graph/plan.json carries no blocks"
    body = sc.render_plan_body(plan)
    for b in plan["blocks"]:
        if b["kind"] == "raw":
            assert b["text"] in body
        elif b["kind"] == "item":
            assert f"- **`[{b['marker']}]`{b['text']}" in body


def test_plan_item_count_and_markers_are_unchanged(graph):
    """The migration gate. A different COUNT is a failed move, not a new plan.

    ⚠ THE MARKER DISTRIBUTION IS NO LONGER FROZEN, AND FREEZING IT WAS A MISTAKE (corrected 2026-08-06).
    This test asserted the exact Counter from the migration moment — `{"x": 17, "~": 3, " ": 15, "–": 1,
    "!": 2}`. That is the plan's LIVE STATE, not a property of the move: the instant a rung lands and its
    marker goes to `x`, a test whose stated purpose is "the move was lossless" goes red for a reason that
    has nothing to do with the move. A guard that fires on ordinary progress gets edited every time it
    fires, and a guard that gets edited routinely stops being read. (It fired here on eight markers
    corrected against the roadmap, which owns a gate's verdict — every one of them a real advance.)

    What actually belongs to the migration, and is kept: the item COUNT (items neither lost nor invented)
    and the marker VOCABULARY (a stray glyph means a mangled parse). Losslessness itself is proven
    elsewhere and more strictly — `systems/extract_plan.py` refuses to write unless re-rendering
    reproduces the original text byte for byte.
    """
    from collections import Counter
    items = [b for b in (graph.get("plan") or {}).get("blocks", []) if b["kind"] == "item"]
    assert len(items) == 38, f"expected 38 plan items, found {len(items)}"
    seen = Counter(b["marker"] for b in items)
    assert set(seen) <= {"x", "~", " ", "–", "!"}, (
        f"unknown plan marker(s) {sorted(set(seen) - {'x', '~', ' ', '–', '!'})} — the vocabulary is "
        f"x/~/space/en-dash/! and anything else is a mangled parse, not a new state"
    )


def test_every_plan_item_text_ends_in_a_newline(graph):
    """⛔ A STRIPPED TRAILING NEWLINE MERGES TWO PLAN ITEMS INTO ONE LINE, AND THE MERGE IS SILENT.

    ★ MEASURED 2026-08-06. Eight plan markers were corrected against the roadmap with
    `item["text"].rstrip() + note`. Every item's text carries a trailing `\\n` that the renderer relies on
    to end the bullet, so `.rstrip()` removed it and each edited item rendered CONCATENATED with the one
    after it. The victim was `R14-b` — an owed, money-gated item — which vanished from the work ledger's
    board entirely while still existing in the graph.

    ⚠ NOTHING CAUGHT IT AT THE TIME: the JSON stayed valid, `systems_check --check` stayed at 0 ERROR, the
    view regenerated without complaint, and the item count stayed 38 because no item was DELETED — only
    made invisible to the parser. It surfaced because `test_work_ledger_reads_the_generated_plan` had just
    been changed to derive the owed count from the graph instead of comparing it to a frozen 20; the
    derived form disagreed 12 vs 13 the first time it ran. The frozen version would have passed.

    This test is the cheap direct check for the same failure, so it does not depend on the ledger.
    """
    items = [b for b in (graph.get("plan") or {}).get("blocks", []) if b["kind"] == "item"]
    bad = [b["text"][:60] for b in items if not b["text"].endswith("\n")]
    assert not bad, (
        "plan item text must end with a newline — the renderer uses it to end the bullet, so an item "
        "without one silently swallows the next item into its own line:\n  " + "\n  ".join(bad)
    )


def test_the_skipped_marker_is_an_en_dash(graph):
    """U+2013, not an ASCII hyphen.

    Matching only `-` reclassifies every skipped item as pending and fills the board with work
    nobody owes. There is exactly one such item and this pins it.
    """
    items = [b for b in (graph.get("plan") or {}).get("blocks", []) if b["kind"] == "item"]
    skipped = [b for b in items if b["marker"] not in " x~!"]
    assert len(skipped) == 1
    assert ord(skipped[0]["marker"]) == 0x2013, f"got U+{ord(skipped[0]['marker']):04X}"


def test_plan_and_spine_notations_share_one_file():
    """pinned-figures `strategy_spine_cum` is a WITHIN-FILE subset check.

    `Cum. ~$N` (the plan) and `Cum ~$N` (the spine) differ deliberately, and separating them across
    files fails that check as "pattern found nothing" — which reads like a broken regex rather than
    a broken move. This is why the two sections had to travel together.
    """
    import re
    view = open(os.path.join(SYS, "views", "plan.md"), encoding="utf-8").read()
    plan_cum = re.findall(r"Cum\. ~\$([0-9]+)", view)
    spine_cum = re.findall(r"Cum ~\$([0-9]+)", view)
    assert plan_cum and spine_cum, "both notations must be present in the one generated file"
    assert set(spine_cum) <= set(plan_cum), \
        f"spine values not a subset of the plan's: {sorted(set(spine_cum) - set(plan_cum))}"


def test_work_ledger_reads_the_generated_plan(graph):
    """The parser follows the plan. A parser left watching the old location goes green on a file
    that no longer holds what it parses — the exact failure parser_guard exists to prevent.

    ⚠ THE OWED COUNT IS DERIVED FROM THE GRAPH, NOT FROZEN (corrected 2026-08-06). This asserted
    `len(got) == 20`, which was the number of not-done items on the day the plan moved. It is live
    state: every rung that lands lowers it, so a test about WHERE THE PARSER LOOKS went red because
    WORK GOT DONE. Comparing the parser's count to the graph's own count of not-done items is
    strictly stronger — it catches a parser that silently drops or double-counts items, which a
    hardcoded 20 never could once the true number moved away from 20.
    """
    sys.path.insert(0, os.path.join(REPO, "research", "modalities"))
    import work_ledger as wl
    assert wl.DEFAULT_PLAN_DOC.endswith(os.path.join("systems", "views", "plan.md"))
    assert wl.DEFAULT_STRATEGY == wl.DEFAULT_PLAN_DOC
    text = open(wl.DEFAULT_PLAN_DOC, encoding="utf-8").read()
    got, how = wl.scan_plan_items(text, None)
    assert not how.startswith("NOT SCANNED"), how

    items = [b for b in (graph.get("plan") or {}).get("blocks", []) if b["kind"] == "item"]
    owed = [b for b in items if b["marker"] not in ("x", "–")]
    assert len(got) == len(owed), (
        f"the ledger parsed {len(got)} owed item(s) from the view but the graph holds {len(owed)} "
        f"not-done item(s) ({len(items)} total). The parser and the model must agree on what is owed; "
        f"a gap means the renderer and the scanner disagree about the marker vocabulary."
    )


def test_the_plan_is_linted_wherever_it_lives():
    """Moving the plan dropped lint_claims from 50 warnings to 43 because ~1,580 lines of gate
    language left the linted set silently. A linter whose scope shrinks while its pass rate improves
    is the worst possible signal."""
    problems = []
    pg.check_paths(lambda p, w, y: problems.append((p, w)))
    assert not [p for p in problems if "not a lint_claims target" in p[1]]


# ───────────────────────── the scan write path (§3) ─────────────────────────

def test_scan_writes_signals_and_never_touches_state(tmp_path, monkeypatch):
    """⛔ THE ONE RULE THAT KEEPS THE WATCH LIST HONEST.

    A hit is machine-matched on a title, not read and not graded. The scan may record it; it may
    never let it change `current_state`, `evidence` or the forecast. If this test ever needs
    relaxing, the change is wrong.
    """
    import shutil
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import trigger_scan as ts

    real = os.path.join(REPO, "systems", "graph", "technologies.json")
    tmp = tmp_path / "technologies.json"
    shutil.copy(real, tmp)
    monkeypatch.setattr(ts, "TECHNOLOGIES", str(tmp))

    before = json.load(open(tmp, encoding="utf-8"))
    fresh = {"TRG-FEP-CRYPTIC-POCKET": [{"id": "MED/TEST", "title": "t", "date": "2026-08-04",
                                         "venue": "v", "url": "u"}]}
    assert ts.write_pending_signals(fresh, "2026-08-05", dry_run=True) == 1
    assert json.load(open(tmp, encoding="utf-8")) == before, "a dry run must write nothing"

    assert ts.write_pending_signals(fresh, "2026-08-05") == 1
    after = json.load(open(tmp, encoding="utf-8"))
    for a, b in zip(after, before):
        for key in ("current_state", "evidence", "forecast", "confidence", "unblocks"):
            assert a.get(key) == b.get(key), f"{a['id']}.{key} changed — the scan must not grade"
    # idempotent: the same paper is not recorded twice
    assert ts.write_pending_signals(fresh, "2026-08-06") == 0


def test_scan_trigger_references_resolve_in_both_directions(graph):
    f = sc.Findings()
    sc.check_scan_interop(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_internal_work_triggers_are_not_expected_to_have_a_technology(graph):
    """An `internal_work` trigger is work THIS program can do, not a capability to wait for.

    Warning on those would be the exact conflation the technology taxonomy exists to prevent — and
    it is how four of them ended up sitting on a watch list, invisible, in the first place.
    """
    with open(os.path.join(REPO, "research", "method-watch-triggers.json"), encoding="utf-8") as fh:
        rows = json.load(fh)["triggers"]
    internal = {t["id"] for t in rows if t.get("trigger_kind") == "internal_work"}
    assert internal, "expected at least one internal_work trigger"
    f = sc.Findings()
    sc.check_scan_interop(graph, f)
    for trg in internal:
        assert not [w for w in f.warns if trg in w and "[X3]" in w], \
            f"{trg} is internal work and must not be flagged as an unwatched capability"


def test_every_capability_is_either_scanned_or_says_why_not(graph):
    """[T3] and [X3] both reach zero — with no fabricated query.

    ⛔ THE POINT IS THAT SILENCE IS NOT ALLOWED AND NEITHER IS A FAKE QUERY. Every TECH-* either names
    a real TRG-* or states in `not_scannable_because` what watches it instead; every scannable TRG-*
    is watched by a TECH-*, so a hit has somewhere to land.
    """
    f = sc.Findings()
    sc.check_technologies(graph, f)
    sc.check_scan_interop(graph, f)
    assert [w for w in f.warns if "[T3]" in w] == [], "\n".join(f.warns)
    assert [w for w in f.warns if "[X3]" in w] == [], "\n".join(f.warns)
    assert [w for w in f.warns if "[X5]" in w] == [], "\n".join(f.warns)


def test_a_disabled_trigger_is_never_described_as_scanned_weekly(graph):
    """The [X3] message was factually WRONG for TRG-PERSES-RDKIT-PATH.

    It printed "is scanned weekly" for a trigger with `scan_enabled: false` whose
    `not_searchable_because` says reopening it buys nothing while pmx serves the avenue. A check that
    misdescribes what it found costs a real investigation to dismiss a fake finding — the failure mode
    MAINTENANCE.md §4 is about.
    """
    with open(os.path.join(REPO, "research", "method-watch-triggers.json"), encoding="utf-8") as fh:
        rows = json.load(fh)["triggers"]
    disabled = {t["id"] for t in rows if not t.get("scan_enabled")}
    assert disabled, "expected at least one disabled trigger"
    f = sc.Findings()
    sc.check_scan_interop(graph, f)
    for trg in disabled:
        assert not [w for w in f.warns if trg in w and "[X3]" in w], \
            f"{trg} has scan_enabled: false and must never be reported as scanned weekly"


def test_not_scannable_because_is_not_a_blanket_escape_hatch(graph):
    """It must stay RARE and always name what watches the dependency instead.

    If this ever covers a large share of the register, the watch list has been silenced rather than
    completed — which is the outcome the field is meant to prevent, not enable.
    """
    techs = graph["technologies"]
    excused = [t for t in techs if t.get("not_scannable_because")]
    assert len(excused) <= 3, \
        f"{len(excused)} of {len(techs)} technologies excuse themselves from the scan — that is a " \
        f"silenced watch list, not a completed one"
    for t in excused:
        why = t["not_scannable_because"]
        assert len(why) >= 40, f"{t['id']} excuses itself in one line and names no alternative"
        assert not t.get("scan_trigger"), \
            f"{t['id']} both names a trigger and excuses itself — one of the two is untrue"


def test_the_antigen_technology_does_not_claim_to_retire_a_permanent_blocker(graph):
    """⭐ TECH-JUNCTION-PMHC unblocks three ROUTES and no BLOCKER, and that is not a modelling slip.

    BLK-ANTIGEN-COLD is a `fundamental_biological_limit` — a fact about what the junction IS. No
    method changes it; what a capability can change is whether that fact stays DECISIVE for the routes
    resting on it. Conflating the two is what [B1] refuses, and the distinction is the reason the
    blocker taxonomy separates `kind` from fan-out at all.
    """
    tech = next(t for t in graph["technologies"] if t["id"] == "TECH-JUNCTION-PMHC")
    blk = next(b for b in graph["blockers"] if b["id"] == "BLK-ANTIGEN-COLD")
    assert blk["permanent"], "premise check: BLK-ANTIGEN-COLD is a permanent blocker"
    assert tech["unblocks"]["blockers"] == [], "a permanent blocker cannot be retired by a technology"
    assert set(tech["unblocks"]["routes"]) == {"RT-TCR-IMMTAC", "RT-JUNCTION-NEOANTIGEN", "RT-VACCINE"}
    assert "TRG-JUNCTION-PHLA" in tech["scan_trigger"], "the trigger it exists to catch"


# ───────────────────────── the generated diagrams ─────────────────────────

MERMAID_BLOCK = re.compile(r"```mermaid\n(.*?)```", re.S)
MM_NODE = re.compile(r'^([A-Za-z0-9_]+)\s*(?:\[\[|\{\{|\(\[|\[|\(|\{)')
MM_EDGE = re.compile(r'^([A-Za-z0-9_]+)\s*(?:--|-\.|==)[^>]*?(?:--|\.-|==)?>\s*([A-Za-z0-9_]+)$')


def _mermaid_blocks():
    import glob
    for p in sorted(glob.glob(os.path.join(SYS, "views", "**", "*.md"), recursive=True)):
        text = open(p, encoding="utf-8").read()
        for m in MERMAID_BLOCK.finditer(text):
            yield os.path.relpath(p, REPO), m.group(1)


def test_every_generated_diagram_parses():
    """⛔ THE GATE THAT MATTERS MOST — because the failure mode is SILENT.

    A mermaid block with an unescaped `"` renders on GitHub as a BLANK SPACE where the diagram should
    be. No error, no warning, nothing that any other check in this repository would notice: the file
    still exists, still has frontmatter, still passes its drift check, still has valid links. The only
    signal is a human opening the page and seeing nothing.

    So the block is checked structurally: a diagram-type header, every node label quoted with no raw
    quote inside it, every edge endpoint declared as a node, and balanced brackets.
    """
    checked, problems = 0, []
    for rel, body in _mermaid_blocks():
        checked += 1
        lines = [l for l in body.splitlines() if l.strip()]
        assert lines, f"{rel}: empty mermaid block"
        if not lines[0].strip().startswith(("flowchart", "graph", "sequenceDiagram")):
            problems.append(f"{rel}: no diagram-type header"); continue
        declared, edges = set(), []
        for ln in lines[1:]:
            s = ln.strip()
            if s.startswith(("classDef", "%%", "subgraph", "end", "style", "linkStyle")):
                continue
            nd = MM_NODE.match(s)
            if nd:
                declared.add(nd.group(1))
                lab = re.search(r'"(.*?)"', s)
                if lab is None:
                    problems.append(f"{rel}: unquoted node label: {s[:60]}")
                elif '"' in lab.group(1):
                    problems.append(f"{rel}: raw quote inside label: {lab.group(1)[:40]}")
                continue
            e = MM_EDGE.match(s)
            if e:
                edges.append((e.group(1), e.group(2))); continue
            problems.append(f"{rel}: unparsed line: {s[:70]}")
        for a, b in edges:
            for n in (a, b):
                if n not in declared:
                    problems.append(f"{rel}: edge endpoint never declared: {n}")
        if body.count("[") != body.count("]") or body.count("{") != body.count("}"):
            problems.append(f"{rel}: unbalanced brackets")
    assert checked >= 45, f"only {checked} diagrams found — the generator has stopped emitting them"
    assert not problems, "\n".join(problems[:15])


def test_mermaid_label_neutralises_the_characters_that_break_a_block():
    """`esc()` escapes table pipes and is WRONG here — mermaid cares about entirely different ones."""
    f = sc.mermaid_label
    assert '"' not in f('a "quoted" thing')
    assert "#quot;" in f('a "quoted" thing')
    for ch in "[]{}()<>|\\":
        assert ch not in f(f"danger {ch} here"), f"{ch!r} survived"
    assert "\n" not in f("two\nlines") and "  " not in f("two   spaces")
    assert len(f("x" * 200, width=40)) <= 40


def test_mermaid_labels_are_safe_on_the_REAL_worst_case_strings(graph):
    """Not invented hazards — the actual longest and punctuation-heaviest strings in the graph today."""
    worst = []
    for coll in ("strategies", "routes", "blockers", "technologies"):
        for row in graph[coll]:
            for k in ("title", "display_name", "name"):
                if row.get(k):
                    worst.append(row[k])
    assert worst, "premise check: the graph has labelable strings"
    for s in worst:
        out = sc.mermaid_label(s)
        assert not re.search(r'["\[\]{}()<>|\\\n]', out), f"unsafe label from {s[:60]!r} -> {out!r}"


def test_the_landscape_draws_only_the_cross_cutting_blockers(graph):
    """'Favor clarity over detail' with a defensible edge, not an aesthetic one.

    A blocker on one family is that family's business; a blocker on six is the portfolio's shape. The
    count is RE-DERIVED here from the graph rather than compared against a typed constant, so the test
    still holds when a blocker's fan-out changes.
    """
    fams = sc._families_per_blocker(graph)
    expected = {b for b, f in fams.items() if len(f) >= 2}
    local = {b for b, f in fams.items() if len(f) == 1}
    assert expected and local, "premise check: the graph has both cross-cutting and local blockers"
    body = "\n".join(sc.diagram_l0(graph))
    for b in expected:
        assert sc.mm_id(b) in body, f"{b} spans {len(fams[b])} families and is missing from the landscape"
    for b in local:
        assert sc.mm_id(b) not in body, f"{b} holds down one family and must not be on the landscape"
    assert str(len(local)) in body, "the view must SAY how many blockers it left out"


def test_the_two_rankings_on_L0_come_from_one_derivation(graph):
    """The landscape ranks by FAMILIES; the table below it ranks by ROUTES — and they disagree.

    ⚠ THAT DISAGREEMENT IS REAL AND IT LOOKED LIKE AN ERROR. `BLK-NO-EMC-DATA` holds the most routes
    (15) and spans only 5 families; `BLK-NO-WET-LAB` holds 6 routes across 6 families. A reader meeting
    "6" in the diagram and "15" three inches below it in the table concludes the page contradicts
    itself and stops trusting it — so both now state their unit, and the table carries BOTH columns.

    What this test protects is that the two numbers are one derivation, not two: the family count in the
    diagram and the family count in the table must both come from `_families_per_blocker`, or they will
    drift into an actual contradiction rather than an apparent one.
    """
    fams = sc._families_per_blocker(graph)
    view = sc.render_l0(graph)
    for b in graph["blockers"]:
        if not b["inherited_by"]:
            continue
        n_fam, n_routes = len(fams.get(b["id"], [])), len(b["inherited_by"])
        row = [l for l in view.splitlines() if l.startswith(f"| **{b['id']}** |")]
        assert row, f"{b['id']} holds {n_routes} route(s) and is missing from the L0 table"
        cells = [c.strip() for c in row[0].split("|")]
        assert cells[3] == str(n_routes) and cells[4] == str(n_fam), \
            f"{b['id']}: table says routes={cells[3]} families={cells[4]}, graph says {n_routes}/{n_fam}"
    assert "ranks by FAMILIES" in view and "Ranked by ROUTES" in view, \
        "both rankings must name their unit — an unlabelled axis reads as a contradiction"


def test_a_permanent_blocker_is_never_drawn_with_a_way_out(graph):
    """⛔ The taxonomy's central distinction, enforced in the artifact read at a glance.

    A `fundamental_biological_limit` is a fact about what the objects ARE. `[B1]` already errors if a
    technology claims to retire one. Drawing it identically to a retirable blocker — or worse, with an
    incoming 'would retire' edge — would reintroduce exactly that conflation visually.
    """
    perm = {b["id"] for b in graph["blockers"] if b["permanent"]}
    assert perm, "premise check: the graph has at least one permanent blocker"
    for r in graph["routes"]:
        body = "\n".join(sc.diagram_l2(r, graph))
        for b in perm:
            if sc.mm_id(b) not in body:
                continue
            assert f'{sc.mm_id(b)}[["' in body, f"{b} is permanent and must use the double-walled shape"
            assert f"-.-> {sc.mm_id(b)}" not in body, \
                f"{b} is permanent — nothing retires it, so it can have no incoming 'would retire' edge"


def test_diagram_generation_is_deterministic(graph):
    """The views are drift-checked by re-render, so a dict-ordering dependence turns CI red later, on
    an unrelated commit, with a diff nobody can explain."""
    assert sc.diagram_l0(graph) == sc.diagram_l0(graph)
    for s in graph["strategies"]:
        assert sc.diagram_l1(s, graph) == sc.diagram_l1(s, graph)
    for r in graph["routes"][:8]:
        assert sc.diagram_l2(r, graph) == sc.diagram_l2(r, graph)


def test_an_empty_case_says_so_instead_of_emitting_an_empty_block(graph):
    """A route with no blockers and a family with none shared are both real and both common."""
    bare = [r for r in graph["routes"]
            if not r.get("blockers_inherited") and not r.get("blockers_retired")]
    for r in bare:
        body = "\n".join(sc.diagram_l2(r, graph))
        assert "```mermaid" not in body, "an empty diagram is worse than a sentence"
        assert "no dependency structure" in body, f"{r['id']} renders nothing at all"
    unshared = [s for s in graph["strategies"] if not s.get("shared_blockers") and s.get("routes")]
    assert unshared, "premise check: most families have no shared blocker"
    for s in unshared:
        body = "\n".join(sc.diagram_l1(s, graph))
        assert "No blocker points at the family node" in body, \
            f"{s['id']} has no shared blocker and must say what that MEANS, not stay silent"


def test_meaning_is_never_carried_by_colour_alone():
    """These render in light and dark on GitHub, and readers are not all trichromatic.

    Shape and edge style carry the meaning; the classDefs deliberately set no `fill`, because a fill
    picked for one theme disappears in the other.
    """
    body = "\n".join(sc.MM_CLASSDEF)
    assert "fill" not in body, "a fill chosen for one theme vanishes in the other"
    assert "stroke-width" in body, "shape/weight must be doing the work"


# ───────────────────────── documents and links (§2) ─────────────────────────

def test_every_hand_written_document_has_frontmatter(graph):
    f = sc.Findings()
    sc.check_documents(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_every_document_id_resolves_to_exactly_one_file(graph):
    """[D6] — the invariant the bulk backfill broke.

    `slug()` derived ids from basenames, so seven files ended up sharing two ids. `check_ids_unique`
    never saw it: that covers the twelve graph collections, and document ids live in frontmatter.
    """
    f = sc.Findings()
    sc.check_doc_ids(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_the_id_scan_reaches_into_the_archive(graph):
    """⚠ Frontmatter ENFORCEMENT stops at `archive/`; UNIQUENESS must not.

    An archived document keeps its id. If the scan skipped the archive, a new file taking an archived
    document's name would mint a duplicate that surfaced only as a broken cross-reference — which is
    the failure mode this whole namespace exists to remove.
    """
    assert "archive/" in sc.DOC_SKIP, "premise check: enforcement does skip the archive"
    assert "archive/" not in sc.ID_SKIP, "the id scan must NOT skip the archive"
    scanned = {rel for rel, _ in sc._walk_md(sc.ID_SKIP)}
    assert any(r.startswith("archive/") for r in scanned), "no archived document was scanned for ids"


def test_the_slug_tie_break_is_root_wins_then_path_qualify():
    """CONVENTIONS.md §1.2 — stated so the next duplicate is renamed the same way, not a new way."""
    sys.path.insert(0, SYS)
    import backfill_frontmatter as bf
    rels = ["README.md", "research/README.md", "results/README.md",
            "METHODOLOGY.md", "research/hypotheses/METHODOLOGY.md", "AGENTS.md"]
    assert bf.slug("README.md", rels) == "DOC-README"                     # root keeps the bare id
    assert bf.slug("research/README.md", rels) == "DOC-RESEARCH-README"   # nested is path-qualified
    assert bf.slug("results/README.md", rels) == "DOC-RESULTS-README"
    assert bf.slug("research/hypotheses/METHODOLOGY.md", rels) == "DOC-RESEARCH-HYPOTHESES-METHODOLOGY"
    assert bf.slug("AGENTS.md", rels) == "DOC-AGENTS"                     # unshared basename: untouched
    assert len({bf.slug(r, rels) for r in rels}) == len(rels)


def test_the_backfill_compares_against_every_document_not_just_its_own_batch():
    """A new document can clash with one that ALREADY carries frontmatter.

    `targets()` returns the backfill set AND the full id-bearing set. Deriving uniqueness from the
    backfill set alone would reintroduce the collision on the very next document added, because the
    182 already-backfilled files would be invisible to the comparison.
    """
    sys.path.insert(0, SYS)
    import backfill_frontmatter as bf
    todo, all_rels = bf.targets()
    assert len(all_rels) > len(todo), "the comparison set must be wider than the write set"
    # Both already carry frontmatter, so neither is in `todo` — and both must still be compared against.
    assert "systems/POLICY-evidence.md" in all_rels
    assert "research/hypotheses/METHODOLOGY.md" in all_rels


def test_a_supersession_names_its_successor(graph):
    """[D7] — a supersession with nothing to redirect to is unfalsifiable."""
    f = sc.Findings()
    sc.check_documents(graph, f)
    assert [e for e in f.errors if "[D7]" in e] == [], "\n".join(f.errors)


def test_a_load_bearing_document_cannot_declare_itself_retired(graph, monkeypatch):
    """[D8] — and its two inputs must be non-empty, or the check is inert.

    ⚠ THIS IS THE FAIL-OPEN GUARD. `_pinned_targets()` and `_instruction_paths()` RAISE rather than
    returning an empty set, because a helper answering "nothing depends on anything" would switch
    [D8] off silently — the exact shape `parser_guard.py` exists to catch.
    """
    pinned, instructed = sc._pinned_targets(), sc._instruction_paths()
    assert pinned, "[D8]'s pinned-figures half is inert"
    assert instructed, "[D8]'s project-instruction half is inert"
    # Keep the pinned scientific target and the current instruction target protected.
    assert "research/manuscripts/degrader/nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md" in pinned
    active = "research/autonomy/OPERATING_PROTOCOL.md"
    assert active in instructed
    f = sc.Findings()
    sc.check_documents(graph, f)
    assert [e for e in f.errors if "[D8]" in e] == [], "\n".join(f.errors)
    # Perturb the parsed metadata, never the active document: retirement must be rejected.
    frontmatter = sc._frontmatter
    with open(os.path.join(REPO, active), encoding="utf-8") as source:
        active_id = frontmatter(source.read())["id"]

    def retired_protocol(text):
        metadata = frontmatter(text)
        if metadata and metadata.get("id") == active_id:
            return dict(metadata, status="historical")
        return metadata

    monkeypatch.setattr(sc, "_frontmatter", retired_protocol)
    f = sc.Findings()
    sc.check_documents(graph, f)
    assert any("[D8]" in e and active in e for e in f.errors), f.errors


def test_a_partial_supersession_is_never_classified_as_a_whole_one():
    """The backfill defect that mislabelled three live documents, replayed on the real files.

    ⛔ THE FIX IS NOT A CLEVERER REGEX — a qualifier can be phrased a hundred ways. It is a REFUSAL
    to classify: when a retirement marker sits next to a qualifier, the status stays `live` and the
    ambiguity is handed to a human. Under-claiming is recoverable; a wrong `historical` archives a
    live document, and one of these three is a `pinned-figures.json` target.
    """
    sys.path.insert(0, SYS)
    import backfill_frontmatter as bf
    partial = ["research/manuscripts/degrader/nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md",
               "research/manuscripts/degrader/nr4a3-degrader-strategy-ternary-first.md",
               "research/manuscripts/degrader/nr4a3-degrader-preprint-plan.md"]
    whole = ["research/manuscripts/degrader/nr4a3-degrader-preprint.md",
             "research/manuscripts/degrader/nr4a3-degrader-preprint-si.md"]

    def replay(rel):
        body = open(os.path.join(REPO, rel), encoding="utf-8").read().split("---\n", 2)[2]
        return bf.classify(rel, "\n".join(body.splitlines()[:40]))

    for rel in partial:
        kind, status, _, needs_review = replay(rel)
        assert status == "live", f"{rel} was classified {status}; only PART of it is superseded"
        assert needs_review, f"{rel} must be flagged for a human, not silently passed as live"
    for rel in whole:
        _, status, _, needs_review = replay(rel)
        assert status == "superseded", f"{rel} is wholly retired and must still be classified"
        assert not needs_review
    # A whole-file history with no qualifier must still classify, or the refusal has eaten the signal.
    body = open(os.path.join(REPO, "STRATEGY.md"), encoding="utf-8").read().split("---\n", 2)[2]
    assert bf.classify("STRATEGY.md", "\n".join(body.splitlines()[:40]))[1] == "historical"


def test_a_redirect_stub_stays_at_the_path_it_redirects_from():
    """⭐ Not archived, deliberately. A stub's entire job is to be found at the old path.

    Both were on the archive shortlist: `historical`, tiny, and referenced only by each other. Moving
    one to `archive/` would destroy the one thing it does, to reclaim 48 lines.
    """
    for rel in ("research/manuscripts/degrader/nr4a3-degrader-preprint.md",
                "research/manuscripts/degrader/nr4a3-degrader-preprint-si.md"):
        p = os.path.join(REPO, rel)
        assert os.path.exists(p), f"{rel} was archived — a redirect must stay where the reader looks"
        fm = sc._frontmatter(open(p, encoding="utf-8").read())
        assert fm.get("superseded_by"), f"{rel} redirects to nothing"


def test_no_new_broken_links(graph):
    """A new broken relative link is an error immediately; the pre-existing ones are baselined.

    Same discipline as the frontmatter backfill: record the baseline, fail on regressions. Turning
    120 pre-existing breakages into build failures on day one makes the build permanently red for
    defects that predate the check — and a permanently red build gets ignored.
    """
    f = sc.Findings()
    sc.check_links(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_a_cited_artifact_exists_on_this_branch(graph):
    """[K1] — the class `check_links` structurally cannot see.

    ⭐ MEASURED: 41 artifacts lived only on `modalities-cache`, 24 of them cited from this branch, and
    the relative-link checker had caught ONE. It was not broken — it validates the shape of a Markdown
    link, and this repository cites results as bare backticked filenames in prose. A file that exists
    one ref away is not a broken link; it is a stale fact that reads as a current one.

    This test does not assert zero. It asserts the check is LIVE and still discriminating: it must
    know about real artifacts (so it cannot flag everything) and must only flag names whose producer
    is in the repo (so a plan or a typo is not reported as drift).
    """
    f = sc.Findings()
    sc.check_artifacts(graph, f)
    assert f.errors == [], "\n".join(f.errors)
    flagged = [w for w in f.warns if "[K1]" in w]
    # ⭐ 2026-08-05: this assertion USED TO PASS FOR THE WRONG REASON, and the swap is the point.
    # It read "an artifact with no producer in this repo is a forward reference, not branch drift" —
    # but `nr4a3-5bt-signature.json` was never a forward reference. Its producer step had run on every
    # 5b-T invocation and crashed every time, hidden by a `|| true`. The artifact now EXISTS here, so
    # the check must not flag it because it is PRESENT, and asserting that is strictly stronger than
    # asserting a forward-reference exemption that no longer applies to anything.
    assert os.path.exists(os.path.join(sc.REPO, "research/modalities/nr4a3-5bt-signature.json")), \
        "the V1 signature read is committed here; if it vanished, [K1]'s exemption is not the answer"
    assert not [w for w in flagged if "nr4a3-5bt-signature" in w], \
        "a present artifact must not be reported as cited-and-absent"
    assert len(flagged) < 15, \
        f"{len(flagged)} artifacts cited but absent — that is a drift event, not a residue; check " \
        f"whether a lane branch holds them before assuming they were never produced"


# ───────────────────────── lanes: executed work as modelled state ─────────────────────────

def test_every_lane_the_documents_name_is_registered(graph):
    """⭐ THE LEVEL THE MODEL WAS MISSING, AND WHY IT COST SOMETHING.

    A ROUTE is a strategic option; a REQUIREMENT is what must be TRUE; a LANE is *we ran X, and here is
    how it ended*. Executed work had no object, so "this lane closed" lived only as a struck-through row
    in roadmap prose — and prose is not queryable. An artifact belonging to a lane that closed on
    2026-07-30 was therefore read as a gap to fill on 2026-08-05, at a cost of 88.5 minutes of CI.

    ⚠ The register is ENUMERATED against every `LANE n` in the repository, not trusted. On its first run
    it found LANE-1, named only in a module comment, which the hand survey had missed.
    """
    f = sc.Findings()
    sc.check_lanes(graph, f)
    assert [e for e in f.errors if "[W1]" in e] == [], "\n".join(f.errors)
    assert len(graph["lanes"]) >= 15, "the lane register has shrunk — executed work is going unmodelled"


def test_a_paused_lane_names_what_would_restart_it(graph):
    """[W3] — `held`/`parked` with no gate is indistinguishable from abandonment.

    The two have very different consequences for anything waiting on the lane, so the distinction is
    required rather than inferred. LANE-20 is `held` behind a named pose diagnostic; that is the shape.
    """
    for l in graph["lanes"]:
        if l["state"] in ("held", "parked"):
            assert l.get("gate"), f"{l['id']} is `{l['state']}` and names no gate"
    f = sc.Findings()
    sc.check_lanes(graph, f)
    assert [e for e in f.errors if "[W3]" in e] == [], "\n".join(f.errors)


def test_a_verdict_is_never_encoded_as_a_lane_state(graph):
    """⛔ 'It failed' and 'it is unfinished' must not render alike.

    The state answers one question — *will this lane still produce what it owes?* — so a null result is
    `complete` with the null in `terminus`, exactly like a positive one. LANE-19 closed with the gate
    FAILING on sign and is `complete`; collapsing that into a distinct state would make a finished
    negative look like an outstanding task, which is how dead work gets re-run.
    """
    assert set(sc.LANE_STATE_DISPOSITION) == {"running", "held", "parked", "complete"}
    null_lane = [l for l in graph["lanes"] if l["id"] == "LANE-19"]
    assert null_lane and null_lane[0]["state"] == "complete"
    assert "NO-GO" in null_lane[0]["terminus"], "the null verdict must live in terminus, not the state"


def test_the_model_derives_the_disposition_instead_of_a_human_asserting_it(graph):
    """⭐ THE PAYOFF. An absence resolves by lookup, not by parsing struck-through prose.

    `valb-triangle-chem.json` is registered on LANE-9 as an artifact it owed and never produced. The
    lane is `complete`, so the disposition is `withdrawn` — derived, with the lane's terminus as the
    evidence, and no human assertion anywhere in the chain.
    """
    verdict, lane, entry = sc._lane_verdict_for("valb-triangle-chem.json", graph)
    assert verdict == "withdrawn", "the closed lane must answer for the artifact it never produced"
    assert lane["id"] == "LANE-9" and lane["state"] == "complete"
    assert entry["produced"] is False
    # A lane that could still run must NOT answer `withdrawn`.
    for state, expect in (("running", "expected"), ("held", "expected"), ("parked", "expected")):
        assert sc.LANE_STATE_DISPOSITION[state] == expect


def test_a_written_disposition_may_not_shadow_a_derived_one(graph):
    """[K2] — the shadowing bug, one layer up from the link baseline.

    If a hand-written disposition short-circuits the lane lookup, the two can drift and the stale
    written one wins silently. That is precisely how the link baseline hid `valb-triangle-chem.json`
    from classification in the first place, so the same mistake is refused here by construction.
    """
    f = sc.Findings()
    sc.check_artifacts(graph, f)
    assert [e for e in f.errors if "[K2]" in e] == [], "\n".join(f.errors)
    written = {r["artifact"] for r in
               json.load(open(os.path.join(SYS, "graph", "artifact-refs.json"), encoding="utf-8"))
               ["dispositions"]}
    for art in written:
        assert sc._lane_verdict_for(art, graph)[0] is None, \
            f"{art} is asserted in artifact-refs AND derivable from a lane — two homes for one fact"


def test_absent_is_an_observation_with_three_meanings_not_a_gap(graph):
    """⛔ THE 2026-08-05 ERROR, PINNED. `[K1]` named two causes and there are three.

    It was written the same day 24 artifacts were found stranded on `modalities-cache`, so its message
    named branch drift and "never run" — the two in front of its author — and stopped. The third is
    **the work CLOSED, so the citation is what is wrong**. Reported that way,
    `valb-triangle-chem.json` sent 88.5 minutes of CI at a lane that had closed five days earlier.

    The three license OPPOSITE actions — fetch it, run it, delete the citation — so the message must
    name all three and the check must refuse to let the choice be implied.
    """
    f = sc.Findings()
    sc.check_artifacts(graph, f)
    # ⚠ Scoped to the branch where the model has NO answer. Where a lane answers, [K1] states the
    # derived disposition instead — a menu would be a worse message, not a safer one.
    for w in [x for x in f.warns if "[K1]" in x and "THE MODEL ANSWERS THIS" not in x]:
        for word in ("elsewhere", "expected", "withdrawn"):
            assert word in w, f"[K1] must name the `{word}` disposition; it said: {w[:200]}"
        assert "OBSERVATION, NOT A GAP" in w, "[K1] must not present an absence as a gap"
    assert set(sc.DISPOSITIONS) == {"elsewhere", "expected", "withdrawn"}


def test_the_link_baseline_never_exempts_an_artifact_from_classification():
    """⛔ THE ROOT CAUSE, AND IT WAS DEEPER THAN THE MISSING THIRD DISPOSITION.

    Two registers were describing overlapping sets under different rules. `link-baseline.json` answers
    *is this Markdown link known-broken?* and carries a FREE-PROSE `why`; the disposition register
    answers *what does this absence MEAN?* and requires evidence. `valb-triangle-chem.json` was in both
    — and being in the baseline SKIPPED it past the disposition requirement, so the only thing
    describing it was unchecked prose. That prose is what said "clears with a larger budget".

    A grandfathered link stops `[K0]` failing the build on the LINK. It says nothing about whether the
    ARTIFACT should exist, and that is the question whose wrong answer costs compute.
    """
    src = open(os.path.join(SYS, "systems_check.py"), encoding="utf-8").read()
    body = src.split("def check_artifacts(", 1)[1].split("\ndef ", 1)[0]
    skip = re.search(r"if name in known(.*?):", body)
    assert skip, "could not find check_artifacts' skip condition"
    assert "baseline" not in skip.group(1), \
        "the link baseline must not exempt an artifact from needing a disposition"


def test_every_cited_and_absent_artifact_is_classified(graph):
    """The register is enumerated, not trusted — so it cannot silently stop covering the set."""
    f = sc.Findings()
    sc.check_artifacts(graph, f)
    unanswered = [w for w in f.warns if "[K1]" in w and "THE MODEL ANSWERS THIS" not in w]
    assert not unanswered, (
        "an artifact is cited here and absent, and NEITHER a lane nor the disposition register answers "
        "for it. That is not a gap to fill on sight — decide which of elsewhere/expected/withdrawn it "
        "is, and prefer putting it on the owing lane so the answer is derived:\n" + "\n".join(unanswered))


def test_the_prose_parsing_shortcut_was_replaced_by_the_model():
    """⚠ SUPERSEDED, DELIBERATELY — and the reason is worth keeping.

    The first fix read the roadmap's struck-through "✅ CLOSED" rows and surfaced them as EVIDENCE
    beside an absent artifact. That worked, and it was still prose-matching: it could only ever inform a
    human, never be a fact the model holds, and it would rot the day someone restyled a table.

    Lanes replaced it. `_closed_work_mentioning` is gone; `_lane_verdict_for` answers from state.
    """
    assert not hasattr(sc, "_closed_work_mentioning"), \
        "the prose shortcut is back — an answer the model can hold must not be re-derived from prose"
    assert hasattr(sc, "_lane_verdict_for")

def test_every_disposition_carries_the_evidence_its_kind_demands(graph):
    """[K2] — the register cannot become where warnings go to die.

    Each disposition is a claim someone must be able to check later, and each needs DIFFERENT evidence:
    `elsewhere` must name the ref and argue a second copy would be actively HARMFUL (CLAUDE.md §7: the
    default is to PORT, and "not ported yet" is drift); `expected` must name the work that is open;
    `withdrawn` must name what closed it. A one-line reason cannot carry any of them.

    The refusal has teeth: when [K2] rejects an entry, [K1] fires again for that artifact, so a
    malformed disposition silences nothing.
    """
    path = os.path.join(SYS, "graph", "artifact-refs.json")
    if not os.path.exists(path):
        pytest.skip("no dispositions recorded")
    rows = json.load(open(path, encoding="utf-8"))["dispositions"]
    assert rows, "an empty register should be deleted, not kept"
    for r in rows:
        art, dis = r.get("artifact"), r.get("disposition")
        assert art and dis in sc.DISPOSITIONS, f"{art!r} has disposition {dis!r}"
        for k in ("why", "checked_on") + sc.DISPOSITIONS[dis]:
            assert r.get(k), f"{art} is `{dis}` and is missing `{k}`"
        assert len(r["why"]) >= 60, f"{art} gives no real argument"
    f = sc.Findings()
    sc.check_artifacts(graph, f)
    assert [e for e in f.errors if "[K2]" in e] == [], "\n".join(f.errors)


def test_the_link_baseline_stays_deleted(graph):
    """It reached zero and was deleted on 2026-08-05, which is what its own note said it was for.

    ⛔ AN EMPTY EXEMPTION REGISTER IS WORSE THAN NONE. Nothing left to exempt, a standing invitation to
    add a line instead of fixing a link, and its loader guarded on `os.path.exists` — so deleting the
    file by accident would have switched every exemption to 'passes' without a word. That is the
    fail-open shape `parser_guard` exists to catch.

    ⚠ The two entries it ever held are why: each carried a confident FREE-PROSE reason that nothing
    could check, and each was wrong. One blamed a probe that had run and committed to another branch;
    the other called rung 5b-T NOT STARTED when it had run and its signature step had failed silently
    behind a `|| true`. Full accounting: systems/MIGRATION.md §3.8.
    """
    path = os.path.join(SYS, "graph", "link-baseline.json")
    assert not os.path.exists(path), \
        "link-baseline.json is back — a link is either fine or an error, and an artifact's absence is " \
        "answered by a lane's produces[] or artifact-refs.json, both of which require evidence"
    f = sc.Findings()
    sc.check_links(graph, f)
    assert not [e for e in f.errors if "[K0]" in e]
    assert any("[K0]" in i for i in f.infos), "the link count must still print — a checker silently " \
                                              "checking zero links is the fail-open shape"


def test_a_preregistration_is_never_archived():
    """A prereg's entire value is that it was written before the result."""
    import glob
    for p in glob.glob(os.path.join(REPO, "archive", "**", "*.md"), recursive=True):
        text = open(p, encoding="utf-8", errors="ignore").read()
        assert "prereg" not in os.path.basename(p).lower(), f"{p} looks like a preregistration"
        assert "status: immutable" not in text[:600], f"{p} is marked immutable and must not be archived"


# ───────────────── the SysML `verify` relation and the edge register ─────────────────

def test_serves_and_serves_derived_are_gone(graph):
    """⛔ THREE FIELDS FOR ONE RELATION, AND THE THIRD WAS READ BY NOTHING.

    `requirement.served_by` and `instrument.serves` were both ASSERTED — the same edge written from
    both ends — and `instrument.serves_derived` computed a third copy that no renderer, check or test
    consumed. 11 of 30 instruments disagreed with the requirement register and six held free prose
    ("the ATR route's structural precondition") in a field the other rows used for identifiers.

    SysML's `verify` has exactly one asserted direction and one derived inverse. Adopting that SHAPE is
    what collapsed them; the name came along with it.
    """
    for i in graph["instruments"]:
        assert "serves" not in i, f"{i['id']} still asserts `serves`"
        assert "serves_derived" not in i, f"{i['id']} still carries the dead `serves_derived`"
        assert isinstance(i.get("verifies"), list), f"{i['id']} has no derived `verifies`"
    for r in graph["requirements"]:
        assert "served_by" not in r, f"{r['id']} still uses the old name"
        assert isinstance(r.get("verified_by"), list)

    # The derived inverse must AGREE with the assertion in both directions, by construction.
    fwd = {(r["id"], v) for r in graph["requirements"] for v in r["verified_by"]}
    rev = {(rid, i["id"]) for i in graph["instruments"] for rid in i["verifies"]}
    assert fwd == rev, f"the derived inverse disagrees: {fwd ^ rev}"


def test_no_relation_field_can_hold_prose(graph):
    """⭐ THE SCHEMA IS WHAT MAKES THE RENAME STICK.

    `requirements` and `instruments` were the two collections with NO schema, and that is not a
    coincidence — it is where the untyped relation between them lived. Sabotage: put back one of the
    six real prose values and the schema must reject it.
    """
    import copy
    g = copy.deepcopy(graph)
    for r in g["requirements"]:
        if r["id"] == "R13":
            r["verified_by"] = ["the exon-level and residue-level definition of every fusion OBJECT"]
    f = sc.Findings()
    sc.check_schemas(g, f)
    assert any("[S3]" in e and "R13" in e for e in f.errors), \
        "a relation field that accepts a sentence is how eleven disagreements accumulated unnoticed"


def test_the_control_state_enum_is_closed(graph):
    """`mixed` was in use and enumerated nowhere. Sabotage with a sixth value; it must be rejected."""
    import copy
    g = copy.deepcopy(graph)
    g["instruments"][0]["known_answer_control"]["state"] = "mostly"
    f = sc.Findings()
    sc.check_schemas(g, f)
    assert any("[S3]" in e for e in f.errors), "a vague control state must not be writable"


def test_every_edge_in_the_model_is_declared(graph):
    """[X1]: an edge the register does not name fails the build.

    ⚠ AN EDGE IS DETECTED STRUCTURALLY — a key one of whose values IS a modelled id — not by name. The
    first draft enumerated non-edge keys by hand and produced 30 false errors on its first run (`path`,
    `workflow`, `statement_about`, `citation`). A checker that cries wolf gets switched off.
    """
    f = sc.Findings()
    sc.check_relations(graph, f)
    assert [e for e in f.errors if "[X1]" in e or "[X2]" in e] == [], "\n".join(f.errors)

    reg = json.load(open(os.path.join(SYS, "graph", "relations.json"), encoding="utf-8"))
    assert reg["_sysml_stereotypes_not_used"], \
        "the stereotypes deliberately NOT adopted are half the answer — without them the next reader " \
        "re-asks whether everything should be `trace`"
    for rel in reg["relations"]:
        assert rel["on"] and rel["to"] and rel["why"], rel["key"]
        assert isinstance(rel["asserted"], bool)
        assert len(rel["why"]) > 40, f"{rel['key']} is declared with no reason"
        assert rel["sysml"] in ("verify", "allocate", "refine", "derive", "domain"), rel["sysml"]


def _graph_copy(tmp_path, monkeypatch, collection, mutate):
    """A whole `systems/graph/` on scratch disk, with one collection mutated, wired into `sc`.

    ⛔⛔ THE TWO TESTS BELOW USED TO MUTATE THE LIVE TRACKED FILES AND RESTORE THEM IN A `finally`.
    That is the shape `tracked_tree_guard` refuses, and its refusal names why: under xdist another
    worker reads the file WHILE it is mutated, and a restore that loses leaves an invented value in
    a tracked artifact with the suite reporting only a flake (AUT-PD-186, measured 2026-08-29). It
    is also the same window that put 13 inverted claims on `origin/main` in a commit taken during a
    mutation seat (CLAUDE.md §6).
    ⚠ THE RESTORE HERE WAS CORRECT AND THAT IS NOT THE POINT — a correct restore still leaves the
    window open, and the cost of the window is paid by whoever commits during it, not by the test.
    ★ `check_relations` re-reads the collections off disk (it enumerates from the SOURCE files
    rather than the derived graph, on purpose), so repointing `sc.GRAPH` at a copy is enough — and
    `sc.RELATIONS` is computed from `GRAPH` at import, so it has to be repointed too or the register
    would still be read from the real tree.
    """
    dst = tmp_path / "graph"
    shutil.copytree(os.path.join(SYS, "graph"), dst)
    target = dst / f"{collection}.json"
    rows = json.loads(target.read_text(encoding="utf-8"))
    mutate(rows)
    target.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setattr(sc, "GRAPH", str(dst))
    monkeypatch.setattr(sc, "RELATIONS", str(dst / "relations.json"))
    return dst


def test_an_undeclared_edge_fails_the_build(graph, tmp_path, monkeypatch):
    """Sabotage: add a new id-valued key nobody declared."""
    _graph_copy(tmp_path, monkeypatch, "blockers",
                lambda rows: rows[0].__setitem__("caused_by_route", [graph["routes"][0]["id"]]))
    f = sc.Findings()
    sc.check_relations(graph, f)
    assert any("[X1]" in e and "caused_by_route" in e for e in f.errors), \
        "a new relation must not be able to appear unnamed"


def test_a_derived_edge_may_not_be_hand_written(graph, tmp_path, monkeypatch):
    """[X2]: a computed fact with a written copy is rule 1's failure mode — the two drift silently."""
    _graph_copy(tmp_path, monkeypatch, "instruments",
                lambda rows: rows[0].__setitem__("verifies", ["R1"]))
    f = sc.Findings()
    sc.check_relations(graph, f)
    assert any("[X2]" in e and "verifies" in e for e in f.errors)


def test_the_sabotage_helper_leaves_the_real_tree_untouched(tmp_path, monkeypatch):
    """⛔ THE CONTROL THAT MAKES THE TWO ABOVE WORTH HAVING. A helper that silently wrote to the
    tree anyway would pass both of them exactly as the old versions did — the guard is what caught
    this, and a guard is not a substitute for the property being asserted."""
    src = os.path.join(SYS, "graph", "blockers.json")
    before = open(src, encoding="utf-8").read()
    _graph_copy(tmp_path, monkeypatch, "blockers",
                lambda rows: rows[0].__setitem__("caused_by_route", ["RT-ANY"]))
    assert open(src, encoding="utf-8").read() == before, \
        "the sabotage was applied to the live tracked file, not to the copy"
    assert sc.GRAPH != os.path.join(SYS, "graph") and str(tmp_path) in sc.RELATIONS


def test_a_lane_may_not_name_a_requirement_in_free_text(graph):
    """[X6] bounds the licence `lane.serves` is given.

    It stays prose because a lane's target is a RUNG as often as an instrument, and rungs are not
    modelled — typing it would mean inventing a collection to point at. But a REQUIREMENT is modelled,
    so the moment `serves` names one, the relation it wants is `verified_by`, and leaving it as prose
    recreates the two-homes problem the reconciliation removed.
    """
    import copy
    g = copy.deepcopy(graph)
    g["lanes"][0]["serves"] = ["R11"]
    f = sc.Findings()
    sc.check_relations(g, f)
    assert any("[X6]" in e for e in f.errors)


def test_a_withdrawal_notice_is_not_a_citation(graph):
    """⛔ [K1] COUNTED A MENTION AS A CITATION, AND WARNED AT DOCUMENTS THAT HAD ALREADY COMPLIED.

    `valb-closure-triangle-pregate-2026-07-25.md` says in three places that the citation IS withdrawn;
    `systems/MAINTENANCE.md` names the artifact only to describe the incident it caused. Both read as
    live citations, so the warning asked for something already done — and a warning nobody can close is
    how the actionable ones get skimmed past.

    ⚠ NOT AN EXEMPTION LIST. It is subtracted from the ENUMERATED citers, so a new document citing the
    artifact still fires.
    """
    import copy
    entry = [p for l in graph["lanes"] if l["id"] == "LANE-9"
             for p in l["produces"] if p["artifact"] == "valb-triangle-chem.json"][0]
    assert entry["produced"] is False and entry["withdrawn_in"], "the withdrawal must be modelled"

    f = sc.Findings()
    sc.check_artifacts(graph, f)
    assert not [w for w in f.warns if "valb-triangle-chem" in w], "\n".join(f.warns)
    assert any("valb-triangle-chem" in i for i in f.infos), "closed is not the same as unreported"

    # Sabotage: a lane that forgets one citer must warn about exactly that citer.
    g = copy.deepcopy(graph)
    for l in g["lanes"]:
        for p in l.get("produces", []):
            if p["artifact"] == "valb-triangle-chem.json":
                p["withdrawn_in"] = p["withdrawn_in"][:1]
    f = sc.Findings()
    sc.check_artifacts(g, f)
    assert any("[K1]" in w and "valb-triangle-chem" in w for w in f.warns), \
        "a citer not on the list must still fire — otherwise this is an off switch"


def test_every_complete_lane_is_dated(graph):
    """A verdict nothing can date is a verdict nothing can call stale.

    All three undated lanes were dated on 2026-08-05 from DOCUMENTS, never from commit timestamps — a
    git date says when a file was written, which for a lane doc is routinely days after the lane closed.
    """
    for l in graph["lanes"]:
        if l["state"] == "complete":
            assert l.get("closed_on"), f"{l['id']} is complete with no date"
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", l["closed_on"]), l["id"]


def test_an_instrument_that_cannot_license_is_not_cited_as_support(graph):
    """[V3]: a passing control is not enough, and this found a real mis-filing.

    RT-MONOVALENT listed INS-MONOVALENT-REACH under `support` while its own route document says the
    test 'came back against the route' and 'Reach can refute a route; it can never license one'.
    """
    f = sc.Findings()
    sc.check_instrument_support(graph, f)
    assert [e for e in f.errors if "[V3]" in e] == [], "\n".join(f.errors)

    import copy
    g = copy.deepcopy(graph)
    for r in g["routes"]:
        if r["id"] == "RT-MONOVALENT":
            r["instruments"]["support"] = ["INS-MONOVALENT-REACH"]
    f = sc.Findings()
    sc.check_instrument_support(g, f)
    assert any("[V3]" in e for e in f.errors), \
        "an instrument that inherits limits it cannot clear must not read as support"


def test_every_produced_artifact_is_registered(graph):
    """[W5]: the two artifact namespaces must meet somewhere.

    ⛔ THEY COVERED DISJOINT SETS AND IT WAS WRITTEN DOWN RATHER THAN FIXED. `lane.produces[]` names a
    FILENAME on purpose — check_artifacts asks "does this file exist on this branch?", which is a
    filesystem question and the one branch drift makes invisible. `artifacts.json` names `ART-*` ids
    with a path, a producer and a workflow. Twelve artifacts were registered and NONE of the six a lane
    produced, so nothing recorded who produced a lane's output or which ref it went to.

    ⚠ relations.json had recorded this as "a real and stated gap … real data, not a rename." Every
    field was findable in minutes. A recorded observation with no owner is the "watching" costume
    CLAUDE.md §4 forbids — either you looked, or you deferred a free answer and called it a decision.
    """
    f = sc.Findings()
    sc.check_lanes(graph, f)
    assert [w for w in f.warns if "[W5]" in w] == [], "\n".join(f.warns)

    import copy
    g = copy.deepcopy(graph)
    g["artifacts"] = [a for a in g["artifacts"] if a["id"] != "ART-SELCAL-VERDICT"]
    f = sc.Findings()
    sc.check_lanes(g, f)
    assert any("[W5]" in w and "selcal-verdict" in w for w in f.warns), \
        "unregistering a produced artifact must fire, or this is decoration"


def test_an_unproduced_artifact_needs_no_registration(graph):
    """The exemption is exact: no file, no path, nothing to register.

    `valb-triangle-chem.json` was owed by LANE-9 and never produced. Its absence IS the fact, and
    check_artifacts derives `withdrawn` from `produced: false` — registering a path that will never
    exist would be the fabricated record CLAUDE.md §4(b) warns about.
    """
    paths = {a.get("path", "").rsplit("/", 1)[-1] for a in graph["artifacts"]}
    assert "valb-triangle-chem.json" not in paths
    f = sc.Findings()
    sc.check_lanes(graph, f)
    assert not [w for w in f.warns if "valb-triangle-chem" in w]


def test_the_github_directory_is_not_skipped_as_if_it_were_dot_git():
    """⛔ `.github`.startswith(`.git`) IS TRUE, AND THREE WALKS RELIED ON THAT PREFIX.

    check_documents, check_lanes and check_links each tested
    `rel_root.startswith((".git", "node_modules", ".pytest_cache"))` — which silently excluded the
    ENTIRE `.github/` tree from all three. Measured 2026-08-05: un-skipping it immediately surfaced
    LANE-8, named in `.github/workflows/fusion-cpu-extras.yml` and absent from the lane register — the
    exact class of unmodelled executed work the lane collection exists to make visible, hidden by a
    string prefix.

    ⚠ The second half is the one that motivated the change: the prefix ALSO failed to skip a real cache
    in a subdirectory, so `research/modalities/.pytest_cache/README.md` turned the build red for missing
    frontmatter on a file pytest wrote. One bug, both directions — too broad at the root and too narrow
    below it, which is what a prefix test does to a path.
    """
    assert ".github/workflows".startswith(".git"), "the trap itself, stated"
    assert not sc._is_transient(".github/workflows"), \
        "`.github` must be walked — it holds the workflows that name lanes and produce artifacts"
    assert not sc._is_transient(".github")
    for d in (".git", ".git/objects", "node_modules", "research/modalities/.pytest_cache",
              "a/b/__pycache__", ".venv/lib", ".worktrees/ci/research", ".cache/research-runs"):
        assert sc._is_transient(d), f"{d} is machinery and must be skipped at ANY depth"


def test_lane_enumeration_actually_reaches_the_workflows(graph):
    """The corollary: a lane named only in a workflow must be found.

    LANE-1 was already the proof that a lane can live in a code comment; LANE-8 is the proof that it
    can live in a workflow, and that the enumeration was not reaching them.
    """
    ids = {l["id"] for l in graph["lanes"]}
    assert "LANE-8" in ids, "LANE-8 is named in .github/workflows/fusion-cpu-extras.yml"
    f = sc.Findings()
    sc.check_lanes(graph, f)
    assert [e for e in f.errors if "[W1]" in e] == [], "\n".join(f.errors)


def test_a_link_checker_that_strips_the_fragment_proves_the_cheaper_half(graph):
    """[K2]: the FILE existing says nothing about the SECTION.

    ⛔ MD_LINK read `(?:#[^)\\s]*)?` — it MATCHED the anchor and threw it away. So every
    `file.md#section` link was validated as `file.md`, and 50 dead anchors passed, including 24 to
    `#open-decisions`, a heading the roadmap's own §0.7 calls FROZEN and "cited by number in 30 files".

    ⚠ AND IT COMPOUNDED WITH TWO OTHER BLIND SPOTS, which is why none was noticed:
      · [P2] inspected only `row["owner"]` and `row["provenance"]["owner"]`, so `grade.owner` anchors
        were never checked at all — `RT-FAP-RLT` asserted `#2` against a heading whose slug is
        `2-fap-targeted-radioligand-therapy-fapi-rlt--emerging-plausibly-applies`;
      · the generated L2 view rendered that bad anchor into a link, which [K1] then declared fine.
    Three checks in a row, each verifying the half it could see.
    """
    f = sc.Findings()
    sc.check_links(graph, f)
    assert [e for e in f.errors if "[K2]" in e] == [], "\n".join(f.errors)
    assert any("anchors" in i for i in f.infos), "the anchor count must print — it is what proves the " \
                                                 "check ran over more than zero anchors"


def test_every_owner_anchor_at_any_depth_is_checked(graph):
    """[P2] must find a `{file, anchor}` wherever it sits, not in the two places it used to look."""
    f = sc.Findings()
    sc.check_pointers(graph, f)
    assert [e for e in f.errors if "[P" in e] == [], "\n".join(f.errors)

    found = {w for r in graph["routes"] for w, _o in sc._owner_blocks(r)}
    assert "grade/owner" in found, "grade.owner is the block that was invisible; the walk must reach it"

    import copy
    g = copy.deepcopy(graph)
    for r in g["routes"]:
        if (r.get("grade") or {}).get("owner"):
            r["grade"]["owner"]["anchor"] = "#no-such-heading-anywhere"
            break
    f = sc.Findings()
    sc.check_pointers(g, f)
    assert any("[P2]" in e and "grade/owner" in e for e in f.errors)


def test_the_row_selector_convention_is_not_reported_as_a_broken_anchor():
    """`#heading|row-selector` addresses a ROW inside a section; only the heading half is a GitHub
    anchor. Validating the whole string called nine live pointers broken on the widened check's first
    run — a correct check earning a reputation for crying wolf."""
    p = os.path.join(REPO, "research/manuscripts/program/emc-post-degrader-options.md")
    assert sc.anchor_resolves(p, "#2--the-ranked-list|tier1-rank2")
    assert sc.anchor_resolves(p, "#2--the-ranked-list")
    assert not sc.anchor_resolves(p, "#2--the-ranked-list-that-does-not-exist|tier1-rank2")


def test_the_plan_view_rehomes_anchors_without_touching_the_lossless_proof(graph):
    """Two things that must both stay true, and the obvious fix broke one of them.

    THE ORDERED PLAN was lifted out of the roadmap VERBATIM, and `extract_plan.py` refuses to write
    unless its render matches the source byte for byte. But a link reading `](#101--open-rows-…)` meant
    *this document, further down* — and "this document" changed, so 26 links in the generated view
    pointed at headings it does not have.

    ⛔ Re-homing them inside `render_plan_body` fixed the view and QUIETLY WEAKENED THE PROOF, which
    still passed. The rewrite belongs on the way into the VIEW; the body stays verbatim.
    """
    plan = graph.get("plan") or {}
    body = sc.render_plan_body(plan)
    for b in plan["blocks"]:
        if b["kind"] == "raw":
            assert b["text"] in body, "render_plan_body must stay byte-verbatim"

    view = sc.render_plan(graph)
    assert "](#" not in view.split("---", 2)[-1] or \
        "nr4a3-program-map.md#" in view, "same-doc anchors must be re-homed in the view"
    assert "](../../research/manuscripts/nr4a3-program-map.md#" in view


def test_slugify_matches_github_where_it_used_to_diverge():
    """Two divergences, both MEASURED against github-slugger@2.0.0 rather than reasoned about.

    ⛔ EACH ONE MADE THE CHECKER CALL A WORKING LINK BROKEN, which is the failure mode that gets a
    checker switched off — this file's own docstrings say so twice, about SMILES strings and about
    leading hyphens.

    1. A MARKDOWN LINK IN A HEADING. GitHub renders it and slugs the TEXT; stripping only the bracket
       characters kept the URL too, so `## GPU economics (full provenance in
       [pricing.md](../compute/pricing.md))` yielded `…-in-pricingmdcomputepricingmd` against a real
       anchor of `…-in-pricingmd`. The roadmap's own §0.7 index linked to it correctly.
    2. SUPERSCRIPT DIGITS. Python's `\\w` keeps U+2076 (`'⁶'.isalnum()` is True, category `No`);
       github-slugger deletes it, so `10⁶ ARTIFACT` anchors as `10-artifact`.

    ⚠ `Lm` IS DELIBERATELY NOT DROPPED. `ⁿ` and `ʰ` are letter modifiers and GitHub keeps them —
    widening the filter to every superscript-looking codepoint would trade one wrong answer for another.
    """
    assert sc.slugify("## GPU economics (full provenance in [pricing.md](../compute/pricing.md))") == \
        "gpu-economics-full-provenance-in-pricingmd"
    assert sc.slugify("## 10. RE-ENUMERATED ON THE CORRECTED 10⁶ ARTIFACT") == \
        "10-re-enumerated-on-the-corrected-10-artifact"
    assert "n" in sc.slugify("## xⁿ notation"), "Lm modifiers are kept by GitHub and must be kept here"
    # The properties the existing docstrings already promise, held so a future edit cannot lose them.
    assert sc.slugify("### 2 · THE RANKED LIST") == "2--the-ranked-list", "· leaves its two spaces"
    assert not sc.slugify("## Plain heading").startswith("-"), "leading # marks must be stripped"


def test_a_dead_code_pointer_still_fires_after_the_external_allowance(graph):
    """[K3] must not have become an off switch.

    `CODE_CITE_CLEARED` lets a document say a name is DELETED, RENAMED or belongs to an EXTERNAL
    repository — all three are legitimate reasons a `.py`/`.yml` this repo names is not a file it has,
    and the first draft flagged a row whose own text read "`alarm_issue.py` deleted".

    ⛔ THE PHRASE MUST BE ON THE LINE, which means a human wrote the reason beside the citation. A name
    nobody has explained still fires — which is how CLAUDE.md §6's three phantom exemplars were found.
    """
    f = sc.Findings()
    sc.check_code_citations(graph, f)
    assert [w for w in f.warns if "[K3]" in w] == [], "\n".join(f.warns)

    import tempfile
    d = os.path.join(REPO, "research", "modalities")
    probe = os.path.join(d, "k3-probe-DELETEME.md")
    try:
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("---\nid: DOC-K3-PROBE\ntitle: probe\nkind: memo\nstatus: live\n"
                     "purpose: probe\nscope: probe\naudience: [maintainers]\n"
                     "last_verified: unverified\n---\n\nRun `no_such_module_anywhere.py` to do the thing.\n")
        f = sc.Findings()
        sc.check_code_citations(graph, f)
        assert any("no_such_module_anywhere.py" in w for w in f.warns), \
            "an unexplained dead code pointer must still fire"

        # ...and the SAME citation, with a reason beside it, must not.
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("---\nid: DOC-K3-PROBE\ntitle: probe\nkind: memo\nstatus: live\n"
                     "purpose: probe\nscope: probe\naudience: [maintainers]\n"
                     "last_verified: unverified\n---\n\nUpstream's `no_such_module_anywhere.py` "
                     "(not ours) does the thing.\n")
        f = sc.Findings()
        sc.check_code_citations(graph, f)
        assert not any("no_such_module_anywhere.py" in w for w in f.warns), \
            "a citation whose line explains the absence is not a dead pointer"
    finally:
        if os.path.exists(probe):
            os.remove(probe)


# ───────── the document contract, the hierarchy's bottom, and the ordinal ─────────
#
# Added 2026-08-06. Three defects, one shape: a rule that was WRITTEN DOWN and enforced by nothing,
# so it drifted from what the repository actually did and nobody could tell.


def test_every_document_frontmatter_is_valid_yaml():
    """⛔ THE HAND-ROLLED PARSER CANNOT FAIL, WHICH IS WHY 24 FILES GOT IN.

    `_frontmatter` partitions on the first `:` and returns a dict no matter what it was handed. Under
    it, 23 documents carried `title: Protocol: systematic review …` — an unquoted colon, which is not
    valid YAML — and two carried a `purpose` beginning `**`, a YAML alias token, salvaged from bolded
    prose by the backfill. Every one read as fine. The whole premise of the frontmatter is that agents
    which did not write this repository can read it; a `yaml.safe_load` failed on 13 % of the corpus.
    """
    bad = []
    for rel, text in sc._walk_md(sc.DOC_SKIP):
        fmv, err = sc._yaml_frontmatter(text)
        if err:
            bad.append(f"{rel}: {err}")
    assert bad == [], "\n".join(bad)


def test_the_document_schema_is_actually_applied(graph):
    """⭐ IT WAS NOT, FOR THE WHOLE OF ITS EXISTENCE.

    `document.schema.json` was loaded by SchemaSet, checked to be a well-formed schema, and applied to
    no collection — while `check_documents` enforced a shorter hardcoded key list that never looked at
    `level` or `kind`. Two homes for one contract; four measured disagreements by the time anyone
    joined them up. This test fails if the wiring is ever removed.
    """
    f = sc.Findings()
    sc.check_document_frontmatter(graph, f)
    assert f.errors == [], "\n".join(f.errors)
    assert any("[D11]" in i and "hierarchy census" in i for i in f.infos), \
        "the census must be REPORTED — it is what replaced the fabricated `~n` column in ARCHITECTURE.md"


def test_a_document_declaring_an_unknown_level_fails(tmp_path, graph):
    """`level` is the field that places a document in the six-level hierarchy, and it was unread."""
    probe = os.path.join(REPO, "research", "d11-probe-DELETEME.md")
    head = ("id: DOC-D11-PROBE\ntitle: probe document\nkind: memo\nstatus: live\n"
            "canonical_for: []\npurpose: probe the level enum is enforced\n"
            "scope: A throwaway probe file; it covers nothing.\naudience: [maintainers]\n"
            "date: 2026-08-06\n"
            "last_verified: unverified\n")
    try:
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write(f"---\n{head}level: L9\n---\n\nbody\n")
        f = sc.Findings()
        sc.check_document_frontmatter(graph, f)
        assert any("d11-probe" in e and "L9" in e for e in f.errors), \
            f"an out-of-enum level must fail: {f.errors}"

        # ...and a legal one must not.
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write(f"---\n{head}level: L4\n---\n\nbody\n")
        f = sc.Findings()
        sc.check_document_frontmatter(graph, f)
        assert not any("d11-probe" in e for e in f.errors), "\n".join(f.errors)
    finally:
        if os.path.exists(probe):
            os.remove(probe)


def test_the_authoring_template_offers_what_the_schema_accepts(graph):
    """CONVENTIONS.md listed 10 of 12 `kind` values, omitting `index` — which 9 live documents use.

    An author or agent following the canonical convention document would have picked a wrong value for
    a common case. The enum has one home now (the schema) and `[D12]` compares them.
    """
    f = sc.Findings()
    sc.check_conventions_template(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_unverified_is_a_legal_freshness_value():
    """⛔ THE SCHEMA FORBADE THE ONE VALUE 126 DOCUMENTS HONESTLY CARRY.

    `last_verified: unverified` says nobody has confirmed the content is still true. Stamping those
    files with a backfill's run date would have claimed a verification nobody performed, in the one
    field whose entire job is to report staleness — so the checker reports the count and the schema
    now admits the value. Had the schema been wired up while still demanding a date, the pressure
    would have been to write the dishonest stamp.
    """
    props = sc.SchemaSet(sc.SCHEMA).docs["document.schema.json"]["properties"]
    assert {"const": "unverified"} in props["last_verified"]["anyOf"]


def test_every_level_links_down_as_well_as_up(graph):
    """⭐ THE HIERARCHY WAS ONE-WAY. Every L2 page linked UP and none linked DOWN.

    All 40 routes carried `instruments`, `objects`, `evidence` and `artifacts` in the graph; the L2
    renderer emitted none of them, so 32 of 40 route pages named no L5 item and `CLM-*` appeared in
    zero generated views. This asserts the down-link exists for every route that has one to make.
    """
    views = sc.all_views(graph)
    assert "L5-evidence-base.md" in views, "L5 must have a view — it is the bottom of the hierarchy"
    missing = []
    for r in graph["routes"]:
        has_edges = any(r.get(k) for k in ("objects", "evidence", "artifacts")) or \
            any((r.get("instruments") or {}).get(k) for k in ("support", "disclosed_failing"))
        if not has_edges:
            continue
        body = views[f"L2-{sc.route_slug(r['id'])}.md"]
        if "L5-evidence-base.md" not in body:
            missing.append(r["id"])
    assert missing == [], f"route pages with L4/L5 edges but no link down: {missing}"


def test_l5_rows_show_who_rests_on_them(graph):
    """`cited_by` is DERIVED from the edges other objects already assert, never written at L5.

    A second asserted home for the same edge is rule 1's failure mode; inverting it cannot disagree.
    """
    deg = next(r for r in graph["routes"] if r["id"] == "RT-DEGRADER")
    for oid in deg["objects"]:
        row = next(o for o in graph["objects"] if o["id"] == oid)
        assert "RT-DEGRADER" in row["cited_by"], f"{oid} does not know the degrader rests on it"


def test_a_claim_must_pin_to_an_artifact_that_exists(graph):
    """A sentence pinned to nothing is unfalsifiable — the finest grain of traceability, checked."""
    f = sc.Findings()
    sc.check_evidence_base(graph, f)
    assert f.errors == [], "\n".join(f.errors)


@pytest.mark.parametrize("path_sep", ["/", "\\"])
@pytest.mark.parametrize("case", ["reference", "correct", "misordered", "missing", "duplicate",
                                  "wrong_total", "unreadable"])
def test_documented_gate_lists_follow_the_script_when_present(tmp_path, monkeypatch, path_sep, case):
    """A direct script reference needs no duplicate list; actual claims must remain accurate."""
    steps = [("consistency", "lint_consistency.py"), ("systems", "systems_check.py"),
             ("system map", "emc_systems_map_check.py"), ("claims", "lint_claims.py"),
             ("prose", "lint_changed_prose.py"), ("citations", "lint_citations.py"),
             ("style", "lint_style.py")]
    script = tmp_path / "scripts" / "preflight.sh"
    script.parent.mkdir()
    script.write_text("\n".join(f'echo "== {title} =="\npython3 {tool}' for title, tool in steps),
                      encoding="utf-8")
    skill = tmp_path / ".claude" / "skills" / "repo-gates" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    entries = [f"({i}) {title} (`{tool}`)" for i, (title, tool) in enumerate(steps, 1)]
    if case == "misordered":
        entries[0], entries[1] = entries[1].replace("(2)", "(1)"), entries[0].replace("(1)", "(2)")
    elif case == "missing":
        entries.pop()
    elif case == "duplicate":
        entries[-1] = entries[-2]
    header = "Eight" if case == "wrong_total" else "Seven"
    text = f"**{header} gates, in this order:** " + "; ".join(entries) + "\n"
    if case == "reference":
        text = "Run `scripts/preflight.sh`; its output identifies each gate.\n"
    elif case == "unreadable":
        text = text.replace("**Seven", "Seven")
    skill.write_text(text, encoding="utf-8")
    monkeypatch.setattr(sc, "REPO", str(tmp_path))
    monkeypatch.setattr(sc, "INSTRUCTION_SKILLS", str(tmp_path / ".claude" / "skills"))
    monkeypatch.setattr(sc, "GATE_ORDINAL_DOCS", ())
    native_relpath = os.path.relpath
    monkeypatch.setattr(sc.os.path, "relpath", lambda *args: native_relpath(*args).replace("\\", "/").replace("/", path_sep))
    assert sc._gate_ordinal_docs() == [".claude/skills/repo-gates/SKILL.md"]
    f = sc.Findings()
    sc.check_preflight_gate_list({}, f)
    if case in {"reference", "correct"}:
        assert f.errors == [], f.errors
    else:
        assert any("[P1]" in e for e in f.errors), f"{case} claim passed: {f.errors}"


def test_the_preflight_gate_ordinal_agrees_with_preflight(graph):
    """*"gate N of preflight"* had four homes; one was right and three said 2.

    CLAUDE.md carries the correction in its own text — "it sends a reader to the wrong gate when
    preflight fails" — and fixed only itself. The ordinal is now read from `preflight.sh`.
    """
    f = sc.Findings()
    sc.check_preflight_gate_ordinal(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_every_route_page_states_a_claim_ceiling(graph):
    """⚠ THE CEILING EXISTED ONE LEVEL ABOVE AND ONE BELOW THE PAGE ANYONE READS.

    ARCHITECTURE.md §5 calls `limitations` one of the three fields carrying most of the weight and said
    it had been "promoted … to every object". Measured 2026-08-06: 9 of 9 strategies carried it, 16 of
    16 requirements carried `claim_ceiling`, and **0 of 40 routes carried anything at all.**

    ⛔ THE FIX IS INHERITANCE, NOT AUTHORSHIP. Forty fresh route-level ceilings would be forty invented
    scientific limits — the one thing this repository must never do. A family limitation binds every
    route inside it by construction, so the existing sentence is surfaced, attributed.
    """
    views = sc.all_views(graph)
    for r in graph["routes"]:
        assert r["limitations_inherited"], f"{r['id']} inherits no claim ceiling from {r['strategy']}"
        body = views[f"L2-{sc.route_slug(r['id'])}.md"]
        assert "Claim ceiling" in body, f"{r['id']}'s page does not state what it may not be used to claim"


def test_the_inherited_ceiling_is_never_a_second_assertion(graph):
    """It must be the family's own sentence, verbatim. A paraphrase would be a second home for it."""
    fam = {s["id"]: s.get("limitations") or [] for s in graph["strategies"]}
    for r in graph["routes"]:
        assert r["limitations_inherited"] == fam[r["strategy"]]


def test_backfill_emits_yaml_a_real_parser_accepts():
    """The generator that produced the 24 invalid files must not be able to produce a 25th."""
    import backfill_frontmatter as bf
    import yaml
    for s in ["Protocol: systematic review & meta-analysis", "** decision memo", "plain title",
              "trailing colon:", "#hash start", "- dash start", "a | pipe", "yes"]:
        assert yaml.load(f"k: {bf.y(s)}", Loader=yaml.BaseLoader) == {"k": s}, s


def test_preflight_runs_the_medical_integrity_guard():
    """⛔ IT DID NOT, AND THE GAP TURNED `main` RED (2026-08-06).

    `emc_systems_map_check.py` is the sibling of `systems_check.py` — same shape, same regenerate-and-
    diff discipline, pure stdlib, ~2 s — and it was CI-only while its sibling was a preflight gate. A
    session could run preflight, read `PREFLIGHT OK`, merge, and only then learn that a newly generated
    view named a cell line whose identity is disputed, which `O4` requires every tracked file to
    classify. A green local gate that skips a medical-integrity check is worse than no local gate,
    because it is trusted.
    """
    with open(os.path.join(REPO, "scripts", "preflight.sh"), encoding="utf-8") as fh:
        sh = fh.read()
    assert "emc_systems_map_check.py --check" in sh
    gates = re.findall(r'^\s*echo "== (.+?) =="', sh, re.M)
    assert any("EMC systems map" in gname for gname in gates), gates


# ── publications: the endpoint every route is for ──────────────────────────────
#
# ⭐ THE RULING THESE GUARD (trimcrae, 2026-08-06): *the end goal of every one of these routes is a
# paper.* With no wet lab and no clinic the published record is the only channel to a patient, so an
# endpoint is a structural property of a route — and the model carried it for no route at all until
# this collection existed. Each test below is the assertion form of a sentence in ARCHITECTURE §3.3,
# because a property asserted in prose about data nobody checks is a hope, not a property.


def test_every_route_names_a_publication_endpoint_that_exists(graph):
    """A route with no endpoint is an activity, not an option — including the closed ones.

    ⚠ CLOSED ROUTES ARE THE POINT, NOT AN EDGE CASE. A definitional closure is a publishable negative
    and the field publishes almost none of them, so the rows with the least remaining science can
    carry the most transferable writing. Exempting them would have removed seven of forty.
    """
    pubs = {p["id"] for p in graph["publications"]}
    for r in graph["routes"]:
        end = r["publication"]["endpoint"]
        assert end in pubs, f"{r['id']} -> {end}"


def test_no_publication_is_orphaned(graph):
    """A paper nothing is trying to reach is an endpoint that lost its route, or a route never modelled."""
    claimed = {r["publication"]["endpoint"] for r in graph["routes"]}
    assert {p["id"] for p in graph["publications"]} == claimed


def test_an_unwritten_paper_still_says_what_it_would_claim(graph):
    """⭐ THE FIELD THAT MAKES AN UNWRITTEN PAPER REAL, and the reason this is a graph row at all.

    Modelling an endpoint that has no file buys nothing if the row is just a name. What it has to
    carry is the sentence the paper would put into the field's record — if that cannot be written,
    there is no endpoint — plus an honest statement of what is missing.
    """
    for p in graph["publications"]:
        assert len(p["what_it_would_claim"]) >= 40, p["id"]
        if p["state"] in ("unwritten", "outlined"):
            assert p.get("why_not_written"), p["id"]
            assert not p.get("document"), f"{p['id']} is unwritten and points at a document"


def test_a_written_endpoint_carries_no_title_of_its_own(graph):
    """⛔ THE ASYMMETRY IN ARCHITECTURE §3 SURVIVES THIS COLLECTION, and this is where it is enforced.

    The rule was never "publications are not modelled"; it was "do not create a second home for a
    fact the file owns". So a row WITH a document has no title and the view reads the file's
    frontmatter; a row WITHOUT one has `working_title`, because an unwritten paper has no file to own
    its name. Both directions are asserted — a title beside a document would be the duplication, and
    a missing one on an unwritten row would be an endpoint nobody can refer to.
    """
    for p in graph["publications"]:
        if p.get("document"):
            assert "working_title" not in p, p["id"]
        else:
            assert p.get("working_title"), p["id"]


def test_an_endpoint_document_is_a_publication_not_a_memo_about_one(graph):
    """A file-exists check is far weaker than it looks: every memo, plan and red-team would pass it.

    `research/manuscripts/` holds ~60 documents declaring `level: L3`, and only a minority are
    deliverables. The frontmatter level is what separates a paper from a note ABOUT a paper, and
    pointing an endpoint at the second is the confusion this register was added to stop.
    """
    for p in graph["publications"]:
        doc = p.get("document")
        if not doc:
            continue
        path = os.path.join(REPO, doc["file"])
        assert os.path.exists(path), doc["file"]
        with open(path, encoding="utf-8") as fh:
            fmv = sc._yaml_frontmatter(fh.read())[0] or {}
        assert fmv.get("level") == "L3", f"{p['id']} -> {doc['file']} is level {fmv.get('level')!r}"


def test_the_checker_catches_a_route_pointed_at_a_nonexistent_paper(graph):
    """The guard must FAIL on the defect, not merely pass on the current data.

    A check that has never been seen to go red is indistinguishable from one that cannot.
    """
    g = copy.deepcopy(graph)
    g["routes"][0]["publication"]["endpoint"] = "PUB-DOES-NOT-EXIST"
    f = sc.Findings()
    sc.check_publications(g, f)
    assert any("[B1]" in e for e in f.errors), f.errors


def test_the_checker_catches_a_paper_no_route_claims(graph):
    g = copy.deepcopy(graph)
    g["publications"].append({"id": "PUB-ORPHAN", "level": "L3", "kind": "publication",
                              "state": "unwritten", "target_venue": "preprint",
                              "working_title": "a paper nothing points at",
                              "what_it_would_claim": "x" * 41,
                              "why_not_written": "it exists only in this test"})
    f = sc.Findings()
    sc.check_publications(g, f)
    assert any("[B2]" in e for e in f.errors), f.errors


def test_the_degrader_is_no_longer_the_north_star(graph):
    """⛔ trimcrae, 2026-08-06: the degrader path hit enough blockers that it gets no special treatment.

    Two things had to move together and neither is cosmetic: the route's own grade stopped calling
    itself the north star, and NO strategy family carries `portfolio_role: lead` any more. The second
    is the one worth pinning — the tempting fix was to promote another family into the empty slot,
    and a portfolio with no lead is the honest state. Leaving `lead` unclaimed is a finding.

    ⚠ THIS TEST GUARDS A STANDING, NOT A RESULT. Nothing here asserts anything about the degrader
    route's evidence, which is unchanged and is why its limits are the best-characterised on the board.
    """
    val = next(r for r in graph["routes"] if r["id"] == "RT-DEGRADER")["grade"]["value"].lower()
    assert "no longer the program's north star" in val
    # ⚠ NOT a bare `"north star" not in val`. The retirement itself has to NAME the retired framing —
    # that is the superseded-retained discipline — so the phrase legitimately appears twice. What must
    # never appear again is an UNNEGATED occurrence, which is what this loop actually checks.
    for m in re.finditer("north star", val):
        prefix = val[max(0, m.start() - 70):m.start()]
        assert "no longer" in prefix or "superseded, retained" in prefix, val[:m.end()]
    assert [s["id"] for s in graph["strategies"] if s["portfolio_role"] == "lead"] == []


def test_the_publication_view_is_linted_for_claim_language(graph):
    """Every row on that page is a sentence beginning "what this paper would claim".

    That is the construction most likely to slide from "this work would ESTABLISH X" into "X works",
    and unlike the manuscript these sentences are authored in JSON where nobody reads them as prose.
    The generated view is where they become readable, so it is where they are linted.
    """
    with open(os.path.join(REPO, "research", "manuscripts", "lint_claims.py"), encoding="utf-8") as fh:
        assert "systems/views/L3-publications.md" in fh.read()


def test_dot_claude_is_excluded_from_every_repo_walk():
    """⛔ Measured 2026-08-07, with 17 agent worktrees live under `.claude/worktrees/`.

    `systems_check --check` reported **541 ERROR** in the main checkout and **0 ERROR** on the
    identical commit checked out cleanly elsewhere. Every error was a duplicate finding against an
    agent worktree's copy of a file this checker had already checked in place. Git never sees those
    copies (`.gitignore:15`); `os.walk` does.

    Why this is a test and not a comment. Gate 2 of preflight is one of the two gates that enforce
    provenance and medical integrity, and this repo has already learned twice that a guard which is
    red — or noisy — for a reason unrelated to the work is a guard whose real failures nobody reads.
    The harness creates those worktrees automatically, so the condition recurs without anyone
    choosing it.

    ⚠ Asserts the WIRING, not the prose. `_walk_md` hand-rolled its own weaker exclusion
    (`"__pycache__" in rel_root`) while three sibling walks used `_is_transient`, and that single
    divergence is what let the defect reach the K1 cross-link checks. Both paths are pinned here so
    they cannot drift apart again.
    """
    assert ".claude" in sc.TRANSIENT_DIRS
    for rel in (".claude", ".claude/worktrees", ".claude/worktrees/agent-x/research/manuscripts"):
        assert sc._is_transient(rel), rel
    assert not sc._is_transient("research/manuscripts"), "must not over-exclude real content"

    # `_walk_md` must route through `_is_transient` rather than carrying a second rule of its own.
    src = inspect.getsource(sc._walk_md)
    assert "_is_transient(rel_root)" in src, "_walk_md stopped using the shared exclusion"

    # And the real function over the real tree: no yielded path may sit under `.claude`.
    assert not [rel for rel, _ in sc._walk_md(sc.DOC_SKIP) if rel.startswith(".claude/")]
