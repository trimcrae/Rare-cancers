#!/usr/bin/env python3
"""NEOANTIGEN-3: correspondence and characterisation of this repository's predicted
EWSR1::NR4A3 junction peptides against the n=15 curated set of EXPERIMENTALLY VALIDATED
cancer fusion-JUNCTION class I epitopes assembled by the EPITOPE-BENCHMARK lane.

Offline. Reads two committed/lane-local inputs read-only; writes only into this lane.

  A. exact / substring / isobaric(I=L) correspondence, reported separately.
  B. characterisation of the validated set vs. this repo's predicted set:
     length, allele, breakpoint position within the peptide, residues per partner.

WHAT THIS IS NOT
  Prediction is not presentation. A validated epitope for BCR::ABL1 says nothing about
  EWSR1::NR4A3. Nine fusion oncoproteins are not a sample of fusions, so a distributional
  difference is a statement about the PREDICTION SET, never about whether any EMC peptide
  is presentable. No clinical claim. No manuscript is edited by this script.
"""
import json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
FUSION = os.path.join(ROOT, "research/modalities/fusion-breakpoint-neoantigens.json")
BENCH = os.path.join(HERE, "..", "EPITOPE-BENCHMARK", "epitope-records.json")

AA = "ACDEFGHIKLMNPQRSTVWY"
AAre = re.compile(r"^[%s]+$" % AA)

# ---------------------------------------------------------------- inputs
fus = json.load(open(FUSION))
rec = json.load(open(BENCH))["records"]

# ------------------------------------------------- EPITOPE-BENCHMARK inclusion rule
# Reproduced verbatim from EPITOPE-BENCHMARK/tabulate_epitopes.py so the reference set
# used here is the same n=15 that lane reported, derived by the same code path.
def has(r, g):    return g in r["evidence"]
def measured(r):  return any(has(r, g) for g in ("MS_ELUTION", "TCELL", "MULTIMER"))
def seq_known(r): return bool(re.fullmatch(r"[%s]+" % AA, r["peptide"]))
def classI_window(r):     return r["len"] is not None and 8 <= r["len"] <= 11
def classI_restricted(r): return bool(re.search(r"HLA-[ABC]\*?\d", r["hla"] or ""))
def natural(r):   return "ANCHOR-MODIFIED" not in r["fusion"] and "heteroclitic" not in r["peptide"]

VALIDATED = [r for r in rec
             if measured(r) and r["spans_junction"] == "yes" and natural(r)
             and seq_known(r) and classI_window(r) and classI_restricted(r)]
assert len(VALIDATED) == 15, "reference set is not the n=15 EPITOPE-BENCHMARK reported"

# ------------------------------------------------- other sequenced reference strata
# Sequence tokens are extracted ONLY from records whose peptide field is not marked
# unretrieved, and only tokens that are all-uppercase valid amino acids of length >= 8.
# (Guard: 'RETRIEVED' is itself a valid amino-acid string, so the marker is excluded first.)
def tokens(r):
    p = r["peptide"]
    if "NOT RETRIEVED" in p or "NOT STATED" in p:
        return []
    return [t for t in re.split(r"[^A-Za-z]+", p)
            if t.isupper() and len(t) >= 8 and AAre.match(t)]

NEG_CONTROL = []            # measured, sequenced, does NOT span the junction
OTHER_REF = []              # sequenced but excluded from the 15 by the rule above
val_ids = {r["id"] for r in VALIDATED}
for r in rec:
    for t in tokens(r):
        row = {"id": r["id"], "fusion": r["fusion"], "seq": t, "hla": r["hla"],
               "evidence": r["evidence"], "spans_junction": r["spans_junction"]}
        if r["id"] in val_ids:
            continue
        (NEG_CONTROL if r["spans_junction"] == "no" else OTHER_REF).append(row)

# ------------------------------------------------- this repository's peptide sets
junctions = fus["junctions"]
peptide_junctions = defaultdict(list)
for j in junctions:
    for p in j["novel_peptides"]:
        peptide_junctions[p].append(j["junction_label"])
JUNC_PEPTIDES = sorted(peptide_junctions)
BINDERS = fus["predicted_binders_ranked"]
BINDER_SEQS = sorted({b["peptide"] for b in BINDERS})
assert set(BINDER_SEQS) <= set(JUNC_PEPTIDES), "a ranked binder is not a junction peptide"
PANEL = fus["_predictor"]["alleles"]

# ================================================================ PART A: correspondence
def collapse(s):  return s.replace("I", "L")   # isobaric: MS/MS cannot separate Leu from Ile

