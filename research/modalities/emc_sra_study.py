#!/usr/bin/env python3
"""Is `PRJNA1357027` / `SRP640302` a FOURTH EMC cohort — and is it readable?

WHY THIS EXISTS, AND WHY IT IS NOT `emc_cohort_search.py`.
`emc_cohort_search.py` asks whether a fourth EMC expression cohort exists and it asks GEO. Its own
header bounds the negative it produces: "GEO's `esearch` matches depositor prose … a null result
bounds what a term search over GEO can reach". `nr4a3-fusion-transcriptional-output.md` §3.13
records that no fourth EMC cohort exists, and that search was GEO-side too. **A deposit that lives
in SRA and never got a GEO series is outside both.** `SRP640302` is exactly that case: it is
already named in this repository — `emc-atr-vulnerability-inputs.json` →
`part_b.dataset_search.sra.studies[0]`, from an SRA term search — with a title and nothing else. A
title is not a characterisation. Nobody has ever read its runs, its samples, its assay, or whether
its data are public.

So this module is the SRA-side sibling: it CHARACTERISES a named archive study rather than
searching for one, the same way `atr_hrd_sarcoma_series.py` characterises one GEO series rather
than searching GEO. It reads two independent archives (NCBI E-utilities and EBI/ENA), records every
payload verbatim, and answers four questions in order, each of which can kill the lead:

    Q1  does the record EXIST?
    Q2  is it actually EMC, and what are the 12 runs — tumours? arms? replicates?
    Q3  are the DATA public and downloadable, or only the metadata?
    Q4  is it already in this repository, and is there a publication or GEO cross-link?

⛔ AN ABSENT READING IS NOT A READING OF ABSENCE, AND THIS MODULE IS ONE QUERY AWAY FROM THAT
FAILURE ON EVERY CALL. NCBI answers `403` to CONNECT from the dev sandbox, and a proxy refusal, a
rate-limit and a genuinely nonexistent accession all arrive as "no records". So every fetch round
carries THREE controls and the verdict is gated on them:

    ctrl_real_bioproject  PRJNA1273954  known real — anchored in `atr-hrd-sarcoma-series.json`
    ctrl_real_sra_study   SRP445369     known real — the EMC WGS deposit, anchored in
                                        `emc-atr-vulnerability-inputs.json`
    ctrl_absent           PRJNA9999999  known ABSENT — must return zero

A zero on the target is a finding ONLY when both positive controls came back non-zero AND the
absent control came back zero. Otherwise the verdict is `UNREADABLE_TRANSPORT` and says which
control failed. `ctrl_absent` is the half people forget: without it, a matcher loose enough to
return something for everything would make every accession "exist".

⛔ AND 12 RUNS IS NOT 12 PATIENTS. Run count, experiment count, sample count and BioSample count are
four different numbers and this module reports all four separately, from the returned metadata
only, never inferred from each other. `TempO-Seq` is a targeted ligation panel, not RNA-seq: if the
library strategy says so, the deposit's usable gene space is the panel's, and that is a different
instrument from the three cohorts the manuscript reads. Whatever the metadata says is recorded
verbatim in `library_strategy_values` / `library_selection_values`; this module never writes the
word TempO-Seq into a result field that the archives did not put there.

REPRODUCTION
    python3 emc_sra_study.py --selftest   # offline invariants; runs BEFORE any fetch in CI
    python3 emc_sra_study.py --fetch      # needs network (GitHub Actions; NCBI 403s in-sandbox)
    python3 emc_sra_study.py              # re-derive the verdict from the cached payloads, offline
    python3 emc_sra_study.py --check      # re-derive and diff against the committed artifact
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-sra-study.json")
INPUTS = os.path.join(HERE, "emc-sra-study-inputs.json")

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ENA_PORTAL = "https://www.ebi.ac.uk/ena/portal/api"
ENA_BROWSER = "https://www.ebi.ac.uk/ena/browser/api"

# The lead, as it was handed over: a BioProject accession and an SRA study accession said to be the
# same deposit. THEY ARE ASSERTED TO BE A PAIR AND THAT IS ITSELF CHECKED — an SRA study belongs to
# exactly one BioProject, so if both resolve and they do not point at each other, the pairing in the
# hand-over is wrong and the verdict says so rather than quietly merging two records.
TARGET_BIOPROJECT = "PRJNA1357027"
TARGET_SRA_STUDY = "SRP640302"

# ⭐ THE CONTROLS. See the module header — the verdict is gated on all three.
# ⚠ NO PROSE `PMID`/`GSE` STRINGS IN HERE. `lint_citations` counts an identifier in a tracked
# `.json` as ANCHORED on the grounds that a JSON is a fetch product; hand-typing an identifier into
# a dict that is then serialised into the artifact would promote a from-memory citation into that
# anchor set. Accessions below are the QUERIES this module sends — they are the input to a fetch,
# and each is recorded with the payload the archive returned for it, which is the anchor.
CONTROLS = {
    "ctrl_real_bioproject": {
        "accession": "PRJNA1273954",
        "kind": "bioproject",
        "why": "known real: the BioProject behind the sarcoma ATR/HRD series this repo already "
               "characterised; anchored in atr-hrd-sarcoma-series.json",
        "expect": "nonzero",
    },
    "ctrl_real_sra_study": {
        "accession": "SRP445369",
        "kind": "sra_study",
        "why": "known real: the EMC metastatic-WGS deposit returned by the same SRA term search "
               "that returned the target; anchored in emc-atr-vulnerability-inputs.json",
        "expect": "nonzero",
    },
    "ctrl_absent": {
        "accession": "PRJNA9999999",
        "kind": "bioproject",
        "why": "known ABSENT: an accession far above the issued range. Without a negative control "
               "a matcher loose enough to return something for everything makes every accession "
               "'exist', and the two positive controls cannot detect that",
        "expect": "zero",
    },
}

# Screens study/sample prose for the disease. Deliberately generous: a false positive here costs one
# extra field to read, a false negative costs the lead. Same token set as `emc_cohort_search.py`'s
# `EMC_TOKENS`, kept separate rather than imported because that module's is tuned to GEO series
# prose and this one reads SRA/BioSample prose — a shared regex that either module could retune is
# a coupling neither wants.
EMC_TOKENS = re.compile(
    r"extraskeletal myxoid chondrosarcoma|myxoid chondrosarcoma|\bEMC\b|EWSR1[-:/ ]?NR4A3|"
    r"EWS[-/ ]?NOR-?1|TAF15[-:/ ]?NR4A3|NR4A3|NOR-?1\b", re.I)

# The strict set, used to COUNT how many samples name the disease. Over-breadth here is fail-open:
# a pan-sarcoma deposit writing "NR4A3: negative" on every sample would score every sample EMC under
# the loose set above. Disease name and fusion only.
EMC_STRICT_TOKENS = re.compile(
    r"extraskeletal myxoid chondrosarcoma|myxoid chondrosarcoma|EWSR1[-:/ ]?NR4A3|"
    r"EWS[-/ ]?NOR-?1|TAF15[-:/ ]?NR4A3", re.I)

# Assay-family probes, applied to whatever the archives return in the library fields and prose.
# ⛔ THESE NAME WHAT WAS FOUND, THEY DO NOT DECIDE WHAT IT IS. Every hit is reported next to the
# verbatim string that produced it, so a reader can disagree with the bucket without losing the data.
ASSAY_PROBES = {
    "tempo_seq": re.compile(r"tempo[-\s_]?seq|templated oligo", re.I),
    "targeted_panel": re.compile(r"targeted|amplicon|panel|capture|ligation", re.I),
    "rna_seq": re.compile(r"\bRNA[-\s_]?Seq\b|transcriptom", re.I),
    "wgs_wxs": re.compile(r"\bWGS\b|\bWXS\b|whole[-\s]genome|whole[-\s]exome", re.I),
}

# ENA read_run fields. Every one of these is a MEASURED property of a run; `fastq_ftp`/`fastq_bytes`
# are the pair that answers Q3, because a registered-but-embargoed run has metadata and no files.
ENA_RUN_FIELDS = [
    "run_accession", "experiment_accession", "sample_accession", "secondary_sample_accession",
    "study_accession", "secondary_study_accession", "instrument_platform", "instrument_model",
    "library_strategy", "library_source", "library_selection", "library_layout", "library_name",
    "read_count", "base_count", "first_public", "last_updated", "fastq_ftp", "fastq_bytes",
    "submitted_ftp", "sra_ftp", "scientific_name", "sample_title", "sample_alias", "description",
    "experiment_title", "study_title",
]
ENA_SAMPLE_FIELDS = [
    "sample_accession", "secondary_sample_accession", "sample_title", "sample_alias",
    "scientific_name", "description", "first_public", "last_updated", "tax_id",
]

# A payload larger than this is stored truncated, with the original length recorded. Truncation is
# NEVER silent — the marker is a key a reader trips over, not a comment.
MAX_PAYLOAD_CHARS = 400_000


# =================================================================================================
# FETCH — the only half that needs a network
# =================================================================================================
def _fetch_round():
    """Every HTTP call this module makes, recorded whether it succeeded or not."""
    import time
    import urllib.error
    import urllib.request

    fetches = []

    def get(key, url, parse):
        """parse in {'json','xml','tsv'}; the raw body is kept regardless of parse outcome."""
        rec = {"key": key, "url": url, "parse": parse}
        body, err, status = None, None, None
        for i in range(3):
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "rare-cancers/1.0 (EMC SRA characterisation)"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    status = r.getcode()
                    body = r.read().decode("utf-8", "replace")
                break
            except urllib.error.HTTPError as exc:            # a server answer, not a transport fail
                status, err = exc.code, f"HTTPError {exc.code}: {exc.reason}"
                try:
                    body = exc.read().decode("utf-8", "replace")
                except Exception:                            # noqa: BLE001
                    body = None
                break
            except Exception as exc:                         # noqa: BLE001
                err = f"{type(exc).__name__}: {exc}"[:300]
                if i < 2:
                    time.sleep(2 * (i + 1))
        rec["http_status"] = status
        if body is None:
            rec["_status"] = "failed"
            rec["error"] = err
            fetches.append(rec)
            return rec
        rec["_status"] = "read" if err is None else "http_error"
        if err:
            rec["error"] = err
        rec["n_bytes"] = len(body)
        if len(body) > MAX_PAYLOAD_CHARS:
            rec["⚠ payload_truncated"] = True
            rec["n_bytes_before_truncation"] = len(body)
            body = body[:MAX_PAYLOAD_CHARS]
        rec["body"] = body
        if parse == "json":
            try:
                rec["json"] = json.loads(body)
            except Exception as exc:                         # noqa: BLE001
                rec["parse_error"] = f"{type(exc).__name__}: {exc}"[:200]
        fetches.append(rec)
        time.sleep(0.4)
        return rec

    def eutils_pair(prefix, db, term, retmax=500):
        """esearch -> esummary, the pair every NCBI read in this repo is built from."""
        q = urllib.parse.urlencode(
            {"db": db, "retmode": "json", "retmax": str(retmax), "term": term})
        es = get(f"{prefix}_esearch", f"{EUTILS}/esearch.fcgi?{q}", "json")
        ids = []
        try:
            ids = (es.get("json") or {}).get("esearchresult", {}).get("idlist") or []
        except Exception:                                    # noqa: BLE001
            ids = []
        if ids:
            q2 = urllib.parse.urlencode(
                {"db": db, "retmode": "json", "id": ",".join(ids[:200])})
            get(f"{prefix}_esummary", f"{EUTILS}/esummary.fcgi?{q2}", "json")
        return ids

    # ── Q1/Q2: NCBI, the target ────────────────────────────────────────────────────────────────
    for acc, kind in ((TARGET_BIOPROJECT, "bioproject"), (TARGET_SRA_STUDY, "sra_study")):
        eutils_pair(f"tgt_{acc}_bioproject", "bioproject", f"{acc}[All Fields]")
        sra_ids = eutils_pair(f"tgt_{acc}_sra", "sra", f"{acc}[All Fields]")
        eutils_pair(f"tgt_{acc}_biosample", "biosample", f"{acc}[All Fields]")
        if sra_ids:
            # The FULL SRA XML is the only NCBI payload carrying per-run library strategy,
            # platform and the BioSample attribute list in one document. Everything Q2 needs.
            q = urllib.parse.urlencode(
                {"db": "sra", "rettype": "full", "retmode": "xml", "id": ",".join(sra_ids[:200])})
            get(f"tgt_{acc}_sra_efetch_xml", f"{EUTILS}/efetch.fcgi?{q}", "xml")

    # ── Q1/Q2/Q3: ENA, the second, INDEPENDENT archive ─────────────────────────────────────────
    # ⭐ ENA is not a redundancy. It mirrors INSDC, so it answers Q1 independently of NCBI's uptime,
    # and `filereport` answers Q3 in a way NCBI's esummary does not: a run whose `fastq_ftp` is
    # empty is registered and not downloadable.
    for acc in (TARGET_BIOPROJECT, TARGET_SRA_STUDY):
        for result, fields in (("read_run", ENA_RUN_FIELDS), ("sample", ENA_SAMPLE_FIELDS)):
            q = urllib.parse.urlencode({
                "accession": acc, "result": result,
                "fields": ",".join(fields), "format": "tsv", "limit": "0"})
            get(f"tgt_{acc}_ena_{result}", f"{ENA_PORTAL}/filereport?{q}", "tsv")
        get(f"tgt_{acc}_ena_xml", f"{ENA_BROWSER}/xml/{acc}", "xml")

    # ── The controls, through the SAME code paths ──────────────────────────────────────────────
    # ⛔ A control that takes a different route proves nothing about the route the target took.
    for key, c in CONTROLS.items():
        acc = c["accession"]
        eutils_pair(f"{key}_bioproject", "bioproject", f"{acc}[All Fields]")
        eutils_pair(f"{key}_sra", "sra", f"{acc}[All Fields]")
        q = urllib.parse.urlencode({
            "accession": acc, "result": "read_run",
            "fields": ",".join(ENA_RUN_FIELDS), "format": "tsv", "limit": "0"})
        get(f"{key}_ena_read_run", f"{ENA_PORTAL}/filereport?{q}", "tsv")

    return fetches


def fetch():
    payload = {
        "_generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_what": "raw NCBI E-utilities and EBI/ENA payloads for the PRJNA1357027 / SRP640302 lead, "
                 "plus three controls through the same code paths",
        "target_bioproject": TARGET_BIOPROJECT,
        "target_sra_study": TARGET_SRA_STUDY,
        "controls": CONTROLS,
        "fetches": _fetch_round(),
    }
    with open(INPUTS, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.write("\n")
    return payload


# =================================================================================================
# DERIVE — offline, from the cached payloads only
# =================================================================================================
def _by_key(inputs):
    return {f["key"]: f for f in inputs.get("fetches", [])}


def _esearch_count(rec):
    """(count, n_ids, status). `None` count means the query could not be read AT ALL."""
    if not rec:
        return None, None, "absent"
    if rec.get("_status") != "read":
        return None, None, rec.get("_status") or "failed"
    r = ((rec.get("json") or {}).get("esearchresult") or {})
    if "count" not in r:
        return None, None, "unparseable"
    try:
        return int(r.get("count") or 0), len(r.get("idlist") or []), "read"
    except (TypeError, ValueError):
        return None, None, "unparseable"


def _tsv_rows(rec):
    """(rows, status). ENA filereport returns a header line even for zero results."""
    if not rec:
        return None, "absent"
    if rec.get("_status") != "read":
        return None, rec.get("_status") or "failed"
    body = (rec.get("body") or "").strip("\n")
    if not body:
        return [], "read_empty_body"
    lines = body.split("\n")
    head = lines[0].split("\t")
    rows = [dict(zip(head, ln.split("\t"))) for ln in lines[1:] if ln.strip()]
    return rows, "read"


def _uniq(vals):
    seen, out = set(), []
    for v in vals:
        v = (v or "").strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _probe_assays(strings):
    text = " || ".join(s for s in strings if s)
    hits = {}
    for name, rx in ASSAY_PROBES.items():
        m = rx.search(text)
        hits[name] = {"matched": bool(m), "matched_text": (m.group(0) if m else None)}
    return hits


def _control_gate(fk):
    """Did the transport work? The verdict is gated on this and nothing else."""
    out, ok = {}, True
    for key, c in CONTROLS.items():
        bp_c, _, bp_s = _esearch_count(fk.get(f"{key}_bioproject_esearch"))
        sra_c, _, sra_s = _esearch_count(fk.get(f"{key}_sra_esearch"))
        ena_rows, ena_s = _tsv_rows(fk.get(f"{key}_ena_read_run"))
        # "Did any archive see it" — a positive control passes if EITHER archive did, because a
        # single-archive outage must not be able to withdraw a real finding; a negative control
        # must be invisible to BOTH, because one loose matcher is enough to break the gate.
        ncbi_total = sum(x for x in (bp_c, sra_c) if isinstance(x, int))
        ncbi_readable = any(s == "read" for s in (bp_s, sra_s))
        ena_n = len(ena_rows) if ena_rows is not None else None
        rec = {
            "accession": c["accession"], "expect": c["expect"], "why": c["why"],
            "ncbi_bioproject_count": bp_c, "ncbi_bioproject_status": bp_s,
            "ncbi_sra_count": sra_c, "ncbi_sra_status": sra_s,
            "ena_read_run_rows": ena_n, "ena_status": ena_s,
        }
        if c["expect"] == "nonzero":
            saw = (ncbi_total > 0) or bool(ena_n)
            rec["passed"] = bool(saw)
            if not saw:
                rec["⛔ meaning"] = (
                    "a control this repository knows is real came back EMPTY, so a zero on the "
                    "target is a transport failure and not an absence"
                    if (ncbi_readable or ena_s == "read")
                    else "the query could not be read at all — no archive was reached")
        else:
            invisible = (ncbi_total == 0) and not ena_n
            rec["passed"] = bool(invisible and (ncbi_readable or ena_s == "read"))
            if not rec["passed"]:
                rec["⛔ meaning"] = (
                    "an accession that does not exist came back NON-EMPTY, so the matcher is loose "
                    "enough to make any accession 'exist' and no positive here means anything"
                    if not invisible
                    else "no archive was reached, so this control proves nothing either way")
        ok = ok and rec["passed"]
        out[key] = rec
    return out, ok


def _read_target(fk, acc):
    """Everything the two archives said about one accession, kept separate by archive."""
    bp_c, _, bp_s = _esearch_count(fk.get(f"tgt_{acc}_bioproject_esearch"))
    sra_c, sra_n, sra_s = _esearch_count(fk.get(f"tgt_{acc}_sra_esearch"))
    bs_c, _, bs_s = _esearch_count(fk.get(f"tgt_{acc}_biosample_esearch"))
    runs, runs_s = _tsv_rows(fk.get(f"tgt_{acc}_ena_read_run"))
    samples, samples_s = _tsv_rows(fk.get(f"tgt_{acc}_ena_sample"))

    rec = {
        "accession": acc,
        "ncbi": {
            "bioproject_esearch_count": bp_c, "bioproject_status": bp_s,
            "sra_esearch_count": sra_c, "sra_ids_returned": sra_n, "sra_status": sra_s,
            "biosample_esearch_count": bs_c, "biosample_status": bs_s,
        },
        "ena": {
            "read_run_status": runs_s,
            "n_read_run_rows": (len(runs) if runs is not None else None),
            "sample_status": samples_s,
            "n_sample_rows": (len(samples) if samples is not None else None),
        },
    }

    # ── NCBI BioProject summary prose (title/description), verbatim ────────────────────────────
    bp_sum = fk.get(f"tgt_{acc}_bioproject_esummary")
    titles = []
    if bp_sum and bp_sum.get("_status") == "read":
        res = ((bp_sum.get("json") or {}).get("result") or {})
        for uid in (res.get("uids") or []):
            d = res.get(uid) or {}
            titles.append({
                "uid": uid,
                "project_acc": d.get("project_acc"),
                "project_title": d.get("project_title"),
                "project_name": d.get("project_name"),
                "project_description": (d.get("project_description") or "")[:2000],
                "registration_date": d.get("registration_date"),
                "project_data_type": d.get("project_data_type"),
            })
    rec["ncbi"]["bioproject_records"] = titles

    # ── ENA XML prose ─────────────────────────────────────────────────────────────────────────
    xml_rec = fk.get(f"tgt_{acc}_ena_xml")
    if xml_rec and xml_rec.get("_status") == "read":
        rec["ena"]["xml_titles"] = _xml_titles(xml_rec.get("body") or "")
    elif xml_rec:
        rec["ena"]["xml_status"] = xml_rec.get("_status")

    # ── Q2: what ARE the runs? Four counts, measured separately, never inferred ────────────────
    if runs:
        rec["runs"] = {
            "n_runs": len(runs),
            "n_distinct_experiments": len(_uniq(r.get("experiment_accession") for r in runs)),
            "n_distinct_samples": len(_uniq(r.get("sample_accession") for r in runs)),
            "n_distinct_studies": len(_uniq(r.get("study_accession") for r in runs)),
            "⚠ note": "these are FOUR different numbers. n_runs is not a patient count; a deposit "
                      "with more runs than samples is re-sequencing or multi-arm, and that is what "
                      "n_distinct_samples measures",
            "library_strategy_values": _uniq(r.get("library_strategy") for r in runs),
            "library_source_values": _uniq(r.get("library_source") for r in runs),
            "library_selection_values": _uniq(r.get("library_selection") for r in runs),
            "library_layout_values": _uniq(r.get("library_layout") for r in runs),
            "instrument_platform_values": _uniq(r.get("instrument_platform") for r in runs),
            "instrument_model_values": _uniq(r.get("instrument_model") for r in runs),
            "scientific_name_values": _uniq(r.get("scientific_name") for r in runs),
            "study_title_values": _uniq(r.get("study_title") for r in runs),
            "sample_titles": [r.get("sample_title") for r in runs],
            "sample_aliases": [r.get("sample_alias") for r in runs],
            "library_names": [r.get("library_name") for r in runs],
            "first_public_values": _uniq(r.get("first_public") for r in runs),
            "read_counts": [r.get("read_count") for r in runs],
        }
        prose = []
        for r in runs:
            prose += [r.get(k) for k in ("library_strategy", "library_selection", "library_name",
                                         "experiment_title", "study_title", "sample_title",
                                         "description", "sample_alias")]
        rec["runs"]["assay_probes"] = _probe_assays([p for p in prose if p])

        # ── Q3: public metadata vs public DATA. The distinguishing field is the file list. ─────
        with_fastq = [r for r in runs if (r.get("fastq_ftp") or "").strip()]
        with_submitted = [r for r in runs if (r.get("submitted_ftp") or "").strip()]
        total_bytes = 0
        for r in with_fastq:
            for b in (r.get("fastq_bytes") or "").split(";"):
                try:
                    total_bytes += int(b)
                except (TypeError, ValueError):
                    pass
        rec["data_availability"] = {
            "n_runs_with_fastq_ftp": len(with_fastq),
            "n_runs_with_submitted_ftp": len(with_submitted),
            "total_fastq_bytes": total_bytes or None,
            "state": ("PUBLIC_DOWNLOADABLE" if with_fastq else
                      ("REGISTERED_METADATA_ONLY" if runs else "UNKNOWN")),
            "⚠ note": "a run with metadata and no file list is registered and NOT downloadable — "
                      "an embargoed deposit looks exactly like a public one until this field is "
                      "read",
        }

    # ── Q2 again, from the OTHER archive: NCBI's full SRA XML ─────────────────────────────────
    ef = fk.get(f"tgt_{acc}_sra_efetch_xml")
    if ef and ef.get("_status") == "read":
        rec["ncbi_sra_xml"] = _sra_xml_summary(ef.get("body") or "",
                                              truncated=bool(ef.get("⚠ payload_truncated")))

    # ── Q2: is any of it EMC? ─────────────────────────────────────────────────────────────────
    study_prose = []
    for t in titles:
        study_prose += [t.get("project_title"), t.get("project_name"), t.get("project_description")]
    study_prose += (rec.get("ena", {}).get("xml_titles") or [])
    if runs:
        study_prose += rec["runs"]["study_title_values"]
    study_hit = EMC_TOKENS.search(" || ".join(p for p in study_prose if p))

    sample_prose = []
    if runs:
        for r in runs:
            sample_prose.append(" ".join(str(r.get(k) or "") for k in
                                         ("sample_title", "sample_alias", "library_name",
                                          "description", "experiment_title")))
    if samples:
        for s in samples:
            sample_prose.append(" ".join(str(s.get(k) or "") for k in
                                         ("sample_title", "sample_alias", "description")))
    for attrs in (rec.get("ncbi_sra_xml", {}) or {}).get("sample_attribute_blobs", []):
        sample_prose.append(attrs)

    rec["emc_evidence"] = {
        "study_level_prose_names_emc": bool(study_hit),
        "study_level_matched_text": (study_hit.group(0) if study_hit else None),
        "n_sample_blobs_read": len(sample_prose),
        "n_sample_blobs_naming_emc_strict": sum(
            1 for p in sample_prose if EMC_STRICT_TOKENS.search(p)),
        "n_sample_blobs_naming_emc_loose": sum(1 for p in sample_prose if EMC_TOKENS.search(p)),
        "⚠ note": "zero sample blobs read means the sample level could NOT be inspected — it is "
                  "not evidence that the samples are not EMC (CLAUDE.md §4)",
    }
    return rec


def _xml_titles(body):
    out = []
    try:
        root = ET.fromstring(body)
    except Exception:                                        # noqa: BLE001
        return out
    for tag in ("TITLE", "NAME", "DESCRIPTION", "STUDY_TITLE", "STUDY_ABSTRACT"):
        for el in root.iter(tag):
            if el.text and el.text.strip():
                out.append(el.text.strip()[:2000])
    return _uniq(out)


def _sra_xml_summary(body, truncated=False):
    """Per-run library/platform and the BioSample attribute lists, from NCBI's own document."""
    out = {"_parsed": False, "⚠ payload_was_truncated": truncated}
    try:
        root = ET.fromstring(body)
    except Exception as exc:                                 # noqa: BLE001
        out["parse_error"] = f"{type(exc).__name__}: {exc}"[:200]
        if truncated:
            out["⚠ note"] = ("the payload was truncated before parsing, so this parse failure is "
                             "an artefact of truncation and NOT evidence about the record")
        return out
    out["_parsed"] = True
    pkgs = list(root.iter("EXPERIMENT_PACKAGE"))
    out["n_experiment_packages"] = len(pkgs)
    strategies, platforms, selections, sources, run_accs, sample_accs, blobs, titles = (
        [], [], [], [], [], [], [], [])
    for p in pkgs:
        for el in p.iter("LIBRARY_STRATEGY"):
            strategies.append((el.text or "").strip())
        for el in p.iter("LIBRARY_SELECTION"):
            selections.append((el.text or "").strip())
        for el in p.iter("LIBRARY_SOURCE"):
            sources.append((el.text or "").strip())
        for el in p.iter("INSTRUMENT_MODEL"):
            platforms.append((el.text or "").strip())
        for el in p.iter("RUN"):
            if el.get("accession"):
                run_accs.append(el.get("accession"))
        for el in p.iter("SAMPLE"):
            if el.get("accession"):
                sample_accs.append(el.get("accession"))
        for el in p.iter("TITLE"):
            if el.text and el.text.strip():
                titles.append(el.text.strip()[:500])
        for el in p.iter("SAMPLE_ATTRIBUTE"):
            tag = "".join((el.findtext("TAG") or "").split())
            val = (el.findtext("VALUE") or "").strip()
            if tag or val:
                blobs.append(f"{tag}={val}")
    out["library_strategy_values"] = _uniq(strategies)
    out["library_selection_values"] = _uniq(selections)
    out["library_source_values"] = _uniq(sources)
    out["instrument_model_values"] = _uniq(platforms)
    out["n_runs"] = len(run_accs)
    out["run_accessions"] = run_accs
    out["n_distinct_samples"] = len(_uniq(sample_accs))
    out["sample_accessions"] = _uniq(sample_accs)
    out["titles"] = _uniq(titles)
    out["sample_attribute_blobs"] = blobs
    out["assay_probes"] = _probe_assays(strategies + selections + sources + titles + blobs)
    return out


