#!/usr/bin/env python3
"""VACCINE-PATH-2 — admissibility audit of the exemplars manuscript section B1 offers as
class I threshold-calibration material.

Question: B1 says the experimentally validated fusion-junction epitopes available to calibrate a
class I presentation-percentile cut are "the HLA-A*24:02-restricted SYT-SSX junction peptide
[17,18], the four EWSR1::FLI1 breakpoint peptides of the Ewing sarcoma case report [20] and the
fusion neoantigens of a head and neck series [21]". How many of those are admissible into a class I
presentation-percentile benchmark AT ALL?

Admissibility rule (fixed BEFORE the sources were read, and identical in substance to the rule
EPITOPE-BENCHMARK used): a record is admissible iff it is (a) a natural, non-anchor-modified
sequence, (b) spans the fusion junction, (c) of length 8-11 inclusive -- the length window the
screen's own predictor is configured for -- (d) carries a named class I allotype, and (e) carries at
least one class I immunological measurement (MS elution, class I-restricted T-cell reactivity, or
multimer).

NO claim about immunogenicity, presentation, tolerance, efficacy, safety, selectivity, therapeutic
window or clinical readiness is made or implied. Admissibility is a property of a RECORD's fit to a
benchmark's inclusion rule, nothing else. A prediction is not a presented epitope.
"""
import hashlib, json, math, os, re

ROOT = "/home/user/Rare-cancers"
SCREEN = os.path.join(ROOT, "research/modalities/fusion-breakpoint-neoantigens.json")
CENSUS = os.path.join(ROOT, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                            "PORTFOLIO-INVESTIGATIONS-2026-09-08/EPITOPE-BENCHMARK/epitope-records.json")

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

# ---- 1. re-derive the predictor's own length window and allele panel, from the artifact ----
screen = json.load(open(SCREEN))
pred = screen.get("_predictor", {})
panel = list(pred.get("alleles", []))
lengths = pred.get("lengths") or pred.get("peptide_lengths")
predictor_block = {
    "path": os.path.relpath(SCREEN, ROOT),
    "sha256": sha256(SCREEN),
    "predictor": {k: v for k, v in pred.items() if k != "alleles"},
    "alleles": panel,
    "n_alleles": len(panel),
    "loci": sorted({a.split("*")[0].replace("HLA-", "") for a in panel}),
    "length_window_raw": lengths,
}

# ---- 2. the B1 exemplars, each scored against the rule, from its own cited source ----
E = [
 {"b1_clause": "the HLA-A*24:02-restricted SYT-SSX junction peptide [17,18]",
  "manuscript_refs": ["17 (PMID 15647119)", "18 (PMID 22726592)"],
  "item": "GYDQIMPKK (SYT-SSX 'B peptide')",
  "n_items": 1,
  "natural": True, "spans_junction": True, "length": 9,
  "class_I_allotype": "HLA-A*24:02",
  "class_I_measurement": "CTL induced from patient PBL; A24 tetramer; class I-restricted lysis of "
                         "HLA-A24+ SYT-SSX+ synovial sarcoma cells (census record E25)",
  "source_evidence": "PMID 15647119 abstract names the sequence verbatim: \"A 9-mer peptide "
                     "(SYT-SSX B: GYDQIMPKK) spanning the SYT-SSX fusion region\"; eligibility "
                     "required HLA-A*2402 positivity.",
  "admissible_items": 1},
 {"b1_clause": "the four EWSR1::FLI1 breakpoint peptides of the Ewing sarcoma case report [20]",
  "manuscript_refs": ["20 (PMID 42570981)"],
  "item": "E1-E4, four overlapping 17-mers spanning the type 1 EWSR1-FLI1 breakpoint",
  "n_items": 4,
  "natural": True, "spans_junction": True, "length": 17,
  "class_I_allotype": None,
  "class_I_measurement": None,
  "source_evidence": "PMC13452805 Methods: \"four overlapping 17-mer peptides ... To ensure broad "
                     "applicability, the vaccine was designed without HLA restriction\"; immune "
                     "monitoring \"detects ... T-cells in an HLA-independent manner\"; Results: "
                     "polyfunctional CD4+ responses to all four; Discussion attributes the absence "
                     "of CD8+ reactivity to \"the class II binding properties of the selected "
                     "peptides\".",
  "fails": ["length 17 is outside the 8-11 window the screen's predictor is configured for",
            "no class I allotype: the construct is deliberately HLA-unrestricted",
            "no class I measurement: the reported responses are CD4+ and the assay is "
            "HLA-independent by design"],
  "admissible_items": 0},
 {"b1_clause": "the fusion neoantigens of a head and neck series [21]",
  "manuscript_refs": ["21 (PMID 31011208)"],
  "item": "QFIDSSWYL (MYB::NFIB), MMYSPICLTQT (MYBL1::NFIB), SLASPLQPT (NFIB::MYB), "
          "DKESEEEVS (DEK::AFF2)  [+ SLASPLQSWYL, binding-only, excluded]",
  "n_items": 5,
  "natural": True, "spans_junction": True, "length": "9-11",
  "class_I_allotype": "HLA-A*02:01 (x3); DEK::AFF2 record carries class I C-locus restrictions",
  "class_I_measurement": "T2 stabilisation + class I-restricted T-cell IFN-g/multimer "
                         "(census records E14, E15, E16, E18); E17 is binding-only and excluded",
  "source_evidence": "PMID 31011208 / doi 10.1038/s41591-019-0434-2 (census records E14-E18).",
  "admissible_items": 4},
]
b1_named = sum(e["n_items"] for e in E)
b1_admissible = sum(e["admissible_items"] for e in E)

