#!/usr/bin/env python3
"""CARE-DELIVERY-4 validator. Independent assertions over the emitted artifact and
its inputs. Exit 0 only if every assertion passes. Nothing here is weakened, skipped
or made conditional."""
import hashlib, json, os, subprocess, sys

REPO = "/home/user/Rare-cancers"
LANE = os.path.dirname(os.path.abspath(__file__))
INV = os.path.dirname(LANE)
P = lambda *a: os.path.join(*a)
A = json.load(open(P(LANE, "margin-element-scope-audit.json")))
V3 = json.load(open(P(INV, "CARE-DELIVERY-3", "care-delivery-element-coverage-v3.json")))
V2 = json.load(open(P(INV, "CARE-DELIVERY-2", "care-delivery-element-coverage-v2.json")))
V1 = json.load(open(P(INV, "PUB-CARE-DELIVERY", "care-delivery-element-coverage.json")))
IPD = json.load(open(P(REPO, "research/modalities/emc-ipd-survival.json")))
SQ = json.load(open(P(REPO, "research/modalities/emc-surgical-quality.json")))

ok = fail = 0
def check(name, cond):
    global ok, fail
    if cond:
        ok += 1; print(f"PASS  {name}")
    else:
        fail += 1; print(f"FAIL  {name}")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

# --- input integrity ---------------------------------------------------------
for rel, want in A["_reads_only"].items():
    p = P(REPO, rel) if rel.startswith("research/") else P(INV, "CARE-DELIVERY-3", os.path.basename(rel))
    check(f"input hash unchanged: {rel}", sha(p) == want)

# --- nothing shared was written ----------------------------------------------
st = subprocess.run(["git", "status", "--porcelain",
                     "research/modalities", "systems", "research/literature",
                     "research/data", "research/manuscripts"],
                    cwd=REPO, capture_output=True, text=True)
