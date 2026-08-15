#!/usr/bin/env python3
"""Where are the junction gapmer's off-target loci EXPRESSED — in the dosed organs, and on site?

⛔ WHY THIS EXISTS, AND WHY IT IS A SEPARATE QUESTION FROM EVERY SCREEN THAT PRECEDED IT.
Five screens stand behind this panel and all five ask the same kind of question: does a SEQUENCE
somewhere in the transcriptome resemble this oligonucleotide closely enough to hybridise. None of
them asks the question that decides whether such a resemblance can matter in a patient, which is
whether the transcript carrying it is PRESENT in a tissue the drug reaches. A perfect match in a
transcript no dosed organ expresses is a different object from a weak match in one the liver runs
at hundreds of TPM, and a screen that reports both as "a near-match" cannot tell them apart.

⭐ THE COMPARTMENT SPLIT IS THE WHOLE POINT, AND COLLAPSING IT WOULD DESTROY THE ANSWER.
Systemically dosed phosphorothioate gapmers distribute predominantly to liver and kidney, so those
two organs carry the EXPOSURE question — what the drug will sit in at concentration. The tumour
compartment (deep soft tissue of the extremities, myxoid stroma) carries a different question
entirely — what is present where the intended target is. A gene can be high in a dosed organ and
absent on site, or the reverse. The two are held in separate blocks of this artifact for
that reason and are never summed, never averaged, and never reduced to one score.

⛔ THIS FILE REPORTS EXPRESSION PER GENE. IT DOES NOT JOIN IT TO THE OLIGONUCLEOTIDE, AND THE
DISTINCTION IS NOT PEDANTRY. A locus is in this panel because a 16-mer matched it at 14/16 — a
sequence match at two mismatches, which is not a predicted cleavage event. So a median TPM here is
evidence about the GENE, not about the reagent, and the step from "this gene is expressed in liver"
to "this reagent does something in liver" needs an affinity argument no screen in this repository
has made. That joining is the manuscript's to do, explicitly, with the missing step named. ⛔ AND
THERE IS NO RISK COLUMN ANYWHERE IN THIS FILE, deliberately: the word would import exactly that
inference. Loci are ordered by transcript-record count — an annotation property, stated as one —
and never by anything that could be read as a hazard ranking.

WHAT THIS IS NOT — and each line is a claim this artifact must never be read as making:
  · NOT a cleavage prediction. Every hit behind this file sits at 14/16 identity: TWO mismatches in
    a 16-mer, the loosest thing the screen admits. Whether such a duplex is a substrate at all is an
    AFFINITY question, and no screen here and no expression value anywhere can answer it. Expression
    is a NECESSARY condition for an off-target effect, never a sufficient one.
  · NOT a safety, efficacy, therapeutic-window or clinical-readiness statement about any sequence.
    A gene turning out to be unexpressed in liver does not make an oligonucleotide safe; it says
    that one gene is unexpressed in liver, which is a fact about the gene.
  · NOT a risk ranking by record count. ANKS1B and ZNF667 carry most of the transcript records
    between them, and that is ANNOTATION DEPTH — how many variants RefSeq happens to list — not
    expression, not affinity and not risk. The record count is carried here only so a reader can see
    that it does NOT track the expression answer.
  · NOT a reading of absence. A locus with no row in a reference matrix is `readable: false` with the
    reason stated. It is NEVER rendered as "not expressed" (CLAUDE.md §4).

METHOD. The locus set is DERIVED from the committed deep screen rather than typed: the reagent's
hits are filtered to the screen's own `true_cleavage_risk` class and recounted per gene. Expression
is then read from three independent arms, each of which records its own failure separately:
  A · GTEx v8 median gene TPM across all tissues — the exposure arm. Liver and kidney are read from
      the same matrix as every other tissue, so the comparison is within one instrument.
  B · The two readable EMC array series — the on-site arm, via `emc_expression_panels._read_target`,
      so this cannot disagree with the panels lane about what a probe mapping is.
  C · NCBI Gene identity for all six loci — the arm that says what the uncharacterised `LOC` entries
      actually are, so their absence from arm A can be attributed rather than guessed.
"""
from __future__ import annotations

import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.join(HERE, "junction-aso-offtarget-e12n3-deep500-b1.json")
OUT = os.path.join(HERE, "aso-offtarget-tissue-expression.json")
INPUTS = os.path.join(HERE, "aso-offtarget-tissue-expression-inputs.json")

sys.path.insert(0, HERE)

#: The one clinically-relevant reagent in the panel: the 16-mer 5-6-5 LNA/DNA/LNA gapmer spanning
#: the EWSR1 exon 12 / TAF15 exon 11 / FUS exon 10 seam joined to NR4A3 exon 3.
REAGENT = "GGGCATATCATCAAAC"

#: ⭐ THE PANEL IS EVERY SEAM CARRYING A PUBLISHED EXON-RESOLVED BREAKPOINT, AND THAT IS THE WHOLE
#: MEMBERSHIP RULE. Expression is the exposure half of a liability assessment, so it is owed to the
#: junctions patients are reported to carry and to no others.
#:   · The multi-partner lead covers EWSR1 exon 12 / TAF15 exon 11 / FUS exon 10. Its EWSR1 arm is
#:     the most commonly reported junction, but its TAF15 arm is exon 11 — and the only
#:     exon-resolved TAF15::NR4A3 breakpoints published in EMC are exon 6 (PMID 10537274,
#:     PMID 12378528). So the lead cannot engage the TAF15 junction patients actually carry.
#:   · The TAF15 exon 6 seam is that junction. Its designs are therefore the second real reagent in
#:     the paper and their off-target expression matters on the same footing as the lead's.
#:   · EWSR1 exon 13 is the third, and it was MISSING FOR A CURATION REASON RATHER THAN A SCIENTIFIC
#:     ONE (added 2026-08-15). Membership is gated on `junction_is_reported_in_patients`, and
#:     `aso_per_junction_table.PUBLISHED_BREAKPOINTS` tiered this seam
#:     `partner_published_this_exon_not_reported` until the same abstract it already cited for
#:     exon 12 was read to the end: PMID 12378528 names exon 13 as the SECOND-most-common EWS/CHN
#:     transcript (type 5, two of its fifteen EWSR1-rearranged tumours), PMID 29937513 resolves it
#:     independently in sample #4 of five by whole-transcriptome sequencing, and PMID 32612944
#:     targets it in a clinical qRT-PCR panel. So the gate was working and its INPUT was wrong, and
#:     the seam was excluded by the very error that was corrected — which is why this entry exists
#:     and why nothing about the method changed to admit it.
#: ⛔ `designs: None` MEANS EVERY SCREENED DESIGN AT THAT SEAM, NOT A CHOSEN ONE. No single design
#: at the exon 6 or exon 13 seams has been selected by the paper, and picking one here would smuggle
#: a recommendation into a measurement — `aso-per-junction-table.json` ranks designs, and a ranking
#: is not a reagent. The union across registers is what the panel has to cover.
PANEL = [
    {"seam": "EWSR1_e12__NR4A3_e3",
     "screen": "junction-aso-offtarget-e12n3-deep500-b1.json",
     "designs": [REAGENT],
     "role": "lead — the multi-partner reagent (EWSR1 e12 / TAF15 e11 / FUS e10)",
     "junction_is_reported_in_patients": True,
     "note": ("The identical 123-hit / 6-locus load is returned independently by the TAF15 e11 and "
              "FUS e10 screens of the same molecule, under three different BLAST request ids and "
              "three different parent-exclusion sets — so the load is a property of the sequence, "
              "not of one screen.")},
    {"seam": "TAF15_e6__NR4A3_e3",
     "screen": "junction-aso-offtarget-taf15e6n3-deep500-b1.json",
     "designs": None,
     "role": "the only exon-resolved TAF15::NR4A3 breakpoint published in EMC",
     "junction_is_reported_in_patients": True,
     "note": ("Cited at PMID 10537274 (the primary report of the variant fusion) and PMID 12378528 "
              "(all three TAF15-rearranged tumours of an 18-case series). The lead reagent shares a "
              "single donor base with this seam and cannot engage it.")},
    {"seam": "EWSR1_e13__NR4A3_e3",
     "screen": "junction-aso-offtarget-e13n3-deep500-b1.json",
     "designs": None,
     "role": "the second-most-common EWSR1::NR4A3 transcript reported in EMC (type 5)",
     "junction_is_reported_in_patients": True,
     "note": ("Two independent patient series and one clinical assay. PMID 12378528: 'the second "
              "most common (type 5; two cases) was fusion of EWS exon 13 with CHN exon 3' — two of "
              "the fifteen EWSR1-rearranged tumours of the same 18-case series that supplies the "
              "exon 12 count, restated in the open-access CTOS 2001 supplement PMC2395470 "
              "(PMID 18521326), which is that series again and NOT a second cohort. PMID 29937513 "
              "IS a second cohort: 'exon13/exon3 and exon7/exon2 were detected respectively in "
              "samples #4 and #1' of five, by whole-transcriptome sequencing. PMID 32612944 builds "
              "a qRT-PCR panel around EWSR1(ex13)/NR4A3(ex3) among four junctions. The lead reagent "
              "shares no register with this seam and cannot engage it.")},
    # ⭐ ADDED 2026-08-15, AND THE ENTRY CRITERION IS WHY IT WAS ABSENT RATHER THAN AN OVERSIGHT.
    # This panel is every seam carrying a PUBLISHED EXON-RESOLVED BREAKPOINT, and TCF12 e5 did not
    # carry one: the primary report describes its chimera by residue count and names no exon, so the
    # assignment was a conversion against this repository's own transcript model. The authors' own
    # deposit — GenBank AF289510.1, whose two chromosome-tagged source features split the record AT
    # the junction — resolves it to the nucleotide, on the same seam this panel's screens already
    # ran. Derivation: research/manuscripts/tcf12_breakpoint_assignment.py.
    # ⛔ SO THE GATE WAS WORKING AND ITS INPUT WAS WRONG, exactly as it was for the exon-13 seam
    # above, and nothing about the criterion changed to admit this one.
    # ⚠ AND THIS IS THE SEAM WHERE A PER-GENE EXPRESSION READING IS MOST INFORMATIVE, because its
    # disclosed load is CONCENTRATED rather than broad: the other screens spread their gap-paired
    # hits over several loci, and this one puts all of them on a single curated gene. ⛔ WHICH IS
    # NOT A STATEMENT THAT THE SEAM IS RISKIER — this file carries no risk column, deliberately, and
    # a locus is in it because a 16-mer matched at 14/16, which is not a predicted cleavage event.
    {"seam": "TCF12_e5__NR4A3_e3",
     "screen": "junction-aso-offtarget-tcf12e5n3-deep500-b1.json",
     "designs": None,
     "role": "the only exon-resolved TCF12::NR4A3 breakpoint published in EMC",
     "junction_is_reported_in_patients": True,
     "note": ("Reported at NUCLEOTIDE resolution rather than as an exon, which is why no literature "
              "sweep found it: GenBank AF289510.1 (421 bp, 'Homo sapiens TCF12-TEC fusion protein "
              "mRNA, partial cds', submitted 25-JUL-2000, citing PMID 11156374) splits 1..263 on "
              "chromosome 15 (15q21) and 264..421 on chromosome 9 (9q22). Mapped against the "
              "committed transcript models the donor side ends at TCF12 exon 5 and no other exon, "
              "the acceptor side begins at NR4A3 exon 3 and no other exon, and the seam is identical "
              "to the one the screens ran on. Corroborated independently by PMID 12826747, a TCF12 "
              "gene-structure paper reporting 21 exons — the same count as the committed model — "
              "and that 'intron 5 in the TCF12 gene corresponds to the region involved in a "
              "translocation, t(9;15)(q22;q21)'. ⚠ ONE TUMOUR: neither breakpoint series behind the "
              "coverage ladder contains a TCF12-rearranged tumour, so this seam has a resolved "
              "junction and no within-partner distribution.")},
]

