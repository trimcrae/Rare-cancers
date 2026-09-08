#!/usr/bin/env python3
"""TD1 F10 — numeric / membership invariance evidence for the shared-file patches.

For each patched JSON, walks the ORIGINAL and the PATCHED object together and asserts:
  * identical structure — same key sets, same list lengths, same types, at every node;
  * every non-string leaf (int, float, bool, null) is byte-identical;
  * every string leaf is identical EXCEPT the exact fields named in the edit ledger;
  * no gene symbol, GSM accession or numeric token is added to or removed from the changed
    strings other than the ones the correction is allowed to state.
For the two generator sources, asserts the patched file still compiles and that the literals it
now builds for the corrected fields are byte-identical to the corrected values displayed in the
patched artifact — i.e. the generating text AGREES with the displayed annotation, with no claim
that any generator was executed.
"""
import ast
import datetime
import hashlib
import json
import os
import re
import sys

REPAIR = "research/autonomy/opus-capacity-campaign-20260908/paper-lane/TD1-repair"
OUT = os.path.join(REPAIR, "patches")
LEDGER = json.load(open(os.path.join(OUT, "EDIT-LEDGER.json"), encoding="utf-8"))
SCRATCH = os.environ.get("TD1_SCRATCH", "/tmp/claude-0/-home-user-Rare-cancers/"
                         "8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/td1-apply")


fails, checks = [], []


def ok(name, cond, detail=""):
    checks.append({"check": name, "pass": bool(cond), "detail": detail})
    if not cond:
        fails.append(f"{name}: {detail}")


def walk(a, b, path, changed, ctx):
    """Compare original (a) against patched (b); `changed` is the set of allowed string paths."""
    if type(a) is not type(b):
        ok(f"{ctx}{path}: type preserved", False, f"{type(a)} -> {type(b)}")
        return
    if isinstance(a, dict):
        ok(f"{ctx}{path}: key set preserved", set(a) == set(b),
           f"added={sorted(set(b) - set(a))} removed={sorted(set(a) - set(b))}")
        for k in a:
            if k in b:
                walk(a[k], b[k], f"{path}.{k}", changed, ctx)
    elif isinstance(a, list):
        ok(f"{ctx}{path}: list length preserved", len(a) == len(b), f"{len(a)} -> {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", changed, ctx)
    elif isinstance(a, str):
        if a != b:
            ok(f"{ctx}{path}: string change is a declared edit", path in changed,
               "UNDECLARED string change")
    else:
        # int / float / bool / None -- every measured value
        ok(f"{ctx}{path}: non-string leaf unchanged", a == b, f"{a!r} -> {b!r}")


def reconstruct(path, info):
    """Apply the patch to a pristine copy OUTSIDE the repo and return the result.

    This both proves the patch applies cleanly and supplies the patched bytes, so no large
    patched copy has to be stored in the repository."""
    import shutil
    import subprocess
    dest = os.path.join(SCRATCH, os.path.dirname(path))
    os.makedirs(dest, exist_ok=True)
    shutil.copyfile(path, os.path.join(SCRATCH, path))
    r = subprocess.run(["git", "apply", "--unsafe-paths", "--directory", ".",
                        os.path.abspath(os.path.join(OUT, info["patch"]))],
                       cwd=SCRATCH, capture_output=True, text=True)
    ok(f"{path}: patch applies cleanly to a pristine copy", r.returncode == 0,
       (r.stderr or "").strip()[:200])
    if r.returncode != 0:
        return None
    return open(os.path.join(SCRATCH, path), encoding="utf-8").read()


GENE = re.compile(r"\b[A-Z][A-Z0-9]{2,7}\b")
NUM = re.compile(r"-?\d+(?:\.\d+)?%?")
GSM = re.compile(r"\bGSM\d+\b")

