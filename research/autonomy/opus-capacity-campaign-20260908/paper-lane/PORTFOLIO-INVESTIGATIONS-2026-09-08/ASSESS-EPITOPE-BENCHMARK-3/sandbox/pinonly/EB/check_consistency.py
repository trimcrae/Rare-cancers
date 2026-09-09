#!/usr/bin/env python3
"""Assert the counts quoted in FINDING.md / VALIDATED-EPITOPE-TABLE.md match the derived JSON."""
import json, re, sys
c = json.load(open("validated-epitope-counts.json")); s = c["strata"]; su = c["sufficiency"]
f = open("FINDING.md").read(); t = open("VALIDATED-EPITOPE-TABLE.md").read()
fails = []
def ck(cond, msg):
    if not cond: fails.append(msg)
ck(s["BENCHMARK_ELIGIBLE"]["n"] == 15,        "benchmark-eligible != 15")
ck(s["ms_eluted_ci_eligible"]["n"] == 6,      "MS-eluted class I subset != 6")
ck(s["prediction_only"]["n"] == 3,            "prediction-only != 3")
ck(s["binding_only"]["n"] == 7,               "binding-only != 7")
ck(s["spans_junction_no"]["n"] == 6,          "negative controls != 6")
ck(su["n_required"] == {"0.5":93,"0.7":78,"0.8":60,"0.9":34}, "Wilson n table changed")
ck(su["verdict"] == "INSUFFICIENT",           "verdict changed")
ck(len(c["distinct_fusions_in_benchmark"]) == 9, "distinct fusions != 9")
ck(su["achieved_ci_width_at_sens_0.5_with_n_available"] == 0.4515, "CI width != 0.4515")
# prose must quote the same numbers
ck("**n = 15**" in f,   "FINDING.md does not quote n = 15")
ck("n = **6**" in f,    "FINDING.md does not quote the MS-eluted n = 6")
ck("0.4515" in f,       "FINDING.md does not quote the achieved CI width")
ck(re.search(r"\|\s*0\.5\s*\|\s*93\s*\|", f) is not None, "FINDING.md sufficiency table lost 93")
ck("PREDICTION ONLY" in t and "BINDING ONLY" in t, "table lost its excluded strata")
ck(t.count("| E") >= 40, "table lost rows")
if fails:
    print("FAIL:"); [print("  -", m) for m in fails]; sys.exit(1)
print("consistency OK: n=15 eligible, 6 MS-eluted, 3 prediction-only, 7 binding-only,")
print("6 negative controls, 9 fusions, Wilson 93/78/60/37, verdict INSUFFICIENT,")
print("and FINDING.md/VALIDATED-EPITOPE-TABLE.md quote the same figures.")
