#!/usr/bin/env python3
"""The four controls the PRMT5 manuscript stated and never ran.

⭐ WHY THIS EXISTS. `emc-mtap-prmt5-hypothesis.md` names its own weaknesses honestly and then leaves
three of them as prose. Each is answerable from data already on disk or one $0 CI fetch away, and a
falsifier nobody tried is not a falsifier — it is a disclaimer.

  1  EXACT PERMUTATION.  The manuscript's t-statistics come from Welch's test on 6 vs 29 and 10 vs 6
                         tumours. At that size the normal approximation is doing real work and the
                         reported t is the only evidence for the reading. Both designs are small
                         enough to ENUMERATE COMPLETELY — C(35,6) and C(16,10) — so an exact
                         permutation p is available and no distributional assumption is needed.
                         ⚠ It is exact for the LABELLING, not for the multiplicity: it answers "how
                         often does a random split of these tumours give a contrast this large",
                         which is a different question from "how many genes were tested".

  2  PRMT FAMILY.        Retrieved 2026-08-09: PRMT1 *and* PRMT5 are reported elevated together
                         across sarcoma types (PMID 40823091). If EMC's elevation is family-wide it
                         says something about transcriptional output, not about PRMT5. The
                         four-gene methylosome group could not ask this.

  3  PROLIFERATION.      Falsifier F7 of the manuscript — "the readings are not proliferation or
                         cellularity effects" — had no data behind it. Here the contrast is
                         recomputed on PRMT5 residuals after regressing out a per-sample
                         proliferation score.

  4  CHONDROID LINEAGE.  EMC is a chondroid tumour and no comparator in either series is
                         cartilage-lineage. ⛔ THIS CONTROL IS STRUCTURALLY WEAKER THAN THE OTHERS
                         AND SAYS SO: with no chondroid comparator it can only ask whether the two
                         move together WITHIN these samples. It cannot exclude "chondroid tumours
                         express PRMT5", and nothing here may be written as if it does.

⛔ AN ABSENT READING IS NOT A READING OF ABSENCE. Controls 2-4 need genes added to
`emc_expression_panels.PANELS` on 2026-08-09; until a `mode=panels` fetch runs, the panel artifact
does not carry them and this module reports NOT MEASURED — never "no confound found".

⛔ Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any agent.

$0 — reads committed artifacts, stdlib only, no network, no RNG.
"""
from __future__ import annotations

import itertools
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "emc-expression-panels.json")
OUT = os.path.join(HERE, "emc-prmt5-route-controls.json")

P6244 = "GSE24369_series_matrix.txt.gz"
P3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATS = (P6244, P3290)

THE_GENE = "PRMT5"
METHYLOSOME = ("PRMT5", "WDR77", "RIOK1", "CLNS1A")
PRMT_FAMILY = ("PRMT1", "PRMT2", "PRMT3", "CARM1", "PRMT5", "PRMT6", "PRMT7", "PRMT8", "PRMT9")
PROLIFERATION = ("MKI67", "PCNA", "TOP2A", "CCNB1", "RRM2", "BUB1", "AURKA", "MCM2", "TYMS",
                 "E2F1", "CCNA2", "CDK1")
CHONDROID = ("COL2A1", "COL9A1", "COL11A1", "COL11A2", "ACAN", "SOX9", "SOX5", "SOX6")

#: Above this many label assignments the exact enumeration is refused rather than approximated.
#: ⛔ NOT a switch to Monte Carlo — this module has no RNG, because a figure or a p-value that
#: changes between runs cannot be checked by anyone.
MAX_ENUMERATIONS = 4_000_000