def derive(inputs):
    fk = _by_key(inputs)
    controls, transport_ok = _control_gate(fk)
    targets = {acc: _read_target(fk, acc)
               for acc in (inputs.get("target_bioproject") or TARGET_BIOPROJECT,
                           inputs.get("target_sra_study") or TARGET_SRA_STUDY)}

    # ── Did the target resolve, in EITHER archive? ────────────────────────────────────────────
    def saw(t):
        n = t["ncbi"]
        counts = [n.get("bioproject_esearch_count"), n.get("sra_esearch_count"),
                  n.get("biosample_esearch_count")]
        ncbi_hit = any(isinstance(c, int) and c > 0 for c in counts)
        ena_hit = bool(t["ena"].get("n_read_run_rows"))
        return ncbi_hit or ena_hit

    resolved = {acc: saw(t) for acc, t in targets.items()}
    any_resolved = any(resolved.values())

    # ── The pairing claim in the hand-over, checked rather than assumed ───────────────────────
    bp, st = TARGET_BIOPROJECT, TARGET_SRA_STUDY
    pairing = {"claim": f"{bp} and {st} are the same deposit"}
    bp_runs = ((targets.get(bp) or {}).get("runs") or {})
    st_runs = ((targets.get(st) or {}).get("runs") or {})
    if bp_runs and st_runs:
        a = set(bp_runs.get("sample_titles") or [])
        b = set(st_runs.get("sample_titles") or [])
        pairing["both_resolved"] = True
        pairing["same_run_count"] = bp_runs.get("n_runs") == st_runs.get("n_runs")
        pairing["sample_title_overlap"] = len(a & b)
        pairing["verdict"] = ("CONSISTENT" if pairing["same_run_count"] and (a & b or not a)
                              else "⚠ INCONSISTENT — they do not look like the same deposit")
    else:
        pairing["both_resolved"] = False
        pairing["verdict"] = "UNTESTED — at least one side returned no runs"

    # ── VERDICT ──────────────────────────────────────────────────────────────────────────────
    # ⛔ THE TRANSPORT GATE COMES FIRST AND OVERRIDES EVERYTHING. A negative from a search that
    # could not reach the archive is not a negative.
    if not transport_ok:
        failed = [k for k, v in controls.items() if not v.get("passed")]
        verdict = {
            "grade": "UNREADABLE_TRANSPORT",
            "headline": (f"the control gate FAILED ({', '.join(failed)}), so nothing here is a "
                         f"reading of the target — re-run before quoting any of it"),
            "⛔ scope": "an absent reading is not a reading of absence (CLAUDE.md §4)",
            "controls_failed": failed,
        }
    elif not any_resolved:
        verdict = {
            "grade": "NOT_FOUND",
            "headline": (f"neither {bp} nor {st} resolved in NCBI or ENA, while both positive "
                         f"controls did and the absent control did not — the accessions as given "
                         f"do not name a public record"),
            "⛔ scope": "this is a statement about these two accession STRINGS in these two "
                       "archives on the fetch date, not about whether an EMC deposit exists",
        }
    else:
        # It resolved. Now: is it EMC, what is it, and can the data be had?
        best = max((t for t in targets.values() if saw(t)),
                   key=lambda t: (len(((t.get("runs") or {}).get("sample_titles")) or []),
                                  (t.get("runs") or {}).get("n_runs") or 0))
        runs = best.get("runs") or {}
        avail = best.get("data_availability") or {}
        emc = best.get("emc_evidence") or {}
        xml = best.get("ncbi_sra_xml") or {}
        n_runs = runs.get("n_runs") or xml.get("n_runs")
        n_samples = runs.get("n_distinct_samples") or xml.get("n_distinct_samples")
        strategies = _uniq((runs.get("library_strategy_values") or []) +
                           (xml.get("library_strategy_values") or []))
        probes = runs.get("assay_probes") or xml.get("assay_probes") or {}
        is_tempo = bool((probes.get("tempo_seq") or {}).get("matched"))
        sample_level_read = (emc.get("n_sample_blobs_read") or 0) > 0
        n_emc_samples = emc.get("n_sample_blobs_naming_emc_strict")

        if not emc.get("study_level_prose_names_emc") and not n_emc_samples:
            grade = "RESOLVED_NOT_EMC"
            head = ("the record exists but nothing in its study prose or its sample metadata names "
                    "extraskeletal myxoid chondrosarcoma or the NR4A3 fusion — it is not an EMC "
                    "cohort")
        elif not sample_level_read:
            grade = "UNGRADED_NO_SAMPLE_LEVEL_READ"
            head = ("the record exists and its study prose names EMC, but NO sample-level metadata "
                    "could be read, so what the runs actually are is unknown — this is not a "
                    "fourth cohort until the samples are read")
        elif avail.get("state") != "PUBLIC_DOWNLOADABLE":
            grade = "EMC_BUT_DATA_NOT_PUBLIC"
            head = (f"an EMC deposit with {n_runs} runs over {n_samples} samples exists, but "
                    f"{avail.get('n_runs_with_fastq_ftp')} runs carry a downloadable file list — "
                    f"the METADATA is public and the DATA is not")
        else:
            grade = "EMC_PUBLIC_CANDIDATE"
            head = (f"an EMC deposit with {n_runs} runs over {n_samples} samples is public and "
                    f"downloadable; library strategy {strategies or 'unreported'}")
        verdict = {
            "grade": grade,
            "headline": head,
            "n_runs_measured": n_runs,
            "n_distinct_samples_measured": n_samples,
            "library_strategy_values": strategies,
            "assay_probe_tempo_seq_matched": is_tempo,
            "assay_probe_matched_text": (probes.get("tempo_seq") or {}).get("matched_text"),
            "n_sample_blobs_naming_emc_strict": n_emc_samples,
            "data_availability_state": avail.get("state"),
            "⛔ scope": ("run count is not patient count; n_distinct_samples is the closest thing "
                        "to a biological n that this metadata supports, and even that counts "
                        "BioSamples rather than people"),
        }

    return {
        "_generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_inputs_generated_utc": inputs.get("_generated_utc"),
        "_question": ("is PRJNA1357027 / SRP640302 a fourth EMC cohort, and is it readable? "
                      "The GEO-side search (emc_cohort_search.py, and §3.13 of the "
                      "transcriptional-output manuscript) cannot see an SRA-only deposit"),
        "target_bioproject": TARGET_BIOPROJECT,
        "target_sra_study": TARGET_SRA_STUDY,
        "transport_controls": controls,
        "transport_gate_passed": transport_ok,
        "targets": targets,
        "resolved": resolved,
        "pairing_check": pairing,
        "verdict": verdict,
    }


