#!/usr/bin/env python3
"""
HLA-COVERAGE-2 — what the neoantigen screen's 10-allele MHCflurry panel actually covers.

Three independent re-derivations, all from files already in this checkout, all offline:

  (a) the panel's own allele list, read verbatim from the committed screen artifact;
  (b) the fraction of EXPERIMENTALLY VALIDATED fusion-junction epitope-allele pairs the
      screen was structurally unable to return, re-derived from the EPITOPE-BENCHMARK
      records by re-implementing that lane's inclusion rule here (not by trusting its count);
  (c) the fraction of a modelled population the panel's alleles cover, using the
      allele-frequency table ALREADY PRESENT in this checkout.

⛔ WHAT THIS IS NOT.  Coverage is allele CARRIAGE under a stated arithmetic model.  It is not
presentation, not immunogenicity, not efficacy, not eligibility for any therapy, and it says
nothing about safety, selectivity, therapeutic window or clinical readiness.  A "pair the
screen could not return" is a statement about the screen's CONFIGURATION, nothing else.

⛔ Route B8 (HLA-C) is CLOSED.  No HLA-C frequency is fetched, proxied or substituted here.
Where HLA-C frequency is required the result is reported UNKNOWN, never zero.
"""
import json, os, re, hashlib, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))

SCREEN = os.path.join(ROOT, "research/modalities/fusion-breakpoint-neoantigens.json")
FREQ   = os.path.join(ROOT, "research/modalities/coverage-threshold-curve.json")
COVER  = os.path.join(ROOT, "research/modalities/hla-coverage.json")
MATRIX = os.path.join(ROOT, "research/modalities/epitope-allele-matrix.json")
CURVE  = os.path.join(ROOT, "research/modalities/coverage-curve.json")
BENCH  = os.path.join(HERE, "..", "EPITOPE-BENCHMARK", "epitope-records.json")

def sha(p):
    h = hashlib.sha256(); b = open(p, "rb").read(); h.update(b)
    return {"path": os.path.relpath(os.path.abspath(p), ROOT), "bytes": len(b), "sha256": h.hexdigest()}

prov = {k: sha(v) for k, v in
        [("screen", SCREEN), ("frequency_table", FREQ), ("hla_coverage", COVER),
         ("expanded_matrix", MATRIX), ("expanded_curve", CURVE), ("epitope_records", BENCH)]}

screen = json.load(open(SCREEN))
freqd  = json.load(open(FREQ))
cover  = json.load(open(COVER))
matrix = json.load(open(MATRIX))
curve  = json.load(open(CURVE))
rec    = json.load(open(BENCH))["records"]

# ---------------------------------------------------------------- (a) the panel, verbatim
PANEL = list(screen["_predictor"]["alleles"])
assert screen["_predictor"]["tool"] == "MHCflurry"
panel_loci = sorted({a.split("*")[0].replace("HLA-", "") for a in PANEL})

# ------------------------------------------------- (b) validated set, rule re-implemented
AA = "ACDEFGHIKLMNPQRSTVWY"
def measured(r):  return any(g in r["evidence"] for g in ("MS_ELUTION", "TCELL", "MULTIMER"))
def seq_known(r): return bool(re.fullmatch("[%s]+" % AA, r["peptide"]))
def cIwin(r):     return r["len"] is not None and 8 <= r["len"] <= 11
def cIres(r):     return bool(re.search(r"HLA-[ABC]\*?\d", r["hla"] or ""))
def natural(r):   return "ANCHOR-MODIFIED" not in r["fusion"] and "heteroclitic" not in r["peptide"]

VALIDATED = [r for r in rec if measured(r) and r["spans_junction"] == "yes" and natural(r)
             and seq_known(r) and cIwin(r) and cIres(r)]

# Restriction parsing.  ONLY the restricting allotype(s) are taken.  Parenthesised
# "(also bound X in vitro)" clauses are IN-VITRO BINDING, not restriction, and are dropped —
# recorded explicitly so the choice is auditable rather than silent.
TWO_FIELD = re.compile(r"HLA-([ABC]\*\d{2}:\d{2})")
LOW_RES   = re.compile(r"HLA-([ABC]\d+)(?![\*:\d])")
def restrictions(r):
    head = r["hla"].split("(")[0]                    # drop "(also bound ...)" clauses
    two  = ["HLA-" + m for m in TWO_FIELD.findall(head)]
    low  = ["HLA-" + m for m in LOW_RES.findall(head)] if not two else []
    return two, low

