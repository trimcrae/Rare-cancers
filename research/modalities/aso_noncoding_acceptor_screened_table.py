#!/usr/bin/env python3
"""The published NON-CANONICAL NR4A3 seams, screened to the panel's depth and reported in its shape.

⛔ WHY THIS EXISTS. `aso_noncoding_acceptor_designs.py` emits designs at the published breakpoints
the manuscript's 38-junction panel cannot express — chiefly *EWSR1* exon 7 :: *NR4A3* exon 2, the
type 2 transcript, reported in sequenced patients by three independent sources. Those designs
carried a parent-exclusion screen and nothing else, and that module says so in its own
`_what_this_is_not`: "⛔ NOT SCREENED FOR OFF-TARGET LOAD … These counts are therefore NOT
comparable with the panel's." An unscreened design beside 38 screened ones is not a candidate; it is
a sequence, and quoting it as though it had been screened is precisely the failure that produced the
withdrawn "nine clean designs".

WHAT THIS IS. The same five screens, at the same geometry, joined into the same field set as
`aso-per-junction-table.json`, so a reader can put the rows side by side and the comparison is
honest. Every field below is joined from a screen artifact that ran; nothing is re-aligned,
re-graded or converted into a predicted cleavage event.

⛔ ONE GRADER, NOT A SECOND COPY OF ONE. The rows are built by `aso_per_junction_table.junction_rows`
and counted by its `_deep_screens`, called with a different root. That is the entire reason those
two were parameterised: a table whose purpose is comparability, computed by a second implementation
of "the same" fields, stops being comparable the first time one side gains a field or changes a
tie-break — silently, and in the direction nobody checks.

⛔ AND THE SCREENS LIVE IN THEIR OWN DIRECTORY, WHICH IS A DATA DECISION AND NOT TIDINESS.
`junction-aso-offtarget-*.json`, `junction-aso-designs-*.json` and `aso-insilico-evaluation-*.json`
are discovered BY PATTERN from `research/modalities` by the panel's own consumers — the per-junction
table, the locus collapse, the chance baseline, the submission tables. Dropping this junction's
screens in beside them would have added a 39th row to a table the manuscript reports as 38, enlarged
the locus-collapse population, and moved manuscript-facing numbers, with nothing in any artifact
able to say a junction the panel excludes had joined it. The loaders list one directory and do not
recurse, so a subdirectory is invisible to them and visible to this module, which names it.

WHAT THIS IS NOT
  · Not an efficacy, potency, knockdown, delivery, tolerability or safety claim, and not a claim
    that any sequence here is active. No wet-lab experiment has been performed.
  · Not a claim that this junction's designs are as clean as the panel's. It puts the numbers in one
    shape; reading them is the reader's, and the manuscript's, job.
  · Not a claim that the type 2 chimera makes a protein or is oncogenic. It is excluded from the
    panel because the acceptor exon is upstream of the start codon — a protein-level filter, and an
    RNase-H1 gapmer cleaves the transcript.
  · Not a coverage claim. What these junctions would add to panel coverage is priced elsewhere
    (`research/manuscripts/aso_coverage_ladder.py`).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aso_per_junction_table as APJT  # noqa: E402
import aso_screen_sets as ass  # noqa: E402
import junction_seam_retraction as JSR  # noqa: E402

#: Where this lane's BLAST-family artifacts live. See the docstring: OUT of the panel's glob.
SCREEN_DIR = os.path.join(HERE, "noncoding-acceptor")
OUT = os.path.join(SCREEN_DIR, "aso-noncoding-acceptor-screened-table.json")

#: The geometry every number here must be at — ASSERTED, never assumed. `load_screens` refuses a
#: screen of any other geometry outright; the two artifacts that are not BLAST-family state their
#: own geometry and are checked against this below.
GEOMETRY = ass.MANUSCRIPT_GEOMETRY

ATLAS = "nr4a3-fusion-junction-atlas-noncoding-acceptor.json"
PARENT_SCREEN = "aso-parent-gap-pairing-noncoding-acceptor.json"
PREMRNA_SCREEN = "aso-premrna-offtarget-noncoding-acceptor.json"
GENOME_SCREEN = "aso-genome-offtarget-noncoding-acceptor.json"


def _read(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _assert_geometry(name, got, want, where):
    """⛔ A GEOMETRY DISAGREEMENT IS A REFUSAL. A screen graded against one window and joined under
    another produces a full, plausible, wrong artifact — see `aso_screen_sets`'s whole header."""
    if list(got) != list(want):
        raise SystemExit(f"{where}: states {name} {got}, which is not {list(want)} — the geometry "
                         f"this table is about. Refusing to join screens of two geometries.")