#: ⭐ THE EXPOSURE TISSUES, and this list is the reason the artifact exists rather than a detail.
#: Named as GTEx v8 `SMTSD` tissue labels exactly, because a label that does not match a column
#: silently reads as "no data" — which is the fail-quiet direction. `_tissue_block` asserts that
#: every one of these resolved to a real column and records any that did not.
EXPOSURE_TISSUES = ["Liver", "Kidney - Cortex", "Kidney - Medulla"]

#: ⚠ PROXIES, AND THE ARTIFACT MUST SAY SO EVERY TIME IT PRINTS THEM. GTEx contains no
#: extraskeletal myxoid chondrosarcoma, no sarcoma of any kind and no myxoid stroma. These are the
#: normal tissues of the anatomical compartment EMC arises in — deep soft tissue of the extremities
#: — and they bound what a normal cell of that region expresses. They are NOT a tumour reading; the
#: tumour reading is arm B, in six and ten archival tumours, and the two are reported apart.
TUMOUR_COMPARTMENT_PROXY_TISSUES = [
    "Muscle - Skeletal",
    "Adipose - Subcutaneous",
    "Nerve - Tibial",
    "Cells - Cultured fibroblasts",
    "Artery - Tibial",
    "Skin - Sun Exposed (Lower leg)",
]

#: ⛔ KNOWN-ANSWER CONTROLS, AND THEY ARE NOT DECORATION. A GCT is a wide tab matrix; a column
#: off-by-one produces a completely plausible artifact in which every gene's tissue profile is
#: shifted by one tissue, and nothing about the numbers looks wrong. These three genes have
#: textbook tissue restriction, so `_control_verdict` can assert that the matrix's own maximum for
#: each falls where it must. A run whose controls fail must not be allowed to emit a locus verdict.
#: (`ALB` -> Liver, `UMOD` -> a kidney tissue, `MYH7` -> a muscle/heart tissue.)
GTEX_CONTROLS = {
    "ALB": {"expect_max_in": ["Liver"],
            "why": "albumin is the canonical hepatocyte-restricted transcript"},
    "UMOD": {"expect_max_in": ["Kidney - Medulla", "Kidney - Cortex"],
             "why": "uromodulin is made only by the thick ascending limb of the nephron"},
    "MYH7": {"expect_max_in": ["Muscle - Skeletal", "Heart - Left Ventricle"],
             "why": "beta-myosin heavy chain is restricted to slow skeletal muscle and ventricle"},
}

#: The GTEx v8 gene-level median TPM matrix, the published release file. A flat matrix is used in
#: preference to the portal's per-gene API on purpose: it is one request whose parse either works or
#: throws, rather than 6 requests against a schema that has moved between versions, and it is the
#: same object a reader can download to check this artifact.
#:
#: ⛔ A LIST, TRIED IN ORDER, WITH THE WINNER RECORDED — NOT A GUESS RE-TYPED (measured 2026-08-13,
#: run 31747675357). The `gtex_analysis_v8/rna_seq_data/` path returned **HTTP 404** and took the
#: whole exposure arm down with it; GTEx reorganised its public bucket under `adult-gtex/`. Editing
#: one constant to another remembered path would have been the same bet placed twice, so this
#: follows the pattern `s_calibrator_survey.GENE_ATTRS` already uses for RCSB's moving schema: try
#: each candidate, record which one the server actually accepted (`endpoint_used`), and record what
#: every other one said (`url_attempts`). A future move then shows up as a recorded 404 next to a
#: recorded success rather than as a silent empty arm.
#: ⚠ The failure was NOT silent even so — every locus read `NOT_MEASURED` with the 404 quoted, and
#: the known-answer controls refused to run. That is the guard working; it is still an arm down.
GTEX_MEDIAN_TPM_URLS = [
    ("https://storage.googleapis.com/adult-gtex/bulk-gex/v8/rna-seq/"
     "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz"),
    ("https://storage.googleapis.com/gtex_analysis_v8/rna_seq_data/"
     "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz"),
]
#: Kept as the nominal citation target: the release object these paths serve.
GTEX_MEDIAN_TPM_URL = GTEX_MEDIAN_TPM_URLS[0]

#: ⚠ FALLBACK ONLY, and it answers a DIFFERENT shape of question, so a run that used it says so.
#: Recorded rather than silently substituted (`arm_a.endpoint_used`).
GTEX_API_MEDIAN = "https://gtexportal.org/api/v2/expression/medianGeneExpression"
GTEX_API_GENE = "https://gtexportal.org/api/v2/reference/gene"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
HPA_SEARCH = "https://www.proteinatlas.org/api/search_download.php"

UA = {"User-Agent": "rare-cancers-aso-offtarget-expression/1.0"}

#: A median TPM at or above this is called `present` for the purpose of the readout below. ⚠ STATED,
#: NOT MEASURED, and deliberately not called a threshold of concern: it is the level at which a
#: transcript is conventionally taken to be detected at all in bulk RNA-seq, and it is applied only
#: to make the table legible. Every raw median is released so any other cut can be applied without
#: re-running this, and no verdict in this file changes across the range 0.5 to 2.
PRESENT_TPM = 1.0

#: The upper legibility cut, separating `LOW_IN_EXPOSURE_ORGANS` from
#: `EXPRESSED_IN_AN_EXPOSURE_ORGAN`. ⛔ THIS WAS A BARE `10` INSIDE `_tier` AND NOTHING ELSE COULD
#: POINT AT IT (2026-08-13). `PRESENT_TPM` one screen above it is a named constant carrying the
#: paragraph that says it is a STATED cut and not a threshold of concern; the upper cut does exactly
#: the same job, decides the tier the manuscript's Table 6 prints, and had no name, so a table
#: legend describing it would have had to re-type the number — rule 1's exact failure. Like
#: `PRESENT_TPM` it is a legibility cut and NOT a threshold of concern: it says where a median stops
#: being a low reading and starts being one an off-target hypothesis would have to be tested
#: against, and every raw median is released so another cut can be applied without re-running.
EXPRESSED_TPM = 10.0

