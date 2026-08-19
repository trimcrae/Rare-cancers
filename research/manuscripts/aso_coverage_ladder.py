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
COUNTED in independent cohorts and SEQUENCED once, in 2000. The 26-case series called its TCF12
tumour by FISH, which reports which genes are joined and never where. So recurrence at this exon is
UNTESTED — not refuted — and "untested" is what a bound is for.
⚠ CORRECTED 2026-08-15, IN THE DIRECTION THAT MAKES THE EVIDENCE THINNER. This read "COUNTED at
least four times in INDEPENDENT cohorts". One of those four is not independent: PMID 12598313's
TCF12 case is the 2000 tumour re-reported, which its own Discussion says by citing the 2000 paper
for that count and its own Table 1 confirms by carrying that tumour's t(9;15)(q22;q21) karyotype.
The open question was recorded in `tcf12-nr4a3-breakpoint-primary-sources.json` as needing "a
publisher fetch or an interlibrary request — not a $0 route"; PMC serves the full text as HTML at
HTTP 200 and it took one GET. Nothing above moves — the arm was already a bound and this only
removes a count that was never sequenced — but "independent" was doing work it had not earned.

⭐ RESULT 5, 2026-08-15 — THE LADDER'S RUNGS ARE NOT THE BEST-SUPPORTED PANEL, AND THE GAP IS 3.9
POINTS OF ARITHMETIC PLUS ONE STALE FACT. The rungs are an INCREMENTAL series — each adds one
reagent to the one before — and the figure quoted from them (79.0%) is rung 1 on the single-series
basis. That is not the same question as *what does the evidence in hand support today*, because two
things moved after the rungs were laid out: the *EWSR1* exon 7 :: *NR4A3* exon 2 reagent went
through all five deep screens (`research/modalities/noncoding-acceptor/`), and the *TCF12* exon 5
junction was resolved to the nucleotide. So a different row is now computable, and it is not a
bigger panel — it is the SAME panel priced on the whole retrieved record instead of one series of
it: `best_supported_buildable_panel` below. **It is an ADDITIONAL row. Every rung and bound above
it is unchanged, and rung 0 still reproduces 68.4% exactly.**

⭐ RESULT 6, 2026-08-15 — THE TWO REMAINING LEVERS ON THE BUILDABLE FIGURE WERE TESTED. ONE IS
BARRED, THE OTHER IS PERMITTED AND LOWERS IT. The buildable row had been read as 82.9% against a
98.3% ceiling with the gap left as a to-do list, and neither of the two things that could have
closed it had been checked against the evidence contract rather than against memory.
  · **LEVER 1 — the third breakpoint series (PMID 11679947), worth +4.5 points. STILL REFUSED, ON
    ONE GROUND INSTEAD OF TWO.** Its type-nomenclature ground was withdrawn: three primary sources
    spanning 1997–2011 (PMID 9060841, 12598313, 22567356) agree on types 1 and 2, the only types
    this series reports, and the nomenclature conflict is at type 5 alone. Its POLICY-evidence.md
    §2.1(3) ground survives and is sufficient by itself, decided by arithmetic rather than by
    reading: the series' EWSR1 arm is 12/12 for the covered junctions BY CONSTRUCTION, because a
    tumour with any other junction could not have entered a denominator defined by that assay's
    own positivity. `third_series_deliberately_not_pooled`.
  · **LEVER 2 — the partner denominator, which every rung prices against one 58-case series.** It
    can be widened, and it did not need new evidence: a four-series pooled EMC partner prevalence
    already exists in this repository, built for another paper against the same policy, and is now
    READ rather than re-derived. ⛔ IT LOWERS THE FIGURE. The TAF15 share rises, which helps, and
    is outweighed by the partner-unassigned residue, which rises much further — one case in 58
    against nine in 163. ⭐ AND IT MOVES THE 95% QUESTION: on the wider basis the arithmetic
    ceiling falls BELOW 95%, so no panel of any size reaches 95% of molecularly confirmed EMC.
    `best_supported_buildable_panel.sensitivity_if_the_partner_denominator_is_pooled`.
  ⚠ Neither result changes a published figure. The manuscript's basis is unchanged, rung 0 still
  reproduces 68.4%, and the buildable row is still 82.9% on that basis.

⭐ RESULT 7, 2026-08-15 — THE LAST UNTESTED LEVER ON THE CEILING WAS PULLED, AND THE CEILING SURVIVES
IT. Result 6 left the arithmetic ceiling below 95% on the pooled basis and named a FIFTH candidate
partner cohort — PMID 12598313, Sjögren 2003, Göteborg — without acting on it, because two
POLICY-evidence.md §2.3 double-counting questions had to be settled first. Both are now settled
against the paper's full text (PMC1868116, HTTP 200), and the cohort is then checked row by row
against §2.1.
  · **THE TWO §2.3 QUESTIONS ARE ANSWERED.** (1) Its TCF12 case IS the 2000 index tumour — and the
    duplication is BROADER than that one case: its Materials and Methods puts FOUR of its nine
    patients in that position, "previously reported regarding the expression of EMC-specific fusion
    transcripts". (2) Its partner counts are TUMOUR-level in the abstract and PATIENT-level in the
    Discussion; Table 3's title ("10 EMCs from Nine Patients") and its two footnotes reconcile them,
    and only the patient-level integers may be pooled.
  · **IT IS REFUSED, ON §2.1(3) ALONE.** §2.1(1), §2.1(2) at patient level and §2.1(4) all pass —
    this is a peer-reviewed, fully-accounted, karyotyped series, not an abstract and not an overlap
    case. Four of its nine patients are in it BECAUSE their fusion transcript had already been
    published, so their partner assignment is the entry ticket and this cohort's headline property —
    a partner-unassigned residue of ZERO — is structural on that half rather than measured. Decided
    by arithmetic: the structurally-admitted half is 3/4 variant-partner, the freely-admitted half
    1/5.
  · **⛔ AND THE REFUSAL COSTS THE HIGHER NUMBER, WHICH IS WHY IT IS PRICED RATHER THAN ASSERTED.** A
    zero-residue cohort RAISES the ceiling. Admitting it would move the ceiling UP by a fraction of
    a point, leave the buildable figure unchanged at one decimal place, and lift the bound slightly
    — and the ceiling would STILL sit below 95%. So the load-bearing conclusion of Result 6 holds on
    both sides of the decision. `fifth_partner_cohort_deliberately_not_pooled` owns every number.
  · ⚠ **IT ALSO REACHES THE TAF15 PROGNOSTIC SYNTHESIS AND IS NOT APPLIED THERE.** Its Table 1
    per-patient follow-up joins to Table 3's partner column, and its three TAF15 patients record no
    tumour-related death — which would pull the pooled TAF15 disease-specific-death arm DOWN. Barred
    by the same §2.1(3), and independently by §2.1(2): the paper publishes no per-partner outcome
    event counts. No prognostic figure moves; the direction is named so that not moving it is
    visible.
  ⚠ Nothing above changes a published figure either. Rung 0 still reproduces 68.4%, the buildable
  row is still 82.9% on the manuscript's basis, and the pooled row's ceiling is unchanged.

WHAT THIS IS NOT.
  · Not a coverage measurement and not an efficacy claim. No sequence here has been synthesised or
    tested, and matching a junction is not activity against it.
  · Not a re-pricing of the manuscript's figure. The primary basis is the same single series the
    manuscript uses, so rung 0 is 68.4% and stays 68.4%. The pooled basis is reported beside it as a
    sensitivity and supersedes nothing.
  · ⚠ SUPERSEDED, RETAINED: "Not a claim that the exon-2 junction is SCREENED … none has been
    through the five deep off-target screens the panel's other junctions went through." That was
    true when written and is false now. All five screens ran at the manuscript geometry and the
    state is read per junction from
    `research/modalities/noncoding-acceptor/aso-noncoding-acceptor-screened-table.json`
    (`screens_complete`), never asserted here. What is still true is the distinction the sentence
    existed to protect: DESIGNED, SCREENED and NOTHING-AT-ALL are three states, and this module
    still renders them three ways — it now reads all three from artifacts rather than two.
  · Not a claim that the best-supported row is a ceiling. It is a point estimate with an unmeasured
    arm reported beside it as a bound, and its distance to the arithmetic ceiling is decomposed
    below rather than left as a remainder.
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
NONCODING_SCREENED = os.path.join(HERE, os.pardir, "modalities", "noncoding-acceptor",
                                  "aso-noncoding-acceptor-screened-table.json")
#: ⭐ THE ONE HOME OF THE POOLED PARTNER PREVALENCE, AND IT IS NOT THIS FILE. Every rung above
#: prices partner share against the single 58-case series `aso_reagent_coverage.py` owns, because
#: that is the basis the manuscript's 68.4% was computed on. A four-series pool of the same quantity
#: already exists in this repository, built against POLICY-evidence.md §2.1–§2.3 for a different
#: paper, and it is READ here rather than re-derived (CLAUDE.md rule 1).
POOLING = os.path.join(HERE, "fusion-partner", "emc-fusion-partner-pooling.json")

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
            "⚠ SUPERSEDED WITHIN THE DAY, RETAINED: 'DESIGNS NOW EXIST, AND ARE NOT YET SCREENED "
            "… ⛔ NONE has been through the five deep off-target screens, which need BLAST and "
            "network, so their load is UNKNOWN and their counts are not comparable with the "
            "panel's.' ⭐ ALL FIVE SCREENS HAVE NOW RUN at the manuscript geometry, in CI, and "
            "their per-design output is joined into the panel's own field set by "
            "research/modalities/aso_noncoding_acceptor_screened_table.py. This module reads that "
            "state per junction from the artifact's `screens_complete` flag and never asserts it. "
            "⛔ WHAT DOES NOT CHANGE: the junction is still not IN the manuscript's 38-junction "
            "panel — the atlas filter that drops it is a protein-level grade and the panel is "
            "reported as 38 — so its screens live in their own directory and its rows are read "
            "beside the panel's rather than pooled into them."),
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


#: ⛔ THE STRUCTURAL LIMIT INSIDE THE UNRESOLVED BLOCK, AND IT IS NOT A RETRIEVAL GAP. The three
#: EWSR1 tumours of the primary series whose transcript type is unnamed are usually written up as a
#: retrieval problem — get the paywalled full text, name the types, design the reagents. That is
#: false as a general statement about the EWS/CHN type nomenclature, because at least one named type
#: has no exon::exon junction to design against AT ALL.
#: ⚠ PROVENANCE, STATED AT ITS REAL WEIGHT. The quote below was read from the OCR layer of
#: PMC1857890's scanned page images on 2026-08-15, and its ONLY home in this repository is the
#: message of commit 218b5fa73 — no committed FILE carries it, which is a provenance weakness and is
#: named here rather than laundered. The paper's identity IS committed:
#: research/manuscripts/aso/lit-targets-aso-verify.json holds its abstract verbatim, and
#: aso/fusion-junction-aso-references.json holds Brody RI et al., Am J Pathol 1997;150(3):1049-1058,
#: PMID 9060841 / PMC1857890. The abstract does not contain this sentence; the full text does.
INTRA_EXONIC_VARIANT = {
    "type": "EWS/CHN type 3",
    "source": "PMID 9060841 (Brody 1997) / PMC1857890",
    "verbatim": ("The type 3 variant appears to be a unique, probably nonrecurrent variant "
                 "resulting from an unusual genomic breakpoint within EWS exon 12."),
    "verbatim_provenance": ("OCR layer of the scanned PMC full text, read 2026-08-15; recorded in "
                            "the message of commit 218b5fa73 and in no committed file. The "
                            "abstract committed in aso/lit-targets-aso-verify.json does NOT "
                            "contain it."),
    "⛔_what_it_means_for_this_modality": (
        "WITHIN exon 12, not between two exons. A junction-spanning oligonucleotide is specified by "
        "an exon PAIR — every design in this panel is a 16-mer straddling one seam — so a breakpoint "
        "interior to an exon has no seam for one to be specified against, at any length and in any "
        "register. This is not 'we have not retrieved the junction yet'; it is 'there is no "
        "exon::exon junction here'."),
    "⚠_what_is_NOT_established_and_must_not_be_inferred": (
        "HOW MANY tumours this accounts for, in any cohort. Type 3 was defined in a different series "
        "from the one whose three tumours are unresolved here, no source states how many tumours of "
        "either series carry it, and its own source calls it probably nonrecurrent — a description, "
        "not a count. So the structurally-undesignable share of the unresolved block is bounded "
        "below by 'at least one named type' and above by nothing, and is DELIBERATELY NOT "
        "QUANTIFIED. What it does establish is that the unresolved block cannot be assumed fully "
        "openable by retrieval alone, which is what pricing it as pure retrieval would assume."),
}