def _screen_state(path, ran, detail):
    """One screen's state, said plainly. ⛔ 'not present' and 'no hits' are DIFFERENT READINGS and
    must never render alike: the first is a screen that did not run, the second is a measurement."""
    return {"artifact": os.path.relpath(path, HERE), "ran": ran, **detail}


#: The panel's own per-junction table, read ONLY to check that this one's rows carry the same keys.
_PANEL_TABLE = os.path.join(HERE, "aso-per-junction-table.json")


def _panel_row_keys():
    """The exact per-design key set a panel junction's row carries, read from the panel's artifact.

    ⛔ READ, NEVER LISTED. The whole claim of this module is "the same field set as a panel
    junction", and a hand-typed list of field names is a claim about another artifact made without
    opening it — which goes stale the first time the panel's table gains a column, silently, in the
    direction that makes an incomplete row look complete.
    """
    art = _read(_PANEL_TABLE) or {}
    for j in art.get("junctions") or []:
        for row in j.get("designs") or []:
            return set(row)
    return set()


def _partial_rows(parent, premrna, genome, skip=()):
    """Rows in the panel's field set for the screens that HAVE run, with the rest explicitly null.

    ⛔ WHY THIS EXISTS AND WHY IT IS NOT `junction_rows`. `junction_rows` ranks designs by
    transcriptome load among those clearing the parent screen, so it cannot run before the alignment
    screen has: its rank key is the thing that is missing. Emitting nothing until then would hide two
    screens that DID run and produced real per-design readings.

    ⛔ AND THE UNMEASURED FIELDS ARE `null` WITH A NAMED REASON, NEVER `0`. A zero here would read as
    "no off-target load found" — an unrun screen rendered as a clean result, which is the single
    failure mode this whole lane is written against. There is deliberately NO `best_available`
    either: "best" is a ranking, the rank key is unmeasured, and a best-of chosen on the two screens
    that happen to have run would be a recommendation manufactured out of an absence.
    """
    atlas = _read(os.path.join(HERE, ATLAS))
    if not atlas:
        return []
    out = []
    for pan in atlas.get("panels") or []:
        if pan.get("junction_label") in set(skip):
            continue                      # this junction has a real alignment screen; not partial
        rows = []
        for d in pan.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            seq = d["antisense_5to3"]
            pa, pm, gn = parent.get(seq, {}), premrna.get(seq, {}), genome.get(seq, {})
            oe = gn.get("observed_over_expected") or {}
            rows.append({
                "antisense_5to3": seq,
                "gap_specificity_margin": pa.get("gap_specificity_margin"),
                "n_gap_paired": None, "n_gap_paired_loci": None, "gap_paired_loci": None,
                "n_hybridisable": None, "n_near_matches": None,
                "parent": pa.get("parent"),
                "parent_duplex_bp": pa.get("longest_parent_duplex_bp_through_gap"),
                "parent_is_liability": pa.get("counts_as_liability"),
                "premrna_gap_paired_hybridisable": pm.get("n_hybridisable_gap_fully_paired"),
                "genome_oe_gap_paired_le2": oe.get("gap_paired_le2"),
                "genome_named_target_sites": gn.get("n_named_target_sites"),
                "genome_named_target_genes": gn.get("named_target_genes"),
            })
        if not rows:
            continue
        unmeasured = sorted(k for k in rows[0] if rows[0][k] is None)
        # ⛔ the field set is CHECKED against the panel's, not asserted in prose
        panel_keys = _panel_row_keys()
        missing = panel_keys - set(rows[0])
        if panel_keys and missing:
            raise SystemExit(
                f"the partial rows are missing {sorted(missing)}, which a panel junction's row "
                "carries. This table claims the panel's field set; a row short of it cannot be "
                "compared with a panel row and must not pretend to be.")
        rows.sort(key=lambda r: -(r["gap_specificity_margin"] or 0))
        tier, refs = APJT._clinical_tier(pan["junction_label"])
        eligible = [r for r in rows if r["parent_is_liability"] is False]
        # ⛔ A COUNT OVER AN UNRUN SCREEN IS NOT A COUNT OF ZERO. If the parent screen never saw
        # these designs, `parent_is_liability` is None for all of them and `len(eligible)` is 0 —
        # which renders identically to "every design is a parent liability", the worst possible
        # misreading in the field that decides whether a design is usable at all. So the count is
        # null when the reading is missing, and the number of unread designs is named beside it.
        unread = sum(1 for r in rows if r["parent_is_liability"] is None)
        out.append({
            "junction_label": pan["junction_label"],
            "clinical_tier": tier,
            "breakpoint_refs": refs,
            "n_designs_screened": len(rows),
            "n_designs_clearing_the_parent_screen": (None if unread == len(rows) else len(eligible)),
            "n_designs_with_no_parent_screen_reading": unread,
            "best_available": None,
            "_why_no_best_available": (
                "the rank key is the transcriptome load among designs clearing the parent screen, "
                "and the alignment screen that measures it has not run. Ranking on the screens that "
                "did run would manufacture a recommendation out of an absence."),
            "best_by_gap_specificity_margin": max(
                rows, key=lambda r: (r["gap_specificity_margin"] or -1))["antisense_5to3"],
            "⛔_unmeasured_fields": unmeasured,
            "⛔_unmeasured_is_not_clean": (
                "every field listed above is null because the screen that measures it HAS NOT RUN. "
                "Null is an absent reading; it is not a reading of absence, and it must never be "
                "read as zero off-target load."),
            "designs": rows,
        })
    return out


