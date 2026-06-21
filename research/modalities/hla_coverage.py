#!/usr/bin/env python3
"""
HLA population coverage for the EWSR1::NR4A3 fusion-junction neoepitopes.

Question this answers: if a recurrent breakpoint's junction epitope is presented on
allele(s) X, what fraction of patients carry >=1 presenting allele (i.e. could be
treated with a public fusion-directed vaccine/TCR-T)? That is the difference between an
interesting prediction and a clinically-framed lead.

Source (CI-fetchable, citable, reproducible — no invented frequencies):
  - Allele frequencies come from the Allele Frequency Net Database (AFND;
    Gonzalez-Galarza 2020, NAR 48:D783) via the `slowkow/allelefrequencies` mirror,
    which republishes AFND as one tab-delimited file (MIT-licensed). We use the mirror
    because AFND itself serves only its interactive search form to a non-browser client
    (the old direct-scrape path returned the empty form — see git history), whereas the
    mirror is a stable raw file reachable from CI and reproducible by commit.
  - Columns used: `allele` (2-field, e.g. A*02:01), `alleles_over_2n` (the population's
    allele frequency, copies/2N) and `n` (individuals sampled).

Method (matches METHODOLOGY.md: denominator-weighted pooling + Wilson 95% CI):
  - For each allele, reconstruct copies_i = round(af_i * 2*n_i) and pool over all AFND
    populations: af = Sigma(copies_i) / Sigma(2*n_i). This is a sample-size
    (2N)-weighted global frequency; larger studies carry more weight.
  - 95% CI: Wilson score interval on (Sigma copies, Sigma 2N).
  - Heterogeneity: report the per-population af range (global means hide large
    between-population variation; confirm per target population).
  - Carrier (phenotype) frequency = 1 - (1 - af)^2 (Hardy-Weinberg, >=1 copy).
  - Combined coverage of an allele set = 1 - prod_i (1 - af_i)^2 (independence across
    loci; the standard IEDB population-coverage formula). A coverage interval is
    propagated from the per-allele Wilson bounds (lower bound from each allele's CI low,
    upper from each CI high) as a transparent — if approximate — uncertainty band.
  - If an allele is absent from the source, it is recorded as source_unavailable rather
    than guessed.

Output: hla-coverage.json
"""

import csv
import io
import json
import math
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(__file__)
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
OUT = os.path.join(HERE, "hla-coverage.json")

# AFND republished as one MIT-licensed TSV; pin to a branch ref (reproducible by commit).
AFND_TSV_URL = "https://raw.githubusercontent.com/slowkow/allelefrequencies/main/afnd.tsv"
AFND_CITATION = ("Gonzalez-Galarza FF, et al. Allele frequency net database (AFND) 2020 "
                 "update. Nucleic Acids Res. 2020;48:D783-D788. Mirror: "
                 "github.com/slowkow/allelefrequencies (MIT).")


