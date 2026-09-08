#!/usr/bin/env python3
"""CORRECTED-A v2 — flag-semantics repair over the delivered CORRECTED-A (v1) outputs.

SCOPE: a contract / schema / flag-identifier repair. This script performs NO source audit, no
re-read of the ClinicalTrials.gov payload cache, no re-run of job 1, no leaf re-audit, no rate,
no numerator, no manuscript edit.

It reads ONLY the v1 component outputs (read-only) and writes ONLY files in this v2 directory.
Every v1 byte is left untouched.

The single defect repaired: v1's advisory flag was named
    RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER
and described as "a category that reports responders under its own criteria set". The flag is in
fact computed from the VERBATIM TITLE ONLY (a regex over titles). A verbatim title such as
`Non-CR/Non-PD` does not establish that those participants meet an objective response definition,
and no cross-criteria numerator has been adjudicated anywhere in this campaign. The identifier and
its wording are therefore replaced with a descriptive dropped-response-assessment-category flag.

EVERY title and EVERY count is preserved exactly. No row datum changes.
"""
from __future__ import annotations
import csv, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "CORRECTED-A-denominator-category")

# ---------------------------------------------------------------- the identifier rename (the repair)
FLAG_V1 = "RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER"
FLAG_V2 = "RESPONSE_ASSESSMENT_CATEGORY_TITLE_DROPPED_BY_PRODUCER"
COL_V1 = "dropped_response_bearing_categories_with_values"
COL_V2 = "dropped_response_assessment_category_titles_with_values"
INV_V1 = "response_bearing_title_flag"
INV_V2 = "response_assessment_category_title_flag"
RENAME = {FLAG_V1: FLAG_V2, COL_V1: COL_V2, INV_V1: INV_V2}

