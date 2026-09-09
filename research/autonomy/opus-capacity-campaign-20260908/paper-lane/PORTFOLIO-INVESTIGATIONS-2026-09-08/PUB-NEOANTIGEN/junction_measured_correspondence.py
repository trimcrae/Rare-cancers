#!/usr/bin/env python3
"""
EXACT-CORRESPONDENCE AND FALSE-MATCH-CONTROL TEST of the EWSR1::NR4A3 junction
peptide set against the MEASURED epitope records this repository already holds.

Question: does any MEASURED peptide record correspond to a junction peptide, at
exact sequence correspondence, and would such a correspondence be attributable to
the fusion rather than to a false match?

Inputs (both already committed; nothing is fetched):
  research/modalities/fusion-breakpoint-neoantigens.json  -> the 5 in-frame junctions'
      novel_peptides (the 174-peptide set) and the 11 predicted binders.
  research/modalities/iedb-validated-epitope-cache.json   -> the normalised IEDB records
      (arm F "fusion" + arm N general), positive-outcome only, 8-11mers, 4-digit HLA.

Tests
  T1 exact correspondence: junction peptide == measured peptide.
  T2 substring correspondence either way (a measured 8-11mer inside a junction peptide
     or vice versa), which an eluate could produce by trimming.
  T3 isobaric false-match control: I and L are indistinguishable by ordinary MS/MS, so
     correspondence is recomputed with I and L collapsed to a single symbol. A hit here
     that is not a hit in T1 is a sequence a spectrum could not separate.
  T4 provenance control on arm F: the inclusion rule is a NAME pattern over source
     antigen text, so records whose antigen is a viral/other protein merely NAMED
     "fusion" are counted separately from human gene-fusion oncoproteins.
  T5 assay-kind resolution: whether the cached records can distinguish MEASURED
     PRESENTATION (eluted-ligand mass spectrometry) from measured BINDING or T-cell
     reactivity at all.

⛔ WHAT A RESULT HERE IS NOT. A miss is not evidence that the junction peptide is absent
from any tumour: it is evidence about what these records contain. A hit would not be
proof of presentation either, because the cached records do not carry the assay method
(T5). Predicted binding remains a prediction throughout; nothing here converts one.
"""
import json, re, sys, datetime

ROOT = "research/modalities/"
NEO = json.load(open(ROOT + "fusion-breakpoint-neoantigens.json"))
IEDB = json.load(open(ROOT + "iedb-validated-epitope-cache.json"))

junction_peptides = {}          # peptide -> set of junction labels
for j in NEO["junctions"]:
    for p in j["novel_peptides"]:
        junction_peptides.setdefault(p, set()).add(j["junction_label"])
binders = {b["peptide"] for b in NEO["predicted_binders_ranked"]}
assert binders <= set(junction_peptides), "a ranked binder is not in the novel set"

measured = []
for arm in ("arm_F_records", "arm_N_records"):
    for r in IEDB[arm]:
        measured.append({"arm": arm[4], "peptide": r["peptide"], "allele": r["allele"],
                         "antigens": r["source_antigens"], "tables": r["tables"]})

def collapse(s):  # I/L isobaric collapse
    return s.replace("I", "J").replace("L", "J")

mset = {m["peptide"] for m in measured}
mcol = {}
for m in measured:
    mcol.setdefault(collapse(m["peptide"]), []).append(m)

t1 = sorted(p for p in junction_peptides if p in mset)
t2 = []
for p in junction_peptides:
    for q in mset:
        if p != q and (p in q or q in p):
            t2.append({"junction_peptide": p, "measured_peptide": q})
t3 = []
for p in junction_peptides:
    c = collapse(p)
    if c in mcol and p not in mset:
        t3.append({"junction_peptide": p,
                   "isobaric_measured": sorted({m["peptide"] for m in mcol[c]})})

# T4 provenance control on arm F source-antigen names
HUMAN_GENE_FUSION = re.compile(
    r"BCR|ABL|EWSR1|EWS-|NR4A3|TAF15|SS18|SYT-SSX|SSX|PML|RARA|ETV6|RUNX1|KMT2A|MLL|"
    r"NPM1|ALK|TMPRSS2|ERG|FLI1|DNAJB1|PRKACA|CBFB|MYH11|PAX3|FOXO1|NUP98|CIC|DUX4|"
    r"BRD4|NUT|FGFR|RET|NTRK|EML4|WT1|ATF1|CREB|TFE3|MYB|NFIB", re.I)
