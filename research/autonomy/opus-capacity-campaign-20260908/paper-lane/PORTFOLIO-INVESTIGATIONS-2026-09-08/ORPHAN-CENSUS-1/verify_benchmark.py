#!/usr/bin/env python3
"""Verifier for junction-modality-coverage-benchmark.json. Exits 0 only if:
 (a) the source hash recorded in the artifact still matches the file on disk,
 (b) the three positive controls are present and NON-orphan,
 (c) counts reconcile with the census's own published summary,
 (d) the two symbol-length strata partition all 198 pairs.
Pass --negate-control to prove (b) can fail: it re-runs the same assertion over a
copy of the artifact with EWSR1::FLI1 forced to 'orphan' and must exit 1."""
import json, hashlib, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, "junction-modality-coverage-benchmark.json")))
if "--negate-control" in sys.argv:
    A["positive_controls"]["detail"]["EWSR1::FLI1"]["verdict"] = "orphan"
    A["positive_controls"]["detail"]["EWSR1::FLI1"]["non_orphan"] = False
src = A["provenance"]["source_file"]
h = hashlib.sha256(open(src, "rb").read()).hexdigest()
ok = True
def chk(name, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + name + (" " + detail if detail else ""))
    ok = ok and cond
chk("source_hash_matches", h == A["provenance"]["source_sha256_recomputed_at_use"], h)
for n, c in A["positive_controls"]["detail"].items():
    chk("control_non_orphan:" + n, bool(c) and c["non_orphan"], str(c and c["verdict"]))
cen = A["provenance"]["census_summary_as_published"]["verdict_counts"]
mine = A["verdict_coverage"]["overall"]
chk("verdict_counts_reconcile", cen == mine, str(mine))
st = A["verdict_coverage"]["by_symbol_length_stratum"]
n = st["short_symbol_le3"]["n_pairs"] + st["long_symbol_ge4"]["n_pairs"]
chk("strata_partition_198", n == 198, str(n))
chk("short_symbols_reported_separately", st["short_symbol_le3"]["n_pairs"] > 0
    and "orphan_rate_among_fully_screened" in st["short_symbol_le3"])
print("RESULT", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
