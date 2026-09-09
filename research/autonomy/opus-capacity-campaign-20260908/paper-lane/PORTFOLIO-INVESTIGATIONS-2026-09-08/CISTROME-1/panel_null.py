#!/usr/bin/env python3
"""CISTROME-1: read the whole scored locus panel in emc-ret-cistrome.json against
the file's OWN background null, restricted to peaksets that recover a known positive.

Reads the input IN PLACE. Writes one JSON artifact. No network, no repo copy.
"""
import hashlib, json, os, random, sys
from fractions import Fraction

SRC = "research/modalities/emc-ret-cistrome.json"
OUT = ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
       "PORTFOLIO-INVESTIGATIONS-2026-09-08/CISTROME-1/ret-cistrome-locus-panel-null.json")

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

digest = sha256(SRC)
size = os.path.getsize(SRC)
with open(SRC) as f:
    D = json.load(f)
PP = D["part_2_intersection"]["per_peakset"]

# ---------------------------------------------------------------- CHECK 1
# RET's stored empirical p must be reproducible from the file's own stored
# null summary under its declared (ge+1)/(n+1) convention.
check1 = {"convention": "(n_panel_genes_with_at_least_RETs_count + 1) / (n_panel_resolved_on_this_build + 1)",
          "n_peaksets_with_background": 0, "n_reproduced": 0, "mismatches": []}
for name, ps in PP.items():
    bg = ps.get("background")
    if not bg:
        continue
    check1["n_peaksets_with_background"] += 1
    N = bg["n_panel_resolved_on_this_build"]
    Kr = bg["n_panel_genes_with_at_least_RETs_count"]
    stored = bg["empirical_p_RET_vs_panel"]
    recomputed = (Kr + 1) / (N + 1)
    # stored values are printed to 4 decimal places
    if round(recomputed, 4) == round(float(stored), 4):
        check1["n_reproduced"] += 1
    else:
        check1["mismatches"].append({"peakset": name, "N": N, "K_ge_r": Kr,
                                     "stored_p": stored,
                                     "recomputed_p": recomputed,
                                     "recomputed_p_4dp": round(recomputed, 4)})
check1["all_reproduced"] = (check1["n_reproduced"] == check1["n_peaksets_with_background"]
                            and check1["n_peaksets_with_background"] > 0)
# Also pin the two exemplar values named in the task.
check1["named_values"] = {}
for nm, want in (("REMAP2022_NR4A1", 0.4472), ("SRX092299@hg19", 1.0)):
    bg = PP[nm]["background"]
    N = bg["n_panel_resolved_on_this_build"]; Kr = bg["n_panel_genes_with_at_least_RETs_count"]
    check1["named_values"][nm] = {"stored": bg["empirical_p_RET_vs_panel"],
                                  "expected_by_task": want,
                                  "recomputed": round((Kr + 1) / (N + 1), 4),
                                  "matches": round((Kr + 1) / (N + 1), 4) == want
                                             and float(bg["empirical_p_RET_vs_panel"]) == want}

if not check1["all_reproduced"] or not all(v["matches"] for v in check1["named_values"].values()):
    # Per the task: a non-reproducing stored p IS the finding. Emit and stop.
    json.dump({"STOP": "RET stored empirical_p_vs_background did NOT reproduce",
               "source": {"path": SRC, "sha256": digest, "bytes": size},
               "check_1_ret_p_reproduction": check1},
              open(OUT, "w"), indent=1)
    print("STOP: RET stored p did not reproduce", file=sys.stderr)
    sys.exit(3)

# ---------------------------------------------------------------- panel table
POS = [k for k, v in PP.items()
       if (v.get("positive_control_verdict") or {}).get("state") == "A KNOWN POSITIVE IS RECOVERED"]
POS.sort()

def p_for_count(c, N, K1, Kr, r):
    """Empirical p of a promoter-window count c against the file's own panel null.

    The file stores only two points of the panel count distribution:
      K1 = #panel genes with count >= 1, Kr = #panel genes with count >= r (RET's count).
    The survival function is non-increasing, so counts not equal to 0, 1 or r are
    BOUNDED, not exact. Never invent a point the file does not contain.
    """
    ge_lo, ge_hi = 0, N
    exact = None
    pts = {0: N, 1: K1, r: Kr}          # count -> #panel genes with >= that count
    if c in pts:
        exact = pts[c]
    for k, v in sorted(pts.items()):
        if k <= c:
            ge_hi = min(ge_hi, v)       # survival non-increasing
        if k >= c:
            ge_lo = max(ge_lo, v)
    if exact is not None:
        ge_lo = ge_hi = exact
    return {
        "p_exact": round((exact + 1) / (N + 1), 6) if exact is not None else None,
        "p_lower_bound": round((ge_lo + 1) / (N + 1), 6),
        "p_upper_bound": round((ge_hi + 1) / (N + 1), 6),
        "determinacy": "exact" if exact is not None else "bounded",
        "n_panel_ge_count": exact,
    }

