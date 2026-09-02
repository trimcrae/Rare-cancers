#!/usr/bin/env python3
"""Exact p, 95% confidence interval and within-platform Benjamini-Hochberg q for the EMC tissue read.

WHY THIS EXISTS. `emc-expression-panels.json` reports every array contrast as a Welch delta with its
t and degrees of freedom, and its verdict strings threshold |t| at 2. A threshold on |t| is not a
test: at these degrees of freedom the two-sided 95% critical value is 2.17 to 2.48, so |t| >= 2 is
MORE permissive than a 95% interval, and the surrogate stage one step earlier already applies
Benjamini-Hochberg. This module closes that gap by computing, from the same committed per-sample
values, the quantities a reader needs to apply a stated alpha: the exact two-sided p, the 95%
interval on delta, and a within-platform BH q across every readable gene on the 100-gene board.

It also runs the three sensitivity analyses the read needs and could not previously cite:

  (a) GPL3290 against the three dermatofibrosarcoma protuberans arrays alone. The deposit's own
      verbatim annotations show the ten EMC and three DFSP arrays were hybridised against a CRH
      reference from mRNA while the three gastrointestinal stromal tumour arrays are total RNA
      against a UHR reference, so half the six-sample comparator arm differs from the EMC arm in
      both reference pool and RNA input. The DFSP-only contrast is reference-matched on both sides.
  (b) GPL6244 with the five solitary fibrous tumour arrays added to the comparator arm. The deposit
      carries 42 samples and the primary analysis classifies 35; the seven the string matcher leaves
      unclassified are five solitary fibrous tumours and two pooled normal skeletal-muscle arrays.
  (c) The two pooled normal skeletal-muscle arrays as a qualitative normal soft-tissue anchor. They
      are the only normal soft tissue anywhere in the study, and the exposure axis's stated binding
      limitation is that its normal arm is visceral organs containing almost no soft tissue.

INPUTS, all committed and all read locally:
  research/modalities/emc-expression-panels-inputs.json   per-sample values, 42 and 16 samples,
                                                          and each sample's whole-array mean and sd
  research/modalities/emc-expression-panels.json          the 100-gene board and the panel scores

The per-sample z is (value - that sample's whole-array mean) / that sample's whole-array sd, which
is the standardisation `emc_expression_panels.py` uses; the module asserts that every recomputed
delta, t and df reproduces the committed one before it writes anything.

    python3 research/modalities/emc_tissue_read_statistics.py
    python3 research/modalities/emc_tissue_read_statistics.py --check   # verify, write nothing
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "emc-expression-panels-inputs.json")
PANELS = os.path.join(HERE, "emc-expression-panels.json")
OUT = os.path.join(HERE, "emc-tissue-read-statistics.json")

G24 = "GSE24369_series_matrix.txt.gz"
G43 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATFORM = {G24: "GPL6244", G43: "GPL3290"}

ALPHA = 0.05
MIN_ARM = 3          # a contrast needs at least three values on each side

#: The comparator arms of the primary analysis, and the two arms it silently excluded.
CLASSES_6244 = {
    "extraskeletal myxoid chondrosarcoma": "EMC",
    "low-grade fibromyxoid": "LGFMS",
    "desmoid": "desmoid_fibromatosis",
    "myxofibrosarcoma": "myxofibrosarcoma",
    "solitary fibrous": "SFT",
    "skeletal muscle": "normal_skeletal_muscle",
}
CLASSES_3290 = {"chondrosarcoma": "EMC", "dfsp": "DFSP", "gist": "GIST"}
COMPARATOR_6244 = ("LGFMS", "desmoid_fibromatosis", "myxofibrosarcoma")
COMPARATOR_3290 = ("DFSP", "GIST")


# ── Student t, stdlib only ────────────────────────────────────────────────────────────────
def _betacf(a, b, x):
    maxit, eps, fpmin = 300, 3.0e-16, 1.0e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (fpmin if abs(d) < fpmin else d)
    h = d
    for m in range(1, maxit + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (fpmin if abs(d) < fpmin else d)
        c = 1.0 + aa / c
        c = fpmin if abs(c) < fpmin else c
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (fpmin if abs(d) < fpmin else d)
        c = 1.0 + aa / c
        c = fpmin if abs(c) < fpmin else c
        step = d * c
        h *= step
        if abs(step - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbeta + a * math.log(x) + b * math.log1p(-x)) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta + b * math.log1p(-x) + a * math.log(x)) * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t, df):
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(df, alpha=ALPHA):
    """Two-sided critical value by bisection on the exact two-sided p."""
    lo, hi = 0.0, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_two_sided_p(mid, df) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def welch(a, b):
    na, nb = len(a), len(b)
    if na < MIN_ARM or nb < MIN_ARM:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se2 = va / na + vb / nb
    if se2 <= 0:
        return None
    se, d = math.sqrt(se2), ma - mb
    t = d / se
    df = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    half = t_crit(df) * se
    return {"delta": round(d, 4), "t": round(t, 3), "df": round(df, 1),
            "p": t_two_sided_p(t, df), "ci_lo": round(d - half, 4), "ci_hi": round(d + half, 4),
            "n_emc": na, "n_comparator": nb}


def benjamini_hochberg(pvals):
    """{key: q} over {key: p}."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    n, out, prev = len(items), {}, 1.0
    for i in range(n - 1, -1, -1):
        key, p = items[i]
        prev = min(prev, p * n / (i + 1))
        out[key] = prev
    return out