#: The screen's own risk class for a hit whose catalytic gap is fully paired. Read from the screen
#: rather than re-derived, so this module cannot disagree with `junction_aso_offtarget` about what a
#: gap-paired hit is.
GAP_PAIRED_CLASS = "true_cleavage_risk"

_PAREN = re.compile(r"\(([^()]+)\)")


def _tkey(t):
    """Endpoint-independent tissue key: lower-cased, stripped of every non-alphanumeric.

    ⛔ WHY THIS EXISTS, MEASURED 2026-08-13 (run 31749264339). The release GCT labels tissues in
    GTEx's `SMTSD` form — `Kidney - Medulla`, `Heart - Left Ventricle`, `Skin - Sun Exposed (Lower
    leg)` — while the portal API returns `tissueSiteDetailId` — `Kidney_Medulla`,
    `Heart_Left_Ventricle`, `Skin_Sun_Exposed_Lower_leg`. The API fallback normalised underscores to
    spaces, which produces `Kidney Medulla` and matches NEITHER form.

    ⚠ THE CONSEQUENCE WAS A FALSE NEGATIVE ON THE SAFETY GATE, WHICH IS THE EXPENSIVE DIRECTION OF
    BEING RIGHT. The fetch was flawless — ALB peaked in Liver at 25,201 TPM, UMOD in Kidney Medulla
    at 2,116, MYH7 in Heart Left Ventricle at 4,514, exactly as they must — but two of three
    controls compared `Kidney Medulla` against `Kidney - Medulla`, failed on the punctuation, and
    the control gate correctly withheld EVERY locus verdict. A whole 26-minute run produced no
    exposure figure because of a hyphen.

    Matching on this key instead means the same tissue compares equal whichever endpoint answered,
    so a fallback run is graded by the same controls as a primary one rather than being failed by
    its own label vocabulary. It cannot merge two real tissues: no two GTEx tissue names differ only
    in punctuation, which `test_the_tissue_key_cannot_merge_two_real_gtex_tissues` asserts over the
    full 54-label list.
    """
    return re.sub(r"[^a-z0-9]", "", str(t).lower())


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The locus set — DERIVED from the committed screen, never typed
# ─────────────────────────────────────────────────────────────────────────────────────────────

def gene_of(entry):
    """The gene symbol a hit belongs to — `junction_aso_locus_collapse.locus_of`, unmodified.

    ⛔ THIS IS A DELIBERATE ONE-LINE DELEGATION AND IT REPLACED A SECOND PASS THAT WAS WRONG IN
    EXACTLY THE WAY THE SHARED PARSER USED TO BE (corrected 2026-08-13 against `5233cf867`).
    `locus_of` originally took the last parenthesised token BEFORE THE FIRST COMMA, which lost the
    symbol for every gene whose own description carries a comma — `"germ cell-less 1,
    spermatogenesis associated (GMCL1), mRNA"` split to a head with no parenthesis at all, so nine
    GMCL1 variants each fell back to their own accession and ONE locus was counted as NINE.

    ⚠ THE SECOND PASS THIS MODULE CARRIED TO WORK AROUND THAT TOOK THE **FIRST** PARENTHETICAL OF
    THE FULL DEFINITION, WHICH IS THE OTHER HALF OF THE SAME BUG. It resolved GMCL1 correctly and
    would have returned `N-ACETYL` for `"glucosaminyl (N-acetyl) transferase 3, mucin type
    (GCNT3), mRNA"` — a confident, plausible, wrong symbol, and the kind that never looks like an
    error downstream. Two independent parsers each right on the case that motivated them is not a
    cross-check; it is two ways to be wrong.

    The corrected shared parser takes the first parenthetical whose closing paren is followed by a
    comma or the end of the definition, which is NCBI's actual defline grammar
    (`<organism> <description> (<SYMBOL>), <tail>`) and handles both cases. There is now one parser
    and this module uses it, so a future correction lands in one place (CLAUDE.md §1).
    """
    from junction_aso_locus_collapse import locus_of  # noqa: E402  (the one home for this rule)
    return locus_of(entry)


def _screen_path(name):
    return name if os.path.isabs(name) else os.path.join(HERE, name)


def _screen_hits(path=SCREEN, reagent=REAGENT):
    """One design's gap-paired hits, straight out of the committed screen."""
    path = _screen_path(path)
    d = json.load(open(path, encoding="utf-8"))
    match = [o for o in d.get("oligos", []) if o.get("antisense_5to3") == reagent]
    if len(match) != 1:
        raise RuntimeError(f"{reagent}: expected exactly one record in {os.path.basename(path)}, "
                           f"found {len(match)}")
    o = match[0]
    hits = o.get("offtargets") or []
    # ⛔ THE CENSORING GUARD. `junction_aso_offtarget` stores `ranked[:15]` on a default-depth run
    # while reporting the FULL count separately, so a truncated list would silently under-report the
    # locus set. A locus census over a truncated list is a lower bound wearing the costume of a
    # count, and this module must refuse rather than emit one.
    if len(hits) != o.get("n_offtarget_near_matches"):
        raise RuntimeError(
            f"{reagent}: the stored hit list holds {len(hits)} of "
            f"{o.get('n_offtarget_near_matches')} reported near-matches — this screen is truncated "
            f"and a locus census over it would be a lower bound, not a count")
    return o, [h for h in hits if h.get("risk") == GAP_PAIRED_CLASS]


def _seam_rows(entry):
    """(locus rows, provenance) for ONE seam, over every design the panel entry names."""
    path = _screen_path(entry["screen"])
    d = json.load(open(path, encoding="utf-8"))
    designs = entry.get("designs")
    if designs is None:
        designs = [o["antisense_5to3"] for o in d.get("oligos", [])
                   if o.get("status") == "screened"]
    per, per_design = {}, []
    for seq in designs:
        oligo, gap_paired = _screen_hits(path, seq)
        seen_here = set()
        for h in gap_paired:
            sym = gene_of(h)
            seen_here.add(sym)
            row = per.setdefault(sym, {
                "locus": sym, "n_transcript_records": 0, "n_curated_records": 0,
                "n_predicted_records": 0, "accessions": [], "definition_example": None,
                "seams": set(), "designs_hitting_it": set()})
            row["n_transcript_records"] += 1
            row["seams"].add(entry["seam"])
            row["designs_hitting_it"].add(seq)
            acc = str(h.get("acc") or "")
            row["accessions"].append(acc)
            if acc.startswith(("NM_", "NR_")):
                row["n_curated_records"] += 1
            elif acc.startswith(("XM_", "XR_")):
                row["n_predicted_records"] += 1
            if row["definition_example"] is None:
                row["definition_example"] = h.get("defn")
        per_design.append({
            "antisense_5to3": seq,
            "gc_percent": oligo.get("gc_percent"),
            "specificity_margin": oligo.get("specificity_margin"),
            "blast_rid": oligo.get("blast_rid"),
            "n_near_matches_reported": oligo.get("n_offtarget_near_matches"),
            "n_minus_strand_not_hybridisable": oligo.get("n_minus_strand_not_hybridisable"),
            "n_gap_disrupted_no_cleavage": oligo.get("n_gap_disrupted_no_cleavage"),
            "n_gap_paired_hybridisable": len(gap_paired),
            "loci": sorted(seen_here),
        })
    prov = dict(entry)
    prov.pop("designs", None)
    prov.update({
        "screen": os.path.basename(path),
        "junction_label": d.get("junction_label"),
        "n_designs": len(designs),
        "designs": per_design,
        "n_gap_paired_hybridisable": sum(x["n_gap_paired_hybridisable"] for x in per_design),
        "risk_class_read": GAP_PAIRED_CLASS,
        "n_loci": len(per),
    })
    return per, prov