VIRAL_OR_NAME_ONLY = re.compile(r"fusion (glyco)?protein|entry-fusion|membrane fusion|"
                                r"fusion complex|virus|viral|OPG|gag|env|nucleoprotein", re.I)
armF = [m for m in measured if m["arm"] == "F"]
buckets = {"human_gene_fusion_named": [], "fusion_word_only_or_viral": [], "unclassified": []}
antigen_index = {}
for m in armF:
    txt = " ; ".join(m["antigens"])
    antigen_index.setdefault(txt, 0)
    antigen_index[txt] += 1
    if HUMAN_GENE_FUSION.search(txt):
        buckets["human_gene_fusion_named"].append(m)
    elif VIRAL_OR_NAME_ONLY.search(txt):
        buckets["fusion_word_only_or_viral"].append(m)
    else:
        buckets["unclassified"].append(m)

# T5 assay-kind resolution
tables_present = sorted({t for m in measured for t in m["tables"]})

out = {
  "_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "_cost": "$0 - CPU only, no network, no GPU, no paid API. Both inputs already committed.",
  "_question": "Does any MEASURED epitope record in this repository correspond to an "
               "EWSR1::NR4A3 junction peptide, at exact correspondence, and could such a "
               "correspondence be attributed to the fusion rather than to a false match?",
  "⛔_what_this_is_not": "Predicted binding is a prediction throughout. A miss is a statement "
               "about these records, not about any tumour. A hit would not establish "
               "presentation, because the cached records do not carry the assay method.",
  "_inputs": {
     "junction_artifact": {"file": "research/modalities/fusion-breakpoint-neoantigens.json",
                           "utc": NEO.get("_utc"), "n_junctions": NEO["n_inframe_junctions"]},
     "measured_records": {"file": "research/modalities/iedb-validated-epitope-cache.json",
                          "utc": IEDB.get("_utc"),
                          "n_arm_F": len(IEDB["arm_F_records"]),
                          "n_arm_N": len(IEDB["arm_N_records"]),
                          "filters_already_applied": "positive assay outcome only; lengths 8-11; "
                                                     "4-digit HLA-A/B/C restriction"}},
  "n_junction_peptides": len(junction_peptides),
  "n_predicted_binders": len(binders),
  "n_distinct_measured_peptides": len(mset),
  "T1_exact_correspondence": {"n": len(t1), "hits": t1},
  "T2_substring_correspondence": {"n": len(t2), "hits": t2},
  "T3_isobaric_IL_false_match_control": {"n": len(t3), "hits": t3,
     "note": "MS/MS does not separate Leu from Ile; a hit here is a sequence a spectrum could not separate."},
  "T4_armF_provenance_control": {
     "n_armF_records": len(armF),
     "n_human_gene_fusion_named": len(buckets["human_gene_fusion_named"]),
     "n_fusion_word_only_or_viral": len(buckets["fusion_word_only_or_viral"]),
     "n_unclassified": len(buckets["unclassified"]),
     "distinct_source_antigen_strings": len(antigen_index),
     "human_gene_fusion_antigens": sorted({" ; ".join(m["antigens"])
                                           for m in buckets["human_gene_fusion_named"]}),
     "armF_source_antigen_census": [{"antigen": k, "n_records": v}
                                    for k, v in sorted(antigen_index.items(),
                                                       key=lambda kv: -kv[1])],
     "note": "arm F membership is a NAME pattern over source-antigen text, so a record can enter "
             "arm F without being a gene-fusion junction epitope. This split is the false-match "
             "control on that rule."},
  "T5_assay_kind_resolution": {
     "tables_present": tables_present,
     "eluted_ligand_mass_spec_distinguishable": False,
     "why": "The cache retains only which IEDB table a record came from (mhc_search = MHC-ligand "
            "assays, tcell_search = T-cell assays) and the qualitative outcome. mhc_search mixes "
            "eluted-ligand mass spectrometry with in-vitro binding assays, so measured PRESENTATION "
            "cannot be separated from measured BINDING in these records. Resolving it requires an "
            "IEDB re-fetch carrying the assay-method columns."},
  "_ewsr1_nr4a3_taf15_in_measured_records": sorted({" ; ".join(m["antigens"]) for m in measured
        if re.search(r"EWSR1|EWS |NR4A3|NOR-1|TAF15", " ; ".join(m["antigens"]), re.I)}),
}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps({k: v for k, v in out.items()
                  if k.startswith(("T1", "T2", "T3", "T4", "T5", "n_", "_ewsr1"))}, indent=1)[:4000])
