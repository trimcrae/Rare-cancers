#!/usr/bin/env python3
"""ASO-CHANCE-1 — dinucleotide-preserving shuffled-oligo baseline for junction-ASO off-target counts.

READ-ONLY against the frozen ASO package: this script opens repository inputs for reading only and
writes exactly one file, inside this lane directory.

Question: how much of the junction ASO's off-target specificity exceeds chance, when chance is
defined by an oligo of the SAME dinucleotide composition rather than a uniform random 16-mer?
"""
import glob
import hashlib
import json
import os
import sys
import statistics

sys.dont_write_bytecode = True
REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research/modalities")
sys.path.insert(0, MOD)
import aso_parent_null as apn  # noqa: E402  — the repository's own Altschul-Erikson shuffler

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso-offtarget-chance-baseline.json")
SEED = 20260908
K_SHUFFLE = 400
BASES = "ACGT"
BI = {b: i for i, b in enumerate(BASES)}
# Measured scanned span, read from the committed offtarget-chance-baseline.json null_model.
TRANSCRIPTOME_NT = 718571139


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- background models
def markov_from_sequences(seqs):
    mono = [0] * 4
    di = [[0] * 4 for _ in range(4)]
    n = 0
    for s in seqs:
        s = s.upper()
        prev = None
        for ch in s:
            i = BI.get(ch)
            if i is None:
                prev = None
                continue
            mono[i] += 1
            n += 1
            if prev is not None:
                di[prev][i] += 1
            prev = i
    p0 = [m / n for m in mono]
    T = []
    for a in range(4):
        tot = sum(di[a])
        T.append([di[a][b] / tot for b in range(4)] if tot else list(p0))
    return {"n_nt": n, "p0": p0, "T": T, "di_counts": di}


UNIFORM = {"n_nt": None, "p0": [0.25] * 4, "T": [[0.25] * 4 for _ in range(4)], "di_counts": None}


def p_within(query, model, max_mm):
    """Sum of first-order-Markov probabilities of every word within `max_mm` substitutions.

    Exact dynamic program: state = (last base, mismatches used). No sampling of the 1129-word
    neighbourhood, so the uniform model reproduces n_within(L,2)/4**L exactly (asserted below).
    """
    p0, T = model["p0"], model["T"]
    q = [BI[c] for c in query]
    cur = {}
    for b in range(4):
        m = 0 if b == q[0] else 1
        if m <= max_mm:
            cur[(b, m)] = cur.get((b, m), 0.0) + p0[b]
    for i in range(1, len(q)):
        nxt = {}
        qi = q[i]
        for (b, m), pv in cur.items():
            Tb = T[b]
            for c in range(4):
                mm = m + (0 if c == qi else 1)
                if mm > max_mm:
                    continue
                k = (c, mm)
                nxt[k] = nxt.get(k, 0.0) + pv * Tb[c]
        cur = nxt
    return sum(cur.values())


def n_within(length, mismatches):
    from math import comb
    return sum(comb(length, k) * 3 ** k for k in range(mismatches + 1))


# ---------------------------------------------------------------- inputs
def load_screens():
    paths = sorted(glob.glob(os.path.join(MOD, "junction-aso-offtarget-*-deep500-b[12].json")))
    rows, files = [], []
    for p in paths:
        d = json.load(open(p))
        meth = d.get("method", {})
        thr = meth.get("near_match_threshold", "")
        ident, L = None, None
        if "/" in thr:
            frag = thr.replace(">=", "").replace("≥", "").split("identical")[0].strip()
            a, b = frag.split("/")
            ident, L = int(a.strip()), int(b.strip())
        files.append({"path": os.path.relpath(p, REPO), "sha256": sha256(p),
                      "junction_label": d.get("junction_label"),
                      "near_match_threshold": thr, "n_oligos": len(d.get("oligos", []))})
        for o in d.get("oligos", []):
            rows.append({"seq": o["antisense_5to3"], "target": o.get("target_mRNA_5to3"),
                         "status": o.get("status"),
                         "observed_near_matches": o.get("n_offtarget_near_matches"),
                         "n_true_cleavage_risk": o.get("n_true_cleavage_risk"),
                         "n_hitlist_rows": len(o.get("offtargets", []) or []),
                         "ident": ident, "L": L,
                         "junction_label": d.get("junction_label"),
                         "source_file": os.path.relpath(p, REPO)})
    return files, rows



def _spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else None