pairs_two, pairs_low, per_epitope = [], [], []
for r in VALIDATED:
    two, low = restrictions(r)
    per_epitope.append({"id": r["id"], "fusion": r["fusion"], "peptide": r["peptide"],
                        "len": r["len"], "hla_field": r["hla"], "evidence": r["evidence"],
                        "two_field_restrictions": two, "low_resolution_only": low})
    pairs_two += [(r["id"], a) for a in two]
    pairs_low += [(r["id"], a) for a in low]

def norm(a): return a.replace("HLA-", "")
panel_set = {norm(a) for a in PANEL}
in_panel  = [p for p in pairs_two if norm(p[1]) in panel_set]
out_panel = [p for p in pairs_two if norm(p[1]) not in panel_set]
c_pairs   = [p for p in pairs_two if norm(p[1]).startswith("C*")]

# low-resolution arm: "HLA-A24" is in the panel only if read at 1-field resolution
def low_in_panel(a):
    fam = norm(a)                                     # e.g. "A24"
    return any(norm(p).startswith(fam[0] + "*" + fam[1:].zfill(2)) for p in PANEL)
low_hits = [(i, a, low_in_panel(a)) for i, a in pairs_low]

allotypes = sorted({norm(a) for _, a in pairs_two})

# ------------------------------------------------------------------ (c) population coverage
AF = freqd["allele_frequencies"]
# cross-check: the frequency table must agree, digit for digit, with the manuscript's own
# artifact on every allele the two share.  A disagreement would itself be the finding.
shared = sorted(set(AF) & set(cover["global"]["allele_frequencies"]))
xcheck = {a: {"threshold_curve": AF[a], "hla_coverage": cover["global"]["allele_frequencies"][a],
              "identical": AF[a] == cover["global"]["allele_frequencies"][a]} for a in shared}

def carrier(af):  return 1.0 - (1.0 - af) ** 2          # Hardy-Weinberg, >=1 copy
def indep(afs):
    p = 1.0
    for af in afs: p *= (1.0 - af) ** 2
    return 1.0 - p

def coverage_block(alleles, label):
    have = [a for a in alleles if a in AF]
    miss = [a for a in alleles if a not in AF]
    afs  = [AF[a]["allele_frequency"] for a in have]
    cars = [carrier(af) for af in afs]
    est  = indep(afs) if have else 0.0
    return {
        "label": label, "alleles_requested": alleles,
        "n_requested": len(alleles),
        "alleles_with_local_frequency": have, "n_with_frequency": len(have),
        "alleles_without_local_frequency_UNKNOWN": miss, "n_unknown": len(miss),
        "independence_model_coverage_over_known_alleles": round(est, 6) if have else None,
        "is_exact": len(miss) == 0,
        "reading": ("exact under the model" if not miss else
                    "LOWER BOUND under the model; the missing alleles' frequencies are "
                    "UNKNOWN in this checkout, not zero"),
        "distribution_free_bounds_over_known_alleles": {
            "lower_max_single_carrier": round(max(cars), 6) if cars else None,
            "upper_min_1_sum_carrier": round(min(1.0, sum(cars)), 6) if cars else None,
            "note": "Frechet/Bonferroni bounds, assuming nothing about linkage or same-locus "
                    "exclusivity; the independence figure need not lie inside them if the "
                    "independence assumption is wrong."},
        "per_allele_carrier_frequency": {a: round(carrier(AF[a]["allele_frequency"]), 6) for a in have},
    }

VALID_ALLOTYPES = ["HLA-" + a for a in allotypes]
blocks = [
    coverage_block(PANEL, "the screen's 10-allele MHCflurry panel"),
    coverage_block(sorted({"HLA-" + norm(a) for _, a in in_panel}),
                   "validated allotypes INSIDE the panel"),
    coverage_block(sorted({"HLA-" + norm(a) for _, a in out_panel}),
                   "validated allotypes OUTSIDE the panel (the screen could not return these)"),
    coverage_block(VALID_ALLOTYPES, "all validated allotypes"),
    coverage_block(cover["global"]["all_strong_binder_alleles"],
                   "manuscript's all-strong base set (re-derivation target)"),
    coverage_block(cover["global"]["e7e3_public_epitope_alleles"],
                   "manuscript's e7::e3 public set (re-derivation target)"),
]

# re-derivation of the two committed headline numbers, digit for digit
redev = []
for key, block_label in [("coverage_any_strong_binder_allele", "manuscript's all-strong base set (re-derivation target)"),
                         ("coverage_e7e3_public", "manuscript's e7::e3 public set (re-derivation target)")]:
    b = [x for x in blocks if x["label"] == block_label][0]
    committed = cover["global"][key]
    mine = b["independence_model_coverage_over_known_alleles"]
    redev.append({"committed_field": key, "committed_value": committed,
                  "re_derived_here": round(mine, 4),
                  "reproduces_to_4dp": round(mine, 4) == round(committed, 4),
                  "absolute_difference": round(abs(mine - committed), 8)})

