#!/usr/bin/env python3
"""
Is the ASO delivery gate ONE gate, or three routes with different requirements? — the retrieval record.

WHY THIS EXISTS. `systems/graph/blockers.json` carries a single `BLK-DELIVERY`
(`requires_future_technology`), retired only by `TECH-OLIGO-DELIVERY`, whose own name describes a
SYSTEMIC solution: "a conjugate, tumour-penetrating peptide or ligand-targeted lipid nanoparticle —
OR a characterised EMC-enriched surface antigen to serve as its targeting arm". The forecast against
it is 2029. So the portfolio grades this route blocked on a technology that does not exist.

⛔ BUT THE MANUSCRIPT'S OWN §3c ALREADY LISTS A DELIVERY ROUTE THAT NEEDS NONE OF THAT, AND LISTS IT
FIRST. Local/intratumoural administration requires no surface antigen, no conjugate and no targeting
technology; it was promoted to the top of §3c precisely because the receptor-targeted routes below it
"all depend on an input that does not yet exist". A single monolithic blocker cannot represent a set
of routes whose requirements differ — it takes the hardest one and applies it to the modality. That
is the shape CLAUDE.md §0 warns about: *"blocked" is a claim that needs evidence, and it is usually
wrong.*

WHAT THIS ASKS, therefore, and it is a retrieval question rather than an opinion:
  R1 LOCAL      — is intratumoural/local oligonucleotide administration an established practice?
  R2 INHALED    — is pulmonary/inhaled oligonucleotide delivery to LUNG TUMOURS an active field?
                  This route matters for EMC specifically because EMC's distant spread is
                  lung-dominant, and inhalation needs no tumour-selective surface antigen either.
  R3 SYSTEMIC   — the antigen-dependent route the current blocker describes.
  R4 FIELD      — is anyone else driving junction-directed oligonucleotide delivery forward in a
                  fusion sarcoma, such that EMC work would meet a solved problem rather than wait on
                  one it must solve alone?

HOW. No network. Every record is read from corpora already published to the `literature-cache`
branch by `.github/workflows/fetch-literature.yml`, via `git show` — the same provenance discipline
as `lit-targets-aso-verify.json`, whose schema this file reproduces so that
`research/manuscripts/lint_citations.py` can anchor the manuscript's prose identifiers against it.

⛔ WHAT AN ENTRY HERE DOES AND DOES NOT LICENSE. A record here is evidence THE RECORD EXISTS, with
that title and that abstract, returned by a machine search. It is NOT evidence that inhaled delivery
works, that it would work in EMC, or that any route is passable. Retrieval is not efficacy. The
manuscript may cite these to say *the field is active and the requirement differs by route*; it may
not cite them to say a gate is passed.

Output: lit-targets-aso-delivery-routes.json
"""

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso", "lit-targets-aso-delivery-routes.json")
BRANCH = "origin/literature-cache"

CORPORA = [
    "literature/inhaled-oligo-lung-metastasis",
    "literature/inhaled-oligonucleotide-delivery",
    "literature/fusion-oligo-delivery-progress",
    "literature/emc-metastatic-site-curation",
]

#: R5 is a DIFFERENT KIND OF QUESTION from R1/R2/R4 and is kept in the same file only because it is
#: the same retrieval act. R1/R2/R4 ask whether a delivery ROUTE is an active field. R5 asks whether
#: this DISEASE goes to the organ that route reaches — the premise without which R2 is irrelevant to
#: EMC no matter how active the field is. It is scored by a different regex on a different corpus and
#: is counted separately so the two can never be summed.
EMC = re.compile(
    r"\b(extraskeletal myxoid chondrosarcoma|extra-skeletal myxoid chondrosarcoma|"
    r"chordoid sarcoma)\b", re.I)
LUNG_ANY = re.compile(r"\b(lung|lungs|pulmonary)\b", re.I)
QUANT = re.compile(r"\b\d+\s*(?:of|/)\s*\d+\b|\b\d+(?:\.\d+)?\s?%|\b\d+\s*-\s*\d+\s?%")

OLIGO = re.compile(
    r"\b(sirna|small interfering rna|antisense oligonucleotide|antisense oligonucleotides|"
    r"oligonucleotide|oligonucleotides|gapmer|shrna|locked nucleic acid|"
    r"phosphorothioate|rnase h)\b", re.I)
INHALED = re.compile(
    r"\b(inhaled|inhalation|inhalable|aerosol|aerosolized|aerosolised|nebulized|nebulised|"
    r"nebuli[sz]ation|intratracheal|intranasal|dry powder|pulmonary delivery|"
    r"pulmonary administration)\b", re.I)
