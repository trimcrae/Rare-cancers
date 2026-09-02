#!/usr/bin/env python3
"""Batch Europe PMC + ClinicalTrials.gov citation probe, run from a GitHub-hosted runner.

The dev sandbox's egress proxy blocks every literature host (europepmc, ncbi, doi.org,
crossref, openalex, clinicaltrials.gov, and every publisher), so verifying a PMID/DOI/NCT
has to happen out here -- CLAUDE.md section 6. This script COMMITS NOTHING: it prints
structured citation records to the job log, which a session reads back with
mcp__github__get_job_logs.

Queries live in scripts/lit_probe_queries.json so the script itself stays generic.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
UA = "Mozilla/5.0 (compatible; rare-cancers-lit-probe/1.0)"


def get_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001 - a probe reports failures, it does not raise
            if i == tries - 1:
                print(f"    !! FETCH FAILED after {tries} tries: {exc}")
                return None
            time.sleep(2 + 3 * i)
    return None


def epmc(query, n=10, abstracts=5):
    url = (f"{EPMC}?query={urllib.parse.quote(query)}&format=json"
           f"&pageSize={n}&resultType=core&sort=CITED%20desc")
    data = get_json(url)
    if not data:
        return
    hits = data.get("resultList", {}).get("result", [])
    print(f"  hitCount={data.get('hitCount','?')}  showing={len(hits)}")
    for i, r in enumerate(hits):
        oa = "OA" if r.get("isOpenAccess") == "Y" else "  "
        print(f"  [{i+1}] {r.get('pubYear','----')} {oa} PMID:{r.get('pmid') or '-'} "
              f"PMCID:{r.get('pmcid') or '-'} DOI:{r.get('doi') or '-'}")
        print(f"      {(r.get('title') or '').strip()}")
        print(f"      {r.get('journalTitle') or ''} | {(r.get('authorString') or '')[:140]}")
        if i < abstracts and r.get("abstractText"):
            ab = " ".join(r["abstractText"].split())
            print(f"      ABSTRACT: {ab[:1700]}")
    print()


def ctgov(term, n=12):
    url = (f"{CTGOV}?query.term={urllib.parse.quote(term)}&pageSize={n}")
    data = get_json(url)
    if not data:
        return
    studies = data.get("studies", [])
    print(f"  studies={len(studies)}")
    for s in studies:
        p = s.get("protocolSection", {})
        idm = p.get("identificationModule", {})
        st = p.get("statusModule", {})
        des = p.get("designModule", {})
        cond = p.get("conditionsModule", {}).get("conditions", [])
        arms = p.get("armsInterventionsModule", {}).get("interventions", [])
        spon = p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "")
        print(f"  {idm.get('nctId','')} [{st.get('overallStatus','')}] "
              f"{'/'.join(des.get('phases', []) or ['-'])} | {spon}")
        print(f"      {idm.get('briefTitle','')}")
        print(f"      cond={'; '.join(cond[:5])}")
        print(f"      intv={'; '.join(i.get('name','') for i in arms[:5])} "
              f"| start={st.get('startDateStruct',{}).get('date','')}")
    print()


def main():
    spec_path = os.environ.get("LIT_PROBE_SPEC", "scripts/lit_probe_queries.json")
    with open(spec_path) as fh:
        spec = json.load(fh)
    for block in spec.get("europepmc", []):
        print("=" * 100)
        print(f"EPMC :: {block['label']}")
        print(f"QUERY: {block['q']}")
        epmc(block["q"], n=block.get("n", 10), abstracts=block.get("abstracts", 5))
        sys.stdout.flush()
    for block in spec.get("clinicaltrials", []):
        print("=" * 100)
        print(f"CTGOV :: {block['label']}")
        print(f"TERM : {block['q']}")
        ctgov(block["q"], n=block.get("n", 12))
        sys.stdout.flush()
    print("PROBE COMPLETE")


if __name__ == "__main__":
    main()
