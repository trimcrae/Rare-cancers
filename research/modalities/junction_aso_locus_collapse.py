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

import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aso_screen_sets as ass                                            # noqa: E402

OUT = os.path.join(HERE, "junction-aso-offtarget-locus-collapse.json")

#: The geometry this artifact describes: the 16-mer 5-6-5 panel the manuscript reports. Screens at
#: other geometries share the filename glob and are partitioned out rather than pooled — see
#: `collapse_screen`. 16 is not typed here as a preference; it is the panel every committed
#: manuscript number was measured on, and `aso_gap_length_tradeoff.py` owns the comparison across
#: geometries.
#: ⭐ AND IT IS NOW DERIVED FROM THE ONE LOADER RATHER THAN TYPED (2026-08-14). This partition was
#: written here by hand, correctly, and the same partition was written by hand in
#: `aso_per_junction_table` and `offtarget_chance_baseline` — three independent implementations of
#: one rule, each landing after its own consumer had already been caught by a human. Three more
#: consumers were still pooling when this was checked (`junction_aso_offtarget.grade_panel`,
#: `submission_tables._graded_loads`, `aso_archive_manifest._screen_coverage`), which is what
#: writing the rule three times rather than once buys. `aso_screen_sets` is the one home; the value
#: below is unchanged and the artifact is byte-identical.
GEOMETRY = ass.MANUSCRIPT_GEOMETRY
MANUSCRIPT_OLIGO_LEN = GEOMETRY.oligo_len

# `Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), transcript variant 1, mRNA; ...`
# The symbol is the FIRST parenthesised token whose closing paren is followed by a comma or the end
# of the definition. NCBI's defline is `<organism> <description> (<SYMBOL>), <tail>`, so that
# lookahead is what separates the symbol from a parenthetical inside the description: in
# "... (Sm) (SNRPB), transcript variant 1" only `(SNRPB)` is comma-terminated.
#
# ⚠ THIS REPLACED "the LAST parenthesised token before the first comma", which was wrong for every
# gene whose DESCRIPTION itself contains a comma (measured 2026-08-13: 888 of 25,893 hits across the
# committed screens, 3.43%). `Homo sapiens germ cell-less 1, spermatogenesis associated (GMCL1),
# mRNA` split to `Homo sapiens germ cell-less 1`, which carries no parenthesis at all, so nine
# GMCL1 variants degraded to nine separate accession fallbacks and ONE locus was counted as NINE.
# The old rule also returned an outright WRONG symbol wherever the description's own parenthetical
# came first: `glucosaminyl (N-acetyl) transferase 3, mucin type (GCNT3)` returned `N-ACETYL`.
# ⚠ AND THE OVER-COUNTING WAS NOT HARMLESS JUST BECAUSE IT WAS THE SAFE DIRECTION. The fallback
# comment below is right that over-counting beats merging, but a locus count is quoted in the
# manuscript as a measure of how many distinct genes a design can cleave, and there an inflated
# count reads as a dirtier reagent than the evidence supports. Safe-direction is a floor on the
# damage, not a licence to leave it.
_PAREN = re.compile(r"\(([^()]{1,20})\)(?=,|$)")

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
    m = _PAREN.search(defn)
    if m:
        sym = m.group(1).strip().upper()
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
        # ⛔⛔ THE SCREEN'S OWN COUNT WINS ONLY WHERE THE RECOUNT CANNOT BE EXACT (2026-08-12,
        # narrowed 2026-08-13). `loci_risk` is derived from the hits this module can see, while the
        # screen computed `n_loci_with_a_gap_spanning_hit` over EVERY ranked hit before truncation.
        # For a CENSORED design the two disagree in the flattering direction: EWSR1 e9 /
        # GGGCATATCACCAGGC recounted to 0 here against the screen's exact 2, so Table 2 printed "≥0"
        # for a design with two gap-spanning loci — a design looking CLEANER than it is, which this
        # module's own docstring names as the dangerous failure.
        # ⚠ BUT THE SCREEN'S FIELD IS FROZEN AT SCREEN TIME, AND `locus_of` HAS SINCE BEEN
        # CORRECTED. Every committed screen predates the first-comma fix above, so its exact count
        # still splits any gene whose description contains a comma across one fallback per
        # accession: TCF12 e5 / GGGCATATCCATCAGA stores 17, and those 17 records are seventeen
        # variants of ONE locus, PIK3CG. Where the stored list is COMPLETE the recount is both
        # exact and current, so it wins there; only a truncated list still falls back to the frozen
        # figure, where it is an over-count and the table marks it as one. Re-running a screen is a
        # network operation, so this is the strongest statement available offline.
        "n_loci_with_a_gap_spanning_hit": (
            oligo["n_loci_with_a_gap_spanning_hit"]
            if censored and oligo.get("n_loci_with_a_gap_spanning_hit") is not None
            else len(loci_risk)),
        "n_loci_with_a_gap_spanning_hit_is_from_the_screen": bool(
            censored and oligo.get("n_loci_with_a_gap_spanning_hit") is not None),
        "loci_with_a_gap_spanning_hit": sorted(loci_risk),
        "named_gap_spanning_loci_are_a_subset_when_censored": censored,
        # named, not just counted, so "none of the gap-spanning loci is curated" is a claim a
        # reader — or a test — can check by set membership instead of by arithmetic on totals
        "loci_seen_only_as_predicted_models": sorted(loci_predicted),
        "n_transcripts_curated": cls.get("curated", 0),
        "n_transcripts_predicted": cls.get("predicted", 0),
        "n_transcripts_other": cls.get("other", 0),
        "max_variants_at_one_locus": max(variants) if variants else 0,
        "n_loci_unresolved_to_a_symbol": sum(1 for k in by_locus if k.startswith("acc:")),
    }


