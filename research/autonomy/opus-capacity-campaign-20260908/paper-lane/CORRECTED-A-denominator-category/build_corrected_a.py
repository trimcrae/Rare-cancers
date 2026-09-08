#!/usr/bin/env python3
"""CORRECTED-A — denominator / category correction component.

New sibling artifact. Reads only:
  (a) the delivered ClinicalTrials.gov payload cache copy (local files, NO network),
  (b) the delivered job-1 shard TSVs (CURATION-endpoint-measurement-contract-rows-*.tsv),
  (c) the delivered leaf evidence LEAF-OUT/LEAF-QA-group{0,1,2,3}.tsv (cross-check only).

Writes only files under CORRECTED-A-denominator-category/. It overwrites nothing, re-fetches
nothing, re-runs no producer, and derives NO rate, proportion or percentage anywhere.
"""
from __future__ import annotations
import collections, csv, glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
CACHE = ("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/"
         "scratchpad/ctg-cache-216bd1b5")
CACHE_REV = "216bd1b5fb25a56b90ef3cc2373e1fe68322708f"

BOR = [f"ctg_results_bor_{t}" for t in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]
PLA = [f"ctg_placebo_onc_{t}" for t in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]

# The PRODUCER's four regexes, reproduced verbatim, used ONLY to label which source categories the
# producer captured / dropped / collided on. They are a description of the old behaviour. They are
# NOT this component's taxonomy: every source category is preserved under its own title regardless.
PRODUCER_CATEGORY = {
    "CR": re.compile(r"^\s*(complete response|complete remission|CR)\b", re.I),
    "PR": re.compile(r"^\s*(partial response|partial remission|PR)\b", re.I),
    "SD": re.compile(r"^\s*(stable disease|SD)\b", re.I),
    "PD": re.compile(r"^\s*(progressive disease|disease progression|PD)\b", re.I),
}

# Response-category vocabularies that the producer's four-label regex DROPS but which are RESPONSE
# categories (not "non-evaluable"). Matching a title here does NOT fold it into any common taxonomy:
# the title is preserved verbatim everywhere. The flag only records that a responder-bearing category
# was dropped by the old extraction, so the loss is visible instead of silent.
RESPONSE_LIKE_DROPPED = re.compile(
    r"^\s*(sCR|stringent complete (response|remission)|VGPR|very good partial (response|remission)|"
    r"CRh|CRi|CRu|CRmrd|nCR|near complete|minimal response|\bMR\b|marrow CR|"
    r"non-?CR ?/ ?non-?PD|molecular (complete )?response|MRD)", re.I)
NONEVAL_LIKE = re.compile(
    r"^\s*(NE\b|not evaluable|non-?evaluable|unknown|missing|not done|UE\b|indeterminate|"
    r"not assessed|no post-?baseline|died before|unable to evaluate|not applicable|NA\b)", re.I)

def payload(name):
    p = os.path.join(CACHE, name + ".txt")
    raw = open(p, encoding="utf-8").read()
    i = raw.find("=" * 30)
    body = raw[raw.find("\n", i) + 1:] if i >= 0 else raw
    return json.loads(body)

def tsv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def esc(s):
    return (s or "").replace("\t", " ").replace("\n", " ").replace("\r", " ")

# ---------------------------------------------------------------- job-1 delivered rows (immutable)
job1 = []
for p in sorted(glob.glob(os.path.join(LANE, "CURATION-endpoint-measurement-contract-rows-*.tsv"))):
    job1 += tsv(p)
J1 = {(r["nct_id"], r["outcome_measure_index"], r["group_id"]): r for r in job1}
assert len(J1) == len(job1) == 552, (len(J1), len(job1))