def build():
    provenance, states = {}, {}

    # ── screen 2: the deep transcriptome BLAST arm (and, through it, the locus recount) ───────
    deep, blast_state = [], None
    blast_screens = []
    try:
        ss = ass.load_screens(GEOMETRY, ass.BLAST_SCREEN, root=SCREEN_DIR,
                              select=ass.is_deep, allow_empty=True)
        blast_screens = sorted(ss.names)
        if blast_screens:
            deep = APJT._deep_screens(root=SCREEN_DIR)
            blast_state = _screen_state(SCREEN_DIR, True, {
                "screens": blast_screens, "geometry": ss.geometry.as_dict(),
                "_geometry_is_measured": "from the designs in each artifact, then checked against "
                                         "the geometry the artifact states about itself"})
        else:
            blast_state = _screen_state(SCREEN_DIR, False, {
                "screens": [],
                "why": ("no DEEP 16-mer 5-6-5 BLAST screen is present in this directory. That is a "
                        "screen that did not run, NOT a screen that found nothing — the two must "
                        "not render alike. It needs NCBI, so it runs in CI: dispatch "
                        ".github/workflows/aso-offtarget.yml with real_junctions "
                        "'EWSR1:7:2:published', screen_mode 'deep_rescreen', suffix_tag "
                        "'-deep500', then commit the published artifacts into this directory.")})
    except ass.GeometryError as exc:                                  # noqa: BLE001
        blast_state = _screen_state(SCREEN_DIR, False, {"error": str(exc)})
    states["transcriptome_blast_deep"] = blast_state

    # ── screen 2 (manuscript numbering): the exhaustive <=1-mismatch transcript scan ──────────
    # ⚠ IT CONTRIBUTES NO FIELD TO THE PANEL'S PER-JUNCTION FIELD SET, AND IS REPORTED ANYWAY.
    # §3 of the manuscript describes FIVE screens; the per-junction table joins four of them,
    # because the exhaustive scan's per-design output (exact and <=1-mismatch counts, site
    # accessibility, siRNA seed) is not among the columns that table carries. A table that silently
    # listed four screens would leave a reader unable to tell whether the fifth ran, which is the
    # absent-reading-as-reading-of-absence failure this whole lane is careful about.
    evals = {}
    try:
        by_geom = ass.load_by_geometry(ass.DESIGN_EVALUATION, root=SCREEN_DIR)
        evals = by_geom.get(GEOMETRY)
    except ass.GeometryError as exc:                                  # noqa: BLE001
        states["exhaustive_transcript_scan"] = _screen_state(SCREEN_DIR, False, {"error": str(exc)})
    if "exhaustive_transcript_scan" not in states:
        if evals:
            states["exhaustive_transcript_scan"] = _screen_state(SCREEN_DIR, True, {
                "screens": sorted(evals.names),
                "geometry": evals.geometry.as_dict(),
                "per_design": sorted(
                    ({"antisense_5to3": d.get("antisense_5to3"),
                      "offtarget_exact": d.get("offtarget_exact"),
                      "offtarget_le1mm": d.get("offtarget_le1mm"),
                      "site_accessibility": d.get("site_accessibility")}
                     for a in evals.artifacts for d in (a.get("top_designs") or [])
                     if d.get("fusion_specific")),
                    key=lambda r: str(r["antisense_5to3"])),
                "_not_in_the_field_set": (
                    "these columns are not part of aso-per-junction-table.json's field set and are "
                    "not joined into the rows below; they are here so the fifth screen's state is "
                    "readable rather than inferred")})
        else:
            states["exhaustive_transcript_scan"] = _screen_state(SCREEN_DIR, False, {
                "screens": [],
                "why": ("no 16-mer design-evaluation panel is present in this directory. It "
                        "downloads the full RefSeq transcript set, so it runs in CI alongside the "
                        "BLAST screen in the same dispatch.")})

    # ── screen 4: mature parent duplexes (offline, from the committed unspliced sequence) ─────
    pa_doc = _read(os.path.join(HERE, PARENT_SCREEN))
    if pa_doc is not None:
        geom = pa_doc.get("_geometry") or {}
        _assert_geometry("oligo_len/wing", [geom.get("oligo_len"), geom.get("wing")],
                         [GEOMETRY.oligo_len, GEOMETRY.wing], PARENT_SCREEN)
        if geom.get("atlas") != ATLAS:
            raise SystemExit(f"{PARENT_SCREEN} was built over atlas {geom.get('atlas')!r}, not "
                             f"{ATLAS!r} — it is about a different design set. Refusing to join it.")
        states["mature_parent_gap_pairing"] = _screen_state(
            os.path.join(HERE, PARENT_SCREEN), True,
            {"parents_searched": (pa_doc.get("method") or {}).get("parents_searched"),
             "min_duplex_bp": (pa_doc.get("method") or {}).get("min_duplex_bp")})
    else:
        states["mature_parent_gap_pairing"] = _screen_state(
            os.path.join(HERE, PARENT_SCREEN), False,
            {"why": "artifact absent; rebuild with OUT_SUFFIX=-noncoding-acceptor "
                    "python3 aso_parent_gap_pairing.py ($0, offline)"})

    # ── screen 3: unspliced pre-mRNA of the six parents ───────────────────────────────────────
    pm_doc = _read(os.path.join(HERE, PREMRNA_SCREEN))
    if pm_doc is not None:
        _assert_geometry("gap_region_1based", (pm_doc.get("method") or {}).get("gap_region_1based"),
                         GEOMETRY.gap_region_1based, PREMRNA_SCREEN)
        states["premrna"] = _screen_state(
            os.path.join(HERE, PREMRNA_SCREEN), True,
            {"genes": sorted((pm_doc.get("genes") or {})),
             "corpus": pm_doc.get("corpus"),
             "genome_wide_arm": (pm_doc.get("genome_wide_arm") or {}).get("ran")})
    else:
        states["premrna"] = _screen_state(
            os.path.join(HERE, PREMRNA_SCREEN), False,
            {"why": "artifact absent; rebuild with ATLAS_JSON=%s PREMRNA_OUT=%s "
                    "python3 aso_premrna_offtarget.py --offline ($0, committed sequence cache)"
                    % (ATLAS, PREMRNA_SCREEN)})

    # ── screen 5: exhaustive GRCh38 ───────────────────────────────────────────────────────────
    gn_doc = _read(os.path.join(HERE, GENOME_SCREEN))
    if gn_doc is not None:
        m = gn_doc.get("method") or {}
        _assert_geometry("gap_region_1based", m.get("gap_region_1based"),
                         GEOMETRY.gap_region_1based, GENOME_SCREEN)
        states["genome_grch38"] = _screen_state(
            os.path.join(HERE, GENOME_SCREEN), True,
            {"reference": gn_doc.get("reference"), "denominator": gn_doc.get("denominator")})
    else:
        states["genome_grch38"] = _screen_state(
            os.path.join(HERE, GENOME_SCREEN), False,
            {"why": ("artifact absent. The scan streams the whole soft-masked GRCh38 primary "
                     "assembly, so it runs in CI: dispatch .github/workflows/aso-offtarget.yml "
                     "with screen_mode 'genome' and suffix_tag '-noncoding-acceptor'. Absent is "
                     "NOT clean — the genome compartment is UNMEASURED for these designs.")})

    parent = APJT._load(PARENT_SCREEN) if pa_doc else {}
    premrna = APJT._load(PREMRNA_SCREEN) if pm_doc else {}
    genome = APJT._load(GENOME_SCREEN) if gn_doc else {}
    # ⛔ THE TWO PATHS COEXIST PER JUNCTION, AND LEARNING THAT COST A ROW (2026-08-15). This read
    # `if deep: … else: …`, so the moment ONE junction's alignment screen landed, every junction
    # WITHOUT one vanished from the table — PGR e2 :: NR4A3 e2 went from a row of explicit nulls to
    # no row at all. That is the absent-reading failure in its purest form: "this junction's screens
    # have not run" and "this junction does not exist" rendered identically, and the disappearance
    # was caused by a DIFFERENT junction's screen succeeding. Screen state is per junction, so the
    # table is built per junction: complete rows where an alignment screen exists, explicit-null
    # rows where it does not, and never a junction dropped because a sibling was luckier.
    lane_screens_all_ran = all(s["ran"] for s in states.values())
    junctions = APJT.junction_rows(deep, parent, premrna, genome) if deep else []
    for j in junctions:
        j["screens_complete"] = lane_screens_all_ran
    covered = {j["junction_label"] for j in junctions}
    for j in _partial_rows(parent, premrna, genome, skip=covered):
        j["screens_complete"] = False
        junctions.append(j)
    junctions.sort(key=lambda j: str(j["junction_label"]))

    # ⛔ EVERY SOURCE SCREEN IS SEAM-GRADED BEFORE ITS NUMBERS ARE QUOTED. The CI publish sweeps the
    # `modalities-cache` tree; the copies committed HERE sit in a subdirectory the repo-level sweep
    # does not reach, and an unswept artifact is exactly the state that let thirteen retracted
    # panels sit on a branch for a month. So the check happens in the producer instead.
    # ⚠ THROUGH `JSR.sweep(..., write=False)`, WHICH OWNS THOSE FILENAME PATTERNS, RATHER THAN A
    # LOCAL LISTING: `tests/test_one_geometry_screen_loading.py` fails the build on any module that
    # discovers these artifacts by pattern, and it is right to — a bare family prefix is how the
    # geometry-mixing defect reached six modules. One home for the globs, one home for the grader.
    seam_grades = {r["path"]: r["grade"] for r in JSR.sweep(SCREEN_DIR, write=False)}
    bad = sorted(n for n, g in seam_grades.items() if g not in (JSR.GRADE_CORRECT,
                                                               JSR.GRADE_MODELLED))
    if bad:
        raise SystemExit(
            f"seam grade {[seam_grades[n] for n in bad]} on {bad} — refusing to publish a table "
            "over an artifact whose acceptor seam the corrected transcript model does not produce.")

    provenance["screens"] = states
    provenance["seam_grades"] = seam_grades
    provenance["atlas"] = ATLAS
    return {
        "_title": ("The published NON-CANONICAL NR4A3 fusion junctions, screened to the panel's "
                   "depth and joined into the panel's field set"),
        "_generated_by": "research/modalities/aso_noncoding_acceptor_screened_table.py",
        "⛔_this_is_not_the_manuscript_panel": (
            "Every junction here is one the manuscript's 38-junction panel EXCLUDES, by a "
            "protein-level filter: the acceptor exon carries no CDS, or the chimeric register does "
            "not compose. They are screened because an RNase-H1 gapmer cleaves a transcript rather "
            "than a protein. Do not pool these rows into the panel's counts."),
        # ⛔ THIS SENTENCE MUST NAME THE PATH THAT ACTUALLY BUILT THE ROWS. It read "…by
        # aso_per_junction_table.junction_rows — the same grader the panel's table uses" while the
        # partial path was in fact building them, which is a provenance field asserting a code path
        # that did not run: the same class of error as a stale "screened", in the field a reader
        # checks to see how much weight the rows carry.
        "⚠_not_a_measurement_of_its_own": (
            "Nothing here was re-screened. A junction with `screens_complete: true` had its rows "
            "built by aso_per_junction_table.junction_rows — the same grader the panel's table "
            "uses, called with a different root — and every field is joined from a screen artifact "
            "that ran. A junction with `screens_complete: false` has NOT had its alignment screen "
            "run: its rows come from this module's `_partial_rows`, carry the same field names "
            "(checked against the panel artifact's own row keys), leave every field of an unrun "
            "screen null and listed in `⛔_unmeasured_fields`, and have no `best_available`, "
            "because the rank key is one of the unmeasured fields. ⛔ The flag is PER JUNCTION: a "
            "sibling junction's screen succeeding says nothing about this one."),
        "⛔_two_axes_not_one": (
            "gap_specificity_margin (fusion-versus-parent discrimination) and the transcriptome "
            "load move in opposite directions at some seams and are never combined into a single "
            "score. Ranking is by load among designs clearing the parent screen; margin is printed "
            "beside it, exactly as in the panel's table."),
        "geometry": GEOMETRY.as_dict(),
        "_geometry_is_asserted": (
            "load_screens(GEOMETRY, …) refuses any BLAST-family artifact of another geometry, and "
            "the parent-duplex and pre-mRNA and genome artifacts are checked against the same "
            "geometry from the block each of them states about itself."),
        "screens": states,
        "n_screens_that_ran": sum(1 for s in states.values() if s["ran"]),
        "n_screens_outstanding": sum(1 for s in states.values() if not s["ran"]),
        "seam_grades_of_the_source_artifacts": seam_grades,
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
            print(f"non-canonical screened table --check: MISSING {OUT}")
            return 1
        if json.load(open(OUT, encoding="utf-8")) != out:
            print("non-canonical screened table --check: STALE — re-run "
                  "aso_noncoding_acceptor_screened_table.py")
            return 1
        print(f"non-canonical screened table --check: OK ({out['n_junctions']} junctions, "
              f"{out['n_screens_that_ran']}/{len(out['screens'])} screens)")
        return 0
    os.makedirs(SCREEN_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    for name, s in out["screens"].items():
        print(f"  screen {name:<28} {'RAN' if s['ran'] else 'NOT RUN'}")
    for j in out["junctions"]:
        b = j["best_available"]
        print(f"  {j['junction_label']:<24}{j['clinical_tier']:<34}"
              f"{j['n_designs_clearing_the_parent_screen']}/{j['n_designs_screened']} clear parent")
        if b:
            print(f"      best {b['antisense_5to3']}  margin={b['gap_specificity_margin']}  "
                  f"loci={b['n_gap_paired_loci']}  hits={b['n_gap_paired']}  "
                  f"premRNA={b['premrna_gap_paired_hybridisable']}  "
                  f"parent={b['parent_duplex_bp']}bp  genome_oe={b['genome_oe_gap_paired_le2']}  "
                  f"named_sites={b['genome_named_target_sites']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
