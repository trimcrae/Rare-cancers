#!/usr/bin/env python3
"""Is there EMC-bearing public molecular data that a DEPOSITOR-PROSE search cannot see?

⭐ WHY THIS EXISTS, AND WHY IT IS NOT A RE-RUN OF `emc_cohort_search.py`.

That module asked GEO for a fourth EMC expression cohort and returned a bounded negative. Its own
header states the bound, and the bound is the opening this module walks through, verbatim:

    "GEO's `esearch` matches depositor prose. A series whose title and summary never say
    'extraskeletal myxoid chondrosarcoma' is invisible to every query below however many EMC
    samples it contains, and EMC samples sitting inside a pan-sarcoma deposit under a generic
    title are exactly the case that would be missed."

⛔ THAT CASE IS NOT HYPOTHETICAL AND THIS REPOSITORY HAS ALREADY BEEN BITTEN BY IT. The docstring of
`atr_hrd_sarcoma_series.py` records that **GSE24369 is titled "low-grade fibromyxoid sarcoma" and
silently contains six EMC tumours** — a third of the EMC samples the transcriptional-output
manuscript reads, sitting in a deposit whose title names a different disease. Every EMC count this
repository holds came from a prose search that could only have found that series by accident.

So the question here is the complement of the cohort search's, and no query in this repository has
ever asked it: **what carries EMC that a prose search structurally cannot reach?** Two arms, chosen
because each searches something other than what a depositor wrote:

  ARM 1 · SNAPTRON / recount3 — search the DATA, not the description.
      Snaptron indexes exon-exon junctions from uniformly reprocessed public RNA-seq (the `srav3h`
      compilation is drawn from the SRA arm of recount3). A junction is a property of the reads. A
      sample whose depositor never typed "EMC" still contributes its junctions, so a query over the
      junction index is blind to the prose and therefore reaches exactly the population the cohort
      search could not. This module does NOT claim a fusion is detectable this way — that is the
      thing it is measuring, and §PROBE below says what would have to be true.

  ARM 2 · A PAN-SARCOMA METHYLATION DEPOSIT — a named deposit in the blind spot.
      GSE140686 is the reference set of Koelsche et al., Nat Commun 2021;12:498, "Sarcoma
      classification by DNA methylation profiling". Its title names no disease, and extraskeletal
      myxoid chondrosarcoma is one of the tumour methylation classes the classifier was trained on.
      It is therefore the textbook instance of the missed case: a pan-sarcoma deposit under a
      generic title. This repository holds ZERO methylation data of any kind for this disease.

⛔ WHAT THIS MODULE MAY AND MAY NOT CONCLUDE.

  * It reports what each endpoint SERVED and what the served record CONTAINS. It grades nothing
    biological. No expression, methylation, fusion, efficacy, selectivity, safety, therapeutic-window
    or clinical-readiness claim is made or implied, and none is derivable from this artifact.
  * A sample counted here is a METADATA MATCH, never a diagnosis. `n_samples_naming_emc` counts
    records whose own text names the disease; it is a claim by the depositor exactly as a series
    title is, and it is reported as such.
  * ⛔ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). Every fetch records its HTTP
    outcome. An arm whose endpoint did not answer is `UNREACHABLE`, never `NOTHING_THERE`, and
    `derive()` refuses to emit a verdict for an arm whose inputs did not arrive.
  * ⛔ AND A ZERO IS NOT A RESULT UNTIL THE TRANSPORT IS PROVEN. Each arm carries a KNOWN-ANSWER
    TRANSPORT CONTROL that must return records, and an ABSENT CONTROL that must return none. If the
    known control comes back empty the arm is `TRANSPORT_FAILED` and its zero is withheld, because a
    null from an instrument that recovers no known positive is a broken search, not a negative.

★ PROBE FIRST, INSTRUMENT SECOND — deliberately, and this is the whole scope of the first run.
  Arm 1's design question is not answerable from documentation and must not be answered from
  recollection: does this junction index carry the junction classes a fusion transcript would
  produce, and in what fields. A chimeric junction joining two chromosomes and an intragenic
  junction inside NR4A3 are different objects, and only one of them is certain to be in a splice
  index at all. So this run MEASURES the served columns, the record counts and the coordinate span,
  and emits `arm_state: PROBED_NOT_SEARCHED` for arm 1. The searchable design is written against
  that measurement, never ahead of it.

REPRODUCTION
    python3 emc_data_level_sweep.py --selftest   # offline arithmetic + guard assertions, no network
    python3 emc_data_level_sweep.py --fetch      # CI only (the dev sandbox egress proxy 403s both hosts)
    python3 emc_data_level_sweep.py              # re-derive the verdict from the cached inputs, offline
    python3 emc_data_level_sweep.py --check      # re-derive and diff against the committed artifact
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-data-level-sweep.json")
INPUTS = os.path.join(HERE, "emc-data-level-sweep-inputs.json")

UA = "rare-cancers-emc-data-level-sweep/1.0 (research; contact via repository)"

# ── ARM 1 · Snaptron ────────────────────────────────────────────────────────────────────────────
# Compilations are TRIED, never assumed. A name that 404s is recorded as such; this repository does
# not get to decide what the service hosts.
SNAPTRON_HOST = "https://snaptron.cs.jhu.edu"
SNAPTRON_COMPILATIONS = ["srav3h", "gtexv2", "tcgav2"]

# The gene the disease is defined by, its two commonest 5' partners, and the third partner that is
# NOT a FET protein. Partner frequencies are the Mod Pathol 2023 (PMID 36948401) distribution the
# roadmap already carries; they are not restated as numbers here (CLAUDE.md §1).
SNAPTRON_TARGETS = ["NR4A3", "EWSR1", "TAF15", "TCF12"]

# ⛔ THE TWO CONTROLS. Neither is optional and neither is decoration.
#   transport — a ubiquitously expressed gene with a dense, well-known junction structure. If this
#               returns nothing the endpoint is not answering and every zero below is meaningless.
#   absent    — a symbol that is not an HGNC gene. If this returns records the service is matching
#               something other than what we asked for, and the target reads cannot be trusted.
SNAPTRON_TRANSPORT_CONTROL = "GAPDH"
SNAPTRON_ABSENT_CONTROL = "ZZZNOTAGENE9"

# ── ARM 2 · the pan-sarcoma methylation deposit ─────────────────────────────────────────────────
GEO_SERIES = "GSE140686"
GEO_ACC_CGI = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
# The EBI mirror of the same study. A SECOND ROUTE, not a second dataset: it exists so that "NCBI
# did not answer" and "this data is not public" stay distinguishable.
ARRAYEXPRESS_ACC = "E-MTAB-9875"
ARRAYEXPRESS_API = "https://www.ebi.ac.uk/biostudies/api/v1/studies/"

# Disease name and the abbreviations a per-sample characteristics field actually uses. Matched
# case-insensitively against sample text; every hit is reported with the sample it came from.
EMC_TERMS = [
    "extraskeletal myxoid chondrosarcoma",
    "extra-skeletal myxoid chondrosarcoma",
    "extraskeletal myxoid chondros",
    "myxoid chondrosarcoma",
    "NR4A3",
    "EWSR1-NR4A3",
    "EWSR1::NR4A3",
    "EWS-NOR1",
    "CHON, EXTRASKEL",
]
# Deliberately separate: a match on one of these is EMC-ADJACENT and must not be summed with the
# list above. Skeletal myxoid chondrosarcoma is a DIFFERENT tumour with a different driver, and a
# substring search for "myxoid chondrosarcoma" hits both.
EMC_CONFUSABLE_TERMS = ["skeletal myxoid chondrosarcoma", "chondrosarcoma, skeletal"]


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get(url, timeout=120, tries=3, note=""):
    """One fetch. Returns (body_or_None, record). The record is the evidence, not a log line."""
    rec = {"url": url, "note": note, "http": None, "error": None, "bytes": 0, "elapsed_s": None}
    t0 = time.time()
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                rec["http"] = r.status
                rec["bytes"] = len(body)
                rec["elapsed_s"] = round(time.time() - t0, 2)
                return body.decode("utf-8", "replace"), rec
        except urllib.error.HTTPError as e:
            rec["http"] = e.code
            rec["error"] = f"HTTPError {e.code}"
            if e.code in (400, 404, 410):
                break          # a real answer: the resource is not there. Do not retry it.
        except Exception as e:                                     # noqa: BLE001
            rec["error"] = f"{type(e).__name__}: {e}"
        if attempt < tries:
            time.sleep(2 * attempt)
    rec["elapsed_s"] = round(time.time() - t0, 2)
    return None, rec


# ────────────────────────────────────────────────────────────────────────────────────────────────
# ARM 1 — the junction index
# ────────────────────────────────────────────────────────────────────────────────────────────────

def _snaptron_url(compilation, region):
    return f"{SNAPTRON_HOST}/{compilation}/snaptron?regions={urllib.parse.quote(region)}"


def parse_snaptron(body):
    """Parse a Snaptron TSV stream into a SHAPE description. No biology, only structure.

    Snaptron returns a TAB-delimited stream whose first line is a header. We do not assume any
    column name: the header we were SERVED is recorded verbatim and every derived field says which
    served column it came from, so a service-side rename shows up as a missing column rather than as
    a silently wrong number.
    """
    lines = [ln for ln in body.split("\n") if ln.strip()]
    if not lines:
        return {"n_lines": 0, "header": None, "columns": [], "n_records": 0,
                "records_sample": [], "chromosomes": {}, "note": "empty body"}
    header = lines[0]
    cols = header.lstrip("#").split("\t")
    recs = [ln.split("\t") for ln in lines[1:]]
    idx = {c: i for i, c in enumerate(cols)}

    def col(r, name):
        i = idx.get(name)
        if i is None or i >= len(r):
            return None
        return r[i]

    chrom_counts = {}
    for r in recs:
        c = col(r, "chromosome")
        if c is not None:
            chrom_counts[c] = chrom_counts.get(c, 0) + 1

    return {
        "n_lines": len(lines),
        "header": header[:2000],
        "columns": cols,
        "n_records": len(recs),
        # A bounded verbatim sample. Enough to see the shape, never enough to be a dataset.
        "records_sample": ["\t".join(r)[:600] for r in recs[:5]],
        "chromosomes": chrom_counts,
        "has_chromosome_column": "chromosome" in idx,
        "has_samples_count_column": "samples_count" in idx,
        "has_annotated_column": "annotated" in idx,
    }


def fetch_snaptron():
    out = {"host": SNAPTRON_HOST, "compilations_tried": SNAPTRON_COMPILATIONS,
           "reachability": {}, "queries": {}, "controls": {}}

    # Reachability is asked ONCE per compilation with the transport control, so a compilation that
    # does not exist is separated from a target that has no records in one that does.
    live = []
    for comp in SNAPTRON_COMPILATIONS:
        body, rec = _get(_snaptron_url(comp, SNAPTRON_TRANSPORT_CONTROL), timeout=180,
                         note=f"transport control in {comp}")
        shape = parse_snaptron(body) if body is not None else None
        out["reachability"][comp] = {"fetch": rec,
                                     "shape": shape,
                                     "answers": bool(body is not None and shape
                                                     and shape["n_records"] > 0)}
        if out["reachability"][comp]["answers"]:
            live.append(comp)
    out["compilations_that_answered"] = live

    if not live:
        out["arm_state"] = "UNREACHABLE"
        return out

    comp = live[0]
    out["compilation_used"] = comp

    body, rec = _get(_snaptron_url(comp, SNAPTRON_ABSENT_CONTROL), timeout=120,
                     note="absent control — must return no records")
    out["controls"]["absent"] = {"fetch": rec,
                                 "shape": parse_snaptron(body) if body is not None else None}
    out["controls"]["transport"] = {"compilation": comp,
                                    "shape": out["reachability"][comp]["shape"]}

    for g in SNAPTRON_TARGETS:
        body, rec = _get(_snaptron_url(comp, g), timeout=300, note=f"target gene {g}")
        out["queries"][g] = {"fetch": rec,
                             "shape": parse_snaptron(body) if body is not None else None}
        time.sleep(1)

    out["arm_state"] = "FETCHED"
    return out


# ────────────────────────────────────────────────────────────────────────────────────────────────
# ARM 2 — the pan-sarcoma methylation deposit
# ────────────────────────────────────────────────────────────────────────────────────────────────

def fetch_methylation():
    out = {"series": GEO_SERIES, "arrayexpress": ARRAYEXPRESS_ACC, "fetches": {}}

    # `targ=self` is the series header alone — small, and it carries the platform, the sample count
    # and the supplementary-file listing. `targ=all` is every sample record in one stream, which is
    # where the per-sample disease labels live and is the only place a pan-sarcoma deposit says
    # which of its samples is which.
    q_self = f"{GEO_ACC_CGI}?acc={GEO_SERIES}&targ=self&form=text&view=brief"
    body, rec = _get(q_self, timeout=180, note="GEO series header")
    out["fetches"]["geo_self"] = rec
    out["geo_self_text"] = body[:200000] if body else None

    q_all = f"{GEO_ACC_CGI}?acc={GEO_SERIES}&targ=all&form=text&view=brief"
    body_all, rec_all = _get(q_all, timeout=600, note="GEO series + every sample record")
    out["fetches"]["geo_all"] = rec_all
    # Bounded: 1,500 brief sample records is a few MB. The cap is recorded so a truncation can never
    # read as a short deposit.
    CAP = 12_000_000
    if body_all is not None:
        out["geo_all_truncated"] = len(body_all) > CAP
        out["geo_all_text"] = body_all[:CAP]
    else:
        out["geo_all_truncated"] = None
        out["geo_all_text"] = None

    # SECOND ROUTE, not a second dataset — see the constant's comment.
    body_ae, rec_ae = _get(ARRAYEXPRESS_API + ARRAYEXPRESS_ACC, timeout=180,
                           note="EBI BioStudies mirror of the same study")
    out["fetches"]["arrayexpress"] = rec_ae
    out["arrayexpress_text"] = body_ae[:400000] if body_ae else None

    out["arm_state"] = "FETCHED" if body is not None or body_all is not None else "UNREACHABLE"
    return out


def _split_geo_samples(txt):
    """Split a GEO `targ=all&view=brief` stream into per-sample blobs keyed by GSM."""
    if not txt:
        return {}
    blobs, cur, key = {}, [], None
    for line in txt.split("\n"):
        if line.startswith("^SAMPLE"):
            if key:
                blobs[key] = "\n".join(cur)
            key = line.split("=", 1)[-1].strip()
            cur = [line]
        elif key:
            cur.append(line)
    if key:
        blobs[key] = "\n".join(cur)
    return blobs


def _term_hits(text, terms):
    low = (text or "").lower()
    return [t for t in terms if t.lower() in low]


# ────────────────────────────────────────────────────────────────────────────────────────────────
# DERIVE
# ────────────────────────────────────────────────────────────────────────────────────────────────

def derive(inp):
    res = {
        "_generated_utc": _now(),
        "_inputs_generated_utc": inp.get("_generated_utc"),
        "_question": ("Is there EMC-bearing public molecular data that a depositor-prose search "
                      "cannot see? `emc_cohort_search.py` bounded its own negative to prose; this "
                      "asks what lies outside that bound."),
        "_language_discipline": ("Nothing here is an efficacy, selectivity, safety, "
                                 "therapeutic-window or clinical-readiness claim. A sample counted "
                                 "here is a metadata match, never a diagnosis."),
        "arms": {},
    }

    # ── ARM 1 ───────────────────────────────────────────────────────────────────────────────────
    s = inp.get("snaptron") or {}
    arm1 = {"_what": ("Does the public splice-junction index answer at all, and does what it serves "
                      "carry the fields a fusion-junction search would need?"),
            "state": s.get("arm_state", "NOT_RUN")}
    if s.get("arm_state") == "FETCHED":
        transport = ((s.get("controls", {}).get("transport") or {}).get("shape") or {})
        absent = ((s.get("controls", {}).get("absent") or {}).get("shape") or {})
        t_n = transport.get("n_records", 0)
        a_n = absent.get("n_records", 0)
        arm1["transport_control_records"] = t_n
        arm1["absent_control_records"] = a_n
        arm1["controls_pass"] = bool(t_n > 0 and a_n == 0)
        arm1["compilation_used"] = s.get("compilation_used")
        arm1["compilations_that_answered"] = s.get("compilations_that_answered", [])
        arm1["served_columns"] = transport.get("columns", [])
        per = {}
        for g, q in (s.get("queries") or {}).items():
            shape = q.get("shape") or {}
            per[g] = {
                "http": (q.get("fetch") or {}).get("http"),
                "n_records": shape.get("n_records") if q.get("shape") else None,
                "chromosomes": shape.get("chromosomes") if q.get("shape") else None,
                "readable": q.get("shape") is not None,
            }
        arm1["per_gene"] = per
        if not arm1["controls_pass"]:
            arm1["verdict"] = "TRANSPORT_FAILED"
            arm1["⛔"] = ("The known-answer control did not behave. Every count in `per_gene` is "
                          "withheld from interpretation: a null from an instrument that recovers no "
                          "known positive is a broken search, not a negative.")
        else:
            arm1["verdict"] = "PROBED_NOT_SEARCHED"
            arm1["what_this_settles"] = ("that the index answers, which compilation answers, and "
                                          "which columns it serves — the inputs a fusion-junction "
                                          "search has to be designed against.")
            arm1["what_this_does_not_settle"] = ("whether any EMC sample is in there. No fusion "
                                                  "search has been run and none is claimed.")
    elif s.get("arm_state") == "UNREACHABLE":
        arm1["verdict"] = "UNREACHABLE"
        arm1["⛔"] = ("No compilation answered. That is a statement about this fetch, not about the "
                      "service and not about the data (CLAUDE.md §4).")
    else:
        arm1["verdict"] = "NOT_RUN"
    res["arms"]["snaptron_junction_index"] = arm1

    # ── ARM 2 ───────────────────────────────────────────────────────────────────────────────────
    m = inp.get("methylation") or {}
    arm2 = {"_what": (f"Does {GEO_SERIES} — a pan-sarcoma deposit whose title names no disease — "
                      "carry EMC samples, and are they open?"),
            "state": m.get("arm_state", "NOT_RUN"),
            "series": GEO_SERIES}
    if m.get("arm_state") == "FETCHED":
        head = m.get("geo_self_text") or ""
        allt = m.get("geo_all_text") or ""
        arm2["series_title"] = next(
            (ln.split("=", 1)[-1].strip() for ln in head.split("\n")
             if ln.startswith("!Series_title")), None)
        arm2["platforms"] = sorted(set(
            re.findall(r"!Series_platform_id\s*=\s*(GPL\d+)", head)
            or re.findall(r"(GPL\d+)", head)))
        blobs = _split_geo_samples(allt)
        arm2["n_samples_read"] = len(blobs)
        arm2["n_samples_declared_by_series"] = len(
            re.findall(r"!Series_sample_id\s*=\s*GSM\d+", head)) or None

        emc, confusable = {}, {}
        for gsm, txt in blobs.items():
            h = _term_hits(txt, EMC_TERMS)
            c = _term_hits(txt, EMC_CONFUSABLE_TERMS)
            if h:
                emc[gsm] = h
            if c:
                confusable[gsm] = c
        arm2["n_samples_naming_emc"] = len(emc)
        arm2["n_samples_naming_a_confusable"] = len(confusable)
        arm2["emc_samples_sample"] = dict(list(emc.items())[:15])
        arm2["⚠ counting_rule"] = ("`n_samples_naming_emc` counts per-sample records whose OWN text "
                                    "matches a disease term. It is a depositor claim exactly as a "
                                    "series title is, and the confusable count is reported "
                                    "separately because a substring search for 'myxoid "
                                    "chondrosarcoma' also hits the skeletal tumour, which is a "
                                    "different disease with a different driver.")

        ae = m.get("arrayexpress_text")
        arm2["mirror_reachable"] = ae is not None
        arm2["mirror_http"] = ((m.get("fetches") or {}).get("arrayexpress") or {}).get("http")

        if not blobs:
            arm2["verdict"] = "SAMPLE_LEVEL_NOT_READ"
            arm2["⛔"] = ("The series header arrived but no per-sample record did, so the EMC count "
                          "is unmeasured. Absent reading, not a reading of absence.")
        elif len(emc) > 0:
            arm2["verdict"] = "EMC_SAMPLES_PRESENT_IN_A_PROSE_INVISIBLE_DEPOSIT"
        else:
            arm2["verdict"] = "NO_SAMPLE_NAMES_EMC"
            arm2["⚠"] = ("Read at sample level and no record names the disease. That bounds what "
                          "these sample records say — a deposit can label by methylation class code "
                          "rather than by disease name, and this arm cannot see such a label.")
    elif m.get("arm_state") == "UNREACHABLE":
        arm2["verdict"] = "UNREACHABLE"
    else:
        arm2["verdict"] = "NOT_RUN"
    res["arms"]["pan_sarcoma_methylation_deposit"] = arm2

    res["headline"] = _headline(arm1, arm2)
    return res


def _headline(arm1, arm2):
    bits = []
    v1 = arm1.get("verdict")
    if v1 == "PROBED_NOT_SEARCHED":
        bits.append(f"junction index answers ({arm1.get('compilation_used')}); no fusion search run yet")
    elif v1:
        bits.append(f"junction index: {v1}")
    v2 = arm2.get("verdict")
    if v2 == "EMC_SAMPLES_PRESENT_IN_A_PROSE_INVISIBLE_DEPOSIT":
        bits.append(f"{arm2.get('n_samples_naming_emc')} EMC-naming samples in {arm2.get('series')}")
    elif v2:
        bits.append(f"{arm2.get('series')}: {v2}")
    return "; ".join(bits) if bits else "nothing run"


# ────────────────────────────────────────────────────────────────────────────────────────────────
# SELFTEST — the guards, asserted offline, BEFORE one byte is fetched
# ────────────────────────────────────────────────────────────────────────────────────────────────

def selftest():
    fails = []

    def ck(cond, msg):
        if not cond:
            fails.append(msg)

    # 1 · An empty cache may never emit a biological verdict.
    empty = derive({})
    ck(empty["arms"]["snaptron_junction_index"]["verdict"] == "NOT_RUN",
       "an empty cache produced a snaptron verdict other than NOT_RUN")
    ck(empty["arms"]["pan_sarcoma_methylation_deposit"]["verdict"] == "NOT_RUN",
       "an empty cache produced a methylation verdict other than NOT_RUN")

    # 2 · A failed transport control WITHHOLDS the target counts rather than reporting them.
    broken = {"snaptron": {"arm_state": "FETCHED", "compilation_used": "srav3h",
                           "compilations_that_answered": ["srav3h"],
                           "controls": {"transport": {"shape": {"n_records": 0, "columns": []}},
                                        "absent": {"shape": {"n_records": 0}}},
                           "queries": {"NR4A3": {"fetch": {"http": 200},
                                                 "shape": {"n_records": 999,
                                                           "chromosomes": {"chr9": 999}}}}}}
    d = derive(broken)["arms"]["snaptron_junction_index"]
    ck(d["verdict"] == "TRANSPORT_FAILED",
       "a dead transport control did not produce TRANSPORT_FAILED")
    ck(d["controls_pass"] is False, "controls_pass was true with zero transport records")

    # 3 · An absent control that RETURNS records also fails the arm.
    leaky = json.loads(json.dumps(broken))
    leaky["snaptron"]["controls"]["transport"]["shape"]["n_records"] = 500
    leaky["snaptron"]["controls"]["absent"]["shape"]["n_records"] = 7
    ck(derive(leaky)["arms"]["snaptron_junction_index"]["verdict"] == "TRANSPORT_FAILED",
       "an absent control returning records did not fail the arm")

    # 4 · A clean pair of controls yields PROBED_NOT_SEARCHED and NEVER a search verdict.
    clean = json.loads(json.dumps(broken))
    clean["snaptron"]["controls"]["transport"]["shape"]["n_records"] = 500
    clean["snaptron"]["controls"]["absent"]["shape"]["n_records"] = 0
    v = derive(clean)["arms"]["snaptron_junction_index"]["verdict"]
    ck(v == "PROBED_NOT_SEARCHED", f"clean controls gave {v}, expected PROBED_NOT_SEARCHED")

    # 5 · A series header with NO sample records is SAMPLE_LEVEL_NOT_READ, never "no EMC".
    hdr_only = {"methylation": {"arm_state": "FETCHED",
                                "geo_self_text": "!Series_title = Sarcoma classification\n",
                                "geo_all_text": "", "fetches": {}}}
    ck(derive(hdr_only)["arms"]["pan_sarcoma_methylation_deposit"]["verdict"]
       == "SAMPLE_LEVEL_NOT_READ",
       "a header-only read reported a sample-level answer")

    # 6 · The confusable term must NOT be counted as EMC.
    only_skeletal = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                                     "geo_all_text": ("^SAMPLE = GSM1\n!Sample_title = "
                                                      "skeletal myxoid chondrosarcoma case 1\n"),
                                     "fetches": {}}}
    a = derive(only_skeletal)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a["n_samples_naming_a_confusable"] == 1,
       "the skeletal confusable was not counted in its own bucket")
    # It also matches "myxoid chondrosarcoma" as a substring, which is exactly why the two buckets
    # exist and are reported side by side rather than summed.
    ck("myxoid chondrosarcoma" in a["emc_samples_sample"].get("GSM1", []),
       "the substring overlap between the two buckets stopped being visible")

    # 7 · The sample splitter must key on GSM and not merge records.
    two = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                           "geo_all_text": ("^SAMPLE = GSM1\n!Sample_title = extraskeletal myxoid "
                                            "chondrosarcoma\n^SAMPLE = GSM2\n!Sample_title = "
                                            "leiomyosarcoma\n"),
                           "fetches": {}}}
    a2 = derive(two)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a2["n_samples_read"] == 2, f"splitter read {a2['n_samples_read']} samples, expected 2")
    ck(a2["n_samples_naming_emc"] == 1,
       f"EMC count was {a2['n_samples_naming_emc']}, expected 1")

    # 8 · The Snaptron TSV parser must not invent columns it was not served.
    shape = parse_snaptron("DataSource:Type\tsnaptron_id\tchromosome\tstart\tend\n"
                           "srav3h:I\t1\tchr9\t100\t200\n"
                           "srav3h:I\t2\tchr9\t300\t400\n")
    ck(shape["n_records"] == 2, "parser miscounted records")
    ck(shape["has_chromosome_column"] is True, "parser lost a served column")
    ck(shape["has_samples_count_column"] is False,
       "parser reported a column it was never served")
    ck(shape["chromosomes"] == {"chr9": 2}, f"chromosome tally wrong: {shape['chromosomes']}")

    if fails:
        print("SELFTEST FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"selftest ok ({8} guard groups)")
    return 0


# ────────────────────────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="retrieve both arms and write the inputs cache (needs network; CI)")
    ap.add_argument("--check", action="store_true",
                    help="re-derive from the cached inputs and diff against the committed artifact")
    ap.add_argument("--selftest", action="store_true",
                    help="offline guard assertions; runs before any fetch")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.fetch:
        inp = {"_generated_utc": _now(),
               "_what": "raw retrieval only; every verdict is computed in derive()",
               "snaptron": fetch_snaptron(),
               "methylation": fetch_methylation()}
        with open(INPUTS, "w") as fh:
            json.dump(inp, fh, indent=1, sort_keys=True)
        print(f"wrote {INPUTS}")
    else:
        if not os.path.exists(INPUTS):
            print(f"no inputs cache at {INPUTS}; run --fetch (CI) first", file=sys.stderr)
            return 2
        with open(INPUTS) as fh:
            inp = json.load(fh)

    res = derive(inp)

    if args.check:
        if not os.path.exists(OUT):
            print(f"no committed artifact at {OUT} to check against", file=sys.stderr)
            return 2
        with open(OUT) as fh:
            old = json.load(fh)
        a = json.dumps({k: v for k, v in old.items() if not k.startswith("_generated")},
                       sort_keys=True)
        b = json.dumps({k: v for k, v in res.items() if not k.startswith("_generated")},
                       sort_keys=True)
        if a != b:
            print("DRIFT: the committed artifact does not re-derive from its own inputs cache")
            return 1
        print("check ok: artifact re-derives from its inputs")
        return 0

    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(f"wrote {OUT}")
    print(json.dumps({"headline": res["headline"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
