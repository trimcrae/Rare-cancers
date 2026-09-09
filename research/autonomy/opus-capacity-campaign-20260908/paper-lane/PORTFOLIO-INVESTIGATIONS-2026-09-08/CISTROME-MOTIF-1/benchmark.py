#!/usr/bin/env python3
"""CISTROME-MOTIF-1 — does the NBRE motif scan predict MEASURED NR4A occupancy?

Unit of analysis: one locus. Predictor = NBRE motif score computed from the frozen
promoter-window sequence. Outcome = measured promoter-window peak presence across the
NR4A ChIP peaksets already intersected in emc-ret-cistrome.json.

Pre-specified BEFORE looking at any concordance number:
  * primary motif score      : exact-NBRE octamer count in the window
  * secondary motif score    : one-mismatch NBRE octamer count (the 'NBRE-like' class)
  * measured occupancy       : fraction of read peaksets with >=1 peak in the promoter window
  * binary label             : occupied = occupancy_fraction >= 0.5
  * discrimination statistic : Mann-Whitney AUC of motif score vs the binary label
  * concordance figure       : Somers'-style concordant-pair fraction (ties = 0.5) and Spearman rho
  * positive controls        : ENO3, PPARG, SEMA3C -- the three published class-A direct
                               EWSR1::NR4A3 targets already named in emc_ret_target_scan.py
                               FOCUS_GENES (PMIDs 26310886 / 31020999), not chosen here.
No transformation, subset or threshold search. One pass.
"""
import hashlib, importlib.util, json, os, random, statistics, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
MOD = os.path.join(REPO, "research/modalities/emc_ret_target_scan.py")
SCAN_INPUTS = os.path.join(REPO, "research/modalities/emc-ret-target-scan-inputs.json")
CISTROME = os.path.join(REPO, "research/modalities/emc-ret-cistrome.json")
OUT = os.path.join(os.path.dirname(__file__), "motif-vs-occupancy-benchmark.json")

