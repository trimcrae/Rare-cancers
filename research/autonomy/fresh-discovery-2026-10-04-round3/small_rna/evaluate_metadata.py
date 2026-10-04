"""Reproduce the source-eligibility gate. No expression values are analyzed."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json, re, hashlib, datetime

B = Path(__file__).resolve().parent

records = []
for chunk in (B / 'GSE69470-samples.txt').read_text(encoding='utf8').split('^SAMPLE = ')[1:]:
    lines = chunk.splitlines()
    records.append({
        'gsm': lines[0].strip(),
        'title': [x.split(' = ', 1)[1] for x in lines if x.startswith('!Sample_title = ')],
        'characteristics': [x.split(' = ', 1)[1] for x in lines if x.startswith('!Sample_characteristics_ch1 = ')]
    })
assert len(records) == 77
(B / 'nci-cell-identities.json').write_text(json.dumps(records, indent=2), encoding='utf8')

class Headers(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_header = False; self.rows = []; self.attrs = {}; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'th':
            self.in_header = True; self.attrs = dict(attrs); self.parts = []
    def handle_data(self, data):
        if self.in_header: self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == 'th' and self.in_header:
            label = ''.join(self.parts).strip()
            if re.search('[A-Za-z]', label):
                self.rows.append({'label': label, 'colspan': int(self.attrs.get('colspan', '1'))})
            self.in_header = False

parser = Headers()
parser.feed((B / 'smed-labels-text.html').read_text(encoding='utf8'))
histology_headers = [x for x in parser.rows if x['label'] != 'hsa-let-7a']
types = Counter(next(x.split(': ', 1)[1] for x in r['characteristics'] if x.startswith('cell type: ')) for r in records)
names = [re.sub(r'-rep\d*$', '', r['title'][0].replace(' [miRNA]', '')) for r in records]
ambiguous = [r for r in records if any(x in ';'.join(r['characteristics']).lower() for x in ['chondro', 'chonodro', 'human sarcoma', 'spindle cell', 'giant cell'])]
summary = {
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'analysis': 'metadata only; mature domain expression not examined',
    'nci_profiles': len(records),
    'nci_distinct_names_after_removing_explicit_rep_suffix': len(set(names)),
    'nci_explicit_replicate_titles': [r['title'][0] for r in records if '-rep' in r['title'][0]],
    'nci_histology_label_counts': dict(types),
    'nci_explicit_emc_labels': [r for r in records if re.search(r'extraskeletal|myxoid|EMC', json.dumps(r), re.I)],
    'nci_ambiguous_labels_requiring_authentication': ambiguous,
    'smed_histology_headers': histology_headers,
    'smed_header_sample_total': sum(x['colspan'] for x in histology_headers),
    'smed_explicit_emc_headers': [x for x in histology_headers if re.search(r'extraskeletal|myxoid|EMC', x['label'], re.I)],
    'caution': 'No explicit EMC label is not proof that all ambiguously labelled samples are non-EMC. Distinct names do not establish distinct patients.'
}
(B / 'metadata-evaluation.json').write_text(json.dumps(summary, indent=2), encoding='utf8')
print(json.dumps({k:summary[k] for k in ['nci_profiles','nci_distinct_names_after_removing_explicit_rep_suffix','smed_header_sample_total','smed_explicit_emc_headers']}, indent=2))