def _locus_rows(path=None, reagent=None, panel=None):
    """(oligo record or None, ordered locus rows, provenance) over the whole panel.

    ⭐ `n_designs_hitting_it` IS A SECOND AXIS AND IT IS NOT THE RECORD COUNT. A locus every design
    at a seam returns is robust to tiling register — it is there wherever you put the window — while
    a locus one register returns may be a property of that window. Record count measures neither;
    it measures how many transcript variants RefSeq lists. The two are reported side by side because
    ranking on either alone is a mistake this file must not invite.
    """
    if path is not None or reagent is not None:      # single-design call, kept for the tests
        panel = [{"seam": "ad-hoc", "screen": path or SCREEN,
                  "designs": [reagent or REAGENT], "role": "ad-hoc single-design call"}]
    panel = panel if panel is not None else PANEL

    merged, seams = {}, []
    for entry in panel:
        per, prov = _seam_rows(entry)
        seams.append(prov)
        for sym, row in per.items():
            tgt = merged.setdefault(sym, {
                "locus": sym, "n_transcript_records": 0, "n_curated_records": 0,
                "n_predicted_records": 0, "accessions": [], "definition_example": None,
                "seams": set(), "designs_hitting_it": set()})
            for k in ("n_transcript_records", "n_curated_records", "n_predicted_records"):
                tgt[k] += row[k]
            tgt["accessions"] += row["accessions"]
            tgt["seams"] |= row["seams"]
            tgt["designs_hitting_it"] |= row["designs_hitting_it"]
            if tgt["definition_example"] is None:
                tgt["definition_example"] = row["definition_example"]

    rows = sorted(merged.values(), key=lambda r: (-r["n_transcript_records"], r["locus"]))
    for r in rows:
        r["accessions"] = sorted(set(r["accessions"]))
        r["seams"] = sorted(r["seams"])
        r["n_designs_hitting_it"] = len(r["designs_hitting_it"])
        r["designs_hitting_it"] = sorted(r["designs_hitting_it"])
        r["identity_of_every_record"] = "14/16 (two mismatches), the loosest the screen admits"
    prov = {
        "panel": seams,
        "n_seams": len(seams),
        "n_loci_over_the_whole_panel": len(rows),
        "n_gap_paired_hybridisable": sum(s["n_gap_paired_hybridisable"] for s in seams),
        "risk_class_read": GAP_PAIRED_CLASS,
        "locus_parser": ("junction_aso_locus_collapse.locus_of, corrected 2026-08-13 (5233cf867) "
                         "to read NCBI's defline grammar rather than the text before the first "
                         "comma. This module delegates to it and carries no parser of its own."),
    }
    return None, rows, prov


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Fetch — every arm records its own failure, and no arm can fail into a biological statement
# ─────────────────────────────────────────────────────────────────────────────────────────────

def _get(url, timeout=600, headers=None):
    req = urllib.request.Request(url, headers=dict(UA, **(headers or {})))
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read()


#: ⛔ NCBI E-UTILITIES RATE LIMIT, MEASURED THE HARD WAY (run 31747675357). Two unthrottled calls
#: per gene took arm C from six genes to ONE: `ANKS1B` read, and the other five returned
#: **HTTP 429 Too Many Requests**. E-utilities allows ~3 requests/second without an API key, and
#: this module was issuing them back to back.
#: ⚠ THE DAMAGE WAS NOT A MISSING FIELD, IT WAS A MISSING DISTINCTION. Arm C is the arm that says
#: what the two `LOC` entries ARE, which is what lets their absence from GTEx be attributed to "no
#: GENCODE model for an uncharacterised NCBI-only locus" rather than left as an unexplained gap. A
#: throttled arm C therefore degrades a *reason* into a *silence*, which is the shape §4 is about.
_NCBI_MIN_INTERVAL_S = 0.4
_NCBI_MAX_RETRIES = 4


def _ncbi_get(url, timeout=120):
    """One E-utilities call, paced and retried on 429/5xx with backoff."""
    delay = _NCBI_MIN_INTERVAL_S
    last = None
    for attempt in range(_NCBI_MAX_RETRIES):
        time.sleep(delay)
        try:
            return _get(url, timeout=timeout)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            delay = min(delay * 3, 8.0)          # 0.4 -> 1.2 -> 3.6 -> 8.0
        except urllib.error.URLError as exc:
            last = exc
            delay = min(delay * 3, 8.0)
    raise last if last is not None else RuntimeError("unreachable")


def _parse_gct(raw_gz, wanted):
    """Rows of a GCT whose `Description` is in `wanted`, plus the tissue column order.

    ⛔ THE SHAPE IS ASSERTED, NOT ASSUMED. A GCT declares its own row and column counts on line 2,
    and a header that disagrees with them means the file is not what this parser thinks it is —
    which, on a wide tab matrix, produces a shifted-by-one artifact that looks entirely normal.
    """
    text = gzip.GzipFile(fileobj=io.BytesIO(raw_gz)).read().decode("utf-8", "replace")
    lines = text.split("\n")
    if not lines or not lines[0].startswith("#1.2"):
        raise RuntimeError(f"not a GCT: first line is {lines[0][:60]!r}")
    n_rows, n_cols = (int(x) for x in lines[1].split("\t")[:2])
    header = lines[2].split("\t")
    if header[0] != "Name" or header[1] != "Description":
        raise RuntimeError(f"unexpected GCT header: {header[:3]}")
    tissues = header[2:]
    if len(tissues) != n_cols:
        raise RuntimeError(f"GCT declares {n_cols} data columns, header carries {len(tissues)}")
    want = {w.upper() for w in wanted}
    found, seen = {}, 0
    for ln in lines[3:]:
        if not ln.strip():
            continue
        seen += 1
        parts = ln.split("\t")
        sym = parts[1].strip()
        if sym.upper() not in want:
            continue
        if len(parts) != n_cols + 2:
            raise RuntimeError(f"{sym}: row has {len(parts) - 2} values against {n_cols} columns")
        vals = []
        for p in parts[2:]:
            try:
                vals.append(float(p))
            except ValueError:
                vals.append(None)
        # A symbol can appear on more than one gene model; keep every row rather than the first.
        found.setdefault(sym.upper(), []).append({"gencode_id": parts[0], "symbol": sym,
                                                  "values": vals})
    if seen != n_rows:
        raise RuntimeError(f"GCT declares {n_rows} rows, parsed {seen}")
    return {"tissues": tissues, "n_rows": n_rows, "rows": found}


def _gtex_api_arm(want):
    """FALLBACK: the portal's per-gene median endpoint, used only if the release file is unreachable.

    ⚠ IT IS RECORDED, NEVER SILENTLY SUBSTITUTED (`endpoint_used`). The two paths differ in ways a
    reader must be able to see: the release file is one immutable published object, while the API
    resolves a symbol to a gencode id first and so can return a DIFFERENT gene model. A run that
    fell back is still a reading; it is just a reading of a slightly different thing, and an
    artifact that could not say which it used would make the two indistinguishable.
    """
    tissues, rows, errs = [], {}, {}
    for sym in want:
        try:
            q = urllib.parse.urlencode({"geneId": sym})
            g = json.loads(_get(f"{GTEX_API_GENE}?{q}", timeout=120).decode())
            recs = [r for r in (g.get("data") or [])
                    if str(r.get("geneSymbol", "")).upper() == sym.upper()]
            if not recs:
                errs[sym] = "no gencode id resolved for this symbol"
                continue
            gid = recs[0]["gencodeId"]
            q2 = urllib.parse.urlencode({"gencodeId": gid, "datasetId": "gtex_v8"})
            m = json.loads(_get(f"{GTEX_API_MEDIAN}?{q2}", timeout=180).decode())
            data = m.get("data") or []
            if not data:
                errs[sym] = f"no median expression rows for {gid}"
                continue
            for r in data:
                t = r.get("tissueSiteDetailId")
                if t and t not in tissues:
                    tissues.append(t)
            vals = {r.get("tissueSiteDetailId"): r.get("median") for r in data}
            rows.setdefault(sym.upper(), []).append(
                {"gencode_id": gid, "symbol": sym, "_by_tissue": vals})
        except Exception as exc:  # noqa: BLE001
            errs[sym] = f"{type(exc).__name__}: {str(exc)[:160]}"
    if not rows:
        return None, errs
    # ⚠ THE API RETURNS `tissueSiteDetailId` (underscored ids), NOT the release file's `SMTSD`
    # labels, so the tissue LISTS in this module would not match. Normalise to the release file's
    # label form; any tissue that does not normalise is left as-is and simply will not be selected,
    # which reads as `tissue_labels_not_found` rather than as a zero.
    norm = {t: t.replace("_", " ") for t in tissues}
    labels = [norm[t] for t in tissues]
    out = {}
    for sym, models in rows.items():
        out[sym] = [{"gencode_id": mo["gencode_id"], "symbol": mo["symbol"],
                     "values": [mo["_by_tissue"].get(t) for t in tissues]} for mo in models]
    return {"tissues": labels, "rows": out, "n_rows": None,
            "_tissue_id_to_label": norm, "_per_symbol_errors": errs}, errs


