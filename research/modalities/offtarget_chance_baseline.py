#!/usr/bin/env python3
"""
Is an off-target count a finding, or is it what any 16-mer would return? — the missing null.

⛔ WHY THIS EXISTS, AND IT INVALIDATES A HEADLINE. The manuscript's central negative was "0 of 58
designs is predicted off-target-clean". A referee pointed out that this is arithmetically
unavoidable, and the arithmetic checks out: the number of 16-mers within 2 substitutions of a given
16-mer is 1,129, so the probability that an arbitrary transcriptome position matches at >= 14/16 is
1129 / 4^16 = 2.6e-07. Against a human RefSeq RNA set of order 1e8-1e9 nucleotides that is TENS TO
HUNDREDS of expected near-matches PER OLIGO, for any 16-mer whatsoever — a scrambled control, a
marketed gapmer, a random string. "Zero near-matches at >= 14/16" is not an achievable state, so a
count of zero-clean designs is a property of the threshold and the size of the transcriptome, not a
property of EMC, NR4A3, or fusion junctions.

⭐ WHAT REPLACES IT. The informative quantity is not whether a design has hits; it is whether it has
MORE hits than chance. This module computes the chance expectation under an explicit null and
reports every committed design as observed-versus-expected. A design at or below expectation is not
"clean" — nothing is — but it is "no worse than an arbitrary oligonucleotide of its length", which is
a defensible statement, is what a chemist actually wants to know, and is the statement the paper
could not previously make.

⚠ THE NULL IS DELIBERATELY CRUDE, AND ITS LIMITS RUN IN BOTH DIRECTIONS. It assumes independent,
uniformly distributed bases. Real transcriptomes are neither: base composition is skewed, sequence is
repetitive, paralogues and transcript variants of one locus multiply near-matches, and a GC-rich or
low-complexity query is enriched for partners. So this is an ORDER-OF-MAGNITUDE reference, not a
p-value, and it is used here only to answer a coarse question — is an observed count in the region
chance alone predicts, or far above it? A design far above chance is a real finding about that
sequence. A design at chance is a statement that the screen found nothing specific to it.
⛔ In particular this must NEVER be reported as a significance test, and no threshold on the ratio is
proposed here, because the null is too crude to license one.

⛔⛔ A PANEL FILE IS NOT A JUNCTION, AND THE GLOB WAS TREATING IT AS ONE (2026-08-13). The input
pattern `aso-insilico-evaluation*.json` was written when one junction meant one file. It stopped
meaning that when the deeper re-screen campaign began emitting a second evaluation per junction under
its own suffix, and `*` matched every one of them. MEASURED 2026-08-13, hours after the first such
panel was committed: a plain `python3 offtarget_chance_baseline.py` read 51 panels instead of 40 and
reported `n_designs` 255 against the committed 200, `mean` 8.1 against 9.5,
`n_at_or_below_chance_upper` 192 against 142, and 61 multi-junction oligonucleotides spanning [2, 4]
seams against the committed 9 spanning [2, 3]. The file reproduced its own artifact only under the
non-default `--panels-from-artifact`.
⚠ THE WINDOW WAS HOURS, NOT WEEKS, AND THAT IS THE WARNING RATHER THAN THE COMFORT. The first
re-emitted panel and the reading above landed the same day, so nothing had time to be quoted from
the wrong population — but the campaign was still running while this was being fixed, and it was:
thirteen further panels under a THIRD suffix (`-deep500-b2`) appeared between writing the fix and
verifying it. A defect that arrives faster than a session can read the directory is not one a
remembered exclusion list can keep up with.
⚠ THE INFLATED MULTI-JUNCTION COUNT IS THE TELL, AND IT NAMES THE MECHANISM. `dedupe_sequences`
exists to stop one physical oligonucleotide being counted once per junction; it keys on the sequence
and appends a junction label per row. Two panels for the SAME junction therefore appended the SAME
label twice, and a design at one seam was recorded as spanning two. So this was not "extra data" —
it was the pseudoreplication that function was written to prevent, reappearing one level above it,
in the step that decides what a panel IS.
⭐ WHAT THE FIX IS, AND WHY IT IS NOT A FILENAME RULE. `-deep500` is a convention, and a convention
is not a discriminator: three spellings are already on disk (`-deep500`, `-clean9-deep500`,
`-deep500-b2`) and the next one will be whatever the next campaign chooses. Excluding a spelling only
holds until somebody spells it differently, which is the failure this repository has paid for before.
So selection is done on the SEAM a panel says it screened (`seam_identity`), read from the panel's own
record: a junction that already has a screen is not a new junction, whatever the file is called.
✅ AND THAT WAS TESTED BY EVENTS RATHER THAN BY ASSERTION. `-deep500-b2` did not exist when this rule
was written; thirteen panels carrying it landed before it was verified, and the default invocation
absorbed all thirteen and still reproduced the artifact byte-for-byte. A suffix blacklist written
that morning would already have been out of date by the afternoon.
⚠ AND THE PANELS DO NOT RECORD THE DEPTH THEY RAN AT — checked, across all 51 files on disk: the
union of their top-level keys is `_note, accessibility, breakpoint, junction_label,
n_candidates_*, n_evaluated, offtarget_screen, ranking_key, sirna_note, top_designs`, and
`offtarget_screen` carries only `status`, `transcripts_scanned` and `source`. A depth-aware rule is
therefore not available to write today, and cannot be until the producer records it. Nor can depth be
inferred from the counts: this artifact reads `offtarget_le1mm`, which is the UNCAPPED local scan and
not the capped BLAST hitlist, so a deeper search ceiling cannot move it — measured, every re-emitted
panel is value-for-value identical to the primary it duplicates, while the deep SCREEN artifacts
(`junction-aso-offtarget-*-deep500.json`, a different file and a different quantity) report counts
for the same designs of up to 305 against an evaluation panel's 0. Two evaluations of one seam that
disagree are therefore not a shallow and a deep reading of one quantity; they are two different
evaluations, and this module refuses them rather than picking.

Outputs: offtarget-chance-baseline.json
"""

