"""Tests for the pan-partner NR4A3 fusion-junction atlas.

The load-bearing one is `test_the_multi_partner_oligo_really_spans_every_seam_it_claims`: the
atlas's headline reading is that a single junction-spanning gapmer is fusion-exclusive at THREE
partners' seams at once, and the way that claim goes wrong is subtle — a 16-mer matching somewhere
inside another 4-kb chimera is finding the shared NR4A3 body, which every one of these fusions
carries, and which is not cross-junction coverage at all. So the test rebuilds the chimeras from the
committed cache itself rather than reading the artifact, and checks the match STRADDLES each seam.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")   # $0, offline, no Ensembl call in a unit test

import junction_aso as ja            # noqa: E402
import nr4a3_fusion_atlas as atlas   # noqa: E402

ARTIFACT = os.path.join(MOD, "nr4a3-fusion-junction-atlas.json")
CACHE = os.path.join(MOD, "emc-construct-inputs.json")


def _cache_model(symbol):
    """A transcript model built straight from the committed cache, bypassing the atlas entirely."""
    g = json.load(open(CACHE))["genes"][symbol]
    lens = [e["exon_length_nt"] for e in g["exons"]]
    ends, c = [], 0
    for L in lens:
        c += L
        ends.append(c)
    return g["cdna"].upper(), ends


def _chimera(donor, d_exon, a_exon=3):
    dc, de = _cache_model(donor)
    ac, ae = _cache_model("NR4A3")
    left = dc[:de[d_exon - 1]]
    right = ac[ae[a_exon - 2]:]
    return left, right, left + right


def _rc(s):
    return s.translate(str.maketrans("ACGT", "TGCA"))[::-1]


@pytest.fixture(scope="module")
def art():
    if not os.path.exists(ARTIFACT):
        pytest.skip("atlas artifact not built in this checkout")
    return json.load(open(ARTIFACT))


def test_the_multi_partner_oligo_really_spans_every_seam_it_claims(art):
    """⭐ THE HEADLINE, CHECKED AGAINST THE CACHE RATHER THAN AGAINST THE ARTIFACT THAT CLAIMS IT.

    A match inside another chimera proves nothing on its own — the shared NR4A3 acceptor body would
    produce one for free. The claim is only that the oligo is JUNCTION-SPANNING at each seam, so
    that is what is asserted here, plus absence from every wild-type parent (without which
    "fusion-exclusive" is not a word that may be used).
    """
    mp = art["isoform_coverage"]["multi_partner_exact"]
    assert mp, "the atlas reports no multi-partner design — that is the headline, so its loss is a bug"
    for aso, rec in mp.items():
        target = _rc(aso)
        labels = [rec["designed_for"]] + rec["also_covers"]
        for label in labels:
            donor, rest = label.split("_e", 1)
            d_exon = int(rest.split("__")[0])
            a_exon = int(label.rsplit("_e", 1)[1])
            left, _right, fusion = _chimera(donor, d_exon, a_exon)
            seam = len(left)
            spans = [s for s in range(len(fusion) - len(target) + 1)
                     if fusion[s:s + len(target)] == target and s < seam < s + len(target)]
            assert spans, (f"{aso} claims coverage of {label} but no exact match straddles that "
                           f"junction's seam — this is the body-match failure mode")
        # fusion-EXCLUSIVE: present in no wild-type parent transcript
        for sym in json.load(open(CACHE))["genes"]:
            cdna, _ = _cache_model(sym)
            assert target not in cdna, f"{aso} is a perfect complement of wild-type {sym}"


def test_the_headline_oligo_is_gap_centred_and_splits_the_seam_evenly(art):
    """The best multi-partner design must satisfy the paper's OWN design rule, not a looser one.

    §3b.1's gap-centred rule requires >=2 junction-unique bases inside the catalytic gap on each
    side. A multi-partner oligo that only reached three seams by pushing the junction to the edge of
    the gap would be buying coverage with the very discrimination the gapmer exists for.
    """
    mp = art["isoform_coverage"]["multi_partner_exact"]
    three = {k: v for k, v in mp.items() if len(v["partners_covered"]) >= 3}
    assert three, "no design covers three partners"
    best = max(three.values(), key=lambda v: v["gap_specificity_margin"])
    assert best["gap_specificity_margin"] >= 2, (
        "the best three-partner design is not gap-centred — coverage was bought with discrimination")
    for split in best["seam_split_per_junction"].values():
        assert split["donor_bases"] + split["acceptor_bases"] == ja.OLIGO_LEN


def test_coverage_is_explained_by_an_identical_donor_run_not_left_to_be_inferred(art):
    """§4: produce the evidence that proves the mechanism. Each multi-partner row must name it."""
    for aso, rec in art["isoform_coverage"]["multi_partner_exact"].items():
        run = rec["shared_donor_run"]
        assert run, f"{aso} covers several partners with no shared donor run recorded"
        longest = max(s["donor_bases"] for s in rec["seam_split_per_junction"].values())
        assert len(run) >= longest, (
            f"{aso}: the shared donor run ({len(run)} nt) is shorter than the donor-side "
            f"contribution it has to explain ({longest} nt) — the coverage claim is impossible")


def test_the_ewsr1_rows_reproduce_the_corrected_2026_08_06_result(art):
    """The generalised builder must not move the answer the retraction was resolved against.

    Under the corrected mRNA-level model the EMITTABLE EWSR1 junctions inside the declared window
    are e7/e9/e10/e12/e13 and e11 is refused as a frame-register mismatch. That set is the
    established result; a donor-generic rewrite reproducing it is the check that the generalisation
    changed reach and not arithmetic.
    """
    inside = {r["donor_exon_end"] for r in art["graded_pairs"]
              if r["donor_symbol"] == "EWSR1" and r.get("grade") == ja.EMITTABLE
              and r.get("within_declared_donor_window") is True}
    assert inside == {7, 9, 10, 12, 13}
    e11 = [r for r in art["graded_pairs"] if r["junction_label"] == "EWSR1_e11__NR4A3_e3"]
    assert e11 and e11[0]["grade"] == "OUT_OF_FRAME"


def test_a_partner_with_no_transcript_model_is_named_not_dropped(art):
    """TFG is a reported EMC partner with no model here. An absent reading must say its own name."""
    assert "TFG" in art["partners_not_scoreable"]
    assert "TFG" not in art["partners_scored"]


def test_the_weaker_provenance_gate_is_disclosed_per_gene(art):
    """The exon audit grades EWSR1/NR4A3 only. Partners resting on the weaker gate must say so."""
    gates = art["provenance_gate_per_gene"]
    assert gates["EWSR1"] == "graded_exon_audit"
    assert gates["NR4A3"] == "graded_exon_audit"
    for sym in ("TAF15", "TCF12", "FUS"):
        assert gates[sym] == "construct_inputs_self_checks_only", (
            f"{sym} claims a provenance gate that cannot run for it")


def test_a_partner_without_a_declared_window_gets_null_not_false(art):
    """A curation gap must never render as a negative finding."""
    for r in art["graded_pairs"]:
        if r["donor_symbol"] == "EWSR1":
            assert r["within_declared_donor_window"] in (True, False)
        else:
            assert r["within_declared_donor_window"] is None


def test_the_parent_screen_actually_widens_and_names_what_it_hits():
    """`design(parents=...)` must screen every supplied parent and report WHICH one an oligo hit.

    The FET donors are paralogues, so a design against one partner's seam can be a perfect
    complement of another partner's wild-type transcript. A widened screen that silently returned
    the same answer as the two-parent one would be decoration.
    """
    left, right, fusion = _chimera("TAF15", 11)
    two = ja.design(left, right, fusion, parents={"TAF15": _cache_model("TAF15")[0],
                                                  "NR4A3": _cache_model("NR4A3")[0]})
    allp = ja.design(left, right, fusion,
                     parents={s: _cache_model(s)[0] for s in ("EWSR1", "TAF15", "TCF12", "FUS",
                                                              "NR4A3")})
    assert {o["antisense_5to3"] for o in allp if o["fusion_specific"]} <= \
           {o["antisense_5to3"] for o in two if o["fusion_specific"]}, \
        "the wider parent set must be strictly stricter — it may only ever remove candidates"
    assert allp[0]["parents_screened"] == ["EWSR1", "FUS", "NR4A3", "TAF15", "TCF12"]
    for o in allp:
        assert o["fusion_specific"] == (not o["exact_parent_hits"])


def test_every_emittable_junction_yields_at_least_one_fusion_specific_design(art):
    """Designability is reported as universal across the atlas; if it stops being so, say so."""
    assert art["n_junctions_with_a_fusion_specific_design"] == art["n_emittable_junctions"]
    for p in art["panels"]:
        assert p["n_fusion_specific"] >= 1


def test_the_artifact_refuses_to_claim_clinical_recurrence(art):
    """The atlas grades frame-compatibility. It must say, in the file, that this is not the same."""
    blob = " ".join(art["_what_this_is_not"]).lower()
    assert "frame-compatible" in blob
    assert "not a claim about which junctions patients carry" in blob
