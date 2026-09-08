#!/usr/bin/env python3
"""TD1 repair — focused source/text bindings.

Binds every quantitative and membership claim in the repaired manuscript to the live frozen
artifacts, and re-derives the conditional arithmetic (two-sided Student-t tail and the
delta/t interval) from the SAME rounded published summaries the independent review used.

⛔ Scope: no raw reanalysis, no producer import, no biological recomputation, no source fetch.
The t-tail routine below operates on the artifact's own rounded delta/t/df, exactly as the
reviewer's retained attempt-2 script did; agreement with that retained output is checked, it is
not assumed.
"""
import json
import math
import re
import sys

ROOT = "research/"
MAN = ROOT + "manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md"
E = ROOT + "modalities/emc-expression-panels.json"
D = ROOT + "modalities/depmap-sarcoma-dependency.json"
G = ROOT + "modalities/census-route-expression-grading.json"
C = ROOT + "literature/fet-fusion-chaperone-clientship-2026-08-27.json"
REVIEWER = ("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/"
            "scratchpad/td1-capsule/extracted/reviewer-checks/summary-arithmetic-attempt2.stdout.json")

fails, checks = [], []


def ok(name, cond, detail=""):
    checks.append({"check": name, "pass": bool(cond), "detail": detail})
    if not cond:
        fails.append(f"{name}: {detail}")


# ---------------------------------------------------------------- t distribution
def _betacf(a, b, x):
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < tiny:
            d = tiny
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < tiny:
            d = tiny
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta)
    if x < (a + 1) / (a + b + 2):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(math.log(1 - x) * b + math.log(x) * a - lbeta) * _betacf(b, a, 1 - x) / b


def t_two_sided_p(t, df):
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(df, alpha=0.05):
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_two_sided_p(mid, df) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# numeric calibration: Cauchy t=1, df=1 -> p = 0.5 exactly
cal = t_two_sided_p(1.0, 1.0)
ok("t-tail numeric calibration (Cauchy t=1 df=1 == 0.5)", abs(cal - 0.5) < 1e-9, f"got {cal!r}")

man = open(MAN, encoding="utf-8").read()
flat = " ".join(man.split())  # newline-insensitive view of the manuscript prose
e = json.load(open(E, encoding="utf-8"))
d = json.load(open(D, encoding="utf-8"))
g = json.load(open(G, encoding="utf-8"))
c = json.load(open(C, encoding="utf-8"))
rev = json.load(open(REVIEWER, encoding="utf-8"))

P6244 = "GSE24369_series_matrix.txt.gz"
P3290 = "GSE4303-GPL3290_series_matrix.txt.gz"

# ---------------------------------------------------------------- 1. cohorts / annotations (F2, F6)
cc6 = e["platforms"][P6244]["class_counts"]
cc3 = e["platforms"][P3290]["class_counts"]
ok("GPL6244 class counts", cc6 == {"EMC": 6, "LGFMS": 17, "desmoid_fibromatosis": 6,
                                   "fibrosarcoma": 6, "unclassified": 7}, repr(cc6))
ok("GPL3290 class counts", cc3 == {"DFSP": 3, "EMC": 10, "GIST": 3}, repr(cc3))

ann6 = e["platforms"][P6244]["sample_annotations_verbatim"]
unc = [a for a in ann6 if a["class"] == "unclassified"]
sft = [a for a in unc if a["annotation"].lower().startswith("solitary fibrous tumor")]
mus = [a for a in unc if "skeletal muscle pooled rna" in a["annotation"].lower()]
ok("5 solitary fibrous tumour records excluded as unclassified", len(sft) == 5, f"n={len(sft)}")
ok("2 pooled skeletal-muscle records excluded as unclassified", len(mus) == 2, f"n={len(mus)}")
ok("unclassified arm is exactly those 7", len(unc) == 7, f"n={len(unc)}")
mfs = [a for a in ann6 if a["class"] == "fibrosarcoma"]
ok("6 'fibrosarcoma'-binned records are annotated Myxofibrosarcoma",
   len(mfs) == 6 and all(a["annotation"].lower().startswith("myxofibrosarcoma") for a in mfs),
   repr([a["annotation"][:22] for a in mfs]))

ann3 = e["platforms"][P3290]["sample_annotations_verbatim"]