# ---- 3. re-derive the full census count independently (do not trust a reported digit) ----
cen = json.load(open(CENSUS))
def adm(r):
    if r.get("spans_junction") != "yes":
        return False
    if "ANCHOR-MODIFIED" in (r.get("fusion") or "") or "NOT A NATURAL" in (r.get("junction_note") or ""):
        return False
    L = r.get("len")
    if not isinstance(L, int) or not (8 <= L <= 11):
        return False
    pep = (r.get("peptide") or "")
    if "NOT RETRIEVED" in pep or not re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", pep.strip().split(" ")[0] or "-"):
        return False   # the rule needs an actual sequence; E29/E30 report a measurement without one
    hla = (r.get("hla") or "").strip()
    if not hla or hla.lower() == "none":
        return False
    ev = set(r.get("evidence") or [])
    return bool(ev & {"TCELL", "MULTIMER", "MS", "ELUTION", "MS_ELUTION"})
census_adm = [r["id"] for r in cen["records"] if adm(r)]

# ---- 4. sample size arithmetic, recomputed here, not imported ----
def wilson_width(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 2 * hw
def n_for_width(sens, target=0.20, rule=round, nmax=5000):
    # k = round(sens*n) is the convention the parent arbitration settled on (k=round and k=ceil both
    # give 34 at sensitivity 0.9; k=floor gives 38). All three families are reported, not just one.
    for n in range(2, nmax):
        if wilson_width(rule(sens * n), n) <= target:
            return n
    return None
sizes = {name: {str(s): n_for_width(s, rule=rule) for s in (0.5, 0.7, 0.8, 0.9)}
         for name, rule in (("k=round", round), ("k=ceil", math.ceil), ("k=floor", math.floor))}
widths = {str(n): round(wilson_width(round(0.5 * n), n), 4) for n in (5, 15, 30)}

out = {
 "_id": "DOC-VACCINE-PATH-2-B1-EXEMPLAR-ADMISSIBILITY",
 "_lane": "VACCINE-PATH-2",
 "_utc_date": "2026-09-09",
 "_route": "offline arithmetic over committed artifacts + PubMed/PMC MCP for the manuscript's own citations",
 "_no_claim": ("No immunogenicity, presentation, tolerance, efficacy, safety, selectivity, "
               "therapeutic-window or clinical-readiness claim is made or implied. Admissibility is "
               "a record's fit to a benchmark inclusion rule and nothing more."),
 "predictor_configuration": predictor_block,
 "admissibility_rule": ["natural (not anchor-modified)", "spans the fusion junction",
                        "length 8-11 (the predictor's configured window)",
                        "a named class I allotype", "at least one class I measurement"],
 "b1_exemplars": E,
 "b1_named_items": b1_named,
 "b1_admissible_items": b1_admissible,
 "b1_inadmissible_items": b1_named - b1_admissible,
 "census_admissible_ids": census_adm,
 "census_admissible_n": len(census_adm),
 "wilson_n_for_ci_width_0.20": sizes,
 "wilson_reproduction_note": ("k=round reproduces PUB-VACCINE-PATH digit for digit: 93/78/60/34, "
   "and 34 (not 37) at sensitivity 0.9 under both k=round and k=ceil, 38 under k=floor -- "
   "matching the parent arbitration. A first attempt in this lane (checks/04) added an extra "
   "'sens*n must be an integer' filter of its own and returned 94/80/60/40; that filter was this "
   "lane's defect, is recorded rather than discarded, and is removed here."),
 "wilson_achievable_width_at_sensitivity_0.5": widths,
}
print(json.dumps(out, indent=2))
with open("b1-exemplar-admissibility.json", "w") as f:
    json.dump(out, f, indent=2)
    f.write("\n")
