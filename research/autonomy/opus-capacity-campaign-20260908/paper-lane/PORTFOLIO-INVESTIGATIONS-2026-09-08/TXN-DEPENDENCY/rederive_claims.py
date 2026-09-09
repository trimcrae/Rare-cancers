#!/usr/bin/env python3
"""TXN-DEPENDENCY lane: first pass re-derivation of the quantitative claims in
research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md
against committed artifacts.

Stop condition: ONE pass. A MISMATCH is reported digit for digit, never repaired,
and no alternative reading of the artifact is sought.

Writes claim-rederivation-ledger.json to this lane directory. Stdlib + scipy only.
No network, no producer re-run, no manuscript edit.
"""
import json, os, subprocess, hashlib, sys
from scipy import stats

ROOT = "/home/user/Rare-cancers"
LANE = os.path.join(ROOT, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                          "PORTFOLIO-INVESTIGATIONS-2026-09-08/TXN-DEPENDENCY")
MS = "research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md"
EXP = "research/modalities/emc-expression-panels.json"
DEP = "research/modalities/depmap-sarcoma-dependency.json"
FET = "research/modalities/fet-ddr-axis-scan.json"
LIT = "research/literature/fet-fusion-chaperone-clientship-2026-08-27.json"

P6 = "GSE24369_series_matrix.txt.gz"
P3 = "GSE4303-GPL3290_series_matrix.txt.gz"

exp = json.load(open(os.path.join(ROOT, EXP)))
dep = json.load(open(os.path.join(ROOT, DEP)))
fet = json.load(open(os.path.join(ROOT, FET)))
lit = json.load(open(os.path.join(ROOT, LIT))) if os.path.exists(os.path.join(ROOT, LIT)) else None

rows = []


def add(cid, section, claim, quoted, artifact, key, derived, verdict, level, note="",
        missing_input=None, control=None):
    r = {
        "claim_id": cid, "manuscript_section": section, "claim": claim,
        "quoted_value": quoted, "source_artifact": artifact, "source_key": key,
        "rederived_value": derived, "verdict": verdict,
        "derivation_level": level, "note": note,
    }
    if missing_input:
        r["missing_input"] = missing_input
    if control:
        r["known_answer_control"] = control
    rows.append(r)


def eq(a, b):
    return "REPRODUCES" if a == b else "MISMATCH"


# ---------------------------------------------------------------- Stream A tables
# Manuscript §2 tables, transcribed verbatim from the working-tree manuscript.
A6 = [
    ("cdk7_initiation_module",          "3/3", 0.2102,  3.688,  6.6, "0.0086",  0.074,  0.347),
    ("cdk9_elongation_module",          "4/4", 0.0450,  1.189,  5.7, "0.282",  -0.049,  0.139),
    ("cdk12_13_processivity",           "3/3", -0.0418, -0.880, 6.8, "0.409",  -0.155,  0.071),
    ("transcriptional_output_context",  "4/4", 0.1983,  3.782,  7.5, "0.0061",  0.076,  0.321),
    ("hsp90_machine",                   "4/4", 0.0899,  3.857, 15.0, "0.0016",  0.040,  0.140),
    ("co_chaperones",                   "5/5", 0.0809,  1.636,  7.6, "0.142",  -0.034,  0.196),
    ("hsp70_arm_and_stress_response",   "4/5", -0.0853, -1.056, 7.5, "0.324",  -0.274,  0.103),
]
A3 = [
    ("cdk7_initiation_module",          "3/3", 0.4966,  4.113,  9.6, "0.0023",   0.226,  0.767),
    ("cdk9_elongation_module",          "4/4", 0.1737,  2.258, 13.1, "0.0416",   0.008,  0.340),
    ("cdk12_13_processivity",           "3/3", -0.0751, -0.690, 13.5, "0.502",  -0.309,  0.159),
    ("transcriptional_output_context",  "4/4", 0.4709,  4.811,  9.8, "0.00075",  0.252,  0.690),
    ("hsp90_machine",                   "3/4", 0.6075,  3.465, 11.0, "0.0053",   0.222,  0.993),
    ("co_chaperones",                   "5/5", 0.2511,  2.011, 12.0, "0.0673",  -0.021,  0.523),
    ("hsp70_arm_and_stress_response",   "4/5", -0.1639, -0.959, 5.9, "0.375",   -0.584,  0.256),
]
PANEL_OF = {
    "cdk7_initiation_module": "transcriptional_cdk",
    "cdk9_elongation_module": "transcriptional_cdk",
    "cdk12_13_processivity": "transcriptional_cdk",
    "transcriptional_output_context": "transcriptional_cdk",
    "hsp90_machine": "chaperone_dependency",
    "co_chaperones": "chaperone_dependency",
    "hsp70_arm_and_stress_response": "chaperone_dependency",
}


