#!/usr/bin/env python3
"""The gap-length trade-off: the complement identity, the parameterisation, and the baseline.

⛔ WHY THIS EXISTS. Three distinct things can go wrong here and only the first is obvious.

  1. THE FINDING can be misstated. It rests on an identity — inside the catalytic gap, the
     junction-unique bases on the shorter side and the bases a wild-type parent pairs on the longer
     side sum to the gap — so raising the gap-level margin raises the contiguous parent-paired DNA
     by the same nucleotide. If that identity is ever broken by a change to the tiler, the trade-off
     artifact would keep emitting both columns and they would silently stop being complements.

  2. THE BASELINE can move. Four modules were parameterised by geometry to make this measurable, and
     every one of them previously wrote to a fixed filename. The 16-mer artifacts are what the
     submission manuscript quotes, so a parameterisation that shifts them by one number is a
     correction to a published figure wearing the costume of a refactor. Each is pinned here.

  3. THE PARAMETERISATION CAN BE INERT. `nr4a3_fusion_atlas` honouring OUT_SUFFIX, and the workflow
     deriving SCREEN_TOP_N from the dispatched geometry, are both properties asserted in prose about
     values passed by a caller — which CLAUDE.md section 6 records as "not a property; it is a hope".
     They are asserted against the real module and the real workflow file instead.
"""
import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
ART = os.path.join(MOD, "aso-gap-length-tradeoff.json")
WORKFLOW = os.path.join(REPO, ".github", "workflows", "aso-offtarget.yml")
sys.path.insert(0, MOD)


#: ⛔ NOT SKIPS (2026-08-19, lane C2 audit). The trade-off artifact, all three atlases and the
#: workflow file are COMMITTED, so an absence is a broken tree — and the gap-length trade is the
#: paper's second headline. A guard that vanishes with its input reports green for a check nobody
#: performed, which is the class the pypdf/pymupdf audit found in this suite.
def _art():
    if not os.path.exists(ART):
        pytest.fail(f"the gap-length trade-off artifact is missing at {ART}; it is committed, and "
                    "the direction of the trade the paper reports is unchecked without it.")
    return json.load(open(ART, encoding="utf-8"))