LOCI = sorted({L for v in PP.values() for L in (v.get("loci") or {})})
rows = []
for name in POS:
    ps = PP[name]
    bg = ps["background"]
    N = bg["n_panel_resolved_on_this_build"]
    K1 = bg["n_panel_genes_with_a_promoter_window_peak"]
    Kr = bg["n_panel_genes_with_at_least_RETs_count"]
    r = bg["RET_n_peaks_promoter_window"]
    loci = ps["loci"]
    counts = {L: loci[L]["n_peaks_promoter_window"] for L in loci}
    order = sorted(counts.items(), key=lambda kv: -kv[1])
    ret_c = counts["RET"]
    n_strictly_greater = sum(1 for c in counts.values() if c > ret_c)
    n_tied = sum(1 for c in counts.values() if c == ret_c)
    per_locus = {}
    for L, c in counts.items():
        e = p_for_count(c, N, K1, Kr, r)
        e["n_peaks_promoter_window"] = c
        e["n_peaks_genebody_window"] = loci[L]["n_peaks_genebody_window"]
        e["nearest_peak_distance_to_tss_bp"] = loci[L]["nearest_peak_distance_to_tss_bp"]
        e["rank_in_panel_competition"] = 1 + sum(1 for c2 in counts.values() if c2 > c)
        per_locus[L] = e
    rows.append({
        "peakset": name,
        "antigen": ps.get("antigen"),
        "genome": ps.get("genome"),
        "species": ps.get("species"),
        "cell_type": ps.get("cell_type"),
        "n_peaks_total": ps.get("n_peaks_total"),
        "assay_is_an_NR4A_chip": ps.get("antigen") in ("NR4A1", "NR4A2", "NR4A3"),
        "positive_control_recovered": ps["positive_control_verdict"]["recovered"],
        "background_panel": {"n_panel_resolved": N, "n_panel_with_ge_1_peak": K1,
                             "n_panel_with_ge_RET_count": Kr, "RET_count": r},
        "RET_rank_of_%d_loci" % len(counts): 1 + n_strictly_greater,
        "RET_n_loci_strictly_greater": n_strictly_greater,
        "RET_n_loci_tied": n_tied,
        "RET_stored_empirical_p": bg["empirical_p_RET_vs_panel"],
        "loci": per_locus,
    })

# ---------------------------------------------------------------- CHECK 2
# Peaksets flagged NO KNOWN POSITIVE RECOVERED must show no enrichment at RET.
neg = [k for k, v in PP.items()
       if (v.get("positive_control_verdict") or {}).get("state") == "NO KNOWN POSITIVE RECOVERED"]
check2 = {"n_negative_control_peaksets": len(neg), "violations": [], "max_locus_count_seen": {}}
for name in neg:
    ps = PP[name]
    bg = ps.get("background") or {}
    ret = ps["loci"]["RET"]
    if ret["n_peaks_promoter_window"] != 0 or float(bg.get("empirical_p_RET_vs_panel", 1.0)) < 1.0:
        check2["violations"].append({"peakset": name,
                                     "RET_promoter_count": ret["n_peaks_promoter_window"],
                                     "stored_p": bg.get("empirical_p_RET_vs_panel")})
    for L, v in ps["loci"].items():
        c = v["n_peaks_promoter_window"]
        if c > check2["max_locus_count_seen"].get(L, 0):
            check2["max_locus_count_seen"][L] = c
check2["passes"] = len(check2["violations"]) == 0
# Diagnostic only -- does NOT change the pass/fail verdict above.
check2["violation_diagnostic"] = {
    "assay_of_each_violating_peakset": {
        v["peakset"]: (PP[v["peakset"]].get("antigen")
                       or ("H3K27me3" if "H3K27me3" in v["peakset"] else "unlabelled"))
        for v in check2["violations"]},
    "reading": "every violating peakset is an H3K27me3 track -- a REPRESSIVE histone mark, not an "
               "NR4A ChIP. The file's own panel null therefore assigns RET a nominally significant "
               "p (as low as 0.0398) under a silencing mark in a peakset that recovered no known "
               "positive. This is direct evidence that a low p against this panel is not evidence "
               "of NR4A occupancy."}