def fetch_gtex(symbols, controls=tuple(GTEX_CONTROLS)):
    rec = {"source": "GTEx v8 gene-level median TPM",
           "url": GTEX_MEDIAN_TPM_URL,
           "release": "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm",
           "unit": "median TPM across that tissue's donors",
           "endpoint_used": None}
    want = sorted(set(symbols) | set(controls))
    attempts = []
    for url in GTEX_MEDIAN_TPM_URLS:
        try:
            raw = _get(url, timeout=1800)
            rec["compressed_bytes"] = len(raw)
            rec.update(_parse_gct(raw, want))
            rec["url"] = url
            rec["endpoint_used"] = "release_gct"
            rec["url_attempts"] = attempts + [{"url": url, "result": "read"}]
            rec["_status"] = "read"
            return rec
        except Exception as exc:  # noqa: BLE001 — every refusal is recorded, none is silent
            attempts.append({"url": url, "result": f"{type(exc).__name__}: {str(exc)[:200]}"})
    rec["url_attempts"] = attempts
    rec["release_file_error"] = "; ".join(a["result"] for a in attempts)[:400]

    # ⛔ THE FALLBACK RUNS ONLY AFTER THE RELEASE FILE FAILED, and it carries the SAME controls
    # through the SAME control gate — a fallback exempt from the known-answer check would be a way
    # for a degraded path to emit figures the primary path could not.
    try:
        got, errs = _gtex_api_arm(want)
        if got is None:
            rec["_status"] = (f"fetch or parse failed: {rec['release_file_error']}; "
                              f"API fallback also returned nothing: {json.dumps(errs)[:300]}")
            return rec
        rec.update(got)
        rec["endpoint_used"] = "portal_api_v2_fallback"
        rec["url"] = GTEX_API_MEDIAN
        rec["_status"] = "read"
        rec["⚠_fallback"] = ("the release GCT was unreachable and the portal API answered instead; "
                             "the two can resolve a symbol to different gene models, so this is a "
                             "reading of a slightly different object and says so here.")
    except Exception as exc:  # noqa: BLE001
        rec["_status"] = (f"fetch or parse failed: {rec['release_file_error']}; "
                          f"API fallback raised {type(exc).__name__}: {str(exc)[:200]}")
    return rec


def fetch_ncbi_gene(symbols):
    """What each locus IS. The arm that lets an absence from GTEx be attributed rather than guessed.

    ⭐ THIS IS THE ARM THAT ANSWERS THE `LOC` QUESTION. An uncharacterised NCBI-only locus has no
    GENCODE gene model under that symbol, so it CANNOT appear in arm A — and without this arm, that
    absence is indistinguishable from a gene GTEx measured at zero. One is "no instrument covered
    it", the other is a reading; conflating them is exactly the failure CLAUDE.md §4 names.
    """
    out = {"source": "NCBI Gene (E-utilities esearch + esummary)", "genes": {}}
    for sym in sorted(symbols):
        g = {"query": sym}
        try:
            q = urllib.parse.urlencode({"db": "gene", "retmode": "json",
                                        "term": f"{sym}[Gene Name] AND human[ORGN]"})
            hits = json.loads(_ncbi_get(f"{EUTILS}/esearch.fcgi?{q}").decode())
            ids = hits.get("esearchresult", {}).get("idlist", [])
            g["gene_ids"] = ids
            if not ids:
                g["_status"] = "no NCBI Gene record matched this symbol"
                out["genes"][sym] = g
                continue
            q2 = urllib.parse.urlencode({"db": "gene", "retmode": "json", "id": ids[0]})
            summ = json.loads(_ncbi_get(f"{EUTILS}/esummary.fcgi?{q2}").decode())
            doc = summ.get("result", {}).get(ids[0], {})
            g["gene_id"] = ids[0]
            for k in ("name", "description", "chromosome", "maplocation", "genomicinfo",
                      "summary", "otheraliases", "status"):
                if k in doc:
                    g[k] = doc[k]
            g["_status"] = "read"
        except Exception as exc:  # noqa: BLE001
            g["_status"] = f"fetch failed: {type(exc).__name__}: {str(exc)[:200]}"
        out["genes"][sym] = g
    return out


def fetch_hpa(symbols):
    """Human Protein Atlas consensus tissue RNA — a cross-check on arm A, best effort.

    ⚠ NOT INDEPENDENT OF GTEx. HPA's consensus tissue data incorporates GTEx among its sources, so
    agreement between this arm and arm A is a transport check, not a second measurement. It is
    fetched because it carries tissue calls and protein-level evidence GTEx does not, and it is
    labelled here so no reader can take concordance as replication.
    """
    out = {"source": "Human Protein Atlas search_download API",
           "_not_independent_of_gtex": (
               "HPA consensus tissue RNA incorporates GTEx; agreement with arm A is a transport "
               "check, not an independent measurement."),
           "genes": {}}
    cols = "g,gs,eg,gd,rnatsm,rnatd,rnats,rnacas,scml"
    for sym in sorted(symbols):
        try:
            q = urllib.parse.urlencode({"search": sym, "format": "json", "columns": cols,
                                        "compress": "no"})
            body = _get(f"{HPA_SEARCH}?{q}", timeout=180).decode("utf-8", "replace")
            rows = json.loads(body)
            exact = [r for r in rows if str(r.get("Gene", "")).upper() == sym.upper()]
            rec = {"_status": "read", "n_rows": len(rows), "exact_symbol_rows": exact[:3]}
            # ⛔ THE SEARCH COLUMNS DO NOT ANSWER THE EXPOSURE QUESTION, MEASURED 2026-08-13.
            # `rnatsm` ("RNA tissue specific nTPM") returns ONLY the tissue a gene is enriched in —
            # ANKS1B came back `{"brain": "66.3"}` and CHST5 `{"intestine": "82.2"}`, with no liver
            # or kidney figure at all. That is a real and useful reading about the gene, and it is
            # NOT the reading this artifact's exposure block needs. So the per-gene record is
            # fetched too, where the full tissue vector lives.
            ens = (exact[0].get("Ensembl") if exact else None)
            rec["ensembl"] = ens
            if ens:
                try:
                    raw = _get(f"https://www.proteinatlas.org/{ens}.json", timeout=180)
                    rec["per_gene"] = _hpa_tissue_vector(json.loads(raw.decode("utf-8", "replace")))
                except Exception as exc:  # noqa: BLE001
                    rec["per_gene"] = {"_status": f"fetch failed: {type(exc).__name__}: "
                                                  f"{str(exc)[:200]}"}
            else:
                rec["per_gene"] = {"_status": "no Ensembl id in the HPA search row"}
            out["genes"][sym] = rec
        except Exception as exc:  # noqa: BLE001
            out["genes"][sym] = {"_status": f"fetch failed: {type(exc).__name__}: "
                                            f"{str(exc)[:200]}"}
    return out


#: HPA tissue labels for the two exposure organs, lower-cased. HPA uses `liver` and `kidney`
#: (it does not split cortex from medulla the way GTEx does), so the kidney figure here is a
#: WHOLE-ORGAN value and is not interchangeable with a GTEx cortex or medulla column.
_HPA_EXPOSURE_KEYS = ("liver", "kidney")


def _hpa_tissue_vector(doc):
    """Pull a {tissue: nTPM} mapping out of an HPA per-gene record, defensively.

    ⛔ WRITTEN TO SURVIVE A SCHEMA IT CANNOT BE TESTED AGAINST HERE. The sandbox 403s
    proteinatlas.org, so the exact key holding the consensus tissue vector cannot be confirmed
    offline. Rather than assume one, this walks the document for any dict whose keys look like
    tissue names and whose values are numeric, records WHICH key path it used, and records the
    candidate paths it rejected. A future schema move then shows up as `matched_path: null` beside
    the paths that were tried — a recorded miss rather than a silent empty column.
    """
    found = []

    def walk(node, path):
        if len(found) > 40 or len(path) > 8:
            return
        if isinstance(node, dict):
            numeric = {}
            for k, v in node.items():
                if isinstance(v, (int, float)):
                    numeric[str(k).lower()] = float(v)
                elif isinstance(v, str):
                    try:
                        numeric[str(k).lower()] = float(v)
                    except ValueError:
                        pass
            if len(numeric) >= 10 and any(t in numeric for t in _HPA_EXPOSURE_KEYS):
                found.append({"path": "/".join(path), "n_tissues": len(numeric),
                              "values": numeric})
            for k, v in node.items():
                walk(v, path + [str(k)])
        elif isinstance(node, list):
            for i, v in enumerate(node[:60]):
                walk(v, path + [str(i)])

    walk(doc, [])
    if not found:
        return {"_status": "no tissue vector found in the HPA record",
                "matched_path": None,
                "top_level_keys": sorted(doc.keys())[:40] if isinstance(doc, dict) else None}
    best = max(found, key=lambda f: f["n_tissues"])
    return {"_status": "read", "matched_path": best["path"], "n_tissues": best["n_tissues"],
            "values": best["values"],
            "other_candidate_paths": [f["path"] for f in found if f is not best][:6]}