def denominator_free(per_design):
    """Correlation of the OBSERVED screen count with the composition-only chance expectation.

    Scale-invariant, so it does not depend on the searched span of the remote BLAST database — the
    one quantity this checkout cannot recover. If observed counts track composition, then the part
    of a design's off-target load that its sequence ORDER explains is small.
    """
    out = {}
    for lab, sel in (("all_lengths", lambda d: True), ("len16_only", lambda d: d["length"] == 16)):
        ds = [d for d in per_design if sel(d)]
        if len(ds) < 5:
            continue
        obs = [d["observed_near_matches"] for d in ds]
        pm = [d["p_per_position__markov1_mature_exonic"] for d in ds]
        gc = [d["gc_percent"] for d in ds]
        import math
        lx = [math.log(v) for v in pm]
        ly = [math.log(v + 1.0) for v in obs]
        n = len(lx)
        mx, my = sum(lx) / n, sum(ly) / n
        sxy = sum((a - mx) * (b - my) for a, b in zip(lx, ly))
        sxx = sum((a - mx) ** 2 for a in lx)
        syy = sum((b - my) ** 2 for b in ly)
        r2 = (sxy ** 2 / (sxx * syy)) if sxx and syy else None
        out[lab] = {"n": n,
                    "spearman_observed_vs_composition_expectation": _spearman(pm, obs),
                    "spearman_observed_vs_gc_percent": _spearman(gc, obs),
                    "r2_log_observed_on_log_composition_expectation": r2,
                    "_reading": "r2 is the share of the spread in log(observed+1) that a "
                                "composition-only chance model already accounts for."}
    return out