def sigfigs(s):
    """number of significant digits in a printed decimal string"""
    t = s.lstrip("0.").replace(".", "")
    return len(t.lstrip("0")) if t.strip("0") else 1


def round_sig(x, n):
    from decimal import Decimal
    if x == 0:
        return 0.0
    import math
    d = n - int(math.floor(math.log10(abs(x)))) - 1
    return round(x, d)


for pf, tab, tag in ((P6, A6, "GPL6244"), (P3, A3, "GPL3290")):
    for i, (grp, cov, delta, t, df, p_q, lo, hi) in enumerate(tab, 1):
        blk = exp["panels"][PANEL_OF[grp]]["groups"][grp]["per_platform"][pf]
        sc = blk["score"]
        got = {"delta_a_minus_b": sc["delta_a_minus_b"], "t": sc["t"], "df": sc["df"],
               "coverage": "%d/%d" % (blk["n_genes_readable"], blk["n_genes_requested"])}
        want = {"delta_a_minus_b": delta, "t": t, "df": df, "coverage": cov}
        add("A-%s-%02d" % (tag, i), "§2 (%s table)" % tag,
            "%s: Δ, Welch t, df and coverage" % grp,
            want, EXP,
            "panels.%s.groups.%s.per_platform.%s.score" % (PANEL_OF[grp], grp, pf),
            got, eq(want, got), "READ-BACK from committed artifact")

        # conditional arithmetic the manuscript itself defines: SE = Δ/t, printed rounded df
        se = delta / t
        p_calc = 2 * stats.t.sf(abs(t), df)
        tcrit = stats.t.ppf(0.975, df)
        lo_c, hi_c = delta - tcrit * abs(se), delta + tcrit * abs(se)
        p_r = round_sig(p_calc, sigfigs(p_q))
        got_ci = {"approx_p": p_r, "ci_low": round(lo_c, 3), "ci_high": round(hi_c, 3)}
        want_ci = {"approx_p": float(p_q), "ci_low": lo, "ci_high": hi}
        add("A-%s-%02d-PCI" % (tag, i), "§2 (%s table)" % tag,
            "%s: approximate two-sided p and 95%% interval" % grp,
            want_ci, EXP + " (+ manuscript-stated rule)",
            "recomputed from the artifact's rounded Δ, t, df; SE = Δ ÷ t; t-quantile at df",
            got_ci, eq(want_ci, got_ci), "RECOMPUTED (conditional arithmetic on rounded inputs)",
            note="Manuscript §2 states these are conditional arithmetic on the rounded published "
                 "Δ/t/df, not new measurements.")

# recomputation of Δ/t/df from the retained per-sample z values (independent of the stored score)
gr = exp["gene_reads"]
for pf, tab, tag in ((P6, A6, "GPL6244"), (P3, A3, "GPL3290")):
    for i, (grp, cov, delta, t, df, p_q, lo, hi) in enumerate(tab, 1):
        blk = exp["panels"][PANEL_OF[grp]]["groups"][grp]["per_platform"][pf]
        members = blk["genes_readable"]
        per = {}
        ok = True
        for g in members:
            e = gr.get(g, {}).get(pf)
            if not e or "per_sample" not in e:
                ok = False
                break
            for s in e["per_sample"]:
                slot = per.setdefault(s["gsm"], {"class": s["class"], "z": []})
                if s["z_vs_array"] is not None:   # a null is a sample with no value for that gene
                    slot["z"].append(s["z_vs_array"])
        if not ok:
            add("A-%s-%02d-RECOMP" % (tag, i), "§8 level 1/2", grp, {"delta": delta},
                EXP, "gene_reads.<member>.%s.per_sample.z_vs_array" % pf, None,
                "NOT-RE-DERIVABLE-LOCALLY", "RECOMPUTED",
                missing_input="per-sample z_vs_array for at least one readable member of %s on %s"
                              % (grp, pf))
            continue
        a = [sum(v["z"]) / len(v["z"]) for v in per.values()
             if v["class"] == "EMC" and v["z"]]
        b = [sum(v["z"]) / len(v["z"]) for v in per.values()
             if v["class"] not in ("EMC", "unclassified") and v["z"]]
        res = stats.ttest_ind(a, b, equal_var=False)
        d_c = sum(a) / len(a) - sum(b) / len(b)
        got = {"delta_a_minus_b": round(d_c, 4), "t": round(float(res.statistic), 3),
               "df": round(float(res.df), 1), "n_EMC": len(a), "n_comparator": len(b)}
        want = {"delta_a_minus_b": delta, "t": t, "df": df,
                "n_EMC": exp["platforms"][pf]["n_EMC"],
                "n_comparator": exp["platforms"][pf]["n_comparator"]}
        add("A-%s-%02d-RECOMP" % (tag, i), "§8 level 1/2 (replay claim)",
            "%s Δ/t/df recomputed from the retained rounded per-sample z values" % grp,
            want, EXP, "gene_reads.<readable member>.%s.per_sample.z_vs_array" % pf,
            got, eq(want, got), "RECOMPUTED from retained per-sample z (unweighted gene mean, Welch)",
            note="Manuscript §1.1 and §8 disclose that stored values are rounded to 4 dp and that "
                 "the original unrounded probe-level computation is NOT recoverable; any deviation "
                 "here is reported as found and is not repaired in this pass.")

