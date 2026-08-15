#!/usr/bin/env python3
"""Is the TCF12::NR4A3 breakpoint REPORTED, or inferred from a residue count?

⛔ WHY THIS EXISTS, AND WHAT IT SETTLES. The junction-ASO coverage ladder cannot cross 95% without
the *TCF12* arm (`aso_coverage_ladder.py`), and that arm's exon was an INFERENCE: the primary report
describes the chimera as retaining "the first 108 amino acids" of TCF12 (PMID 11156374), and this
repository converted that residue count against its own transcript model. A conversion is not a
report, so the ladder's top row was a bound resting on an unverified assignment, and the manuscript
said so in terms.

⭐ IT IS NO LONGER AN INFERENCE. The authors of that report also DEPOSITED the chimeric cDNA:
GenBank **AF289510.1**, 421 bp, "Homo sapiens TCF12-TEC fusion protein mRNA, partial cds", submitted
25-JUL-2000 and citing PMID 11156374. Its two chromosome-tagged `source` features split the record
AT the junction — bases 1..263 are chromosome 15 (15q21, *TCF12*) and 264..421 are chromosome 9
(9q22, *TEC*/*NR4A3*) — so the deposit resolves the breakpoint to the NUCLEOTIDE, not to an exon
label that would need a model to interpret.

⛔ WHY 295 + 104 RETRIEVED PAPERS MISSED IT, WHICH IS THE TRANSFERABLE LESSON. The breakpoint was
never published as an exon in prose. It was deposited. No literature sweep of any width reaches a
sequence database, and the two routes that do reach it are cheap: NCBI `elink` from the report's
PubMed record to `nuccore`, and a `nuccore` term search. Both return exactly one record here.
⚠ A CORPUS SWEEP RETURNING NOTHING IS EVIDENCE ABOUT THE CORPUS, NOT ABOUT THE WORLD.
⚠ AND THIS REPOSITORY HAD ALREADY PAID FOR THAT LESSON ONCE, a week earlier and in another lane:
`nr4a3-fusion-transcriptional-output.md` retracted "no genome-wide chromatin experiment ... was
retrieved in 2,276 full-text documents across five corpora" on 2026-08-08 when a search of the
primary sequence archives — rather than of the literature alone — returned GEO GSE243553, whose
library carries a TCF12-NR4A3 construct among others. Same failure, same fix, same partner. The
corpus counts were right both times; the inference from them to an absence was not.

WHAT THIS MODULE DOES. It re-derives the assignment from the two committed inputs and refuses to
restate any of it from prose:
  A. the deposited donor side ends at exactly one *TCF12* exon boundary — and which;
  B. the deposited acceptor side begins at exactly one *NR4A3* exon boundary — and which;
  C. the deposited seam equals, base for base, the seam the design panel was built on;
  D. translating the deposit reproduces the deposited protein, which is a substring of the modelled
     chimera; and the modelled chimera retains exactly 108 leading *TCF12* residues, then a HYBRID
     codon, then the entire *NR4A3* protein — the abstract's two independent clauses at once;
  E. the residue-108 arithmetic that was the OLD basis, kept and re-run, because "the inference was
     right" is a different statement from "the inference is no longer what we rest on".

WHAT THIS IS NOT.
  · Not a within-partner breakpoint DISTRIBUTION, and the difference decides the coverage ladder.
    This is ONE sequenced tumour. Neither breakpoint series behind the ladder contains a
    TCF12-rearranged tumour at all, so nothing here says how the OTHER TCF12 case in the 58-case
    partner cohort breaks. The *TCF12* arm stays priced at its ceiling — for this reason now,
    rather than for an unverified exon.
  · Not an efficacy or coverage claim. A confirmed junction is a target, not a result.
  · Not a re-annotation of TCF12. The exon NUMBER is read against the committed transcript model
    (ENST00000333725, 21 transcript exons); the seam SEQUENCE is what the deposit itself carries and
    is the transcript-model-independent fact. A design hybridises to the seam, not to the label.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.join(HERE, os.pardir, "modalities")
SOURCES = os.path.join(HERE, os.pardir, "literature",
                       "tcf12-nr4a3-breakpoint-primary-sources.json")
OUT = os.path.join(HERE, "aso", "tcf12-breakpoint-assignment.json")

#: The junction this repository designs at, named once.
JUNCTION = "TCF12_e5__NR4A3_e3"


def _models():
    """The committed transcript models, read through the lane's own gated loader.

    ⛔ `TRANSCRIPT_SOURCE=cache` IS DELIBERATE AND IS NOT A SHORTCUT. This module must produce the
    same answer in CI, in the sandbox and on a runner, and a live Ensembl read that silently
    re-annotated an exon would change an assignment the manuscript quotes. The loader's four
    self-checks and its exon-audit gate still run on the cached model; what is excluded is the
    network, not the checking.
    """
    sys.path.insert(0, os.path.abspath(MODALITIES))
    os.environ["TRANSCRIPT_SOURCE"] = "cache"
    import junction_aso as JA  # noqa: E402
    return JA


def _deposit():
    """Accession, sequence and the junction position, parsed from the committed GenBank flat file.

    ⛔ THE JUNCTION IS READ FROM THE CHROMOSOME-TAGGED `source` FEATURES, AND THE PARSE IS THE PART
    THAT CAN GO WRONG SILENTLY. This record carries THREE `source` features: one spanning the whole
    421 bp with no chromosome, then 1..263 on chromosome 15 and 264..421 on chromosome 9. A
    non-greedy span from the first `source` to the first `/chromosome=` runs straight through the
    whole-length feature and reports the entire record as chromosome 15 — which puts the "junction"
    at the end of the record and makes every downstream test vacuously true rather than failing.
    Measured while writing this: tests A and C both changed verdict on that one regex. So the
    features are split on the feature KEY, only blocks carrying BOTH a span and a `/chromosome=`
    are kept, and the count of them is asserted.
    """
    src = json.load(open(SOURCES, encoding="utf-8"))
    rec = next(r for r in src["records"] if r["kind"] == "sequence_deposit")
    raw = rec["genbank_flatfile_verbatim"]

    origin = raw.split("ORIGIN", 1)[1].split("//", 1)[0]
    seq = "".join(re.findall(r"[acgtn]+", origin)).upper()
    stated_len = int(re.search(r"^LOCUS\s+\S+\s+(\d+)\s+bp", raw, re.M).group(1))
    if len(seq) != stated_len:
        raise RuntimeError(f"{rec['version']}: ORIGIN parses to {len(seq)} nt, LOCUS states "
                           f"{stated_len} — refusing to map a sequence we cannot read whole")

    feat = raw.split("FEATURES", 1)[1].split("ORIGIN", 1)[0]
    blocks = re.split(r"\n(?=\s*(?:source|CDS|gene|misc_feature)\s)", feat)
    tagged = []
    for b in blocks:
        span = re.match(r"\s*source\s+(\d+)\.\.(\d+)", b)
        chrom = re.search(r'/chromosome="(\d+)"', b)
        if span and chrom:
            tagged.append((int(span.group(1)), int(span.group(2)), chrom.group(1)))
    if len(tagged) != 2:
        raise RuntimeError(f"{rec['version']}: expected exactly two chromosome-tagged source "
                           f"features, parsed {len(tagged)} — the junction is defined by their "
                           "boundary, so any other count means the parse is wrong")
    (a_start, a_end, a_chr), (b_start, b_end, b_chr) = tagged
    if a_start != 1 or b_start != a_end + 1 or b_end != len(seq):
        raise RuntimeError(f"{rec['version']}: the two source features do not tile the record "
                           f"({tagged}) — refusing to infer a junction from a gapped annotation")

    prot = "".join(re.findall(r"[A-Z]+", re.search(r'/translation="([^"]+)"', raw, re.S).group(1)))
    return {
        "accession_version": rec["version"], "ncbi_nuccore_uid": rec["ncbi_nuccore_uid"],
        "definition": rec["definition"], "cites_pmid": rec["cites_pmid"],
        "length_bp": len(seq), "sequence": seq,
        "junction_after_base": a_end,
        "donor_side": {"span_1based": [a_start, a_end], "chromosome": a_chr,
                       "map": re.search(r'/map="([^"]+)"', raw.split("FEATURES", 1)[1]).group(1)},
        "acceptor_side": {"span_1based": [b_start, b_end], "chromosome": b_chr},
        "codon_start": int(re.search(r"/codon_start=(\d+)", raw).group(1)),
        "protein_id": rec["protein_id"], "deposited_translation": prot,
    }


def _residue_arithmetic(JA, model):
    """Complete residues encoded through each transcript exon — the OLD, inference-only basis.

    Kept and re-run rather than deleted. It is now a CHECK on the deposit rather than the evidence
    for the assignment, and the two answering the same is worth more than either alone.
    """
    coding, cum, rows = JA.coding_nt_per_exon(model), 0, []
    for rank, nt in enumerate(coding, start=1):
        cum += nt
        rows.append({"transcript_exon": rank, "coding_nt_in_exon": nt,
                     "cumulative_coding_nt": cum,
                     "complete_residues_through_this_exon": cum // 3,
                     "nt_into_the_next_codon": cum % 3})
    return rows


def build():
    JA = _models()
    tcf, nr4 = JA.transcript_model("TCF12"), JA.transcript_model("NR4A3")
    dep = _deposit()
    seq, j = dep["sequence"], dep["junction_after_base"]
    left, right = seq[:j], seq[j:]

    # -- A: which TCF12 exon END does the deposited donor side stop at? ------------------------
    donor_exons = [e for e in range(1, len(tcf["tx_ends"]) + 1)
                   if tcf["cdna"][:JA.exon_tx_end(tcf, e)].endswith(left)]
    # -- B: which NR4A3 exon START does the deposited acceptor side begin at? ------------------
    acceptor_exons = [a for a in range(1, len(nr4["tx_ends"]) + 1)
                      if nr4["cdna"][JA.exon_tx_start(nr4, a):].startswith(right)]

    # -- C: does the deposit's seam equal the seam the panel designed on? ----------------------
    graded = JA.mrna_junction_generic(tcf, nr4, donor_exons[0], acceptor_exons[0]) \
        if len(donor_exons) == 1 and len(acceptor_exons) == 1 else None
    deposited_seam = f"{left[-12:]}|{right[:12]}"

    # -- D: the protein ------------------------------------------------------------------------
    import fusion_breakpoints as fb  # noqa: E402  — the lane's own translator
    our_translation = fb.translate(seq[dep["codon_start"] - 1:])[:len(dep["deposited_translation"])]
    tprot = tcf["protein"].replace("*", "").rstrip("X")
    nprot = nr4["protein"].replace("*", "").rstrip("X")
    chim = None
    leading = span = None
    if graded is not None:
        whole = (tcf["cdna"][:JA.exon_tx_end(tcf, donor_exons[0])]
                 + nr4["cdna"][JA.exon_tx_start(nr4, acceptor_exons[0]):])
        chim = fb.translate(whole[tcf["utr5_len"]:]).split("*")[0]
        leading = 0
        while leading < min(len(chim), len(tprot)) and chim[leading] == tprot[leading]:
            leading += 1
        if dep["deposited_translation"] in chim:
            s = chim.index(dep["deposited_translation"])
            span = [s + 1, s + len(dep["deposited_translation"])]

    # -- E: the residue arithmetic that used to be the whole basis ------------------------------
    rows = _residue_arithmetic(JA, tcf)
    at_108 = [r["transcript_exon"] for r in rows if r["complete_residues_through_this_exon"] == 108]

    src = json.load(open(SOURCES, encoding="utf-8"))
    by_kind = {r["kind"]: r for r in src["records"]}
    confirmed = (len(donor_exons) == 1 and len(acceptor_exons) == 1
                 and graded is not None
                 and graded["junction_context_mRNA"] == deposited_seam
                 and our_translation == dep["deposited_translation"])

    return {
        "_what": ("Whether the TCF12::NR4A3 breakpoint this repository designs at is REPORTED or "
                  "inferred, re-derived from the deposited chimeric cDNA and the committed "
                  "transcript models."),
        "_why": ("The junction-ASO coverage ladder cannot cross 95% without the TCF12 arm, and that "
                 "arm's exon was converted from a residue count rather than reported. This settles "
                 "which it is."),
        "_what_this_is_not": src["_what_this_is_not"],
        "_cost": "$0 — arithmetic over committed artifacts; the retrieval behind them was one free "
                 "runner dispatch.",
        "⭐_verdict": (
            f"REPORTED, AT NUCLEOTIDE RESOLUTION — no longer an inference. {dep['accession_version']} "
            f"splits at base {j}|{j + 1} into a chromosome {dep['donor_side']['chromosome']} "
            f"(TCF12) and a chromosome {dep['acceptor_side']['chromosome']} (NR4A3) side, and that "
            f"seam lands on TCF12 transcript exon {donor_exons[0]} joined to NR4A3 transcript exon "
            f"{acceptor_exons[0]} — one exon boundary on each side and no other."
            if confirmed else
            "⛔ NOT CONFIRMED by this run — read the tests below before quoting anything."),
        "⚠_what_the_verdict_does_not_license": (
            "The arm is still priced at its CEILING in the coverage ladder, and the reason has "
            "CHANGED rather than gone away. Before: the exon was unverified. Now: the exon is "
            "verified from ONE sequenced tumour, and no series has resolved a second "
            "TCF12-rearranged tumour, so nothing measures whether this junction recurs across the "
            "two TCF12 cases of the 58-case partner cohort. A confirmed junction raises the floor "
            "under the design; it does not measure the arm."),
        "deposit": {k: v for k, v in dep.items() if k != "sequence"},
        "sources": {
            "sequence_deposit": {k: by_kind["sequence_deposit"][k] for k in
                                 ("accession", "version", "ncbi_nuccore_uid", "definition",
                                  "length_bp", "protein_id", "submitted", "cites_pmid",
                                  "sha256_of_flatfile", "source_url")},
            "primary_report": {k: by_kind["primary_report"][k] for k in
                               ("pmid", "title", "journal", "year", "abstract_verbatim")},
            "corroborating_primary": {k: by_kind["corroborating_primary"][k] for k in
                                      ("pmid", "title", "journal", "year", "abstract_verbatim",
                                       "role")},
            "secondary_review": {k: by_kind["secondary_review"][k] for k in
                                 ("pmid", "pmcid", "verbatim", "role")},
            "_one_home": "research/literature/tcf12-nr4a3-breakpoint-primary-sources.json",
        },
        "transcript_models": {
            "TCF12": {"transcript": tcf["transcript"], "n_transcript_exons": len(tcf["tx_ends"]),
                      "protein_length": len(tprot),
                      "_agrees_with_the_corroborating_paper_on_exon_count": (
                          len(tcf["tx_ends"]) == 21)},
            "NR4A3": {"transcript": nr4["transcript"], "n_transcript_exons": len(nr4["tx_ends"]),
                      "protein_length": len(nprot)},
            "source": JA.transcript_source_provenance(),
            "provenance_gate_used": dict(JA.PROVENANCE_GATE_USED),
        },
        "tests": {
            "A_donor_side_ends_at_exactly_one_TCF12_exon": {
                "_method": ("The deposit's chromosome-15 side must be a SUFFIX of the TCF12 cDNA "
                            "truncated at an exon boundary. Suffix, not substring: a fusion "
                            "transcript's donor side ends where the exon ends."),
                "exons_matching": donor_exons, "unique": len(donor_exons) == 1,
                "donor_side_length_nt": len(left)},
            "B_acceptor_side_starts_at_exactly_one_NR4A3_exon": {
                "_method": ("The deposit's chromosome-9 side must be a PREFIX of the NR4A3 cDNA "
                            "taken from an exon start, including any 5'UTR that exon carries — "
                            "which is what a fusion transcript actually contains."),
                "exons_matching": acceptor_exons, "unique": len(acceptor_exons) == 1,
                "acceptor_side_length_nt": len(right)},
            "C_the_deposited_seam_equals_the_seam_the_panel_designed_on": {
                "modelled_junction_label": graded["junction_label"] if graded else None,
                "modelled_seam": graded["junction_context_mRNA"] if graded else None,
                "deposited_seam": deposited_seam,
                "identical": bool(graded and graded["junction_context_mRNA"] == deposited_seam),
                "_why_this_is_the_load_bearing_one": (
                    "An exon LABEL depends on a transcript model; a seam does not. Every design in "
                    "the panel hybridises to twelve bases either side of this seam, so a seam that "
                    "matches the deposit base for base is the statement that matters for a reagent, "
                    "and it survives any future re-annotation of TCF12's exon numbering.")},
            "D_the_protein": {
                "our_translation_reproduces_the_deposited_one": (
                    our_translation == dep["deposited_translation"]),
                "deposited_protein_length_aa": len(dep["deposited_translation"]),
                "deposited_protein_is_a_substring_of_the_modelled_chimera": span is not None,
                "spans_chimera_residues": span,
                "modelled_chimera_length_aa": len(chim) if chim else None,
                "leading_residues_identical_to_TCF12": leading,
                "residue_at_the_seam": {
                    "position": (leading + 1) if leading is not None else None,
                    "in_the_chimera": chim[leading] if chim and leading is not None else None,
                    "in_TCF12": tprot[leading] if leading is not None else None,
                    "_what_it_is": ("a HYBRID codon. TCF12 exon 5 ends one nucleotide into codon "
                                    "109, so the chimera keeps 108 whole TCF12 residues and then "
                                    "one codon built from both genes — which is exactly what a "
                                    "report of 'the first 108 amino acids' describes.")},
                "chimera_ends_with_the_entire_NR4A3_protein": bool(chim and chim.endswith(nprot)),
                "_why_both_clauses_matter": (
                    "The abstract makes TWO claims — 'the first 108 amino acids' of TCF12, and 'the "
                    "entire TEC protein'. The residue count alone constrains only the donor side. "
                    "The modelled junction satisfies both at once, and the second is what pins the "
                    "ACCEPTOR exon.")},
            "E_the_residue_arithmetic_that_used_to_be_the_only_basis": {
                "_question": ("Which TCF12 transcript exon boundary leaves exactly 108 COMPLETE "
                              "residues? This was the whole of the old evidence."),
                "per_exon": rows[:8],
                "exons_leaving_exactly_108_complete_residues": at_108,
                "unique": len(at_108) == 1,
                "_reading": (
                    "Cumulative coding nt through TCF12 exon 5 is 325. 108 whole codons are 324 nt, "
                    "so the exon ends ONE nucleotide into codon 109 — 108 complete residues and a "
                    "hybrid codon. The neighbouring boundaries leave 74 (exon 4) and 130 (exon 6), "
                    "so no other exon is close. ⚠ THE INFERENCE WAS CORRECT, AND THAT IS NOT WHY "
                    "THE ASSIGNMENT NOW STANDS: it stands on the deposit. An inference that turns "
                    "out right is still an inference, and the difference is what a reader is "
                    "entitled to know."),
                "⚠_what_this_arithmetic_could_never_have_settled": (
                    "Residue numbering is isoform-dependent. It happens to be safe here — the "
                    "committed Ensembl protein and UniProt Q99081 are identical over their first "
                    "396 residues, so residue 108 is the same residue in both — but that is a "
                    "property this repository checked, not one the source stated."),
            },
        },
        "what_changes_downstream": [
            {"file": "research/modalities/aso_per_junction_table.py",
             "change": (f"{JUNCTION} moves from clinical tier "
                        "`no_published_exon_resolved_breakpoint` to "
                        "`published_exon_resolved_breakpoint`, and TCF12 joins the partners with "
                        "any published exon — so its OTHER seven junctions become `this exon not "
                        "reported` rather than merely unreported.")},
            {"file": "research/manuscripts/aso_coverage_ladder.py",
             "change": ("the top row stays a BOUND, and its reason is rewritten: the exon is no "
                        "longer unverified, the within-partner distribution is still unmeasured at "
                        "n=1.")},
            {"file": "research/manuscripts/aso/fusion-junction-aso-research-article.md",
             "change": ("§3.3 and the Limitations must stop calling the TCF12 exon an inference "
                        "from a residue count.")},
        ],
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("tcf12-breakpoint-assignment.json is stale; re-run without --check",
                  file=sys.stderr)
            return 1
        print("tcf12-breakpoint-assignment artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    t = art["tests"]
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    print(f"  A donor exon(s)   : {t['A_donor_side_ends_at_exactly_one_TCF12_exon']['exons_matching']}",
          file=sys.stderr)
    print(f"  B acceptor exon(s): "
          f"{t['B_acceptor_side_starts_at_exactly_one_NR4A3_exon']['exons_matching']}",
          file=sys.stderr)
    print(f"  C seam identical  : "
          f"{t['C_the_deposited_seam_equals_the_seam_the_panel_designed_on']['identical']}",
          file=sys.stderr)
    print(f"  D translation ok  : "
          f"{t['D_the_protein']['our_translation_reproduces_the_deposited_one']}, "
          f"leading TCF12 residues "
          f"{t['D_the_protein']['leading_residues_identical_to_TCF12']}", file=sys.stderr)
    print(f"  E 108-residue exon: "
          f"{t['E_the_residue_arithmetic_that_used_to_be_the_only_basis']['exons_leaving_exactly_108_complete_residues']}",
          file=sys.stderr)
    print(f"  {art['⭐_verdict']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