def fetch_emc_series(symbols):
    """The on-site arm: the six loci read in the two readable EMC series.

    ⭐ IT REUSES `emc_expression_panels._read_target` RATHER THAN RE-IMPLEMENTING IT, and that is a
    correctness argument, not laziness. Probe-to-symbol mapping on these two platforms is the part
    that has actually been hard here — GPL3290 needs an accession bridge whose completeness is
    budget-bound — and a second implementation would be free to disagree with the panels lane about
    whether a gene is readable at all. One mapping, one answer.
    ⛔ It writes NOTHING that lane owns: `_read_target` is a pure read, and the output lands only in
    this module's own inputs cache.
    """
    out = {"source": "GEO series matrices, read through emc_expression_panels._read_target",
           "targets": {}}
    try:
        from emc_expression_panels import TARGETS, _read_target  # noqa: E402
    except Exception as exc:  # noqa: BLE001
        out["_status"] = f"import failed: {type(exc).__name__}: {str(exc)[:200]}"
        return out
    want = {s.upper() for s in symbols}
    for tgt in TARGETS:
        try:
            rec = _read_target(tgt, want)
        except Exception as exc:  # noqa: BLE001
            rec = {"_status": f"read failed: {type(exc).__name__}: {str(exc)[:200]}",
                   "gse": tgt.get("gse")}
        # the full probe matrix is not ours to keep; only the wanted genes and the readability facts
        keep = {k: rec.get(k) for k in (
            "gse", "platform", "platform_matches_expected", "n_samples", "n_probes",
            "n_probes_mapped_to_a_symbol", "measured_probe_mapping_rate", "value_kind",
            "samples", "genes", "probe_symbol_mapping", "_status")}
        out["targets"][tgt["matrix_file"]] = keep
    return out


def collect():
    _, rows, prov = _locus_rows()
    symbols = [r["locus"] for r in rows]
    print(f"loci from the screen: {symbols}", file=sys.stderr)
    inp = {
        "_what": ("Raw retrievals behind aso-offtarget-tissue-expression.json. One block per arm; "
                  "an arm that failed says so here and its verdict downstream is `readable: false`."),
        "_generated_utc": datetime.now(timezone.utc).isoformat(),
        "loci_provenance": prov,
        "loci": rows,
        "arm_a_gtex": fetch_gtex(symbols),
        "arm_b_emc_series": fetch_emc_series(symbols),
        "arm_c_ncbi_gene": fetch_ncbi_gene(symbols),
        "arm_d_hpa": fetch_hpa(symbols),
    }
    with open(INPUTS, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(inp, indent=1, sort_keys=False) + "\n")
    print(f"wrote {os.path.basename(INPUTS)}", file=sys.stderr)
    return inp


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Derive — pure, offline, and unable to turn a failed arm into a biological statement
# ─────────────────────────────────────────────────────────────────────────────────────────────

def _control_verdict(gtex):
    """Did the matrix parse land the known-answer controls where they must be?

    ⛔ A RUN THAT FAILS THIS MUST NOT EMIT A LOCUS VERDICT. A column shift in a wide matrix is
    invisible in the numbers and fatal to every conclusion drawn from them; these three genes are
    the cheapest observation that discriminates a correct parse from a shifted one.
    """
    if gtex.get("_status") != "read":
        return {"ran": False, "why": "arm A was not read", "passed": None, "controls": {}}
    tissues = gtex.get("tissues") or []
    res, ok = {}, True
    for sym, spec in GTEX_CONTROLS.items():
        got = (gtex.get("rows") or {}).get(sym.upper())
        if not got:
            res[sym] = {"found": False, "passed": False, "why": spec["why"]}
            ok = False
            continue
        vals = got[0]["values"]
        pairs = [(t, v) for t, v in zip(tissues, vals) if v is not None]
        top = max(pairs, key=lambda p: p[1]) if pairs else (None, None)
        # ⛔ COMPARED ON `_tkey`, NOT ON THE RAW LABEL. Two of three controls failed on a hyphen in
        # run 31749264339 and took every locus verdict down with them; see `_tkey`.
        passed = _tkey(top[0]) in {_tkey(x) for x in spec["expect_max_in"]}
        res[sym] = {"found": True, "max_tissue": top[0], "max_median_tpm": top[1],
                    "expected_max_in": spec["expect_max_in"], "passed": passed,
                    "why": spec["why"]}
        ok = ok and passed
    return {"ran": True, "passed": ok, "controls": res,
            "_meaning": ("These assert that the tissue COLUMNS are aligned to the values. A failure "
                         "means the parse is shifted and every tissue figure below is wrong; it "
                         "does not mean the genes are unusual.")}


def _hpa_exposure_block(hpa, sym, label):
    """The exposure block from HPA when GTEx could not be read at all.

    ⚠ IT IS A DIFFERENT INSTRUMENT AND SAYS SO ON EVERY ROW. HPA reports consensus nTPM over a
    whole `kidney`, where GTEx splits cortex from medulla, and HPA's consensus incorporates GTEx
    among its sources — so this is neither interchangeable with the GTEx block nor independent of
    it. It exists because an arm-A outage taking the entire exposure question down with it is worse
    than a labelled second-choice reading, not because the two are equivalent.
    """
    rec = ((hpa.get("genes") or {}).get(sym) or {}).get("per_gene") or {}
    if rec.get("_status") != "read":
        return None
    vals = rec.get("values") or {}
    got = {k: vals[k] for k in _HPA_EXPOSURE_KEYS if k in vals}
    if not got:
        return None
    return {"readable": True, "block": label, "values": got,
            "source": "Human Protein Atlas consensus tissue nTPM",
            "unit": "nTPM (HPA consensus), NOT GTEx median TPM — do not pool the two",
            "matched_path": rec.get("matched_path"),
            "⚠_substituted_for_gtex": (
                "GTEx arm A could not be read on this run, so the exposure figure here is HPA's. "
                "HPA gives a WHOLE-KIDNEY value rather than GTEx's cortex/medulla split, and its "
                "consensus incorporates GTEx, so this is a second-choice reading and not an "
                "independent confirmation of one."),
            "max_tissue_in_block": max(got, key=lambda t: got[t]),
            "any_present_at_cut": any(v >= PRESENT_TPM for v in got.values())}


def _tissue_block(gtex, sym, tissues, label, hpa=None):
    """Median TPM for one locus across one named tissue list, or an explicit unreadable state."""
    if gtex.get("_status") != "read":
        # ⛔ ONLY THE EXPOSURE BLOCK HAS A FALLBACK. The soft-tissue proxy block has no HPA
        # equivalent worth substituting, so it stays unreadable rather than being filled from a
        # source that does not carry those tissues.
        if hpa is not None and label == "exposure_liver_kidney":
            alt = _hpa_exposure_block(hpa, sym, label)
            if alt is not None:
                return alt
        return {"readable": False,
                "reason": f"arm A was not read ({gtex.get('_status')})",
                "block": label, "values": None}
    got = (gtex.get("rows") or {}).get(sym.upper())
    if not got:
        return {"readable": False,
                "reason": ("no row for this symbol in the GTEx v8 gene model — the locus is not "
                           "measured by this instrument. ⚠ THIS IS NOT A READING OF ZERO."),
                "block": label, "values": None}
    order = gtex.get("tissues") or []
    idx = {_tkey(t): i for i, t in enumerate(order)}      # see `_tkey`: endpoint-independent
    missing = [t for t in tissues if _tkey(t) not in idx]
    vals, per_model = {}, []
    for row in got:
        v = row["values"]
        one = {t: (v[idx[_tkey(t)]] if _tkey(t) in idx and idx[_tkey(t)] < len(v) else None)
               for t in tissues}
        per_model.append({"gencode_id": row["gencode_id"], "median_tpm": one})
    for t in tissues:
        seen = [m["median_tpm"][t] for m in per_model if m["median_tpm"][t] is not None]
        vals[t] = max(seen) if seen else None       # the highest model, the conservative direction
    return {"readable": True, "block": label, "values": vals,
            "n_gene_models": len(per_model), "per_gene_model": per_model,
            "tissue_labels_not_found": missing,
            "max_tissue_in_block": (max((t for t in tissues if vals.get(t) is not None),
                                        key=lambda t: vals[t], default=None)),
            "any_present_at_cut": any(v is not None and v >= PRESENT_TPM for v in vals.values())}


def _whole_body_context(gtex, sym):
    """Where this locus is HIGHEST across all 54 tissues, so a compartment figure has a scale.

    Without it a reader cannot tell 3 TPM in liver from "3 TPM in liver and 300 in brain", and those
    are different objects for a drug that does not cross the blood-brain barrier.
    """
    if gtex.get("_status") != "read":
        return None
    got = (gtex.get("rows") or {}).get(sym.upper())
    if not got:
        return None
    order = gtex.get("tissues") or []
    best = {}
    for row in got:
        for t, v in zip(order, row["values"]):
            if v is None:
                continue
            if t not in best or v > best[t]:
                best[t] = v
    top = sorted(best.items(), key=lambda kv: -kv[1])[:6]
    return {"top_tissues": [{"tissue": t, "median_tpm": v} for t, v in top],
            "n_tissues_at_or_above_cut": sum(1 for v in best.values() if v >= PRESENT_TPM),
            "n_tissues_read": len(best)}