def _t(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se = math.sqrt(va / na + vb / nb)
    return None if se == 0 else (ma - mb) / se


def _per_sample(panel, gene, plat):
    """[(gsm, class, z)] for one gene on one platform, or None if the read could not be taken."""
    v = (panel.get("gene_reads", {}).get(gene) or {}).get(plat)
    if not isinstance(v, dict) or not v.get("readable"):
        return None
    return [(s["gsm"], s["class"], s["z_vs_array"]) for s in v["per_sample"]
            if s.get("z_vs_array") is not None]


def exact_permutation(panel, gene, plat):
    rows = _per_sample(panel, gene, plat)
    if rows is None:
        return {"_status": "⛔ NOT READABLE on this platform — the read could not be taken. This "
                           "says NOTHING about whether the gene is expressed."}
    z = [r[2] for r in rows]
    emc = [i for i, r in enumerate(rows) if r[1] == "EMC"]
    n, k = len(z), len(emc)
    obs = _t([z[i] for i in emc], [z[i] for i in range(n) if i not in set(emc)])
    if obs is None:
        return {"_status": "no contrast computable — an arm has fewer than 2 values"}
    total = math.comb(n, k)
    if total > MAX_ENUMERATIONS:
        return {"_status": f"⚠ NOT ENUMERATED — {total} labelings exceeds this module's ceiling. "
                           f"No approximation is substituted; the question is left open.",
                "n_labelings": total}
    at_least = 0
    idx = range(n)
    for combo in itertools.combinations(idx, k):
        s = set(combo)
        t = _t([z[i] for i in combo], [z[i] for i in idx if i not in s])
        if t is not None and abs(t) >= abs(obs) - 1e-12:
            at_least += 1
    return {
        "_status": "EXACT — every labeling enumerated, no approximation and no random sampling",
        "n_EMC": k, "n_comparator": n - k, "n_labelings_enumerated": total,
        "observed_t": round(obs, 4),
        "n_labelings_at_least_as_extreme_two_sided": at_least,
        "exact_p_two_sided": round(at_least / total, 6),
        "⚠_what_this_p_is_not": "It is exact for the LABELLING only. It corrects nothing for the "
            "number of genes examined, and the manuscript's 'uncorrected for multiple testing' "
            "limit stands unchanged. The genome-wide placement below is the field that speaks to "
            "that, and it is a different quantity.",
    }


def _group_score(panel, genes, plat):
    """Per-sample mean z over the readable members. Returns (by_gsm, members_used, missing)."""
    got, missing = {}, []
    for g in genes:
        rows = _per_sample(panel, g, plat)
        if rows is None:
            missing.append(g)
            continue
        got[g] = {r[0]: r[2] for r in rows}
    if not got:
        return {}, [], missing
    gsms = set.intersection(*[set(v) for v in got.values()])
    by = {s: sum(got[g][s] for g in got) / len(got) for s in gsms}
    return by, sorted(got), missing


def _residualise(y_by_gsm, x_by_gsm):
    """y regressed on x (one covariate + intercept); returns residuals by gsm, plus the slope."""
    common = sorted(set(y_by_gsm) & set(x_by_gsm))
    if len(common) < 4:
        return None, None, common
    xs = [x_by_gsm[s] for s in common]
    ys = [y_by_gsm[s] for s in common]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None, None, common
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    return {s: y_by_gsm[s] - (a + b * x_by_gsm[s]) for s in common}, b, common


def _pearson(y_by_gsm, x_by_gsm):
    common = sorted(set(y_by_gsm) & set(x_by_gsm))
    if len(common) < 4:
        return None
    xs = [x_by_gsm[s] for s in common]
    ys = [y_by_gsm[s] for s in common]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def confound_control(panel, plat, genes, label):
    """Does PRMT5's EMC-vs-comparator contrast survive conditioning on this axis?"""
    rows = _per_sample(panel, THE_GENE, plat)
    if rows is None:
        return {"_status": f"⛔ {THE_GENE} NOT READABLE on this platform — control not runnable."}
    cls = {r[0]: r[1] for r in rows}
    y = {r[0]: r[2] for r in rows}
    x, used, missing = _group_score(panel, genes, plat)
    if not x:
        return {"_status": f"⛔ NOT MEASURED — no {label} gene is readable in the committed panel. "
                           f"Run `emc-expression-datasets.yml mode=panels` after the 2026-08-09 "
                           f"PANELS additions. THIS IS AN ABSENT READING, NOT A FINDING OF NO "
                           f"CONFOUND.",
                "genes_requested": list(genes), "genes_missing": missing}
    raw = _t([y[s] for s in y if cls[s] == "EMC"], [y[s] for s in y if cls[s] != "EMC"])
    resid, slope, common = _residualise(y, x)
    out = {
        "_status": "run",
        "axis": label,
        "genes_used": used,
        "genes_not_readable": missing,
        "⚠_coverage": f"{len(used)} of {len(genes)} requested genes readable — a score built on "
                      f"few genes is a weak instrument and a null from it is weak evidence.",
        "n_samples_scored": len(common),
        "score_is_higher_in_EMC_by_t": (
            round(_t([x[s] for s in common if cls.get(s) == "EMC"],
                     [x[s] for s in common if cls.get(s) not in (None, "EMC")]) or 0, 3)
            if len(common) > 3 else None),
        "correlation_of_PRMT5_with_the_score_across_all_samples": (
            round(_pearson(y, x), 3) if _pearson(y, x) is not None else None),
        "PRMT5_t_raw": round(raw, 3) if raw is not None else None,
        "regression_slope_PRMT5_on_score": round(slope, 3) if slope is not None else None,
    }
    if resid:
        rt = _t([resid[s] for s in common if cls.get(s) == "EMC"],
                [resid[s] for s in common if cls.get(s) not in (None, "EMC")])
        out["PRMT5_t_after_removing_the_score"] = round(rt, 3) if rt is not None else None
        if rt is not None and raw is not None:
            keeps = abs(rt) >= 0.6 * abs(raw) and (rt > 0) == (raw > 0)
            out["reading"] = (
                "✅ THE CONTRAST SURVIVES the adjustment — it retains its sign and most of its "
                "magnitude, so this axis does not account for it." if keeps else
                "⛔ THE CONTRAST DOES NOT SURVIVE the adjustment. On this platform the reading is "
                "consistent with being a shadow of this axis, and the manuscript must say so.")
    out["⛔_what_this_cannot_settle"] = (
        "A transcript score is a proxy. Adjusting for it removes the part of the contrast that is "
        "LINEARLY predicted by that proxy and nothing more; a confound the proxy measures badly "
        "survives adjustment untouched. And with n this small the adjustment itself is unstable.")
    return out


def family_specificity(panel, plat):
    rows = {}
    for g in PRMT_FAMILY:
        r = _per_sample(panel, g, plat)
        if r is None:
            rows[g] = {"readable": False,
                       "_meaning": "⛔ the read could not be taken on this platform — an "
                                   "instrument statement, never evidence the gene is not expressed"}
            continue
        cls = {x[0]: x[1] for x in r}
        z = {x[0]: x[2] for x in r}
        t = _t([z[s] for s in z if cls[s] == "EMC"], [z[s] for s in z if cls[s] != "EMC"])
        rows[g] = {"readable": True, "t": round(t, 3) if t is not None else None,
                   "n_EMC": sum(1 for s in z if cls[s] == "EMC"),
                   "n_comparator": sum(1 for s in z if cls[s] != "EMC")}
    scored = {g: v["t"] for g, v in rows.items() if v.get("t") is not None}
    if len(scored) < 3:
        return {"_status": "⛔ NOT MEASURED — fewer than 3 family members readable in the committed "
                           "panel. The PRMT family was added to PANELS on 2026-08-09; run "
                           "`emc-expression-datasets.yml mode=panels`. ABSENT READING, NOT a "
                           "finding that the elevation is PRMT5-specific.",
                "per_gene": rows}
    order = sorted(scored, key=lambda g: -scored[g])
    return {
        "_status": "run",
        "per_gene": rows,
        "n_family_members_readable": len(scored),
        "ranked_by_t_desc": order,
        "PRMT5_rank": order.index(THE_GENE) + 1 if THE_GENE in order else None,
        "reading": (
            f"⭐ {THE_GENE} is the highest-scoring readable PRMT on this platform — the elevation "
            f"is not simply family-wide." if order and order[0] == THE_GENE else
            f"⚠ {THE_GENE} is NOT the highest-scoring readable PRMT on this platform "
            f"({order[0] if order else '?'} is). Consistent with a family-wide or "
            f"transcription-wide effect rather than something specific to PRMT5, which is what "
            f"PMID 40823091 reports across sarcoma types."),
        "⛔_what_this_cannot_settle": "Abundance, not activity. Every PRMT here is a transcript "
            "level; none of them says an enzyme is working, and a family member with no probe is "
            "simply unread.",
    }


def genome_wide_placement(panel, plat):
    gw = ((panel.get("platforms") or {}).get(plat) or {}).get("genome_wide_null")
    if not gw or not gw.get("placed_wanted_genes"):
        return {"_status": "⛔ NOT AVAILABLE — the committed panel predates the genome-wide null "
                           "(added 2026-08-09). Run `emc-expression-datasets.yml mode=panels`. "
                           "The manuscript's 'uncorrected for multiple testing' limit therefore "
                           "stands with nothing measured against it."}
    placed = gw["placed_wanted_genes"]
    want = [g for g in (THE_GENE, "WDR77", "MAT2A", "MTAP", "CDKN2A", "CDKN2B", "NR4A3", "ENO3")
            if g in placed]
    return {
        "_status": "run",
        "n_symbols_scored": gw.get("n_symbols_scored"),
        "t_distribution": gw.get("t_distribution"),
        "self_check": gw.get("self_check"),
        "placed": {g: placed[g] for g in want},
        "⭐_how_to_read_it": "`frac_of_array_at_least_as_extreme_two_sided` is the fraction of all "
            "symbols on this array whose EMC-vs-comparator |t| is at least this gene's. NR4A3 and "
            "ENO3 are included as the instrument's positive controls: the disease-defining "
            "transcript and a published direct target should sit far out, and if they do not, no "
            "other row on this list means anything.",
        "⛔_not_a_correction": "This controls no error rate. It answers 'is this t remarkable on "
            "this array', which is the question the phrase 'uncorrected for multiple testing' "
            "leaves open — not the same as correcting for it.",
    }


def build():
    with open(PANEL, encoding="utf-8") as fh:
        panel = json.load(fh)
    per_plat = {}
    for plat in PLATS:
        per_plat[plat] = {
            "exact_permutation_PRMT5": exact_permutation(panel, THE_GENE, plat),
            "prmt_family_specificity": family_specificity(panel, plat),
            "proliferation_control": confound_control(panel, plat, PROLIFERATION, "proliferation"),
            "chondroid_lineage_control": confound_control(panel, plat, CHONDROID,
                                                          "chondroid lineage"),
            "genome_wide_placement": genome_wide_placement(panel, plat),
        }
    return {
        "_title": "The controls the EMC PRMT5 manuscript stated and had not run.",
        "_generated_by": "research/modalities/emc_prmt5_route_controls.py",
        "_source": "research/modalities/emc-expression-panels.json — every z is lifted from it; "
                   "nothing new is measured here, only cut differently and tested differently.",
        "_no_clinical_claim": "⛔ Nothing here asserts efficacy, safety, a therapeutic window or "
                              "clinical readiness for any agent in any disease.",
        "⚠_these_are_controls_not_further_hypothesis_tests": "They were specified before they were "
            "run, each against a named weakness in the manuscript. Reading a control's result as a "
            "new finding would be a multiplicity problem wearing a control's clothes.",
        "⛔_the_chondroid_control_is_the_weak_one_and_stays_labelled_so": "No comparator in either "
            "series is cartilage-lineage, so it can only ask whether PRMT5 and chondroid markers "
            "move together within these samples. 'Chondroid tumours express PRMT5' is NOT excluded "
            "by anything in this file.",
        "per_platform": per_plat,
    }


def main():
    res = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    for plat, r in res["per_platform"].items():
        print(f"  {plat[:28]}")
        p = r["exact_permutation_PRMT5"]
        print(f"    permutation : {p.get('_status','')[:40]} "
              f"t={p.get('observed_t')} exact_p={p.get('exact_p_two_sided')}")
        f = r["prmt_family_specificity"]
        print(f"    PRMT family : {f.get('reading', f.get('_status'))[:96]}")
        for key in ("proliferation_control", "chondroid_lineage_control"):
            c = r[key]
            print(f"    {key[:18]:18}: "
                  f"{c.get('reading', c.get('_status',''))[:92]}")
        g = r["genome_wide_placement"]
        if g.get("_status") == "run":
            for gene, v in g["placed"].items():
                print(f"      {gene:7} t={v['t']:+7.3f} "
                      f"top {100 * v['frac_of_array_at_least_as_extreme_two_sided']:.2f}% of array")
        else:
            print(f"    genome-wide : {g['_status'][:92]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
