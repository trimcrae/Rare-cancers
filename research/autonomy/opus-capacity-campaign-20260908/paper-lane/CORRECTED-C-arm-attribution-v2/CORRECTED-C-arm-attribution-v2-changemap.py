"""Emit the exact row-level change map v1 -> v2 and its cross-tabulations.
Reads both maps read-only. Writes CHANGE-MAP-v1-to-v2.tsv and prints the cross-tabs."""
import collections, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
V1 = os.path.join(LANE, "CORRECTED-C-arm-attribution", "CORRECTED-C-arm-attribution-map.tsv")
V2 = os.path.join(HERE, "CORRECTED-C-arm-attribution-v2-map.tsv")
OUT = os.path.join(HERE, "CHANGE-MAP-v1-to-v2.tsv")

def rd(p):
    with open(p, encoding="utf-8") as fh:
        return {(r["nct"], r["om_title"], r["group_title"]): r
                for r in csv.DictReader(fh, delimiter="\t")}

a, b = rd(V1), rd(V2)
assert set(a) == set(b), "key sets differ"
cols = ["nct", "om_title", "group_title", "n_arms_registered",
        "v1_arm_link_state", "v1_arm_link_evidence_code", "v1_confirmed_registry_arm_label",
        "v1_control_status",
        "v2_arm_link_state", "v2_arm_link_relation", "v2_bound_arm_label",
        "v2_bound_arm_registered_type_verbatim", "v2_n_candidate_arms",
        "v2_comparator_role", "v2_registry_type_statement",
        "v2_registry_type_statement_assumption", "v2_leaf_claim_state",
        "v2_leaf_claim_verification", "v2_arm_link_source_locator",
        "change_arm_link", "change_comparator_class"]
rows = []
for k in sorted(a):
    x, y = a[k], b[k]
    rows.append({
        "nct": k[0], "om_title": k[1], "group_title": k[2],
        "n_arms_registered": y["n_arms_registered"],
        "v1_arm_link_state": x["arm_link_state"],
        "v1_arm_link_evidence_code": x["arm_link_evidence_code"],
        "v1_confirmed_registry_arm_label": x["confirmed_registry_arm_label"],
        "v1_control_status": x["control_status"],
        "v2_arm_link_state": y["arm_link_state"],
        "v2_arm_link_relation": y["arm_link_relation"],
        "v2_bound_arm_label": y["bound_arm_label"],
        "v2_bound_arm_registered_type_verbatim": y["bound_arm_registered_type_verbatim"],
        "v2_n_candidate_arms": y["n_candidate_arms"],
        "v2_comparator_role": y["comparator_role"],
        "v2_registry_type_statement": y["registry_type_statement"],
        "v2_registry_type_statement_assumption": y["registry_type_statement_assumption"],
        "v2_leaf_claim_state": y["leaf_claim_state"],
        "v2_leaf_claim_verification": y["leaf_claim_verification"],
        "v2_arm_link_source_locator": y["arm_link_source_locator"],
        "change_arm_link": "%s -> %s" % (x["arm_link_state"], y["arm_link_state"]),
        "change_comparator_class": y["disposition_vs_v1"]})
with open(OUT, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols})

def tab(f):
    return dict(sorted(collections.Counter(f(r) for r in rows).items(),
                       key=lambda kv: -kv[1]))
print(json.dumps(dict(
    rows=len(rows),
    arm_link_state_transition=tab(lambda r: r["change_arm_link"]),
    comparator_class_transition=tab(lambda r: r["change_comparator_class"]),
    v1_evidence_code_to_v2_state=tab(lambda r: "%s => %s" % (r["v1_arm_link_evidence_code"],
                                                             r["v2_arm_link_state"])),
    v2_state_by_leaf_claim=tab(lambda r: "%s / %s" % (r["v2_arm_link_state"],
                                                      r["v2_leaf_claim_state"])),
    unresolved_counts=dict(
        total_rows=len(rows),
        source_confirmed=sum(1 for r in rows if r["v2_arm_link_state"] == "SOURCE_CONFIRMED"),
        not_source_confirmed=sum(1 for r in rows if r["v2_arm_link_state"] != "SOURCE_CONFIRMED"),
        label_match_only=sum(1 for r in rows if r["v2_arm_link_state"] == "LABEL_MATCH"),
        proposed_unverified=sum(1 for r in rows if r["v2_arm_link_state"] == "PROPOSED"),
        unresolved=sum(1 for r in rows if r["v2_arm_link_state"] == "UNRESOLVED"),
        contested=sum(1 for r in rows if r["v2_arm_link_state"] == "CONTESTED"),
        unknown_in_this_cache=sum(1 for r in rows
                                  if r["v2_arm_link_state"] == "UNKNOWN_IN_THIS_CACHE"),
        comparator_role_supported=sum(1 for r in rows if r["v2_comparator_role"].startswith(
            "COMPARATOR_SUPPORTED")),
        comparator_role_proposed=sum(1 for r in rows if r["v2_comparator_role"].startswith(
            "COMPARATOR_PROPOSED")),
        comparator_role_contested=sum(1 for r in rows if r["v2_comparator_role"] == "CONTESTED"),
        comparator_role_not_established=sum(1 for r in rows if r["v2_comparator_role"] ==
                                            "NOT_ESTABLISHED_IN_THIS_CACHE"),
        comparator_role_unknown=sum(1 for r in rows if r["v2_comparator_role"] ==
                                    "UNKNOWN_IN_THIS_CACHE"),
        v1_rows_confirmed_by_the_narrative_token_test=sum(
            1 for r in rows if r["v1_arm_link_evidence_code"] == "LEAF_WITHIN_RECORD_RELATION"),
    )), indent=1, sort_keys=True))
sys.exit(0)
