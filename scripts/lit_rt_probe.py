#!/usr/bin/env python3
"""Europe PMC probe: has ablative radiotherapy ever been given to EMC lung metastases?

Pure stdlib, same shape as scripts/lit_lane_probe.py (CLAUDE.md section 6, escape hatch 1 -
the dev sandbox's egress proxy 403s www.ebi.ac.uk on CONNECT, so this runs on a runner).

The question trimcrae asked on 2026-08-10 was empirical and had never been asked here:
the clinical registry records metastasectomy, pazopanib, anthracycline, trabectedin and
watchful waiting for metastatic EMC, and mentions ablative radiotherapy to a metastasis
NOWHERE - no `SBRT`, no `SABR`, no `oligometastatic`, and no occurrence of `radiat` outside
the localised-disease and regional rows. That absence is a fact about this repository, not
about the world, and the two are only distinguishable by looking.

BOTH directions matter, which is why hit counts are recorded next to the query verbatim:

  * a non-zero count with a PMID lets the answer be cited rather than remembered - and
    CLAUDE.md section 7 records a manuscript citation written from recollection whose PMID
    existed in no source anywhere, which is the failure this file is shaped to avoid;
  * a hit count of ZERO on a named query is the only honest basis for "nobody has tried
    this", which is otherwise indistinguishable from "nobody here looked".

The queries are grouped by what each one could settle, because a probe whose queries all
ask the same thing produces a confident answer to one question and silence on the rest.

Output: research/literature/rt-lung-mets-probe.json, plus a digest printed to the job log
(the one channel readable from the dev sandbox - see lit_lane_probe.py for why the file,
the run artifact and the pushed ref have each failed to deliver at least once).
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OUT = pathlib.Path("research/literature/rt-lung-mets-probe.json")

# (key, query). Keep queries quotable in the report verbatim - a zero is evidence of
# absence ONLY for the exact string beside it.
QUERIES: list[tuple[str, str]] = [
    # ⛔ NO WILDCARD INSIDE A QUOTED PHRASE (fixed 2026-08-10, on this file's first run).
    # The first version asked for `"lung metastas*"`. Europe PMC matches a quoted phrase
    # literally, so the whole conjunction returned hitCount=0 — while two papers answering it
    # were already in hand from a plain web search. A zero a broken query produced is
    # indistinguishable from a zero the literature produced, and this one was one step from
    # being reported as "nobody has ever tried it". Spell the variants out instead.
    #
    # ⚠ AND FIELD-RESTRICT THE PRECISION QUESTIONS. An unfielded query searches FULL TEXT, so
    # `("extraskeletal myxoid chondrosarcoma") AND (stereotactic)` returned 42 hits whose top
    # rows were national sarcoma GUIDELINES naming both terms paragraphs apart. That is not a
    # count of papers about radiotherapy in this disease. TITLE:/ABSTRACT: is.
    # Superseded, retained: the unfielded EMC queries and `"lung metastas*"`.
    ('emc_topic_radiotherapy',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND (radiotherapy OR radiation OR irradiation OR SBRT OR SABR OR stereotactic OR radiosurgery)'),
    ('emc_topic_stereotactic',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND (SBRT OR SABR OR stereotactic OR radiosurgery OR "stereotactic body" OR ablative)'),
    ('emc_topic_lung_mets',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND ("lung metastasis" OR "lung metastases" OR "pulmonary metastasis" OR "pulmonary metastases")'),
    ('emc_topic_lung_mets_local_therapy',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND ("lung metastasis" OR "lung metastases" OR "pulmonary metastasis" OR "pulmonary metastases") AND ((radiotherapy OR radiation OR irradiation OR SBRT OR SABR OR stereotactic OR radiosurgery) OR metastasectomy OR ablation)'),
    ('emc_topic_metastasectomy',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND (metastasectomy OR "pulmonary resection" OR "wedge resection")'),
    ('emc_topic_oligometastatic',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND (oligometastatic OR oligometastases OR "metastasis-directed" OR "local control")'),
    ('emc_topic_thermal_ablation',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND ("radiofrequency ablation" OR cryoablation OR microwave OR "thermal ablation")'),
    ('emc_topic_whole_lung_rt',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND ("whole lung" OR "whole-lung" OR "lung irradiation" OR "hemithoracic")'),
    ('emc_topic_metastatic_pattern',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND ("first site" OR "site of metastasis" OR "metastatic pattern" OR "pattern of metastasis" OR "distant recurrence")'),
    ('emc_topic_natural_history',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND ("natural history" OR indolent OR "watchful waiting" OR "active surveillance" OR "long-term survival")'),
    ('emc_topic_series_outcomes',
     '(TITLE:"extraskeletal myxoid chondrosarcoma" OR ABSTRACT:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma" OR ABSTRACT:"extra-skeletal myxoid chondrosarcoma") AND (cohort OR series OR retrospective OR SEER) AND (survival OR outcome OR recurrence)'),
    ('sarcoma_lung_sbrt',
     '(TITLE:sarcoma OR ABSTRACT:sarcoma) AND ("lung metastasis" OR "lung metastases" OR "pulmonary metastasis" OR "pulmonary metastases") AND (SBRT OR SABR OR "stereotactic body radiation" OR "stereotactic ablative")'),
    ('sarcoma_lung_sbrt_title',
     'TITLE:sarcoma AND TITLE:(SBRT OR SABR OR stereotactic) AND TITLE:(lung OR pulmonary OR metastases)'),
    ('sarcoma_sbrt_vs_surgery',
     '(TITLE:sarcoma OR ABSTRACT:sarcoma) AND ("lung metastasis" OR "lung metastases" OR "pulmonary metastasis" OR "pulmonary metastases") AND (SBRT OR SABR OR stereotactic) AND (metastasectomy OR resection OR surgery)'),
    ('sarcoma_sbrt_histology_subgroup',
     '(TITLE:sarcoma OR ABSTRACT:sarcoma) AND (SBRT OR SABR OR stereotactic) AND ("histologic subtype" OR "histological subtype" OR histotype OR "by histology")'),
    ('chondrosarcoma_sbrt_lung',
     '(TITLE:chondrosarcoma OR ABSTRACT:chondrosarcoma) AND (SBRT OR SABR OR stereotactic) AND (lung OR pulmonary)'),
    ('chondrosarcoma_radioresistance',
     '(TITLE:chondrosarcoma OR ABSTRACT:chondrosarcoma) AND (radioresistance OR radioresistant OR radiosensitivity OR "radiation resistance")'),
    ('sarcoma_alpha_beta_ratio',
     '(sarcoma OR chondrosarcoma) AND ("alpha/beta ratio" OR "alpha beta ratio") AND (radiotherapy OR fractionation)'),
    ('myxoid_liposarcoma_radiosensitivity',
     '(TITLE:"myxoid liposarcoma" OR ABSTRACT:"myxoid liposarcoma") AND (radiosensitivity OR radiosensitive OR "response to radiation" OR radiotherapy)'),
    ('nr4a3_dna_damage_radiation',
     '(TITLE:NR4A3 OR ABSTRACT:NR4A3 OR TITLE:"NOR-1" OR ABSTRACT:"NOR-1") AND (radiation OR radiotherapy OR "DNA damage" OR irradiation)'),
    ('myxoid_matrix_hypoxia_radioresponse',
     '("myxoid matrix" OR "chondroid matrix" OR "hypocellular") AND (hypoxia OR "oxygen enhancement" OR radioresistance) AND (radiotherapy OR radiation)'),
    ('mdt_rare_histology_concept',
     '"metastasis-directed therapy" AND (sarcoma OR "rare cancer" OR "ultra-rare" OR "rare histology")'),
    ('oligometastatic_patient_selection_biology',
     '(oligometastatic OR "metastasis-directed therapy") AND ("patient selection" OR "selection bias" OR biomarker) AND (indolent OR biology)'),
    ('fusion_sarcoma_local_therapy_concept',
     '(TITLE:sarcoma OR ABSTRACT:sarcoma) AND (fusion OR translocation) AND (oligometastatic OR "metastasis-directed therapy" OR "local therapy") AND (rationale OR concept OR perspective OR hypothesis)'),
    # --- (f) the plural trap, and the papers a phrase query cannot see ------------
    # `emc_topic_whole_lung_rt` returned 0 while a plain web search had already surfaced
    # "Whole Lung Radiotherapy to Treat Metastatic Extraskeletal Myxoid ChondrosarcomaS"
    # (Clinical Oncology, 2023). The suspected mechanism is the PLURAL: an exact-phrase match on
    # "extraskeletal myxoid chondrosarcoma" need not match inside "...chondrosarcomas". These
    # three discriminate -- unfielded word-AND, the plural phrase, and the title outright. If the
    # paper appears here and not above, the zero was the phrase form, not the literature.
    ('emc_words_whole_lung_rt',
     '(extraskeletal AND myxoid AND chondrosarcoma) AND ("whole lung" OR "whole-lung" OR "lung irradiation" OR hemithoracic)'),
    ('emc_plural_phrase',
     '(TITLE:"extraskeletal myxoid chondrosarcomas" OR ABSTRACT:"extraskeletal myxoid chondrosarcomas")'),
    ('whole_lung_rt_title_lookup',
     'TITLE:"Whole Lung Radiotherapy to Treat Metastatic Extraskeletal Myxoid Chondrosarcomas"'),
    # And the radiation-to-EMC papers the fielded run did surface, pulled by identifier so their
    # abstracts land in the artifact rather than being read off a search-results page.
    ('emc_rt_papers_by_doi',
     '(DOI:"10.1159/000548238" OR DOI:"10.5114/jcb.2022.115161" OR DOI:"10.1136/bcr-2022-250218" '
     'OR DOI:"10.1186/s13569-020-00150-8" OR DOI:"10.1097/COC.0000000000000590" OR DOI:"10.1097/COC.0000000000000341")'),
]


def fetch(query: str, page_size: int = 25, retries: int = 4) -> dict:
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": "core",
        "sort": "CITED desc",
    })
    url = f"{BASE}?{params}"
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-rt-probe/1.0"})
            with urllib.request.urlopen(req, timeout=90) as fh:
                return json.loads(fh.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - report, do not mask
            last = exc
            time.sleep(2 + 3 * attempt)
    return {"__error__": f"{type(last).__name__}: {last}"}


def slim(rec: dict) -> dict:
    return {
        "pmid": rec.get("pmid"),
        "pmcid": rec.get("pmcid"),
        "doi": rec.get("doi"),
        "title": (rec.get("title") or "").strip().rstrip("."),
        "journal": (rec.get("journalInfo") or {}).get("journal", {}).get("title")
        or rec.get("journalTitle"),
        "year": rec.get("pubYear"),
        "cited_by": rec.get("citedByCount"),
        "is_oa": rec.get("isOpenAccess"),
        "type": rec.get("pubType"),
        # ⛔ THE ABSTRACT IS THE POINT FOR THE PAPERS THAT MATTER MOST HERE. Both papers that
        # answer the direct question -- the SABR case report and the whole-lung RT report --
        # sit behind Cloudflare, which returns 403 to the runner as well as to the sandbox.
        # Europe PMC serves their abstracts through the API that is designed to serve them,
        # which is the right channel: no scraping, no paywall, and a record of what was read.
        "abstract": (rec.get("abstractText") or "")[:1800] or None,
    }


def main() -> int:
    only = os.environ.get("RT_PROBE_ONLY", "").strip()
    queries = QUERIES
    if only:
        keys = {k.strip() for k in only.replace(",", " ").split() if k.strip()}
        queries = [(k, q) for k, q in QUERIES if k in keys]
        if not queries:
            print(f"no query matched RT_PROBE_ONLY={only!r}", file=sys.stderr)
            return 2

    out: dict = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "Europe PMC REST search API",
        "question": (
            "Has ablative radiotherapy ever been delivered to lung metastases in extraskeletal "
            "myxoid chondrosarcoma, and is there a concept paper in it?"
        ),
        "note": (
            "Hit counts are Europe PMC's, on the query string recorded beside them. A zero is "
            "evidence of absence ONLY for that exact query - quote the query, never just the zero. "
            "A non-zero count is evidence a paper EXISTS, not that it says what its title suggests: "
            "every figure taken from these hits must come from reading the paper."
        ),
        "queries": {},
    }

    errors = 0
    for key, query in queries:
        data = fetch(query)
        if "__error__" in data:
            errors += 1
            out["queries"][key] = {"query": query, "error": data["__error__"]}
            print(f"[ERR ] {key}: {data['__error__']}", file=sys.stderr)
            continue
        results = (data.get("resultList") or {}).get("result", []) or []
        out["queries"][key] = {
            "query": query,
            "hit_count": data.get("hitCount"),
            "returned": len(results),
            "top": [slim(r) for r in results],
        }
        print(f"[ok  ] {key}: hitCount={data.get('hitCount')} returned={len(results)}")
        time.sleep(0.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT} ({OUT.stat().st_size} bytes); {errors} query error(s)")

    top_n = int(os.environ.get("RT_PROBE_DIGEST_N", "8"))
    print("\n===BEGIN RT-PROBE-DIGEST===")
    for key, q in queries:
        rec = out["queries"].get(key, {})
        if "error" in rec:
            print(f"## {key}\tERROR\t{rec['error']}")
            continue
        print(f"## {key}\thits={rec.get('hit_count')}\tq={q}")
        for r in (rec.get("top") or [])[:top_n]:
            print("   - PMID:{pmid} | {year} | {journal} | {title} | doi:{doi} | cited:{cited_by} | oa:{oa}".format(
                pmid=r.get("pmid") or "-", year=r.get("year") or "-",
                journal=(r.get("journal") or "-")[:38],
                title=(r.get("title") or "-")[:120],
                doi=r.get("doi") or "-", cited_by=r.get("cited_by"), oa=r.get("is_oa")))
    print("===END RT-PROBE-DIGEST===")
    return 1 if errors == len(queries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
