#!/usr/bin/env python3
"""Offline integration identities and assertion preservation; no source acquisition."""
from __future__ import annotations
import ast
import hashlib
import json
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
def main():
    plan = json.loads(Path(__file__).with_name("integration-plan.json").read_text())
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
    print("INTEGRATION_IDENTITIES_OK 72 source paths;", len(untouched), "main entries preserved; nine source ancestors/two-parent merges")
    print("TERMINAL_GROUPING_OK eight original AST bodies/four meaningful families; fourteen scenario markers")
    print("AMENDMENT_APPEND_OK six declarations; every prior source log byte preserved")
    print("MAIN_CI_HISTORY_OK exact pytest checkout-only diff; both historical witnesses available")
    print("REUSED_SCIENCE_BINDINGS_OK six tissue inputs and USZ model; historical audits not rerun")
    print("HEAD", git("rev-parse", "HEAD").decode().strip())
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
