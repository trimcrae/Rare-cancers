#!/usr/bin/env python3
"""
HLA population coverage for the EWSR1::NR4A3 fusion-junction neoepitopes.

Question this answers: if a recurrent breakpoint's junction epitope is presented on
allele(s) X, what fraction of patients carry >=1 presenting allele (i.e. could be
treated with a public fusion-directed vaccine/TCR-T)? That is the difference between an
interesting prediction and a clinically-framed lead. Coverage is reported globally AND
per geographic region, because HLA frequencies vary enormously between populations.

Sources (CI-fetchable, citable, reproducible — no invented frequencies):
  - Allele frequencies: Allele Frequency Net Database (AFND; Gonzalez-Galarza 2020,
    NAR 48:D783) via the MIT-licensed `slowkow/allelefrequencies` mirror, which
    republishes AFND as one tab-delimited file. We use the mirror because AFND itself
    serves only its interactive search form to a non-browser client; the mirror is a
    stable raw file, reproducible by commit. Columns used: `allele` (2-field, e.g.
    A*02:01), `alleles_over_2n` (the population's allele frequency, copies/2N), `n`
    (individuals sampled), `population` (free-text country/ethnicity label).
  - Population -> region: ISO 3166 / UN M49 region + sub-region table
    (`lukes/ISO-3166-Countries-with-Regional-Codes`, raw JSON). AFND population labels
    are resolved to a country by longest leading-country-name match (a curated alias
    table covers AFND's informal spellings and a few territories); the region is then
    the country's UN M49 sub-region. This approximates IEDB's geographic-area breakdown
    with a sourced, reproducible mapping (IEDB's own population->area table is not
    reproducibly CI-fetchable). Unresolved populations are pooled into an "Unassigned"
    bucket and reported — never silently dropped — and are still counted in the global
    figures.

Method (matches METHODOLOGY.md: denominator-weighted pooling + Wilson 95% CI):
  - For each allele, reconstruct copies_i = round(af_i * 2*n_i) and pool: af =
    Sigma(copies_i) / Sigma(2*n_i). A sample-size (2N)-weighted frequency; larger
    studies carry more weight. Computed globally and within each region.
  - 95% CI: Wilson score interval on (Sigma copies, Sigma 2N).
  - Heterogeneity: per-allele af range across populations (global), and the full
    per-region table.
  - Carrier (phenotype) frequency = 1 - (1 - af)^2 (Hardy-Weinberg, >=1 copy).
  - Combined coverage of an allele set = 1 - prod_i (1 - af_i)^2 (independence across
    loci; the standard IEDB population-coverage formula). A coverage interval is
    propagated from the per-allele Wilson bounds (approximate).
  - If an allele is absent from the source, it is recorded as source_unavailable rather
    than guessed.

Output: hla-coverage.json
"""

import csv
import io
import json
import math
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(__file__)
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
CD4_DEMO = os.path.join(HERE, "patient-cd4-demo.json")  # class-II (DRB1) helper epitopes
OUT = os.path.join(HERE, "hla-coverage.json")

AFND_TSV_URL = "https://raw.githubusercontent.com/slowkow/allelefrequencies/main/afnd.tsv"
ISO_JSON_URL = ("https://raw.githubusercontent.com/lukes/"
                "ISO-3166-Countries-with-Regional-Codes/master/all/all.json")
AFND_CITATION = ("Gonzalez-Galarza FF, et al. Allele frequency net database (AFND) 2020 "
                 "update. Nucleic Acids Res. 2020;48:D783-D788. Mirror: "
                 "github.com/slowkow/allelefrequencies (MIT).")
ISO_CITATION = ("Region mapping: ISO 3166 / UN M49 sub-regions via "
                "github.com/lukes/ISO-3166-Countries-with-Regional-Codes.")


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