def correspond(query, refs, key="seq"):
    """Return exact, substring (either direction), and I/L-collapsed hits."""
    out = {"exact": [], "substring": [], "isobaric_exact": [], "isobaric_substring": []}
    for q in query:
        cq = collapse(q)
        for r in refs:
            s = r[key]; cs = collapse(s)
            hit = {"query": q, "ref_id": r["id"], "ref_seq": s, "ref_fusion": r["fusion"]}
            if q == s:
                out["exact"].append(hit)
            if q in s or s in q:
                out["substring"].append(dict(hit, direction=("query_in_ref" if q in s else "ref_in_query")))
            if cq == cs and q != s:
                out["isobaric_exact"].append(hit)
            if (cq in cs or cs in cq) and not (q in s or s in q):
                out["isobaric_substring"].append(hit)
    return out

# Context-level arm: the 174 windows are 8-11mers that all cross the seam, so a validated
# epitope lying wholly inside a donor or acceptor flank could not be caught above. This arm
# tests the full 21-residue junction context of each in-frame junction instead.
CONTEXTS = [{"junction": j["junction_label"],
             "context": j["junction_context"].replace("|", "")} for j in junctions]
CONTEXT_HITS = []
ALL_REF = ([{"id": r["id"], "seq": r["peptide"], "fusion": r["fusion"], "set": "validated_15"}
            for r in VALIDATED]
           + [dict(x, set="negative_control") for x in NEG_CONTROL]
           + [dict(x, set="other_sequenced") for x in OTHER_REF])
for c in CONTEXTS:
    for r in ALL_REF:
        if r["seq"] in c["context"]:
            CONTEXT_HITS.append({"junction": c["junction"], "ref_id": r["id"], "ref_seq": r["seq"],
                                 "ref_set": r["set"], "ref_fusion": r["fusion"],
                                 "isobaric_only": False})
        elif collapse(r["seq"]) in collapse(c["context"]):
            CONTEXT_HITS.append({"junction": c["junction"], "ref_id": r["id"], "ref_seq": r["seq"],
                                 "ref_set": r["set"], "ref_fusion": r["fusion"],
                                 "isobaric_only": True})

TESTS = {}
for qname, qset in (("junction_peptides_174", JUNC_PEPTIDES),
                    ("predicted_binders_11", BINDER_SEQS)):
    for rname, rset in (("validated_junction_epitopes_15",
                         [{"id": r["id"], "seq": r["peptide"], "fusion": r["fusion"]} for r in VALIDATED]),
                        ("non_junction_negative_controls", NEG_CONTROL),
                        ("other_sequenced_records", OTHER_REF)):
        TESTS["%s__vs__%s" % (qname, rname)] = correspond(qset, rset)

# ---- matcher self-test: a zero is only informative if the matcher can find a true hit ----
_ref15 = [{"id": r["id"], "seq": r["peptide"], "fusion": r["fusion"]} for r in VALIDATED]
_self = correspond([r["peptide"] for r in VALIDATED], _ref15)
_swapped = [(p.replace("L", "\x00").replace("I", "L").replace("\x00", "I")) for p in
            [q["peptide"] for q in VALIDATED] if ("I" in p or "L" in p)]
_iso = correspond(_swapped, _ref15)
SELFTEST = {
  "exact_arm_validated_vs_itself": {"n": len(_self["exact"]), "expected_min": 15},
  "isobaric_arm_IL_swapped_validated_vs_itself": {
      "n_queries": len(_swapped), "n_isobaric_exact": len(_iso["isobaric_exact"]),
      "n_exact": len(_self["exact"])},
  "substring_arm_live_positive": "the E38 EWSR1 exon-7 donor motif hit below is a live "
                                 "positive for the substring arm on the real query set",
}
assert len(_self["exact"]) >= 15, "matcher fails its own exact self-test"
assert len(_iso["isobaric_exact"]) > 0, "matcher fails its own isobaric self-test"

# ================================================================ PART B: characterisation
# ---- B1 validated set --------------------------------------------------------------
val_len = Counter(len(r["peptide"]) for r in VALIDATED)
val_alleles = Counter()
for r in VALIDATED:
    for a in re.findall(r"HLA-[ABC]\*\d{2}:\d{2}", r["hla"]):
        val_alleles[a] += 1
val_loci = Counter(a[4] for a in val_alleles.elements())
val_fusions = Counter(r["fusion"].split(" (")[0] for r in VALIDATED)
val_cterm = Counter(r["peptide"][-1] for r in VALIDATED)

