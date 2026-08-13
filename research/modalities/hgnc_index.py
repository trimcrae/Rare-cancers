#!/usr/bin/env python3
"""The approved human gene symbol set, its aliases, and its RefSeq accessions — fetched, never typed.

⭐ WHY THIS EXISTS, AND IT CLOSES THREE SEPARATE HOLES AT ONCE (2026-08-13).

**(1) A FUSION TOKEN THAT IS NOT A GENE IS NOT A FUSION.** The census shakeout (run 31740571888)
classified `ACT::FOSB` as `attempted` on 322 supposed junction-directed records, because `ACT` matches
the English word "act". `ACT` is **not an approved HGNC symbol**, so validating both halves of a pair
against this index rejects that row at the source rather than merely flagging it downstream. Query
sharpening treats the symptom; symbol validation removes the cause.

**(2) THE PARENT-ACCESSION ARM OF THE OFF-TARGET SCREEN WAS INERT FOR EVERY NON-EWSR1 DONOR.**
`junction_aso_offtarget.py` says so in its own comment: `PARENT_ACCS` stays EWSR1/NR4A3 "because this
repository holds no verified RefSeq accession for TAF15, TCF12 or FUS, and typing one from memory is
exactly the failure gate 4 exists for." That was the correct refusal and the wrong permanent state. HGNC
publishes `refseq_accession` per gene, openly and with no account, so the accessions arrive as a FETCH:
TAF15 NM_139215, TCF12 NM_003205, FUS NM_004960, TFG NM_006070. ✅ And the two that were hardcoded are
CONFIRMED rather than merely reused — HGNC independently gives EWSR1 NM_005243 and NR4A3 NM_006981.

**(3) THE HAND-WRITTEN ALIAS TABLE GENERALISES.** `_DONOR_ALIASES` covers four genes by hand. HGNC carries
`alias_symbol` and `prev_symbol` for all 45,032 approved genes, which is what a catalog spanning every
recurrent fusion needs.

⛔ AN ALIAS IS NOT A KEY. The same alias can point at more than one approved gene, so `resolve()` returns
an AMBIGUOUS marker rather than picking one. Guessing here would silently retarget a screen at the wrong
transcript, which is worse than declining to resolve.

⚠ WHAT THIS IS NOT. HGNC is a nomenclature authority, not a fusion catalog and not a clinical source. It
says a symbol is approved and what accession it carries; it says nothing about whether a fusion is real,
recurrent, or worth targeting.

Reachable from the dev sandbox (storage.googleapis.com is not behind the egress proxy's 403), so unlike
most fetches here this one can be refreshed locally as well as in CI.

    python3 hgnc_index.py            # fetch + write hgnc-gene-index.json
    python3 hgnc_index.py --check    # verify the committed index against its own invariants
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
#: ⚠ GZIPPED, AND THAT IS A SIZE DECISION NOT A STYLE ONE. 45,032 gene records are ~14 MB pretty-printed
#: and ~9.6 MB compact — too heavy for a git object that is re-fetched wholesale on every HGNC refresh.
#: Gzipped it is ~2 MB, and nothing reads this file by eye: it is an index, consumed through the
#: accessors below.
OUT = os.path.join(HERE, "hgnc-gene-index.json.gz")

HGNC_URL = ("https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/"
            "hgnc_complete_set.txt")
UA = "rare-cancers-research/1.0 (gene symbol index; mailto:trimcrae@gmail.com)"

AMBIGUOUS = "__AMBIGUOUS__"


def fetch_tsv(url=HGNC_URL, timeout=300):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace"), r.status


def build_index(tsv_text):
    """Approved symbols only, with aliases, previous symbols and RefSeq/Ensembl identifiers.

    Columns are read BY NAME. HGNC's schema is stable but not frozen, and a positional read of a file
    that gains a column is a silent mis-parse.
    """
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    required = {"symbol", "status", "alias_symbol", "prev_symbol", "refseq_accession",
                "ensembl_gene_id", "entrez_id", "locus_group"}
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise RuntimeError(f"HGNC schema is missing {sorted(missing)} — refusing to build an index "
                           f"from a file whose shape is not the one this parser was written against")

    genes, alias_to, n_rows, n_withdrawn = {}, {}, 0, 0
    for row in reader:
        n_rows += 1
        if (row.get("status") or "").strip() != "Approved":
            n_withdrawn += 1
            continue
        sym = (row.get("symbol") or "").strip()
        if not sym:
            continue
        aliases = [a for a in (row.get("alias_symbol") or "").split("|") if a]
        prev = [a for a in (row.get("prev_symbol") or "").split("|") if a]
        genes[sym] = {
            "symbol": sym,
            "refseq_accession": (row.get("refseq_accession") or "").strip() or None,
            "ensembl_gene_id": (row.get("ensembl_gene_id") or "").strip() or None,
            "entrez_id": (row.get("entrez_id") or "").strip() or None,
            "locus_group": (row.get("locus_group") or "").strip() or None,
            "alias_symbol": aliases,
            "prev_symbol": prev,
        }
        for a in aliases + prev:
            if a == sym:
                continue
            if a in alias_to and alias_to[a] != sym:
                alias_to[a] = AMBIGUOUS          # never guess between two approved genes
            else:
                alias_to.setdefault(a, sym)
    return genes, alias_to, {"rows_read": n_rows, "not_approved": n_withdrawn}


def _envelope(genes, alias_to, stats, url, status):
    with_refseq = sum(1 for g in genes.values() if g["refseq_accession"])
    return {
        "_what": ("HGNC's approved human gene symbols with aliases, previous symbols and RefSeq / "
                  "Ensembl / Entrez identifiers. The authority for 'is this token a gene?' and for "
                  "'which transcript is this gene's parent?'."),
        "_why": ("Symbol validation rejects fusion tokens that are English words (the census shakeout's "
                 "`ACT::FOSB`), and `refseq_accession` supplies the parent accessions the off-target "
                 "screen previously could not hold without typing them from memory."),
        "⚠_an_alias_is_not_a_key": (
            f"An alias shared by two approved genes resolves to {AMBIGUOUS!r}, never to a guess. "
            "Silently picking one would retarget a screen at the wrong transcript."),
        "⚠_what_this_is_not": ("A nomenclature authority, not a fusion catalog and not a clinical "
                               "source. Nothing here says a fusion is real, recurrent or targetable."),
        "_source_url": url,
        "_http_status": status,
        "n_approved_symbols": len(genes),
        "n_with_refseq_accession": with_refseq,
        "n_alias_keys": len(alias_to),
        "n_ambiguous_aliases": sum(1 for v in alias_to.values() if v == AMBIGUOUS),
        "parse_stats": stats,
        "genes": genes,
        "alias_to_symbol": alias_to,
    }


# ── consumer API (offline; reads the committed index) ───────────────────────────────────────────
_CACHE = None


def load(path=OUT):
    global _CACHE
    if _CACHE is None or _CACHE.get("_path") != path:
        if not os.path.exists(path):
            raise RuntimeError(f"{path} is missing — run `python3 hgnc_index.py` to fetch it. An "
                               "absent index is not an empty one, and must not be treated as one.")
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt") as fh:
            blob = json.load(fh)
        blob["_path"] = path
        _CACHE = blob
    return _CACHE


def is_approved_symbol(sym, path=OUT):
    return (sym or "").strip() in load(path)["genes"]


def resolve(sym, path=OUT):
    """Approved symbol for a token, or None if unknown, or AMBIGUOUS if an alias of several genes."""
    blob = load(path)
    s = (sym or "").strip()
    if s in blob["genes"]:
        return s
    return blob["alias_to_symbol"].get(s)


def refseq_for(sym, path=OUT):
    g = load(path)["genes"].get((sym or "").strip())
    return g["refseq_accession"] if g else None


def aliases_for(sym, path=OUT):
    """Every name a paper might use for this gene: the symbol, its aliases and its previous symbols."""
    g = load(path)["genes"].get((sym or "").strip())
    if not g:
        return ()
    return tuple([g["symbol"]] + list(g["alias_symbol"]) + list(g["prev_symbol"]))


def check(path=OUT):
    blob = load(path)
    problems = []
    if blob["n_approved_symbols"] != len(blob["genes"]):
        problems.append("n_approved_symbols disagrees with the gene table")
    derived_refseq = sum(1 for g in blob["genes"].values() if g["refseq_accession"])
    if derived_refseq != blob["n_with_refseq_accession"]:
        problems.append(f"n_with_refseq_accession {blob['n_with_refseq_accession']} != "
                        f"derived {derived_refseq}")
    derived_amb = sum(1 for v in blob["alias_to_symbol"].values() if v == AMBIGUOUS)
    if derived_amb != blob["n_ambiguous_aliases"]:
        problems.append("n_ambiguous_aliases disagrees with the alias table")
    if problems:
        for p in problems:
            print(f"⛔ {p}", file=sys.stderr)
        return 1
    print(f"✅ HGNC index self-consistent: {blob['n_approved_symbols']} approved symbols, "
          f"{blob['n_with_refseq_accession']} with RefSeq, "
          f"{blob['n_ambiguous_aliases']} ambiguous aliases")
    return 0


def main(argv):
    if "--check" in argv:
        return check()
    text, status = fetch_tsv()
    genes, alias_to, stats = build_index(text)
    blob = _envelope(genes, alias_to, stats, HGNC_URL, status)
    # ⚠ COMPACT ON PURPOSE. Pretty-printing 45,032 nested gene records costs ~14 MB against ~4 MB
    # compact, for a file no human reads by eye — it is an index, consumed through the accessors above.
    # The envelope's own summary fields stay readable at the top of the file, which is the part a
    # reader actually checks.
    opener = gzip.open if OUT.endswith(".gz") else open
    with opener(OUT, "wt") as fh:
        json.dump(blob, fh, separators=(",", ":"), sort_keys=False)
        fh.write("\n")
    print(f"{blob['n_approved_symbols']} approved symbols, "
          f"{blob['n_with_refseq_accession']} with RefSeq accession, "
          f"{blob['n_ambiguous_aliases']} ambiguous aliases -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
