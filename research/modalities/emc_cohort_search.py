#!/usr/bin/env python3
"""Is there a FOURTH EMC expression cohort anyone could read?

WHY THIS EXISTS. The transcriptional-output manuscript rests on three cohorts of 4, 6 and 10 EMC
tumours, and its Limitation 1 says so. Whether a fourth exists has been carried in the submission
checklist as an open "if one exists" for as long as that checklist has existed, which is a question
nobody had asked rather than an answer. This asks it, records every query including the ones that
return nothing, and produces a bounded statement either way.

⛔ THE GUARD IS THE DELIVERABLE AS MUCH AS THE SEARCH IS. A re-deposit of a cohort already in the
paper looks exactly like a new one. `GSE170983` is the worked example and it is not hypothetical:
99 samples, four of them EMC, its own accession, its own series record — and its `pubmed_ids` is
`22929540`, the Brunner et al. paper, making it the same deposit as **GSE28866**, which is already
this paper's 3SEQ arm, with the same four EMC samples. Counting it as a fourth cohort would have
double-counted an arm and inflated the paper's n. So every candidate is checked at THREE levels:

    1. accession        — is it one of the three already used, or a GDS VIEW of one?
    2. linked PubMed id — does it share a primary publication with one of them?
    3. sample identity  — do its GSMs overlap the ones already read?

Only a series that is new on all three, and carries at least MIN_EMC_SAMPLES samples naming EMC
AT SAMPLE LEVEL, counts as a fourth cohort.

⛔ AND A SERIES WITH NO SAMPLE-LEVEL READ IS UNGRADED, NEVER NEW. The first version of this module
declared `is_new_fourth_cohort` from a series whose GSM listing had never been fetched — an accession
that is new, a PMID that is new, and no sample evidence at all reads as a clean pass. That is an
absent reading rendered as a reading of absence, the failure this repository has recorded most often.
Grading is now three-state (`NEW_CANDIDATE` / `EXCLUDED` / `UNGRADED_NO_SAMPLE_LEVEL_READ`) and the
ungraded count is carried into the verdict, so "we could not look" can never be counted as "we looked
and it was fine".

⛔ WHAT A NEGATIVE HERE MEANS, AND WHAT IT DOES NOT. GEO's `esearch` matches depositor prose. A
series whose title and summary never say "extraskeletal myxoid chondrosarcoma" is invisible to every
query below however many EMC samples it contains, and EMC samples sitting inside a pan-sarcoma
deposit under a generic title are exactly the case that would be missed. So a null result bounds
what a term search over GEO can reach; it is not a statement that no fourth cohort exists.

REPRODUCTION
    python3 emc_cohort_search.py --fetch     # needs network (GitHub Actions; NCBI 403s in-sandbox)
    python3 emc_cohort_search.py             # re-derive the verdict from the cached inputs, offline
    python3 emc_cohort_search.py --check     # re-derive and diff against the committed artifact
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-cohort-search.json")
INPUTS = os.path.join(HERE, "emc-cohort-search-inputs.json")
FUSION_INPUTS = os.path.join(HERE, "nr4a3-fusion-targets-inputs.json")
BRUNNER_SERIES = os.path.join(HERE, "geo-gse28866-brunner-series.json")
BRUNNER_ACCESSION = "GSE28866"
# ⛔ THIS FILE HAS ITS OWN NAME BECAUSE THE SHARED ONE HELD TWO DIFFERENT SERIES AT DIFFERENT TIMES.
# Until 2026-08-27 the 3SEQ arm was read out of `atr-hrd-sarcoma-series.json`, whose producer
# (`atr_hrd_sarcoma_series.py`) declares `SERIES = "GSE299349"`. Committed history, not inference:
# 325258cb8 (2026-08-07) overwrote that filename with GSE28866 because the SAME workflow
# (`emc-expression-datasets.yml mode=gse-series`) writes a fixed path whatever series it is given;
# this module and its committed verdict were written on 2026-08-08 against that content; a8caba9
# (2026-08-27 04:37 UTC) re-fetched GSE299349 to repair PUB-ATR §8 and took the 3SEQ arm with it.
# `_known_gsms()` fell 157 -> 126, lost every GSE28866 GSM, and labelled 68 BCOR-rearranged sarcoma
# CELL-LINE samples as "the Brunner deposit". Two modules were each right about a filename that
# could only be right for one of them. The file named above holds 325258cb8's blob verbatim,
# fetched 2026-08-07T17:26:52Z by emc-expression-datasets.yml run 31200667719, and nothing but a
# GSE28866 fetch may ever be written to it.

sys.path.insert(0, HERE)

MIN_EMC_SAMPLES = 3          # below this no group contrast is computable at all
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# The cohorts the manuscript already reads, and the re-deposit that must not be mistaken for a new
# one. GSE170983 is listed as KNOWN precisely because it is the trap this module exists to catch.
KNOWN_COHORTS = {
    "GSE24369": "GPL6244 array arm of the manuscript (6 EMC vs 29 comparators)",
    "GSE4303": "GPL3290 array arm (10 EMC vs 6); the Subramanian 2005 cohort",
    # ⛔ NO `PMID <number>` PROSE IN HERE, AND THE OMISSION IS DELIBERATE. `lint_citations` treats a
    # tracked `.json` as a FETCH PRODUCT and counts any identifier in one as anchored — the whole
    # point being that a network read, a curation or a graph edit is something a model does not do
    # from memory. Hand-typing `PMID 22929540` into a dict that is then serialised into a generated
    # artifact smuggles a prose citation into that anchor set and silently promotes it, which is the
    # ledger-anchors-itself defect one level removed. The identifiers this module reasons about live
    # in `KNOWN_PMIDS` and in GEO's own `pubmed` field, both of which come back from the esummary
    # fetch recorded in the inputs cache. The human-readable label names the paper, not the number.
    "GSE28866": "3SEQ arm (4 EMC); the Brunner et al. lncRNA deposit",
    "GSE170983": "⛔ NOT a fourth cohort — the same Brunner deposit as GSE28866, the same linked "
                 "publication and the same four EMC samples, under a different accession",
}
KNOWN_PMIDS = {"22929540", "15920699", "21536545"}

# Datasets the repository already reads that a query returns and that are NOT EMC tumour cohorts.
# Naming them here rather than letting the floor throw them out silently: "excluded because 2 of its
# 4 samples name EMC" is true of GSE11185 and tells a reader nothing, while "HEK293 cells carrying a
# tet-inducible construct, already read, and not a tumour cohort at all" tells them everything.
KNOWN_NON_COHORT_DATASETS = {
    "GSE11185": "293 cells overexpressing NOR1 or EWS/NOR1 — a CELL-LINE construct experiment, not "
                "an EMC tumour cohort. Already read by `gse11185_wt_vs_fusion.py`.",
    "GDS3481": "the curated DataSet view of GSE11185, same four samples.",
}

# ⭐ THE POSITIVE CONTROL. A search that finds no fourth cohort is worth nothing unless the same
# queries recover the cohorts that DO exist — otherwise "we found nothing" and "the search is
# broken" are the same output. These three must come back, or the negative is withdrawn.
#
# ⭐ AND THE ARM SIZE IS CHECKED, NOT JUST THE ACCESSION, which turned out to be the stronger test.
# The counts below are the manuscript's own EMC arms. Recovering the accession only proves a query
# reached a deposit; recovering SIX EMC samples in GSE24369 by reading GEO sample titles — with no
# reference to the series matrix the manuscript actually scores — is an independent corroboration
# of the n the paper reports. If GEO ever returns a different count, either the deposit changed or
# this repository's copy is stale, and both are things a reader of the paper needs to know before
# the negative is quoted.
POSITIVE_CONTROLS = ["GSE24369", "GSE4303", "GSE28866"]
EXPECTED_EMC_ARM = {"GSE24369": 6, "GSE4303": 10, "GSE28866": 4}

# Deliberately overlapping. A query that returns nothing is indistinguishable from a dataset that
# does not exist, so several are run and every one is recorded — the discipline `discover_geo` in
# `emc_ret_cistrome.py` already uses for the ChIP-seq side of this lane.
GEO_QUERIES = [
    ('"extraskeletal myxoid chondrosarcoma"[All Fields]',
     "the disease name in full, the highest-precision term"),
    ('"myxoid chondrosarcoma"[All Fields] AND "expression profiling"[Filter]',
     "the shortened name, restricted to expression series"),
    ('(EWSR1 AND NR4A3) OR "EWS-NOR1" OR "EWSR1-NR4A3" OR "TAF15-NR4A3"',
     "the fusion rather than the disease — catches a deposit indexed by its driver"),
    ('NR4A3[All Fields] AND sarcoma[All Fields] AND "expression profiling"[Filter]',
     "the 3' partner plus lineage, for a pan-sarcoma deposit that names NR4A3 but not EMC"),
    ('"chondrosarcoma"[All Fields] AND "expression profiling"[Filter] AND "Homo sapiens"[Organism]',
     "deliberately over-broad: EMC samples inside a general chondrosarcoma series"),
    ('sarcoma[All Fields] AND "translocation"[All Fields] AND "expression profiling"[Filter]',
     "translocation-sarcoma panels, the kind of deposit EMC hides inside"),
]

# TWO TOKEN SETS, AND THE DIFFERENCE BETWEEN THEM IS A DIRECTION OF ERROR.
#
# `EMC_TOKENS` screens series prose IN. Over-breadth there is safe: the cost of a false positive is
# one extra candidate that the sample-level checks then throw out, and the cost of a false negative
# is a cohort nobody ever looks at again. So it accepts a bare `NR4A3` or a bare `EMC`.
#
# `EMC_SAMPLE_TOKENS` counts how many SAMPLES are EMC, and that number is what a series has to clear
# to be called a fourth cohort — so over-breadth there is fail-OPEN and inflates a series into
# qualifying. A pan-sarcoma deposit that writes "NR4A3 status: negative" on every sample would score
# every sample as EMC under the loose set. It therefore takes only the disease name and the fusion,
# both of which appear verbatim in the real EMC sample titles of both cohorts already used
# ("Extraskeletal myxoid chondrosarcoma 1" on GSE24369, "STT3699-Myxoid Chondrosarcoma" on GSE4303).
EMC_TOKENS = re.compile(
    r"extraskeletal myxoid chondrosarcoma|myxoid chondrosarcoma|\bEMC\b|EWSR1[-:/ ]?NR4A3|"
    r"EWS[-/ ]?NOR-?1|TAF15[-:/ ]?NR4A3|NR4A3|NOR-?1\b", re.I)
# An E-utilities field RESTRICTION — `[Filter]`, `[All Fields]`, `[Organism]` — and nothing else.
# ⚠ It matches the bracket only, never the phrase in front of it. An earlier version swallowed the
# search term with its restriction, which turns `"myxoid chondrosarcoma"[All Fields] AND
# "expression profiling"[Filter]` into the empty string: a probe that asks GEO nothing, gets nothing
# back, and reads as confirmation that the original zero was real. The probe has to ask the SAME
# question with the restrictions lifted, or it is not a control.
FIELD_TOKEN = re.compile(r"\[[A-Za-z ]+\]")

EMC_SAMPLE_TOKENS = re.compile(
    r"extraskeletal myxoid chondrosarcoma|myxoid chondrosarcoma|EWSR1[-:/ ]?NR4A3|"
    r"EWS[-/ ]?NOR-?1|TAF15[-:/ ]?NR4A3", re.I)


def _r(x, nd=4):
    return None if x is None else round(x, nd)


def _strip_field_tokens(term):
    """The same question with the E-utilities field restrictions lifted, and nothing else changed."""
    s = FIELD_TOKEN.sub("", term)
    s = re.sub(r"\s+AND\s+(?=AND\s|$)", " ", s)
    s = re.sub(r"^\s*AND\s+|\s+AND\s*$", "", s)
    return re.sub(r"\s{2,}", " ", s).strip()


# =================================================================================================
# FETCH — the only half that needs a network
# =================================================================================================
def fetch():
    import urllib.request
    import time

    def get_json(url, tries=3):
        for i in range(tries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
                with urllib.request.urlopen(req, timeout=90) as r:
                    return json.loads(r.read().decode("utf-8", "replace"))
            except Exception as exc:                       # noqa: BLE001
                if i == tries - 1:
                    return {"_error": f"{type(exc).__name__}: {exc}"[:200]}
                time.sleep(2 * (i + 1))
        return None

    def esearch(term):
        q = urllib.parse.urlencode({"db": "gds", "retmax": "80", "retmode": "json", "term": term})
        es = get_json(f"{EUTILS}/esearch.fcgi?{q}")
        if not es or "_error" in (es or {}):
            return None, (es or {}).get("_error")
        r = es.get("esearchresult") or {}
        return r.get("idlist") or [], int(r.get("count") or 0)

    out = {"_generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "queries": [], "series": {}, "series_samples": {}}
    seen = {}
    for term, why in GEO_QUERIES:
        ids, count = esearch(term)
        rec = {"term": term, "why": why}
        if ids is None:
            rec["_status"] = "failed"
            rec["error"] = count
            ids = []
        else:
            rec["_status"] = "read"
            rec["count_reported_by_geo"] = count
            rec["n_ids_returned"] = len(ids)
        time.sleep(0.4)

        # ⛔ A ZERO FROM A MALFORMED QUERY IS NOT A NEGATIVE, AND THE TWO ARE THE SAME LENGTH.
        # Measured on the first real run: four of six queries returned EXACTLY zero, and all four
        # shared an `"expression profiling"[Filter]` clause that the two returning 17 and 5 records
        # did not have — including `"chondrosarcoma" AND "expression profiling" AND "Homo sapiens"`,
        # a query GEO cannot honestly answer with nothing. Recorded as `read, 0 results`, a broken
        # query is indistinguishable from a genuine absence, and four silently broken queries would
        # have made "six queries, no fourth cohort" a far stronger claim than the evidence supports.
        # So a zero-returning query with a bracketed field token is re-asked with those tokens
        # stripped. If the stripped form returns records, the original is a SYNTAX failure and says
        # so; the stripped form's records are the ones used, because a query that reaches GEO is
        # worth more than one that parses cleanly and reaches nothing.
        if not ids and rec["_status"] == "read" and FIELD_TOKEN.search(term):
            stripped = _strip_field_tokens(term)
            sids, scount = esearch(stripped)
            rec["zero_return_probe"] = {
                "_why": ("a zero and a malformed query are the same length; this asks the same "
                         "question with the field tokens removed"),
                "stripped_term": stripped,
                "_status": "failed" if sids is None else "read",
                "count_reported_by_geo": scount if sids is not None else None,
                "n_ids_returned": len(sids or []),
            }
            if sids:
                rec["_status"] = "read_after_syntax_repair"
                rec["⛔ original_query_returned_zero"] = (
                    "the field tokens in the original term matched nothing in db=gds; the stripped "
                    "term returned records, so the original zero was a SYNTAX result and is not "
                    "reported as an absence")
                rec["n_ids_returned"] = len(sids)
                ids = sids
            time.sleep(0.4)
        out["queries"].append(rec)
        if not ids:
            continue
        su = get_json(f"{EUTILS}/esummary.fcgi?db=gds&retmode=json&id={','.join(ids)}")
        for uid, r in ((su or {}).get("result") or {}).items():
            if uid == "uids" or not isinstance(r, dict):
                continue
            acc = r.get("accession")
            if not acc or acc in seen:
                continue
            seen[acc] = True
            out["series"][acc] = {
                "accession": acc, "title": r.get("title"), "gdsType": r.get("gdsType"),
                "taxon": r.get("taxon"), "n_samples": r.get("n_samples"),
                "gpl": r.get("GPL"), "pubmed": r.get("PubMedIds"),
                "summary": (r.get("summary") or "")[:1200],
                # ⛔ BOTH OF THESE ARE DEDUP FIELDS, NOT DESCRIPTION. `db=gds` returns curated
                # DataSet (GDS) records ALONGSIDE the series they are built from, and a GDS carries
                # its own accession — so a GDS assembled from GSE4303 arrives looking like a brand
                # new deposit under a brand new number. `entrytype` says which kind of record this
                # is and the `GSE` field names the parent series, which is the only thing that can
                # unmask it. This is the GSE170983 trap in a second costume.
                "entrytype": r.get("entryType") or r.get("entrytype"),
                "parent_gse": (f"GSE{r.get('GSE')}" if r.get("GSE") else None),
                "_found_by": term,
                "⚠": "title and summary are the depositors' CLAIM, not a measurement",
            }
        time.sleep(0.4)

    # Sample-level identity for every candidate that could plausibly be a cohort. This is what
    # catches a re-deposit; an accession and a PMID can both differ while the samples are identical.
    # ⛔ EVERY GSE, NOT ONLY THE ONES WHOSE PROSE NAMES EMC. The first version gated this on the
    # prose screen, and the first real run showed why that is wrong: GEO returned `GSE43632` ("Large
    # scale screening for fusion genes in sarcoma patient samples") and `GSE80126` from queries that
    # name EWSR1/NR4A3 — so GEO matched them on SOMETHING — while the title and the 1200 characters
    # of summary this module captures name no EMC token. Excluding them as "does not name EMC" would
    # have been an artifact of that truncation, in exactly the case the docstring warns about: EMC
    # samples inside a pan-sarcoma deposit under a generic title. There are tens of series here, not
    # thousands, so the honest thing is to read them all at sample level and let the samples decide.
    for acc, s in sorted(out["series"].items()):
        if not str(acc).startswith("GSE"):
            continue
        # GSM listing via the series' own esummary relation is unreliable; use esearch over gsm.
        q2 = urllib.parse.urlencode({"db": "gds", "retmax": "400", "retmode": "json",
                                     "term": f"{acc}[GSE] AND gsm[ETYP]"})
        es = get_json(f"{EUTILS}/esearch.fcgi?{q2}")
        ids = ((es or {}).get("esearchresult") or {}).get("idlist") or []
        gsms = []
        if ids:
            su = get_json(f"{EUTILS}/esummary.fcgi?db=gds&retmode=json&id={','.join(ids[:400])}")
            for uid, r in ((su or {}).get("result") or {}).items():
                if uid == "uids" or not isinstance(r, dict):
                    continue
                a = r.get("accession")
                if a and str(a).startswith("GSM"):
                    gsms.append({"gsm": a, "title": r.get("title"),
                                 "summary": (r.get("summary") or "")[:300]})
        out["series_samples"][acc] = {"n_gsm_read": len(gsms), "samples": gsms}
        time.sleep(0.4)
    return out


# =================================================================================================
# DERIVE — offline, from the cached inputs
# =================================================================================================
def _known_gsms():
    """Every GSM the manuscript's cohorts actually read, plus the GSE170983 re-deposit's EMC ids."""
    out = {}
    with open(FUSION_INPUTS) as fh:
        d = json.load(fh)
    for plat, t in (d.get("targets") or {}).items():
        acc = "GSE24369" if "GSE24369" in plat else "GSE4303"
        for s in t.get("samples") or []:
            out[s["gsm"]] = acc
    # ⛔ REFUSE, NEVER DEGRADE. This half used to be wrapped in `if os.path.exists(...)` and to
    # take the series identifier out of whatever it found, so a file that was absent, empty or
    # about a DIFFERENT series produced a smaller map and no complaint — and a smaller map means
    # every sample-overlap check passes and the third dedup level is silently gone. That is the
    # failure this module's own docstring calls an absent reading rendered as a reading of absence,
    # and it happened: see BRUNNER_SERIES above. A guard that can quietly stop guarding is not one.
    if not os.path.exists(BRUNNER_SERIES):
        raise RuntimeError(
            f"{os.path.basename(BRUNNER_SERIES)} is missing. It carries the {BRUNNER_ACCESSION} "
            "3SEQ arm, which is dedup level 3 for the GSE170983 re-deposit. Without it a "
            "re-deposit of an arm this paper already reads grades NEW_CANDIDATE. Restore it "
            "rather than letting the search run.")
    with open(BRUNNER_SERIES) as fh:
        a = json.load(fh)
    series = a.get("series")
    if series != BRUNNER_ACCESSION:
        raise RuntimeError(
            f"{os.path.basename(BRUNNER_SERIES)} holds series {series!r}, not "
            f"{BRUNNER_ACCESSION!r}. Some other series' samples would be labelled as the Brunner "
            "deposit and counted as already-read EMC tumours. Refusing.")
    for s in (a.get("samples") or []):
        g = s.get("gsm") or s.get("accession")
        if g:
            out.setdefault(g, f"{series} = GSE170983, the Brunner deposit (the 3SEQ arm)")
    return out


def derive(inp):
    known_gsms = _known_gsms()
    res = {
        "_what": __doc__.strip().splitlines()[0],
        "_language_discipline": (
            "A search result is not a cohort and a cohort is not a result. Nothing here is an "
            "efficacy, selectivity, safety or clinical-readiness claim, and no expression value is "
            "computed in this module."),
        "_what_a_negative_bounds": (
            "GEO esearch matches DEPOSITOR PROSE. A series whose title and summary never name EMC "
            "is invisible to every query here however many EMC samples it holds. A null result "
            "bounds what a term search over GEO can reach; it is NOT a statement that no fourth "
            "cohort exists."),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_inputs_generated_utc": inp.get("_generated_utc"),
        "known_cohorts": KNOWN_COHORTS,
        "n_known_gsms": len(known_gsms),
        "queries": inp.get("queries") or [],
        "candidates": {},
    }
    n_read = sum(1 for q in res["queries"]
                 if q.get("_status") in ("read", "read_after_syntax_repair"))
    repaired = [q["term"] for q in res["queries"]
                if q.get("_status") == "read_after_syntax_repair"]
    # A query that returned zero, was re-asked without its field restrictions, and returned zero
    # AGAIN. That is the only kind of zero this module is willing to read as an absence.
    zero_confirmed = [q["term"] for q in res["queries"]
                      if q.get("_status") == "read" and not q.get("n_ids_returned")
                      and (q.get("zero_return_probe") or {}).get("_status") == "read"]
    zero_unprobed = [q["term"] for q in res["queries"]
                     if q.get("_status") == "read" and not q.get("n_ids_returned")
                     and not q.get("zero_return_probe")]
    res["query_summary"] = {
        "n_queries": len(res["queries"]), "n_read": n_read,
        "n_failed": len(res["queries"]) - n_read,
        "n_distinct_series_returned": len(inp.get("series") or {}),
        "queries_repaired_after_a_syntax_zero": repaired,
        "zeros_confirmed_by_an_unrestricted_reask": zero_confirmed,
        "zeros_never_probed": zero_unprobed,
        "_why_zeros_are_probed": (
            "measured 2026-08-08: four of six queries returned EXACTLY zero and all four shared an "
            "`\"expression profiling\"[Filter]` clause the two returning 17 and 5 records lacked — "
            "including a chondrosarcoma query GEO cannot honestly answer with nothing. A zero and a "
            "malformed query are the same length, and four silently broken queries would have made "
            "'six queries, no fourth cohort' a far stronger claim than the evidence supports."),
        "_why_every_query_is_recorded": ("a query that returns nothing is indistinguishable from a "
                                         "dataset that does not exist unless the query itself is "
                                         "on the record"),
    }

    for acc, s in sorted((inp.get("series") or {}).items()):
        blob = f"{s.get('title') or ''} {s.get('summary') or ''}"
        names_emc = bool(EMC_TOKENS.search(blob))
        samp = (inp.get("series_samples") or {}).get(acc) or {}
        gsms = [x.get("gsm") for x in (samp.get("samples") or []) if x.get("gsm")]
        overlap = sorted(g for g in gsms if g in known_gsms)
        emc_samples = [x for x in (samp.get("samples") or [])
                       if EMC_SAMPLE_TOKENS.search(
                           f"{x.get('title') or ''} {x.get('summary') or ''}")]
        pmids = [str(p) for p in (s.get("pubmed") or [])]
        shared_pmid = sorted(set(pmids) & KNOWN_PMIDS)
        parent = s.get("parent_gse")

        # ⛔ RECORD TYPE FIRST, BECAUSE MOST OF WHAT `db=gds` RETURNS IS NOT A SERIES AT ALL. The
        # first real run returned 22 "candidates" of which ten were individual GSM sample records
        # and one was a GPL platform record — and six of those GSMs were GSE24369's own EMC samples,
        # sitting in the ungraded list while `_known_gsms` held every one of their accessions. A
        # single sample is not a cohort under any reading, and a platform is not a deposit; grading
        # them as if they might be buried the ONE record that genuinely needed a decision.
        kind = (s.get("entrytype") or ("GSM" if str(acc).startswith("GSM")
                else "GPL" if str(acc).startswith("GPL")
                else "GDS" if str(acc).startswith("GDS") else "GSE"))

        reasons = []
        if kind == "GSM":
            owner = known_gsms.get(acc)
            reasons.append(
                f"a single SAMPLE record, not a cohort" +
                (f" — and it is one this manuscript already reads, from {owner}" if owner else ""))
        elif kind == "GPL":
            reasons.append("a platform record, not a deposit")
        if acc in KNOWN_NON_COHORT_DATASETS:
            reasons.append(KNOWN_NON_COHORT_DATASETS[acc])
        if acc in KNOWN_COHORTS:
            reasons.append(f"accession already used: {KNOWN_COHORTS[acc]}")
        if parent and parent in KNOWN_COHORTS and parent != acc:
            reasons.append(f"a curated view of {parent}, which is already used: "
                           f"{KNOWN_COHORTS[parent]}")
        if shared_pmid:
            reasons.append(f"shares a primary publication with a cohort already used: {shared_pmid}")
        if overlap:
            reasons.append(f"{len(overlap)} sample(s) already read by an existing cohort "
                           f"(e.g. {overlap[:4]})")
        if not names_emc and not samp:
            reasons.append("neither title nor summary names EMC, NR4A3 or the fusion, and no "
                           "sample-level read contradicted that")
        elif samp and len(emc_samples) < MIN_EMC_SAMPLES:
            reasons.append(f"{len(emc_samples)} sample(s) name EMC at sample level; "
                           f"floor is {MIN_EMC_SAMPLES}")

        # ⛔ THREE STATES, AND THE THIRD IS THE POINT. A series that named EMC in prose but whose
        # GSM listing was never read cannot be excluded — and must not be promoted. It is UNGRADED,
        # it is counted as such in the verdict, and it is named there so the next look starts from
        # a list rather than from this module's silence.
        graded_at_sample_level = bool(samp) and samp.get("n_gsm_read")
        if reasons:
            state = "EXCLUDED"
        elif graded_at_sample_level:
            state = "NEW_CANDIDATE"
        else:
            state = "UNGRADED_NO_SAMPLE_LEVEL_READ"

        res["candidates"][acc] = {
            "title": s.get("title"), "n_samples": s.get("n_samples"), "gpl": s.get("gpl"),
            "pubmed": pmids, "found_by": s.get("_found_by"),
            "entrytype": s.get("entrytype"), "parent_gse": parent,
            "names_emc_in_prose": names_emc,
            "n_gsm_read": samp.get("n_gsm_read"),
            "n_samples_naming_emc": len(emc_samples) if graded_at_sample_level else None,
            "n_gsm_overlapping_a_known_cohort": len(overlap),
            "gsm_overlap_examples": overlap[:6],
            "grade": state,
            "is_new_fourth_cohort": state == "NEW_CANDIDATE",
            "excluded_because": reasons or None,
        }

    # ⭐ THE POSITIVE CONTROL, AND IT IS REPORTED BEFORE THE VERDICT. "No fourth cohort exists" and
    # "this search does not work" produce the same empty list, and the only thing that separates
    # them is whether the same queries recovered the cohorts that DO exist.
    recovered = [a for a in POSITIVE_CONTROLS if a in res["candidates"]]
    missed = [a for a in POSITIVE_CONTROLS if a not in res["candidates"]]
    arms, arm_disagreements = {}, []
    for a in recovered:
        got = res["candidates"][a].get("n_samples_naming_emc")
        want = EXPECTED_EMC_ARM.get(a)
        arms[a] = {"emc_samples_found_in_geo_sample_titles": got,
                   "emc_arm_the_manuscript_reports": want,
                   "agree": got == want}
        if got is not None and got != want:
            arm_disagreements.append(f"{a}: GEO sample titles give {got}, the manuscript reads "
                                     f"{want}")
    res["positive_control"] = {
        "_why": ("a null result from an instrument that recovers no known positive is not a "
                 "negative, it is a broken search"),
        "cohorts_the_manuscript_reads": POSITIVE_CONTROLS,
        "recovered_by_these_queries": recovered,
        "not_recovered": missed,
        "emc_arm_sizes": arms,
        "arm_size_disagreements": arm_disagreements or None,
        "passes": not missed and not arm_disagreements,
        "_note": ("each is recovered and then EXCLUDED by the dedup, which is the intended path: "
                  "recovery proves the queries reach EMC deposits, exclusion proves the guard "
                  "recognises the ones already used"),
        "_arm_note": ("the arm sizes are read from GEO SAMPLE TITLES here and from the series "
                      "MATRIX in nr4a3_fusion_targets.py — two independent paths to the same "
                      "number, which is why agreement is worth recording"),
    }

    new = sorted(a for a, c in res["candidates"].items() if c["grade"] == "NEW_CANDIDATE")
    ungraded = sorted(a for a, c in res["candidates"].items()
                      if c["grade"] == "UNGRADED_NO_SAMPLE_LEVEL_READ")
    res["verdict"] = {
        "positive_control_passes": res["positive_control"]["passes"],
        "n_candidates_examined": len(res["candidates"]),
        "n_naming_emc_in_prose": sum(1 for c in res["candidates"].values()
                                     if c["names_emc_in_prose"]),
        "new_fourth_cohorts": new,
        "ungraded_no_sample_level_read": ungraded,
        # ⛔ THE HEADLINE KEYS ON THE WHOLE POSITIVE CONTROL, NOT JUST ON RECOVERY. The first
        # version keyed on `missed` alone, so an arm-size disagreement set `passes: False` in one
        # field and printed a clean negative in the next — a guard that noticed and did not act,
        # which is worth less than no guard because it reads as reassurance. Whatever fails the
        # control withholds the negative.
        "headline": (
            ("No fourth EMC expression cohort was found. Every series any query returned is either "
             "already used by the manuscript, shares a publication or samples with one, is not a "
             "series at all, or carries too few EMC samples to contrast."
             if res["positive_control"]["passes"] else
             "WITHHELD — this search did not clear its own positive control, so a null from it is "
             "uninterpretable. " + "; ".join(
                 ([f"cohorts not recovered: {missed}"] if missed else []) +
                 (arm_disagreements or [])) + ".")
            if not new else
            f"{len(new)} candidate fourth cohort(s) survived every dedup check: {new}. Each needs "
            "characterising at sample level before any number is read from it."),
        "⛔ scope": res["_what_a_negative_bounds"],
    }
    if zero_unprobed:
        res["verdict"]["⚠ unprobed zeros"] = (
            f"{len(zero_unprobed)} quer{'y' if len(zero_unprobed) == 1 else 'ies'} returned zero "
            "and carried no field restriction to lift, so the zero could not be cross-checked: " +
            "; ".join(zero_unprobed))
    if ungraded:
        res["verdict"]["⚠ incomplete"] = (
            f"{len(ungraded)} series named EMC in prose and could not be read at sample level, so "
            "they are neither excluded nor counted: " + ", ".join(ungraded) + ". The headline above "
            "is a statement about what WAS graded.")
    return res


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items()
                if k not in ("generated_utc", "_generated_utc")}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="run the GEO queries (needs network)")
    ap.add_argument("--check", action="store_true", help="re-derive and diff; do not write")
    args = ap.parse_args()

    if args.fetch:
        inp = fetch()
        with open(INPUTS, "w") as fh:
            json.dump(inp, fh, indent=1, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        print(f"cohort-search: fetched {len(inp.get('series') or {})} series across "
              f"{len(inp.get('queries') or [])} queries")

    if not os.path.exists(INPUTS):
        print("cohort-search: no cached inputs; run with --fetch on a networked runner")
        return 1
    with open(INPUTS) as fh:
        inp = json.load(fh)
    res = derive(inp)

    if args.check:
        if not os.path.exists(OUT):
            print("cohort-search --check: artifact does not exist yet")
            return 1
        with open(OUT) as fh:
            have = json.load(fh)
        if _strip(have) == _strip(res):
            print("cohort-search --check: OK -- artifact is current")
            return 0
        print("cohort-search --check: DRIFT -- re-run without --check")
        return 1

    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    v = res["verdict"]
    print(f"cohort-search: wrote {os.path.basename(OUT)}")
    print(f"  queries {res['query_summary']['n_read']}/{res['query_summary']['n_queries']} read | "
          f"series returned {res['query_summary']['n_distinct_series_returned']} | "
          f"naming EMC {v['n_naming_emc_in_prose']}")
    print(f"  new fourth cohorts: {v['new_fourth_cohorts'] or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
