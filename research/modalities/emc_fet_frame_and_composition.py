#!/usr/bin/env python3
"""
The frame rule, the type-2 seam at nucleotide resolution, and the compositional background — the
numbers a reviewer asked for that no committed artifact yet held.

WHY THIS MODULE EXISTS
----------------------
`emc_fet_construct_designs.py` computes the four reported EMC constructs and their retained-RG
placement. A simulated review of the manuscript built on it
(`research/manuscripts/emc-atr-collaborator-package-peer-review-2026-08-10.md`) asked for five
things that were computable from the same committed cache and lived nowhere:

  1. THE FRAME RULE. The manuscript reported four in-frame junctions as four checked examples.
     One rule governs all of them, and `junction-mrna-frame-audit.json` already grades it across
     27 EWSR1 x NR4A3 pairs. This module reads that audit, re-derives every row from the cache
     independently, and states the rule as a rule.
  2. THE SEAM ARITHMETIC. "176 nucleotides ... encoding 59 residues" was one nucleotide short in
     four places of the manuscript. 176 is not a multiple of three. The 59th codon is completed by
     a base EWSR1 donates across the seam, so the residues span 177 nt: 1 from EWSR1 and 176 from
     NR4A3 (174 of exon 2, 2 of exon 3's 5'UTR). The substance was right and the sentence was
     wrong; this pins the arithmetic so no future sentence can drift off it.
  3. THE SYMMETRIC PREFIX SWEEP. The TCF12 sweep gave TCF12 every prefix from 50 aa to full length
     and compared its BEST value against the FET proteins at a single fixed 250-aa window. That is
     an asymmetric comparison and it flatters the separation. Sweeping all four proteins over the
     same grid is the honest test.
  4. A BACKGROUND FOR [S,Y,G,Q]. Those four residues have a substantial background frequency in any
     protein, so 0.368 carries no scale on its own. The committed cache already holds four non-FET
     proteins (TCF12, NR4A3, FLI1, ATF1); measuring all of them on the same window puts the value
     on a scale at no cost.
  5. COUNTED FUSION-TYPE FREQUENCIES. The manuscript ranked EWSR1::NR4A3 type 2 "second" with no
     counted source. Three counted series sit in this repository's own committed retrieval record.
     They are extracted here VERBATIM, by PMID, never typed.

WHAT IT DOES NOT DO
-------------------
No potency, binding, expression, tolerability or clinical claim. Exon arithmetic, sequence
composition, and counts quoted from committed abstracts. It performs no network call: every input
is a committed file.

    python3 research/modalities/emc_fet_frame_and_composition.py            # write the artifact
    python3 research/modalities/emc_fet_frame_and_composition.py --check    # recompute and diff
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
INPUTS = os.path.join(HERE, "emc-construct-inputs.json")
FRAME_AUDIT = os.path.join(HERE, "junction-mrna-frame-audit.json")
DESIGNS = os.path.join(HERE, "emc-fet-construct-designs.json")
LIT = os.path.join(REPO, "research", "manuscripts", "aso", "lit-targets-aso-verify.json")
OUT = os.path.join(HERE, "emc-fet-frame-and-composition.json")

#: The prefix grid, identical for every protein. Taken from the existing TCF12 sweep in
#: `emc_fet_construct_designs.tcf12_negative_control` so the two are comparable: 50 aa to full
#: length in 10-aa steps.
PREFIX_MIN, PREFIX_STEP = 50, 10
SYGQ = "SYGQ"
IDR_WINDOW = 250  # the fixed N-terminal window the existing test_1 uses

_BASES = "TCAG"
_AAS = ("FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG")
CODON_TABLE = {a + b + c: _AAS[i] for i, (a, b, c) in enumerate(
    (x, y, z) for x in _BASES for y in _BASES for z in _BASES)}


def translate(cds: str) -> str:
    return "".join(CODON_TABLE[cds[i:i + 3]] for i in range(0, len(cds) - len(cds) % 3, 3))


def sygq_fraction(seq: str, lo: int, hi: int):
    """[S,Y,G,Q] fraction of a 1-based inclusive span, rounded as the census rounds it."""
    seg = seq[max(0, lo - 1):hi]
    if not seg:
        return None
    return round(sum(seg.count(c) for c in SYGQ) / len(seg), 3)


def prefix_sweep(seq: str):
    """Every N-terminal prefix on the shared grid, as (cut, fraction) pairs."""
    return [(cut, sygq_fraction(seq, 1, cut))
            for cut in range(PREFIX_MIN, len(seq) + 1, PREFIX_STEP)]


def rg_positions(seq: str):
    """1-based positions of the first residue of every RG dipeptide."""
    return [m.start() + 1 for m in re.finditer("(?=RG)", seq)]


# ── inputs ────────────────────────────────────────────────────────────────────────────────────
def load():
    with open(INPUTS, encoding="utf-8") as fh:
        inputs = json.load(fh)
    with open(FRAME_AUDIT, encoding="utf-8") as fh:
        audit = json.load(fh)
    with open(DESIGNS, encoding="utf-8") as fh:
        designs = json.load(fh)
    with open(LIT, encoding="utf-8") as fh:
        lit = json.load(fh)
    return inputs, audit, designs, lit


def exon(gene: dict, rank: int) -> dict:
    for e in gene["exons"]:
        if e["transcript_exon_rank"] == rank:
            return e
    raise KeyError(rank)


def coding_nt_through(gene: dict, rank: int) -> int:
    return exon(gene, rank)["cumulative_coding_nt_through_exon"]


# ── 1. the frame rule ─────────────────────────────────────────────────────────────────────────
def frame_rule(inputs, audit):
    """Re-derive the audit's verdict independently, then state the rule it implies.

    ⚠ The audit is READ for its rows and RE-COMPUTED here from the cache rather than trusted, because
    an artifact agreeing with itself is not a check. Any disagreement is emitted rather than smoothed.
    """
    ew, nr = inputs["genes"]["EWSR1"], inputs["genes"]["NR4A3"]

    # what each NR4A3 acceptor contributes ahead of NR4A3's own initiator codon
    acceptor_5utr = {}
    for rank in (2, 3):
        nt = 0
        for e in nr["exons"]:
            if e["transcript_exon_rank"] < rank:
                continue
            if e["is_coding"]:
                nt += e["exon_length_nt"] - e["coding_nt_in_exon"]
                break
            nt += e["exon_length_nt"]
        acceptor_5utr[rank] = nt

    rows, disagreements = [], []
    audit_rows = {(r["EWSR1_exon_end"], r["NR4A3_exon_start"]): r for r in audit["rows"]}
    for rank in sorted({e["transcript_exon_rank"] for e in ew["exons"] if e["is_coding"]}):
        cds = coding_nt_through(ew, rank)
        row = {
            "ewsr1_donor_exon": rank,
            "ewsr1_coding_nt_through_exon": cds,
            "ewsr1_last_whole_residue": cds // 3,
            "donor_end_phase": cds % 3,
            "in_frame_with_nr4a3_exon_2": (cds + acceptor_5utr[2]) % 3 == 0,
            "in_frame_with_nr4a3_exon_3": (cds + acceptor_5utr[3]) % 3 == 0,
        }
        rows.append(row)
        for acc in (2, 3):
            a = audit_rows.get((rank, acc))
            if a is None:
                continue
            if a["in_frame"] != row[f"in_frame_with_nr4a3_exon_{acc}"]:
                disagreements.append(f"EWSR1 e{rank} :: NR4A3 e{acc}")
            if a["nr4a3_acceptor_exon_5utr_nt_retained"] != acceptor_5utr[acc]:
                disagreements.append(f"acceptor 5'UTR nt for NR4A3 e{acc}")

    taf = inputs["genes"]["TAF15"]
    taf6 = coding_nt_through(taf, 6)

    in_frame = sorted(r["ewsr1_donor_exon"] for r in rows
                      if r["in_frame_with_nr4a3_exon_3"])
    phase1 = sorted(r["ewsr1_donor_exon"] for r in rows if r["donor_end_phase"] == 1)
    return {
        "_the_rule": "A 5' partner exon joined to NR4A3 exon 2 or exon 3 is in frame if and only if "
                     "the donor exon ends one nucleotide into a codon, that is if its cumulative "
                     "coding nucleotide count is congruent to 1 modulo 3. Both acceptors give the "
                     "same register, because NR4A3 exon 2 is 174 nt, a multiple of three.",
        "_why_both_acceptors_agree": {
            "nr4a3_exon_2_length_nt": exon(nr, 2)["exon_length_nt"],
            "nr4a3_exon_2_length_is_multiple_of_3": exon(nr, 2)["exon_length_nt"] % 3 == 0,
            "nr4a3_5utr_nt_retained_from_acceptor_exon_2": acceptor_5utr[2],
            "nr4a3_5utr_nt_retained_from_acceptor_exon_3": acceptor_5utr[3],
        },
        "ewsr1_donor_exons": rows,
        "phase_1_donor_exons": phase1,
        "in_frame_donor_exons": in_frame,
        "rule_holds_for_every_ewsr1_donor": in_frame == phase1,
        "taf15_exon_6": {
            "coding_nt_through_exon": taf6,
            "last_whole_residue": taf6 // 3,
            "donor_end_phase": taf6 % 3,
            "in_frame_with_nr4a3_exon_3": (taf6 + acceptor_5utr[3]) % 3 == 0,
        },
        "_cross_check_against_committed_audit": {
            "artifact": "junction-mrna-frame-audit.json",
            "n_rows_in_audit": audit["n_rows"],
            "disagreements": sorted(set(disagreements)),
        },
        "_limits": [
            "Frame only. Being in frame is not evidence that a junction occurs in a patient, that "
            "its transcript is stable, or that its protein is made.",
            "Canonical transcripts only, and one transcript per gene.",
        ],
    }


# ── 2. the type-2 seam ────────────────────────────────────────────────────────────────────────
def type2_seam(inputs, designs):
    ew, nr = inputs["genes"]["EWSR1"], inputs["genes"]["NR4A3"]
    e7 = exon(ew, 7)
    donor_cds = coding_nt_through(ew, 7)
    acc = exon(nr, 2)
    chimeric_cdna = (ew["cdna"][ew["utr5_len"]:e7["cdna_end_exclusive"]]
                     + nr["cdna"][acc["cdna_start_0based"]:])
    protein = translate(chimeric_cdna)
    stop = protein.find("*")
    orf = protein[:stop] if stop >= 0 else protein

    whole = donor_cds // 3
    donated = donor_cds % 3
    nr4a3_utr_nt = nr["utr5_len"] - sum(
        e["exon_length_nt"] for e in nr["exons"] if e["transcript_exon_rank"] < 2)
    span_nt = donated + nr4a3_utr_nt
    n_extra = span_nt // 3
    segment = orf[whole:whole + n_extra]
    hybrid_codon = (chimeric_cdna[donor_cds - donated:donor_cds]
                    + chimeric_cdna[donor_cds:donor_cds + 3 - donated])

    committed = next((c for c in designs["constructs"] if c["id"] == "EWSR1_NR4A3_type2"), None)
    return {
        "junction": "EWSR1 exon 7 :: NR4A3 exon 2",
        "ewsr1_coding_nt_through_exon_7": donor_cds,
        "ewsr1_whole_codons": whole,
        "ewsr1_nucleotides_donated_across_the_seam": donated,
        "nr4a3_5utr_nt_retained_total": nr4a3_utr_nt,
        "nr4a3_5utr_nt_from_exon_2": exon(nr, 2)["exon_length_nt"],
        "nr4a3_5utr_nt_from_exon_3": exon(nr, 3)["exon_length_nt"] - exon(nr, 3)["coding_nt_in_exon"],
        "nucleotides_spanned_by_the_extra_residues": span_nt,
        "_the_arithmetic": f"{donated} nt donated by EWSR1 + {nr4a3_utr_nt} nt of NR4A3 5'UTR "
                           f"= {span_nt} nt = {n_extra} codons",
        "extra_residues": n_extra,
        "first_extra_residue_is_a_hybrid_codon": {
            "codon": hybrid_codon,
            "residue": CODON_TABLE[hybrid_codon],
            "position_in_the_chimeric_protein": whole + 1,
            "composition": f"{donated} nt from EWSR1 + {3 - donated} nt from NR4A3",
        },
        "remaining_residues_encoded_by_nr4a3_alone": n_extra - 1,
        "extra_residue_sequence": segment,
        "internal_stop_codon_in_the_extension": "*" in translate(
            chimeric_cdna[donor_cds - donated:donor_cds - donated + span_nt]),
        "chimeric_orf_length_aa": len(orf),
        "nr4a3_moiety_starts_at_residue": whole + n_extra + 1,
        "nr4a3_moiety_complete": orf[whole + n_extra:] == nr["protein"],
        "matches_committed_construct_artifact": bool(
            committed and committed["protein_length_aa"] == len(orf)
            and committed["protein_sequence"] == orf),
        "_the_extension_is_a_property_of_the_acceptor": "Any 5' partner exon joined to NR4A3 exon 2 "
            "retains the same 176 nt of NR4A3 5' untranslated sequence. The extension therefore "
            "belongs to the exon 2 acceptor, not to type 2 in particular; what type 2 fixes is the "
            "frame it is read in.",
        "_limits": [
            "A computed consequence of the canonical transcripts for a reported exon junction, not "
            "an observed protein. No transcript, peptide or antibody evidence is offered here.",
        ],
    }


# ── 3 and 4. composition ──────────────────────────────────────────────────────────────────────
def composition(inputs):
    genes = inputs["genes"]
    uni = inputs["uniprot_sequences"]
    seqs = {k: genes[k]["protein"] for k in ("EWSR1", "TAF15", "FUS", "TCF12", "NR4A3")}
    seqs["FLI1"] = uni["FLI1"]
    seqs["ATF1"] = uni["ATF1"]
    fets = ["EWSR1", "TAF15", "FUS"]

    sweeps = {}
    for name, seq in seqs.items():
        pref = prefix_sweep(seq)
        best = max(pref, key=lambda p: p[1])
        low = min(pref, key=lambda p: p[1])
        sweeps[name] = {
            "length_aa": len(seq),
            "n_prefixes": len(pref),
            "best_sygq_fraction": best[1], "best_at_prefix": [1, best[0]],
            "lowest_sygq_fraction": low[1], "lowest_at_prefix": [1, low[0]],
        }
    fet_floor_name = min(fets, key=lambda k: sweeps[k]["lowest_sygq_fraction"])
    fet_floor = sweeps[fet_floor_name]["lowest_sygq_fraction"]
    tcf_best = sweeps["TCF12"]["best_sygq_fraction"]

    background = {name: {"n_terminal_%d_aa" % IDR_WINDOW: sygq_fraction(seq, 1, IDR_WINDOW),
                         "whole_protein": sygq_fraction(seq, 1, len(seq)),
                         "length_aa": len(seq),
                         "family": "FET" if name in fets else "non-FET"}
                  for name, seq in seqs.items()}

    return {
        "symmetric_prefix_sweep": {
            "_what": "The [S,Y,G,Q] fraction of every N-terminal prefix from %d aa to full length in "
                     "%d-aa steps, computed on the same grid for all four proteins. The published "
                     "version of this test swept TCF12 alone and compared its best value against the "
                     "FET proteins at one fixed 250-aa window, which is asymmetric and overstates "
                     "the separation." % (PREFIX_MIN, PREFIX_STEP),
            "per_protein": sweeps,
            "lowest_fet_prefix_value": fet_floor,
            "lowest_fet_prefix_protein": fet_floor_name,
            "lowest_fet_prefix_span": sweeps[fet_floor_name]["lowest_at_prefix"],
            "tcf12_best_prefix_value": tcf_best,
            "gap": round(fet_floor - tcf_best, 3),
            "any_tcf12_prefix_reaches_the_lowest_fet_prefix": tcf_best >= fet_floor,
            "_reading": "The separation survives on the symmetric test and it is narrow: no TCF12 "
                        "prefix of any length reaches the lowest value any FET prefix takes, but the "
                        "margin is the gap above, not the difference against the fixed-window value.",
        },
        "sygq_background_panel": {
            "_what": "The same statistic on every protein the committed cache holds, so the TCF12 "
                     "value can be read against a scale rather than against the FET proteins alone.",
            "_limits": [
                "Seven proteins is a comparison panel, not a proteome background. It bounds where "
                "the FET and non-FET values sit relative to each other and supplies no null "
                "distribution.",
                "ATF1 is 271 aa, so its N-terminal 250-aa value is nearly its whole-protein value.",
            ],
            "per_protein": background,
            "fet_range_n_terminal": [min(background[k]["n_terminal_250_aa"] for k in fets),
                                     max(background[k]["n_terminal_250_aa"] for k in fets)],
            "non_fet_range_n_terminal": [
                min(v["n_terminal_250_aa"] for v in background.values() if v["family"] == "non-FET"),
                max(v["n_terminal_250_aa"] for v in background.values() if v["family"] == "non-FET")],
        },
        "rg_content": {
            name: {"rg_dipeptides": len(rg_positions(seq)),
                   "rg_positions": rg_positions(seq)}
            for name, seq in seqs.items()
        },
        "taf15_zero_rg_margin": {
            "_two_conventions_that_differ_by_one": "The census reports the RG-free ceiling, the "
                "largest retained length carrying no RG dipeptide, which is one residue before the "
                "first RG. Subtracting the retained length from the ceiling gives the number of "
                "further residues that could be retained without touching an RG; subtracting it "
                "from the RG position gives the distance to that position.",
            "taf15_first_rg_position": rg_positions(seqs["TAF15"])[0],
            "rg_free_ceiling": rg_positions(seqs["TAF15"])[0] - 1,
            "retained_at_taf15_exon_6": 161,
            "residues_of_headroom_below_the_ceiling": rg_positions(seqs["TAF15"])[0] - 1 - 161,
            "distance_to_the_first_rg_position": rg_positions(seqs["TAF15"])[0] - 161,
        },
    }


# ── 5. counted fusion-type frequencies ────────────────────────────────────────────────────────
#: (PMID, the substring that anchors the extraction). Each quotation is CUT FROM the committed
#: abstract by locating this anchor, never transcribed, so a drifting abstract breaks the run
#: rather than silently changing a count in a manuscript.
SERIES = [
    ("12378528", "The most frequent EWS/CHN transcript", "Panagopoulos 2002"),
    ("11679947", "EWS-CHN type 1 in 11 cases", "Okamoto 2001"),
    ("12598313", "All tumors contained translocation-generated", "Sjogren 2003"),
]
GENOMIC = ("12378528", "In CHN, 12 breakpoints were found")


def _record(lit, pmid):
    for r in lit["records"]:
        if pmid in str(r.get("id", "")):
            return r
    raise KeyError(pmid)


def _sentence(text, anchor):
    i = text.index(anchor)
    start = text.rfind(". ", 0, i)
    start = 0 if start < 0 else start + 2
    end = text.find(". ", i)
    return text[start:end + 1 if end > 0 else len(text)].strip()


def counted_frequencies(lit):
    out = []
    for pmid, anchor, short in SERIES:
        r = _record(lit, pmid)
        out.append({
            "series": short,
            "pmid": pmid,
            "authors": r["authors"],
            "title": r["title"],
            "quotation": _sentence(r["abstract_verbatim"], anchor),
        })
    gen = _record(lit, GENOMIC[0])
    return {
        "_what": "Every counted EMC fusion-type series held in this repository's committed retrieval "
                 "record, quoted by locating an anchor substring inside the stored abstract.",
        "_why": "The manuscript ranked EWSR1::NR4A3 type 2 as the second commonest fusion. Neither "
                "source cited for that rank makes a frequency claim: one is a definition of the "
                "types and the other is an RT-PCR primer design. The rank appears to have been "
                "inferred from the type NUMBER. These are the counts that exist.",
        "series": out,
        "genomic_breakpoint_mapping": {
            "series": "Panagopoulos 2002",
            "pmid": GENOMIC[0],
            "quotation": _sentence(gen["abstract_verbatim"], GENOMIC[1]),
            "_what_it_fixes": "A genomic break in NR4A3 intron 2 produces a transcript joining to "
                              "exon 3; a break in intron 1 produces one joining to exon 2. The "
                              "12-to-2 split therefore maps the breakpoint literature's exon "
                              "numbering onto transcript exon ranks 2 and 3, and it counts how "
                              "often each acceptor is used.",
        },
        "_reading": [
            "Type 1 is the commonest EWSR1::NR4A3 transcript in every series that counts types.",
            "Type 2 is counted once, in Okamoto's 15 fusion-positive cases, and does not appear "
            "among the counted types of Panagopoulos's 15 EWS/CHN cases, whose stated second "
            "commonest transcript is type 5.",
            "TAF15::NR4A3 is counted in 3 of 18 (Panagopoulos), 3 of 15 fusion-positive (Okamoto) "
            "and 4 of 10 (Sjogren 2003), so it is the more frequently counted of the two zero-RG "
            "EMC fusions.",
        ],
        "_not_pooled_and_why": "The series are reported separately rather than pooled. The reports "
            "come from overlapping centres and the abstracts as retrieved do not establish that the "
            "cases are non-overlapping, which the repository's pooling policy requires "
            "(systems/POLICY-evidence.md).",
    }


# ── 6. the recruitment-axis rows, with what was and was not measured ──────────────────────────
def axis_rows(designs):
    """Every row the designs artifact carries, with the measurement status separated from the axis.

    ⚠ The manuscript's table labelled two different EWSR1::ATF1 breakpoints "measured" while the
    source built one EWSR1-ATF1 construct, and dropped both the third ATF1 breakpoint and the
    RGG(1) anchor. The artifact holds all four ATF1/FLI1 comparators and all four RGG anchors; the
    label they carry is that the mechanism was measured ON THAT FUSION, which does not fix which
    breakpoint the construct used.
    """
    r = designs["rgg_dose_calibration_and_predictions"]
    anchors = [{
        "row": a["construct"],
        "rg_retained": a["ewsr1_RG_retained"],
        "fraction": a["fraction_of_wildtype_RG"],
        "status": "measured in the source" if a["fraction_of_wildtype_RG"] is not None
                  else "measured in the source; not placeable on this axis",
        "why_not_placeable": None if a["fraction_of_wildtype_RG"] is not None
                             else "the source does not identify which RGG-rich domain was "
                                  "reintroduced, so its retained RG count is unknown",
    } for a in r["source_anchors"]]
    comparators = [{
        "row": c["comparator"],
        "ewsr1_residues_retained": c["ewsr1_residues_retained"],
        "rg_retained": c["rg_dipeptides_retained"],
        "fraction": c["fraction_of_wildtype_RG_retained"],
        "status": "a reported breakpoint of a fusion in which the mechanism was measured",
    } for c in r["measured_comparator_fusions"]]
    atf1 = [c for c in comparators if "ATF1" in c["row"]]
    fracs = sorted(c["fraction"] for c in atf1)
    return {
        "source_anchors": anchors,
        "reported_breakpoints_of_measured_fusions": comparators,
        "atf1_comparator_span": [fracs[0], fracs[-1]],
        "_why_a_span": "Reference 1 built one EWSR1-ATF1 construct and the retrieved text does not "
                       "state its EWSR1 breakpoint. Three EWSR1::ATF1 breakpoints are reported in "
                       "the literature, retaining 0, 7 and 8 of 30 RG dipeptides, so the comparator "
                       "is a span rather than a point.",
        "emc_constructs": r["emc_constructs_on_the_same_axis"],
        "firmly_measured_fractions": sorted(
            {a["fraction"] for a in anchors if a["fraction"] is not None}),
    }


# ── assembly ──────────────────────────────────────────────────────────────────────────────────
def derive():
    inputs, audit, designs, lit = load()
    return {
        "_title": "The donor-exon frame rule, the type-2 seam at nucleotide resolution, the "
                  "symmetric compositional sweep, and the counted EMC fusion-type series",
        "_status": "COMPUTED FROM COMMITTED INPUTS. No experiment, no reagent, no patient, no cell "
                   "and no animal. No potency, efficacy, safety, selectivity or clinical claim is "
                   "made or implied.",
        "_inputs": {
            "sequence_cache": "emc-construct-inputs.json",
            "sequence_cache_fetched_utc": inputs["_fetched_utc"],
            "sequence_source": inputs["_ensembl"],
            "frame_audit": "junction-mrna-frame-audit.json",
            "construct_designs": "emc-fet-construct-designs.json",
            "literature_retrieval_record": "research/manuscripts/aso/lit-targets-aso-verify.json",
        },
        "_cost": "$0 — CPU only, pure stdlib, no network call.",
        "frame_rule": frame_rule(inputs, audit),
        "type2_seam": type2_seam(inputs, designs),
        "composition": composition(inputs),
        "counted_fusion_type_frequencies": counted_frequencies(lit),
        "recruitment_axis_rows": axis_rows(designs),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="recompute and diff against the committed artifact")
    a = ap.parse_args(argv)

    got = derive()
    if a.check:
        if not os.path.exists(OUT):
            print("::error::no committed artifact at %s" % os.path.relpath(OUT, REPO))
            return 1
        with open(OUT, encoding="utf-8") as fh:
            have = json.load(fh)
        if json.dumps(have, sort_keys=True) != json.dumps(got, sort_keys=True):
            print("DRIFT — the committed artifact disagrees with a fresh derivation")
            return 1
        print("REPRODUCES")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(got, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    fr = got["frame_rule"]
    seam = got["type2_seam"]
    sw = got["composition"]["symmetric_prefix_sweep"]
    print(f"wrote {os.path.relpath(OUT, REPO)}")
    print(f"  frame rule holds for every EWSR1 donor: {fr['rule_holds_for_every_ewsr1_donor']}"
          f"  (phase-1 donors {fr['phase_1_donor_exons']})")
    print(f"  type-2 seam: {seam['_the_arithmetic']} -> {seam['extra_residues']} residues, "
          f"ORF {seam['chimeric_orf_length_aa']} aa")
    print(f"  symmetric sweep: lowest FET prefix {sw['lowest_fet_prefix_value']} "
          f"({sw['lowest_fet_prefix_protein']}) vs TCF12 best {sw['tcf12_best_prefix_value']}, "
          f"gap {sw['gap']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
