"""CORRECTED-C (arm attribution) -- NEW SIBLING producer. Does NOT overwrite and does NOT re-run
Job 3 (`CURATION-endpoint-arm-attribution-derive.py`). Job 3's map is read ONLY as a prior-state
index for the disposition/change map.

What it changes relative to Job 3:
  1. results-group -> registered-arm links are split into CONFIRMED / CANDIDATE / CONTESTED /
     UNRESOLVED / UNKNOWN_IN_THIS_CACHE as DISTINCT machine values, never collapsed;
  2. label-only substring containment can NEVER populate a confirmed registry_arm_label/type;
  3. punctuation / hyphen / bracket / dosage-unit / spelling differences are NOT normalised into
     clinical equivalence -- only case and whitespace are;
  4. zero registered arms => control status UNKNOWN_IN_THIS_CACHE, never NOT_CONTROL;
  5. a placebo/control claim in the group's own record against an EXPERIMENTAL/OTHER registry type
     is CONTESTED, and a CONTESTED row is never counted as a comparator.
No effect estimate, response rate, unique-patient total or control comparison is computed here.
"""
import collections, csv, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(BASE)
CACHE = "/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5"
JOB3_MAP = os.path.join(LANE, "CURATION-endpoint-arm-attribution-map.tsv")
LEAVES = [(os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group0.tsv"), "join_field", "join_class",
           "recovered_arm_label", "recovered_arm_type"),
          (os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group1.tsv"), "field_used", "verdict",
           "recovered_arm_label", "recovered_armGroupType"),
          (os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group2.tsv"), "join_field", "verdict",
           "recovered_arm_label", "recovered_arm_type"),
          (os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group3.tsv"), "evidence_field", "verdict",
           "recovered_arm_label", "recovered_arm_type")]

BOR = [f"ctg_results_bor_{e}" for e in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]
PLA = [f"ctg_placebo_onc_{e}" for e in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]
FILES = BOR + PLA

# --- Job 3's key logic, reproduced UNCHANGED so the new table is key-compatible with C2_arms ----
CATEGORY = {"CR": re.compile(r"^\s*(complete response|complete remission|CR)\b", re.I),
            "PR": re.compile(r"^\s*(partial response|partial remission|PR)\b", re.I),
            "SD": re.compile(r"^\s*(stable disease|SD)\b", re.I),
            "PD": re.compile(r"^\s*(progressive disease|disease progression|PD)\b", re.I)}

def payload(name):
    with open(os.path.join(CACHE, name + ".txt"), encoding="utf-8") as fh:
        raw = fh.read()
    return json.loads(raw.split("=" * 70, 1)[1])

def cells_for_groups(om):
    per = collections.defaultdict(dict)
    for cl in om.get("classes") or []:
        for cat in cl.get("categories") or []:
            label = next((k for k, rx in CATEGORY.items() if rx.match(cat.get("title") or "")), None)
            if not label:
                continue
            for meas in cat.get("measurements") or []:
                gid, val = meas.get("groupId"), meas.get("value")
                if gid is None or val is None:
                    continue
                try:
                    f = float(val)
                except (TypeError, ValueError):
                    continue
                if f.is_integer():
                    per[gid][label] = int(f)
    return per

# --- NEW: the ONLY label normalisation permitted for a CONFIRMED link ---------------------------
# Case and whitespace only. Punctuation, internal hyphens, brackets, dosage units and spelling are
# NOT normalised: `3.2 mg/kg` and `3.2 kg/mg` are a dose and a unit, not a formatting variant.
def label_fold(s):
    return re.sub(r"\s+", "", (s or "")).casefold()

