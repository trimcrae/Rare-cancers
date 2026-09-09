"""Disposable negative fixtures for the three new Agaram-only pins.

Nothing here touches the tracked tree: files are copied into a temp dir under the scratchpad,
perturbed there, and checked with the UNMODIFIED lint_consistency.check_artifact_figures.
"""
import copy, importlib.util, json, os, re, shutil, sys, tempfile

REPO = "/home/user/Rare-cancers"
ART = "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json"
MD = "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"
IDS = ["fusion_partner_agaram2014_dod_taf15_percent",
       "fusion_partner_agaram2014_dod_comparator_percent",
       "fusion_partner_agaram2014_dod_fisher_p"]

spec = importlib.util.spec_from_file_location(
    "lc", os.path.join(REPO, "research/manuscripts/lint_consistency.py"))
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)

full = json.load(open(os.path.join(REPO, "research/manuscripts/pinned-figures.json"),
                      encoding="utf-8"))
entries = {e["id"]: e for e in full["artifact_figures"] if e.get("id") in IDS}
assert len(entries) == 3, sorted(entries)

CUR = ("analyses.B_outcome_by_partner.source_verified_recorded_outcomes"
       ".disease_specific_death")
LEAF = {IDS[0]: ("taf15_arm", "percent"), IDS[1]: ("comparator_arm", "percent"),
        IDS[2]: ("fisher_exact_two_sided_p",)}
BUMP = {IDS[0]: 41.9, IDS[1]: 7.2, IDS[2]: 0.0772}
MDSUB = {IDS[0]: (r"\*\*3/7 = 42\.9 %\*\*", "**3/7 = 41.9 %**"),
         IDS[1]: (r"\*\*1/16 = 6\.2 %\*\* \(95 % CI 1\.1", "**1/16 = 7.2 %** (95 % CI 1.1"),
         IDS[2]: (r"\| 36\.6 pts \| 0\.0672 \|", "| 36.6 pts | 0.0772 |")}

def build(tmp):
    for rel in (ART, MD):
        os.makedirs(os.path.join(tmp, os.path.dirname(rel)), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), os.path.join(tmp, rel))

def run(tmp, ids):
    reg = {"artifact_figures": [entries[i] for i in ids]}
    return lc.check_artifact_figures(reg, repo=tmp)

def perturb_artifact(tmp, pid):
    p = os.path.join(tmp, ART)
    doc = json.load(open(p, encoding="utf-8"))
    cur = doc
    for part in CUR.split("."):
        cur = cur[part]
    path = LEAF[pid]
    for part in path[:-1]:
        cur = cur[part]
    before = cur[path[-1]]
    cur[path[-1]] = BUMP[pid]
    json.dump(doc, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return before, BUMP[pid]

def perturb_md(tmp, pid):
    p = os.path.join(tmp, MD)
    txt = open(p, encoding="utf-8").read()
    pat, rep = MDSUB[pid]
    new, n = re.subn(pat, rep, txt, count=1)
    assert n == 1, (pid, "manuscript perturbation pattern did not match exactly once")
    open(p, "w", encoding="utf-8").write(new)

results = []

# C0 -- unperturbed baseline: all three must PASS.
with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as t:
    build(t)
    f = run(t, IDS)
    results.append(("C0 baseline, no perturbation", "PASS (0 findings)", len(f) == 0,
                    [x["rule"] for x in f]))

# C1-C3 -- perturb the ARTIFACT leaf, one at a time.
for pid in IDS:
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as t:
        build(t)
        b, a = perturb_artifact(t, pid)
        f = run(t, [pid])
        ok = len(f) == 1 and f[0]["rule"] in ("A-figure-mismatch","A-figure-not-stated")
        results.append((f"C-art {pid}: artifact {b} -> {a}", "REJECT", ok,
                        [x["rule"] + ": " + x["message"] for x in f]))

# C4-C6 -- perturb the MANUSCRIPT printed digits, one at a time.
for pid in IDS:
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as t:
        build(t)
        perturb_md(t, pid)
        f = run(t, [pid])
        ok = len(f) == 1 and f[0]["rule"] in ("A-figure-mismatch","A-figure-not-stated")
        results.append((f"C-md {pid}: manuscript cell perturbed", "REJECT", ok,
                        [x["rule"] + ": " + x["message"] for x in f]))

# C7 -- specificity: perturb the NEIGHBOURING local-recurrence row's identical 1/16 = 6.2 %.
#       The comparator pin must NOT fire, proving it is bound to the right row.
with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as t:
    build(t)
    p = os.path.join(t, MD)
    txt = open(p, encoding="utf-8").read()
    new, n = re.subn(r"local recurrence \| 2/7 = 28\.6 % \(8\.2–64\.1\) \| 1/16 = 6\.2 %",
                     "local recurrence | 2/7 = 28.6 % (8.2–64.1) | 1/16 = 9.9 %", txt, count=1)
    assert n == 1, "neighbour-row pattern did not match exactly once"
    open(p, "w", encoding="utf-8").write(new)
    f = run(t, [IDS[1]])
    results.append(("C7 specificity: neighbouring local-recurrence 6.2 % -> 9.9 %",
                    "PASS (comparator pin unaffected)", len(f) == 0,
                    [x["rule"] for x in f]))

bad = 0
for name, expect, ok, detail in results:
    print(("OK  " if ok else "FAIL") + f" | {name} | expected {expect}")
    for d in detail:
        print("       " + d[:200])
    bad += 0 if ok else 1
print(f"\n{len(results)} fixtures, {bad} not as required")
sys.exit(1 if bad else 0)
