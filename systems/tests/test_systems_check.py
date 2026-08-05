#!/usr/bin/env python3
"""Tests for the systems model's checker and guard. ($0, pure stdlib + pytest)

Every test here guards a rule that exists because of a measured failure, and each says which.
"""
from __future__ import annotations

import copy
import json
import os
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


def test_views_match_the_graph(graph):
    """A generated view that has been hand-edited, or has drifted, is a defect.

    This is the whole reason the views are generated: prose drifts and cannot be checked.
    """
    f = sc.Findings()
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


# ───────────────────────── the mini schema validator is real ─────────────────────────

def test_validator_enforces_enums_and_patterns():
    mv = sc.MiniValidator(os.path.join(SYS, "schema"))
    schema = mv.docs["blocker.schema.json"]
    bad = {"id": "NOTABLOCKER", "name": "x" * 20, "kind": "not_a_kind",
           "statement_about": "y" * 20, "owner": {"file": "a"}}
    msgs = mv.validate(bad, schema, schema)
    assert any("does not match" in m for m in msgs), msgs
    assert any("not in enum" in m for m in msgs), msgs


def test_validator_enforces_conditional_requirements():
    """work_state `in_work` must name the running job.

    `in_work` instructs every reader not to start a second copy, so one on something nobody has
    started is an instruction not to do the work. It has been wrong seven times in this repository.
    """
    mv = sc.MiniValidator(os.path.join(SYS, "schema"))
    doc = mv.docs["research-object.schema.json"]
    msgs = mv.validate({"work_state": "in_work", "status": "active", "confidence": "low",
                        "last_verified": "2026-08-05"}, doc["$defs"]["state"], doc)
    assert any("running_job" in m for m in msgs), msgs


def test_validator_reports_each_problem_once():
    """A schema that both declares `required` and $refs a base declaring it must not double-report."""
    mv = sc.MiniValidator(os.path.join(SYS, "schema"))
    schema = mv.docs["route.schema.json"]
    msgs = mv.validate({"id": "RT-X", "level": "L2", "kind": "route"}, schema, schema)
    assert len(msgs) == len(set(msgs)), msgs


# ───────────────────────── the fail-red guard ─────────────────────────

def test_parser_guard_passes_on_the_committed_tree():
    assert pg.main([]) == 0


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


def test_the_two_kinds_of_gap_are_distinguished(graph):
    """'No instrument exists' and 'every instrument failed' are opposite work items.

    The first needs something built or a bench; the second needs a better method. Filing them under
    one word is how the cheap one stays invisible — the same failure the technology taxonomy found on
    the watch list.
    """
    inst = sc.by_id(graph["instruments"])
    holes, unusable = [], []
    for r in graph["requirements"]:
        served = r.get("served_by", [])
        if not served:
            holes.append(r["id"])
        elif not [v for v in served
                  if (inst.get(v, {}).get("known_answer_control") or {}).get("state")
                  not in sc.NON_SUPPORTING_CONTROL]:
            unusable.append(r["id"])
    assert holes and unusable, "both categories should be populated in the current state"
    assert not set(holes) & set(unusable), "a requirement cannot be in both categories"


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
    """The migration gate. A different count is a failed move, not a new plan."""
    items = [b for b in (graph.get("plan") or {}).get("blocks", []) if b["kind"] == "item"]
    from collections import Counter
    assert len(items) == 38, f"expected 38 plan items, found {len(items)}"
    assert dict(Counter(b["marker"] for b in items)) == \
        {"x": 17, "~": 3, " ": 15, "–": 1, "!": 2}


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


def test_work_ledger_reads_the_generated_plan():
    """The parser follows the plan. A parser left watching the old location goes green on a file
    that no longer holds what it parses — the exact failure parser_guard exists to prevent."""
    sys.path.insert(0, os.path.join(REPO, "research", "modalities"))
    import work_ledger as wl
    assert wl.DEFAULT_PLAN_DOC.endswith(os.path.join("systems", "views", "plan.md"))
    assert wl.DEFAULT_STRATEGY == wl.DEFAULT_PLAN_DOC
    text = open(wl.DEFAULT_PLAN_DOC, encoding="utf-8").read()
    got, how = wl.scan_plan_items(text, None)
    assert not how.startswith("NOT SCANNED"), how
    assert len(got) == 20, f"expected 20 owed items, got {len(got)}"


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


def test_no_new_broken_links(graph):
    """A new broken relative link is an error immediately; the pre-existing ones are baselined.

    Same discipline as the frontmatter backfill: record the baseline, fail on regressions. Turning
    120 pre-existing breakages into build failures on day one makes the build permanently red for
    defects that predate the check — and a permanently red build gets ignored.
    """
    f = sc.Findings()
    sc.check_links(graph, f)
    assert f.errors == [], "\n".join(f.errors)


def test_the_link_baseline_is_not_a_silencer(graph):
    """Every baselined entry names WHY it is broken, and the list is meant to reach zero.

    ⚠ These are not typos — each is a document citing an artifact that was never produced. Fixing one
    means producing the artifact or withdrawing the citation, not adding a line here.
    """
    path = os.path.join(SYS, "graph", "link-baseline.json")
    d = json.load(open(path, encoding="utf-8"))
    assert d["known_broken"], "an empty baseline should be deleted, not kept"
    assert len(d["known_broken"]) <= 3, \
        "the baseline grew — a new broken link must be fixed, not grandfathered"
    for row in d["known_broken"]:
        assert row.get("why") and len(row["why"]) > 40, f"{row['to']} is baselined with no reason"


def test_a_preregistration_is_never_archived():
    """A prereg's entire value is that it was written before the result."""
    import glob
    for p in glob.glob(os.path.join(REPO, "archive", "**", "*.md"), recursive=True):
        text = open(p, encoding="utf-8", errors="ignore").read()
        assert "prereg" not in os.path.basename(p).lower(), f"{p} looks like a preregistration"
        assert "status: immutable" not in text[:600], f"{p} is marked immutable and must not be archived"