# ---------------------------------------------------------------- cohort counts
pl6, pl3 = exp["platforms"][P6], exp["platforms"][P3]
add("A-COHORT-1", "§1.1 cohort table",
    "GSE24369/GPL6244: 42 specimens, 6 EMC-labelled, comparator 17 LGFMS + 6 desmoid + 6 "
    "myxofibrosarcoma (binned as fibrosarcoma), 5 SFT + 2 pooled muscle excluded",
    {"n_samples": 42, "n_EMC": 6, "n_comparator": 29,
     "class_counts": {"EMC": 6, "LGFMS": 17, "desmoid_fibromatosis": 6, "fibrosarcoma": 6,
                      "unclassified": 7}},
    EXP, "platforms.%s.{n_samples,n_EMC,n_comparator,class_counts}" % P6,
    {"n_samples": pl6["n_samples"], "n_EMC": pl6["n_EMC"], "n_comparator": pl6["n_comparator"],
     "class_counts": pl6["class_counts"]},
    eq({"n_samples": 42, "n_EMC": 6, "n_comparator": 29,
        "class_counts": {"EMC": 6, "LGFMS": 17, "desmoid_fibromatosis": 6, "fibrosarcoma": 6,
                         "unclassified": 7}},
       {"n_samples": pl6["n_samples"], "n_EMC": pl6["n_EMC"], "n_comparator": pl6["n_comparator"],
        "class_counts": pl6["class_counts"]}),
    "READ-BACK",
    note="The artifact stores 7 'unclassified'; the manuscript names them as 5 solitary fibrous "
         "tumour + 2 pooled skeletal-muscle RNA. The split 5+2 is NOT stored as counts in "
         "class_counts and is re-derived below from the verbatim annotations (A-COHORT-3).")
add("A-COHORT-2", "§1.1 cohort table",
    "GSE4303/GPL3290: 16 specimens, 10 EMC-labelled, 3 DFSP + 3 GIST comparator, none excluded",
    {"n_samples": 16, "n_EMC": 10, "n_comparator": 6,
     "class_counts": {"DFSP": 3, "EMC": 10, "GIST": 3}},
    EXP, "platforms.%s.{n_samples,n_EMC,n_comparator,class_counts}" % P3,
    {"n_samples": pl3["n_samples"], "n_EMC": pl3["n_EMC"], "n_comparator": pl3["n_comparator"],
     "class_counts": pl3["class_counts"]},
    eq({"n_samples": 16, "n_EMC": 10, "n_comparator": 6,
        "class_counts": {"DFSP": 3, "EMC": 10, "GIST": 3}},
       {"n_samples": pl3["n_samples"], "n_EMC": pl3["n_EMC"], "n_comparator": pl3["n_comparator"],
        "class_counts": pl3["class_counts"]}), "READ-BACK")

ann = [a["annotation"] for a in pl6["sample_annotations_verbatim"]]
cls = [a.get("class") for a in pl6["sample_annotations_verbatim"]]
unc = [a for a, c in zip(ann, cls) if c == "unclassified"]
n_sft = sum(1 for a in unc if "solitary fibrous" in a.lower())
n_mus = sum(1 for a in unc if "muscle" in a.lower())
add("A-COHORT-3", "§1.1 cohort table",
    "the 7 records outside both arms are 5 solitary fibrous tumour and 2 pooled skeletal-muscle RNA",
    {"solitary_fibrous_tumour": 5, "pooled_skeletal_muscle": 2},
    EXP, "platforms.%s.sample_annotations_verbatim[].annotation (string match on the "
         "unclassified records)" % P6,
    {"solitary_fibrous_tumour": n_sft, "pooled_skeletal_muscle": n_mus,
     "n_unclassified": len(unc)},
    eq({"solitary_fibrous_tumour": 5, "pooled_skeletal_muscle": 2},
       {"solitary_fibrous_tumour": n_sft, "pooled_skeletal_muscle": n_mus}),
    "RECOMPUTED from retained verbatim annotations")