#: ⛔ A THIRD SERIES WITH EXPLICIT INTEGER COUNTS EXISTS AND IS DELIBERATELY NOT POOLED. Recorded
#: here, with the reasons and with what pooling it WOULD have produced, because a pooling rule
#: chosen after seeing the number it yields is not a rule — and this one costs coverage rather than
#: buying it, which is the check a reader is entitled to make.
THIRD_SERIES_NOT_POOLED = {
    "pmid": "11679947",
    "who": "Okamoto 2001, Hum Pathol — 18 EMCs, RT-PCR on paraffin-embedded tissue",
    "verbatim": ("EWS-CHN or TAF2N-CHN fusion gene transcripts characteristic of EMCS could be "
                 "detected in 15 (83%) of the 18 cases: EWS-CHN type 1 in 11 cases, EWS-CHN type 2 "
                 "in 1, and TAF2N-CHN in 3."),
    "verbatim_source": "research/manuscripts/aso/lit-targets-aso-verify.json (abstract_verbatim)",
    "⛔_why_it_is_not_pooled": [
        "⛔ ITS DENOMINATOR IS DEFINED BY ITS OWN ASSAY'S POSITIVITY, which is POLICY-evidence.md "
        "§2.1(3) — the outcome must not be the inclusion criterion. Twelve cases are 'EWSR1-"
        "rearranged' here only because a type-1 or type-2 primer pair fired; the three "
        "fusion-negative cases may be EWSR1-rearranged at a junction the panel had no primer for. "
        "The 58-case cohort's 46 are FISH-confirmed, which is a different and wider denominator.",
        "A JUNCTION-SPECIFIC ASSAY CANNOT REPORT A JUNCTION IT HAS NO PRIMER FOR, so its zero for "
        "the exon-13 junction is an assay-scope zero, not a measured zero — the same argument the "
        "census already makes about PMID 32612944's fixed four-junction panel.",
        "⚠ AND A NEAR-MISS WORTH NAMING: this series and the primary breakpoint series BOTH have "
        "n=18 and are different cohorts (Japanese 2001, Scandinavian/Belgian/US 2002). Two 18-case "
        "EMC series is exactly the shape of a double-count under §2.3.",
    ],
    "⭐_2026_08_15_A_SECOND_GROUND_WAS_TESTED_AND_IT_FELL_—_THE_REFUSAL_NARROWED": {
        "the_ground_that_fell": (
            "⚠ SUPERSEDED, RETAINED — this list's FIRST bullet used to read: 'IT REPORTS TYPE "
            "NUMBERS, NOT EXON PAIRS, and the two are not interchangeable across sources. PMID "
            "12378528 calls type 5 EWS exon 13 :: CHN exon 3; PMID 12598313 calls \"EMC type 5\" "
            "EWS exon 10 fused to a 72-bp sequence from TEC intron 2.' Both halves of that "
            "observation are still TRUE, and the inference drawn from them does not reach THIS "
            "series. The nomenclature is unreliable AT TYPE 5. It is not unreliable at types 1 "
            "and 2, and types 1 and 2 are all this series reports."),
        "three_concordant_primary_definitions_of_types_1_and_2": [
            "PMID 9060841 (Brody 1997), read from the OCR layer of PMC1857890's scanned pages: "
            "'In the type 1 fusion, EWS exon 12 is fused to position -2 of the CHN cDNA. The type "
            "2 variant fuses EWS exon 7 to position -176 of the CHN cDNA, resulting in a novel "
            "open reading frame of 59 amino acids.' ⭐ THIS ONE PREDATES OKAMOTO 2001, which is "
            "what makes it load-bearing: it is the numbering in circulation when this series was "
            "written. It fixes the acceptor by cDNA POSITION rather than by exon because, in its "
            "own words, 'The exon structure of CHN has not yet been elucidated' — and both "
            "positions land where the modern exon assignments put them (NR4A3 exon 3 retains 2 nt "
            "of 5'UTR; 176 nt of 5'UTR upstream of the ATG is an exon-2 acceptor).",
            "PMID 12598313 (Sjögren 2003), read from PMC1868116: 'a type 1 fusion in which EWS "
            "exon 12 is fused in frame to TEC exon 3' and 'a type 2 fusion in which EWS exon 7 is "
            "fused to TEC exon 2'. ⭐ THE SAME PAPER THAT SUPPLIES THE TYPE-5 CONFLICT AGREES ON "
            "TYPES 1 AND 2 — the divergence is not a general unreliability, it is one type.",
            "PMID 22567356 (Nishio 2011): type 1 = EWSR1 exon 12 :: NR4A3 exon 3, type 2 = EWSR1 "
            "exon 7 :: NR4A3 exon 2. Already in the census as the definition of the type 2 "
            "transcript.",
        ],
        "⚠_what_is_still_NOT_verified": (
            "WHICH numbering Okamoto 2001 cites. Its full text is not open access "
            "(lit-targets-aso-verify.json records open_access_full_text_retrieved: false), so the "
            "argument is that all three extant definitions of types 1 and 2 agree, not that this "
            "paper's source was read. That is weaker than a direct check and is stated as weaker."),
        "⛔_AND_IT_CHANGES_NOTHING_BECAUSE_THE_OTHER_GROUND_IS_SUFFICIENT_ALONE": (
            "§2.1(3) is not a supporting reason here, it is decisive, and the arithmetic says so "
            "without argument: this series' EWSR1 arm is 11 type 1 + 1 type 2, the panel covers "
            "BOTH types, so k/n = 12/12 = 100% BY CONSTRUCTION. That is exactly the structural "
            "100% §2.1(3) names — its own example is a 'metastatic at diagnosis' cohort whose "
            "metastasis count cannot be anything but 100%. Computed rather than asserted in "
            "`_the_structural_100_percent`."),
        "⭐_the_mechanism_is_MEASURED_not_argued": (
            "PMID 9060841 ran both assays on the same tumours and reports the discrepancy: "
            "'Long-range DNA PCR analysis for the type 1 fusion ... EWS/CHN rearrangements were "
            "identified in 3 cases of extraskeletal myxoid CS, 2 of which were negative by "
            "RT-PCR.' A type-panel RT-PCR denominator DEMONSTRABLY drops rearranged tumours — so "
            "'the three fusion-negative cases may be EWSR1-rearranged' is an observation about "
            "this class of assay, not a hypothetical."),
        "⛔_and_the_primary_series_does_NOT_have_this_defect_—_the_discriminator": (
            "PMID 12378528 names the type of 12 of its 15 EWSR1-rearranged tumours and leaves 3 "
            "UNNAMED, so k ≠ n and its denominator is not fixed by its type panel. It can do that "
            "because its partner assignment does not come from the type assay at all: the "
            "open-access restatement of the same series (PMC2395470) reports 'Cytogenetic "
            "analysis was performed after short-term culturing' and 'Chromosomal aberrations were "
            "detected in 16/17 cases in our series; 13 with involvement of 9q22 and 22q12, and "
            "three with rearrangements of 9q22 and 17q11' — an independent, karyotype-level "
            "partner determination. Okamoto worked on PARAFFIN-EMBEDDED tissue by RT-PCR alone, "
            "where no such independent determination is possible. That is the whole difference, "
            "and it is why one series is pooled and the other is not."),
        "verdict": (
            "THE REFUSAL STANDS AND THE FIGURE DOES NOT MOVE. One of its two original grounds has "
            "been withdrawn on evidence; the remaining one is sufficient by itself. Recorded this "
            "way rather than silently rewritten because a refusal that quietly swaps its reasons "
            "is indistinguishable from a refusal chosen on the outcome — and this one costs 4.5 "
            "points."),
    },
    "_the_sensitivity_it_would_have_produced": "computed in the artifact, not typed here",
    "⛔_the_sensitivity_may_not_be_quoted_as_coverage": (
        "It is reported so that the pooling rule can be seen not to have been chosen on the "
        "outcome. Applying the rule COSTS coverage relative to ignoring it, which is the direction "
        "that makes the rule credible."),
}

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


#: ⛔ THE FIVE DEEP SCREENS, AND WHERE EACH ONE DECLARES WHAT IT ACTUALLY READ.
#: Until 2026-08-19 this module recorded a junction's screen state by echoing the screened table's
#: DOCUMENT-level `n_screens_that_ran` onto every junction in it, so `PGR_e2__NR4A3_e2` — which §4.1
#: and §2.6 both state is graded on four of the five, because the pre-mRNA screen's parent set does
#: not carry that donor's unspliced sequence — carried `n_screens_that_ran: 5` in the deposited
#: artifact. A document-level count cannot be a per-junction fact, and echoing one is how a junction
#: comes to claim evidence that was never read for it.
#: ⚠ TWO OF THE FIVE ARE PARENT-SCOPED and three are transcriptome- or genome-wide. A parent-scoped
#: screen reads a NAMED set of parent transcripts, so whether it read a given junction depends on
#: whether that junction's own two parents are in the set — which is exactly the question the
#: document-level count cannot answer. The gene sets are READ from each screen's own artifact.
PARENT_SCOPED_SCREENS = ("mature_parent_gap_pairing", "premrna")
SCREEN_ARTIFACTS = {
    "panel": {
        "transcriptome_blast_deep": None,          # blastn vs refseq_rna — not gene-scoped
        "exhaustive_transcript_scan": None,        # every transcript — not gene-scoped
        "mature_parent_gap_pairing": "aso-parent-gap-pairing.json",
        "premrna": "aso-premrna-offtarget.json",
        "genome_grch38": None,                     # every position of GRCh38 — not gene-scoped
    },
    "noncoding_acceptor": {
        "transcriptome_blast_deep": None,
        "exhaustive_transcript_scan": None,
        "mature_parent_gap_pairing": "aso-parent-gap-pairing-noncoding-acceptor.json",
        "premrna": "aso-premrna-offtarget-noncoding-acceptor.json",
        "genome_grch38": None,
    },
}
MODALITIES = os.path.join(HERE, os.pardir, "modalities")


