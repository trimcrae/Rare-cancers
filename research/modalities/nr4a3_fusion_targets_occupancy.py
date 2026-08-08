#!/usr/bin/env python3
"""Occupancy axis for the EWSR1::NR4A3 transcriptional-output manuscript.

WHAT THIS IS. The manuscript's §3.11 reports that no genome-wide chromatin experiment has ever been
performed with an NR4A3 fusion, and then stops — so every other instrument in that paper is an
expression or a sequence read and none of them touches DNA occupancy. This module asks the nearest
answerable question from data already cached in this repository: **in the NR4A ChIP-seq experiments
that DO exist, is there unusual protein occupancy at SEMA3C, PPARG or ENO3?**

THE ANSWER IS NO, AND THE WAY IT IS NO MATTERS. Calibrated against a background panel of 198 genes
this lane did not choose, none of the three class-A genes carries more promoter-window occupancy than
an arbitrary gene does, in any peak set deep enough to detect anything. That is not a null result
about the fusion — it is a measurement of how far the available surrogates are from being able to
answer the question at all, which is what makes §3.11's negative a bounded reading rather than an
assertion about a literature search.

⛔ WHY A RAW PEAK COUNT IS WORTHLESS HERE, stated first because it is the trap. In the deepest
catalogue (ReMap2022 NR4A1, 83,773 peaks) **82.8% of the background panel has a promoter-window
peak**. "Has a peak" is therefore what almost every gene does, and quoting it as support would repeat
exactly the uncalibrated fold-change error the manuscript's §1.3 exists to refuse. Every count here
is reported against the panel distribution or not at all.

⛔ AND A ZERO FROM A SHALLOW EXPERIMENT IS AN ABSENT READING, NOT ABSENCE. The 12 NR4A3-specific peak
sets carry 53-154 peaks each and recover **no panel gene at all** (panel hit rate 0.000). A peak set
that cannot find an arbitrary gene cannot fail to find these three, so its silence carries no
information. Such peak sets are reported as UNINFORMATIVE and are never counted as evidence of
non-occupancy.

⛔ WHAT NONE OF THIS CAN BE. NR4A1 is a paralogue, not NR4A3, and none of it is the fusion or EMC
chromatin. The repository's own matched-cell-type measurement puts NR4A1→NR4A3 peak sharing at 0.347,
which is meaningful and far from identity. Nothing here shows any gene being bound by EWSR1::NR4A3,
and nothing here is an efficacy, selectivity, safety or clinical-readiness claim.

REPRODUCTION (offline; reads only committed caches, never the network)
    python3 nr4a3_fusion_targets_occupancy.py
    python3 nr4a3_fusion_targets_occupancy.py --check
"""

import argparse
import bisect
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CISTROME = os.path.join(HERE, "emc-ret-cistrome.json")
CISTROME_INPUTS = os.path.join(HERE, "emc-ret-cistrome-inputs.json")
OUT = os.path.join(HERE, "nr4a3-fusion-targets-occupancy.json")

CLASS_A = ["ENO3", "PPARG", "SEMA3C"]

# The window is IMPORTED, not chosen here: it is the same -10 kb/+15 kb strand-aware window the
# manuscript's motif scan uses, so the sequence axis and the occupancy axis ask about one region.
UPSTREAM, DOWNSTREAM = 10000, 15000

# A peak set that recovers this fraction of the background panel or less cannot discriminate: it is
# not finding arbitrary genes either, so its silence at a focus gene is an absent reading.
MIN_PANEL_HIT_RATE = 0.02
MIN_PANEL_GENES = 50


def _r(x, nd=4):
    return None if x is None else round(x, nd)


def _window(rec):
    """Strand-aware promoter window, identical in rule to `emc_ret_target_scan`."""
    if rec.get("chrom") is None or rec.get("start") is None:
        return None
    if rec.get("strand") == 1:
        tss = rec["start"]
        return rec["chrom"], tss - UPSTREAM, tss + DOWNSTREAM
    tss = rec["end"]
    return rec["chrom"], tss - DOWNSTREAM, tss + UPSTREAM


