#!/usr/bin/env python3
"""Source methods/table identity gate only; never inspect numerical outcomes."""
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
plan = json.loads((ROOT/'SOURCE-GATE-PLAN.json').read_text())
item = plan['source_binding']
data = Path(item['path']).read_bytes()
assert len(data) == item['bytes']
assert hashlib.sha256(data).hexdigest() == item['sha256']
root = ET.fromstring(data)
section = next(s for s in root.iter('sec') if s.attrib.get('id') == 'sec2.4')
method = ' '.join(' '.join(p.itertext()) for p in section.findall('p'))
table = next(s for s in root.iter('table-wrap') if s.attrib.get('id') == 'tab1')
headers = [' '.join(n.itertext()).strip() for n in table.findall('.//thead//th')]
case_ids = [' '.join(list(n)[0].itertext()).strip() for n in table.findall('.//tbody/tr')]
assert case_ids == list(map(str, range(1,14)))
# Whole-source keyword presence test, not value extraction or result reading.
normalized = re.sub('[^a-z0-9]', '', unicodedata.normalize('NFKC', ' '.join(root.itertext())).lower())
terms = {s: s in normalized for s in ['ki67','mib1','mitotic','mitoses']}
assert not any(terms.values())
record = {'source_sha256':item['sha256'],'primary_DOI':'10.1155/2018/9684268','primary_PMID':'29977924','pathological_method_section':'sec2.4','pathological_method':method,'public_table_headers':headers,'all_source_case_ids':case_ids,'case_count':13,'normalized_literal_proliferation_terms_present':terms,'meaning':'No named target assay or linked direct proliferation measurement in inspected public primary. Unspecified IHC on some specimens is not known Ki67 or tumor-cell specificity. No biological absence or full-literature conclusion.','eligible_outcome_values_used':False,'images_or_new_downloads':False}
(ROOT/'SOURCE-METHOD-OBSERVATIONS.json').write_text(json.dumps(record,indent=2)+'\n')
validation = {'status':'PASS','original_source_bindings':1,'original_source_mismatches':0,'all_case_ids':13,'measurement_values_read':False,'scope':'Pathological method text, public table headers and case-ID column, normalized literal assay-name presence only.'}
(ROOT/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps(validation))