def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def build_region_resolver(iso_json):
    """Return resolve(pop) -> sub-region name, or None. Sourced ISO/UN M49 + aliases."""
    name2reg = {}
    iso = json.loads(iso_json) if iso_json else []
    for c in iso:
        sub = c.get("sub-region")
        if not sub:
            continue
        name2reg[_norm(c["name"])] = sub
        base = c["name"].split(",")[0].split("(")[0]  # "Iran, Islamic Republic of" -> Iran
        name2reg.setdefault(_norm(base), sub)
    # AFND informal names / territories not in ISO -> UN M49 sub-region (sourced by hand).
    aliases = {
        "usa": "Northern America", "united states": "Northern America",
        "uk": "Northern Europe", "england": "Northern Europe", "scotland": "Northern Europe",
        "wales": "Northern Europe", "ireland northern": "Northern Europe",
        "russia": "Eastern Europe", "turkey": "Western Asia", "turkiye": "Western Asia",
        "czech republic": "Eastern Europe", "vietnam": "South-eastern Asia",
        "laos": "South-eastern Asia", "syria": "Western Asia", "burma": "South-eastern Asia",
        "ivory coast": "Sub-Saharan Africa", "swaziland": "Sub-Saharan Africa",
        "cape verde": "Sub-Saharan Africa", "brunei": "South-eastern Asia",
        "macedonia": "Southern Europe", "south korea": "Eastern Asia",
        "taiwan": "Eastern Asia",
        "azores": "Southern Europe", "madeira": "Southern Europe", "kosovo": "Southern Europe",
        "gaza": "Western Asia", "sao tome": "Sub-Saharan Africa",
        "ecuadorean": "Latin America and the Caribbean", "borneo": "South-eastern Asia",
        "western samoa": "Polynesia",
    }
    name2reg.update(aliases)
    names_sorted = sorted(name2reg, key=len, reverse=True)

    def resolve(pop):
        p = _norm(pop)
        for nm in names_sorted:
            if p == nm or p.startswith(nm + " "):
                return name2reg[nm]
        return None

    return resolve


def load_afnd(alleles, resolve):
    """Pool AFND frequencies globally and per region.

    Returns (global_info, region_acc, source_ok, unassigned).
    global_info[allele] = info dict (af/CI/...) or source_unavailable.
    region_acc[region][allele] = {"copies","twoN"} accumulator.
    """
    want = {a.replace("HLA-", ""): a for a in alleles}  # AFND alleles have no 'HLA-' prefix
    gacc = {a: {"copies": 0, "twoN": 0, "pops": 0, "af_min": None, "af_max": None}
            for a in want}
    racc = {}                       # region -> allele(raw) -> {copies,twoN,pops}
    unassigned = {"populations": set(), "individuals": 0}

    html = fetch(AFND_TSV_URL)
    source_ok = bool(html) and "alleles_over_2n" in html
    if source_ok:
        for row in csv.DictReader(io.StringIO(html), delimiter="\t"):
            if row.get("group") != "hla":
                continue
            raw = row.get("allele")
            if raw not in want:
                continue
            try:
                af = float(row["alleles_over_2n"])
                n = int(row["n"])
            except (ValueError, TypeError, KeyError):
                continue
            if n <= 0 or not (0.0 <= af <= 1.0):
                continue
            twoN = 2 * n
            copies = int(round(af * twoN))
            g = gacc[raw]
            g["copies"] += copies
            g["twoN"] += twoN
            g["pops"] += 1
            g["af_min"] = af if g["af_min"] is None else min(g["af_min"], af)
            g["af_max"] = af if g["af_max"] is None else max(g["af_max"], af)
            region = resolve(row.get("population", "")) or "Unassigned"
            if region == "Unassigned":
                unassigned["populations"].add(row.get("population", ""))
                unassigned["individuals"] += n
            r = racc.setdefault(region, {}).setdefault(raw, {"copies": 0, "twoN": 0, "pops": 0})
            r["copies"] += copies
            r["twoN"] += twoN
            r["pops"] += 1

    ginfo = {}
    for raw, orig in want.items():
        g = gacc[raw]
        if not source_ok:
            ginfo[orig] = {"source_unavailable": True,
                           "reason": "AFND mirror TSV not retrievable from CI"}
        elif g["twoN"] == 0:
            ginfo[orig] = {"source_unavailable": True,
                           "reason": f"allele {raw} not found in AFND mirror"}
        else:
            af = g["copies"] / g["twoN"]
            lo, hi = wilson(g["copies"], g["twoN"])
            ginfo[orig] = {
                "allele_frequency": round(af, 4),
                "af_95ci": [lo, hi],
                "carrier_frequency": round(1 - (1 - af) ** 2, 4),
                "n_populations": g["pops"],
                "total_individuals": g["twoN"] // 2,
                "af_range_across_populations": [round(g["af_min"], 4), round(g["af_max"], 4)],
            }
    unassigned["populations"] = len(unassigned["populations"])
    return ginfo, racc, source_ok, unassigned


def _af_info_from_acc(acc):
    """acc {copies,twoN} -> small info dict with af + Wilson CI (or None)."""
    if not acc or acc["twoN"] == 0:
        return None
    af = acc["copies"] / acc["twoN"]
    lo, hi = wilson(acc["copies"], acc["twoN"])
    return {"allele_frequency": round(af, 4), "af_95ci": [lo, hi]}