def _emc_block(emc, sym):
    """The on-site arm for one locus: was a probe there at all, and what did it read."""
    per = {}
    readable_anywhere = False
    for mf, tgt in (emc.get("targets") or {}).items():
        if (tgt or {}).get("_status") != "read":
            per[mf] = {"readable": False,
                       "reason": f"series not read ({(tgt or {}).get('_status')})"}
            continue
        genes = tgt.get("genes") or {}
        g = genes.get(sym.upper()) or genes.get(sym)
        if not g:
            per[mf] = {"readable": False, "platform": tgt.get("platform"),
                       "reason": ("no probe on this platform maps to this symbol — the READ could "
                                  "not be taken. ⚠ THIS IS NOT A STATEMENT THAT THE GENE IS OFF."),
                       "probe_mapping_rate": tgt.get("measured_probe_mapping_rate")}
            continue
        readable_anywhere = True
        pct = [p for p in (g.get("array_percentile") or []) if p is not None]
        per[mf] = {"readable": True, "platform": tgt.get("platform"),
                   "n_probes_mapping": g.get("n_probes_mapping"),
                   "n_samples": tgt.get("n_samples"),
                   "value_kind": tgt.get("value_kind"),
                   "array_percentile": g.get("array_percentile"),
                   "median_array_percentile": (sorted(pct)[len(pct) // 2] if pct else None),
                   "_percentile_is_the_readout": (
                       "the gene's rank within THIS array's own probe distribution, which is the "
                       "only 'is it on at all' reading an array supports; the raw value is "
                       "platform-relative and is not comparable to a TPM.")}
    return {"readable_on_any_platform": readable_anywhere, "per_series": per}


def _locus_verdict(row, exposure, tumour_proxy, emc, ncbi):
    """One sentence per locus, and it is allowed to say that nothing can be concluded."""
    sym = row["locus"]
    ident = (ncbi.get("genes") or {}).get(sym) or {}
    uncharacterised = "uncharacterized" in str(ident.get("description", "")).lower() \
        or sym.startswith("LOC")

    if not exposure["readable"]:
        if uncharacterised:
            return ("NOT_MEASURABLE_UNCHARACTERISED",
                    "An uncharacterised locus with no GTEx v8 gene model, so no exposure-organ "
                    "expression figure exists in this instrument. Nothing here says it is absent "
                    "from liver or kidney — only that public bulk expression data as retrieved "
                    "cannot answer the question for it.")
        return ("NOT_MEASURED",
                "No expression reading could be taken in the exposure arm; the reason is recorded "
                "and is not a reading of absence.")

    vals = {k: v for k, v in exposure["values"].items() if v is not None}
    hi = max(vals.values()) if vals else None
    if hi is None:
        return ("NOT_MEASURED", "The exposure arm carried no value for this locus.")
    if hi >= EXPRESSED_TPM:
        return ("EXPRESSED_IN_AN_EXPOSURE_ORGAN",
                f"Median TPM reaches {hi:g} in {exposure['max_tissue_in_block']}. A transcript at "
                f"this level in a dosed organ is where an off-target hypothesis would have to be "
                f"tested; whether a two-mismatch duplex engages it is not answered by any screen "
                f"here.")
    if hi >= PRESENT_TPM:
        return ("LOW_IN_EXPOSURE_ORGANS",
                f"Median TPM peaks at {hi:g} in {exposure['max_tissue_in_block']} — detectable and "
                f"low against the whole-body maximum recorded alongside it.")
    return ("BELOW_DETECTION_IN_EXPOSURE_ORGANS",
            f"Median TPM is below {PRESENT_TPM:g} in every exposure tissue (highest {hi:g}). This "
            f"is a measured low reading in GTEx v8, not a safety statement.")


def derive(inp):
    gtex = inp.get("arm_a_gtex") or {}
    emc = inp.get("arm_b_emc_series") or {}
    ncbi = inp.get("arm_c_ncbi_gene") or {}
    hpa = inp.get("arm_d_hpa") or {}
    controls = _control_verdict(gtex)

    per_locus = []
    for row in inp.get("loci") or []:
        sym = row["locus"]
        exposure = _tissue_block(gtex, sym, EXPOSURE_TISSUES, "exposure_liver_kidney", hpa=hpa)
        proxy = _tissue_block(gtex, sym, TUMOUR_COMPARTMENT_PROXY_TISSUES,
                              "tumour_compartment_normal_tissue_proxy")
        # ⛔ THE CONTROL GATE. A shifted parse must not be able to produce a locus verdict.
        if controls["ran"] and controls["passed"] is False:
            tier, sentence = ("NOT_MEASURED",
                              "The GTEx known-answer controls failed, so the tissue columns of this "
                              "parse are not trusted and no exposure figure is emitted.")
            exposure = {"readable": False, "block": "exposure_liver_kidney", "values": None,
                        "reason": "withheld: arm A's known-answer controls failed"}
            proxy = {"readable": False, "block": "tumour_compartment_normal_tissue_proxy",
                     "values": None, "reason": "withheld: arm A's known-answer controls failed"}
        else:
            tier, sentence = _locus_verdict(row, exposure, proxy, emc, ncbi)
        ident = (ncbi.get("genes") or {}).get(sym) or {}
        # ⛔ READ WITH `.get`, BECAUSE A COMMITTED INPUTS CACHE OUTLIVES THE CODE THAT WROTE IT.
        # Measured 2026-08-13: run 31747675357's published cache carries the single-seam locus rows
        # written before the panel existed, so `row["seams"]` raised `KeyError` and the derive half
        # could not reproduce the artifact from its OWN published inputs. A module whose `--check`
        # crashes on last run's cache has no reproduction test at all, which is worse than a stale
        # number — so a pre-panel cache degrades to an explicit "not recorded" rather than throwing.
        per_locus.append({
            "locus": sym,
            "seams": row.get("seams") or ["not_recorded_by_the_run_that_wrote_this_cache"],
            "designs_hitting_it": row.get("designs_hitting_it") or [],
            "n_designs_hitting_it": row.get("n_designs_hitting_it"),
            "⭐_recurrence_is_a_second_axis_and_not_the_record_count": (
                "A locus every design at a seam returns is robust to tiling register — it is there "
                "wherever the window is put — while a locus one register returns may be a property "
                "of that window. Record count measures neither. Ranking on either alone is a "
                "mistake; both are reported so neither has to stand in for the other."),
            "screen_records": {
                "n_transcript_records": row.get("n_transcript_records"),
                "n_curated_records": row.get("n_curated_records"),
                "n_predicted_records": row.get("n_predicted_records"),
                "identity_of_every_record": row.get("identity_of_every_record"),
                "⚠_record_count_is_annotation_depth": (
                    "how many transcript variants RefSeq lists for this gene, not expression, not "
                    "affinity and not risk. A locus with many records is not thereby a larger "
                    "liability, and one with a single record is not thereby a smaller one."),
            },
            "identity": {
                "ncbi_status": ident.get("_status"),
                "ncbi_gene_id": ident.get("gene_id"),
                "description": ident.get("description"),
                "map_location": ident.get("maplocation"),
                "ncbi_summary": ident.get("summary"),
            },
            "exposure_compartment_liver_kidney": exposure,
            "tumour_compartment_normal_tissue_proxy": proxy,
            "tumour_compartment_emc_tumours": _emc_block(emc, sym),
            "whole_body_context": _whole_body_context(gtex, sym),
            "hpa_cross_check": (hpa.get("genes") or {}).get(sym),
            "tier": tier,
            "sentence": sentence,
        })

    readable = [p for p in per_locus if p["exposure_compartment_liver_kidney"]["readable"]]
    # ⚠ NAMED FOR WHAT IT MEASURES, NOT FOR WHAT IT MIGHT IMPLY. An earlier draft called this
    # `concern`, which is a hazard word for a list of genes whose only property here is a median
    # TPM in an organ. The reading is "this gene is expressed there"; the step to "this reagent
    # matters there" is the manuscript's, and it needs an affinity argument nothing here supplies.
    expressed_in_exposure = [p["locus"] for p in per_locus
                             if p["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN"]
    unmeasurable = [p["locus"] for p in per_locus
                    if p["tier"] in ("NOT_MEASURED", "NOT_MEASURABLE_UNCHARACTERISED")]

    return {
        "_what": ("Tissue expression of every gene locus the clinically-relevant junction gapmer's "
                  "deep off-target screen returns, split into the organs a systemically dosed "
                  "phosphorothioate reaches and the compartment the tumour occupies."),
        "_framing": (
            "⛔ NOTHING IN THIS FILE IS AN EFFICACY, SELECTIVITY, SAFETY, THERAPEUTIC-WINDOW OR "
            "CLINICAL-READINESS CLAIM FOR ANY SEQUENCE. Every hit behind it sits at 14/16 identity "
            "— two mismatches in a 16-mer — and whether such a duplex is an RNase-H1 substrate at "
            "all is an affinity question no screen here answers. Expression is a NECESSARY "
            "condition for an off-target effect and never a sufficient one, so a gene being "
            "expressed is not a predicted cleavage event and a gene being unexpressed is not "
            "safety."),
        "_what_this_is_not": [
            "Not a cleavage assay, and not a prediction of one. No hit was re-aligned, no duplex "
            "stability was computed, and no thermodynamic threshold separates these hits from each "
            "other — they are the screen's loosest admitted class, all at two mismatches.",
            "Not a risk ranking by transcript-record count, or by anything else. Record count is "
            "annotation depth, and this file carries no hazard ordering of any kind.",
            "Not evidence about the oligonucleotide. Every figure here is expression of a GENE. "
            "The join from 'this gene is expressed in liver' to 'this reagent does something in "
            "liver' requires an affinity argument no screen in this repository has made, and it is "
            "the manuscript's to make explicitly, with the missing step named.",
            "Not a tumour measurement where it says proxy. GTEx contains no EMC and no sarcoma; the "
            "soft-tissue block is the NORMAL tissue of the compartment EMC arises in.",
            "Not a reading of absence anywhere. Every unreadable locus carries the reason the read "
            "could not be taken, and no absence is rendered as a zero.",
            f"PRESENT_TPM = {PRESENT_TPM:g} is a STATED legibility cut, not a threshold of concern, "
            f"and every raw median is released so another cut can be applied without re-running.",
        ],
        "_cost": "$0 — public reference data on a CPU runner. No GPU, no rental, no wet lab.",
        "_generated_utc": inp.get("_generated_utc"),
        "panel": inp.get("loci_provenance"),
        "method": {
            "exposure_tissues": EXPOSURE_TISSUES,
            "_why_those": ("Systemically dosed phosphorothioate gapmers distribute predominantly to "
                           "liver and kidney, so those organs carry the exposure question."),
            "tumour_compartment_proxy_tissues": TUMOUR_COMPARTMENT_PROXY_TISSUES,
            "_why_a_proxy": ("EMC arises in deep soft tissue of the extremities and has a myxoid "
                             "stroma. No reference expression atlas contains that tumour, so these "
                             "are the normal tissues of that anatomical compartment, and the actual "
                             "tumour reading is the EMC array arm beside them."),
            "present_tpm_cut": PRESENT_TPM,
            "arms": {
                "A_gtex": {"status": gtex.get("_status"), "url": gtex.get("url"),
                           "release": gtex.get("release"), "unit": gtex.get("unit"),
                           "endpoint_used": gtex.get("endpoint_used"),
                           "n_tissues": len(gtex.get("tissues") or []) or None},
                "B_emc_series": {"targets": {k: (v or {}).get("_status")
                                             for k, v in (emc.get("targets") or {}).items()}},
                "C_ncbi_gene": {"status": {k: (v or {}).get("_status")
                                           for k, v in (ncbi.get("genes") or {}).items()}},
                "D_hpa": {"status": {k: (v or {}).get("_status")
                                     for k, v in (hpa.get("genes") or {}).items()},
                          "_not_independent": hpa.get("_not_independent_of_gtex")},
            },
            "known_answer_controls": controls,
        },
        "summary": {
            "n_loci": len(per_locus),
            "n_loci_with_a_readable_exposure_reading": len(readable),
            "loci_expressed_in_an_exposure_organ": expressed_in_exposure,
            "loci_whose_exposure_question_is_unanswerable_from_public_data": unmeasurable,
            "⛔_this_list_is_not_a_ranking_and_this_file_has_no_risk_column": (
                "These are the genes whose median TPM reaches the stated cut in liver or kidney. "
                "That is a reading about each GENE. It is not an ordering of the panel by hazard, "
                "and no such ordering exists anywhere in this file, because every hit behind it is "
                "a 14/16 sequence match and the step from an expressed gene to an affected one "
                "needs an affinity argument no screen here has made. Loci are ordered by "
                "transcript-record count, which is an annotation property and is labelled as one."),
            "⚠_what_a_clean_exposure_column_does_and_does_not_buy": (
                "It says those genes are low or absent in the dosed organs. It does not make the "
                "reagent clean: the same panel holds loci this instrument cannot measure at all, "
                "and none of these hits has been shown to be cleavable in the first place."),
        },
        "per_locus": per_locus,
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────

def _empty_inputs():
    """A coherent not-yet-fetched state, so the derive half is exercisable with no network."""
    _, rows, prov = _locus_rows()
    return {"_what": "placeholder: no retrieval has been run yet",
            "_generated_utc": None,
            "loci_provenance": prov, "loci": rows,
            "arm_a_gtex": {"_status": "not fetched", "url": GTEX_MEDIAN_TPM_URL},
            "arm_b_emc_series": {"targets": {}},
            "arm_c_ncbi_gene": {"genes": {}},
            "arm_d_hpa": {"genes": {}}}


def _load_inputs():
    if os.path.exists(INPUTS):
        return json.load(open(INPUTS, encoding="utf-8"))
    return _empty_inputs()


def selftest():
    """Offline assertions of the guards, run BEFORE the fetch so a broken derive costs seconds.

    ⛔ EVERY ONE OF THESE IS A WAY THIS ARTIFACT COULD LIE, and all four are pure arithmetic over
    constructed inputs, so none of them needs a network.
    """
    # (1) the locus set derives from the screens and the censoring guard is live
    _, rows, prov = _locus_rows()
    assert prov["n_gap_paired_hybridisable"] == sum(r["n_transcript_records"] for r in rows)
    assert prov["n_loci_over_the_whole_panel"] == len(rows) >= 1
    assert prov["n_seams"] == len(PANEL) >= 2

    # (2) an unfetched arm can never become a biological statement
    art = derive(_empty_inputs())
    for p in art["per_locus"]:
        assert p["exposure_compartment_liver_kidney"]["readable"] is False
        assert p["tier"] in ("NOT_MEASURED", "NOT_MEASURABLE_UNCHARACTERISED")
        assert "not a reading of absence" in p["sentence"] or "cannot answer" in p["sentence"]

    # (3) a shifted parse cannot emit a locus verdict — the control gate really gates
    bad = _empty_inputs()
    bad["arm_a_gtex"] = {"_status": "read", "tissues": ["Liver", "Kidney - Cortex"],
                         "rows": {"ALB": [{"gencode_id": "x", "symbol": "ALB",
                                           "values": [1.0, 900.0]}],
                                  rows[0]["locus"].upper(): [
                                      {"gencode_id": "y", "symbol": rows[0]["locus"],
                                       "values": [500.0, 500.0]}]}}
    shifted = derive(bad)
    assert shifted["method"]["known_answer_controls"]["passed"] is False
    for p in shifted["per_locus"]:
        assert p["tier"] == "NOT_MEASURED", "a failed control still emitted a verdict"
        assert p["exposure_compartment_liver_kidney"]["readable"] is False

    # (4) a real high liver reading, with controls passing, IS reported as one
    good = _empty_inputs()
    tis = EXPOSURE_TISSUES + ["Heart - Left Ventricle", "Muscle - Skeletal"]
    def _row(sym, mapping):
        return [{"gencode_id": "g", "symbol": sym,
                 "values": [mapping.get(t, 0.0) for t in tis]}]
    good["arm_a_gtex"] = {"_status": "read", "tissues": tis, "rows": {
        "ALB": _row("ALB", {"Liver": 999.0}),
        "UMOD": _row("UMOD", {"Kidney - Medulla": 800.0}),
        "MYH7": _row("MYH7", {"Heart - Left Ventricle": 700.0}),
        rows[0]["locus"].upper(): _row(rows[0]["locus"], {"Liver": 120.0}),
    }}
    ok = derive(good)
    assert ok["method"]["known_answer_controls"]["passed"] is True
    first = [p for p in ok["per_locus"] if p["locus"] == rows[0]["locus"]][0]
    assert first["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN", first["tier"]
    assert first["exposure_compartment_liver_kidney"]["values"]["Liver"] == 120.0
    # and a locus with no row is unreadable rather than zero
    other = [p for p in ok["per_locus"] if p["locus"] != rows[0]["locus"]]
    assert other, "the screen must return more than one locus for this assertion to mean anything"
    assert all(not p["exposure_compartment_liver_kidney"]["readable"] for p in other)
    assert all("NOT A READING OF ZERO" in
               p["exposure_compartment_liver_kidney"]["reason"].upper() for p in other)

    print("selftest ok: locus derivation, unfetched-arm refusal, control gate, and the "
          "unreadable-is-not-zero rule all hold", file=sys.stderr)
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    inp = collect() if "--fetch" in argv else _load_inputs()
    art = derive(inp)
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("aso-offtarget-tissue-expression.json is stale; re-run without --check",
                  file=sys.stderr)
            return 1
        print("off-target tissue-expression artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    s = art["summary"]
    print(f"wrote {os.path.basename(OUT)}: {s['n_loci']} loci, "
          f"{s['n_loci_with_a_readable_exposure_reading']} with a readable exposure reading; "
          f"expressed in an exposure organ: {s['loci_expressed_in_an_exposure_organ']}; "
          f"unanswerable: {s['loci_whose_exposure_question_is_unanswerable_from_public_data']}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