check("git status clean over shared paths", st.returncode == 0 and st.stdout.strip() == "")
mine = subprocess.run(["git", "status", "--porcelain",
                       "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                       "PORTFOLIO-INVESTIGATIONS-2026-09-08/CARE-DELIVERY-2",
                       "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                       "PORTFOLIO-INVESTIGATIONS-2026-09-08/CARE-DELIVERY-3",
                       "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                       "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-CARE-DELIVERY"],
                      cwd=REPO, capture_output=True, text=True)
check("no modification to the three parent lanes", mine.stdout.strip() == "")

# --- part 1: every re-derivation reproduces ----------------------------------
checks = A["part_1_re_derivation_of_the_margin_element"]["checks"]
check("part 1 has 16 checks", len(checks) == 16)
check("part 1 every verdict is REPRODUCES", all(c["verdict"] == "REPRODUCES" for c in checks))
check("part 1 all_reproduce flag true", A["part_1_re_derivation_of_the_margin_element"]["all_reproduce"] is True)
check("no MISMATCH or NOT-RE-DERIVABLE anywhere in the artifact",
      "MISMATCH" not in json.dumps(A) and "NOT-RE-DERIVABLE" not in json.dumps(A))

# --- the margin element partitions the 17 series and the 1,133 patients ------
red = A["part_1_re_derivation_of_the_margin_element"]["rederived_from_the_matrix_rows"]
allser = sorted(sum((red[k]["series"] for k in red), []))
check("margin buckets partition all 17 series", len(allser) == 17 == len(set(allser)))
check("margin buckets cover the matrix exactly", set(allser) == set(V3["coverage_matrix"]))
check("margin bucket patients sum to candidate_patients_sum (1133)",
      sum(red[k]["patients"] for k in red) == V3["candidate_patients_sum"] == 1133)

# --- the two counts CARE-DELIVERY-3 left untouched ---------------------------
check("emc-surgical-quality counts.series == 2", SQ["counts"]["series"] == 2 == len(SQ["series"]))
check("emc-surgical-quality operated_patients_with_a_margin_recorded == 196",
      SQ["counts"]["operated_patients_with_a_margin_recorded"] == 196)
check("196 == 156 + 40, re-derived from the two series blocks",
      196 == sum(SQ["series"][0]["margin_all_registered"][k] for k in ("R0", "R1", "R2"))
             + SQ["series"][1]["margin_field_available_for"])
check("196 is NOT the margin-REPORTED patient total (358) — its scope is the two-series artifact",
      196 != red["REPORTED"]["patients"] == 358)
check("the poolable margin denominator is 239 (156+40+43) and is NOT the 196 the "
      "two-series artifact carries",
      156 + 40 + 43 == 239
      and SQ["counts"]["operated_patients_with_a_margin_recorded"] == 196 != 239)

# --- part 2: design classification -------------------------------------------
D = A["part_2_design_class_of_all_17_candidate_series"]["by_series"]
check("design class assigned to all 17 candidate series", len(D) == 17)
ipdw = {s["source_id"]: s["why_candidate"] for s in IPD["candidate_sources"]}
check("every why_candidate string is copied verbatim from emc-ipd-survival.json",
      all(D[k]["why_candidate_verbatim"] == ipdw[k] for k in D))
check("no series is left DESIGN_NOT_STATED or MIXED_WORDING",
      all(D[k]["design_class"] in ("TRIAL_DESIGN", "NON_TRIAL_DESIGN") for k in D))
trials = A["part_2_design_class_of_all_17_candidate_series"]["trial_design_series"]
check("exactly 4 trial-design series", len(trials) == 4 ==
      A["part_2_design_class_of_all_17_candidate_series"]["n_trial_design_series"])
check("stacchiotti2013anthracycline is NOT classified as a trial",
      D["stacchiotti2013anthracycline"]["design_class"] == "NON_TRIAL_DESIGN"
      and "retrospective" in ipdw["stacchiotti2013anthracycline"])
check("morioka2016trabectedin IS a trial-design series (randomised-trial sub-analysis)",
      "morioka2016trabectedin" in trials)

# --- part 3: the scope test ---------------------------------------------------
S = A["part_3_the_scope_test"]
arith = S["verdict"]["arithmetic"]
check("1 of 4 trial-design series examined for the margin element",
      arith["of_which_examined_for_the_margin_element"] == 1)
check("3 of 4 trial-design series NOT_EXAMINED for the margin element",
      arith["of_which_NOT_EXAMINED_for_the_margin_element"] == 3)
check("the examined trial series is martinbroto2020immunosarc1",
      arith["examined"] == ["martinbroto2020immunosarc1"])
check("morioka margin cell in v3 is NOT_EXAMINED — v3's own artifact asserts no absence",
      V3["coverage_matrix"]["morioka2016trabectedin"]["elements"]
        ["surgical_margin_distribution"]["status"] == "NOT_EXAMINED")
check("the phrase is present in CARE-DELIVERY-3/FINDING.md",
      S["where_it_appears"]["CARE-DELIVERY-3/FINDING.md"] is True)
check("the phrase is ABSENT from the v3 machine-readable artifact",
      S["where_it_appears"]["care-delivery-element-coverage-v3.json"] is False)
check("verdict is the bounded-statement answer, not a claim about the papers",
      S["verdict"]["answer"].startswith("BOUNDED STATEMENT"))

# --- margin counts unchanged from v2, i.e. this lane changed nothing ----------
# CORRECTED after check 02 failed: v3 DID move the margin element. What is unchanged
# between v2 and v3 is the REPORTED bucket only -- which is exactly what
# CARE-DELIVERY-3 §7's "still four series REPORTED, three poolable" asserts. The
# EXAMINED_NOT_PRINTED bucket grew 0 -> 2. Both facts are asserted separately.
check("margin REPORTED bucket identical in v2 and v3 (the 'still four / three poolable' claim)",
      V2["element_counts"]["surgical_margin_distribution"]["REPORTED"]
      == V3["element_counts"]["surgical_margin_distribution"]["REPORTED"])
check("margin EXAMINED_NOT_PRINTED grew 0 -> 2 between v2 and v3, so v3 did read the element",
      V2["element_counts"]["surgical_margin_distribution"]["EXAMINED_NOT_PRINTED"]["n_series"] == 0
      and V3["element_counts"]["surgical_margin_distribution"]["EXAMINED_NOT_PRINTED"]["n_series"] == 2)
check("margin NOT_EXAMINED fell 13 -> 11, and the two that moved are the two table-complete reads",
      V2["element_counts"]["surgical_margin_distribution"]["NOT_EXAMINED"]["n_series"] == 13
      and V3["element_counts"]["surgical_margin_distribution"]["NOT_EXAMINED"]["n_series"] == 11
      and sorted(set(V2["element_counts"]["surgical_margin_distribution"]["NOT_EXAMINED"]["series"])
                 - set(V3["element_counts"]["surgical_margin_distribution"]["NOT_EXAMINED"]["series"]))
          == ["martinbroto2020immunosarc1", "stacchiotti2013anthracycline"])
check("v1 margin REPORTED was 2 series / 230 patients, so 4/358 came from v2's two readings",
      V1["element_counts"]["surgical_margin_distribution"]["REPORTED"]["n_series"] == 2
      and V1["element_counts"]["surgical_margin_distribution"]["REPORTED"]["patients"] == 230)

# --- fences -------------------------------------------------------------------
# the fence scan excludes the two banner fields, which NAME the fenced words in order to
# disclaim them; it scans everything else in the artifact.
_B = {k: v for k, v in A.items() if k not in ("_not_medical_advice",)}
blob = json.dumps(_B, ensure_ascii=False).lower()
for word in ("efficacy", "safe ", "survival benefit", "should be referred",
             "recommend", "pooled rate", "digitis", "digitiz"):
    check(f"no clinical/pooling word '{word.strip()}' in the artifact", word not in blob)
check("artifact carries the not-medical-advice banner", "_not_medical_advice" in A)
check("artifact records that no retrieval was performed", "_no_retrieval" in A)

print(f"\n{ok}/{ok+fail} pass")
sys.exit(0 if fail == 0 else 1)