def reflabel(a):
    parts = [p.strip() for p in a["annotation"].split("|")]
    return parts[1] if len(parts) > 1 else None


refs = {}
for a in ann3:
    refs.setdefault(a["class"], set()).add(reflabel(a))
ok("GPL3290 EMC reference label is CRH-mRNA on all 10",
   refs.get("EMC") == {"CRH-mRNA"} and len([a for a in ann3 if a["class"] == "EMC"]) == 10, repr(refs))
ok("GPL3290 DFSP reference label is CRH on all 3", refs.get("DFSP") == {"CRH"}, repr(refs))
ok("GPL3290 GIST reference label is UHR on all 3", refs.get("GIST") == {"UHR"}, repr(refs))
ok("GPL3290 value_kind is a two-colour log-ratio vs a reference pool",
   "two-colour log-ratio" in e["platforms"][P3290]["value_kind"], e["platforms"][P3290]["value_kind"][:60])
ok("GPL6244 value_kind is single-channel intensity",
   "single-channel intensity" in e["platforms"][P6244]["value_kind"], e["platforms"][P6244]["value_kind"][:60])

# ---------------------------------------------------------------- 2. seven memberships (F6)
EXPECT = {
    ("transcriptional_cdk", "cdk7_initiation_module"): ["CDK7", "CCNH", "MNAT1"],
    ("transcriptional_cdk", "cdk9_elongation_module"): ["CDK9", "CCNT1", "CCNT2", "AFF4"],
    ("transcriptional_cdk", "cdk12_13_processivity"): ["CDK12", "CDK13", "CCNK"],
    ("transcriptional_cdk", "transcriptional_output_context"): ["POLR2A", "MYC", "GTF2B", "TAF1"],
    ("chaperone_dependency", "hsp90_machine"): ["HSP90AA1", "HSP90AB1", "HSP90B1", "TRAP1"],
    ("chaperone_dependency", "co_chaperones"): ["CDC37", "AHSA1", "STIP1", "PTGES3", "PPID"],
    ("chaperone_dependency", "hsp70_arm_and_stress_response"): ["HSPA8", "HSPA4", "DNAJB1", "HSPH1", "HSF1"],
}
ok("exactly seven scored group memberships", len(EXPECT) == 7)
for (pan, grp), members in EXPECT.items():
    live = e["panels"][pan]["groups"][grp]["genes_requested"]
    ok(f"membership {pan}/{grp}", sorted(live) == sorted(members), f"live={live}")
    for gene in members:
        ok(f"manuscript lists {gene} for {grp}", gene in man, "missing from manuscript text")

UNREADABLE = {("hsp90_machine", P3290): ["HSP90AA1"],
              ("hsp70_arm_and_stress_response", P6244): ["HSPA8"],
              ("hsp70_arm_and_stress_response", P3290): ["HSF1"]}
for (pan, grp), _ in EXPECT.items():
    for plat in (P6244, P3290):
        pp = e["panels"][pan]["groups"][grp]["per_platform"][plat]
        exp_missing = UNREADABLE.get((grp, plat), [])
        ok(f"unreadable members {grp}@{plat}", sorted(pp["genes_not_readable"]) == sorted(exp_missing),
           f"live={pp['genes_not_readable']}")