POSITIVE_CONTROLS = ["ENO3", "PPARG", "SEMA3C"]
N_SHUFFLES = 20000
SHUFFLE_SEED = 20260908


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module():
    spec = importlib.util.spec_from_file_location("emc_ret_target_scan", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def auc(scores, labels):
    """Mann-Whitney AUC, ties counted 0.5. None if either class is empty."""
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    tot = 0.0
    for p in pos:
        for n in neg:
            tot += 1.0 if p > n else (0.5 if p == n else 0.0)
    return tot / (len(pos) * len(neg))


def concordant_fraction(x, y):
    """Fraction of informative pairs ordered the same way in x and y; ties in either = 0.5."""
    n = len(x)
    tot = c = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            tot += 1
            dx, dy = x[i] - x[j], y[i] - y[j]
            if dx == 0 or dy == 0:
                c += 0.5
            elif (dx > 0) == (dy > 0):
                c += 1
    return c / tot if tot else None


def main():
    m = load_module()
    hashes = {os.path.relpath(p, REPO): sha256(p) for p in (SCAN_INPUTS, CISTROME, MOD)}

    inputs = json.load(open(SCAN_INPUTS, encoding="utf-8"))
    cis = json.load(open(CISTROME, encoding="utf-8"))
    windows = inputs["gene_windows"]
    peaksets = cis["part_2_intersection"]["per_peakset"]

    read_sets = {k: v for k, v in peaksets.items() if v.get("_status") == "read"}
    loci = sorted({g for v in read_sets.values() for g in v.get("loci", {})})
    loci = [g for g in loci if g in windows and windows[g].get("sequence")]

    per_locus, window_mismatches = {}, []
    for g in loci:
        w = windows[g]
        seq = w["sequence"].upper()
        exact = m.scan_nbre(seq, max_mismatch=0)
        onemm = m.scan_nbre(seq, max_mismatch=1)
        nurre = m.scan_nurre(seq)

        present, n_peaks, maxscores, win_seen = [], [], [], set()
        for pk, v in read_sets.items():
            L = v["loci"].get(g)
            if L is None:
                continue
            win_seen.add(tuple(L["promoter_window_bed"]))
            present.append(1 if L["n_peaks_promoter_window"] > 0 else 0)
            n_peaks.append(L["n_peaks_promoter_window"])
            if L.get("max_score_promoter_window") is not None:
                maxscores.append(L["max_score_promoter_window"])
        # provenance check: the cistrome promoter window must BE the scanned window
        scan_win = tuple(w["window"])
        agree = all(cw == scan_win for cw in win_seen)
        if not agree:
            window_mismatches.append({"locus": g, "scan_window": list(scan_win),
                                      "cistrome_windows": [list(x) for x in sorted(win_seen)]})

        per_locus[g] = {
            "motif_score_exact_nbre": len(exact),
            "motif_score_1mm_nbre": len(onemm),
            "n_nurre": len(nurre),
            "gc": w.get("gc"),
            "n_peaksets_scored": len(present),
            "n_peaksets_with_promoter_peak": sum(present),
            "occupancy_fraction": sum(present) / len(present) if present else None,
            "mean_n_peaks_promoter_window": statistics.mean(n_peaks) if n_peaks else None,
            "max_peak_score_over_peaksets": max(maxscores) if maxscores else None,
            "window_agrees_with_cistrome": agree,
            "is_prespecified_positive_control": g in POSITIVE_CONTROLS,
        }

    order = sorted(per_locus)
    occ = [per_locus[g]["occupancy_fraction"] for g in order]
    labels = [1 if o >= 0.5 else 0 for o in occ]
    # The PRIMARY prespecified label turned out degenerate on this panel (no locus reaches 0.5),
    # so the AUC against it is UNDEFINED, not zero. That degeneracy is reported, not repaired.
    # ONE declared fallback label -- the median split of the same measured quantity -- is added so
    # a discrimination statistic exists at all. It is reported whatever it gives; no further
    # threshold, transformation or subset is tried.
    primary_label_degenerate = len(set(labels)) < 2
    occ_median = statistics.median(occ)
    labels_fb = [1 if o > occ_median else 0 for o in occ]
    for g, l, lf in zip(order, labels, labels_fb):
        per_locus[g]["label_occupied_primary"] = bool(l)
        per_locus[g]["label_occupied_median_split_fallback"] = bool(lf)

    results = {}
    rng = random.Random(SHUFFLE_SEED)
    for key in ("motif_score_exact_nbre", "motif_score_1mm_nbre", "n_nurre"):
        sc = [per_locus[g][key] for g in order]
        a = auc(sc, labels)
        a_fb = auc(sc, labels_fb)
        rho = m.spearman(sc, occ)
        conc = concordant_fraction(sc, occ)
        # score-label shuffle null: must give chance concordance
        null_auc, null_conc = [], []
        for _ in range(N_SHUFFLES):
            perm = sc[:]
            rng.shuffle(perm)
            a0 = auc(perm, labels_fb)
            if a0 is not None:
                null_auc.append(a0)
            null_conc.append(concordant_fraction(perm, occ))
        p_auc = ((sum(1 for x in null_auc if x >= a_fb) + 1) / (len(null_auc) + 1)
                 if a_fb is not None and null_auc else None)
        # positive-control median test
        med = statistics.median(sc)
        pcs = {g: {"score": per_locus[g][key], "above_median": per_locus[g][key] > med}
               for g in POSITIVE_CONTROLS if g in per_locus}
        results[key] = {
            "auc_vs_primary_label": a,
            "auc_vs_primary_label_note": ("UNDEFINED — the prespecified label has only one class on "
                                          "this panel" if a is None else "defined"),
            "auc_vs_median_split_fallback_label": a_fb,
            "auc_permutation_p_one_sided": p_auc,
            "spearman_rho_vs_occupancy_fraction": rho,
            "concordant_pair_fraction": conc,
            "shuffle_null_auc_mean": statistics.mean(null_auc) if null_auc else None,
            "shuffle_null_auc_sd": statistics.pstdev(null_auc) if len(null_auc) > 1 else None,
            "shuffle_null_concordance_mean": statistics.mean(null_conc) if null_conc else None,
            "median_score_across_loci": med,
            "positive_controls": pcs,
            "positive_controls_all_above_median": all(v["above_median"] for v in pcs.values()) if pcs else None,
        }

    primary = results["motif_score_exact_nbre"]
    checks = {
        "check_1_score_label_shuffle_gives_chance": {
            "_must_be_able_to_fail": True,
            "criterion": "mean shuffled AUC within 0.05 of 0.50 and mean shuffled concordance within 0.05 of 0.50",
            "_against_label": "median-split fallback label (the primary label is degenerate)",
            "observed_mean_auc": primary["shuffle_null_auc_mean"],
            "observed_mean_concordance": primary["shuffle_null_concordance_mean"],
            "passed": (primary["shuffle_null_auc_mean"] is not None
                       and abs(primary["shuffle_null_auc_mean"] - 0.5) <= 0.05
                       and abs(primary["shuffle_null_concordance_mean"] - 0.5) <= 0.05),
        },
        "check_2_positive_controls_above_median": {
            "_must_be_able_to_fail": True,
            "criterion": "ENO3, PPARG and SEMA3C each strictly above the median motif score",
            "exact_nbre": primary["positive_controls"],
            "one_mismatch_nbre": results["motif_score_1mm_nbre"]["positive_controls"],
            "passed_exact": primary["positive_controls_all_above_median"],
            "passed_1mm": results["motif_score_1mm_nbre"]["positive_controls_all_above_median"],
        },
    }
    disc = primary["auc_vs_median_split_fallback_label"]
    checks["check_0_primary_label_is_non_degenerate"] = {
        "_must_be_able_to_fail": True,
        "criterion": "the prespecified label (occupancy_fraction >= 0.5) has both classes present",
        "passed": not primary_label_degenerate,
        "occupancy_fraction_range": [min(occ), max(occ)],
        "occupancy_fraction_median": occ_median,
    }
    benchmark_passes = bool(checks["check_1_score_label_shuffle_gives_chance"]["passed"]
                            and checks["check_2_positive_controls_above_median"]["passed_exact"]
                            and disc is not None and disc > 0.5
                            and primary["auc_permutation_p_one_sided"] is not None
                            and primary["auc_permutation_p_one_sided"] < 0.05)

    out = {
        "_what": ("Benchmark: does the NBRE motif scan predict MEASURED NR4A ChIP occupancy? "
                  "One row per locus; predictor = motif score from the frozen window sequence, "
                  "outcome = measured promoter-window peak presence across NR4A peaksets."),
        "_lane": "CISTROME-MOTIF-1 (OPUS-CAPACITY-CAMPAIGN-20260908)",
        "_boundary_vs_sibling_lane": ("CISTROME-1's unit is occupancy-versus-background per locus "
                                      "(is this locus bound more than chance?). THIS lane's unit is "
                                      "motif-score-versus-measured-occupancy concordance across loci "
                                      "(does the sequence predictor rank the measured outcome?). "
                                      "No background null is computed here; no occupancy call is made."),
        "_input_sha256": hashes,
        "_prespecification": {
            "primary_score": "motif_score_exact_nbre",
            "secondary_score": "motif_score_1mm_nbre",
            "label": "occupancy_fraction >= 0.5",
            "discrimination_statistic": "Mann-Whitney AUC with permutation p",
            "declared_fallback_label": ("median split of occupancy_fraction, added only because the "
                                        "primary label proved degenerate (see check_0); reported "
                                        "whatever it gives, with no further threshold search"),
            "concordance_figure": "concordant_pair_fraction and Spearman rho",
            "positive_controls": POSITIVE_CONTROLS,
            "positive_control_source": ("emc_ret_target_scan.py FOCUS_GENES — published class-A "
                                        "direct EWSR1::NR4A3 targets, PMID 26310886 and PMID 31020999"),
            "n_shuffles": N_SHUFFLES, "seed": SHUFFLE_SEED,
        },
        "_scope": {
            "n_loci": len(order),
            "loci": order,
            "n_peaksets_read": len(read_sets),
            "n_peaksets_total": len(peaksets),
            "window": "promoter window as frozen in the scan inputs, -10 kb / +15 kb strand-aware",
            "window_agreement_between_inputs": "all loci agree" if not window_mismatches else window_mismatches,
        },
        "per_locus": per_locus,
        "results": results,
        "checks": checks,
        "benchmark_verdict": {
            "passes": benchmark_passes,
            "_reading": ("PASS means the motif scan discriminated measured occupancy on this panel "
                         "AND the prespecified positive controls ranked above median. FAIL is a real "
                         "result about the substitution of motif scans for occupancy, not an error."),
        },
        "_what_this_cannot_conclude": [
            "Nothing about EMC efficacy, safety, selectivity, therapeutic window or clinical readiness.",
            "A motif is not a binding site and a peak is not a function.",
            f"n = {len(order)} loci. This is a very small panel; absence of discrimination here does "
            "not prove absence genome-wide, and presence would not establish it either.",
            "Occupancy is measured in the cell types those peaksets were generated in, not in EMC "
            "tumour cells, and not with the EWSR1::NR4A3 chimera.",
            "Peaksets are wild-type NR4A1/2/3 ChIP; the fusion protein's cistrome is not measured here.",
            "Only loci already intersected in emc-ret-cistrome.json can enter; the 200-gene background "
            "panel has sequence but NO measured occupancy, so it cannot be benchmarked.",
        ],
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("n_loci=%d  n_peaksets_read=%d" % (len(order), len(read_sets)))
    for g in order:
        p = per_locus[g]
        print("  %-8s exact=%d  1mm=%-3d  occ=%.3f  primary_label=%d  median_split=%d  pc=%s"
              % (g, p["motif_score_exact_nbre"], p["motif_score_1mm_nbre"],
                 p["occupancy_fraction"], p["label_occupied_primary"],
                 p["label_occupied_median_split_fallback"], p["is_prespecified_positive_control"]))
    print("primary label degenerate:", primary_label_degenerate)
    for k, v in results.items():
        print("%s: AUC_primary=%s AUC_fallback=%s p=%s rho=%s conc=%s nullAUCmean=%s PCabove=%s"
              % (k, v["auc_vs_primary_label"], v["auc_vs_median_split_fallback_label"],
                 v["auc_permutation_p_one_sided"], v["spearman_rho_vs_occupancy_fraction"],
                 v["concordant_pair_fraction"], v["shuffle_null_auc_mean"],
                 v["positive_controls_all_above_median"]))
    print("CHECK 1 shuffle-gives-chance passed:", checks["check_1_score_label_shuffle_gives_chance"]["passed"])
    print("CHECK 2 positive-controls-above-median passed(exact):", checks["check_2_positive_controls_above_median"]["passed_exact"],
          " (1mm):", checks["check_2_positive_controls_above_median"]["passed_1mm"])
    print("BENCHMARK VERDICT:", "PASS" if benchmark_passes else "FAIL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
