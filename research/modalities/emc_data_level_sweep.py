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

# ⛔ THE POSITIVE CONTROL FOR THE SEARCH, AND WITHOUT IT THE SEARCH MAY NOT REPORT.
# The signature this instrument looks for is 5' DEPLETION: in a sample where a gene's 3' half is
# transcribed from a partner's promoter, the gene's own 5'-most junctions carry ~no coverage while
# its downstream junctions carry plenty. That is a property of the ARCHITECTURE, not of EMC, so it
# is testable on a disease whose samples are certainly in this compilation.
#   FLI1  — in Ewing sarcoma the FLI1 3' half is driven from the EWSR1 promoter. Public Ewing
#           RNA-seq is abundant, so if the signature is detectable at all it is detectable here.
#   GAPDH — a gene with no recurrent 5'-truncating fusion. It must NOT produce a pile of hits, or
#           the score is measuring depth and annotation sparsity rather than truncation.
# If FLI1 yields nothing the arm reports SIGNATURE_NOT_DEMONSTRATED and every NR4A3 count is
# withheld: a null from an instrument that recovers no known positive is a broken search.
SNAPTRON_SIGNATURE_POSITIVE = "FLI1"
SNAPTRON_SIGNATURE_NEGATIVE = "GAPDH"

# A sample must carry at least this much coverage on the gene's DOWNSTREAM annotated junctions
# before its 5' end is worth calling depleted. Below it, "no 5' coverage" is indistinguishable from
# "this sample barely expresses the gene at all", which is the dominant confound.
MIN_DOWNSTREAM_COVERAGE = 20
# The 5' fraction of the gene's annotated junctions treated as the "5' end" for the ratio.
FIVE_PRIME_FRACTION = 0.34
# A candidate carries at most this share of its junction coverage on the 5' end.
MAX_FIVE_PRIME_SHARE = 0.02

# ── ARM 2 · the pan-sarcoma methylation deposit ─────────────────────────────────────────────────
GEO_SERIES = "GSE140686"
GEO_ACC_CGI = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
# The EBI mirror of the same study. A SECOND ROUTE, not a second dataset: it exists so that "NCBI
# did not answer" and "this data is not public" stay distinguishable.
ARRAYEXPRESS_ACC = "E-MTAB-9875"
ARRAYEXPRESS_API = "https://www.ebi.ac.uk/biostudies/api/v1/studies/"

# ⛔ WHY THE ARTICLE IS FETCHED AT ALL, AND IT IS THE FINDING OF THE FIRST RUN.
# All 1,505 sample records in the deposit are titled "sarcoma classifier reference case N" with
# characteristics "tissue: sarcoma" and nothing else -- the strings EMC, chondrosarcoma, myxoid and
# NR4A3 appear ZERO times across the whole stream. The repository is fully readable and simply does
# not state which case is which, so "no sample names EMC" was a statement about the LABELS, not about
# the samples. The per-case diagnoses are published with the paper. This stage goes and gets them.
# ⚠ THE SUPPLEMENTARY URLS ARE DISCOVERED, NEVER TYPED. A guessed MOESM number that 404s and a
# supplement that does not exist are the same length, and this repository does not write identifiers
# from recollection (CLAUDE.md §7). The article page is parsed for its own links.
GEO_ARTICLE_URL = "https://www.nature.com/articles/s41467-020-20603-4"
SUPPL_HOST_HINT = "static-content.springer.com"
MAX_SUPPL_FILES = 8
MAX_SUPPL_BYTES = 40_000_000

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

    n_annot = sum(1 for r in recs if col(r, "annotated") == "1")
    return {
        "n_lines": len(lines),
        "header": header[:2000],
        "columns": cols,
        "n_records": len(recs),
        "n_annotated": n_annot,
        # A bounded verbatim sample. Enough to see the shape, never enough to be a dataset.
        "records_sample": ["\t".join(r)[:600] for r in recs[:5]],
        "chromosomes": chrom_counts,
        "has_chromosome_column": "chromosome" in idx,
        "has_samples_count_column": "samples_count" in idx,
        "has_annotated_column": "annotated" in idx,
    }