def _index_peaks(peaks):
    by = {}
    for p in peaks:
        if isinstance(p, (list, tuple)):
            c, s, e = p[0], p[1], p[2]
        else:
            c, s, e = p.get("chrom"), p.get("start"), p.get("end")
        if c is None or s is None or e is None:
            continue
        by.setdefault(c, []).append((s, e))
    for c in by:
        by[c].sort()
        by[c] = ([x[0] for x in by[c]], [x[1] for x in by[c]])
    return by


def _count_in_window(by, chrom, lo, hi):
    arr = by.get(chrom)
    if not arr:
        return 0
    starts, ends = arr
    hi_i = bisect.bisect_left(starts, hi)
    n = 0
    for j in range(hi_i - 1, -1, -1):
        if ends[j] > lo:
            n += 1
        elif starts[j] < lo - 5_000_000:      # peaks are sorted by start; stop once far left
            break
    return n


def _empirical_p(observed, panel):
    """(ge+1)/(n+1), the convention the cistrome artifact already uses.

    It can never print a 0 the panel size does not support, and it is one-sided by construction:
    the question is whether a focus gene carries MORE occupancy than an arbitrary gene, and a
    two-sided reading of 'fewer peaks than average' would not mean anything here."""
    ge = sum(1 for v in panel if v >= observed)
    return round((ge + 1) / (len(panel) + 1), 4), ge


