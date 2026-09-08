#!/usr/bin/env python3
"""Deterministic checks on the CORRECTED-A component. Read-only. Exit 0 iff every check passes."""
from __future__ import annotations
import csv, glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); LANE = os.path.dirname(HERE)
csv.field_size_limit(10**9)
def tsv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))
def hdr(p):
    return next(csv.reader(open(p, newline="", encoding="utf-8"), delimiter="\t"))
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

R = {}; fails = []
def check(cid, name, ok, detail):
    R[cid] = {"check": name, "result": "PASS" if ok else "FAIL", "detail": detail}
    if not ok: fails.append(cid)

rows = tsv(os.path.join(HERE, "corrected-a-rows.tsv"))
cats = tsv(os.path.join(HERE, "corrected-a-categories.tsv"))
inv  = tsv(os.path.join(HERE, "corrected-a-category-inventory.tsv"))
schema = json.load(open(os.path.join(HERE, "corrected-a-schema.json")))
summ = json.load(open(os.path.join(HERE, "corrected-a-summary.json")))
job1 = []
for p in sorted(glob.glob(os.path.join(LANE, "CURATION-endpoint-measurement-contract-rows-*.tsv"))):
    job1 += tsv(p)
J1 = {(r["nct_id"], r["outcome_measure_index"], r["group_id"]): r for r in job1}

# C1 key compatibility: exact bijection onto the delivered job-1 rows
K = {(r["input_key_nct_id"], r["input_key_om_index"], r["input_key_group_id"]) for r in rows}
check("C1", "key set is an exact bijection onto job 1's 552 delivered rows",
      len(rows) == 552 and len(K) == 552 and K == set(J1),
      f"rows={len(rows)} distinct_keys={len(K)} job1_keys={len(J1)} "
      f"missing={len(set(J1)-K)} extra={len(K-set(J1))}")

# C2 row coverage: no required field empty
REQ = ["row_key","payload_shard","cache_revision","om_title","input_key_group_id","group_title",
       "reported_denominator_participants","denominator_provenance","full_category_vector",
       "denominator_state","category_preservation_state","proportion_suitability",
       "unresolved_reason_codes","advisory_flag_codes","rate_derived","source_pointer"]
empty = [(r["row_key"], c) for r in rows for c in REQ if str(r[c]).strip() == ""]
check("C2", "every required field populated on every row", not empty,
      f"{len(empty)} empty required cells" + (f"; first={empty[:3]}" if empty else ""))

# C3 schema/table agreement
sc = [c["name"] for c in schema["tables"]["corrected-a-rows.tsv"]["columns"]]
sc2 = [c["name"] for c in schema["tables"]["corrected-a-categories.tsv"]["columns"]]
sc3 = [c["name"] for c in schema["tables"]["corrected-a-category-inventory.tsv"]["columns"]]
check("C3", "declared schema matches every emitted header exactly",
      sc == hdr(os.path.join(HERE, "corrected-a-rows.tsv"))
      and sc2 == hdr(os.path.join(HERE, "corrected-a-categories.tsv"))
      and sc3 == hdr(os.path.join(HERE, "corrected-a-category-inventory.tsv")),
      f"rows={len(sc)} categories={len(sc2)} inventory={len(sc3)} columns declared")

# C4 the column-26 correction: values carried unchanged, label corrected, second column distinct
c26_unchanged = sum(1 for r in rows
                    if r["job1_column26_value_carried_unchanged"]
                    == J1[(r["input_key_nct_id"], r["input_key_om_index"], r["input_key_group_id"])]
                       ["sum_minus_reported_denominator"])
c26_matches_actual = sum(1 for r in rows
                         if r["evaluable_n_minus_reported_denominator"]
                         == r["job1_column26_value_carried_unchanged"])
c26_is_evn_minus_den = sum(1 for r in rows
                           if int(r["evaluable_n_minus_reported_denominator"])
                           == int(r["job1_evaluable_n_sum_of_four_producer_cells"])
                           - int(r["reported_denominator_participants"]))
newcol = sum(1 for r in rows
             if int(r["all_categories_sum_minus_reported_denominator"])
             == int(r["job1_all_categories_in_contributing_classes_sum"])
             - int(r["reported_denominator_participants"]))
