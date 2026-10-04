#!/usr/bin/env python3
"""Independent clinical-roster arithmetic; read frozen originals in place.

No retrieval, copied originals, tissue analysis, ratios or disease inference.
Missing cache is a reproduction limitation, not a reason to exclude a cohort.
"""
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import argparse
import datetime
import hashlib
import json
import re
import subprocess


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th'):
            self.cell = []

    def handle_data(self, text):
        if self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            if self.row is not None:
                self.row.append(' '.join(' '.join(self.cell).split()))
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    return re.sub(r'\s+', '', text).lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-04-round6/fapi_broader'))
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('SOURCE-VERIFICATION.json'))
    args = parser.parse_args()
    root = args.source
    checks, bindings = [], []

    def read(name):
        return json.loads((root / name).read_text())

    def bind(name, disposition):
        file = root / name
        bindings.append({'path': name, 'bytes': file.stat().st_size,
                         'sha256': sha(file), 'disposition': disposition,
                         'actual_read_location': str(file)})

    def check(name, truth, details):
        checks.append({'check': name, 'passed': bool(truth), 'details': details})

    def table(name):
        bind('raw/' + name, 'owner-cache-only; read in place, not copied')
        p = TableParser()
        p.feed((root / 'raw' / name).read_text())
        return p.rows

    for manifest in ('MANIFEST.json', 'ADDITIVE-MANIFEST.json'):
        bind(manifest, 'committed owner freeze')
        data = read(manifest)
        mismatches = [r['path'] for r in data['files']
                      if sha(root / r['path']) != r['sha256'] or (root / r['path']).stat().st_size != r['bytes']]
        check(manifest + ' binding', not mismatches, {'entries': len(data['files']), 'mismatches': mismatches})

    names = ('PLAN.json', 'COVERAGE.json', 'DECISION.json', 'HANDOFF.txt',
             'PORTABILITY.json', 'clinical-eligibility-excerpts.json',
             'hirmas2023-roster.json', 'hirmas2024-roster.json',
             'liver2026-rosters.json', 'three-timepoint-roster.json',
             'interobserver-teaching-eligibility.json',
             'HIRMAS-HISTOLOGY-COMPLETENESS-AMENDMENT.json')
    for name in names:
        bind(name, 'committed owner evidence')

    # Original HTML tables independently recovered with the stdlib parser.
    h23 = read('hirmas2023-roster.json')
    rows = table('hirmas2023_popup1.html')
    start = next(i for i, r in enumerate(rows) if r[0] == 'Tumor entity') + 1
    end = next(i for i, r in enumerate(rows[start:], start) if r[0].startswith('Tumor staging'))
    macro = [[r[0].replace(' *', '*'), r[1]] for r in rows[start:end]]
    check('Hirmas2023 entire macro roster', macro == h23['macro_entity_rows'],
          {'original_rows': macro, 'patients': sum(int(r[1].split()[0]) for r in macro)})

    # Only clinical Supplemental Table1 PDF pages13–14 are extracted.
    pdf = root / 'raw/hirmas2023_supp.pdf'
    bind('raw/hirmas2023_supp.pdf', 'owner-cache-only; selected clinical pages only')
    text = subprocess.run(['pdftotext', '-f', '13', '-l', '14', '-layout', str(pdf), '-'],
                          capture_output=True, text=True, check=True).stdout
    parsed = []
    for line in text.splitlines():
        match = re.match(r'^\s*(.+?)\s{2,}(\d+)\s*\(\d+\)', line)
        if match and not re.match(r'^[\d(]', match[1]):
            parsed.append((match[1], int(match[2])))
    headings = ['Sarcomas', 'Pancreas', 'Brain', 'Lung', 'Pleura',
                'Cholangiocellular carcinoma (CCC)', 'Colorectal', 'Prostate',
                'Head and Neck', 'Bladder', 'Lymphoma', 'Myeloma', 'Ovarian',
                'Breast', 'Duodenum', 'Other']
    headings_set = set(headings)
    group, sarcoma, other = None, [], []
    for label, number in parsed:
        if label in headings_set and not (label == 'Other' and group == 'Ovarian'):
            group = label
        elif group == 'Sarcomas':
            sarcoma.append({'source_label': label, 'patients': number})
        else:
            export_group = 'Cholangiocellular carcinoma' if group == 'Cholangiocellular carcinoma (CCC)' else group
            other.append({'group': export_group, 'source_label': label, 'patients': number})
    amendment = read('HIRMAS-HISTOLOGY-COMPLETENESS-AMENDMENT.json')
    check('Hirmas2023 all sarcoma leaves', sarcoma == h23['sarcoma_subtype_rows'],
          {'rows': len(sarcoma), 'patients': sum(x['patients'] for x in sarcoma)})
    check('Hirmas2023 all remaining histology leaves', other == amendment['non_sarcoma_leaf_rows'],
          {'rows': len(other), 'patients': sum(x['patients'] for x in other),
           'generic_remaining_patients': sum(x['patients'] for x in amendment['additional_unresolved_labels'])})
    footnote = text[text.index('Each entity (N=1):'):].replace('\n', ' ')
    check('Hirmas2023 eleven Other+ source labels',
          all(compact(label) in compact(footnote) for label in h23['other_footnote_labels']),
          {'labels': h23['other_footnote_labels'], 'n_each': 1})

    h24 = read('hirmas2024-roster.json')
    rows = table('hirmas2024_popup1.html')
    start = next(i for i, r in enumerate(rows) if r[0] == 'Tumor entities') + 1
    end = next(i for i, r in enumerate(rows[start:], start) if r[0].startswith('Regional detection'))
    entities = rows[start:end]
    check('Hirmas2024 all eight entities', entities == h24['entities'],
          {'patients': sum(int(r[1].split()[0]) for r in entities), 'rows': entities})
    clinical = read('clinical-eligibility-excerpts.json')
    for name in ('hirmas2024_supp.pdf', 'hirmas2023_supp.txt',
                 'three_timepoint_jnm.html', 'interobserver2023_jnm.html'):
        bind('raw/' + name, 'owner-cache-only; clinical pages/snippets inspected only, excluded tissue sections not read')
    exclusion = clinical['hirmas2024_jnm.html'][0]['text']
    check('Hirmas2024 explicit sarcoma exclusion in selected clinical excerpt',
          'Patients with sarcoma, pancreatic cancer, and pleural mesothelioma have been excluded from this analysis' in exclusion,
          {'scope': 'Selected source-bound clinical excerpt; no full article/tissue inspection'})

    tp = read('three-timepoint-roster.json')
    rows = table('three_timepoint_table1.html')
    check('ThreeTimePoint entire14-type roster', rows[1:] == tp['rows'][1:],
          {'rows': rows[1:], 'patients': sum(int(r[1]) for r in rows[1:]),
           'generic_sarcoma_donors': int(next(r[1] for r in rows if r[0] == 'Sarcoma')),
           'conditions': '10min/1h/3h after one injection; dependent repeated acquisition, not additional donors'})

    liver = read('liver2026-rosters.json')
    rows = table('liver2026_table1.html')
    start = next(i for i, r in enumerate(rows) if r[0] == 'Gastrointestinal stromal tumors')
    types = rows[start:]
    numbers = [tuple(map(int, re.fullmatch(r'(\d+)\s*\((\d+)\)', r[1]).groups())) for r in types]
    check('Liver2026 all19 categories', types == liver['main_entity_rows'],
          {'patients': sum(n[0] for n in numbers), 'lesions': sum(n[1] for n in numbers), 'source_rows': types})

    docx = root / 'raw/liver2026_supp.docx'
    bind('raw/liver2026_supp.docx', 'owner-cache-only; original clinical roster')
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(docx) as archive:
        xml = ET.fromstring(archive.read('word/document.xml'))
    all_originals, discrepancies = [], []
    for table_index, t in enumerate(xml.findall('.//w:tbl', ns)):
        extracted = [[' '.join(' '.join((n.text or '') for n in c.findall('.//w:t', ns)).split())
                      for c in r.findall('w:tc', ns)] for r in t.findall('w:tr', ns)]
        for cells in extracted[2:]:
            index, age = int(compact(cells[0])), int(compact(cells[2]))
            numbers = [int(compact(v)) for v in cells[4:]]
            original = {'source_table': 'S' + str(table_index + 1), 'source_id': index,
                        'original_cells': cells, 'pair_lesion_total': sum(numbers[:2]),
                        'tracer_totals_equal': sum(numbers[:2]) == sum(numbers[2:])}
            all_originals.append(original)
            match = next(r for r in liver['individual_rows']
                         if r['source_table'] == original['source_table'] and r['source_id'] == index)
            comparisons = [age == match['age_years'], compact(cells[1]) == compact(match['gender']),
                           compact(cells[3]) == compact(match['source_histology']),
                           numbers == [match[k] for k in ('FDG_positive_lesions', 'FDG_negative_lesions',
                                                        'FAPI_positive_lesions', 'FAPI_negative_lesions')]]
            if not all(comparisons):
                discrepancies.append(original)
    check('Liver2026 all76 original donor rows and both tracer conditions',
          not discrepancies and len(all_originals) == 76 and all(x['tracer_totals_equal'] for x in all_originals),
          {'source_rows': all_originals, 'mismatches': discrepancies,
           'tables': [{'table': name, 'donors': sum(x['source_table'] == name for x in all_originals),
                       'lesions': sum(x['pair_lesion_total'] for x in all_originals if x['source_table'] == name)}
                      for name in ('S1', 'S2')],
           'normalization': 'Only whitespace/case for comparison, including split source glyph words; original cells retained above.'})
    sarcoma_types = [r for r in types if 'sarcoma' in r[0].lower() or r[0] in
                     ('Gastrointestinal stromal tumors', 'Chordoma', 'Solitary fibroma')]
    sums = [tuple(map(int, re.fullmatch(r'(\d+)\s*\((\d+)\)', r[1]).groups())) for r in sarcoma_types]
    check('Liver2026 classification inconsistency preserved',
          sum(x[0] for x in sums) == 10 and sum(x[1] for x in sums) == 32,
          {'explicit_sarcoma_plus_GIST_chordoma_SFT_donors': 10, 'lesions': 32,
           'source_assertion': '11sarcomas/37lesions',
           'unassigned_difference': 'G2NET row supplies1/5 numerically; this does not justify reclassification.'})

    teaching = read('interobserver-teaching-eligibility.json')
    for name in ('interobserver2023_teaching.pdf', 'interobserver2023_guide.pdf',
                 'teaching-captions.png', 'guide-page1.png', 'guide-page3.png'):
        bind('raw/' + name, 'owner-cache-only public supplement/caption render; read in place')
    check('Interobserver original teaching and guide PDF hashes',
          sha(root / 'raw/interobserver2023_teaching.pdf') == teaching['teaching_cases_pdf_sha256'] and
          sha(root / 'raw/interobserver2023_guide.pdf') == teaching['reader_guide_pdf_sha256'],
          {'independent_visual_verification': 'All four diagnoses and conditions in cached caption render; guidep1 workbook/PatientsA-I; guidep3 reader access provisions. Outside daily ban.',
           'teaching_donors_not_crosswalked': True, 'full_workbook_access_attempted': False})
    inter = clinical['interobserver2023_jnm.html'][0]['text']
    counts = [int(n) for n in re.findall(r'(?:sarcoma|pancreatic adenocarcinoma|colorectal cancer|genitourinary cancer|miscellaneous cases) \(n = (\d+)\)', inter)]
    check('Interobserver complete macro source counts', counts == [10] * 5,
          {'patients': sum(counts), 'generic_sarcoma_donors': 10,
           'availability': 'Unlocated named workbook does not establish public access; no full50 histology claim.'})

    # Bind later access amendment if the owner has frozen it before this run.
    for file in sorted(root.glob('AVAILABILITY-AMENDMENT*.json')):
        bind(file.name, 'committed additive access clarification; original freeze unchanged')
        amendment = read(file.name)
        check('Interobserver additive availability correction and unchanged originals',
              all(sha(root / r['path']) == r['sha256'] for r in amendment['original_artifacts']) and
              amendment['corrected_disposition']['full_workbook_and_50patient_subtype_roster'] == 'unavailable evidence' and
              amendment['corrected_disposition']['access'] == 'unlocated/access unresolved; not established publicly accessible',
              {'amendment_sha256': sha(file), 'full_workbook': 'unavailable evidence; actual public access unresolved',
               'evaluated': 'five macro categories and four public teaching cases',
               'decision_changed': False, 'private_access_attempted': False})
    output = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Independent original clinical roster arithmetic and source hashes, bounded five-source review',
              'all_checks_passed': all(x['passed'] for x in checks),
              'checks': checks, 'input_bindings': bindings,
              'limitations': ['Originals are owner cache only; read in place, not copied into reviewer or Git.',
                             'Clinical excerpts were reviewed at selected release resolution; excluded tissue sections were not inspected.',
                             'This verifies identity/access suitability and counts, not a biological or imaging effect in EMC.',
                             'All generic identities and donor/date/treatment/cohort-overlap gaps remain unresolved.'],
              'no_new_data_retrieval': True, 'no_EMC_effect_estimation': True}
    args.output.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'passed': output['all_checks_passed'], 'checks': len(checks),
                      'failures': [x['check'] for x in checks if not x['passed']], 'output': str(args.output)}))
    raise SystemExit(0 if output['all_checks_passed'] else 1)


if __name__ == '__main__':
    main()
