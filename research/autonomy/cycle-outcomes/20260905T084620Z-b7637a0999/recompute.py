"""Independent native-prefix arithmetic; never imports the analysis producer."""
from pathlib import Path
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = args.root
source = json.loads((root / 'research/autonomy/evidence-fus-ddit3-2026-09-05/primary-junctions.json').read_text())
design = json.loads((root / 'research/modalities/emc-fet-construct-designs.json').read_text())
model = design['gene_models']['FUS']
seq = json.loads((root / 'research/modalities/fet-sequences-cache.json').read_text())['FUS']
all_rg = [index + 1 for index, (left, right) in enumerate(zip(seq, seq[1:])) if left == 'R' and right == 'G']
rows = []
for junction in source['junctions']:
    rank = junction['five_prime_exon']
    exon = next(row for row in model['exons'] if row['transcript_exon_rank'] == rank)
    nt = sum(row['coding_nt_in_exon'] for row in model['exons'] if row['transcript_exon_rank'] <= rank)
    assert nt == exon['cumulative_coding_nt_through_exon'] == exon['cdna_end_exclusive'] - model['utr5_len']
    residues, remaining = divmod(nt, 3)
    retained = [position for position in all_rg if position + 1 <= residues]
    rows.append({'type': junction['reported_type'], 'exon': rank, 'coding_nt': nt,
                 'complete_native_residues': residues, 'residual_nt': remaining,
                 'rg_positions_1based': retained, 'rg_count': len(retained),
                 'native_terminal_residue': seq[residues - 1], 'native_prefix_zero_rg': not retained})
result = {'method': 'Coordinator independently summed exon coding nucleotides and enumerated full native sequence adjacent RG positions, then filtered pairs wholly within complete codons. No producer imported.',
          'native_length': len(seq), 'native_rg_count': len(all_rg), 'native_first_rg': all_rg[0],
          'rows': rows, 'mapping_is_conditional': True, 'full_fusion_reconstructed': False}
args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(result, indent=2))