CONTROL_TYPES = {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR", "NO_INTERVENTION", "ACTIVE_COMPARATOR"}
NONCONTROL_TYPES = {"EXPERIMENTAL", "OTHER"}
PLACEBO_TXT = re.compile(r"\bplacebo|\bsham\b|\bvehicle control\b", re.I)
NOINT_TXT = re.compile(r"\bno intervention\b|\bobservation only\b|\bwatchful waiting\b|\buntreated control\b", re.I)
CONTROL_TXT = re.compile(r"\bcontrol\b|\bcomparator\b", re.I)
CONTROL_DESC = re.compile(r"\bcontrol (arm|group|drug)\b|\brandomi[sz]ed to (the )?(control|placebo)\b", re.I)
PLACEBO_SEQUENCE = re.compile(r"[A-Za-z0-9]\s*/\s*placebo", re.I)

def link_by_label(gtitle, armgroups):
    """Returns (link_state, evidence_code, arm|None, candidates[]).
    CONFIRMED only for byte-exact or case/whitespace-only equality that is unique."""
    if not armgroups:
        return "UNKNOWN_IN_THIS_CACHE", "NO_ARM_GROUPS_REGISTERED_IN_THIS_CACHE", None, []
    exact = [g for g in armgroups if (g.get("label") or "") == gtitle]
    if len(exact) == 1:
        return "CONFIRMED", "LABEL_BYTE_EXACT", exact[0], []
    if len(exact) > 1:
        return "UNRESOLVED", "LABEL_EXACT_AMBIGUOUS_MULTI", None, exact
    gt = label_fold(gtitle)
    if not gt:
        return "UNKNOWN_IN_THIS_CACHE", "EMPTY_RESULTS_GROUP_TITLE", None, []
    fold = [g for g in armgroups if label_fold(g.get("label")) == gt]
    if len(fold) == 1:
        return "CONFIRMED", "LABEL_CASE_AND_WHITESPACE_ONLY", fold[0], []
    if len(fold) > 1:
        return "UNRESOLVED", "LABEL_FOLD_AMBIGUOUS_MULTI", None, fold
    # everything below is PROPOSED ONLY and may never populate a confirmed field
    lower = [(( g.get("label") or "").casefold(), g) for g in armgroups]
    glow = (gtitle or "").casefold()
    cont = [g for k, g in lower if k and (k in glow or glow in k)]
    if cont:
        return ("CANDIDATE", "LABEL_SUBSTRING_CONTAINMENT_ONLY" if len(cont) == 1
                else "LABEL_SUBSTRING_CONTAINMENT_AMBIGUOUS", None, cont)
    return "UNKNOWN_IN_THIS_CACHE", "NO_LABEL_RELATION_IN_THIS_CACHE", None, []

# --- NEW: deterministic grading of the delivered leaf recoveries --------------------------------
CORROBORATION = ("description", "interventionnames", "bijection", "complement", "partition",
                 "enumerat", "verbatim", "reproduced", "drug set", "elimination")
TYPE_ONLY = ("all 7 registered", "armgroups[*].type", "only armgrouptype available",
             "arm_set_type_invariant")
CARDINALITY = ("cardinality", "sole registered arm", "only one registered arm",
               "n_arms_registered=1", "single registered arm")

def grade_leaf(field, verdict):
    f = (field or "").casefold()
    v = (verdict or "").upper()
    if v == "GENUINELY_UNJOINABLE":
        return ("UNKNOWN_IN_THIS_CACHE", "LEAF_NO_ARM_GROUPS_IN_THIS_CACHE"
                if ("empty" in f or "0 arms" in f or "none" in f) else "LEAF_UNJOINABLE_IN_THIS_CACHE")
    if v == "UNRESOLVED":
        return ("UNRESOLVED", "LEAF_ARMS_MUTUALLY_INDISTINGUISHABLE")
    if v != "JOIN_RECOVERABLE":
        return ("UNRESOLVED", "LEAF_VERDICT_NOT_RECOGNISED")
    corr = any(t in f for t in CORROBORATION)
    if any(t in f for t in TYPE_ONLY) and not corr:
        return ("CONFIRMED_TYPE_ONLY", "LEAF_ARM_SET_TYPE_INVARIANT")
    if corr:
        return ("CONFIRMED", "LEAF_WITHIN_RECORD_RELATION")
    if any(t in f for t in CARDINALITY):
        return ("CONFIRMED_TYPE_ONLY", "LEAF_SOLE_REGISTERED_ARM_TYPE_ONLY")
    return ("CANDIDATE", "LEAF_LABEL_STRING_ONLY_NOT_CONFIRMED")

def load_leaves():
    ov = {}
    for path, ffield, vfield, lab, typ in LEAVES:
        src = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                k = (r["nct"], r["om_title"], r["group_title"])
                state, code = grade_leaf(r.get(ffield), r.get(vfield))
                rec = dict(leaf_source=src, leaf_verdict=r.get(vfield, ""),
                           leaf_field=(r.get(ffield) or "").replace("\n", " ")[:400],
                           leaf_arm_label=r.get(lab, "") or "", leaf_arm_type=r.get(typ, "") or "",
                           leaf_state=state, leaf_code=code)
                if k in ov and ov[k]["leaf_source"] != src:
                    ov[k]["leaf_duplicate_in"] = src   # corpus-wide AMBIGUOUS_MULTI triage overlap
                else:
                    ov[k] = rec
    return ov

def semantic(v):
    """Collapse EITHER vocabulary to one of four comparable classes, for the change map only.
    The four classes are never written back onto a row: the row keeps its full machine value."""
    if not v:
        return "NONE"
    if v == "CONTESTED":
        return "CONTESTED"
    if v.startswith("NOT_CONTROL"):
        return "NOT_CONTROL"
    if "CANDIDATE" in v or "BY_GROUP_TEXT" in v:
        return "CONTROL_PROPOSED"
    if v.startswith("CONTROL_"):
        return "CONTROL_SUPPORTED"
    return "UNKNOWN"


def main(out_tsv, out_checks):
    leaf = load_leaves()
    job3 = {}
    with open(JOB3_MAP, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            job3[(r["nct"], r["om_title"], r["group_title"])] = r

    rows, seen = [], set()
    for name in FILES:
        era = name.rsplit("_", 2)[-2] + "_" + name.rsplit("_", 1)[-1]
        family = "bor" if name in BOR else "placebo"
        for s in payload(name).get("studies") or []:
            ps, rs = s.get("protocolSection") or {}, s.get("resultsSection") or {}
            nct = (ps.get("identificationModule") or {}).get("nctId")
            ai = (ps.get("armsInterventionsModule") or {}).get("armGroups") or []
            n_arms = len(ai)
            types = [(g.get("type") or "") for g in ai]
            typed = [t for t in types if t]
            arm_set_type_state = (
                "NO_ARMS_REGISTERED_IN_THIS_CACHE" if n_arms == 0 else
                "ARM_TYPE_ABSENT_IN_THIS_CACHE" if not typed else
                "PARTIALLY_TYPED_IN_THIS_CACHE" if len(typed) != n_arms else
                "ALL_ARMS_NON_CONTROL_TYPED" if set(typed) <= NONCONTROL_TYPES else
                "ALL_ARMS_CONTROL_TYPED" if set(typed) <= CONTROL_TYPES else "MIXED_ARM_TYPES")
            for om in (rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []:
                gmeta = {g.get("id"): g for g in om.get("groups") or []}
                n_results_groups = len(gmeta)
                for gid, cells in cells_for_groups(om).items():
                    if len(cells) < 4:
                        continue
                    n = sum(cells.values())
                    if n <= 0:
                        continue
                    g = gmeta.get(gid) or {}
                    gtitle = g.get("title") or ""
                    omtitle = om.get("title") or ""
                    key = (nct, omtitle, gtitle, n)
                    if key in seen:
                        continue
                    seen.add(key)
                    gdesc = (g.get("description") or "")
                    k3 = (nct, omtitle, gtitle)

                    state, code, arm, cands = link_by_label(gtitle, ai)
                    leaf_unbound_label = ""
                    lf = leaf.get(k3)
                    link_source = "LABEL_IN_THIS_PRODUCER"
                    if state in ("CANDIDATE", "UNKNOWN_IN_THIS_CACHE", "UNRESOLVED") and lf:
                        # delivered leaf evidence may only strengthen a non-confirmed label link
                        state, code = lf["leaf_state"], lf["leaf_code"]
                        link_source = "DELIVERED_LEAF:" + lf["leaf_source"]
                        arm = next((a for a in ai if (a.get("label") or "") == lf["leaf_arm_label"]), arm)
                        if lf["leaf_arm_label"] and arm is None:
                            arm = next((a for a in ai
                                        if label_fold(a.get("label")) == label_fold(lf["leaf_arm_label"])), None)
                        if state == "CANDIDATE" and lf["leaf_arm_label"]:
                            cands = [a for a in ai if (a.get("label") or "") == lf["leaf_arm_label"]] or cands
                        if state == "CONFIRMED" and arm is None:
                            # the leaf established a relation but not a single registered arm
                            if arm_set_type_state == "ALL_ARMS_NON_CONTROL_TYPED":
                                state, code = "CONFIRMED_TYPE_ONLY", "LEAF_ARM_IDENTITY_NOT_BOUND_ARM_SET_TYPE_INVARIANT"
                            else:
                                state, code = "CANDIDATE", "LEAF_ARM_IDENTITY_NOT_BOUND_TO_A_SINGLE_ARM"
                                cands = []
                            leaf_unbound_label = lf["leaf_arm_label"]

                    conf_label = (arm.get("label") or "") if (arm and state == "CONFIRMED") else ""
                    conf_type = ((arm.get("type") or "ARM_TYPE_ABSENT_IN_THIS_CACHE")
                                 if (arm and state == "CONFIRMED") else "")
                    cand_labels = (" | ".join((c.get("label") or "") for c in cands) or leaf_unbound_label) \
                        if state == "CANDIDATE" else (
                        (arm.get("label") or "") if (arm and state == "CONFIRMED_TYPE_ONLY") else "")
                    cand_types = " | ".join((c.get("type") or "ARM_TYPE_ABSENT_IN_THIS_CACHE") for c in cands) \
                        if state == "CANDIDATE" else ""

                    # ---- control status, on the corrected link only ----
                    seq = bool(PLACEBO_SEQUENCE.search(gtitle))
                    txt_placebo = bool(PLACEBO_TXT.search(gtitle) or PLACEBO_TXT.search(gdesc)) and not seq
                    txt_noint = bool(NOINT_TXT.search(gtitle))
                    txt_ctl = bool(CONTROL_TXT.search(gtitle) or CONTROL_DESC.search(gdesc))
                    contested = ""
                    if state == "CONFIRMED" and conf_type in NONCONTROL_TYPES and (txt_placebo or txt_noint):
                        cs = "CONTESTED"
                        cb = (f"group record states placebo/no-intervention but the CONFIRMED registry arm "
                              f"'{conf_label}' is typed {conf_type}; neither field wins")
                        contested = "PLACEBO_OR_NOINT_TEXT_VS_NONCONTROL_REGISTRY_TYPE"
                    elif state == "CONFIRMED" and conf_type in {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR"}:
                        cs, cb = "CONTROL_PLACEBO_CONFIRMED", f"confirmed arm '{conf_label}' type={conf_type}"
                    elif state == "CONFIRMED" and conf_type == "NO_INTERVENTION":
                        cs, cb = "CONTROL_NO_INTERVENTION_CONFIRMED", f"confirmed arm '{conf_label}' type={conf_type}"
                    elif state == "CONFIRMED" and conf_type == "ACTIVE_COMPARATOR":
                        cs, cb = "CONTROL_ACTIVE_COMPARATOR_CONFIRMED", f"confirmed arm '{conf_label}' type={conf_type}"
                    elif state == "CONFIRMED" and conf_type in NONCONTROL_TYPES:
                        cs, cb = "NOT_CONTROL_CONFIRMED", f"confirmed arm '{conf_label}' type={conf_type}"
                    elif state == "CONFIRMED":
                        cs, cb = "UNKNOWN_IN_THIS_CACHE", "confirmed arm carries no type field in this cache"
                    elif state == "CONFIRMED_TYPE_ONLY" and arm_set_type_state == "ALL_ARMS_NON_CONTROL_TYPED":
                        cs, cb = ("NOT_CONTROL_BY_ARM_SET_TYPE_INVARIANT",
                                  f"arm identity not resolved; all {n_arms} registered arm(s) typed "
                                  f"{sorted(set(typed))} in this cache")
                    elif txt_placebo:
                        cs, cb = "CONTROL_PLACEBO_CANDIDATE_GROUP_TEXT_ONLY", \
                                 "group record states placebo/sham; no confirmed registry link"
                    elif txt_noint:
                        cs, cb = "CONTROL_NO_INTERVENTION_CANDIDATE_GROUP_TEXT_ONLY", \
                                 "group record states no-intervention/observation; no confirmed registry link"
                    elif txt_ctl:
                        cs, cb = "CONTROL_UNSPECIFIED_CANDIDATE_GROUP_TEXT_ONLY", \
                                 "group record says control/comparator without naming placebo; no confirmed registry link"
                    elif seq:
                        cs, cb = "UNKNOWN_IN_THIS_CACHE", \
                                 "group title names a treatment SEQUENCE ending in placebo; not evidence of a placebo arm"
                    elif n_arms == 0:
                        cs, cb = "UNKNOWN_IN_THIS_CACHE", \
                                 "zero registered arm groups in this cache: control status is UNKNOWN, not NOT_CONTROL"
                    elif state == "UNRESOLVED":
                        cs, cb = "UNKNOWN_IN_THIS_CACHE", "arm link unresolved in this cache"
                    else:
                        cs, cb = "UNKNOWN_IN_THIS_CACHE", "no confirmed arm link and no control language in the group record"
                    if seq:
                        contested = (contested + ";" if contested else "") + \
                                    "GROUP_TITLE_IS_A_TREATMENT_SEQUENCE_CONTAINING_A_PLACEBO_TOKEN"
                    if cs.startswith("CONTROL_PLACEBO") and not any(
                            t in {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR"} for t in types):
                        contested = (contested + ";" if contested else "") + \
                                    "PLACEBO_CLAIM_WITHOUT_PLACEBO_TYPED_ARM_IN_THIS_CACHE"

                    prior = job3.get(k3) or {}
                    p_cs = prior.get("control_status", "")
                    disp = ("NO_PRIOR_ROW" if not prior else
                            "UNCHANGED_CLASS" if semantic(p_cs) == semantic(cs) else
                            "CHANGED_CLASS:%s->%s" % (semantic(p_cs), semantic(cs)))
                    rows.append(dict(
                        nct=nct, om_title=omtitle, group_title=gtitle, evaluable_n=n, era=era, family=family,
                        n_arms_registered=n_arms, n_results_groups_in_om=n_results_groups,
                        arm_set_type_state=arm_set_type_state,
                        registry_arm_types_in_record=" | ".join(types),
                        arm_link_state=state, arm_link_evidence_code=code, arm_link_source=link_source,
                        confirmed_registry_arm_label=conf_label, confirmed_registry_arm_type=conf_type,
                        candidate_registry_arm_labels=cand_labels, candidate_registry_arm_types=cand_types,
                        candidate_evidence=(lf["leaf_field"] if lf and link_source.startswith("DELIVERED_LEAF") else ""),
                        control_status=cs, control_basis=cb, contested_flag=contested,
                        sole_arm_multi_results_group_flag=("YES" if n_arms == 1 and n_results_groups > 1 else "NO"),
                        job3_arm_match_quality=prior.get("arm_match_quality", ""),
                        job3_registry_arm_label=prior.get("registry_arm_label", ""),
                        job3_registry_arm_type=prior.get("registry_arm_type", ""),
                        job3_control_status=p_cs, disposition_vs_job3=disp,
                        group_description=gdesc.replace("\n", " ")[:400]))

    cols = list(rows[0].keys())
    with open(out_tsv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n",
                           quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: str(v).replace("\t", " ").replace("\n", " ") for k, v in r.items()})

    chk, fail = [], 0
    def check(name, ok, detail):
        nonlocal fail
        chk.append(dict(check=name, result="PASS" if ok else "FAIL", detail=detail))
        if not ok:
            fail += 1
    check("row_count_equals_552", len(rows) == 552, f"rows={len(rows)}")
    j3keys = set(job3)
    newkeys = {(r["nct"], r["om_title"], r["group_title"]) for r in rows}
    check("key_set_identical_to_job3", newkeys == j3keys,
          f"only_new={len(newkeys-j3keys)} only_job3={len(j3keys-newkeys)}")
    check("no_row_missing_a_prior_row", all(r["disposition_vs_job3"] != "NO_PRIOR_ROW" for r in rows),
          f"missing={sum(1 for r in rows if r['disposition_vs_job3']=='NO_PRIOR_ROW')}")
    bad = [r for r in rows if r["arm_link_state"] != "CONFIRMED"
           and (r["confirmed_registry_arm_label"] or r["confirmed_registry_arm_type"])]
    check("confirmed_fields_only_when_CONFIRMED", not bad, f"violations={len(bad)}")
    bad = [r for r in rows if r["arm_link_evidence_code"].startswith("LABEL_SUBSTRING")
           and r["arm_link_state"] == "CONFIRMED"]
    check("substring_containment_never_confirmed", not bad, f"violations={len(bad)}")
    bad = [r for r in rows if r["n_arms_registered"] == 0 and r["control_status"] != "UNKNOWN_IN_THIS_CACHE"]
    check("zero_arms_never_not_control", not bad, f"violations={len(bad)}")
    bad = [r for r in rows if r["contested_flag"].startswith("PLACEBO_OR_NOINT")
           and r["control_status"] != "CONTESTED"]
    check("contested_never_resolved_to_a_side", not bad, f"violations={len(bad)}")
    bad = [r for r in rows if r["control_status"].startswith("CONTROL_") and "CANDIDATE" in r["control_status"]
           and r["confirmed_registry_arm_type"]]
    check("candidate_control_carries_no_confirmed_type", not bad, f"violations={len(bad)}")
    bad = [r for r in rows if r["arm_link_state"] == "CONFIRMED" and not r["confirmed_registry_arm_label"]]
    check("CONFIRMED_always_binds_one_registered_arm", not bad, f"violations={len(bad)}")
    bad = [r for r in rows if semantic(r["job3_control_status"]) == "UNKNOWN"
           and semantic(r["control_status"]) == "NOT_CONTROL" and not r["confirmed_registry_arm_type"]
           and r["arm_set_type_state"] != "ALL_ARMS_NON_CONTROL_TYPED"]
    check("unknown_to_not_control_only_on_record_evidence", not bad, f"violations={len(bad)}")
    states = collections.Counter(r["arm_link_state"] for r in rows)
    check("all_five_machine_states_distinct",
          set(states) <= {"CONFIRMED", "CONFIRMED_TYPE_ONLY", "CANDIDATE", "CONTESTED",
                          "UNRESOLVED", "UNKNOWN_IN_THIS_CACHE"},
          json.dumps(states, sort_keys=True))
    absent = collections.Counter()
    for name in FILES:
        with open(os.path.join(CACHE, name + ".txt"), encoding="utf-8") as fh:
            blob = fh.read()
        absent["participantFlowModule"] += blob.count("participantFlowModule")
        absent["armGroupLabels"] += blob.count("armGroupLabels")
    check("absent_modules_stay_absent_in_this_cache",
          absent["participantFlowModule"] == 0 and absent["armGroupLabels"] == 0,
          f"occurrences across the 12 payloads: {dict(absent)} (0 expected; they were never fetched)")
    code_src = open(__file__, encoding="utf-8").read()
    check("producer_makes_no_network_call",
          not re.search(r"^\s*(import|from)\s+(urllib|requests|httpx|http|socket|subprocess|ssl)\b",
                        code_src, re.M),
          "no network, http or subprocess module is imported by this producer; "
          "imports are: " + ", ".join(sorted(set(re.findall(r"^import ([a-z, ]+)$", code_src, re.M)[0].split(", ")))))
    summary = dict(rows=len(rows),
                   arm_link_state=dict(states),
                   control_status=dict(collections.Counter(r["control_status"] for r in rows)),
                   disposition_vs_job3=dict(collections.Counter(r["disposition_vs_job3"] for r in rows)),
                   arm_set_type_state=dict(collections.Counter(r["arm_set_type_state"] for r in rows)),
                   sole_arm_multi_results_group=sum(1 for r in rows if r["sole_arm_multi_results_group_flag"] == "YES"),
                   contested_rows=sum(1 for r in rows if r["control_status"] == "CONTESTED"),
                   checks=chk, checks_failed=fail)
    with open(out_checks, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