import json
import os
import sys
import time
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aso_screen_sets as ass                                            # noqa: E402

OUT = os.path.join(HERE, "offtarget-chance-baseline.json")

#: ⛔⛔ THE NULL IS A FUNCTION OF THE LENGTH, SO THE PANEL SET AND THE LENGTH MOVE TOGETHER OR THE
#: WHOLE ARTIFACT IS WRONG. `n_within(length, 2) / 4**length` is the entire model: at 16 it is
#: 1129/4^16 = 2.6e-07, at 18 it is 1.0e-08 — a factor of 26. An 18-mer panel scored against this
#: 16-mer expectation would be graded against a null predicting 26 times too many hits, and every
#: one of its designs would come back "far below chance". That is the flattering direction, on the
#: module whose only job is to say whether a count is a finding.
#: ⭐ NAMED AS A GEOMETRY RATHER THAN AN INT (2026-08-14), so the panel selection and the null are
#: the same fact rather than two constants that agree today. `load_screens` has no default
#: geometry; this is what this module passes it.
GEOMETRY = ass.MANUSCRIPT_GEOMETRY
OLIGO_LEN = GEOMETRY.oligo_len

#: A source panel counts as a REAL junction only if its own record says its seam was built from a
#: spliced transcript model. Both remaining panels predate that rebuild: neither carries a
#: `junction_label`, and the one that carries a breakpoint at all states it in AMINO-ACID
#: coordinates (`EWSR1_keep_aa` / `NR4A3_from_aa`), i.e. a protein-coordinate seam of the kind the
#: manuscript's Declarations record as withdrawn in full. The classification is therefore read off
#: each source file, never inferred from a filename.
REAL_JUNCTION_BREAKPOINT_MODE = "real_exon_junction_mRNA"
#: ⚠ *Superseded, retained:* "Transcriptome size is not recorded by the screens (they record
#: transcript COUNT, 186,185, not nucleotides), so the expectation is reported as a RANGE over a
#: plausible span rather than as a single number nobody measured. Naming the uncertainty is the
#: point; picking a midpoint would hide it." That was the right call while the span was unmeasured,
#: and it cost the manuscript a 2.7x-wide band on its central quantitative claim ("79-210",
#: "3.4-9.1"). ⛔ THE SPAN WAS NEVER HARD TO MEASURE — the scan loop in `aso_insilico.py` reads every
#: base of every transcript and simply did not count them. It now does, so the expectation below is
#: referred to a COUNTED denominator and is a single figure.
#: The fallback range is kept for a checkout whose eval artifacts predate the accumulator; a run that
#: falls back SAYS SO in the artifact rather than silently reporting a wider band as if measured.
TRANSCRIPTOME_NT_RANGE = (3.0e8, 8.0e8)


def measured_transcriptome_nt():
    """The scanned nucleotide span, read from whichever committed eval artifact recorded it.

    Returns (nt, source_filename) or (None, None). ⛔ REQUIRES AGREEMENT: if two artifacts report
    different spans the corpus changed under the screens, and an expectation computed against either
    one would be referred to a denominator half the panel was not measured against. That refuses
    rather than picking.

    ⚠ AGREEMENT IS CHECKED ACROSS EVERY GEOMETRY; ATTRIBUTION IS NOT (2026-08-14). The span is a
    property of the DATABASE, not of the oligonucleotide, so an 18-mer panel reporting a different
    span is still evidence the corpus moved and must still refuse — the check stays global. But the
    filename this returns is published as `transcriptome_nt_source`, and naming a panel this
    artifact does not use misattributes the manuscript's denominator: on merge the 18-mer screens
    sorted first and took the credit for a 16-mer corpus's span. So the source is preferentially a
    panel of this corpus's own geometry, and the value it carries is identical either way.

    ⛔ AND "PANEL WHOSE LENGTH COULD NOT BE MEASURED" IS NOT "PANEL OF OUR GEOMETRY" (2026-08-14).
    The first version of that preference read `if not lens or lens == {OLIGO_LEN}`, which credits a
    panel holding no design as though it had been measured and agreed — an absent reading rendered
    as a reading of absence, in a provenance field. The loader answers the same question by
    returning only what it could measure at this geometry, so a panel that states nothing is simply
    not a candidate for the credit rather than a silent winner of it.
    ⚠ The ITERATION ORDER is deliberately global-alphabetical, unchanged: `seen[nt]` is a
    first-wins fallback and re-ordering it would move a published `transcriptome_nt_source` string.
    """
    seen, same_geometry = {}, {}
    same_names = {os.path.basename(p) for p in panel_paths()}
    every = sorted((s for _g, ss in ass.iter_geometries(ass.DESIGN_EVALUATION, root=HERE)
                    for s in ss), key=lambda s: s.name)
    for s in every:
        scr = s.artifact.get("offtarget_screen") or {}
        nt = scr.get("scanned_nt")
        if not (isinstance(nt, int) and nt > 0):
            continue
        seen.setdefault(nt, s.name)
        if s.name in same_names:
            same_geometry.setdefault(nt, s.name)
    if not seen:
        return None, None
    if len(seen) > 1:
        raise RuntimeError(
            "eval artifacts disagree about the scanned transcriptome span: %s. One expectation "
            "cannot be referred to two denominators; re-run the scans or exclude the stale ones."
            % {k: v for k, v in sorted(seen.items())})
    nt = next(iter(seen))
    return nt, same_geometry.get(nt, seen[nt])


