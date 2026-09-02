#!/usr/bin/env python3
"""
Does the EMC "untranslated acceptor sequence gets translated" trap generalise across recurrent
fusion oncogenes, or is it a local curiosity of NR4A3?

THE QUESTION
------------
`research/manuscripts/emc-atr-collaborator-package.md` establishes, for ONE ultra-rare cancer,
that a fusion construct assembled by joining the two partners' CODING sequences can be the wrong
protein. Two conditions have to coincide:

  (i)  the 3' partner's breakpoint lands in sequence that is NOT protein-coding in that gene -- a
       wholly non-coding exon, or the 5' untranslated part of the exon that carries its initiator
       codon; and
  (ii) the 5' partner's retained coding sequence ends at a non-zero phase, i.e. part-way through
       a codon.

When both hold, the fusion mRNA is read continuously through sequence that is untranslated in the
native gene, and the protein carries residues NEITHER partner contributes in its own frame. A
construct built from the two CDSs omits them. In the worked EMC case the omission is 59 residues.

Neither condition is a property of NR4A3. Both are properties of gene architecture. Nobody had
checked whether they coincide anywhere else. This module checks.

WHAT IS MEASURED, AND WHAT IS NOT
---------------------------------
MEASURED. For every fusion in the catalogue, from the Ensembl canonical transcript of each
partner:
  * L  -- nucleotides of 5'-partner CODING sequence retained through its breakpoint exon;
  * phase = L mod 3 -- condition (ii) is `phase != 0`;
  * U  -- nucleotides of the 3' partner's retained transcript that lie 5' of its own initiator
          codon; condition (i) is `U > 0`;
  * whether the acceptor's own reading frame resumes, `(L + U) mod 3 == 0`;
  * the residue count a CDS-on-CDS construct would omit, `(L mod 3 + U) / 3`.

NOT MEASURED, and it must not be read in. Nothing here is an efficacy, potency, selectivity,
safety, tolerability or clinical claim, and nothing here says any of these constructs was ever
built. This is exon arithmetic over public reference transcripts plus breakpoints quoted from
fetched literature records.

THE ANTI-FABRICATION GATE, WHICH IS THE POINT OF THE FILE LAYOUT
---------------------------------------------------------------
A breakpoint typed from recollection is exactly the failure class this repository spent
2026-08-07 correcting (CLAUDE.md section 7, gate 4). So NO exon number in this analysis is typed
into a Python literal. Every one lives in `fusion-frame-trap-breakpoints.json` beside a VERBATIM
QUOTE and the Europe PMC identifier it came from, and `verify_quotes()` refuses to run unless
each quote is found character-for-character inside the abstract that identifier returned into the
committed corpus. A row whose quote cannot be located is a hard error, not a warning.

Consequence, deliberately accepted: a fusion whose breakpoint could not be sourced is EXCLUDED
and counted as INDETERMINATE. An unresolvable case is not a negative case, and the memo reports
the indeterminate count beside the positive one.

NUMBERING RISK, STATED RATHER THAN ASSUMED
------------------------------------------
Literature exon numbers are stated against whichever transcript that paper used. This module
computes against the Ensembl CANONICAL transcript. For a gene with one first exon those agree;
for a gene with several alternative first exons (ABL1 1a/1b, RUNX1 P1/P2) they may not, and the
difference lands exactly on the quantity being measured. So each gene carries
`n_distinct_first_exons` counted over its protein-coding transcripts, and any fusion whose 3'
partner has more than one is graded INDETERMINATE unless its source names the transcript. That is
a measured flag, not a judgement call.

NETWORK. Ensembl REST and Europe PMC. The dev sandbox 403s both at CONNECT, so `--refresh` runs
on a GitHub Actions runner (CLAUDE.md section 6). Pure stdlib, no pip. Everything except
`--refresh` is offline and reads the committed inputs.

    python3 research/modalities/fusion_frame_trap.py --refresh   # CI only: fetch inputs
    python3 research/modalities/fusion_frame_trap.py             # compute + write the artifact
    python3 research/modalities/fusion_frame_trap.py --check     # recompute, diff, never write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "fusion-frame-trap-inputs.json")
BREAKPOINTS = os.path.join(HERE, "fusion-frame-trap-breakpoints.json")
OUT = os.path.join(HERE, "fusion-frame-trap.json")

ENS = "https://rest.ensembl.org"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# ── the catalogue ────────────────────────────────────────────────────────────────────────────
# Recurrent, well-characterised fusion oncogenes. The PAIR is what is asserted here (these gene
# pairs are the defining rearrangement of the named entity); the BREAKPOINT is not asserted here
# at all -- it is sourced separately, quoted, and gated. `query` is the Europe PMC search whose
# returned abstracts are the only place a breakpoint may come from.
#
# Selection rule, stated so the sample can be criticised: entities whose defining fusion is named
# in the WHO classification of the relevant tumour type or in standard haematology nomenclature,
# spanning promoter-swap and chimeric-protein architectures, both haematological and solid. This
# is a convenience sample of the canonical set, NOT a random draw from a fusion database, and the
# memo says so. It is biased toward well-studied fusions, which is the direction that makes an
# unsourceable breakpoint LESS likely, not more.
FUSIONS = [
    dict(id="EWSR1--NR4A3", five="EWSR1", three="NR4A3",
         disease="extraskeletal myxoid chondrosarcoma",
         query='(EWSR1 OR EWS) AND NR4A3 AND fusion AND exon'),
    dict(id="TAF15--NR4A3", five="TAF15", three="NR4A3",
         disease="extraskeletal myxoid chondrosarcoma",
         query='TAF15 AND NR4A3 AND fusion AND exon'),
    dict(id="EWSR1--FLI1", five="EWSR1", three="FLI1",
         disease="Ewing sarcoma",
         query='EWSR1 AND FLI1 AND fusion AND exon AND breakpoint'),
    dict(id="EWSR1--ERG", five="EWSR1", three="ERG",
         disease="Ewing sarcoma",
         query='EWSR1 AND ERG AND Ewing AND fusion AND exon'),
    dict(id="EWSR1--WT1", five="EWSR1", three="WT1",
         disease="desmoplastic small round cell tumour",
         query='EWSR1 AND WT1 AND desmoplastic AND fusion AND exon'),
    dict(id="EWSR1--ATF1", five="EWSR1", three="ATF1",
         disease="clear cell sarcoma",
         query='EWSR1 AND ATF1 AND "clear cell sarcoma" AND fusion AND exon'),
    dict(id="FUS--DDIT3", five="FUS", three="DDIT3",
         disease="myxoid liposarcoma",
         query='FUS AND DDIT3 AND liposarcoma AND fusion AND exon'),
    dict(id="BCR--ABL1", five="BCR", three="ABL1",
         disease="chronic myeloid leukaemia",
         query='BCR AND ABL1 AND fusion AND exon AND breakpoint'),
    dict(id="EML4--ALK", five="EML4", three="ALK",
         disease="non-small-cell lung cancer",
         query='EML4 AND ALK AND fusion AND exon AND variant'),
    dict(id="NPM1--ALK", five="NPM1", three="ALK",
         disease="anaplastic large-cell lymphoma",
         query='NPM1 AND ALK AND lymphoma AND fusion AND exon'),
    dict(id="TMPRSS2--ERG", five="TMPRSS2", three="ERG",
         disease="prostate carcinoma",
         query='TMPRSS2 AND ERG AND prostate AND fusion AND exon'),
    dict(id="PML--RARA", five="PML", three="RARA",
         disease="acute promyelocytic leukaemia",
         query='PML AND RARA AND promyelocytic AND fusion AND exon AND breakpoint'),
    dict(id="RUNX1--RUNX1T1", five="RUNX1", three="RUNX1T1",
         disease="acute myeloid leukaemia t(8;21)",
         query='RUNX1 AND RUNX1T1 AND "t(8;21)" AND fusion AND exon'),
    dict(id="CBFB--MYH11", five="CBFB", three="MYH11",
         disease="acute myeloid leukaemia inv(16)",
         query='CBFB AND MYH11 AND "inv(16)" AND fusion AND exon'),
    dict(id="ETV6--RUNX1", five="ETV6", three="RUNX1",
         disease="B-cell acute lymphoblastic leukaemia",
         query='ETV6 AND RUNX1 AND leukemia AND fusion AND exon'),
    dict(id="KMT2A--AFF1", five="KMT2A", three="AFF1",
         disease="acute lymphoblastic leukaemia t(4;11)",
         query='(KMT2A OR MLL) AND (AFF1 OR AF4) AND fusion AND exon'),
    dict(id="KMT2A--MLLT3", five="KMT2A", three="MLLT3",
         disease="acute myeloid leukaemia t(9;11)",
         query='(KMT2A OR MLL) AND (MLLT3 OR AF9) AND fusion AND exon'),
    dict(id="PAX3--FOXO1", five="PAX3", three="FOXO1",
         disease="alveolar rhabdomyosarcoma",
         query='PAX3 AND (FOXO1 OR FKHR) AND rhabdomyosarcoma AND fusion AND exon'),
    dict(id="PAX7--FOXO1", five="PAX7", three="FOXO1",
         disease="alveolar rhabdomyosarcoma",
         query='PAX7 AND (FOXO1 OR FKHR) AND rhabdomyosarcoma AND fusion AND exon'),
    dict(id="SS18--SSX1", five="SS18", three="SSX1",
         disease="synovial sarcoma",
         query='(SS18 OR SYT) AND SSX1 AND "synovial sarcoma" AND fusion AND exon'),
    dict(id="SS18--SSX2", five="SS18", three="SSX2",
         disease="synovial sarcoma",
         query='(SS18 OR SYT) AND SSX2 AND "synovial sarcoma" AND fusion AND exon'),
    dict(id="COL1A1--PDGFB", five="COL1A1", three="PDGFB",
         disease="dermatofibrosarcoma protuberans",
         query='COL1A1 AND PDGFB AND dermatofibrosarcoma AND fusion AND exon'),
    dict(id="NAB2--STAT6", five="NAB2", three="STAT6",
         disease="solitary fibrous tumour",
         query='NAB2 AND STAT6 AND "solitary fibrous" AND fusion AND exon'),
    dict(id="ETV6--NTRK3", five="ETV6", three="NTRK3",
         disease="secretory carcinoma / infantile fibrosarcoma",
         query='ETV6 AND NTRK3 AND fusion AND exon AND breakpoint'),
    dict(id="CIC--DUX4", five="CIC", three="DUX4",
         disease="CIC-rearranged sarcoma",
         query='CIC AND DUX4 AND sarcoma AND fusion AND exon'),
    dict(id="BCOR--CCNB3", five="BCOR", three="CCNB3",
         disease="BCOR-rearranged sarcoma",
         query='BCOR AND CCNB3 AND sarcoma AND fusion AND exon'),
    dict(id="FGFR3--TACC3", five="FGFR3", three="TACC3",
         disease="glioblastoma / urothelial carcinoma",
         query='FGFR3 AND TACC3 AND fusion AND exon'),
    dict(id="CD74--ROS1", five="CD74", three="ROS1",
         disease="non-small-cell lung cancer",
         query='CD74 AND ROS1 AND fusion AND exon'),
    dict(id="SLC34A2--ROS1", five="SLC34A2", three="ROS1",
         disease="non-small-cell lung cancer",
         query='SLC34A2 AND ROS1 AND fusion AND exon'),
    dict(id="KIF5B--RET", five="KIF5B", three="RET",
         disease="non-small-cell lung cancer",
         query='KIF5B AND RET AND fusion AND exon'),
    dict(id="CCDC6--RET", five="CCDC6", three="RET",
         disease="papillary thyroid carcinoma",
         query='(CCDC6 OR H4) AND RET AND thyroid AND fusion AND exon'),
    dict(id="NCOA4--RET", five="NCOA4", three="RET",
         disease="papillary thyroid carcinoma",
         query='(NCOA4 OR ELE1) AND RET AND thyroid AND fusion AND exon'),
    dict(id="MYB--NFIB", five="MYB", three="NFIB",
         disease="adenoid cystic carcinoma",
         query='MYB AND NFIB AND "adenoid cystic" AND fusion AND exon'),
    dict(id="HEY1--NCOA2", five="HEY1", three="NCOA2",
         disease="mesenchymal chondrosarcoma",
         query='HEY1 AND NCOA2 AND chondrosarcoma AND fusion AND exon'),
    dict(id="ASPSCR1--TFE3", five="ASPSCR1", three="TFE3",
         disease="alveolar soft part sarcoma",
         query='(ASPSCR1 OR ASPL) AND TFE3 AND "alveolar soft part" AND fusion AND exon'),
    dict(id="JAZF1--SUZ12", five="JAZF1", three="SUZ12",
         disease="endometrial stromal sarcoma",
         query='JAZF1 AND (SUZ12 OR JJAZ1) AND endometrial AND fusion AND exon'),
    dict(id="DNAJB1--PRKACA", five="DNAJB1", three="PRKACA",
         disease="fibrolamellar hepatocellular carcinoma",
         query='DNAJB1 AND PRKACA AND fibrolamellar AND fusion AND exon'),
    dict(id="ZFTA--RELA", five="ZFTA", three="RELA",
         disease="supratentorial ependymoma",
         query='(ZFTA OR C11orf95) AND RELA AND ependymoma AND fusion AND exon'),
    dict(id="LMNA--NTRK1", five="LMNA", three="NTRK1",
         disease="infantile fibrosarcoma / soft-tissue tumour",
         query='LMNA AND NTRK1 AND fusion AND exon'),
    dict(id="TPM3--NTRK1", five="TPM3", three="NTRK1",
         disease="papillary thyroid / colon carcinoma",
         query='TPM3 AND NTRK1 AND fusion AND exon'),
    dict(id="STIL--TAL1", five="STIL", three="TAL1",
         disease="T-cell acute lymphoblastic leukaemia",
         query='(STIL OR SIL) AND TAL1 AND leukemia AND fusion AND exon'),
    dict(id="GOPC--ROS1", five="GOPC", three="ROS1",
         disease="glioblastoma",
         query='(GOPC OR FIG) AND ROS1 AND fusion AND exon'),
]

#: Every gene the catalogue names, in the order first seen. Derived, never typed twice.
def gene_symbols() -> list:
    seen, out = set(), []
    for f in FUSIONS:
        for sym in (f["five"], f["three"]):
            if sym not in seen:
                seen.add(sym)
                out.append(sym)
    return out


# ── fetch (CI only) ──────────────────────────────────────────────────────────────────────────
def _fetch(url: str, ctype: str, tries: int = 4):
    """One HTTP GET with bounded retries.

    Ensembl REST rate-limits at 15 requests/second and answers a breach with 429 + Retry-After.
    A retry loop that ignores that header turns one breach into a queue of breaches, so the
    header is honoured when present. `timeout=` is per socket operation, not per transfer, so
    the bounded try count is the real hang guard.
    """
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"Content-Type": ctype, "Accept": ctype,
                              "User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                raw = r.read().decode("utf-8", "replace")
            return json.loads(raw) if "json" in ctype else raw
        except urllib.error.HTTPError as exc:
            last = exc
            wait = 2 ** i
            if exc.code == 429:
                try:
                    wait = max(wait, float(exc.headers.get("Retry-After") or 0) + 1)
                except (TypeError, ValueError):
                    pass
            print(f"  retry {i + 1} ({exc.code}) {url}: sleeping {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  retry {i + 1} {url}: {exc}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}: {last}")


def _post(url: str, payload: dict):
    """Ensembl batch POST. 67 genes x 4 GETs is 272 requests and measured out past a 30-minute
    CI timeout (run 31428431853); the same work is 7 POSTs. Batching is not an optimisation
    here, it is the difference between the lane working and not."""
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json",
                         "Accept": "application/json",
                         "User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            last = exc
            wait = 2 ** i
            if exc.code == 429:
                try:
                    wait = max(wait, float(exc.headers.get("Retry-After") or 0) + 1)
                except (TypeError, ValueError):
                    pass
            print(f"  POST retry {i + 1} ({exc.code}) {url}: sleeping {wait:.0f}s",
                  file=sys.stderr)
            time.sleep(wait)
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  POST retry {i + 1} {url}: {exc}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed POST: {url}: {last}")


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def gene_model(symbol: str, look: dict, seqs: dict) -> dict:
    """Canonical transcript, exon table in cDNA coordinates, 5'UTR length, self-checked.

    The arithmetic is the same as `emc_fet_construct_designs.gene_model` -- deliberately, so the
    index case computed here is comparable with the one the EMC manuscript computed. What is
    added is `n_distinct_first_exons`, the numbering-risk flag, which that module had no use for
    because it handled five genes a human had checked by hand.

    `look` is this gene's expanded Ensembl lookup and `seqs` maps an Ensembl id to its sequence;
    both arrive from batch POSTs, so this function performs no network call of its own.
    """
    coding = [t for t in look.get("Transcript", []) if t.get("biotype") == "protein_coding"]
    tr = next((t for t in look["Transcript"] if t.get("is_canonical") == 1), None)
    if tr is None or not tr.get("Translation"):
        tr = next((t for t in coding if t.get("Translation")), None)
    if tr is None:
        raise RuntimeError(f"{symbol}: no protein-coding transcript with a translation")

    # Numbering risk: how many DISTINCT first exons do this gene's protein-coding transcripts
    # use? >1 means the literature's "exon N" may be counted on a different first exon than the
    # canonical transcript's, and the fusion is graded INDETERMINATE for that reason.
    first_exons = set()
    for t in coding:
        ex = t.get("Exon") or []
        if not ex:
            continue
        ordered = sorted(ex, key=lambda e: e["start"], reverse=(t["strand"] == -1))
        first_exons.add(ordered[0]["id"])

    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    trans = tr["Translation"]
    cds_lo, cds_hi = trans["start"], trans["end"]

    rows, cdna_cum, coding_cum, utr5 = [], 0, 0, 0
    for rank, ex in enumerate(exons, start=1):
        elen = ex["end"] - ex["start"] + 1
        cstart, cend = max(ex["start"], cds_lo), min(ex["end"], cds_hi)
        clen = max(0, cend - cstart + 1)
        if strand == 1:
            before = max(0, min(ex["end"], cds_lo - 1) - ex["start"] + 1)
        else:
            before = max(0, ex["end"] - max(ex["start"], cds_hi + 1) + 1)
        utr5 += before
        row = {
            "transcript_exon_rank": rank,
            "exon_id": ex.get("id"),
            "exon_length_nt": elen,
            "cdna_start_0based": cdna_cum,
            "cdna_end_exclusive": cdna_cum + elen,
            "coding_nt_in_exon": clen,
            "utr5_nt_in_exon": before,
            "is_coding": bool(clen),
        }
        cdna_cum += elen
        if clen:
            row["first_protein_residue"] = coding_cum // 3 + 1
            coding_cum += clen
        row["cumulative_coding_nt_through_exon"] = coding_cum
        rows.append(row)

    def seq(kind: str, ident: str) -> str:
        # Ensembl echoes the query id, but a version suffix can appear on either side; match on
        # the unversioned accession so a present sequence is never read as an absent one.
        v = seqs.get((kind, ident))
        if v is None:
            base = ident.split(".")[0]
            v = next((s for (k, i), s in seqs.items()
                      if k == kind and i.split(".")[0] == base), None)
        return v or ""

    cdna = seq("cdna", tr["id"]).upper()
    cds = seq("cds", tr["id"]).upper()
    protein = seq("protein", trans["id"]).strip()
    if not (cdna and cds and protein):
        raise RuntimeError(
            f"{symbol}: a sequence is missing from the batch fetch "
            f"(cdna={len(cdna)}, cds={len(cds)}, protein={len(protein)}) — refusing to build a "
            "model whose self-checks would silently pass on empty strings")

    initiator_exon = next((r["transcript_exon_rank"] for r in rows if r["is_coding"]), None)
    checks = {
        # The load-bearing one: the measured 5'UTR length must place the CDS exactly where
        # Ensembl says it is. If this is false, U is wrong for every fusion using this gene.
        "cdna_slice_at_utr5_equals_cds": cdna[utr5:utr5 + len(cds)] == cds,
        "exon_lengths_sum_equals_cdna": cdna_cum == len(cdna),
        "coding_nt_sum_equals_cds": coding_cum == len(cds),
        "cds_len_is_multiple_of_three": len(cds) % 3 == 0,
        "protein_len_matches_cds": len(protein) == len(cds) // 3 - 1,
    }
    return {
        "symbol": symbol,
        "gene_id": look.get("id"),
        "transcript": tr["id"],
        "translation": trans["id"],
        "strand": strand,
        "utr5_len": utr5,
        "cdna_len": len(cdna),
        "cds_len": len(cds),
        "protein_len": len(protein),
        "cds_md5": hashlib.md5(cds.encode()).hexdigest(),
        "protein_md5": hashlib.md5(protein.encode()).hexdigest(),
        "n_transcript_exons": len(rows),
        "n_protein_coding_transcripts": len(coding),
        "n_distinct_first_exons": len(first_exons),
        "initiator_codon_exon_rank": initiator_exon,
        "n_wholly_untranslated_leading_exons": max(0, (initiator_exon or 1) - 1),
        "utr5_nt_in_initiator_exon": next(
            (r["utr5_nt_in_exon"] for r in rows if r["is_coding"]), 0),
        "exons": rows,
        "self_checks": checks,
    }


def epmc(query: str, page_size: int = 12) -> dict:
    url = (f"{EPMC}?query={urllib.parse.quote(query)}&format=json"
           f"&resultType=core&pageSize={page_size}")
    body = _fetch(url, "application/json")
    res = body.get("resultList", {}).get("result", [])
    recs = []
    for r in res:
        ab = (r.get("abstractText") or "")
        ab = re.sub(r"<[^>]+>", " ", ab)
        ab = re.sub(r"\s+", " ", ab).strip()
        if not ab:
            continue
        # Keep only records that could possibly carry a breakpoint statement. A record with no
        # exon/intron language cannot source a breakpoint, and storing it would only pad the file.
        if not re.search(r"\bexon|\bintron|\bnucleotide", ab, re.I):
            continue
        recs.append({
            "id": r.get("id"),
            "source": r.get("source"),
            "pmid": r.get("pmid"),
            "pmcid": r.get("pmcid"),
            "doi": r.get("doi"),
            "title": (r.get("title") or "").strip(),
            "authors": (r.get("authorString") or "").strip(),
            "journal": (r.get("journalInfo", {}) or {}).get("journal", {}).get("title"),
            "year": r.get("pubYear"),
            "abstract_verbatim": ab,
        })
    return {"query": query, "hit_count": body.get("hitCount"),
            "records_kept": len(recs), "records": recs}


def refresh() -> dict:
    symbols = gene_symbols()
    failures = []

    # 1. every gene's expanded lookup, in batches
    looks = {}
    for chunk in _chunks(symbols, 12):
        body = _post(f"{ENS}/lookup/symbol/homo_sapiens?expand=1", {"symbols": chunk})
        looks.update(body)
        print(f"  lookup: {len(looks)}/{len(symbols)}", file=sys.stderr)
    for sym in symbols:
        if sym not in looks:
            failures.append({"symbol": sym, "error": "not returned by the Ensembl symbol lookup"})

    # 2. pick the transcript per gene, then fetch the three sequences in batches
    picked = {}
    for sym, look in looks.items():
        coding = [t for t in look.get("Transcript", []) if t.get("biotype") == "protein_coding"]
        tr = next((t for t in look.get("Transcript", []) if t.get("is_canonical") == 1), None)
        if tr is None or not tr.get("Translation"):
            tr = next((t for t in coding if t.get("Translation")), None)
        if tr is None:
            failures.append({"symbol": sym,
                             "error": "no protein-coding transcript with a translation"})
            continue
        picked[sym] = (tr["id"], tr["Translation"]["id"])

    seqs = {}
    for kind, ids in (("cdna", sorted({t for t, _ in picked.values()})),
                      ("cds", sorted({t for t, _ in picked.values()})),
                      ("protein", sorted({p for _, p in picked.values()}))):
        for chunk in _chunks(ids, 40):
            body = _post(f"{ENS}/sequence/id?type={kind}", {"ids": chunk})
            for rec in body:
                if rec.get("seq"):
                    seqs[(kind, rec.get("query") or rec.get("id"))] = rec["seq"]
        print(f"  sequences[{kind}]: {sum(1 for k in seqs if k[0] == kind)}/{len(ids)}",
              file=sys.stderr)

    genes = {}
    for sym in symbols:
        if sym not in picked:
            continue
        try:
            genes[sym] = gene_model(sym, looks[sym], seqs)
            c = genes[sym]["self_checks"]
            print(f"  {sym}: {genes[sym]['transcript']} {genes[sym]['protein_len']} aa "
                  f"utr5={genes[sym]['utr5_len']} init_exon="
                  f"{genes[sym]['initiator_codon_exon_rank']} "
                  f"first_exons={genes[sym]['n_distinct_first_exons']} "
                  f"checks={all(c.values())}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            failures.append({"symbol": sym, "error": str(exc)})
            print(f"  {sym}: MODEL FAILED {exc}", file=sys.stderr)
    corpus = {}
    for f in FUSIONS:
        try:
            corpus[f["id"]] = epmc(f["query"])
            print(f"  {f['id']}: {corpus[f['id']]['records_kept']} abstracts kept "
                  f"of {corpus[f['id']]['hit_count']} hits", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            failures.append({"fusion": f["id"], "error": str(exc)})
            print(f"  {f['id']}: EPMC FAILED {exc}", file=sys.stderr)
        time.sleep(0.4)
    return {
        "_note": "Reference transcript structures (Ensembl REST, canonical transcript) and the "
                 "Europe PMC abstract corpus that fusion-frame-trap-breakpoints.json quotes "
                 "from. Fetched on a GitHub Actions runner; the dev sandbox 403s both hosts at "
                 "CONNECT. Nothing in this file was typed.",
        "_limits": [
            "An Ensembl CANONICAL transcript is not necessarily the transcript a given paper "
            "numbered its exons on. n_distinct_first_exons is the flag for that risk and the "
            "analysis grades on it; it is a proxy, not a resolution.",
            "An abstract returned by a search is evidence the record exists and says what it "
            "says. It is not evidence the breakpoint it reports is the only one, or the "
            "commonest one, for that entity.",
            "Abstracts are kept only when they contain exon/intron/nucleotide language, because "
            "a record without it cannot source a breakpoint.",
        ],
        "_fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_ensembl": ENS,
        "_europepmc": EPMC,
        "fetch_failures": failures,
        "genes": genes,
        "corpus": corpus,
    }


# ── the anti-fabrication gate ────────────────────────────────────────────────────────────────
def _norm(s: str) -> str:
    """Whitespace- and dash-insensitive, so a quote survives line wrapping and en/em dashes."""
    s = s.replace("‐", "-").replace("‑", "-").replace("‒", "-")
    s = s.replace("–", "-").replace("—", "-").replace("−", "-")
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def verify_quotes(inputs: dict, rows: list) -> list:
    """Every sourced breakpoint quote must appear verbatim in the committed corpus.

    Returns the per-row verification record. Raises on any failure -- a quote that cannot be
    located is indistinguishable from a quote that was invented, and this module refuses to
    emit an artifact in that state.
    """
    index = {}
    for fid, block in inputs.get("corpus", {}).items():
        for rec in block.get("records", []):
            for key in (rec.get("id"), rec.get("pmid"), rec.get("pmcid"), rec.get("doi")):
                if key:
                    index.setdefault(str(key), []).append((fid, rec))
    out, bad = [], []
    for row in rows:
        ev = row.get("evidence") or {}
        src, quote = str(ev.get("source_id") or ""), ev.get("quote") or ""
        if not src or not quote:
            out.append({"fusion": row["id"], "verified": False,
                        "reason": "no source_id/quote supplied"})
            continue
        hits = index.get(src, [])
        if not hits:
            bad.append(f"{row['id']}: source {src} is not in the committed corpus")
            continue
        found = any(_norm(quote) in _norm(rec["abstract_verbatim"]) for _, rec in hits)
        if not found:
            bad.append(f"{row['id']}: quote not found verbatim in {src}")
            continue
        rec = hits[0][1]
        out.append({"fusion": row["id"], "verified": True, "source_id": src,
                    "pmid": rec.get("pmid"), "pmcid": rec.get("pmcid"), "doi": rec.get("doi"),
                    "title": rec.get("title"), "year": rec.get("year"),
                    "quote": quote})
    if bad:
        raise SystemExit("UNVERIFIED BREAKPOINT QUOTE(S) — refusing to emit:\n  "
                         + "\n  ".join(bad))
    return out


# ── the arithmetic ───────────────────────────────────────────────────────────────────────────
def exon_row(gene: dict, rank: int) -> dict:
    for r in gene["exons"]:
        if r["transcript_exon_rank"] == rank:
            return r
    raise ValueError(f"{gene['symbol']}: no transcript exon {rank}")


def grade(fusion: dict, row: dict, genes: dict) -> dict:
    """One JUNCTION, graded on conditions (i) and (ii). Every field derived, none typed.

    A fusion may contribute several rows. That is deliberate and it is the whole reason the
    index case was findable at all: EWSR1::NR4A3's trap is on a MINORITY junction, so an
    analysis that graded one junction per entity would have missed it in its own worked example.
    """
    fid = fusion["id"]
    g5, g3 = genes.get(fusion["five"]), genes.get(fusion["three"])
    out = {
        "id": fid,
        "junction": row.get("junction") or "the junction the source states",
        "five_prime": fusion["five"],
        "three_prime": fusion["three"],
        "disease": fusion["disease"],
    }
    if g5 is None or g3 is None:
        out.update(verdict="INDETERMINATE",
                   indeterminate_reason="a partner gene has no fetched transcript model")
        return out

    out["five_prime_transcript"] = g5["transcript"]
    out["three_prime_transcript"] = g3["transcript"]
    out["three_prime_initiator_exon_rank"] = g3["initiator_codon_exon_rank"]
    out["three_prime_utr5_len"] = g3["utr5_len"]
    out["three_prime_n_untranslated_leading_exons"] = g3["n_wholly_untranslated_leading_exons"]
    out["three_prime_n_distinct_first_exons"] = g3["n_distinct_first_exons"]
    out["five_prime_n_distinct_first_exons"] = g5["n_distinct_first_exons"]

    e5, e3 = row.get("five_prime_exon"), row.get("three_prime_exon")
    out["five_prime_exon"] = e5
    out["three_prime_exon"] = e3
    out["breakpoint_note"] = row.get("note")

    if e5 is None or e3 is None:
        out.update(verdict="INDETERMINATE",
                   indeterminate_reason=row.get("indeterminate_reason")
                   or "the sourced record does not fix the breakpoint at exon resolution")
        return out
    if e5 > g5["n_transcript_exons"] or e3 > g3["n_transcript_exons"]:
        out.update(verdict="INDETERMINATE",
                   indeterminate_reason=(
                       f"quoted exon number exceeds the canonical transcript's exon count "
                       f"({fusion['five']} {e5}/{g5['n_transcript_exons']}, "
                       f"{fusion['three']} {e3}/{g3['n_transcript_exons']}) — the source "
                       "numbered a different transcript"))
        return out
    # Numbering risk on the 3' partner is disqualifying unless the source names the transcript,
    # because it lands exactly on U. On the 5' partner it lands on L, and therefore on the phase.
    unresolved = []
    if g3["n_distinct_first_exons"] > 1 and not row.get("three_prime_transcript_named"):
        unresolved.append(
            f"{fusion['three']} has {g3['n_distinct_first_exons']} distinct first exons across "
            f"its {g3['n_protein_coding_transcripts']} protein-coding transcripts and the source "
            "does not name which one it numbered")
    if g5["n_distinct_first_exons"] > 1 and not row.get("five_prime_transcript_named"):
        unresolved.append(
            f"{fusion['five']} has {g5['n_distinct_first_exons']} distinct first exons across "
            f"its {g5['n_protein_coding_transcripts']} protein-coding transcripts and the source "
            "does not name which one it numbered")

    r5, r3 = exon_row(g5, e5), exon_row(g3, e3)
    L = r5["cumulative_coding_nt_through_exon"]
    U = max(0, g3["utr5_len"] - r3["cdna_start_0based"])
    phase = L % 3
    in_frame = (L + U) % 3 == 0
    out.update({
        "five_prime_retained_coding_nt": L,
        "five_prime_retained_residues": L // 3,
        "five_prime_end_phase": phase,
        "acceptor_untranslated_nt_retained": U,
        "acceptor_exon_class": (
            "five_prime_partner_contributes_no_coding_sequence" if L == 0 else
            "wholly_untranslated_acceptor_exon" if r3["coding_nt_in_exon"] == 0 else
            "initiator_exon_with_retained_5utr" if U > 0 else
            "wholly_coding_acceptor_position"),
        "condition_i_breakpoint_in_untranslated_sequence": bool(U > 0),
        "condition_ii_five_prime_ends_mid_codon": bool(phase != 0),
        "acceptor_own_frame_resumes": bool(in_frame),
        "residues_a_cds_on_cds_construct_would_omit": ((phase + U) // 3) if in_frame else None,
    })
    both = out["condition_i_breakpoint_in_untranslated_sequence"] and \
        out["condition_ii_five_prime_ends_mid_codon"]
    if unresolved:
        out.update(verdict="INDETERMINATE",
                   indeterminate_reason="; ".join(unresolved),
                   provisional_both_conditions=bool(both))
    elif L == 0:
        out.update(verdict="NOT_APPLICABLE_PROMOTER_SWAP",
                   verdict_reason="the 5' partner contributes no coding sequence, so there is no "
                                  "chimeric reading frame and a construct is just the 3' "
                                  "partner's own open reading frame")
    elif both:
        out.update(verdict="BOTH_CONDITIONS_HOLD")
    elif U > 0:
        out.update(verdict="CONDITION_I_ONLY",
                   verdict_reason="the acceptor contributes untranslated sequence, but the 5' "
                                  "partner ends on a codon boundary")
    elif phase != 0:
        out.update(verdict="CONDITION_II_ONLY",
                   verdict_reason="the 5' partner ends mid-codon, but the acceptor contributes "
                                  "no untranslated sequence, so the extra nucleotides are the 3' "
                                  "partner's own coding sequence read out of frame")
    else:
        out.update(verdict="NEITHER_CONDITION",
                   verdict_reason="the 5' partner ends on a codon boundary and the acceptor "
                                  "contributes no untranslated sequence — a CDS-on-CDS construct "
                                  "reproduces the predicted fusion protein")
    return out


def exposure_sweep(fusion: dict, genes: dict) -> dict:
    """Is the trap REACHABLE for this gene pair, whatever breakpoint is actually reported?

    A reported breakpoint is one draw. The architecture fixes the whole space. For every pair of
    exon-boundary breakpoints this gene pair could produce -- every coding donor exon of the 5'
    partner against every acceptor exon of the 3' partner that retains untranslated sequence --
    this asks how many satisfy both conditions AND leave the acceptor's own frame intact, which
    is the combination that yields a translated, silently-extended chimera.

    It is a combinatorial count over exon boundaries, NOT a claim that any of these junctions
    occurs in a patient. It answers the narrower question the memo needs: for this pair, is the
    trap architecturally possible, or is it excluded outright?
    """
    g5, g3 = genes.get(fusion["five"]), genes.get(fusion["three"])
    if g5 is None or g3 is None:
        return {"id": fusion["id"], "status": "a partner gene has no fetched transcript model"}
    donors = [r for r in g5["exons"] if r["cumulative_coding_nt_through_exon"] > 0]
    acceptors = [r for r in g3["exons"]
                 if max(0, g3["utr5_len"] - r["cdna_start_0based"]) > 0]
    hits, best = 0, None
    for d in donors:
        L = d["cumulative_coding_nt_through_exon"]
        phase = L % 3
        if phase == 0:
            continue
        for a in acceptors:
            U = g3["utr5_len"] - a["cdna_start_0based"]
            if (L + U) % 3:
                continue
            hits += 1
            n = (phase + U) // 3
            if best is None or n > best["novel_residues"]:
                best = {"five_prime_exon": d["transcript_exon_rank"],
                        "three_prime_exon": a["transcript_exon_rank"],
                        "five_prime_end_phase": phase,
                        "acceptor_untranslated_nt_retained": U,
                        "novel_residues": n}
    return {
        "id": fusion["id"],
        "n_coding_donor_exons": len(donors),
        "n_acceptor_exons_retaining_untranslated_sequence": len(acceptors),
        "n_exon_pairs_satisfying_both_conditions_in_frame": hits,
        "trap_architecturally_reachable": bool(hits),
        "largest_reachable_insertion": best,
    }


def architecture_survey(genes: dict) -> dict:
    """How often is condition (i) even ARCHITECTURALLY available, breakpoints aside?

    This is the exposure measure, and it is the half of the question that needs no breakpoint:
    a 3' partner whose initiator codon sits in transcript exon 1 has no upstream exon boundary a
    breakpoint could land at, so condition (i) is unreachable for it whatever the breakpoint.
    """
    three_prime = sorted({f["three"] for f in FUSIONS})
    rows = []
    for sym in three_prime:
        g = genes.get(sym)
        if g is None:
            rows.append({"symbol": sym, "status": "no transcript model fetched"})
            continue
        rows.append({
            "symbol": sym,
            "transcript": g["transcript"],
            "n_transcript_exons": g["n_transcript_exons"],
            "initiator_codon_exon_rank": g["initiator_codon_exon_rank"],
            "n_wholly_untranslated_leading_exons": g["n_wholly_untranslated_leading_exons"],
            "utr5_len": g["utr5_len"],
            "utr5_nt_in_initiator_exon": g["utr5_nt_in_initiator_exon"],
            "condition_i_architecturally_available": bool(
                g["n_wholly_untranslated_leading_exons"] > 0),
            "n_distinct_first_exons": g["n_distinct_first_exons"],
        })
    graded = [r for r in rows if "condition_i_architecturally_available" in r]
    avail = [r for r in graded if r["condition_i_architecturally_available"]]
    return {
        "_question": "For each distinct 3' partner in the catalogue, does its canonical "
                     "transcript place the initiator codon after transcript exon 1? If not, no "
                     "exon-boundary breakpoint can satisfy condition (i).",
        "n_distinct_three_prime_partners": len(three_prime),
        "n_graded": len(graded),
        "n_condition_i_architecturally_available": len(avail),
        "symbols_available": [r["symbol"] for r in avail],
        "rows": rows,
    }


# ── controls ─────────────────────────────────────────────────────────────────────────────────
def known_answer_control(results: list) -> dict:
    """The EMC index case must reproduce the manuscript's published numbers, or nothing here is
    trustworthy. 176 untranslated NR4A3 nt retained, and 59 omitted residues, are the values
    `emc_fet_frame_and_composition.py` pins for the EWSR1 exon 7 :: NR4A3 exon 2 junction."""
    row = next((r for r in results
                if r["id"] == "EWSR1--NR4A3" and r.get("three_prime_exon") == 2), None)
    if row is None:
        return {"status": "ABSENT",
                "detail": "the EWSR1 :: NR4A3 exon 2 junction is not in the graded set — the "
                          "instrument has no known answer to be checked against"}
    got_u = row.get("acceptor_untranslated_nt_retained")
    got_n = row.get("residues_a_cds_on_cds_construct_would_omit")
    ok = (got_u == 176 and got_n == 59)
    return {
        "status": "PASS" if ok else "FAIL",
        "expected_untranslated_nt": 176,
        "expected_omitted_residues": 59,
        "observed_untranslated_nt": got_u,
        "observed_omitted_residues": got_n,
        "_why": "The EMC manuscript's independently-computed junction is the known answer for "
                "this instrument. If the general-case arithmetic does not reproduce it, the "
                "general-case counts mean nothing.",
        "_source_of_expectation": "research/modalities/emc-fet-frame-and-composition.json, "
                                  "computed by a different module from the same Ensembl model",
    }


# ── assemble ─────────────────────────────────────────────────────────────────────────────────
def build() -> dict:
    with open(INPUTS, encoding="utf-8") as fh:
        inputs = json.load(fh)
    with open(BREAKPOINTS, encoding="utf-8") as fh:
        bp = json.load(fh)
    genes = inputs["genes"]
    catalogue = {f["id"]: f for f in FUSIONS}
    rows = bp["breakpoints"]
    unknown = sorted({r["fusion"] for r in rows} - set(catalogue))
    if unknown:
        raise SystemExit(f"breakpoint rows name fusions not in the catalogue: {unknown}")

    # The gate. Every sourced junction's quote must be locatable, verbatim, in the committed
    # corpus. A failure raises rather than degrading the row, because a quote that cannot be
    # found is indistinguishable from one that was invented.
    verified = verify_quotes(inputs, [dict(r, id=f"{r['fusion']} :: {r.get('junction')}")
                                      for r in rows if (r.get("evidence") or {}).get("quote")])

    results = []
    for f in FUSIONS:
        mine = [r for r in rows if r["fusion"] == f["id"]]
        if not mine:
            results.append(grade(f, {"indeterminate_reason":
                                     "no exon-resolution breakpoint could be sourced from the "
                                     "fetched corpus for this fusion"}, genes))
            continue
        for r in mine:
            results.append(grade(f, r, genes))

    tally = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    both = [r for r in results if r["verdict"] == "BOTH_CONDITIONS_HOLD"]
    indet = [r for r in results if r["verdict"] == "INDETERMINATE"]

    # Per-ENTITY roll-up beside the per-junction tally. A fusion counts as a positive if any of
    # its graded junctions is one, and as indeterminate only if NONE of its junctions resolved.
    by_fusion = {}
    for r in results:
        by_fusion.setdefault(r["id"], []).append(r["verdict"])
    entity = {
        "n_fusions": len(by_fusion),
        "with_a_junction_where_both_conditions_hold": sorted(
            k for k, v in by_fusion.items() if "BOTH_CONDITIONS_HOLD" in v),
        "wholly_indeterminate": sorted(
            k for k, v in by_fusion.items() if set(v) == {"INDETERMINATE"}),
        "promoter_swap_only": sorted(
            k for k, v in by_fusion.items() if set(v) == {"NOT_APPLICABLE_PROMOTER_SWAP"}),
    }
    entity["n_with_a_junction_where_both_conditions_hold"] = len(
        entity["with_a_junction_where_both_conditions_hold"])
    entity["n_wholly_indeterminate"] = len(entity["wholly_indeterminate"])
    entity["n_resolved_with_no_trap_junction"] = (
        entity["n_fusions"] - entity["n_with_a_junction_where_both_conditions_hold"]
        - entity["n_wholly_indeterminate"])

    failed_checks = sorted(s for s, g in genes.items()
                           if not all(g["self_checks"].values()))
    return {
        "_note": "Do conditions (i) and (ii) of the EMC frame trap coincide anywhere else? "
                 "Exon arithmetic over Ensembl canonical transcripts, with every breakpoint "
                 "quoted verbatim from a fetched Europe PMC abstract. No efficacy, safety, "
                 "selectivity or clinical claim is made or implied.",
        "_limits": [
            "The catalogue is a convenience sample of canonical, well-characterised fusions, "
            "not a random draw from a fusion database. It cannot support a population frequency.",
            "Exon numbering is computed on the Ensembl canonical transcript; where a gene has "
            "several distinct first exons the source's numbering may differ and the row is "
            "graded INDETERMINATE for that reason rather than guessed.",
            "A single reported breakpoint per fusion is graded. Several of these entities have "
            "multiple recurrent junction types, and a fusion graded NEITHER_OR_ONE on its "
            "commonest junction may still have a minority junction that satisfies both — which "
            "is exactly the situation in the index case.",
            "The 5' partner's retained coding length is taken through a whole exon. A breakpoint "
            "inside an exon would change L and therefore the phase.",
        ],
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs_fetched_utc": inputs.get("_fetched_utc"),
        "n_fusions_in_catalogue": len(FUSIONS),
        "n_junctions_graded": len(results),
        "known_answer_control": known_answer_control(results),
        "gene_models_failing_self_checks": failed_checks,
        "counts": {
            "_unit": "one graded JUNCTION, not one fusion — several entities contribute more "
                     "than one, and the index case's trap is on a minority junction",
            "both_conditions_hold": tally.get("BOTH_CONDITIONS_HOLD", 0),
            "_of_which": "conditions (i) and (ii) can coincide and still leave the acceptor's own "
                         "reading frame shifted, in which case the whole downstream product "
                         "differs and no construct of the published kind would be attempted. The "
                         "actionable case — a silently extended but otherwise correct chimera — "
                         "is the subset below.",
            "both_conditions_and_acceptor_frame_resumes": sum(
                1 for r in both if r.get("acceptor_own_frame_resumes")),
            "condition_i_only": tally.get("CONDITION_I_ONLY", 0),
            "condition_ii_only": tally.get("CONDITION_II_ONLY", 0),
            "neither_condition": tally.get("NEITHER_CONDITION", 0),
            "promoter_swap_not_applicable": tally.get("NOT_APPLICABLE_PROMOTER_SWAP", 0),
            "indeterminate": tally.get("INDETERMINATE", 0),
        },
        "counts_by_fusion": entity,
        "both_conditions_hold": [f"{r['id']} :: {r['junction']}" for r in both],
        "indeterminate": [{"id": r["id"], "junction": r["junction"],
                           "reason": r.get("indeterminate_reason")} for r in indet],
        "architecture_survey": architecture_survey(genes),
        "exposure_sweep": {
            "_question": "Whatever breakpoint is actually reported, is the trap REACHABLE for "
                         "this gene pair at all? A count over exon-boundary combinations, not a "
                         "claim that any of them occurs in a patient.",
            "n_pairs_with_at_least_one_trap_combination": sum(
                1 for f in FUSIONS
                if exposure_sweep(f, genes).get("trap_architecturally_reachable")),
            "rows": [exposure_sweep(f, genes) for f in FUSIONS],
        },
        "breakpoint_provenance": verified,
        "fusions": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--refresh", action="store_true",
                    help="CI only: fetch Ensembl + Europe PMC and rewrite the inputs file")
    ap.add_argument("--check", action="store_true",
                    help="recompute and diff against the committed artifact; never writes")
    a = ap.parse_args()

    if a.refresh:
        data = refresh()
        with open(INPUTS, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=False)
            fh.write("\n")
        print(f"wrote {INPUTS} ({len(data['genes'])} genes, "
              f"{len(data['corpus'])} corpora, {len(data['fetch_failures'])} failures)")
        if not os.path.exists(BREAKPOINTS):
            print("no breakpoint table yet — curate it from the corpus, then re-run")
            return 0

    if not os.path.exists(INPUTS):
        print(f"missing {INPUTS}: run --refresh on a runner first", file=sys.stderr)
        return 2
    if not os.path.exists(BREAKPOINTS):
        print(f"missing {BREAKPOINTS}", file=sys.stderr)
        return 2

    out = build()
    ctrl = out["known_answer_control"]
    if ctrl["status"] != "PASS":
        print(f"KNOWN-ANSWER CONTROL {ctrl['status']}: {ctrl}", file=sys.stderr)
        return 3

    if a.check:
        if not os.path.exists(OUT):
            print(f"missing {OUT}", file=sys.stderr)
            return 2
        with open(OUT, encoding="utf-8") as fh:
            old = json.load(fh)
        drift = []
        for k in ("counts", "counts_by_fusion", "both_conditions_hold", "indeterminate",
                  "n_fusions_in_catalogue", "n_junctions_graded", "architecture_survey",
                  "exposure_sweep"):
            if old.get(k) != out.get(k):
                drift.append(k)
        key = lambda rs: [f"{r['id']}::{r.get('junction')}" for r in rs]  # noqa: E731
        if key(old.get("fusions", [])) != key(out["fusions"]):
            drift.append("fusions:order")
        for a_, b_ in zip(old.get("fusions", []), out["fusions"]):
            if a_.get("verdict") != b_.get("verdict"):
                drift.append(f"fusions:{a_.get('id')}:verdict")
        if drift:
            print("DRIFT: " + ", ".join(sorted(set(drift))), file=sys.stderr)
            return 1
        print(f"OK — {out['counts']} reproduced; control {ctrl['status']}")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"wrote {OUT}")
    print(f"  control: {ctrl['status']}")
    print(f"  counts:  {out['counts']}")
    print(f"  both:    {out['both_conditions_hold']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
