#!/usr/bin/env python3
"""CORRECTED-B2 relabeller — inference-strength repair of contract B's identity/overlap labels.

READS ONLY the v1 sibling's already-emitted artifacts. It does NOT open the source cache,
does NOT re-run build_ledger.py, does NOT re-run job2 and does NOT re-run any leaf analysis.
It writes ONLY into this v2 directory; not one byte of the v1 component is opened for writing.

What it repairs (and nothing else):
  1. "Different preserved strings" is relabelled as NON-IDENTICAL ENCODING. It is NOT relabelled
     as a distinct clinical measurement or population. Semantic duplication stays UNRESOLVED
     wherever correspondence has not been established.
  2. Pooled parent -> component relations become CANDIDATE relations at their real evidence
     strength, EXCEPT where an exact record field states the relationship; that field and its
     verbatim text are recorded.
  3. The enrollment-excess categories are presented as the schema actually defines them, with
     the disjoint partition and the non-exclusive membership stated separately. No total is
     manufactured.

Explicitly NOT done: no normalisation of unit order, signs, case or misspellings; no merge of
any two records; no preferred endpoint; no new rate, unique-patient total or capacity bound.
"""
import csv, json, os, re, sys

csv.field_size_limit(10 * 1024 * 1024)
BASE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.normpath(os.path.join(BASE, "..", "CORRECTED-B-identity-selection-overlap"))
V1A = os.path.join(V1, "artifacts")
OUT = os.path.join(BASE, "artifacts")
os.makedirs(OUT, exist_ok=True)

def rd(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))

