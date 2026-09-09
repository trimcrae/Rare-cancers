#!/usr/bin/env python3
"""TD1 residual batch 2 — BOUNDED STATIC changed-field / structure check.

⛔ This is annotation integrity, not scientific validation. Nothing is computed, executed, sampled,
fetched or re-derived. Every check below is a structural or literal comparison between the frozen
BEFORE bytes and the patched/edited bytes.

Checks
  A  JSON leaf structure — C, G, PUB: no leaf added or removed, no NON-STRING leaf changed, and the
     set of changed STRING leaves is exactly the declared set.
  B  Literal preservation in C — every query string, hit count, PMID/PMCID/DOI, verbatim source
     quotation and dated retrieval declaration survives byte-identically.
  C  G <-> GP generator agreement — each changed G string appears verbatim as a string constant in
     the patched GP source (parsed with `ast`, never executed).
  D  Main manuscript quantities — every numeric token in the frozen BEFORE main is still present in
     the edited main with at least the same multiplicity.
  E  Cohort/threshold literal preservation in the main.

Exit 0 only if every check passes. Any failure exits 1 and prints the failure.
"""
import ast
import hashlib
import json
import re
import sys

BEFORE = sys.argv[1]      # frozen BEFORE copies, flat, path-with-underscores
PATCHED = sys.argv[2]     # patched pristine copies, same naming
LIVE_MAIN = "research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md"

C = "research/literature/fet-fusion-chaperone-clientship-2026-08-27.json"
G = "research/modalities/census-route-expression-grading.json"
GP = "research/modalities/census_route_expression_grading.py"
PUB = "systems/graph/publications.json"
MAIN = LIVE_MAIN

DECLARED = {
    C: {
        "searches_that_returned_nothing_relevant.queries[1].outcome",
        "searches_that_returned_nothing_relevant.queries[5].outcome",
        "searches_that_returned_nothing_relevant.queries[8].outcome",
        "searches_that_returned_nothing_relevant.queries[0].outcome",
        "searches_that_returned_nothing_relevant.queries[3].outcome",
        "searches_that_returned_nothing_relevant.queries[4].outcome",
        "searches_that_returned_nothing_relevant.queries[11].outcome",
        "searches_that_returned_nothing_relevant.queries[13].outcome",
        "what_this_changes.the_grade_should_not_move",
        "what_this_changes.falsifier_F5_of_the_dependency_manuscript",
        "what_this_changes.the_rationale_needs_one_correction",
        "evidence[6].what_it_establishes",   # PMID 28383167
        "evidence[4].what_it_establishes",   # PMID 31171724
        "evidence[9].category",              # PMID 25036637
        "evidence[9].what_it_does_NOT_establish",
        "open_questions_stated_as_unknown[0]",
        "open_questions_stated_as_unknown[3]",
        "retrieval.full_text_read[0]",
        "_supersedes.what_changed",
    },
    G: {
        "routes.RT-TXN-CDK.route_action",
        "routes.RT-CHAPERONE.observed",
        "routes.RT-CHAPERONE.verdict",
    },
    PUB: None,   # list-of-objects graph; declared by id below
}
PUB_DECLARED = {"[PUB-TXN-DEPENDENCY].outcome_potential_why"}

FAIL = []


def flat(path):
    return path.replace("/", "__")


def read(root, path):
    with open(root + "/" + flat(path), encoding="utf-8") as fh:
        return fh.read()


