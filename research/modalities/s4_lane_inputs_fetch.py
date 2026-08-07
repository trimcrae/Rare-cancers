#!/usr/bin/env python3
"""
FETCH-ONLY. The three network reads that section 4 of `emc-unexplored-treatment-lanes.md` needs and the
dev sandbox cannot make. $0, CPU, pure stdlib, no pip.

WHY A FETCH-ONLY SCRIPT AND NOT THE ANALYSIS ITSELF. The egress proxy 403s NCBI/GEO and RCSB on CONNECT
(CLAUDE.md §6), so the *reads* have to happen on a GitHub-hosted runner. Nothing else does. Splitting the
fetch from the analysis means the analysis is exercised in the sandbox against real bytes, under the repo's
own test discipline, instead of being written blind and debugged through the Actions queue — and it means a
re-run of the analysis costs nothing and cannot re-hit GEO.

⛔ THIS SCRIPT MAKES NO SCIENTIFIC CLAIM AND DERIVES NOTHING. It writes bytes and a manifest of what it got,
including the HTTP status of every request, so that "the collector could not read this" and "this is absent"
stay distinguishable (CLAUDE.md §4).

WHAT IT FETCHES
  1. GEO GSE11185 — "Differences between NOR1 and EWS/NOR1". The series record, EVERY sample record at
     `view=full` (which carries the per-sample value table), and the platform's ID->annotation table.
     The series is in this repository's own GEO census (`emc-atr-vulnerability.json`) and has never been read.
  2. RCSB 7WNH — Nurr1 (NR4A2) bound to the NBRE response element, 3.1 A. Named in
     `apo-pose-site-in-regime.json` as an apo reference; its coordinates have never been on disk.
  3. RCSB 1OVL — the Nurr1 LBD entry that PMC12095788 (Lopez-Garcia 2025, Commun Chem 8:159) states it
     docked vidofludimus into ("Chain E of the Nurr1 LBD (pdb id: 1ovl)"), with a stated grid centre. It is
     fetched so the published allosteric site can be located in a real frame rather than only as a list of
     residue numbers.

Usage:  python s4_lane_inputs_fetch.py            # fetch everything into _s4_lane_inputs/
        python s4_lane_inputs_fetch.py --plan     # offline: print exactly what would be requested
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_s4_lane_inputs")

GEO_ACC = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
RCSB = "https://files.rcsb.org/download/%s.pdb"
SERIES = "GSE11185"
PDB_IDS = ("7WNH", "1OVL")

UA = "Mozilla/5.0 (X11; Linux x86_64) rare-cancers-research/1.0 (+https://github.com/trimcrae/Rare-cancers)"
MAX_BYTES = 80 * 1024 * 1024          # a platform table is the only thing that can be large; refuse, never truncate
TIMEOUT = 120


def get(url, tries=3):
    """Return (status, bytes, error). NEVER raises: a failed read is a recorded row, not a dead run."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                buf = r.read(MAX_BYTES + 1)
                if len(buf) > MAX_BYTES:
                    return r.status, b"", "response exceeded %d bytes — REFUSED, not truncated" % MAX_BYTES
                return r.status, buf, None
        except urllib.error.HTTPError as e:
            last = "HTTPError %s" % e.code
            if e.code in (429, 500, 502, 503):
                time.sleep(3 * (i + 1))
                continue
            return e.code, b"", last
        except Exception as e:                                   # noqa: BLE001
            last = repr(e)
            time.sleep(3 * (i + 1))
    return None, b"", last


def geo_url(acc, view="full", targ="self"):
    return "%s?acc=%s&targ=%s&form=text&view=%s" % (GEO_ACC, acc, targ, view)


def write(name, data, manifest, url, status, error, gz=False):
    rec = {"name": name, "url": url, "http": status, "error": error, "bytes": len(data)}
    if data:
        path = os.path.join(OUT, name + (".gz" if gz else ""))
        if gz:
            with gzip.open(path, "wb") as fh:
                fh.write(data)
        else:
            with open(path, "wb") as fh:
                fh.write(data)
        rec["path"] = os.path.relpath(path, HERE)
        rec["stored_bytes"] = os.path.getsize(path)
    manifest.append(rec)
    print("%-28s http=%-5s bytes=%-9d %s" % (name, status, len(data), error or ""), flush=True)
    return rec


def parse_series(text):
    """The sample accessions and the platform accession, read from the SOFT record — never guessed."""
    gsms, gpls, meta = [], [], {}
    for line in text.splitlines():
        if not line.startswith("!"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip().lstrip("!"), v.strip()
        if k == "Series_sample_id":
            gsms.append(v)
        elif k == "Series_platform_id":
            gpls.append(v)
        meta.setdefault(k, []).append(v)
    return gsms, gpls, meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--series", default=SERIES)
    args = ap.parse_args(argv)

    if args.plan:
        print(geo_url(args.series, view="brief"))
        print(geo_url(args.series, view="full") + "   (per-sample records discovered from the brief record)")
        for p in PDB_IDS:
            print(RCSB % p)
        return 0

    os.makedirs(OUT, exist_ok=True)
    manifest = []

    # ---- 1. the series record ------------------------------------------------------------------------
    u = geo_url(args.series, view="brief")
    st, data, err = get(u)
    write("%s_series.soft.txt" % args.series, data, manifest, u, st, err)
    gsms, gpls, _meta = parse_series(data.decode("utf-8", "replace")) if data else ([], [], {})
    print("  discovered %d sample(s), %d platform(s): %s | %s" % (len(gsms), len(gpls), gsms, gpls), flush=True)

    # ---- 2. every sample record, at view=full (carries the per-sample value table) --------------------
    for g in gsms:
        u = geo_url(g, view="full")
        st, data, err = get(u)
        write("%s.soft.txt" % g, data, manifest, u, st, err)
        time.sleep(1.0)                                          # NCBI courtesy; 4 samples, not a crawl

    # ---- 3. the platform annotation table -------------------------------------------------------------
    for p in gpls:
        u = geo_url(p, view="full")
        st, data, err = get(u)
        write("%s.annot.txt" % p, data, manifest, u, st, err, gz=True)
        time.sleep(1.0)

    # ---- 4. the two PDB entries -----------------------------------------------------------------------
    for pid in PDB_IDS:
        u = RCSB % pid
        st, data, err = get(u)
        write("%s.pdb" % pid, data, manifest, u, st, err, gz=True)

    with open(os.path.join(OUT, "_manifest.json"), "w") as fh:
        json.dump({
            "_what": "raw network reads for section 4 of emc-unexplored-treatment-lanes.md; NO derivation",
            "_fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "series": args.series,
            "samples_discovered": gsms,
            "platforms_discovered": gpls,
            "reads": manifest,
            "_reading_discipline": ("a row with http != 200 or bytes == 0 is a READ FAILURE, not evidence "
                                    "that the record is empty (CLAUDE.md §4)"),
        }, fh, indent=1)
        fh.write("\n")
    bad = [r for r in manifest if r.get("http") != 200 or not r.get("bytes")]
    print("\n%d read(s), %d failed" % (len(manifest), len(bad)), flush=True)
    return 1 if not manifest or len(bad) == len(manifest) else 0


if __name__ == "__main__":
    sys.exit(main())