# ---- B2 breakpoint position inside the validated peptides ---------------------------
# Only recorded where the SOURCE RECORD states the split, or where another record's
# stated split fixes it in the same fusion protein. Everything else stays UNKNOWN:
# the sequences alone do not say where the junction falls.
VAL_SPLIT = {
 "E01": {"donor": 3, "acceptor": 6, "basis": "stated in the record's junction_note: "
         "'BCR b3 ...ATGFKQSSK | ABL a2 ALQRPVASD; peptide SSK|ALQRPV crosses it'",
         "confidence": "stated"},
 "E21": {"donor": 5, "acceptor": 4, "basis": "stated in the record's junction_note: "
         "'5 residues from DNAJB1 exon 1 + 4 from PRKACA exon 2'", "confidence": "stated"},
 "E19": {"donor": 9, "acceptor": 1, "basis": "derived: E21 fixes the DNAJB1::PRKACA seam at "
         "RYGEE|VKEF, so EIFDRYGEEV is EIFDRYGEE|V; consistent with this record's own note that "
         "the wild-type counterpart EIFDRYGEEG ends in glycine", "confidence": "derived"},
 "E20": {"donor": 8, "acceptor": 1, "basis": "derived from the same E21 anchor: IFDRYGEE|V",
         "confidence": "derived"},
}
val_split_rows = []
for r in VALIDATED:
    s = VAL_SPLIT.get(r["id"])
    row = {"id": r["id"], "fusion": r["fusion"], "peptide": r["peptide"], "len": len(r["peptide"]),
           "hla": r["hla"]}
    if s:
        row.update(donor_residues=s["donor"], acceptor_residues=s["acceptor"],
                   junction_after_position=s["donor"], basis=s["basis"], confidence=s["confidence"],
                   cterm_from="acceptor" if s["acceptor"] >= 1 else "donor")
    else:
        row.update(donor_residues=None, acceptor_residues=None, junction_after_position=None,
                   basis="UNKNOWN — neither the record nor any lane-local file states where the "
                         "junction falls inside this peptide; not inferable from the sequence alone "
                         "and not resolvable offline", confidence="unknown", cterm_from=None)
    val_split_rows.append(row)
n_split_known = sum(1 for r in val_split_rows if r["confidence"] != "unknown")

# ---- B3 this repository's peptides: partner split is fully determined ----------------
# junction_context is 'DONOR10|SEAM+ACCEPTOR'; the seam residue is a HYBRID codon
# (1 leftover donor nt + 2 retained acceptor nt), so it is counted in its own category.
def split_peptide(pep, j):
    ctx = j["junction_context"]
    donor, rest = ctx.split("|")
    full = donor + rest
    seam_idx = len(donor)                       # index of the hybrid seam residue in `full`
    i = full.find(pep)
    if i < 0:
        return None
    off = seam_idx - i                          # residues of pep before the seam
    n_donor = max(0, min(off, len(pep)))
    has_seam = 0 <= off < len(pep)
    n_acc = len(pep) - n_donor - (1 if has_seam else 0)
    return {"donor_residues": n_donor, "seam_hybrid_residue": int(has_seam),
            "acceptor_residues": n_acc, "junction_after_position": n_donor,
            "cterm_from": ("acceptor" if n_acc > 0 else ("seam" if has_seam else "donor"))}

repo_rows = []
for j in junctions:
    for pep in j["novel_peptides"]:
        s = split_peptide(pep, j)
        assert s is not None, "peptide %s not found in its own junction context" % pep
        repo_rows.append(dict(junction=j["junction_label"], peptide=pep, len=len(pep), **s))
assert len(repo_rows) == sum(j["n_novel_peptides"] for j in junctions)

repo_len = Counter(r["len"] for r in repo_rows)
repo_acc = Counter(r["acceptor_residues"] for r in repo_rows)
repo_don = Counter(r["donor_residues"] for r in repo_rows)
repo_cterm = Counter(r["cterm_from"] for r in repo_rows)
n_span_seam = sum(1 for r in repo_rows if r["seam_hybrid_residue"])

binder_rows = []
for b in BINDERS:
    js = peptide_junctions[b["peptide"]]
    s = split_peptide(b["peptide"], next(j for j in junctions if j["junction_label"] == js[0]))
    binder_rows.append(dict(peptide=b["peptide"], allele=b["allele"], len=len(b["peptide"]),
                            presentation_percentile=b["presentation_percentile"],
                            klass=b["class"], junctions=js, **s))
bind_len = Counter(r["len"] for r in binder_rows)
bind_all = Counter(r["allele"] for r in binder_rows)