def wr(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(rows)

summary = {}

# =========================================================== 1 · encoding vs semantics
rel = rd(os.path.join(V1A, "RELATED-SETS-unresolved.tsv"))

# Field classes. TEXT_DERIVED fields are free-text source strings, or tokens derived from
# free-text; a difference in them establishes only that the encodings differ.
TEXT_DERIVED = [
    ("MEASURE_TITLE", "distinct_titles"),
    ("TIME_FRAME_TEXT", "distinct_time_frames"),
    ("ENDPOINT_CONSTRUCT_TOKENS", "distinct_constructs"),
    ("ASSESSMENT_CRITERIA_TOKENS", "distinct_criteria"),
    ("CRITERIA_VERSION_TOKENS", "distinct_criteria_versions"),
    ("POPULATION_DESCRIPTION_TEXT", "distinct_population_descriptions"),
    # unitOfMeasure is a free-text source string too: the negative control showed that a pure
    # case difference in it ("percentage of participants" vs "Percentage of Participants")
    # otherwise counted as a structured distinction. Reclassified, NOT normalised.
    ("UNIT_OF_MEASURE_TEXT", "distinct_units"),
]
STRUCTURED = [
    ("PARAM_TYPE", "distinct_param_types"),
]

REL_HEADER = [
    "cohort_key", "nct", "results_group_title_norm", "n_observations", "observation_ids",
    "om_indices",
    "encoding_identity_status",           # what the field comparison actually shows
    "distinguishing_field_classes",       # which classes of field differ
    "distinction_basis",                  # TEXT_DERIVED_ONLY / INCLUDES_STRUCTURED_FIELD / NONE
    "semantic_duplication_status",        # the repaired claim: unresolved unless established
    "semantic_correspondence_evidence",   # what would be needed, and what is present
    "v1_duplicate_encoding_candidate", "v1_unresolved_states", "v2_unresolved_states",
    "selection_status", "resolution_note",
]
rel_rows = []
enc_census = {}
basis_census = {}
sem_census = {}
for r in rel:
    n = int(r["n_observations"])
    classes = []
    for label, col in TEXT_DERIVED:
        try:
            if int(r[col]) > 1:
                classes.append(label)
        except ValueError:
            pass
    structured = []
    for label, col in STRUCTURED:
        try:
            if int(r[col]) > 1:
                structured.append(label)
        except ValueError:
            pass
    # these two v1 columns are pipe-joined value lists, not counts
    if len(set(r["distinct_denominator_values"].split("|"))) > 1:
        structured.append("PARTICIPANTS_DENOMINATOR_VALUE")
    if len(set(r["distinct_om_types"].split("|"))) > 1:
        structured.append("OUTCOME_MEASURE_TYPE")
    if len(set(r["distinct_denominator_states"].split("|"))) > 1:
        structured.append("DENOMINATOR_STATE")
    classes += structured

    if n <= 1:
        enc = "SINGLE_OBSERVATION__NO_COMPARISON_MADE"
        basis = "NONE"
        sem = "NOT_APPLICABLE__SINGLE_OBSERVATION"
        sem_ev = "No competing observation in this cohort key."
    elif classes:
        enc = "NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS"
        basis = "INCLUDES_STRUCTURED_FIELD" if structured else "TEXT_DERIVED_ONLY"
        sem = "UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED"
        sem_ev = ("The preserved fields differ, which establishes only that the encodings are not "
                  "identical. Whether these are the same measurement on the same patients, or "
                  "different ones, is NOT established by the source and is not decided here.")
    else:
        enc = "IDENTICAL_ON_ALL_PRESERVED_FIELDS"
        basis = "NONE"
        sem = "UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED"
        sem_ev = ("No preserved field separates the competing observations. This is still not a "
                  "finding of semantic duplication; nothing is merged.")
    v2_states = []
    for tok in r["unresolved_states"].split("|"):
        if not tok:
            continue
        if tok == "DUPLICATE_ENCODING_CANDIDATE":
            v2_states.append("IDENTICAL_ON_ALL_PRESERVED_FIELDS__SEMANTIC_DUPLICATION_UNRESOLVED")
        elif tok == "UNRESOLVED_NO_DISTINGUISHING_FIELD_FOUND":
            v2_states.append("UNRESOLVED_NO_DISTINGUISHING_FIELD_FOUND")
        else:
            v2_states.append(tok)
    if n > 1:
        v2_states.append("SEMANTIC_DUPLICATION_UNRESOLVED")
        if basis == "TEXT_DERIVED_ONLY":
            v2_states.append("DISTINCTION_IS_TEXT_DERIVED_ONLY")
    enc_census[enc] = enc_census.get(enc, 0) + 1
    basis_census[basis] = basis_census.get(basis, 0) + 1
    sem_census[sem] = sem_census.get(sem, 0) + 1
    rel_rows.append([
        r["cohort_key"], r["nct"], r["results_group_title_norm"], n,
        r["observation_ids"], r["om_indices"], enc, "|".join(classes) or "NONE", basis,
        sem, sem_ev, r["duplicate_encoding_candidate"], r["unresolved_states"],
        "|".join(v2_states), r["selection_status"],
        "No preferred endpoint, criteria version, time point, population or selection rule is "
        "introduced by this repair. Nothing is normalised and nothing is merged.",
    ])
wr(os.path.join(OUT, "RELATED-SETS-encoding-vs-semantics-v2.tsv"), REL_HEADER, rel_rows)
summary["related_sets_rows"] = len(rel_rows)
summary["encoding_identity_census"] = enc_census
summary["distinction_basis_census"] = basis_census
summary["semantic_duplication_census"] = sem_census
summary["competing_sets"] = sum(1 for r in rel if int(r["n_observations"]) > 1)

# =========================================================== 2 · parent/component relations
grp = rd(os.path.join(V1A, "GROUP-RELATIONS-pooled-parent-component.tsv"))
wanted = {r["parent_cohort_key"] for r in grp}
comp_wanted = set()
for r in grp:
    comp_wanted |= set(r["component_cohort_keys"].split("|"))

# Pull the parent's own source strings out of the v1 ledger (read-only, streaming).
titles, descs = {}, {}
with open(os.path.join(V1A, "LEDGER-response-observations.tsv"), encoding="utf-8", newline="") as fh:
    for o in csv.DictReader(fh, delimiter="\t"):
        key = o["nct"] + "||" + o["results_group_title_norm"]
        if key in wanted or key in comp_wanted:
            if o["results_group_title"] and key not in titles:
                titles[key] = o["results_group_title"]
            d = o["results_group_description"]
            if d:
                descs.setdefault(key, set()).add(d)

# Relation evidence is read from the record itself, in two tiers. Neither tier infers a
# relation from a pooled-sounding NAME alone; a name-only case stays CANDIDATE.
#   Tier A  the field enumerates the components or states the arithmetic.
#   Tier B  the field uses all-participants/superset language but names no component.
ENUM_RE = re.compile(
    r"(equals?\s+[^.;]*\bplus\b|\bsum of\b|\btotal of (?:arms?|groups?|cohorts?|doses?)\b|"
    r"\bcombined\b[^.;]{0,40}\b(?:arms?|groups?|cohorts?|doses?|schedules?)\b|"
    r"\b(?:arms?|groups?|cohorts?|doses?)\b[^.;]{0,60}\bcombined\b|"
    r"\bboth\b[^.;]{0,60}\b(?:arms?|groups?|cohorts?|treatment arms?)\b|"
    r"\b(?:cohorts?|groups?|arms?|parts?)\s+[0-9A-Z][^.;]{0,40}\b(?:and|\+)\s+[0-9A-Z]|"
    r"\bpooled (?:across|from|analysis of)\b|"
    r"\b(?:dose )?(?:escalation|expansion) arms\b)", re.I)
SUPERSET_RE = re.compile(
    r"\ball (?:participants|patients|subjects)\b[^.;]{0,80}\b(?:who|in|from|across|receiv\w+|"
    r"treated|enrolled)\b", re.I)

GRP_HEADER = grp[0].keys() if grp else []
GRP_HEADER = list(GRP_HEADER) + [
    "relation_status", "relation_evidence_field", "relation_evidence_text",
    "relation_evidence_strength", "same_patients_claim",
]
grp_rows = []
rel_status_census = {}
for r in grp:
    pk = r["parent_cohort_key"]
    cand_fields = []
    if pk in titles:
        cand_fields.append(("results_group_title", titles[pk]))
    for d in sorted(descs.get(pk, ())):
        cand_fields.append(("results_group_description", d))
    hit = None
    for field, text in cand_fields:
        m = ENUM_RE.search(text or "")
        if m:
            hit = ("A", field, text, m.group(0))
            break
    if hit is None:
        for field, text in cand_fields:
            m = SUPERSET_RE.search(text or "")
            if m:
                hit = ("B", field, text, m.group(0))
                break
    if hit and hit[0] == "A":
        status = "SOURCE_STATED_PARENT_COMPONENT_RELATION__COMPONENTS_NAMED_IN_RECORD"
        ev_field, ev_text = hit[1], hit[2]
        strength = ("EXPLICIT_IN_RECORD__the named field enumerates the component groups or states "
                    "the pooling arithmetic. Matched source text: " + hit[3])
        same = ("SOURCE_STATED for the components the record names: the record itself describes this "
                "parent as covering them. Parent and components are still never added together, and "
                "the mapping to every component cohort key listed in this row is not thereby proven.")
    elif hit:
        status = "SOURCE_DESCRIBED_SUPERSET_LANGUAGE__COMPONENTS_NOT_NAMED"
        ev_field, ev_text = hit[1], hit[2]
        strength = ("SOURCE_DESCRIBED__the named field uses all-participants/superset language but "
                    "names no component group. Matched source text: " + hit[3])
        same = ("NOT ESTABLISHED as to WHICH cohorts are the components. The record describes a "
                "superset group; which of this trial's other cohorts it contains is not stated.")
    else:
        status = "CANDIDATE_PARENT_COMPONENT_RELATION__NAME_PATTERN_ONLY"
        ev_field = "results_group_title_norm"
        ev_text = titles.get(pk, r["parent_cohort_key"].split("||", 1)[-1])
        strength = ("CANDIDATE__the only basis is that the normalised group title begins with a "
                    "pooled-sounding word (total/overall/all participants/all patients/"
                    "all subjects/combined). A name is not evidence of who the patients are.")
        same = ("NOT ESTABLISHED: this repair does NOT assert that the parent and its components "
                "are the same people. That relation is a candidate at name-level evidence only.")
    rel_status_census[status] = rel_status_census.get(status, 0) + 1
    row = [r[k] for k in grp[0].keys()]
    row[list(grp[0].keys()).index("relation_type")] = status
    grp_rows.append(row + [status, ev_field, ev_text, strength, same])
wr(os.path.join(OUT, "GROUP-RELATIONS-candidate-parent-component-v2.tsv"), GRP_HEADER, grp_rows)
summary["parent_component_relations"] = len(grp_rows)
summary["relation_status_census"] = rel_status_census

# =========================================================== 3 · excess-category presentation
enr = rd(os.path.join(V1A, "ENROLLMENT-CONFLICT.tsv"))
exact = {}
for r in enr:
    exact[r["conflict_findings"]] = exact.get(r["conflict_findings"], 0) + 1
within = [r for r in enr if "WITHIN_MEASURE_SUM_EXCEEDS" in r["conflict_findings"]]
single = [r for r in enr if r["conflict_findings"].startswith("SINGLE_COHORT")]
pooled = [r for r in enr if "POOLED_LABEL_IN_MEASURE" in r["conflict_findings"]]
plain_within = [r for r in within if r not in pooled and r not in single]
one_group = [r for r in within if r["groups_in_that_measure"] == "1"]

EXC_HEADER = ["category", "definition", "trials", "exclusivity", "note"]
exc_rows = [
    ["EXACT_LABEL__WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT",
     "conflict_findings is exactly this label: a within-one-measure denominator sum above "
     "registered enrollment, no pooled/total group in that measure",
     len(plain_within), "DISJOINT from the other two excess labels",
     "This is the 70 in the v1 contract's table."],
    ["EXACT_LABEL__WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT__POOLED_LABEL_IN_MEASURE",
     "as above, and that measure contains a pooled/total-labelled group",
     len(pooled), "DISJOINT from the other two excess labels",
     "This is the 35. It is NOT a subset of the 70; the v1 table's indentation reads as if it "
     "were."],
    ["EXACT_LABEL__SINGLE_COHORT_EXCEEDS_ENROLLMENT__…|WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT",
     "one reported cohort denominator alone exceeds registered enrollment",
     len(single), "DISJOINT from the other two excess labels",
     "This is the 1 (NCT00756509, 41 vs 34). Its measure holds exactly one group, so its "
     "within-measure 'sum' IS that single cohort, not an additional summation phenomenon."],
    ["MEMBERSHIP__ANY_WITHIN_MEASURE_SUM_EXCESS",
     "trials whose conflict_findings contains WITHIN_MEASURE_SUM_EXCEEDS at all",
     len(within), "NON-EXCLUSIVE membership view; it is the union of the three labels above",
     "This is the 106 in the v1 contract's prose. 106 and 70 are two different quantities and "
     "the v1 text uses them as if comparable. No total is manufactured here: the union is "
     "stated as a membership view, the labels as the partition."],
    ["EXACT_LABEL__NO_CONFLICT_DETECTED", "neither a single cohort nor any within-measure sum "
     "exceeds enrollment", exact.get("NO_CONFLICT_DETECTED", 0),
     "DISJOINT", "Remaining trial rows in the v1 enrollment file."],
]
wr(os.path.join(OUT, "ENROLLMENT-EXCESS-CATEGORIES-v2.tsv"), EXC_HEADER, exc_rows)
summary["enrollment_rows"] = len(enr)
summary["exact_label_census"] = exact
summary["within_measure_membership"] = len(within)
summary["single_cohort_excess"] = len(single)
summary["single_cohort_excess_measure_group_count"] = sorted({r["groups_in_that_measure"] for r in single})
summary["within_measure_excess_with_one_group_only"] = len(one_group)

with open(os.path.join(OUT, "RELABEL-SUMMARY-v2.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=1, sort_keys=True)
    fh.write("\n")
print(json.dumps(summary, indent=1, sort_keys=True))