def fetch(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-hub/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return ""


def wilson(events, n, z=1.96):
    """Wilson score 95% interval for a binomial proportion (events out of n)."""
    if n <= 0:
        return (None, None)
    p = events / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = p + z2 / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (round((centre - half) / denom, 4), round((centre + half) / denom, 4))


def load_afnd_freqs(alleles):
    """Return {allele: info} with denominator(2N)-weighted af, Wilson CI, heterogeneity."""
    # AFND alleles are 2-field with no 'HLA-' prefix (e.g. A*02:01); our binders carry it.
    want = {a.replace("HLA-", ""): a for a in alleles}
    acc = {a: {"copies": 0, "twoN": 0, "pops": 0, "af_min": None, "af_max": None}
           for a in want}

    html = fetch(AFND_TSV_URL)
    source_ok = bool(html) and "alleles_over_2n" in html
    if source_ok:
        reader = csv.DictReader(io.StringIO(html), delimiter="\t")
        for row in reader:
            if row.get("group") != "hla":
                continue
            al = row.get("allele")
            if al not in want:
                continue
            try:
                af = float(row["alleles_over_2n"])
                n = int(row["n"])
            except (ValueError, TypeError, KeyError):
                continue
            if n <= 0 or not (0.0 <= af <= 1.0):
                continue
            twoN = 2 * n
            a = acc[al]
            a["copies"] += int(round(af * twoN))
            a["twoN"] += twoN
            a["pops"] += 1
            a["af_min"] = af if a["af_min"] is None else min(a["af_min"], af)
            a["af_max"] = af if a["af_max"] is None else max(a["af_max"], af)

    out = {}
    for raw, orig in want.items():
        a = acc[raw]
        if not source_ok:
            out[orig] = {"source_unavailable": True,
                         "reason": "AFND mirror TSV not retrievable from CI"}
            continue
        if a["twoN"] == 0:
            out[orig] = {"source_unavailable": True,
                         "reason": f"allele {raw} not found in AFND mirror"}
            continue
        af = a["copies"] / a["twoN"]
        lo, hi = wilson(a["copies"], a["twoN"])
        out[orig] = {
            "allele_frequency": round(af, 4),
            "af_95ci": [lo, hi],
            "carrier_frequency": round(1 - (1 - af) ** 2, 4),
            "n_populations": a["pops"],
            "total_individuals": a["twoN"] // 2,
            "af_range_across_populations": [round(a["af_min"], 4), round(a["af_max"], 4)],
        }
    return out, source_ok


def coverage(afs, bound=None):
    """Combined fraction carrying >=1 presenting allele = 1 - prod (1-af)^2.

    bound: None uses the point af; 'lo'/'hi' uses the Wilson CI edge for an interval."""
    prod = 1.0
    used = []
    for al, info in afs.items():
        if not info or info.get("allele_frequency") is None:
            continue
        if bound == "lo":
            af = (info.get("af_95ci") or [info["allele_frequency"]])[0]
        elif bound == "hi":
            af = (info.get("af_95ci") or [None, info["allele_frequency"]])[1]
        else:
            af = info["allele_frequency"]
        if af is None:
            af = info["allele_frequency"]
        prod *= (1 - af) ** 2
        used.append(al)
    if not used:
        return None, used
    return round(1 - prod, 4), used


def coverage_with_ci(afs):
    pt, used = coverage(afs)
    if not used:
        return None, None, used
    lo, _ = coverage(afs, "lo")
    hi, _ = coverage(afs, "hi")
    return pt, [lo, hi], used


def main():
    with open(BREAKPOINTS) as fh:
        bp = json.load(fh)

    # alleles for the candidate-public junction EWSR1 e7 :: NR4A3 e3 (strong binders)
    e7e3_alleles, all_strong_alleles = set(), set()
    for jn in bp.get("junctions", []):
        is_e7e3 = (jn.get("EWSR1_exon_end") == 7 and jn.get("NR4A3_exon_start") == 3)
        for b in jn.get("binders", []):
            if b.get("class") == "strong":
                all_strong_alleles.add(b["allele"])
                if is_e7e3:
                    e7e3_alleles.add(b["allele"])

    alleles = sorted(all_strong_alleles | e7e3_alleles)
    print(f"  loading AFND frequencies for {len(alleles)} alleles: {alleles}", file=sys.stderr)
    freqs, source_ok = load_afnd_freqs(alleles)
    for al in alleles:
        print(f"    {al}: {freqs[al]}", file=sys.stderr)

    cov_e7e3, ci_e7e3, used_e7e3 = coverage_with_ci(
        {a: freqs[a] for a in sorted(e7e3_alleles)})
    cov_all, ci_all, used_all = coverage_with_ci(freqs)

    have_data = any(v.get("allele_frequency") is not None for v in freqs.values())
    result = {
        "_note": "HLA population coverage of EWSR1::NR4A3 junction neoepitopes. Allele "
                 "frequencies are denominator(2N)-weighted global means pooled over all "
                 "AFND populations, with Wilson 95% CIs (per METHODOLOGY.md). Coverage = "
                 "fraction carrying >=1 presenting allele = 1 - prod(1-af)^2 (independence "
                 "across loci; IEDB population-coverage formula). Global means hide large "
                 "between-population variation (see af_range_across_populations); confirm "
                 "per target population before clinical inference.",
        "_source": AFND_CITATION,
        "_source_url": AFND_TSV_URL,
        "_source_status": ("AFND frequencies retrieved from MIT-licensed mirror"
                           if have_data else
                           "UNAVAILABLE: AFND mirror TSV not retrievable; coverage NOT "
                           "computed rather than fabricated (see per-allele reason)."),
        "_method": "pooled af = sum(copies)/sum(2N) over AFND populations; Wilson 95% CI; "
                   "carrier = 1-(1-af)^2; coverage = 1-prod(1-af)^2; coverage CI "
                   "propagated from per-allele Wilson bounds (approximate).",
        "allele_frequencies": freqs,
        "e7e3_public_epitope_alleles": sorted(e7e3_alleles),
        "coverage_e7e3_public": cov_e7e3,
        "coverage_e7e3_public_95ci": ci_e7e3,
        "coverage_e7e3_alleles_used": used_e7e3,
        "all_strong_binder_alleles": sorted(all_strong_alleles),
        "coverage_any_strong_binder_allele": cov_all,
        "coverage_any_strong_binder_allele_95ci": ci_all,
        "coverage_all_alleles_used": used_all,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "allele_frequencies"}, indent=2))


if __name__ == "__main__":
    main()