def _declared_gene_scope(basename):
    """The genes whose OWN sequence a parent-scoped screen read, plus any it admits it skipped.

    Both are READ from the screen's artifact. `parents_searched` is the mature-parent screen's own
    record of what it searched; the pre-mRNA screen keys its sequence records by gene and carries an
    explicit block naming the atlas parents it could not scan.
    """
    path = os.path.join(MODALITIES, basename)
    if not os.path.exists(path):
        return {"artifact": basename, "present": False, "genes": None, "declared_unscanned": []}
    doc = json.load(open(path, encoding="utf-8"))
    genes = (doc.get("method") or {}).get("parents_searched")
    if genes is None and isinstance(doc.get("genes"), dict):
        genes = sorted(doc["genes"])
    skipped = doc.get("⛔_parents_in_the_atlas_that_were_NOT_scanned") or {}
    return {"artifact": basename, "present": True,
            "genes": sorted(genes) if genes else None,
            "declared_unscanned": sorted(skipped.get("genes") or [])}


def parent_genes_of(label):
    """The two genes a junction's own sequence is built from, read off its label."""
    donor, _, acceptor = str(label).partition("__")
    return (donor.split("_")[0], acceptor.split("_")[0])


def per_screen_record(label, table_key, ran_here):
    """Per junction, per screen: did this screen read THIS junction's own parents?

    ⛔ `ran` AND `read_this_junctions_own_parents` ARE DIFFERENT QUESTIONS and the artifact now
    carries both. A parent-scoped screen can run over a junction's designs and still never look at
    the compartment that junction's own donor supplies, which is an ABSENT reading and not a clean
    one — the distinction CLAUDE.md §4 exists for.
    """
    own = parent_genes_of(label)
    out = {}
    for screen, basename in SCREEN_ARTIFACTS[table_key].items():
        if screen not in PARENT_SCOPED_SCREENS:
            out[screen] = {"ran": ran_here.get(screen), "gene_scoped": False,
                           "scope": "not gene-scoped — the whole transcriptome or the whole genome",
                           "this_junctions_parents_not_read": [],
                           "read_this_junctions_own_parents": bool(ran_here.get(screen))}
            continue
        scope = _declared_gene_scope(basename)
        genes = scope["genes"]
        missing = sorted({g for g in own
                          if (genes is not None and g not in genes)
                          or g in scope["declared_unscanned"]})
        out[screen] = {
            "ran": ran_here.get(screen), "gene_scoped": True,
            "source_artifact": scope["artifact"],
            "genes_searched": genes,
            "genes_the_screen_declares_it_did_not_scan": scope["declared_unscanned"],
            "this_junctions_own_parents": list(own),
            "this_junctions_parents_not_read": missing,
            "read_this_junctions_own_parents": bool(ran_here.get(screen)) and not missing,
        }
    return out


def _screen_ran_flags(doc, table_key):
    """`ran` per screen, from the table's own `screens` block when it has one."""
    block = doc.get("screens") or {}
    return {screen: bool((block.get(screen) or {}).get("ran", True))
            for screen in SCREEN_ARTIFACTS[table_key]}


def _junctions_the_deep_screens_name(doc, subdir):
    """The junction labels the per-junction screen artifacts actually declare.

    ⚠ PER JUNCTION, FROM THE ARTIFACT'S OWN `junction_label`. The screened table lists the files
    each deep screen ran; opening them turns "the alignment screen ran" from a table-level sentence
    into a per-junction fact, which is what the membership rule below needs.
    """
    named = {}
    for screen in ("transcriptome_blast_deep", "exhaustive_transcript_scan"):
        labels = set()
        for basename in ((doc.get("screens") or {}).get(screen) or {}).get("screens") or []:
            path = os.path.join(MODALITIES, subdir, basename)
            if os.path.exists(path):
                label = json.load(open(path, encoding="utf-8")).get("junction_label")
                if label:
                    labels.add(label)
        named[screen] = labels
    return named


def screened_published_junctions():
    """Every junction with BOTH a published exon-resolved breakpoint AND a SCREENED reagent —
    READ from the two screened tables, never listed here, and now with a PER-SCREEN record.

    ⛔ THE MEMBERSHIP RULE IS THE WHOLE CLAIM OF THE BEST-SUPPORTED ROW, so it is derived from the
    artifacts that own each half rather than written down as a list of five labels. A hand-typed
    membership goes stale in the direction that flatters the panel: a junction whose tier is
    downgraded, or whose screen is later found to have been run at the wrong geometry, would keep
    contributing coverage from a list nobody re-reads.

    ⛔ AND IT IS "A SCREENED REAGENT", NOT "ALL FIVE SCREENS" — THE TWO ARE NOT THE SAME SET, WHICH
    IS WHY THE COUNT IS NOW REPORTED BOTH WAYS (2026-08-19). This rule used to be written as "a
    reagent through all five deep screens" while being implemented as a `screens_complete` flag that
    reads true for a junction graded on four of the five. §4.1 states the honest version — "Eight of
    those nine designs are taken through all five screens. The ninth, at the PGR seam, is graded on
    four of them" — so the qualifying count is nine on a SCREENED-design rule, and the all-five
    subset is carried beside it as its own derived count rather than folded into the same word.

    ⚠ THE FIVE-SCREEN EVIDENCE IS DIFFERENT IN SHAPE ON EACH SIDE, AND SAYING SO IS NOT PEDANTRY.
    The panel's table carries no per-junction screen-state flag: its five-screen claim is a property
    of the whole artifact, stated in its own `what` field, and the per-junction check available here
    is that `best_available` exists — which the ranking cannot produce unless the deep alignment
    screen ran. The non-canonical table lists the per-junction artifacts each deep screen ran, so
    there the same question is answered by opening them and reading `junction_label`. Both readings
    are recorded per junction so a reader can see which one is behind each row.
    """
    out = {}
    sources = [
        (PER_JUNCTION, "aso-per-junction-table.json", "the manuscript's 38-junction panel",
         "panel", ""),
        (NONCODING_SCREENED, "noncoding-acceptor/aso-noncoding-acceptor-screened-table.json",
         "the published NON-CANONICAL seams, screened to the panel's depth",
         "noncoding_acceptor", "noncoding-acceptor"),
    ]
    for path, name, what, table_key, subdir in sources:
        if not os.path.exists(path):
            continue
        doc = json.load(open(path, encoding="utf-8"))
        table_evidence = doc.get("what") or doc.get("_title")
        ran_here = _screen_ran_flags(doc, table_key)
        named = _junctions_the_deep_screens_name(doc, subdir) if subdir else {}
        for j in doc.get("junctions") or []:
            if j.get("clinical_tier") != "published_exon_resolved_breakpoint":
                continue
            best = j.get("best_available")
            if not best:
                continue                       # no ranked reagent ⇒ the alignment screen did not run
            label = j["junction_label"]
            # ⛔ THE ALIGNMENT SCREEN MUST HAVE RUN FOR THIS JUNCTION, not for the table it sits in.
            # Where the table names its per-junction screen artifacts, that is checked by opening
            # them; where it does not, the ranked `best_available` above is the per-junction check,
            # because the rank key is that screen's output.
            deep = named.get("transcriptome_blast_deep")
            if deep is not None and deep and label not in deep:
                continue
            screens = per_screen_record(label, table_key, ran_here)
            n_ran = sum(1 for s in screens.values() if s["read_this_junctions_own_parents"])
            out[label] = {
                "partner": str(label).split("_")[0],
                "source_table": name,
                "source_table_is": what,
                "clinical_tier": j["clinical_tier"],
                "breakpoint_refs": j.get("breakpoint_refs"),
                "screen_evidence": {
                    "per_screen": screens,
                    "n_screens_that_read_this_junctions_own_parents": n_ran,
                    "n_screens": len(screens),
                    "all_five_read_this_junctions_own_parents": n_ran == len(screens),
                    "screens_that_did_not": sorted(
                        s for s, r in screens.items()
                        if not r["read_this_junctions_own_parents"]),
                    "⛔_an_absent_reading_is_not_a_reading_of_absence": (
                        "a screen that never scanned this junction's own parent leaves that "
                        "compartment UNMEASURED, not clean. The count above is of screens that read "
                        "this junction's own parents, not of screens that produced a row for it."),
                    "table_level_statement": table_evidence,
                    "per_junction_check": (
                        "the deep alignment screen's own artifact declares this junction_label"
                        if named.get("transcriptome_blast_deep") else
                        "best_available is present, so the deep alignment screen that supplies its "
                        "rank key ran for this junction"),
                    "⚠_the_table_level_flag_this_replaces": {
                        "field": "screens_complete", "value": j.get("screens_complete"),
                        "document_level_n_screens_that_ran": doc.get("n_screens_that_ran"),
                        "why_it_is_not_used": (
                            "both are properties of the whole table. Echoing them onto a junction "
                            "recorded n_screens_that_ran: 5 for a seam the manuscript states is "
                            "graded on four."),
                    },
                },
                "n_designs_screened": j.get("n_designs_screened"),
                "n_designs_clearing_the_parent_screen":
                    j.get("n_designs_clearing_the_parent_screen"),
                "best_available": {"antisense_5to3": best["antisense_5to3"],
                                   "gap_specificity_margin": best["gap_specificity_margin"]},
            }
    return out


def _pooling_admissibility():
    """⛔ POLICY-evidence.md §2.1 CHECKED, NOT ASSUMED — the four conditions, one row each.

    The pooled basis is the headline basis of the best-supported row, so the question "is this
    legal?" has to be answered against the contract rather than against intuition. Every count below
    is derived from `BASES` and from the census; the second series' counts are computed as
    pooled MINUS single-series, which is the identity `tests/test_aso_coverage_ladder.py` already
    enforces, so this block cannot disagree with the bases without that test failing first.
    """
    single, pooled = BASES["single_series"]["EWSR1"], BASES["pooled_two_series"]["EWSR1"]
    n_second = pooled["n"] - single["n"]
    second_k = {j: pooled["k"][j] - single["k"].get(j, 0) for j in pooled["k"]}
    per_series = {}
    for j, k_pooled in pooled["k"].items():
        per_series[j] = {
            "PMID 12378528": {"k": single["k"].get(j, 0), "n": single["n"],
                              "rate": round(single["k"].get(j, 0) / single["n"], 4)},
            "PMID 29937513": {"k": second_k[j], "n": n_second,
                              "rate": round(second_k[j] / n_second, 4)},
            "pooled": {"k": k_pooled, "n": pooled["n"], "rate": round(k_pooled / pooled["n"], 4)},
            "between_series_rate_range": sorted(
                [round(single["k"].get(j, 0) / single["n"], 4), round(second_k[j] / n_second, 4)]),
        }
    return {
        "_governing_policy": "systems/POLICY-evidence.md §2.1 (what may be pooled), §2.2 (the "
                             "denominator-weighted crude pool and its Wilson interval), §2.3 "
                             "(double-counting)",
        "series": [
            {"pmid": RC.BREAKPOINT_COHORT["pmid"], "role": "primary; the basis rung 0 uses",
             "n_EWSR1_rearranged": single["n"], "method": "RT-PCR and sequencing"},
            {"pmid": "29937513", "role": "the only other retrieved cohort resolving EVERY case to "
                                         "an exon pair by sequencing",
             "n_EWSR1_rearranged": n_second, "method": "whole-transcriptome sequencing"},
        ],
        "§2.1_conditions": {
            "1_confirmed_EMC": "MET — both series are molecularly characterised EMC, and each "
                               "resolved its cases' fusion transcripts by sequencing.",
            "2_explicit_integer_counts": (
                f"MET — {single['k']} of {single['n']} and {second_k} of {n_second}. No count here "
                "is back-derived from a published percentage, which §2.1(2) forbids."),
            "3_outcome_is_not_the_inclusion_criterion": (
                "MET — entry to each arm is 'this tumour is rearranged for this partner'; the "
                "outcome is WHICH exon pair. Being EWSR1-rearranged does not determine the exon, so "
                "the outcome is not structurally fixed by the inclusion rule. ⚠ This is exactly the "
                "condition the third series below FAILS, which is why it is not pooled."),
            "4_non_overlapping_populations": (
                "MET on the evidence available — different countries, different institutions and "
                "sixteen years apart (a Scandinavian/Belgian/US consortium series published 2002, "
                "an Italian series published 2018). §2.3 permits distinct populations explicitly. "
                "⚠ Neither paper publishes patient identifiers, so this is an argument from "
                "provenance rather than a linkage check, and it is stated as one."),
        },
        "§2.2_disclosures": {
            "one_study_dominates": (
                f"YES, and §2.2 requires saying so: {single['n']} of {pooled['n']} EWSR1-rearranged "
                f"tumours ({round(100 * single['n'] / pooled['n'], 1)}%) come from one series, so "
                "the pooled estimate is close to that series' own wherever the two agree."),
            "heterogeneity_per_junction": per_series,
            "_how_to_read_the_range": (
                "§2.2 asks for the per-cohort rates side by side and their range rather than an I². "
                "The two series agree closely on the exon-12 and exon-13 junctions and disagree "
                "completely on exon 7 :: exon 2 — 0/15 against 1/5 — which is the entire reason the "
                "basis choice matters and is discussed under `_why_the_pooled_basis_is_the_headline`"
                " below."),
        },
        "third_series_deliberately_not_pooled": THIRD_SERIES_NOT_POOLED,
    }