# the expanded scan: code vs committed artifact
import ast
scan_src = open(os.path.join(ROOT, "research/modalities/coverage_scan.py")).read()
def literal_list(name):
    m = re.search(name + r"\s*=\s*(\[[^\]]*\])", scan_src, re.S)
    return ast.literal_eval(m.group(1)) if m else None
panel_ab, panel_c = literal_list("PANEL_AB"), literal_list("PANEL_C")
expanded = {
    "committed_artifact_panel_n": len(matrix["panel"]),
    "committed_artifact_loci": sorted({a.split("*")[0].replace("HLA-", "") for a in matrix["panel"]}),
    "committed_curve_panel_size": curve["panel_size"],
    "producer_PANEL_AB_n": len(panel_ab), "producer_PANEL_C_n": len(panel_c),
    "producer_PANEL_total_n": len(panel_ab) + len(panel_c),
    "artifact_matches_producer": len(matrix["panel"]) == len(panel_ab) + len(panel_c),
}

# is there ANY HLA-C allele frequency anywhere in the local frequency sources?
c_freq_present = sorted([a for a in AF if "C*" in a] +
                        [a for a in cover["global"]["allele_frequencies"] if "C*" in a])

out = {
    "_id": "HLA-COVERAGE-2-panel-coverage",
    "_lane": "HLA-COVERAGE-2",
    "_what": "What the neoantigen screen's 10-allele MHCflurry panel covers, against the "
             "validated fusion-junction epitope set and against the allele-frequency table "
             "already present in this checkout.",
    "⛔_what_this_is_not":
        "Allele carriage under a stated arithmetic model. NOT presentation, immunogenicity, "
        "efficacy, safety, selectivity, therapeutic window, clinical readiness or patient "
        "eligibility. A pair 'the screen could not return' is a statement about the screen's "
        "configuration only.",
    "⛔_route_B8": "HLA-C is a CLOSED route. No HLA-C frequency was fetched, proxied or "
                  "substituted. Every HLA-C population quantity below is UNKNOWN, not zero.",
    "_provenance": prov,
    "_offline": True, "_cost_usd": 0.0,

    "a_panel": {
        "source_field": "research/modalities/fusion-breakpoint-neoantigens.json :: _predictor.alleles",
        "tool": screen["_predictor"]["tool"], "version": screen["_predictor"]["version"],
        "models_release": screen["_predictor"]["models_release"],
        "peptide_lengths": screen["_predictor"]["peptide_lengths"],
        "thresholds": screen["_predictor"]["thresholds"],
        "alleles": PANEL, "n": len(PANEL), "loci_present": panel_loci,
        "n_HLA_C_in_panel": sum(1 for a in PANEL if "C*" in a),
    },

    "b_validated_pairs": {
        "n_validated_epitopes": len(VALIDATED),
        "inclusion_rule": "measured (MS_ELUTION|TCELL|MULTIMER) AND spans_junction=yes AND "
                          "natural (not anchor-modified/heteroclitic) AND sequenced AND "
                          "8<=len<=11 AND class-I restricted",
        "restriction_parsing": "two-field HLA-[ABC]*NN:NN taken from the restriction field with "
                               "any parenthesised '(also bound X)' in-vitro clause dropped; "
                               "one-field labels (e.g. HLA-A24) reported separately, never "
                               "silently promoted to a two-field allotype",
        "per_epitope": per_epitope,
        "distinct_two_field_allotypes": allotypes,
        "n_distinct_two_field_allotypes": len(allotypes),
        "n_two_field_pairs": len(pairs_two),
        "pairs_in_panel": [list(p) for p in in_panel], "n_in_panel": len(in_panel),
        "pairs_out_of_panel": [list(p) for p in out_panel], "n_out_of_panel": len(out_panel),
        "fraction_screen_could_not_return": round(len(out_panel) / len(pairs_two), 4),
        "HLA_C_pairs": [list(p) for p in c_pairs], "n_HLA_C_pairs": len(c_pairs),
        "n_HLA_C_epitopes": len({i for i, _ in c_pairs}),
        "low_resolution_only_pairs": [list(x) for x in low_hits],
        "n_low_resolution_only": len(low_hits),
    },

    "c_population_coverage": {
        "frequency_source": prov["frequency_table"],
        "frequency_source_field": "allele_frequencies",
        "n_alleles_in_frequency_table": len(AF),
        "loci_in_frequency_table": sorted({a.split("*")[0].replace("HLA-", "") for a in AF}),
        "HLA_C_frequencies_present_anywhere_local": c_freq_present,
        "upstream": freqd["_sources"],
        "model": "carrier = 1-(1-af)^2 (Hardy-Weinberg, >=1 copy); "
                 "coverage of a set = 1-prod(1-af)^2. This is the manuscript's own formula, "
                 "and the manuscript itself (§2.3) records it as an UNJUSTIFIED approximation: "
                 "the product runs over same-locus alleles that are not independent draws, and "
                 "A/B linkage disequilibrium is not modelled.",
        "⚠_intervals": "Wilson 95% CIs exist in the upstream artifacts but the manuscript's "
                       "§2.3 withdraws them (a single-urn binomial refuted by its own "
                       "between-population spread). None is quoted here.",
        "blocks": blocks,
        "re_derivation_of_committed_headline_numbers": redev,
    },

    "d_expanded_scan_code_vs_artifact": expanded,
}