# ── data ──────────────────────────────────────────────────────────────────────────────────
def _classify(annotation, table):
    low = annotation.lower()
    for needle, label in table.items():
        if needle in low:
            return label
    return "unclassified"


class Cohort:
    def __init__(self, inputs, key, table):
        self.key = key
        self.platform = PLATFORM[key]
        t = inputs["targets"][key]
        self.background = t["background_per_sample"]
        self.samples = t["samples"]
        self.genes = t["genes"]
        self.cls = [_classify(s["annotation_verbatim"], table) for s in self.samples]

    def z(self, gene):
        g = self.genes.get(gene)
        if not g:
            return None
        return [None if v is None else (v - self.background[i]["mean"]) / self.background[i]["sd"]
                for i, v in enumerate(g["values"])]

    def contrast(self, gene, comparator):
        z = self.z(gene)
        if z is None:
            return None
        emc = [v for v, c in zip(z, self.cls) if c == "EMC" and v is not None]
        cmp_ = [v for v, c in zip(z, self.cls) if c in comparator and v is not None]
        return welch(emc, cmp_)

    def arm_mean(self, gene, label):
        z = self.z(gene)
        if z is None:
            return None
        vals = [v for v, c in zip(z, self.cls) if c == label and v is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    def counts(self):
        return {c: self.cls.count(c) for c in sorted(set(self.cls))}


def _board(panels):
    return panels["reads"]["read_8_SURFACE_ANTIGEN"]["cross_platform_board"]["per_gene"]


def _corrected(cohort, genes, comparator):
    rows = {}
    for g in genes:
        r = cohort.contrast(g, comparator)
        if r:
            rows[g] = r
    q = benjamini_hochberg({g: r["p"] for g, r in rows.items()})
    for g, r in rows.items():
        r["q"] = q[g]
        r["significant"] = q[g] < ALPHA
        r["p"] = round(r["p"], 6)
        r["q"] = round(q[g], 6)
    return rows


def _state(a, b):
    """Cross-platform state under the corrected criterion."""
    if a is None and b is None:
        return "NOT_READABLE_ON_EITHER_PLATFORM"
    if a is None or b is None:
        return "READABLE_ON_ONE_PLATFORM_ONLY"
    if a["significant"] and b["significant"]:
        if a["delta"] > 0 and b["delta"] > 0:
            return "CONCORDANT_UP_ON_BOTH"
        if a["delta"] < 0 and b["delta"] < 0:
            return "CONCORDANT_DOWN_ON_BOTH"
        return "DISCORDANT_OPPOSITE_SIGNS"
    if a["significant"] or b["significant"]:
        return "MOVED_ON_ONE_FLAT_ON_THE_OTHER"
    return "FLAT_ON_BOTH"


def _verify(panels, primary):
    """Every recomputed delta, t and df must reproduce the committed contrast."""
    board, bad = _board(panels), []
    for gene, row in board.items():
        for key in (G24, G43):
            committed = row.get("per_platform", {}).get(key)
            mine = primary[PLATFORM[key]].get(gene)
            if not committed or "t" not in committed or not mine:
                continue
            if (abs(committed["t"] - mine["t"]) > 0.02
                    or abs(committed["delta_a_minus_b"] - mine["delta"]) > 0.002
                    or abs(committed["df"] - mine["df"]) > 0.15):
                bad.append(f"{gene}/{PLATFORM[key]}")
    return bad


def main(argv):
    inputs = json.load(open(INPUTS, encoding="utf-8"))
    panels = json.load(open(PANELS, encoding="utf-8"))
    board = _board(panels)
    genes = sorted(board)

    c6244 = Cohort(inputs, G24, CLASSES_6244)
    c3290 = Cohort(inputs, G43, CLASSES_3290)

    primary = {"GPL6244": _corrected(c6244, genes, COMPARATOR_6244),
               "GPL3290": _corrected(c3290, genes, COMPARATOR_3290)}
    bad = _verify(panels, primary)
    if bad:
        raise SystemExit("recomputed contrasts disagree with the committed artifact: "
                         + ", ".join(bad))

    states = {}
    for g in genes:
        states[g] = _state(primary["GPL6244"].get(g), primary["GPL3290"].get(g))
    by_state = {}
    for g, s in states.items():
        by_state.setdefault(s, []).append(g)
    by_state = {k: sorted(v) for k, v in sorted(by_state.items())}

    dfsp_only = _corrected(c3290, genes, ("DFSP",))
    with_sft = _corrected(c6244, genes, COMPARATOR_6244 + ("SFT",))

    def conc(a_rows, b_rows, sign):
        out = []
        for g in genes:
            a, b = a_rows.get(g), b_rows.get(g)
            if a and b and a["significant"] and b["significant"]:
                if sign > 0 and a["delta"] > 0 and b["delta"] > 0:
                    out.append(g)
                if sign < 0 and a["delta"] < 0 and b["delta"] < 0:
                    out.append(g)
        return sorted(out)

    def resolution(rows):
        halves = sorted((r["ci_hi"] - r["ci_lo"]) / 2 for r in rows.values())
        sig = [abs(r["delta"]) for r in rows.values() if r["significant"]]
        mid = halves[len(halves) // 2] if halves else None
        return {"n_readable": len(rows),
                "n_significant": len(sig),
                "median_ci_half_width_sd": round(mid, 3) if mid else None,
                "smallest_significant_abs_delta_sd": round(min(sig), 3) if sig else None}

    muscle_genes = ["ALCAM", "CSPG4", "CD44", "VCAN", "BGN", "GPC1", "CD248", "CD276", "FAP",
                    "SSTR2", "PRAME", "FGFR1", "PTK7", "DLL3", "NR4A3", "ENO3", "MKI67"]
    muscle = {}
    for g in muscle_genes:
        emc = c6244.arm_mean(g, "EMC")
        if emc is None:
            continue
        mus = c6244.arm_mean(g, "normal_skeletal_muscle")
        z = c6244.z(g)
        cmp_ = [v for v, c in zip(z, c6244.cls) if c in COMPARATOR_6244 and v is not None]
        muscle[g] = {"emc_mean_z": emc,
                     "comparator_mean_z": round(sum(cmp_) / len(cmp_), 4),
                     "pooled_skeletal_muscle_mean_z": mus,
                     "emc_minus_muscle_z": round(emc - mus, 4) if mus is not None else None}

    panel_p = {}
    for name, grp in panels["panels"]["surface_antigen"]["groups"].items():
        row = {}
        for key in (G24, G43):
            pp = grp["per_platform"].get(key, {})
            score = pp.get("score")
            if not score:
                row[PLATFORM[key]] = {"scored": False,
                                      "n_genes_readable": pp.get("n_genes_readable"),
                                      "n_genes_requested": pp.get("n_genes_requested")}
                continue
            row[PLATFORM[key]] = {"scored": True, "delta": score["delta_a_minus_b"],
                                  "t": score["t"], "df": score["df"],
                                  "p": round(t_two_sided_p(score["t"], score["df"]), 4),
                                  "n_genes_readable": pp.get("n_genes_readable"),
                                  "n_genes_requested": pp.get("n_genes_requested")}
        panel_p[name] = row

    out = {
        "_what": "Exact two-sided p, 95% confidence interval and within-platform Benjamini-Hochberg "
                 "q for every gene on the 100-gene cross-platform board, plus three sensitivity "
                 "analyses, computed from the committed per-sample values.",
        "_why": "The board's verdict strings threshold |t| at 2, which at these degrees of freedom "
                "is more permissive than a 95% interval, and the surrogate stage one step earlier "
                "already corrects for multiple testing. Every count in the manuscript is derived "
                "from this file rather than from a |t| threshold.",
        "_cost": "$0. Committed artifacts only; no network, no GPU.",
        "_alpha": ALPHA,
        "_correction": "Benjamini-Hochberg within platform, across every gene on the board that "
                       "produced a contrast on that platform. The two platforms are corrected "
                       "separately because they are different instruments with different "
                       "comparator arms, and concordance requires both.",
        "_verified_against": "research/modalities/emc-expression-panels.json — every delta, t and "
                             "df below reproduces the committed contrast before this file is "
                             "written; a disagreement is a hard failure of this module.",
        "_not_a_test": "The 3'-end sequencing cohort carries no test here or anywhere. It is "
                       "medians of per-peak medians at n = 4.",
        "_language_discipline": "Transcript abundance only. Nothing here measures protein, surface "
                                "localisation, receptor density, safety, a therapeutic window or "
                                "clinical readiness for any antigen or agent.",
        "cohorts": {
            "GPL6244": {"series": "GSE24369", "n_samples_in_deposit": len(c6244.samples),
                        "class_counts": c6244.counts(),
                        "comparator_arm_of_the_primary_analysis": list(COMPARATOR_6244),
                        "_excluded_from_the_primary_analysis":
                            "five solitary fibrous tumour arrays and two pooled normal "
                            "skeletal-muscle arrays; both are used in the sensitivity analyses "
                            "below and neither enters the primary contrast."},
            "GPL3290": {"series": "GSE4303", "n_samples_in_deposit": len(c3290.samples),
                        "class_counts": c3290.counts(),
                        "comparator_arm_of_the_primary_analysis": list(COMPARATOR_3290),
                        "_reference_and_input_mismatch":
                            "the deposit's verbatim annotations record the EMC and DFSP arrays as "
                            "mRNA against a CRH reference and the GIST arrays as total RNA against "
                            "a UHR reference, so half the comparator arm differs from the EMC arm "
                            "in both reference pool and RNA input."},
        },
        "primary": primary,
        "cross_platform_state_corrected": {"by_gene": states, "by_state": by_state},
        "resolution": {"GPL6244": resolution(primary["GPL6244"]),
                       "GPL3290": resolution(primary["GPL3290"]),
                       "_how_to_read": "the half-width of a gene's 95% interval is the elevation "
                                       "that gene's data cannot exclude. Concordance requires both "
                                       "platforms, so the design is governed by the wider one."},
        "sensitivity_reference_matched_GPL3290_DFSP_only": {
            "_what": "GPL3290 with the three GIST arrays dropped, leaving a comparator arm "
                     "processed like the EMC arm: mRNA against a CRH reference on both sides.",
            "rows": dfsp_only,
            "concordant_up_with_GPL6244": conc(primary["GPL6244"], dfsp_only, +1),
            "concordant_down_with_GPL6244": conc(primary["GPL6244"], dfsp_only, -1),
            "n_sign_changes_vs_the_full_comparator_arm": sum(
                1 for g in dfsp_only if g in primary["GPL3290"]
                and (dfsp_only[g]["delta"] > 0) != (primary["GPL3290"][g]["delta"] > 0)),
            "genes_changing_sign": sorted(
                g for g in dfsp_only if g in primary["GPL3290"]
                and (dfsp_only[g]["delta"] > 0) != (primary["GPL3290"][g]["delta"] > 0)),
        },
        "sensitivity_GPL6244_with_solitary_fibrous_tumour": {
            "_what": "GPL6244 with the five solitary fibrous tumour arrays added to the comparator "
                     "arm, giving 6 against 34.",
            "rows": with_sft,
            "concordant_up_with_GPL3290": conc(with_sft, primary["GPL3290"], +1),
            "concordant_down_with_GPL3290": conc(with_sft, primary["GPL3290"], -1),
            "n_sign_changes_vs_the_29_sample_comparator_arm": sum(
                1 for g in with_sft if g in primary["GPL6244"]
                and (with_sft[g]["delta"] > 0) != (primary["GPL6244"][g]["delta"] > 0)),
            "genes_changing_sign": sorted(
                g for g in with_sft if g in primary["GPL6244"]
                and (with_sft[g]["delta"] > 0) != (primary["GPL6244"][g]["delta"] > 0)),
        },
        "normal_skeletal_muscle_anchor": {
            "_what": "The two pooled normal skeletal-muscle arrays in GSE24369, the only normal "
                     "soft tissue in this study, read on the same platform as the primary cohort.",
            "_limits": "n = 2, pooled RNA rather than individual donors, one tissue rather than a "
                       "normal-tissue panel, and no test is computed. It is an anchor, not an arm.",
            "_the_control_that_qualifies_it": "ENO3 and NR4A3, the instrument's two positive "
                                              "controls, both read HIGHER in pooled skeletal "
                                              "muscle than in EMC. Both are muscle-expressed, so "
                                              "the anchor behaves as normal muscle should and the "
                                              "two controls do not discriminate this disease from "
                                              "that tissue.",
            "rows": muscle,
        },
        "panel_scores_with_p": {
            "_what": "The committed panel-level scores with their exact two-sided p, so panels and "
                     "genes are judged by one rule.",
            "rows": panel_p,
        },
    }

    if "--check" in argv:
        print(f"emc_tissue_read_statistics: verified, {len(genes)} board genes, "
              f"{len(primary['GPL6244'])} readable on GPL6244, {len(primary['GPL3290'])} on GPL3290")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(os.path.dirname(HERE)))}")
    print("  concordant up  :", by_state.get("CONCORDANT_UP_ON_BOTH", []))
    print("  concordant down:", by_state.get("CONCORDANT_DOWN_ON_BOTH", []))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