def n_within(length, mismatches):
    """How many distinct strings lie within `mismatches` substitutions of one string of `length`."""
    return sum(comb(length, k) * 3 ** k for k in range(mismatches + 1))


_MEASURED_NT, _MEASURED_SRC = None, None


def chance_expectation(length, mismatches):
    """(p_per_position, (lo, hi) expected hits per oligo) under an i.i.d. uniform-base null.

    When the span has been measured the two bounds are the SAME number, so every consumer keeps
    working unchanged and a reader can see at a glance whether the expectation is a range or a
    measurement.
    """
    global _MEASURED_NT, _MEASURED_SRC
    p = n_within(length, mismatches) / 4 ** length
    nt, src = measured_transcriptome_nt()
    _MEASURED_NT, _MEASURED_SRC = nt, src
    spans = (nt, nt) if nt else TRANSCRIPTOME_NT_RANGE
    return p, tuple(round(p * n, 1) for n in spans)


def seam_class(d):
    """('real_exon_junction'|'modelled_breakpoint', the breakpoint record that decided it)."""
    bp = d.get("breakpoint") or {}
    if d.get("junction_label") and bp.get("mode") == REAL_JUNCTION_BREAKPOINT_MODE:
        return "real_exon_junction", bp.get("mode")
    return "modelled_breakpoint", (bp or None)


def seam_identity(d):
    """WHICH SEAM this panel screened, read from the panel's own record and never from its filename.

    ⛔ THIS IS THE DISCRIMINATOR, AND ITS WHOLE VALUE IS THAT A NEW SUFFIX CANNOT DEFEAT IT. A
    re-screen re-runs a junction; it does not invent one. So the label a panel states is the identity
    that matters, and two panels stating the same label are two readings of one seam however they are
    named.

    ⚠ THE TWO LEGACY CONTROL PANELS STATE NO LABEL, and falling back to their filename would put the
    hole straight back — a re-emission of one of them would key on its own basename and duplicate
    silently, which is exactly the defect this function exists to close. What identifies THEIR seam is
    what they do record: the breakpoint they declare (one states it in amino-acid coordinates, the
    other declares none at all) and the accessibility window that breakpoint produced. Both are
    properties of the seam, so a re-emission of the same seam carries the same pair.
    """
    label = d.get("junction_label")
    if label:
        return ("junction_label", label)
    return ("unlabelled_seam",
            json.dumps(d.get("breakpoint") or {}, sort_keys=True),
            json.dumps((d.get("accessibility") or {}).get("window_mRNA_span")))


def _panel_measurements(d):
    """{sequence: every value this module reads from that design} — the panel's whole contribution.

    Scoped deliberately to what is READ. Two panels that differ only in a field nothing here consumes
    are the same measurement for this artifact's purposes, and refusing them would be a false alarm.
    """
    return {o["antisense_5to3"]: (o.get("gc_percent"), o.get("offtarget_exact"),
                                  o.get("offtarget_le1mm"))
            for o in d.get("top_designs", []) if o.get("offtarget_le1mm") is not None}


def panel_oligo_lens(d):
    """The design lengths a panel actually evaluated, from its own designs and not its filename.

    ⭐ ONE HOME (2026-08-14). This measurement existed here, in `junction_aso_locus_collapse`, in
    `aso_per_junction_table` and inline in three tests — five copies of one rule, four of which
    checked only the LENGTH while a screen also states where its gap is. It now asks
    `aso_screen_sets`, which checks both.
    """
    return {ass.measure_oligo_len(ass.DESIGN_EVALUATION, d)} - {None}


def panel_paths():
    """Every design-evaluation panel of THIS module's geometry, through the one loader.

    ⛔ NOT A GLOB. `aso-insilico-evaluation*.json` matches 18-mer and 20-mer panels too, and this
    module's docstring records that a plain invocation over that glob DIED. `load_screens` measures
    each panel's design length, checks it against whatever the panel states about itself, and
    returns only the one geometry; there is no call it could have made that returns a mixed set.
    """
    return [s.path for s in ass.load_screens(GEOMETRY, ass.DESIGN_EVALUATION, root=HERE)]