def _three_series_sensitivity(junctions):
    """What pooling the third series WOULD have produced. ⛔ Not coverage; see the reasons above."""
    counts, n_cohort = RC.PARTNER_COHORT["counts"], RC.PARTNER_COHORT["n"]
    pooled = BASES["pooled_two_series"]["EWSR1"]
    # Okamoto's EWSR1 arm, read off its own verbatim: type 1 in 11, type 2 in 1 → n = 12.
    okamoto = {E12: 11, E7X2: 1, E13: 0}
    n3 = sum(okamoto.values())
    covered = [j for j in junctions if j.startswith("EWSR1_")]
    k = sum(pooled["k"].get(j, 0) + okamoto.get(j, 0) for j in covered)
    n = pooled["n"] + n3
    frac = k / n
    taf15 = counts["TAF15"] / n_cohort           # unchanged: this series reports TAF2N at gene level
    total = counts["EWSR1"] / n_cohort * frac + taf15
    return {
        "_what_it_is": (
            "the same panel, priced on THREE series instead of two, by adding PMID 11679947's "
            "type-numbered counts to the EWSR1 arm."),
        "EWSR1_arm": f"{k}/{n}",
        "_okamoto_arm_as_read": okamoto,
        "_okamoto_n_derivation": (
            f"11 type 1 + 1 type 2 = {n3} EWS-CHN-positive cases; the 3 TAF2N cases go to the TAF15 "
            "arm, which this series reports at gene level and which therefore does not move; the 3 "
            "fusion-negative cases are excluded by the assay, which is the defect."),
        "coverage_percent_it_would_give": round(100 * total, 1),
        "⛔_it_is_HIGHER_than_the_reported_figure_and_is_still_refused": (
            f"{round(100 * total, 1)}% against the reported figure — so excluding this series is "
            "the conservative choice as well as the correct one, and the pooling rule cannot have "
            "been chosen to maximise the headline. The reasons it is refused are in "
            "`third_series_deliberately_not_pooled` and none of them is the number."),
        "⛔_the_structural_100_percent": {
            "_what_this_shows": (
                "POLICY-evidence.md §2.1(3) refuses a cohort whose outcome is fixed by its own "
                "inclusion rule. Whether this series is such a cohort is DECIDED BY ARITHMETIC "
                "rather than by reading its methods: if every case admitted to its EWSR1 arm is "
                "admitted BECAUSE a covered junction's primer fired, then k equals n exactly."),
            "okamoto_k_over_n_for_the_covered_junctions":
                f"{sum(okamoto.get(j, 0) for j in covered)}/{n3}",
            "is_it_structurally_one_hundred_percent":
                sum(okamoto.get(j, 0) for j in covered) == n3,
            "⛔_verdict": (
                "YES — every case in this arm carries one of the two junctions the panel covers, "
                "because a case with any OTHER junction could not have entered the arm. §2.1(3) "
                "fails, and it fails on its own without the type-nomenclature ground that was "
                "withdrawn on 2026-08-15."),
            "the_same_check_on_the_series_that_IS_pooled": {
                "PMID 12378528":
                    f"{sum(BASES['single_series']['EWSR1']['k'].values())}/"
                    f"{BASES['single_series']['EWSR1']['n']}",
                "why_it_passes": (
                    "k < n. Three of its fifteen EWSR1-rearranged tumours carry types it never "
                    "names, so membership of its denominator is NOT the outcome — the partner was "
                    "established by karyotype after short-term culture, independently of the "
                    "transcript typing."),
            },
        },
    }


#: ⛔ THE FIFTH PARTNER COHORT. `emc_fusion_partner_pooling.py` carries it as a `pool: false`
#: prevalence row with `contextReason: "outcome-is-the-inclusion-criterion"`; this module PRICES the
#: refusal. The id is named once, here, so the row below cannot silently start reading a different
#: cohort than the one the pooling module refused.
FIFTH_PARTNER_COHORT_ID = "sjogren-2003-prevalence"


