"""Compare worker outputs against coordinator expectations computed before output review."""
from pathlib import Path
import json, hashlib, sys
from fractions import Fraction

root = Path(sys.argv[1])
expected = json.loads(Path(sys.argv[2]).read_text())
result = json.loads((root / 'research/modalities/fus-ddit3-prefix-comparison.json').read_text())
rows = {row['source_variant']['reported_type']: row for row in result['variants']}
assert set(rows) == {row['type'] for row in expected['rows']}
assert result['total_native_fus_rg_count'] == expected['native_rg_count']
assert result['accession_version_alignment_established'] is False
assert result['all_native_prefixes_meet_zero_rg_rule'] is False
for item in expected['rows']:
    row = rows[item['type']]
    assert row['source_variant']['five_prime_exon'] == item['exon']
    assert row['arithmetic']['coding_nt_sum'] == item['coding_nt']
    assert row['arithmetic']['model_cumulative_coding_nt'] == item['coding_nt']
    assert row['arithmetic']['cdna_end_minus_utr5_nt'] == item['coding_nt']
    assert row['complete_native_residues'] == item['complete_native_residues']
    assert row['residual_native_nucleotides'] == item['residual_nt']
    assert row['rg_pairs_1based'] == [[p, p + 1] for p in item['rg_positions_1based']]
    assert row['rg_count'] == item['rg_count']
    assert row['native_terminal_residue'] == item['native_terminal_residue']
    assert row['native_prefix_meets_zero_rg_rule'] == item['native_prefix_zero_rg']
    assert row['retained_rg_fraction']['exact'] == str(Fraction(item['rg_count'], expected['native_rg_count']))
    assert row['junction']['residue'] is None
    assert row['junction']['whole_fusion_rg_count'] is None
    assert row['junction']['unresolved_partial_codon_position'] == item['complete_native_residues'] + 1
    assert row['frozen_census_consistency']['direct_count_agrees_with_first_rg'] is True
    assert row['frozen_census_consistency']['direct_count_agrees_with_frozen_ceiling_classification'] is True
    print(f"Type {item['type']}: {item['coding_nt']} nt; {item['complete_native_residues']} complete native residues; {item['residual_nt']} unresolved codon nucleotide; {item['rg_count']}/{expected['native_rg_count']} internal native RG pairs: PASS")
for item in result['input_provenance']:
    assert hashlib.sha256((root / item['path']).read_bytes()).hexdigest() == item['sha256']
print('All three variants, native RG positions, exact fractions, uncertainty flags and input hashes independently agree.')
