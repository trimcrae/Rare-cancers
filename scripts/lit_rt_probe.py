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
    # --- (a) the direct question: RT to an EMC metastasis, any modality ----------
    ("emc_radiotherapy_any",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "chordoid sarcoma") '
     'AND (radiotherapy OR radiation OR irradiation)'),
    ("emc_sbrt_sabr",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") '
     'AND (SBRT OR SABR OR stereotactic OR "stereotactic body" OR radiosurgery OR ablative)'),
    ("emc_lung_met_local_therapy",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") '
     'AND ("lung metastas*" OR "pulmonary metastas*") AND (radiotherapy OR stereotactic OR ablation OR metastasectomy)'),
    ("emc_oligometastatic",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") '
     'AND (oligometastatic OR oligometastas* OR "local therapy" OR "local control")'),
    ("emc_metastasectomy",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") AND metastasectomy'),
    ("emc_thermal_ablation",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") '
     'AND ("radiofrequency ablation" OR cryoablation OR microwave OR "thermal ablation")'),

    # --- (b) the denominator: is the metastatic pattern actually lung-confined? --
    # RT-LUNG-DIRECTED's stated missing numerator. Its view says metastatic SITE was never
    # curated as a field; that is a statement about the registry, not about the primary reports.
    ("emc_first_site_of_metastasis",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") '
     'AND ("first site" OR "site of metastasis" OR "metastatic pattern" OR "distant recurrence")'),
    ("emc_natural_history_indolent",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") '
     'AND ("natural history" OR indolent OR "long-term survival" OR "watchful waiting" OR observation)'),
    ("emc_large_series_outcomes",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") '
     'AND (cohort OR series OR retrospective OR registry OR SEER) AND (survival OR outcome OR recurrence)'),

    # --- (c) the borrowed evidence base: SBRT for sarcoma lung metastases -------
    # If EMC-specific evidence is thin, the concept paper's weight rests on whether the
    # generic sarcoma-lung-SBRT literature is strong AND whether it reports histology subsets.
    ("sarcoma_lung_sbrt_series",
     '(sarcoma) AND ("lung metastas*" OR "pulmonary metastas*") AND (SBRT OR SABR OR "stereotactic body radiation" '
     'OR "stereotactic ablative")'),
    ("sarcoma_lung_sbrt_meta",
     '(sarcoma) AND (SBRT OR SABR OR "stereotactic ablative") AND ("systematic review" OR "meta-analysis")'),
    ("sarcoma_sbrt_histology_subgroup",
     '(sarcoma) AND (SBRT OR SABR OR "stereotactic ablative") AND (histology OR "histologic subtype" OR "per-histology")'),
    ("sarcoma_sbrt_vs_metastasectomy",
     '(sarcoma) AND ("lung metastas*" OR "pulmonary metastas*") AND (SBRT OR SABR OR "stereotactic") '
     'AND (metastasectomy OR surgery OR resection) AND (compar* OR versus)'),
    ("sabr_comet_oligometastatic_trials",
     '("SABR-COMET" OR "oligometastatic") AND ("randomized" OR "randomised" OR "phase II" OR "phase 2") '
     'AND (radiotherapy OR SABR OR SBRT) AND (survival OR "overall survival")'),
    ("chondrosarcoma_sbrt_lung",
     '(chondrosarcoma) AND (SBRT OR SABR OR stereotactic) AND (lung OR pulmonary OR metastas*)'),

    # --- (d) the radiobiology: is the "radioresistant" label right for THIS tumour? -
    # The repository already holds a live contradiction about whether RT does anything in EMC
    # (RT-RT-INTENSIFY), and a hypoxia/matrix correction that has closed one route in this family.
    ("sarcoma_alpha_beta_radiobiology",
     '(sarcoma OR chondrosarcoma) AND ("alpha/beta" OR "alpha beta ratio" OR fractionation OR radiobiology) '
     'AND (radioresistan* OR radiosensitiv*)'),
    ("chondrosarcoma_radioresistance",
     '(chondrosarcoma) AND (radioresistan* OR radiosensitiv* OR "particle therapy" OR "carbon ion" OR proton)'),
    ("myxoid_matrix_hypoxia_radiation",
     '(myxoid OR "chondroid matrix" OR "extracellular matrix") AND (hypoxia OR "oxygen enhancement") '
     'AND (radiotherapy OR radiation) AND (tumour OR tumor OR sarcoma)'),
    ("nr4a3_radiation_response",
     '(NR4A3 OR "NOR-1" OR "NOR1") AND (radiation OR radiotherapy OR "DNA damage" OR irradiation)'),
    ("myxoid_liposarcoma_radiosensitivity",
     '("myxoid liposarcoma") AND (radiosensitiv* OR radiotherapy OR "response to radiation")'),

    # --- (e) has the concept paper already been written by someone else? --------
    # The cheapest way to kill this idea, and the one nobody runs first.
    ("ultrarare_sarcoma_oligomet_concept",
     '(sarcoma OR "rare cancer") AND (oligometastatic OR "local therapy") AND '
     '("conceptual" OR "concept" OR "hypothesis" OR "position paper" OR "perspective" OR "opinion")'),
    ("indolent_biology_local_therapy_rationale",
     '(indolent OR "slow-growing" OR "long natural history") AND (oligometastatic OR "metastasis-directed therapy") '
     'AND (rationale OR "patient selection" OR "who benefits")'),
    ("metastasis_directed_therapy_rare_histology",
     '"metastasis-directed therapy" AND (sarcoma OR "rare histology" OR "ultra-rare")'),
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
