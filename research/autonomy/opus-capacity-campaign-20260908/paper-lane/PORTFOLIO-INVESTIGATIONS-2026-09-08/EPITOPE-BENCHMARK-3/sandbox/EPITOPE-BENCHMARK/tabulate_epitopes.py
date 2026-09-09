#!/usr/bin/env python3
"""EPITOPE-BENCHMARK: derive countable strata from epitope-records.json.

Prediction is not validation. Every count below states its inclusion rule.
No network. No IEDB. Sources are PubMed/PMC records retrieved this session.
"""
import json, math, sys, re

REC = json.load(open("epitope-records.json"))
rows = REC["records"]

def has(r, g):     return g in r["evidence"]
def measured(r):   return any(has(r, g) for g in ("MS_ELUTION", "TCELL", "MULTIMER"))
def seq_known(r):  return bool(re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", r["peptide"]))
def classI_window(r):
    return r["len"] is not None and 8 <= r["len"] <= 11
def classI_restricted(r):
    return bool(re.search(r"HLA-[ABC]\*?\d", r["hla"] or ""))
def natural(r):
    return "ANCHOR-MODIFIED" not in r["fusion"] and "heteroclitic" not in r["peptide"]

S = {}
S["all_records"]              = rows
S["spans_junction_yes"]       = [r for r in rows if r["spans_junction"] == "yes"]
S["spans_junction_no"]        = [r for r in rows if r["spans_junction"] == "no"]
S["prediction_only"]          = [r for r in rows if r["evidence"] == ["PREDICTION"]]
S["binding_only"]             = [r for r in rows if set(r["evidence"]) <= {"BINDING", "PREDICTION"}
                                                  and "BINDING" in r["evidence"]]
S["measured_any"]             = [r for r in rows if measured(r)]
S["measured_and_spans"]       = [r for r in S["measured_any"] if r["spans_junction"] == "yes"]
S["measured_spans_natural"]   = [r for r in S["measured_and_spans"] if natural(r)]
S["BENCHMARK_ELIGIBLE"]       = [r for r in S["measured_spans_natural"]
                                 if seq_known(r) and classI_window(r) and classI_restricted(r)]
S["ms_eluted_junction"]       = [r for r in S["measured_spans_natural"] if has(r, "MS_ELUTION")]
S["ms_eluted_ci_eligible"]    = [r for r in S["BENCHMARK_ELIGIBLE"] if has(r, "MS_ELUTION")]
S["measured_seq_unresolved"]  = [r for r in S["measured_spans_natural"] if not seq_known(r)]
S["classII_or_outside_window"]= [r for r in S["measured_spans_natural"]
                                 if seq_known(r) and not (classI_window(r) and classI_restricted(r))]

# ---- sufficiency arithmetic, reproducing PUB-VACCINE-PATH's criterion -----------
def wilson_width(p, n, z=1.959963984540054):
    d = 1 + z*z/n
    half = (z/d)*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return 2*half

def n_for_width(p, target=0.20):
    # 2026-09-09 (EPITOPE-BENCHMARK-3): successes convention corrected to k = round(p*n).
    # SUPERSEDED VALUE, PRESERVED: this function previously fed the CONTINUOUS sensitivity p
    # straight into wilson_width (phat := p, no integer success count ever formed). That
    # "p-exact" convention is reproducible and internally coherent -- it yields 93 / 78 / 60 / 37 --
    # and 37 is where the retired pin came from. It was NOT a typo and NOT k=floor (k=floor
    # gives 38). It was retired because a sensitivity is estimated from an integer count of
    # successes out of n, so phat must be attainable at that n; at n = 37 the attainable
    # k = round(0.9*37) = 33 gives width 0.204233 > 0.20, i.e. the p-exact requirement is not
    # met by any real sample of that size. See PARENT-ADJUDICATION-34-vs-37.md.
    # k = round and k = ceil both give 34; k = floor gives 38. Rows 0.5 / 0.7 / 0.8 are
    # UNCHANGED at 93 / 78 / 60 under the corrected convention.
    n = 1
    while n < 100000:
        k = int(round(p * n))
        if wilson_width(k / n, n) <= target:
            return n
        n += 1
    return None

REQ = {p: n_for_width(p) for p in (0.5, 0.7, 0.8, 0.9)}
PREREG_FLOOR = 30

n_bench = len(S["BENCHMARK_ELIGIBLE"])
n_ms    = len(S["ms_eluted_ci_eligible"])

# per-allele depth: how many benchmark-eligible epitopes per HLA allotype
alleles = {}
for r in S["BENCHMARK_ELIGIBLE"]:
    for a in re.findall(r"HLA-[ABC]\*\d{2}:\d{2}", r["hla"]):
        alleles.setdefault(a, []).append(r["peptide"])

fusions = sorted({r["fusion"].split(" (")[0] for r in S["BENCHMARK_ELIGIBLE"]})

out = {
  "_id": "ARTIFACT-EPITOPE-BENCHMARK-COUNTS",
  "_derived_from": "epitope-records.json",
  "strata": {k: {"n": len(v), "ids": [r["id"] for r in v]} for k, v in S.items()},
  "benchmark_eligible_detail": [
      {"id": r["id"], "fusion": r["fusion"], "peptide": r["peptide"], "hla": r["hla"],
       "evidence": r["evidence"], "material": r["material"], "pmid": r["pmid"]}
      for r in S["BENCHMARK_ELIGIBLE"]],
  "distinct_fusions_in_benchmark": fusions,
  "per_allele_depth": {a: {"n": len(v), "peptides": v} for a, v in sorted(alleles.items())},
  "sufficiency": {
      "criterion": "PUB-VACCINE-PATH: 95% CI width <= 0.20 on sensitivity at the cut (Wilson)",
      "n_required": REQ,
      "preregistered_floor": PREREG_FLOOR,
      "n_available_benchmark_eligible": n_bench,
      "n_available_ms_eluted_only": n_ms,
      "shortfall_vs_sens_0.5": REQ[0.5] - n_bench,
      "shortfall_vs_sens_0.8": REQ[0.8] - n_bench,
      "shortfall_vs_prereg_floor": PREREG_FLOOR - n_bench,
      "achieved_ci_width_at_sens_0.5_with_n_available": round(wilson_width(0.5, n_bench), 4),
      "verdict": ("INSUFFICIENT" if n_bench < REQ[0.8] else "SUFFICIENT")
  },
  "quantitative_observations": REC["quantitative_observations"],
}
json.dump(out, open("validated-epitope-counts.json", "w"), indent=2)

# ---- console report -------------------------------------------------------------
w = sys.stdout.write
w("EPITOPE-BENCHMARK  -- counts derived from epitope-records.json\n")
w("=" * 78 + "\n")
for k in ("all_records","spans_junction_yes","spans_junction_no","prediction_only",
          "binding_only","measured_any","measured_and_spans","measured_spans_natural",
          "measured_seq_unresolved","classII_or_outside_window",
          "BENCHMARK_ELIGIBLE","ms_eluted_junction","ms_eluted_ci_eligible"):
    w("%-30s %3d   %s\n" % (k, len(S[k]), ",".join(r["id"] for r in S[k])))
w("-" * 78 + "\n")
w("BENCHMARK-ELIGIBLE epitopes (natural sequence, spans junction, 8-11mer,\n")
w("class I allotype named, at least one immunological measurement):\n")
for r in S["BENCHMARK_ELIGIBLE"]:
    w("  %-4s %-13s %-24s %-30s %s\n" % (r["id"], r["peptide"], r["hla"][:24],
                                         r["fusion"][:30], "+".join(r["evidence"])))
w("-" * 78 + "\n")
w("distinct fusions represented: %d  -> %s\n" % (len(fusions), "; ".join(fusions)))
w("per-allele depth: %s\n" % {a: len(v) for a, v in sorted(alleles.items())})
w("-" * 78 + "\n")
w("SUFFICIENCY (Wilson, 95%% CI width <= 0.20 on sensitivity)\n")
for p, n in REQ.items():
    w("  true sensitivity %.1f  requires n = %3d   have %d   shortfall %d\n"
      % (p, n, n_bench, n - n_bench))
w("  preregistered floor n>=30: have %d, shortfall %d\n" % (n_bench, PREREG_FLOOR - n_bench))
w("  CI width actually achievable at sens 0.5 with n=%d : %.3f (target <= 0.200)\n"
  % (n_bench, wilson_width(0.5, n_bench)))
w("  MS-ELUTED subset only (true 'presentation' ground truth): n = %d\n" % n_ms)
w("  VERDICT: %s\n" % out["sufficiency"]["verdict"])