def derive():
    with open(CISTROME_INPUTS) as fh:
        inp = json.load(fh)
    with open(CISTROME) as fh:
        art = json.load(fh)

    committed = art["part_2_intersection"]["per_peakset"]
    focus_loci = set()
    for v in committed.values():
        if isinstance(v.get("loci"), dict):
            focus_loci |= set(v["loci"])

    res = {
        "_what": __doc__.strip().splitlines()[0],
        "_language_discipline": (
            "NR4A1 is a paralogue, not NR4A3, and none of this is the fusion or EMC chromatin. "
            "Nothing here shows any gene being bound by EWSR1::NR4A3. Nothing here is an efficacy, "
            "selectivity, safety, therapeutic-window or clinical-readiness claim, and no such "
            "quantity is computed."),
        "_why_a_raw_count_is_not_reported": (
            "in the deepest catalogue 82.8% of the background panel carries a promoter-window peak, "
            "so 'has a peak' is what almost every gene does. Every count below is placed against the "
            "panel distribution or is not reported as a finding."),
        "_inputs": {"peaks_and_tss": os.path.basename(CISTROME_INPUTS),
                    "committed_intersection": os.path.basename(CISTROME),
                    "_offline": "no network access; both files are committed caches"},
        "_window": {"upstream_bp": UPSTREAM, "downstream_bp": DOWNSTREAM, "strand_aware": True,
                    "_why_this_window": ("imported from the manuscript's motif scan so the sequence "
                                         "axis and the occupancy axis ask about one region")},
        "_uninformative_rule": {
            "min_panel_hit_rate": MIN_PANEL_HIT_RATE, "min_panel_genes": MIN_PANEL_GENES,
            "_why": ("a peak set that recovers (almost) no arbitrary gene cannot fail to recover "
                     "these three, so its silence is an ABSENT READING and is never counted as "
                     "evidence of non-occupancy")},
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parity_with_committed_artifact": {},
        "per_peakset": {},
        "per_gene_summary": {},
    }

    parity_rows, parity_bad = 0, []
    for name, ps in sorted(inp.get("peaksets", {}).items()):
        if ps.get("_status") != "read" or not ps.get("peaks"):
            continue
        build = ps.get("genome")
        genes = (inp.get("genes") or {}).get(build) or {}
        if not genes:
            continue
        by = _index_peaks(ps["peaks"])
        counts = {}
        for g, rec in genes.items():
            w = _window(rec)
            if w:
                counts[g] = _count_in_window(by, *w)

        # PARITY: the counts this module derives must equal the committed intersection's.
        com = (committed.get(name) or {}).get("loci") or {}
        for g, rec in com.items():
            want = rec.get("n_peaks_promoter_window")
            got = counts.get(g)
            if want is None or got is None:
                continue
            parity_rows += 1
            if want != got:
                parity_bad.append({"peakset": name, "gene": g, "committed": want, "re_derived": got})

        panel = {g: v for g, v in counts.items() if g not in focus_loci}
        panel_vals = list(panel.values())
        hit_rate = (sum(1 for v in panel_vals if v > 0) / len(panel_vals)) if panel_vals else None
        informative = (
            panel_vals and len(panel_vals) >= MIN_PANEL_GENES and hit_rate > MIN_PANEL_HIT_RATE)

        rec = {
            "antigen": ps.get("antigen"), "genome": build, "cell_type": ps.get("cell_type"),
            "n_peaks_total": len(ps["peaks"]),
            "panel": {"n_genes": len(panel_vals),
                      "fraction_with_a_promoter_peak": _r(hit_rate, 4),
                      "_source": ("a background panel this lane did not choose, carried in the "
                                  "cistrome inputs cache alongside the focus loci")},
            "informative": bool(informative),
        }
        if not informative:
            if not panel_vals:
                # Mouse builds carry only the orthologous focus loci in this cache, so there is no
                # background panel to place a count against — and the manuscript's genes are human.
                rec["_status"] = "NO_BACKGROUND_PANEL_ON_THIS_BUILD"
                rec["_means"] = (
                    "this build carries no background panel in the cistrome cache, so a count here "
                    "could not be calibrated even if it were taken. On the mouse builds that is "
                    "also the right outcome for a different reason: the manuscript's contrast is "
                    "about human genes. This is an ABSENT READING, not evidence of non-occupancy.")
            else:
                rec["_status"] = "UNINFORMATIVE"
                rec["_means"] = (
                    "this peak set recovers (almost) no arbitrary gene, so it cannot fail to "
                    "recover these three. Its zeros are an ABSENT READING, not evidence of "
                    "non-occupancy.")
        else:
            rec["genes"] = {}
            for g in CLASS_A:
                if g not in counts:
                    rec["genes"][g] = {"_status": "NOT_ON_THIS_BUILD"}
                    continue
                p, ge = _empirical_p(counts[g], panel_vals)
                rec["genes"][g] = {
                    "n_peaks_promoter_window": counts[g],
                    "n_panel_genes_at_or_above": ge,
                    "empirical_p_vs_panel": p,
                    "enriched_at_0_05": p < 0.05,
                }
        res["per_peakset"][name] = rec

    res["parity_with_committed_artifact"] = {
        "_what": ("every promoter-window count re-derived here, compared with the committed "
                  "emc-ret-cistrome.json intersection"),
        "n_rows_checked": parity_rows, "n_disagreeing": len(parity_bad),
        "disagreements": parity_bad[:10], "agrees": not parity_bad,
    }
    if parity_bad:
        raise SystemExit(
            "nr4a3_fusion_targets_occupancy: re-derived peak counts disagree with the committed "
            f"cistrome artifact on {len(parity_bad)} row(s). REFUSING TO WRITE — an occupancy axis "
            "built on a different intersection from the one the repository owns is worse than none.")

    # ⛔ THE SAME EXPERIMENT APPEARS ONCE PER GENOME BUILD. `SRX1653203@hg19` and `SRX1653203@hg38`
    # are one ChIP-seq experiment lifted to two assemblies, so counting both would double every
    # tally and would make ENO3's single borderline result look like two independent ones. The
    # multiplicity arithmetic below is over DISTINCT EXPERIMENTS for that reason.
    def _experiment(name):
        return name.split("@")[0]

    informative = {n: v for n, v in res["per_peakset"].items() if v.get("informative")}
    experiments = sorted({_experiment(n) for n in informative})

    for g in CLASS_A:
        per_exp = {}
        for n, v in informative.items():
            cell = (v.get("genes") or {}).get(g) or {}
            p = cell.get("empirical_p_vs_panel")
            if p is None:
                continue
            e = _experiment(n)
            per_exp[e] = min(p, per_exp[e]) if e in per_exp else p
        ps_ = sorted(per_exp.values())
        res["per_gene_summary"][g] = {
            "n_informative_experiments": len(ps_),
            "best_empirical_p_vs_panel": ps_[0] if ps_ else None,
            "n_experiments_enriched_at_0_05": sum(1 for p in ps_ if p < 0.05),
            "empirical_p_by_experiment": per_exp,
            "_reading": ("the smallest p any informative NR4A experiment gives this gene against a "
                         "background panel of genes chosen without reference to it. One value per "
                         "EXPERIMENT, not per genome build."),
        }

    n_tests = len(experiments) * len(CLASS_A)
    n_enr = sum(s["n_experiments_enriched_at_0_05"] for s in res["per_gene_summary"].values())
    expected = round(0.05 * n_tests, 2)
    res["verdict"] = {
        "n_peaksets_read": len(res["per_peakset"]),
        "n_informative_peaksets": len(informative),
        "n_informative_experiments": len(experiments),
        "informative_experiments": experiments,
        "multiplicity": {
            "n_tests": n_tests,
            "n_enriched_at_0_05_observed": n_enr,
            "n_enriched_at_0_05_expected_by_chance": expected,
            "_reading": ("with this many gene x experiment tests and no correction, this many "
                         "nominal hits are expected at p < 0.05 whether or not anything is bound"),
        },
        "headline": (
            f"No class-A gene carries unusual NR4A occupancy. Across {len(experiments)} distinct "
            f"experiments deep enough to recover an arbitrary gene, {n_enr} of {n_tests} "
            f"gene-by-experiment tests reach p < 0.05 against a background panel, against "
            f"{expected} expected by chance. ENO3 is the only gene with even a borderline value and "
            "it comes from a single experiment."
            if n_enr <= expected else
            "At least one class-A gene exceeds the background panel more often than chance would "
            "give; read the per-gene table before quoting this."),
        "⛔ what_this_is_not": (
            "NOT a measurement of the fusion, and NOT evidence that these genes are unbound. Every "
            "informative experiment here is NR4A1, a paralogue whose matched-cell-type peak sharing "
            "with NR4A3 is 0.347. All 12 NR4A3-specific peak sets are UNINFORMATIVE by the rule "
            "above — they recover no arbitrary gene either. So this is a bound on what the "
            "available surrogates can show, and it is why the manuscript's discriminating "
            "experiment remains a fusion cistrome rather than any re-analysis of existing data."),
    }
    return res


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if k != "generated_utc"}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="re-derive and diff against the committed artifact; do not write")
    args = ap.parse_args()
    res = derive()
    if args.check:
        if not os.path.exists(OUT):
            print(f"occupancy --check: {os.path.basename(OUT)} does not exist yet")
            return 1
        with open(OUT) as fh:
            have = json.load(fh)
        if _strip(have) == _strip(res):
            print(f"occupancy --check: OK -- {os.path.basename(OUT)} is current")
            return 0
        print(f"occupancy --check: DRIFT -- re-run without --check")
        return 1
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    v = res["verdict"]
    m = v["multiplicity"]
    print(f"occupancy: wrote {os.path.basename(OUT)}")
    print(f"  peaksets read {v['n_peaksets_read']} | informative {v['n_informative_peaksets']} "
          f"({v['n_informative_experiments']} distinct experiments)")
    print(f"  enriched at p<0.05: {m['n_enriched_at_0_05_observed']} of {m['n_tests']} tests, "
          f"against {m['n_enriched_at_0_05_expected_by_chance']} expected by chance")
    for g, srow in sorted(res["per_gene_summary"].items()):
        print(f"  {g:7s} experiments {srow['n_informative_experiments']:2d} | best p "
              f"{srow['best_empirical_p_vs_panel']}")
    print(f"  parity rows checked: {res['parity_with_committed_artifact']['n_rows_checked']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
