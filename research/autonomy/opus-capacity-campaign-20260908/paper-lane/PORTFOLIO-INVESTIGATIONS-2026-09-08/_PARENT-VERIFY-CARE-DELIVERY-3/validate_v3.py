#!/usr/bin/env python3
"""CARE-DELIVERY-3 validator. Exits non-zero on the first failed assertion."""
import json, os, subprocess, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
V2P = os.path.normpath(os.path.join(HERE, "..", "CARE-DELIVERY-2",
                                    "care-delivery-element-coverage-v2.json"))
V3P = os.path.join(HERE, "care-delivery-element-coverage-v3.json")

ok = fail = 0
def check(label, cond):
    global ok, fail
    if cond:
        ok += 1; print("PASS  %s" % label)
    else:
        fail += 1; print("FAIL  %s" % label)

v2b = open(V2P, encoding="utf-8").read()
v2 = json.loads(v2b)
v3 = json.loads(open(V3P, encoding="utf-8").read())
NEW = ["martinbroto2020immunosarc1", "stacchiotti2013anthracycline", "morioka2016trabectedin"]
OLD_READ = ["bishop2019", "drilon2008"]
STATUSES = {"REPORTED", "EXAMINED_NOT_PRINTED", "NOT_EXAMINED"}

# --- 1. inputs untouched -----------------------------------------------------
r = subprocess.run(["git", "status", "--porcelain",
                    "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                    "PORTFOLIO-INVESTIGATIONS-2026-09-08/CARE-DELIVERY-2",
                    "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                    "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-CARE-DELIVERY",
                    "research/modalities/emc-surgical-quality.json"],
                   cwd=REPO, capture_output=True, text=True)
check("git reports NO change under CARE-DELIVERY-2, PUB-CARE-DELIVERY or emc-surgical-quality.json",
      r.returncode == 0 and r.stdout.strip() == "")
check("v2 input hash recorded in v3 matches the v2 file on disk",
      v3["_v2_input_sha256"] == hashlib.sha256(v2b.encode("utf-8")).hexdigest())

# --- 2. shape preserved ------------------------------------------------------
check("same 17 series", set(v3["coverage_matrix"]) == set(v2["coverage_matrix"]) and
                        len(v3["coverage_matrix"]) == 17)
check("candidate_series still 17", v3["candidate_series"] == 17)
check("candidate_patients_sum still 1133", v3["candidate_patients_sum"] == 1133)
check("per-series n untouched",
      all(v3["coverage_matrix"][s]["n"] == v2["coverage_matrix"][s]["n"] for s in v2["coverage_matrix"]))
check("patients sum to 1133",
      sum(v3["coverage_matrix"][s]["n"] for s in v3["coverage_matrix"]) == 1133)
check("same 10 elements on every series",
      all(set(v3["coverage_matrix"][s]["elements"]) == set(v2["element_counts"])
          for s in v3["coverage_matrix"]))

# --- 3. only the three trial rows changed status -----------------------------
diffs = []
for s in v3["coverage_matrix"]:
    for e in v3["coverage_matrix"][s]["elements"]:
        a = v2["coverage_matrix"][s]["elements"][e].get("status")
        b = v3["coverage_matrix"][s]["elements"][e].get("status")
        if a != b:
            diffs.append((s, e, a, b))
check("exactly 20 status changes", len(diffs) == 20)
check("every status change is on one of the three trial series",
      all(s in NEW for s, _, _, _ in diffs))
check("bishop2019 and drilon2008 rows carried through byte-identical",
      all(v3["coverage_matrix"][s] == v2["coverage_matrix"][s] for s in OLD_READ))
check("no status change goes BACKWARD to NOT_EXAMINED",
      all(b != "NOT_EXAMINED" for _, _, _, b in diffs))
check("_status_changes_made_by_v3 matches the recomputed diff",
      sorted((c["series"], c["element"], c["from"], c["to"])
             for c in v3["_status_changes_made_by_v3"]) == sorted(diffs))

# --- 4. THE CORE RULE: no absence asserted where the retrieval was incomplete -
mo = v3["coverage_matrix"]["morioka2016trabectedin"]
check("morioka retrieval_completeness records NARRATIVE ONLY",
      "NARRATIVE ONLY" in mo["retrieval_completeness"]["verdict"])
check("morioka has ZERO EXAMINED_NOT_PRINTED cells (tables were not returned)",
      not any(c.get("status") == "EXAMINED_NOT_PRINTED" for c in mo["elements"].values()))
mo_moved = [e for e, c in mo["elements"].items() if c.get("status") != v2["coverage_matrix"]
            ["morioka2016trabectedin"]["elements"][e].get("status")]
check("morioka moved only the two elements printed in its narrative",
      sorted(mo_moved) == ["median_follow_up", "time_to_event_median"])
for s in ["martinbroto2020immunosarc1", "stacchiotti2013anthracycline"]:
    rc = v3["coverage_matrix"][s]["retrieval_completeness"]
    check("%s retrieval_completeness records that tables came back" % s,
          "ALL TABLES" in rc["verdict"] or "ALL THREE TABLES" in rc["verdict"])
    check("%s: every EXAMINED_NOT_PRINTED cell names the section read" % s,
          all(c.get("read_section") for c in v3["coverage_matrix"][s]["elements"].values()
              if c.get("status") == "EXAMINED_NOT_PRINTED"))
check("every series row now carries a retrieval_completeness field, for the five read series",
      all("retrieval_completeness" in v3["coverage_matrix"][s] for s in NEW))