# ---- B4 allele-panel comparison ------------------------------------------------------
panel = set(PANEL)
val_a = set(val_alleles)
panel_cover = {
  "predictor_panel": sorted(panel),
  "validated_allotypes": sorted(val_a),
  "in_panel": sorted(val_a & panel),
  "not_in_panel": sorted(val_a - panel),
  "n_validated_epitopes_on_in_panel_allotypes": sum(v for a, v in val_alleles.items() if a in panel),
  "n_validated_epitopes_on_off_panel_allotypes": sum(v for a, v in val_alleles.items() if a not in panel),
  "hla_C_in_panel": sorted(a for a in panel if a.startswith("HLA-C")),
  "hla_C_in_validated": sorted(a for a in val_a if a.startswith("HLA-C")),
  "panel_allotypes_with_zero_ranked_binders": sorted(panel - set(bind_all)),
}

# ================================================================ output
out = {
 "_id": "ARTIFACT-NEOANTIGEN-3-CORRESPONDENCE-CHARACTERISATION",
 "_utc_note": "generated offline; see checks/ for the execution record",
 "_cost": "$0 — CPU only. No network, no GPU, no paid API.",
 "⛔_what_this_is_not": (
   "Prediction is not presentation. The 15 validated epitopes come from nine other fusion "
   "oncoproteins; none of them is evidence about EWSR1::NR4A3. A distributional difference "
   "between the validated set and this repository's predicted set is a checkable statement "
   "about the prediction and its allele panel, and is NOT an argument that any EMC peptide is "
   "or is not presentable. No clinical claim."),
 "_inputs": {
   "repo_junction_artifact": {"file": "research/modalities/fusion-breakpoint-neoantigens.json",
                              "utc": fus["_utc"], "n_inframe_junctions": fus["n_inframe_junctions"],
                              "n_distinct_junction_peptides": len(JUNC_PEPTIDES),
                              "n_ranked_binders": len(BINDERS),
                              "predictor": fus["_predictor"]["tool"] + " " + fus["_predictor"]["version"]},
   "validated_reference": {"file": "PORTFOLIO-INVESTIGATIONS-2026-09-08/EPITOPE-BENCHMARK/"
                                   "epitope-records.json",
                           "n_records": len(rec), "n_benchmark_eligible": len(VALIDATED),
                           "inclusion_rule": "natural sequence · spans the junction · 8-11mer · "
                                             "named class I allotype · >=1 immunological measurement"}},
 "A_correspondence": {
   "reference_sets": {
     "validated_junction_epitopes_15": [{"id": r["id"], "seq": r["peptide"], "fusion": r["fusion"]}
                                        for r in VALIDATED],
     "non_junction_negative_controls": NEG_CONTROL,
     "other_sequenced_records": OTHER_REF},
   "tests": {k: {kk: {"n": len(vv), "hits": vv} for kk, vv in v.items()} for k, v in TESTS.items()},
   "context_level_arm": {"contexts": CONTEXTS, "n_hits": len(CONTEXT_HITS), "hits": CONTEXT_HITS,
     "_note": "each reference sequence tested as a substring of the full 21-residue junction "
              "context, so an epitope lying wholly in a donor or acceptor flank would be caught"},
   "matcher_selftest": SELFTEST,
   "_isobaric_note": "I/L collapse models the one ambiguity ordinary MS/MS cannot resolve; "
                     "Q/K and residue-pair equivalences such as GG/N are NOT modelled, so the "
                     "isobaric arm is a floor on false-match risk, not a bound on it."},
 "B_characterisation": {
   "validated": {
     "n": len(VALIDATED),
     "length_distribution": dict(sorted(val_len.items())),
     "allele_distribution": dict(val_alleles.most_common()),
     "locus_distribution": dict(val_loci.most_common()),
     "fusion_distribution": dict(val_fusions.most_common()),
     "cterminal_residue_distribution": dict(val_cterm.most_common()),
     "breakpoint_position": {
        "n_with_stated_or_derivable_split": n_split_known,
        "n_unknown": len(VALIDATED) - n_split_known,
        "rows": val_split_rows}},
   "repository_predicted": {
     "n_distinct_junction_peptides": len(JUNC_PEPTIDES),
     "n_peptide_instances_across_5_junctions": len(repo_rows),
     "length_distribution_instances": dict(sorted(repo_len.items())),
     "n_instances_containing_the_hybrid_seam_residue": n_span_seam,
     "donor_residue_distribution": dict(sorted(repo_don.items())),
     "acceptor_residue_distribution": dict(sorted(repo_acc.items())),
     "cterminal_source_distribution": dict(repo_cterm.most_common()),
     "ranked_binders": {
        "n": len(BINDERS),
        "length_distribution": dict(sorted(bind_len.items())),
        "allele_distribution": dict(bind_all.most_common()),
        "rows": binder_rows}},
   "allele_panel_comparison": panel_cover},
}
json.dump(out, open(os.path.join(HERE, "neoantigen3-correspondence.json"), "w"), indent=2)

