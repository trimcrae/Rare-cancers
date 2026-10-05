"""Source/QC and annotation-only audit; never reads numerical peak outcomes."""
import collections
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile
import pandas as pd
from lxml import etree

ROOT = Path(__file__).resolve().parent
MATRIX = Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round8/neurosecretory/raw-cache/GSE28866_normalized.txt.gz')
EXPECTED = '11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n')


assert sha(MATRIX) == EXPECTED
with gzip.open(MATRIX, 'rt') as handle:
    reader = csv.reader(handle, delimiter='\t')
    header = next(reader)
    annotations = [row[:7] for row in reader]  # Sample columns are never accessed.
classes = collections.Counter(row[2] for row in annotations)
coding = [row for row in annotations if row[2] == 'coding' and row[4] and not re.search(r'[,;| ]', row[4])]
by_gene = collections.defaultdict(list)
for row in coding:
    match = re.fullmatch(r'(chr[^:]+):(\d+)-(\d+)_([+-])', row[1])
    if match:
        chromosome, start, end, strand = match.groups()
        by_gene[row[4]].append({'peak': row[0], 'coordinates': row[1], 'chromosome': chromosome,
                              'start': int(start), 'end': int(end), 'strand': strand,
                              'source_gene_id': row[3]})
multiple = {gene: rows for gene, rows in by_gene.items() if len(rows) > 1}
same_transcript_close = []
for gene, rows in multiple.items():
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            if (left['chromosome'], left['strand'], left['source_gene_id']) == (right['chromosome'], right['strand'], right['source_gene_id']):
                gap = max(left['start'], right['start']) - min(left['end'], right['end'])
                if 0 <= gap <= 300:
                    same_transcript_close.append({'gene': gene, 'left': left, 'right': right, 'gap_bp': gap})
write('ANNOTATION-ONLY-AUDIT.json', {
    'scope': 'All seven annotation fields; no sample expression columns or processing phenotype outcomes inspected.',
    'matrix_path': str(MATRIX), 'matrix_bytes': MATRIX.stat().st_size, 'matrix_sha256': EXPECTED,
    'header_annotations': header[:7], 'library_columns': header[7:],
    'rows': len(annotations), 'classes': dict(classes),
    'literal_single_symbol_coding_rows': len(coding), 'coordinate_parsed_genes': len(by_gene),
    'multiple_peak_genes': len(multiple), 'same_transcript_separated_pairs_gap_0_to_300bp': len(same_transcript_close),
    'diagnostic_examples_first_five_source_order': same_transcript_close[:5],
    'interpretation': 'Peak intervals and transcript labels contain neither per-peak cleavage-site positions, terminal-exon status, PAS identity nor internal-priming flags. Close distinct peaks with one transcript label demonstrate why multiple peaks are not automatically multiple polyadenylation sites. The 300bp illustration is structural, not a locus-selection threshold or biological test.'})

archive = ROOT / 'raw' / 'Brunner2012-supplements.zip'
with zipfile.ZipFile(archive) as zip_handle:
    member = next(name for name in zip_handle.namelist() if name.lower().endswith('.xls'))
    content = zip_handle.read(member)
    sheet = pd.read_excel(io.BytesIO(content), sheet_name='Table_S1', header=None)
columns = [str(value) for value in sheet.iloc[2].tolist()]
diagnosis = None
qc = []
for values in sheet.iloc[3:].itertuples(index=False, name=None):
    if pd.notna(values[0]):
        diagnosis = str(values[0])
    if pd.notna(values[1]) and str(values[1]).startswith('STT'):
        qc.append({'diagnosis': diagnosis, 'sample': str(values[1]), **{columns[i]: int(values[i]) for i in range(2, 7)}})
assert len(qc) == 93
emc = [row for row in qc if '(EMC)' in row['diagnosis']]
assert {row['sample'] for row in emc} == {'STT5525', 'STT5526', 'STT5527', 'STT5592'}
write('ALL93-LIBRARY-QC.json', {'source_archive_sha256': sha(archive), 'member': member,
                            'member_bytes': len(content), 'member_sha256': hashlib.sha256(content).hexdigest(),
                            'sheet': 'Table_S1', 'source_columns': columns, 'all93_libraries': qc,
                            'all4_emc': emc, 'RIN': 'Not present in this Table_S1; no individual RIN inferred.',
                            'biological_replication': 'Four author-labelled EMC source specimens. ESS_STT5520 rep1/rep2 and LMS_STT516 rep1/rep2 are two technical pairs, not four donors. Cross-study EMC donor overlap and NR4A3 authentication not established by this table.'})

observations = []
selectors = {
    'Brunner2012-PMC4053743.xml': ['captures only', 'clustering', 'at least 25', '200–300', '100–200', 'square root', 'divided by', 'five kilobases', '5 kb', 'coding exon', 'Data availability', 'formalin', 'normal tissue'],
    'Beck2010-PMC2808244.xml': ['25-oligo-dT', 'fragmented to', 'P5 end', 'first 25 bp', 'polyadenylation', 'internal prim'],
}
for filename, terms in selectors.items():
    path = ROOT / 'raw' / filename
    root = etree.parse(str(path))
    for paragraph in root.xpath('//p'):
        text = ' '.join(paragraph.itertext())
        if any(term.lower() in text.lower() for term in terms):
            observations.append({'source': filename, 'source_sha256': sha(path), 'xml_id': paragraph.get('id'), 'text': text})
write('ASSAY-ELIGIBILITY-EXCERPTS.json', observations)
print('annotation rows', len(annotations), 'multiple genes', len(multiple), 'close same transcript pairs', len(same_transcript_close))
print('QC', len(qc), 'EMC', len(emc))