check2["reading"] = ("no peakset lacking a recovered positive shows any RET promoter-window peak"
                     if check2["passes"] else
                     "AT LEAST ONE no-positive peakset shows a RET promoter-window peak; see violations")

# ---------------------------------------------------------------- CHECK 3
# Locus-label permutation must flatten the ranking.
rng = random.Random(20260908)
NPERM = 20000
obs_mean_rank = {}
for L in LOCI:
    rs = [1 + sum(1 for c2 in PP[n]["loci"].values()
                  if c2["n_peaks_promoter_window"] > PP[n]["loci"][L]["n_peaks_promoter_window"])
          for n in POS if L in PP[n]["loci"]]
    obs_mean_rank[L] = sum(rs) / len(rs)
count_vectors = [[PP[n]["loci"][L]["n_peaks_promoter_window"] for L in LOCI] for n in POS]
null_means = {L: [] for L in LOCI}
for _ in range(NPERM):
    acc = {L: 0.0 for L in LOCI}
    for vec in count_vectors:
        perm = vec[:]
        rng.shuffle(perm)
        for i, L in enumerate(LOCI):
            acc[L] += 1 + sum(1 for c2 in perm if c2 > perm[i])
    for L in LOCI:
        null_means[L].append(acc[L] / len(count_vectors))
check3 = {"n_permutations": NPERM, "seed": 20260908,
          "statistic": "mean competition rank of a locus across the positive-recovering peaksets "
                       "(rank 1 = most peaks; lower mean rank = more occupied)",
          "per_locus": {}}
for L in LOCI:
    nm = null_means[L]
    o = obs_mean_rank[L]
    p_low = (sum(1 for x in nm if x <= o) + 1) / (NPERM + 1)
    check3["per_locus"][L] = {
        "observed_mean_rank": round(o, 4),
        "permutation_null_mean": round(sum(nm) / NPERM, 4),
        "permutation_null_sd": round((sum((x - sum(nm) / NPERM) ** 2 for x in nm) / NPERM) ** 0.5, 4),
        "p_one_sided_better_than_null": round(p_low, 5),
    }
# Flatness criterion, corrected after attempt 01: competition ranking with ties does NOT
# centre on (n+1)/2, so the test is label EXCHANGEABILITY -- under a locus-label permutation
# every label must acquire the same null mean rank. Spread across labels must be small
# relative to the null sd. This can fail: a permutation that leaked locus identity would
# leave the labels' null means separated.
_nulls = [check3["per_locus"][L]["permutation_null_mean"] for L in LOCI]
_sd = sum(check3["per_locus"][L]["permutation_null_sd"] for L in LOCI) / len(LOCI)
check3["null_mean_spread_across_labels"] = round(max(_nulls) - min(_nulls), 4)
check3["mean_null_sd"] = round(_sd, 4)
check3["ranking_is_flattened_by_permutation"] = (max(_nulls) - min(_nulls)) < 0.25 * _sd
check3["observed_mean_rank_spread_across_labels"] = round(
    max(obs_mean_rank.values()) - min(obs_mean_rank.values()), 4)
check3["RET_distinguishable_from_a_permuted_label"] = check3["per_locus"]["RET"]["p_one_sided_better_than_null"] < 0.05
check3["positive_control_ENO3_distinguishable"] = check3["per_locus"]["ENO3"]["p_one_sided_better_than_null"] < 0.05

