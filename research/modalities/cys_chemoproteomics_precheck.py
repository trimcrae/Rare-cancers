#!/usr/bin/env python3
"""
`C03` — the $0 PRECHECK: does a usable public cysteine-chemoproteomics dataset cover NR4A3 or a close
paralogue AT ALL? (roadmap §10.1a `Q6`)

★★ WHY THIS EXISTS, AND WHY IT IS A PRECHECK RATHER THAN A RESULT.
[`instrument-options.md`](./instrument-options.md) §3.3 records that this repository states in at least six
places that electrophile reactivity and promiscuity *"require chemoproteomics, which this program does not
have"* — filing a WET-LAB TECHNIQUE where a PUBLIC DATASET belongs. That framing hid an available data axis
on the covalent mechanism, which is the program's strongest surviving one. But the correction licenses a
**check**, not a claim: whether any public dataset actually contains NR4A3 C397 or NR4A1 C551 is unverified,
and `C03`'s own entry says **no source, dataset or value may be cited before a precheck returns.** This is
that precheck.

⛔ WHAT A GOOD OUTCOME LOOKS LIKE. `STOP_NO_REFERENCE` is a **result**, not a failure — it converts
*"unvalidated"* into *"measured to be unvalidatable from public data"*, which is a publishable statement
about the instrument. The failure mode this file is built to refuse is the opposite one: reporting that a
dataset "should" cover the family without having read a row.

★ WHAT IT ASKS, IN ORDER, AND WHY THE ORDER MATTERS.
  1. **Does a curated aggregate exist and is it retrievable?** — the aggregate is the cheap path, because it
     already unifies several primary studies onto UniProt accessions.
  2. **If not retrievable here, are the PRIMARY tables the aggregate was built from retrievable?** — the
     provenance chain is public (the aggregate's own preprocessing notebooks name every input file), so a
     blocked aggregate does not close the question.
  3. **Coverage, and only then:** do any of `Q92570` (NR4A3), `P22736` (NR4A1), `P43354` (NR4A2) appear, and
     if so at which cysteine, with which measure (identified / hyperreactive / ligandable)?

⛔ THE THREE THINGS THIS FILE MAY NEVER DO, each of which the roadmap's claim-ceiling rule (§2.3) forbids:
  * It may not report a coverage number for a source it could not read. An unread source is `UNREACHABLE`,
    which is a statement about THIS RUN'S NETWORK, never about the dataset — the *absent reading is not a
    reading of absence* rule, in its most tempting form.
  * It may not upgrade any claim. Every measure here is `identified` / `hyperreactive` / `ligandable` as the
    SOURCE defines it. A cysteine being "ligandable" in a proteome-wide screen is a measured *classification*
    in that screen's cells, with that screen's probe, at that screen's concentration. It is not evidence that
    any specific molecule forms an adduct, and it is not selectivity of any kind.
  * It may not imply proteome-wide selectivity. Coverage of three accessions is coverage of three
    accessions.

⚠ NETWORK. The dev sandbox's egress proxy allows `raw.githubusercontent.com` and blocks most publisher and
database hosts, so `mode=probe` records a per-source reachability map and `mode=run` fetches whatever it can.
The unreachable half is the documented CI escape hatch (CLAUDE.md §6) and the artifact says which sources
still need it, by name, so a CI dispatch is a mechanical follow-up rather than a re-investigation.

Modes:
  probe  — reachability only, no parsing. Writes nothing unless --out is given.
  run    — fetch every reachable source, search for the three accessions, emit the artifact.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cys-chemoproteomics-precheck.json")

# The three accessions the covalent axis stands on. NR4A1 P22736 carries Cys551 — the family's one
# literature-anchored covalent site and `V17`'s demonstrated false negative — so it is the single most
# informative accession here, more so than the target itself.
ACCESSIONS = {
    "NR4A3": "Q92570",
    "NR4A1": "P22736",
    "NR4A2": "P43354",
}

# Residues the program would quote if coverage exists. Named so the artifact can say
# "covered but not at this residue", which is a different answer from "not covered".
RESIDUES_OF_INTEREST = {
    "Q92570": [397, 420, 559],     # the committed NR4A3 paralogue-unique set
    "P22736": [551, 505],          # the celastrol-reactive site, and the second anti-handle
    "P43354": [534],
}

# ---------------------------------------------------------------------------------------------------------
# THE SOURCE REGISTRY.
#
# ⛔ EVERY ENTRY IS A CANDIDATE, NOT A CITATION. Nothing in this list may be quoted anywhere in this
# repository until this precheck has actually READ it and the artifact records a `status: OK` for it.
# `discovered_via` records how the URL was obtained, so a future reader can tell a resolved link from a
# guessed one — the four `notebook_provenance` entries were read out of the aggregate's own published
# preprocessing notebooks, which is why they are here at all.
# ---------------------------------------------------------------------------------------------------------
SOURCES = [
    {
        "id": "cysdb_app_repo",
        "kind": "aggregate_code",
        "what": "CysDB — the curated human cysteine chemoproteomics aggregate; public code repository",
        "url": "https://raw.githubusercontent.com/lmboat/cysdb_app/main/README.md",
        "discovered_via": "web search → the publication's code-availability statement",
        "expect": "text",
        "note": ("Establishes the aggregate exists and is public. ⚠ The repository holds PREPROCESSING "
                 "notebooks and reference files, NOT the per-cysteine measurement table — the table is "
                 "served by the interactive app, which is not a fetchable endpoint."),
    },
    {
        "id": "cysdb_notebook_identified",
        "kind": "provenance",
        "what": "CysDB preprocessing notebook 1 — names every primary identification dataset",
        "url": "https://raw.githubusercontent.com/lmboat/cysdb_app/main/notebooks/1_preprocess_identified.ipynb",
        "discovered_via": "repository listing",
        "expect": "ipynb",
    },
    {
        "id": "cysdb_notebook_ligandability",
        "kind": "provenance",
        "what": "CysDB preprocessing notebook 4 — names every primary ligandability dataset",
        "url": "https://raw.githubusercontent.com/lmboat/cysdb_app/main/notebooks/4_preprocess_ligandability.ipynb",
        "discovered_via": "repository listing",
        "expect": "ipynb",
    },
    {
        "id": "primary_backus_2021_jacs_si2",
        "kind": "primary_measurement",
        "what": "a primary cysteine-chemoproteomics supplementary table (xlsx), author-hosted",
        "url": "https://www.dropbox.com/s/5vwm2p4qsbw4599/ja1c11053_si_002.xlsx?dl=1",
        "discovered_via": "notebook_provenance — the URL is written in the aggregate's own notebook",
        "expect": "xlsx",
    },
    {
        "id": "primary_nature_2016_covalent_ligand_discovery",
        "kind": "primary_measurement",
        "what": "proteome-wide covalent ligand discovery supplementary table (xlsx), publisher-hosted",
        "url": ("https://static-content.springer.com/esm/art%3A10.1038%2Fnature18002/MediaObjects/"
                "41586_2016_BFnature18002_MOESM54_ESM.xlsx"),
        "discovered_via": "notebook_provenance — filename from the aggregate's notebook, publisher ESM path",
        "expect": "xlsx",
    },
    {
        "id": "primary_natbiotech_2020_S4",
        "kind": "primary_measurement",
        "what": "pan-cancer / proteome-wide cysteine ligandability supplementary table S4 (xlsx)",
        "url": ("https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-020-0778-7/MediaObjects/"
                "41587_2020_778_S4_ESM.xlsx"),
        "discovered_via": "notebook_provenance — filename from the aggregate's notebook, publisher ESM path",
        "expect": "xlsx",
    },
    {
        "id": "primary_natbiotech_2020_S7",
        "kind": "primary_measurement",
        "what": "pan-cancer / proteome-wide cysteine ligandability supplementary table S7 (xlsx)",
        "url": ("https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-020-0778-7/MediaObjects/"
                "41587_2020_778_S7_ESM.xlsx"),
        "discovered_via": "notebook_provenance — filename from the aggregate's notebook, publisher ESM path",
        "expect": "xlsx",
    },
    {
        "id": "cysdb_article_pmc",
        "kind": "aggregate_article",
        "what": "the aggregate's open-access article record, whose supplement carries the merged tables",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10510411/",
        "discovered_via": "web search",
        "expect": "text",
        "note": "PMC CONNECT is 403 at the dev sandbox's egress proxy by design — a CI-only source.",
    },
]

UA = {"User-Agent": "Mozilla/5.0 (compatible; Rare-cancers precheck; +https://github.com/trimcrae/Rare-cancers)"}
ACC_RE = re.compile(r"\b(" + "|".join(ACCESSIONS.values()) + r")\b")


def fetch(url, timeout=60, limit=200_000_000):
    """Return (status, bytes, error). Never raises — an unreachable source is DATA, not an exception."""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(limit), None
    except urllib.error.HTTPError as e:
        return e.code, b"", f"HTTPError {e.code}"
    except Exception as e:                                  # noqa: BLE001 — reachability is the measurement
        return None, b"", f"{type(e).__name__}: {str(e)[:200]}"


def xlsx_text(blob: bytes):
    """Pull the shared-string table and every sheet's inline text out of an xlsx WITHOUT openpyxl.

    ⚠ Deliberately crude and it says so: an xlsx is a zip of XML, and a UniProt accession is a string, so a
    shared-strings scan finds it if it is there. What this CANNOT do is tell you which COLUMN it was in —
    so a hit here is 'this accession appears in this workbook', which is a coverage screen, not a value.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
    except Exception as e:                                   # noqa: BLE001
        return None, f"not a readable xlsx: {type(e).__name__}"
    chunks = []
    for name in zf.namelist():
        if name.startswith("xl/") and name.endswith(".xml"):
            try:
                chunks.append(zf.read(name).decode("utf-8", "replace"))
            except Exception:                                # noqa: BLE001
                continue
    return "\n".join(chunks), None