def coverage(afs, bound=None):
    """Combined fraction carrying >=1 presenting allele = 1 - prod (1-af)^2.

    bound: None -> point af; 'lo'/'hi' -> per-allele Wilson edge (interval)."""
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


def load_class_ii_alleles(path):
    """DRB1 alleles presenting a *strong* CD4 helper binder in the class-II demo."""
    try:
        with open(path) as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return [], None
    strong = sorted({r["allele"] for r in d.get("all_predictions", [])
                     if r.get("call") == "strong"})
    return strong, d.get("patient_class2_hla")


def regional_table(racc, e7e3_raw, all_raw, cd4_raw):
    """Per-region coverage for the e7e3, all-strong (class I) and CD4 (class II) sets."""
    out = {}
    for region, alleles in racc.items():
        e7 = {a: _af_info_from_acc(alleles.get(a)) for a in e7e3_raw}
        allset = {a: _af_info_from_acc(alleles.get(a)) for a in all_raw}
        cd4 = {a: _af_info_from_acc(alleles.get(a)) for a in cd4_raw}
        cov_e7, ci_e7, used_e7 = coverage_with_ci(e7)
        cov_all, ci_all, used_all = coverage_with_ci(allset)
        cov_cd4, ci_cd4, used_cd4 = coverage_with_ci(cd4)
        total_indiv = max((alleles[a]["twoN"] // 2) for a in alleles)  # largest allele survey
        n_pops = max((alleles[a]["pops"]) for a in alleles)
        out[region] = {
            "coverage_e7e3_public": cov_e7,
            "coverage_e7e3_public_95ci": ci_e7,
            "coverage_e7e3_alleles_used": used_e7,
            "coverage_any_strong_binder_allele": cov_all,
            "coverage_any_strong_binder_allele_95ci": ci_all,
            "coverage_all_alleles_used": used_all,
            "coverage_cd4_classii": cov_cd4,
            "coverage_cd4_classii_95ci": ci_cd4,
            "coverage_cd4_classii_alleles_used": used_cd4,
            "max_n_populations": n_pops,
            "max_total_individuals": total_indiv,
            "allele_frequencies": {a: _af_info_from_acc(alleles.get(a)) for a in all_raw},
        }
    # sort by descending all-strong coverage (None last) for readability
    return dict(sorted(out.items(),
                       key=lambda kv: (kv[1]["coverage_any_strong_binder_allele"] is None,
                                       -(kv[1]["coverage_any_strong_binder_allele"] or 0))))


def main():
    with open(BREAKPOINTS) as fh:
        bp = json.load(fh)

    e7e3_alleles, all_strong_alleles = set(), set()
    for jn in bp.get("junctions", []):
        is_e7e3 = (jn.get("EWSR1_exon_end") == 7 and jn.get("NR4A3_exon_start") == 3)
        for b in jn.get("binders", []):
            if b.get("class") == "strong":
                all_strong_alleles.add(b["allele"])
                if is_e7e3:
                    e7e3_alleles.add(b["allele"])

    # class II: DRB1 alleles presenting a strong CD4 helper binder (limited demo panel)
    cd4_alleles_list, cd4_panel = load_class_ii_alleles(CD4_DEMO)
    cd4_alleles = set(cd4_alleles_list)

    alleles = sorted(all_strong_alleles | e7e3_alleles | cd4_alleles)
    print(f"  loading AFND frequencies for {len(alleles)} alleles: {alleles}", file=sys.stderr)
    resolve = build_region_resolver(fetch(ISO_JSON_URL))
    freqs, racc, source_ok, unassigned = load_afnd(alleles, resolve)
    for al in alleles:
        print(f"    {al}: {freqs[al]}", file=sys.stderr)

    cov_e7e3, ci_e7e3, used_e7e3 = coverage_with_ci(
        {a: freqs[a] for a in sorted(e7e3_alleles)})
    cov_all, ci_all, used_all = coverage_with_ci(
        {a: freqs[a] for a in sorted(all_strong_alleles)})
    cov_cd4, ci_cd4, used_cd4 = coverage_with_ci(
        {a: freqs[a] for a in sorted(cd4_alleles)}) if cd4_alleles else (None, None, [])

    # Both arms: fraction with >=1 class-I presenting allele AND >=1 class-II helper allele
    # (HLA-A/B and DRB1 are independent loci). A durable vaccine wants both CD8 and CD4.
    cov_both = (round(cov_all * cov_cd4, 4)
                if (cov_all is not None and cov_cd4 is not None) else None)

    e7e3_raw = sorted(a.replace("HLA-", "") for a in e7e3_alleles)
    all_raw = sorted(a.replace("HLA-", "") for a in all_strong_alleles)
    cd4_raw = sorted(a.replace("HLA-", "") for a in cd4_alleles)
    regions = regional_table(racc, e7e3_raw, all_raw, cd4_raw) if source_ok else {}

    have_data = any(v.get("allele_frequency") is not None for v in freqs.values())
    result = {
        "_note": "HLA population coverage of EWSR1::NR4A3 junction neoepitopes. Allele "
                 "frequencies are denominator(2N)-weighted means pooled over AFND "
                 "populations, with Wilson 95% CIs (per METHODOLOGY.md). Coverage = "
                 "fraction carrying >=1 presenting allele = 1 - prod(1-af)^2 (independence "
                 "across loci; IEDB population-coverage formula). Reported globally AND per "
                 "UN M49 sub-region, because HLA frequencies vary enormously between "
                 "populations (see `regions` and af_range_across_populations).",
        "_sources": [AFND_CITATION, ISO_CITATION],
        "_source_urls": {"allele_frequencies": AFND_TSV_URL, "region_mapping": ISO_JSON_URL},
        "_source_status": ("AFND frequencies retrieved from MIT-licensed mirror"
                           if have_data else
                           "UNAVAILABLE: AFND mirror TSV not retrievable; coverage NOT "
                           "computed rather than fabricated (see per-allele reason)."),
        "_method": "pooled af = sum(copies)/sum(2N); Wilson 95% CI; carrier = 1-(1-af)^2; "
                   "coverage = 1-prod(1-af)^2; coverage CI propagated from per-allele "
                   "Wilson bounds (approximate). Regional split: AFND population label -> "
                   "country (longest-name match) -> UN M49 sub-region.",
        "_region_mapping": {
            "scheme": "UN M49 sub-region (ISO 3166), sourced; approximates IEDB's "
                      "geographic-area breakdown (IEDB's own area table is not reproducibly "
                      "CI-fetchable). Unassigned populations are pooled separately and still "
                      "counted in the GLOBAL figures.",
            "unassigned_populations": unassigned["populations"],
            "unassigned_individuals": unassigned["individuals"],
        },
        "global": {
            "allele_frequencies": freqs,
            "e7e3_public_epitope_alleles": sorted(e7e3_alleles),
            "coverage_e7e3_public": cov_e7e3,
            "coverage_e7e3_public_95ci": ci_e7e3,
            "coverage_e7e3_alleles_used": used_e7e3,
            "all_strong_binder_alleles": sorted(all_strong_alleles),
            "coverage_any_strong_binder_allele": cov_all,
            "coverage_any_strong_binder_allele_95ci": ci_all,
            "coverage_all_alleles_used": used_all,
            "class_ii_cd4_helper_alleles": sorted(cd4_alleles),
            "coverage_cd4_classii": cov_cd4,
            "coverage_cd4_classii_95ci": ci_cd4,
            "coverage_cd4_classii_alleles_used": used_cd4,
            "coverage_cd8_and_cd4_combined": cov_both,
        },
        "_class_ii_note": (
            "Class-II (CD4 helper) coverage is over DRB1 alleles presenting a STRONG binder "
            "in patient-cd4-demo.json (MHCnuggets, EWSR1 e7::e3 junction). That screen tested "
            "only a 3-allele DR panel (" + ", ".join(cd4_panel or []) + "), so this coverage "
            "is a FLOOR over a tested panel, not a complete DR scan: untested DR alleles may "
            "also present the helper peptides, which would only raise coverage. "
            "coverage_cd8_and_cd4_combined = P(>=1 class-I allele) x P(>=1 class-II allele), "
            "treating HLA-A/B and DRB1 as independent loci."),
        "regions": regions,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    print("wrote", OUT, file=sys.stderr)
    summary = {"global_e7e3_classI": cov_e7e3, "global_any_strong_classI": cov_all,
               "global_cd4_classII": cov_cd4, "global_cd8_and_cd4": cov_both,
               "n_regions": len(regions), "unassigned_pops": unassigned["populations"]}
    print(json.dumps(summary, indent=2))
    for reg, r in regions.items():
        print(f"  {reg:28s} e7e3={r['coverage_e7e3_public']}  "
              f"anyI={r['coverage_any_strong_binder_allele']}  "
              f"cd4={r['coverage_cd4_classii']}  (<=N={r['max_total_individuals']})",
              file=sys.stderr)


if __name__ == "__main__":
    main()