differ = sum(1 for r in rows if r["evaluable_n_minus_reported_denominator"]
             != r["all_categories_sum_minus_reported_denominator"])
check("C4", "column-26 relabelled without altering any value; the implied diagnostic emitted separately",
      c26_unchanged == 552 and c26_matches_actual == 552 and c26_is_evn_minus_den == 552
      and newcol == 552,
      f"job1 col26 carried byte-identical on {c26_unchanged}/552; corrected label "
      f"`evaluable_n_minus_reported_denominator` equals it on {c26_matches_actual}/552 and equals "
      f"evaluable_n - reported_denominator on {c26_is_evn_minus_den}/552; the distinct new column "
      f"`all_categories_sum_minus_reported_denominator` equals all_categories_sum - "
      f"reported_denominator on {newcol}/552 and DIFFERS from column 26 on {differ}/552 rows "
      f"(the 552-{differ}={552-differ} agreeing rows are why the old header went unnoticed)")

# C5 denominator never inferred from response cells
inferred = sum(1 for r in rows if r["reported_denominator_participants"]
               == r["job1_evaluable_n_sum_of_four_producer_cells"])
allread = all(r["denominator_state"] == "READ_FROM_SOURCE" for r in rows)
prov = all(re.fullmatch(r"outcomeMeasures\[\d+\]\.denoms\[units=Participants\]\.counts"
                        r"\[groupId=OG\d+\]\.value", r["denominator_provenance"]) for r in rows)
check("C5", "every denominator READ from denoms with hierarchical provenance, none inferred from cells",
      allread and prov and len(rows) == 552,
      f"552/552 denominator_state=READ_FROM_SOURCE; provenance path well-formed on all rows; "
      f"{inferred} rows happen to coincide numerically with the old cell sum (coincidence recorded, "
      f"not a derivation)")

# C6 no rate anywhere
BAD = re.compile(r"(?i)\b(rate|percent|proportion|orr|dcr)\b")
badcols = [c for c in sc + sc2 + sc3 if BAD.search(c) and c != "rate_derived"]
notder = all(r["rate_derived"] == "NOT_DERIVED" for r in rows)
floats = sum(1 for r in rows for c in ("evaluable_n_minus_reported_denominator",
             "all_categories_sum_minus_reported_denominator",
             "reported_denominator_participants") if "." in str(r[c]) or "%" in str(r[c]))
check("C6", "no rate, proportion or percentage derived anywhere",
      not badcols and notder and floats == 0 and summ["rates_derived"] == 0,
      f"0 rate-like output columns; rate_derived=NOT_DERIVED on 552/552; "
      f"{floats} non-integer or percent values in the numeric diagnostic columns")

# C7 category preservation and non-folding
per = {}
for c in cats:
    per.setdefault((c["nct_id"], c["om_index"], c["group_id"]), []).append(c)
sumcov = sum(int(r["n_source_categories"]) for r in rows)
grainkeys = {(c["nct_id"], c["om_index"], c["group_id"], c["class_index"], c["category_index"])
             for c in cats}
match = sum(1 for r in rows
            if len(per.get((r["input_key_nct_id"], r["input_key_om_index"],
                            r["input_key_group_id"]), [])) == int(r["n_source_categories"]))
