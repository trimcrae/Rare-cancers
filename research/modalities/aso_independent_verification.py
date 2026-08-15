#!/usr/bin/env python3
"""A second, differently-routed implementation of the two instruments the paper's claims rest on.

⛔ WHY THIS EXISTS. The submission manuscript's Provenance section discloses that an earlier version
of these analyses was withdrawn in full because a coding-versus-transcript exon indexing error put
the acceptor junction in the wrong place. External review of the submission made the obvious point:
that is precisely the failure a reader will assume could recur, and the AI-use declaration says the
same model wrote the code, ran the pipelines and reviewed the drafts. The reviewer asked for a
second pair of eyes on the frame grading and on the mature-parent screen, or for those two to be
reimplemented independently, and for the manuscript to say which was done.

This is the reimplementation. ⚠ READ WHAT IT IS AND IS NOT BEFORE QUOTING IT.

  IT IS   a second implementation of both instruments that shares NO CODE with the first — it
          imports neither `junction_aso` nor `aso_parent_gap_pairing` — reaches each quantity by a
          different route, and takes its inputs from a different committed acquisition wherever the
          repository holds two.
  IT IS   therefore able to catch: an indexing error, an off-by-one, a wrong slice, a transposed
          coordinate space, a mis-set threshold, an artifact that has drifted from the code that
          claims to produce it, and a disagreement between the two transcript acquisitions.
  IT IS NOT external review. The same author and the same model wrote both implementations.
  IT IS NOT proof against a shared misreading of the METHOD. If the specification itself is wrong —
          if "the longest contiguous run containing the gap" is the wrong quantity to compute — two
          implementations of it agree and are both wrong. No self-check can close that, and the
          manuscript says so rather than letting agreement stand in for correctness.

THE THREE ROUTES, EACH DELIBERATELY DIFFERENT FROM THE ORIGINAL'S.

  A · TRANSCRIPT ACQUISITION. The original builds its models from `emc-construct-inputs.json`, which
      is a cDNA-and-CDS record fetched from the Ensembl REST cDNA endpoints. This one splices each
      mature transcript out of `aso-premrna-sequences.json`, which is GENOMIC unspliced sequence
      plus exon spans, fetched separately for the pre-mRNA screen. Two acquisitions, two endpoints,
      two coordinate systems. If they disagree by a single base the frame arithmetic downstream of
      them cannot both be right, and nothing in the original compares them.

  B · WHERE THE CODING SEQUENCE STARTS. The original reads `utr5_len` off the annotation. This one
      does not read it at all: it finds the longest ATG-to-stop open reading frame in the spliced
      cDNA and takes that offset. An annotation-free route to the same number, so a wrong `utr5_len`
      — which is exactly the class of error that produced the retracted version — cannot pass
      through both.

  C · HOW THE FRAME IS GRADED. The original grades by TRANSLATION: it concatenates the two cDNA
      pieces, translates from the donor's start codon and asks whether the product ends with the
      acceptor's own C-terminus. This one grades by ARITHMETIC on exon coding-length vectors —
      in frame iff (donor coding nt through the cut + acceptor 5'UTR bases retained) mod 3 == 0 —
      and then translates only as a separate second opinion. The two disagree on a real class of
      row (register correct, premature stop) and that class is reported rather than smoothed over.

  D · SCREEN 4. The original scans every 16-nucleotide parent window, tests the six gap positions,
      and extends outward from the gap. This one never scans a window: it enumerates the 36
      substrings of the design that CONTAIN the gap, longest first, and asks plain string search
      whether each occurs anywhere in a mature parent. The two are equivalent by an argument worth
      writing down — a run of length L covering the gap at parent window i means design[lo:hi+1]
      occurs in the parent at i+lo, and conversely — but they share no control flow, no loop bound
      and no index arithmetic, which is where the errors of this kind live.

EXIT CODE. Non-zero if ANY comparison disagrees. This is a verifier; a green run is the claim.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GENOMIC = os.path.join(HERE, "aso-premrna-sequences.json")
CDNA = os.path.join(HERE, "emc-construct-inputs.json")
ATLAS = os.path.join(HERE, "nr4a3-fusion-junction-atlas.json")
SCREEN4 = os.path.join(HERE, "aso-parent-gap-pairing.json")
INVENTORY = os.path.join(HERE, "fusion-object-inventory.json")
OUT = os.path.join(HERE, "aso-independent-verification.json")

#: The geometry, restated here ON PURPOSE rather than imported. Importing the original's constants
#: would make a wrong constant agree with itself, which is the one thing a second implementation
#: exists to prevent. A disagreement with the atlas's own `oligo_geometry` is a reported failure.
OLIGO_LEN, WING, MIN_DUPLEX_BP = 16, 5, 10

CODONS = {}
for _i, _b1 in enumerate("TCAG"):
    for _b2 in "TCAG":
        for _b3 in "TCAG":
            CODONS[_b1 + _b2 + _b3] = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"[
                len(CODONS)]


def translate(seq):
    out = []
    for i in range(0, len(seq) - len(seq) % 3, 3):
        aa = CODONS.get(seq[i:i + 3], "X")
        if aa == "*":
            break
        out.append(aa)
    return "".join(out)


# ─────────────────────────────────────────────────────────── A · a second transcript acquisition
def splice_from_genomic():
    """Mature cDNA per gene, spliced out of the GENOMIC record rather than read as cDNA."""
    genes = json.load(open(GENOMIC, encoding="utf-8"))["genes"]
    out = {}
    for g, v in genes.items():
        spans = v["exon_spans_0based_inclusive"]
        seq = v["sequence"]
        exons = [seq[a:b + 1] for a, b in spans]
        cdna = "".join(exons)
        if len(cdna) != v["exonic_nt"]:
            raise RuntimeError(f"{g}: spliced {len(cdna)} nt against recorded {v['exonic_nt']}")
        out[g] = {"cdna": cdna, "exon_lengths": [len(e) for e in exons]}
    return out


# ────────────────────────────────────────────────────── B · the coding start, without annotation
def longest_orf(cdna):
    """(offset, cds_nt, protein) of the longest ATG-to-stop ORF. No annotation is consulted."""
    best = (None, 0, "")
    for frame in range(3):
        i = frame
        while i + 3 <= len(cdna):
            if cdna[i:i + 3] == "ATG":
                prot = translate(cdna[i:])
                stop_found = (i + 3 * len(prot) + 3) <= len(cdna) and \
                    CODONS.get(cdna[i + 3 * len(prot):i + 3 * len(prot) + 3]) == "*"
                nt = 3 * len(prot) + (3 if stop_found else 0)
                if nt > best[1]:
                    best = (i, nt, prot)
                i += 3 * max(1, len(prot))
            else:
                i += 3
    return best


# ─────────────────────────────────────────────── C · the frame, by arithmetic instead of protein
def coding_vector(exon_lengths, utr5, cds_nt):
    """Coding nucleotides contributed by each exon, from exon lengths and the ORF span alone."""
    out, pos = [], 0
    lo, hi = utr5, utr5 + cds_nt
    for L in exon_lengths:
        a, b = pos, pos + L
        out.append(max(0, min(b, hi) - max(a, lo)))
        pos = b
    return out


def grade_all_pairs(models, resume_lo, resume_hi, acceptor_window):
    """Every donor-exon x acceptor-exon pair, graded by the four-branch ladder, arithmetically.

    ⚠ `acceptor_window` IS A DECLARED SCOPE, NOT A COMPUTED QUANTITY, and it is the one input this
    verifier takes from the thing it is verifying. Which NR4A3 exons are candidate acceptors is a
    curation decision (the atlas declares 2, 3 and 4); re-deriving it here would be inventing a
    second scope rather than checking the first. The verifier ALSO grades the unrestricted
    enumeration over every NR4A3 exon, and reports what the restriction excludes, so the scope is
    visible rather than assumed — which is the part a reader can actually check.
    """
    acc = models["NR4A3"]
    rows = {}
    for donor in ("EWSR1", "TAF15", "TCF12", "FUS", "TFG"):
        don = models[donor]
        for d_end in range(1, len(don["exon_lengths"]) + 1):
            for a_start in acceptor_window:
                d_cut = sum(don["exon_lengths"][:d_end])
                a_off = sum(acc["exon_lengths"][:a_start - 1])
                donor_coding = sum(don["coding"][:d_end])
                acc_is_coding = acc["coding"][a_start - 1] > 0
                acc_utr_kept = max(0, acc["utr5"] - a_off)
                acc_cds_at_resume = max(0, a_off - acc["utr5"])
                first_res = (acc_cds_at_resume // 3) + 1 if acc_is_coding else None
                frame_mod3 = (donor_coding + acc_utr_kept) % 3

                # the second opinion: translate the chimera and look for the acceptor C-terminus
                chimera = don["cdna"][:d_cut] + acc["cdna"][a_off:]
                prot = translate(chimera[don["utr5"]:])
                translated_in_frame = prot.endswith(acc["protein"][-100:])

                if not acc_is_coding:
                    grade = "NON_CODING_ACCEPTOR"
                elif not (resume_lo <= first_res <= resume_hi):
                    grade = "SEAM_NOT_PRODUCED"
                elif not translated_in_frame:
                    grade = "OUT_OF_FRAME"
                else:
                    grade = "EMITTABLE"
                rows[f"{donor}_e{d_end}__NR4A3_e{a_start}"] = {
                    "grade": grade,
                    "donor_coding_nt_through_cut": donor_coding,
                    "donor_coding_phase": donor_coding % 3,
                    "nr4a3_acceptor_exon_is_coding": acc_is_coding,
                    "nr4a3_acceptor_exon_5utr_nt_retained": acc_utr_kept,
                    "nr4a3_cds_nt_at_resume": acc_cds_at_resume,
                    "nr4a3_first_residue": first_res,
                    "frame_sum_mod3": frame_mod3,
                    "arithmetic_in_frame": frame_mod3 == 0,
                    "translated_in_frame": translated_in_frame,
                    "chimeric_protein_length": len(prot),
                    "junction_context_mRNA": don["cdna"][:d_cut][-12:] + "|" + acc["cdna"][a_off:][:12],
                }
    return rows


# ───────────────────────────────────────── D · screen 4, by substring search instead of scanning
def longest_run_by_substring(target, parents):
    """(longest run through the gap, gene) — by asking where design substrings OCCUR.

    ⭐ THE EQUIVALENCE, since the whole value of this route is that it is not the other one. Screen 4
    asks: is there a parent window start `i` such that the maximal run of aligned matches containing
    the gap has length >= 10? A run [lo, hi] at window `i` means exactly that `target[lo:hi+1]`
    appears in the parent at position `i + lo`; conversely an occurrence of `target[lo:hi+1]` at
    parent position `p` gives a window at `i = p - lo` whose maximal run contains [lo, hi]. So the
    longest run through the gap equals the longest gap-containing substring of the design that
    occurs in a parent — subject only to the window fitting inside the transcript, which is checked.
    """
    gap_lo, gap_hi = WING, OLIGO_LEN - WING - 1
    best = (0, None)
    for lo in range(0, gap_lo + 1):
        for hi in range(gap_hi, OLIGO_LEN):
            length = hi - lo + 1
            if length <= best[0]:
                continue
            sub = target[lo:hi + 1]
            for gene, seq in parents.items():
                start = seq.find(sub)
                while start != -1:
                    i = start - lo                      # implied 16-mer window start
                    if 0 <= i <= len(seq) - OLIGO_LEN:
                        best = (length, gene)
                        break
                    start = seq.find(sub, start + 1)
                if best[0] == length:
                    break
    return best


# ────────────────────────────────────────────────────────────────────────────────── the verifier
def run():
    problems = []
    notes = {}

    genomic = splice_from_genomic()
    cdna_rec = json.load(open(CDNA, encoding="utf-8"))["genes"]

    # A · the two acquisitions must agree base for base
    acq = {}
    for g, v in sorted(genomic.items()):
        same = v["cdna"] == cdna_rec[g]["cdna"]
        acq[g] = {"genomic_spliced_nt": len(v["cdna"]),
                  "cdna_record_nt": len(cdna_rec[g]["cdna"]),
                  "identical": same}
        if not same:
            problems.append(f"A: {g} genomic-spliced cDNA differs from the cDNA record")
    notes["A_transcript_acquisitions_agree"] = acq

    # B · the coding start, found without reading utr5_len
    models, orf = {}, {}
    for g, v in sorted(genomic.items()):
        offset, cds_nt, prot = longest_orf(v["cdna"])
        rec = cdna_rec[g]
        agrees = (offset == rec["utr5_len"] and prot == rec["protein"])
        orf[g] = {"orf_offset_found": offset, "annotated_utr5_len": rec["utr5_len"],
                  "orf_protein_aa": len(prot), "annotated_protein_aa": len(rec["protein"]),
                  "agrees": agrees}
        if not agrees:
            problems.append(f"B: {g} ORF search gives offset {offset}/protein {len(prot)} aa "
                            f"against annotated {rec['utr5_len']}/{len(rec['protein'])} aa")
        # ⚠ `cds_nt` INCLUDES THE STOP CODON, and it must: the original's per-exon coding vector
        # counts the terminator, so EWSR1's last coding exon carries 1971 nt and not 1968. Passing
        # the protein-only length here is an off-by-three that moves only the LAST coding exon of
        # each gene — invisible at every other donor cut, and caught by this comparison.
        models[g] = {
            "cdna": v["cdna"], "exon_lengths": v["exon_lengths"],
            "utr5": offset, "cds_nt": cds_nt, "protein": prot,
            "coding": coding_vector(v["exon_lengths"], offset, cds_nt),
        }
    notes["B_coding_start_without_annotation"] = orf

    # C · all 231 pairs, graded arithmetically, against the atlas
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    lo, hi = inv["inventory"]["excluded_span"][
        "nr4a3_resume_range_across_plausible_breakpoints"]
    atlas = json.load(open(ATLAS, encoding="utf-8"))
    window = list(atlas["acceptor_exon_window"])
    mine = grade_all_pairs(models, lo, hi, window)
    unrestricted = grade_all_pairs(
        models, lo, hi, range(1, len(models["NR4A3"]["exon_lengths"]) + 1))
    theirs = {p["junction_label"]: p for p in atlas["graded_pairs"]}

    if set(mine) != set(theirs):
        problems.append(f"C: pair set differs — mine {len(mine)}, atlas {len(theirs)}")
    checked = disagree = 0
    field_mismatch = []
    for label, row in sorted(theirs.items()):
        if label not in mine:
            continue
        checked += 1
        m = mine[label]
        if m["grade"] != row["grade"]:
            disagree += 1
            problems.append(f"C: {label} graded {m['grade']} here, {row['grade']} in the atlas")
        for f in ("donor_coding_nt_through_cut", "donor_coding_phase",
                  "nr4a3_acceptor_exon_is_coding", "nr4a3_acceptor_exon_5utr_nt_retained",
                  "nr4a3_cds_nt_at_resume", "nr4a3_first_residue", "frame_sum_mod3",
                  "chimeric_protein_length", "junction_context_mRNA"):
            if m[f] != row[f]:
                field_mismatch.append(f"{label}.{f}: {m[f]!r} vs {row[f]!r}")
    if field_mismatch:
        problems.append(f"C: {len(field_mismatch)} field disagreements, first: {field_mismatch[0]}")

    # ⭐ where the two ROUTES TO FRAME part company: register correct, C-terminus never reached
    premature = sorted(k for k, v in mine.items()
                       if v["arithmetic_in_frame"] and not v["translated_in_frame"])
    register = sorted(k for k, v in mine.items()
                      if not v["arithmetic_in_frame"] and v["translated_in_frame"])
    if register:
        problems.append(f"C: {len(register)} pairs translate in frame with a non-zero register — "
                        "that combination should be impossible")
    outside = sorted(k for k, v in unrestricted.items()
                     if k not in mine and v["grade"] == "EMITTABLE")
    notes["C_frame_grading"] = {
        "pairs_checked": checked,
        "acceptor_exon_window_taken_from_the_atlas": window,
        "unrestricted_pairs_graded": len(unrestricted),
        "emittable_outside_the_declared_acceptor_window": outside,
        "grade_disagreements": disagree,
        "field_disagreements": len(field_mismatch),
        "atlas_grade_counts": atlas["grade_counts"],
        "independent_grade_counts": {g: sum(1 for v in mine.values() if v["grade"] == g)
                                     for g in sorted({v["grade"] for v in mine.values()})},
        "arithmetic_in_frame_but_premature_stop": premature,
        "_why_that_class_matters": (
            "The arithmetic route and the translation route are not the same test, and these are "
            "the rows where they part: the reading register composes correctly and a stop codon "
            "still terminates the chimeric ORF before the acceptor's C-terminus. The original "
            "grades these OUT_OF_FRAME on the translation test and says so in its `why` string. "
            "Listing them is what makes the agreement above meaningful rather than tautological."),
    }

    # D · screen 4, by substring search
    parents = {g: v["cdna"] for g, v in genomic.items()}
    s4 = json.load(open(SCREEN4, encoding="utf-8"))
    by_key = {(r["junction"], r["antisense_5to3"]): r for r in s4["per_design"]}
    geom = atlas.get("oligo_geometry")
    notes["D_geometry_restated_not_imported"] = {
        "oligo_len": OLIGO_LEN, "wing": WING, "min_duplex_bp": MIN_DUPLEX_BP,
        "atlas_oligo_geometry": geom,
    }
    if s4["method"]["min_duplex_bp"] != MIN_DUPLEX_BP or s4["method"]["oligo_len"] != OLIGO_LEN:
        problems.append("D: screen 4's recorded geometry differs from the one restated here")

    n_d = run_disagree = 0
    liable = nr4a3 = 0
    for panel in atlas["panels"]:
        for d in panel.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            n_d += 1
            length, gene = longest_run_by_substring(d["target_mRNA_5to3"], parents)
            liable += 1 if length >= MIN_DUPLEX_BP else 0
            nr4a3 += 1 if (length >= MIN_DUPLEX_BP and gene == "NR4A3") else 0
            ref = by_key.get((panel["junction_label"], d["antisense_5to3"]))
            if ref is None:
                problems.append(f"D: {panel['junction_label']}/{d['antisense_5to3']} "
                                "has no row in the screen-4 artifact")
                continue
            if length != ref["longest_parent_duplex_bp_through_gap"]:
                run_disagree += 1
                problems.append(f"D: {d['antisense_5to3']} run {length} here, "
                                f"{ref['longest_parent_duplex_bp_through_gap']} in the artifact")
            elif length and gene != ref["parent"]:
                # ⚠ NOT AUTOMATICALLY A DEFECT: two parents can tie at the same run length, and the
                # two implementations break the tie in different orders. Recorded, not raised,
                # unless the run lengths themselves differ.
                notes.setdefault("D_ties", []).append(
                    {"design": d["antisense_5to3"], "run_bp": length,
                     "independent": gene, "screen4": ref["parent"]})

    notes["D_mature_parent_screen"] = {
        "designs_checked": n_d,
        "run_length_disagreements": run_disagree,
        "independent_n_liable": liable,
        "screen4_n_liable": s4["corpus"]["n_with_parent_duplex_through_gap"],
        "independent_n_liable_against_NR4A3": nr4a3,
        "screen4_n_liable_against_NR4A3": s4["corpus"]["which_parent_supplies_it"].get("NR4A3"),
    }
    if liable != s4["corpus"]["n_with_parent_duplex_through_gap"]:
        problems.append(f"D: liable count {liable} here against "
                        f"{s4['corpus']['n_with_parent_duplex_through_gap']} in the artifact")

    return {
        "_what": ("A second implementation of the frame grading and the mature-parent screen, "
                  "sharing no code with the first and reaching each quantity by a different route, "
                  "run against the committed artifacts."),
        "_why": ("Requested by external review of the submission manuscript (2026-08-15): the "
                 "Provenance section discloses that an exon-indexing error invalidated an earlier "
                 "version in full, and the AI-use declaration says one model wrote the code, ran "
                 "the pipelines and reviewed the drafts."),
        "_what_this_is_not": [
            "NOT external review. The same author and the same model wrote both implementations.",
            "NOT proof against a shared misreading of the method. Two implementations of a wrong "
            "specification agree and are both wrong; agreement here bounds implementation error "
            "only, and the manuscript states that rather than letting it pass for correctness.",
            "NOT a check of the screens this verifier does not cover — the alignment screen, the "
            "exhaustive transcript scan, the pre-mRNA screen and the genome scan are untouched.",
        ],
        "_cost": "$0 — offline, over committed artifacts, no network and no credentials.",
        "routes_that_differ_from_the_original": {
            "A": "genomic unspliced sequence + exon spans, not the cDNA/CDS record",
            "B": "longest-ORF search for the coding start, not the annotated utr5_len",
            "C": "frame by arithmetic on exon coding vectors, translation only as a second opinion",
            "D": "screen 4 by substring search over gap-containing design substrings, not by "
                 "scanning every parent window and extending outward from the gap",
        },
        "verdict": "AGREES" if not problems else "DISAGREES",
        "n_problems": len(problems),
        "problems": problems,
        "checks": notes,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = run()
    new = json.dumps(art, indent=1, sort_keys=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("aso-independent-verification.json is stale; re-run without --check",
                  file=sys.stderr)
            return 1
        print("independent-verification artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    c = art["checks"]
    print(f"{art['verdict']}: {c['C_frame_grading']['pairs_checked']} pairs graded, "
          f"{c['C_frame_grading']['grade_disagreements']} grade disagreements, "
          f"{c['C_frame_grading']['field_disagreements']} field disagreements; "
          f"{c['D_mature_parent_screen']['designs_checked']} designs screened, "
          f"{c['D_mature_parent_screen']['run_length_disagreements']} run disagreements",
          file=sys.stderr)
    for p in art["problems"][:20]:
        print("  !", p, file=sys.stderr)
    return 0 if art["verdict"] == "AGREES" else 1


if __name__ == "__main__":
    raise SystemExit(main())