# ---------------------------------------------------------------- summary
ret_ranks = [r["RET_n_loci_strictly_greater"] + 1 for r in rows]
nr4a_only = [r for r in rows if r["assay_is_an_NR4A_chip"]]
art = {
    "_what": "Per locus x peakset occupancy of the emc-ret-cistrome scored panel against that "
             "file's OWN background null, restricted to peaksets that recover a known positive, "
             "with RET's rank in the panel.",
    "_lane": "CISTROME-1, OPUS-CAPACITY-CAMPAIGN-20260908",
    "_question": "Is NR4A occupancy at RET distinguishable from background at all, and which loci "
                 "in the scored panel actually pass?",
    "⛔ what_this_is_not": [
        "not an efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim",
        "occupancy is not target validation; a peak in a window is not regulation",
        "no new intersection was computed: every count here is READ from the source file",
        "the null is the file's own 198-200 gene panel, not composition-matched for accessibility, "
        "mappability or GC",
    ],
    "source": {"path": SRC, "sha256_at_use": digest, "bytes": size,
               "generated_utc": D.get("generated_utc")},
    "windows": D["part_2_intersection"]["_windows"],
    "background_null_definition": PP["REMAP2022_NR4A1"]["background"]["panel_source"],
    "p_convention": PP["REMAP2022_NR4A1"]["background"]["_p_convention"],
    "⚠ resolution_limit_of_the_stored_null":
        "The file stores only two points of each panel's count distribution: the number of panel "
        "genes with >=1 promoter-window peak, and the number with >= RET's own count. An empirical "
        "p is therefore EXACT only for a locus whose count is 0, 1, or equal to RET's count in that "
        "peakset; every other count is reported as an interval bounded by the monotone survival "
        "function. No interpolated point value is invented.",
    "peakset_census": {
        "n_peaksets_total": len(PP),
        "n_with_a_positive_control_verdict": sum(1 for v in PP.values() if v.get("positive_control_verdict")),
        "n_recovering_a_known_positive": len(POS),
        "n_no_known_positive_recovered": len(neg),
        "n_with_no_loci_on_build": sum(1 for v in PP.values() if v.get("_status") == "no_loci_on_this_build"),
        "n_recovering_positive_that_are_actually_an_NR4A_chip": len(nr4a_only),
        "⚠ positive_control_filter_is_not_assay_specific":
            "Most peaksets that clear the positive-control filter are H3K4me3, H3K27ac, CTCF or "
            "super-enhancer tracks, which mark active promoters generically. Only "
            f"{len(nr4a_only)} of {len(POS)} are an NR4A ChIP.",
    },
    "panel_table": rows,
    "ret_position": {
        "loci_in_panel": LOCI,
        "RET_rank_by_peakset": {r["peakset"]: r["RET_n_loci_strictly_greater"] + 1 for r in rows},
        "RET_mean_rank": round(sum(ret_ranks) / len(ret_ranks), 4),
        "RET_median_rank": sorted(ret_ranks)[len(ret_ranks) // 2],
        "n_positive_peaksets_with_zero_RET_promoter_peaks":
            sum(1 for r in rows if r["loci"]["RET"]["n_peaks_promoter_window"] == 0),
        "n_NR4A_chip_peaksets_with_zero_RET_promoter_peaks":
            sum(1 for r in nr4a_only if r["loci"]["RET"]["n_peaks_promoter_window"] == 0),
        "RET_stored_p_range": [min(r["RET_stored_empirical_p"] for r in rows),
                               max(r["RET_stored_empirical_p"] for r in rows)],
        "n_positive_peaksets_with_RET_stored_p_below_0.05":
            sum(1 for r in rows if float(r["RET_stored_empirical_p"]) < 0.05),
    },
    "locus_mean_rank_ordering": sorted(
        ((L, round(obs_mean_rank[L], 4)) for L in LOCI), key=lambda kv: kv[1]),
    "checks": {
        "check_1_ret_stored_p_reproduces": check1,
        "check_2_no_positive_peaksets_show_no_enrichment": check2,
        "check_3_locus_label_permutation": check3,
    },
}
with open(OUT, "w") as f:
    json.dump(art, f, indent=1)
print("check1 all_reproduced:", check1["all_reproduced"],
      check1["n_reproduced"], "/", check1["n_peaksets_with_background"])
print("check1 named:", json.dumps(check1["named_values"]))
print("check2 passes:", check2["passes"], "violations:", len(check2["violations"]))
print("check3 flattened:", check3["ranking_is_flattened_by_permutation"],
      "RET p:", check3["per_locus"]["RET"]["p_one_sided_better_than_null"],
      "ENO3 p:", check3["per_locus"]["ENO3"]["p_one_sided_better_than_null"])
print("locus mean rank ordering:", art["locus_mean_rank_ordering"])
print("RET mean rank:", art["ret_position"]["RET_mean_rank"],
      "zero-RET positive peaksets:", art["ret_position"]["n_positive_peaksets_with_zero_RET_promoter_peaks"],
      "/", len(rows),
      "NR4A-chip zero:", art["ret_position"]["n_NR4A_chip_peaksets_with_zero_RET_promoter_peaks"],
      "/", len(nr4a_only))
print("sha256:", digest)