# ---------------------------------------------------------------- console report
w = sys.stdout.write
w("NEOANTIGEN-3  correspondence + characterisation\n" + "=" * 78 + "\n")
w("reference: %d validated junction epitopes, %d sequenced non-junction negative controls, "
  "%d other sequenced records\n" % (len(VALIDATED), len(NEG_CONTROL), len(OTHER_REF)))
w("query:     %d distinct junction peptides, %d ranked predicted binders\n\n"
  % (len(JUNC_PEPTIDES), len(BINDER_SEQS)))
w("PART A - correspondence (each arm reported separately)\n" + "-" * 78 + "\n")
for k, v in TESTS.items():
    w("%-62s exact=%d substring=%d isobaric_exact=%d isobaric_substring=%d\n"
      % (k, len(v["exact"]), len(v["substring"]), len(v["isobaric_exact"]), len(v["isobaric_substring"])))
    for arm, hits in v.items():
        for h in hits:
            w("      %-18s %s ~ %s (%s %s)\n" % (arm, h["query"], h["ref_seq"], h["ref_id"], h["ref_fusion"][:28]))
w("context-level arm: %d hit(s) of %d reference sequences against the 5 junction contexts\n"
  % (len(CONTEXT_HITS), len(ALL_REF)))
for h in CONTEXT_HITS:
    w("      %s  %s (%s, %s%s)\n" % (h["junction"], h["ref_seq"], h["ref_id"], h["ref_set"],
                                      ", ISOBARIC ONLY" if h["isobaric_only"] else ""))
w("matcher self-test: exact arm recovers %d/15 on the reference vs itself; isobaric arm "
  "recovers %d hits on %d I/L-swapped queries\n"
  % (SELFTEST["exact_arm_validated_vs_itself"]["n"],
     SELFTEST["isobaric_arm_IL_swapped_validated_vs_itself"]["n_isobaric_exact"], len(_swapped)))
w("\nPART B - characterisation\n" + "-" * 78 + "\n")
w("VALIDATED n=%d  lengths %s\n" % (len(VALIDATED), dict(sorted(val_len.items()))))
w("  alleles %s\n  loci %s\n" % (dict(val_alleles.most_common()), dict(val_loci.most_common())))
w("  C-terminal residues %s\n" % dict(val_cterm.most_common()))
w("  breakpoint position stated/derivable for %d of %d:\n" % (n_split_known, len(VALIDATED)))
for r in val_split_rows:
    if r["confidence"] != "unknown":
        w("    %-4s %-11s %d|%d  (%s)\n" % (r["id"], r["peptide"], r["donor_residues"],
                                            r["acceptor_residues"], r["confidence"]))
w("    UNKNOWN: %s\n" % ", ".join(r["id"] for r in val_split_rows if r["confidence"] == "unknown"))
w("REPO predicted: %d distinct peptides (%d instances over 5 junctions)\n"
  % (len(JUNC_PEPTIDES), len(repo_rows)))
w("  lengths %s\n  donor residues %s\n  acceptor residues %s\n"
  % (dict(sorted(repo_len.items())), dict(sorted(repo_don.items())), dict(sorted(repo_acc.items()))))
w("  instances containing the hybrid seam residue: %d/%d\n" % (n_span_seam, len(repo_rows)))
w("  C-terminal source %s\n" % dict(repo_cterm.most_common()))
w("  ranked binders: lengths %s alleles %s\n" % (dict(sorted(bind_len.items())), dict(bind_all.most_common())))
w("ALLELE PANEL\n")
w("  validated allotypes in the predictor panel: %s\n" % panel_cover["in_panel"])
w("  validated allotypes NOT in the panel:       %s\n" % panel_cover["not_in_panel"])
w("  validated epitope-allele pairs on-panel %d / off-panel %d\n"
  % (panel_cover["n_validated_epitopes_on_in_panel_allotypes"],
     panel_cover["n_validated_epitopes_on_off_panel_allotypes"]))
w("  HLA-C in panel %s ; HLA-C in validated set %s\n"
  % (panel_cover["hla_C_in_panel"], panel_cover["hla_C_in_validated"]))
w("  panel allotypes with ZERO ranked binders: %s\n" % panel_cover["panel_allotypes_with_zero_ranked_binders"])
w("\nwrote neoantigen3-correspondence.json\n")
