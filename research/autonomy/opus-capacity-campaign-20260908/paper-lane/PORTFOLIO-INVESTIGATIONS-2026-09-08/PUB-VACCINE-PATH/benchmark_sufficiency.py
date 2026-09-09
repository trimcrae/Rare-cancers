#!/usr/bin/env python3
"""PUB-VACCINE-PATH portfolio lane, 2026-09-08.

Question: on the public evidence, is the threshold-calibration bottleneck (B1 / Section 6.1
step 1 of emc-vaccine-development-path.md) rate-limiting because the validated epitope set is
absent, or because the collector never took the reading -- and how large must that benchmark
be before it can decide anything?

Entirely offline. Inputs are two committed artifacts and one committed script in this tree.
No network, no predictor, no new scientific measurement. Nothing here is a claim about
presentation, immunogenicity, efficacy, safety or clinical readiness.
"""
import json, math, re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[6]
CAL = ROOT / "research/modalities/vaccine-threshold-calibration.json"
SCRIPT = ROOT / "research/modalities/vaccine_threshold_calibration.py"

art = json.loads(CAL.read_text())
src = SCRIPT.read_text()

# ---- 1. Why arm F is empty: classify every recorded failure -------------------------------
errs = art["errors"]
buckets = collections.Counter()
for e in errs:
    if "offset parameter without an order parameter" in e:
        buckets["postgrest_400_offset_without_order"] += 1
    elif "HTTPError" in e:
        buckets["other_http_error"] += 1
    elif "URLError" in e or "CONNECT" in e or "403" in e:
        buckets["transport_or_egress"] += 1
    else:
        buckets["unclassified"] += 1
offset_urls = [e for e in errs if "offset=" in e]
order_absent = [e for e in offset_urls if "order=" not in e.split("->")[0]]

diagnosis = {
    "n_errors": len(errs),
    "classes": dict(buckets),
    "n_error_urls_carrying_offset": len(offset_urls),
    "n_of_those_carrying_no_order": len(order_absent),
    "server_reached": bool(buckets["postgrest_400_offset_without_order"]),
    "reading": (
        "Every recorded failure is one client-side PostgREST 400 -- offset sent without order -- "
        "and the body was returned BY the API, so the host was reachable on that run. Arm F's zero "
        "is a reading the collector could not take, not a reading of absence. The artifact already "
        "withholds the absence claim on its own guard."
    ),
    "arm_F_n_distinct_epitopes_recorded": art["verdict"]["n_distinct_validated_fusion_junction_epitopes"],
    "artifact_finding_verbatim": art["verdict"]["finding"],
}

# ---- 2. Static audit of the committed fix -------------------------------------------------
paging_sites = [m.start() for m in re.finditer(r"offset=\{", src)]
sites = []
for pos in paging_sites:
    window = src[max(0, pos - 400):pos + 40]
    sites.append({"char_offset": pos, "carries_order_param": "&order=" in window})
order_by = re.search(r'^ORDER_BY\s*=\s*"([^"]+)"', src, re.M).group(1)
cols = art["_schema_discovery"]["columns_of_tables_used"]
unique_candidates = {t: sorted(c for c in v if c in ("elution_id", "tcell_id", "structure_id"))
                     for t, v in cols.items()}
audit = {
    "n_paging_sites": len(sites),
    "n_paging_sites_carrying_order": sum(s["carries_order_param"] for s in sites),
    "order_by_column": order_by,
    "order_by_present_in_every_used_table": all(order_by in v for v in cols.values()),
    "order_by_is_row_unique": False,
    "residual_defect": (
        "order=linear_sequence is not a unique key: one peptide sequence recurs across alleles, "
        "assays and references, so limit/offset paging over a non-unique sort key has no total "
        "order and rows can be SKIPPED as well as repeated between pages. fetch_table dedupes "
        "repeats with `seen`, which hides duplication but cannot recover a skip. Arm F's probes "
        "are declared exhaustive (MAX_PAGES=60 x 1000 rows), and an undercount there lands "
        "directly on the preregistered min_n gate."
    ),
    "row_unique_columns_available_in_the_live_schema": unique_candidates,
    "proposed_repair": "order=<row-unique id>  (elution_id for mhc_search, tcell_id for tcell_search), "
                       "or order=linear_sequence,<row-unique id> to keep the current grouping.",
    "not_applied_here": "This lane writes only under its own directory; the repair is stated, not applied.",
}

# ---- 3. How big must the benchmark be? ----------------------------------------------------
def wilson(k, n, z=1.959963985):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))

def beta_quantile(a, b, q, lo=0.0, hi=1.0):
    # regularised incomplete beta by bisection on a continued-fraction-free series is overkill;
    # bisect on the binomial tail instead (exact Clopper-Pearson via search on p).
    return None