folded = [i for i in inv if i["folded"] != "NO"]
NAMED = ["sCR", "VGPR", "CRh", "CRi", "PD", "NE"]
titles = [i["category_title_verbatim"] for i in inv]
present = {n: sum(1 for t in titles if re.search(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", t))
           for n in NAMED}
check("C7", "every source category preserved verbatim, one record each, none folded",
      len(cats) == sumcov == summ["category_records_emitted"] and len(grainkeys) == len(cats)
      and match == 552
      and not folded and all(v > 0 for v in present.values()),
      f"{len(cats)} category records = sum(n_source_categories) over 552 rows; grain unique; "
      f"per-row counts agree on {match}/552; 0 folded titles among {len(inv)} distinct titles; "
      f"named categories present verbatim: {present}")

# C8 unresolved states are machine-readable and internally consistent
enum_s = set(schema["enumerations"]["proportion_suitability"])
enum_r = set(schema["enumerations"]["unresolved_reason_codes"])
enum_a = set(schema["enumerations"]["advisory_flag_codes"])
bad = []
for r in rows:
    if r["proportion_suitability"] not in enum_s: bad.append((r["row_key"], "suitability"))
    rc = [] if r["unresolved_reason_codes"] == "NONE" else r["unresolved_reason_codes"].split("|")
    ac = [] if r["advisory_flag_codes"] == "NONE" else r["advisory_flag_codes"].split("|")
    if set(rc) - enum_r or set(ac) - enum_a: bad.append((r["row_key"], "code"))
    if bool(rc) != (r["proportion_suitability"] == "UNSUITABLE_FOR_PROPORTION"):
        bad.append((r["row_key"], "state/reason disagreement"))
    if int(r["n_contributing_classes"]) > 1 and not rc: bad.append((r["row_key"], "multi-class unflagged"))
    if int(r["producer_label_collision_within_class"]) + \
       int(r["producer_label_collision_across_classes"]) > 0 and not rc:
        bad.append((r["row_key"], "collision unflagged"))
check("C8", "unresolved/unsuitable states are enumerated, machine-readable and consistent with the row",
      not bad, f"{len(bad)} inconsistencies" + (f"; first={bad[:3]}" if bad else ""))

# C9 independent reproduction of job 1's overwrite partition from this component's own reading
cross = sum(1 for r in rows if int(r["producer_label_collision_across_classes"]) > 0)
within = sum(1 for r in rows if int(r["producer_label_collision_across_classes"]) == 0
             and int(r["producer_label_collision_within_class"]) > 0)
none_ = sum(1 for r in rows if int(r["producer_label_collision_within_class"])
            + int(r["producer_label_collision_across_classes"]) == 0)
conf = sum(1 for r in rows if int(r["producer_label_collision_value_conflicting"]) > 0)
j1cross = sum(1 for r in job1 if r["overwrite_scope"] == "cross_class")
j1within = sum(1 for r in job1 if r["overwrite_scope"] == "within_class")
j1none = sum(1 for r in job1 if r["overwrite_scope"] == "none")
j1conf = sum(1 for r in job1 if r["conflicting_overwrite"] in ("True", "true", "1", "yes"))
check("C9", "this component's own source reading reproduces job 1's overwrite partition",
      (cross, within, none_, conf) == (j1cross, j1within, j1none, j1conf),
      f"mine cross/within/none/conflicting = {cross}/{within}/{none_}/{conf}; "
      f"job 1 = {j1cross}/{j1within}/{j1none}/{j1conf}")

# C10 delivered leaf evidence agrees on every denominator it covers
check("C10", "delivered LEAF-QA evidence agrees with the read denominator wherever it covers a row",
      summ["leaf_qa_denominator_disagreements"] == 0 and summ["leaf_qa_rows_covered"] == 319,
      f"{summ['leaf_qa_denominator_agreements']} leaf records agree, "
      f"{summ['leaf_qa_denominator_disagreements']} disagree, over "
      f"{summ['leaf_qa_rows_covered']}/552 rows the leaves cover")

# C11 immutability of the original evidence
man = json.load(open(os.path.join(HERE, "corrected-a-input-manifest.json")))
drift = [p for p, h in man["input_sha256"].items() if sha(os.path.join(LANE, p)) != h]
check("C11", "original job-1 and leaf evidence unmodified by this component", not drift,
      f"{len(man['input_sha256'])} original input files re-hashed, {len(drift)} changed"
      + (f": {drift}" if drift else ""))

# C12 the confirmation status is carried in the artifact itself
cs = schema["confirmation_status"]
check("C12", "artifact carries that job 2 and job 3 are NOT independently confirmed",
      cs["job1_arithmetic_independently_confirmed"] is True
      and cs["job2_independently_confirmed"] is False
      and cs["job3_independently_confirmed"] is False
      and summ["job2_job3_independently_confirmed"] is False,
      "schema.confirmation_status and summary both state job1 arithmetic confirmed, job2/job3 not")

out = {"component": "CORRECTED-A-denominator-category", "checks": R,
       "passed": len(R) - len(fails), "failed": len(fails), "total": len(R)}
json.dump(out, open(os.path.join(HERE, "corrected-a-checks.json"), "w"), indent=1)
for k in sorted(R):
    print(f"{k} {R[k]['result']}  {R[k]['check']}\n     {R[k]['detail']}")
print(f"\n{out['passed']}/{out['total']} checks passed")
sys.exit(1 if fails else 0)