# ------------------------------------------------------------------------ corrected source reading
CATROWS = []          # atomic category ledger
ROWS = {}             # per job-1 key
for name in BOR + PLA:
    doc = payload(name)
    for s in doc.get("studies") or []:
        ps, rs = s.get("protocolSection") or {}, s.get("resultsSection") or {}
        nct = (ps.get("identificationModule") or {}).get("nctId")
        oms = ((rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures")) or []
        for oi, om in enumerate(oms):
            groups = {g.get("id"): (g.get("title") or "") for g in om.get("groups") or []}
            classes = om.get("classes") or []
            # denominators, READ from the record. Never inferred from any sum.
            denoms = {}          # units -> {gid: value}
            for d in om.get("denoms") or []:
                u = d.get("units") or ""
                denoms.setdefault(u, {})
                for c in d.get("counts") or []:
                    denoms[u][c.get("groupId")] = c.get("value")
            for gid in groups:
                key = (nct, str(oi), gid)
                if key not in J1:
                    continue
                j = J1[key]
                # The same study can appear in more than one payload family. Job 1 recorded exactly
                # one shard per row; read that shard's copy only, so the grain stays 1:1 with the
                # delivered row and no duplicate-shard record inflates the category ledger.
                if j["shard"] != name:
                    continue
                dparts = denoms.get("Participants", {}).get(gid)
                # every class/category of this group in this outcome measure, preserved as reported
                cats, cls_sum, contributing = [], {}, set()
                prod_assign = collections.defaultdict(list)   # producer label -> [(ci, title, val)]
                for ci, cl in enumerate(classes):
                    ctitle = cl.get("title") or ""
                    for kk, cat in enumerate(cl.get("categories") or []):
                        title = cat.get("title") or ""
                        for meas in cat.get("measurements") or []:
                            if meas.get("groupId") != gid:
                                continue
                            raw = meas.get("value")
                            try:
                                f = float(raw); isint = f.is_integer()
                            except (TypeError, ValueError):
                                f, isint = None, False
                            lab = next((k for k, rx in PRODUCER_CATEGORY.items() if rx.match(title)), "")
                            kept = bool(lab) and isint
                            if kept:
                                prod_assign[lab].append((ci, title, int(f)))
                                contributing.add(ci)
                            if isint:
                                cls_sum[ci] = cls_sum.get(ci, 0) + int(f)
                            cats.append(dict(
                                nct_id=nct, payload_shard=name, om_index=oi,
                                om_title=om.get("title") or "", group_id=gid,
                                group_title=groups[gid], class_index=ci, class_title=ctitle,
                                category_index=kk, category_title=title,
                                category_value_raw="" if raw is None else str(raw),
                                category_value_is_integer="yes" if isint else "no",
                                category_value_int="" if not isint else str(int(f)),
                                producer_label_assigned=lab or "NONE",
                                producer_kept="yes" if kept else "no",
                                reported_denominator_participants="" if dparts is None else str(dparts),
                                denominator_units_available="|".join(sorted(denoms)) or "NONE",
                                source_pointer=(f"{name}.txt :: studies[nct={nct}] :: "
                                                f"outcomeMeasures[{oi}] :: classes[{ci}] :: "
                                                f"categories[{kk}] :: groups[{gid}]"),
                            ))
                CATROWS.extend(cats)
                # producer-label collisions (a stored cell that does not identify one source category)
                coll_within = sum(1 for l, v in prod_assign.items()
                                  if len(set(ci for ci, _, _ in v)) == 1 and len(v) > 1)
                coll_cross = sum(1 for l, v in prod_assign.items()
                                 if len(set(ci for ci, _, _ in v)) > 1)
                conflicting = sum(1 for l, v in prod_assign.items() if len(set(x[2] for x in v)) > 1)
                colliding_labels = sorted(l for l, v in prod_assign.items() if len(v) > 1)
                dparts_i = None
                try:
                    dparts_i = int(dparts)
                except (TypeError, ValueError):
                    pass
                contrib_sum = sum(cls_sum.get(ci, 0) for ci in sorted(contributing))
                ints = [c for c in cats if c["category_value_is_integer"] == "yes"]
                dropped = [c for c in cats if c["producer_kept"] == "no"]
                d_resp = [c for c in dropped if RESPONSE_LIKE_DROPPED.match(c["category_title"])]
                d_ne = [c for c in dropped if not RESPONSE_LIKE_DROPPED.match(c["category_title"])
                        and NONEVAL_LIKE.match(c["category_title"])]
                d_oth = [c for c in dropped if not RESPONSE_LIKE_DROPPED.match(c["category_title"])
                         and not NONEVAL_LIKE.match(c["category_title"])]
                def _tv(lst):
                    return "|".join(f"[class {c['class_index']}] {esc(c['category_title'])}="
                                    f"{c['category_value_raw']}" for c in lst)
                ROWS[key] = dict(
                    nct_id=nct, payload_shard=name, om_index=oi, om_title=om.get("title") or "",
                    om_type=om.get("type") or "", param_type=om.get("paramType") or "",
                    unit_of_measure=om.get("unitOfMeasure") or "",
                    time_frame=om.get("timeFrame") or "",
                    population_description=om.get("populationDescription") or "",
                    group_id=gid, group_title=groups[gid], n_classes_in_om=len(classes),
                    contributing_class_indices=";".join(str(c) for c in sorted(contributing)),
                    n_contributing_classes=len(contributing),
                    class_titles_contributing="|".join(
                        (classes[ci].get("title") or "<untitled>") for ci in sorted(contributing)),
                    reported_denominator_participants="" if dparts is None else str(dparts),
                    denominator_units_available="|".join(sorted(denoms)) or "NONE",
                    n_source_categories=len(cats), n_source_categories_integer=len(ints),
                    n_categories_kept_by_producer=sum(1 for c in cats if c["producer_kept"] == "yes"),
                    full_category_vector="|".join(
                        f"[class {c['class_index']}] {esc(c['category_title'])}={c['category_value_raw']}"
                        for c in cats),
                    all_categories_contributing_classes_sum=contrib_sum,
                    producer_label_collision_within_class=coll_within,
                    producer_label_collision_across_classes=coll_cross,
                    producer_label_collision_value_conflicting=conflicting,
                    producer_colliding_labels="|".join(colliding_labels),
                    categories_kept_by_producer_with_values=_tv(
                        [c for c in cats if c["producer_kept"] == "yes"]),
                    categories_dropped_by_producer_with_values=_tv(dropped),
                    dropped_response_like_titles=_tv(d_resp),
                    dropped_noneval_titles=_tv(d_ne),
                    dropped_other_titles=_tv(d_oth),
                    n_distinct_source_category_titles=len(set(c["category_title"] for c in cats)),
                    _dparts_i=dparts_i,
                )

missing = set(J1) - set(ROWS)
assert not missing, sorted(missing)[:5]

# ------------------------------------------------------------------- resolution / suitability state
def state_for(key):
    r, j = ROWS[key], J1[key]
    d = r["_dparts_i"]
    reasons = []
    if d is None:
        reasons.append("DENOMINATOR_NOT_REPORTED_AS_PARTICIPANTS")
    if r["n_contributing_classes"] > 1:
        reasons.append("MULTIPLE_CONTRIBUTING_CLASSES_NO_SOURCE_SUPPORTED_SELECTION_BASIS")
    if d and r["all_categories_contributing_classes_sum"] > d:
        if r["all_categories_contributing_classes_sum"] % d == 0:
            reasons.append("CATEGORY_SUM_IS_A_MULTIPLE_OF_REPORTED_DENOMINATOR_OVERLAPPING_STRATA")
        else:
            reasons.append("CATEGORY_SUM_EXCEEDS_REPORTED_DENOMINATOR")
    if r["producer_label_collision_across_classes"]:
        reasons.append("PRODUCER_LABEL_COLLISION_ACROSS_CLASSES")
    if r["producer_label_collision_within_class"]:
        reasons.append("PRODUCER_LABEL_COLLISION_WITHIN_CLASS")
    adv = []
    if r["n_source_categories"] != r["n_source_categories_integer"]:
        adv.append("NON_INTEGER_CATEGORY_VALUE_PRESENT")
    if d is not None and r["all_categories_contributing_classes_sum"] < d:
        adv.append("REPORTED_CATEGORIES_DO_NOT_ACCOUNT_FOR_FULL_DENOMINATOR")
    if r["dropped_response_like_titles"]:
        adv.append("RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER")
    if r["dropped_noneval_titles"]:
        adv.append("NON_EVALUABLE_CATEGORY_DROPPED_BY_PRODUCER")
    if r["dropped_other_titles"]:
        adv.append("UNCLASSIFIED_CATEGORY_DROPPED_BY_PRODUCER")
    suit = "UNSUITABLE_FOR_PROPORTION" if reasons else "NOT_REFUTED_BY_THIS_COMPONENT"
    return suit, reasons, adv

# ------------------------------------------------------------------------------- leaf cross-check
LEAFSPEC = {
    "LEAF-QA-group0.tsv": ("nct_id", "outcome_measure_index", "group_id"),
    "LEAF-QA-group1.tsv": ("nct_id", "outcome_measure_index", "group_id"),
    "LEAF-QA-group2.tsv": ("nct_id", "outcome_measure_index", "group_id"),
    "LEAF-QA-group3.tsv": ("nct_id", "outcome_measure_index", "group_id"),
}
leaf_cov, leaf_denom_agree, leaf_denom_disagree, leaf_denom_absent = {}, 0, 0, 0
DENOM_FIELDS = ("reported_denominator", "reported_denominator_participants")
for fn, (a, b, c) in LEAFSPEC.items():
    for rec in tsv(os.path.join(LANE, "LEAF-OUT", fn)):
        k = (rec[a], rec[b], rec[c])
        if k not in ROWS:
            continue
        leaf_cov.setdefault(k, set()).add(fn)
        dv = next((rec[f] for f in DENOM_FIELDS if f in rec and rec[f] not in ("", None)), None)
        if dv is None:
            leaf_denom_absent += 1
        elif str(ROWS[k]["_dparts_i"]) == str(dv).strip():
            leaf_denom_agree += 1
        else:
            leaf_denom_disagree += 1

# ------------------------------------------------------------------------------------ emit tables
ROW_COLS = [
 "row_key","input_key_nct_id","input_key_om_index","input_key_group_id",
 "payload_shard","cache_revision","om_title","om_type","param_type","unit_of_measure",
 "time_frame","population_description","group_title","n_classes_in_om",
 "n_contributing_classes","contributing_class_indices","class_titles_contributing",
 "reported_denominator_participants","denominator_provenance","denominator_units_available",
 "n_source_categories","n_source_categories_integer","n_distinct_source_category_titles",
 "n_categories_kept_by_producer","full_category_vector",
 "categories_kept_by_producer_with_values","categories_dropped_by_producer_with_values",
 "dropped_response_bearing_categories_with_values","dropped_non_evaluable_categories_with_values",
 "dropped_unclassified_categories_with_values",
 "all_categories_contributing_classes_sum",
 "job1_evaluable_n_sum_of_four_producer_cells",
 "job1_all_categories_in_contributing_classes_sum",
 "evaluable_n_minus_reported_denominator",
 "all_categories_sum_minus_reported_denominator",
 "job1_column26_original_label","job1_column26_value_carried_unchanged",
 "producer_label_collision_within_class","producer_label_collision_across_classes",
 "producer_label_collision_value_conflicting","producer_colliding_labels",
 "job1_classification_carried","category_vector_source","leaf_qa_coverage",
 "denominator_state","category_preservation_state","proportion_suitability",
 "unresolved_reason_codes","advisory_flag_codes","rate_derived","source_pointer",
]
CAT_COLS = ["nct_id","payload_shard","om_index","om_title","group_id","group_title","class_index",
            "class_title","category_index","category_title","category_value_raw",
            "category_value_is_integer","category_value_int","producer_label_assigned",
            "producer_kept","reported_denominator_participants","denominator_units_available",
            "source_pointer"]

counts = collections.Counter()
with open(os.path.join(HERE, "corrected-a-rows.tsv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(ROW_COLS)
    for key in sorted(ROWS, key=lambda k: (k[0], int(k[1]), k[2])):
        r, j = ROWS[key], J1[key]
        suit, reasons, adv = state_for(key)
        d = r["_dparts_i"]
        counts[suit] += 1
        for x in reasons:
            counts["reason:" + x] += 1
        for x in adv:
            counts["advisory:" + x] += 1
        ev = int(j["evaluable_n_sum_of_cells"])
        allsum = int(j["all_categories_in_contributing_classes_sum"])
        w.writerow([
          f"{key[0]}|OM{key[1]}|{key[2]}", key[0], key[1], key[2],
          r["payload_shard"], CACHE_REV, esc(r["om_title"]), r["om_type"], r["param_type"],
          r["unit_of_measure"], esc(r["time_frame"]), esc(r["population_description"]),
          esc(r["group_title"]), r["n_classes_in_om"],
          r["n_contributing_classes"], r["contributing_class_indices"],
          esc(r["class_titles_contributing"]),
          r["reported_denominator_participants"],
          f"outcomeMeasures[{key[1]}].denoms[units=Participants].counts[groupId={key[2]}].value",
          r["denominator_units_available"],
          r["n_source_categories"], r["n_source_categories_integer"],
          r["n_distinct_source_category_titles"],
          r["n_categories_kept_by_producer"], esc(r["full_category_vector"]),
          esc(r["categories_kept_by_producer_with_values"]),
          esc(r["categories_dropped_by_producer_with_values"]),
          esc(r["dropped_response_like_titles"]), esc(r["dropped_noneval_titles"]),
          esc(r["dropped_other_titles"]),
          r["all_categories_contributing_classes_sum"],
          ev, allsum,
          "" if d is None else ev - d,
          "" if d is None else allsum - d,
          "sum_minus_reported_denominator", j["sum_minus_reported_denominator"],
          r["producer_label_collision_within_class"], r["producer_label_collision_across_classes"],
          r["producer_label_collision_value_conflicting"], r["producer_colliding_labels"],
          j["classification"],
          "CACHE_DIRECT_" + CACHE_REV[:8],
          "|".join(sorted(leaf_cov.get(key, []))) or "NONE",
          "READ_FROM_SOURCE" if d is not None else "ABSENT",
          "FULL_VECTOR" if r["n_source_categories"] else "NONE",
          suit, "|".join(reasons) or "NONE", "|".join(adv) or "NONE", "NOT_DERIVED",
          f"{r['payload_shard']}.txt :: studies[nct={key[0]}] :: outcomeMeasures[{key[1]}] :: groups[{key[2]}]",
        ])

with open(os.path.join(HERE, "corrected-a-categories.tsv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(CAT_COLS)
    for c in CATROWS:
        w.writerow([esc(str(c[k])) for k in CAT_COLS])

inv = collections.defaultdict(lambda: dict(records=0, ncts=set(), labels=set(), kept=0, dropped=0))
for c in CATROWS:
    e = inv[c["category_title"]]
    e["records"] += 1
    e["ncts"].add(c["nct_id"])
    e["labels"].add(c["producer_label_assigned"])
    e["kept" if c["producer_kept"] == "yes" else "dropped"] += 1
with open(os.path.join(HERE, "corrected-a-category-inventory.tsv"), "w", newline="",
          encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["category_title_verbatim", "records", "distinct_nct", "producer_labels_assigned",
                "records_kept_by_producer", "records_dropped_by_producer",
                "response_bearing_title_flag", "non_evaluable_title_flag", "folded", "note"])
    for t, e in sorted(inv.items(), key=lambda kv: (-kv[1]["records"], kv[0])):
        w.writerow([esc(t), e["records"], len(e["ncts"]), "|".join(sorted(e["labels"])),
                    e["kept"], e["dropped"],
                    "yes" if RESPONSE_LIKE_DROPPED.match(t) else "no",
                    "yes" if NONEVAL_LIKE.match(t) else "no", "NO",
                    "preserved verbatim under its own source definition; not mapped to any "
                    "common numerator vocabulary"])

summary = {
 "component": "CORRECTED-A-denominator-category",
 "cache_revision": CACHE_REV,
 "input_rows_job1": len(job1),
 "rows_emitted": len(ROWS),
 "category_records_emitted": len(CATROWS),
 "rows_with_reported_participant_denominator": sum(1 for k in ROWS if ROWS[k]["_dparts_i"] is not None),
 "proportion_suitability": {k: v for k, v in counts.items()
                           if not k.startswith(("reason:", "advisory:"))},
 "unresolved_reason_codes": {k[7:]: v for k, v in counts.items() if k.startswith("reason:")},
 "advisory_flag_codes": {k[9:]: v for k, v in counts.items() if k.startswith("advisory:")},
 "distinct_source_category_titles": len(inv),
 "leaf_qa_rows_covered": len(leaf_cov),
 "leaf_qa_denominator_agreements": leaf_denom_agree,
 "leaf_qa_denominator_disagreements": leaf_denom_disagree,
 "leaf_qa_records_without_a_denominator_field": leaf_denom_absent,
 "rates_derived": 0,
 "job2_job3_independently_confirmed": False,
 "job1_arithmetic_independently_confirmed": True,
}
json.dump(summary, open(os.path.join(HERE, "corrected-a-summary.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(summary, indent=1, sort_keys=True))