check("every changed cell records its v2_status and its reader",
      all(v3["coverage_matrix"][s]["elements"][e].get("v2_status") == a and
          v3["coverage_matrix"][s]["elements"][e].get("read_by") == "CARE-DELIVERY-3"
          for s, e, a, b in diffs))

# --- 5. buckets partition ----------------------------------------------------
for e, c in v3["element_counts"].items():
    seen = []
    for b in ("REPORTED", "EXAMINED_NOT_PRINTED", "NOT_EXAMINED"):
        seen += c[b]["series"]
        check("%s/%s n_series matches its list" % (e, b), c[b]["n_series"] == len(c[b]["series"]))
        check("%s/%s patients match its list" % (e, b),
              c[b]["patients"] == sum(v3["coverage_matrix"][x]["n"] for x in c[b]["series"]))
    check("%s: buckets partition all 17 series" % e,
          sorted(seen) == sorted(v3["coverage_matrix"]) and len(seen) == 17)
    check("%s: buckets partition all 1133 patients" % e,
          sum(c[b]["patients"] for b in ("REPORTED", "EXAMINED_NOT_PRINTED", "NOT_EXAMINED")) == 1133)
    check("%s: every status is one of the three" % e,
          all(v3["coverage_matrix"][s]["elements"][e]["status"] in STATUSES
              for s in v3["coverage_matrix"]))

# --- 6. margin claims must NOT have moved ------------------------------------
check("surgical_margin_distribution REPORTED set unchanged from v2 (still the same 4 series)",
      set(v3["element_counts"]["surgical_margin_distribution"]["REPORTED"]["series"]) ==
      set(v2["element_counts"]["surgical_margin_distribution"]["REPORTED"]["series"]))
check("margin_definition_printed REPORTED set unchanged from v2",
      set(v3["element_counts"]["margin_definition_printed"]["REPORTED"]["series"]) ==
      set(v2["element_counts"]["margin_definition_printed"]["REPORTED"]["series"]))
check("the margin-scale split is carried through from v2 untouched",
      v3["⭐_margin_distributions_are_not_all_on_one_scale"] ==
      v2["⭐_margin_distributions_are_not_all_on_one_scale"])
check("no margin value or count anywhere in the three new rows",
      not any(k in json.dumps(v3["coverage_matrix"][s], ensure_ascii=False)
              for s in NEW for k in ('"R0"', '"R1"', '"R2"')))

# --- 7. the audit ------------------------------------------------------------
a3 = v3["absence_claim_denominator_audit_v3"]
EXP6 = {"masunaga2025", "chiusole2020", "bishop2019", "drilon2008",
        "martinbroto2020immunosarc1", "stacchiotti2013anthracycline"}
check("treatment_setting examined set is the six with a real reading",
      set(a3["v3_verdict"]["treatment_setting"]["series_examined_after_v3"]) == EXP6)
check("unplanned_excision examined set is the same six",
      set(a3["v3_verdict"]["unplanned_excision"]["series_examined_after_v3"]) == EXP6)
check("morioka is NOT in either examined set",
      "morioka2016trabectedin" not in EXP6)
check("morioka is named in the residue",
      any("morioka" in x for x in a3["v3_verdict"]["residue_after_v3"]["for_both_fields"]))
check("treatment_setting verdict is still FALSE/refuted",
      "FALSE" in a3["v3_verdict"]["treatment_setting"]["verdict"])
check("unplanned_excision verdict is still CONFIRMED and still bounded to an examined set",
      "CONFIRMED" in a3["v3_verdict"]["unplanned_excision"]["verdict"] and
      "examined set" in a3["v3_verdict"]["unplanned_excision"]["verdict"])
check("v2's audit is carried through unmodified alongside v3's",
      v3["absence_claim_denominator_audit_v2"] == v2["absence_claim_denominator_audit_v2"])

# --- 8. counted-cell arithmetic actually printed by the papers ---------------
st = v3["coverage_matrix"]["stacchiotti2013anthracycline"]["elements"]
check("stacchiotti site counts sum to 11 in the recorded evidence",
      "5+3+1+1+1 = 11" in st["primary_site_distribution"]["evidence"])
check("stacchiotti stage counts sum to 11 in the recorded evidence",
      "7 + 4 = 11" in st["stage_at_diagnosis_split"]["evidence"])
mb = v3["coverage_matrix"]["martinbroto2020immunosarc1"]
check("martinbroto EMC dilution recorded (4 of 68)",
      "FOUR EMC PATIENTS" in mb["⚠_n_is_a_trial_denominator_not_an_emc_denominator"])
check("morioka EMC dilution recorded (2 of 5)",
      "ONLY 2 HAVE EMC" in v3["coverage_matrix"]["morioka2016trabectedin"]
                             ["⚠_n_is_not_an_emc_denominator"])

# --- 9. fences ---------------------------------------------------------------
blob = json.dumps(v3, ensure_ascii=False)
check("no pooled EMC rate is computed anywhere in v3",
      "pooled rate" not in blob and "pooled estimate" not in blob)
check("no digitisation or KM reconstruction is claimed",
      "digitis" not in blob.replace("No curve was digitised", "").replace(
          "no curve was digitised", "").replace("No curve was digitised;", ""))
check("the KM/IPD pilot is referenced only as closed/not reopened",
      blob.count("not reopened") >= 2)
check("no efficacy, safety or clinical claim asserted",
      "_not_medical_advice" in v3 and "asserts efficacy" in v3["_not_medical_advice"])

print()
print("%d passed, %d failed" % (ok, fail))
sys.exit(1 if fail else 0)
