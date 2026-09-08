"""Verify the item-5 residual correction changed EXACTLY the intended assumption field.

Compares the retained BEFORE map against the re-derived map, key by key, cell by cell.
Exit 1 on any disagreement. Nothing is reformatted and no threshold is relaxed.
"""
import csv, collections, sys, os, json
csv.field_size_limit(10 ** 9)
H = os.path.dirname(os.path.abspath(__file__))
C = os.path.dirname(H)
KEY = ("nct", "om_title", "group_title", "evaluable_n")
fail = []
def ck(n, ok, d):
    print(("PASS  " if ok else "FAIL  ") + n + "  " + d)
    if not ok: fail.append(n)

def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))

B = rd(os.path.join(H, "BEFORE", "CORRECTED-C-arm-attribution-v3-map.tsv"))
A = rd(os.path.join(C, "CORRECTED-C-arm-attribution-v3-map.tsv"))
ck("V1_row_count_unchanged_552", len(B) == len(A) == 552, "before=%d after=%d" % (len(B), len(A)))
ck("V2_columns_unchanged", list(B[0]) == list(A[0]), "%d columns, identical order" % len(A[0]))
bk = {tuple(r[k] for k in KEY): r for r in B}
ak = {tuple(r[k] for k in KEY): r for r in A}
ck("V3_all_552_keys_identical", set(bk) == set(ak) and len(ak) == 552,
   "added=%d removed=%d" % (len(set(ak) - set(bk)), len(set(bk) - set(ak))))

FIELD = "registry_type_statement_assumption"
diff = collections.Counter()
rows_changed = []
for k in ak:
    if k not in bk: continue
    d = [c for c in A[0] if bk[k][c] != ak[k][c]]
    if d:
        rows_changed.append((k, d))
        for c in d: diff[c] += 1
ck("V4_only_the_assumption_field_changed_and_on_exactly_one_row",
   dict(diff) == {FIELD: 1} and len(rows_changed) == 1,
   "changed cells by column=%s; rows changed=%d" % (dict(diff), len(rows_changed)))

if len(rows_changed) == 1:
    k, _ = rows_changed[0]
    ck("V5_the_changed_row_is_the_description_only_NCT02994953_row",
       k[0] == "NCT02994953" and
       ak[k]["arm_link_relation"] == "DESCRIPTION_FIELD_MATCH_ONLY:DESC_BYTE_EXACT" and
       ak[k]["bound_arm_index"] == "5",
       "nct=%s relation=%s bound_arm_index=%s\n        before=%s\n        after =%s"
       % (k[0], ak[k]["arm_link_relation"], ak[k]["bound_arm_index"],
          bk[k][FIELD], ak[k][FIELD]))
    ck("V6_comparator_role_of_that_row_unchanged_NOT_ESTABLISHED",
       ak[k]["comparator_role"] == bk[k]["comparator_role"] ==
       "NOT_ESTABLISHED_IN_THIS_CACHE",
       "comparator_role=%s (unchanged)" % ak[k]["comparator_role"])

# the partition root named: 57 two-agreeing + 1 description-only + 132 label-only
rel = collections.Counter()
for r in A:
    if r[FIELD]:
        rel[r[FIELD]] += 1
ck("V7_assumption_partition_is_57_two_agreeing_1_description_only_132_label_only",
   rel.get("ASSUMES_TWO_AGREEING_SOURCE_FIELD_MATCHES_ARE_ARM_IDENTITY_UNPROVED") == 57 and
   rel.get("ASSUMES_DESCRIPTION_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED") == 1 and
   rel.get("ASSUMES_LABEL_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED") == 132,
   json.dumps({k: v for k, v in sorted(rel.items()) if "ARM_IDENTITY" in k}, indent=0).replace("\n", " "))
ck("V8_the_catch_all_relation_form_token_is_unused",
   not any(r[FIELD].endswith("RELATION_FORM_UNCLASSIFIED") for r in A),
   "rows carrying the unclassified-relation catch-all = %d (expected 0)"
   % sum(1 for r in A if r[FIELD].endswith("RELATION_FORM_UNCLASSIFIED")))

for col, want in (("arm_link_state", 58), ("comparator_role", 8)):
    pass
sb = collections.Counter(r["arm_link_state"] for r in B)
sa = collections.Counter(r["arm_link_state"] for r in A)
ck("V9_every_arm_link_state_count_unchanged", sb == sa, json.dumps(dict(sa), sort_keys=True))
rb = collections.Counter(r["comparator_role"] for r in B)
ra = collections.Counter(r["comparator_role"] for r in A)
ck("V10_every_comparator_role_count_unchanged_including_the_8_inferred", rb == ra,
   "COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH=%d (unchanged)"
   % ra["COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH"])
bi = collections.Counter(r["bound_arm_index"] for r in B)
ai = collections.Counter(r["bound_arm_index"] for r in A)
ck("V11_every_binding_unchanged", bi == ai and all(bk[k]["bound_arm_index"] == ak[k]["bound_arm_index"] for k in ak),
   "bound_arm_index identical on all 552 rows")
NUM = ("evaluable_n", "n_arms_registered", "n_results_groups_in_om", "n_candidate_arms")
ck("V12_every_numeric_field_unchanged",
   all(bk[k][c] == ak[k][c] for k in ak for c in NUM),
   "fields checked: %s" % ", ".join(NUM))
fb = collections.Counter(t for r in B for t in r["contested_flags"].split("|") if t)
fa = collections.Counter(t for r in A for t in r["contested_flags"].split("|") if t)
sab = collections.Counter(r["sole_arm_multi_results_group_flag"] for r in B)
saa = collections.Counter(r["sole_arm_multi_results_group_flag"] for r in A)
ck("V13_every_flag_unchanged", fb == fa and sab == saa,
   "contested tokens=%d, sole_arm YES=%d" % (sum(fa.values()), saa["YES"]))
print("\nfailed=%d" % len(fail))
sys.exit(1 if fail else 0)