def _atlas(suffix):
    p = os.path.join(MOD, f"nr4a3-fusion-junction-atlas{suffix}.json")
    if not os.path.exists(p):
        pytest.fail(f"the atlas{suffix} is missing at {p}; all three geometries' atlases are "
                    "committed, and the trade cannot be compared across geometries without them.")
    return json.load(open(p, encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1 · the identity the finding rests on
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_gap_halves_are_complements_at_every_geometry():
    """margin + parent-paired DNA == gap, for every design. This IS the trade-off.

    A failure means the two columns of the artifact have stopped being two views of one
    subtraction, at which point the claim that they move together nucleotide for nucleotide is no
    longer supported by the numbers beside it.
    """
    art = _art()
    gaps = {g["architecture"]: g["gap_nt"] for g in art["geometries"] if g.get("present")}
    assert gaps, "no geometry is present in the artifact"
    for r in art["per_design"]:
        gap = gaps[r["architecture"]]
        assert r["gap_specificity_margin"] + r["parent_paired_gap_dna_nt"] == gap, r
        assert r["parent_seam_hybrid_bp"] == r["parent_paired_gap_dna_nt"] + 5, r


def test_a_longer_gap_raises_the_margin_and_the_parent_paired_dna_together():
    """The direction of the trade, asserted rather than described."""
    art = _art()
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit). All three geometries are `present` in the
    #: committed artifact. Fewer than two means a regeneration dropped one — precisely the edit
    #: after which the direction of the trade must be re-checked, not the edit after which this
    #: test should fall silent.
    present = [g for g in art["geometries"] if g.get("present")]
    assert len(present) >= 2, (
        f"only {len(present)} geometry is marked present in {ART}, so there is no trade to "
        "compare and this test asserted nothing. The committed artifact carries three; a "
        "regeneration that drops one is what this guard has to speak about.")
    present.sort(key=lambda g: g["gap_nt"])
    best_margin = [max(int(k) for k in g["gap_margin_distribution"]) for g in present]
    worst_dna = [max(int(k) for k in g["parent_paired_gap_dna_distribution"]) for g in present]
    assert best_margin == sorted(best_margin), best_margin
    assert worst_dna == sorted(worst_dna), worst_dna
    # ⚠ AND THE COST IS NOT OPTIONAL AT THE LONGEST GAP. Every design of the widest geometry must
    # present some wild-type parent with at least the SMALLER reported RNase-H1 minimum, because the
    # smaller half of a gap of 10 cannot be under 5. If this ever passes vacuously the identity
    # above has been broken.
    widest = present[-1]
    floor = min(art["thresholds"]["min_contiguous_dna_nt_for_rnaseh1"]["values"])
    if widest["gap_nt"] >= 2 * floor:
        assert (widest["n_reaching_reported_dna_minimum"][str(floor)]
                == widest["n_fusion_specific_designs"])


def _keys(node):
    """Every key name anywhere in the artifact, so the guard below reads FIELDS and not prose."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from _keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from _keys(v)


def test_no_composite_score_is_emitted():
    """The two directions must never be collapsed, so no combined rank may appear in the artifact.

    ⚠ KEYS ONLY. The first version matched the serialised artifact and failed on the sentence that
    PROMISES no composite rank — a guard tripped by its own rationale. What must not exist is a
    FIELD a reader could sort on; saying so in prose is the opposite of the defect.
    """
    art = _art()
    banned = re.compile(r"combined_score|composite|overall_rank|total_score", re.I)
    offenders = sorted({k for k in _keys(art) if banned.search(k)})
    assert not offenders, f"a composite score field appeared in the trade-off artifact: {offenders}"
    assert "_never_collapse_these" in art["the_trade"]


def test_the_thresholds_are_anchored_to_committed_quotes_not_recollection():
    """Gate-4 discipline: both reported minima must resolve to a fragment in the committed anchor."""
    art = _art()
    thr = art["thresholds"]["min_contiguous_dna_nt_for_rnaseh1"]
    lit = json.load(open(os.path.join(REPO, thr["anchor_file"]), encoding="utf-8"))
    quotes = {(r["pmid"], q["fragment"]) for r in lit["records"] for q in r["quotes"]}
    assert set(thr["values"]) == {int(k) for k in thr["anchors"]}
    for _nt, a in thr["anchors"].items():
        assert (a["pmid"], a["fragment"]) in quotes, a


def test_the_lead_reagent_row_is_present_and_covers_three_partners():
    """The one candidate with a clinical readership. Its row must exist at every geometry present."""
    art = _art()
    lead = art["lead_reagent_at_the_most_commonly_reported_seam"]["by_geometry"]
    present = {g["architecture"] for g in art["geometries"] if g.get("present")}
    assert set(lead) == present
    for arch, row in lead.items():
        assert row.get("n_partners_covered_exactly") == 3, (arch, row)
        # the coverage ceiling is a property of the transcripts and cannot move with geometry
        assert row["bases_from_donor"] <= row["maximal_shared_donor_run_nt"], (arch, row)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2 · the baseline the manuscript quotes must not have moved
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_16mer_parent_duplex_artifact_still_reproduces():
    import aso_parent_gap_pairing as m  # noqa: PLC0415
    assert m.OLIGO_LEN == 16 and m.WING == 5, "the default geometry moved"
    assert m.main(["--check"]) == 0, "aso-parent-gap-pairing.json no longer reproduces"


def test_the_16mer_thermo_artifact_still_reproduces():
    import junction_aso_thermo as m  # noqa: PLC0415
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit): `junction-aso-thermo.json` is committed. The
    #: guarded expression was also inert — `m.build.__module__` is a non-empty string for any
    #: imported function, so the condition reduced to "the artifact is missing".
    if not os.path.exists(m.OUT):
        pytest.fail(f"the thermo artifact is missing at {m.OUT}; it is committed, and whether it "
                    "still reproduces from its generator is exactly what this test measures.")
    assert m.main(["--check"]) == 0, "junction-aso-thermo.json no longer reproduces"


def test_the_premrna_seed_blocks_reproduce_the_literal_they_replaced():
    """The partition was `[(0, 6), (6, 11), (11, L)]`. At L=16 the derivation must equal it exactly.

    And at any length the blocks must PARTITION the window, because completeness at <=2 mismatches
    is a pigeonhole argument over disjoint blocks covering the whole window — not a property of
    their sizes.
    """
    import aso_premrna_offtarget as m  # noqa: PLC0415
    assert m.seed_blocks(16) == [(0, 6), (6, 11), (11, 16)]
    assert m.N_SEED_BLOCKS == m.MAX_MM + 1
    for length in (16, 18, 20, 25):
        b = m.seed_blocks(length)
        assert len(b) == m.N_SEED_BLOCKS
        assert b[0][0] == 0 and b[-1][1] == length
        assert all(b[i][1] == b[i + 1][0] for i in range(len(b) - 1))
        assert all(end > start for start, end in b)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3 · the parameterisation is wired, not merely documented
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_atlas_output_path_actually_follows_out_suffix():
    """⛔ A SUFFIX THAT DOES NOT MOVE THE FILE IS THE BUG IT EXISTS TO PREVENT.

    Re-imported under a set OUT_SUFFIX, because the path is resolved at import: asserting on the
    already-imported module would test the environment this test process happens to have.
    """
    import importlib  # noqa: PLC0415
    prev = os.environ.get("OUT_SUFFIX")
    try:
        os.environ["OUT_SUFFIX"] = "-unit-test-suffix"
        mod = importlib.reload(importlib.import_module("nr4a3_fusion_atlas"))
        assert mod.OUT.endswith("nr4a3-fusion-junction-atlas-unit-test-suffix.json"), mod.OUT
    finally:
        if prev is None:
            os.environ.pop("OUT_SUFFIX", None)
        else:
            os.environ["OUT_SUFFIX"] = prev
        importlib.reload(importlib.import_module("nr4a3_fusion_atlas"))


def test_screen_top_n_defaults_to_six_and_follows_the_environment():
    """The default must be untouched, or every committed screen's scope silently re-bases."""
    import importlib  # noqa: PLC0415
    prev = os.environ.get("SCREEN_TOP_N")
    try:
        os.environ.pop("SCREEN_TOP_N", None)
        m = importlib.reload(importlib.import_module("junction_aso_offtarget"))
        assert m.N_OLIGOS == 6
        os.environ["SCREEN_TOP_N"] = "9"
        m = importlib.reload(importlib.import_module("junction_aso_offtarget"))
        assert m.N_OLIGOS == 9
        assert m.screen_parameters()["screen_top_n"] == 9
        assert "SCREEN_TOP_N" in m.screen_parameters()["overridden_from_env"]
    finally:
        if prev is None:
            os.environ.pop("SCREEN_TOP_N", None)
        else:
            os.environ["SCREEN_TOP_N"] = prev
        importlib.reload(importlib.import_module("junction_aso_offtarget"))


def test_the_workflow_derives_screen_top_n_from_the_dispatched_geometry():
    """⛔ THE SHELL IS THE THING UNDER TEST, SO IT IS RUN, NOT READ.

    A grep for the arithmetic would pass on a line that never executes. This extracts nothing and
    asserts nothing about the text; it reproduces the workflow's own derivation and checks that a
    blank geometry leaves the knob UNSET — the property that keeps every existing dispatch
    bit-for-bit unchanged — while 18,5 and 20,5 select every junction-spanning register.
    """
    if not os.path.exists(WORKFLOW):
        pytest.fail(f"the off-target workflow is missing at {WORKFLOW}; it is committed, and the "
                    "screen-depth derivation this test reproduces lives only there.")
    body = open(WORKFLOW, encoding="utf-8").read()
    assert "SCREEN_TOP_N=$(( OLIGO_LEN - 2 * WING - 1 ))" in body, \
        "the workflow no longer derives SCREEN_TOP_N from the geometry"
    script = (
        'OLIGO_LEN="${G%%,*}"; case "$G" in *,*) WING="${G#*,}" ;; *) WING="" ;; esac\n'
        'if [ -n "${OLIGO_LEN:-}" ] && [ -n "${WING:-}" ]; then '
        'SCREEN_TOP_N=$(( OLIGO_LEN - 2 * WING - 1 )); fi\n'
        'echo "${SCREEN_TOP_N:-unset}"\n')
    for geometry, expected in (("", "unset"), ("18,5", "7"), ("20,5", "9")):
        got = subprocess.run(["sh", "-c", script], env={**os.environ, "G": geometry},
                             capture_output=True, text=True, check=True).stdout.strip()
        assert got == expected, f"geometry {geometry!r} derived {got!r}, expected {expected!r}"


def test_the_registers_per_seam_are_gap_minus_one_at_every_geometry():
    """`GAP - 1` is why SCREEN_TOP_N has to follow the geometry. Measured from the atlases."""
    art = _art()
    for g in art["geometries"]:
        if not g.get("present"):
            continue
        atlas = _atlas(g["suffix"])
        assert g["junction_spanning_registers_per_seam"] == g["gap_nt"] - 1
        for panel in atlas["panels"]:
            assert panel["n_fusion_specific"] <= g["gap_nt"] - 1, panel["junction_label"]


def test_the_screen_union_never_pools_two_search_depths():
    """⛔ A UNION ACROSS CEILINGS PRODUCES A NUMBER THAT DESCRIBES NEITHER POPULATION.

    Three junctions carry two screens each, because an NCBI transport drop hit a different design in
    each run. Unioning them recovers every record — but the same mechanism would happily pool a
    default-ceiling screen with a deep one, which is exactly the defect 5233cf867 corrected in the
    collapse artifact (a widening glob moved a manuscript-quoted median from 2.14 to 4.55 with no
    science behind it). The union is therefore gated on a RECORDED, IDENTICAL depth pair, and a
    screen that cannot prove its depth never joins one.
    """
    import aso_gap_length_tradeoff as m  # noqa: PLC0415
    deep = {"method": {"parameters": {"blast_hitlist_size": 500, "saved_hits_per_design": 500}},
            "oligos": []}
    shallow = {"method": {"parameters": {"blast_hitlist_size": 50, "saved_hits_per_design": 15}},
               "oligos": []}
    unrecorded = {"method": {}, "oligos": []}
    cands = [("deep-a.json", deep), ("deep-b.json", dict(deep)),
             ("shallow.json", shallow), ("unrecorded.json", unrecorded)]
    sibs = sorted(f for f, _ in m._same_depth_siblings(cands, deep))
    assert sibs == ["deep-a.json", "deep-b.json"], sibs
    # a screen with no recorded depth cannot anchor a union either
    assert m._same_depth_siblings(cands, unrecorded) == []


def test_the_union_recovers_dropped_records_without_editing_any_screen():
    """Every design at a matched seam must carry a count, and no artifact may have been merged.

    ⚠ THE RECOVERY MUST COME FROM A NAMED FILE. `_from_screen` records which run supplied each
    design's record, so a reader can see that a recovered design came from the sibling rather than
    from an edit to the primary screen.
    """
    art = _art()
    m = art["the_trade"]["transcriptome_coincidence_falls_but_it_MUST"]["matched_junctions"]
    if not m["n_junctions"]:
        pytest.skip("no matched junctions in this checkout")
    for arch, v in m["by_geometry"].items():
        assert v["n_designs_the_remote_service_dropped"] == 0, (arch, v["designs_with_no_count"])
    # every screened row names the file it came from, and that file exists
    named = 0
    for r in art["per_design"]:
        a = r.get("alignment_screen") or {}
        if a.get("status") != "screened":
            continue
        src = a.get("_from_screen")
        assert src, r
        assert os.path.exists(os.path.join(MOD, src)), src
        named += 1
    assert named


def test_locus_counts_are_recounted_with_todays_parser_not_read_from_the_screen():
    """⛔ THE SCREENS' OWN LOCUS FIELDS WERE PRODUCED BY A PARSER THAT OVER-COUNTED.

    `locus_of` took the symbol as the last parenthesised token BEFORE THE FIRST COMMA, so a gene
    whose description contains a comma lost its symbol and every transcript variant fell back to its
    own accession. On this lane's lead reagent that turned ONE locus (nine GMCL1 variants) into
    nine, and `n_loci_with_a_gap_spanning_hit` read 14 where the corrected parser reads 6.

    A failed parse can only SPLIT a locus, never merge two, so the error is strictly one-directional
    and every stored field is an over-count. This asserts the artifact recomputes rather than reads,
    which is what makes the correction durable: reading the field again would silently reintroduce
    the inflation the moment anyone regenerates.
    """
    art = _art()
    sys.path.insert(0, MOD)
    from junction_aso_locus_collapse import locus_of  # noqa: PLC0415

    # the parser fix itself, on the two deflines that named it
    assert locus_of({"defn": "Homo sapiens germ cell-less 1, spermatogenesis associated (GMCL1), "
                             "mRNA", "acc": "NM_178439.4"}) == "GMCL1"
    assert locus_of({"defn": "Homo sapiens glucosaminyl (N-acetyl) transferase 3, mucin type "
                             "(GCNT3), mRNA", "acc": "NM_004751.3"}) == "GCNT3"

    checked = 0
    for r in art["per_design"]:
        a = r.get("alignment_screen") or {}
        if a.get("status") != "screened":
            continue
        loci, old = a["loci"], a["_superseded_locus_counts_from_the_old_parser"]
        checked += 1
        # the recount never exceeds what the superseded parser reported, on any design
        if old.get("n_loci_with_a_gap_spanning_hit") is not None and loci["exact"]:
            assert loci["n_loci_with_a_gap_spanning_hit"] <= old["n_loci_with_a_gap_spanning_hit"], r
        if old.get("n_distinct_loci") is not None and loci["exact"]:
            assert loci["n_distinct_loci"] <= old["n_distinct_loci"], r
        # a locus list and its count are one fact
        assert len(loci["loci_with_a_gap_spanning_hit"]) == loci["n_loci_with_a_gap_spanning_hit"]
        # no accession ever survives as a locus name where the recount is exact
        if loci["exact"]:
            assert not [s for s in loci["loci_with_a_gap_spanning_hit"]
                        if re.fullmatch(r"[NX][MR]_\d+", s)], (
                "an accession fallback survived the corrected parser", r)
    if not checked:
        pytest.skip("no alignment screens in this checkout")


def test_the_lead_reagent_locus_counts_are_the_corrected_ones():
    """The number the correction actually moved, pinned so it cannot drift back to 14."""
    art = _art()
    lead = art["lead_reagent_at_the_most_commonly_reported_seam"]["by_geometry"]
    row = lead.get("5-6-5")
    if not row or (row.get("alignment_screen") or {}).get("status") != "screened":
        pytest.skip("the 5-6-5 lead has no alignment screen in this checkout")
    loci = row["alignment_screen"]["loci"]
    assert loci["exact"], "the lead's hit list must be complete for this count to be a measurement"
    assert loci["n_loci_with_a_gap_spanning_hit"] == 6, loci
    assert loci["loci_with_a_gap_spanning_hit"] == [
        "ANKS1B", "CHST5", "GMCL1", "LOC105370997", "LOC105374140", "ZNF667"], loci
    assert row["alignment_screen"]["_superseded_locus_counts_from_the_old_parser"][
        "n_loci_with_a_gap_spanning_hit"] == 14


def test_a_screen_with_no_hits_is_not_graded_strand_blind():
    """⛔ THE CLEANEST POSSIBLE SCREEN WAS BEING LABELLED THE LEAST TRUSTWORTHY.

    `screen_orientation_status` decided "was orientation parsed" by looking for `hit_frame` on a
    stored hit. A screen whose every design returns NO near-match stores no hit, so the flag never
    went true and the screen was graded `orientation_UNPARSED_counts_are_upper_bounds` — an absent
    reading reported as a reading of absence, on a set of counts that are all zero and cannot be
    upper bounds of anything.

    ⚠ AND THE TRUNCATION CASE MUST STILL FAIL. Zero STORED hits against a non-zero near-match count
    is a censored screen, not an empty one: its hits exist and their strand is unrecoverable, so it
    keeps the upper-bound label. Both directions are asserted, because a fix that admitted the
    censored case would hand a clean verdict to exactly the screens the retraction history is about.
    """
    import junction_aso_offtarget as jo  # noqa: PLC0415
    empty = {"oligos": [{"status": "screened", "antisense_5to3": "A" * 20,
                         "n_offtarget_near_matches": 0, "offtargets": []}]}
    assert jo.screen_orientation_status(empty) == jo.ORIENTATION_NO_HITS
    assert jo.screen_counts_are_orientation_filtered(empty)

    censored = {"oligos": [{"status": "screened", "antisense_5to3": "A" * 20,
                            "n_offtarget_near_matches": 7, "offtargets": []}]}
    assert jo.screen_orientation_status(censored) == jo.ORIENTATION_UNPARSED
    assert not jo.screen_counts_are_orientation_filtered(censored)

    # and the state is distinct from "hits existed and every minus-strand one was diverted"
    assert jo.ORIENTATION_NO_HITS != jo.ORIENTATION_FILTERED


def test_every_new_geometry_screen_is_orientation_safe():
    """A geometry comparison must not put a filtered count beside a strand-blind one."""
    import aso_screen_sets as ass  # noqa: PLC0415
    import junction_aso_offtarget as jo  # noqa: PLC0415
    # ⛔ "LONGER GEOMETRY" IS A MEASUREMENT, NOT THE SUBSTRING `mer-deep500` (2026-08-14). That
    # pattern misses a longer-geometry screen re-dispatched under any other spelling — three
    # `-18mer-deep500-b2` / `-20mer-deep500-b2` files are already on disk and it matches none of
    # them — so this guard was silently narrower than its own name. Every geometry that is NOT the
    # manuscript's is checked here, whatever its file is called.
    longer = [s for g, ss in ass.iter_geometries(ass.BLAST_SCREEN, root=MOD)
              if g != ass.MANUSCRIPT_GEOMETRY for s in ss]
    if not longer:
        pytest.skip("no longer-geometry screens in this checkout")
    for s in sorted(longer, key=lambda x: x.name):
        assert jo.screen_counts_are_orientation_filtered(s.artifact), (
            f"{s.name} is {jo.screen_orientation_status(s.artifact)} — its counts cannot "
            "be compared with an orientation-filtered geometry")


def test_the_artifact_reproduces_from_its_committed_inputs():
    """`--check` is the artifact's own reproduction test; a stale artifact fails here."""
    import aso_gap_length_tradeoff as m  # noqa: PLC0415
    assert m.main(["--check"]) == 0, "aso-gap-length-tradeoff.json is stale; re-run the script"


def test_the_artifact_refuses_to_imply_efficacy_or_safety():
    """Language discipline, on a file a reader can download without the manuscript around it."""
    art = _art()
    txt = json.dumps(art["_what_this_is_not"]) + json.dumps(art.get("_what", ""))
    for required in ("Not a cleavage measurement", "clinical-readiness"):
        assert required in txt, required
