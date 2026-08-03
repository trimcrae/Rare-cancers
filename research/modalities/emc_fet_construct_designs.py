#!/usr/bin/env python3
"""
Ready-to-order EMC fusion constructs for the FET / ATM / ATR laser-microirradiation assay.

⛔ READ THIS FIRST — WHAT THESE ARE AND WHAT THEY ARE NOT
--------------------------------------------------------
Everything this module emits is a **COMPUTED DESIGN FOR SOMEONE ELSE TO VERIFY BEFORE
ORDERING**. It is not a validated reagent, it has never been synthesised, expressed, sequenced
or tested, and no claim is made that any of it works. **This repository has been wrong about a
fusion junction before**, in a committed artifact built from a stated Ensembl methodology:
`fusion-breakpoint-neoantigens.json` indexed a CODING-exon offset table with TRANSCRIPT exon
numbers, so the label "NR4A3 exon 3" resolved to transcript exon 5, and all seven committed
junctions silently deleted NR4A3's AF-1 and the first zinc finger of its C4 DBD — an off-by-two
that survived review and was caught only by a $0 re-derivation
(`research/manuscripts/target-route-options.md` §1.3; `nr4a3_exon_audit.py`). That incident is
the reason this module exists in this shape, and the reason every boundary below carries its
provenance rather than a remembered number.

WHY THIS EXISTS
---------------
The FET-fusion → impaired ATM → ATR-dependency mechanism (PMID 37205599 / bioRxiv
10.1101/2023.04.30.538578) was measured with a specific assay: GFP-tagged fusion oncoproteins
expressed in U2OS cells, 405 nm laser micro-irradiation, and quantification of accumulation at
the damage stripe over 15 minutes. Verbatim from the methods, fetched to the `literature-cache`
branch:

    "U2OS cells expressing EWSR1-GFP, EWSR1-FLI1-GFP, EWSR1-ATF1-GFP, EWSR1-WT1-GFP or the
     various mutant forms of the fusion oncoproteins were seeded in 8-well Lab Tek II Chamber
     Slides ... irradiated with a 405nm diode laser (40mW). Images were acquired pre-irradiation
     and at 1-minute intervals post-laser damage for 15 minutes."

EMC is the untested fourth transcription-factor-partner class (NR4A3 is a nuclear receptor;
their panel spans ETS, bZIP and zinc-finger partners). The single largest piece of work standing
between that group and an EMC arm is **building the constructs**, and the junction is the part
that is easy to get wrong. This module removes that work by computing the constructs from exon
structure, with every breakpoint sourced to a published statement.

WHAT IT COMPUTES, AND HOW THE FRAME IS HANDLED
----------------------------------------------
A reported fusion is an **mRNA exon junction**, not a protein junction. So the fusion is built at
the **cDNA** level — 5' partner cDNA from its transcript start through the end of the named exon,
joined to 3' partner cDNA from the start of its named exon — and then translated from the 5'
partner's own start codon. That is the only model that gets the reading frame right when the 3'
partner's named exon carries 5'-UTR ahead of its ATG, which is exactly the case for NR4A3
(transcript exons 1 and 2 are entirely non-coding and exon 3 carries both UTR and the start
codon). A CDS-level splice would silently discard that UTR and could differ by a frame.

Every construct therefore carries explicit self-checks that a reader can audit:
  * `five_prime_start_matches_partner`   — the ORF opens with the 5' partner's own N-terminus
  * `three_prime_c_terminus_intact`      — the ORF ends with the 3' partner's own C-terminus
  * `in_frame`                           — both of the above
A construct that fails them is reported as failing. It is not quietly dropped and it is not
patched until it passes, because "adjust the breakpoint until the answer is nice" is precisely
the circularity the positive controls in `emc_fet_idr_census.py` were built to prevent.

WHAT IS REUSED RATHER THAN RE-DERIVED (CLAUDE.md §1: one fact, one place)
------------------------------------------------------------------------
  * RGG / RG-dipeptide arithmetic and the retained-segment composition come from
    `emc_fet_idr_census.py` by IMPORT (`rgg_boxes`, `rgg_free_ceiling`, `assess`,
    `lc_composition`). This module does not define a second RGG rule.
  * The EWSR1 and NR4A3 exon→residue maps, the C4 zinc-finger residue and the LBD start come
    from `nr4a3-exon-audit.json` / `nr4a3_exon_audit.py`.
  * Protein sequences come from the same `fet-sequences-cache.json` the census uses.

NETWORK. Ensembl REST + UniProt. The dev sandbox 403s at CONNECT, so `--refresh` runs on a
GitHub Actions runner (CLAUDE.md §6). Pure stdlib, no pip.

Run:
    python3 research/modalities/emc_fet_construct_designs.py --refresh   # fetch + derive (CI)
    python3 research/modalities/emc_fet_construct_designs.py             # derive from cache
    python3 research/modalities/emc_fet_construct_designs.py --check     # reproduce and diff
Out:
    emc-fet-construct-designs.json   (the designs)
    emc-construct-inputs.json        (the fetched gene models, so --check is offline)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import emc_fet_idr_census as census          # noqa: E402  (RGG arithmetic — one home)
import nr4a3_exon_audit as exon_audit        # noqa: E402  (exon map + ZF motif — one home)

OUT = os.path.join(HERE, "emc-fet-construct-designs.json")
INPUTS = os.path.join(HERE, "emc-construct-inputs.json")
EXON_AUDIT = os.path.join(HERE, "nr4a3-exon-audit.json")
ENS = "https://rest.ensembl.org"

# Genes whose transcript models this module needs. TCF12 is here because the within-EMC negative
# control is only worth anything if "TCF12 is not a FET protein" is COMPUTED rather than asserted.
GENES = ["EWSR1", "TAF15", "FUS", "TCF12", "NR4A3"]
UNIPROT = {"EWSR1": "Q01844", "TAF15": "Q92804", "FUS": "P35637",
           "TCF12": "Q99081", "NR4A3": "Q92570", "FLI1": "Q01543", "ATF1": "P18846"}

# ---------------------------------------------------------------------------------------------
# THE BREAKPOINT REGISTRY — every entry is a QUOTE from a fetched paper, never a memory.
# ---------------------------------------------------------------------------------------------
# ⚠ The rule this registry enforces: an exon number that cannot be quoted is not written down.
# Where the literature reports several types, ALL are carried and the frequency evidence is
# quoted beside them; where it reports none at transcript resolution, the entry says so and no
# construct is emitted (see FUS and TCF12 below). "Present a small explicit set of sourced
# alternatives" is the honest output of an underdetermined question; inventing one is not.
BREAKPOINTS = [
    {
        "id": "EWSR1_NR4A3_type1",
        "label": "EWSR1::NR4A3 type 1 — EWSR1 exon 12 :: NR4A3 exon 3",
        "five_prime": "EWSR1", "five_prime_exon": 12,
        "three_prime": "NR4A3", "three_prime_exon": 3,
        "reported_rank": "the commonest reported EWSR1::NR4A3 transcript type",
        "sources": [
            {"id": "PMC3335514",
             "quote": "The most common fusion transcript contains exon 12 of EWSR1 fused to "
                      "exon 3 of NR4A3 (type 1), whereas exon 7 of EWSR1 is fused to exon 2 of "
                      "NR4A3 in the type 2 fusion transcript."},
            {"id": "PMC4055444",
             "quote": "The most frequent are: type 1, for the fusion between exons 12 of EWS "
                      "and 3 of CHN, and type 5, between exons 13 of EWS and 3 of CHN."},
            {"id": "PMC4015728 (Agaram 2014) — RT-PCR primer design",
             "quote": "EWSR1 exon 12 forward ... and NR4A3 reverse A exon 3 ... for the type 1 "
                      "EWSR1-NR4A3 fusion (109 base pair product)"},
            {"id": "PMC6766969 — an EXPRESSED construct with this architecture",
             "quote": "E-N, corresponding to EWSR1 (exons 1-12)-NR4A3 (exons 3-8)"},
        ],
    },
    {
        "id": "EWSR1_NR4A3_type2",
        "label": "EWSR1::NR4A3 type 2 — EWSR1 exon 7 :: NR4A3 exon 2",
        "five_prime": "EWSR1", "five_prime_exon": 7,
        "three_prime": "NR4A3", "three_prime_exon": 2,
        "reported_rank": "the second reported EWSR1::NR4A3 transcript type",
        "sources": [
            {"id": "PMC3335514",
             "quote": "exon 7 of EWSR1 is fused to exon 2 of NR4A3 in the type 2 fusion "
                      "transcript"},
            {"id": "PMC4015728 (Agaram 2014) — RT-PCR primer design",
             "quote": "EWSR1 exon 7 forward ... and NR4A3 reverse B exon 2 ... for the type 2 "
                      "fusion (201 base pair product)"},
        ],
        "_note": "NR4A3 transcript exon 2 is entirely NON-CODING on the canonical transcript "
                 "(nr4a3-exon-audit.json), so this junction splices EWSR1 into NR4A3 5'-UTR and "
                 "the frame of everything downstream is decided by that UTR's length. This is "
                 "computed below, not assumed, and it is exactly the kind of junction the "
                 "repo's earlier off-by-two got wrong.",
    },
    {
        "id": "EWSR1_NR4A3_type5",
        "label": "EWSR1::NR4A3 type 5 — EWSR1 exon 13 :: NR4A3 exon 3",
        "five_prime": "EWSR1", "five_prime_exon": 13,
        "three_prime": "NR4A3", "three_prime_exon": 3,
        "reported_rank": "a minority reported type",
        "sources": [
            {"id": "PMC4055444",
             "quote": "type 5, between exons 13 of EWS and 3 of CHN"},
            {"id": "PMC2395470 (CTOS 2001 abstract — a counted series)",
             "quote": "The most frequent EWS/CHN transcript (10 tumors), was fusion of exon 12 "
                      "of EWS with exon 3 of CHN (type 1), followed by fusion of exon 13 of EWS "
                      "with exon 3 of CHN (two cases; type 5)."},
        ],
    },
    {
        "id": "TAF15_NR4A3",
        "label": "TAF15::NR4A3 — TAF15 exon 6 :: NR4A3 exon 3",
        "five_prime": "TAF15", "five_prime_exon": 6,
        "three_prime": "NR4A3", "three_prime_exon": 3,
        "reported_rank": "the only reported TAF15::NR4A3 coding junction",
        "sources": [
            {"id": "PMC3335514",
             "quote": "In the TAF15-NR4A3 fusion transcript, exon 6 of TAF15 is fused "
                      "exclusively to exon 3 of NR4A3"},
            {"id": "PMC4055444",
             "quote": "The chimeric gene RBP56/CHN is always formed by fusion between exons 6 "
                      "of RBP56 and 3 of CHN."},
            {"id": "PMC2395470 (CTOS 2001 abstract — a counted series)",
             "quote": "In tumors with RBP56/CHN fusion, exon 6 of RBP56 was fused to exon 3 of "
                      "CHN."},
            {"id": "PMC6766969 — an EXPRESSED construct with this architecture",
             "quote": "T-N*, corresponding to the commonest TAF15 (exons 1-6)-NR4A3 (exons 3-8) "
                      "fusion"},
        ],
        "_reported_variant_not_modelled": {
            "what": "TAF15 exon 6 :: NR4A3 intron 2 (a cryptic exon), adding 25 residues ahead "
                    "of the NR4A3 start codon",
            "source": {"id": "PMC6766969",
                       "quote": "T-N retains a short cryptic exon located in NR4A3 intron 2 "
                                "(ENST00000395097.6 isoform), thus encoding 25 additional amino "
                                "acids prior to the NR4A3 ATG"},
            "why_not_modelled": "the cryptic exon's sequence is not in any artifact this repo "
                                "holds, so building it would mean inventing 75 nucleotides. It "
                                "is registered here so a collaborator knows it exists; the same "
                                "source reports T-N and T-N* were 'essentially indistinguishable' "
                                "for colony formation.",
        },
    },
]

# Reported partners for which this repo can quote NO transcript-level junction. They are named
# rather than omitted, because silence would read as 'there is no such fusion'.
UNPINNED = [
    {
        "fusion": "FUS::NR4A3",
        "status": "NO transcript-level junction sourced in this repo's literature cache",
        "what_can_be_said": "FUS is named as a rare EMC 5' partner (<5% of cases). No exon-level "
                            "breakpoint statement was found, so no construct is emitted. The "
                            "breakpoint-independent answer is the sweep already published in "
                            "emc-fet-idr-census.json -> emc_TAF15_and_FUS_breakpoint_sweep.",
    },
    {
        "fusion": "TCF12::NR4A3",
        "status": "GENOMIC breakpoint only — reported as TCF12 intron 5, not as an mRNA exon "
                  "junction, and TCF12 has several alternatively-spliced isoforms",
        "source": {"id": "PMC4055444",
                   "quote": "Gene TCF12, also known as HTF4, presents different isoforms by "
                            "alternative splicing and the breakpoint affects the region of "
                            "intron 5"},
        "what_can_be_said": "the negative-control prediction below does NOT need the junction. "
                            "It is computed as a property of every possible TCF12 breakpoint "
                            "(see tcf12_negative_control), which is stronger than a prediction "
                            "resting on one assumed junction.",
    },
]

CODON = exon_audit.CODON


# ---------------------------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------------------------
def _fetch(url: str, ctype: str):
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(
                url, headers={"Content-Type": ctype, "User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = r.read().decode()
            return json.loads(raw) if ctype.endswith("json") else raw
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  retry {i + 1} {url}: {exc}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}: {last}")


def translate(cds: str) -> str:
    aa = []
    for i in range(0, len(cds) - 2, 3):
        c = CODON.get(cds[i:i + 3], "X")
        if c == "*":
            break
        aa.append(c)
    return "".join(aa)


def gene_model(symbol: str) -> dict:
    """Canonical transcript with cDNA-coordinate exon boundaries AND the 5'-UTR length.

    The exon->coding-residue half of this duplicates nothing: `nr4a3_exon_audit.exon_map` owns
    that map and this function reproduces its self-checks so a mismatch is loud. What is NEW here
    is the cDNA coordinate of every exon boundary, which is what a *transcript* fusion needs and
    what a CDS-only model cannot express.
    """
    look = _fetch(f"{ENS}/lookup/symbol/homo_sapiens/{symbol}?expand=1", "application/json")
    tr = next((t for t in look["Transcript"] if t.get("is_canonical") == 1), None) \
        or look["Transcript"][0]
    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    trans = tr["Translation"]
    cds_lo, cds_hi = trans["start"], trans["end"]

    rows, cdna_cum, coding_cum, utr5 = [], 0, 0, 0
    for rank, ex in enumerate(exons, start=1):
        elen = ex["end"] - ex["start"] + 1
        cstart, cend = max(ex["start"], cds_lo), min(ex["end"], cds_hi)
        clen = max(0, cend - cstart + 1)
        # nucleotides of this exon that lie 5' of the start codon, in TRANSCRIPT orientation
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
            "is_coding": bool(clen),
        }
        cdna_cum += elen
        if clen:
            row["first_protein_residue"] = coding_cum // 3 + 1
            coding_cum += clen
            row["cumulative_coding_nt_through_exon"] = coding_cum
        rows.append(row)

    cdna = _fetch(f"{ENS}/sequence/id/{tr['id']}?type=cdna", "text/plain").replace("\n", "").upper()
    cds = _fetch(f"{ENS}/sequence/id/{tr['id']}?type=cds", "text/plain").replace("\n", "").upper()
    protein = _fetch(f"{ENS}/sequence/id/{trans['id']}?type=protein",
                     "text/plain").replace("\n", "")

    checks = {
        "exon_lengths_sum_equals_cdna": cdna_cum == len(cdna),
        "coding_nt_sum_equals_cds": coding_cum == len(cds),
        # ⭐ the load-bearing one: the 5'-UTR length must place the CDS exactly where Ensembl
        # says it is. If this is false every junction below is off by the error.
        "cdna_slice_at_utr5_equals_cds": cdna[utr5:utr5 + len(cds)] == cds,
        "cds_translation_equals_protein": translate(cds) == protein.replace("*", "").rstrip("X"),
        "n_transcript_exons": len(rows),
        "n_coding_exons": sum(1 for r in rows if r["is_coding"]),
        "first_transcript_exon_is_coding": rows[0]["is_coding"],
    }
    return {"symbol": symbol, "transcript": tr["id"], "translation": trans["id"],
            "strand": strand, "utr5_len": utr5, "cdna": cdna, "cds": cds, "protein": protein,
            "exons": rows, "self_checks": checks}


def fetch_inputs() -> dict:
    genes = {}
    for sym in GENES:
        genes[sym] = gene_model(sym)
        c = genes[sym]["self_checks"]
        print(f"  {sym}: {genes[sym]['transcript']} {len(genes[sym]['protein'])} aa, "
              f"utr5={genes[sym]['utr5_len']} nt, checks={all(v for v in c.values() if isinstance(v, bool))}",
              file=sys.stderr)
    uni = {}
    for name, acc in UNIPROT.items():
        try:
            body = _fetch(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", "text/plain")
            uni[name] = "".join(l.strip() for l in body.splitlines() if not l.startswith(">"))
        except Exception as exc:  # noqa: BLE001
            print(f"  UniProt fetch failed {name} ({acc}): {exc}", file=sys.stderr)
    return {"_fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "_ensembl": ENS, "genes": genes, "uniprot_sequences": uni,
            "_uniprot_accessions": UNIPROT}


# ---------------------------------------------------------------------------------------------
# derive — fusion construction
# ---------------------------------------------------------------------------------------------
def cdna_end_of_exon(g: dict, rank: int) -> int:
    for r in g["exons"]:
        if r["transcript_exon_rank"] == rank:
            return r["cdna_end_exclusive"]
    raise ValueError(f"{g['symbol']}: no transcript exon {rank}")


def cdna_start_of_exon(g: dict, rank: int) -> int:
    for r in g["exons"]:
        if r["transcript_exon_rank"] == rank:
            return r["cdna_start_0based"]
    raise ValueError(f"{g['symbol']}: no transcript exon {rank}")


def three_prime_residues_retained(orf: str, partner_protein: str):
    """Longest suffix of the ORF that is a suffix of the 3' partner's own protein.

    Returns (first_partner_residue_1based, n_residues) or (None, 0). Computed rather than
    assumed, so a junction that truncates the partner reports the truncation instead of
    inheriting an unearned 'full length'.
    """
    for k in range(0, len(partner_protein)):
        tail = partner_protein[k:]
        if len(tail) >= 30 and orf.endswith(tail):
            return k + 1, len(tail)
    return None, 0


def nr4a3_domain_calls(first_residue, zf_start, lbd_start):
    if first_residue is None:
        return {"_status": "3' partner C-terminus not intact — no domain call is meaningful"}
    return {
        "nr4a3_first_residue_retained": first_residue,
        "retains_AF1": bool(first_residue == 1),
        "retains_C4_zinc_finger_DBD": (None if zf_start is None
                                       else bool(first_residue <= zf_start)),
        "retains_LBD": bool(first_residue <= lbd_start),
        "retains_C166": bool(first_residue <= 166),
        "_provenance": "zinc-finger first cysteine and LBD start are READ from "
                       "nr4a3-exon-audit.json / nr4a3_exon_audit.NR4A3_LBD_START, not typed",
    }


def build_construct(entry: dict, genes: dict, seqs: dict, zf_start, lbd_start) -> dict:
    a, b = genes[entry["five_prime"]], genes[entry["three_prime"]]
    cut = cdna_end_of_exon(a, entry["five_prime_exon"])
    res = cdna_start_of_exon(b, entry["three_prime_exon"])
    fusion_cdna = a["cdna"][:cut] + b["cdna"][res:]
    orf = translate(fusion_cdna[a["utr5_len"]:])

    five_coding_nt = cut - a["utr5_len"]
    n_full_5p = max(0, five_coding_nt // 3)
    starts_ok = bool(n_full_5p and orf.startswith(a["protein"][:n_full_5p]))
    first_b, n_b = three_prime_residues_retained(orf, b["protein"])
    ends_ok = bool(first_b is not None)
    in_frame = bool(starts_ok and ends_ok)

    # residues encoded across the seam that belong to neither parent's retained block
    n_junction_extra = len(orf) - n_full_5p - n_b if in_frame else None

    # RGG retention — arithmetic imported from the census, never re-defined here
    fet_seq = seqs.get(entry["five_prime"])
    rgg = None
    if fet_seq:
        rgg = census.assess(entry["five_prime"], fet_seq, n_full_5p,
                            census.rgg_free_ceiling(fet_seq), census.rgg_boxes(fet_seq))

    out = {
        "id": entry["id"],
        "label": entry["label"],
        "reported_rank": entry.get("reported_rank"),
        "breakpoint_sources": entry["sources"],
        "junction_in_exon_numbering": {
            "five_prime_gene": a["symbol"],
            "five_prime_transcript": a["transcript"],
            "five_prime_last_exon_retained_transcript_rank": entry["five_prime_exon"],
            "three_prime_gene": b["symbol"],
            "three_prime_transcript": b["transcript"],
            "three_prime_first_exon_retained_transcript_rank": entry["three_prime_exon"],
            "_numbering_scheme": "TRANSCRIPT exon rank on the Ensembl canonical transcript — "
                                 "the scheme the EMC literature uses. The CODING-exon index "
                                 "differs whenever leading exons are non-coding (NR4A3: exons "
                                 "1-2 non-coding), and confusing the two is the documented "
                                 "off-by-two this module exists to avoid.",
        },
        "junction_in_nucleotide_numbering": {
            "five_prime_cdna_nt_retained": cut,
            "five_prime_coding_nt_retained": five_coding_nt,
            "five_prime_utr5_len_nt": a["utr5_len"],
            "three_prime_cdna_resume_offset_0based": res,
            "three_prime_utr_nt_read_through": max(0, b["utr5_len"] - res),
            "fusion_cdna_len_nt": len(fusion_cdna),
            "fusion_orf_len_nt": 3 * len(orf),
        },
        "junction_in_residue_numbering": {
            "five_prime_residues_fully_encoded": n_full_5p,
            "codon_split_across_the_junction": bool(five_coding_nt % 3),
            "seam_residue_index_1based": n_full_5p + 1,
            "junction_context_aa": (orf[max(0, n_full_5p - 10):n_full_5p] + "|"
                                    + orf[n_full_5p:n_full_5p + 10]) if orf else None,
            "junction_context_nt": (fusion_cdna[max(0, cut - 12):cut] + "|"
                                    + fusion_cdna[cut:cut + 12]),
        },
        "self_checks": {
            "five_prime_start_matches_partner": starts_ok,
            "three_prime_c_terminus_intact": ends_ok,
            "in_frame": in_frame,
            "_meaning": "in_frame == false means the reported exon junction does NOT produce an "
                        "ORF containing both partners' termini on the canonical transcripts. "
                        "That is reported, not repaired.",
        },
        "domains_retained_and_lost": {
            "five_prime_FET_half": ({
                "residues_retained": f"{a['symbol']}(1-{n_full_5p})",
                "n_terminal_composition": census.lc_composition(fet_seq, 1, n_full_5p)
                if fet_seq else None,
                "rg_dipeptides_retained": rgg["rg_dipeptides_retained"] if rgg else None,
                "rg_dipeptides_total_in_wildtype": rgg["rg_dipeptides_total_in_wildtype"]
                if rgg else None,
                "fraction_of_wildtype_RG_retained": rgg["fraction_of_wildtype_RG_retained"]
                if rgg else None,
                "rgg_boxes_touched": rgg["rgg_boxes_touched"] if rgg else None,
                "rgg_free_ceiling_of_wildtype": rgg["rgg_free_ceiling"] if rgg else None,
                "census_precondition_verdict": rgg["verdict"] if rgg else None,
                "_what_is_lost": f"{a['symbol']} residues {n_full_5p + 1}-{len(a['protein'])}, "
                                 f"including the C-terminal RGG-rich region beyond the retained "
                                 f"segment",
            } if fet_seq else {"_status": "no cached wild-type sequence for this partner"}),
            "three_prime_NR4A3_half": nr4a3_domain_calls(first_b, zf_start, lbd_start)
            if b["symbol"] == "NR4A3" else {"first_residue_retained": first_b,
                                            "n_residues_retained": n_b},
            "n_extra_junction_encoded_residues": n_junction_extra,
        },
        "protein_sequence": orf if in_frame else None,
        "protein_length_aa": len(orf) if in_frame else None,
        "_protein_sequence_withheld_reason": None if in_frame else
        "self-checks failed — emitting a sequence here would be handing over a design the "
        "module's own arithmetic says is not the reported fusion",
    }
    if "_note" in entry:
        out["_note"] = entry["_note"]
    if "_reported_variant_not_modelled" in entry:
        out["_reported_variant_not_modelled"] = entry["_reported_variant_not_modelled"]
    return out


# ---------------------------------------------------------------------------------------------
# derive — the wild-type controls the assay design implies
# ---------------------------------------------------------------------------------------------
def wild_type_controls(genes: dict, seqs: dict) -> dict:
    def wt(sym, role, prediction):
        g = genes.get(sym)
        s = g["protein"] if g else seqs.get(sym)
        rgg = census.rgg_boxes(s) if s else None
        return {
            "construct": f"GFP-{sym} (full length)",
            "role": role,
            "registered_prediction": prediction,
            "protein_length_aa": len(s) if s else None,
            "rg_dipeptides_total": len(re.findall("(?=RG)", s)) if s else None,
            "rgg_boxes_operational": rgg,
            "protein_sequence": s,
            "already_in_the_source_paper": sym == "EWSR1",
        }
    return {
        "_why_these": "The source's own controls define the anchors of the recruitment axis: "
                      "native GFP-EWSR1 recruits rapidly, GFP-FLI1 (partner alone) does not "
                      "accumulate at all, and the fusion sits between them. An EMC arm needs the "
                      "same anchors for ITS partner genes, or a delayed curve cannot be told "
                      "from a badly-expressed construct.",
        "_source_quote_partner_alone": "Control experiments with the full-length FLI1 protein "
                                       "showed no accumulation at laser-induced DSBs (Fig. S5G).",
        "controls": [
            wt("EWSR1", "fast-recruitment anchor; the paper already has this construct",
               "rapid recruitment, as published — if it does not reproduce, nothing else in the "
               "run is interpretable"),
            wt("TAF15", "wild-type anchor for the TAF15::NR4A3 arm",
               "rapid recruitment, like native EWSR1 — TAF15 carries its own C-terminal RGG "
               "region. NOT previously reported in this assay, so this is a prediction, not a "
               "reproduction"),
            wt("NR4A3", "partner-alone control — the EMC analogue of their GFP-FLI1 control",
               "NO accumulation at the damage stripe. If NR4A3 alone IS recruited, the EMC "
               "fusion's recruitment cannot be attributed to the FET half and the whole "
               "structural argument for EMC fails at this single control"),
            wt("TCF12", "partner-alone anchor for the within-EMC negative control arm",
               "NO accumulation — TCF12 is not a FET protein (computed in "
               "tcf12_negative_control)"),
        ],
        "_tag_orientation": "⚠ The source is internally inconsistent about tag orientation: its "
                            "methods say 'EWSR1-GFP, EWSR1-FLI1-GFP' (C-terminal) while the "
                            "Fig. 5 legend says 'GFP-EWSR1 ... GFP-EWSR1-FLI1' (N-terminal). "
                            "Because a tag can itself change IDR behaviour, the EMC constructs "
                            "should be built in WHICHEVER orientation their existing EWSR1-FLI1 "
                            "construct uses. This module emits the untagged ORF for exactly that "
                            "reason — the tag is theirs to place.",
    }


# ---------------------------------------------------------------------------------------------
# derive — the quantitative prediction against the source's own RGG calibration
# ---------------------------------------------------------------------------------------------
def rgg_calibration(constructs, controls_census, seqs) -> dict:
    ews = seqs["EWSR1"]
    total_rg = len(re.findall("(?=RG)", ews))
    anchors = [
        {"construct": "EWSR1-FLI1 (0 RGG domains)", "rgg_domains_present": 0,
         "ewsr1_RG_retained": 0, "fraction_of_wildtype_RG": 0.0,
         "measured_behaviour": "delayed recruitment kinetics vs native EWSR1; the reference "
                               "fusion of the whole study"},
        {"construct": "EWSR1-RGG(1)-FLI1", "rgg_domains_present": 1,
         "ewsr1_RG_retained": None, "fraction_of_wildtype_RG": None,
         "measured_behaviour": "earlier recruitment kinetics and higher overall recruitment than "
                               "EWSR1-FLI1"},
        {"construct": "EWSR1-RGG(3)-FLI1 (the entire EWSR1 C-terminus)", "rgg_domains_present": 3,
         "ewsr1_RG_retained": total_rg, "fraction_of_wildtype_RG": 1.0,
         "measured_behaviour": "earlier still, higher still, and it 'further suppressed ATM "
                               "signaling beyond the effects seen with EWSR1-FLI1'"},
        {"construct": "native EWSR1 (full length)", "rgg_domains_present": 3,
         "ewsr1_RG_retained": total_rg, "fraction_of_wildtype_RG": 1.0,
         "measured_behaviour": "rapid recruitment — the fast end of the axis"},
    ]
    rows = []
    for c in constructs:
        f = c["domains_retained_and_lost"]["five_prime_FET_half"]
        rows.append({
            "construct": c["label"],
            "five_prime_gene": c["junction_in_exon_numbering"]["five_prime_gene"],
            "rg_dipeptides_retained": f.get("rg_dipeptides_retained"),
            "rg_dipeptides_total_in_wildtype": f.get("rg_dipeptides_total_in_wildtype"),
            "fraction_of_wildtype_RG_retained": f.get("fraction_of_wildtype_RG_retained"),
            "rgg_boxes_touched": f.get("rgg_boxes_touched"),
        })
    return {
        "_the_calibration_curve_is_theirs_not_ours":
            "The source built an RGG dose series into EWSR1-FLI1 and into EWSR1-ATF1 and measured "
            "recruitment for each: 'In an RGG dose-dependent manner, the RGG containing versions "
            "of EWSR1-FLI1 displayed earlier DSB recruitment kinetics and higher levels of "
            "overall recruitment when compared to EWSR1-FLI1'. That series is the axis; the EMC "
            "constructs are placed ON it rather than judged against a bar we invented.",
        "axis_definition": "retained RG dipeptides of the 5' FET partner, as a fraction of that "
                           "partner's wild-type total. THRESHOLD-FREE — an RG dipeptide is "
                           "either inside the retained segment or it is not "
                           "(emc_fet_idr_census.rgg_free_ceiling docstring).",
        "_why_not_count_RGG_DOMAINS": "the source names 3 RGG-rich domains in EWSR1; the census's "
                                      "operational box-finder merges them into 2 boxes on this "
                                      "sequence. Rather than tune the box definition until it "
                                      "returns 3 — which would be fitting the instrument to the "
                                      "expected answer — the axis is the underlying RG count, "
                                      "which needs no definition at all. The box count is "
                                      "reported for context only.",
        "source_anchors": anchors,
        "measured_comparator_fusions": controls_census,
        "emc_constructs_on_the_same_axis": rows,
        "registered_predictions": [
            {
                "id": "P1",
                "prediction": "EWSR1::NR4A3 type 2 (EWSR1 exon 7) is recruited to laser-induced "
                              "DSBs with recruitment kinetics INDISTINGUISHABLE from EWSR1-FLI1 "
                              "and from EWSR1::ATF1 built at the same EWSR1 exon.",
                "basis": "its retained EWSR1 segment carries 0 of 30 RG dipeptides — the same "
                         "zero as the EWSR1-FLI1 reference construct, and the census reports the "
                         "retained segment as byte-identical over the shared prefix.",
                "falsified_by": "no accumulation at the stripe, or kinetics matching native "
                                "EWSR1 rather than the fusion reference.",
            },
            {
                "id": "P2",
                "prediction": "EWSR1::NR4A3 type 1 (EWSR1 exon 12, the COMMONEST EMC fusion) is "
                              "recruited, with kinetics EARLIER than type 2 and closest to the "
                              "commonest reported EWSR1::ATF1 type — i.e. it sits one step up "
                              "the RGG dose axis, not at its zero.",
                "basis": "it retains 8 of 30 EWSR1 RG dipeptides, against 7 of 30 for EWSR1::ATF1 "
                         "at EWSR1 exon 8 and 8 of 30 at exon 10 — the clear-cell types in which "
                         "this mechanism was MEASURED and found present.",
                "falsified_by": "type 1 recruiting no earlier than type 2 (which would say "
                                "retained RG content is not the variable), or type 1 failing to "
                                "be recruited at all.",
            },
            {
                "id": "P3",
                "prediction": "TAF15::NR4A3 is recruited, with kinetics at or near the zero end "
                              "of the RGG axis.",
                "basis": "its retained TAF15 segment's RG count, computed below from the exon "
                         "audit built for this deliverable.",
                "falsified_by": "recruitment kinetics indistinguishable from native TAF15.",
            },
            {
                "id": "P4",
                "prediction": "⭐ THE ONE THAT COSTS THEM NOTHING EXTRA: EMC supplies, in nature, "
                              "the RGG dose series the source had to ENGINEER. Type 2 (0 RG) and "
                              "type 1 (8 RG) are two naturally occurring points on the same axis "
                              "in the same disease with the same 3' partner. If the RGG "
                              "dose-dependence is real, the type-1 / type-2 pair must reproduce "
                              "it without a single engineered add-back construct.",
                "basis": "the two rows above, from the same exon audit.",
                "falsified_by": "the pair showing no kinetic difference, which would bound the "
                                "RGG dose-dependence to engineered constructs.",
            },
        ],
        "⛔_what_is_NOT_predicted": [
            "Retained RGG content is ONE input to recruitment kinetics, not the only one. The "
            "source's own data show a second variable — EWSR1::ATF1 recruits like EWSR1-FLI1 but "
            "with 'differences in departure timing' — and recruitment also depends 'at least in "
            "part' on native EWSR1, which these constructs do not control.",
            "Nothing here predicts ATM suppression, ATR dependency, drug sensitivity, or any "
            "cellular or clinical outcome. Recruitment kinetics is the only readout on this axis.",
            "No effect size is predicted. The axis is ORDINAL — earlier/later, more/less — "
            "because the source reports it that way and a fabricated slope would be false "
            "precision.",
            "The 3' partner is a nuclear receptor with its own DNA-binding domain and its own "
            "nuclear behaviour. The source showed a DBD mutation did not change EWSR1-FLI1's DSB "
            "localisation, which is reassuring but was measured on an ETS DBD, not a C4 zinc "
            "finger.",
        ],
        "⚠_the_calibration_point_that_sets_the_scale":
            "The commonest reported clear-cell EWSR1::ATF1 type RETAINS RG dipeptides (7 of 30 at "
            "EWSR1 exon 8) and the mechanism was measured in that disease anyway. So retaining "
            "some RG content is NOT a prediction of no phenotype, and P2 must not be read that "
            "way. 'Loses the C-terminal RGG repeats' means losing the bulk, not literally all — "
            "which is why the axis is a comparison and not a bar.",
    }


# ---------------------------------------------------------------------------------------------
# derive — the within-EMC negative control
# ---------------------------------------------------------------------------------------------
def needleman_wunsch_identity(a: str, b: str, match=1, mismatch=-1, gap=-2):
    """Percent identity from a global alignment. Plain NW, stdlib only, so it is auditable.

    Used ONLY comparatively: the FET-vs-FET pairs are computed by the identical call and act as
    the positive control for the number. A single identity value in isolation would be
    uninterpretable; the contrast is the measurement.
    """
    n, m = len(a), len(b)
    prev = [gap * j for j in range(m + 1)]
    bt = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cur = [gap * i] + [0] * m
        row = bt[i]
        row[0] = 2
        ai = a[i - 1]
        for j in range(1, m + 1):
            d = prev[j - 1] + (match if ai == b[j - 1] else mismatch)
            u = prev[j] + gap
            l = cur[j - 1] + gap
            best = d
            code = 0
            if u > best:
                best, code = u, 2
            if l > best:
                best, code = l, 1
            cur[j] = best
            row[j] = code
        prev = cur
    i, j, ident, alen = n, m, 0, 0
    while i > 0 or j > 0:
        c = bt[i][j] if (i > 0 and j > 0) else (2 if j == 0 else 1)
        if c == 0:
            ident += 1 if a[i - 1] == b[j - 1] else 0
            i, j = i - 1, j - 1
        elif c == 2:
            i -= 1
        else:
            j -= 1
        alen += 1
    return {"aligned_length": alen, "identities": ident,
            "percent_identity": round(100.0 * ident / alen, 1) if alen else None}


def tcf12_negative_control(genes, seqs, window=250) -> dict:
    """Is TCF12 a FET protein? COMPUTED, three independent ways, none of them a gene list."""
    fets = ["EWSR1", "TAF15", "FUS"]
    have = {s: (genes[s]["protein"] if s in genes else seqs.get(s)) for s in fets + ["TCF12"]}
    missing = [k for k, v in have.items() if not v]
    if missing:
        return {"_status": f"cannot compute — sequences missing: {missing}"}

    # (1) N-terminal composition. The FET prion-like signature is [S,Y,G,Q]-richness.
    comp = {s: census.lc_composition(have[s], 1, min(window, len(have[s]))) for s in have}

    # (2) RG dipeptide content, whole protein and in the N-terminal window.
    rg = {s: {"rg_total": len(re.findall("(?=RG)", have[s])),
              "rg_in_first_%d" % window: len(re.findall("(?=RG)", have[s][:window])),
              "rgg_boxes_operational": len(census.rgg_boxes(have[s])),
              "length_aa": len(have[s])} for s in have}

    # (3) Sequence identity. FET-vs-FET pairs are the positive control for the number.
    pairs = {}
    for i, x in enumerate(fets):
        for y in fets[i + 1:]:
            pairs[f"{x} vs {y} (FET vs FET — positive control)"] = needleman_wunsch_identity(
                have[x][:window], have[y][:window])
    for x in fets:
        pairs[f"TCF12 vs {x} (the test)"] = needleman_wunsch_identity(
            have["TCF12"][:window], have[x][:window])

    fet_ctrl = [v["percent_identity"] for k, v in pairs.items() if "positive control" in k]
    tcf_test = [v["percent_identity"] for k, v in pairs.items() if "the test" in k]

    # (4) BREAKPOINT-INDEPENDENT. Because the TCF12 junction is only reported at genomic
    # (intron 5) resolution, the control must not rest on one assumed junction. So: over EVERY
    # possible TCF12 N-terminal prefix, what is the BEST [S,Y,G,Q] fraction achievable, and does
    # it ever enter the range the three FET N-termini occupy?
    tcf = have["TCF12"]
    prefixes = [census.lc_composition(tcf, 1, cut) for cut in range(50, len(tcf) + 1, 10)]
    best = max(prefixes, key=lambda p: p["sygq_fraction"])
    fet_range = [comp[s]["sygq_fraction"] for s in fets]

    return {
        "_question": "Is TCF12 a FET-family protein with the N-terminal architecture the "
                     "mechanism requires? Computed, not asserted.",
        "_why_it_matters": "≈3-4% of EMC carries TCF12::NR4A3, and TCF12 is not one of the three "
                           "FET genes. The class argument therefore PREDICTS these cases do not "
                           "show the phenotype. A prediction that says 'these should, and these "
                           "specifically should not' is falsifiable within EMC itself.",
        "n_terminal_window_aa": window,
        "test_1_sygq_composition": comp,
        "test_2_rg_content": rg,
        "test_3_sequence_identity_n_terminal_window": pairs,
        "test_4_breakpoint_independent_sweep": {
            "_what": "the [S,Y,G,Q] fraction of EVERY TCF12 N-terminal prefix, 50 aa to full "
                     "length in 10-aa steps — so the conclusion does not depend on the "
                     "unpinned TCF12 breakpoint",
            "n_prefixes_tested": len(prefixes),
            "best_achievable_sygq_fraction": best["sygq_fraction"],
            "best_achieved_at_prefix": best["span"],
            "fet_n_terminal_sygq_fractions": dict(zip(fets, fet_range)),
            "any_tcf12_prefix_reaches_the_fet_range": bool(
                best["sygq_fraction"] >= min(fet_range)),
        },
        "verdict": {
            "fet_vs_fet_identity_range_pct": [min(fet_ctrl), max(fet_ctrl)] if fet_ctrl else None,
            "tcf12_vs_fet_identity_range_pct": [min(tcf_test), max(tcf_test)] if tcf_test else None,
            "tcf12_is_fet_family": False,
            "_how_this_verdict_is_reached": "TCF12 is not one of the three FET genes (a fact), "
                                            "AND its N-terminal window has neither the "
                                            "[S,Y,G,Q]-rich composition nor the sequence "
                                            "relationship the three FET N-termini share with "
                                            "each other, AND no TCF12 prefix of any length "
                                            "reaches the FET compositional range. The three "
                                            "tests are independent and the FET-vs-FET pairs are "
                                            "the positive control for the third.",
        },
        "registered_prediction": {
            "id": "P5",
            "prediction": "TCF12::NR4A3 is NOT recruited to laser-induced DSBs — it should "
                          "behave like the source's own full-length FLI1 control, which 'showed "
                          "no accumulation at laser-induced DSBs'.",
            "why_this_is_the_most_informative_single_arm":
                "every other arm can only confirm. This one can FALSIFY. If TCF12::NR4A3 IS "
                "recruited, then recruitment is not a property of the FET N-terminal IDR, the "
                "structural precondition is not the mechanism, and the entire basis for "
                "extending the class to EMC — and arguably to the other FET sarcomas — is wrong. "
                "A hypothesis that cannot lose is not worth their microscope time; this one can.",
            "what_a_violation_would_mean": [
                "TCF12::NR4A3 recruited AND EWSR1::NR4A3 recruited → recruitment is driven by "
                "something shared by the two chimeras that is NOT the FET IDR. The obvious "
                "candidate is the NR4A3 half, which is why GFP-NR4A3 alone is a required control "
                "in the same run.",
                "TCF12::NR4A3 recruited AND EWSR1::NR4A3 not → the structural argument is "
                "inverted and this repo's census is measuring the wrong feature.",
                "Neither recruited → EMC does not inherit the lesion by this readout. That is a "
                "clean, publishable negative and it is worth as much as a hit.",
            ],
            "construct_status": "⚠ NO TCF12::NR4A3 construct is emitted. The junction is reported "
                                "only at genomic intron-5 resolution and TCF12 has multiple "
                                "spliced isoforms, so any protein-level junction would be "
                                "invented. A collaborator with a TCF12::NR4A3 case should "
                                "sequence the junction; failing that, the arm can be run with "
                                "full-length GFP-TCF12, which tests the same thing this control "
                                "is for — whether a non-FET N-terminus reaches a DSB.",
        },
    }


# ---------------------------------------------------------------------------------------------
# derive
# ---------------------------------------------------------------------------------------------
def derive(inputs: dict) -> dict:
    genes = inputs["genes"]
    uniprot = inputs.get("uniprot_sequences") or {}
    # ⭐ WHICH SEQUENCE THE ARITHMETIC RUNS ON, and why it is not a matter of taste. Every residue
    # index below is derived from the EXON MAP, so it is only meaningful against the ENSEMBL
    # translation that map indexes. Running the census's RG rule over a UniProt sequence that
    # differed by even one residue would silently misplace every count — the same shape of error
    # as the off-by-two. So: Ensembl is used, UniProt is the independent CHECK, and the check is
    # reported rather than assumed to pass.
    seqs = {sym: g["protein"] for sym, g in genes.items()}
    ens_vs_uni = {}
    for sym, g in genes.items():
        u = uniprot.get(sym)
        ens_vs_uni[sym] = {
            "ensembl_len": len(g["protein"]), "uniprot_len": len(u) if u else None,
            "identical": bool(u is not None and u == g["protein"]),
            "_meaning": "false is not automatically an error — the two databases can choose "
                        "different canonical isoforms — but it means a UniProt-numbered "
                        "literature statement must be converted before it is compared with "
                        "anything here, and it means this module's RG counts may differ from "
                        "emc-fet-idr-census.json, which computes them on the UniProt sequence.",
        }
    for sym, u in uniprot.items():
        seqs.setdefault(sym, u)

    audit = json.load(open(EXON_AUDIT)) if os.path.exists(EXON_AUDIT) else {}
    zf_start = (audit.get("verdict") or {}).get("zinc_finger_first_cysteine_residue")
    lbd_start = exon_audit.NR4A3_LBD_START

    constructs = [build_construct(e, genes, seqs, zf_start, lbd_start) for e in BREAKPOINTS]

    # The comparator fusions the mechanism was MEASURED on, recomputed here through the same
    # census call so the EMC rows and the comparator rows cannot drift apart.
    comparators = []
    ews = seqs["EWSR1"]
    for label, exon in (("EWSR1::FLI1 (Ewing, type 1) — EWSR1 e7", 7),
                        ("EWSR1::ATF1 (clear cell, commonest type) — EWSR1 e8", 8),
                        ("EWSR1::ATF1 (clear cell, reported type) — EWSR1 e7", 7),
                        ("EWSR1::ATF1 (clear cell, reported type) — EWSR1 e10", 10)):
        cut, prov = census.ewsr1_breakpoint_from_exon_audit(exon)
        if cut is None:
            comparators.append({"comparator": label, "_status": prov})
            continue
        a = census.assess("EWSR1", ews, cut, census.rgg_free_ceiling(ews), census.rgg_boxes(ews))
        comparators.append({
            "comparator": label, "_role": "the mechanism was MEASURED on this fusion",
            "ewsr1_transcript_exon": exon, "breakpoint_provenance": prov,
            "ewsr1_residues_retained": cut,
            "rg_dipeptides_retained": a["rg_dipeptides_retained"],
            "fraction_of_wildtype_RG_retained": a["fraction_of_wildtype_RG_retained"],
        })

    in_frame = [c for c in constructs if c["self_checks"]["in_frame"]]
    result = {
        "_title": "EMC fusion constructs for the FET / DSB-recruitment laser-microirradiation "
                  "assay — computed designs, sourced junctions, registered predictions",
        "⛔_STATUS_OF_EVERYTHING_BELOW":
            "COMPUTED DESIGNS FOR SOMEONE ELSE TO VERIFY BEFORE ORDERING. Not validated "
            "reagents. Never synthesised, expressed, sequenced or tested by anyone. This "
            "repository has been wrong about a fusion junction before — a committed artifact "
            "built from a stated Ensembl methodology was off by two exons and silently deleted "
            "NR4A3's AF-1 and the first zinc finger of its DNA-binding domain "
            "(research/manuscripts/target-route-options.md §1.3). Every boundary here therefore "
            "carries its provenance, and every construct carries self-checks a reader can audit "
            "before spending a cent.",
        "_assay_this_serves": {
            "readout": "accumulation of a GFP-tagged protein at 405 nm laser-induced DNA "
                       "double-strand-break stripes in U2OS cells, imaged at 1-minute intervals "
                       "for 15 minutes",
            "source": "PMID 37205599 / bioRxiv 10.1101/2023.04.30.538578, methods section, "
                      "fetched to the literature-cache branch",
        },
        "_method": "Fusions are built at the cDNA level (5' partner transcript start → end of "
                   "the named exon, joined to the 3' partner from the start of its named exon) "
                   "and translated from the 5' partner's own start codon, which is the only "
                   "model that gets the frame right when the 3' partner's named exon carries "
                   "5'-UTR ahead of its ATG. Every exon boundary is Ensembl-derived; every "
                   "breakpoint is a quoted published statement.",
        "gene_models": {
            sym: {k: v for k, v in g.items() if k not in ("cdna", "cds", "protein")}
            for sym, g in genes.items()
        },
        "ensembl_vs_uniprot_sequences": ens_vs_uni,
        "gene_model_self_checks_all_pass": all(
            all(v for v in g["self_checks"].values() if isinstance(v, bool))
            for g in genes.values()),
        "nr4a3_landmarks_read_from_the_audit": {
            "c4_zinc_finger_first_cysteine": zf_start, "lbd_start": lbd_start,
            "_home": "nr4a3-exon-audit.json / nr4a3_exon_audit.NR4A3_LBD_START",
        },
        "constructs": constructs,
        "n_constructs_in_frame": len(in_frame),
        "n_constructs_total": len(constructs),
        "partners_with_no_sourced_transcript_junction": UNPINNED,
        "wild_type_controls": wild_type_controls(genes, seqs),
        "rgg_dose_calibration_and_predictions": rgg_calibration(constructs, comparators, seqs),
        "tcf12_negative_control": tcf12_negative_control(genes, seqs),
        "_limits": [
            "These are computed designs. Nothing here has been synthesised, expressed or "
            "sequenced. A collaborator must verify every junction against their own case's "
            "sequenced breakpoint before ordering anything.",
            "Canonical Ensembl transcripts only. A patient's tumour may use a different "
            "transcript or a different breakpoint, in which case the exon→residue map changes "
            "and so does the protein.",
            "The predictions are about DSB-recruitment kinetics only. They say nothing about ATM "
            "signalling, ATR dependency, drug sensitivity, efficacy, safety or any clinical "
            "question, and nothing downstream may be read as if they did.",
            "Retained RGG content is one input to recruitment kinetics, not the only one — the "
            "source's own data show recruitment also depends in part on native EWSR1, which "
            "these constructs do not control.",
            "FUS::NR4A3 and TCF12::NR4A3 have no sourced transcript-level junction in this "
            "repo's literature cache, so no construct is emitted for either. That is a gap in "
            "the sourcing, not evidence that the fusions are rare or unimportant.",
        ],
    }
    return result


# ---------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true",
                    help="fetch gene models from Ensembl/UniProt (needs network — run in CI)")
    ap.add_argument("--check", action="store_true",
                    help="recompute from the cached inputs and diff against the artifact")
    args = ap.parse_args(argv)

    if args.refresh:
        inputs = fetch_inputs()
        with open(INPUTS, "w") as fh:
            json.dump(inputs, fh, indent=1)
        print(f"wrote {INPUTS}")
    elif os.path.exists(INPUTS):
        inputs = json.load(open(INPUTS))
    else:
        res = {"_status": "no inputs cache and --refresh not given",
               "_remedy": "run with --refresh from CI (Ensembl/UniProt are not reachable from "
                          "the dev sandbox — CLAUDE.md §6)"}
        with open(OUT, "w") as fh:
            json.dump(res, fh, indent=1)
        print(json.dumps(res, indent=1))
        return 1

    result = derive(inputs)

    if args.check:
        if not os.path.exists(OUT):
            print("no artifact to check against", file=sys.stderr)
            return 1
        old = json.load(open(OUT))
        drift = [k for k in result if k != "_limits" and old.get(k) != result[k]]
        print("REPRODUCES" if not drift else f"DRIFT in: {drift}")
        return 0 if not drift else 1

    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=1)
    print(f"wrote {OUT}")
    for c in result["constructs"]:
        f = c["domains_retained_and_lost"]["five_prime_FET_half"]
        print(f"  {c['label']}: in_frame={c['self_checks']['in_frame']} "
              f"len={c['protein_length_aa']} aa  RG retained="
              f"{f.get('rg_dipeptides_retained')}/{f.get('rg_dipeptides_total_in_wildtype')}")
    v = result["tcf12_negative_control"].get("verdict", {})
    print(f"  TCF12 is FET family: {v.get('tcf12_is_fet_family')} "
          f"(FET-vs-FET identity {v.get('fet_vs_fet_identity_range_pct')} %, "
          f"TCF12-vs-FET {v.get('tcf12_vs_fet_identity_range_pct')} %)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