def screen_oligo_len(screen):
    """The oligo length a screen ACTUALLY ran at, measured from its own designs, or None.

    ⛔ MEASURED, NEVER TAKEN FROM THE FILENAME, for the same reason `depth` below is a partition
    rather than a comment: the length is the thing that ran, and it is in the file whether or not
    anyone remembered to name the file after it. Screens committed before 2026-08-13 carry no
    geometry block at all, so a recorded field would be absent exactly where it is needed.
    A screen whose designs are not all one length returns None and is never pooled with anything.

    ⭐ THE MEASUREMENT IS THE LOADER'S NOW (2026-08-14) — this is a thin adapter kept because the
    artifact's `oligo_len` field and three tests read it. `aso_screen_sets.measure_oligo_len` does
    the same thing and ALSO checks the answer against whatever geometry the screen states about
    itself, which is the half a per-consumer copy of this rule kept omitting: a screen graded
    against one window and counted against another crashes nothing.
    """
    try:
        return ass.measure_oligo_len(ass.BLAST_SCREEN, screen)
    except ass.GeometryError:
        return None                      # designs of two lengths: never pooled with anything


def collapse_screen(screen):
    """Locus-level counts for one `aso_screen_sets.Screen`.

    ⚠ TAKES THE LOADED SCREEN, NOT A PATH, so a caller cannot reach this function with a file the
    loader never measured a geometry for. The type IS the check.
    """
    d = screen.artifact
    oligos = [o for o in (d.get("oligos") or []) if o.get("offtargets") is not None]
    per = [collapse_oligo(o) for o in oligos]
    try:  # the orientation verdict is owned elsewhere; this module reports it, never derives it
        from junction_aso_offtarget import screen_orientation_status  # noqa: PLC0415
        orient = screen_orientation_status(d)
    except Exception as exc:  # noqa: BLE001
        orient = {"status": "unreadable", "why": str(exc)[:120]}
    return {
        "screen": screen.name,
        "junction_label": d.get("junction_label"),
        "orientation": orient,
        # ⛔ DEPTH IS PART OF A SCREEN'S IDENTITY AND MUST NOT BE POOLED AWAY. The same design
        # returns a different near-match count at the default alignment ceiling and at ten times it,
        # so an inflation median taken across both describes neither population — the same defect
        # the censoring note above refuses for truncated lists. Tagged here so `main` can partition.
        # ⚠ AND IT IS NOW READ FROM THE ARTIFACT RATHER THAN FROM THE FILENAME (2026-08-14). This
        # was `"deep500" in basename`, sitting one line above a comment that says geometry is
        # measured "NEVER TAKEN FROM THE FILENAME" — the same rule enforced on one axis and not the
        # other, in one dict literal. Three spellings of that suffix are already on disk.
        # `aso_screen_sets.is_deep` reads the recorded ceiling where there is one and otherwise the
        # retention evidence a default run cannot produce. Verified: the two agree on all 93 screens
        # in this tree, so no committed value moves.
        "depth": "deep" if ass.is_deep(screen) else "default",
        # ⛔ AND SO IS GEOMETRY, FOR EXACTLY THE SAME REASON (2026-08-14). The gap-length screens
        # put 18-mer 5-8-5 and 20-mer 5-10-5 artifacts under the same `junction-aso-offtarget-*`
        # glob. A longer gap is a different question — different catalytic span, different mismatch
        # budget — so a near-match median taken across the three describes none of them. Measured
        # on merge: pooling moved the deep population 38 screens/187 designs to 53/303 and
        # `oligos_with_no_gap_spanning_locus` 12 to 110, which reads as a tenfold cleaner panel and
        # is only a wider glob. Partition, exactly as depth is partitioned above.
        "oligo_len": screen.geometry.oligo_len,
        "n_oligos": len(per),
        "per_oligo": per,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # ⛔ ONE LOADER. The glob that used to live here matched three geometries; `iter_geometries`
    # hands them back one at a time and there is no call that would have returned them pooled.
    all_screens = [collapse_screen(s)
                   for _geom, screens in ass.iter_geometries(ass.BLAST_SCREEN, root=HERE)
                   for s in screens]

    # ⛔ THIS ARTIFACT DESCRIBES ONE GEOMETRY, AND EVERY NUMBER IN THE MANUSCRIPT IS THAT GEOMETRY'S
    # (2026-08-14). The gap-length work screens the same seams at 18-mer 5-8-5 and 20-mer 5-10-5 and
    # writes them under this same glob, so the geometries are separated here before anything is
    # counted. They are not dropped: `other_geometries` names every screen this artifact declines to
    # pool, so a widening is visible rather than silent. The cross-geometry comparison has its own
    # module, `aso_gap_length_tradeoff.py`, which is where a like-for-like contrast belongs.
    screens = [s for s in all_screens if s["oligo_len"] == MANUSCRIPT_OLIGO_LEN]
    other = [s for s in all_screens if s["oligo_len"] != MANUSCRIPT_OLIGO_LEN]

    # ⛔ THE HEADLINE POPULATION IS DEFAULT-DEPTH SCREENS ONLY, AND THIS IS LOAD-BEARING (2026-08-13).
    # `main` globs every `junction-aso-offtarget-*.json` on disk, so when the 38 deep re-screens
    # landed they silently doubled the population: a re-run moved `n_oligos` 192 -> 379 and the
    # median inflation factor 2.14 -> 4.55, both of which the manuscript quotes. Nothing about the
    # science changed; the glob simply widened under a number that reads as a measurement. Partition
    # rather than pool, and let the deep population carry its own summary.
    default_screens = [s for s in screens if s["depth"] == "default"]
    deep_screens = [s for s in screens if s["depth"] == "deep"]

    def _totals(subset):
        every_ = [o for s in subset for o in s["per_oligo"]]
        # ⛔ EVERY HEADLINE IS COMPUTED ON THE UNCENSORED SUBSET AND SAYS SO. Mixing a complete hit
        # list with a top-15 sample produces a number that describes neither.
        clean_ = [o for o in every_ if not o["right_censored"]]
        infl_ = sorted(o["inflation_factor"] for o in clean_
                       if o["inflation_factor"] is not None)
        return every_, clean_, infl_, {
            "transcript_near_matches": sum(o["n_transcript_near_matches_stored"] for o in clean_),
            "distinct_loci_summed_over_oligos": sum(o["n_distinct_loci"] for o in clean_),
            "median_inflation_factor": (infl_[len(infl_) // 2] if infl_ else None),
            "max_inflation_factor": (infl_[-1] if infl_ else None),
            "oligos_whose_loci_are_all_curated": sum(
                1 for o in clean_ if o["n_loci_seen_only_as_predicted_models"] == 0),
            "oligos_with_no_gap_spanning_locus": sum(
                1 for o in clean_ if o["n_loci_with_a_gap_spanning_hit"] == 0),
        }

    every, clean, infl, default_totals = _totals(default_screens)
    _, deep_clean, _, deep_totals = _totals(deep_screens)
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
        "⛔_one_geometry": (
            f"Every count in this file is the {MANUSCRIPT_OLIGO_LEN}-mer 5-6-5 panel the manuscript "
            f"reports. Screens at other geometries live under the same filename glob and are "
            f"listed in `other_geometries` rather than pooled: a longer catalytic gap is a "
            f"different question, so a count taken across geometries describes none of them."),
        "manuscript_oligo_len": MANUSCRIPT_OLIGO_LEN,
        "other_geometries": [
            {"oligo_len": s["oligo_len"], "screen": s["screen"], "depth": s["depth"],
             "n_oligos": s["n_oligos"]}
            for s in sorted(other, key=lambda s: (s["oligo_len"] or 0, s["screen"]))],
        "n_screens": len(screens),
        "n_oligos": len(every),
        "n_oligos_uncensored": len(clean),
        "n_oligos_right_censored": len(every) - len(clean),
        "totals_over_uncensored_oligos_only": default_totals,
        "⚠_population": ("`totals_over_uncensored_oligos_only` and every count above it cover the "
                         "DEFAULT-DEPTH screens only. The deeper re-screens are summarised "
                         "separately below; the two are never pooled, because the same design "
                         "returns a different near-match count at each ceiling."),
        "n_deep_screens": len(deep_screens),
        "n_deep_oligos_uncensored": len(deep_clean),
        "deep_totals_over_uncensored_oligos_only": deep_totals,
        # ⛔ `screens` IS DEFAULT-DEPTH ONLY, AND EVERY DOWNSTREAM READER DEPENDS ON THAT (2026-08-13).
        # Partitioning only the summary while leaving this key on the raw glob is not a partition:
        # the moment the 38 deep re-screens landed on disk, `screens` widened 40 -> 78 and
        # `test_aso_submission_numbers._clean_set` — which iterates it — returned 13 designs where
        # the manuscript says 9. The clean set is a default-depth claim, so the deep re-screens get
        # their own key rather than being mixed into the list consumers already read.
        "screens": default_screens,
        "deep_screens": deep_screens,
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