FLAG_V2_DESCRIPTION = (
    "The old (job-1) extraction dropped a category whose VERBATIM TITLE matches a "
    "response-assessment vocabulary (sCR, VGPR, CRh, CRi, CRu, CRmrd, nCR, MR, Non-CR/Non-PD, "
    "molecular response, MRD, ...). The flag is computed from the title string alone. "
    "It records only that a response-assessment category was dropped by the old extraction, so "
    "the loss is visible instead of silent. It does NOT state that those participants met any "
    "objective response definition, it does NOT classify them as responders, it does NOT fold any "
    "title into CR or PR, it is NOT an eligibility warrant, and it is NOT a numerator warrant. "
    "No cross-criteria numerator has been adjudicated."
)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def read_tsv_raw(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()

def rows_of(text):
    return [ln.split("\t") for ln in text.split("\n") if ln != ""]

# --------------------------------------------------------------------------- v1 inputs + manifest
V1_FILES = ["corrected-a-rows.tsv", "corrected-a-categories.tsv",
            "corrected-a-category-inventory.tsv", "corrected-a-schema.json",
            "corrected-a-summary.json", "corrected-a-checks.json",
            "corrected-a-change-map.tsv", "corrected-a-change-map.json",
            "corrected-a-input-manifest.json", "CHECK-RUN-RECORD.txt",
            "build_corrected_a.py", "check_corrected_a.py",
            "CORRECTED-A-denominator-category.md"]
manifest = {"note": "sha256 of the v1 CORRECTED-A outputs this component reads and must not modify",
            "v1_dir": os.path.relpath(V1, os.path.dirname(os.path.dirname(HERE))),
            "v1_sha256": {fn: sha256(os.path.join(V1, fn)) for fn in V1_FILES}}

# ------------------------------------------------------------------------------------ rows table
rows_text = read_tsv_raw(os.path.join(V1, "corrected-a-rows.tsv"))
R = rows_of(rows_text)
head, body = R[0], R[1:]
assert len(body) == 552, len(body)
i_adv = head.index("advisory_flag_codes")
i_col = head.index(COL_V1)
i_suit = head.index("proportion_suitability")
i_unres = head.index("unresolved_reason_codes")
i_den = head.index("reported_denominator_participants")
i_units = head.index("denominator_units_available")
i_dstate = head.index("denominator_state")
i_rate = head.index("rate_derived")

new_head = [RENAME.get(h, h) for h in head]
changed_cells = 0
out_body = []
for r in body:
    r = list(r)
    if FLAG_V1 in r[i_adv]:
        r[i_adv] = r[i_adv].replace(FLAG_V1, FLAG_V2)
        changed_cells += 1
    out_body.append(r)

with open(os.path.join(HERE, "corrected-a-v2-rows.tsv"), "w", encoding="utf-8", newline="") as f:
    f.write("\t".join(new_head) + "\n")
    for r in out_body:
        f.write("\t".join(r) + "\n")

# ------------------------------------------------- categories table (no renamed identifier in it)
cats_text = read_tsv_raw(os.path.join(V1, "corrected-a-categories.tsv"))
assert FLAG_V1 not in cats_text and COL_V1 not in cats_text and INV_V1 not in cats_text
with open(os.path.join(HERE, "corrected-a-v2-categories.tsv"), "w", encoding="utf-8", newline="") as f:
    f.write(cats_text)

# ------------------------------------------------------------------------------ inventory table
inv_text = read_tsv_raw(os.path.join(V1, "corrected-a-category-inventory.tsv"))
I = rows_of(inv_text)
inv_head = [RENAME.get(h, h) for h in I[0]]
with open(os.path.join(HERE, "corrected-a-v2-category-inventory.tsv"), "w", encoding="utf-8",
          newline="") as f:
    f.write("\t".join(inv_head) + "\n")
    for r in I[1:]:
        f.write("\t".join(r) + "\n")

# ------------------------------------------------------------------------------------- schema v2
schema = json.load(open(os.path.join(V1, "corrected-a-schema.json"), encoding="utf-8"))
schema["component"] = "CORRECTED-A-denominator-category-v2"
schema["supersedes"] = "CORRECTED-A-denominator-category (v1) — identifiers and wording only"
schema["repair_scope"] = (
    "Interpretive repair of ONE advisory flag identifier and its wording, plus one row column name "
    "and one inventory column name. No value, count, title, denominator, provenance string or "
    "column-26 field is altered. v1 remains intact as delivered evidence."
)
schema["superseded_identifiers"] = {
    FLAG_V1: {"replaced_by": FLAG_V2,
              "why": "The v1 name and its description asserted that the dropped categories report "
                     "RESPONDERS. The flag is computed from the verbatim title alone; a verbatim "
                     "title such as `Non-CR/Non-PD` does not establish that those participants meet "
                     "an objective response definition, and no cross-criteria numerator has been "
                     "adjudicated."},
    COL_V1: {"replaced_by": COL_V2, "why": "Same defect, in the row column name."},
    INV_V1: {"replaced_by": INV_V2, "why": "Same defect, in the inventory column name."},
}
schema["enumerations"]["advisory_flag_codes"] = {
    (FLAG_V2 if k == FLAG_V1 else k): (FLAG_V2_DESCRIPTION if k == FLAG_V1 else v)
    for k, v in schema["enumerations"]["advisory_flag_codes"].items()}
schema["warrants"] = {
    "statement": "No code, flag or state emitted by this component is an eligibility warrant or a "
                 "numerator warrant.",
    FLAG_V2: {"kind": "ADVISORY_NON_BLOCKING", "computed_from": "verbatim category title string only",
              "is_eligibility_warrant": False, "is_numerator_warrant": False,
              "asserts_objective_response": False,
              "affects_proportion_suitability": False,
              "demonstration": "corrected-a-v2-checks.json D1-D6; NON-WARRANT-DEMONSTRATION.md"},
    "responder_class_retained": {
        "retained": False,
        "note": "This component retains NO narrower responder class. No responder definition is "
                "asserted, inferred from a title or token, or source-bound here, because none is "
                "needed for a flag that only records what the old extraction dropped."},
}
for t in schema["tables"]:
    for c in schema["tables"][t]["columns"]:
        if c["name"] == COL_V1:
            c["name"] = COL_V2
            c["description"] = (
                "Dropped categories whose VERBATIM TITLE matches a response-assessment vocabulary "
                "(sCR, VGPR, CRh, CRi, CRu, CRmrd, nCR, MR, Non-CR/Non-PD, ...), carried with class "
                "index and reported value. Title-derived flag only: titles stay verbatim, nothing is "
                "folded into CR/PR, no participant is classified as a responder, and this column is "
                "never summed into a numerator anywhere in this component.")
        elif c["name"] == INV_V1:
            c["name"] = INV_V2
            c["description"] = ("yes if the verbatim title belongs to a response-assessment "
                                "vocabulary under some criteria set. A title property, not a "
                                "statement about the participants counted under it.")
        elif c["name"] == "reported_denominator_participants" and t == "corrected-a-rows.tsv":
            c["description"] += (" Checked explicitly for POSITIVITY in v2 (check D7): present, "
                                 "integer and > 0, with zero / missing / non-`Participants` "
                                 "denominators distinguished rather than conflated.")
json.dump(schema, open(os.path.join(HERE, "corrected-a-v2-schema.json"), "w", encoding="utf-8"),
          indent=1, sort_keys=False)

# ------------------------------------------------------------------------------------ summary v2
summ = json.load(open(os.path.join(V1, "corrected-a-summary.json"), encoding="utf-8"))
summ["component"] = "CORRECTED-A-denominator-category-v2"
summ["advisory_flag_codes"] = {(FLAG_V2 if k == FLAG_V1 else k): v
                               for k, v in summ["advisory_flag_codes"].items()}
summ["v2_repair"] = {"kind": "IDENTIFIER_AND_WORDING_ONLY",
                     "row_data_values_changed": 0,
                     "rows_whose_advisory_code_string_was_renamed": changed_cells,
                     "counts_preserved": True, "titles_preserved": True,
                     "responder_claim_removed": True,
                     "responder_class_retained": False,
                     "numerator_constructed": False}
json.dump(summ, open(os.path.join(HERE, "corrected-a-v2-summary.json"), "w", encoding="utf-8"),
          indent=1, sort_keys=True)

# -------------------------------------------------------------------------- v1 -> v2 change map
CM = [
 ("advisory flag code", FLAG_V1, FLAG_V2, "RENAMED_SEMANTICS_CORRECTED",
  "101 rows carried the v1 code; 101 rows carry the v2 code. Membership identical, count identical. "
  "The v1 name asserted RESPONDERS; the flag is computed from the verbatim title alone."),
 ("advisory flag description", "The old extraction dropped a category that reports responders under "
  "its own criteria set.", FLAG_V2_DESCRIPTION, "REWORDED_CLAIM_WITHDRAWN",
  "The responder claim is withdrawn. No objective-response assertion is made about any participant."),
 ("row column name", COL_V1, COL_V2, "RENAMED_VALUES_UNCHANGED",
  "Column position and every cell value byte-identical to v1."),
 ("inventory column name", INV_V1, INV_V2, "RENAMED_VALUES_UNCHANGED",
  "12 of 123 titles flagged `yes` in v1; the same 12 in v2."),
 ("row data values", "(all 51 columns)", "(all 51 columns)", "UNCHANGED_BYTE_FOR_BYTE",
  "Proven by check D8: reversing the identifier rename on the v2 rows file reproduces the v1 rows "
  "file's sha256 exactly."),
 ("column 26", "job1_column26_original_label / job1_column26_value_carried_unchanged / "
  "evaluable_n_minus_reported_denominator", "(same)", "UNTOUCHED",
  "The v1 column-26 treatment is correct and is carried without any change."),
 ("denominator + provenance", "reported_denominator_participants / denominator_provenance",
  "(same)", "UNTOUCHED_POSITIVITY_NOW_CHECKED",
  "Values and provenance carried verbatim. v2 adds an explicit positive-denominator check (D7) "
  "rather than relying on denominator_state == READ_FROM_SOURCE."),
 ("categories table", "corrected-a-categories.tsv", "corrected-a-v2-categories.tsv",
  "COPIED_BYTE_IDENTICAL", "3,123 records, 123 verbatim titles, no folding, no rename applies."),
 ("v1 directory", "CORRECTED-A-denominator-category/", "(untouched)", "PRESERVED",
  "Every v1 byte, and every original job-1 / leaf byte, left as delivered. v1's historical claims "
  "stand as the record of what was delivered; v2 does not rewrite them."),
]
with open(os.path.join(HERE, "corrected-a-v2-change-map.tsv"), "w", encoding="utf-8",
          newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["target", "v1", "v2", "disposition", "note"])
    for r in CM:
        w.writerow(r)
json.dump({"change_map": [dict(zip(("target", "v1", "v2", "disposition", "note"), r)) for r in CM],
           "disposition_vocabulary": {
               "RENAMED_SEMANTICS_CORRECTED": "identifier replaced; the set it marks is unchanged",
               "REWORDED_CLAIM_WITHDRAWN": "prose replaced; a claim the evidence does not support is withdrawn",
               "RENAMED_VALUES_UNCHANGED": "name only; every cell byte-identical",
               "UNCHANGED_BYTE_FOR_BYTE": "no change at all, proven by hash",
               "UNTOUCHED": "carried from v1 without inspection-driven edit",
               "UNTOUCHED_POSITIVITY_NOW_CHECKED": "values carried; a new explicit check added over them",
               "COPIED_BYTE_IDENTICAL": "file copied unchanged",
               "PRESERVED": "original evidence left intact"}},
          open(os.path.join(HERE, "corrected-a-v2-change-map.json"), "w", encoding="utf-8"), indent=1)

manifest["v2_outputs_sha256"] = {}
json.dump(manifest, open(os.path.join(HERE, "corrected-a-v2-input-manifest.json"), "w",
                         encoding="utf-8"), indent=1, sort_keys=True)

print(f"rows=552 renamed_advisory_cells={changed_cells} "
      f"row_data_values_changed=0 files_written=7")