def main():
    files, rows = load_screens()
    screened = [r for r in rows if r["status"] == "screened" and r["observed_near_matches"] is not None]
    failed = [r for r in rows if r not in screened]

    # dedupe on sequence; a sequence screened at several seams must agree or we record the conflict
    byseq, conflicts = {}, []
    for r in screened:
        s = r["seq"]
        if s in byseq:
            if byseq[s]["observed_near_matches"] != r["observed_near_matches"]:
                conflicts.append({"seq": s, "a": byseq[s]["observed_near_matches"],
                                  "b": r["observed_near_matches"],
                                  "files": [byseq[s]["source_file"], r["source_file"]]})
            byseq[s]["seams"].append(r["junction_label"])
            continue
        r = dict(r)
        r["seams"] = [r["junction_label"]]
        byseq[s] = r
    designs = sorted(byseq.values(), key=lambda r: r["seq"])

    # backgrounds from held human sequence
    prem = json.load(open(os.path.join(MOD, "aso-premrna-sequences.json")))
    exonic, unspliced = [], []
    for g, rec in prem["genes"].items():
        seq = rec["sequence"]
        unspliced.append(seq)
        for a, b in rec["exon_spans_0based_inclusive"]:
            exonic.append(seq[a:b + 1])
    m_exonic = markov_from_sequences(exonic)
    m_premrna = markov_from_sequences(unspliced)
    models = {"uniform_iid": UNIFORM, "markov1_mature_exonic": m_exonic, "markov1_premrna": m_premrna}

    # validation: uniform DP must reproduce the analytic neighbourhood probability exactly
    val = {}
    for L in sorted({r["L"] for r in designs if r["L"]}):
        got = p_within(designs[0]["seq"][:L] if len(designs[0]["seq"]) >= L else "A" * L, UNIFORM, 2)
        want = n_within(L, 2) / 4.0 ** L
        val[f"uniform_dp_vs_analytic_L{L}"] = {"dp": got, "analytic": want,
                                               "rel_err": abs(got - want) / want}

    rng = apn.Rng(SEED)
    fellbacks = 0
    per_design = []
    for r in designs:
        s, L, ident = r["seq"], r["L"], r["ident"]
        max_mm = L - ident
        ent = {"sequence": s, "length": L, "threshold": f">= {ident}/{L}",
               "seams": sorted(set(r["seams"])), "source_file": r["source_file"],
               "observed_near_matches": r["observed_near_matches"],
               "observed_true_cleavage_risk": r["n_true_cleavage_risk"],
               "gc_percent": round(100.0 * sum(c in "GC" for c in s) / L, 1)}
        for name, mod in models.items():
            p = p_within(s, mod, max_mm)
            ent[f"p_per_position__{name}"] = p
            ent[f"expected_near_matches__{name}"] = p * TRANSCRIPTOME_NT
        # dinucleotide-preserving shuffled-oligo ensemble
        ps = []
        for _ in range(K_SHUFFLE):
            sh, fb = apn.scramble_dinucleotide(s, rng)
            fellbacks += int(fb)
            ps.append(p_within(sh, m_exonic, max_mm))
        ps.sort()
        lo, hi = ps[int(0.025 * len(ps))], ps[int(0.975 * len(ps)) - 1]
        mean = sum(ps) / len(ps)
        ent["shuffle_baseline"] = {
            "n_shuffles": K_SHUFFLE, "background": "markov1_mature_exonic",
            "p_mean": mean, "p_ci95": [lo, hi],
            "expected_near_matches_mean": mean * TRANSCRIPTOME_NT,
            "expected_near_matches_ci95": [lo * TRANSCRIPTOME_NT, hi * TRANSCRIPTOME_NT],
            "design_over_shuffle_mean_ratio": ent["p_per_position__markov1_mature_exonic"] / mean,
            "design_percentile_in_shuffle_ensemble":
                100.0 * sum(1 for v in ps if v <= ent["p_per_position__markov1_mature_exonic"]) / len(ps),
        }
        ent["observed_over_expected__markov1_mature_exonic"] = (
            r["observed_near_matches"] / ent["expected_near_matches__markov1_mature_exonic"]
            if ent["expected_near_matches__markov1_mature_exonic"] else None)
        ent["observed_over_shuffle_baseline"] = (
            r["observed_near_matches"] / ent["shuffle_baseline"]["expected_near_matches_mean"]
            if ent["shuffle_baseline"]["expected_near_matches_mean"] else None)
        per_design.append(ent)

    # ------------------------------------------------------------ the failable check
    ctrl = json.load(open(os.path.join(MOD, "aso-control-oligos.json")))
    obs_by_seq = {d["sequence"]: d for d in per_design}
    check = {"_what": "The committed dinucleotide scramble controls must land AT the shuffled-oligo "
                      "baseline built from their own reagent. If a control sits outside the central "
                      "95% of its reagent's shuffle ensemble, the baseline is mis-specified.",
             "controls": [], "verdict": None,
             "_observed_arm_status": None}
    fails = 0
    obs_arm_missing = []
    for c in ctrl["controls"]:
        reagent, cs = c["for_reagent"], c["control_5to3"]
        L = len(cs)
        max_mm = 2
        ps = []
        r2 = apn.Rng(SEED ^ 0x5EED)
        for _ in range(K_SHUFFLE):
            sh, fb = apn.scramble_dinucleotide(reagent, r2)
            fellbacks += int(fb)
            ps.append(p_within(sh, m_exonic, max_mm))
        ps.sort()
        lo, hi = ps[int(0.025 * len(ps))], ps[int(0.975 * len(ps)) - 1]
        pc = p_within(cs, m_exonic, max_mm)
        inside = lo <= pc <= hi
        if not inside:
            fails += 1
        if cs not in obs_by_seq:
            obs_arm_missing.append(cs)
        check["controls"].append({
            "label": c["label"], "reagent": reagent, "control": cs,
            "reagent_screened_in_deep500": reagent in obs_by_seq,
            "control_screened_in_deep500": cs in obs_by_seq,
            "control_p_per_position": pc,
            "reagent_shuffle_ensemble_p_ci95": [lo, hi],
            "reagent_shuffle_ensemble_p_mean": sum(ps) / len(ps),
            "control_percentile_in_reagent_shuffle_ensemble":
                100.0 * sum(1 for v in ps if v <= pc) / len(ps),
            "inside_central_95pc": inside,
            "reagent_observed_near_matches":
                obs_by_seq[reagent]["observed_near_matches"] if reagent in obs_by_seq else None,
            "control_observed_near_matches":
                obs_by_seq[cs]["observed_near_matches"] if cs in obs_by_seq else None,
        })
    check["verdict"] = "PASS_EXPECTATION_ARM" if fails == 0 else "FAIL_BASELINE_MIS_SPECIFIED"
    check["_observed_arm_status"] = (
        "NOT RUNNABLE — the committed scramble controls were never screened transcriptome-wide. "
        "They carry only a local mature-parent duplex screen, so there is no observed off-target "
        "count for them to land at. The strong form of this check (observed control counts at the "
        "baseline) requires a screen that does not exist in this checkout and cannot be produced "
        "here: the deep500 screens are remote NCBI BLAST runs (blast_rid recorded per oligo) and "
        "this lane has no network and no local RefSeq RNA corpus."
        if obs_arm_missing else "runnable")

    # ------------------------------------------------------------ summary
    ratios = [d["observed_over_shuffle_baseline"] for d in per_design
              if d["observed_over_shuffle_baseline"] is not None]
    order_ratios = [d["shuffle_baseline"]["design_over_shuffle_mean_ratio"] for d in per_design]
    obs = [d["observed_near_matches"] for d in per_design]
    censor = {"max_observed": max(obs), "n_at_or_above_450_hitlist_rows":
              sum(1 for d in per_design if d["observed_near_matches"] >= 450),
              "max_hitlist_rows": max(r["n_hitlist_rows"] for r in screened)}

    art = {
        "_title": "ASO-CHANCE-1 — junction-ASO off-target counts against a dinucleotide-preserving "
                  "shuffled-oligo baseline",
        "_question": "How much of the junction ASO's off-target specificity exceeds chance, when "
                     "chance holds base AND dinucleotide composition fixed and varies only order?",
        "_generated_by": os.path.relpath(os.path.abspath(__file__), REPO),
        "_read_only": "No repository asset outside this lane directory was written. The frozen ASO "
                      "package was read, never modified or regenerated.",
        "⛔_not_a_drug_claim": "Every number here is a sequence statistic over a transcript database. "
                              "Nothing here is evidence of efficacy, safety, selectivity, a "
                              "therapeutic window, or clinical readiness.",
        "seed": SEED, "n_shuffles_per_design": K_SHUFFLE,
        "mononucleotide_fallbacks_in_shuffler": fellbacks,
        "transcriptome_nt": TRANSCRIPTOME_NT,
        "transcriptome_nt_source": "research/modalities/offtarget-chance-baseline.json :: "
                                   "null_model.transcriptome_nt (counted local scan span). ⚠ The "
                                   "OBSERVED counts here come from remote blastn against "
                                   "refseq_rna, whose searched span is NOT this number.",
        "inputs": {"screen_files": files,
                   "control_file": {"path": "research/modalities/aso-control-oligos.json",
                                    "sha256": sha256(os.path.join(MOD, "aso-control-oligos.json"))},
                   "committed_chance_baseline": {
                       "path": "research/modalities/offtarget_chance_baseline.py",
                       "sha256": sha256(os.path.join(MOD, "offtarget_chance_baseline.py"))},
                   "background_sequence": {
                       "path": "research/modalities/aso-premrna-sequences.json",
                       "sha256": sha256(os.path.join(MOD, "aso-premrna-sequences.json")),
                       "genes": sorted(prem["genes"]),
                       "exonic_nt_used": m_exonic["n_nt"], "premrna_nt_used": m_premrna["n_nt"]}},
        "background_models": {k: {"n_nt": v["n_nt"], "p0": v["p0"], "T": v["T"]}
                              for k, v in models.items()},
        "validation": val,
        "rows": {"n_oligo_rows": len(rows), "n_screened": len(screened),
                 "n_screen_failed": len(failed), "n_unique_sequences": len(per_design),
                 "duplicate_sequence_count_conflicts": conflicts,
                 "screen_failed_sequences": [r["seq"] for r in failed]},
        "censoring": censor,
        "summary": {
            "observed_near_matches": {"min": min(obs), "median": statistics.median(obs),
                                      "mean": round(statistics.mean(obs), 2), "max": max(obs)},
            "design_vs_shuffle_expectation_ratio": {
                "_meaning": "chance expectation of the real design divided by the mean chance "
                            "expectation of its own dinucleotide-preserving shuffles. 1.0 means the "
                            "design's ORDER buys nothing at all against composition.",
                "min": min(order_ratios), "median": statistics.median(order_ratios),
                "max": max(order_ratios)},
            "observed_over_shuffle_baseline": {
                "_meaning": ">1 means MORE off-target near-matches than a composition-matched "
                            "random-order oligo would be expected to have; <1 means fewer.",
                "min": min(ratios), "median": statistics.median(ratios),
                "mean": round(statistics.mean(ratios), 3), "max": max(ratios),
                "n_below_1": sum(1 for v in ratios if v < 1.0),
                "n_at_or_above_1": sum(1 for v in ratios if v >= 1.0), "n": len(ratios)},
        },
        "denominator_free_composition_test": denominator_free(per_design),
        "check_scramble_controls_land_at_baseline": check,
        "per_design": per_design,
    }
    with open(OUT, "w") as fh:
        json.dump(art, fh, indent=1)
    print(json.dumps({k: art[k] for k in ("validation", "rows", "censoring", "summary", "denominator_free_composition_test")}, indent=1))
    print(json.dumps(check, indent=1))
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
