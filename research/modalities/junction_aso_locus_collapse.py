#!/usr/bin/env python3
"""Collapse junction-gapmer off-target hit lists from TRANSCRIPTS to GENE LOCI.

⛔ WHY THIS EXISTS: A COUNT OF NEAR-MATCHES IS NOT A COUNT OF RISKS (2026-08-12, adversarial
review). Every screen in this repository reports `n_offtarget_near_matches` as a count of RefSeq
ACCESSIONS, and RefSeq carries one accession per transcript VARIANT. A 16-mer that matches a
constitutive exon of a gene with six annotated variants scores six, and a 16-mer that matches six
unrelated genes also scores six — the same number for two situations a reviewer would treat
completely differently. The inflation is not hypothetical: in the very first screened oligo of the
E7::N3 panel, three of its 32 accessions are ATP5F1C transcript variants 1, 2 and 3.

⛔ AND HALF THE RefSeq NAMESPACE IS NOT OBSERVED SEQUENCE. `XM_`/`XR_` are Gnomon PREDICTED models;
`NM_`/`NR_` are curated. Pooling them makes a ranking depend on how aggressively the current
annotation release predicted transcripts at a locus, which is a property of the annotation and not
of the oligonucleotide. They are separated here rather than filtered, because a predicted model at a
real locus is still a reason to look.

⚠ WHAT THIS DOES NOT DO. It does not re-screen, re-align or re-score anything: it re-counts a hit
list that already exists, and every graded risk class is carried through unchanged. A locus count
is a better denominator than a transcript count; it is not a measurement of off-target activity, and
nothing here converts either number into one.

⚠ ORIENTATION IS INHERITED, NOT FIXED HERE. Screens produced before 2026-08-12 did not parse
`Hsp_hit-frame`, so a minus-strand hit — which an antisense oligonucleotide cannot hybridise to —
is still counted among the near-matches of those artifacts. Collapsing to loci does not remove
those; `junction_aso_offtarget.screen_orientation_status` is what says whether a given screen's
counts are upper bounds, and this module records that verdict per screen rather than restating it.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "junction-aso-offtarget-locus-collapse.json")

# `Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), transcript variant 1, mRNA; ...`
# The symbol is the LAST parenthesised token before the first comma — last, because descriptions
# such as "... (Sm) (SNRPB), transcript variant 1" carry an earlier parenthetical that is part of
# the protein name rather than the gene symbol.
_PAREN = re.compile(r"\(([^()]{1,20})\)")

# curated vs predicted, per NCBI's RefSeq accession prefixes
CURATED_PREFIXES = ("NM_", "NR_")
PREDICTED_PREFIXES = ("XM_", "XR_")


def locus_of(entry):
    """The gene symbol a hit belongs to, or a stable fallback that cannot merge two loci.

    ⚠ THE FALLBACK MUST NOT BE A SHARED CONSTANT. An unparseable definition returning a single
    sentinel would merge every such hit into ONE locus and UNDERCOUNT — the direction that flatters
    the result. Falling back to the accession over-counts instead, which is the safe direction: it
    can only report more distinct loci than exist, never fewer.
    """
    defn = str(entry.get("defn") or "")
    head = defn.split(",")[0]
    hits = _PAREN.findall(head)
    if hits:
        sym = hits[-1].strip().upper()
        # a parenthetical that is plainly not a symbol (spaces, or a lone descriptor) is refused
        if sym and " " not in sym and not sym.isdigit():
            return sym
    return "acc:" + str(entry.get("acc") or "?")


def accession_class(entry):
    acc = str(entry.get("acc") or "")
    if acc.startswith(CURATED_PREFIXES):
        return "curated"
    if acc.startswith(PREDICTED_PREFIXES):
        return "predicted"
    return "other"


def collapse_oligo(oligo):
    """Locus-level counts for one screened oligonucleotide.

    Risk classes are those the screen already assigned per hit (`risk`), carried through: a locus
    is counted as a gap-spanning risk if ANY of its transcripts was graded one, which is the
    conservative direction.

    ⛔ AND THE HIT LIST IT READS IS USUALLY TRUNCATED (measured 2026-08-12, the first time this
    module was run). `junction_aso_offtarget` saves `ranked[:15]` while reporting the FULL count in
    `n_offtarget_near_matches`: 41 of 67 committed oligonucleotides store 15 hits and report more,
    one of them 50. Collapsing the stored list and calling the answer "distinct loci" would have
    reported a 16-mer with 50 near-matches as touching one locus. So each oligonucleotide carries
    `right_censored`, the locus count is a LOWER BOUND when censored, and the inflation factor is
    published as `null` there — a ratio of a truncated numerator to a truncated denominator bounds
    the true ratio in neither direction, and quoting it anyway is how a sampling artifact becomes a
    finding.
    """
    hits = oligo.get("offtargets") or []
    reported = oligo.get("n_offtarget_near_matches")
    censored = bool(reported is not None and reported > len(hits))
    by_locus = defaultdict(list)
    for h in hits:
        by_locus[locus_of(h)].append(h)

    cls = Counter(accession_class(h) for h in hits)
    loci_curated, loci_predicted, loci_risk = set(), set(), set()
    for locus, hs in by_locus.items():
        classes = {accession_class(h) for h in hs}
        if "curated" in classes:
            loci_curated.add(locus)
        if classes == {"predicted"}:
            loci_predicted.add(locus)
        if any(str(h.get("risk") or "").startswith("true_cleavage") for h in hs):
            loci_risk.add(locus)

    variants = [len(v) for v in by_locus.values()]
    return {
        "antisense_5to3": oligo.get("antisense_5to3"),
        "specificity_margin": oligo.get("specificity_margin"),
        "right_censored": censored,
        "n_transcript_near_matches_reported": reported,
        "n_transcript_near_matches_stored": len(hits),
        "n_distinct_loci": len(by_locus),
        "n_distinct_loci_is_a_lower_bound": censored,
        "inflation_factor": (None if censored or not by_locus
                             else round(len(hits) / len(by_locus), 2)),
        "n_loci_with_a_curated_transcript": len(loci_curated),
        "n_loci_seen_only_as_predicted_models": len(loci_predicted),
        "n_loci_with_a_gap_spanning_hit": len(loci_risk),
        "loci_with_a_gap_spanning_hit": sorted(loci_risk),
        # named, not just counted, so "none of the gap-spanning loci is curated" is a claim a
        # reader — or a test — can check by set membership instead of by arithmetic on totals
        "loci_seen_only_as_predicted_models": sorted(loci_predicted),
        "n_transcripts_curated": cls.get("curated", 0),
        "n_transcripts_predicted": cls.get("predicted", 0),
        "n_transcripts_other": cls.get("other", 0),
        "max_variants_at_one_locus": max(variants) if variants else 0,
        "n_loci_unresolved_to_a_symbol": sum(1 for k in by_locus if k.startswith("acc:")),
    }


def collapse_screen(path):
    d = json.load(open(path))
    oligos = [o for o in (d.get("oligos") or []) if o.get("offtargets") is not None]
    per = [collapse_oligo(o) for o in oligos]
    try:  # the orientation verdict is owned elsewhere; this module reports it, never derives it
        sys.path.insert(0, HERE)
        from junction_aso_offtarget import screen_orientation_status  # noqa: PLC0415
        orient = screen_orientation_status(d)
    except Exception as exc:  # noqa: BLE001
        orient = {"status": "unreadable", "why": str(exc)[:120]}
    return {
        "screen": os.path.basename(path),
        "junction_label": d.get("junction_label"),
        "orientation": orient,
        "n_oligos": len(per),
        "per_oligo": per,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    paths = sorted(p for p in glob.glob(os.path.join(HERE, "junction-aso-offtarget-*.json"))
                   if "-graded" not in p and "locus-collapse" not in p)
    screens = [collapse_screen(p) for p in paths]

    every = [o for s in screens for o in s["per_oligo"]]
    # ⛔ EVERY HEADLINE IS COMPUTED ON THE UNCENSORED SUBSET AND SAYS SO. Mixing a complete hit
    # list with a top-15 sample produces a number that describes neither.
    clean = [o for o in every if not o["right_censored"]]
    infl = sorted(o["inflation_factor"] for o in clean if o["inflation_factor"] is not None)
    out = {
        "what": ("Off-target near-matches from every committed junction-gapmer screen, re-counted "
                 "per GENE LOCUS instead of per RefSeq transcript accession, and split by whether "
                 "the locus was seen in curated (NM_/NR_) or only predicted (XM_/XR_) records."),
        "⚠_not_a_measurement": ("A locus count is a denominator, not an off-target activity. No "
                                "hit was re-aligned or re-graded; the screens' own risk classes "
                                "are carried through unchanged."),
        "⛔_censoring": ("The screens store the top 15 hits per oligonucleotide and report the full "
                        "near-match count separately, so an oligonucleotide with more than 15 is "
                        "right-censored: its locus count is a lower bound and its inflation factor "
                        "is not computable. Every summary below is over the UNCENSORED subset."),
        "n_screens": len(screens),
        "n_oligos": len(every),
        "n_oligos_uncensored": len(clean),
        "n_oligos_right_censored": len(every) - len(clean),
        "totals_over_uncensored_oligos_only": {
            "transcript_near_matches": sum(o["n_transcript_near_matches_stored"] for o in clean),
            "distinct_loci_summed_over_oligos": sum(o["n_distinct_loci"] for o in clean),
            "median_inflation_factor": (infl[len(infl) // 2] if infl else None),
            "max_inflation_factor": (infl[-1] if infl else None),
            "oligos_whose_loci_are_all_curated": sum(
                1 for o in clean if o["n_loci_seen_only_as_predicted_models"] == 0),
            "oligos_with_no_gap_spanning_locus": sum(
                1 for o in clean if o["n_loci_with_a_gap_spanning_hit"] == 0),
        },
        "screens": screens,
    }
    if "--write" in argv:
        with open(OUT, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
        print(f"wrote {OUT}")
    print(json.dumps({k: out[k] for k in
                      ("n_oligos", "n_oligos_uncensored", "n_oligos_right_censored",
                       "totals_over_uncensored_oligos_only")}, indent=2))
    for s in screens:
        for o in s["per_oligo"]:
            mark = "  [censored]" if o["right_censored"] else ""
            print(f"  {str(s['junction_label']):<24} {o['antisense_5to3']}  "
                  f"tx={o['n_transcript_near_matches_reported']:>3}"
                  f"({o['n_transcript_near_matches_stored']:>2} stored)  "
                  f"loci={o['n_distinct_loci']:>3}  x{o['inflation_factor']}  "
                  f"gap_loci={o['n_loci_with_a_gap_spanning_hit']}  "
                  f"pred_only={o['n_loci_seen_only_as_predicted_models']}{mark}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