def select_primary_panels(paths):
    """(the one panel per seam this artifact is built from, what was set aside and why).

    ⛔ A DISAGREEMENT IS REFUSED, NOT RESOLVED. Because `offtarget_le1mm` is the uncapped scan, two
    evaluations of one seam cannot legitimately differ by search depth — so if they differ at all
    they are different evaluations, and choosing between them is a data decision with manuscript
    consequences that must not be taken as a side effect of a regeneration. The refusal names both
    files and the escape (`--panels-from-artifact`), because a gate that stops the work without
    saying what to do next is a gate that gets deleted.

    ⚠ THE TIE-BREAK IS A FILENAME, AND THAT IS DELIBERATELY THE ONLY THING A FILENAME DECIDES HERE.
    Once the copies are proven value-for-value identical, NOTHING in their content distinguishes
    them, so the choice cannot move a number — it decides only which `_source` string is recorded.
    The primary screen's name is a prefix of every re-emission of it, so the primary is the shortest;
    ties after that are lexicographic, so the selection is deterministic.

    ⛔ THE KEY IS (SEAM, GEOMETRY), NOT SEAM ALONE (2026-08-14). Two panels are re-emissions of each
    other only if they screened the same seam WITH THE SAME REAGENT. The gap-length work evaluates
    these seams at 18 and 20 nucleotides as well, and grouping those with the 16-mer panel of the
    same seam made this function raise its "two different evaluations" refusal on every build. The
    refusal was right about the fact and wrong about the remedy: they are different evaluations
    because they are different molecules, so they must not be compared, rather than one being chosen
    over the other. Length is measured from the designs, never from the filename, which is the same
    rule `seam_identity` follows and for the same reason.
    ⭐ THE COMPOUND KEY IS THE LOADER'S SHAPE (2026-08-14) — `aso_screen_sets.group_by_geometry_and`
    exists because this is not a one-off: any artifact that says "two records are re-emissions of
    each other" needs (what was measured, what it was measured WITH). Built here from the same
    measurement so the key cannot be right in this module and subtly different in the next one.
    """
    groups = {}
    for path in paths:
        d = json.load(open(path))
        key = (seam_identity(d), tuple(sorted(panel_oligo_lens(d))))
        groups.setdefault(key, []).append((path, d))

    chosen, collapsed = [], []
    for members in groups.values():
        members.sort(key=lambda pd: (len(os.path.basename(pd[0])), os.path.basename(pd[0])))
        primary, d_primary = members[0]
        for other, d_other in members[1:]:
            if _panel_measurements(d_primary) != _panel_measurements(d_other):
                raise ValueError(
                    f"{os.path.basename(primary)} and {os.path.basename(other)} evaluate the same "
                    f"seam and report different off-target counts. They are two different "
                    f"evaluations, not a shallow and a deep reading of one, so this module will not "
                    f"choose between them. Decide which panel set this artifact is about, then "
                    f"either retire the stale file or regenerate with --panels-from-artifact.")
            collapsed.append({"kept": os.path.basename(primary),
                              "set_aside": os.path.basename(other)})
        chosen.append((primary, d_primary))
    chosen.sort(key=lambda pd: pd[0])
    return chosen, collapsed


def committed_panel_set():
    """The source panels the CURRENTLY COMMITTED artifact was built from, or None if there is none.

    ⚠ WHY A CALLER WOULD EVER WANT THIS. The panel set grows: junctions acquire an uncapped
    <=1-mismatch screen at different times, and every one that lands changes every count derived
    here — the median, the at-or-below fraction, and therefore the figure and the sentences the
    manuscript writes off them. Regenerating over a LARGER panel set is a data decision with
    manuscript consequences, so it must be taken deliberately and not as a side effect of somebody
    fixing an unrelated defect in the same file. `--panels-from-artifact` pins the panel set to the
    committed one so that a derivation change can be shipped on its own; the default remains "read
    everything that exists", which is what a refresh should do.
    """
    try:
        d = json.load(open(OUT))
    except (OSError, ValueError):
        return None
    return {r["_source"] for r in d.get("per_design", [])} or None


