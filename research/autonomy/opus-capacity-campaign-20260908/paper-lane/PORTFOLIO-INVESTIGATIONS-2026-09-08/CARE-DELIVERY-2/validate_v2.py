#!/usr/bin/env python3
"""Validate care-delivery-element-coverage-v2.json. Non-zero exit on any failure."""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
V1P = os.path.join(os.path.dirname(HERE), "PUB-CARE-DELIVERY", "care-delivery-element-coverage.json")
v1 = json.load(open(V1P)); v2 = json.load(open(os.path.join(HERE, "care-delivery-element-coverage-v2.json")))
ok = []; bad = []
def ck(name, cond, detail=""):
    (ok if cond else bad).append(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")

# 1. the other lane's artifact was not written by this lane
import subprocess
r = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", os.path.relpath(V1P, "/home/user/Rare-cancers")],
                   cwd="/home/user/Rare-cancers")
ck("v1 artifact untouched in the working tree (git diff clean)", r.returncode == 0,
   f"git diff rc={r.returncode}")

# 2. the matrix still spans exactly the v1 series set, same denominators
ck("same series set as v1", set(v2["coverage_matrix"]) == set(v1["coverage_matrix"]))
ck("same n per series as v1",
   all(v2["coverage_matrix"][s]["n"] == v1["coverage_matrix"][s]["n"] for s in v1["coverage_matrix"]))
ck("17 candidate series", v2["candidate_series"] == 17 == len(v2["coverage_matrix"]))
ck("patient sum 1133", sum(c["n"] for c in v2["coverage_matrix"].values()) == 1133 == v2["candidate_patients_sum"])

# 3. every element bucket partitions the 17 series and the 1133 patients
for el, b in v2["element_counts"].items():
    ck(f"[{el}] buckets partition 17 series",
       sum(b[k]["n_series"] for k in b) == 17 and
       sorted(sum((b[k]["series"] for k in b), [])) == sorted(v2["coverage_matrix"]))
    ck(f"[{el}] buckets partition 1133 patients", sum(b[k]["patients"] for k in b) == 1133)

# 4. exactly two series changed, and only rows this lane actually read
changed = [s for s in v1["coverage_matrix"]
           if [v1["coverage_matrix"][s]["elements"][e]["status"] for e in v1["coverage_matrix"][s]["elements"]]
           != [v2["coverage_matrix"][s]["elements"][e]["status"] for e in v2["coverage_matrix"][s]["elements"]]]
ck("only bishop2019 and drilon2008 changed status", sorted(changed) == ["bishop2019", "drilon2008"],
   f"changed={sorted(changed)}")
ck("series_newly_read matches", v2["series_newly_read_by_this_lane"] == ["bishop2019", "drilon2008"])

# 5. every element of the two read rows carries a reading, a section and its v1 status
for s in ("bishop2019", "drilon2008"):
    for el, cell in v2["coverage_matrix"][s]["elements"].items():
        ck(f"[{s}.{el}] has _was_in_v1", "_was_in_v1" in cell)
        if cell["status"] != "NOT_EXAMINED":
            ck(f"[{s}.{el}] cites a section", bool(cell.get("section")))
    ck(f"[{s}] every v1 status was NOT_EXAMINED except a known site row",
       all(c["_was_in_v1"] == "NOT_EXAMINED" for e, c in v2["coverage_matrix"][s]["elements"].items()
           if not (s == "bishop2019" and e == "primary_site_distribution")))

# 6. arithmetic of the quoted counts
b = v2["coverage_matrix"]["bishop2019"]["elements"]
ck("bishop2019 margin 35+6 == 41", 35 + 6 == v2["coverage_matrix"]["bishop2019"]["n"])
px = b["unplanned_excision_defined"]["proxy_reported"]
ck("bishop2019 outside-excision 14 of 41, 27+14==41", px["n"] == 14 and px["of"] == 41 and 27 + 14 == 41)
ck("bishop2019 referral-margin split 12+2==14",
   px["margin_at_referral"]["positive_or_uncertain"] + px["margin_at_referral"]["negative"] == px["n"])
d = v2["coverage_matrix"]["drilon2008"]["elements"]["surgical_margin_distribution"]["derived"]
ck("drilon2008 margin 24+12+7 == 43", d["R0"] + d["R1"] + d["R2"] == d["denominator"] == 43)

# 7. the audit's verdicts are the two decided values and the residue is the three trial reports
a = v2["absence_claim_denominator_audit_v2"]
ck("treatment_setting verdict is FALSE", a["treatment_setting"]["verdict"] == "FALSE")
ck("unplanned_excision verdict is CONFIRMED-at-wider-denominator",
   a["unplanned_excision"]["verdict"].startswith("CONFIRMED AT A WIDER DENOMINATOR"))
ck("examined set is now 4", a["n_examined_now"] == 4 and
   a["series_examined_for_these_two_fields_now"] == sorted(["masunaga2025","chiusole2020","bishop2019","drilon2008"]))
ck("residue is the 3 systemic-therapy trial reports",
   sorted(a["still_reachable_and_unexamined_for_these_fields"]) ==
   ["martinbroto2020immunosarc1", "morioka2016trabectedin", "stacchiotti2013anthracycline"])
ck("treatment_setting REPORTED count is exactly 1 (bishop2019)",
   v2["element_counts"]["treatment_setting_or_referral"]["REPORTED"]["series"] == ["bishop2019"])
ck("unplanned_excision REPORTED count is 0",
   v2["element_counts"]["unplanned_excision_defined"]["REPORTED"]["n_series"] == 0)

# 8. the margin-scale split adds to the margin-REPORTED set
sc = v2["⭐_margin_distributions_are_not_all_on_one_scale"]
ck("margin scale split covers exactly the 4 REPORTED series",
   sorted(sc["on_the_printed_R0_R1_R2_scale"]["series"] + sc["not_on_that_scale"]["series"]) ==
   sorted(v2["element_counts"]["surgical_margin_distribution"]["REPORTED"]["series"]))

for l in ok + bad: print(l)
print(f"\n{len(ok)}/{len(ok)+len(bad)} checks pass")
sys.exit(1 if bad else 0)
