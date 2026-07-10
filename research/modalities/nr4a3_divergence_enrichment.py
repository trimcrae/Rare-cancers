#!/usr/bin/env python3
"""
Statistical test for review comment 9: is the orthosteric cryptic pocket (Pocket 5) SIGNIFICANTLY more
paralogue-divergent than the rest of the NR4A3 LBD, or is 7/10 unremarkable? We test Pocket-5 divergence
against the pooled background of all other LBD pocket-lining residues with a one-sided Fisher exact test
(pure-python hypergeometric; no scipy dependency), for both "divergent vs >=1 paralogue" and "vs both".

Input: nr4a-selectivity.json (BLOSUM62 alignment of NR4A3 vs NR4A1/NR4A2; per-residue AAs + divergent
flag). Output: nr4a3-divergence-enrichment.json. Pure + unit-tested.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "nr4a-selectivity.json")
OUT = os.path.join(HERE, "nr4a3-divergence-enrichment.json")
ORTHOSTERIC_DRUGGABILITY = 0.495  # Pocket 5 is the orthosteric warhead pocket (unique by this score)


def _hypergeom_pmf(k, N, K, n):
    """P(X = k): draw n from N with K successes."""
    return (math.comb(K, k) * math.comb(N - K, n - k)) / math.comb(N, n)


def fisher_exact_greater(a, b, c, d):
    """One-sided Fisher exact p-value for enrichment of the first row (a) over the table
    [[a, b], [c, d]]. Returns P(X >= a) under the hypergeometric null."""
    N = a + b + c + d
    K = a + c          # total 'divergent'
    n = a + b          # pocket size
    lo = max(0, n - (N - K))
    hi = min(n, K)
    p = 0.0
    for k in range(a, hi + 1):
        if k < lo:
            continue
        p += _hypergeom_pmf(k, N, K, n)
    return min(1.0, p)


def _aa(tok):
    """'D423' -> 'D' (nr4a3 AA); paralogue tokens are already single letters."""
    return tok[0] if tok else ""


def collect_residues(data):
    """Return {resnum: {'div1': bool, 'divboth': bool, 'pocket5': bool}} deduped across all LBD pockets.
    A residue is 'pocket5' if it lines the orthosteric pocket (the one with druggability 0.495)."""
    out = {}
    for pk in data["nr4a3_lbd_pockets"]:
        is_p5 = abs(pk.get("druggability", 0) - ORTHOSTERIC_DRUGGABILITY) < 1e-6
        for r in pk.get("residues", []):
            tok = r.get("nr4a3", "")
            num = "".join(ch for ch in tok if ch.isdigit())
            if not num:
                continue
            a3 = _aa(tok)
            a1, a2 = r.get("nr4a1", ""), r.get("nr4a2", "")
            div1 = bool(r.get("divergent", (a3 != a1) or (a3 != a2)))
            divboth = (a3 != a1) and (a3 != a2) and bool(a1) and bool(a2)
            e = out.setdefault(num, {"div1": div1, "divboth": divboth, "pocket5": False})
            e["div1"] = e["div1"] or div1
            e["divboth"] = e["divboth"] or divboth
            if is_p5:
                e["pocket5"] = True
    return out


def enrichment(residues):
    p5 = [r for r in residues.values() if r["pocket5"]]
    rest = [r for r in residues.values() if not r["pocket5"]]
    res = {}
    for key in ("div1", "divboth"):
        a = sum(1 for r in p5 if r[key])
        b = len(p5) - a
        c_div = sum(1 for r in rest if r[key])
        c_not = len(rest) - c_div
        p = fisher_exact_greater(a, b, c_div, c_not)
        res[key] = {
            "pocket5_divergent": a, "pocket5_total": len(p5),
            "background_divergent": c_div, "background_total": len(rest),
            "pocket5_frac": round(a / len(p5), 3) if p5 else None,
            "background_frac": round(c_div / len(rest), 3) if rest else None,
            "fisher_p_one_sided": round(p, 5),
        }
    return res


def main():
    data = json.load(open(SRC))
    residues = collect_residues(data)
    res = enrichment(residues)
    out = {
        "_title": "Pocket-5 paralogue-divergence enrichment vs the LBD pocket-residue background (review comment 9)",
        "_method": "One-sided Fisher exact (pure hypergeometric) on deduped LBD pocket-lining residues; "
                   "Pocket 5 = orthosteric warhead pocket (druggability 0.495).",
        "n_unique_lbd_pocket_residues": len(residues),
        "results": res,
    }
    json.dump(out, open(OUT, "w"), indent=2)
    for key, r in res.items():
        print(f"{key}: pocket5 {r['pocket5_divergent']}/{r['pocket5_total']} ({r['pocket5_frac']}) vs "
              f"background {r['background_divergent']}/{r['background_total']} ({r['background_frac']}) "
              f"-> Fisher p(one-sided) = {r['fisher_p_one_sided']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
