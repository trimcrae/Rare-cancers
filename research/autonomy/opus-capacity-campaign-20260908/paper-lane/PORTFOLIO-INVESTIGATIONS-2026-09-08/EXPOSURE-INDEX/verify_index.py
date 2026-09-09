#!/usr/bin/env python3
"""Independent verification of emc-patient-exposure-index.json.

Reads ONLY the emitted index plus LOCOREGIONAL-2's ledger. Re-derives the
control from the index rows; re-checks that no row is an untraceable zero.
"""
import json
import os
import sys

REPO = "/home/user/Rare-cancers"
L = ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
     "PORTFOLIO-INVESTIGATIONS-2026-09-08")
idx = json.load(open(os.path.join(REPO, L, "EXPOSURE-INDEX",
                                  "emc-patient-exposure-index.json")))
loco = json.load(open(os.path.join(REPO, L, "LOCOREGIONAL-2",
                                   "rt-local-control-contrast-ledger-k2.json")))
fail = []

# 1 -- control reproduces FROM THE INDEX ROWS, not from the control block.
n = e = 0
used = []
for r in idx["rows"]:
    s = r.get("locoregional_contrast_subset")
    if s:
        used.append(r["row_id"])
        n += sum(s["arm_sizes"].values())
        e += sum(s["arm_events"].values())
tn = loco["crude_pooled_per_arm_proportions"]["total_patients_carrying_the_contrast"]
te = loco["crude_pooled_per_arm_proportions"][
    "total_counted_local_recurrence_events_carrying_the_contrast"]
print("control rows:", used)
print("patients from index rows: %d  target %d  %s" % (n, tn, n == tn))
print("events   from index rows: %d  target %d  %s" % (e, te, e == te))
if n != tn:
    fail.append("control patients %d != %d" % (n, tn))
if e != te:
    fail.append("control events %d != %d" % (e, te))
if len(used) != 2:
    fail.append("control must use exactly two rows, used %d" % len(used))

# 2 -- no untraceable zero; every n names a source file.
for r in idx["rows"]:
    for nk, fk in (("n_headline_as_reported", "n_headline_quoted_from"),
                   ("n_emc_patients_as_reported", "n_emc_quoted_from")):
        v = r.get(nk)
        if v is not None and not r.get(fk):
            fail.append("%s: %s has no quoted_from" % (r["row_id"], nk))
        if v == 0 and "MEASURED zero" not in (r.get("note") or ""):
            fail.append("%s: zero without a measured-zero justification"
                        % r["row_id"])

# 3 -- retrieval_completeness is three-valued everywhere.
allowed = {"complete", "partial", "unread"}
bad = [r["row_id"] for r in idx["rows"]
       if r["retrieval_completeness"] not in allowed]
if bad:
    fail.append("bad retrieval_completeness: %s" % bad)

# 4 -- overlap flag present on every row.
miss = [r["row_id"] for r in idx["rows"] if "overlap_unknown" not in r]
if miss:
    fail.append("missing overlap_unknown: %s" % miss)

# 5 -- the index must contain NO portfolio-wide patient total.
banned = ("total_emc_patients", "pooled_n", "distinct_patients",
          "patients_sum", "portfolio_total")
keys = set()
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            keys.add(k)
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
walk(idx)
for b in banned:
    hit = [k for k in keys if b in k]
    if hit:
        fail.append("index contains a forbidden total-shaped key: %s" % hit)

print("rows:", len(idx["rows"]))
print("unread rows:", sum(1 for r in idx["rows"]
                          if r["retrieval_completeness"] == "unread"))
print("n_emc UNKNOWN rows:", sum(1 for r in idx["rows"]
                                 if r["n_emc_status"] == "UNKNOWN"))
print("FAILURES:", fail if fail else "none")
sys.exit(1 if fail else 0)