def collect_observed(panels=None, collapsed=None, off_geometry=None):
    """Every committed design's uncapped <=1-mismatch count, keyed by junction and sequence."""
    # ⛔ GEOMETRY IS PART OF A PANEL'S IDENTITY, AND WITHOUT THIS THE MODULE REFUSES TO BUILD AT ALL
    # (2026-08-14). The gap-length work evaluates the same seams at 18-mer 5-8-5 and 20-mer 5-10-5
    # and writes them under this same glob. `seam_identity` keys on the junction label — correctly,
    # because a re-screen must not escape it by renaming itself — so an 18-mer panel of the EWSR1
    # e12 seam grouped with the 16-mer one, their counts differed, and `select_primary_panels` threw:
    # "two different evaluations, not a shallow and a deep reading of one". That refusal was RIGHT,
    # and this is the answer to the question it asks. They are different evaluations because they
    # are different reagents, so they are separated before grouping rather than chosen between. This
    # artifact is the manuscript's 16-mer corpus; `aso_gap_length_tradeoff.py` owns the contrast
    # across geometries, where the comparison is like-for-like by construction.
    # ⚠ AND THE SELECTION IS AT `GEOMETRY`, THE SAME GEOMETRY THE EXPECTATION IS COMPUTED AT, because
    # that is what makes it a correctness guard rather than a scoping preference: every `expected`
    # below is `chance_expectation(OLIGO_LEN, k)` with `OLIGO_LEN = GEOMETRY.oligo_len`, so an
    # 18-mer observation admitted here would be divided by a 16-mer expectation and the ratio would
    # belong to neither length.
    # ⭐ THE SEPARATION IS THE LOADER'S (2026-08-14): the glob-then-filter above was a third hand
    # written copy of the same rule, and it treated a panel whose length could not be measured as
    # in-geometry (`if lens and lens != {OLIGO_LEN}` keeps an empty `lens`) — an absent reading read
    # as a reading of absence. `load_screens` returns only what it MEASURED at this geometry, so an
    # unmeasurable panel is excluded rather than admitted, and the exclusion is reported below.
    every = sorted((s for _g, ss in ass.iter_geometries(ass.DESIGN_EVALUATION, root=HERE)
                    for s in ss), key=lambda s: s.name)
    keep_names = {os.path.basename(p) for p in panel_paths()}
    paths = []
    for s in every:
        if panels is not None and s.name not in panels:
            continue
        if s.name not in keep_names:
            if off_geometry is not None:
                off_geometry.append({"panel": s.name,
                                     "oligo_lens": [s.geometry.oligo_len]})
            continue
        paths.append(s.path)

    selected, dropped = select_primary_panels(paths)
    if collapsed is not None:
        collapsed.extend(dropped)

    rows = []
    for path, d in selected:
        label = d.get("junction_label") or os.path.basename(path)
        cls, bp = seam_class(d)
        for o in d.get("top_designs", []):
            if o.get("offtarget_le1mm") is None:
                continue
            rows.append({"junction": label, "antisense_5to3": o["antisense_5to3"],
                         "gc_percent": o.get("gc_percent"),
                         "offtarget_exact": o.get("offtarget_exact"),
                         "offtarget_le1mm": o["offtarget_le1mm"],
                         "_source": os.path.basename(path),
                         "seam_class": cls,
                         "breakpoint_record": bp,
                         "transcripts_scanned":
                             (d.get("offtarget_screen") or {}).get("transcripts_scanned")})

    # ⛔ THE INVARIANT, ASSERTED WHERE IT IS CHEAP TO ASSERT. A row of `per_design` is a
    # (junction, design) PAIR and each pair may appear exactly once; every count, fraction and span
    # below is arithmetic over these rows. Nothing checked this, so when a second panel per junction
    # appeared the population silently grew by a quarter and every derived number moved with it, in a
    # file whose whole job is to say what a number means. `select_primary_panels` is the fix and this
    # is the guard: it is one dict comparison, it is independent of how panels are chosen, and it
    # fails loudly the next time something enlarges this population by a route nobody anticipated.
    seen = {}
    for r in rows:
        key = (r["junction"], r["antisense_5to3"])
        if key in seen:
            raise ValueError(
                f"design {r['antisense_5to3']} appears twice at {r['junction']} — from "
                f"{seen[key]} and {r['_source']}. A (junction, design) pair is one row; counting it "
                f"twice is pseudoreplication and moves every figure derived below.")
        seen[key] = r["_source"]
    return rows


def dedupe_sequences(rows):
    """One entry per distinct oligonucleotide, in the row order first seen.

    ⛔ WHY THIS EXISTS, AND WHAT IT FIXES. A row of `per_design` is a (junction, design) PAIR, not a
    molecule. Five of these 16-mers are junction-spanning at THREE partners' seams at once — the
    multi-partner designs the manuscript headlines — so each appears once per junction and any
    consumer that iterates rows counts one physical oligonucleotide three times. That is
    pseudoreplication, and it inflated the published at-or-below fraction. The de-duplicated view is
    built HERE rather than in a figure script so that every consumer gets the same one.

    The three copies of a multi-partner design are the same sequence screened against the same
    transcriptome, so their counts must agree; a disagreement would mean the screens are not
    comparable and is raised rather than silently resolved by picking a copy.
    """
    keyed = {}
    for r in rows:
        s = r["antisense_5to3"]
        prev = keyed.get(s)
        if prev is None:
            keyed[s] = {"antisense_5to3": s, "junctions": [r["junction"]],
                        "n_junctions": 1, "seam_class": r["seam_class"],
                        "gc_percent": r["gc_percent"],
                        "offtarget_exact": r["offtarget_exact"],
                        "offtarget_le1mm": r["offtarget_le1mm"],
                        "_sources": [r["_source"]]}
            continue
        for k in ("gc_percent", "offtarget_exact", "offtarget_le1mm", "seam_class"):
            if prev[k] != r[k]:
                raise ValueError(
                    f"the same oligonucleotide {s} carries {k}={prev[k]!r} at "
                    f"{prev['junctions'][0]} and {r[k]!r} at {r['junction']}; the copies are not "
                    "the same screen and must not be merged")
        prev["junctions"].append(r["junction"])
        prev["_sources"].append(r["_source"])
        prev["n_junctions"] += 1
    return list(keyed.values())


def _uniform(vals):
    """The single value shared by every element, or a raise — never a silent pick."""
    s = set(vals)
    if len(s) != 1:
        raise ValueError(f"expected one shared value, got {sorted(s)}")
    return s.pop()


def _span(vals):
    """[min, max] over a non-empty iterable, for captions that quote a range."""
    v = sorted(vals)
    return [v[0], v[-1]]