def leaves(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(leaves(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(leaves(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def pub_leaves(text):
    """publications.json is a list of entries; key by entry id so positions are irrelevant."""
    data = json.loads(text)
    out = {}
    for ent in data:
        out.update(leaves(ent, f"[{ent.get('id')}]"))
    return out


def check_json(path, declared, loader=None):
    a = (loader or leaves)(read(BEFORE, path) if loader else json.loads(read(BEFORE, path)))
    b = (loader or leaves)(read(PATCHED, path) if loader else json.loads(read(PATCHED, path)))
    res = {"path": path, "leaves_before": len(a), "leaves_after": len(b)}
    added, removed = sorted(set(b) - set(a)), sorted(set(a) - set(b))
    changed_str, changed_nonstr = [], []
    for k in set(a) & set(b):
        if a[k] != b[k]:
            (changed_str if isinstance(a[k], str) and isinstance(b[k], str)
             else changed_nonstr).append(k)
    res.update({"added": added, "removed": removed,
                "changed_non_string": sorted(changed_nonstr),
                "changed_string": sorted(changed_str)})
    if added or removed:
        FAIL.append(f"{path}: leaves added {added} / removed {removed}")
    if changed_nonstr:
        FAIL.append(f"{path}: NON-STRING leaves changed: {sorted(changed_nonstr)}")
    if set(changed_str) != declared:
        FAIL.append(f"{path}: changed={sorted(changed_str)} declared={sorted(declared)}")
    return res


# ---------------------------------------------------------------- A
report = {"A_json_structure": []}
report["A_json_structure"].append(check_json(C, DECLARED[C]))
report["A_json_structure"].append(check_json(G, DECLARED[G]))
a_pub = pub_leaves(read(BEFORE, PUB))
b_pub = pub_leaves(read(PATCHED, PUB))
pub_changed = sorted(k for k in set(a_pub) & set(b_pub) if a_pub[k] != b_pub[k])
pub_nonstr = [k for k in pub_changed if not (isinstance(a_pub[k], str) and isinstance(b_pub[k], str))]
if set(a_pub) != set(b_pub):
    FAIL.append(f"{PUB}: leaf set changed")
if pub_nonstr:
    FAIL.append(f"{PUB}: NON-STRING leaves changed: {pub_nonstr}")
if set(pub_changed) != PUB_DECLARED:
    FAIL.append(f"{PUB}: changed strings {pub_changed} differ from declared {sorted(PUB_DECLARED)}")
report["A_json_structure"].append({"path": PUB, "leaves_before": len(a_pub),
                                   "leaves_after": len(b_pub), "added": [], "removed": [],
                                   "changed_non_string": pub_nonstr,
                                   "changed_string": pub_changed})

# ---------------------------------------------------------------- B  literal preservation in C
c_before, c_after = json.loads(read(BEFORE, C)), json.loads(read(PATCHED, C))
must_keep = []
for q in c_before["searches_that_returned_nothing_relevant"]["queries"]:
    must_keep.append(("query string " + q["id"], q["query"]))
    must_keep.append(("hit count " + q["id"], str(q["hits"])))
for e in c_before["evidence"]:
    for k in ("PMID", "pmid", "pubmed_url", "doi", "pmcid", "title", "verbatim", "assay"):
        if e.get(k):
            must_keep.append((f"evidence {e.get('PMID')} {k}", e[k]))
must_keep.append(("retrieval date", c_before["retrieval"]["date_et"]))
for s in c_before["retrieval"]["full_text_refused"]:
    must_keep.append(("full_text_refused", s))
def _strings(o):
    if isinstance(o, str):
        return [o]
    if isinstance(o, dict):
        return [x for v in o.values() for x in _strings(v)]
    if isinstance(o, list):
        return [x for v in o for x in _strings(v)]
    return []


after_strings = _strings(c_after)
after_join = "\u0000".join(after_strings)
missing = [(lab, v) for lab, v in must_keep if v not in after_join]
if missing:
    FAIL.append(f"{C}: literals lost: {missing[:8]}")
report["B_literal_preservation_C"] = {"checked": len(must_keep), "missing": len(missing),
                                      "query_ids": [q["id"] for q in c_before["searches_that_returned_nothing_relevant"]["queries"]],
                                      "hit_counts": {q["id"]: q["hits"] for q in c_before["searches_that_returned_nothing_relevant"]["queries"]}}
# hit counts must also be numerically identical leaf-for-leaf
hb = [q["hits"] for q in c_before["searches_that_returned_nothing_relevant"]["queries"]]
ha = [q["hits"] for q in c_after["searches_that_returned_nothing_relevant"]["queries"]]
if hb != ha:
    FAIL.append(f"{C}: hit counts changed {hb} -> {ha}")

# ---------------------------------------------------------------- C  G <-> GP literal agreement
gp_src = read(PATCHED, GP)
tree = ast.parse(gp_src)
consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
g_after = json.loads(read(PATCHED, G))
pairs = {
    "routes.RT-TXN-CDK.route_action": g_after["routes"]["RT-TXN-CDK"]["route_action"],
    "routes.RT-CHAPERONE.observed": g_after["routes"]["RT-CHAPERONE"]["observed"],
    "routes.RT-CHAPERONE.verdict": g_after["routes"]["RT-CHAPERONE"]["verdict"],
}
agree = {}
for field, val in pairs.items():
    n = consts.count(val)
    agree[field] = n
    if n != 1:
        FAIL.append(f"GP: patched source has {n} string constants equal to G's {field} (want 1)")
report["C_G_GP_agreement"] = agree

# ---------------------------------------------------------------- D  main-manuscript quantities
NUM = re.compile(r"(?<![\w.])[-+]?\d+(?:[.,]\d+)*\s*%?")
m_before = read(BEFORE, MAIN)
with open(LIVE_MAIN, encoding="utf-8") as fh:
    m_after = fh.read()
from collections import Counter
nb, na = (Counter(t.strip() for t in NUM.findall(m_before)),
          Counter(t.strip() for t in NUM.findall(m_after)))
lost = {k: (v, na.get(k, 0)) for k, v in nb.items() if na.get(k, 0) < v}
if lost:
    FAIL.append(f"MAIN: numeric tokens lost or reduced: {lost}")
report["D_main_numeric_tokens"] = {
    "distinct_before": len(nb), "total_before": sum(nb.values()),
    "distinct_after": len(na), "total_after": sum(na.values()),
    "lost_or_reduced": lost,
    "added_tokens": sorted(k for k in na if na[k] > nb.get(k, 0))[:60],
}

# ---------------------------------------------------------------- E  cohort / threshold literals
MAIN_KEEP = [
    "24Q4", "Chronos", "− 0.5".replace(" ", ""), "91", "176", "97.8", "GPL6244", "GPL3290",
    "1.0625", "1.8630", "0.1983", "0.4709", "−0.025", "0.077", "−0.832", "0.839",
    "−0.130", "0.200", "Bonferroni", "SMARCB1", "BRD9", "25036637", "24388362", "36495678",
    "25985210", "31171724", "28383167", "26706127",
]
lost_lit = [s for s in MAIN_KEEP if s in m_before and s not in m_after]
if lost_lit:
    FAIL.append(f"MAIN: literals lost: {lost_lit}")
report["E_main_literals"] = {"checked": len(MAIN_KEEP), "lost": lost_lit,
                             "not_present_before": [s for s in MAIN_KEEP if s not in m_before]}

report["identities"] = {
    "main_before_sha256": hashlib.sha256(m_before.encode()).hexdigest(),
    "main_after_sha256": hashlib.sha256(m_after.encode()).hexdigest(),
    "main_before_bytes": len(m_before.encode()), "main_after_bytes": len(m_after.encode()),
}
report["status"] = "FAILED" if FAIL else "PASSED"
report["failures"] = FAIL
json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
print()
sys.exit(1 if FAIL else 0)