add("A-COHORT-4", "title / abstract / §7",
    "16 archival EMC-labelled specimen records in total",
    16, EXP, "platforms.%s.n_EMC + platforms.%s.n_EMC" % (P6, P3),
    pl6["n_EMC"] + pl3["n_EMC"], eq(16, pl6["n_EMC"] + pl3["n_EMC"]), "RECOMPUTED")

# ---------------------------------------------------------------- readability claims
read_claims = [
    ("A-READ-1", "hsp90_machine on GPL3290 is 3/4 — HSP90AA1 unreadable", "HSP90AA1", P3, False),
    ("A-READ-2", "hsp70 list on GPL6244 is 4/5 — HSPA8 unreadable", "HSPA8", P6, False),
    ("A-READ-3", "hsp70 list on GPL3290 is 4/5 — HSF1 unreadable", "HSF1", P3, False),
]
for cid, claim, gene, pf, expect in read_claims:
    got = gr.get(gene, {}).get(pf, {}).get("readable")
    add(cid, "§1.1 gene-list table", claim, {"readable": expect}, EXP,
        "gene_reads.%s.%s.readable" % (gene, pf), {"readable": got},
        eq(expect, got), "READ-BACK")

# ---------------------------------------------------------------- MYC / algebra
myc6 = gr["MYC"][P6]["EMC"]["mean_z"] - gr["MYC"][P6]["comparator"]["mean_z"]
myc3 = gr["MYC"][P3]["EMC"]["mean_z"] - gr["MYC"][P3]["comparator"]["mean_z"]
add("A-MYC-1", "§2 'what the lists do and do not show internally'",
    "MYC's own difference is +1.0625 on GPL6244 and +1.863 on GPL3290",
    {"GPL6244": 1.0625, "GPL3290": 1.863}, EXP,
    "gene_reads.MYC.<platform>.{EMC.mean_z, comparator.mean_z}",
    {"GPL6244": round(myc6, 4), "GPL3290": round(myc3, 4)},
    eq({"GPL6244": 1.0625, "GPL3290": 1.863},
       {"GPL6244": round(myc6, 4), "GPL3290": round(myc3, 4)}), "RECOMPUTED")

oth6 = (4 * 0.1983 - 1.0625) / 3
oth3 = (4 * 0.4709 - 1.863) / 3
add("A-MYC-2", "§2 'simple algebra on those published summaries'",
    "the other three members of transcriptional_output_context give approximately −0.090 "
    "(GPL6244) and +0.007 (GPL3290)",
    {"GPL6244": -0.090, "GPL3290": 0.007},
    EXP, "(4 × group Δ − MYC Δ) ÷ 3, on the published rounded summaries",
    {"GPL6244": round(oth6, 3), "GPL3290": round(oth3, 3)},
    eq({"GPL6244": -0.090, "GPL3290": 0.007},
       {"GPL6244": round(oth6, 3), "GPL3290": round(oth3, 3)}), "RECOMPUTED")

h6 = gr["HSP90AA1"][P6]["EMC"]["mean_z"] - gr["HSP90AA1"][P6]["comparator"]["mean_z"]
add("A-HSP90AA1", "§2", "HSP90AA1's own difference is negative on GPL6244 and unreadable on GPL3290",
    {"GPL6244_sign": "negative", "GPL3290_readable": False}, EXP,
    "gene_reads.HSP90AA1.<platform>",
    {"GPL6244_difference": round(h6, 4), "GPL6244_sign": "negative" if h6 < 0 else "non-negative",
     "GPL3290_readable": gr["HSP90AA1"][P3]["readable"]},
    eq({"GPL6244_sign": "negative", "GPL3290_readable": False},
       {"GPL6244_sign": "negative" if h6 < 0 else "non-negative",
        "GPL3290_readable": gr["HSP90AA1"][P3]["readable"]}), "RECOMPUTED")

