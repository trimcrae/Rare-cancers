#!/usr/bin/env python3
"""Census of recurrent gene fusions: which fusion-driven cancers have EVER had a junction-directed oligo?

⭐ WHY THIS EXISTS. `fusion-junction-aso-research-article.md` establishes for ONE disease (EMC) that a
breakpoint seam admits parent-sparing gapmers, that the EXON rather than the GENE predicts a clean design,
and that the limiting step — RNase-H1 single-mismatch discrimination — is not computable. The per-disease
marginal cost of asking that question is a ~10-minute $0 CI job, and for a cancer with tens of cases a year
nobody will ever ask it individually. This module is the first stage of asking it for all of them: it
measures the universe of recurrent fusions and, per fusion, whether the oligonucleotide modality has ever
been pointed at that junction.

⛔ THE UNIVERSE IS FETCHED, NEVER TYPED. A fusion -> disease -> citation table written from a model's
recollection is exactly the failure `research/manuscripts/lint_citations.py` (preflight gate 4) exists to
catch: on 2026-08-07 an agent drafting a manuscript produced a PMID present in no committed source
anywhere in this repository, and it passed `lint_claims` twice. So every row here carries the source that
served it, and when NO source answers this module emits `status: no_universe_fetched` with zero rows and
exits 3. **There is no fallback list, because a fallback list is the defect.**

★ WHAT A CLASSIFICATION IS AND IS NOT. `orphan` means THIS query over THIS corpus on THIS date retrieved
no record pointing an oligonucleotide at that fusion. It is not proof that no such work exists — a paper
indexed under different terms, or not indexed at all, would not appear. The same limit the EMC manuscript
states for its own first-in-kind claim applies here and is recorded in the artifact rather than left to
the reader to infer. Every query string is stored verbatim with its hit count and date so a reader can
re-run it.

★ AND AN ORPHAN IS NOT THEREBY A TARGET. Rows carry whatever existing therapy the source records, because
this catalog covers every recurrent fusion including the kinase-druggable ones, and a catalog that implied
an antisense oligonucleotide is NEEDED where an approved inhibitor works would be making a clinical claim
it has no basis for. What recurrence and resistance mean for those diseases is a question for the paper,
not a field this module may fill in.

⏸ PARKED 2026-08-13, BY trimcrae, UNTIL THE EMC ASO PAPER IS PUBLISHED. This module and its HGNC index
are on `main` because they are self-contained and nothing else reads them; the rest of the catalog work
stays on `claude/orphaned-fusion-junction-catalog-0jgizz`. Two things were deliberately HELD BACK from
`main`, and both matter to whoever resumes:

  1. **The `aso_insilico.offtarget_scan` inverted-index rewrite.** It makes screening cost independent
     of design count (measured: 400 designs 16.91 s -> 3.02 s) and is the change that makes a catalog
     affordable. It is also the ONLY change that touches the instrument that produced the EMC paper's
     PUBLISHED off-target counts, and its equivalence test runs on a SYNTHETIC transcriptome, not on the
     real EMC artifacts. ⛔ Before merging it, re-run the real EMC screen and diff it against the
     committed `aso-insilico-evaluation*.json` design-for-design. `tests/test_aso_insilico_scan_
     equivalence.py` IS on `main` and currently passes against the OLD implementation, so it is a live
     characterisation guard rather than a dormant file.
  2. **`fusion-junction-orphan-census.json` from run 31741055846.** It carries `status: ok` and reports
     139 of 198 fusions already `attempted` — and those numbers are WRONG. That run predates the
     known-answer control, and it classified `EWSR1::NR4A3` as `attempted` against a published,
     5,153-record count of zero. An artifact that says `ok` while disagreeing with the one checkable
     case is exactly the stale-fact-reading-as-current hazard CLAUDE.md §7 describes, so it is not on
     `main`. **Do not quote those counts.** Re-run with the control before reporting any orphan number.

★ ALSO UNRESOLVED WHEN THIS WAS PARKED: prior art. A `CRISPR-Cas13b` paper (bioRxiv 2022/2025) already
does systematic, breakpoint-targeted silencing across multiple fusions WITH wet-lab validation, so "nobody
has systematically targeted fusion breakpoints" is not a claim this work may make. `FusionHub`
(PLOS One 2018) is the closest catalog analogue and its web platform no longer resolves. Neither was read
at primary source — the egress proxy blocks NCBI, PLOS and bioRxiv — so both need the CI-routed check
before anything is written down.

Modes:
    python3 fusion_junction_census.py --probe    # reachability of every universe source; emits no rows
    python3 fusion_junction_census.py            # full census (needs network: source hosts + Europe PMC)
    python3 fusion_junction_census.py --check    # re-derive the arithmetic offline; nonzero on disagreement

Network required (source hosts + Europe PMC). The dev sandbox egress-proxy 403s these, so this runs on a
GitHub Actions runner — the `fusion_census` task of `.github/workflows/fusion-cpu-extras.yml`.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fusion-junction-orphan-census.json")
PROBE_OUT = os.path.join(HERE, "fusion-junction-census-source-probe.json")

UA = ("rare-cancers-research/1.0 (pan-fusion junction-oligonucleotide census; "
      "mailto:trimcrae@gmail.com)")

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

#: Politeness spacing between Europe PMC calls. Three queries per fusion pair, so this sets the stage's
#: wall clock: at 0.34 s a 1,000-pair universe is ~17 min of request time.
EPMC_SPACING_S = 0.34

#: Write the artifact every N pairs. CLAUDE.md §6: a job whose runtime you are estimating checkpoints after
#: each unit and treats the partial checkpoint as the deliverable on a timeout.
CHECKPOINT_EVERY = 10

# ─────────────────────────────────────────────────────────────────────────────────────────────────
# Universe sources
#
# ⚠ ONLY THE CIViC ARM HAS A PARSER WRITTEN AGAINST A KNOWN SCHEMA. The other three are recorded as
# PROBE arms: this module asks whether they answer and what they served, and does NOT pretend to parse a
# payload whose shape nobody here has measured. `--probe` exists to turn that ignorance into a reading
# before a parser is written for it — which is the whole point of running the probe first.
# ─────────────────────────────────────────────────────────────────────────────────────────────────
SOURCES = [
    {
        "name": "civic_clinical_evidence",
        "url": "https://civicdb.org/downloads/nightly/nightly-ClinicalEvidenceSummaries.tsv",
        "licence": "CC0",
        "gives": "fusion variant, disease, therapies, source PMIDs",
        "parser": "civic_evidence_tsv",
    },
    {
        "name": "civic_variant_summaries",
        "url": "https://civicdb.org/downloads/nightly/nightly-VariantSummaries.tsv",
        "licence": "CC0",
        "gives": "variant types (fusion flagging), transcripts",
        "parser": "civic_variant_tsv",
    },
    {
        "name": "mitelman_isb_cgc",
        "url": "https://mitelmandatabase.isb-cgc.org/",
        "licence": "free for research use, citation required",
        "gives": "disease <-> fusion recurrence",
        "parser": None,
    },
    {
        "name": "chimerdb4",
        "url": "http://www.kobic.re.kr/chimerdb/download",
        "licence": "free",
        "gives": "curated fusions with breakpoints",
        "parser": None,
    },
    {
        "name": "fusiongdb2",
        "url": "https://compbio.uth.edu/FusionGDB2/",
        "licence": "free",
        "gives": "ORF/frame annotation per breakpoint",
        "parser": None,
    },
]

#: A CIViC variant name that denotes a fusion. Modern CIViC uses `GENE1::GENE2`; the legacy hyphen form is
#: NOT accepted, because `V600E-like` and `Exon 14-skipping` match it and a permissive pattern would seed
#: the catalog with variants that are not fusions at all.
FUSION_NAME_RE = re.compile(r"^([A-Z][A-Z0-9orf.\-]{0,14})::([A-Z][A-Z0-9orf.\-]{0,14})$")

#: ⭐ MEASURED 2026-08-13 (probe run 31739900759): CIViC's evidence export keys on `molecular_profile`, and
#: a profile is frequently a fusion PLUS something else — `BCR::ABL1 T315I`, or a two-variant profile. A
#: whole-string match therefore drops real fusions on the floor, silently and in the direction that makes
#: the universe look smaller than it is. This searches WITHIN the profile for a `GENE::GENE` token at a
#: word boundary, which keeps the `::` requirement (the thing that makes it a fusion and not a point
#: mutation) while no longer requiring the fusion to be the entire profile.
FUSION_TOKEN_RE = re.compile(r"(?<![\w:])([A-Z][A-Z0-9orf.\-]{0,14})::([A-Z][A-Z0-9orf.\-]{0,14})(?![\w:])")


#: Tokens rejected because a half was not an approved gene. Recorded, never silently dropped —
#: a filter whose removals nobody can see is indistinguishable from a filter that is not running.
REJECTED_TOKENS = {}


def _fusion_tokens(text, validate=True):
    """Every distinct GENE::GENE token in a free-text variant/profile name, upper-cased.

    ⛔ BOTH HALVES MUST BE APPROVED HGNC SYMBOLS. The shakeout produced `ACT::FOSB`, scored `attempted`
    on 322 records, because `ACT` matches the English word "act" — and `ACT` is not a gene. Validating
    here removes the row at its source rather than flagging it downstream. Aliases and previous symbols
    resolve to their approved symbol; an AMBIGUOUS alias is rejected rather than guessed at, because
    picking one of two approved genes would retarget a screen at the wrong transcript.
    """
    out = []
    for m in FUSION_TOKEN_RE.finditer(text or ""):
        donor, acceptor = m.group(1).upper(), m.group(2).upper()
        if validate:
            resolved = []
            for half in (donor, acceptor):
                r = _resolve_symbol(half)
                if r is None or r == "__AMBIGUOUS__":
                    REJECTED_TOKENS[f"{donor}::{acceptor}"] = (
                        f"{half} is {'an ambiguous alias' if r else 'not an approved HGNC symbol'}")
                    resolved = None
                    break
                resolved.append(r)
            if resolved is None:
                continue
            donor, acceptor = resolved
        key = f"{donor}::{acceptor}"
        if key not in [o[2] for o in out]:
            out.append((donor, acceptor, key))
    return out


#: Whether HGNC validation was actually live during this run. ⛔ NEITHER FAILURE DIRECTION IS SAFE
#: SILENTLY: failing closed empties the universe and reads as "no fusions found"; failing open restores
#: the `ACT::FOSB` defect while the code still LOOKS validated. So the run fails open — an unavailable
#: index must not fabricate a universe of zero — and records that it did, in the artifact, where a
#: reader sees it beside the counts rather than having to infer it.
HGNC_VALIDATION = {"available": None, "error": None}


def _resolve_symbol(sym):
    """Approved symbol for a token via the committed HGNC index, or the token unchanged if the index
    is unavailable — with `HGNC_VALIDATION` recording which of those happened."""
    try:
        import hgnc_index
        r = hgnc_index.resolve(sym)
        HGNC_VALIDATION["available"] = True
        return r
    except Exception as e:  # noqa: BLE001
        HGNC_VALIDATION["available"] = False
        HGNC_VALIDATION["error"] = f"{type(e).__name__}: {e}"
        return sym


def _get(url, timeout=180, accept=None):
    """Fetch a URL. Returns (body, http_status, error). Never raises — a source that does not answer is a
    reading about that source, and the run continues to the ones that do."""
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace"), r.status, None
    except urllib.error.HTTPError as e:
        return "", e.code, f"HTTPError {e.code}"
    except Exception as e:  # noqa: BLE001
        return "", None, f"{type(e).__name__}: {e}"


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# Source probe
# ─────────────────────────────────────────────────────────────────────────────────────────────────
def probe_sources():
    """Ask every source whether it answers, and record what it served. Emits no catalog rows.

    ⭐ This is deliberately a separate mode. Writing four speculative parsers against payloads nobody has
    measured is how a pipeline acquires three arms that silently return nothing; one cheap run tells us
    which arms are real, and the parsers get written for those.
    """
    results = []
    for src in SOURCES:
        t0 = time.time()
        body, status, err = _get(src["url"], timeout=120)
        head = body[:400] if body else ""
        results.append({
            "name": src["name"],
            "url": src["url"],
            "licence": src["licence"],
            "gives": src["gives"],
            "has_parser": bool(src["parser"]),
            "http_status": status,
            "error": err,
            "answered": status == 200 and bool(body),
            "bytes": len(body.encode("utf-8", "replace")) if body else 0,
            "elapsed_s": round(time.time() - t0, 1),
            "first_line": head.splitlines()[0][:300] if head.splitlines() else "",
            "looks_like_tsv": bool(head) and "\t" in head.splitlines()[0] if head.splitlines() else False,
        })
    return {
        "_what": ("Reachability probe for every candidate universe source. Emits NO catalog rows on "
                  "purpose — it exists so parsers are written against measured payloads rather than "
                  "assumed ones."),
        "_cost": "$0 — a few HTTP GETs on a free runner.",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_sources": len(results),
        "n_answered": sum(1 for r in results if r["answered"]),
        "sources": results,
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# CIViC parsers
# ─────────────────────────────────────────────────────────────────────────────────────────────────
def _tsv_rows(body):
    """Yield dicts keyed by the header line. Tolerant of ragged rows (CIViC free-text fields contain
    newlines in some releases); a row with fewer fields than the header is skipped and counted."""
    lines = body.splitlines()
    if not lines:
        return [], 0
    header = lines[0].split("\t")
    rows, skipped = [], 0
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < len(header):
            skipped += 1
            continue
        rows.append(dict(zip(header, parts)))
    return rows, skipped


def parse_civic_evidence(body):
    """Extract fusion pairs, their diseases, therapies and source identifiers from CIViC evidence.

    Columns are located BY NAME, never by index — a positional read of a schema that adds a column is a
    silent mis-parse, and CIViC's nightly schema is not frozen.
    """
    rows, skipped = _tsv_rows(body)
    if not rows:
        return {}, {"n_rows": 0, "n_skipped_ragged": skipped, "fusion_rows": 0,
                    "error": "no parseable rows"}
    cols = set(rows[0].keys())
    col_variant = next((c for c in ("variant", "molecular_profile") if c in cols), None)
    col_disease = "disease" if "disease" in cols else None
    col_drugs = next((c for c in ("therapies", "drugs") if c in cols), None)
    col_pmid = next((c for c in ("citation_id", "pubmed_id", "source_id") if c in cols), None)
    if not col_variant:
        return {}, {"n_rows": len(rows), "n_skipped_ragged": skipped, "fusion_rows": 0,
                    "error": f"no variant column among {sorted(cols)[:25]}"}

    pairs, fusion_rows = {}, 0
    for r in rows:
        name = (r.get(col_variant) or "").strip()
        tokens = _fusion_tokens(name)
        if not tokens:
            continue
        fusion_rows += 1
        for donor, acceptor, key in tokens:
            e = pairs.setdefault(key, {
                "donor_gene": donor, "acceptor_gene": acceptor, "fusion": key,
                "diseases": [], "existing_therapies": [], "source_identifiers": [],
                "universe_sources": ["civic_clinical_evidence"],
                "civic_profiles": [],
            })
            if name not in e["civic_profiles"]:
                e["civic_profiles"].append(name)
            d = (r.get(col_disease) or "").strip() if col_disease else ""
            if d and d not in e["diseases"]:
                e["diseases"].append(d)
            if col_drugs:
                for drug in re.split(r"[,;]", r.get(col_drugs) or ""):
                    drug = drug.strip()
                    if drug and drug not in e["existing_therapies"]:
                        e["existing_therapies"].append(drug)
            if col_pmid:
                pid = (r.get(col_pmid) or "").strip()
                if pid.isdigit() and pid not in e["source_identifiers"]:
                    e["source_identifiers"].append(pid)
    return pairs, {"n_rows": len(rows), "n_skipped_ragged": skipped, "fusion_rows": fusion_rows,
                   "columns_used": {"variant": col_variant, "disease": col_disease,
                                    "therapies": col_drugs, "citation": col_pmid}}


def parse_civic_variants(body):
    """Second CIViC arm: variants flagged as fusions by variant_type, which catches pairs that carry no
    clinical-evidence row. Same by-name column discipline."""
    rows, skipped = _tsv_rows(body)
    if not rows:
        return {}, {"n_rows": 0, "n_skipped_ragged": skipped, "fusion_rows": 0,
                    "error": "no parseable rows"}
    cols = set(rows[0].keys())
    col_variant = "variant" if "variant" in cols else None
    col_types = next((c for c in ("variant_types", "variant_type") if c in cols), None)
    # measured 2026-08-13: this export also carries `feature_type` / `feature_name`, and a fusion feature
    # names the pair even when the variant row itself is a sub-variant of it.
    col_ftype = "feature_type" if "feature_type" in cols else None
    col_fname = "feature_name" if "feature_name" in cols else None
    if not col_variant:
        return {}, {"n_rows": len(rows), "n_skipped_ragged": skipped, "fusion_rows": 0,
                    "error": f"no variant column among {sorted(cols)[:25]}"}
    pairs, fusion_rows, fusion_features = {}, 0, 0
    for r in rows:
        tokens = _fusion_tokens((r.get(col_variant) or "").strip())
        if not tokens and col_fname and (r.get(col_ftype) or "").strip().lower() == "fusion":
            tokens = _fusion_tokens((r.get(col_fname) or "").strip())
            if tokens:
                fusion_features += 1
        if not tokens:
            continue
        fusion_rows += 1
        for donor, acceptor, key in tokens:
            e = pairs.setdefault(key, {
                "donor_gene": donor, "acceptor_gene": acceptor, "fusion": key,
                "diseases": [], "existing_therapies": [], "source_identifiers": [],
                "universe_sources": ["civic_variant_summaries"],
            })
            if col_types:
                t = (r.get(col_types) or "").strip()
                if t:
                    e.setdefault("variant_types", [])
                    if t not in e["variant_types"]:
                        e["variant_types"].append(t)
    return pairs, {"n_rows": len(rows), "n_skipped_ragged": skipped, "fusion_rows": fusion_rows,
                   "fusion_rows_via_feature_name": fusion_features,
                   "columns_used": {"variant": col_variant, "variant_types": col_types,
                                    "feature_type": col_ftype, "feature_name": col_fname}}


PARSERS = {"civic_evidence_tsv": parse_civic_evidence, "civic_variant_tsv": parse_civic_variants}


def fetch_universe():
    """Fetch every source that has a parser; merge into one keyed universe. Records per-source outcome.

    ⛔ Returns an EMPTY universe if nothing answered. The caller must not proceed from that state, and
    must not substitute anything for it.
    """
    universe, per_source = {}, []
    for src in SOURCES:
        if not src["parser"]:
            body, status, err = _get(src["url"], timeout=120)
            # ⚠ HTTP 200 IS NOT A DATA SOURCE. Measured 2026-08-13 (probe run 31739900759): Mitelman and
            # FusionGDB2 both answer 200 — with an HTML landing page, not a bulk export. Recording those
            # as "answered" without saying what they served would let two decorative arms read as live
            # coverage, which is the shape of the `fetch-literature.yml` query path that was believed to
            # be searching Europe PMC while invoking nothing.
            served_html = body.lstrip()[:15].lower().startswith("<!doctype") or \
                body.lstrip()[:6].lower().startswith("<html")
            per_source.append({"name": src["name"], "url": src["url"], "http_status": status,
                               "error": err, "answered": status == 200 and bool(body),
                               "served_html_not_data": served_html,
                               "bytes": len(body.encode("utf-8", "replace")) if body else 0,
                               "parsed": False,
                               "why_not_parsed": "no parser written against a measured payload — "
                                                 "see --probe"})
            continue
        body, status, err = _get(src["url"], timeout=300)
        if status != 200 or not body:
            per_source.append({"name": src["name"], "url": src["url"], "http_status": status,
                               "error": err, "answered": False, "parsed": False})
            continue
        pairs, stats = PARSERS[src["parser"]](body)
        for key, entry in pairs.items():
            if key in universe:
                merged = universe[key]
                for field in ("diseases", "existing_therapies", "source_identifiers",
                              "universe_sources", "variant_types"):
                    for v in entry.get(field, []):
                        merged.setdefault(field, [])
                        if v not in merged[field]:
                            merged[field].append(v)
            else:
                universe[key] = entry
        per_source.append({"name": src["name"], "url": src["url"], "http_status": status,
                           "error": None, "answered": True, "parsed": True,
                           "pairs_contributed": len(pairs), "parse_stats": stats})
    return universe, per_source


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# Prior-art determination (Europe PMC)
# ─────────────────────────────────────────────────────────────────────────────────────────────────
#: ⛔ EVERY VOCABULARY IS TITLE_ABS-RESTRICTED, AND THE KNOWN-ANSWER CONTROL IS WHAT FORCED IT
#: (run 31741055846, 2026-08-13). The first full census restricted only the GENE tokens to title and
#: abstract and let the modality and junction words match anywhere in full text. That classified
#: **EWSR1::NR4A3 as `attempted` with 19 hits** — against a disease whose own manuscript established,
#: over 5,153 retrieved records, that the count of junction-directed oligonucleotide work against any
#: NR4A3 fusion is **zero**. A paper about EMC that says "siRNA" once in its methods and "breakpoint"
#: once in its discussion was being counted as an attempt on the junction.
#:
#: A study that actually points an oligonucleotide at a fusion junction says so in its title or
#: abstract. That is the EMC manuscript's own standard — it counted mentions "at title or abstract
#: level" — so it is the standard used here.
_MODALITY_WORDS = ["antisense", "gapmer", "siRNA", "shRNA", "morpholino",
                   "antisense oligonucleotide", "splice-switching", "oligonucleotide"]
_JUNCTION_WORDS = ["junction", "breakpoint", "fusion-specific", "fusion specific", "chimeric"]


def _title_abs_any(words):
    return "(" + " OR ".join(f'TITLE_ABS:"{w}"' for w in words) + ")"


MODALITY_TERMS = _title_abs_any(_MODALITY_WORDS)
JUNCTION_TERMS = _title_abs_any(_JUNCTION_WORDS)

#: ⛔ A BARE `("G1" AND "G2")` QUERY IS NOT A QUERY ABOUT A FUSION, AND THE SHAKEOUT PROVED IT
#: (run 31740571888, 2026-08-13). Five pairs were screened and four came back `attempted`, including
#: `ACT::FOSB` with **322** supposed junction-directed oligonucleotide records. `ACT` is a three-letter
#: token that matches the English word "act" everywhere in full text, so that count measures the
#: language, not the literature. Left alone this would have reported most of the universe as already
#: attempted — the exact opposite of the paper's finding, produced by a query rather than by the world.
#:
#: Two corrections, both mirroring what the EMC manuscript actually did (it counted mentions "at title
#: or abstract level" over a retrieved corpus):
#:   1. gene tokens are restricted to TITLE_ABS, not full text;
#:   2. an explicit FUSION-NAME arm is searched as a phrase, since a paper about a fusion nearly always
#:      names it, and a phrase hit is worth far more than a co-occurrence.
#: The loose full-text count is still recorded as `denominator_loose` — it is the corpus size the
#: absence claim sits inside, and dropping it would hide how much the sharpening moved the number.
AMBIGUOUS_SYMBOL_MAX_LEN = 3


def fusion_phrase_clause(donor, acceptor):
    """The fusion named as a phrase, in the spellings the literature actually uses."""
    forms = [f"{donor}::{acceptor}", f"{donor}-{acceptor}", f"{donor}/{acceptor}",
             f"{donor} {acceptor} fusion"]
    return "(" + " OR ".join(f'"{f}"' for f in forms) + ")"


def title_abs_clause(donor, acceptor):
    return f'(TITLE_ABS:"{donor}" AND TITLE_ABS:"{acceptor}")'


def epmc_query(query, page_size=25, tries=4):
    """One Europe PMC search. Returns hit count and the top identifiers, or the failure.

    ⚠ RETRIES ON 5xx, BECAUSE THE FIRST FULL RUN LOST 23 OF 198 PAIRS TO THEM (run 31741055846). The
    failures were 502/503/504 in a contiguous alphabetical window — Europe PMC throttling a sustained
    ~1.2 req/s, not anything about those fusions. A transient server error must not be allowed to look
    like a screened pair, and `screen_failed` correctly refused to call them orphans; retrying is what
    turns the refusal back into a measurement.
    """
    url = EPMC + "?" + urllib.parse.urlencode({
        "query": query, "format": "json", "pageSize": page_size, "resultType": "lite"})
    body, status, err = _get(url, timeout=60)
    for attempt in range(1, tries):
        if status is not None and 500 <= status < 600:
            time.sleep(2 ** attempt)
            body, status, err = _get(url, timeout=60)
        else:
            break
    if status != 200 or not body:
        return {"query": query, "http_status": status, "error": err, "hit_count": None,
                "identifiers": []}
    try:
        blob = json.loads(body)
    except json.JSONDecodeError as e:
        return {"query": query, "http_status": status, "error": f"JSONDecodeError: {e}",
                "hit_count": None, "identifiers": []}
    results = (blob.get("resultList") or {}).get("result") or []
    ids = []
    for r in results:
        pmid = (r.get("pmid") or "").strip()
        if pmid:
            ids.append(pmid)
    return {"query": query, "http_status": status, "error": None,
            "hit_count": blob.get("hitCount"), "identifiers": ids}


def classify_pair(donor, acceptor):
    """The four-query determination. Every query string travels with its own count and identifiers.

    The VERDICT is taken from the sharpened arms (title/abstract gene mentions, or the fusion named as
    a phrase). The loose full-text co-occurrence count is retained as context, never as the verdict.
    """
    sharp = f'({fusion_phrase_clause(donor, acceptor)} OR {title_abs_clause(donor, acceptor)})'
    q_loose = f'("{donor}" AND "{acceptor}")'
    q_denom = sharp
    q_modality = f'{sharp} AND ({MODALITY_TERMS})'
    q_junction = f'{q_modality} AND ({JUNCTION_TERMS})'

    loose = epmc_query(q_loose)
    time.sleep(EPMC_SPACING_S)
    denom = epmc_query(q_denom)
    time.sleep(EPMC_SPACING_S)
    modality = epmc_query(q_modality)
    time.sleep(EPMC_SPACING_S)
    junction = epmc_query(q_junction)
    time.sleep(EPMC_SPACING_S)

    counts = [denom["hit_count"], modality["hit_count"], junction["hit_count"]]
    if any(c is None for c in counts):
        verdict = "screen_failed"
    elif junction["hit_count"] > 0:
        verdict = "attempted"
    elif modality["hit_count"] > 0:
        verdict = "modality_touched"
    else:
        verdict = "orphan"

    # ⚠ A SHORT SYMBOL STAYS NOISY EVEN IN TITLE_ABS. `ACT`, `FUS`, `MET` and their kind are English
    # words as well as genes, so a row carrying one is flagged for human reading rather than silently
    # trusted. The flag does not change the verdict — it says which verdicts a reader must check.
    ambiguous = [s for s in (donor, acceptor) if len(s) <= AMBIGUOUS_SYMBOL_MAX_LEN]
    return {
        "verdict": verdict,
        "ambiguous_symbols": ambiguous,
        "needs_human_read": bool(ambiguous) and verdict == "attempted",
        "queries": {"denominator_loose_fulltext": loose, "denominator": denom,
                    "modality": modality, "junction_directed": junction},
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────────
#: ⭐ THE KNOWN-ANSWER POSITIVE CONTROL, RUN ON EVERY CENSUS. `fusion-junction-aso-research-article.md`
#: established over 5,153 retrieved Europe PMC records that the count of junction-directed
#: oligonucleotide work against any NR4A3 fusion is ZERO. That makes EWSR1::NR4A3 the one pair in this
#: universe whose answer is independently known — so it is the one pair that can tell a working
#: instrument from a broken one.
#:
#: ⛔ THIS IS NOT DECORATION. The first full run (31741055846) classified it `attempted` with 19 hits and
#: reported a clean `status: ok` while doing so. Nothing in the artifact said the instrument disagreed
#: with the only case anybody could check. A census whose control fails is a census reporting numbers it
#: has not earned, and it now says so in its own summary rather than leaving that to a reader who
#: happens to know the EMC literature.
CONTROL_FUSION = ("EWSR1", "NR4A3")
CONTROL_EXPECTED = "orphan"
CONTROL_BASIS = ("fusion-junction-aso-research-article.md: across 5,153 unique Europe PMC records, "
                 "no junction-directed oligonucleotide study exists against any NR4A3 fusion")


def run_control():
    """Screen the control pair and report whether the instrument reproduces the known answer."""
    donor, acceptor = CONTROL_FUSION
    got = classify_pair(donor, acceptor)
    return {
        "fusion": f"{donor}::{acceptor}",
        "expected_verdict": CONTROL_EXPECTED,
        "observed_verdict": got["verdict"],
        "passed": got["verdict"] == CONTROL_EXPECTED,
        "basis": CONTROL_BASIS,
        "⛔_if_this_failed": ("The screen disagrees with the one pair whose answer is independently "
                             "known, so every other verdict in this file is suspect in the same "
                             "direction. Do not read the orphan count as a measurement."),
        "queries": got["queries"],
    }


def _summarise(rows):
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    with_therapy = sum(1 for r in rows if r.get("existing_therapies"))
    return {
        "n_fusion_pairs": len(rows),
        "verdict_counts": counts,
        "n_with_recorded_existing_therapy": with_therapy,
        "n_without_recorded_existing_therapy": len(rows) - with_therapy,
        "n_needing_human_read": sum(1 for r in rows if r.get("needs_human_read")),
    }


def _envelope(status, rows, per_source, extra=None):
    env = {
        "_what": ("Per-fusion census: has any retrieved record ever pointed an oligonucleotide at this "
                  "fusion junction? One row per recurrent fusion pair in the fetched universe."),
        "_cost": "$0 — HTTP reads on a free GitHub Actions runner. No rental, no GPU.",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "⚠_what_a_verdict_is_not": (
            "'orphan' means THESE queries over Europe PMC on THIS date retrieved no record pointing an "
            "oligonucleotide at this fusion. It is not proof that no such work exists: a paper indexed "
            "under different terms, or not indexed at all, would not appear. Every query string is stored "
            "verbatim so the count can be re-run rather than trusted."),
        "⚠_an_orphan_is_not_a_target": (
            "This universe includes kinase-druggable fusions on purpose. `existing_therapies` records "
            "what the source associates with the fusion. Nothing here asserts that an oligonucleotide is "
            "needed, better, or available for any disease, and no row is a clinical recommendation."),
        "_universe_is_fetched_never_typed": (
            "Rows exist only for fusion pairs a named source served. If no source answers, this file "
            "carries status 'no_universe_fetched' and zero rows, and the run exits 3."),
        "⚠_short_symbols_stay_noisy": (
            "A gene symbol of <=3 characters is an English word as well as a gene (ACT, FUS, MET). Rows "
            "carrying one are flagged `needs_human_read` when they classify as `attempted`; the flag "
            "does not change the verdict, it names which verdicts a reader must check by hand."),
        "hgnc_symbol_validation": {
            "ran": HGNC_VALIDATION["available"],
            "error": HGNC_VALIDATION["error"],
            "⚠": ("When this is false the fusion tokens were NOT checked against approved gene symbols, "
                  "so non-genes such as `ACT` can enter the universe. The run fails open rather than "
                  "emitting an empty universe, and says so here."),
            "n_tokens_rejected": len(REJECTED_TOKENS),
            "rejected": dict(sorted(REJECTED_TOKENS.items())[:200]),
        },
        "status": status,
        "n_universe_pairs": None,        # set by run_census — the FULL fetched universe, not the rows
        "epmc_endpoint": EPMC,
        "modality_terms": MODALITY_TERMS,
        "junction_terms": JUNCTION_TERMS,
        "sources": per_source,
        "summary": _summarise(rows),
        "rows": rows,
    }
    if extra:
        env.update(extra)
    return env


def _write(path, blob):
    with open(path, "w") as fh:
        json.dump(blob, fh, indent=2, sort_keys=False)
        fh.write("\n")


def run_census(limit=None, resume=True):
    universe, per_source = fetch_universe()
    if not universe:
        blob = _envelope("no_universe_fetched", [], per_source, {"n_universe_pairs": 0})
        _write(OUT, blob)
        print("⛔ no universe source answered — emitted zero rows and exiting 3", file=sys.stderr)
        return blob, 3

    done = {}
    if resume and os.path.exists(OUT):
        try:
            with open(OUT) as fh:
                prev = json.load(fh)
            for r in prev.get("rows", []):
                if r.get("verdict") not in (None, "screen_failed"):
                    done[r["fusion"]] = r
        except (json.JSONDecodeError, KeyError, OSError):
            done = {}

    # ⭐ CONTROL FIRST. CLAUDE.md §6: when one leg carries the most information about whether to trust
    # the rest, run that leg first. Here it is the only pair whose answer is independently known.
    control = run_control()
    if not control["passed"]:
        print(f"⛔ KNOWN-ANSWER CONTROL FAILED: {control['fusion']} expected "
              f"{control['expected_verdict']}, got {control['observed_verdict']}", file=sys.stderr)

    keys = sorted(universe)
    if limit:
        keys = keys[:limit]
    rows = []
    for i, key in enumerate(keys, 1):
        entry = universe[key]
        if key in done:
            rows.append(done[key])
            continue
        verdict = classify_pair(entry["donor_gene"], entry["acceptor_gene"])
        row = dict(entry)
        row.update(verdict)
        rows.append(row)
        if i % CHECKPOINT_EVERY == 0:
            _write(OUT, _envelope("partial", rows, per_source,
                                  {"progress": f"{i}/{len(keys)}",
                                   "n_universe_pairs": len(universe),
                                   "known_answer_control": control}))
            print(f"  checkpoint {i}/{len(keys)}", file=sys.stderr)

    # ⭐ THE UNIVERSE SIZE IS THE NUMBER THE WHOLE CATALOG PLAN RESTS ON, so it goes in the artifact
    # rather than being inferable only by adding up per-source stats. `--limit` screens a subset;
    # it must never make the universe look smaller than it was measured to be.
    blob = _envelope("ok" if control["passed"] else "ok_but_control_failed", rows, per_source,
                     {"n_universe_pairs": len(universe),
                      "n_screened_this_run": len(rows),
                      "screened_subset": len(rows) < len(universe),
                      "known_answer_control": control})
    _write(OUT, blob)
    return blob, 0


def check():
    """Offline re-derivation: the summary must equal what the rows say. Nonzero on disagreement."""
    if not os.path.exists(OUT):
        print(f"⛔ {OUT} does not exist — nothing to check", file=sys.stderr)
        return 2
    with open(OUT) as fh:
        blob = json.load(fh)
    want = _summarise(blob.get("rows", []))
    got = blob.get("summary")
    if want != got:
        print(f"⛔ summary disagrees with rows\n  recorded: {got}\n  derived:  {want}", file=sys.stderr)
        return 1
    if blob.get("status") == "no_universe_fetched" and blob.get("rows"):
        print("⛔ status says no universe was fetched but rows are present", file=sys.stderr)
        return 1
    print(f"✅ census self-consistent: {want}")
    return 0


def main(argv):
    if "--check" in argv:
        return check()
    if "--probe" in argv:
        blob = probe_sources()
        _write(PROBE_OUT, blob)
        for s in blob["sources"]:
            mark = "✅" if s["answered"] else "⛔"
            print(f"{mark} {s['name']:<28} http={s['http_status']} bytes={s['bytes']} "
                  f"parser={'yes' if s['has_parser'] else 'no'} {s['error'] or ''}")
        print(f"\n{blob['n_answered']}/{blob['n_sources']} sources answered -> {PROBE_OUT}")
        return 0
    limit = None
    for a in argv:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
    blob, rc = run_census(limit=limit)
    print(json.dumps(blob["summary"], indent=2))
    print(f"-> {OUT}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
