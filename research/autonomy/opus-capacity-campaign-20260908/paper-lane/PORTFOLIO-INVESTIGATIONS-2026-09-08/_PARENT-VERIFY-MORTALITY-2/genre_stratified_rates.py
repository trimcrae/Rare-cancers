#!/usr/bin/env python3
"""Death-cue rates WITHIN pre-specified study-type strata: does the EMC excess reported by
PUB-MORTALITY-MECHANISM survive genre matching, or is it composition?

ORDERING. This is the FIRST script in this lane that reads a cue field or computes a rate.
The genre rule it uses is imported unchanged from genre_classifier.py, which was written,
run and frozen first (checks/02), and hand-checked next (checks/03, checks/04). This script
re-prints the classifier's sha256 so the frozen rule can be shown to be the one used.

WHAT IS COMPUTED
  A. Composition: how the 34 EMC-titled and 128 other papers, and their death-cue sentences,
     distribute across the five strata. This alone answers whether a genre confound exists.
  B. Within-stratum sentence-level cue rates for both instruments, with per-stratum Fisher.
  C. An exact stratified (conditional) test: the null distribution of the total flagged-in-EMC
     count is the convolution of the per-stratum hypergeometrics given the observed margins,
     which is the exact form of the Cochran-Mantel-Haenszel test and is the right tool at
     these counts. Mantel-Haenszel odds ratio reported alongside.
  D. The collapsed contrast that the confound is actually about: case_report_or_series vs all
     other genres. The hand-check gives this stratum precision 1.00 and recall 0.90, so it is
     the one boundary the instrument measures well.
  E. Direct standardisation: the EMC rate reweighted to the comparator's genre mix and the
     comparator's rate reweighted to EMC's, so the composition effect is expressed as a number.
  F. A misclassification simulation: how the stratified result moves if papers are reassigned
     at the error rate the hand-check actually measured.

WHAT IS NOT COMPUTED, AND STAYS NOT COMPUTED. No cause of death is assigned to anyone. No
survival curve is read, re-read or reinterpreted. The unit here is a SENTENCE, not a patient:
a flagged sentence is not a death, a death is not a patient, and no count here may be read as
a patient count or as a clinical statement about this or any disease.

No network. Reads two committed artifacts plus this lane's own frozen classification.
"""
import hashlib, json, math, pathlib, random, re, sys
from math import comb

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from genre_classifier import classify, STRATA  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[6]
PROBE = ROOT / "research/literature/emc-mortality-probe.json"
OUT = pathlib.Path(__file__).with_name("genre-stratified-rates.json")

# Corpus split, verbatim from research/manuscripts/emc_terminal_events.py:56 (as used by the
# completed lane), so the 34/128 split is the manuscript's own.
EMC_TITLE = re.compile(r"myxoid chondrosarcoma|chordoid sarcoma|NR4A3", re.I)

# Both instruments reused VERBATIM from the completed lane's cue_instrument_check.py, which
# took the shipped one from scripts/lit_mortality_probe.py:145 and pre-specified the strict
# one against the hand-read gold standard's tier-1 definition. Neither is re-tuned here.
CUE_SHIPPED = re.compile(
    r"\b("
    r"respiratory (?:failure|insufficiency|distress)|"
    r"pulmonary (?:insufficiency|failure|embolism|haemorrhage|hemorrhage)|"
    r"sepsis|septic|infection|pneumonia|"
    r"cachexia|malnutrition|"
    r"haemorrhage|hemorrhage|bleeding|"
    r"thrombosis|thromboembolism|embolism|"
    r"cord compression|"
    r"obstruction|"
    r"hepatic failure|liver failure|renal failure|"
    r"cardiac|myocardial|"
    r"cerebral|intracranial|"
    r"multi-?organ|"
    r"asphyxia|airway|"
    r"toxicity|complication|postoperative|"
    r"unrelated|other cause|intercurrent|comorbid"
    r")\b", re.I)
CUE_STRICT = re.compile(
    r"\b("
    r"respiratory (?:failure|insufficiency|arrest)|"
    r"pulmonary (?:failure|insufficiency)|"
    r"cardiac arrest|cardiopulmonary arrest|"
    r"multi-?organ (?:failure|dysfunction)|"
    r"(?:hepatic|liver|renal|heart) failure|"
    r"septic shock|sepsis|"
    r"asphyxia|exsanguinat\w+|"
    r"(?:cerebral|intracranial|intracerebral|subarachnoid) (?:haemorrhage|hemorrhage)|"
    r"pulmonary embolism"
    r")\b", re.I)