def five_prime_depletion(body):
    """Per-sample 5'-depletion profile over ONE gene's annotated junctions.

    ⛔ WHAT THIS MEASURES, STATED BEFORE THE ARITHMETIC. A junction record carries the samples it
    was seen in and the coverage in each. So for one gene we can rebuild, per sample, how its
    junction coverage is distributed along the gene. A sample whose coverage sits entirely on the
    DOWNSTREAM junctions and not at all on the 5'-most ones is a sample in which that gene's 3' half
    is being transcribed while its own 5' end is not.

    ⛔ WHAT IT IS NOT. That pattern is CONSISTENT WITH a 5'-truncating rearrangement; it does not
    identify one, does not name a partner, and is not a diagnosis. An alternative promoter, 3' bias
    in a degraded library, or a poorly-annotated 5' end all produce it too. The output is a
    CANDIDATE LIST for orthogonal checking, and it is labelled that way in the artifact.

    ⚠ STRAND IS DERIVED, NEVER ASSUMED. "5'-most" is the lowest coordinate on the plus strand and
    the highest on the minus strand, and getting it backwards silently inverts the whole result. The
    strand is taken as the majority strand of the gene's ANNOTATED junctions and is reported.
    """
    lines = [ln for ln in body.split("\n") if ln.strip()]
    if len(lines) < 2:
        return {"usable": False, "why": "no records"}
    cols = lines[0].lstrip("#").split("\t")
    idx = {c: i for i, c in enumerate(cols)}
    need = ("chromosome", "start", "end", "strand", "annotated", "samples")
    missing = [c for c in need if c not in idx]
    if missing:
        return {"usable": False, "why": f"served columns lack {missing}"}

    annotated = []
    for ln in lines[1:]:
        r = ln.split("\t")
        if len(r) <= max(idx.values()):
            continue
        if r[idx["annotated"]] != "1":
            continue
        annotated.append(r)
    if len(annotated) < 6:
        return {"usable": False, "why": f"only {len(annotated)} annotated junctions; too few to split"}

    strands = {}
    for r in annotated:
        s = r[idx["strand"]]
        strands[s] = strands.get(s, 0) + 1
    strand = max(strands, key=strands.get)
    annotated = [r for r in annotated if r[idx["strand"]] == strand]

    # Order along the transcript: ascending coordinate on +, descending on -.
    annotated.sort(key=lambda r: int(r[idx["start"]]), reverse=(strand == "-"))
    k = max(1, int(len(annotated) * FIVE_PRIME_FRACTION))
    five, rest = annotated[:k], annotated[k:]

    def accumulate(rows):
        per = {}
        for r in rows:
            for tok in r[idx["samples"]].split(","):
                if not tok or ":" not in tok:
                    continue
                sid, _, cov = tok.partition(":")
                try:
                    per[sid] = per.get(sid, 0.0) + float(cov)
                except ValueError:
                    continue
        return per

    cov5, cov3 = accumulate(five), accumulate(rest)
    candidates = []
    for sid, down in cov3.items():
        if down < MIN_DOWNSTREAM_COVERAGE:
            continue
        up = cov5.get(sid, 0.0)
        share = up / (up + down)
        if share <= MAX_FIVE_PRIME_SHARE:
            candidates.append({"rail_id": sid, "five_prime_cov": round(up, 1),
                               "downstream_cov": round(down, 1), "five_prime_share": round(share, 5)})
    candidates.sort(key=lambda c: -c["downstream_cov"])
    n_expressing = sum(1 for s, d in cov3.items() if d >= MIN_DOWNSTREAM_COVERAGE)
    return {
        "usable": True,
        "strand_derived": strand,
        "strand_vote": strands,
        "n_annotated_junctions": len(annotated),
        "n_five_prime_junctions": len(five),
        "n_samples_expressing_downstream": n_expressing,
        "n_candidates": len(candidates),
        "candidate_rate": round(len(candidates) / n_expressing, 5) if n_expressing else None,
        "candidates_top": candidates[:40],
        "thresholds": {"min_downstream_coverage": MIN_DOWNSTREAM_COVERAGE,
                       "five_prime_fraction": FIVE_PRIME_FRACTION,
                       "max_five_prime_share": MAX_FIVE_PRIME_SHARE},
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

    # The search runs on the targets AND on both controls, from the same fetch, so the control and
    # the target are never scored by different code paths.
    genes = list(dict.fromkeys(
        SNAPTRON_TARGETS + [SNAPTRON_SIGNATURE_POSITIVE, SNAPTRON_SIGNATURE_NEGATIVE]))
    out["search_genes"] = genes
    out["signature_positive"] = SNAPTRON_SIGNATURE_POSITIVE
    out["signature_negative"] = SNAPTRON_SIGNATURE_NEGATIVE
    for g in genes:
        body, rec = _get(_snaptron_url(comp, g), timeout=600, note=f"gene {g}")
        out["queries"][g] = {
            "fetch": rec,
            "shape": parse_snaptron(body) if body is not None else None,
            "depletion": five_prime_depletion(body) if body is not None else None,
        }
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

    # ── the per-case diagnosis table, which is what actually decides this arm ────────────────────
    art, rec_art = _get(GEO_ARTICLE_URL, timeout=180, note="article page, for its supplementary links")
    out["fetches"]["article"] = rec_art
    links, suppl = [], {}
    if art:
        for m in re.finditer(r'href="(https?://[^"]*%s[^"]*)"' % re.escape(SUPPL_HOST_HINT), art):
            u = m.group(1).replace("&amp;", "&")
            if u not in links:
                links.append(u)
    out["supplementary_links_found"] = links[:40]
    for u in links[:MAX_SUPPL_FILES]:
        raw, rec_s = _get(u, timeout=300, note="supplementary file")
        entry = {"fetch": rec_s, "parsed": None, "parse_error": None}
        if raw is not None and rec_s.get("bytes", 0) <= MAX_SUPPL_BYTES:
            entry["parsed"] = _parse_supplementary(u, raw)
        elif raw is not None:
            entry["parse_error"] = f"over the {MAX_SUPPL_BYTES}-byte cap; not parsed"
        suppl[u] = entry
        time.sleep(1)
    out["supplementary"] = suppl

    out["arm_state"] = "FETCHED" if body is not None or body_all is not None else "UNREACHABLE"
    return out


def _parse_supplementary(url, raw):
    """Pull disease-term evidence out of one supplementary file, whatever format it arrived in.

    ⛔ REPORTS WHAT IT COULD READ, SEPARATELY FROM WHAT IT FOUND. A binary this parser cannot open
    is `readable: false` with the reason, never "contains no EMC" -- that distinction is the whole
    reason the first run's zero did not close this route.
    """
    low = url.lower()
    res = {"url": url, "kind": None, "readable": False, "why": None,
           "n_rows_scanned": 0, "emc_rows": [], "n_emc_rows": 0, "confusable_rows": 0}
    try:
        if low.endswith((".xlsx", ".xls")):
            res["kind"] = "spreadsheet"
            try:
                import openpyxl                                        # noqa: PLC0415
            except ImportError as exc:                                 # pragma: no cover
                res["why"] = f"openpyxl unavailable ({exc}); NOT a statement about the file"
                return res
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as fh:
                fh.write(raw.encode("utf-8", "surrogateescape") if isinstance(raw, str) else raw)
                tmp = fh.name
            wb = openpyxl.load_workbook(tmp, read_only=True, data_only=True)
            rows = []
            for ws in wb.worksheets:
                for r in ws.iter_rows(values_only=True):
                    rows.append(" | ".join("" if c is None else str(c) for c in r))
                    if len(rows) > 40000:
                        break
            res["readable"] = True
            res["n_rows_scanned"] = len(rows)
        else:
            res["kind"] = "text"
            rows = (raw if isinstance(raw, str) else raw.decode("utf-8", "replace")).split("\n")
            res["readable"] = True
            res["n_rows_scanned"] = len(rows)
    except Exception as exc:                                           # noqa: BLE001
        res["why"] = f"{type(exc).__name__}: {exc} -- NOT a statement about the file's contents"
        return res

    for line in rows:
        hits = _term_hits(line, EMC_TERMS)
        if _term_hits(line, EMC_CONFUSABLE_TERMS):
            res["confusable_rows"] += 1
        if hits:
            res["n_emc_rows"] += 1
            if len(res["emc_rows"]) < 25:
                res["emc_rows"].append(line[:300])
    return res


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
            arm1.update(_depletion_verdict(s))
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

        # ── the supplementary table, which is where the diagnoses actually live ─────────────────
        sup = m.get("supplementary") or {}
        parsed = [(u, e.get("parsed")) for u, e in sup.items() if e.get("parsed")]
        readable = [(u, d) for u, d in parsed if d.get("readable")]
        arm2["supplementary_files_fetched"] = len(sup)
        arm2["supplementary_files_readable"] = len(readable)
        arm2["supplementary_unreadable"] = [
            {"url": u, "why": d.get("why")} for u, d in parsed if not d.get("readable")]
        sup_emc = sum(d.get("n_emc_rows", 0) for _, d in readable)
        arm2["supplementary_emc_rows"] = sup_emc
        arm2["supplementary_confusable_rows"] = sum(
            d.get("confusable_rows", 0) for _, d in readable)
        arm2["supplementary_emc_rows_sample"] = [
            r for _, d in readable for r in d.get("emc_rows", [])][:20]

        if not blobs:
            arm2["verdict"] = "SAMPLE_LEVEL_NOT_READ"
            arm2["⛔"] = ("The series header arrived but no per-sample record did, so the EMC count "
                          "is unmeasured. Absent reading, not a reading of absence.")
        elif len(emc) > 0:
            arm2["verdict"] = "EMC_SAMPLES_PRESENT_IN_A_PROSE_INVISIBLE_DEPOSIT"
        elif sup_emc > 0:
            arm2["verdict"] = "EMC_IN_THE_PUBLISHED_TABLE_NOT_IN_THE_DEPOSIT_LABELS"
            arm2["⭐"] = ("The deposit's own sample records name no disease, and the published "
                          "supplementary table does. The samples are therefore labelled — just not "
                          "in the repository — and the join is what makes this cohort usable. "
                          "⚠ A row naming the disease is not yet a sample count: mapping rows to "
                          "the deposit's cases is the step after this one.")
        elif readable:
            arm2["verdict"] = "NO_EMC_ROW_IN_A_READABLE_SUPPLEMENT"
            arm2["⚠"] = ("Sample records name no disease AND the supplementary files that could be "
                          "read carry no row naming it. That is a real negative for what was read "
                          "— it is not a claim about files that could not be parsed, which are "
                          "listed in `supplementary_unreadable`.")
        else:
            arm2["verdict"] = "LABELS_NOT_LOCATED"
            arm2["⛔"] = ("Every one of the deposit's sample records is present and none names a "
                          "disease, and no supplementary file could be read. Where the per-case "
                          "diagnoses live is therefore still unmeasured. This is the state in which "
                          "reporting 'no EMC samples' would close a live route on a label that was "
                          "never read.")
    elif m.get("arm_state") == "UNREACHABLE":
        arm2["verdict"] = "UNREACHABLE"
    else:
        arm2["verdict"] = "NOT_RUN"
    res["arms"]["pan_sarcoma_methylation_deposit"] = arm2

    res["headline"] = _headline(arm1, arm2)
    return res


def _depletion_verdict(s):
    """Grade the 5'-depletion search, and REFUSE to report the target if the controls do not hold."""
    q = s.get("queries") or {}
    pos_name = s.get("signature_positive", SNAPTRON_SIGNATURE_POSITIVE)
    neg_name = s.get("signature_negative", SNAPTRON_SIGNATURE_NEGATIVE)

    def dep(g):
        return ((q.get(g) or {}).get("depletion") or {})

    out = {"search": {}, "signature_positive": pos_name, "signature_negative": neg_name}
    for g, rec in q.items():
        d = rec.get("depletion") or {}
        out["search"][g] = {
            "usable": d.get("usable", False),
            "why_unusable": d.get("why"),
            "strand_derived": d.get("strand_derived"),
            "n_annotated_junctions": d.get("n_annotated_junctions"),
            "n_samples_expressing_downstream": d.get("n_samples_expressing_downstream"),
            "n_candidates": d.get("n_candidates"),
            "candidate_rate": d.get("candidate_rate"),
        }

    pos, neg = dep(pos_name), dep(neg_name)
    if not pos.get("usable"):
        out["verdict"] = "SIGNATURE_NOT_DEMONSTRATED"
        out["⛔"] = (f"The positive control ({pos_name}) could not be scored: "
                     f"{pos.get('why', 'no reason recorded')}. Every target count above is "
                     "WITHHELD from interpretation — a search that cannot be shown to detect a "
                     "signature it is known to contain reports nothing about a gene where the "
                     "answer is unknown.")
        return out

    pos_n = pos.get("n_candidates", 0)
    pos_rate = pos.get("candidate_rate")
    neg_rate = neg.get("candidate_rate") if neg.get("usable") else None
    out["positive_control_candidates"] = pos_n
    out["positive_control_rate"] = pos_rate
    out["negative_control_rate"] = neg_rate

    if pos_n == 0:
        out["verdict"] = "SIGNATURE_NOT_DEMONSTRATED"
        out["⛔"] = (f"{pos_name} is scoreable but yielded ZERO candidates. The signature this "
                     "instrument looks for was not recovered where it is known to exist, so the "
                     "instrument has not been shown to work and no target count may be read.")
        return out

    if neg_rate is not None and pos_rate is not None and neg_rate >= pos_rate:
        out["verdict"] = "SPECIFICITY_NOT_DEMONSTRATED"
        out["⛔"] = (f"The negative control ({neg_name}) produces candidates at least as often as "
                     f"the positive one ({neg_rate} vs {pos_rate}), so the score is tracking "
                     "expression depth or annotation sparsity rather than 5' truncation. Target "
                     "counts are WITHHELD.")
        return out

    out["verdict"] = "SEARCHED"
    tgt = dep("NR4A3")
    out["nr4a3_candidates"] = tgt.get("n_candidates") if tgt.get("usable") else None
    out["nr4a3_candidates_top"] = tgt.get("candidates_top", [])[:20] if tgt.get("usable") else None
    out["⚠ what_a_candidate_is"] = (
        "a public sample in which this gene's downstream junction coverage is substantial while its "
        "5'-most junctions carry essentially none. That is CONSISTENT WITH a 5'-truncating "
        "rearrangement and is not one: an alternative promoter, 3' bias in a degraded library, or a "
        "poorly annotated 5' end produce the same pattern. It is a candidate list for orthogonal "
        "checking, never a detection and never a diagnosis.")
    return out


def _headline(arm1, arm2):
    bits = []
    v1 = arm1.get("verdict")
    if v1 == "SEARCHED":
        bits.append(f"junction search ran; NR4A3 5'-depleted candidates: {arm1.get('nr4a3_candidates')}")
    elif v1 == "PROBED_NOT_SEARCHED":
        bits.append(f"junction index answers ({arm1.get('compilation_used')}); no fusion search run yet")
    elif v1:
        bits.append(f"junction index: {v1}")
    v2 = arm2.get("verdict")
    if v2 == "EMC_SAMPLES_PRESENT_IN_A_PROSE_INVISIBLE_DEPOSIT":
        bits.append(f"{arm2.get('n_samples_naming_emc')} EMC-naming samples in {arm2.get('series')}")
    elif v2 == "EMC_IN_THE_PUBLISHED_TABLE_NOT_IN_THE_DEPOSIT_LABELS":
        bits.append(f"{arm2.get('series')}: labels are in the paper, not the deposit — "
                    f"{arm2.get('supplementary_emc_rows')} EMC row(s) found")
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

    # 4 · ⛔ CLEAN TRANSPORT CONTROLS ARE NOT ENOUGH TO REPORT A TARGET, and this is the guard that
    #     stops the two control layers being confused. The transport pair only proves the ENDPOINT
    #     answers. Whether the SEARCH can see the signature is a separate question with its own
    #     control, so a fetch that answered cleanly but carries no depletion payload must still
    #     withhold every target count.
    clean = json.loads(json.dumps(broken))
    clean["snaptron"]["controls"]["transport"]["shape"]["n_records"] = 500
    clean["snaptron"]["controls"]["absent"]["shape"]["n_records"] = 0
    a4 = derive(clean)["arms"]["snaptron_junction_index"]
    ck(a4["verdict"] == "SIGNATURE_NOT_DEMONSTRATED",
       f"clean transport controls alone gave {a4['verdict']}; the search control must still gate")
    ck("nr4a3_candidates" not in a4,
       "a target count was reported on transport controls alone")

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

    # 9 · The depletion search must REFUSE to report a target when the positive control is dead.
    def _snap(pos_cands, neg_cands, tgt_cands, pos_usable=True):
        def mk(n, usable=True, expr=1000):
            return {"usable": usable, "why": None if usable else "too few annotated junctions",
                    "n_candidates": n, "n_samples_expressing_downstream": expr,
                    "candidate_rate": (n / expr) if (usable and expr) else None,
                    "candidates_top": [], "n_annotated_junctions": 40, "strand_derived": "+"}
        return {"snaptron": {
            "arm_state": "FETCHED", "compilation_used": "srav3h",
            "compilations_that_answered": ["srav3h"],
            "signature_positive": "FLI1", "signature_negative": "GAPDH",
            "controls": {"transport": {"shape": {"n_records": 500, "columns": []}},
                         "absent": {"shape": {"n_records": 0}}},
            "queries": {"FLI1": {"fetch": {"http": 200}, "shape": {"n_records": 9},
                                 "depletion": mk(pos_cands, pos_usable)},
                        "GAPDH": {"fetch": {"http": 200}, "shape": {"n_records": 9},
                                  "depletion": mk(neg_cands)},
                        "NR4A3": {"fetch": {"http": 200}, "shape": {"n_records": 9},
                                  "depletion": mk(tgt_cands)}}}}

    a = derive(_snap(0, 1, 12))["arms"]["snaptron_junction_index"]
    ck(a["verdict"] == "SIGNATURE_NOT_DEMONSTRATED",
       f"a positive control with zero candidates gave {a['verdict']}")
    ck("nr4a3_candidates" not in a, "target counts were reported despite a dead positive control")

    a = derive(_snap(5, 1, 12, pos_usable=False))["arms"]["snaptron_junction_index"]
    ck(a["verdict"] == "SIGNATURE_NOT_DEMONSTRATED",
       "an unscoreable positive control did not withhold the target")

    a = derive(_snap(30, 60, 12))["arms"]["snaptron_junction_index"]
    ck(a["verdict"] == "SPECIFICITY_NOT_DEMONSTRATED",
       f"a negative control firing more than the positive gave {a['verdict']}")
    ck("nr4a3_candidates" not in a, "target counts survived a failed specificity check")

    a = derive(_snap(30, 2, 12))["arms"]["snaptron_junction_index"]
    ck(a["verdict"] == "SEARCHED", f"clean controls gave {a['verdict']}")
    ck(a["nr4a3_candidates"] == 12, f"target count was {a.get('nr4a3_candidates')}, expected 12")

    # 10 · 5'-depletion arithmetic, including the strand inversion that would silently flip it.
    hdr = ("DataSource:Type\tsnaptron_id\tchromosome\tstart\tend\tlength\tstrand\tannotated"
           "\tleft_motif\tright_motif\tleft_annotated\tright_annotated\tsamples\tsamples_count"
           "\tcoverage_sum\tcoverage_avg\tcoverage_median\tsource_dataset_id")

    def jrow(i, start, strand, samples):
        return (f"srav3h:I\t{i}\tchr9\t{start}\t{start+100}\t100\t{strand}\t1\tGT\tAG\t1\t1"
                f"\t{samples}\t1\t0\t0.0\t0\t0")

    # Nine annotated junctions on +. TRUNC carries coverage only on the three DOWNSTREAM-most.
    rows = [jrow(i, 1000 + 100 * i, "+",
                 ",NORMAL:50" + (",TRUNC:200" if i >= 6 else "")) for i in range(9)]
    d = five_prime_depletion(hdr + "\n" + "\n".join(rows))
    ck(d["usable"] is True, f"depletion unusable: {d.get('why')}")
    ck(d["strand_derived"] == "+", "strand vote did not return +")
    ids = [c["rail_id"] for c in d["candidates_top"]]
    ck(ids == ["TRUNC"], f"expected only TRUNC as a candidate, got {ids}")

    # Same coverage pattern, minus strand: the "5' end" is now the OTHER end, so TRUNC — which
    # carries the HIGH coordinates — is no longer 5'-depleted. A strand bug would keep calling it.
    rows_m = [r.replace("\t+\t", "\t-\t") for r in rows]
    dm = five_prime_depletion(hdr + "\n" + "\n".join(rows_m))
    ck(dm["strand_derived"] == "-", "strand vote did not return -")
    ck([c["rail_id"] for c in dm["candidates_top"]] == [],
       "a minus-strand gene still called the high-coordinate sample 5'-depleted — strand inverted")

    # A sample below the downstream-coverage floor must not be called: "no 5' coverage" and "barely
    # expressed" are the confound this floor exists to separate.
    faint = [jrow(i, 1000 + 100 * i, "+", ",FAINT:1" if i >= 6 else "") for i in range(9)]
    df = five_prime_depletion(hdr + "\n" + "\n".join(faint))
    ck([c["rail_id"] for c in df["candidates_top"]] == [],
       "a barely-expressed sample was called 5'-depleted")

    # Unannotated junctions must not enter the profile at all.
    unann = [r.replace("\t1\tGT", "\t0\tGT") for r in rows]
    du = five_prime_depletion(hdr + "\n" + "\n".join(unann))
    ck(du["usable"] is False, "unannotated junctions were admitted to the profile")

    # 11 · An unreadable supplement is never "no EMC".
    unread = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                              "geo_all_text": "^SAMPLE = GSM1\n!Sample_title = case 1\n",
                              "fetches": {},
                              "supplementary": {"u": {"parsed": {"readable": False,
                                                                 "why": "openpyxl unavailable"}}}}}
    a2 = derive(unread)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a2["verdict"] == "LABELS_NOT_LOCATED",
       f"an unreadable supplement gave {a2['verdict']}, expected LABELS_NOT_LOCATED")

    found = {"methylation": {"arm_state": "FETCHED", "geo_self_text": "!Series_title = x\n",
                             "geo_all_text": "^SAMPLE = GSM1\n!Sample_title = case 1\n",
                             "fetches": {},
                             "supplementary": {"u": {"parsed": {
                                 "readable": True, "n_emc_rows": 3, "confusable_rows": 0,
                                 "emc_rows": ["case 12 | extraskeletal myxoid chondrosarcoma"]}}}}}
    a3 = derive(found)["arms"]["pan_sarcoma_methylation_deposit"]
    ck(a3["verdict"] == "EMC_IN_THE_PUBLISHED_TABLE_NOT_IN_THE_DEPOSIT_LABELS",
       f"a supplement naming EMC gave {a3['verdict']}")
    ck(a3["supplementary_emc_rows"] == 3, "supplementary EMC row count was lost")

    if fails:
        print("SELFTEST FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print("selftest ok (11 guard groups)")
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