LOCAL = re.compile(
    r"\b(intratumou?ral|intratumou?rally|intralesional|local administration|"
    r"direct injection into the tumou?r)\b", re.I)
LUNG_TUMOUR = re.compile(
    r"\b(lung cancer|lung tumou?r|lung metasta\w*|pulmonary metasta\w*|"
    r"lung adenocarcinoma|metastatic lung)\b", re.I)
FUSION = re.compile(
    r"\b(fusion (?:oncogene|transcript|gene|junction|breakpoint)|breakpoint junction|"
    r"ews[-_ ]?fli1?|ewsr1|pax3[-_ ]?foxo1|ss18[-_ ]?ssx|bcr[-_ ]?abl|"
    r"dnajb1[-_ ]?prkaca|translocation[- ]driven)\b", re.I)
SARCOMA = re.compile(r"\b(sarcoma|ewing|rhabdomyosarcoma|synovial sarcoma)\b", re.I)
#: Words that mark a record as a CLINICAL-stage report rather than a preclinical one. Kept separate
#: because "the field is active" and "the field has reached patients" are different claims and the
#: manuscript must not be able to blur them.
CLINICAL = re.compile(
    r"\b(phase (?:1|2|3|i|ii|iii)\b|clinical trial|first-in-human|randomi[sz]ed|"
    r"in patients|patients received)\b", re.I)


def _git_show(path):
    return subprocess.run(["git", "show", f"{BRANCH}:{path}"],
                          cwd=os.path.dirname(os.path.dirname(HERE)),
                          capture_output=True, text=True, check=True).stdout


def _load(corpus):
    """Records of one corpus, or None if the corpus is not on the branch (an absent reading)."""
    try:
        return json.loads(_git_show(f"{corpus}/_index.json"))
    except subprocess.CalledProcessError:
        return None


#: Europe PMC returns structured-abstract headings and italics as HTML, and the sibling anchor
#: (`lit-targets-aso-verify.json`) promises "markup stripped". Honouring that promise here is not
#: cosmetic: a quote copied into the manuscript with `<i>` or `&lt;sub&gt;` in it is a quote nobody
#: can match back to the source, which defeats the point of an anchor file.
_TAG = re.compile(r"<[^>]+>")
_ENT = {"&lt;": "<", "&gt;": ">", "&amp;": "&", "&quot;": '"', "&apos;": "'", "&#39;": "'"}


def _strip_markup(s):
    if not s:
        return ""
    for k, v in _ENT.items():
        s = s.replace(k, v)
    s = _TAG.sub(" ", s)                      # headings become spaces, never silent joins
    return re.sub(r"\s+", " ", s).strip()


def _text(r):
    return f"{_strip_markup(r.get('title'))} {_strip_markup(r.get('abstract'))}"


def _record(r, corpus, routes):
    return {
        "id": f"PMID: {r['pmid']}" if r.get("pmid") else f"PMCID: {r.get('pmcid')}",
        "pmid": r.get("pmid"), "pmcid": r.get("pmcid"), "doi": r.get("doi"),
        "title": _strip_markup(r.get("title")), "authors": r.get("authors"), "year": r.get("year"),
        "routes": routes,
        "clinical_stage_language_present": bool(CLINICAL.search(_text(r))),
        "corpus": f"{corpus} (branch literature-cache)",
        "abstract_verbatim": _strip_markup(r.get("abstract")),
    }


def classify(r):
    """Which delivery-route questions this record speaks to. A record may answer more than one."""
    t = _text(r)
    # R5 first, and it is deliberately NOT gated on the oligonucleotide regex: it is a question
    # about this disease's natural history, and an EMC outcome series has no reason to mention an
    # oligonucleotide. Gating it on OLIGO would have returned zero and read as "no evidence".
    if EMC.search(t) and LUNG_ANY.search(t) and QUANT.search(t):
        return ["R5_EMC_LUNG_DOMINANCE"]
    if not OLIGO.search(t):
        return []
    routes = []
    if INHALED.search(t) and LUNG_TUMOUR.search(t):
        routes.append("R2_INHALED_LUNG_TUMOUR")
    elif INHALED.search(t):
        routes.append("R2b_INHALED_ANY_INDICATION")
    if LOCAL.search(t):
        routes.append("R1_LOCAL_INTRATUMOURAL")
    if FUSION.search(t) and SARCOMA.search(t):
        routes.append("R4_FUSION_SARCOMA_FIELD")
    return routes