INSTRUMENTS = {"strict_terminal_event": CUE_STRICT, "shipped_has_mechanism_cue": CUE_SHIPPED}


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def fisher(a, b, c, d):
    """Two-sided Fisher exact on [[a,b],[c,d]] by the point-probability method."""
    n = a + b + c + d
    if n == 0 or (a + b) == 0 or (c + d) == 0 or (a + c) == 0 or (b + d) == 0:
        return None
    r1, c1 = a + b, a + c
    def pr(x):
        return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)
    p0 = pr(a)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    return round(sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9)), 6)


def hyper_pmf(n1, n2, m):
    """P(a) for a ~ Hypergeom: n1 EMC sentences, n2 other, m flagged in total."""
    N = n1 + n2
    lo, hi = max(0, m - n2), min(n1, m)
    return {a: comb(n1, a) * comb(n2, m - a) / comb(N, m) for a in range(lo, hi + 1)}


def convolve(dists):
    cur = {0: 1.0}
    for d in dists:
        nxt = {}
        for k, p in cur.items():
            for a, q in d.items():
                nxt[k + a] = nxt.get(k + a, 0.0) + p * q
        cur = nxt
    return cur


def exact_stratified(tables):
    """tables: list of (a, b, c, d) = (EMC flagged, EMC unflagged, oth flagged, oth unflagged).
    Exact conditional (CMH) test on T = sum a_i given all margins."""
    live = [t for t in tables if (t[0] + t[1]) and (t[2] + t[3]) and (t[0] + t[2])]
    if not live:
        return None
    dists = [hyper_pmf(a + b, c + d, a + c) for a, b, c, d in live]
    dist = convolve(dists)
    tobs = sum(t[0] for t in live)
    p_obs = dist.get(tobs, 0.0)
    one = sum(p for t, p in dist.items() if t >= tobs)
    two = sum(p for t, p in dist.items() if p <= p_obs * (1 + 1e-9))
    num = sum(a * d / (a + b + c + d) for a, b, c, d in live)
    den = sum(b * c / (a + b + c + d) for a, b, c, d in live)
    return {"strata_used": len(live), "T_observed": tobs,
            "E_T_under_null": round(sum(sum(a * p for a, p in d.items()) for d in dists), 4),
            "p_one_sided_emc_higher": round(one, 6),
            "p_two_sided_point_prob": round(two, 6),
            "mantel_haenszel_odds_ratio": (round(num / den, 4) if den else None),
            "note": "Exact conditional test; strata with an empty row or zero flagged sentences carry no information and are dropped (they contribute a degenerate distribution)."}


def cell(sents, rx):
    k = sum(1 for s in sents if rx.search(s))
    return k, len(sents) - k


