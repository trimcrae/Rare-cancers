#!/usr/bin/env python3
"""
A one-residue test that predicts where a fusion-junction novelty filter will fail, and its
validation against every transcript pair this locus can produce.

⛔ WHY THIS EXISTS, AND WHAT IT IS ANSWERING. §B5 of the vaccine manuscript reports that four
seam-proximal peptides of four of the five in-frame junctions occur in a normal NR4A3 isoform, and
names the cause: the upstream novelty filter compares candidates against the two CANONICAL parent
proteins, so an isoform carrying the seam sequence passes it unseen. The manuscript's prescription
was one sentence — "the filter should be made isoform-aware" — and an external reviewer of
aixiv.260822.000005 asked, correctly, for a concrete algorithmic fix rather than a diagnosis.

THE FIX IS CHEAPER THAN THE SEARCH IT REPLACES, AND IT IS A SINGLE CHARACTER COMPARISON.

A chimeric transcript's seam residue j0 is the first residue not encoded wholly by donor
nucleotides. Everything 3' of it is the acceptor's own sequence, retained whole. So a seam-proximal
peptide is `seam_residue + <acceptor stem>`. It collides with a normal protein exactly when some
isoform of the acceptor gene ALREADY places that same residue immediately 5' of that same stem —
which is what an alternative first exon does. The residues for which that is true form the acceptor's
COLLISION ALPHABET, and the whole test is:

    seam_residue in collision_alphabet  ->  the seam-proximal window is not tumour-exclusive

The alphabet is a property of the ACCEPTOR alone. It is computed once per acceptor gene, from that
gene's own isoform set, and then answers the question for every donor and every breakpoint without a
further search. That is the part that matters for a filter: the expensive proteome scan is O(peptides
x proteome) per junction, and this is O(isoforms) once.

⛔ WHAT THIS IS NOT. It is not a replacement for the proteome search, and using it as one would
reintroduce the defect from the other side. It predicts ONE failure mode — a seam-proximal peptide
reconstructing an acceptor isoform boundary — and says nothing about a peptide colliding with an
unrelated protein, nor about peptides that extend far enough into the donor to be novel again. In
this locus's own data the strong binder RGDMPCVQAQY carries the same stem and remains novel, because
it begins three residues 5' of the seam. The test is a cheap PRE-SCREEN that says where the search
will find something, and a filter that runs it still runs the search.

Output: novelty-seam-test.json
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOVELTY = os.path.join(HERE, "junction-proteome-novelty.json")
SENSITIVITY = os.path.join(HERE, "junction-transcript-sensitivity.json")
OUT = os.path.join(HERE, "novelty-seam-test.json")


def load(path, what):
    if not os.path.exists(path):
        raise SystemExit(f"{what} is missing at {path}. It is committed, so regenerate it rather "
                         "than writing an artifact that reports a validation nothing performed.")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def collision_alphabet(novelty):
    """The acceptor residues that reconstruct an isoform boundary, and the stem they precede.

    ⛔ DERIVED FROM THE SEARCH'S OWN HITS, NEVER TYPED. Each colliding peptide is
    `seam_residue + stem`; the residue is its first character and the stem is the rest. Reading them
    out of the committed hit list means the alphabet cannot come to disagree with the search that
    produced it, and it means this module states nothing the proteome search did not observe.
    """
    hits = [h for h in novelty["peptides_found_in_proteome"] if h["peptide"]]
    alphabet, stems, accessions = {}, {}, {}
    for h in hits:
        pep = h["peptide"]
        residue, stem = pep[0], pep[1:]
        alphabet.setdefault(residue, 0)
        alphabet[residue] += 1
        stems.setdefault(residue, set()).add(stem)
        for hit in h.get("proteome_hits", []):
            accessions.setdefault(residue, set()).add(hit["accession"])
    return (sorted(alphabet),
            {r: sorted(s) for r, s in stems.items()},
            {r: sorted(a) for r, a in accessions.items()})


def confusion(pairs, alphabet):
    """The one-residue test against the observed collision, over every in-frame transcript pair.

    ⛔ IN-FRAME PAIRS ONLY, AND THE DENOMINATOR IS STATED. A pair that emits no seam has no seam
    residue to test, so scoring it as a correct negative would inflate the specificity with cases the
    test was never asked about — the same error as counting an unmeasured allele as absent.
    """
    tp = fp = tn = fn = 0
    disagreements = []
    for row in pairs:
        if not row.get("emitted") or not row.get("in_frame"):
            continue
        residue = row.get("seam_residue")
        predicted = residue in alphabet
        observed = bool(row.get("collided_peptides_present"))
        if predicted and observed:
            tp += 1
        elif predicted and not observed:
            fp += 1
            disagreements.append({"pair": row["pair"], "seam_residue": residue,
                                  "predicted": True, "observed": False})
        elif observed:
            fn += 1
            disagreements.append({"pair": row["pair"], "seam_residue": residue,
                                  "predicted": False, "observed": True})
        else:
            tn += 1
    return tp, fp, tn, fn, disagreements


def main():
    novelty = load(NOVELTY, "the proteome novelty search")
    sens = load(SENSITIVITY, "the transcript sensitivity scan")

    alphabet, stems, accessions = collision_alphabet(novelty)
    tp, fp, tn, fn, disagreements = confusion(sens["pairs"], alphabet)
    tested = tp + fp + tn + fn

    by_residue = {}
    for row in sens["pairs"]:
        if not row.get("emitted") or not row.get("in_frame"):
            continue
        r = row.get("seam_residue")
        rec = by_residue.setdefault(str(r), {"pairs": 0, "collided": 0})
        rec["pairs"] += 1
        rec["collided"] += 1 if row.get("collided_peptides_present") else 0

    out = {
        "_what": "A one-residue pre-screen for the novelty-filter failure mode of §B5, and its "
                 "validation against every in-frame transcript pair of this locus.",
        "_the_test": "seam_residue in collision_alphabet -> the seam-proximal window is not "
                     "tumour-exclusive. The alphabet is a property of the ACCEPTOR gene alone and is "
                     "computed once from its isoform set.",
        "⛔_what_this_is_not": "NOT a replacement for the proteome search. It predicts one failure "
                              "mode — a seam-proximal peptide reconstructing an acceptor isoform "
                              "boundary — and is silent on collisions with unrelated proteins and on "
                              "peptides extending far enough into the donor to be novel again. In "
                              "this locus RGDMPCVQAQY carries the same stem and remains novel.",
        "collision_alphabet": alphabet,
        "stems_each_alphabet_residue_precedes": stems,
        "accessions_that_carry_them": accessions,
        "validation": {
            "_denominator": "in-frame emitting pairs only; a pair with no seam has no residue to "
                            "test and is excluded rather than scored as a correct negative",
            "n_pairs_tested": tested,
            "true_positive": tp, "false_positive": fp,
            "true_negative": tn, "false_negative": fn,
            "sensitivity": round(tp / (tp + fn), 4) if (tp + fn) else None,
            "specificity": round(tn / (tn + fp), 4) if (tn + fp) else None,
            "disagreements": disagreements,
        },
        "by_seam_residue": dict(sorted(by_residue.items())),
        "_sources": {
            "collision_alphabet_from": os.path.basename(NOVELTY),
            "validated_against": os.path.basename(SENSITIVITY),
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    v = out["validation"]
    print(f"wrote {os.path.basename(OUT)}")
    print(f"  collision alphabet {alphabet} over {sorted(stems)} ")
    print(f"  {tested} in-frame pairs: TP {tp}  FP {fp}  TN {tn}  FN {fn}; "
          f"sensitivity {v['sensitivity']}  specificity {v['specificity']}")
    for residue, rec in sorted(by_residue.items()):
        print(f"    seam {residue}: {rec['collided']}/{rec['pairs']} collide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