# ---------------------------------------------------------------- proliferation control
prol = exp["panels"]["mtap_prmt5"]["groups"]["proliferation_confound_control"]
g6 = prol["per_platform"][P6]["score"]
g3 = prol["per_platform"][P3]["score"]
want = {"n_genes": 11, "t": [0.441, 2.905], "df": [6.7, 14.0], "delta": [0.0896, 0.4459]}
got = {"n_genes": len(prol["genes_requested"]),
       "t": [g6["t"], g3["t"]], "df": [g6["df"], g3["df"]],
       "delta": [g6["delta_a_minus_b"], g3["delta_a_minus_b"]]}
add("A-PROLIF", "§2 'proliferation and other covariates'",
    "the retained eleven-gene proliferation-control list gives t = 0.441 and 2.905 at df 6.7 and "
    "14.0 with Δ = 0.0896 and 0.4459", want, EXP,
    "panels.mtap_prmt5.groups.proliferation_confound_control.per_platform.<platform>.score",
    got, eq(want, got), "READ-BACK")

mki = exp["panels"]["instrument_controls"]["groups"]["proliferation_reference"]["per_platform"][P6]
add("A-MKI67", "§2", "the single-gene MKI67 group is marked unscored by the panel-size rule",
    {"score": None}, EXP,
    "panels.instrument_controls.groups.proliferation_reference.per_platform.%s.score" % P6,
    {"score": mki["score"], "verdict": mki["verdict"][:90]},
    eq(None, mki["score"]), "READ-BACK")

# ---------------------------------------------------------------- multiplicity
allp = []
for tab, tag in ((A6, "GPL6244"), (A3, "GPL3290")):
    for grp, cov, delta, t, df, p_q, lo, hi in tab:
        allp.append((tag, grp, 2 * stats.t.sf(abs(t), df)))
thr = 0.05 / 14
clear = sorted([(g, tg) for tg, g, p in allp if p < thr])
want = sorted([("cdk7_initiation_module", "GPL3290"),
               ("transcriptional_output_context", "GPL3290"),
               ("hsp90_machine", "GPL6244")])
add("A-BONF", "§2 multiplicity",
    "α = 0.05/14 ≈ 0.0036 is cleared by exactly three readings — cdk7_initiation_module and "
    "transcriptional_output_context on GPL3290, hsp90_machine on GPL6244 — and no group clears "
    "it on both platforms",
    {"threshold": 0.0036, "n_clearing": 3, "clearing": want},
    EXP + " (+ manuscript rule)",
    "conditional p from the artifact's rounded t/df, compared with 0.05/14",
    {"threshold": round(thr, 4), "n_clearing": len(clear), "clearing": clear},
    eq({"threshold": 0.0036, "n_clearing": 3, "clearing": want},
       {"threshold": round(thr, 4), "n_clearing": len(clear), "clearing": clear}), "RECOMPUTED")

# ---------------------------------------------------------------- Stream B
rowmap = {}
for grp, rs in dep["genes_by_group"].items():
    for r in rs:
        rowmap[r["gene"]] = (grp, r)

B = [
    ("CDK7",     -1.847, -1.762,  0.085, 1.0,   0.999, 91),
    ("CDK9",     -1.464, -1.447,  0.017, 1.0,   0.994, 91),
    ("HSP90AA1", -0.230, -0.256, -0.026, 0.055, 0.052, 5),
    ("HSP90AB1", -0.348, -0.275,  0.073, 0.187, 0.119, 17),
    ("CDC37",    -1.093, -1.160, -0.067, 0.978, 0.987, 89),
]
CONTROL_NOTE = ("Known-answer control required by the RANK 8 proposal: DEP-THRESHOLD row A3 "
                "(CLAIMS-AT-RISK.md §A) independently re-derived CDK7 = −1.847 with selectivity "
                "+0.085 and rest_frac_dependent 0.999, and CDK9 = −1.464 with selectivity +0.017 "
                "and rest_frac_dependent 0.994, from the same artifact. This lane's harness must "
                "reproduce those values; if it does not, THIS HARNESS is wrong and that is the "
                "reported result.")
