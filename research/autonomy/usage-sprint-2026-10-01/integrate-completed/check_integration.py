#!/usr/bin/env python3
"""Offline integration identities and assertion preservation; no source acquisition."""
from __future__ import annotations
import ast
import hashlib
import json
import importlib.util
import re
import tempfile
from unittest.mock import patch
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)
def tree(ref):
    result = {}
    for row in git("ls-tree", "-rz", ref).split(b"\0"):
        if row:
            left, path = row.split(b"\t", 1)
            result[path.decode()] = tuple(left.decode().split())
    return result
def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
def methods(raw):
    module = ast.parse(raw.decode())
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == "TerminalVerdictTests")
    return [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
def dump(nodes):
    return [ast.dump(n, include_attributes=False) for n in nodes]

def check_catalogue_rendering(plan):
    """Exercise only pure formatting and the unchanged native classifier, offline."""
    render = plan["controlled_catalogue_rendering"]
    for item in render["patches"]:
        previous = git("show", item["original_blob"])
        patched = previous
        for replacement in item["replacements"]:
            old, new = replacement["before"].encode(), replacement["after"].encode()
            assert patched.count(old) == 1, item["path"]
            patched = patched.replace(old, new)
        current = (ROOT / item["path"]).read_bytes()
        assert current == patched and blob(current) == item["patched_blob"], item["path"]
    def module(name, path):
        spec = importlib.util.spec_from_file_location(name, ROOT / path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        return loaded
    formatter = module("integration_trigger_formatter", "scripts/trigger_scan.py")
    classifier = module("integration_citation_types", "research/manuscripts/lint_citation_types.py")
    cfg = json.loads((ROOT / "research/method-watch-triggers.json").read_text())
    trigger = next(t for t in cfg["triggers"] if t["id"] == render["trigger_id"])
    raw_ledger = (ROOT / "research/method-watch-trigger-hits.json").read_bytes()
    assert blob(raw_ledger) == render["raw_hit_blob"]
    ledger_doc = json.loads(raw_ledger)
    hit = ledger_doc["hits"][render["trigger_id"]][render["hit_id"]]
    before = json.dumps(hit, sort_keys=True)
    assert not {"article_types", "pmid", "doi"} & set(hit), "No source type inferred"
    assert blob((ROOT / "research/manuscripts/citation-article-types.json").read_bytes()) == render["cache_blob"]
    records, index = classifier.load_cache()
    assert records is not None and ("PMCID", hit["id"]) not in index
    ideas_patch, board_patch = render["patches"][1:]
    with tempfile.TemporaryDirectory(prefix="integration-catalogue-") as temporary:
        temp = Path(temporary)
        with patch.object(formatter.urllib.request, "urlopen", side_effect=AssertionError("Network forbidden in formatter control")):
            bullet = formatter.ideas_bullet(trigger, hit, hit["first_seen"])
            assert bullet + "\n" == ideas_patch["replacements"][0]["after"]
            one_run = dict(date=hit["first_seen"], mode="scan", triggers=1, queries=1,
                           new_hits=0, appended=0, errors=[])
            fixture = {"runs": [one_run], "hits": {trigger["id"]: {hit["id"]: hit}}}
            fixture_before = json.dumps(fixture, sort_keys=True)
            stats = {trigger["id"]: dict(queries=1, seen=1, in_window=0, new=0, appended=0)}
            with patch.object(formatter, "BOARD", str(temp / "board.md")):
                formatter.write_board({"triggers": [trigger]}, fixture, one_run, stats)
            assert json.dumps(fixture, sort_keys=True) == fixture_before, "Raw ledger mutated"
            rows = (temp / "board.md").read_text().splitlines()
            assert rows.count(board_patch["replacements"][0]["after"].rstrip("\n")) == 1
            assert "Nothing here has been read, graded or verified" in (temp / "board.md").read_text()
            for item in (ideas_patch, board_patch):
                old, new = item["replacements"][0]["before"], item["replacements"][0]["after"]
                for key in ("title", "venue", "date", "id", "url"):
                    assert hit[key] in old and hit[key] in new, (item["path"], key)
                assert old.count(hit["url"]) == new.count(hit["url"]) == 1
                (temp / "old.md").write_text(old)
                found = classifier.claims(["old.md"], root=str(temp))
                assert len(found) == 1 and found[0][2:5] == ("case report", "PMCID", hit["id"]), found
                errors, _ = classifier.evaluate(found, records, index)
                assert len(errors) == 1 and errors[0][0] == "MISSING", errors
                (temp / "new.md").write_text(new)
                assert classifier.claims(["new.md"], root=str(temp)) == [], item["path"]
            linked = formatter._catalogue_title_link(hit)
            # Explicit type prose outside the title still binds and fails missing-cache metadata.
            explicit = linked + "\nA case report (" + hit["id"] + ").\n"
            (temp / "explicit.md").write_text(explicit)
            found = classifier.claims(["explicit.md"], root=str(temp))
            assert len(found) == 1 and found[0][2:5] == ("case report", "PMCID", hit["id"]), found
            errors, _ = classifier.evaluate(found, records, index)
            assert len(errors) == 1 and errors[0][0] == "MISSING", errors
            special = dict(hit, title=r"A [catalogue] \ path *literal* _term_: A case report",
                           url="https://example.invalid/catalogue")
            escaped = formatter._catalogue_title_link(special)
            label = re.fullmatch(r"\[(.*)\]\((.*)\)", escaped)
            assert label is not None and label.group(2) == special["url"]
            assert re.sub(r"\\(.)", r"\1", label.group(1)) == special["title"]
            (temp / "escaped.md").write_text(escaped + " (" + hit["id"] + ").\n")
            assert classifier.claims(["escaped.md"], root=str(temp)) == []
    assert json.dumps(hit, sort_keys=True) == before, "Hit metadata mutated"
    initial = plan["initial_combined_ci"]
    original_log = (ROOT / initial["log_path"]).read_bytes()
    assert len(original_log) == initial["log_bytes"] and blob(original_log) == initial["log_blob"]
    assert hashlib.sha256(original_log).hexdigest() == initial["log_sha256"]
    for annotation in (b"IDEAS.md:656", b"method-watch-trigger-scan.md:347"):
        assert annotation in original_log
    assert b"TYPE CLAIM WITH NO CACHED METADATA" in original_log
    print("CATALOGUE_RENDERING_OK exact two rows and pure formatter; all literal metadata/warnings retained")
    print("NATIVE_TYPE_CONTROLS_OK old title shapes fail MISSING; linked titles excluded; explicit classification still fails MISSING")
    print("INITIAL_FAILED_LOG_OK original observed two annotations and exact bytes/hash preserved")

def main():
    plan = json.loads(Path(__file__).with_name("integration-plan.json").read_text())
    assert plan["validation_scope"] == "catalogue_render_repair", plan["validation_scope"]
    base, current = tree(plan["base_revision"]), tree("HEAD")
    expected = {r["path"]: (r["mode"], r["type"], r["sha"]) for r in plan["expected_source_delta"]}
    assert len(expected) == plan["source_path_count"] == 72
    extras = set(plan["allowed_integration_paths"])
    changed = {p for p in set(base) | set(current) if base.get(p) != current.get(p)}
    assert changed <= set(expected) | extras, sorted(changed - set(expected) - extras)
    for path, pin in expected.items():
        assert current.get(path) == pin, (path, current.get(path), pin)
    untouched = [p for p in base if p not in expected and p not in extras]
    assert all(current.get(p) == base[p] for p in untouched)
    for source in plan["sources"]:
        subprocess.run(["git", "merge-base", "--is-ancestor", source["head"], "HEAD"], cwd=ROOT, check=True)
        assert git("show", "-s", "--format=%P", source["merge_commit"]).decode().split() == source["merge_parents"]
    assert len(plan["sources"]) == 9
    adj = plan["controlled_adjustments"]
    original = git("show", adj["terminal_original_blob"])
    grouped = (ROOT / "research/autonomy/tests/test_ci_terminal_verdict.py").read_bytes()
    assert blob(grouped) == adj["terminal_grouped_blob"]
    old, new = methods(original), methods(grouped)
    assert len(old) == 8 and len(new) == 4
    for final, indices in zip(new, adj["groups"], strict=True):
        assert dump(final.body) == dump([n for i in indices for n in old[i].body]), final.name
    assert grouped.count(b"# Retained scenario family:") == 14
    assert grouped.startswith(original[:original.index(b"    def test_")]), "Helpers/patches changed"
    before = git("show", adj["amendment_prior_source_blob"])
    amended = (ROOT / "research/autonomy/amendments.jsonl").read_bytes()
    assert amended.startswith(before), "Prior amendment bytes changed"
    appended = [json.loads(r) for r in amended[len(before):].splitlines() if r.strip()]
    assert len(appended) == adj["new_declarations"] == 6
    assert {r["path"] for r in appended} == set(adj["governed_paths"])
    assert all(r["cycle_id"] == plan["cycle_id"] and r["self_serving_check"] for r in appended)
    ci = adj["main_ci_history"]
    ci_old, ci_new = git("show", ci["original_blob"]), (ROOT / ci["path"]).read_bytes()
    anchor = b"  pytest:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"
    assert ci_new == ci_old.replace(anchor, anchor + b"        with:\n          fetch-depth: 0\n")
    assert blob(ci_new) == ci["patched_blob"]
    assert blob(git("show", "184e6aff659180492f4df94ed46a222849ab1b7c:research/autonomy/await_ci.py")) == "121bb8798debff50e207a14e50aa5aae162f3d0e"
    assert len(git("show", "f6b73790809e82f7058639e7b94a9d6842b054fc")) == 9124
    audit = json.loads((ROOT / "research/autonomy/usage-sprint-2026-10-01/aso-tissue-join/audit-evidence.json").read_text())
    pins = audit["exact_historical_current_bindings"]
    assert len(pins) == 6 and audit["status"] == "complete_no_scientific_change"
    for pin in pins:
        assert blob((ROOT / pin["path"]).read_bytes()) == pin["current_blob"] == pin["historical_blob"]
    usz = json.loads((ROOT / "research/autonomy/usage-sprint-2026-10-01/usz-junction-inputs/input-fingerprints.json").read_text())["model_evidence"]
    raw = (ROOT / usz["path"]).read_bytes()
    assert blob(raw) == usz["current_blob"] == usz["known_previous_blob"] and len(raw) == usz["bytes"]
    check_catalogue_rendering(plan)
    print("INTEGRATION_IDENTITIES_OK 72 source paths;", len(untouched), "main entries preserved; nine source ancestors/two-parent merges")
    print("TERMINAL_GROUPING_OK eight original AST bodies/four meaningful families; fourteen scenario markers")
    print("AMENDMENT_APPEND_OK six declarations; every prior source log byte preserved")
    print("MAIN_CI_HISTORY_OK exact pytest checkout-only diff; both historical witnesses available")
    print("REUSED_SCIENCE_BINDINGS_OK six tissue inputs and USZ model; historical audits not rerun")
    print("HEAD", git("rev-parse", "HEAD").decode().strip())
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
