#!/usr/bin/env python3
"""
HLA population coverage for the EWSR1::NR4A3 fusion-junction neoepitopes.

Question this answers: if a recurrent breakpoint's junction epitope is presented on
allele(s) X, what fraction of patients carry >=1 presenting allele (i.e. could be
treated with a public fusion-directed vaccine/TCR-T)? That is the difference between an
interesting prediction and a clinically-framed lead.

Method (reproducible, sourced — no invented frequencies):
  - Read the breakpoint-resolved binders (`fusion-breakpoint-neoantigens.json`).
  - For (a) the candidate-public junction EWSR1 e7::NR4A3 e3 and (b) all strong binders,
    collect the presenting HLA alleles.
  - Fetch each allele's frequencies across populations from the Allele Frequency Net
    Database (AFND) [Gonzalez-Galarza 2020, NAR], parse the per-population allele
    frequency + sample size, and compute a sample-size-weighted global allele frequency.
  - Phenotype frequency (carriers) = 1 - (1 - af)^2 (Hardy-Weinberg, >=1 copy).
  - Combined coverage of an allele set = 1 - prod_i (1 - af_i)^2 (independence; the
    standard IEDB population-coverage formula).
  - If AFND parsing yields nothing for an allele, it is recorded as source_unavailable
    rather than guessed.

Output: hla-coverage.json
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(__file__)
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
OUT = os.path.join(HERE, "hla-coverage.json")

AFND_BASE = "https://www.allelefrequencies.net/hla6006a.asp"


def fetch(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120 Safari/537.36",
                "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return ""


def afnd_allele_freq(allele):
    """Sample-size-weighted global allele frequency from AFND. Returns dict or None."""
    params = {"hla_locus_type": "Classical", "hla_allele1": allele,
              "hla_order": "order_1", "standard": "a"}
    url = AFND_BASE + "?" + urllib.parse.urlencode(params)
    html = fetch(url)
    # diagnostics so a failed scrape is debuggable from the published JSON, not silent
    decimals = re.findall(r"\b0?\.\d{3,6}\b", html)
    ctx = ""
    m = re.search(r"0?\.\d{3,6}", html)
    if m:
        ctx = re.sub(r"\s+", " ", html[max(0, m.start()-160):m.start()+40])
    diag = {"html_len": len(html),
            "allele_in_html": allele in html,
            "n_tr": len(re.findall(r"<tr", html, flags=re.I)),
            "n_decimals_0to1": len(decimals),
            "has_datatable": ("aaData" in html or "DataTable" in html or "fnAddData" in html),
            "first_decimal_context": ctx}
    if not html:
        return {"_diag": diag}
    # AFND result rows carry the allele frequency (a small decimal) and a sample size.
    # Grab table rows and, within each, the first 0<x<1 decimal (allele freq) and a
    # plausible integer sample size (>=20). Weighted mean over populations.
    rows = re.split(r"<tr[ >]", html, flags=re.I)
    pairs = []
    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S)
        if len(cells) < 4:
            continue
        texts = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip() for c in cells]
        freq = None
        size = None
        for t in texts:
            tt = t.replace(",", "")
            m = re.fullmatch(r"0?\.\d{3,6}", tt)
            if m and freq is None:
                v = float(tt)
                if 0 < v < 1:
                    freq = v
            if re.fullmatch(r"\d{2,7}", tt):
                iv = int(tt)
                if iv >= 20:
                    size = iv if (size is None or iv > size) else size
        if freq is not None and size is not None:
            pairs.append((freq, size))
    diag["n_pairs_parsed"] = len(pairs)
    # snapshot the first parsed table region to debug structure if parsing under-counts
    if len(pairs) < 3:
        mt = re.search(r"<table.*?</table>", html, flags=re.I | re.S)
        diag["table_snippet"] = re.sub(r"\s+", " ", (mt.group(0)[:600] if mt else html[:600]))
    if not pairs:
        return {"_diag": diag}
    num = sum(f * n for f, n in pairs)
    den = sum(n for _, n in pairs)
    af = num / den if den else None
    if af is None:
        return {"_diag": diag}
    return {"allele_frequency": round(af, 4), "n_population_samples": len(pairs),
            "total_individuals": den, "_diag": diag}


def coverage(afs):
    """Combined fraction carrying >=1 presenting allele = 1 - prod (1-af)^2."""
    prod = 1.0
    used = []
    for al, info in afs.items():
        if info and info.get("allele_frequency") is not None:
            af = info["allele_frequency"]
            prod *= (1 - af) ** 2
            used.append(al)
    if not used:
        return None, used
    return round(1 - prod, 4), used


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
    print(f"  fetching AFND frequencies for {len(alleles)} alleles: {alleles}", file=sys.stderr)
    freqs = {}
    for al in alleles:
        info = afnd_allele_freq(al)
        freqs[al] = info
        print(f"    {al}: {info}", file=sys.stderr)

    cov_e7e3, used_e7e3 = coverage({a: freqs[a] for a in sorted(e7e3_alleles)})
    cov_all, used_all = coverage(freqs)

    result = {
        "_note": "HLA population coverage of EWSR1::NR4A3 junction neoepitopes. Allele "
                 "frequencies are sample-size-weighted global means scraped from the Allele "
                 "Frequency Net Database (AFND; Gonzalez-Galarza 2020). Coverage = fraction "
                 "of individuals carrying >=1 presenting allele = 1 - prod(1-af)^2. Global "
                 "means hide large between-population variation; confirm per target population.",
        "allele_frequencies": freqs,
        "e7e3_public_epitope_alleles": sorted(e7e3_alleles),
        "coverage_e7e3_public": cov_e7e3,
        "coverage_e7e3_alleles_used": used_e7e3,
        "all_strong_binder_alleles": sorted(all_strong_alleles),
        "coverage_any_strong_binder_allele": cov_all,
        "coverage_all_alleles_used": used_all,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "allele_frequencies"}, indent=2))


if __name__ == "__main__":
    main()