# ---------------------------------------------------------------- 3. expression table (F7)
ROWS = [  # (panel, group, platform, delta, t, df, coverage) as printed in the manuscript
    ("transcriptional_cdk", "cdk7_initiation_module", P6244, 0.2102, 3.688, 6.6, 1.0),
    ("transcriptional_cdk", "cdk9_elongation_module", P6244, 0.045, 1.189, 5.7, 1.0),
    ("transcriptional_cdk", "cdk12_13_processivity", P6244, -0.0418, -0.88, 6.8, 1.0),
    ("transcriptional_cdk", "transcriptional_output_context", P6244, 0.1983, 3.782, 7.5, 1.0),
    ("chaperone_dependency", "hsp90_machine", P6244, 0.0899, 3.857, 15.0, 1.0),
    ("chaperone_dependency", "co_chaperones", P6244, 0.0809, 1.636, 7.6, 1.0),
    ("chaperone_dependency", "hsp70_arm_and_stress_response", P6244, -0.0853, -1.056, 7.5, 0.8),
    ("transcriptional_cdk", "cdk7_initiation_module", P3290, 0.4966, 4.113, 9.6, 1.0),
    ("transcriptional_cdk", "cdk9_elongation_module", P3290, 0.1737, 2.258, 13.1, 1.0),
    ("transcriptional_cdk", "cdk12_13_processivity", P3290, -0.0751, -0.69, 13.5, 1.0),
    ("transcriptional_cdk", "transcriptional_output_context", P3290, 0.4709, 4.811, 9.8, 1.0),
    ("chaperone_dependency", "hsp90_machine", P3290, 0.6075, 3.465, 11.0, 0.75),
    ("chaperone_dependency", "co_chaperones", P3290, 0.2511, 2.011, 12.0, 1.0),
    ("chaperone_dependency", "hsp70_arm_and_stress_response", P3290, -0.1639, -0.959, 5.9, 0.8),
]
ok("fourteen printed group/platform readings", len(ROWS) == 14)
revmap = {(r["group"], r["platform"]): r for r in rev["expression"]}
bonf_pass = []
for pan, grp, plat, delta, t, df, cov in ROWS:
    pp = e["panels"][pan]["groups"][grp]["per_platform"][plat]
    sc = pp["score"]
    ok(f"delta {grp}@{plat}", sc["delta_a_minus_b"] == delta, f"live={sc['delta_a_minus_b']}")
    ok(f"t {grp}@{plat}", sc["t"] == t, f"live={sc['t']}")
    ok(f"df {grp}@{plat}", sc["df"] == df, f"live={sc['df']}")
    ok(f"coverage {grp}@{plat}", pp["coverage"] == cov, f"live={pp['coverage']}")
    p = t_two_sided_p(t, df)
    se = abs(delta / t)
    tc = t_crit(df)
    lo, hi = delta - tc * se, delta + tc * se
    rv = revmap[(grp, plat)]
    ok(f"p agrees with retained reviewer attempt-2 {grp}@{plat}",
       abs(p - rv["approx_two_sided_p"]) < 1e-9, f"mine={p} reviewer={rv['approx_two_sided_p']}")
    ok(f"interval agrees with retained reviewer attempt-2 {grp}@{plat}",
       abs(lo - rv["approx_95CI_from_rounded_summaries"][0]) < 1e-6
       and abs(hi - rv["approx_95CI_from_rounded_summaries"][1]) < 1e-6,
       f"mine=({lo},{hi}) reviewer={rv['approx_95CI_from_rounded_summaries']}")
    if p < 0.05 / 14:
        bonf_pass.append((grp, plat))
ok("illustrative Bonferroni-14 passes are exactly the three named in the manuscript",
   sorted(bonf_pass) == sorted([("cdk7_initiation_module", P3290),
                                ("transcriptional_output_context", P3290),
                                ("hsp90_machine", P6244)]), repr(bonf_pass))
groups_pass = {gg for gg, _ in bonf_pass}
both = [gg for gg in groups_pass if sum(1 for x, _ in bonf_pass if x == gg) == 2]
ok("no group clears the illustrative Bonferroni-14 threshold on BOTH platforms", not both, repr(both))

# HSP70 intervals include positive differences (F4)
for plat in (P6244, P3290):
    rv = revmap[("hsp70_arm_and_stress_response", plat)]
    ok(f"HSP70 approximate interval includes positive differences @{plat}",
       rv["approx_95CI_from_rounded_summaries"][1] > 0, repr(rv["approx_95CI_from_rounded_summaries"]))

# MYC algebra (F6)
for plat, gdelta, mycd in ((P6244, 0.1983, 1.0625), (P3290, 0.4709, 1.863)):
    live_myc = g["routes"]["RT-TXN-CDK"]["genes"]["MYC"][plat]["delta_emc_minus_comparator"]
    ok(f"MYC delta @{plat}", live_myc == mycd, f"live={live_myc}")
    other3 = (4 * gdelta - mycd) / 3
    rvv = [x for x in rev["transcriptional_context_algebra"] if x["platform"] == plat][0]
    ok(f"other-three algebra agrees with retained reviewer attempt-2 @{plat}",
       abs(other3 - rvv["mean_delta_other_three_by_algebra"]) < 1e-9,
       f"mine={other3} reviewer={rvv['mean_delta_other_three_by_algebra']}")

