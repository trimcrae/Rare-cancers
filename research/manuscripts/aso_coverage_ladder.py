#!/usr/bin/env python3
"""What would it take to get junction-ASO coverage of EMC back above 95%, and is that reachable?

⛔ WHAT QUESTION THIS ANSWERS, AND WHY IT IS NOT THE ONE `aso_reagent_coverage.py` ANSWERS.
That module owns ONE fact: the coverage of the two reagents the manuscript names, 68.4%. This module
owns a different one: what each ADDITIONAL reagent would add, and where the ceiling is. It imports
the cohort counts from that module rather than retyping them, and its first rung reproduces 68.4%
exactly — which is the check that the two have not drifted.

★ RESULT 1 — BETTER DESIGN CANNOT RECOVER THE LOST COVERAGE, AND THIS IS COMPUTED RATHER THAN
ARGUED. Two breakpoints of the SAME partner share almost nothing at their donor 3' ends: *EWSR1*
exon 12 ends AATGGTTTGATG and exon 13 ends CACTCCGTGGAG, agreeing over a SINGLE terminal base (both
end in G, which is chance, not homology), and the best *EWSR1* pair anywhere in the panel shares
three. No register and no length lets one
junction-spanning oligonucleotide straddle two such seams. The nine multi-junction designs the
manuscript reports are all CROSS-partner at the same relative seam (*EWSR1* e12 / *TAF15* e11 /
*FUS* e10 share ten donor bases, TGGTTTGATG), and no patient is reported at those partner exons.
So coverage scales with PANEL SIZE and with nothing else. One breakpoint, one reagent.

★ RESULT 2 — THE PANEL HAS A STRUCTURAL BLIND SPOT, AND IT IS A DESIGN CHOICE RATHER THAN A
SEQUENCE FACT. All 38 junctions in the panel join a donor exon to *NR4A3* exon 3. The *EWSR1* type 2
transcript does not: it joins *EWSR1* exon 7 to *NR4A3* exon **2**, and it is recurrent — defined as
a type in a review, sequenced in a whole-transcriptome series, and sequenced again in an independent
case report (lit-targets-aso-breakpoint-census.json). The panel cannot express that junction because
the atlas grades every exon-2 acceptor NON_CODING_ACCEPTOR: *NR4A3* exon 2 lies upstream of the
start codon. ⛔ THAT IS A PROTEIN-LEVEL FILTER APPLIED TO AN RNA-LEVEL MODALITY. An RNase-H gapmer
cleaves a transcript; whether the chimera's reading frame survives is irrelevant to whether the
transcript exists and can be cut. The same reasoning excludes the *TAF15* exon 6 to *NR4A3* intron 2
variant — which is not a retained intron but a spliced 75-nt cryptic exon, and which the report
describing it calls one of "the two major TAF15-NR4A3 isoforms detected in human tumors". That
matters more than the *EWSR1* exon-2 case does for the headline, because the *TAF15* arm is priced
at 3/3: every *TAF15* patient is assumed to carry the exon-3 acceptor. It is an upper bound, and no
published series reports how far below it the truth sits.

★ RESULT 3 — 95% IS NOT REACHABLE FROM *EWSR1* AND *TAF15* ALONE. A panel covering EVERY *EWSR1*
and EVERY *TAF15* breakpoint reaches 94.8% — 55 of 58 cases — and stops. Crossing 95% REQUIRES the
*TCF12* arm.

⭐ RESULT 4, 2026-08-15 — THE *TCF12* BREAKPOINT IS NOW REPORTED AT NUCLEOTIDE RESOLUTION, AND THE
TOP ROW'S REASON FOR BEING A BOUND HAS CHANGED RATHER THAN GONE AWAY. This module used to say no
exon-resolved *TCF12::NR4A3* junction appears in 295 retrieved papers. That is still true OF THOSE
PAPERS and it was the wrong place to look: the junction was never published as an exon in prose, it
was DEPOSITED. GenBank AF289510.1 — 421 bp, submitted by the primary report's own authors, citing
PMID 11156374 — carries two chromosome-tagged `source` features that split the record at the
junction (1..263 chromosome 15, *TCF12*; 264..421 chromosome 9, *NR4A3*), and that seam is identical
base for base to the seam this panel already designed on. Derivation, and the five tests it passes:
`tcf12_breakpoint_assignment.py`.
⚠ THE ARM IS STILL PRICED AT ITS CEILING, FOR A DIFFERENT AND WEAKER REASON. Before: the exon was
an inference from a residue count. Now: the exon is confirmed from ONE sequenced tumour, and neither
breakpoint series behind this ladder contains a TCF12-rearranged tumour at all — so nothing measures
whether this junction recurs across the two TCF12 cases of the 58-case cohort. A confirmed junction
raises the floor under the DESIGN; it does not measure the ARM.

⛔ AND THE RECURRENCE QUESTION WAS THEN ASKED OF THE ARCHIVES, WHICH IS WHY THIS ROW STAYS A BOUND
RATHER THAN BECOMING A RUNG. A second deposited TCF12::NR4A3 junction matching exon 5 would make it
a rung. There is none: nuccore returns ONE record for (TCF12 OR HTF4) AND (chondrosarcoma OR myxoid)
and it is AF289510.1 itself, `"t(9;15)"` returns zero, SRA returns zero, and none of the three later
cohorts that COUNT a TCF12 tumour (PMID 12598313, 24746215, 36948401) deposited anything.
⭐ THE REASON IS STRUCTURAL AND IS THE HONEST SENTENCE FOR THE PAPER: TCF12-rearranged EMC has been
COUNTED at least four times in independent cohorts and SEQUENCED once, in 2000. The 26-case series
called its TCF12 tumour by FISH, which reports which genes are joined and never where. So recurrence
at this exon is UNTESTED — not refuted — and "untested" is what a bound is for.

WHAT THIS IS NOT.
  · Not a coverage measurement and not an efficacy claim. No sequence here has been synthesised or
    tested, and matching a junction is not activity against it.
  · Not a re-pricing of the manuscript's figure. The primary basis is the same single series the
    manuscript uses, so rung 0 is 68.4% and stays 68.4%. The pooled basis is reported beside it as a
    sensitivity and supersedes nothing.
  · Not a claim that the exon-2 junction is SCREENED. Five designs at that seam now exist
    (`research/modalities/aso_noncoding_acceptor_designs.py`, added the same day as this note) and
    all five clear a parent-exclusion test, but none has been through the five deep off-target
    screens the panel's other junctions went through. Designed is not screened, and the ladder
    renders the two states differently for that reason.
  · Not free of the assumption `aso_reagent_coverage.py` states about transporting a breakpoint
    distribution from an 18-case series to a 58-case one.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso", "fusion-junction-aso-coverage-ladder.json")
CENSUS = os.path.join(HERE, "aso", "lit-targets-aso-breakpoint-census.json")
ATLAS = os.path.join(HERE, os.pardir, "modalities", "nr4a3-fusion-junction-atlas.json")
PER_JUNCTION = os.path.join(HERE, os.pardir, "modalities", "aso-per-junction-table.json")
NONCODING = os.path.join(HERE, os.pardir, "modalities", "aso-noncoding-acceptor-designs.json")

import aso_reagent_coverage as RC  # noqa: E402  — the one home for the cohort counts

#: TWO BASES, AND THE DIFFERENCE BETWEEN THEM IS THE POINT. The manuscript's coverage rests on ONE
#: series (PMID 12378528), and this module's primary basis is the same one so that rung 0 reproduces
#: the published 68.4% exactly. The pooled basis adds the only other retrieved series that resolves
#: every case in a cohort to an exon pair by sequencing (PMID 29937513, n=5). Reported side by side;
#: the pooled figure supersedes nothing.
BASES = {
    "single_series": {
        "_what": "PMID 12378528 alone — the basis the manuscript's 68.4% is computed on.",
        "EWSR1": {"n": 15, "k": {"EWSR1_e12__NR4A3_e3": 10, "EWSR1_e13__NR4A3_e3": 2,
                                 "EWSR1_e7__NR4A3_e2": 0}},
        "TAF15": {"n": 3, "k": {"TAF15_e6__NR4A3_e3": 3}},
    },
    "pooled_two_series": {
        "_what": ("PMID 12378528 + PMID 29937513, pooled on exon pairs. Both report explicit "
                  "integer counts against the same outcome definition, which is what "
                  "POLICY-evidence.md §2.1 requires. Type NUMBERING is not pooled; only exon pairs."),
        "EWSR1": {"n": 20, "k": {"EWSR1_e12__NR4A3_e3": 13, "EWSR1_e13__NR4A3_e3": 3,
                                 "EWSR1_e7__NR4A3_e2": 1}},
        "TAF15": {"n": 3, "k": {"TAF15_e6__NR4A3_e3": 3}},
    },
}

#: ⚠ TCF12 HAS NO WITHIN-PARTNER MEASUREMENT, AND THAT IS NOW A NARROWER STATEMENT THAN IT WAS.
#: No TCF12-rearranged tumour appears in either breakpoint series, so there is no fraction to
#: discount its arm by and it is priced at its CEILING — flagged on the arm rather than smuggled
#: into the total.
#: ⛔ THIS IS NO LONGER "WE DO NOT KNOW THE EXON". Since 2026-08-15 the junction is reported at
#: nucleotide resolution (GenBank AF289510.1; `tcf12_breakpoint_assignment.py`). What is unmeasured
#: is the DISTRIBUTION: one tumour has been sequenced at this partner, ever, and a k of 1 over an n
#: of 1 is not a within-partner fraction — it is the same tumour the junction was defined by. Adding
#: it to `BASES` would manufacture a measurement out of the observation that produced the category.
PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT = {"TCF12"}

#: The junctions no design in the panel can express, with the reason. Both are acceptor-side.
UNDESIGNABLE_IN_THE_CURRENT_PANEL = {
    "EWSR1_e7__NR4A3_e2": {
        "why": ("the atlas grades every NR4A3 exon-2 acceptor NON_CODING_ACCEPTOR, because NR4A3 "
                "exon 2 carries no CDS — it is upstream of the start codon. A protein-level "
                "exclusion, correct for a degrader or a neoantigen and wrong for a gapmer."),
        "evidence": ["PMID 22567356 defines it as the type 2 transcript",
                     "PMID 29937513 sequenced it as sample #1 of five",
                     "PMID 35488288 sequenced it in an independent patient"],
        "what_it_would_take": ("emit exon-2 acceptors for the ASO lane specifically, then run the "
                               "same five screens the other 38 junctions went through. No new "
                               "method, no GPU, no rental."),
        "⭐_status_2026_08_15": (
            "DESIGNS NOW EXIST, AND ARE NOT YET SCREENED. "
            "research/modalities/aso_noncoding_acceptor_designs.py emits five 16-mers spanning "
            "this seam at the manuscript geometry; all five clear the parent-exclusion test "
            "against six partner transcripts, and the best holds a gap-level margin of 3 — the "
            "same top margin as both named reagents. ⛔ NONE has been through the five deep "
            "off-target screens, which need BLAST and network, so their load is UNKNOWN and their "
            "counts are not comparable with the panel's. A margin is not a clean screen."),
    },
    "TAF15_e6__NR4A3_intron2": {
        "why": "same filter — an intronic acceptor carries no CDS either.",
        "evidence": [
            "PMID 31020999 calls T-N and T-N* 'the two major TAF15-NR4A3 isoforms detected in "
            "human tumors', and describes T-N as 'TAF15 (exons 1-6)-NR4A3 (intron 2-exon 8)'",
            "PMID 31020999 engineered both isoforms into cells and found them 'essentially "
            "indistinguishable' in colony formation",
        ],
        "what_it_would_take": ("emit the cryptic-exon acceptor for the ASO lane, then run the same "
                               "five screens the other 38 junctions went through. No new method, "
                               "no GPU, no rental — the same shape as the exon-2 case."),
        "⭐_corrected_2026_08_15": (
            "THE ACCEPTOR IS NOT A RETAINED INTRON, AND THAT CHANGES WHAT THIS ROW COSTS. This "
            "entry previously called for 'a retained-intron acceptor model, which the atlas does "
            "not currently build', and priced the row as more work than the exon-2 case. PMID "
            "31020999 says otherwise in its own words: 'T-N retains a short cryptic exon located "
            "in NR4A3 intron 2 (ENST00000395097.6 isoform), thus encoding 25 additional amino "
            "acids prior to the NR4A3 ATG.' A SPLICED cryptic exon has a definite length and "
            "definite boundaries, and junction_aso.mrna_junction_generic builds it unchanged — no "
            "retained-intron model is needed. The length is not a free parameter either: TAF15 "
            "contributes 484 coding nt through exon 6 and NR4A3 exon 3 retains 2 nt of 5'UTR, so "
            "the paper's '25 additional amino acids' is reproduced at exactly one exon length, 75 "
            "nt, and at no other (74 and 76 both destroy the NR4A3 reading frame the same sentence "
            "asserts). One home for the derivation and the measured sequence: "
            "research/modalities/nr4a3-intron2-cryptic-exon.json."),
        "⛔_prevalence_is_still_unmeasured": (
            "The paper orders the two isoforms — 'the commonest' T-N* against 'the less common' "
            "T-N — and reports NO count of either among its five TAF15-NR4A3 tumours. A search of "
            "782 unique full texts across the three retrieved corpora finds the intron-2 form "
            "mentioned in that one paper alone, never with a count. ⚠ AND THE ABSENCE IS PARTLY "
            "STRUCTURAL: PMID 32612944's 59-patient series states its 'Primers and probes used in "
            "this assay are specific for the detection of the following fusion: ... "
            "TAF15(ex6)/NR4A3(ex3)', so a junction-specific assay of that design cannot report an "
            "intron-2 acceptor as such — the same junction-spanning specificity that makes a T-N* "
            "gapmer miss T-N makes that assay miss it too. So the TAF15 arm's 3/3 is an UPPER "
            "BOUND carrying a named, unquantified risk, and no number here moves: converting 'less "
            "common' into a fraction would fabricate the one quantity the literature declines to "
            "give."),
    },
}


def _atlas_donor_ends():
    """3'-terminal donor context of every NR4A3-exon-3 junction, from the committed atlas."""
    atlas = json.load(open(ATLAS, encoding="utf-8"))
    return {g["junction_label"]: {"donor_3prime_context": g["junction_context_mRNA"].split("|")[0],
                                  "grade": g["grade"], "partner": g["donor_symbol"],
                                  "donor_exon": g["donor_exon_end"]}
            for g in atlas["graded_pairs"] if g["acceptor_exon_start"] == 3}


