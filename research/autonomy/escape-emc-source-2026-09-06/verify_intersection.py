"""Re-extract exact released XLS cells and intersect pinned EMC peptides; no predictors.

Run with Python and xlrd==2.0.2 installed, optionally via --xlrd-path.
Writes deterministic JSON evidence adjacent to this script; --check checks instead.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument('--xlrd-path')
ap.add_argument('--check', action='store_true')
args = ap.parse_args()
if args.xlrd_path:
    sys.path.insert(0, args.xlrd_path)
import xlrd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
if args.check:
    manifest = json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
    for entry in manifest['files']:
        p = HERE/entry['path']
        assert p.stat().st_size == entry['bytes'], entry['path']
        assert sha(p) == entry['sha256'], entry['path']
def output(name, data):
    text = json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + '\n'
    p = HERE / name
    if args.check:
        assert p.read_text(encoding='utf-8') == text, name
    else:
        p.write_text(text, encoding='utf-8')
def rows(s):
    return [{'excel_row': i+1, 'values': s.row_values(i)} for i in range(s.nrows)]
def column(n):
    r = ''
    while n:
        n, v = divmod(n-1, 26)
        r = chr(65+v)+r
    return r

files = ['fusion-breakpoint-neoantigens.json', 'junction-frameshift-peptides.json']
peptides = {}
inputs = []
for filename in files:
    p = ROOT / 'research/modalities' / filename
    d = json.loads(p.read_text(encoding='utf-8'))
    inputs.append({'path': str(p.relative_to(ROOT)).replace('\\','/'), 'sha256': sha(p)})
    for j in d['junctions']:
        for peptide in j['novel_peptides']:
            peptides.setdefault(peptide, []).append({
                'file': filename, 'junction_label': j['junction_label'],
                'grade': j['grade'], 'junction_context': j.get('junction_context'),
                'nmd_predicted': j.get('nmd', {}).get('nmd_predicted')})
output('pinned-peptides.json', {'inputs': inputs, 'peptides': peptides})

construct_path = ROOT/'research/modalities/emc-fet-construct-designs.json'
gene_path = ROOT/'research/modalities/emc-construct-inputs.json'
integrity_path = ROOT/'systems/graph/integrity.json'
object_path = ROOT/'systems/graph/objects.json'
constructs = json.loads(construct_path.read_text(encoding='utf-8'))
genes = json.loads(gene_path.read_text(encoding='utf-8'))['genes']
hit = 'QSSSYGQQN'
provenance = {'peptide': hit, 'inputs': [
    {'path': str(p.relative_to(ROOT)).replace('\\','/'), 'sha256': sha(p)}
    for p in [construct_path, gene_path, integrity_path, object_path]],
    'model_object': next(o for o in json.loads(object_path.read_text(encoding='utf-8')) if o['id']=='OBJ-MODEL-E7E3'),
    'integrity_conflict': next(c for c in json.loads(integrity_path.read_text(encoding='utf-8'))['open_conflicts'] if c['id']=='OC-2'),
    'reported_architecture_construct_checks': [], 'wild_type_checks': []}
for c in constructs['constructs']:
    seq = c.get('protein_sequence')
    provenance['reported_architecture_construct_checks'].append({
        'id': c['id'], 'breakpoint_sources': c['breakpoint_sources'],
        'junction': c['junction_in_exon_numbering'],
        'seam': c['junction_in_residue_numbering'],
        'protein_sequence_available': bool(seq),
        'exact_peptide_present': hit in seq if seq else None,
        'scope': 'Computed protein from source-supported exon architecture, not measured tumor protein'})
for gene in ['EWSR1', 'NR4A3']:
    seq = genes[gene]['protein']
    provenance['wild_type_checks'].append({'gene': gene, 'transcript': genes[gene]['transcript'],
        'protein_length': len(seq), 'exact_peptide_present': hit in seq,
        'scope': 'Pinned canonical protein only; not a proteome-wide or isoform-wide absence claim'})
output('biological-provenance-check.json', provenance)

s4file = HERE/'originals/41588_2025_2268_MOESM6_ESM.xls'
sourcefile = HERE/'originals/41588_2025_2268_MOESM10_ESM.xls'
assert s4file.read_bytes()[:8] == bytes.fromhex('d0cf11e0a1b11ae1')
assert sourcefile.read_bytes()[:8] == bytes.fromhex('d0cf11e0a1b11ae1')
s4 = xlrd.open_workbook(s4file)
output('supplementary-table4-cells.json', {s.name: rows(s) for s in s4.sheets()})
alias = re.compile(r'NR4A3|\bCHN\b|\bNOR[- ]?1\b|\bTEC\b', re.I)
partner = re.compile(r'EWSR1|\bEWS\b|TAF15|TAF2N|TAFII68|RBP56|\bFUS\b|\bTLS\b|TCF12|\bHTF4\b|\bTFG\b|\bHSPA8\b', re.I)
fg = s4.sheet_by_name('fusion_gene')
inventory = [{'excel_row': i+1, 'range': f'A{i+1}:D{i+1}', 'values': fg.row_values(i)[:4]}
             for i in range(2, fg.nrows) if alias.search(str(fg.row_values(i)[:4])) or partner.search(str(fg.row_values(i)[:4]))]
details = [{'excel_row': i+1, 'range': f'G{i+1}:V{i+1}', 'values': fg.row_values(i)[6:]}
           for i in range(4,fg.nrows) if str(fg.cell_value(i,6)).startswith('COSF')]
output('library-block-evidence.json', {'inventory_header_range': 'A2:D2',
    'detail_header_range': 'G4:V4', 'inventory_alias_or_partner_rows': inventory,
    'selected_detail_rows': details,
    'nr4a3_selected_detail_rows': [r for r in details if alias.search(str(r['values']))],
    'partner_selected_detail_rows': [r for r in details if partner.search(str(r['values']))]})

source = xlrd.open_workbook(sourcefile)
matches = []
candidate_rows = {}
summary = {}
for sn in ['oncogene', 'onco_wt']:
    s = source.sheet_by_name(sn)
    header = s.row_values(0)
    ai = header.index('AA')
    ac = [c for c, h in enumerate(header) if re.fullmatch(r'[ABC]\*\d+:\d+', str(h))]
    candidate_rows[sn] = {'headers': header, 'rows': []}
    for i in range(1, s.nrows):
        row = s.row_values(i)
        if alias.search(str(row)) or partner.search(str(row)):
            candidate_rows[sn]['rows'].append({'excel_row': i+1, 'values': row})
        if row[ai] in peptides:
            values = []
            for c in ac:
                v = row[c]
                values.append({'cell': column(c+1)+str(i+1), 'allele': header[c], 'released_value': v,
                    'above_paper_combinatorial_cutoff': v > 3.8 if isinstance(v, (int,float)) else None,
                    'per_pair_read_qc_available': False})
            matches.append({'sheet': sn, 'excel_row': i+1, 'name2': row[0],
                'peptide_cell': column(ai+1)+str(i+1), 'peptide': row[ai],
                'repo_matches': peptides[row[ai]], 'values': values})
    summary[sn] = {'data_rows': s.nrows-1, 'columns': s.ncols, 'alleles': [header[c] for c in ac],
        'nr4a3_label_rows': [i+1 for i in range(1,s.nrows) if alias.search(str(s.row_values(i)))],
        'peptide_lengths': dict(sorted(Counter(len(str(s.cell_value(i,ai))) for i in range(1,s.nrows)).items())),
        'exact_match_rows': len([m for m in matches if m['sheet']==sn]),
        'blank_allele_cells': sum(s.cell_value(i,c)=='' for i in range(1,s.nrows) for c in ac)}
output('source-partner-rows.json', candidate_rows)
output('exact-peptide-allele-matches.json', matches)
summary['selected_detail_count'] = len(details)
summary['pinned_unique_peptide_count'] = len(peptides)
summary['pinned_9mer_count'] = sum(len(p)==9 for p in peptides)
summary['exact_unique_peptides'] = sorted(set(m['peptide'] for m in matches))
summary['extraction'] = {'library': 'xlrd', 'version': xlrd.__version__,
    'format': 'Legacy binary Excel (OLE/BIFF); row_values cached cell values; 1-based Excel rows and cells; no formula recalculation or XLS rewriting'}
output('intersection-summary.json', summary)
print(json.dumps(summary, indent=2))
print('Exact matches:', [(m['sheet'], m['excel_row'], m['peptide'],
    min(v['released_value'] for v in m['values']),max(v['released_value'] for v in m['values']),
    sum(v['above_paper_combinatorial_cutoff'] is True for v in m['values'])) for m in matches])
print('Verification complete' if args.check else 'Extraction complete')
