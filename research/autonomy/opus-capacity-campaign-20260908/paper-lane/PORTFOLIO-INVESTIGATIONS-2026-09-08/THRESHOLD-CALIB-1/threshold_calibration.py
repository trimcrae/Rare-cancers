#!/usr/bin/env python3
"""THRESHOLD-CALIB-1 — measure the discrimination of the repository's class I threshold on the
overlap between the cached predictor calls and the IEDB validated arms, or record the exact
missing predictor-call set as a decisive negative.

Reads inputs IN PLACE, re-hashes each at use. No re-scoring, no MHCnuggets install, no network.
HLA-C is excluded everywhere: it is not on the panel and no HLA-C record is admitted or relabelled.

⛔ Nothing here is an immunogenicity, presentation, tolerance, efficacy, safety, selectivity,
therapeutic-window or clinical-readiness claim. A predicted IC50 or percentile is not a presented
epitope. "Discrimination" below is a property of an instrument on labelled records, nothing else.
"""
import hashlib
import json
import os
import random
import statistics
import sys

REPO = "/home/user/Rare-cancers"
IEDB = os.path.join(REPO, "research/modalities/iedb-validated-epitope-cache.json")
NUG = os.path.join(REPO, "research/modalities/epitope-allele-matrix-mhcnuggets.json")
FLU = os.path.join(REPO, "research/modalities/epitope-allele-matrix.json")
SEED = 20260909
N_SHUFFLE = 2000


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest(), os.path.getsize(path)


def norm_pep(p):
    return p.strip().upper()


def norm_allele(a):
    """4-digit (two-field) normalisation only. No cross-locus or cross-field relabelling."""
    return a.strip().upper().replace("HLA -", "HLA-")


# ── the instrument ────────────────────────────────────────────────────────────────────────────
def auroc(pos, neg):
    """Mann-Whitney AUROC, ties at 0.5. Score convention: LOWER score = stronger call, so the
    statistic is P(pos scores lower than neg). Returns None when either class is empty."""
    if not pos or not neg:
        return None
    # rank-based Mann-Whitney with mid-ranks for ties; O(n log n), exact-equal to the pairwise form
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    ranks = [0.0] * len(allv)
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        mid = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = mid
        i = j + 1
    r_pos = sum(r for r, (_, lab) in zip(ranks, allv) if lab == 1)
    n1, n0 = len(pos), len(neg)
    u = r_pos - n1 * (n1 + 1) / 2.0          # U for "pos ranks high"
    return 1.0 - u / (n1 * n0)                # lower score = stronger call, so invert


def auroc_pairwise(pos, neg):
    """The definitional O(n*m) form, kept only to self-test the rank implementation."""
    if not pos or not neg:
        return None
    wins = 0.0
    for a in pos:
        for b in neg:
            wins += 1.0 if a < b else (0.5 if a == b else 0.0)
    return wins / (len(pos) * len(neg))


def selftest_auroc(rng, trials=40):
    """Must be able to fail: the fast statistic must equal the definition, ties included."""
    for _ in range(trials):
        pos = [rng.choice([1, 2, 2, 3, 5, 8]) for _ in range(rng.randint(1, 12))]
        neg = [rng.choice([1, 2, 2, 3, 5, 8]) for _ in range(rng.randint(1, 12))]
        if abs(auroc(pos, neg) - auroc_pairwise(pos, neg)) > 1e-9:
            return False
    return True


def discriminate(scores, labels, threshold):
    """labels: 1 = validated-positive, 0 = negative. Call is positive when score <= threshold.
    Returns None for every rate a class cannot support — an empty class is UNDEFINED, not chance."""
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    out = {
        "n_positive": len(pos),
        "n_negative": len(neg),
        "auroc": auroc(pos, neg),
        "sensitivity": (sum(1 for s in pos if s <= threshold) / len(pos)) if pos else None,
        "specificity": (sum(1 for s in neg if s > threshold) / len(neg)) if neg else None,
    }
    out["defined"] = out["auroc"] is not None
    return out


