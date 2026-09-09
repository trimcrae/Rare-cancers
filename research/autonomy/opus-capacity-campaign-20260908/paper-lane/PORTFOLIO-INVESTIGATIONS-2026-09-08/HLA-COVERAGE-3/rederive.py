#!/usr/bin/env python3
"""HLA-COVERAGE-3 step 1: independent re-derivation of HLA-COVERAGE-2's three key facts.

Offline, read-only. Does NOT import or run any producer under research/modalities/.
Route B8 (HLA-C) is closed: no HLA-C frequency is fetched, substituted or invented anywhere.
"""
import ast, hashlib, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
MOD = os.path.join(ROOT, "research", "modalities")

def sha(p):
    b = open(p, "rb").read()
    return len(b), hashlib.sha256(b).hexdigest()

def load(p):
    return json.load(open(p))

out = {"_lane": "HLA-COVERAGE-3", "_what": "independent re-derivation of HLA-COVERAGE-2 key facts",
       "_provenance": {}, "facts": {}}

paths = {
    "breakpoints": os.path.join(MOD, "fusion-breakpoint-neoantigens.json"),
    "coverage_scan_py": os.path.join(MOD, "coverage_scan.py"),
    "strict_matrix": os.path.join(MOD, "epitope-allele-matrix.json"),
    "loose_matrix": os.path.join(MOD, "epitope-allele-loose-matrix.json"),
    "coverage_curve": os.path.join(MOD, "coverage-curve.json"),
    "threshold_curve": os.path.join(MOD, "coverage-threshold-curve.json"),
    "hla_coverage": os.path.join(MOD, "hla-coverage.json"),
}
for k, p in paths.items():
    n, h = sha(p)
    out["_provenance"][k] = {"path": os.path.relpath(p, ROOT), "bytes": n, "sha256": h}

# ---- FACT 1: the 10-allele MHCflurry panel, verbatim -------------------------------
bp = load(paths["breakpoints"])
pred = bp.get("_predictor", {})
panel10 = pred.get("alleles")
out["facts"]["predictor_panel"] = {
    "field": "_predictor.alleles",
    "alleles": panel10,
    "n": len(panel10) if panel10 else None,
    "loci": sorted({a.split("*")[0].replace("HLA-", "") for a in (panel10 or [])}),
    "n_HLA_C": sum(1 for a in (panel10 or []) if a.startswith("HLA-C")),
    "predictor_meta": {k: v for k, v in pred.items() if k != "alleles"},
}

# ---- FACT 2: the 34-vs-52 divergence -----------------------------------------------
# Parse coverage_scan.py's module-level PANEL_AB / PANEL_C WITHOUT importing or running it.
src = open(paths["coverage_scan_py"]).read()
tree = ast.parse(src)
consts = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        if name in ("PANEL_AB", "PANEL_C"):
            consts[name] = [ast.literal_eval(e) for e in node.value.elts]
producer_panel = consts.get("PANEL_AB", []) + consts.get("PANEL_C", [])
strict = load(paths["strict_matrix"])
loose = load(paths["loose_matrix"])
curve = load(paths["coverage_curve"])
out["facts"]["panel_divergence"] = {
    "producer": {"PANEL_AB": len(consts.get("PANEL_AB", [])), "PANEL_C": len(consts.get("PANEL_C", [])),
                 "PANEL_total": len(producer_panel),
                 "loci": sorted({a.split("*")[0].replace("HLA-", "") for a in producer_panel})},
    "artifacts": {
        "epitope-allele-matrix.json:panel": {
            "n": len(strict["panel"]),
            "loci": sorted({a.split("*")[0].replace("HLA-", "") for a in strict["panel"]}),
            "has_alleles_without_a_model": "alleles_without_a_model" in strict},
        "epitope-allele-loose-matrix.json:panel": {
            "n": len(loose["panel"]),
            "loci": sorted({a.split("*")[0].replace("HLA-", "") for a in loose["panel"]})},
        "coverage-curve.json:panel_size": curve["panel_size"],
    },
    "producer_AB_equals_committed_panel": consts.get("PANEL_AB") == strict["panel"],
    "loose_panel_equals_strict_panel": loose["panel"] == strict["panel"],
    "divergence": len(producer_panel) - len(strict["panel"]),
}

# ---- FACT 3: the two committed headline coverage numbers ---------------------------
# Independent implementation of the paper's formula: coverage = 1 - prod (1-af)^2
def cov(afs):
    prod = 1.0
    for af in afs:
        prod *= (1.0 - af) ** 2
    return round(1.0 - prod, 4)

hcv = load(paths["hla_coverage"])
g = hcv["global"]
freqs = g["allele_frequencies"]

# Rebuild the two allele SETS from the underlying breakpoint records, not from hla-coverage.json.
e7e3, all_strong = set(), set()
for jn in bp.get("junctions", []):
    is_e7e3 = (jn.get("EWSR1_exon_end") == 7 and jn.get("NR4A3_exon_start") == 3)
    for b in jn.get("binders", []):
        if b.get("class") == "strong":
            all_strong.add(b["allele"])
            if is_e7e3:
                e7e3.add(b["allele"])

def block(name, alleles, committed_key):
    als = sorted(alleles)
    missing = [a for a in als if a not in freqs or freqs[a].get("allele_frequency") is None]
    used = [a for a in als if a not in missing]
    rede = cov([freqs[a]["allele_frequency"] for a in used])
    committed = g[committed_key]
    return {"alleles_rebuilt_from_breakpoints": als,
            "alleles_committed": g.get(name),
            "allele_set_matches_committed": als == g.get(name),
            "af_used": {a: freqs[a]["allele_frequency"] for a in used},
            "alleles_with_UNKNOWN_frequency": missing,
            "committed": committed, "re_derived": rede,
            "reproduces": committed == rede}

out["facts"]["headline_numbers"] = {
    "coverage_e7e3_public": block("e7e3_public_epitope_alleles", e7e3, "coverage_e7e3_public"),
    "coverage_any_strong_binder_allele": block("all_strong_binder_alleles", all_strong,
                                               "coverage_any_strong_binder_allele"),
    "_note": ("These two figures are produced by hla_coverage.py from the breakpoint records' "
              "own binder list. They are NOT downstream of coverage_scan.py's PANEL."),
}

ok = (out["facts"]["predictor_panel"]["n"] == 10
      and out["facts"]["predictor_panel"]["n_HLA_C"] == 0
      and out["facts"]["panel_divergence"]["producer"]["PANEL_total"] == 52
      and out["facts"]["panel_divergence"]["artifacts"]["epitope-allele-matrix.json:panel"]["n"] == 34
      and out["facts"]["headline_numbers"]["coverage_e7e3_public"]["reproduces"]
      and out["facts"]["headline_numbers"]["coverage_any_strong_binder_allele"]["reproduces"])
out["all_three_facts_reproduce"] = ok
print(json.dumps(out, indent=2))
sys.exit(0 if ok else 3)