def _fifth_partner_cohort_not_pooled(doc, screened, counts, residue, tested, classify):
    """⛔ WHAT THE FIFTH PARTNER COHORT WOULD HAVE DONE TO THE CEILING, COMPUTED NOT ARGUED.

    ⭐ WHY THIS IS THE ROW THAT HAD TO BE WRITTEN. The four-series partner denominator above put the
    arithmetic ceiling BELOW 95%, and it did so because of one quantity: the partner-unassigned
    residue, 9 of 163. A fifth cohort with proportionally FEWER unassigned tumours would push the
    ceiling back UP. Sjögren 2003 (PMID 12598313) is exactly that cohort — every one of its patients
    is fusion-positive, so its residue is ZERO — and it was named as a candidate and left untested.
    Leaving it untested is the failure mode: an unpriced refusal is indistinguishable from a refusal
    chosen on the number it avoids.

    ⛔ IT IS REFUSED, AND THE REFUSAL COSTS US THE HIGHER FIGURE. POLICY-evidence.md §2.1(3) is the
    single ground; §2.1(1), §2.1(2) at patient level and §2.1(4) all pass. The counts, the entry
    routes and the reason live in the pooling module's cohort row and are READ here (CLAUDE.md rule
    1); what this function adds is the arithmetic — the ceiling the refusal declines to claim.

    ⚠ THE RESIDUE STAYS IN THE DENOMINATOR HERE TOO. The sensitivity adds the fifth cohort's
    partner-assigned counts to the numerator AND its `n_tested` to the denominator, and asserts the
    reconstruction closes on its own published total, exactly as the four-series row does. A
    zero-residue cohort is precisely the shape that would tempt a denominator swap.
    """
    row = next((c for c in doc["cohorts"] if c["id"] == FIFTH_PARTNER_COHORT_ID), None)
    if row is None:
        return {"_unavailable": (f"{FIFTH_PARTNER_COHORT_ID} is not in the pooling artifact; the "
                                 "refusal has no home to be read from and is not restated here")}
    if row.get("pool"):
        raise SystemExit(
            f"{FIFTH_PARTNER_COHORT_ID} is now pool==true in the pooling artifact. This row prices "
            "a REFUSAL; if the refusal has been lifted the four-series figures above are the stale "
            "ones and must be rebuilt, not annotated. Refusing to publish a sensitivity that "
            "contradicts its own basis.")
    add = {k.split("::")[0]: v for k, v in row["counts"].items()}
    if sum(add.values()) + row["not_partner_assigned"] != row["n_tested"]:
        raise SystemExit(
            f"{FIFTH_PARTNER_COHORT_ID} does not close: {sum(add.values())} assigned + "
            f"{row['not_partner_assigned']} unassigned != {row['n_tested']} tested.")

    w_counts = dict(counts)
    for p, v in add.items():
        w_counts[p] = w_counts.get(p, 0) + v
    w_residue = residue + row["not_partner_assigned"]
    w_tested = tested + row["n_tested"]
    if sum(w_counts.values()) + w_residue != w_tested:
        raise SystemExit("the five-series reconstruction does not close on its own totals")

    # ⛔ THE THREE ARM STATES ARE THE CALLER'S, NOT THIS FUNCTION'S. `classify` is the same
    # membership-and-measurement test the four-series row runs, handed in rather than reimplemented,
    # so a partner cannot be scored one way there and another way here. A partner with no qualifying
    # reagent contributes ZERO to the bound as well as to the point estimate — it is not a bound,
    # because a bound needs a reagent whose reach is unmeasured.
    def _cov_bound_ceiling(cnt, tot):
        point = bound = 0.0
        for p in sorted(cnt):
            state, frac = classify(p)
            if state == "measured":
                point += cnt[p] / tot * frac
                bound += cnt[p] / tot * frac
            elif state == "bound_only":
                bound += cnt[p] / tot
        return point, bound, sum(cnt.values()) / tot

    now_c, now_b, now_ceil = _cov_bound_ceiling(counts, tested)
    would_c, would_b, would_ceil = _cov_bound_ceiling(w_counts, w_tested)

    routes = row["entry_route_per_patient"]
    new, prior = routes["new_in_this_series"], routes["previously_reported_by_the_same_group"]

    def _variant_share(block):
        p = block["partners"]
        n = sum(p.values())
        return f"{n - p.get('EWSR1::NR4A3', 0)}/{n}", round(100 * (n - p.get("EWSR1::NR4A3", 0)) / n, 1)

    return {
        "_what": ("★ LEVER 3, TESTED 2026-08-15 — the fifth candidate partner cohort, PMID "
                  "12598313 (Sjögren 2003, Göteborg), named by an earlier pass and left unacted "
                  "on. It is refused, and what refusing it costs is computed below."),
        "cohort": {"id": row["id"], "label": row["label"], "sourceId": row["sourceId"],
                   "counts_patient_level": row["counts"], "n_patients": row["n_tested"],
                   "partner_unassigned": row["not_partner_assigned"],
                   "contextReason": row["contextReason"]},
        "⭐_the_two_§2.3_adjudications_that_had_to_be_settled_FIRST": {
            "_why_first": (
                "Both are double-counting questions, and §2.3 calls double-counting the cardinal "
                "sin of pooling. Neither could be answered from the abstract, and the earlier pass "
                "recorded them as prerequisites rather than settling them. Both are now settled "
                "against the full text (PMC1868116, HTTP 200)."),
            "1_is_its_TCF12_case_the_2000_index_tumour": {
                "answer": "YES — it is not an independent TCF12 observation.",
                "evidence": ("its Discussion cites the 2000 report for that count, its "
                             "Introduction claims it in the first person, and its Table 3 case 8 "
                             "carries that tumour's t(9;15)(q22;q21) karyotype. One home: "
                             "research/literature/tcf12-nr4a3-breakpoint-primary-sources.json."),
                "⭐_and_it_is_BROADER_than_the_TCF12_case": (
                    "The full text's Materials and Methods puts FOUR of the nine patients in that "
                    "position, not one: 'The remaining five tumors from four patients (cases 6-I "
                    "and 6-II as well as cases 7 to 9) have been previously reported regarding the "
                    "expression of EMC-specific fusion transcripts.' That is the finding that "
                    "decides the poolability, and it decides it at §2.1(3) rather than §2.3."),
                "⚠_it_does_NOT_bar_the_cohort_under_§2.3": (
                    "None of the three prior reports (refs 7, 12, 15) is in the partner-prevalence "
                    "pool, and §2.3 holds out the SMALLER of an overlapping pair — which would be "
                    "those reports, not this series. §2.1(4) passes."),
            },
            "2_are_its_partner_counts_tumour_level_or_patient_level": {
                "answer": "TUMOUR-level in the abstract, PATIENT-level in the Discussion.",
                "evidence": ("Table 3's title is 'Summary of Cytogenetics, SKY, FISH, and RT-PCR "
                             "Analyses in 10 EMCs from Nine Patients' and its footnotes are "
                             "'*Case 4 A, B, and C represent different parts of the same tumor' "
                             "and '† Case 6 I and II represent two separate metastases from one "
                             "patient'. The abstract's 5/4/1 sums to ten tumours; the Discussion's "
                             "'five, three, and one patient' sums to nine patients."),
                "what_was_carried_into_the_cohort_row": (
                    "the PATIENT-level integers, which is what §2.3's mutually-exclusive-strata "
                    "rule requires. Pooling the abstract's TAF2N integer would have counted case "
                    "6's patient twice."),
            },
        },
        "⛔_§2.1_checked_row_by_row": {
            "1_confirmed_EMC": (
                "MET — molecularly characterised EMC; every case carries a translocation-generated "
                "or cryptic fusion, and all but one tumour is karyotyped."),
            "2_explicit_integer_counts": (
                "MET, AT PATIENT LEVEL ONLY. The Discussion gives the three integers and Table 3's "
                "title gives the denominator; no count here is back-derived from a percentage. "
                "⚠ The abstract's integers would NOT satisfy §2.1(2)+§2.3 together — see the "
                "adjudication above."),
            "3_outcome_is_not_the_inclusion_criterion": (
                "⛔ FAILS, AND THIS IS THE WHOLE REFUSAL. Four of the nine patients are in this "
                "series because their fusion transcript had already been published by the same "
                "group, so for them the outcome — which partner, and whether a partner can be "
                "named at all — IS the entry criterion. A tumour whose partner nobody could name "
                "could not have been among them, which makes this cohort's headline property, a "
                "partner-unassigned residue of ZERO, structural on that half of the cohort rather "
                "than measured. Same failure mode as `third_series_deliberately_not_pooled`, "
                "reached from the other direction: there the assay fixed the denominator, here the "
                "publication history does."),
            "4_non_overlapping_populations": (
                "MET against the four pooled series — Göteborg 2003 against MSKCC 2014, Taiwan "
                "2023, Czech Republic 2023 and the Italian Sarcoma Group 2021, with no shared "
                "authors, institutions or referral network and eighteen years of separation from "
                "the nearest."),
            "verdict": "REFUSED on §2.1(3) alone. Three of the four conditions pass.",
        },
        "⛔_§2.1(3)_is_DECIDED_BY_ARITHMETIC_NOT_BY_READING": {
            "_the_test": (
                "partition the cohort by how each patient got in, then compare what each half "
                "contains. If the structurally-admitted half is enriched for the outcome, the "
                "inclusion rule is doing the work the outcome is supposed to."),
            "freely_admitted_new_patients": {
                "cases": new["cases"], "partners": new["partners"],
                "variant_partner_share": _variant_share(new)[0],
                "variant_partner_percent": _variant_share(new)[1]},
            "structurally_admitted_previously_reported_patients": {
                "cases": prior["cases"], "partners": prior["partners"],
                "variant_partner_share": _variant_share(prior)[0],
                "variant_partner_percent": _variant_share(prior)[1]},
            "structurally_admitted_fraction_of_the_cohort":
                f"{len(prior['cases'])}/{row['n_tested']}",
            "⛔_verdict": (
                f"The half admitted on published fusion status is "
                f"{_variant_share(prior)[1]}% variant-partner; the half admitted without it is "
                f"{_variant_share(new)[1]}%. The group's own index reports of the two RARE "
                "partners are what those four patients are, so the inclusion rule imports exactly "
                "the partners the prevalence question is asking about. That is §2.1(3), computed."),
        },
        "the_sensitivity_it_would_have_produced": {
            "pooled_partner_counts": w_counts,
            "n_partner_assigned": sum(w_counts.values()),
            "n_partner_unassigned": w_residue,
            "n_molecularly_confirmed_total": w_tested,
            "coverage_percent": round(100 * would_c, 1),
            "bound_if_the_unmeasured_arms_are_at_their_ceiling_percent": round(100 * would_b, 1),
            "arithmetic_ceiling_percent": round(100 * would_ceil, 1),
            "against_the_four_series_row": {
                "coverage_percent": round(100 * now_c, 1),
                "bound_percent": round(100 * now_b, 1),
                "arithmetic_ceiling_percent": round(100 * now_ceil, 1)},
            "ceiling_movement_percentage_points": round(100 * (would_ceil - now_ceil), 2),
            "⛔_the_residue_is_STILL_IN_THE_DENOMINATOR": (
                f"{w_residue} of {w_tested}. The fifth cohort contributes zero unassigned cases, "
                "so the residue COUNT does not move and only the denominator grows — which is "
                "precisely why the ceiling rises. The residue was not dropped, and the "
                "reconstruction is asserted to close on every cohort's own published total."),
        },
        "⭐_AND_THE_ANSWER_TO_THE_95_PERCENT_QUESTION_DOES_NOT_CHANGE_EITHER_WAY": (
            f"The refused sensitivity puts the arithmetic ceiling at "
            f"{round(100 * would_ceil, 1)}% against the four-series row's "
            f"{round(100 * now_ceil, 1)}%. It rises — and it is STILL BELOW 95%. So the "
            "load-bearing conclusion of the four-series row survives the strongest lever anyone "
            "has named against it: on a pooled partner denominator no panel of any size reaches "
            "95% of molecularly confirmed EMC, and that holds whether or not this cohort is "
            "admitted. ⚠ Read as robustness, not as licence — the sensitivity is refused, and one "
            "cohort's admission was never going to move a 163-case denominator far."),
        "⚠_DO_NOT_CONFUSE_THIS_CEILING_WITH_THE_LADDER_S_OTHER_94_8_PERCENT": (
            "The ladder's `ceiling.EWSR1_and_TAF15_complete_percent` is also 94.8%, and it is a "
            "DIFFERENT quantity that happens to round to the same value: that one is a PANEL "
            "figure on the single 58-case series — what covering every EWSR1 and every TAF15 "
            "breakpoint reaches, with TCF12 excluded. This one is a DENOMINATOR figure on a "
            "five-series pooled partner prevalence — what every named partner including TCF12 "
            "reaches once the partner-unassigned residue is in. They agree by coincidence and "
            "diverge the moment either input moves; neither may be quoted for the other."),
        "⚠_what_it_would_NOT_have_moved": (
            f"The buildable figure. {round(100 * would_c, 1)}% against "
            f"{round(100 * now_c, 1)}% — the cohort's partner mix is close enough to the pool's "
            "that the coverage point estimate is unchanged at one decimal place. The whole effect "
            "of this lever is in the ceiling and the bound, which is where the residue lives."),
        "⛔_it_ALSO_reaches_the_TAF15_PROGNOSTIC_synthesis_and_is_NOT_applied_there": (
            "FLAGGED, NOT DONE. This series publishes a per-patient follow-up string (Table 1) "
            "that joins to Table 3's partner column, so a TAF15-vs-EWSR1 outcome arm could be "
            "CONSTRUCTED from it — and its three TAF15 patients record no tumour-related death, "
            "which would pull the pooled TAF15 disease-specific-death arm DOWN. It is refused on "
            "two independent grounds recorded in the pooling module's own cohort row: §2.1(3) as "
            "above, and §2.1(2), because the paper publishes no per-partner outcome EVENT COUNTS "
            "— only narrative per patient. ⚠ NO PROGNOSTIC FIGURE IN THIS REPOSITORY MOVES, and "
            "the direction is named here so that not moving it is a visible decision."),
    }