# =================================================================================================
# SELFTEST — runs BEFORE the fetch in CI, so a broken derivation costs seconds not a run
# =================================================================================================
def selftest():
    def synth(fetches, tb=TARGET_BIOPROJECT, ts=TARGET_SRA_STUDY):
        return {"target_bioproject": tb, "target_sra_study": ts, "fetches": fetches}

    def es(key, count, ids=None):
        return {"key": key, "_status": "read",
                "json": {"esearchresult": {"count": str(count),
                                           "idlist": ids or [str(i) for i in range(count)]}}}

    def ena(key, rows, header=None):
        header = header or ENA_RUN_FIELDS
        body = "\t".join(header) + "\n" + "\n".join(
            "\t".join(str(r.get(h, "")) for h in header) for r in rows)
        return {"key": key, "_status": "read", "body": body}

    def good_controls():
        out = []
        for key, c in CONTROLS.items():
            n = 0 if c["expect"] == "zero" else 1
            out += [es(f"{key}_bioproject_esearch", n), es(f"{key}_sra_esearch", n),
                    ena(f"{key}_ena_read_run", [{"run_accession": "SRR1"}] * n)]
        return out

    # 1. A clean absence: controls pass, target invisible -> NOT_FOUND.
    r = derive(synth(good_controls() +
                     [es(f"tgt_{TARGET_BIOPROJECT}_bioproject_esearch", 0),
                      es(f"tgt_{TARGET_SRA_STUDY}_sra_esearch", 0)]))
    assert r["verdict"]["grade"] == "NOT_FOUND", r["verdict"]

    # 2. ⛔ THE CENTRAL INVARIANT. Same invisible target, but a positive control also went dark.
    #    This must NOT read as NOT_FOUND.
    dead = [f for f in good_controls()
            if not f["key"].startswith("ctrl_real_bioproject")]
    dead += [es("ctrl_real_bioproject_bioproject_esearch", 0),
             es("ctrl_real_bioproject_sra_esearch", 0),
             ena("ctrl_real_bioproject_ena_read_run", [])]
    r = derive(synth(dead + [es(f"tgt_{TARGET_BIOPROJECT}_bioproject_esearch", 0)]))
    assert r["verdict"]["grade"] == "UNREADABLE_TRANSPORT", r["verdict"]
    assert "ctrl_real_bioproject" in r["verdict"]["controls_failed"]

    # 3. The NEGATIVE control is load-bearing too: if an accession that cannot exist comes back
    #    populated, the matcher is loose and no positive means anything.
    loose = [f for f in good_controls() if not f["key"].startswith("ctrl_absent")]
    loose += [es("ctrl_absent_bioproject_esearch", 3), es("ctrl_absent_sra_esearch", 0),
              ena("ctrl_absent_ena_read_run", [])]
    r = derive(synth(loose + [es(f"tgt_{TARGET_BIOPROJECT}_bioproject_esearch", 0)]))
    assert r["verdict"]["grade"] == "UNREADABLE_TRANSPORT", r["verdict"]
    assert "ctrl_absent" in r["verdict"]["controls_failed"]

    # 4. Resolves, but nothing anywhere says EMC -> RESOLVED_NOT_EMC, never a cohort.
    rows = [{"run_accession": f"SRR{i}", "sample_accession": f"SAMN{i}",
             "experiment_accession": f"SRX{i}", "study_accession": TARGET_BIOPROJECT,
             "library_strategy": "RNA-Seq", "sample_title": f"liver donor {i}",
             "fastq_ftp": f"ftp/x{i}.fastq.gz", "fastq_bytes": "100"} for i in range(12)]
    r = derive(synth(good_controls() +
                     [es(f"tgt_{TARGET_BIOPROJECT}_bioproject_esearch", 1),
                      ena(f"tgt_{TARGET_BIOPROJECT}_ena_read_run", rows)]))
    assert r["verdict"]["grade"] == "RESOLVED_NOT_EMC", r["verdict"]

    # 5. EMC prose, 12 runs, files present -> a public candidate; and the run/sample counts must
    #    stay SEPARATE numbers. Six samples sequenced twice is not twelve patients.
    rows = [{"run_accession": f"SRR{i}", "sample_accession": f"SAMN{i // 2}",
             "experiment_accession": f"SRX{i}", "study_accession": TARGET_BIOPROJECT,
             "library_strategy": "OTHER", "library_selection": "other",
             "library_name": "TempO-Seq S1500+",
             "sample_title": f"extraskeletal myxoid chondrosarcoma case {i // 2}",
             "study_title": "Prognostic biomarkers in extraskeletal myxoid chondrosarcoma",
             "fastq_ftp": f"ftp/x{i}.fastq.gz", "fastq_bytes": "1000"} for i in range(12)]
    r = derive(synth(good_controls() +
                     [es(f"tgt_{TARGET_BIOPROJECT}_bioproject_esearch", 1),
                      ena(f"tgt_{TARGET_BIOPROJECT}_ena_read_run", rows)]))
    v = r["verdict"]
    assert v["grade"] == "EMC_PUBLIC_CANDIDATE", v
    assert v["n_runs_measured"] == 12, v
    assert v["n_distinct_samples_measured"] == 6, (
        "run count leaked into sample count — the whole '12 runs is not 12 patients' guard")
    assert v["assay_probe_tempo_seq_matched"] is True, v

    # 6. Same deposit, files withheld -> the data are NOT public, and that is a different grade.
    for row in rows:
        row["fastq_ftp"] = ""
        row["fastq_bytes"] = ""
    r = derive(synth(good_controls() +
                     [es(f"tgt_{TARGET_BIOPROJECT}_bioproject_esearch", 1),
                      ena(f"tgt_{TARGET_BIOPROJECT}_ena_read_run", rows)]))
    assert r["verdict"]["grade"] == "EMC_BUT_DATA_NOT_PUBLIC", r["verdict"]

    # 7. Study prose names EMC but NO sample level was readable -> UNGRADED, never a cohort.
    r = derive(synth(good_controls() + [
        es(f"tgt_{TARGET_BIOPROJECT}_bioproject_esearch", 1),
        {"key": f"tgt_{TARGET_BIOPROJECT}_bioproject_esummary", "_status": "read",
         "json": {"result": {"uids": ["1"], "1": {
             "project_acc": TARGET_BIOPROJECT,
             "project_title": "Extraskeletal myxoid chondrosarcoma prognostic biomarkers"}}}}]))
    assert r["verdict"]["grade"] == "UNGRADED_NO_SAMPLE_LEVEL_READ", r["verdict"]

    # 8. A failed esearch is not a zero.
    assert _esearch_count({"key": "x", "_status": "failed"}) == (None, None, "failed")
    assert _esearch_count(None) == (None, None, "absent")

    # 9. An ENA response with only a header row is zero rows, not a parse failure.
    rows_out, st = _tsv_rows({"_status": "read", "body": "run_accession\tlibrary_strategy\n"})
    assert st == "read" and rows_out == [], (st, rows_out)

    print("selftest OK — 9 checks, including the transport gate in both directions")
    return True