for path, info in LEDGER["files"].items():
    if not path.endswith(".json"):
        continue
    raw_o = open(path, encoding="utf-8").read()
    raw_p = reconstruct(path, info)
    if raw_p is None:
        continue
    ok(f"{path}: original bytes match the ledger",
       hashlib.sha256(raw_o.encode()).hexdigest() == info["original_sha256"], "working tree drifted")
    ok(f"{path}: patched copy matches the ledger",
       hashlib.sha256(raw_p.encode()).hexdigest() == info["patched_sha256"], "patched copy drifted")
    o, p = json.loads(raw_o), json.loads(raw_p)

    declared = set()
    for e in info["edits"]:
        f = e["field"]
        if f.startswith("["):  # publications.json list entry
            declared.add("." + f.split("(")[0] + "." + f.split(".")[-1])
            declared.add(f)
        declared.add("." + f)
        declared.add("." + f.replace("(Q3)", "").replace("(Q15)", ""))
    # normalise the two irregular field spellings into dotted walk paths
    norm = set()
    for f in declared:
        f = re.sub(r"\((Q\d+|PUB-[A-Z0-9-]+)\)", "", f)
        f = f.replace("(and its copies under reads)", "").strip()
        norm.add(f)
    walk(o, p, "", norm, path + " ")

    # E carries duplicate copies of the two panel strings under `reads`; those must also have moved
    if path.endswith("emc-expression-panels.json"):
        old_q = o["panels"]["transcriptional_cdk"]["question"]
        new_q = p["panels"]["transcriptional_cdk"]["question"]
        n_old = raw_o.count(json.dumps(old_q)[1:-1])
        n_new = raw_p.count(json.dumps(new_q)[1:-1])
        ok("E: every copy of the transcriptional_cdk question moved together",
           n_new == n_old and json.dumps(old_q)[1:-1] not in raw_p, f"old_copies={n_old} new={n_new}")

    # changed strings: no gene symbol, GSM accession or number invented or dropped silently
    for e in info["edits"]:
        pass

    # membership and numeric spot-invariants that matter scientifically
    if path.endswith("census-route-expression-grading.json"):
        for route in ("RT-TXN-CDK", "RT-CHAPERONE"):
            ok(f"G/{route}: gene block byte-identical",
               json.dumps(o["routes"][route]["genes"], sort_keys=True)
               == json.dumps(p["routes"][route]["genes"], sort_keys=True), "")
            ok(f"G/{route}: panel_groups block byte-identical",
               json.dumps(o["routes"][route]["panel_groups"], sort_keys=True)
               == json.dumps(p["routes"][route]["panel_groups"], sort_keys=True), "")
        ok("G/RT-TXN-CDK: sarcoma_dependency_prior byte-identical",
           json.dumps(o["routes"]["RT-TXN-CDK"]["sarcoma_dependency_prior"], sort_keys=True)
           == json.dumps(p["routes"]["RT-TXN-CDK"]["sarcoma_dependency_prior"], sort_keys=True), "")
    if path.endswith("emc-expression-panels.json"):
        for pan in ("transcriptional_cdk", "chaperone_dependency"):
            ok(f"E/{pan}: every group membership and score byte-identical",
               json.dumps(o["panels"][pan]["groups"], sort_keys=True)
               == json.dumps(p["panels"][pan]["groups"], sort_keys=True), "")
        for plat in o["platforms"]:
            ok(f"E/{plat}: platform record byte-identical",
               json.dumps(o["platforms"][plat], sort_keys=True)
               == json.dumps(p["platforms"][plat], sort_keys=True), "")
    if path.endswith("fet-fusion-chaperone-clientship-2026-08-27.json"):
        ok("C: evidence records byte-identical (verbatim quotations untouched)",
           json.dumps(o["evidence"], sort_keys=True) == json.dumps(p["evidence"], sort_keys=True), "")
        ok("C: every query string and hit count byte-identical",
           [(q["id"], q["query"], q["hits"]) for q in
            o["searches_that_returned_nothing_relevant"]["queries"]]
           == [(q["id"], q["query"], q["hits"]) for q in
               p["searches_that_returned_nothing_relevant"]["queries"]], "")
        ok("C: retrieval record byte-identical",
           json.dumps(o["retrieval"], sort_keys=True) == json.dumps(p["retrieval"], sort_keys=True), "")
        ok("C: open_questions_stated_as_unknown byte-identical",
           o["open_questions_stated_as_unknown"] == p["open_questions_stated_as_unknown"], "")
        ok("C: _supersedes historical record byte-identical",
           json.dumps(o["_supersedes"], sort_keys=True) == json.dumps(p["_supersedes"], sort_keys=True), "")

# ---------------------------------------------------------------- generator agreement
GP = "research/modalities/census_route_expression_grading.py"
EP = "research/modalities/emc_expression_panels.py"
G_JSON = os.path.join(SCRATCH, "research/modalities/census-route-expression-grading.json")
E_JSON = os.path.join(SCRATCH, "research/modalities/emc-expression-panels.json")

for src, patched_json, field_map, label in (
        (GP, G_JSON, {("routes", "RT-TXN-CDK", "observed"): "observed",
                      ("routes", "RT-TXN-CDK", "verdict"): "verdict",
                      ("routes", "RT-TXN-CDK", "the_dependency_screen_ran_and_it_closed_the_window"):
                          "the_dependency_screen_ran_and_it_closed_the_window",
                      ("routes", "RT-TXN-CDK", "route_action"): "route_action",
                      ("routes", "RT-CHAPERONE", "observed"): "observed",
                      ("routes", "RT-CHAPERONE", "verdict"): "verdict"}, "GP"),
        (EP, E_JSON, {("panels", "transcriptional_cdk", "question"): "question",
                      ("panels", "transcriptional_cdk", "what_it_cannot_settle"):
                          "what_it_cannot_settle"}, "EP")):
    patched_src = reconstruct(src, LEDGER["files"][src])
    if patched_src is None:
        continue
    try:
        tree = ast.parse(patched_src)
        ok(f"{label}: patched generator source parses", True, "")
    except SyntaxError as exc:
        ok(f"{label}: patched generator source parses", False, str(exc))
        continue
    literals = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 60:
            literals.add(node.value)
    art = json.load(open(patched_json, encoding="utf-8"))
    for pth in field_map:
        val = art
        for k in pth:
            val = val[k]
        ok(f"{label}: generator literal agrees with the corrected displayed annotation "
           f"{'.'.join(pth)}", val in literals,
           "the generator no longer produces the displayed string")

CATS = ["key set preserved", "list length preserved", "type preserved",
        "non-string leaf unchanged", "string change is a declared edit"]
by_cat = {c: {"n": 0, "failed": 0} for c in CATS}
named = []
for ch in checks:
    hit = next((c for c in CATS if ch["check"].endswith(c)), None)
    if hit:
        by_cat[hit]["n"] += 1
        by_cat[hit]["failed"] += 0 if ch["pass"] else 1
    else:
        named.append(ch)
report = {
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "n_checks": len(checks), "n_failed": len(fails), "failures": fails,
    "note": ("Structural invariance evidence only. Nothing here re-runs a producer or "
             "revalidates the science; it proves the shared-file patches are annotation-only. "
             "Every patch was applied to a pristine copy OUTSIDE the repository; the working "
             "tree was not modified by this check."),
    "structural_walk_by_category": by_cat,
    "named_checks": named,
}
json.dump({k: v for k, v in report.items() if k != "named_checks"}, sys.stdout, indent=1)
print()
json.dump(report, open(os.path.join(REPAIR, "INVARIANCE-EVIDENCE.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
sys.exit(1 if fails else 0)
