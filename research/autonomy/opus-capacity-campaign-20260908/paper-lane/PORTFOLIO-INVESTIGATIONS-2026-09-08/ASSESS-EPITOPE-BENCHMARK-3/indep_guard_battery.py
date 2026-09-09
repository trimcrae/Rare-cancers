#!/usr/bin/env python3
"""Independent re-run of the guard-firing battery, written here, not imported.

Adds what the subject's battery does not check: the FAIL REASON of every fixture
(a fixture that trips for an unrelated assertion is not evidence for this pin),
and mutations of the OTHER guarded quantities, to show the rest of the guard is
still live after the patch.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/EPITOPE-BENCHMARK"
PATCHED = os.path.join(HERE, "sandbox", "patched", REL)
CORRECT = {"0.5": 93, "0.7": 78, "0.8": 60, "0.9": 34}

def run(mutate):
    d = tempfile.mkdtemp(prefix="assess-")
    t = os.path.join(d, "t")
    shutil.copytree(PATCHED, t)
    p = os.path.join(t, "validated-epitope-counts.json")
    c = json.load(open(p))
    fmd = os.path.join(t, "FINDING.md")
    mutate(c, t)
    json.dump(c, open(p, "w"), indent=2)
    r = subprocess.run([sys.executable, "check_consistency.py"], cwd=t,
                       capture_output=True, text=True)
    shutil.rmtree(d)
    reasons = [l.strip()[2:].strip() for l in r.stdout.splitlines() if l.strip().startswith("- ")]
    return r.returncode, reasons, (r.stdout + r.stderr).strip().replace("\n", " | ")

def lad(**kw):
    def f(c, t):
        L = dict(CORRECT); L.update({k.replace("_", "."): v for k, v in kw.items()})
        c["sufficiency"]["n_required"] = L
    return f

def lad_del(c, t):
    L = dict(CORRECT); L.pop("0.9"); c["sufficiency"]["n_required"] = L

WILSON = "Wilson n table changed"
cases = []
# controls
cases.append(("CONTROL correct ladder 93/78/60/34", lad(), 0, None))
cases.append(("CONTROL 0.9 = 34.0 (same value, float)", lad(**{"0_9": 34.0}), 0, None))
# the eleven claimed fixtures
for lbl, mut in [("0.9=37 (stale value)", lad(**{"0_9": 37})),
                 ("0.9=33", lad(**{"0_9": 33})), ("0.9=35", lad(**{"0_9": 35})),
                 ("0.9=38 (k=floor)", lad(**{"0_9": 38})),
                 ("0.5=92", lad(**{"0_5": 92})), ("0.5=94", lad(**{"0_5": 94})),
                 ("0.7=77", lad(**{"0_7": 77})), ("0.7=79", lad(**{"0_7": 79})),
                 ("0.8=59", lad(**{"0_8": 59})), ("0.8=61", lad(**{"0_8": 61})),
                 ("0.9 row deleted", lad_del)]:
    cases.append(("FIXTURE " + lbl, mut, 1, WILSON))
# extra fixtures this assessment adds
def extra_key(c, t):
    L = dict(CORRECT); L["0.95"] = 20; c["sufficiency"]["n_required"] = L
cases.append(("EXTRA   spurious extra row 0.95=20", extra_key, 1, WILSON))
def str_val(c, t):
    L = dict(CORRECT); L["0.9"] = "34"; c["sufficiency"]["n_required"] = L
cases.append(("EXTRA   0.9 = \"34\" (string, wrong type)", str_val, 1, WILSON))
# other guarded quantities must still be live after the patch
cases.append(("LIVENESS verdict -> SUFFICIENT",
              lambda c, t: (c["sufficiency"].__setitem__("verdict", "SUFFICIENT"),
                            c["sufficiency"].__setitem__("n_required", dict(CORRECT))), 1, "verdict changed"))
cases.append(("LIVENESS CI width -> 0.4507",
              lambda c, t: (c["sufficiency"].__setitem__("achieved_ci_width_at_sens_0.5_with_n_available", 0.4507),
                            c["sufficiency"].__setitem__("n_required", dict(CORRECT))), 1, "CI width != 0.4515"))
cases.append(("LIVENESS BENCHMARK_ELIGIBLE n -> 16",
              lambda c, t: (c["strata"]["BENCHMARK_ELIGIBLE"].__setitem__("n", 16),
                            c["sufficiency"].__setitem__("n_required", dict(CORRECT))), 1, "benchmark-eligible != 15"))

w = max(len(x[0]) for x in cases)
allok = True
print("%-*s | want | got | reason(s)" % (w, "case"))
print("-" * (w + 60))
for label, mut, want, reason in cases:
    rc, reasons, out = run(mut)
    good = (rc == want) and (reason is None or reasons == [reason])
    allok &= good
    print("%-*s | %4d | %3d | %s   %s" % (w, label, want, rc, reasons, "PASS" if good else "**BAD**"))
print()
print("all cases as required:", allok)
sys.exit(0 if allok else 1)