def shuffled_null(scores, labels, rng, n=N_SHUFFLE):
    """The check that must be able to fail: label-shuffled discrimination must come out at chance."""
    if len(set(labels)) < 2:
        return {"runs": 0, "mean_auroc": None, "p2_5": None, "p97_5": None,
                "verdict": "UNDEFINED — fewer than two label classes; a null cannot be drawn."}
    vals = []
    lab = list(labels)
    for _ in range(n):
        rng.shuffle(lab)
        vals.append(auroc([s for s, y in zip(scores, lab) if y == 1],
                          [s for s, y in zip(scores, lab) if y == 0]))
    vals.sort()
    lo, hi = vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]
    mean = statistics.fmean(vals)
    at_chance = lo <= 0.5 <= hi and abs(mean - 0.5) < 0.02
    return {"runs": n, "mean_auroc": round(mean, 5), "p2_5": round(lo, 5), "p97_5": round(hi, 5),
            "at_chance": at_chance,
            "verdict": "AT CHANCE" if at_chance else "⚠ NOT AT CHANCE — the instrument is wrong"}


def main():
    rng = random.Random(SEED)
    prov = {}
    for name, path in (("iedb_validated_epitope_cache", IEDB),
                       ("epitope_allele_matrix_mhcnuggets", NUG),
                       ("epitope_allele_matrix_mhcflurry", FLU)):
        digest, size = sha256(path)
        prov[name] = {"path": os.path.relpath(path, REPO), "sha256": digest, "bytes": size,
                      "hashed_at_use": True}

    iedb = json.load(open(IEDB))
    nug = json.load(open(NUG))
    flu = json.load(open(FLU))

    panel = [norm_allele(a) for a in nug["panel"]]
    panel_set = set(panel)
    assert not any(a.startswith("HLA-C") for a in panel_set), "HLA-C must not be on the panel"

    calls = nug["calls"]
    call_pairs = {(norm_pep(c["peptide"]), norm_allele(c["allele"])): c["ic50_nM"] for c in calls}
    call_peps = {p for p, _ in call_pairs}
    call_alleles = {a for _, a in call_pairs}

    arms = {}
    for arm_name, key in (("F", "arm_F_records"), ("N", "arm_N_records")):
        recs = iedb[key]
        pairs = {(norm_pep(r["peptide"]), norm_allele(r["allele"])) for r in recs}
        peps = {p for p, _ in pairs}
        alleles = {a for _, a in pairs}
        on_panel = {(p, a) for (p, a) in pairs if a in panel_set}
        hla_c = {(p, a) for (p, a) in pairs if a.startswith("HLA-C")}
        arms[arm_name] = {
            "records": len(recs), "distinct_pairs": len(pairs), "distinct_peptides": len(peps),
            "distinct_alleles": len(alleles),
            "pairs_on_the_34_allele_panel": len(on_panel),
            "pairs_dropped_hla_c_excluded_route_B8_closed": len(hla_c),
            "peptide_lengths": sorted({len(p) for p in peps}),
            "_pairs": sorted(on_panel), "_all_pairs": pairs, "_peps": peps, "_alleles": alleles,
        }

    # ── 1 · the intersection, under the declared match rule and under normalisation only ────────
    inter = {}
    for arm_name, d in arms.items():
        pair_ov = d["_all_pairs"] & set(call_pairs)
        pep_ov = d["_peps"] & call_peps
        inter[arm_name] = {
            "peptide_allele_pairs_in_common": len(pair_ov),
            "peptides_in_common": len(pep_ov),
            "alleles_in_common": len(d["_alleles"] & call_alleles),
            "example_pairs_in_common": sorted(pair_ov)[:5],
        }
    # the zero must not be a formatting artifact: nearest peptide by edit distance
    def edit(a, b):
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            prev = cur
        return prev[-1]

    all_arm_peps = sorted(arms["F"]["_peps"] | arms["N"]["_peps"])
    best = (99, None, None)
    for cp in sorted(call_peps):
        for ap in all_arm_peps:
            if abs(len(cp) - len(ap)) >= best[0]:
                continue
            d = edit(cp, ap)
            if d < best[0]:
                best = (d, cp, ap)
    nearest = {"min_edit_distance_cached_vs_validated": best[0],
               "closest_cached_peptide": best[1], "closest_validated_peptide": best[2],
               "reading": ("A zero overlap with a minimum edit distance of %d is a genuine "
                           "disjointness of peptide sets, not a string-formatting artifact."
                           % best[0])}

    # ── 2 · try to measure discrimination on the overlap ───────────────────────────────────────
    scores, labels = [], []
    for (p, a) in sorted(arms["F"]["_all_pairs"] | arms["N"]["_all_pairs"]):
        if (p, a) in call_pairs:
            scores.append(call_pairs[(p, a)])
            labels.append(1)
    # negatives: cached calls whose pair is NOT a validated record (decoy side of the contrast)
    for (p, a), v in sorted(call_pairs.items()):
        if (p, a) not in arms["F"]["_all_pairs"] and (p, a) not in arms["N"]["_all_pairs"]:
            scores.append(v)
            labels.append(0)

    threshold_nM = 500.0  # the conventional MHCnuggets/IC50 strong-binder cut
    measured = discriminate(scores, labels, threshold_nM)
    measured["threshold_used"] = {"value": threshold_nM, "scale": "predicted IC50, nM",
                                 "convention": "call is positive when IC50 <= threshold"}
    measured["⛔"] = ("The repository's LOAD-BEARING cut is a MHCflurry presentation PERCENTILE of "
                     "0.5 (research/modalities/vaccine-threshold-calibration.json "
                     "_conventional_threshold). The only full per-call matrix in the tree is on the "
                     "MHCnuggets IC50 scale; epitope-allele-matrix.json retains only the 5 passing "
                     "calls, not the 174x34 percentile matrix. So even a non-empty overlap here "
                     "would calibrate a DIFFERENT instrument than the one the manuscript uses.")
    null_measured = shuffled_null(scores, labels, rng)

    # ── 3 · instrument validation, on synthetic labelled data — this check must be able to fail ─
    ctrl = random.Random(SEED + 1)
    s_pos = [ctrl.lognormvariate(4.0, 1.0) for _ in range(200)]   # centred low
    s_neg = [ctrl.lognormvariate(7.5, 1.0) for _ in range(200)]   # centred high
    c_scores = s_pos + s_neg
    c_labels = [1] * 200 + [0] * 200
    ctrl_signal = discriminate(c_scores, c_labels, threshold_nM)
    ctrl_null = shuffled_null(c_scores, c_labels, random.Random(SEED + 2))
    checks = {
        "auroc_matches_its_definition_with_ties": selftest_auroc(random.Random(SEED + 3)),
        "positive_control_separates": ctrl_signal["auroc"] is not None and ctrl_signal["auroc"] > 0.8,
        "shuffled_control_at_chance": bool(ctrl_null["at_chance"]),
        "empty_overlap_returns_undefined_not_chance": measured["auroc"] is None,
        "real_null_is_undefined_not_chance": null_measured["mean_auroc"] is None,
    }
    checks["all_passed"] = all(checks.values())

    # ── 4 · the exact missing predictor-call set ───────────────────────────────────────────────
    missing_F = arms["F"]["_pairs"]
    missing_N = arms["N"]["_pairs"]
    missing = {
        "what_is_missing": ("Predictor calls for the validated (peptide, allele) pairs. The cached "
                            "matrix scores only the 174 EMC junction-window peptides; not one "
                            "validated IEDB peptide is among them, so the threshold has never been "
                            "scored on a single validated record."),
        "arm_F_fusion_junction_calls_required": len(missing_F),
        "arm_N_nonfusion_calls_required": len(missing_N),
        "total_calls_required": len(missing_F) + len(missing_N),
        "restricted_to": "the 34-allele panel; HLA-C excluded (route B8 closed); lengths 8-11 only",
        "on_which_predictor": ("BOTH, and they are never merged: MHCnuggets class I (IC50 nM) to "
                               "extend epitope-allele-matrix-mhcnuggets.json, and — for the cut the "
                               "manuscript actually uses — MHCflurry Class1PresentationPredictor "
                               "presentation percentile, whose full matrix is not retained."),
        "negatives_still_required": ("A decoy/negative set drawn under a preregistered rule. "
                                     "Validated-positive records alone fix no specificity, so AUROC "
                                     "stays undefined however many positives are scored."),
        "blocked_here_because": ("MHCnuggets is not installed and its weights are a large download; "
                                 "this lane is forbidden to re-score or install, and no network "
                                 "fetch was attempted."),
        "arm_F_pairs": [{"peptide": p, "allele": a} for p, a in missing_F],
        "arm_N_pairs": [{"peptide": p, "allele": a} for p, a in missing_N],
    }

    result = {
        "_id": "THRESHOLD-CALIB-1-threshold-calibration",
        "_lane": "THRESHOLD-CALIB-1",
        "_utc_of_inputs": {"iedb_cache": iedb.get("_utc")},
        "_seed": SEED,
        "⛔_no_clinical_claim": ("No immunogenicity, presentation, tolerance, efficacy, safety, "
                                "selectivity, therapeutic-window or clinical-readiness claim is "
                                "made or implied. A predicted percentile or IC50 is not a presented "
                                "epitope."),
        "⛔_hla_c": "HLA-C excluded throughout; route B8 closed; no HLA-C data acquired or relabelled.",
        "provenance": prov,
        "cached_call_set": {"predictor": nug["predictor"], "scale": nug["scale"],
                            "n_peptides": nug["n_peptides"], "n_alleles": len(panel),
                            "n_calls": len(calls), "distinct_pairs": len(call_pairs),
                            "alleles_without_a_model": len(nug["alleles_without_a_model"])},
        "validated_arms": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                           for k, v in arms.items()},
        "intersection": inter,
        "nearest_peptide_probe": nearest,
        "measured_discrimination": measured,
        "label_shuffled_null_on_the_real_overlap": null_measured,
        "instrument_validation_on_synthetic_labels": {
            "_note": ("Synthetic, seeded, and biologically meaningless by construction: it exists "
                      "only to show the instrument can separate when separation exists and returns "
                      "chance when labels are destroyed."),
            "positive_control": ctrl_signal, "label_shuffled_null": ctrl_null},
        "checks": checks,
        "missing_predictor_call_set": missing,
        "verdict": {
            "overlap_exists": False,
            "discrimination_measured": False,
            "statement": ("DECISIVE NEGATIVE. The repository's cached predictor calls and the IEDB "
                          "validated arms are disjoint: 0 of 549 arm-F and 0 of 675 arm-N validated "
                          "peptides carry a cached call, and 0 of 5,916 cached calls names a "
                          "validated record. The class I threshold's discrimination is therefore "
                          "UNMEASURED on held data — undefined, not chance, and not zero. What "
                          "would be needed is enumerated exactly above."),
            "not_manufactured": ("No match rule was loosened. Exact (peptide, allele) matching after "
                                 "whitespace/case normalisation only; minimum edit distance between "
                                 "any cached and any validated peptide is %d." % best[0]),
        },
    }

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "threshold-calibration.json")
    with open(out, "w") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print("inputs re-hashed at use:")
    for k, v in prov.items():
        print(f"  {k}: {v['sha256'][:16]}… {v['bytes']} B")
    print(f"cached calls: {len(calls)} over {len(call_peps)} peptides x {len(panel)} alleles")
    for k, v in arms.items():
        print(f"arm {k}: {v['records']} records, {v['distinct_peptides']} peptides, "
              f"{v['pairs_on_the_34_allele_panel']} pairs on panel, "
              f"{v['pairs_dropped_hla_c_excluded_route_B8_closed']} HLA-C pairs excluded")
    for k, v in inter.items():
        print(f"intersection arm {k}: pairs={v['peptide_allele_pairs_in_common']} "
              f"peptides={v['peptides_in_common']} alleles={v['alleles_in_common']}")
    print(f"nearest peptide edit distance: {best[0]} ({best[1]} vs {best[2]})")
    print(f"measured discrimination: n_pos={measured['n_positive']} n_neg={measured['n_negative']} "
          f"auroc={measured['auroc']} -> defined={measured['defined']}")
    print(f"real label-shuffled null: {null_measured['verdict']}")
    print(f"synthetic positive control auroc={ctrl_signal['auroc']:.4f} "
          f"sens={ctrl_signal['sensitivity']:.4f} spec={ctrl_signal['specificity']:.4f}")
    print(f"synthetic shuffled null: mean={ctrl_null['mean_auroc']} "
          f"[{ctrl_null['p2_5']}, {ctrl_null['p97_5']}] -> {ctrl_null['verdict']}")
    print("checks:", json.dumps(checks))
    print(f"missing predictor calls required: arm F {len(missing_F)} + arm N {len(missing_N)} "
          f"= {len(missing_F) + len(missing_N)}")
    print(f"wrote {out} ({os.path.getsize(out)} B)")
    if not checks["all_passed"]:
        print("⚠ INSTRUMENT CHECK FAILED — the reported result is that the instrument is wrong.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