# proliferation control (F6)
prol = e["panels"]["mtap_prmt5"]["groups"]["proliferation_confound_control"]
ok("proliferation control list has 11 requested members", len(prol["genes_requested"]) == 11,
   repr(prol["genes_requested"]))
mki = e["panels"]["instrument_controls"]["groups"]["proliferation_reference"]
ok("MKI67 proliferation_reference group is one gene and emits no score",
   mki["genes_requested"] == ["MKI67"] and all(pp["score"] is None for pp in mki["per_platform"].values()),
   repr(mki["genes_requested"]))
for plat, t, df, delta in ((P6244, 0.441, 6.7, 0.0896), (P3290, 2.905, 14.0, 0.4459)):
    sc = prol["per_platform"][plat]["score"]
    ok(f"proliferation control stats @{plat}",
       (sc["t"], sc["df"], sc["delta_a_minus_b"]) == (t, df, delta), repr(sc))

# ---------------------------------------------------------------- 4. dependency table (F3)
ok("DepMap release label is 24Q4", "24Q4" in d["data_source"], d["data_source"])
ok("dependent threshold is -0.5", d["dependent_threshold"] == -0.5, repr(d["dependent_threshold"]))
ok("catalogued sarcoma models = 176", d["n_sarcoma_models"] == 176, repr(d["n_sarcoma_models"]))
rows = {r["gene"]: r for grp in d["genes_by_group"].values() for r in grp}
DEP = {"CDK7": (-1.847, -1.762, 0.085, 1.0, 0.999, 91),
       "CDK9": (-1.464, -1.447, 0.017, 1.0, 0.994, 91),
       "HSP90AA1": (-0.23, -0.256, -0.026, 0.055, 0.052, 5),
       "HSP90AB1": (-0.348, -0.275, 0.073, 0.187, 0.119, 17),
       "CDC37": (-1.093, -1.16, -0.067, 0.978, 0.987, 89)}
for gene, (sm, rm, sel, sfd, rfd, ndep) in DEP.items():
    r = rows[gene]
    ok(f"dependency row {gene}",
       (r["sarcoma_mean"], r["rest_mean"], r["selectivity"], r["sarcoma_frac_dependent"],
        r["rest_frac_dependent"], r["n_sarcoma"]) == (sm, rm, sel, sfd, rfd, 91), repr(r))
    compat = [k for k in range(92) if round(k / 91, 3) == sfd]
    ok(f"integer count uniquely compatible with rounded fraction, {gene}",
       compat == [ndep], f"compatible={compat}")
    ok(f"selectivity is rest_mean - sarcoma_mean, {gene}",
       abs((r["rest_mean"] - r["sarcoma_mean"]) - r["selectivity"]) < 5e-4, repr(r))
ok("selectivity definition string in artifact says rest_mean - sarcoma_mean",
   "selectivity = rest_mean - sarcoma_mean" in d["_note"], d["_note"][:120])
ok("artifact records that EMC has no DepMap line", "no DepMap line" in d["_note"], d["_note"][:80])

# self_validation failure (F3)
sv = d["self_validation"]
smarcb1 = rows["SMARCB1"]
ok("SMARCB1 rhabdoid control n/mean/frac as stated",
   (sv["SMARCB1_in_rhabdoid"]["n"], sv["SMARCB1_in_rhabdoid"]["mean_gene_effect"],
    sv["SMARCB1_in_rhabdoid"]["frac_dependent"]) == (13, -0.025, 0.077), repr(sv["SMARCB1_in_rhabdoid"]))
ok("SMARCB1 rest-of-panel mean/frac as stated",
   (smarcb1["rest_mean"], smarcb1["rest_frac_dependent"]) == (-0.832, 0.839), repr(smarcb1))
ok("SMARCB1 control FAILS its stated expected-positive criterion",
   sv["SMARCB1_in_rhabdoid"]["mean_gene_effect"] > smarcb1["rest_mean"]
   and sv["SMARCB1_in_rhabdoid"]["frac_dependent"] < smarcb1["rest_frac_dependent"],
   "control is LESS dependent than the rest of the panel, opposite to _pass_criterion")
