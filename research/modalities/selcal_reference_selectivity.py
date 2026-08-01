#!/usr/bin/env python3
"""OPEN PRECONDITION 1 of the endpoint-MD SENSITIVITY CONTROL — the reference number, fetched not remembered.

WHAT THIS IS FOR. `selectivity-resolution-options.md` §2-D makes this a **blocking, $0 step that must precede
the spend**:

    ⚠ Open precondition 1 — the reference number. A positive control needs a **measured, primary-source**
    selectivity value, and STRATEGY Open decision 7 binds: *the accuracy band may not be wider than the signal
    being calibrated*. The survey explicitly does **not** supply one (`selectivity_kcal: null`,
    `needs_primary_source_verification: true`) for either pair.

A sensitivity control is only a control if the answer is genuinely KNOWN before the run. So this module goes and
reads it, on a CI runner with unrestricted internet (CLAUDE.md §6 — the dev sandbox's egress proxy answers
Europe PMC / PMC / NCBI with 403 at CONNECT, which is never a reason to defer).

⛔ IT CURATES NOTHING AND CONCLUDES NOTHING. It emits **quoted spans of real text with their source**, plus the
RCSB chemical-component record for each candidate ligand. Every number that later enters the frozen panel is
transcribed BY HAND from this artifact, with the quote beside it, exactly the way `extract_smarca2_ic50.py`
already works on this repo's other literature step. AGENTS.md's medical-integrity rule is the binding one:
*if you cannot find a source, say the information is not available — never fill the gap with a plausible number.*

★ WHAT A "SELECTIVITY VALUE" MUST BE HERE, and why it is not a ΔΔG. The endpoint-MD readout (E1, the
interface-RMSD plateau in Å) has **no established quantitative link to degradation selectivity** — that is
§1d(3) of the options paper and it does not change because we would like a calibration curve. So this step is
NOT trying to convert a DC50 ratio into an expected Ångström separation; doing that would be fabricating the
very link the program does not have. What the reference number must establish is narrower and sufficient:

    1. that a REAL paralogue difference exists for the chosen ligand, measured in a primary source, and
    2. WHICH DIRECTION it points.

Those two facts are what make the panel a sensitivity control rather than an experiment with an unknown answer.
The magnitude enters only as a sanity floor: a difference so small that the reference measurement itself cannot
resolve it would fail STRATEGY Open decision 7 (*the accuracy band may not be wider than the signal being
calibrated*) and the pair would be rejected here rather than after the spend.

USAGE (CI, `python3 selcal_reference_selectivity.py`; writes selcal-reference-selectivity.json)
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "selcal-reference-selectivity.json")
UA = {"User-Agent": "rare-cancers-selcal-reference/1.0 (research; contact via github.com/trimcrae)"}

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
RCSB_CHEMCOMP = "https://data.rcsb.org/rest/v1/core/chemcomp/{ccd}"
RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{pdb}"

#: The searches to run. Each is a candidate REFERENCE PAPER for one arm-pair/ligand combination. They are
#: queries, not conclusions — whichever returns a primary source with both paralogues measured wins, and the
#: curation step records which one and why.
QUERIES = [
    {"tag": "D1_acbi2_kofink2022",
     "pair": ["SMARCA2", "SMARCA4"],
     "ligand_hint": "ACBI2",
     "query": 'TITLE:"A selective and orally bioavailable VHL-recruiting PROTAC achieves SMARCA2 degradation '
              'in vivo"'},
    {"tag": "D1_acbi1_farnaby2019",
     "pair": ["SMARCA2", "SMARCA4"],
     "ligand_hint": "ACBI1",
     "query": 'TITLE:"BAF complex vulnerabilities in cancer demonstrated via structure-based PROTAC design"'},
    {"tag": "D1_wurz2023",
     "pair": ["SMARCA2", "SMARCA4"],
     "ligand_hint": "Wurz compound 1 (CCD YHB, 8G1Q)",
     "query": 'TITLE:"Affinity and cooperativity modulate ternary complex formation to drive targeted protein '
              'degradation"'},
    {"tag": "D2_ikzf",
     "pair": ["IKZF1", "IKZF3"],
     "ligand_hint": "lenalidomide / CELMoD",
     "query": '(IKZF1 AND IKZF3 AND (selectivity OR selective) AND (degradation OR degrader) AND cereblon)'},
]

#: Deposited ternaries named by `s-calibrator-survey.json` for the two symmetric pairs. Their chemical
#: components are the only NON-FABRICATED source of a posed ligand's chemistry, which is what the co-fold
#: needs — the survey itself carries no SMILES.
TERNARY_PDBS = {
    "SMARCA2": ["6HAX", "6HAY", "7S4E", "7Z6L", "7Z76", "7Z77", "8G1P", "9D4B", "9DTY", "9HYB"],
    "SMARCA4": ["6HR2", "8G1Q", "8QJR", "9DTX"],
}

#: Sentence filter. Deliberately broad on the QUANTITY and strict on the requirement that BOTH paralogues are
#: named, because a selectivity claim that mentions only one arm is not a selectivity measurement.
_QUANT = re.compile(r"(DC\s?50|DC[₅5]0|Dmax|D\s?max|IC\s?50|IC[₅5]0|\bK[dD]\b|\bK[iI]\b|cooperativ|alpha|α|"
                    r"\bfold\b|selectiv)", re.I)
_BOTH_SMARCA = re.compile(r"SMARCA2", re.I), re.compile(r"SMARCA4|BRG1", re.I)
_BOTH_IKZF = re.compile(r"IKZF1|Ikaros", re.I), re.compile(r"IKZF3|Aiolos", re.I)


def _get(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _get_json(url, timeout=90):
    return json.loads(_get(url, timeout=timeout).decode("utf-8", "replace"))


def epmc_search(query, page_size=10):
    """Europe PMC `search` -> the core records. Returns [] on any transport failure, with the error recorded
    by the caller — an unreachable API is an ABSENT READING, never a reading of absence (CLAUDE.md §4)."""
    url = "%s/search?query=%s&resultType=core&format=json&pageSize=%d" % (
        EPMC, urllib.parse.quote(query), page_size)
    return (_get_json(url).get("resultList") or {}).get("result") or []


def epmc_fulltext_xml(pmcid):
    """Open-access full text for a PMCID, or None when it is not OA. Raises nothing."""
    try:
        return _get("%s/%s/fullTextXML" % (EPMC, pmcid)).decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return None


def _strip_tags(xml):
    txt = re.sub(r"<[^>]+>", " ", xml)
    return re.sub(r"\s+", " ", txt)


def quantitative_spans(text, both):
    """Sentences that carry a QUANTITY and name BOTH members of the pair. Returns the raw sentences.

    Both conditions matter and neither is sufficient: a sentence with a DC50 and one paralogue is an affinity,
    not a selectivity; a sentence naming both with no number is a claim, not a measurement."""
    a_re, b_re = both
    out = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        s = sent.strip()
        if len(s) < 25 or len(s) > 700:
            continue
        if _QUANT.search(s) and a_re.search(s) and b_re.search(s):
            out.append(s)
    # de-duplicate while keeping order (full texts repeat the abstract)
    seen, uniq = set(), []
    for s in out:
        k = s[:160].lower()
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq[:60]


def chemcomp(ccd):
    """The RCSB chemical-component record for one CCD id — formula, weight and the DEPOSITED SMILES.

    This is the primary, non-fabricated source of a posed ligand's chemistry. `nrv04_covalent_assemble`
    needs exactly this: heavy-atom count + a template SMILES whose graph matches the co-folded atoms."""
    try:
        d = _get_json(RCSB_CHEMCOMP.format(ccd=ccd.upper()))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        return {"ccd": ccd, "error": "%s: %s" % (type(e).__name__, e)}
    cc = d.get("chem_comp") or {}
    smiles = {}
    for row in (d.get("pdbx_chem_comp_descriptor") or []):
        if (row.get("type") or "").upper() == "SMILES_CANONICAL":
            smiles[row.get("program") or "?"] = row.get("descriptor")
    return {"ccd": cc.get("id") or ccd, "name": cc.get("name"), "formula": cc.get("formula"),
            "formula_weight": cc.get("formula_weight"), "type": cc.get("type"),
            "smiles_canonical_by_program": smiles,
            "_source": RCSB_CHEMCOMP.format(ccd=(cc.get("id") or ccd))}


def entry_ligands(pdb):
    """(title, resolution, [CCD ids of the non-polymer components]) for one PDB entry."""
    try:
        d = _get_json(RCSB_ENTRY.format(pdb=pdb.upper()))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        return {"pdb": pdb, "error": "%s: %s" % (type(e).__name__, e)}
    return {"pdb": pdb.upper(),
            "title": (d.get("struct") or {}).get("title"),
            "resolution_A": ((d.get("rcsb_entry_info") or {}).get("resolution_combined") or [None])[0],
            "method": ((d.get("exptl") or [{}])[0]).get("method"),
            "nonpolymer_ccd_ids": (d.get("rcsb_entry_info") or {}).get("nonpolymer_bound_components") or [],
            "_source": RCSB_ENTRY.format(pdb=pdb.upper())}


def run(queries=QUERIES, pdbs=TERNARY_PDBS, out_path=OUT):
    doc = {
        "_what": "OPEN PRECONDITION 1 for the endpoint-MD SENSITIVITY CONTROL (options paper §2-D): the "
                 "MEASURED, PRIMARY-SOURCE paralogue-selectivity reference for the candidate calibrator "
                 "pairs, fetched rather than remembered.",
        "_this_is_evidence_not_a_conclusion": "Every field below is either a Europe PMC / RCSB API response "
                                              "or a verbatim sentence from an open-access full text. Nothing "
                                              "here is curated, averaged or interpreted. The frozen panel "
                                              "transcribes from this file by hand, with the quote attached.",
        "_what_the_number_must_establish": "(1) that a real paralogue difference exists for the chosen "
                                           "ligand, in a primary source, and (2) its DIRECTION. NOT a "
                                           "conversion into an expected Angstrom separation — E1 has no "
                                           "established quantitative link to degradation selectivity "
                                           "(selectivity-resolution-options.md §1d(3)), so such a "
                                           "conversion would fabricate the link the program lacks.",
        "_decision_7": "STRATEGY Open decision 7 binds: the accuracy band may not be wider than the signal "
                       "being calibrated. A pair whose reported difference is inside its own measurement "
                       "error is REJECTED here, before any spend.",
        "papers": [], "ligands": {}, "entries": [],
    }
    for q in queries:
        rec = {"tag": q["tag"], "pair": q["pair"], "ligand_hint": q["ligand_hint"], "query": q["query"]}
        try:
            hits = epmc_search(q["query"])
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
            rec["error"] = "%s: %s" % (type(e).__name__, e)
            rec["_absent_reading"] = ("the search could not be READ. That is not evidence that no reference "
                                      "exists (CLAUDE.md §4) — re-run before concluding anything.")
            doc["papers"].append(rec)
            continue
        rec["n_hits"] = len(hits)
        rec["records"] = []
        both = _BOTH_IKZF if "IKZF1" in q["pair"] else _BOTH_SMARCA
        for h in hits[:4]:
            r = {"title": h.get("title"), "journal": (h.get("journalInfo") or {}).get("journal", {}).get("title"),
                 "year": h.get("pubYear"), "doi": h.get("doi"), "pmid": h.get("pmid"), "pmcid": h.get("pmcid"),
                 "isOpenAccess": h.get("isOpenAccess"), "authorString": h.get("authorString"),
                 "_source": "%s/search?query=%s" % (EPMC, urllib.parse.quote(q["query"]))}
            abstract = h.get("abstractText") or ""
            r["abstract_quantitative_spans"] = quantitative_spans(_strip_tags(abstract), both)
            if h.get("pmcid") and (h.get("isOpenAccess") == "Y"):
                xml = epmc_fulltext_xml(h["pmcid"])
                if xml:
                    r["fulltext_chars"] = len(xml)
                    r["fulltext_quantitative_spans"] = quantitative_spans(_strip_tags(xml), both)
                else:
                    r["fulltext_quantitative_spans"] = []
                    r["_fulltext_absent"] = ("declared open access but fullTextXML did not return — an absent "
                                             "reading, not a reading of absence")
            rec["records"].append(r)
        doc["papers"].append(rec)

    seen_ccd = set()
    for gene, ids in (pdbs or {}).items():
        for pdb in ids:
            e = entry_ligands(pdb)
            e["arm_gene"] = gene
            doc["entries"].append(e)
            for ccd in (e.get("nonpolymer_ccd_ids") or []):
                if ccd not in seen_ccd:
                    seen_ccd.add(ccd)
                    doc["ligands"][ccd] = chemcomp(ccd)

    with open(out_path, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    n_span = sum(len(r.get("fulltext_quantitative_spans") or []) + len(r.get("abstract_quantitative_spans") or [])
                 for p in doc["papers"] for r in (p.get("records") or []))
    print("[selcal-ref] wrote %s: %d paper queries, %d quantitative spans, %d PDB entries, %d ligands"
          % (os.path.basename(out_path), len(doc["papers"]), n_span, len(doc["entries"]), len(doc["ligands"])),
          flush=True)
    for p in doc["papers"]:
        for r in (p.get("records") or [])[:1]:
            print("  [%s] %s (%s %s) OA=%s spans=%d"
                  % (p["tag"], (r.get("title") or "")[:80], r.get("journal"), r.get("year"),
                     r.get("isOpenAccess"),
                     len(r.get("fulltext_quantitative_spans") or []) +
                     len(r.get("abstract_quantitative_spans") or [])), flush=True)
    return doc


if __name__ == "__main__":
    sys.exit(0 if run() else 0)
