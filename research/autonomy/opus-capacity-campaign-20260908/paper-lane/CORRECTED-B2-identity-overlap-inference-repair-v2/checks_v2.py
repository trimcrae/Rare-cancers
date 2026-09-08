#!/usr/bin/env python3
"""Checks for CORRECTED-B2. A check that cannot run is a FAIL. Exit 1 on any failure."""
import csv, hashlib, json, os, re, subprocess, sys

csv.field_size_limit(10 * 1024 * 1024)
BASE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.normpath(os.path.join(BASE, "..", "CORRECTED-B-identity-selection-overlap"))
V1A = os.path.join(V1, "artifacts")
OUT = os.path.join(BASE, "artifacts")
EV = os.path.join(BASE, "evidence")

results = []
def check(name, ok, detail):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)

def rd(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

rel1 = rd(os.path.join(V1A, "RELATED-SETS-unresolved.tsv"))
rel2 = rd(os.path.join(OUT, "RELATED-SETS-encoding-vs-semantics-v2.tsv"))
grp1 = rd(os.path.join(V1A, "GROUP-RELATIONS-pooled-parent-component.tsv"))
grp2 = rd(os.path.join(OUT, "GROUP-RELATIONS-candidate-parent-component-v2.tsv"))
enr = rd(os.path.join(V1A, "ENROLLMENT-CONFLICT.tsv"))
exc = rd(os.path.join(OUT, "ENROLLMENT-EXCESS-CATEGORIES-v2.tsv"))

# V1 --------------------------------------------------- v1 component bytes are untouched
base = os.path.join(EV, "ORIGINAL-v1-BASELINE-sha256.txt")
want = {}
for line in open(base, encoding="utf-8"):
    if "  ./" in line:
        h, p = line.rstrip("\n").split("  ", 1)
        want[p] = h
bad = []
for p, h in want.items():
    full = os.path.join(V1, p[2:])
    if not os.path.exists(full) or sha(full) != h:
        bad.append(p)
check("V1_original_v1_component_bytes_unchanged", not bad and len(want) == 19,
      f"{len(want)} baseline files re-hashed, {len(bad)} changed ({bad}); this repair writes only "
      f"into its own v2 directory")

# V2 ------------------------------ the v1 duplicate rule is transcribed, not paraphrased
mismatch = 0
for r in rel1:
    n = int(r["n_observations"])
    same_all = all(int(r[c]) == 1 for c in ("distinct_titles", "distinct_time_frames",
                                            "distinct_constructs", "distinct_criteria",
                                            "distinct_criteria_versions",
                                            "distinct_population_descriptions",
                                            "distinct_param_types", "distinct_units"))
    dens_one = len(set(r["distinct_denominator_values"].split("|"))) == 1
    dup = n > 1 and same_all and dens_one
    if str(dup) != r["duplicate_encoding_candidate"]:
        mismatch += 1
check("V2_v1_duplicate_rule_reproduced_from_v1_columns", mismatch == 0,
      f"{len(rel1)} v1 rows recomputed, {mismatch} disagreements with the emitted "
      f"duplicate_encoding_candidate column; the v1 rule under test is v1's own rule")

# V3 ------------------------------------------- the relabel is 1:1: nothing merged or lost
k1 = [r["cohort_key"] for r in rel1]
k2 = [r["cohort_key"] for r in rel2]
n_ok = all(a["n_observations"] == b["n_observations"] for a, b in zip(rel1, rel2))
obs_ok = all(a["observation_ids"] == b["observation_ids"] for a, b in zip(rel1, rel2))
check("V3_related_sets_relabelled_one_to_one_no_merge_no_drop",
      k1 == k2 and n_ok and obs_ok and len(k1) == 8740,
      f"{len(k1)} v1 cohort keys, {len(k2)} v2 rows, identical order={k1==k2}, "
      f"n_observations preserved={n_ok}, observation_ids preserved verbatim={obs_ok}")

# V4 ------------------------------------- no v2 row claims a distinct measurement/population
multi = [r for r in rel2 if int(r["n_observations"]) > 1]
resolved = [r for r in multi if not r["semantic_duplication_status"].startswith("UNRESOLVED")]
claims = [r for r in rel2 if re.search(r"\bdistinct (outcome|population|measurement)\b",
                                       r["semantic_correspondence_evidence"], re.I)
          and "not" not in r["semantic_correspondence_evidence"].lower()]
check("V4_no_v2_row_asserts_a_distinct_measurement_or_population",
      not resolved and not claims,
      f"{len(multi)} competing sets, {len(resolved)} carrying a resolved semantic status, "
      f"{len(claims)} asserting distinctness")

# V5 ---------------------------------- the encoding label is exactly what the fields support
enc = {}
for r in rel2:
    enc[r["encoding_identity_status"]] = enc.get(r["encoding_identity_status"], 0) + 1
allowed = {"NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS", "IDENTICAL_ON_ALL_PRESERVED_FIELDS",
           "SINGLE_OBSERVATION__NO_COMPARISON_MADE"}
bad_enc = [r for r in rel2 if r["encoding_identity_status"] == "NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS"
           and r["distinguishing_field_classes"] == "NONE"]
check("V5_encoding_label_closed_vocabulary_and_field_backed",
      set(enc) <= allowed and not bad_enc,
      f"census={enc}; {len(bad_enc)} rows labelled non-identical with no differing field")

# V6 -------------------------------- text-only distinctions are counted, not normalised away
tonly = [r for r in rel2 if r["distinction_basis"] == "TEXT_DERIVED_ONLY"]
still_unresolved = all(r["semantic_duplication_status"].startswith("UNRESOLVED") for r in tonly)
check("V6_text_only_distinctions_counted_and_left_unresolved",
      len(tonly) > 0 and still_unresolved,
      f"{len(tonly)} of {len(multi)} competing sets are separated ONLY by free-text-derived "
      f"fields; all remain semantically unresolved={still_unresolved}")

# V7 ----------------------------------------- parent/component relations at real strength
ALLOWED_REL = {"CANDIDATE_PARENT_COMPONENT_RELATION__NAME_PATTERN_ONLY",
               "SOURCE_DESCRIBED_SUPERSET_LANGUAGE__COMPONENTS_NOT_NAMED",
               "SOURCE_STATED_PARENT_COMPONENT_RELATION__COMPONENTS_NAMED_IN_RECORD"}
statuses = {r["relation_status"] for r in grp2}
name_only = [r for r in grp2 if r["relation_status"].startswith("CANDIDATE")]
bad_claim = [r for r in name_only if "NOT ESTABLISHED" not in r["same_patients_claim"]]
no_field = [r for r in grp2 if not r["relation_evidence_field"].strip()]
carried = all(a["parent_cohort_key"] == b["parent_cohort_key"] and
              a["component_cohort_keys"] == b["component_cohort_keys"] and
              a["parent_denominator"] == b["parent_denominator"]
              for a, b in zip(grp1, grp2))
check("V7_parent_component_relations_are_candidate_unless_a_field_states_them",
      statuses <= ALLOWED_REL and not bad_claim and not no_field and carried and len(grp2) == 47,
      f"{len(grp2)} relations, statuses={sorted(statuses)}, name-only rows without a "
      f"NOT-ESTABLISHED same-patients note={len(bad_claim)}, rows with no evidence field="
      f"{len(no_field)}, v1 parent/component/denominator columns carried verbatim={carried}")

# V8 ------------------------------ excess categories: disjoint partition + membership union
by = {}
for r in enr:
    by[r["conflict_findings"]] = by.get(r["conflict_findings"], 0) + 1
plain = by.get("WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT", 0)
pooled = by.get("WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT__POOLED_LABEL_IN_MEASURE", 0)
single_key = [k for k in by if k.startswith("SINGLE_COHORT")]
single = sum(by[k] for k in single_key)
union = sum(1 for r in enr if "WITHIN_MEASURE_SUM_EXCEEDS" in r["conflict_findings"])
tbl = {r["category"]: int(r["trials"]) for r in exc}
onegroup = [r for r in enr if r["conflict_findings"].startswith("SINGLE_COHORT")
            and r["groups_in_that_measure"] == "1"]
check("V8_excess_categories_partition_and_membership_agree_with_the_schema",
      plain == 70 and pooled == 35 and single == 1 and union == 106
      and plain + pooled + single == union
      and tbl.get("MEMBERSHIP__ANY_WITHIN_MEASURE_SUM_EXCESS") == union
      and len(onegroup) == 1,
      f"exact labels: plain={plain}, pooled={pooled}, single={single}; they are disjoint and "
      f"sum to the membership view {union}; the single-cohort trial's measure holds "
      f"{onegroup[0]['groups_in_that_measure'] if onegroup else 'NA'} group, so its within-measure "
      f"'sum' is that one cohort")

# V9 --------------------------------------------- the negative control runs and its exit code
p = subprocess.run([sys.executable, os.path.join(BASE, "negative_control.py")],
                   capture_output=True, text=True)
open(os.path.join(EV, "negative-control-from-checks.out"), "w").write(p.stdout)
open(os.path.join(EV, "negative-control-from-checks.err"), "w").write(p.stderr)
check("V9_negative_control_exits_zero_on_all_three_assertions", p.returncode == 0,
      f"returncode={p.returncode}; stdout={p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ''}")

# V10 ------------------------------------- no rate, unique-patient total or capacity quantity
FORBIDDEN = re.compile(r"response_rate|unique_patient|capacity|numerator|proportion_value|"
                       r"pooled_total|grand_total|parent_plus", re.I)
hdrs = {}
for f in sorted(os.listdir(OUT)):
    if f.endswith(".tsv"):
        hdrs[f] = open(os.path.join(OUT, f), encoding="utf-8").readline().rstrip("\n").split("\t")
offending = {f: [c for c in cs if FORBIDDEN.search(c)] for f, cs in hdrs.items()}
offending = {f: c for f, c in offending.items() if c}
check("V10_no_rate_unique_patient_total_or_capacity_column_emitted", not offending,
      f"{len(hdrs)} v2 TSVs checked; offending columns={offending}")

# V11 -------------------------- the v2 prose does not carry the withdrawn overclaim sentences
BAD = ["Genuinely duplicate encodings do not occur",
       "a distinct outcome, time point or population",
       "parent and components are the SAME people"]
prose = {}
for f in sorted(os.listdir(BASE)):
    if f.endswith((".md", ".json")) and os.path.isfile(os.path.join(BASE, f)):
        prose[f] = open(os.path.join(BASE, f), encoding="utf-8").read()
hits = {}
for f, t in prose.items():
    for b in BAD:
        if b in t and "WITHDRAWN" not in t[max(0, t.index(b) - 400):t.index(b) + 200] \
           and "v1" not in t[max(0, t.index(b) - 400):t.index(b)]:
            hits.setdefault(f, []).append(b)
check("V11_withdrawn_overclaim_sentences_are_not_restated_as_v2_claims", not hits,
      f"{len(prose)} v2 prose files scanned; unqualified restatements={hits}")

# V12 --------------------------------- v1 artifact hashes still match v1's own SCHEMA.json
sch = json.load(open(os.path.join(V1, "SCHEMA.json"), encoding="utf-8"))
drift = []
for name, meta in sch["artifacts"].items():
    p2 = os.path.join(V1A, name)
    if not os.path.exists(p2) or sha(p2) != meta["sha256"] or os.path.getsize(p2) != meta["bytes"]:
        drift.append(name)
check("V12_v1_artifacts_still_match_v1_schema_hashes_and_bytes", not drift,
      f"{len(sch['artifacts'])} v1 artifacts re-hashed against v1 SCHEMA.json, {len(drift)} drifted "
      f"({drift})")

npass = sum(1 for r in results if r["pass"])
with open(os.path.join(OUT, "CHECKS-v2.json"), "w", encoding="utf-8") as fh:
    json.dump({"checks": results, "passed": npass, "total": len(results)}, fh, indent=1)
    fh.write("\n")
print(f"{npass}/{len(results)} checks passed")
sys.exit(0 if npass == len(results) else 1)
