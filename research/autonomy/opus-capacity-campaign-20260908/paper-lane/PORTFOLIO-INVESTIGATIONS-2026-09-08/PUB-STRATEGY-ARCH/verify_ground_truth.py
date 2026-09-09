#!/usr/bin/env python3
"""Validation: every ground-truth label in keyword_screen_benchmark.py must be
recoverable from the committed deposit text it cites. Fails loudly, does not warn."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keyword_screen_benchmark import GROUND_TRUTH, FET, ADJ

fet = json.load(open(FET))["task_2_widened_search"]
adj = json.load(open(ADJ))
blob = {}
for key in ("confirmed_fusion_family_defined", "molecularly_defined_not_histology_defined",
            "candidates_requiring_eligibility_text_verification", "screened_and_excluded"):
    for r in fet[key]:
        blob.setdefault(r["nct_id"], "")
        blob[r["nct_id"]] += json.dumps(r)
for a in adj["adjudications"]:
    blob.setdefault(a["nct_id"], "")
    blob[a["nct_id"]] += json.dumps(a)

# Deposit wording that licenses each label, per record. No label is inferred here.
EXPECT = {
    "NCT05918640": ("admits", "fusion FAMILY rather than a specific partner gene"),
    "NCT06571734": ("admits", "ADMITS"),
    "NCT04151342": ("admits", "ADMITS BY WORDING"),
    "NCT06094101": ("refuses", "DOES NOT ADMIT"),
    "NCT07188532": ("refuses", "DOES NOT ADMIT"),
    "NCT07695311": ("refuses", "EXCLUDED for EMC on the retrieved eligibility text"),
    "NCT07328425": ("refuses", "EXCLUDED for EMC on the retrieved eligibility text"),
    "NCT05275426": ("admits", "would have admitted EMC"),
}
fail = 0
for g in GROUND_TRUTH:
    want_verdict, phrase = EXPECT[g["nct"]]
    ok_v = g["verdict"] == want_verdict
    ok_p = phrase in blob.get(g["nct"], "")
    print("%s verdict=%s licensed_by=%r verdict_ok=%s phrase_present=%s"
          % (g["nct"], g["verdict"], phrase, ok_v, ok_p))
    if not (ok_v and ok_p):
        fail += 1
print("FAILURES:", fail)
sys.exit(1 if fail else 0)