def build():
    corpora, missing = {}, {}
    for c in CORPORA:
        recs = _load(c)
        if recs is None:
            missing[c] = ("not present on the literature-cache branch at read time — an ABSENT "
                          "READING, never a reading of absence. Re-run this script after the "
                          "corresponding fetch-literature.yml dispatch publishes.")
        else:
            corpora[c] = recs

    selected, seen = [], set()
    for c, recs in corpora.items():
        for r in recs:
            routes = classify(r)
            if not routes:
                continue
            key = r.get("pmid") or r.get("pmcid") or r.get("doi")
            if not key or key in seen:
                continue
            seen.add(key)
            selected.append(_record(r, c, routes))

    selected.sort(key=lambda r: (-(r["year"] or 0), r["title"] or ""))

    def by(route):
        return [r for r in selected if route in r["routes"]]

    counts = {route: len(by(route)) for route in
              ("R1_LOCAL_INTRATUMOURAL", "R2_INHALED_LUNG_TUMOUR", "R2b_INHALED_ANY_INDICATION",
               "R4_FUSION_SARCOMA_FIELD", "R5_EMC_LUNG_DOMINANCE")}

    return {
        "_note": "Retrieval record for the fusion-junction ASO manuscript's DELIVERY-ROUTE section. "
                 "Every identifier was returned by a Europe PMC search run on a GitHub runner and "
                 "is read here from the published corpus on branch literature-cache — none was "
                 "typed from recollection. This file is an ANCHOR that "
                 "research/manuscripts/lint_citations.py checks the manuscript's prose identifiers "
                 "against.",
        "_limits": [
            "A record here is evidence THE RECORD EXISTS with that title and abstract. It is NOT "
            "evidence that inhaled or local delivery works, that either would work in EMC, or that "
            "any delivery gate is passed. Retrieval is not efficacy.",
            "Title/abstract matching only. Counts are LOWER BOUNDS — a paper that names its route "
            "only in the body is missed. That direction is the safe one for an 'is this field "
            "active' question and the wrong one for any claim of exhaustiveness.",
            "`clinical_stage_language_present` is a REGEX ON THE ABSTRACT, not a verified trial "
            "stage. It flags records worth reading; it does not establish that any agent reached "
            "patients.",
            "No EMC record is expected or claimed here. These corpora speak to whether a DELIVERY "
            "ROUTE is an active field, never to whether it has been tried in this disease.",
        ],
        "_what_this_does_not_settle": (
            "Whether an inhaled oligonucleotide could reach an EMC pulmonary metastasis. EMC "
            "metastases are parenchymal nodules, not airway-surface disease, and every barrier "
            "question — deposition, mucus and surfactant, distance from airway lumen to a "
            "matrix-dominated hypocellular nodule, cellular uptake, endosomal escape — is "
            "untouched by a literature count. What the count can settle is narrower and is the "
            "only thing it is used for: the route is not hypothetical, and it does not require the "
            "EMC-enriched surface antigen the current blocker is written around."),
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "produced_by": {
            "script": "research/manuscripts/aso_delivery_routes.py",
            "workflow": ".github/workflows/fetch-literature.yml (query path -> scripts/fetch-paper.mjs)",
            "corpora_read": sorted(corpora),
            "corpora_missing_at_read_time": missing,
            "network": "none — corpora read from branch literature-cache via `git show`",
            "cost": "$0",
        },
        "route_questions": {
            "R1_LOCAL_INTRATUMOURAL": "Is intratumoural/local oligonucleotide administration an "
                                      "established practice? Needs no surface antigen.",
            "R2_INHALED_LUNG_TUMOUR": "Is inhaled/pulmonary oligonucleotide delivery to lung "
                                      "tumours or lung metastases an active field? Needs no "
                                      "surface antigen either.",
            "R2b_INHALED_ANY_INDICATION": "Inhaled oligonucleotide delivery outside oncology — "
                                          "counted separately because a non-tumour indication says "
                                          "the ROUTE works and nothing about a tumour nodule.",
            "R4_FUSION_SARCOMA_FIELD": "Is junction-directed oligonucleotide work in fusion "
                                       "sarcomas being driven forward by other groups?",
            "R5_EMC_LUNG_DOMINANCE": "Does EMC actually go to the lung? R2's relevance to this "
                                     "disease rests entirely on this premise, and it is a "
                                     "DIFFERENT KIND of question from R1/R2/R4 — natural history, "
                                     "not delivery engineering. Never sum it with the others.",
        },
        "counts": counts,
        "n_records": len(selected),
        "records": selected,
    }


def main():
    res = build()
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in res.items() if k != "records"}, indent=2))
    for r in res["records"][:25]:
        print(f"  {r['year']} {r['id']:<16} {'+'.join(x[:2] for x in r['routes']):<10} "
              f"{(r['title'] or '')[:88]}")


if __name__ == "__main__":
    main()