def cp_interval(k, n):
    """Exact Clopper-Pearson by bisection on the binomial tail (no scipy in this environment)."""
    def tail_le(p, k, n):  # P(X <= k)
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))
    def tail_ge(p, k, n):  # P(X >= k)
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))
    lo, hi = 0.0, 1.0
    if k == 0:
        low = 0.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            m = (a + b) / 2
            if tail_ge(m, k, n) < 0.025:
                a = m
            else:
                b = m
        low = (a + b) / 2
    if k == n:
        high = 1.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            m = (a + b) / 2
            if tail_le(m, k, n) > 0.025:
                a = m
            else:
                b = m
        high = (a + b) / 2
    return (low, high)

pre = art["_preregistered"]
min_n, max_w = pre["min_n_for_a_calibration"], pre["max_ci_width_for_a_calibration"]

at_min_n = []
for k in range(0, min_n + 1):
    w_lo, w_hi = wilson(k, min_n)
    c_lo, c_hi = cp_interval(k, min_n)
    at_min_n.append({"k": k, "sensitivity": k / min_n,
                     "wilson_width": w_hi - w_lo, "cp_width": c_hi - c_lo,
                     "meets_ci_width_wilson": (w_hi - w_lo) <= max_w,
                     "meets_ci_width_cp": (c_hi - c_lo) <= max_w})
pass_w = [r["sensitivity"] for r in at_min_n if r["meets_ci_width_wilson"]]
pass_c = [r["sensitivity"] for r in at_min_n if r["meets_ci_width_cp"]]

def n_for_width(p, w, exact=False):
    for n in range(2, 4001):
        k = round(p * n)
        lo, hi = cp_interval(k, n) if exact else wilson(k, n)
        if (hi - lo) <= w:
            return n
    return None

required = {f"sensitivity_{p}": {"wilson": n_for_width(p, max_w),
                                 "clopper_pearson": n_for_width(p, max_w, exact=True)}
            for p in (0.5, 0.7, 0.8, 0.9)}

benchmark = {
    "preregistered_gate": {"min_n": min_n, "max_ci_width": max_w,
                           "source": "vaccine-threshold-calibration.json::_preregistered"},
    "at_min_n_the_two_criteria_are_jointly_satisfiable_only_for": {
        "wilson_sensitivities": pass_w, "clopper_pearson_sensitivities": pass_c},
    "n_required_for_the_declared_ci_width": required,
    "reading": (
        "The preregistered floor of 30 epitopes and the preregistered CI-width ceiling of 0.20 are "
        "jointly satisfiable at n=30 only when the observed sensitivity is near 0 or near 1. In the "
        "regime where the acceptance cut actually matters -- an intermediate sensitivity, which is "
        "what separates 0.5 from 0.2 -- n=30 cannot meet the declared width. The benchmark this "
        "route needs is roughly 3x the preregistered floor at sensitivity 0.5 and about 1.5-2x it "
        "even at sensitivity 0.9. The floor is a floor, not a sufficient size, and reporting it as "
        "the gate understates the set a defensible cut would take."
    ),
    "what_this_does_not_settle": (
        "Whether IEDB holds that many experimentally validated class I epitopes from fusion or "
        "chimeric source antigens is UNKNOWN and unmeasured here: this environment cannot reach "
        "query-api.iedb.org (CONNECT 403, checks/01-iedb-probe), and the only run that reached it "
        "failed on the paging bug above. The published fusion-junction epitopes the manuscript "
        "itself names are single-digit; IEDB may hold more, and that count is the measurement."
    ),
}

out = {
    "_lane": "PUB-VACCINE-PATH",
    "_campaign": "OPUS-CAPACITY-CAMPAIGN-20260908",
    "_date": "2026-09-08",
    "_question": (
        "Is Section 6.1 step 1 (defend the acceptance threshold) rate-limiting because the validated "
        "fusion-junction epitope set is absent, or because it was never measured -- and how large "
        "would that benchmark have to be to decide the cut?"
    ),
    "_inputs": {
        "artifact": "research/modalities/vaccine-threshold-calibration.json (run 2026-09-01T20:31:04Z)",
        "script": "research/modalities/vaccine_threshold_calibration.py (HEAD)",
        "manuscript": "research/manuscripts/neoantigen/emc-vaccine-development-path.md",
    },
    "_no_claims": (
        "No efficacy, safety, presentation, immunogenicity or clinical-readiness claim. A threshold "
        "benchmark is an instrument calibration and nothing else. No wet lab. No new cohort."
    ),
    "why_arm_F_is_empty": diagnosis,
    "static_audit_of_the_committed_fix": audit,
    "benchmark_sufficiency": benchmark,
}
print(json.dumps(out, indent=1))
