#!/usr/bin/env python3
"""Focused negative control for contract B's identity rule.

Question the control answers: if the SAME substantive record is entered twice with different but
harmless wording, does the rule report a distinct outcome / time point / population?

Fixture: two synthetic observations of one cohort key. Same trial, same cohort, same paramType,
same unit, same Participants denominator, same reported values. The only differences are
cosmetic: capitalisation and an abbreviation in the title, an abbreviated month unit in the time
frame, a hyphen and 'patients' vs 'participants' in the population text, and a misspelling.
Nothing about the measurement differs.

The control asserts three things:
  NC1  the v1 rule reports NO duplicate-encoding candidate here, so the v1 contract sentences
       "Genuinely duplicate encodings do not occur" and "every one ... a distinct outcome, time
       point or population" would be applied to a pair that is one record twice. The control is
       designed to FAIL the v1 claim; that failure is the finding.
  NC2  the v2 labels report NON_IDENTICAL_ENCODING with distinction_basis TEXT_DERIVED_ONLY and
       semantic_duplication_status UNRESOLVED, i.e. a statement about encodings only.
  NC3  NEITHER rule merges, normalises, de-duplicates or rewrites a clinical record. Both
       observations survive, byte-identical to the fixture, under both rules.

No source record is read, written or altered by this control. It is entirely synthetic.
Exit 0 only if all three assertions hold.
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "artifacts")
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ fixture (synthetic)
A = {
    "obs_id": "NCT_SYNTHETIC_0001#om0#OG000",
    "om_title": "Objective Response Rate (ORR)",
    "om_time_frame": "Up to 24 months",
    "om_population_description": "Efficacy evaluable participants",
    "om_type": "PRIMARY",
    "om_param_type": "NUMBER",
    "om_unit_of_measure": "percentage of participants",
    "endpoint_constructs": "ORR",
    "assessment_criteria": "RECIST",
    "criteria_version_tokens": "1.1",
    "denominator_state": "PRESENT",
    "denominator_value_participants": "58",
    "measurement_value_raw": "31.0",
}
B = dict(A)
B.update({
    "obs_id": "NCT_SYNTHETIC_0001#om1#OG000",
    "om_title": "Objective response rate, ORR",           # case + punctuation only
    "om_time_frame": "up to 24 mo.",                      # abbreviation only
    "om_population_description": "Efficacy-evaluable patients",  # hyphen + synonym
    "om_unit_of_measure": "Percentage of Participants",   # case only
    "criteria_version_tokens": "1.1 ",                    # trailing space
    "assessment_criteria": "RECSIT",                      # misspelling, left as recorded
})
# A genuinely different second record, for contrast. Same cohort key, real differences.
C = dict(A)
C.update({
    "obs_id": "NCT_SYNTHETIC_0002#om1#OG000",
    "om_time_frame": "Up to 6 months",
    "denominator_value_participants": "44",
})

FIXTURE = {"pair_same_record_different_wording": [A, B],
           "pair_genuinely_different": [dict(A, obs_id="NCT_SYNTHETIC_0002#om0#OG000"), C]}

# -------------------------------------------- rule under test, transcribed from each version
V1_FIELDS = ["om_title", "om_time_frame", "endpoint_constructs", "assessment_criteria",
             "criteria_version_tokens", "om_population_description", "om_param_type",
             "om_unit_of_measure", "denominator_value_participants"]

def v1_rule(obs):
    """build_ledger.py's dup predicate: identical on every preserved field -> candidate.
    No normalisation of case, spacing, spelling, sign or unit order is performed by v1, and
    none is added here."""
    dup = len(obs) > 1 and all(len({o[f] for o in obs}) == 1 for f in V1_FIELDS)
    return {"duplicate_encoding_candidate": dup,
            "v1_contract_sentence_applied":
                ("DUPLICATE_ENCODING_CANDIDATE" if dup else
                 "no duplicate encoding -> v1 contract asserts 'a distinct outcome, time point "
                 "or population'")}

TEXT_DERIVED = ["om_title", "om_time_frame", "endpoint_constructs", "assessment_criteria",
                "criteria_version_tokens", "om_population_description", "om_unit_of_measure"]
STRUCTURED = ["om_param_type", "denominator_value_participants", "om_type", "denominator_state"]

def v2_rule(obs):
    """relabel_v2.py's classification: encodings only, semantics explicitly unresolved."""
    diff_text = [f for f in TEXT_DERIVED if len({o[f] for o in obs}) > 1]
    diff_struct = [f for f in STRUCTURED if len({o.get(f) for o in obs}) > 1]
    if len(obs) <= 1:
        return {"encoding_identity_status": "SINGLE_OBSERVATION__NO_COMPARISON_MADE",
                "distinction_basis": "NONE",
                "semantic_duplication_status": "NOT_APPLICABLE__SINGLE_OBSERVATION"}
    if diff_text or diff_struct:
        enc = "NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS"
        basis = "INCLUDES_STRUCTURED_FIELD" if diff_struct else "TEXT_DERIVED_ONLY"
    else:
        enc, basis = "IDENTICAL_ON_ALL_PRESERVED_FIELDS", "NONE"
    return {"encoding_identity_status": enc, "distinction_basis": basis,
            "distinguishing_fields": diff_text + diff_struct,
            "semantic_duplication_status": "UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED"}