for gene, sm, rm, diff, sfd, rfd, cnt in B:
    grp, r = rowmap[gene]
    want = {"sarcoma_mean": sm, "rest_mean": rm, "difference_rest_minus_sarcoma": diff,
            "sarcoma_frac_dependent": sfd, "rest_frac_dependent": rfd, "n_sarcoma": 91}
    got = {"sarcoma_mean": r["sarcoma_mean"], "rest_mean": r["rest_mean"],
           "difference_rest_minus_sarcoma": r["selectivity"],
           "sarcoma_frac_dependent": r["sarcoma_frac_dependent"],
           "rest_frac_dependent": r["rest_frac_dependent"], "n_sarcoma": r["n_sarcoma"]}
    ctrl = CONTROL_NOTE if gene in ("CDK7", "CDK9") else None
    add("B-%s" % gene, "§3 dependency table",
        "%s row: sarcoma mean, rest-of-panel mean, difference, dependent fractions" % gene,
        want, DEP, "genes_by_group.%s[gene=%s]" % (grp, gene), got, eq(want, got), "READ-BACK",
        note="Manuscript prints HSP90AA1 sarcoma mean as −0.230; the artifact stores −0.23 "
             "(same number, trailing zero)." if gene == "HSP90AA1" else "",
        control=ctrl)

    # unique-integer claim
    cands = [k for k in range(0, 92) if round(k / 91, 3) == r["sarcoma_frac_dependent"]]
    add("B-%s-INT" % gene, "§3 preamble",
        "%s: '%d/91' is the unique integer compatible with the stored rounded fraction" % (gene, cnt),
        {"integer": cnt, "unique": True}, DEP,
        "genes_by_group.%s[gene=%s].sarcoma_frac_dependent, n_sarcoma" % (grp, gene),
        {"compatible_integers": cands, "unique": len(cands) == 1},
        eq({"integer": cnt, "unique": True},
           {"integer": cands[0] if len(cands) == 1 else cands, "unique": len(cands) == 1}),
        "RECOMPUTED")

add("B-DENOM", "§1.2 / §3",
    "the release catalogues 176 Soft Tissue/Bone models but every gene summarized has non-missing "
    "gene-effect values for 91 of them; 91 is the denominator of every percentage",
    {"n_sarcoma_models": 176, "n_sarcoma_per_gene": 91,
     "all_genes_agree_on_91": True, "dependent_threshold": -0.5},
    DEP, "n_sarcoma_models, dependent_threshold, genes_by_group[*].n_sarcoma",
    {"n_sarcoma_models": dep["n_sarcoma_models"],
     "n_sarcoma_per_gene": sorted({r["n_sarcoma"] for _, r in rowmap.values()}),
     "all_genes_agree_on_91": {r["n_sarcoma"] for _, r in rowmap.values()} == {91},
     "dependent_threshold": dep["dependent_threshold"]},
    eq({"n_sarcoma_models": 176, "n_sarcoma_per_gene": 91, "all_genes_agree_on_91": True,
        "dependent_threshold": -0.5},
       {"n_sarcoma_models": dep["n_sarcoma_models"],
        "n_sarcoma_per_gene": (sorted({r["n_sarcoma"] for _, r in rowmap.values()})[0]
                               if len({r["n_sarcoma"] for _, r in rowmap.values()}) == 1
                               else sorted({r["n_sarcoma"] for _, r in rowmap.values()})),
        "all_genes_agree_on_91": {r["n_sarcoma"] for _, r in rowmap.values()} == {91},
        "dependent_threshold": dep["dependent_threshold"]}),
    "READ-BACK",
    control="Known-answer control: SYNLETH-2 and DEP-THRESHOLD both re-derived 91 as the "
            "per-gene screened denominator against 176 catalogued models.")

sv = dep["self_validation"]
want = {"BRD9_synovial": {"n": 5, "mean": -0.13, "frac_dependent": 0.20},
        "SMARCB1_rhabdoid": {"n": 13, "mean": -0.025, "frac_dependent": 0.077},
        "SMARCB1_rest_of_panel": {"mean": -0.832, "frac_dependent": 0.839}}
got = {"BRD9_synovial": {"n": sv["BRD9_in_synovial"]["n"],
                         "mean": sv["BRD9_in_synovial"]["mean_gene_effect"],
                         "frac_dependent": sv["BRD9_in_synovial"]["frac_dependent"]},
       "SMARCB1_rhabdoid": {"n": sv["SMARCB1_in_rhabdoid"]["n"],
                            "mean": sv["SMARCB1_in_rhabdoid"]["mean_gene_effect"],
                            "frac_dependent": sv["SMARCB1_in_rhabdoid"]["frac_dependent"]},
       "SMARCB1_rest_of_panel": {"mean": rowmap["SMARCB1"][1]["rest_mean"],
                                 "frac_dependent": rowmap["SMARCB1"][1]["rest_frac_dependent"]}}
add("B-SELFVAL", "§1.2 self_validation",
    "BRD9 in 5 synovial models: mean −0.13, 20 % dependent. SMARCB1 in 13 rhabdoid models: mean "
    "−0.025, 7.7 % dependent, against a rest-of-panel mean of −0.832 and 83.9 % dependent",
    want, DEP, "self_validation.*, genes_by_group['BAF / SWI-SNF core'][gene=SMARCB1]",
    got, eq(want, got), "READ-BACK",
    note="Manuscript prints 20 % / 7.7 % / 83.9 % for the stored 0.2 / 0.077 / 0.839.")

