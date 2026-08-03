"""The construct designer's arithmetic, exercised on a SYNTHETIC gene pair.

WHY SYNTHETIC. `emc_fet_construct_designs.py` needs Ensembl and UniProt, which the dev sandbox
403s at CONNECT (CLAUDE.md §6), so the real run happens in CI. That is not a reason to ship the
frame arithmetic untested: the whole point of this module is that a junction model built from a
stated Ensembl methodology WAS ONCE WRONG BY TWO EXONS in this repository, and the failure mode
was a silent index slide, not a crash. These tests build a tiny two-gene model whose right answer
can be read off by hand, so an index slide fails loudly here rather than in an artifact.

The load-bearing case is the third one: a 3' partner whose named exon carries 5'-UTR ahead of its
ATG, which is exactly NR4A3's situation (transcript exons 1-2 non-coding, exon 3 carries UTR +
the start codon). A CDS-level fusion model cannot even express that case.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_fet_construct_designs as cd  # noqa: E402


def _gene(symbol, utr5, cds, utr3, exon_nt_boundaries):
    """Build a gene model by hand. `exon_nt_boundaries` are cDNA cut points, ascending."""
    cdna = utr5 + cds + utr3
    exons, prev = [], 0
    for i, b in enumerate(list(exon_nt_boundaries) + [len(cdna)], start=1):
        exons.append({"transcript_exon_rank": i, "exon_id": f"{symbol}E{i}",
                      "exon_length_nt": b - prev, "cdna_start_0based": prev,
                      "cdna_end_exclusive": b, "coding_nt_in_exon": max(
                          0, min(b, len(utr5) + len(cds)) - max(prev, len(utr5))),
                      "is_coding": max(0, min(b, len(utr5) + len(cds))
                                       - max(prev, len(utr5))) > 0})
        prev = b
    return {"symbol": symbol, "transcript": f"T_{symbol}", "translation": f"P_{symbol}",
            "strand": 1, "utr5_len": len(utr5), "cdna": cdna, "cds": cds,
            "protein": cd.translate(cds), "exons": exons, "self_checks": {}}


# A: 5' partner. 6 nt 5'UTR, then 5 codons per "exon".
A_CDS = "ATG" + "GCT" * 9 + "TAA"          # M + 9 A + stop
# B: 3' partner. Its FIRST NAMED EXON carries 9 nt of 5'UTR before the ATG — the NR4A3 case.
# 40 W, comfortably past the 30-residue suffix guard in three_prime_residues_retained.
B_CDS = "ATG" + "TGG" * 40 + "TAA"


def _pair(a_boundaries, b_boundaries, b_utr5="GGGCCCAAA"):
    a = _gene("A", "AAAAAA", A_CDS, "TTT", a_boundaries)
    b = _gene("B", b_utr5, B_CDS, "TTT", b_boundaries)
    return {"A": a, "B": b}


def test_translate_and_gene_helper_agree():
    g = _gene("A", "AAAAAA", A_CDS, "TTT", [12])
    assert g["protein"] == "M" + "A" * 9
    assert g["cdna"][g["utr5_len"]:g["utr5_len"] + len(A_CDS)] == A_CDS


def test_exon_lookup_is_by_transcript_rank_and_raises_on_a_missing_exon():
    genes = _pair([12, 21], [15, 24])
    assert cd.cdna_end_of_exon(genes["A"], 1) == 12
    assert cd.cdna_start_of_exon(genes["B"], 2) == 15
    with pytest.raises(ValueError):
        cd.cdna_end_of_exon(genes["A"], 99)


def test_in_frame_fusion_recovers_both_termini_and_the_right_residue_count():
    # A cut at cDNA 15 -> 15-6 = 9 coding nt = 3 full residues (M,A,A).
    # B resumed at cDNA 9 = exactly its ATG, so no UTR read-through.
    genes = _pair([15], [9], b_utr5="GGGCCCAAA")
    entry = {"id": "t", "label": "A::B", "five_prime": "A", "five_prime_exon": 1,
             "three_prime": "B", "three_prime_exon": 2, "sources": []}
    out = cd.build_construct(entry, genes, {}, zf_start=None, lbd_start=1)
    assert out["self_checks"]["in_frame"] is True
    assert out["junction_in_residue_numbering"]["five_prime_residues_fully_encoded"] == 3
    assert out["protein_sequence"] == "MAA" + "M" + "W" * 40
    assert out["domains_retained_and_lost"]["n_extra_junction_encoded_residues"] == 0


def test_utr_read_through_is_counted_not_silently_dropped():
    """The NR4A3 case: the 3' partner's named exon starts BEFORE its ATG.

    A CDS-level model would join at the ATG and report the same protein. The transcript-level
    model translates the intervening UTR in the 5' partner's frame, so the extra residues appear
    in the output — which is the only way a reader can see that they exist.
    """
    genes = _pair([15], [0], b_utr5="GGGCCCAAA")   # B resumed at its exon 1 = cDNA 0
    entry = {"id": "t", "label": "A::B", "five_prime": "A", "five_prime_exon": 1,
             "three_prime": "B", "three_prime_exon": 1, "sources": []}
    out = cd.build_construct(entry, genes, {}, zf_start=None, lbd_start=1)
    assert out["junction_in_nucleotide_numbering"]["three_prime_utr_nt_read_through"] == 9
    assert out["self_checks"]["in_frame"] is True
    # 9 nt of UTR = 3 extra residues ahead of B's own methionine
    assert out["domains_retained_and_lost"]["n_extra_junction_encoded_residues"] == 3
    assert out["protein_sequence"] == "MAA" + "GPK" + "M" + "W" * 40


def test_an_out_of_frame_junction_fails_loudly_and_withholds_the_sequence():
    """One nucleotide of UTR read-through shifts the frame; the module must SAY so.

    The whole design brief is that a junction the arithmetic cannot support is reported as
    failing rather than quietly repaired until it looks right.
    """
    genes = _pair([15], [0], b_utr5="G")   # 1 nt of UTR -> frameshift into B
    entry = {"id": "t", "label": "A::B", "five_prime": "A", "five_prime_exon": 1,
             "three_prime": "B", "three_prime_exon": 1, "sources": []}
    out = cd.build_construct(entry, genes, {}, zf_start=None, lbd_start=1)
    assert out["self_checks"]["in_frame"] is False
    assert out["self_checks"]["three_prime_c_terminus_intact"] is False
    assert out["protein_sequence"] is None
    assert out["_protein_sequence_withheld_reason"]


def test_split_codon_across_the_junction_is_flagged():
    genes = _pair([14], [9])   # 14-6 = 8 coding nt -> 2 full residues, 2 nt hanging
    entry = {"id": "t", "label": "A::B", "five_prime": "A", "five_prime_exon": 1,
             "three_prime": "B", "three_prime_exon": 2, "sources": []}
    out = cd.build_construct(entry, genes, {}, zf_start=None, lbd_start=1)
    assert out["junction_in_residue_numbering"]["codon_split_across_the_junction"] is True
    assert out["junction_in_residue_numbering"]["five_prime_residues_fully_encoded"] == 2


def test_three_prime_retention_reports_truncation_rather_than_assuming_full_length():
    prot = "M" + "W" * 60
    assert cd.three_prime_residues_retained("XXXX" + prot, prot) == (1, 61)
    assert cd.three_prime_residues_retained("XXXX" + prot[10:], prot) == (11, 51)
    assert cd.three_prime_residues_retained("QQQQ", prot) == (None, 0)


def test_needleman_wunsch_identity_is_sane_at_both_ends():
    same = cd.needleman_wunsch_identity("ACDEFGHIKL", "ACDEFGHIKL")
    assert same["percent_identity"] == 100.0
    diff = cd.needleman_wunsch_identity("AAAAAAAAAA", "WWWWWWWWWW")
    assert diff["percent_identity"] == 0.0
    # a gap is tolerated rather than crashing the traceback
    gapped = cd.needleman_wunsch_identity("ACDEFGHIKL", "ACDEFGHIK")
    assert 0.0 < gapped["percent_identity"] <= 100.0


def test_every_registered_breakpoint_carries_at_least_one_quoted_source():
    """⛔ The rule the registry exists to enforce: an exon number nobody can quote is not written
    down. If a future edit adds a breakpoint from memory, this fails."""
    for e in cd.BREAKPOINTS:
        assert e["sources"], f"{e['id']} has no source"
        for s in e["sources"]:
            assert s.get("id") and s.get("quote"), f"{e['id']} has a source without a quote"


def test_unpinned_partners_are_named_rather_than_omitted():
    fusions = {u["fusion"] for u in cd.UNPINNED}
    assert "FUS::NR4A3" in fusions and "TCF12::NR4A3" in fusions
    for u in cd.UNPINNED:
        assert u["status"] and u["what_can_be_said"]


def test_build_construct_does_not_mutate_its_inputs_and_round_trips_through_json():
    """`--check` re-derives from the inputs cache and diffs the artifact, so it is only a
    reproduce mode if the derive half is deterministic THROUGH serialisation and leaves its
    input untouched. A derive step that quietly edited the cache would leave the committed
    cache disagreeing with the one the artifact was built from."""
    genes = _pair([15], [9])
    before = json.dumps(genes, sort_keys=True)
    entry = {"id": "t", "label": "A::B", "five_prime": "A", "five_prime_exon": 1,
             "three_prime": "B", "three_prime_exon": 2, "sources": []}
    out = cd.build_construct(entry, genes, {}, zf_start=None, lbd_start=1)
    assert json.dumps(genes, sort_keys=True) == before, "build_construct mutated its input"
    assert json.loads(json.dumps(out)) == out, "output does not survive a JSON round-trip"
    again = cd.build_construct(entry, genes, {}, zf_start=None, lbd_start=1)
    assert again == out, "build_construct is not deterministic"