# =================================================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fetch", action="store_true", help="hit NCBI + ENA and rewrite the cache")
    ap.add_argument("--check", action="store_true", help="re-derive and diff against the artifact")
    ap.add_argument("--selftest", action="store_true", help="offline invariants; no network")
    a = ap.parse_args()

    if a.selftest:
        selftest()
        return 0

    if a.fetch:
        inputs = fetch()
        print(f"fetched {len(inputs['fetches'])} payloads -> {os.path.basename(INPUTS)}")
    else:
        if not os.path.exists(INPUTS):
            print(f"no cached inputs at {INPUTS}; run with --fetch (needs network)",
                  file=sys.stderr)
            return 2
        with open(INPUTS, "r", encoding="utf-8") as fh:
            inputs = json.load(fh)

    res = derive(inputs)

    if a.check:
        if not os.path.exists(OUT):
            print(f"no committed artifact at {OUT} to check against", file=sys.stderr)
            return 2
        with open(OUT, "r", encoding="utf-8") as fh:
            old = json.load(fh)
        drift = [k for k in ("verdict", "resolved", "transport_gate_passed")
                 if json.dumps(old.get(k), sort_keys=True) != json.dumps(res.get(k),
                                                                         sort_keys=True)]
        if drift:
            print(f"⚠ DRIFT in {drift}: the committed artifact does not re-derive from its "
                  f"own cached payloads")
            return 1
        print("--check OK — the verdict re-derives from the cached payloads")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print(f"{res['verdict']['grade']}: {res['verdict']['headline']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
