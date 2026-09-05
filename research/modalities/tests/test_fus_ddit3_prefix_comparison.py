"""Synthetic arithmetic failures and an independent scan of the committed inputs."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fus_ddit3_prefix_comparison as comparison


@pytest.fixture
def inputs():
    return [json.loads((comparison.ROOT / p).read_bytes()) for p in comparison.INPUTS]


def synthetic_model():
    # 2 nt UTR; exon 1 encodes AR plus 1 nt of the next codon.
    # Exon 2 completes that codon and adds one more complete codon.
    return {
        "utr5_len": 2,
        "exons": [
            {"transcript_exon_rank": 1, "cdna_start_0based": 0,
             "cdna_end_exclusive": 9, "exon_length_nt": 9,
             "coding_nt_in_exon": 7, "cumulative_coding_nt_through_exon": 7},
            {"transcript_exon_rank": 2, "cdna_start_0based": 9,
             "cdna_end_exclusive": 14, "exon_length_nt": 5,
             "coding_nt_in_exon": 5, "cumulative_coding_nt_through_exon": 12},
        ],
    }


def test_internal_pairs_include_adjacent_search_windows_but_exclude_boundary():
    # Native RGRG has pairs 1-2 and 3-4; cutting after R3 excludes pair 3-4.
    row = comparison.native_prefix("RGRG", 9)
    assert row["rg_pairs_1based"] == [[1, 2]]
    assert row["rg_count"] == 1
    assert row["total_native_fus_rg_count"] == 2
    assert row["retained_rg_fraction"]["exact"] == "1/2"
    assert row["junction"]["rg_crossing_complete_prefix_boundary_possible"]
    assert comparison.native_prefix("RGRG", 12)["rg_pairs_1based"] == [[1, 2], [3, 4]]


@pytest.mark.parametrize("remainder", [0, 1, 2])
def test_partial_codon_never_copies_the_native_continuation(remainder):
    # R is fully encoded; a partly encoded native G cannot be copied into the fusion.
    row = comparison.native_prefix("ARG", 6 + remainder)
    assert row["native_prefix_sequence"] == "AR"
    assert row["complete_native_residues"] == 2
    assert row["residual_native_nucleotides"] == remainder
    assert row["rg_count"] == 0
    assert row["native_prefix_meets_zero_rg_rule"]
    assert row["junction"]["unresolved_partial_codon_position"] == (3 if remainder else None)
    assert row["junction"]["residue"] is None
    assert row["junction"]["whole_fusion_rg_count"] is None


def test_empty_prefix_and_zero_denominator_are_not_fabricated_fractions():
    row = comparison.native_prefix("AAA", 1)
    assert row["native_prefix_sequence"] == ""
    assert row["native_terminal_residue"] is None
    assert row["retained_rg_fraction"]["exact"] is None


@pytest.mark.parametrize("nt", [-1, True, 1.5, 10])
def test_invalid_or_out_of_protein_endpoint_is_rejected(nt):
    with pytest.raises(comparison.InputError):
        comparison.native_prefix("ARG", nt)


def test_exon_sum_is_independent_of_list_order_and_handles_partial_codons():
    model = synthetic_model()
    model["exons"].reverse()
    first = comparison.exon_arithmetic(model, 1)
    row = comparison.native_prefix("ARGA", first["coding_nt_sum"])
    assert row["native_prefix_sequence"] == "AR"
    assert row["residual_native_nucleotides"] == 1
    whole = comparison.exon_arithmetic(model, 2)
    assert whole["coding_nt_sum"] == whole["model_cumulative_coding_nt"] == 12
    assert whole["cdna_end_minus_utr5_nt"] == 12
    assert comparison.native_prefix("ARGA", whole["coding_nt_sum"])["rg_pairs_1based"] == [[2, 3]]


@pytest.mark.parametrize("missing", [1, 2])
def test_missing_intermediate_or_retained_exon_is_rejected(missing):
    model = synthetic_model()
    model["exons"] = [e for e in model["exons"] if e["transcript_exon_rank"] != missing]
    with pytest.raises(comparison.InputError, match="Missing exon"):
        comparison.exon_arithmetic(model, 2)


def test_duplicate_rank_is_rejected():
    model = synthetic_model()
    model["exons"].append(deepcopy(model["exons"][0]))
    with pytest.raises(comparison.InputError, match="Duplicate exon"):
        comparison.exon_arithmetic(model, 2)


@pytest.mark.parametrize("field", ["coding_nt_in_exon", "cumulative_coding_nt_through_exon",
                                  "cdna_end_exclusive", "cdna_start_0based", "exon_length_nt"])
def test_inconsistent_exon_arithmetic_is_rejected(field):
    model = synthetic_model()
    model["exons"][1][field] += 1
    with pytest.raises(comparison.InputError):
        comparison.exon_arithmetic(model, 2)


def test_matching_stored_cumulative_cannot_hide_wrong_cdna_arithmetic():
    model = synthetic_model()
    model["exons"][1]["coding_nt_in_exon"] += 1
    model["exons"][1]["cumulative_coding_nt_through_exon"] += 1
    with pytest.raises(comparison.InputError, match="cDNA-minus-UTR"):
        comparison.exon_arithmetic(model, 2)


@pytest.mark.parametrize("failure", ["identity", "self_check", "aggregate", "length", "cache", "cds_length"])
def test_committed_model_checks_fail_closed(inputs, failure):
    _, designs, _, sequences = inputs
    if failure == "identity":
        designs["ensembl_vs_uniprot_sequences"]["FUS"]["identical"] = False
    elif failure == "self_check":
        designs["gene_models"]["FUS"]["self_checks"]["cds_translation_equals_protein"] = False
    elif failure == "aggregate":
        designs["gene_model_self_checks_all_pass"] = False
    elif failure == "length":
        designs["ensembl_vs_uniprot_sequences"]["FUS"]["uniprot_len"] += 1
    elif failure == "cache":
        sequences["FUS"] = sequences["FUS"][:-1]
    else:
        designs["gene_models"]["FUS"]["exons"][-1]["coding_nt_in_exon"] += 1
    with pytest.raises(comparison.InputError):
        comparison.compare(*inputs)


def test_source_variant_and_exon_ranks_drive_the_analysis(inputs):
    # A changed source must change the computed prefix, with no hardcoded type -> cut map.
    inputs[0]["junctions"] = [deepcopy(inputs[0]["junctions"][-1])]
    inputs[0]["junctions"][0].update(reported_type="synthetic", five_prime_exon=2)
    rows = comparison.compare(*inputs)["variants"]
    assert len(rows) == 1
    expected_nt = sum(e["coding_nt_in_exon"] for e in inputs[1]["gene_models"]["FUS"]["exons"]
                      if e["transcript_exon_rank"] <= 2)
    assert rows[0]["source_variant"] == inputs[0]["junctions"][0]
    assert rows[0]["complete_native_residues"] == expected_nt // 3


def test_frozen_ceiling_is_not_substituted_for_internal_count(inputs):
    protein = inputs[3]["FUS"]
    first_r = re.search("RG", protein).start() + 1
    frozen = inputs[2]["wild_type_annotation"]["FUS"]["rgg_free_ceiling"]
    assert first_r > frozen
    assert comparison.native_prefix(protein, first_r * 3)["native_prefix_meets_zero_rg_rule"]
    assert not comparison.native_prefix(protein, (first_r + 1) * 3)["native_prefix_meets_zero_rg_rule"]


def test_committed_rows_match_independent_regex_and_all_three_endpoints(inputs):
    evidence, designs, _, sequences = inputs
    result = comparison.compare(*inputs)
    assert [r["source_variant"] for r in result["variants"]] == evidence["junctions"]
    model, protein = designs["gene_models"]["FUS"], sequences["FUS"]
    total = len(re.findall("(?=RG)", protein))
    for row in result["variants"]:
        rank = row["source_variant"]["five_prime_exon"]
        exons = [e for e in model["exons"] if e["transcript_exon_rank"] <= rank]
        endpoint = next(e for e in exons if e["transcript_exon_rank"] == rank)
        nt = sum(e["coding_nt_in_exon"] for e in exons)
        assert nt == endpoint["cumulative_coding_nt_through_exon"]
        assert nt == endpoint["cdna_end_exclusive"] - model["utr5_len"]
        prefix = protein[:nt // 3]
        expected = [[m.start() + 1, m.start() + 2] for m in re.finditer("(?=RG)", prefix)]
        assert row["native_prefix_sequence"] == prefix
        assert row["rg_pairs_1based"] == expected
        assert row["rg_count"] == len(expected)
        assert row["total_native_fus_rg_count"] == total
        assert row["complete_native_residues"] * 3 + row["residual_native_nucleotides"] == nt
        assert row["native_prefix_meets_zero_rg_rule"] == (len(expected) == 0)


def test_provenance_hashes_match_input_bytes():
    result = comparison.build()
    assert [p["path"] for p in result["input_provenance"]] == list(comparison.INPUTS)
    for item in result["input_provenance"]:
        assert item["sha256"] == hashlib.sha256((comparison.ROOT / item["path"]).read_bytes()).hexdigest()