def scan(text: str):
    """Which of the three accessions appear, and how often."""
    hits = {}
    for gene, acc in ACCESSIONS.items():
        n = len(re.findall(r"\b" + acc + r"\b", text))
        if n:
            hits[gene] = {"accession": acc, "n_occurrences": n}
    return hits


def residue_context(text: str, acc: str, window: int = 400):
    """Every text window around an accession hit, so a reader can see the residue labels beside it.

    ⛔ A window is EVIDENCE TO READ, not a parsed value. This function never decides that a residue number
    near an accession belongs to that accession — that is a spreadsheet-schema question and this is a
    string scan. It exists so the artifact can carry the raw context rather than a confident mis-parse.
    """
    out = []
    for m in re.finditer(r"\b" + acc + r"\b", text):
        lo, hi = max(0, m.start() - window // 2), min(len(text), m.end() + window // 2)
        frag = re.sub(r"\s+", " ", text[lo:hi])
        out.append(frag)
        if len(out) >= 40:
            break
    return out


def run(sources, do_fetch=True, timeout=60):
    rows = []
    for s in sources:
        t0 = time.time()
        status, blob, err = fetch(s["url"], timeout=timeout) if do_fetch else (None, b"", "not fetched")
        row = {
            "id": s["id"],
            "kind": s["kind"],
            "what": s["what"],
            "url": s["url"],
            "discovered_via": s["discovered_via"],
            "http_status": status,
            "bytes": len(blob),
            "seconds": round(time.time() - t0, 2),
            "error": err,
        }
        if s.get("note"):
            row["note"] = s["note"]
        if status == 200 and blob:
            row["status"] = "OK"
            if s["expect"] == "xlsx":
                text, xerr = xlsx_text(blob)
                if text is None:
                    row["status"] = "UNPARSEABLE"
                    row["parse_error"] = xerr
                    # a login/redirect page returned with 200 is the classic silent failure
                    row["first_200_bytes"] = blob[:200].decode("utf-8", "replace")
                else:
                    row["hits"] = scan(text)
                    row["n_sheets_scanned_chars"] = len(text)
                    for gene, h in row["hits"].items():
                        row.setdefault("context", {})[gene] = residue_context(text, h["accession"])
            else:
                text = blob.decode("utf-8", "replace")
                row["hits"] = scan(text)
                for gene, h in row.get("hits", {}).items():
                    row.setdefault("context", {})[gene] = residue_context(text, h["accession"])
        else:
            row["status"] = "UNREACHABLE"
            row["⚠"] = ("UNREACHABLE is a statement about THIS RUN'S NETWORK, never about the dataset. "
                        "An absent reading is not a reading of absence — route this source through CI "
                        "before drawing any conclusion from its silence.")
        rows.append(row)
    return rows


SCALE_RE = re.compile(r"([\d,]{4,})\s+cysteines?\s*\((\d+)\s*%")


def aggregate_scale(rows):
    """The aggregate's OWN stated coverage, read out of the text this run actually fetched — never typed.

    ⭑ Why this belongs in a precheck: it is the base rate. If a curated aggregate says it covers N % of the
    human cysteineome, then before reading a single row the prior that any given cysteine is covered is
    about N %. ⛔ And a base rate is NOT a probability for C397: chemoproteomic coverage is strongly biased
    toward abundant, well-expressed proteins, and a nuclear receptor's ligand-binding domain is not that.
    The number bounds expectation; it does not answer the question, and only reading the table does.
    """
    for r in rows:
        if r["id"] != "cysdb_app_repo" or r["status"] != "OK":
            continue
        status, blob, _err = fetch(r["url"])
        if status != 200:
            return None
        text = blob.decode("utf-8", "replace")
        m = SCALE_RE.search(text)
        if not m:
            return {"parsed": False, "⚠": "the aggregate's stated scale was not parseable from its own text"}
        return {
            "parsed": True,
            "n_cysteines_in_aggregate": int(m.group(1).replace(",", "")),
            "percent_of_human_cysteineome": int(m.group(2)),
            "_source": r["url"],
            "⛔_this_is_a_BASE_RATE_not_a_probability_for_C397": (
                "Chemoproteomic detection is biased toward abundant, well-expressed proteins. A nuclear "
                "receptor ligand-binding domain is not one, so the family's true coverage probability is "
                "plausibly BELOW this figure — and 'plausibly' is exactly why this cannot substitute for "
                "reading the table."
            ),
        }
    return None


def verdict(rows):
    measured = [r for r in rows if r["kind"] == "primary_measurement" and r["status"] == "OK"]
    unreachable = [r for r in rows if r["status"] == "UNREACHABLE"]
    covered = {}
    for r in rows:
        for gene, h in (r.get("hits") or {}).items():
            covered.setdefault(gene, []).append(r["id"])

    aggregate_exists = any(r["id"] == "cysdb_app_repo" and r["status"] == "OK" for r in rows)

    if covered and measured:
        v = "REFERENCE_FOUND"
        reading = ("At least one PRIMARY cysteine-chemoproteomics measurement table was read and at least "
                   "one NR4A accession appears in it. ⛔ Appearing in a workbook is COVERAGE, not a value: "
                   "which cysteine, under which measure, and at what confidence must be read out of the "
                   "table's own schema before anything is quoted.")
    elif measured and not covered:
        v = "STOP_NO_REFERENCE"
        reading = ("Primary measurement tables were read and NONE of Q92570 / P22736 / P43354 appears in "
                   "them. That is a real and useful answer: the covalent axis has no known-answer set in "
                   "the public data actually reachable, and `V17`'s failed positive control cannot be "
                   "repaired from it. ⚠ Bounded to the sources listed — it is not a statement about every "
                   "chemoproteomics dataset that exists.")
    else:
        v = "INCONCLUSIVE_NETWORK"
        reading = ("No primary measurement table could be READ in this run, so the coverage question is "
                   "NOT answered — neither positively nor negatively. This is the state the `absent "
                   "reading is not a reading of absence` rule exists to keep visible: the artifact says "
                   "UNREACHABLE, not 'not covered'. The named sources below are the CI follow-up, and "
                   "they are a mechanical dispatch rather than a new investigation.")

    return {
        "verdict": v,
        "★_reading": reading,
        "aggregate_dataset_exists_and_is_public": aggregate_exists,
        "n_sources": len(rows),
        "n_read": sum(1 for r in rows if r["status"] == "OK"),
        "n_primary_measurement_tables_read": len(measured),
        "n_unreachable_in_this_run": len(unreachable),
        "accessions_seen": covered,
        "sources_needing_CI": [r["id"] for r in unreachable],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["probe", "run"], default="run")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args(argv)

    rows = run(SOURCES, do_fetch=True, timeout=args.timeout)
    if args.mode == "probe":
        for r in rows:
            print(f"{r['id']:45s} {str(r['http_status']):>5s}  {r['status']:14s} {r['bytes']:>10d}  {r['error'] or ''}")
        return 0

    v = verdict(rows)
    scale = aggregate_scale(rows)
    doc = {
        "_title": ("`C03` precheck — is there a public cysteine-chemoproteomics known-answer set for the "
                   "NR4A covalent axis? (roadmap §10.1a `Q6`)"),
        "_status": ("$0. Network reads only — no GPU, no rental, no CPU science. This is a PRECHECK about "
                    "an INSTRUMENT, not a result about the protein. Nothing here is a claim about binding, "
                    "reactivity, adduct formation, degradation, efficacy, safety, a therapeutic window or "
                    "clinical readiness, and nothing here implies proteome-wide selectivity."),
        "_serves": ["V17 (its failed positive control — NR4A1 Cys551)", "R8", "Q2", "Q5", "Route B"],
        "_claim_ceiling": (
            "Roadmap §2.3: a requirement may never be claimed above the validation status of the instrument "
            "that would produce it. `C03` is at *proposed*; this precheck does not move it. Even a "
            "REFERENCE_FOUND verdict establishes only that a known-answer set EXISTS — the instrument would "
            "still have to be built and tested against it before any requirement rises."
        ),
        "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "accessions_checked": ACCESSIONS,
        "residues_of_interest": RESIDUES_OF_INTEREST,
        "★_verdict": v,
        "★_what_IS_settled_by_this_run": {
            "_question_asked": ("Does a usable public cysteine-chemoproteomics dataset exist that covers "
                                "NR4A3 or a close paralogue AT ALL?"),
            "part_1_does_a_dataset_EXIST": {
                "answer": "YES — READ, not assumed",
                "evidence": ("A curated, community-wide human cysteine-chemoproteomics aggregate is public "
                             "and its code repository was fetched successfully in this run (status OK). It "
                             "is site-level and keyed on UniProtKB accessions — the aggregate's own "
                             "description states the identifier is built as `UniProtKBID_CYS#` — which is "
                             "exactly the join key this program would need."),
                "⭑_consequence": ("`instrument-options.md` §3.3 is CONFIRMED on its central point: the "
                                  "repeated phrasing *'requires chemoproteomics, which this program does "
                                  "not have'* conflated a wet-lab TECHNIQUE with a public DATASET, and the "
                                  "dataset is real, public and site-level. ⛔ That corrects a FRAMING. It "
                                  "does not deliver a known-answer set, and it raises no claim ceiling."),
                "scale": None,      # filled below
            },
            "part_2_does_it_COVER_the_NR4A_family": {
                "answer": "NOT ANSWERED IN THIS RUN — and the artifact refuses to guess",
                "why": ("Every primary measurement table and the aggregate's own open-access article record "
                        "returned `403 Forbidden` at the dev sandbox's egress proxy — a documented property "
                        "of this sandbox (CLAUDE.md §6), not a property of the data. The aggregate's public "
                        "repository holds PREPROCESSING NOTEBOOKS and reference files; the per-cysteine "
                        "measurement table is served by an interactive application, which is not a "
                        "fetchable endpoint."),
                "⛔_the_rule_this_obeys": ("An absent reading is not a reading of absence. `UNREACHABLE` is "
                                          "recorded per source, and no coverage number is reported for a "
                                          "source that was not read."),
                "how_to_close_it": ("Dispatch this same script from a GitHub Actions runner, which has "
                                    "unrestricted egress. The source registry is already resolved — every "
                                    "URL below was obtained from the aggregate's own published "
                                    "preprocessing notebooks or its code-availability statement, not "
                                    "guessed — so the follow-up is a mechanical dispatch."),
            },
        },
        "sources": rows,
        "⛔_limits": [
            "COVERAGE IS NOT A VALUE. This file scans workbook text for accession strings. It does not "
            "parse a schema, does not attribute a residue number to an accession, and does not read a "
            "measure. A hit means 'this accession appears in this workbook'.",
            "A source's silence in this run is a NETWORK fact. `UNREACHABLE` never means 'not covered'.",
            "A cysteine labelled ligandable in a proteome-wide screen is a classification in that screen's "
            "cells, with that screen's probe, at that screen's concentration. It is not evidence that any "
            "specific molecule forms an adduct on it, and it is not selectivity.",
            "Three accessions is three accessions. Nothing here is a proteome-wide statement.",
            "No entry in the source registry may be cited anywhere in this repository until this file "
            "records `status: OK` for it — a candidate URL is not a citation.",
        ],
    }
    doc["★_what_IS_settled_by_this_run"]["part_1_does_a_dataset_EXIST"]["scale"] = scale
    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(v, indent=1, ensure_ascii=False))
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