def _pooled_partner_denominator_sensitivity(screened):
    """⭐ THE SAME PANEL, PRICED ON A PARTNER DENOMINATOR OF FOUR SERIES INSTEAD OF ONE.

    ⛔ WHY THIS ROW EXISTS AND WHAT IT IS NOT. Every rung and bound above prices partner share
    against ONE 58-case series (PMID 36948401), because that is the basis the manuscript's published
    68.4% was computed on and rung 0 has to reproduce it exactly. That is a basis choice, not a
    measurement, and it had never been tested. It is tested here.

    ⛔ THE COUNTS ARE NOT RE-DERIVED AND NOT RETYPED. `research/manuscripts/emc_fusion_partner_
    pooling.py` already owns a pooled EMC partner prevalence, built for a different paper against
    POLICY-evidence.md §2.1–§2.3, with its own admissibility argument and its own exclusions — two
    congress abstracts held out, one for being abstract-only and one for population overlap with a
    peer-reviewed report of the same patients. This function READS that artifact's cohort table and
    would rather fail than restate a count (CLAUDE.md rule 1).

    ⚠ ONE ADJUSTMENT IS REQUIRED AND IT IS THE WHOLE DIFFICULTY. That module's denominator is
    PARTNER-ASSIGNED CASES ONLY: each series' NR4A3-rearranged-but-partner-unassigned residue is
    excluded from both numerator and denominator, because the series do not report it comparably.
    ⛔ THAT CONVENTION IS CORRECT FOR ITS QUESTION AND WRONG FOR THIS ONE. A tumour whose partner
    nobody could name is precisely a tumour no junction reagent can ever engage, so for COVERAGE it
    belongs in the denominator and nowhere else. Dropping it would compute coverage of
    partner-assigned EMC while calling it coverage of EMC — the same denominator swap that put 95%
    in the manuscript's abstract. So the residue is added back, and the reconstruction is asserted
    to close against each cohort's own published total rather than assumed to.
    """
    if not os.path.exists(POOLING):
        return {"_unavailable": f"{POOLING} is not present in this checkout"}
    doc = json.load(open(POOLING, encoding="utf-8"))
    prev = [c for c in doc["cohorts"]
            if c["endpoint"] == "partner_prevalence" and c.get("pool")]
    if not prev:
        return {"_unavailable": "the pooling artifact carries no pooled partner-prevalence cohort"}

    counts, residue, tested, per_cohort = {}, 0, 0, {}
    for c in prev:
        tested += c["n_tested"]
        residue += c["not_partner_assigned"]
        for label, v in c["counts"].items():
            counts[label.split("::")[0]] = counts.get(label.split("::")[0], 0) + v
        per_cohort[c["id"]] = {
            "label": c["label"], "sourceId": c["sourceId"],
            "counts": c["counts"], "n_tested": c["n_tested"],
            "partner_unassigned": c["not_partner_assigned"]}
    # ⛔ THE RECONSTRUCTION MUST CLOSE ON EVERY COHORT'S OWN PUBLISHED TOTAL. Adding a residue back
    # into a denominator is exactly where an invented case would hide, so this raises rather than
    # prints — the same rule the gap decomposition below follows.
    if sum(counts.values()) + residue != tested:
        raise SystemExit(
            f"the pooled partner reconstruction does not close: {sum(counts.values())} assigned + "
            f"{residue} unassigned != {tested} tested. One cohort's counts, residue and total "
            "disagree; refusing to publish a denominator that cannot account for its own cases.")

    pooled = BASES["pooled_two_series"]

    # ⛔ THE ARM CLASSIFIER IS DEFINED ONCE AND SHARED WITH THE FIFTH-COHORT SENSITIVITY BELOW,
    # because a partner scored `measured` in one row and `bound_only` in the other would make the
    # two rows silently incomparable — and the fifth-cohort row's whole job is to be compared.
    def _classify(partner):
        if not any(r["partner"] == partner for r in screened.values()):
            return "no_reagent", None
        spec = pooled.get(partner)
        if spec is None or partner in PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT:
            return "bound_only", None
        covered = [l for l, r in screened.items() if r["partner"] == partner]
        return "measured", sum(spec["k"].get(j, 0) for j in covered) / spec["n"]

    measured, unmeasured, no_reagent = [], [], []
    point = lo = hi = 0.0
    for partner in sorted(counts):
        share = counts[partner] / tested
        covered = sorted(l for l, r in screened.items() if r["partner"] == partner)
        row = {"partner": partner, "junctions_in_panel": covered,
               "partner_share_of_pooled_cohort": round(share, 4),
               "partner_share_counts": f"{counts[partner]}/{tested}"}
        if not covered:
            row["⛔_why_it_contributes_zero"] = (
                "NO junction of this partner has both a published exon-resolved breakpoint and a "
                "reagent through all five deep screens, so there is nothing to engage it with. "
                "This is not a bound either: a bound needs a reagent whose reach is unmeasured, "
                "and here there is no reagent. The partner is visible only because the wider "
                "denominator contains it — which is itself the point of widening.")
            no_reagent.append(row)
            continue
        spec = pooled.get(partner)
        if spec is None or partner in PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT:
            row["within_partner_distribution"] = "UNMEASURED"
            row["contribution_to_the_point_estimate"] = 0.0
            row["contribution_if_every_case_of_this_partner_carried_it"] = round(share, 4)
            unmeasured.append(row)
            continue
        k = sum(spec["k"].get(j, 0) for j in covered)
        f_lo, f_hi = RC.wilson(k, spec["n"])
        row["breakpoint_fraction_pooled"] = f"{k}/{spec['n']}"
        row["contribution"] = round(share * k / spec["n"], 4)
        measured.append(row)
        point += share * k / spec["n"]
        lo += share * f_lo
        hi += share * f_hi

    bound = point + sum(u["contribution_if_every_case_of_this_partner_carried_it"]
                        for u in unmeasured)
    ceiling = sum(counts.values()) / tested
    return {
        "_what": ("★ LEVER 2, TESTED 2026-08-15 — the best-supported buildable panel priced on the "
                  "pooled four-series partner prevalence instead of the single 58-case series."),
        "_it_is_a_SENSITIVITY_and_supersedes_nothing": (
            "⛔ Every rung, bound and figure above is unchanged and rung 0 still reproduces 68.4% "
            "exactly. The manuscript's basis is the single series and stays the single series; "
            "this row says what the same panel is worth if the partner denominator is widened as "
            "far as the retrieved record and POLICY-evidence.md together allow."),
        "_the_counts_are_READ_not_derived_here": {
            "artifact": "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json",
            "generator": doc.get("_generated_by"),
            "selection": ("every cohort in that artifact with endpoint == 'partner_prevalence' and "
                          "pool == true. Its own exclusions are inherited unexamined, which is the "
                          "point of reading rather than re-deciding: "
                          + json.dumps(doc["analyses"]["C_partner_prevalence"]["cohorts_excluded"],
                                       ensure_ascii=False)),
            "its_non_overlap_argument":
                doc["analyses"]["C_partner_prevalence"]["non_overlap_argument"],
            "per_cohort": per_cohort,
        },
        "⚠_the_denominator_is_NOT_that_artifacts_denominator": (
            "That artifact pools over PARTNER-ASSIGNED cases and reports 154. This row adds each "
            f"cohort's partner-unassigned residue back, giving {tested}, because a tumour whose "
            "partner nobody could name is a tumour no junction reagent can engage and therefore "
            "belongs in a coverage denominator. Quoting that artifact's percentages as coverage "
            "shares would compute coverage of partner-assigned EMC and call it coverage of EMC."),
        "pooled_partner_counts": counts,
        "n_partner_assigned": sum(counts.values()),
        "n_partner_unassigned": residue,
        "n_molecularly_confirmed_total": tested,
        "arms_with_a_measured_within_partner_distribution": measured,
        "arms_with_NO_measured_within_partner_distribution": unmeasured,
        "arms_with_NO_qualifying_reagent_at_all": no_reagent,
        "coverage_percent": round(100 * point, 1),
        "coverage_percent_range": [round(100 * lo, 1), round(100 * hi, 1)],
        "bound_if_the_unmeasured_arms_are_at_their_ceiling_percent": round(100 * bound, 1),
        "arithmetic_ceiling_percent": round(100 * ceiling, 1),
        "⭐_WHAT_IT_ACTUALLY_DOES_TO_THE_FIGURE": (
            "IT LOWERS IT, AND THAT IS REPORTED BECAUSE IT IS WHAT HAPPENED. Widening the partner "
            "denominator was expected to be able to move coverage either way — a pooled mix with "
            "proportionally more TAF15 would have raised it, since the TAF15 arm is priced at 3/3 "
            "against EWSR1's 17/20. The TAF15 share does rise. It is outweighed by the "
            "partner-unassigned residue, which rises much further: 1 of 58 in the single series "
            f"against {residue} of {tested} pooled. A single cohort that could name the partner in "
            "all but one case understates how often the partner cannot be named."),
        "⛔_AND_IT_MOVES_THE_95_PERCENT_QUESTION_—_THIS_IS_THE_LOAD_BEARING_CONSEQUENCE": (
            "On the single series the arithmetic ceiling is above 95%, so 95% is reachable in "
            "principle and the ladder's result is that reaching it REQUIRES the TCF12 arm. On the "
            "pooled partner denominator the ceiling itself falls BELOW 95%: no panel of any size, "
            "covering every breakpoint of every named partner including TCF12, reaches 95% of "
            "molecularly confirmed EMC — because more than five percent of it has no named partner "
            "to build a junction reagent against. ⚠ THIS IS A SENSITIVITY, NOT A REPLACEMENT: it "
            "does not retract the single-series ceiling, it shows that the ceiling's position "
            "relative to 95% depends on a basis choice nobody had tested, and that on the wider "
            "basis the 95% target is unreachable rather than merely hard."),
        "⚠_what_this_row_does_NOT_fix": (
            "The within-partner breakpoint fractions are unchanged — still 20 sequenced EWSR1 "
            "tumours and three TAF15 ones, still transported from series that are not these four. "
            "Widening the partner denominator makes the PARTNER share better measured and does "
            "nothing whatever for the exon distribution inside it, which is the arm carrying the "
            "narrower evidence."),
        "fifth_partner_cohort_deliberately_not_pooled":
            _fifth_partner_cohort_not_pooled(doc, screened, counts, residue, tested, _classify),
    }