json.dump(out, open(os.path.join(HERE, "panel-coverage.json"), "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------------------------ report
P = print
P("(a) PANEL, verbatim from %s" % prov["screen"]["path"])
P("    %s %s / models %s, lengths %s" % (out["a_panel"]["tool"], out["a_panel"]["version"],
                                         out["a_panel"]["models_release"], out["a_panel"]["peptide_lengths"]))
for a in PANEL: P("      " + a)
P("    n = %d ; loci = %s ; HLA-C in panel = %d" % (len(PANEL), panel_loci, out["a_panel"]["n_HLA_C_in_panel"]))

P("\n(b) VALIDATED EPITOPE-ALLELE PAIRS")
P("    validated epitopes re-derived here: %d" % len(VALIDATED))
P("    distinct two-field allotypes: %d  %s" % (len(allotypes), allotypes))
P("    two-field epitope-allele pairs: %d" % len(pairs_two))
P("    in panel      : %d  %s" % (len(in_panel), sorted({norm(a) for _, a in in_panel})))
P("    OUT of panel  : %d  %s" % (len(out_panel), sorted({norm(a) for _, a in out_panel})))
P("    fraction the screen was structurally unable to return: %d/%d = %.4f"
  % (len(out_panel), len(pairs_two), len(out_panel) / len(pairs_two)))
P("    HLA-C pairs   : %d across %d epitopes  %s"
  % (len(c_pairs), len({i for i, _ in c_pairs}), [f"{i}:{norm(a)}" for i, a in c_pairs]))
P("    one-field-only restrictions NOT counted as two-field pairs: %s" % low_hits)

P("\n(c) POPULATION COVERAGE  (frequency source: %s, sha256 %s)"
  % (prov["frequency_table"]["path"], prov["frequency_table"]["sha256"]))
P("    table holds %d alleles at loci %s ; HLA-C frequencies present locally: %s"
  % (len(AF), out["c_population_coverage"]["loci_in_frequency_table"],
     c_freq_present if c_freq_present else "NONE"))
P("    cross-check against hla-coverage.json on shared alleles:")
for a, v in xcheck.items():
    P("      %-14s identical=%s" % (a, v["identical"]))
for b in blocks:
    P("    -- %s" % b["label"])
    P("       requested %d; frequency known for %d; UNKNOWN for %d %s"
      % (b["n_requested"], b["n_with_frequency"], b["n_unknown"],
         b["alleles_without_local_frequency_UNKNOWN"] or ""))
    P("       independence-model coverage = %s  (%s)"
      % (b["independence_model_coverage_over_known_alleles"],
         "EXACT under the model" if b["is_exact"] else "LOWER BOUND"))
    d = b["distribution_free_bounds_over_known_alleles"]
    P("       distribution-free bounds  = [%s, %s]"
      % (d["lower_max_single_carrier"], d["upper_min_1_sum_carrier"]))
P("    re-derivation of committed headline numbers:")
for r in redev:
    P("      %-36s committed %.4f  re-derived %.4f  reproduces=%s"
      % (r["committed_field"], r["committed_value"], r["re_derived_here"], r["reproduces_to_4dp"]))

P("\n(d) EXPANDED SCAN — producer code vs committed artifact")
P("    producer coverage_scan.py PANEL = %d A/B + %d C = %d"
  % (expanded["producer_PANEL_AB_n"], expanded["producer_PANEL_C_n"], expanded["producer_PANEL_total_n"]))
P("    committed epitope-allele-matrix.json panel = %d, loci %s"
  % (expanded["committed_artifact_panel_n"], expanded["committed_artifact_loci"]))
P("    committed coverage-curve.json panel_size  = %d" % expanded["committed_curve_panel_size"])
P("    artifact matches producer: %s" % expanded["artifact_matches_producer"])

xall = all(v["identical"] for v in xcheck.values())
assert xall, "frequency sources disagree — see cross-check"
P("\nOK  cross-check passed; artifact written to panel-coverage.json")
