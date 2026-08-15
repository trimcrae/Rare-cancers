#!/usr/bin/env python3
"""One best-available gapmer PER JUNCTION, across all five screens.

⛔ WHY THIS EXISTS (2026-08-13, trimcrae: *"Why do we only have one candidate instead of one per
fusion type? Are we claiming it's impossible to make an ASO for any other fusion?"*). No — the
paper's own headline is that all 38 frame-compatible junctions yield a gapmer matching no parent
perfectly. But the candidate set was selected GLOBALLY: it answers "what is the single cleanest
reagent in the whole panel", which is not the question a reader has. A patient carries ONE fusion at
ONE exon pair, and is not served by the fact that the panel's cleanest design sits somewhere else.

So this ranks WITHIN each junction and publishes the whole table. The global winner is still
visible; it is simply no longer the only row.

⚠ WHAT THIS IS NOT. It is not a new measurement. Every number here is joined from a screen that
already ran, and no hit is re-aligned or re-graded. It is a re-presentation, and the honest framing
of it is that §3.2 of the manuscript already did this analysis in prose for the junctions that
mattered most — this makes it usable as a reagent list rather than something a reader reconstructs.

⛔ AND IT DOES NOT COLLAPSE TO ONE SCORE. Two quantities move in opposite directions and the whole
value of the table is in seeing both:

  * **gap-level margin** — junction-unique bases inside the catalytic gap on the shorter side. This
    is fusion-versus-parent discrimination, which is the entire point of the modality.
  * **transcriptome load** — gap-paired hybridisable near-matches at the deeper ceiling, recounted
    to gene LOCI rather than RefSeq accessions.

At the *EWSR1* exon 12 seam these disagree outright: `GGGCATATCATCAAAC` has margin 3 and a load of
123 hits, `GCATATCATCAAACCA` has margin 1 and a load of 34. Neither is "the" answer, and a composite
score would have hidden the trade instead of reporting it. The rank here is by load among designs
that clear the parent screens, with margin printed beside it, never folded in.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso-per-junction-table.json")

sys.path.insert(0, HERE)
import aso_screen_sets as ass  # noqa: E402
import junction_aso_locus_collapse as C  # noqa: E402

#: The geometry this table is about — the panel the manuscript recommends from. Named, never
#: defaulted: `load_screens` has no default geometry, precisely so that the module which has not
#: thought about geometry cannot silently inherit one. ⚠ `junction_aso_offtarget` is no longer
#: imported here: the only thing this module took from it was `GAP_REGION_1BASED`, which is the
#: geometry THIS PROCESS's environment built rather than the one the screen ran at — the constant
#: at the centre of the defect. The window now comes from `screen.geometry`.
GEOMETRY = ass.MANUSCRIPT_GEOMETRY

#: ⛔ EXON-RESOLVED PATIENT BREAKPOINTS, AND ONLY WHAT IS ACTUALLY CITED IN THE MANUSCRIPT.
#: Nothing is inferred here. EMC case reports overwhelmingly name the partner GENE without
#: sequencing to nucleotide resolution, so a junction absent from this map is "no published
#: exon-resolved breakpoint" — which is ABSENCE OF EVIDENCE, not evidence the junction does not
#: occur. The two are different and the paper must not blur them: for *TAF15* the published
#: breakpoint is exon 6, so a design at *TAF15* exon 1 is CONTRADICTED by the literature, whereas
#: *FUS* has no exon-resolved EMC breakpoint published at all and its junctions are merely unreported.
#: ⛔ AND A SECOND COHORT IS A SECOND REFERENCE, NOT A FOOTNOTE (2026-08-15). PMID 29937513 resolves
#: every case of a five-tumour series to an exon pair by whole-transcriptome sequencing — exon12/exon3
#: in #2, #3, #5 and exon13/exon3 in #4 — so ONE literal sentence supports the exon 12 and exon 13
#: rows alike, and it was cited in neither. It is added to both in the same edit for that reason:
#: citing it only at exon 13 would make the newly-corrected junction look better-sourced than the
#: manuscript's lead, which is a comparison artefact rather than a fact about the evidence.
#: ⚠ NOT ADDED, DELIBERATELY: PMID 32612944, whose clinical qRT-PCR panel targets EWSR1(ex13)/
#: NR4A3(ex3). Those are ASSAY TARGETS chosen by a laboratory, not junctions observed in its
#: patients — the paper reports its 23 molecularly analysed cases at gene level only. It corroborates
#: that the field considers this junction worth detecting; it is not a patient breakpoint, and this
#: map holds patient breakpoints. Its verbatim sentence is in lit-targets-aso-breakpoint-census.json.
PUBLISHED_BREAKPOINTS = {
    # type 1, 10 of the 15 EWSR1-rearranged tumours of an 18-case series; and 3 of the 5 cases of
    # the independent whole-transcriptome series (#2, #3, #5)
    "EWSR1_e12__NR4A3_e3": ["PMID: 12378528", "PMID: 29937513"],
    # ⛔ ADDED 2026-08-15, AND IT WAS A CURATION MISS RATHER THAN A NEW RETRIEVAL. type 5, 2 of the
    # same 15 EWSR1-rearranged tumours — the SECOND-most-common EWS/CHN transcript, named in the
    # very sentence of the very abstract this map already cited for exon 12, and committed verbatim
    # in this repository since then: "The most frequent EWS/CHN transcript (type 1; 10 tumors),
    # involved fusion of EWS exon 12 with CHN exon 3, and the second most common (type 5; two
    # cases) was fusion of EWS exon 13 with CHN exon 3."  Tiering it
    # `partner_published_this_exon_not_reported` asserted the opposite of the source, and because
    # the tier drives which junctions the manuscript is willing to name a reagent at, the miss cost
    # real coverage: this junction is 2 of 15 EWSR1 tumours, or 10.6 percentage points of
    # molecularly confirmed EMC, and its best design already existed and already cleared the
    # screens. See research/manuscripts/aso_coverage_ladder.py for what the correction buys.
    # ⚠ THE OPEN-ACCESS PMC2395470 IS THE SAME SERIES, NOT A SECOND ONE. It is the CTOS 2001
    # abstract supplement (PMID 18521326, Sarcoma 2001;5(Suppl 1)), whose abstract 035 is this same
    # 18-case Panagopoulos series restated — "followed by fusion of exon 13 of EWS with exon 3 of
    # CHN (two cases; type 5)". Retrievable as full text where PMID 12378528 is not, which is why
    # the census carries it; counting it as independent support would double-count two patients.
    # The independent confirmation is PMID 29937513, sample #4 of five.
    "EWSR1_e13__NR4A3_e3": ["PMID: 12378528", "PMID: 29937513"],
    # primary report of the variant fusion, and all three TAF15-rearranged tumours of that series
    "TAF15_e6__NR4A3_e3": ["PMID: 10537274", "PMID: 12378528"],
    # ⭐ ADDED 2026-08-15, AND IT WAS A RETRIEVAL GAP RATHER THAN A CURATION MISS. This junction sat
    # at `no_published_exon_resolved_breakpoint` because the primary report describes its chimera by
    # RESIDUE COUNT — "the first 108 amino acids" of TCF12 — and names no exon, so this repository's
    # exon-5 assignment was a conversion against its own transcript model. The same authors also
    # DEPOSITED the chimeric cDNA: GenBank AF289510.1, 421 bp, whose two chromosome-tagged source
    # features split the record AT the junction (1..263 chr15/TCF12, 264..421 chr9/NR4A3). That
    # resolves the breakpoint to the NUCLEOTIDE, and the deposited seam is identical, base for base,
    # to the seam this panel already designed on.
    # ⚠ NO LITERATURE SWEEP OF ANY WIDTH WOULD HAVE FOUND IT — 295 + 104 retrieved papers did not,
    # because the breakpoint was never published as an exon in prose; it was deposited. NCBI `elink`
    # from the report's PubMed record to `nuccore` returns it in one call. Every test:
    # research/manuscripts/tcf12_breakpoint_assignment.py.
    "TCF12_e5__NR4A3_e3": ["PMID: 11156374", "GenBank: AF289510.1"],
}

#: partners for which SOME exon-resolved EMC breakpoint is published, so "unreported exon" at that
#: partner is a weaker statement than at a partner with none. ⭐ TCF12 joined 2026-08-15 on the
#: strength of AF289510.1, which also moves its other seven junctions from "unreported" to "this
#: exon not reported while another exon of this partner is" — a stronger negative, and the right one.
PARTNERS_WITH_ANY_PUBLISHED_EXON = {"EWSR1", "TAF15", "TCF12"}


def _published_noncanonical_tiers():
    """`{label: [refs]}` for the published breakpoints the manuscript's PANEL cannot express.

    ⛔ DERIVED FROM THE WHITELIST, NEVER RE-TYPED HERE. `junction_aso`'s published-breakpoint
    whitelist is the curated list of seams a report places in a patient at exon resolution — the
    same object that gates whether the design and screen lane may build them at all. Those seams are
    excluded from the panel by a PROTEIN-level filter, not by an absence of clinical evidence, so
    scoring them `partner_published_this_exon_not_reported` would state the opposite of three
    published sources. ⚠ NEITHER whitelisted junction is in the 38-junction panel (measured
    2026-08-15: the panel holds EWSR1 e1/e4/e7/e9/e10/e12/e13/e15 :: NR4A3 e3 and no exon-2
    acceptor), so this changes no row of the committed table; it is here for the tables built over
    the non-canonical lane, which share this grader rather than forking a second one.
    """
    try:
        import junction_aso as _ja                                   # noqa: PLC0415
        wl = _ja.published_noncoding_acceptor_junctions()
    except Exception:                                                # noqa: BLE001
        return {}
    out = {}
    for (d_sym, d_end, a_sym, a_start), meta in wl.items():
        refs = [e.split("—")[0].strip() for e in meta.get("evidence") or [] if "PMID" in e]
        out[f"{d_sym}_e{d_end}__{a_sym}_e{a_start}"] = sorted({r for r in refs if r})
    return out


def _clinical_tier(label):
    """Three tiers, reported separately from specificity. See PUBLISHED_BREAKPOINTS."""
    if label in PUBLISHED_BREAKPOINTS:
        return "published_exon_resolved_breakpoint", PUBLISHED_BREAKPOINTS[label]
    noncanonical = _published_noncanonical_tiers()
    if label in noncanonical:
        return "published_exon_resolved_breakpoint", noncanonical[label]
    partner = str(label).split("_")[0]
    if partner in PARTNERS_WITH_ANY_PUBLISHED_EXON:
        # the partner is established and other exons of it are resolved, so this exon is contradicted
        # by the resolved ones rather than merely unobserved
        return "partner_published_this_exon_not_reported", []
    return "no_published_exon_resolved_breakpoint", []


def _deep_screens(root=None):
    """Every deep re-screen as (junction, design) PAIRS, with gap-paired hits recounted to loci.

    ⭐ `root` IS A PARAMETER AS OF 2026-08-15, AND IT DEFAULTS TO THIS DIRECTORY SO THE PANEL TABLE
    IS UNMOVED. The published NON-CANONICAL seams (`aso_noncoding_acceptor_screened_table`) are
    screened into their own directory precisely so they cannot be globbed into the panel's
    population, and they must be counted by THIS function rather than by a second copy of it — the
    whole value of putting an excluded junction beside the panel's is that the two numbers were
    produced by one grader.

    ⛔ NOT KEYED BY DESIGN. Nine designs span the seam of more than one junction exactly — that is
    §3.2's whole cross-partner-coverage result — so one sequence legitimately belongs to three
    junctions at once. Keying a dict by the sequence silently kept only the last screen read, and
    dropped `EWSR1_e12__NR4A3_e3` and `FUS_e10__NR4A3_e3` from the table entirely: 36 junctions
    where the panel has 38, with the MOST COMMONLY REPORTED patient junction among the missing.
    A per-junction table that loses the clinically-central junction to a dict collision is worse
    than no table, so the pairs are emitted flat and grouped by the caller.

    ⛔ ONE GEOMETRY, AND THE GUARD THAT USED TO SAY SO HERE IS NOW REDUNDANT (2026-08-14). The
    gap-length screens write 18-mer 5-8-5 and 20-mer 5-10-5 artifacts under the same glob this
    function used. Two things go wrong if they are let in, and the second is not a pooling complaint
    but a wrong number: the gap span applied below was `ja.GAP_REGION_1BASED`, which is 5-6-5's
    (6, 11), so an 18-mer's gap-paired hits were counted over six of its eight catalytic bases.
    Measured on merge: admitting them took the six re-screened junctions from 5 designs to 21 and
    moved `best_available` at the EWSR1 e12, FUS e10 and TAF15 e11 seams — the three clinically
    central rows — off the 16-mer this paper reports and onto an 18-mer scored against the wrong gap.

    ⭐ WHAT REPLACED THE GUARD, AND WHY THAT IS DIFFERENT IN KIND. The guard was a length check and
    a gap-region assertion written HERE, protecting THIS call site; six other modules had the same
    defect and three of them still did when this was written. Both of its checks survive — in
    `aso_screen_sets`, once, for every consumer — and the third thing it did, `continue` on a wrong
    length, is now unrepresentable: `load_screens` cannot return two geometries and this function is
    never handed a screen whose geometry was not measured. The gap window below comes from the
    SCREEN's own geometry rather than from a module constant, so the two can no longer be different
    things wearing the same name.
    ⚠ WHAT IS NOT THE LOADER'S JOB AND STAYS HERE: the truncation check. That is a property of a hit
    list, not of a geometry, and it is what stops a lower bound being reported as a measurement.
    """
    pairs = []
    for screen in ass.load_screens(GEOMETRY, ass.BLAST_SCREEN, root=(root or HERE),
                                   select=ass.is_deep):
        d = screen.artifact
        label = d.get("junction_label")
        lo, hi = screen.geometry.gap_region_1based
        for o in d.get("oligos", []):
            if o.get("status") != "screened":
                continue
            hits = o.get("offtargets") or []
            # ⛔ a truncated list would make every count below a lower bound wearing the costume of
            # a measurement — the exact defect that produced the withdrawn "nine clean designs".
            if o.get("n_offtarget_near_matches") != len(hits):
                raise SystemExit(
                    f"{screen.name}: {o['antisense_5to3']} stores {len(hits)} hits but "
                    f"reports {o.get('n_offtarget_near_matches')}; the deep screens must retain all")
            plus = [h for h in hits if not h.get("is_minus_strand")]
            paired = [h for h in plus
                      if h["q_from"] <= lo and h["q_to"] >= hi and h.get("gap_mismatches") == 0]
            loci = Counter(C.locus_of(h) for h in paired)
            pairs.append((label, o["antisense_5to3"], {
                "n_near_matches": len(hits),
                "n_hybridisable": len(plus),
                "n_gap_paired": len(paired),
                "n_gap_paired_loci": len(loci),
                "gap_paired_loci": sorted(loci),
            }))
    return pairs


def _load(name, key="per_design", root=None):
    path = os.path.join(root or HERE, name)
    if not os.path.exists(path):
        return {}
    return {r["antisense_5to3"]: r for r in json.load(open(path, encoding="utf-8"))[key]}


def junction_rows(deep, parent, premrna, genome):
    """The per-junction rows and their ranking — ONE grader, shared by every table in this lane.

    ⛔ EXTRACTED 2026-08-15 SO THE PUBLISHED NON-CANONICAL SEAMS ARE SCORED BY THIS CODE AND NOT BY
    A COPY OF IT. The whole point of screening an excluded junction to the panel's depth is to make
    its numbers comparable with the panel's; two functions computing "the same" fields is exactly
    how that comparability quietly stops being true — a field added here and not there, a tie-break
    changed on one side. `build()` below is unchanged in behaviour and simply calls this.
    """
    by_junction = defaultdict(list)
    seen = set()
    for label, seq, dp in deep:
        # the same (junction, design) can appear in more than one batch file; keep it once
        if (label, seq) in seen:
            continue
        seen.add((label, seq))
        pa, pm, gn = parent.get(seq, {}), premrna.get(seq, {}), genome.get(seq, {})
        oe = gn.get("observed_over_expected") or {}
        row = {
            "antisense_5to3": seq,
            "gap_specificity_margin": pa.get("gap_specificity_margin"),
            # screen 2: transcriptome at ten times the default ceiling
            "n_gap_paired": dp["n_gap_paired"],
            "n_gap_paired_loci": dp["n_gap_paired_loci"],
            "gap_paired_loci": dp["gap_paired_loci"],
            "n_hybridisable": dp["n_hybridisable"],
            "n_near_matches": dp["n_near_matches"],
            # screen 4: mature parent transcript, the liability no transcriptome screen reaches
            "parent": pa.get("parent"),
            "parent_duplex_bp": pa.get("longest_parent_duplex_bp_through_gap"),
            "parent_is_liability": pa.get("counts_as_liability"),
            # screen 3: unspliced pre-mRNA, since RNase-H1 is nuclear
            "premrna_gap_paired_hybridisable": pm.get("n_hybridisable_gap_fully_paired"),
            # screen 5: exhaustive GRCh38
            "genome_oe_gap_paired_le2": oe.get("gap_paired_le2"),
            "genome_named_target_sites": gn.get("n_named_target_sites"),
            "genome_named_target_genes": gn.get("named_target_genes"),
        }
        by_junction[label].append(row)

    junctions = []
    for label in sorted(by_junction, key=str):
        rows = by_junction[label]
        # ⛔ RANK, DO NOT SCORE, AND BREAK TIES ON MARGIN RATHER THAN ON RAW HITS. Parent liability
        # is disqualifying because sparing the wild-type parents is the modality's reason to exist;
        # then pre-mRNA; then LOCI, which §3.7 establishes is the honest breadth denominator.
        #
        # ⚠ WHEN LOCI TIE, THE TIE-BREAK IS MARGIN — NOT the hit count. Ranking equal-breadth
        # designs by raw hits reintroduces exactly the inflation the locus recount exists to remove,
        # and it produced a wrong answer at the junction that matters most: at EWSR1 e12 the two
        # leading registers BOTH touch 6 loci, but `GCATATCATCAAACCA` shows 34 hits against
        # `GGGCATATCATCAAAC`'s 123, so a hit-count tie-break promoted the margin-1 design over the
        # margin-3 one and made the manuscript's long-standing pick look superseded. It is not:
        # equal breadth, better fusion-versus-parent discrimination. Raw hits stay as the last key,
        # where they can only order designs that already tie on both real measures.
        rows.sort(key=lambda r: (bool(r["parent_is_liability"]),
                                 r["premrna_gap_paired_hybridisable"] or 0,
                                 r["n_gap_paired_loci"],
                                 -(r["gap_specificity_margin"] or 0),
                                 r["n_gap_paired"]))
        tier, refs = _clinical_tier(label)
        eligible = [r for r in rows if not r["parent_is_liability"]]
        junctions.append({
            "junction_label": label,
            "clinical_tier": tier,
            "breakpoint_refs": refs,
            "n_designs_screened": len(rows),
            "n_designs_clearing_the_parent_screen": len(eligible),
            "best_available": eligible[0] if eligible else None,
            "best_by_gap_specificity_margin": max(
                rows, key=lambda r: (r["gap_specificity_margin"] or -1))["antisense_5to3"],
            "designs": rows,
        })
    return junctions


def build():
    deep = _deep_screens()
    parent = _load("aso-parent-gap-pairing.json")
    premrna = _load("aso-premrna-offtarget.json")
    genome = _load("aso-genome-offtarget.json")
    junctions = junction_rows(deep, parent, premrna, genome)

    return {
        "what": ("The best available junction-spanning gapmer for EACH of the frame-compatible "
                 "NR4A3-fusion junctions, joined across all five specificity screens, with the "
                 "clinical-occurrence tier of the junction reported separately from specificity."),
        "⚠_not_a_measurement": ("Nothing here was re-screened. Every field is joined from an "
                                "artifact that already existed; no hit was re-aligned or re-graded, "
                                "and no number is converted into a predicted cleavage event."),
        "⛔_two_axes_not_one": ("gap_specificity_margin (fusion-versus-parent discrimination) and "
                               "the transcriptome load move in opposite directions at some seams "
                               "and are never combined into a single score. Ranking is by load "
                               "among designs clearing the parent screen; margin is printed beside."),
        "⚠_absence_of_evidence": ("A junction with no published exon-resolved breakpoint is "
                                  "UNREPORTED, not shown absent: EMC case reports usually name the "
                                  "partner gene without sequencing to nucleotide resolution. That "
                                  "is a weaker statement than a contradiction, and the tiers keep "
                                  "them apart."),
        "n_junctions": len(junctions),
        "junctions": junctions,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild from committed inputs and fail if the artifact is stale")
    args = ap.parse_args(argv)
    out = build()
    if args.check:
        if not os.path.exists(OUT):
            print(f"per-junction table --check: MISSING {OUT}")
            return 1
        if json.load(open(OUT, encoding="utf-8")) != out:
            print("per-junction table --check: STALE — re-run aso_per_junction_table.py")
            return 1
        print(f"per-junction table --check: OK ({out['n_junctions']} junctions)")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"wrote {OUT}  ({out['n_junctions']} junctions)")
    for j in out["junctions"]:
        b = j["best_available"]
        tier = {"published_exon_resolved_breakpoint": "PUBLISHED",
                "partner_published_this_exon_not_reported": "exon-unreported",
                "no_published_exon_resolved_breakpoint": "unreported"}[j["clinical_tier"]]
        if b is None:
            print(f"  {j['junction_label']:<24}{tier:<17}  no design clears the parent screen")
            continue
        print(f"  {j['junction_label']:<24}{tier:<17}{b['antisense_5to3']:<19}"
              f"margin={str(b['gap_specificity_margin']):<3}"
              f"loci={b['n_gap_paired_loci']:<3}hits={b['n_gap_paired']:<4}"
              f"parent={str(b['parent_duplex_bp']):<3}bp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
