"""Independently inspect original assay cells and pinned peptide/protein equality."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--xlrd-path', required=True)
args = parser.parse_args()
sys.path.insert(0, args.xlrd_path)
import xlrd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
read = lambda path: json.loads(path.read_text(encoding='utf-8'))
source = HERE/'originals/41588_2025_2268_MOESM10_ESM.xls'
book = xlrd.open_workbook(source)
peptides = set()
for name in ('fusion-breakpoint-neoantigens.json', 'junction-frameshift-peptides.json'):
    for junction in read(ROOT/'research/modalities'/name)['junctions']:
        peptides.update(junction['novel_peptides'])
saved = read(HERE/'exact-peptide-allele-matches.json')
findings = []
for sheetname in ('oncogene', 'onco_wt'):
    sheet = book.sheet_by_name(sheetname)
    header = [sheet.cell_value(0, j) for j in range(sheet.ncols)]
    peptide_column = header.index('AA')
    allele_columns = [j for j, label in enumerate(header) if re.fullmatch(r'[ABC]\*\d{2}:\d{2}', str(label))]
    assert len(allele_columns) == 50
    hits = [i for i in range(1, sheet.nrows) if sheet.cell_value(i, peptide_column) in peptides]
    assert len(hits) == 1
    i = hits[0]
    peptide = sheet.cell_value(i, peptide_column)
    assert peptide == 'QSSSYGQQN' and i+1 == 1231
    record = next(r for r in saved if r['sheet'] == sheetname)
    values = []
    for j in allele_columns:
        value = sheet.cell_value(i, j)
        assert isinstance(value, (float, int)) and value < 3.8
        expected = next(v for v in record['values'] if v['allele'] == header[j])
        assert value == expected['released_value']
        values.append(value)
    findings.append(dict(sheet=sheetname, rows=sheet.nrows-1, row=i+1,
                         peptide=peptide, alleles=50, minimum=min(values), maximum=max(values)))
s4 = xlrd.open_workbook(HERE/'originals/41588_2025_2268_MOESM6_ESM.xls').sheet_by_name('fusion_gene')
assert 'NR4A3' in s4.cell_value(33, 0) and 'NR4A3' in s4.cell_value(60, 0)
selected = [i for i in range(s4.nrows) if str(s4.cell_value(i, 6)).startswith('COSF')]
assert len(selected) == 31
for i in selected:
    assert not any(re.search(r'NR4A3|\bCHN\b|\bNOR[- ]?1\b|\bTEC\b', str(s4.cell_value(i,j)), re.I) for j in range(6,s4.ncols))
constructs = read(ROOT/'research/modalities/emc-fet-construct-designs.json')['constructs']
tested = []
for construct in constructs:
    sequence = construct.get('protein_sequence')
    assert sequence and 'QSSSYGQQN' not in sequence
    tested.append(construct['id'])
genes = read(ROOT/'research/modalities/emc-construct-inputs.json')['genes']
for gene in ('EWSR1', 'NR4A3'):
    assert 'QSSSYGQQN' not in genes[gene]['protein']
model = next(o for o in read(ROOT/'systems/graph/objects.json') if o['id'] == 'OBJ-MODEL-E7E3')
out = dict(passed=True, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
           unique_pinned_peptides=len(peptides), sheets=findings, selected_fusion_details=31,
           nr4a3_selected_details=0, reported_architecture_constructs_checked=tested,
           model_classification=model,
           scope='Independent original XLS cell reads and exact peptide/full pinned protein equality. All 100 saved cells checked, representing two released sheets rather than independent experiments. Missing read QC prevents biological-negative claims; no endogenous EMC presentation or clinical inference.')
(HERE/'coordinator-check-result.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({k:v for k,v in out.items() if k != 'model_classification'}))