def best_supported_buildable_panel(screened):
    """★ THE ROW THIS MODULE WAS MISSING: what the evidence ACTUALLY IN HAND supports today.

    ⛔ WHY IT IS NOT A RUNG, AND WHY IT IS NOT A REPLACEMENT EITHER. The ladder is incremental — each
    rung adds one reagent to the previous panel — and every rung is priced on the single series the
    manuscript uses, so the ladder answers "what does one more oligonucleotide buy?" This row answers
    a different question: given every junction that has BOTH a published exon-resolved breakpoint AND
    a reagent through all five deep screens, and given the whole retrieved breakpoint record rather
    than one series of it, what fraction of molecularly confirmed EMC could a panel engage today? It
    sits beside the ladder. It replaces nothing, and rung 0 still reproduces 68.4%.

    ⛔ THE POINT ESTIMATE COVERS ONLY PARTNERS WITH A MEASURED WITHIN-PARTNER DISTRIBUTION, AND THE
    REST IS A NAMED BOUND RATHER THAN A NUMBER FOLDED IN. That is the whole difference between this
    row and the bounds above it: a bound that is added into a total stops being visible as a bound.
    """
    counts, n_cohort = RC.PARTNER_COHORT["counts"], RC.PARTNER_COHORT["n"]
    pooled, single = BASES["pooled_two_series"], BASES["single_series"]

    in_cohort = {lab: rec for lab, rec in screened.items() if rec["partner"] in counts}
    outside = sorted(set(screened) - set(in_cohort))

    # ⛔ ONE COUNT WAS HIDING THREE STATES, AND IT READ 7 WHERE 5 MOVE THE ESTIMATE.
    # `n_junctions_that_can_move_this_cohort` tested only whether the PARTNER is in the cohort. Two
    # junctions -- EWSR1_e13__NR4A3_e2 and TAF15_e6__NR4A3_e2 -- have partners that ARE in it while
    # their exon pairs are absent from the measured within-partner distribution, so they passed the
    # test and moved the total by zero. The field's NAME is its contract, so the test is widened to
    # match the name rather than the name loosened to match the test. Three states, named:
    #   · moves the POINT ESTIMATE -- partner in the cohort AND its exon pair carries a count
    #   · moves only the BOUND     -- partner in the cohort but its arm has no measured
    #                                 distribution at all, so its whole share sits in the band
    #   · moves NOTHING            -- partner absent from the cohort entirely
    # ⚠ These are read from the same `k` maps the arithmetic uses, never listed, so a junction
    # cannot drift into the wrong bucket while the coverage total stays right.
    def _moves(lab, rec):
        spec = pooled.get(rec["partner"])
        if spec is None or rec["partner"] in PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT:
            return "bound_only"
        return "point_estimate" if spec["k"].get(lab, 0) else "neither"

    moves_point = sorted(l for l, r in in_cohort.items() if _moves(l, r) == "point_estimate")
    moves_bound_only = sorted(l for l, r in in_cohort.items() if _moves(l, r) == "bound_only")
    in_cohort_but_moves_nothing = sorted(
        l for l, r in in_cohort.items() if _moves(l, r) == "neither")

    measured, unmeasured = [], []
    point = lo = hi = 0.0
    single_point = 0.0
    for partner in sorted({r["partner"] for r in in_cohort.values()}):
        covered = sorted(l for l, r in in_cohort.items() if r["partner"] == partner)
        share = counts[partner] / n_cohort
        spec = pooled.get(partner)
        if spec is None or partner in PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT:
            unmeasured.append({
                "partner": partner, "junctions_in_panel": covered,
                "partner_share_of_cohort": round(share, 4),
                "partner_share_counts": f"{counts[partner]}/{n_cohort}",
                "reagent_state": "screened and in hand — see `panel_membership`",
                "within_partner_distribution": "UNMEASURED",
                "contribution_to_the_point_estimate": 0.0,
                "contribution_if_every_case_of_this_partner_carried_it": round(share, 4),
                "⛔_zero_here_is_an_ABSENT_READING_NOT_A_READING_OF_ABSENCE": (
                    "This arm contributes 0 to the point estimate because nothing measures it, NOT "
                    "because the reagent reaches nobody. Its whole share is carried in the bound "
                    "below, which is the honest rendering of an unmeasured arm: a band, not a "
                    "number chosen inside one."),
            })
            continue
        k = sum(spec["k"].get(j, 0) for j in covered)
        f_lo, f_hi = RC.wilson(k, spec["n"])
        s_spec = single.get(partner)
        s_k = sum(s_spec["k"].get(j, 0) for j in covered) if s_spec else 0
        measured.append({
            "partner": partner, "junctions_in_panel": covered,
            "partner_share_of_cohort": round(share, 4),
            "partner_share_counts": f"{counts[partner]}/{n_cohort}",
            "breakpoint_fraction_pooled": f"{k}/{spec['n']}",
            "breakpoint_fraction_pooled_value": round(k / spec["n"], 4),
            "breakpoint_fraction_wilson95": [f_lo, f_hi],
            "breakpoint_fraction_single_series": f"{s_k}/{s_spec['n']}" if s_spec else None,
            "contribution": round(share * k / spec["n"], 4),
            "contribution_single_series_basis": round(share * s_k / s_spec["n"], 4) if s_spec else 0,
        })
        point += share * k / spec["n"]
        lo += share * f_lo
        hi += share * f_hi
        single_point += share * s_k / s_spec["n"] if s_spec else 0

    bound = point + sum(u["contribution_if_every_case_of_this_partner_carried_it"]
                        for u in unmeasured)
    ceiling = sum(counts[p] for p in counts if p != "no_identified_partner") / n_cohort

    # ── the distance to the ceiling, DECOMPOSED rather than left as a remainder ────────────────
    gap_rows = []
    ew = pooled["EWSR1"]
    n_unresolved = ew["n"] - sum(ew["k"].get(j, 0) for j in ew["k"])
    gap_rows.append({
        "block": "EWSR1 tumours whose transcript type the retrieved record never names",
        "counts": f"{n_unresolved}/{ew['n']} of pooled EWSR1-rearranged tumours, "
                  f"times {counts['EWSR1']}/{n_cohort} EWSR1 prevalence",
        "percent_points": round(100 * counts["EWSR1"] / n_cohort * n_unresolved / ew["n"], 1),
        "what_would_close_it": (
            "the full text of the primary series (PMID 12378528), which is not open access, or a "
            "deposited junction sequence for those tumours — elink from that record returns no "
            "direct submission, so the deposit route that resolved TCF12 does not reach it."),
        "⛔_it_is_NOT_fully_openable_and_this_is_the_structural_part": INTRA_EXONIC_VARIANT,
    })
    for u in unmeasured:
        gap_rows.append({
            "block": f"{u['partner']} — reagent in hand, within-partner distribution unmeasured",
            "counts": u["partner_share_counts"],
            # ⛔ FROM THE COUNTS, NOT FROM THE ROW'S OWN 4-dp SHARE — rounding twice turned 3.4483
            # into 3.5 and broke the decomposition's own sum by 0.1 pp in the printed summary.
            "percent_points": round(100 * counts[u["partner"]] / n_cohort, 1),
            "what_would_close_it": (
                "a SECOND tumour of this partner sequenced at junction resolution. The archives "
                "have been searched and hold nothing (see `what_would_actually_move_this`), so the "
                "assay is RNA sequencing of archival tissue — wet lab, outside this programme's "
                "operating regime, and not purchasable with compute."),
            "⚠_it_is_a_BOUND_not_a_target": (
                "Closing it could also LOWER the figure: if neither of the cohort's tumours carries "
                "this exon the arm is 0 and this row shrinks the band from the top, not the "
                "bottom."),
        })
    # ⛔ THE GAP IS THE DIFFERENCE, AND THE BLOCKS MUST REPRODUCE IT. Two independent derivations —
    # ceiling minus coverage, and the sum of the named blocks — computed separately and reconciled.
    # A decomposition that does not close is a block that is missing or double-counted, and printing
    # it anyway is how a remainder gets a name it has not earned (CLAUDE.md rule 1.1).
    # ⚠ THE BLOCKS ARE RECOMPUTED FROM THE COUNTS, NOT READ BACK OUT OF THE ROUNDED ROWS. Reading
    # the displayed 4-dp shares back in makes the check pass or fail on rounding rather than on
    # arithmetic — it failed by 0.0017 pp the first time this ran, which is a rounding artefact
    # wearing the costume of a missing block.
    gap_from_difference = 100 * (ceiling - point)
    gap_from_blocks = sum(100 * b for b in (
        counts["EWSR1"] / n_cohort * n_unresolved / ew["n"],
        *(counts[u["partner"]] / n_cohort for u in unmeasured)))
    if abs(gap_from_difference - gap_from_blocks) > 1e-9:
        raise SystemExit(
            f"the gap to the ceiling is {gap_from_difference}pp by difference but "
            f"{gap_from_blocks}pp by the named blocks. A decomposition that does not close means a "
            "block is missing or a case is counted twice; refusing to publish it.")
    gap_total = round(gap_from_difference, 1)

    return {
        "_what": ("★ THE BEST-SUPPORTED BUILDABLE PANEL — the coverage of the junctions that have "
                  "BOTH a published exon-resolved breakpoint AND a reagent through all five deep "
                  "screens at the manuscript geometry, priced on the whole retrieved breakpoint "
                  "record."),
        "_why_it_is_an_ADDITIONAL_row": (
            "⛔ IT REPLACES NOTHING. The ladder's rungs and bounds above are unchanged and rung 0 "
            "still reproduces the published 68.4% on the manuscript's own single-series basis. This "
            "row is better specified — membership is an evidence test rather than a position in an "
            "incremental series, and the basis is the whole retrieved record rather than one series "
            "of it — and it is reported beside them, never instead of them."),
        "panel_membership": {
            "_rule": ("a junction qualifies on TWO independent conditions: (i) clinical_tier == "
                      "'published_exon_resolved_breakpoint' in a screened table, and (ii) a reagent "
                      "through all five deep screens. Both are READ from the tables that own them."),
            "n_junctions_qualifying": len(screened),
            "junctions": screened,
            "n_junctions_moving_the_point_estimate": len(moves_point),
            "junctions_moving_the_point_estimate": moves_point,
            "n_junctions_moving_only_the_bound": len(moves_bound_only),
            "junctions_moving_only_the_bound": moves_bound_only,
            "⛔_in_cohort_but_moving_NOTHING": {
                "junctions": in_cohort_but_moves_nothing,
                "why": ("the PARTNER is in the cohort but this exon pair carries no count in the "
                        "measured within-partner distribution, so the reagent engages no case the "
                        "denominator contains. ⚠ A SECOND WAY TO CONTRIBUTE ZERO, and the one an "
                        "earlier partner-only test could not see: it counted these among the "
                        "junctions that can move the cohort while the unchanged total proved they "
                        "move it by zero."),
            },
            "⛔_qualifying_but_contributing_exactly_zero": {
                "junctions": outside,
                "why": ("the partner is not in the 58-case cohort's partner counts, so the "
                        "denominator contains no case such a reagent could engage. It moves "
                        "coverage by EXACTLY ZERO — not by a small amount, by zero. What it changes "
                        "is which patients are REACHABLE AT ALL, which is a different statement and "
                        "must never be added to a coverage percentage. One home for that reading: "
                        "research/modalities/aso_noncoding_acceptor_designs.py."),
            },
        },
        "basis": "pooled_two_series",
        "_why_the_pooled_basis_is_the_headline": [
            "POLICY-evidence.md §2.1's four conditions are MET and are checked row by row in "
            "`pooling_admissibility` rather than asserted. §2.2's method — a denominator-weighted "
            "crude pool with a Wilson interval on the summed counts — is the repository's standard "
            "for a simple proportion, and is what is computed here.",
            "⛔ THE SINGLE-SERIES BASIS PRICES ONE JUNCTION AT A ZERO ITS OWN SOURCE NEVER "
            "MEASURED. PMID 12378528 names the transcript type of 12 of its 15 EWSR1 tumours and "
            "leaves 3 unnamed; the exon 7 :: exon 2 junction gets 0/15 because that series never "
            "named it, which is an UNNAMED count, not an observed absence. The same series' genomic "
            "mapping reports one EWS break in intron 7 — the genomic origin a type 2 transcript "
            "comes from — so its own data points at the junction its transcript typing does not "
            "name. A basis whose zero is contradicted by its own source is not the conservative "
            "choice; it is the less informative one, and its error runs one way.",
            "⚠ BOTH BASES ARE REPORTED. The single-series figure for this identical panel is "
            "carried in `coverage_percent_single_series_basis` below and in every arm's "
            "`contribution_single_series_basis`, so a reader who rejects the pooling can read the "
            "row off the manuscript's own basis without recomputing anything.",
            "⚠ AND NEITHER BASIS IS LARGE. Twenty sequenced EWSR1 tumours and three TAF15 ones "
            "carry every fraction here; the interval below is wide for that reason and is not "
            "cosmetic.",
        ],
        "arms_with_a_measured_within_partner_distribution": measured,
        "arms_with_NO_measured_within_partner_distribution": unmeasured,
        "coverage_percent": round(100 * point, 1),
        "coverage_percent_range": [round(100 * lo, 1), round(100 * hi, 1)],
        "_how_the_range_is_built": (
            "the same composed-endpoint convention aso_reagent_coverage.py states: coverage is "
            "increasing in every breakpoint fraction, so the endpoints compose exactly when each "
            "fraction is taken to its own Wilson bound. That treats the arms as moving together and "
            "is therefore CONSERVATIVE — wider than letting them vary independently. Partner shares "
            "are held at their point estimates, as there."),
        "coverage_percent_single_series_basis": round(100 * single_point, 1),
        "bound_if_the_unmeasured_arms_are_at_their_ceiling_percent": round(100 * bound, 1),
        "⛔_the_bound_is_not_a_target": (
            "The upper figure is what coverage WOULD be if every case of an unmeasured partner "
            "carried the sequenced exon. Nothing measures that, the band's own top is not more "
            "likely than its bottom, and quoting it as achievable coverage is the same denominator "
            "error the 68.4% correction was made to fix, one level up."),
        "⚠_the_point_estimate_is_not_a_floor_either": (
            "The TAF15 arm is priced at 3/3 on three tumours, and a functional study calls a second "
            "acceptor form one of 'the two major TAF15-NR4A3 isoforms detected in human tumors' "
            "without counting it. If any TAF15 patient carries that form, the single TAF15 reagent "
            "does not reach them and this figure is optimistic on that arm. So the honest reading "
            "is a point estimate carrying a NAMED, UNQUANTIFIED downward risk at TAF15 and an "
            "UNMEASURED upward increment at TCF12 — not a floor, and not a ceiling."),
        "⛔_downstream_statements_this_row_makes_STALE_and_which_are_NOT_fixed_here": [
            {"where": "research/manuscripts/aso/fusion-junction-aso-research-article.md §5.1",
             "the_sentence": ("\"Emitting and screening those acceptors is the largest piece of "
                              "designable but undesigned coverage this analysis identifies; no "
                              "design at either junction is reported here, and none should be "
                              "assumed to exist.\""),
             "why_it_is_now_wrong": (
                 "Half of it. The EWSR1 exon 7 :: NR4A3 exon 2 acceptor is no longer UNDESIGNED — "
                 "five designs exist and all five deep screens have run at the manuscript geometry "
                 "(research/modalities/noncoding-acceptor/aso-noncoding-acceptor-screened-table"
                 ".json, `screens_complete: true`). The TAF15 exon 6 :: NR4A3 intron 2 acceptor in "
                 "the same sentence IS still undesigned, so the sentence is half true, which is "
                 "the hardest kind to notice."),
             "⚠_why_it_is_not_edited_here": (
                 "This module owns the coverage accounting, not the submission text. The "
                 "manuscript's language passes through its own claim and prose gates and one "
                 "sentence cannot be corrected in isolation without them. Recorded here so the "
                 "defect has a home in the tree rather than only in a report."),
             "what_the_corrected_statement_would_say": (
                 "the largest piece of designable-but-undesigned coverage is now the TAF15 intron-2 "
                 "acceptor alone; the exon-2 acceptor is designed and screened, is not in the "
                 "38-junction panel, and is what moves this row from the single-series 79.0% to the "
                 "pooled figure above."),
             },
        ],
        "pooling_admissibility": _pooling_admissibility(),
        "sensitivity_if_the_third_series_were_pooled": _three_series_sensitivity(sorted(in_cohort)),
        "sensitivity_if_the_partner_denominator_is_pooled":
            _pooled_partner_denominator_sensitivity(screened),
        "distance_to_the_arithmetic_ceiling": {
            "ceiling_percent": round(100 * ceiling, 1),
            "_what_the_ceiling_is": (
                f"{sum(counts[p] for p in counts if p != 'no_identified_partner')} of {n_cohort} "
                f"cases. The remaining {counts['no_identified_partner']} is NR4A3-rearranged with no "
                "identified partner, so no junction reagent can ever be built for it — a hard limit "
                "for the modality as specified, not a gap in this panel."),
            "gap_percent_points": gap_total,
            "_gap_is_DERIVED_and_checked": (
                "the blocks below are computed from the same counts as the coverage above and are "
                "asserted to sum to the gap; a mismatch raises rather than prints."),
            "⚠_do_not_derive_this_gap_by_subtracting_the_two_DISPLAYED_percentages": (
                f"They disagree by 0.1 and neither is wrong. The gap is computed from the unrounded "
                f"quantities ({round(100 * ceiling, 5)} − {round(100 * point, 5)} = "
                f"{round(gap_from_difference, 5)} → {gap_total}); subtracting the 1-dp figures a "
                f"reader sees gives {round(round(100 * ceiling, 1) - round(100 * point, 1), 1)}. "
                "The blocks sum to the derived value, not to the display arithmetic, which is why "
                "the decomposition can look 0.1 short of a hand subtraction. Quote this field, not "
                "a subtraction."),
            "blocks": gap_rows,
        },
    }


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
    screened = screened_published_junctions()
    n_cohort = RC.PARTNER_COHORT["n"]
    counts = RC.PARTNER_COHORT["counts"]

    ladder, prev = [], None
    for panel in PANELS:
        arms, point, lo, hi = _panel_coverage(panel["junctions"], BASES["single_series"],
                                              panel["complete_partners"])
        _, p_pool, _, _ = _panel_coverage(panel["junctions"], BASES["pooled_two_series"],
                                          panel["complete_partners"])
        unnamed = 3 if panel["complete_partners"] else 0
        # ⚠ FOUR STATES, NOT THREE, AND THE NEW ONE IS THE ONE THAT MOVED. A junction the panel
        # excludes is now in one of three states of its own — SCREENED in the non-canonical lane
        # (all five screens ran, read from `screens_complete`), DESIGNED BUT UNSCREENED (a
        # parent-exclusion margin only, off-target load unknown), or NOTHING AT ALL — and a junction
        # inside the panel is screened by construction. ⛔ SCREENED-OUTSIDE-THE-PANEL MUST NOT
        # RENDER AS EITHER NEIGHBOUR: as "designed" it would understate a reagent that exists, and
        # as a panel member it would enlarge a panel the manuscript reports as 38 junctions.
        outside_screened = [j for j in panel["junctions"]
                            if j in UNDESIGNABLE_IN_THE_CURRENT_PANEL and j in screened]
        designed_unscreened = [j for j in panel["junctions"]
                               if j in noncoding_designed and j not in screened]
        missing = [j for j in panel["junctions"]
                   if j in UNDESIGNABLE_IN_THE_CURRENT_PANEL
                   and j not in noncoding_designed and j not in screened]
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
            "junctions_screened_outside_the_manuscript_panel": {
                j: screened[j] for j in outside_screened},
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
            "series and reproduces 68.4%; the pooled column supersedes nothing, and neither does "
            "`best_supported_buildable_panel`, which is an additional and better-specified row "
            "beside the ladder rather than a replacement for any part of it.",
            "⚠ SUPERSEDED, RETAINED: 'Not a claim that the NR4A3 exon-2 junction is designable — "
            "nothing has been designed or screened there. That is the work this file argues for, "
            "not work it reports.' Both halves are now out of date: designs exist and all five "
            "deep screens have run at the manuscript geometry. This module reads that state per "
            "junction rather than asserting it, so the sentence it replaces cannot recur.",
            "Not a guess at the unresolved EWSR1 transcript types; they are priced, not named. ⛔ "
            "And not an assumption that pricing them would open them — at least one named EWS/CHN "
            "variant is INTRA-EXONIC and has no exon::exon seam to design against at all, which is "
            "recorded under the gap decomposition as a structural limit rather than a retrieval "
            "gap.",
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
        "best_supported_buildable_panel": best_supported_buildable_panel(screened),
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
            "⛔_EVERY_FIGURE_IN_THIS_BLOCK_RESTS_ON_ONE_58_CASE_PARTNER_SERIES": (
                "Including the statement that 95% is reachable at all. That basis was tested on "
                "2026-08-15 against a four-series pooled partner prevalence and the ceiling moved "
                "BELOW 95% — see best_supported_buildable_panel."
                "sensitivity_if_the_partner_denominator_is_pooled, which owns that arithmetic and "
                "is the only place it is stated. Nothing here is retracted: what changed is that "
                "the ceiling's position relative to 95% is now known to depend on the basis."),
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
                            "sources behind it."),
             "⭐_done_2026_08_15": (
                 "DONE. All five deep screens ran at the manuscript geometry and their per-design "
                 "output is joined into the panel's field set by "
                 "research/modalities/aso_noncoding_acceptor_screened_table.py. This is the step "
                 "that makes `best_supported_buildable_panel` computable at all: without a screened "
                 "reagent the junction has a published breakpoint and nothing to engage it with. "
                 "⚠ The points it buys are visible only on the pooled basis — on the single series "
                 "this junction is priced at a zero that series never measured."),
             "⛔_what_it_does_NOT_do": (
                 "put the junction into the manuscript's 38-junction panel. The atlas grade that "
                 "excludes it is unchanged, its screens live in their own directory so the panel's "
                 "own consumers cannot glob them, and the manuscript still reports 38.")},
            {"step": "Name the remaining unresolved EWSR1 transcript types",
             "buys_percent_points": round(100 * (counts["EWSR1"] / n_cohort) * (3 / 15), 1),
             "cost": "$0 — one more literature retrieval on a free runner",
             "blocked_on": "the full text of the primary series, which is not open access",
             "⛔_and_it_would_not_open_all_of_it": (
                 "This row prices the block as pure retrieval and that is an upper bound on what "
                 "retrieval can buy. At least one named EWS/CHN variant has no exon::exon junction "
                 "to retrieve: see the type 3 entry under "
                 "best_supported_buildable_panel.distance_to_the_arithmetic_ceiling. How much of "
                 "the block that accounts for is NOT reported by any source and is not guessed "
                 "here.")},
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
                 "TCF12-rearranged EMC has been COUNTED in independent cohorts and SEQUENCED once, "
                 "in 2000. Every later count used a partner-level assay — the 26-case series "
                 "called its TCF12 tumour by fluorescence in situ hybridization, which reports "
                 "which genes are joined and never where. So recurrence at this exon is UNTESTED "
                 "rather than refuted, and nothing in the record licenses calling this junction "
                 "private, rare or non-recurrent."),
             "⚠_corrected_2026_08_15_one_of_the_counts_was_not_independent": (
                 "This said 'COUNTED at least four times in INDEPENDENT cohorts'. PMID 12598313 is "
                 "not an independent cohort at this partner: it re-reports the 2000 tumour, citing "
                 "the 2000 paper for that very count and carrying that tumour's t(9;15)(q22;q21) "
                 "karyotype in its own Table 1. Three independent cohorts (2014, 2021, 2023) count "
                 "four TCF12 tumours between them, none sequenced. ⛔ THE CORRECTION RUNS TOWARD "
                 "THE BOUND, NOT AWAY FROM IT — one fewer independent observation of this partner "
                 "means even less is known about whether the junction recurs, which is the "
                 "conclusion this row already reached. One home for the evidence: "
                 "research/literature/tcf12-nr4a3-breakpoint-primary-sources.json."),
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
                else "  ⚠ includes a junction screened OUTSIDE the 38-junction panel"
                if r["junctions_screened_outside_the_manuscript_panel"] else "")
        print(f"  {n:>6} reagents  {r['coverage_percent']:>5}%  {d:<8} "
              f"pooled {r['coverage_percent_pooled_basis']:>5}%  {r['panel']}{flag}",
              file=sys.stderr)
    b = art["best_supported_buildable_panel"]
    g = b["distance_to_the_arithmetic_ceiling"]
    print(f"  ★ BEST-SUPPORTED BUILDABLE PANEL  {b['coverage_percent']}% "
          f"({b['coverage_percent_range'][0]}-{b['coverage_percent_range'][1]}%), pooled basis; "
          f"{b['coverage_percent_single_series_basis']}% on the single series",
          file=sys.stderr)
    pm = b["panel_membership"]
    print(f"      {pm['n_junctions_moving_the_point_estimate']} screened reagents move the estimate "
          f"({pm['n_junctions_qualifying']} qualify; "
          f"{pm['n_junctions_moving_only_the_bound']} move only the bound; "
          f"{len(pm['⛔_in_cohort_but_moving_NOTHING']['junctions'])} in-cohort worth 0; "
          f"{len(pm['⛔_qualifying_but_contributing_exactly_zero']['junctions'])} at a partner this "
          "cohort does not contain)", file=sys.stderr)
    for u in b["arms_with_NO_measured_within_partner_distribution"]:
        pp = next(r["percent_points"] for r in g["blocks"] if r["block"].startswith(u["partner"]))
        print(f"      ⛔ {u['partner']} arm UNMEASURED — 0 in the point estimate, +{pp} pp at "
              "its ceiling. A BOUND, never a target.", file=sys.stderr)
    print(f"      bound if every unmeasured arm is at its ceiling: "
          f"{b['bound_if_the_unmeasured_arms_are_at_their_ceiling_percent']}%   "
          f"arithmetic ceiling {g['ceiling_percent']}%   gap {g['gap_percent_points']} pp",
          file=sys.stderr)
    for row in g["blocks"]:
        print(f"        {row['percent_points']:>5} pp  {row['block']}", file=sys.stderr)
    ps = b.get("sensitivity_if_the_partner_denominator_is_pooled") or {}
    if "coverage_percent" in ps:
        print(f"      ⚠ on the POOLED four-series partner denominator "
              f"({ps['n_partner_assigned']}+{ps['n_partner_unassigned']}="
              f"{ps['n_molecularly_confirmed_total']} cases): {ps['coverage_percent']}% "
              f"({ps['coverage_percent_range'][0]}-{ps['coverage_percent_range'][1]}%), bound "
              f"{ps['bound_if_the_unmeasured_arms_are_at_their_ceiling_percent']}%, ceiling "
              f"{ps['arithmetic_ceiling_percent']}% — LOWER, and the ceiling is BELOW 95%",
              file=sys.stderr)
    f5 = (ps.get("fifth_partner_cohort_deliberately_not_pooled") or {}).get(
        "the_sensitivity_it_would_have_produced")
    if f5:
        print(f"      ⛔ fifth partner cohort (PMID 12598313) REFUSED at POLICY §2.1(3): it would "
              f"have raised the ceiling to {f5['arithmetic_ceiling_percent']}% "
              f"(+{f5['ceiling_movement_percentage_points']} pp) — still below 95%",
              file=sys.stderr)
    m = art["can_better_design_raise_coverage"]
    print(f"  EWSR1 e12 vs e13 donor 3' agreement: "
          f"{m['the_two_junctions_that_matter_most']['shared_3prime_donor_nt']} nt — "
          "one oligo cannot serve two breakpoints", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