# ------------------------------------------------------------------------------ run
results, failures = {}, []
import copy
before = copy.deepcopy(FIXTURE)

for name, obs in FIXTURE.items():
    results[name] = {"n_input_records": len(obs), "v1": v1_rule(obs), "v2": v2_rule(obs)}

same = results["pair_same_record_different_wording"]
diff = results["pair_genuinely_different"]

# NC1 — the v1 claim is falsified by a pair that is one record twice.
nc1 = (same["v1"]["duplicate_encoding_candidate"] is False)
results["NC1_v1_claim_overclaims"] = {
    "assertion": "v1 reports no duplicate-encoding candidate for a same-record/different-wording "
                 "pair, so v1's 'every one ... a distinct outcome, time point or population' is "
                 "applied to a pair that is not distinct.",
    "holds": nc1}
if not nc1:
    failures.append("NC1")

# NC2 — v2 states only what the comparison shows.
nc2 = (same["v2"]["encoding_identity_status"] == "NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS"
       and same["v2"]["distinction_basis"] == "TEXT_DERIVED_ONLY"
       and same["v2"]["semantic_duplication_status"].startswith("UNRESOLVED"))
results["NC2_v2_label_is_about_encodings_only"] = {"assertion":
    "v2 labels the same pair NON_IDENTICAL_ENCODING / TEXT_DERIVED_ONLY and leaves semantic "
    "duplication UNRESOLVED, claiming nothing about outcome, time point or population.",
    "holds": nc2}
if not nc2:
    failures.append("NC2")

# NC3 — no auto-merge, no normalisation, under either rule.
nc3 = (before == FIXTURE
       and same["n_input_records"] == 2 and diff["n_input_records"] == 2
       and same["v2"]["semantic_duplication_status"].startswith("UNRESOLVED")
       and diff["v2"]["semantic_duplication_status"].startswith("UNRESOLVED"))
results["NC3_no_clinical_record_is_merged_or_normalised"] = {"assertion":
    "Both records survive unchanged under both rules; no case-folding, unit reordering, sign or "
    "spelling repair is applied; the genuinely different pair is left UNRESOLVED too, so the v2 "
    "label cannot be used to merge either pair.",
    "holds": nc3}
if not nc3:
    failures.append("NC3")

results["fixture"] = FIXTURE
results["failures"] = failures
with open(os.path.join(OUT, "NEGATIVE-CONTROL-wording-only-duplicate.json"), "w",
          encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)
    fh.write("\n")

for k in ("NC1_v1_claim_overclaims", "NC2_v2_label_is_about_encodings_only",
          "NC3_no_clinical_record_is_merged_or_normalised"):
    print(("PASS " if results[k]["holds"] else "FAIL ") + k)
print(f"{3 - len(failures)}/3 negative-control assertions hold")
sys.exit(1 if failures else 0)