add("B-EMCLINE", "§1.2 / §7",
    "the single DepMap model carrying the EMC label (ACH-001519) contributes no CRISPR "
    "gene-effect data",
    {"model_id": "ACH-001519", "in_model_metadata": True, "has_crispr_gene_effect": False},
    FET, "emc_line",
    {"model_id": fet["emc_line"]["model_id"],
     "in_model_metadata": fet["emc_line"]["in_model_metadata"],
     "has_crispr_gene_effect": fet["emc_line"]["has_crispr_gene_effect"]},
    eq({"model_id": "ACH-001519", "in_model_metadata": True, "has_crispr_gene_effect": False},
       {"model_id": fet["emc_line"]["model_id"],
        "in_model_metadata": fet["emc_line"]["in_model_metadata"],
        "has_crispr_gene_effect": fet["emc_line"]["has_crispr_gene_effect"]}), "READ-BACK")

# ---------------------------------------------------------------- not re-derivable locally
add("B-NRD-1", "§3 / §1.2",
    "the dependent fractions and mean differences describe per-line Chronos gene effects in the "
    "91 screened sarcoma-lineage lines and the non-sarcoma remainder",
    "5/91, 17/91, 89/91, 91/91 and the five mean differences, as per-line observations",
    DEP, "no per-line values are retained anywhere in the artifact", None,
    "NOT-RE-DERIVABLE-LOCALLY", "PER-LINE",
    missing_input="DepMap public release 24Q4 CRISPRGeneEffect.csv (per-line Chronos gene effects) "
                  "and Model.csv (OncotreeLineage per model). Neither file is in this repository; "
                  "the producer research/modalities/depmap_sarcoma_dependency.py retains only "
                  "mean/fraction summaries per gene (DEP-THRESHOLD finding C1: no SD, no quantile, "
                  "no order statistic, no per-line value). Fetching them is outside worker "
                  "authority in this lane and was NOT attempted.")
add("B-NRD-2", "§1.2 / §3",
    "the non-sarcoma comparator arm's non-missing sample size (the denominator behind "
    "'99.9 %', '99.4 %', '5.2 %', '11.9 %', '98.7 %')",
    "not stated in the manuscript; the manuscript states it is unavailable",
    DEP, "no n_rest / n_rest_non_missing field exists in the artifact", None,
    "NOT-RE-DERIVABLE-LOCALLY", "PER-LINE",
    missing_input="a retained non-sarcoma non-missing count per gene (n_rest). The producer emits "
                  "only n_sarcoma. Recovering it requires CRISPRGeneEffect.csv + Model.csv. The "
                  "manuscript's own §1.2 states the artifact supplies none of these, so the "
                  "manuscript makes NO claim that fails here — the input is simply absent.")
add("A-NRD-1", "§8 level 3",
    "the within-array standardized scores were formed from the arrays' all-probe reference "
    "distributions (per-array mean and SD over all probes)",
    "the standardization construct itself",
    EXP, "background_reads / per-array mean & SD are stored rounded; the probe values are not",
    None, "NOT-RE-DERIVABLE-LOCALLY", "RAW-INPUT",
    missing_input="the original GEO series matrices GSE24369_series_matrix.txt.gz (GPL6244) and "
                  "GSE4303-GPL3290_series_matrix.txt.gz, plus the probe-to-symbol mapping tables. "
                  "Not held in this repository, no hash is claimed for them (§8), and no network "
                  "retrieval was attempted in this lane.")
add("A-NRD-2", "§1.1 interpretation hold",
    "whether the deposited GPL3290 values were harmonized upstream across the three reference "
    "labels CRH, CRH-mRNA and UHR",
    "explicitly stated as 'not established'",
    EXP, "platforms.%s.sample_annotations_verbatim (labels present; harmonization status absent)" % P3,
    None, "NOT-RE-DERIVABLE-LOCALLY", "RAW-INPUT",
    missing_input="the authentic deposited processing and reference documentation for GSE4303 on "
                  "GPL3290. The manuscript does not claim harmonization either way; the missing "
                  "input is named here because the hold rests on it.")