def main():
    papers = json.loads(PROBE.read_text())["terminal_events"]
    rows = []
    for p in papers:
        stratum, trigger = classify(p.get("title"), p.get("journal"))
        rows.append({"pmid": p.get("pmid"), "title": p.get("title"), "journal": p.get("journal"),
                     "emc": bool(EMC_TITLE.search(p.get("title") or "")),
                     "stratum": stratum, "trigger": trigger,
                     "sentences": [s["sentence"] for s in p["sentences"]]})

    # --- A. composition ---
    comp = {}
    for s in STRATA:
        e = [r for r in rows if r["stratum"] == s and r["emc"]]
        o = [r for r in rows if r["stratum"] == s and not r["emc"]]
        comp[s] = {"emc_papers": len(e), "other_papers": len(o),
                   "emc_sentences": sum(len(r["sentences"]) for r in e),
                   "other_sentences": sum(len(r["sentences"]) for r in o)}
    tot_e_p = sum(c["emc_papers"] for c in comp.values())
    tot_o_p = sum(c["other_papers"] for c in comp.values())
    for s, c in comp.items():
        c["emc_paper_share"] = round(c["emc_papers"] / tot_e_p, 4)
        c["other_paper_share"] = round(c["other_papers"] / tot_o_p, 4)

    def strat_block(rx, strata_of, keys):
        out = {}
        tables = []
        for s in keys:
            e = [x for r in rows if strata_of(r) == s and r["emc"] for x in r["sentences"]]
            o = [x for r in rows if strata_of(r) == s and not r["emc"] for x in r["sentences"]]
            ka, kb = cell(e, rx)
            kc, kd = cell(o, rx)
            ep = [r for r in rows if strata_of(r) == s and r["emc"]]
            op = [r for r in rows if strata_of(r) == s and not r["emc"]]
            out[s] = {
                "emc": {"papers": len(ep), "sentences": ka + kb, "flagged": ka,
                        "rate": round(ka / (ka + kb), 4) if ka + kb else None,
                        "wilson95": wilson(ka, ka + kb),
                        "papers_with_flag": sum(1 for r in ep if any(rx.search(x) for x in r["sentences"]))},
                "other": {"papers": len(op), "sentences": kc + kd, "flagged": kc,
                          "rate": round(kc / (kc + kd), 4) if kc + kd else None,
                          "wilson95": wilson(kc, kc + kd),
                          "papers_with_flag": sum(1 for r in op if any(rx.search(x) for x in r["sentences"]))},
                "fisher_two_sided": fisher(ka, kb, kc, kd),
                "direction": (None if not (ka + kb) or not (kc + kd) else
                              "emc_higher" if ka / (ka + kb) > kc / (kc + kd) else
                              "emc_lower" if ka / (ka + kb) < kc / (kc + kd) else "equal"),
            }
            tables.append((ka, kb, kc, kd))
        return out, tables

    results = {}
    for name, rx in INSTRUMENTS.items():
        five, t5 = strat_block(rx, lambda r: r["stratum"], STRATA)
        coll_key = lambda r: ("case_report_or_series" if r["stratum"] == "case_report_or_series"
                              else "all_other_genres")
        two, t2 = strat_block(rx, coll_key, ["case_report_or_series", "all_other_genres"])
        # unstratified, reproducing the completed lane's headline
        alle = [x for r in rows if r["emc"] for x in r["sentences"]]
        allo = [x for r in rows if not r["emc"] for x in r["sentences"]]
        ka, kb = cell(alle, rx); kc, kd = cell(allo, rx)
        crude = {"emc": {"flagged": ka, "sentences": ka + kb,
                         "rate": round(ka / (ka + kb), 4), "wilson95": wilson(ka, ka + kb)},
                 "other": {"flagged": kc, "sentences": kc + kd,
                           "rate": round(kc / (kc + kd), 4), "wilson95": wilson(kc, kc + kd)},
                 "fisher_two_sided": fisher(ka, kb, kc, kd)}
        # E. direct standardisation on the five strata
        we = {s: comp[s]["emc_sentences"] for s in STRATA}
        wo = {s: comp[s]["other_sentences"] for s in STRATA}
        se, so = sum(we.values()), sum(wo.values())
        def std(rate_key, weights, wsum):
            acc, used = 0.0, 0
            for s in STRATA:
                r = five[s][rate_key]["rate"]
                if r is None:
                    continue
                acc += weights[s] / wsum * r
                used += weights[s]
            return round(acc, 5), round(used / wsum, 4)
        emc_std_to_other, cov1 = std("emc", wo, so)
        other_std_to_emc, cov2 = std("other", we, se)
        results[name] = {
            "crude_unstratified": crude,
            "by_five_strata": five,
            "exact_stratified_five": exact_stratified(t5),
            "by_case_vs_noncase": two,
            "exact_stratified_case_vs_noncase": exact_stratified(t2),
            "direct_standardisation": {
                "emc_rate_standardised_to_comparator_genre_mix": emc_std_to_other,
                "weight_coverage": cov1,
                "comparator_rate_standardised_to_emc_genre_mix": other_std_to_emc,
                "weight_coverage_2": cov2,
                "crude_emc_rate": crude["emc"]["rate"],
                "crude_other_rate": crude["other"]["rate"]},
            "flagged_sentences_by_stratum": {
                s: {"emc": [{"pmid": r["pmid"], "sentence": x} for r in rows
                            if r["stratum"] == s and r["emc"] for x in r["sentences"] if rx.search(x)],
                    "other": [{"pmid": r["pmid"], "sentence": x} for r in rows
                              if r["stratum"] == s and not r["emc"] for x in r["sentences"] if rx.search(x)]}
                for s in STRATA} if name == "strict_terminal_event" else "omitted (28 sentences; see completed lane)",
        }

    # --- F. misclassification simulation on the collapsed case/non-case contrast ---
    sim = {}
    for name, rx in INSTRUMENTS.items():
        flags = [(r["emc"], r["stratum"] == "case_report_or_series",
                  [bool(rx.search(x)) for x in r["sentences"]]) for r in rows]
        for err, label in ((0.10, "e=0.10 (measured case-report recall miss)"),
                           (0.30, "e=0.30 (measured overall disagreement rate)")):
            rng = random.Random(20260908)
            ps, dirs = [], {"emc_higher": 0, "emc_lower_or_equal": 0}
            for _ in range(2000):
                tabs = {True: [0, 0, 0, 0], False: [0, 0, 0, 0]}
                for emc, iscase, fl in flags:
                    g = (not iscase) if rng.random() < err else iscase
                    t = tabs[g]
                    for f in fl:
                        if emc:
                            t[0 if f else 1] += 1
                        else:
                            t[2 if f else 3] += 1
                res = exact_stratified([tuple(tabs[True]), tuple(tabs[False])])
                if res:
                    ps.append(res["p_two_sided_point_prob"])
                    dirs["emc_higher" if res["mantel_haenszel_odds_ratio"] and res["mantel_haenszel_odds_ratio"] > 1 else "emc_lower_or_equal"] += 1
            ps.sort()
            sim[f"{name} {label}"] = {
                "n_sims": len(ps),
                "median_p_two_sided": round(ps[len(ps) // 2], 6) if ps else None,
                "p_2.5pct": round(ps[int(0.025 * len(ps))], 6) if ps else None,
                "p_97.5pct": round(ps[int(0.975 * len(ps))], 6) if ps else None,
                "frac_p_below_0.05": round(sum(1 for p in ps if p < 0.05) / len(ps), 4) if ps else None,
                "direction_counts": dirs}

    src = (pathlib.Path(__file__).parent / "genre_classifier.py").read_bytes()
    out = {
        "_what_this_is": __doc__.strip(),
        "_sentence_is_not_a_patient": (
            "Every count in this file is a count of SENTENCES matched by a regular expression. "
            "A matched sentence is not a death, not a patient and not a cause. Nothing here "
            "assigns a cause of death, reinterprets any survival curve, or makes any clinical "
            "or patient-specific claim."),
        "classifier_sha256_at_analysis_time": hashlib.sha256(src).hexdigest(),
        "inputs": {"probe": str(PROBE.relative_to(ROOT)),
                   "emc_title_regex": EMC_TITLE.pattern,
                   "genre_rule": "genre_classifier.py (frozen; see checks/02)"},
        "composition_by_stratum": comp,
        "results": results,
        "misclassification_simulation": sim,
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print("classifier_sha256_at_analysis_time:", out["classifier_sha256_at_analysis_time"])
    print("\n== COMPOSITION (papers / death-cue sentences) ==")
    for s in STRATA:
        c = comp[s]
        print(f'{s:26s} EMC {c["emc_papers"]:3d}p ({c["emc_paper_share"]:.0%}) {c["emc_sentences"]:4d}s | '
              f'OTH {c["other_papers"]:3d}p ({c["other_paper_share"]:.0%}) {c["other_sentences"]:4d}s')
    for name in INSTRUMENTS:
        r = results[name]
        print(f"\n== {name} ==")
        c = r["crude_unstratified"]
        print(f'  crude: EMC {c["emc"]["flagged"]}/{c["emc"]["sentences"]}={c["emc"]["rate"]:.4f} vs '
              f'OTH {c["other"]["flagged"]}/{c["other"]["sentences"]}={c["other"]["rate"]:.4f}  Fisher p={c["fisher_two_sided"]}')
        for s in STRATA:
            b = r["by_five_strata"][s]
            print(f'  {s:26s} EMC {b["emc"]["flagged"]:3d}/{b["emc"]["sentences"]:4d} '
                  f'({"n/a" if b["emc"]["rate"] is None else format(b["emc"]["rate"], ".4f")}) | '
                  f'OTH {b["other"]["flagged"]:3d}/{b["other"]["sentences"]:4d} '
                  f'({"n/a" if b["other"]["rate"] is None else format(b["other"]["rate"], ".4f")})  '
                  f'Fisher p={b["fisher_two_sided"]}  {b["direction"]}')
        print("  exact stratified (5 strata):", json.dumps(r["exact_stratified_five"]))
        print("  case vs non-case:")
        for s in ("case_report_or_series", "all_other_genres"):
            b = r["by_case_vs_noncase"][s]
            print(f'    {s:24s} EMC {b["emc"]["flagged"]:3d}/{b["emc"]["sentences"]:4d} | '
                  f'OTH {b["other"]["flagged"]:3d}/{b["other"]["sentences"]:4d}  Fisher p={b["fisher_two_sided"]}  {b["direction"]}')
        print("  exact stratified (case vs non-case):", json.dumps(r["exact_stratified_case_vs_noncase"]))
        print("  standardisation:", json.dumps(r["direct_standardisation"]))
    print("\n== MISCLASSIFICATION SIMULATION ==")
    print(json.dumps(sim, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
