"""Exact field map and row map between CORRECTED-C v2 and the v3 C2 correction.

Both maps are read READ-ONLY. Nothing is written back to v2. The point of this script is to show,
per column and per row, exactly what the five corrections changed -- and to separate a change of
WORDING (a machine token renamed so it states the strength of the evidence it actually has) from a
change of SUBSTANCE (a different value for the same row). No row is re-adjudicated here.

Writes FIELD-MAP-v2-to-v3.tsv and ROW-DELTA-v2-to-v3.tsv; prints the cross-tabulations.
"""
import collections, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
V2 = os.path.join(LANE, "CORRECTED-C-arm-attribution-v2", "CORRECTED-C-arm-attribution-v2-map.tsv")
V3 = os.path.join(HERE, "CORRECTED-C-arm-attribution-v3-map.tsv")

# column renames (v2 name -> v3 name), root item 4
COLUMN_RENAMES = {
    "leaf_narrative_verbatim_not_parsed": "leaf_narrative_transformed_excerpt_not_parsed",
    "group_description": "group_description_transformed_excerpt"}
# value-token renames (v2 token -> v3 token), root items 3 and 5. Longest first.
VALUE_RENAMES = [
    ("COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE",
     "COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH"),
    ("COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE",
     "COMPARATOR_PROPOSED_BY_LABEL_FIELD_MATCHED_ARM_TYPE"),
    ("LABEL_AND_DESCRIPTION_SOURCE_IDENTITIES_NAME_DIFFERENT_ARMS",
     "LABEL_AND_DESCRIPTION_FIELD_MATCHES_NAME_DIFFERENT_ARMS"),
    ("LABEL_IDENTITY_AND_DESCRIPTION_IDENTITY_DISAGREE",
     "LABEL_FIELD_MATCH_AND_DESCRIPTION_FIELD_MATCH_DISAGREE"),
    ("ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY",
     "ASSUMES_LABEL_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED"),
    ("TWO_INDEPENDENT_FIELD_IDENTITIES", "TWO_AGREEING_FIELD_MATCHES"),
    ("DESCRIPTION_FIELD_IDENTITY", "DESCRIPTION_FIELD_MATCH_ONLY"),
    ("LABEL_IDENTITY_ONLY", "LABEL_FIELD_MATCH_ONLY"),
    ("CONTRARY_DESCRIPTION:", "CONTRARY_DESCRIPTION_BINDING_CLEARED:"),
    ("NO_ARMS_REGISTERED_IN_THIS_CACHE", "UNKNOWN_NO_ARMS_REGISTERED_IN_THIS_CACHE"),
    ("COMPARATOR_SUPPORTED", "COMPARATOR_TYPE_INFERRED"),
    ("SOURCE_CONFIRMED", "SOURCE_FIELD_MATCH"),
    ("source-confirmed", "source-field-matched"),
]
# columns whose prose basis is expected to be rewritten by the corrections, and which are therefore
# compared only for their leading state token
PROSE = {"comparator_role_basis", "arm_link_source_locator"}


def rd(p):
    with open(p, encoding="utf-8") as fh:
        r = csv.DictReader(fh, delimiter="\t")
        return r.fieldnames, {(x["nct"], x["om_title"], x["group_title"]): x for x in r}


def retoken(v):
    for a, b in VALUE_RENAMES:
        v = v.replace(a, b)
    return v


f2, a = rd(V2)
f3, b = rd(V3)
assert set(a) == set(b), "key sets differ: v2=%d v3=%d" % (len(a), len(b))

# ---------------------------------- field map ----------------------------------
fm = []
for col in f2:
    new = COLUMN_RENAMES.get(col, col)
    fm.append(dict(v2_column=col, v3_column=(new if new in f3 else "<REMOVED>"),
                   status=("RENAMED" if col != new else
                           "REMOVED" if new not in f3 else "CARRIED")))
for col in f3:
    if col not in f2 and col not in COLUMN_RENAMES.values():
        fm.append(dict(v2_column="<NEW IN v3>", v3_column=col, status="ADDED"))
with open(os.path.join(HERE, "FIELD-MAP-v2-to-v3.tsv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["v2_column", "v3_column", "status"], delimiter="\t",
                       lineterminator="\n")
    w.writeheader()
    for r in fm:
        w.writerow(r)

# ---------------------------------- row map ----------------------------------
compared = [c for c in f2 if COLUMN_RENAMES.get(c, c) in f3 and c not in PROSE]
rows, percol = [], collections.Counter()
for k in sorted(a):
    x, y = a[k], b[k]
    vocab, subst = [], []
    for c in compared:
        c3 = COLUMN_RENAMES.get(c, c)
        if x[c] == y[c3]:
            continue
        (vocab if retoken(x[c]) == y[c3] else subst).append(c)
        percol[("VOCABULARY" if retoken(x[c]) == y[c3] else "SUBSTANTIVE") + " " + c] += 1
    rows.append(dict(
        nct=k[0], om_title=k[1], group_title=k[2],
        v2_arm_link_state=x["arm_link_state"], v3_arm_link_state=y["arm_link_state"],
        v2_comparator_role=x["comparator_role"], v3_comparator_role=y["comparator_role"],
        v2_registry_type_statement=x["registry_type_statement"],
        v3_registry_type_statement=y["registry_type_statement"],
        v2_registry_type_statement_assumption=x["registry_type_statement_assumption"],
        v3_registry_type_statement_assumption=y["registry_type_statement_assumption"],
        v3_comparator_role_identity_assumption=y["comparator_role_identity_assumption"],
        v3_group_text_comparator_wording_unverified=y[
            "group_text_comparator_wording_unverified"],
        v3_source_join_verification=y["source_join_verification"],
        v2_bound_arm_index=x["bound_arm_index"], v3_bound_arm_index=y["bound_arm_index"],
        v3_downgraded_candidate_arm_index=y["downgraded_candidate_arm_index"],
        vocabulary_only_changed_columns=";".join(vocab),
        substantively_changed_columns=";".join(subst),
        row_disposition=("IDENTICAL" if not vocab and not subst else
                         "VOCABULARY_ONLY" if not subst else "SUBSTANTIVE")))
cols = list(rows[0].keys())
with open(os.path.join(HERE, "ROW-DELTA-v2-to-v3.tsv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols})

state_changed = [r for r in rows if r["v2_arm_link_state"] != retoken(r["v2_arm_link_state"])
                 and False] + [r for r in rows
                               if retoken(r["v2_arm_link_state"]) != r["v3_arm_link_state"]]
print(json.dumps(dict(
    rows=len(rows),
    v2_columns=len(f2), v3_columns=len(f3),
    columns_renamed=sum(1 for r in fm if r["status"] == "RENAMED"),
    columns_added=sum(1 for r in fm if r["status"] == "ADDED"),
    columns_removed=sum(1 for r in fm if r["status"] == "REMOVED"),
    row_disposition=dict(collections.Counter(r["row_disposition"] for r in rows)),
    changed_cells_by_column_and_kind=dict(sorted(percol.items())),
    rows_whose_arm_link_state_changed_after_renaming=len(state_changed),
    rows_whose_comparator_role_changed_after_renaming=sum(
        1 for r in rows if retoken(r["v2_comparator_role"]) != r["v3_comparator_role"]),
    rows_whose_bound_arm_index_changed=sum(
        1 for r in rows if r["v2_bound_arm_index"] != r["v3_bound_arm_index"]),
    prose_columns_not_diffed=sorted(PROSE)), indent=1, sort_keys=True))
sys.exit(0)