ok("BRD9 synovial control values as stated",
   (sv["BRD9_in_synovial"]["n"], sv["BRD9_in_synovial"]["mean_gene_effect"],
    sv["BRD9_in_synovial"]["frac_dependent"]) == (5, -0.13, 0.2), repr(sv["BRD9_in_synovial"]))

# EMC line has no CRISPR data
fd = json.load(open(ROOT + "modalities/fet-ddr-axis-scan.json", encoding="utf-8"))
ok("fet-ddr-axis-scan records emc_line.has_crispr_gene_effect = false",
   fd["emc_line"]["has_crispr_gene_effect"] is False, repr(fd["emc_line"].get("has_crispr_gene_effect")))

# ---------------------------------------------------------------- 5. literature bounds (F8)
qs = {q["id"]: q for q in c["searches_that_returned_nothing_relevant"]["queries"]}
ok("fifteen dated queries", len(qs) == 15, f"n={len(qs)}")
ok("search date is 2026-08-27", c["retrieval"]["date_et"] == "2026-08-27", repr(c["retrieval"]["date_et"]))
ok("Q15 returned 25 hits", qs["Q15"]["hits"] == 25, repr(qs["Q15"]["hits"]))
ok("Q15 outcome records that the hits were not individually screened",
   "Not individually screened" in qs["Q15"]["outcome"], qs["Q15"]["outcome"][:80])
ok("Q13 supplement membership recorded UNKNOWN", "UNKNOWN" in qs["Q13"]["outcome"], qs["Q13"]["outcome"][:80])
ok("preprints/non-PubMed recorded NOT SEARCHED",
   any("NOT SEARCHED" in s for s in c["open_questions_stated_as_unknown"]), "")
ok("manuscript reports Q15's 25 unscreened hits", "25 hits that were not individually screened" in flat)
ok("manuscript reports Q13 supplement unknown", "supplementary panel is unknown" in flat)
ok("manuscript reports preprints/non-PubMed not searched",
   "preprint servers and non-PubMed-indexed sources were not searched" in flat)

# ---------------------------------------------------------------- 6. withdrawn claims absent (F1/F3/F4/F7/F11)
BANNED = [
    "disagree in opposite directions", "opposite disagreement", "most concordant elevation", "largest t-statistics",
    "nothing to select on", "no selective handle", "no selectivity appears anywhere",
    "essentially no selectivity", "internally contradictory",
    "the reading shows none", "not testable singly",
    "one measurement, and it is not an expression question",
    "no producer was run to write it", "the whole literature",
    "buries the chaperone", "burying", "would have been wrong",
]
for phrase in BANNED:
    ok(f"withdrawn phrase absent: {phrase!r}", phrase.lower() not in flat.lower(), "still present")

# Two withdrawn phrases survive ONLY inside an explicit negation, which is the repair itself.
NEGATED_ONLY = {
    "absence of elevation": "do not establish absence of elevation",
    "untestable singly": 'the paralogues are **not** "untestable singly"',
    "abundance and dependency disagree": ("makes **no claim that abundance and "
                                          "dependency disagree**"),
}
for phrase, negated in NEGATED_ONLY.items():
    n_total = flat.lower().count(phrase.lower())
    n_neg = flat.count(negated)
    ok(f"withdrawn phrase {phrase!r} appears only in its explicit negation",
       n_total >= 1 and n_total == n_neg, f"total={n_total} negated={n_neg}")

REQUIRED = [
    "unpaired", "interpretation hold", "24Q4", "gene effect < −0.5", "Soft Tissue or Bone",
    "91 is the denominator", "176", "fails its own criterion", "uncalibrated assumption",
    "exploratory", "Bonferroni", "CDC37's 97.8 % is the measured", "no exhaustive clinical-exposure census",
    "unweighted", "not proliferation matching", "Update conditions", "References",
]
for phrase in REQUIRED:
    ok(f"required content present: {phrase!r}", phrase in flat, "missing")

# ---------------------------------------------------------------- report
out = {"generated_utc": None, "n_checks": len(checks),
       "n_failed": len(fails), "failures": fails, "checks": checks}
import datetime
out["generated_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(out, sys.stdout, indent=1)
print()
sys.exit(1 if fails else 0)