add("L-NRD-1", "§4 literature assessment",
    "fifteen dated PubMed queries run on 2026-08-27, with Q15 returning 25 unscreened hits",
    {"n_queries": 15, "Q15_hits": 25},
    LIT, "the committed clientship artifact",
    None if lit is None else "artifact present; hit counts are a record of a dated network "
                             "retrieval, not a locally recomputable quantity",
    "NOT-RE-DERIVABLE-LOCALLY", "DATED-RETRIEVAL",
    missing_input="a live PubMed/E-utilities query at the same date. Re-running the queries today "
                  "would be a different dated search, and direct HTTP egress is refused in this "
                  "environment (proxy CONNECT 403). The counts can be READ BACK from the artifact "
                  "but cannot be re-derived.")

# ---------------------------------------------------------------- blob identities §8
blobs = {
    "research/modalities/emc-expression-panels.json": "330c04cb9277c3900919d45b548c730ec1746849",
    "research/modalities/emc_expression_panels.py": "d260a5d3f080f2ca1299609e199b5dce492efca1",
    "research/modalities/census-route-expression-grading.json": "b45a35a4ee2636993e42e897c3be6d7705ccae8a",
    "research/modalities/census_route_expression_grading.py": "18625608b378122adbe9dbcca16de370c357367b",
    "research/modalities/depmap-sarcoma-dependency.json": "1f00ad1cf509c540985d2d4be2830bcbec9a94a8",
    "research/modalities/depmap_sarcoma_dependency.py": "fc0a0cc0316e562b03e2ad9eda36477d0c1c88d9",
    "research/modalities/emc_atr_vulnerability.py": "177df6cfd72a787e316cfba07e71e4c4231026fb",
    "research/modalities/fet-ddr-axis-scan.json": "41a575d2090457bc8e1eac15a56fab4c0f1bc0ac",
    "research/literature/txn-dependency-class-definitions-2026-08-09.json": "a8fa744a1bcdabde4d60a1f56760b33070ff47c9",
    "research/literature/fet-fusion-chaperone-clientship-2026-08-27.json": "8728c34de793da848ccae012e808e668b69b24bd",
}
for path, want_id in blobs.items():
    got_id = subprocess.run(["git", "hash-object", path], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    add("ID-%s" % os.path.basename(path), "§8 fixed identities",
        "Git blob SHA-1 of %s as read against" % path, want_id, path,
        "git hash-object (working tree, re-hashed at use time)", got_id,
        eq(want_id, got_id), "RECOMPUTED",
        note="Re-hashed from the working tree at run time rather than trusting a recorded hash.")

# ---------------------------------------------------------------- manuscript state
ms_abs = os.path.join(ROOT, MS)
ms_sha = hashlib.sha256(open(ms_abs, "rb").read()).hexdigest()
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                      text=True).stdout.strip()
dirty = subprocess.run(["git", "status", "--porcelain", MS], cwd=ROOT, capture_output=True,
                       text=True).stdout.strip()
committed_sha = hashlib.sha256(
    subprocess.run(["git", "show", "HEAD:" + MS], cwd=ROOT, capture_output=True).stdout
).hexdigest()

verdicts = {}
for r in rows:
    verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1

out = {
    "id": "ART-TXN-DEPENDENCY-CLAIM-REDERIVATION-LEDGER",
    "lane": "TXN-DEPENDENCY",
    "campaign": "OPUS-CAPACITY-CAMPAIGN-20260908",
    "date": "2026-09-09",
    "endpoint": "PUB-TXN-DEPENDENCY",
    "manuscript": {
        "path": MS,
        "sha256_working_tree_at_use_time": ms_sha,
        "sha256_of_HEAD_blob": committed_sha,
        "git_status_porcelain": dirty,
        "repo_head": head,
        "warning": "THE MANUSCRIPT IS MODIFIED AND UNCOMMITTED IN THE WORKING TREE. Every quoted "
                   "value in this ledger is transcribed from the WORKING-TREE file, re-hashed at "
                   "the moment of use. It was not edited, reverted or diffed by this lane.",
    },
    "scope": "One pass over the quantitative claims of the manuscript. Verdicts are REPRODUCES, "
             "MISMATCH or NOT-RE-DERIVABLE-LOCALLY. A MISMATCH is reported, never repaired.",
    "verdict_counts": verdicts,
    "claims": rows,
}
os.makedirs(LANE, exist_ok=True)
with open(os.path.join(LANE, "claim-rederivation-ledger.json"), "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")

for r in rows:
    print(r["verdict"], r["claim_id"], "|", r["claim"][:70])
print()
print("counts:", verdicts)
print("manuscript working-tree sha256:", ms_sha)
print("manuscript HEAD-blob sha256:  ", committed_sha)
print("dirty:", repr(dirty))
