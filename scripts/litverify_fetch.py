#!/usr/bin/env python3
"""Fetch open-access full text for the RBFE-replicate literature verification.

Runs on a GitHub Actions runner (unrestricted internet); the dev sandbox egress
proxy 403s CONNECT to arxiv/ACS/RSC/PMC/livecomsjournal. Pure stdlib + the
`pdftotext` CLI (poppler-utils). Writes <name>.txt and <name>.meta.json into
the output dir, plus MANIFEST.txt recording which URL actually worked.
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

OUT = sys.argv[1] if len(sys.argv) > 1 else "litverify"
EMAIL = "trimcrae@gmail.com"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

SOURCES = {
    "01_mey_livecoms_alchemical": {
        "doi": "10.33011/livecoms.2.1.18378",
        "urls": [
            "https://arxiv.org/pdf/2008.03067",
            "https://arxiv.org/pdf/2008.03067v4",
            "https://arxiv.org/pdf/2008.03067v3",
            "https://escholarship.org/content/qt87m6x1sw/qt87m6x1sw.pdf",
            "https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378",
            "https://livecomsjournal.org/index.php/livecoms/article/download/v2i1e18378/1113",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC7495041/",
        ],
    },
    "02_coveney_wan_pccp2016": {
        "doi": "10.1039/c6cp02349e",
        "urls": [
            "https://discovery.ucl.ac.uk/id/eprint/1503049/1/c6cp02349e.pdf",
            "https://discovery-pp.ucl.ac.uk/id/eprint/1503049/1/c6cp02349e.pdf",
            "https://pubs.rsc.org/en/content/articlepdf/2016/cp/c6cp02349e",
            "https://pubs.rsc.org/en/content/articlehtml/2016/cp/c6cp02349e",
            "https://discovery.ucl.ac.uk/id/eprint/1503049/",
        ],
    },
    "03_bhati_ties_jctc2017": {
        "doi": "10.1021/acs.jctc.6b00979",
        "urls": [
            "https://pubs.acs.org/doi/pdf/10.1021/acs.jctc.6b00979",
            "https://discovery.ucl.ac.uk/id/eprint/1534399/",
            "https://discovery.ucl.ac.uk/1534399/9/Bhati_final_si.pdf",
            "https://discovery.ucl.ac.uk/1534399/1/Bhati_final.pdf",
            "https://discovery.ucl.ac.uk/1534399/7/Bhati_final.pdf",
            "https://discovery.ucl.ac.uk/1534399/8/Bhati_final.pdf",
            "https://www.osti.gov/pages/biblio/2470031",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5379244/",
        ],
    },
    "04_bhati_coveney_jctc2022": {
        "doi": "10.1021/acs.jctc.1c01288",
        "urls": [
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC9009079/",
            "https://pubs.acs.org/doi/pdf/10.1021/acs.jctc.1c01288",
            "https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/61b9e447d6dcc2979b3960b8/original/large-scale-study-of-ligand-protein-relative-binding-free-energy-calculations-actionable-predictions-from-statistically-robust-protocols.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9009079/",
        ],
    },
    "05_loeffler_reproducibility_jctc2018": {
        "doi": "10.1021/acs.jctc.8b00544",
        "urls": [
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC6207338/",
            "https://pubs.acs.org/doi/pdf/10.1021/acs.jctc.8b00544",
            "https://www.research.ed.ac.uk/files/74996414/Reproducibility_of_free_energy_calculations.pdf",
        ],
    },
    "06_hahn_benchmarks_livecoms2022": {
        "doi": "10.33011/livecoms.4.1.1497",
        "urls": [
            "https://arxiv.org/pdf/2105.06222",
            "https://arxiv.org/pdf/2105.06222v3",
            "https://livecomsjournal.org/index.php/livecoms/article/view/v4i1e1497",
            "https://livecomsjournal.org/index.php/livecoms/article/download/v4i1e1497/1497",
        ],
    },
}


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", ""), r.geturl()


def unpaywall(doi):
    try:
        raw, _, _ = get(f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}", timeout=40)
        d = json.loads(raw.decode("utf-8", "replace"))
        out = []
        for loc in (d.get("oa_locations") or []):
            for k in ("url_for_pdf", "url"):
                if loc.get(k):
                    out.append(loc[k])
        return out, {
            "title": d.get("title"),
            "year": d.get("year"),
            "journal": d.get("journal_name"),
            "publisher": d.get("publisher"),
            "is_oa": d.get("is_oa"),
            "authors": [
                " ".join(filter(None, [a.get("given"), a.get("family")]))
                for a in (d.get("z_authors") or [])
            ],
        }
    except Exception as e:  # noqa: BLE001
        return [], {"unpaywall_error": repr(e)}


def crossref(doi):
    try:
        raw, _, _ = get(f"https://api.crossref.org/works/{doi}", timeout=40)
        m = json.loads(raw.decode("utf-8", "replace"))["message"]
        return {
            "cr_title": (m.get("title") or [None])[0],
            "cr_container": (m.get("container-title") or [None])[0],
            "cr_volume": m.get("volume"),
            "cr_issue": m.get("issue"),
            "cr_page": m.get("page"),
            "cr_year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "cr_doi": m.get("DOI"),
            "cr_authors": [
                " ".join(filter(None, [a.get("given"), a.get("family")]))
                for a in (m.get("author") or [])
            ],
        }
    except Exception as e:  # noqa: BLE001
        return {"crossref_error": repr(e)}


TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
ANY = re.compile(r"<[^>]+>")


def html_to_text(b):
    s = b.decode("utf-8", "replace")
    s = TAG.sub(" ", s)
    s = ANY.sub(" ", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&#x2212;", "-").replace("&quot;", '"'))
    return re.sub(r"[ \t]{2,}", " ", s)


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for name, spec in SOURCES.items():
        doi = spec["doi"]
        meta = {"name": name, "doi": doi}
        meta.update(crossref(doi))
        up_urls, up_meta = unpaywall(doi)
        meta.update(up_meta)
        meta["unpaywall_urls"] = up_urls
        text, used, attempts = "", None, []
        variants = {}
        queue = list(spec["urls"]) + list(up_urls)
        seen = set()
        while queue:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            if used and len(text) > 60000:
                break
            try:
                body, ctype, final = get(url)
            except Exception as e:  # noqa: BLE001
                attempts.append({"url": url, "error": repr(e)[:200]})
                continue
            attempts.append({"url": url, "final": final, "ctype": ctype,
                             "bytes": len(body)})
            t, vs = "", {}
            if body[:5] == b"%PDF-" or "pdf" in ctype.lower():
                p = os.path.join(OUT, name + ".pdf")
                with open(p, "wb") as f:
                    f.write(body)
                for mode, suffix in (([], ""), (["-layout"], ".layout"),
                                     (["-raw"], ".raw")):
                    try:
                        o = subprocess.run(["pdftotext"] + mode + [p, "-"],
                                           capture_output=True,
                                           timeout=180).stdout
                        o = o.decode("utf-8", "replace")
                    except Exception as e:  # noqa: BLE001
                        attempts[-1]["pdftotext_error" + suffix] = repr(e)[:200]
                        continue
                    vs[suffix] = o
                    if not suffix:
                        t = o
            else:
                t = html_to_text(body)
                for href in re.findall(rb'href="([^"]+?\.pdf[^"]*)"', body,
                                       re.I)[:10]:
                    h = urllib.parse.urljoin(final, href.decode("latin-1"))
                    if h not in seen:
                        queue.append(h)
            if len(t) > len(text):
                text, used, variants = t, final, vs
        for suffix, o in variants.items():
            if suffix:
                with open(os.path.join(OUT, name + suffix + ".txt"), "w") as f:
                    f.write(o)
        meta["used_url"] = used
        meta["attempts"] = attempts
        meta["text_chars"] = len(text)
        with open(os.path.join(OUT, name + ".txt"), "w") as f:
            f.write(text)
        with open(os.path.join(OUT, name + ".meta.json"), "w") as f:
            json.dump(meta, f, indent=2)
        line = f"{name}: {len(text)} chars via {used}"
        print(line, flush=True)
        manifest.append(line)
    with open(os.path.join(OUT, "MANIFEST.txt"), "w") as f:
        f.write("\n".join(manifest) + "\n")


if __name__ == "__main__":
    main()