def _shared_suffix(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def multiplexing_check(ends):
    """Can ONE oligonucleotide ever serve two breakpoints of the SAME partner? Computed, not argued.

    A junction-spanning oligonucleotide draws bases from both sides of the seam. Two junctions
    sharing an acceptor exon agree trivially on the acceptor side — the atlas says so in terms — so
    the load-bearing quantity is how many bases the two DONOR exons share at their 3' ends. Zero
    shared bases means no register and no length can straddle both.
    """
    by_partner = {}
    for lab, e in ends.items():
        by_partner.setdefault(e["partner"], []).append((lab, e))
    within = []
    for partner, rows in sorted(by_partner.items()):
        rows = [r for r in rows if r[1]["grade"] == "EMITTABLE"]
        best = None
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                s = _shared_suffix(rows[i][1]["donor_3prime_context"],
                                   rows[j][1]["donor_3prime_context"])
                if best is None or s > best["shared_3prime_donor_nt"]:
                    best = {"partner": partner, "junction_a": rows[i][0], "junction_b": rows[j][0],
                            "shared_3prime_donor_nt": s}
        if best:
            within.append(best)
    labs = sorted(k for k, v in ends.items() if v["grade"] == "EMITTABLE")
    cross = []
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            a, b = ends[labs[i]], ends[labs[j]]
            if a["partner"] == b["partner"]:
                continue
            s = _shared_suffix(a["donor_3prime_context"], b["donor_3prime_context"])
            if s >= 8:
                cross.append({"junction_a": labs[i], "junction_b": labs[j],
                              "shared_3prime_donor_nt": s,
                              "shared_run": a["donor_3prime_context"][-s:]})
    e12 = ends["EWSR1_e12__NR4A3_e3"]["donor_3prime_context"]
    e13 = ends["EWSR1_e13__NR4A3_e3"]["donor_3prime_context"]
    return {
        "_question": ("Can one oligonucleotide cover two breakpoints, so that coverage rises "
                      "without the panel growing? This is the ONLY way better design could raise "
                      "coverage, and it is decided by sequence rather than by skill."),
        "_method": ("Shared 3'-terminal bases between the donor exons of two junctions, over the "
                    "12-nt donor context the atlas emits per seam. The acceptor side is excluded "
                    "because these junctions share their acceptor exon and would agree trivially."),
        "the_two_junctions_that_matter_most": {
            "EWSR1_e12__NR4A3_e3_donor_3prime": e12,
            "EWSR1_e13__NR4A3_e3_donor_3prime": e13,
            "shared_3prime_donor_nt": _shared_suffix(e12, e13),
        },
        "within_partner_best_pair_per_partner": within,
        "max_within_partner_shared_donor_nt": max(w["shared_3prime_donor_nt"] for w in within),
        "cross_partner_pairs_sharing_8_or_more": cross,
        "_answer": ("NO. Within a partner the best pair shares far too few 3' donor bases for one "
                    "oligonucleotide to straddle both seams, so every additional breakpoint costs "
                    "an additional reagent. The long shared runs are all CROSS-partner, at the FET "
                    "donors' paralogous exons — §3.2's result — and no patient is reported at "
                    "those partner exons."),
    }


def _panel_coverage(junctions, basis, complete_partners=()):
    """Coverage of a panel on one basis: partner share times the breakpoint fraction it covers."""
    n_cohort = RC.PARTNER_COHORT["n"]
    arms, point, lo, hi = [], 0.0, 0.0, 0.0
    for partner, counts in RC.PARTNER_COHORT["counts"].items():
        if partner == "no_identified_partner":
            continue
        covered = [j for j in junctions if j.startswith(partner + "_")]
        if not covered:
            continue
        share = counts / n_cohort
        spec = basis.get(partner)
        if partner in complete_partners:
            frac = f_lo = f_hi = 1.0
            basis_note = "every breakpoint of this partner, by construction"
        elif spec is None or partner in PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT:
            frac = f_lo = f_hi = 1.0
            basis_note = ("⚠ NO measured within-partner fraction exists for this partner — the arm "
                          "is priced at its CEILING, which makes the total an upper bound rather "
                          "than an estimate")
        else:
            k = sum(spec["k"].get(j, 0) for j in covered)
            frac = k / spec["n"]
            f_lo, f_hi = RC.wilson(k, spec["n"])
            basis_note = f"{k}/{spec['n']} of this partner's rearranged tumours"
        arms.append({"partner": partner, "junctions_in_panel": sorted(covered),
                     "partner_share_of_cohort": round(share, 4),
                     "breakpoint_fraction_covered": round(frac, 4), "basis": basis_note,
                     "contribution": round(share * frac, 4)})
        point += share * frac
        lo += share * f_lo
        hi += share * f_hi
    return arms, point, lo, hi


E12 = "EWSR1_e12__NR4A3_e3"
E13 = "EWSR1_e13__NR4A3_e3"
E7X2 = "EWSR1_e7__NR4A3_e2"
T6 = "TAF15_e6__NR4A3_e3"
TCF5 = "TCF12_e5__NR4A3_e3"

#: The ladder. Each rung is a panel; each rung's delta is what one more reagent buys.
PANELS = [
    {"name": "as published — the two named reagents",
     "junctions": [E12, T6], "complete_partners": [],
     "status": "both named in §5.1, both screened, both designable today",
     "cost": "nothing new — this is the manuscript's panel"},
    {"name": "+ EWSR1 exon 13 → NR4A3 exon 3",
     "junctions": [E12, E13, T6], "complete_partners": [],
     "status": ("AVAILABLE NOW, AND IT WAS A CURATION MISS. The second-most-common EWS/CHN "
                "transcript, named in the same abstract that establishes exon 12 and confirmed "
                "independently by a whole-transcriptome series. Already screened; its best design "
                "holds the same top gap-level margin of 3 and carries a LIGHTER disclosed "
                "transcriptome load than the exon-12 reagent."),
     "cost": "one oligonucleotide; no new screen, no new retrieval"},
    {"name": "+ EWSR1 exon 7 → NR4A3 exon 2 (the type 2 transcript)",
     "junctions": [E12, E13, E7X2, T6], "complete_partners": [],
     "status": ("⛔ NOT DESIGNABLE IN THE CURRENT PANEL, and the obstacle is a filter rather than "
                "the sequence. Every panel junction uses NR4A3 exon 3; this one uses exon 2, which "
                "the atlas drops as a non-coding acceptor. Lifting that filter for the ASO lane is "
                "the single largest piece of designable-but-undesigned coverage."),
     "cost": ("emit exon-2 acceptors, then the same five screens the other junctions ran. CPU and "
              "CI only — no GPU, no rental"),
     "_why_the_single_series_delta_is_zero": (
         "⚠ READ THE TWO COLUMNS TOGETHER ON THIS RUNG. The single-series basis prices this "
         "junction at ZERO because that series never named the type 2 transcript — an UNNAMED "
         "count, not a measured absence, and the same series maps one genomic break to EWSR1 "
         "intron 7, which is where a type 2 fusion would come from. The pooled basis, which "
         "includes the only cohort that resolved every case by sequencing, prices it at 1 in 20. "
         "A rung whose value is invisible on the manuscript's own basis is exactly the rung a "
         "single-cohort estimate is worst at seeing.")},
    {"name": "BOUND — every remaining EWSR1 breakpoint covered", "kind": "bound",
     "_why_a_bound_and_not_a_rung": (
         "⛔ THIS IS NOT A PANEL ANYONE CAN BUILD, AND RENDERING IT AS A RUNG OVERSTATED IT. "
         "Three of the 15 EWSR1-rearranged tumours carry transcript types the retrieved record "
         "does not name, so the number of reagents needed is unknown — and if those breakpoints "
         "are PRIVATE rather than recurrent, no stocked panel reaches them at any size. A "
         "per-patient design-and-manufacture route is a different clinical object, not a bigger "
         "panel. What makes this a bound rather than a guess is that the primary series DID "
         "sequence them: its genomic mapping reports EWSR1 breaks in introns 7, 12 and 13, so the "
         "junctions exist and are documented — in a paper that is not open access."),
     "junctions": [E12, E13, E7X2, T6], "complete_partners": ["EWSR1", "TAF15"],
     "status": ("BLOCKED ON RETRIEVAL, NOT ON DESIGN. Three of the 15 EWSR1-rearranged tumours of "
                "the primary series carry transcript types that record does not name. Naming them "
                "names the junctions."),
     "cost": "one retrieval, then roughly one to three additional oligonucleotides"},
    {"name": "BOUND — the above plus TCF12", "kind": "bound",
     "_why_a_bound_and_not_a_rung": (
         "⛔ THE TCF12 ARM IS PRICED AT ITS CEILING BECAUSE THERE IS NOTHING TO DISCOUNT IT BY, "
         "and the total silently inherits that. Neither breakpoint series behind this ladder "
         "contains a TCF12-rearranged tumour, so no within-partner fraction exists to apply. "
         "⭐ WHAT IS NO LONGER TRUE, AS OF 2026-08-15: that the exon itself is unverified. The "
         "junction is reported at nucleotide resolution in GenBank AF289510.1, the chimeric cDNA "
         "the primary report's own authors deposited, and it lands on TCF12 exon 5 joined to NR4A3 "
         "exon 3 and on no other exon pair. So this figure is an upper bound resting on an "
         "unmeasured within-partner DISTRIBUTION — one sequenced tumour against the cohort's two — "
         "rather than on an unverified exon, and it must still never be quoted as a reachable "
         "coverage target."),
     "junctions": [E12, E13, E7X2, T6, TCF5], "complete_partners": ["EWSR1", "TAF15"],
     "status": ("REQUIRED TO CROSS 95%. The junction is now published at nucleotide resolution "
                "(GenBank AF289510.1, deposited with PMID 11156374), and the exon-5 design was "
                "already screened through all five screens and holds a gap-level margin of 3 — so "
                "the reagent is available today. What is missing is the distribution: one TCF12 "
                "tumour has ever been sequenced at this junction."),
     "cost": "one oligonucleotide — designed and screened already; nothing further to retrieve"},
]


def build():
    ends = _atlas_donor_ends()
    designs = {j["junction_label"]: j
               for j in json.load(open(PER_JUNCTION, encoding="utf-8"))["junctions"]}
    census = json.load(open(CENSUS, encoding="utf-8"))
    # Junctions the non-coding-acceptor lane has emitted designs for. Read from the artifact rather
    # than listed here, so this cannot claim a design that lane never produced.
    noncoding_designed = {}
    if os.path.exists(NONCODING):
        for j in json.load(open(NONCODING, encoding="utf-8"))["junctions"]:
            if j["n_clearing_the_parent_exclusion"]:
                noncoding_designed[j["junction_label"]] = {
                    "antisense_5to3": j["best_by_gap_specificity_margin"],
                    "n_clearing_the_parent_exclusion": j["n_clearing_the_parent_exclusion"],
                    "n_designs_spanning_the_seam": j["n_designs_spanning_the_seam"],
                    "offtarget_screens_run": "NONE — load unknown, not comparable with the panel",
                    "one_home": "research/modalities/aso-noncoding-acceptor-designs.json"}
    n_cohort = RC.PARTNER_COHORT["n"]
    counts = RC.PARTNER_COHORT["counts"]

    ladder, prev = [], None
    for panel in PANELS:
        arms, point, lo, hi = _panel_coverage(panel["junctions"], BASES["single_series"],
                                              panel["complete_partners"])
        _, p_pool, _, _ = _panel_coverage(panel["junctions"], BASES["pooled_two_series"],
                                          panel["complete_partners"])
        unnamed = 3 if panel["complete_partners"] else 0
        # ⚠ THREE STATES, NOT TWO, AND COLLAPSING THEM WOULD OVERSTATE THE PANEL. A junction is
        # either screened (in the panel's per-junction table), DESIGNED BUT UNSCREENED (emitted by
        # the non-coding-acceptor lane, off-target load unknown), or has nothing at all. Rendering
        # the middle state as "designed" would let an unscreened sequence read like a panel member.
        missing = [j for j in panel["junctions"]
                   if j in UNDESIGNABLE_IN_THE_CURRENT_PANEL and j not in noncoding_designed]
        designed_unscreened = [j for j in panel["junctions"] if j in noncoding_designed]
        ladder.append({
            "panel": panel["name"],
            "kind": panel.get("kind", "rung"),
            "_why_a_bound_and_not_a_rung": panel.get("_why_a_bound_and_not_a_rung"),
            "n_reagents_named": len(panel["junctions"]),
            "n_reagents_additional_unnamed": unnamed,
            "coverage_percent": round(100 * point, 1),
            "coverage_percent_range": [round(100 * lo, 1), round(100 * hi, 1)],
            "coverage_percent_pooled_basis": round(100 * p_pool, 1),
            "delta_percent_vs_previous": None if prev is None else round(100 * (point - prev), 1),
            "junctions": panel["junctions"],
            "junctions_with_no_design_at_all": missing,
            "junctions_designed_but_not_yet_screened": {
                j: noncoding_designed[j] for j in designed_unscreened},
            "status": panel["status"],
            "_note": panel.get("_why_the_single_series_delta_is_zero"),
            "what_it_costs": panel["cost"],
            "arms": arms,
            "designs_available_today": {
                j: (None if not designs.get(j, {}).get("best_available") else {
                    "antisense_5to3": designs[j]["best_available"]["antisense_5to3"],
                    "gap_specificity_margin": designs[j]["best_available"]["gap_specificity_margin"],
                    "n_gap_paired_at_deep_ceiling": designs[j]["best_available"]["n_gap_paired"],
                    "n_gap_paired_loci": designs[j]["best_available"]["n_gap_paired_loci"],
                    "clinical_tier": designs[j]["clinical_tier"]})
                for j in panel["junctions"]},
        })
        prev = point

    ceiling_named = sum(counts[p] for p in ("EWSR1", "TAF15", "TCF12")) / n_cohort
    ewsr1_taf15 = (counts["EWSR1"] + counts["TAF15"]) / n_cohort

    return {
        "_what": ("What each additional junction reagent would add to EMC coverage, where the "
                  "ceiling is, and whether 95% is reachable at all."),
        "_why": ("The manuscript's coverage was corrected from 95% to 68.4% on 2026-08-15. The "
                 "question that follows is whether better design can recover it. It cannot; a "
                 "bigger panel can, up to a ceiling computed here."),
        "_what_this_is_not": [
            "Not a coverage measurement and not an efficacy claim. Nothing here has been "
            "synthesised or tested, and matching a junction is not activity against it.",
            "Not a re-pricing of the manuscript's figure. Rung 0 is computed on the same single "
            "series and reproduces 68.4%; the pooled column supersedes nothing.",
            "Not a claim that the NR4A3 exon-2 junction is designable — nothing has been designed "
            "or screened there. That is the work this file argues for, not work it reports.",
            "Not a guess at the unresolved EWSR1 transcript types; they are priced, not named.",
            "Not free of the assumption aso_reagent_coverage.py states about transporting a "
            "breakpoint distribution from an 18-case series to a 58-case one.",
        ],
        "_cost": "$0 — arithmetic over committed artifacts plus one free-runner literature fetch.",
        "inputs": {
            "partner_prevalence": {"pmid": RC.PARTNER_COHORT["pmid"], "n": n_cohort,
                                   "counts": counts,
                                   "_one_home": "research/manuscripts/aso_reagent_coverage.py"},
            "breakpoint_bases": BASES,
            "breakpoint_census": {"_one_home": "aso/lit-targets-aso-breakpoint-census.json",
                                  "n_papers_retrieved": census["source"]["n_papers_retrieved"],
                                  "n_reporting_an_exon_resolved_junction":
                                      census["source"]["n_reporting_an_exon_resolved_junction"]},
            "undesignable_in_the_current_panel": UNDESIGNABLE_IN_THE_CURRENT_PANEL,
        },
        "can_better_design_raise_coverage": multiplexing_check(ends),
        "ladder": ladder,
        "ceiling": {
            "all_named_partners_at_every_breakpoint_percent": round(100 * ceiling_named, 1),
            "_what_is_left_over": (f"{counts['no_identified_partner']} of {n_cohort} cases are "
                                   "NR4A3-rearranged with no identified partner. No junction "
                                   "reagent can be built for a junction nobody has sequenced, so "
                                   "this is a hard ceiling for the modality as specified."),
            "EWSR1_and_TAF15_complete_percent": round(100 * ewsr1_taf15, 1),
            "⛔_the_result_that_decides_the_panel": (
                f"A panel covering every EWSR1 and every TAF15 breakpoint reaches "
                f"{round(100 * ewsr1_taf15, 1)}% and stops. It cannot reach 95%. Crossing 95% "
                "REQUIRES the TCF12 arm. ⭐ That arm's junction is reported at nucleotide "
                "resolution as of 2026-08-15 (GenBank AF289510.1) and its reagent is designed and "
                "screened, so the 95% target is no longer a retrieval problem at TCF12. It is now "
                "a DISTRIBUTION problem: one TCF12 tumour has ever been sequenced, so the arm is "
                "priced at its ceiling and the total above it is an upper bound."),
        },
        "what_would_actually_move_this": [
            {"step": "Add the EWSR1 exon-13 reagent",
             "buys_percent_points": round(100 * (counts["EWSR1"] / n_cohort) * (2 / 15), 1),
             "cost": "one oligonucleotide; the design and its screen already exist",
             "blocked_on": None},
            {"step": "Emit and screen NR4A3 exon-2 acceptor junctions for the ASO lane",
             "buys_percent_points": round(100 * (counts["EWSR1"] / n_cohort) * (1 / 20), 1),
             "cost": "CPU and CI only — no GPU, no rental",
             "blocked_on": ("nothing. The filter that excludes them is a protein-coding grade the "
                            "ASO lane does not need, and the junction has three independent "
                            "sources behind it.")},
            {"step": "Name the remaining unresolved EWSR1 transcript types",
             "buys_percent_points": round(100 * (counts["EWSR1"] / n_cohort) * (3 / 15), 1),
             "cost": "$0 — one more literature retrieval on a free runner",
             "blocked_on": "the full text of the primary series, which is not open access"},
            {"step": "Establish the TCF12 breakpoint as an exon",
             "buys_percent_points": round(100 * counts["TCF12"] / n_cohort, 1),
             "cost": "$0 retrieval, then one oligonucleotide",
             "blocked_on": None,
             "⭐_done_2026_08_15": (
                 "GenBank AF289510.1, the chimeric cDNA deposited with PMID 11156374, resolves the "
                 "junction to the nucleotide: TCF12 exon 5 to NR4A3 exon 3, one exon boundary on "
                 "each side and no other, with a seam identical to the one the panel designed on. "
                 "The reagent already exists and is already through all five screens. "
                 "⚠ WHAT REMAINS is not retrieval but sampling: one TCF12 tumour has ever been "
                 "sequenced at this junction, so the arm stays priced at its ceiling. See "
                 "research/manuscripts/tcf12_breakpoint_assignment.py."),
             "⚠_why_295_papers_missed_it": (
                 "The breakpoint was never published as an exon in prose. A literature sweep of any "
                 "width therefore could not find it, and a second sweep of 104 more papers did not "
                 "either. NCBI elink from the report's PubMed record to the nucleotide database "
                 "returns it in one call, and a nuccore term search returns the same single record. "
                 "⛔ AN EMPTY CORPUS SWEEP IS EVIDENCE ABOUT THE CORPUS, NOT ABOUT THE WORLD.")},
            {"step": "Sequence the junction in a SECOND TCF12-rearranged EMC",
             "buys_percent_points": round(100 * counts["TCF12"] / n_cohort, 1),
             "cost": "wet lab — outside this programme's operating regime",
             "blocked_on": ("material. ⛔ THE ARCHIVES HAVE BEEN SEARCHED AND HOLD NOTHING: nuccore "
                            "returns one record for (TCF12 OR HTF4) AND (chondrosarcoma OR myxoid) "
                            "and it is AF289510.1 itself, `t(9;15)` returns zero, SRA returns zero, "
                            "and none of the three later cohorts that COUNT a TCF12 tumour "
                            "(PMID 12598313, 24746215, 36948401) deposited a sequence."),
             "⭐_why_this_is_the_step_that_decides_the_95_percent_question": (
                 "It is the ONLY step that turns this row from a BOUND into a RUNG. Everything else "
                 "at TCF12 is done: the junction is resolved, the reagent is designed and screened. "
                 "What is missing is a second observation — whether the two TCF12 tumours of the "
                 "58-case cohort share this exon. ⚠ AND IT CANNOT BE BOUGHT WITH COMPUTE: the "
                 "material exists (the 26-case series and the 58-case cohort each hold at least one "
                 "FISH-confirmed TCF12 tumour) and the assay is RNA sequencing of archival tissue."),
             "⛔_why_the_absence_is_structural_rather_than_a_gap_in_retrieval": (
                 "TCF12-rearranged EMC has been COUNTED at least four times in independent cohorts "
                 "and SEQUENCED once, in 2000. Every later count used a partner-level assay — the "
                 "26-case series called its TCF12 tumour by fluorescence in situ hybridization, "
                 "which reports which genes are joined and never where. So recurrence at this exon "
                 "is UNTESTED rather than refuted, and nothing in the record licenses calling this "
                 "junction private, rare or non-recurrent."),
             "one_home": "research/literature/tcf12-nr4a3-breakpoint-primary-sources.json"},
        ],
    }


def main(argv=None):
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("fusion-junction-aso-coverage-ladder.json is stale; re-run without --check",
                  file=sys.stderr)
            return 1
        print("coverage-ladder artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    for r in art["ladder"]:
        n = str(r["n_reagents_named"]) + (f"+1–{r['n_reagents_additional_unnamed']}"
                                          if r["n_reagents_additional_unnamed"] else "")
        d = "" if r["delta_percent_vs_previous"] is None else f"(+{r['delta_percent_vs_previous']})"
        flag = ("  ⛔ BOUND, not a buildable panel" if r["kind"] == "bound"
                else "  ⛔ no design exists" if r["junctions_with_no_design_at_all"]
                else "  ⚠ designed, NOT screened" if r["junctions_designed_but_not_yet_screened"]
                else "")
        print(f"  {n:>6} reagents  {r['coverage_percent']:>5}%  {d:<8} "
              f"pooled {r['coverage_percent_pooled_basis']:>5}%  {r['panel']}{flag}",
              file=sys.stderr)
    m = art["can_better_design_raise_coverage"]
    print(f"  EWSR1 e12 vs e13 donor 3' agreement: "
          f"{m['the_two_junctions_that_matter_most']['shared_3prime_donor_nt']} nt — "
          "one oligo cannot serve two breakpoints", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