def build(panels=None, collapsed=None, off_geometry=None):
    p2, exp2 = chance_expectation(OLIGO_LEN, 2)
    p1, exp1 = chance_expectation(OLIGO_LEN, 1)
    # ⛔ THE OFF-GEOMETRY LIST IS COLLECTED WHETHER OR NOT A CALLER ASKED FOR IT, because it is now
    # part of the ARTIFACT and not just of `main`'s stderr readout. `collapsed` and `off_geometry`
    # are out-parameters for that readout, and leaving the artifact's content dependent on whether
    # one was passed would mean `build()` and `main()` produced different bytes — a `--check` that
    # compares them would then be red on a tree nobody had touched. One artifact, one content.
    off_geometry = [] if off_geometry is None else off_geometry
    rows = collect_observed(panels, collapsed, off_geometry)
    counts = sorted(r["offtarget_le1mm"] for r in rows)
    n = len(counts)
    median = counts[n // 2] if n % 2 else (counts[n // 2 - 1] + counts[n // 2]) / 2
    lo, hi = exp1

    for r in rows:
        c = r["offtarget_le1mm"]
        r["expected_le1mm_lo"], r["expected_le1mm_hi"] = lo, hi
        r["at_or_below_chance"] = c <= hi
        r["ratio_to_chance_hi"] = round(c / hi, 2) if hi else None

    seqs = dedupe_sequences(rows)
    for s in seqs:
        c = s["offtarget_le1mm"]
        s["expected_le1mm_lo"], s["expected_le1mm_hi"] = lo, hi
        s["at_or_below_chance"] = c <= hi
        s["ratio_to_chance_hi"] = round(c / hi, 2) if hi else None
    seqs.sort(key=lambda s: (s["offtarget_le1mm"], s["antisense_5to3"]))

    plotted = [s for s in seqs if s["seam_class"] == "real_exon_junction"]
    excluded = [s for s in seqs if s["seam_class"] != "real_exon_junction"]
    exc_above = [s for s in excluded if not s["at_or_below_chance"]]
    multi = [s for s in plotted if s["n_junctions"] > 1]
    scanned = sorted({r["transcripts_scanned"] for r in rows})

    return {
        "_title": "Chance baseline for junction-gapmer off-target counts",
        "_generated_by": "research/modalities/offtarget_chance_baseline.py",
        "_cost": "$0 — arithmetic over committed artifacts. No network, no GPU.",
        # ⛔ NO TIMESTAMP. A wall-clock field in a DERIVED artifact makes regeneration
        # non-idempotent: the file changes on every run whether or not a single input did,
        # so "did anything actually change?" stops being answerable by a diff. That question
        # is load-bearing here — an unattended routine folds new junction screens in only
        # when the chain produces a diff, and a per-run timestamp would make it report a
        # change every hour with nothing behind it. The inputs are content-hashed and the
        # git history already records when this ran, which is the same information without
        # the cost. Superseded, retained (rule 1.2): `"_utc": time.strftime(...)`.
        "_why": (
            "The manuscript's negative headline — '0 of 58 designs predicted off-target-clean' — is "
            "arithmetically unavoidable at a >=14/16 identity threshold and therefore says nothing "
            "about this disease, this fusion, or these junctions. This file computes what chance "
            "alone predicts, so an observed count can be read against it."),
        "_what_this_is_not": [
            "NOT a significance test and NOT a p-value. The null assumes independent uniform bases; "
            "real transcript sequence is composition-skewed, repetitive, and full of paralogues and "
            "transcript variants of one locus. It is an order-of-magnitude reference only.",
            "NOT a cleanliness criterion. Nothing here licenses calling any design clean, and no "
            "threshold on the observed/expected ratio is proposed, because the null cannot support "
            "one.",
            "NOT a substitute for calibration against oligonucleotides with MEASURED off-target "
            "behaviour, which is what would actually convert these counts into a decision and which "
            "this repository has not done.",
        ],
        # ⛔ THE PANELS THIS CORPUS DECLINED FOR BEING A DIFFERENT REAGENT LENGTH (published
        # 2026-08-14). Until then this was printed to STDERR ONLY, and stderr does not survive into
        # the record: nothing a reader of the deposited artifact could do would recover it.
        # ⚠ THE ARGUMENT THAT KEPT THE *COLLAPSE* OUT OF THE ARTIFACT DOES NOT REACH HERE, WHICH IS
        # WHY ONE IS PUBLISHED AND THE OTHER STILL IS NOT. That argument is "the artifact already
        # names every panel it used in `per_design[]._source`" — true of a collapsed re-emission,
        # whose seam IS in the file under the panel that was kept, and FALSE of an off-geometry
        # panel, which was excluded outright. Measured on the committed artifact before this change:
        # the twelve excluded 18-mer and 20-mer panels appear nowhere in it, and the strings "18mer"
        # and "20mer" occur zero times. A reader could not tell that a longer-geometry panel of a
        # seam existed and was declined, nor — the fail-quiet direction — that some seam was absent
        # from this corpus entirely because it was only ever evaluated at 18-mer.
        # ⭐ AND `junction_aso_locus_collapse` ALREADY PUBLISHES EXACTLY THIS, under exactly this
        # name. Two modules making the same geometry decision with two visibilities is how one of
        # them silently stops being true.
        "⛔_one_geometry": (
            f"Every count in this file is the {OLIGO_LEN}-mer panel the manuscript reports. Panels "
            f"at other geometries are evaluated under the same filename glob and are listed in "
            f"`other_geometries` rather than pooled: the expectation below is computed at "
            f"{OLIGO_LEN} nt, so a count taken across geometries describes none of them."),
        "manuscript_oligo_len": OLIGO_LEN,
        "other_geometries": sorted(
            ({"panel": g["panel"], "oligo_lens": list(g["oligo_lens"])}
             for g in (off_geometry or [])),
            key=lambda g: (g["oligo_lens"], g["panel"])),
        "null_model": {
            "oligo_len": OLIGO_LEN,
            "assumption": "independent, uniformly distributed bases",
            "transcriptome_nt": _MEASURED_NT or None,
            "transcriptome_nt_source": _MEASURED_SRC or None,
            "transcriptome_nt_range_assumed": (None if _MEASURED_NT
                                               else list(TRANSCRIPTOME_NT_RANGE)),
            "_transcriptome_nt_caveat": (
                ("MEASURED, not assumed: %d nucleotides counted across the scan's 186,185 "
                 "transcripts, read from %s. Every expectation below is therefore a single figure. "
                 "Superseded, retained: the span used to be assumed over 3e8-8e8 nt because the "
                 "screens recorded transcript COUNT and not bases, which made the manuscript's "
                 "headline expectations a 2.7x-wide band." % (_MEASURED_NT, _MEASURED_SRC))
                if _MEASURED_NT else
                "The screens record transcripts SCANNED (186,185), not nucleotides, so the "
                "nucleotide span is assumed over a range rather than measured. Every expectation "
                "below inherits that range. ⚠ THIS IS THE FALLBACK: an eval artifact recording "
                "`scanned_nt` would make it a measurement, and none was found in this checkout."),
            "n_strings_within_2_substitutions": n_within(OLIGO_LEN, 2),
            "p_per_position_ge_14_of_16": p2,
            "expected_near_matches_per_oligo_ge_14_of_16": list(exp2),
            "n_strings_within_1_substitution": n_within(OLIGO_LEN, 1),
            "p_per_position_ge_15_of_16": p1,
            "expected_hits_per_oligo_ge_15_of_16": list(exp1),
        },
        "observed": {
            "n_designs": n,
            "min": counts[0], "median": median, "max": counts[-1],
            "mean": round(sum(counts) / n, 1),
            "n_at_or_below_chance_upper": sum(1 for r in rows if r["at_or_below_chance"]),
            "_unit_caveat": (
                "⚠ THESE ARE ROWS, NOT MOLECULES. A row is a (junction, design) pair, and five "
                "designs are junction-spanning at three seams each, so they are counted three "
                "times here. Anything that reports a FRACTION OF DESIGNS must read "
                "`observed_distinct_sequences` or `figure_series` instead; this block is retained "
                "because per-junction consumers legitimately want the per-junction rows."),
        },
        "observed_distinct_sequences": {
            "_what": (
                "The same designs counted as PHYSICAL OLIGONUCLEOTIDES: one entry per distinct "
                "antisense sequence, whatever number of junctions it spans."),
            "n_rows": n,
            "n_sequences": len(seqs),
            "n_sequences_spanning_multiple_junctions": len(multi),
            "junctions_spanned_by_each_of_those": sorted({s["n_junctions"] for s in multi}),
            "n_at_or_below_chance_upper": sum(1 for s in seqs if s["at_or_below_chance"]),
        },
        "figure_series": {
            "_what": (
                "Exactly what the manuscript's chance-baseline figure draws, resolved here so the "
                "drawing script computes nothing: one bar per distinct oligonucleotide at a REAL "
                "exon junction, ranked by observed load."),
            "unit": "one distinct oligonucleotide",
            "seam_class_plotted": "real_exon_junction",
            "transcripts_scanned": scanned[0] if len(scanned) == 1 else scanned,
            "n_plotted": len(plotted),
            "n_at_or_below_chance_upper": sum(1 for s in plotted if s["at_or_below_chance"]),
            "n_above_chance_upper": sum(1 for s in plotted if not s["at_or_below_chance"]),
            "n_multi_junction_sequences": len(multi),
            #: A scalar when every multi-junction oligo spans the same number of seams, because a
            #: caption has to say "each spans N junctions" in words; `[min, max]` when they differ,
            #: because then that sentence is false and the caption has to quote a range.
            #: ⛔ THIS WAS `_uniform(...)`, WHICH RAISED AND STOPPED THE SCRIPT DEAD (2026-08-13).
            #: `_uniform` refuses a mixed set by design — correctly, since silently picking one
            #: value would put a false "each spans 3" into a caption. But refusing is right for a
            #: VALUE and wrong for a SCRIPT: the committed artefact was built from a panel set in
            #: which every multi-junction oligo spanned three seams, and the wider set now on disk
            #: holds both two- and three-seam oligos, so a plain `python3 offtarget_chance_baseline.py`
            #: died on `expected one shared value, got [2, 3]`.
            #: ⚠ AND THAT MADE A MANUSCRIPT SENTENCE FALSE. The Availability paragraph names five
            #: recomputations that run offline; four were verified byte-identical with the network
            #: hard-blocked and this was the fifth. Naming them item by item is what made the claim
            #: falsifiable, and it is how this surfaced. The module already carried `_span` for
            #: exactly this shape.
            #: ⚠ *Superseded, retained (rule 1.2): "The committed artefact does not move: its panel
            #: set is uniform, so this still emits the scalar 3. Only the wider set gets a range."*
            #: The committed artefact was never uniform and has always emitted the LIST [2, 3] —
            #: five oligonucleotides meet three seams and four meet two, which
            #: `test_the_figure_3_legend_matches_the_series_it_describes` has asserted all along.
            #: The claim was made about the artefact rather than read off it, and it read as
            #: reassurance that the change was inert. What actually did not move is the artefact's
            #: BYTES, which is checkable and was checked. A reader can still tell a scalar from a
            #: range by its type; that half stands.
            "multi_junction_span": (
                _uniform(s["n_junctions"] for s in multi) if len({s["n_junctions"] for s in multi}) == 1
                else _span(s["n_junctions"] for s in multi)),
            "multi_junction_sequences": [s["antisense_5to3"] for s in multi],
            "excluded": {
                "_why": (
                    "These panels' seams were not built from a spliced transcript model: neither "
                    "source records a `junction_label`, and the one that records a breakpoint at "
                    "all states it in amino-acid coordinates. They are modelled control seams, and "
                    "plotting them beside real junctions invites the reader to grade real designs "
                    "against sequence that no patient transcript is known to carry."),
                "n_excluded": len(excluded),
                "n_breakpoints": len({s["_sources"][0] for s in excluded}),
                "sources": sorted({s["_sources"][0] for s in excluded}),
                "n_at_or_below_chance_upper": len(excluded) - len(exc_above),
                "n_above_chance_upper": len(exc_above),
                "above_offtarget_le1mm": [s["offtarget_le1mm"] for s in exc_above],
                "above_offtarget_le1mm_range": _span(s["offtarget_le1mm"] for s in exc_above),
                "above_gc_percent": [s["gc_percent"] for s in exc_above],
                "above_gc_percent_range": _span(s["gc_percent"] for s in exc_above),
                "gc_percent_all": [s["gc_percent"] for s in excluded],
            },
            "series": plotted,
        },
        "_reading": (
            f"At the <=1-mismatch threshold chance alone predicts "
            f"{lo if lo == hi else f'{lo}-{hi}'} hits per 16-mer"
            f"{' over a MEASURED span' if lo == hi else ' over an assumed span range'}. The "
            f"observed median across {n} committed designs is {median}. The median design is "
            "therefore AT OR BELOW what an arbitrary oligonucleotide of this length would return, "
            "which is the honest form of the paper's specificity statement: no design is clean "
            "because no 16-mer can be, and most designs carry no more transcriptome load than "
            "chance. The outliers are the informative rows."),
        "per_design": rows,
        "per_sequence": seqs,
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    panels = committed_panel_set() if "--panels-from-artifact" in argv else None
    if panels is not None:
        print(f"panel set pinned to the committed artifact's {len(panels)} sources", file=sys.stderr)
    collapsed = []
    off_geometry = []
    res = build(panels, collapsed, off_geometry)
    new = json.dumps(res, indent=2)

    # ⚠ AND SO IS THE GEOMETRY EXCLUSION, for the same reason as the collapse below: a panel set
    # aside for being a different reagent length must be visible where the operator is looking,
    # or the next person to add a geometry sees a corpus that silently ignored it.
    if off_geometry:
        print(f"{len(off_geometry)} panel(s) at other geometries excluded from this "
              f"{OLIGO_LEN}-mer corpus (the expectation is computed at {OLIGO_LEN} nt):",
              file=sys.stderr)
        # ⚠ "excluded", not "set aside": the collapse readout below uses "set aside X -> kept Y",
        # and a line with the same verb and no `-> kept` reads as a truncated collapse rather than
        # as a different decision. Two kinds of omission, two unambiguous wordings.
        for g in off_geometry:
            print(f"  excluded {g['panel']} (designs of length "
                  f"{', '.join(str(n) for n in g['oligo_lens'])})", file=sys.stderr)

    # ⚠ THE COLLAPSE IS REPORTED, NEVER SILENT. A selection rule that quietly drops eleven files
    # reads exactly like the glob that quietly added them; the difference has to be visible at the
    # place the operator is looking. It is NOT written into the artifact: the artifact already names
    # every panel it used in `per_design[]._source`, and its bytes are hashed by
    # `aso-figure-provenance.json`, so a provenance block here would re-base a recorded hash to say
    # something the file can already answer.
    if collapsed:
        print(f"{len(collapsed)} re-emitted panel(s) collapsed onto the seam they re-screen "
              f"(identical off-target counts, so no value moves):", file=sys.stderr)
        for c in collapsed:
            print(f"  set aside {c['set_aside']} -> kept {c['kept']}", file=sys.stderr)

    # ⛔ A `--check` THAT WRITES IS NOT A CHECK. Until 2026-08-13 this module had no `--check` at
    # all, so `offtarget_chance_baseline.py --check` fell through to the write path: it OVERWROTE
    # the artifact it was being asked to verify and exited 0, which is the one behaviour a staleness
    # gate must never have. `regenerate_aso_chain.sh` records the absence as "(no --check mode;
    # verified by the tree diff below)" and can now use this instead.
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("offtarget-chance-baseline.json is stale; re-run without --check", file=sys.stderr)
            return 1
        print("chance-baseline artifact is current")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    print("wrote", OUT, file=sys.stderr)
    summary = {k: v for k, v in res.items() if k not in ("per_design", "per_sequence")}
    summary["figure_series"] = {k: v for k, v in summary["figure_series"].items()
                                if k != "series"}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
