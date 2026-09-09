#!/usr/bin/env python3
"""Re-derive every quantity the EMC treatment roadmap cites, from its own cited artifacts.
Read-only. No network. Prints CLAIMED vs DERIVED, digit for digit."""
import json, os
R = "/home/user/Rare-cancers"
def load(p): return json.load(open(os.path.join(R, p)))
rows = []
def chk(tag, claimed, derived, src):
    ok = "MATCH" if str(claimed) == str(derived) else "DIFFER"
    rows.append((tag, claimed, derived, ok, src))

# --- structure
s = load("research/modalities/nr4a3-structure-assessment.json")["NR4A3"]
chk("fpocket top druggability", "0.495", s["fpocket"]["top_pocket_locale"]["druggability"],
    "nr4a3-structure-assessment.json")
chk("TAD disorder frac pLDDT<50", "(disordered)", s["regions"]["AF1/N-terminal (disordered)"]["frac_pLDDT_below_50"],
    "nr4a3-structure-assessment.json")

# --- selectivity handles
sel = load("research/modalities/nr4a-selectivity.json")
handles = sorted({h for p in sel["nr4a3_lbd_pockets"] for h in p.get("selectivity_handles", [])})
chk("divergent pocket residues (handles)", "7", len(handles), "nr4a-selectivity.json:"+",".join(handles))
# how many of the engageable ones distinguish NR4A2
d2 = [r for p in sel["nr4a3_lbd_pockets"] for r in p["residues"]
      if r["divergent"] and r["nr4a3"][0] != r["nr4a2"]]
chk("handles that differ from NR4A2", "4 of 5", len({r["nr4a3"] for r in d2}), "nr4a-selectivity.json")

# --- DepMap dependency
dep = load("research/modalities/depmap-sarcoma-dependency.json")
fa = dep["fusion_addiction_proxy"]
chk("FLI1 Ewing gene effect", "-0.93", fa["FLI1_in_ewing"]["mean_gene_effect"], "depmap-sarcoma-dependency.json")
chk("FLI1 Ewing frac dependent", "74%", fa["FLI1_in_ewing"]["frac_dependent"], "depmap-sarcoma-dependency.json")
chk("n Ewing lines", "27", fa["FLI1_in_ewing"]["n"], "depmap-sarcoma-dependency.json")
chk("dependency threshold used", "(unstated in ms)", dep["dependent_threshold"], "depmap-sarcoma-dependency.json")
ew = fa["EWSR1_overall"]
chk("EWSR1 selectivity", "(not in ms)", ew["selectivity"], "depmap-sarcoma-dependency.json")
chk("EWSR1 rest_frac_dependent", "(not in ms)", ew["rest_frac_dependent"], "depmap-sarcoma-dependency.json")
chk("EWSR1 sarcoma_frac_dependent", "(not in ms)", ew["sarcoma_frac_dependent"], "depmap-sarcoma-dependency.json")
chk("NR4A3 sarcoma_frac_dependent", "(not in ms)", fa["NR4A3_overall"]["sarcoma_frac_dependent"], "depmap-sarcoma-dependency.json")
brd9 = [g for grp in dep["genes_by_group"].values() for g in grp if g["gene"] == "BRD9"][0]
chk("BRD9 sarcoma selectivity", "not selectively essential", brd9["selectivity"], "depmap-sarcoma-dependency.json")
chk("BRD9 sarcoma frac dependent", "not selectively essential", brd9["sarcoma_frac_dependent"], "depmap-sarcoma-dependency.json")

# --- expression
ex = load("research/modalities/depmap-target-expression.json")
flat = {g["gene"]: g for grp in ex["genes_by_group"].values() for g in grp}
chk("CD276 sarcoma mean log2TPM", "5.73", flat["CD276"]["sarcoma_mean_log2tpm"], "depmap-target-expression.json")
chk("CD276 frac expressed", "99%", flat["CD276"]["sarcoma_frac_expressed"], "depmap-target-expression.json")
chk("CD276 n lines (ms says 'sarcoma lines')", "n_sarcoma_lines=176 in header", flat["CD276"]["n_sarcoma"],
    "depmap-target-expression.json")
for g, c in (("PRAME", "53%"), ("CTAG1B", "5%"), ("MAGEA4", "7%")):
    if g in flat:
        chk(f"{g} frac expressed", c, flat[g]["sarcoma_frac_expressed"], "depmap-target-expression.json")
sub = ex.get("surface_and_cta_by_subtype", {})
myx = {k: v for k, v in sub.items() if "myx" in k.lower()} or sub
print("SUBTYPE KEYS:", list(sub)[:20])
try:
    m = json.dumps(myx)[:600]
    print("MYXOID BLOCK:", m)
except Exception as e:
    print("subtype read error", e)

# --- ASO
a = load("research/modalities/aso-insilico-evaluation.json")
chk("gapmers evaluated", "5", a["n_evaluated"], "aso-insilico-evaluation.json")
chk("transcripts scanned", "186,185", a["offtarget_screen"]["transcripts_scanned"], "aso-insilico-evaluation.json")
chk("candidates transcriptome-clean", "0", a["n_candidates_zero_offtarget"], "aso-insilico-evaluation.json")
chk("seed straddles junction", "2 of 5", a["n_candidates_fusion_specific_sirna_seed"], "aso-insilico-evaluation.json")
td = a["top_designs"]
chk("best candidate one-mismatch hits", "8", td[0]["offtarget_le1mm"], "aso-insilico-evaluation.json top_designs[0]")
chk("best candidate exact hits", "0", td[0]["offtarget_exact"], "aso-insilico-evaluation.json top_designs[0]")
best_acc = max(x["site_accessibility"] for x in td)
chk("BEST site accessibility over all 5", "~0.35 (best)", best_acc, "aso-insilico-evaluation.json max over top_designs")
chk("GC of designs", "~75%", sorted({x["gc_percent"] for x in td}), "aso-insilico-evaluation.json")
chk("min le1mm over all 5", "8 (best)", min(x["offtarget_le1mm"] for x in td), "aso-insilico-evaluation.json")
chk("listed offtarget_hits for design 0", "8", len(td[0]["offtarget_hits"]), "aso-insilico-evaluation.json")

w = max(len(r[0]) for r in rows)
print("\n%-*s | %-28s | %-28s | %s" % (w, "QUANTITY", "MANUSCRIPT", "RE-DERIVED", "STATUS"))
for t, c, d, ok, src in rows:
    print("%-*s | %-28s | %-28s | %s  [%s]" % (w, t, c, d, ok, src))
