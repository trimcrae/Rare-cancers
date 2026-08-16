#!/usr/bin/env python3
"""The transcript→locus collapse, and the censoring guard that stops it lying.

⛔ THE DANGEROUS FAILURE IS THE FLATTERING ONE. Every mistake this module can make — merging two
loci under one fallback key, counting a truncated top-15 sample as if it were the whole hit list —
makes a candidate look CLEANER than it is. Those are the cases asserted first.
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
sys.path.insert(0, MOD)

import junction_aso_locus_collapse as C  # noqa: E402


def _hit(acc, defn, risk="true_cleavage_risk"):
    return {"acc": acc, "defn": defn, "risk": risk}


def test_transcript_variants_of_one_gene_collapse_to_one_locus():
    hits = [_hit("NM_001001973", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), "
                                 "transcript variant 1, mRNA; nuclear gene"),
            _hit("NM_005174", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), "
                              "transcript variant 2, mRNA"),
            _hit("NM_001320886", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), "
                                 "transcript variant 3, mRNA")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 3})
    assert out["n_distinct_loci"] == 1
    assert out["inflation_factor"] == 3.0
    assert out["right_censored"] is False


def test_two_different_genes_do_not_collapse():
    hits = [_hit("NM_005174", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), variant 2"),
            _hit("NM_001271022", "Homo sapiens ATR interacting protein (ATRIP), variant 3, mRNA")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_distinct_loci"] == 2


def test_a_truncated_hit_list_is_marked_censored_and_publishes_no_inflation_factor():
    """⛔ THE GUARD THIS MODULE EXISTS UNDER. The screens save `ranked[:15]` and report the full
    count separately; 41 of 67 committed oligonucleotides are truncated, one of them from 50. If
    the collapse read the stored list as complete, a 16-mer with 50 near-matches would be published
    as touching one locus — the single most flattering error available here."""
    hits = [_hit(f"NM_{i:06d}", f"Homo sapiens gene {i} (GENE{i}), mRNA") for i in range(15)]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 50})
    assert out["right_censored"] is True
    assert out["inflation_factor"] is None, "a ratio of truncated to truncated bounds nothing"
    assert out["n_distinct_loci_is_a_lower_bound"] is True
    # and the count itself is still reported — a lower bound is information, silence is not
    assert out["n_distinct_loci"] == 15


def test_an_exactly_full_but_uncensored_list_is_not_marked_censored():
    hits = [_hit(f"NM_{i:06d}", f"Homo sapiens gene {i} (GENE{i}), mRNA") for i in range(15)]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 15})
    assert out["right_censored"] is False and out["inflation_factor"] == 1.0


def test_an_unparseable_definition_falls_back_to_the_accession_and_cannot_merge_loci():
    """⚠ THE FALLBACK DIRECTION IS LOAD-BEARING. A shared sentinel would merge every unparseable
    hit into one locus and UNDERCOUNT; falling back to the accession can only over-count."""
    hits = [_hit("NM_000001", "no parenthetical here at all"),
            _hit("NM_000002", "nor here")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_distinct_loci"] == 2
    assert out["n_loci_unresolved_to_a_symbol"] == 2


def test_curated_and_predicted_records_are_separated_not_pooled():
    hits = [_hit("XM_017018783", "Homo sapiens DEP domain containing 4 (DEPDC4), mRNA"),
            _hit("XR_007073896", "Homo sapiens uncharacterized LOC105374140 (LOC105374140), ncRNA"),
            _hit("NM_005174", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), variant 2")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 3})
    assert out["n_transcripts_predicted"] == 2 and out["n_transcripts_curated"] == 1
    assert out["n_loci_seen_only_as_predicted_models"] == 2
    assert out["n_loci_with_a_curated_transcript"] == 1


def test_a_locus_with_one_curated_and_one_predicted_variant_counts_as_curated_not_predicted_only():
    hits = [_hit("XM_017018783", "Homo sapiens DEP domain containing 4 (DEPDC4), mRNA"),
            _hit("NM_017018783", "Homo sapiens DEP domain containing 4 (DEPDC4), variant 1")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_distinct_loci"] == 1
    assert out["n_loci_seen_only_as_predicted_models"] == 0


def test_a_locus_is_a_gap_spanning_risk_if_any_of_its_variants_is():
    hits = [_hit("NM_000001", "Homo sapiens thing (AAA), variant 1", risk="gap_disrupted_no_cleavage"),
            _hit("NM_000002", "Homo sapiens thing (AAA), variant 2", risk="true_cleavage_risk")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_loci_with_a_gap_spanning_hit"] == 1 and out["loci_with_a_gap_spanning_hit"] == ["AAA"]


@pytest.mark.committed_artifact
def test_the_committed_collapse_summarises_only_uncensored_oligos():
    """⛔ ASSERTED AGAINST THE REAL ARTIFACT, NOT A FIXTURE. The headline medians are what the
    manuscript quotes, and the one way they go wrong is by silently including censored rows."""
    path = os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json")
    if not os.path.exists(path):
        pytest.skip("locus-collapse artifact is not present in this checkout")
    d = json.load(open(path))
    every = [o for s in d["screens"] for o in s["per_oligo"]]
    assert len(every) == d["n_oligos"]
    assert d["n_oligos_uncensored"] == sum(1 for o in every if not o["right_censored"])
    assert d["n_oligos_right_censored"] == sum(1 for o in every if o["right_censored"])
    assert d["n_oligos_right_censored"] > 0, (
        "if nothing is censored the guard is untested by the real data — check the screens still "
        "truncate, rather than assuming the collapse is safe")
    clean = [o for o in every if not o["right_censored"]]
    t = d["totals_over_uncensored_oligos_only"]
    assert t["distinct_loci_summed_over_oligos"] == sum(o["n_distinct_loci"] for o in clean)
    assert t["transcript_near_matches"] == sum(o["n_transcript_near_matches_stored"] for o in clean)
    assert all(o["inflation_factor"] is None for o in every if o["right_censored"])


@pytest.mark.committed_artifact
def test_the_lead_candidates_gap_spanning_load_is_the_one_locus_the_manuscript_claims():
    """The manuscript names ONE locus, LOC105374140, and no curated transcript, for
    5′-GGGCATATCATCAAAC-3′. Checked here rather than trusted — it is the sentence a reviewer is most
    likely to test.

    ⚠ THIS TEST PREVIOUSLY ASSERTED THREE LOCI, AND IT WENT RED BY DOING ITS JOB (2026-08-12). The
    orientation filter removed the hits at DEPDC4 and SGMS1 as minus-strand, leaving five
    gap-spanning hits that are all variants of one uncharacterised locus. The manuscript sentence
    was rewritten to match the artifact, and this assertion follows it. Superseded, retained: three
    loci, from the screens that counted both strands."""
    path = os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json")
    if not os.path.exists(path):
        pytest.skip("locus-collapse artifact is not present in this checkout")
    d = json.load(open(path))
    rows = [o for s in d["screens"] for o in s["per_oligo"]
            if o["antisense_5to3"] == "GGGCATATCATCAAAC"]
    assert rows, "the lead candidate is absent from every committed screen"
    for o in rows:
        assert o["right_censored"] is False, "the claim would be a lower bound, not a count"
        assert o["n_loci_with_a_gap_spanning_hit"] == 1, o["loci_with_a_gap_spanning_hit"]
        assert o["loci_with_a_gap_spanning_hit"] == ["LOC105374140"], (
            "the manuscript names this locus explicitly; if it moved, fix the manuscript too")
        curated_and_gap_spanning = (set(o["loci_with_a_gap_spanning_hit"])
                                    - set(o["loci_seen_only_as_predicted_models"]))
        assert not curated_and_gap_spanning, (
            f"the manuscript says none of the gap-spanning loci is curated, but {sorted(curated_and_gap_spanning)} "
            f"carries a curated transcript. Fix the manuscript, not this test.")


def test_the_clinically_relevant_reagents_deep_load_is_six_loci_not_123_transcripts():
    """⛔ THE ONE DESIGN AT A JUNCTION PATIENTS ACTUALLY CARRY, AND THE NUMBER MOST LIKELY TO BE
    MISREAD. 5′-GGGCATATCATCAAAC-3′ spans the EWSR1 e12 / TAF15 e11 / FUS e10 seams, the most
    commonly reported EMC junction. At ten times the default search depth it returns 189
    near-matches, and a reader who stops at that figure concludes the reagent is unusable.

    Three facts bound it, and the manuscript states all three because dropping any one of them
    changes the conclusion: the 123 gap-paired hits recount to SIX gene loci rather than 123 genes;
    every one of them sits at the screen's loosest admitted identity (14 of 16, i.e. two
    mismatches); and NO parent transcript is among them, which is the liability the whole modality
    turns on. Asserted against the artifact so the paper cannot drift off it.

    ⚠ This test is also why `locus_of` was fixed (2026-08-13). Under the old first-comma split,
    GMCL1's nine variants each became their own accession fallback and this count read FOURTEEN
    loci, not six — an inflated locus count reads as a dirtier reagent than the evidence supports,
    and it would have been quoted in a manuscript sentence about how many genes the design can
    cleave.
    """
    import junction_aso_offtarget as ja  # noqa: PLC0415
    from collections import Counter  # noqa: PLC0415

    path = os.path.join(MOD, "junction-aso-offtarget-e12n3-deep500-b1.json")
    if not os.path.exists(path):
        pytest.skip("the deep re-screen of the EWSR1 e12 junction is not in this checkout")
    d = json.load(open(path, encoding="utf-8"))
    o = next(x for x in d["oligos"] if x["antisense_5to3"] == "GGGCATATCATCAAAC")

    hits = o["offtargets"]
    assert len(hits) == o["n_offtarget_near_matches"] == 189, (
        "the deeper re-screen must retain every hit; a truncated list makes this a lower bound")

    lo, hi = ja.GAP_REGION_1BASED
    plus = [h for h in hits if not h.get("is_minus_strand")]
    spanning = [h for h in plus if h["q_from"] <= lo and h["q_to"] >= hi]
    paired = [h for h in spanning if h.get("gap_mismatches") == 0]
    assert (len(plus), len(spanning), len(paired)) == (141, 141, 123), (
        len(plus), len(spanning), len(paired))

    loci = Counter(C.locus_of(h) for h in paired)
    assert len(loci) == 6, sorted(loci)
    assert sum(n for _, n in loci.most_common(2)) == 104, loci.most_common()
    assert {"ANKS1B", "ZNF667"} == {s for s, _ in loci.most_common(2)}, loci.most_common(2)
    assert not any(s.startswith("acc:") for s in loci), (
        f"a hit failed to resolve to a gene symbol, which over-counts loci: {sorted(loci)}")

    # every one at the loosest identity the screen admits, so none is a close match
    assert {h["identity"] for h in paired} == {14}, sorted({h["identity"] for h in paired})

    # and no parent, which is the claim the modality depends on
    assert not (set(loci) & {"EWSR1", "TAF15", "FUS", "NR4A3", "TCF12", "TFG"}), sorted(loci)

    cls = Counter(C.accession_class(h) for h in paired)
    assert cls["predicted"] == 82 and cls["curated"] == 41, cls

    paper = os.path.join(REPO, "research", "manuscripts", "aso",
                         "fusion-junction-aso-research-article.md")
    if not os.path.exists(paper):
        pytest.skip("submission manuscript is not present in this checkout")
    txt = re.sub(r"\s+", " ", open(paper, encoding="utf-8").read())

    # ⛔⛔ `assert "189 near-matches" in txt` WAS MEASURING THE WRONG SENTENCE (found 2026-08-16).
    # 189 is this design's raw deep near-match count AND, by coincidence, the chance expectation the
    # Methods quote — "189 near-matches for any 16-mer whatever over the exhaustive scan's measured
    # span". When the editorial restructure moved this design's raw count out of the prose and into
    # generated Table 2, the assertion went on passing against the chance sentence, which is a
    # different quantity about a different population. A substring that two unrelated claims can both
    # satisfy is not a guard. The count is now checked WHERE IT LIVES — Table 2's deeper-ceiling
    # columns, generated from the screens — and against the design's own row.
    tables = os.path.join(REPO, "research", "manuscripts", "aso",
                          "fusion-junction-aso-submission-tables.md")
    if os.path.exists(tables):
        whole = open(tables, encoding="utf-8").read()
        assert "**Table 2." in whole, "Table 2 is not in the generated tables file"
        # ⚠ SCOPED TO TABLE 2's OWN BLOCK. This molecule has a row in four of the seven tables, and
        # they carry different quantities under similar-looking columns.
        body = whole[whole.index("**Table 2."):]
        body = body[:body.index("**Table 3.")] if "**Table 3." in body else body
        rows = [r for r in body.splitlines()
                if "5′-GGGCATATCATCAAAC-3′" in r and "::NR4A3 e3 |" in r]
        assert len(rows) == 3, rows          # the one molecule spans EWSR1 e12, TAF15 e11, FUS e10
        for r in rows:
            assert f"| {len(hits)} | {len(plus)} | {len(loci)} |" in r, r

    # ⭐ THE THREE BOUNDING FACTS MOVED TO §4.3 AND KEPT ALL THREE, 2026-08-16. "123 pair the
    # catalytic gap perfectly … They recount to six gene loci … no parent transcript is among them"
    # is now one clause where the reagent is recommended: "123 gap-paired sense-strand near-matches
    # at the deeper ceiling, recounting to six gene loci, all at the screen's loosest admitted
    # identity and none on a parent transcript". Asserted as one string, because the docstring above
    # is right that dropping any one of them changes the conclusion — and three separate substring
    # checks would let the sentence be split up until the bounds no longer travel with the number.
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
    assert (f"{len(paired)} gap-paired sense-strand near-matches at the deeper ceiling, recounting "
            f"to {words[len(loci)]} gene loci, all at the screen's loosest admitted identity and "
            f"none on a parent transcript") in txt
    # ⭐ AND THE PREDICTED/CURATED SPLIT, WHICH MOVED TO §5 AND GAINED ITS COMPLEMENT. "Of the 123,
    # 82 are `XM_`/`XR_` predicted models" is now "82 of the 123 are predicted models and the other
    # 41 are curated records", under a paragraph that has just defined the two namespaces — so the
    # curated count is stated rather than left to be subtracted, and both are derived here.
    assert (f"{cls['predicted']} of the {len(paired)} are predicted models and the other "
            f"{cls['curated']} are curated records") in txt
    # ⭐ THE TWO DOMINANT LOCI ARE STILL NAMED, ON THE CURATED SUBSET RATHER THAN ON ALL 123.
    # "*ANKS1B* and *ZNF667* supply 104 between them" became "those 41 are themselves inflated, 32 of
    # them *ANKS1B* accessions and three *ZNF667*" — the same two loci making the same
    # records-are-not-genes point, cut over the records where it bites hardest, since 32 curated
    # accessions of one gene is the sharper instance of inflation than 67 mixed ones. ⚠ MEASURED
    # OVER THE CURATED HITS HERE so the prose cannot borrow the all-123 figure for this sentence:
    # ANKS1B is 67 of 123 overall and 32 of the 41 curated, and those are different numbers.
    cur = Counter(C.locus_of(h) for h in paired if C.accession_class(h) == "curated")
    assert sum(cur.values()) == cls["curated"], cur
    assert (f"those {cls['curated']} are themselves inflated, {cur['ANKS1B']} of them *ANKS1B* "
            f"accessions and {words[cur['ZNF667']]} *ZNF667*") in txt
    # ⛔ AND THE DEPTH-DEPENDENCE OF THE CURATED SHARE, WHICH IS WHY THE DEFAULT-DEPTH READING OF THIS
    # DESIGN CANNOT BE CARRIED FORWARD. The prose used to say its one curated sense-strand hit is
    # *H2AP* while naming the deeper ceiling, which is false at that depth: at the default ceiling
    # the design has 1 curated sense-strand hit and at the deeper one it has 43. Both are counted
    # here from the two screens rather than taken from the sentence.
    shallow = os.path.join(MOD, "junction-aso-offtarget-e12n3.json")
    if os.path.exists(shallow):
        so = next(x for x in json.load(open(shallow, encoding="utf-8"))["oligos"]
                  if x["antisense_5to3"] == "GGGCATATCATCAAAC")
        s_plus = [h for h in so["offtargets"] if not h.get("is_minus_strand")]
        s_cur = [h for h in s_plus if C.accession_class(h) == "curated"]
        d_cur = [h for h in plus if C.accession_class(h) == "curated"]
        assert (len(s_cur), len(d_cur)) == (1, 43), (len(s_cur), len(d_cur))
        assert (f"At the default ceiling that design carried a single curated sense-strand hit, "
                f"*H2AP*,") in txt
        assert f"at the deeper ceiling it carries {len(d_cur)}" in txt


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


def test_every_blast_submission_happens_before_any_poll():
    """⛔ THE SCREEN'S WHOLE COST WAS THIS ORDERING (measured 2026-08-12). Submitting, blocking to
    READY, fetching, then starting the next design made a five-design junction pay five full BLAST
    round-trips back to back: 27.6 min per junction, ~5.5 h for the paper's twelve against a
    six-hour job ceiling. NCBI's URL API continues a search server-side whether or not anyone is
    waiting, so the searches were always parallel and only this client was serialising them.

    Asserted as an ORDERING rather than a duration, because a timing test would be flaky and would
    not say what went wrong. If a future edit reintroduces submit-then-wait inside the loop, the
    first poll moves ahead of the last submit and this fails."""
    import junction_aso_offtarget as M
    order = []
    put, poll, hits, sleep = M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep
    try:
        M.blast_put = lambda seq: (order.append(("put", seq)), f"RID_{seq}")[1]
        M.blast_poll = lambda rid: order.append(("poll", rid))
        M.blast_hits = lambda rid: []
        M.time.sleep = lambda s: None
        designs = [{"target_mRNA_5to3": f"SEQ{i}", "antisense_5to3": f"A{i}",
                    "gc_percent": 50.0, "specificity_margin": 3} for i in range(5)]
        recs = M.screen_all(designs)
    finally:
        M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep = put, poll, hits, sleep
    kinds = [k for k, _ in order]
    assert kinds.count("put") == 5 and kinds.count("poll") == 5 and len(recs) == 5
    assert max(i for i, k in enumerate(kinds) if k == "put") \
        < min(i for i, k in enumerate(kinds) if k == "poll"), (
        "a poll happened before the last submission — the screen is serial again")


def test_one_failed_submission_does_not_lose_the_other_designs():
    """Four transport failures are already on record and they are per-oligo. Batching must not turn
    one of them into a lost junction."""
    import junction_aso_offtarget as M
    put, poll, hits, sleep = M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep
    try:
        def flaky(seq):
            if seq == "SEQ2":
                raise RuntimeError("Remote end closed connection without response")
            return f"RID_{seq}"
        M.blast_put, M.blast_hits, M.time.sleep = flaky, (lambda rid: []), (lambda s: None)
        M.blast_poll = lambda rid: None
        designs = [{"target_mRNA_5to3": f"SEQ{i}", "antisense_5to3": f"A{i}",
                    "gc_percent": 50.0, "specificity_margin": 3} for i in range(5)]
        recs = M.screen_all(designs)
    finally:
        M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep = put, poll, hits, sleep
    assert len(recs) == 5
    assert sum(1 for r in recs if r.get("status") == "screened") == 4
    assert sum(1 for r in recs if r.get("status") == "screen_failed") == 1


def test_the_artifact_covers_one_geometry_and_names_the_screens_it_declines_to_pool():
    """⛔ GEOMETRY IS PART OF A SCREEN'S IDENTITY, EXACTLY AS DEPTH IS (2026-08-14).

    The gap-length work writes 18-mer 5-8-5 and 20-mer 5-10-5 screens under the same
    `junction-aso-offtarget-*` glob this module reads. Merging that branch and regenerating pooled
    them into the deep population: 38 screens/187 designs became 53/303 and
    `oligos_with_no_gap_spanning_locus` went 12 -> 110, which reads as a panel an order of magnitude
    cleaner and is only a wider glob. It is the same defect `5233cf867` fixed one axis out, where a
    widening glob moved a manuscript-quoted median from 2.14 to 4.55.

    ⚠ AND THEY MUST BE NAMED, NOT SILENTLY DROPPED. A filter that quietly excludes files is how the
    next geometry gets screened and then never noticed, so `other_geometries` lists every screen the
    partition set aside and this asserts the list is populated rather than merely present.
    """
    d = json.load(open(os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json"),
                       encoding="utf-8"))
    assert d["manuscript_oligo_len"] == C.MANUSCRIPT_OLIGO_LEN == 16

    for key in ("screens", "deep_screens"):
        for s in d[key]:
            assert s["oligo_len"] == 16, (
                f"{key}: {s['screen']} is a {s['oligo_len']}-mer screen inside the 16-mer "
                f"population; the geometry partition has stopped working")

    other = d["other_geometries"]
    assert other, ("no screen was set aside — either the longer geometries have left this "
                   "checkout, or the partition is matching nothing")
    assert {o["oligo_len"] for o in other} == {18, 20}, sorted({o["oligo_len"] for o in other})
    named = {o["screen"] for o in other}
    assert not (named & {s["screen"] for s in d["screens"] + d["deep_screens"]}), (
        "a screen is both counted and set aside")


def test_screen_oligo_len_is_measured_from_the_designs_not_the_filename():
    """A filename is a convention; the design length is the thing that ran.

    ⚠ Pre-2026-08-13 screens carry no geometry block at all, so a recorded field would be absent
    exactly where the partition is needed. A screen whose designs disagree is refused rather than
    guessed at, because pooling two lengths under one label is the failure being prevented.
    """
    assert C.screen_oligo_len({"oligos": [{"antisense_5to3": "A" * 20}]}) == 20
    assert C.screen_oligo_len({"oligos": [{"antisense_5to3": "A" * 16},
                                          {"antisense_5to3": "A" * 18}]}) is None
    assert C.screen_oligo_len({"oligos": []}) is None
    # and the name really is ignored: a 20-mer screen called "16mer" still measures 20
    assert C.screen_oligo_len({"screen": "junction-aso-offtarget-16mer.json",
                               "oligos": [{"antisense_5to3": "C" * 20}]}) == 20
