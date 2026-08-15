#!/usr/bin/env python3
"""Emit `emc-model-junction-evidence.json` — the one home for the two USZ exon-2 acceptor seams.

⛔ WHY THIS FILE EXISTS. `aso_noncoding_acceptor_designs.PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS`
admits a seam ONLY where a published report places a patient's breakpoint at it, and every entry
must name a home for that evidence. The two entries added on 2026-08-15 — EWSR1 e13 :: NR4A3 e2 and
TAF15 e6 :: NR4A3 e2, the junctions of the identity-clean patient-derived models USZ20-EMC1 and
USZ22-EMC2 — had none: the wider EMC breakpoint census is built from sequenced-junction case series
and carries no row for either model, which was CHECKED rather than assumed.

⛔ AND THE COORDINATES ARE COMPUTED, NEVER TYPED. The curated half of this artifact is verbatim
quotation from primary records that were read; every seam, offset, exon boundary and validation
result is derived at emit time from the committed transcript models and from the cached UCSC
response, re-parsed here rather than quoted. A remembered coordinate is exactly what produced the
retracted EWSR1-e11 seam.

The curated half (verbatim quotes, accessions, source paths) is typed here from primary records
that were READ; the derived half (seams, offsets, exon boundaries, the deriver's validation) is
COMPUTED from the committed transcript models at emit time so no coordinate in the artifact is a
remembered number.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-model-junction-evidence.json")
os.environ["TRANSCRIPT_SOURCE"] = "cache"
sys.path.insert(0, HERE)

import junction_aso as ja  # noqa: E402
import aso_screen_sets as ass  # noqa: E402
import aso_noncoding_acceptor_designs as NCA  # noqa: E402


def seam(d_sym, d_end, a_sym, a_start):
    return ja.mrna_junction_generic(ja.transcript_model(d_sym), ja.transcript_model(a_sym),
                                    d_end, a_start)


def committed_context(path, key, label):
    with open(os.path.join(HERE, path), encoding="utf-8") as fh:
        art = json.load(fh)
    for row in art[key]:
        if row.get("junction_label") == label:
            return row["junction_context_mRNA"]
    return None


#: The cached UCSC response, on the branch `fetch-literature` publishes to. ⛔ NOT COPIED INTO THIS
#: TREE: the literature cache is that branch's, and a second copy here would be the more
#: authoritative-looking one the day the two diverge.
UCSC_BLOB = ("literature/emc-cell-models-round2b-2026-08-15/ucsc_NR4A3_refseq_hg38.txt")
_REPO = os.path.dirname(os.path.dirname(HERE))


def _git(*args):
    return subprocess.run(["git", *args], cwd=_REPO, capture_output=True, text=True)


def ucsc_rows():
    """Read the NR4A3 RefSeq transcript records back out of the literature-cache branch.

    ⛔ READ AND RE-PARSED, NOT QUOTED. The answer this function computes — does any curated NR4A3
    transcript begin its CDS in exon 2 — is the load-bearing measurement under the whole acceptor
    ambiguity, so it is derived from the cached response's own exonStarts/exonEnds every time this
    artifact is built, rather than typed as a conclusion somebody once reached.

    ⚠ A MISSING REF IS A REFUSAL, NEVER AN EMPTY LIST. An empty result here would render as "no
    NR4A3 transcript numbers its coding acceptor exon 2" — the same sentence a successful run
    produces — which is an unread file answering the question it could not look at.
    """
    for ref in ("origin/literature-cache", "literature-cache"):
        r = _git("show", f"{ref}:{UCSC_BLOB}")
        if r.returncode == 0:
            blob = r.stdout
            break
    else:
        f = _git("fetch", "origin", "literature-cache", "--depth=1")
        r = _git("show", f"FETCH_HEAD:{UCSC_BLOB}")
        if r.returncode != 0:
            raise RuntimeError(
                f"cannot read {UCSC_BLOB} from the literature-cache branch "
                f"(git show: {r.stderr.strip()[:200]}; git fetch: {f.stderr.strip()[:200]}). That "
                "file is the ONLY record of whether any curated NR4A3 transcript begins its CDS in "
                "exon 2, and an unread file must not be reported as a negative answer. Run "
                "`git fetch origin literature-cache --depth=1` and retry.")
        blob = r.stdout
    payload = json.loads(blob[blob.index("{", blob.index("=====")):])
    out = []
    for t in payload["ncbiRefSeqCurated"]:
        if t.get("name2") != "NR4A3":
            continue
        starts = [int(x) for x in t["exonStarts"].rstrip(",").split(",")]
        ends = [int(x) for x in t["exonEnds"].rstrip(",").split(",")]
        cds = t["cdsStart"]
        cds_exon = next((i + 1 for i, (s, e) in enumerate(zip(starts, ends)) if s <= cds < e), None)
        out.append({
            "refseq": t["name"], "strand": t["strand"], "n_exons": t["exonCount"],
            "cdsStart": cds,
            "exon_containing_cdsStart_1based": cds_exon,
            "exon_frames": t["exonFrames"],
            "n_leading_noncoding_exons_by_exonFrames":
                len(t["exonFrames"].rstrip(",").split(",")) - len(
                    [f for f in t["exonFrames"].rstrip(",").split(",") if f != "-1"]),
            "exon1_span": [starts[0], ends[0]], "exon2_span": [starts[1], ends[1]],
        })
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    nr4a3 = ja.transcript_model("NR4A3")
    with open(os.path.join(HERE, "aso-premrna-sequences.json"), encoding="utf-8") as fh:
        pre = json.load(fh)["genes"]["NR4A3"]["sequence"].upper()
    e1, e2 = nr4a3["exon_lens"][0], nr4a3["exon_lens"][1]
    exon2 = nr4a3["cdna"][e1:e1 + e2]
    exon2_off = pre.find(exon2)

    validation = []
    for d_sym, d_end, a_sym, a_start, path, key, pins in (
            ("EWSR1", 7, "NR4A3", 2, "aso-noncoding-acceptor-designs.json", "junctions",
             "the NR4A3 exon-2 ACCEPTOR half, at a seam with three independent published sources"),
            ("PGR", 2, "NR4A3", 2, "aso-noncoding-acceptor-designs.json", "junctions",
             "the NR4A3 exon-2 ACCEPTOR half again, through an unrelated donor gene"),
            ("EWSR1", 13, "NR4A3", 3, "nr4a3-fusion-junction-atlas.json", "graded_pairs",
             "the EWSR1 exon-13 DONOR half — USZ20-EMC1's donor, at the panel's own acceptor"),
            ("TAF15", 6, "NR4A3", 3, "nr4a3-fusion-junction-atlas.json", "graded_pairs",
             "the TAF15 exon-6 DONOR half — USZ22-EMC2's donor, at the panel's own acceptor")):
        label = f"{d_sym}_e{d_end}__{a_sym}_e{a_start}"
        got = seam(d_sym, d_end, a_sym, a_start)["junction_context_mRNA"]
        want = committed_context(path, key, label)
        validation.append({"junction_label": label, "pins": pins, "committed_artifact": path,
                           "committed_junction_context_mRNA": want,
                           "rederived_junction_context_mRNA": got, "agree": got == want})

    derived = []
    for d_sym, d_end, model, rrid in (("EWSR1", 13, "USZ20-EMC1", "RRID:CVCL_C6MX"),
                                      ("TAF15", 6, "USZ22-EMC2", "RRID:CVCL_C6MY")):
        j = seam(d_sym, d_end, "NR4A3", 2)
        donor = ja.transcript_model(d_sym)
        derived.append({
            "junction_label": j["junction_label"],
            "model": model, "rrid": rrid,
            "junction_context_mRNA_12plus12": j["junction_context_mRNA"],
            "donor_transcript": donor["transcript"], "acceptor_transcript": nr4a3["transcript"],
            "donor_tx_nt_through_cut": ja.exon_tx_end(donor, d_end),
            "acceptor_tx_start_0based": ja.exon_tx_start(nr4a3, 2),
            "acceptor_exon_is_coding": j["nr4a3_acceptor_exon_is_coding"],
            "acceptor_5utr_nt_retained": j["nr4a3_acceptor_exon_5utr_nt_retained"],
            "measured_grade": ja.grade_junction(j, *ja.plausible_nr4a3_resume_residues())[0],
        })

    art = {
        "_what": ("The published fusion-junction evidence behind the two NR4A3 exon-2 acceptor "
                  "seams whitelisted for the identity-clean patient-derived EMC cell models "
                  "USZ20-EMC1 and USZ22-EMC2 — and the re-derivation of those seams from this "
                  "repository's committed transcript models."),
        "_why": ("`aso_noncoding_acceptor_designs.PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS` admits a "
                 "seam ONLY where a published report places a patient's breakpoint at it, and each "
                 "entry must name a home for that evidence. The wider EMC breakpoint census "
                 "(research/manuscripts/aso/lit-targets-aso-breakpoint-census.json) is built from "
                 "sequenced-junction case series and carries NO row for either USZ model — checked, "
                 "not assumed — so these two entries had no home and this file is it."),
        "_what_this_is_not": [
            "Not an efficacy, activity, potency or safety claim. It is evidence and coordinates.",
            "Not a resolution of the acceptor exon index. The ambiguity is the subject of this "
            "file, not something it settles; the reading a user must hold is the one home'd on "
            "`aso_noncoding_acceptor_designs._USZ_ACCEPTOR_AMBIGUITY` and is not restated here.",
            "Not a coverage claim. Neither junction has a published patient count and neither is in "
            "the 58-case partner cohort every rung of aso_coverage_ladder.py is computed against, "
            "so a reagent at either seam moves coverage by exactly zero.",
            "Not a survey of EMC models. It covers only the two junctions the whitelist needs.",
        ],
        "_cost": "$0 — CPU, committed transcript caches, and reads of the literature-cache branch.",
        "geometry": ass.MANUSCRIPT_GEOMETRY.as_dict(),
        "transcript_source": ja.transcript_source_provenance(),
        "provenance_gate_per_gene": dict(ja.PROVENANCE_GATE_USED),

        "models": [
            {
                "model": "USZ20-EMC1",
                "rrid": "RRID:CVCL_C6MX",
                "cellosaurus_id_line_verbatim": "ID USZ20-EMC1",
                "cellosaurus_ac_line_verbatim": "AC CVCL_C6MX",
                "cellosaurus_sy_line_verbatim":
                    "SY UniversitatsSpital Zurich 2020-Extraskeletal Myxoid Chondrosarcoma 1",
                "reported_junction": "EWSR1 exon 13 :: NR4A3 exon 2",
                "primary_source": "PMID 36316541 / PMC9813045 / DOI 10.1007/s13577-022-00818-x — "
                                  "Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, "
                                  "Pauli C. Hum Cell 36:446-455 (2023)",
                "primary_quote_figure4_legend_verbatim":
                    "The rearrangement and fusion partner was confirmed by NGS using the "
                    "FoundationOne®HEME assay. For USZ20-EMC1; EWSR1 was confirmed as fusion "
                    "partner having exon 13 for EWSR1 on chr22 and exon 2 from NR4A3 on chr9 "
                    "involved (B).",
                "registry_quote_verbatim":
                    "CC Sequence variation: Gene fusion; HGNC; HGNC:3508; EWSR1 + HGNC; HGNC:7982; "
                    "NR4A3; Name(s)=EWSR1-NR4A3; Note=EWSR1 exon 13 fused to NR4A3 exon 2 "
                    "(PubMed=36316541).",
            },
            {
                "model": "USZ22-EMC2",
                "rrid": "RRID:CVCL_C6MY",
                "cellosaurus_id_line_verbatim": "ID USZ22-EMC2",
                "cellosaurus_ac_line_verbatim": "AC CVCL_C6MY",
                "cellosaurus_sy_line_verbatim":
                    "SY UniversitatsSpital Zurich 2022-Extraskeletal Myxoid Chondrosarcoma 2",
                "reported_junction": "TAF15 exon 6 :: NR4A3 exon 2",
                "primary_source": "PMID 36316541 / PMC9813045 (the same paper)",
                "primary_quote_figure4_legend_verbatim":
                    "For USZ22-EMC2; TAF15 was confirmed as fusion partner having exon 6 for TAF15 "
                    "on chr17 and exon 2 from NR4A3 on chr9 involved (D).",
                "registry_quote_verbatim":
                    "CC Sequence variation: Gene fusion; HGNC; HGNC:7982; NR4A3 + HGNC; "
                    "HGNC:11547; TAF15; Name(s)=TAF15-NR4A3; Note=TAF15 exon 6 fused to NR4A3 exon "
                    "2 (PubMed=36316541).",
            },
        ],

        "shared_evidence": {
            "the_call_was_made_in_native_tumour_tissue_too_verbatim":
                "For USZ20-EMC1, an EWSR1-NR4A3 rearrangement and, for USZ22-EMC2, a TAF15-NR4A3 "
                "rearrangement in the native tumor tissue and the corresponding cell model was "
                "confirmed on the RNA level (Fig. b, d).",
            "⭐_why_that_sentence_matters": (
                "The whitelist admits a seam only where a published report places a PATIENT's "
                "breakpoint at it. This sentence is what makes these two cell-model junctions "
                "patient breakpoints rather than properties of a culture."),
            "assay_verbatim":
                "FoundationOne®HEME assay is a next generation sequencing (NGS) assay that uses a "
                "hybrid capture methodology and detects base substitutions, insertions, deletions, "
                "and copy number (CN) alterations in up to 406 genes and gene rearrangements in up "
                "to 265 genes, tumor mutation burden and microsatellite instability using the "
                "previously described methods. DNA and RNA was extracted using the Maxwell® Tissue "
                "DNA Purification Kit (Promega AS1030).",
            "identity_authentication_verbatim":
                "We further authenticated both cell models by analyzing highly polymorphic short "
                "tandem repeats (STR) of 16 microsatelllites and confirmed identical STR allel "
                "patterns between the native tumor and corresponding cell model. Both STR patterns "
                "did not mach those of any other cell line abvaialbel with within public cell banks "
                "examined using the cell line database, Cellosaurus",
            "orthogonal_identity_verbatim":
                "DNA methylation profiling was performed from cells at passage 8 and confirmed the "
                "methylation class for EMC with a score of 0.99 for both cell models using the DKFZ "
                "Sarcoma Classifier platform version 12",
            "availability_verbatim":
                "Both cell models USZ20-EMC1 and USZ22-EMC2 can be made available from the "
                "Laboratory for Systems Pathology and Functional Tumor Pathology, Department for "
                "Pathology and Molecular Parhology, University of Zurich, Zurich.",
            "⛔_n_independent_sources_is_ONE_for_each": (
                "The Cellosaurus rows cite PubMed=36316541, which is the same paper as the figure "
                "legend. One report, one assay, one pipeline — and the two models share it, so they "
                "are not independent corroboration of each other either."),
            "⛔_no_nucleotide_resolution": (
                "Neither the paper nor Cellosaurus reports a sequenced exon-exon boundary, a "
                "transcript accession or a junction sequence. The exon labels are the assay "
                "report's."),
        },

        "sources_read": [
            {"what": "PMC9813045 full text (figure 4 legend, methods, results)",
             "path": "literature-cache:literature/emc-cell-models-round2b-2026-08-15/"
                     "ftxt_PMC9813045_usz.txt"},
            {"what": "Cellosaurus records for both models",
             "path": "literature-cache:literature/emc-cell-models-registry-2026-08-15/"
                     "cellosaurus_usz20_emc1.txt and cellosaurus_usz22_emc2.txt"},
            {"what": "UCSC ncbiRefSeqCurated, hg38, chr9:99,815,000-99,900,000 — every curated "
                     "NR4A3 transcript, read here and re-parsed rather than quoted",
             "path": "literature-cache:literature/emc-cell-models-round2b-2026-08-15/"
                     "ucsc_NR4A3_refseq_hg38.txt",
             "source_url": "https://api.genome.ucsc.edu/getData/track?genome=hg38;"
                           "track=ncbiRefSeqCurated;chrom=chr9;start=99815000;end=99900000"},
        ],

        "⭐_is_there_any_NR4A3_numbering_that_makes_exon_2_the_coding_acceptor": {
            "_question": "Under any curated NR4A3 transcript model, does the CDS begin in exon 2?",
            "_method": ("every ncbiRefSeqCurated NR4A3 transcript in the window was re-parsed from "
                        "the cached UCSC response at emit time; the 1-based exon containing "
                        "cdsStart was computed from exonStarts/exonEnds, and the exonFrames vector "
                        "is carried beside it as an independent statement of the same thing"),
            "_result": ucsc_rows(),
            "_answer": ("NO. Every curated NR4A3 transcript begins its CDS in exon 3, and each "
                        "carries exactly two leading non-coding exons by its own exonFrames vector. "
                        "This repository's committed model agrees: nr4a3-exon-audit.json records "
                        "transcript exons 1 and 2 with coding_nt_in_exon 0 and exon 3 with "
                        "first_protein_residue 1."),
            "⚠_what_that_does_and_does_not_settle": (
                "It removes the SIMPLEST form of the breakpoint-label reading — that the report was "
                "numbering against some alternative transcript in which the coding acceptor really "
                "is exon 2. It does NOT remove that reading, because a breakpoint-flanking label is "
                "not a transcript-exon label at all. The full statement, and the reason both "
                "acceptors are designed rather than one chosen, is home'd on "
                "`aso_noncoding_acceptor_designs._USZ_ACCEPTOR_AMBIGUITY`."),
            "⚠_NR4A3_numbering_does_diverge_past_exon_2": (
                "In NM_173200.3 the third exon is the ~73-nt NR4A3 intron-2 cryptic exon this "
                "repository measured independently at 72 nt (nr4a3-intron2-cryptic-exon.json). So "
                "NR4A3 exon numbering genuinely differs between transcripts — it just never makes "
                "the canonical coding acceptor 'exon 2'."),
        },

        "⭐_the_deriver_and_its_validation": {
            "_why": ("A seam handed over as a string is a claim about a coordinate, and this "
                     "programme has already retracted one junction that came from a vendor exon "
                     "label. So both seams are rebuilt from junction_aso.transcript_model, and the "
                     "rebuilder is first required to reproduce four seams this repository already "
                     "holds committed — two that fix the ACCEPTOR half and two that fix the DONOR "
                     "half. A deriver validated on nothing is indistinguishable from a broken one."),
            "validation_cases": validation,
            "all_validation_cases_agree": all(v["agree"] for v in validation),
        },

        "seams_derived": derived,

        "nr4a3_wild_type_acceptor_context": {
            "_why": ("The acceptor half of every design at these seams is NR4A3 exon-2 5'UTR "
                     "sequence. In the patient's UN-REARRANGED allele that same sequence sits "
                     "immediately 3' of intron 1, so this is the coordinate a wild-type-allele "
                     "liability lives at. Measured here so the finding at "
                     "EWSR1_e13__NR4A3_e2 can be read without re-deriving it."),
            "nr4a3_exon1_len_nt": e1,
            "nr4a3_exon2_len_nt": e2,
            "nr4a3_exon2_start_in_unspliced_0based": exon2_off,
            "nr4a3_exon2_is_a_unique_substring_of_the_unspliced_sequence": pre.count(exon2) == 1,
            "nr4a3_intron1_last_12_nt": pre[exon2_off - 12:exon2_off],
            "nr4a3_exon2_first_12_nt": pre[exon2_off:exon2_off + 12],
            "donor_last_12_nt_vs_nr4a3_intron1_last_12_nt": {
                lbl: {
                    "donor_last_12_nt": d12,
                    "identity_over_12": sum(a == b for a, b in
                                            zip(d12, pre[exon2_off - 12:exon2_off])),
                    "contiguous_identity_from_the_3_prime_end": next(
                        (i for i, (a, b) in enumerate(
                            zip(d12[::-1], pre[exon2_off - 12:exon2_off][::-1])) if a != b),
                        12),
                }
                for lbl, d12 in (
                    ("EWSR1_e13", ja.transcript_model("EWSR1")["cdna"][
                        :ja.exon_tx_end(ja.transcript_model("EWSR1"), 13)][-12:]),
                    ("TAF15_e6", ja.transcript_model("TAF15")["cdna"][
                        :ja.exon_tx_end(ja.transcript_model("TAF15"), 6)][-12:]),
                    ("EWSR1_e7", ja.transcript_model("EWSR1")["cdna"][
                        :ja.exon_tx_end(ja.transcript_model("EWSR1"), 7)][-12:]),
                    ("PGR_e2", ja.transcript_model("PGR")["cdna"][
                        :ja.exon_tx_end(ja.transcript_model("PGR"), 2)][-12:]))
            },
            "⚠_this_is_a_context_measurement_not_a_verdict": (
                "Which designs are actually condemned is measured by the scan, not by this table: "
                "read `⭐_wild_type_NR4A3_cleavage_liability` in "
                "aso-noncoding-acceptor-designs.json, which runs against NR4A3's whole unspliced "
                "sequence with a fixed known-positive control."),
        },

        "⛔⛔_the_only_purchasable_EMC_line_cannot_test_a_junction_reagent": {
            "_why_this_is_in_THIS_file": (
                "This file exists to say which EMC models a junction-spanning reagent can be tested "
                "in. The two USZ models above are available ON REQUEST from one laboratory. The "
                "model a reader would reach for first is H-EMC-SS (RRID:CVCL_1238) — the only EMC "
                "line purchasable from a repository, named in 37 Europe PMC papers, and a member of "
                "DepMap/CCLE, GDSC and COSMIC. A reader who is not told, here, that no "
                "junction-spanning reagent can be tested in it will discover it after ordering."),
            "line": "H-EMC-SS", "rrid": "RRID:CVCL_1238",
            "purchasable_from": ["ECACC 94042258", "RIKEN BRC RCB0508", "ICLC HTL99016"],
            "⛔_verdict": "NOT FUSION-POSITIVE ON THE PUBLIC RECORD. A junction-spanning gapmer has "
                         "nothing to span in this line.",
            "⛔_one_home_for_the_verdict": (
                "research/modalities/emc-atr-vulnerability.json -> part_a_hemcss_identity, which "
                "owns the verdict string, the DepMap fusion-caller read, the expression read and "
                "the Cellosaurus record. NOT restated here — this block adds only the "
                "primary-source reading below, which that file does not carry, and the reagent "
                "consequence, which is this file's own subject."),
            "⭐_the_primary_source_read_here_rather_than_the_registry_summary": {
                "_why": ("The Cellosaurus caution cites exactly ONE PubMed ID, so the whole "
                         "registry flag rests on one paper. It is quoted everywhere as 'PCR and "
                         "FISH evidence'. That paper was therefore read in full rather than "
                         "summarised, and the reading below WEAKENS the citation — while leaving "
                         "the verdict standing on the independent evidence that does not depend "
                         "on it."),
                "citation": "PMID 34413129 / PMC8571037 — Gartrell et al., Mol Cancer Ther 20:"
                            "2151-2165 (2021)",
                "⚠_what_the_paper_is_about": (
                    "NOT EMC. Its title is 'SLFN11 is widely expressed in pediatric sarcoma and "
                    "induces variable sensitization to replicative stress caused by DNA damaging "
                    "agents'. EWSR1-translocation status is a COVARIATE across a 14-line sarcoma "
                    "drug panel, not the object of study."),
                "where_the_negative_appears": (
                    "the Figure 2A legend only, as a parenthetical: 'Although extraskeletal myxoid "
                    "chondrosarcoma (EMC) cancers such as H-EMC-SS typically have EWSR1-NR4A3 "
                    "fusions, we did not detect a EWSR1-translocation in this line. n >= 2.' There "
                    "is no results sentence, figure, table or supplementary file reporting the "
                    "assay for this line. The 'n >= 2' is the drug-assay replicate count, not the "
                    "translocation assay's."),
                "the_methods_sentence_in_full_context": (
                    "'Cell lines were authenticated using short tandem repeat analysis via "
                    "PowerPlex (Promega) and tested for mycoplasma using MycoAlert (Lonza). "
                    "Translocation status was confirmed using PCR and Fluorescence In Situ "
                    "Hybridization (FISH).' — it sits in the Cell Lines paragraph as a BLANKET "
                    "statement over the whole panel, immediately after the STR and mycoplasma "
                    "sentences."),
                "⛔_what_the_paper_does_NOT_say": [
                    "which FISH probe was used — an EWSR1 BREAK-APART probe would detect an "
                    "EWSR1 rearrangement whatever the partner, whereas a fusion-specific probe or "
                    "an EWSR1-FLI1 RT-PCR (the fusion this Ewing-focused paper cares about) would "
                    "not exclude EWSR1::NR4A3. The text does not distinguish these, so the assay's "
                    "sensitivity to an NR4A3 partner is NOT established by this source.",
                    "which PCR primers were used, or against which fusion",
                    "a per-line result for H-EMC-SS, anywhere outside the figure legend",
                    "how many times the translocation assay was run",
                ],
                "⚠_the_honest_reading": (
                    "'PCR and FISH evidence behind it' overstates this citation. What the paper "
                    "supports is that a group holding the line from ECACC looked for an EWSR1 "
                    "translocation with unstated methods and did not find one. That is real "
                    "evidence and it is thin, and the verdict must not rest on it alone."),
            },
            "⭐_why_the_verdict_stands_anyway": [
                "DepMap's filtered fusion caller is INDEPENDENT of that paper and is not an absent "
                "reading: emc-atr-vulnerability.json records the model PRESENT in "
                "OmicsFusionFiltered.csv with 2 calls, neither naming NR4A3 nor any FET gene. A "
                "caller that ran and produced output is a different thing from a caller that never "
                "ran, and that distinction is recorded rather than assumed.",
                "DepMap expression is weak corroboration in the same direction: NR4A3 sits at "
                "floor level in absolute terms, which is not what a line whose driver transcript "
                "carries the NR4A3 body under a partner promoter would read. The numbers have one "
                "home in emc-atr-vulnerability.json and are not copied here.",
                "Cellosaurus carries NO `CC Sequence variation: Gene fusion` line for CVCL_1238, "
                "while it carries one for each USZ model. The absence is visible in the record "
                "itself rather than inferred from the caution.",
                "NO source found anywhere reports a POSITIVE NR4A3 fusion in this line. A Europe "
                "PMC sweep of ('H-EMC-SS' OR 'HEMCSS' OR 'HEMC-SS') AND (NR4A3 OR EWSR1 OR "
                "'EWS/CHN' OR TAF15 OR fusion) returns hitCount 12, and not one abstract names the "
                "line at all — so the sweep bounds the abstract layer only, and is reported as "
                "that rather than as a proven absence.",
                "⚠ It is NOT an STR misidentification call. Cellosaurus records no `CC Problematic "
                "cell line:` line and carries an 18-locus STR profile from three independent "
                "sources, so this is a molecular-identity question about a real, profiled line.",
            ],
            "⛔_consequence_for_this_reagent_programme": (
                "Every reagent in this repository is a junction-spanning gapmer, and a gapmer needs "
                "a junction to span. So the one EMC line anyone can buy cannot test any of them — "
                "not because a reagent is missing but because the target is. The testable surface "
                "is the ENGINEERED tBJ/ER arms (E-N, T-N*, T-N — rebuildable from published exon "
                "spans, deposited nowhere) and the two USZ models (available on request from the "
                "University of Zurich, and only for those does a patient-derived test exist). "
                "⚠ This is a statement about a fusion-junction modality. It is NOT a claim that "
                "H-EMC-SS is useless, nor that it is not EMC — see the verdict home's own "
                "`_what_this_cannot_settle`."),
            "what_would_change_it": (
                "RT-PCR across an NR4A3 junction in H-EMC-SS, or an EWSR1 break-apart FISH reported "
                "with its probe. Either would settle in one experiment what four indirect sources "
                "currently agree on."),
        },

        "what_would_settle_the_acceptor": [
            "One RT-PCR/Sanger read across the junction in either USZ model, published or supplied "
            "— the same nucleotide-resolution confirmation §5.4 of the manuscript already requires "
            "before any reagent is used.",
            "The FoundationOne®HEME report's own transcript reference for NR4A3, which would say "
            "whether its exon indices are RefSeq transcript indices or breakpoint-flanking labels.",
            "Supplementary Table 1 of PMC9813045 — Europe PMC supplementaryFiles returned HTTP 200 "
            "with 0 bytes after three paced retries, which is an unanswered question rather than an "
            "empty one.",
        ],
    }
    if "--check" in argv:
        if not os.path.exists(OUT):
            print(f"emc-model-junction-evidence --check: MISSING {OUT}")
            return 1
        with open(OUT, encoding="utf-8") as fh:
            if json.load(fh) != art:
                print("emc-model-junction-evidence --check: STALE — re-run "
                      "emc_model_junction_evidence.py")
                return 1
        print("emc-model-junction-evidence --check: OK")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    print("  validation all agree:", art["⭐_the_deriver_and_its_validation"][
        "all_validation_cases_agree"])
    for r in art["⭐_is_there_any_NR4A3_numbering_that_makes_exon_2_the_coding_acceptor"]["_result"]:
        print(f"  {r['refseq']}  {r['n_exons']} exons  CDS starts in exon "
              f"{r['exon_containing_cdsStart_1based']}  leading non-coding exons "
              f"{r['n_leading_noncoding_exons_by_exonFrames']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
