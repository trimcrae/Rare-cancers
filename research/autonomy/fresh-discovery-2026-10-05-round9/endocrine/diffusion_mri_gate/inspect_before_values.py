#!/usr/bin/env python3
"""Inspect methods/identity/schema; mask all numbers in non-method case text."""
import hashlib,json,re
from pathlib import Path
from xml.etree import ElementTree as ET
from lxml import html
ROOT=Path(__file__).resolve().parent;CACHE=ROOT/'raw-cache'
BAN=('hla','fap','glycan','breakpoint','structural genomic')
def text(node):return ' '.join(''.join(node.itertext()).split())
def blind(t):return re.sub(r'(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?','[NUMBER]',t)
def main():
 out=[]
 for path in sorted(CACHE.glob('PMC*.xml')):
  r=ET.parse(path).getroot();title=text(r.find('./front/article-meta/title-group/article-title'));body=r.find('./body');entry={'source':path.stem,'title':title,'cache_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'methods':[],'blinded_ADC_DWI_body_context':[],'body_EMC_labels':[],'table_headers':[]}
  for sec in body.findall('sec'):
   heading=sec.find('title');name=text(heading) if heading is not None else ''
   if 'method' in name.lower():
    for p in sec.findall('.//p'):
     s=text(p)
     if any(k in s.lower() for k in BAN):continue
     if any(k in s.lower() for k in ['diffusion','adc','b-value','roi','imaging','magnetic resonance','mr images','histologic','histopath','extraskeletal','chondrosarcoma']):entry['methods'].append(s)
  for p in body.findall('.//p'):
   s=text(p)
   if any(k in s.lower() for k in BAN):continue
   if re.search(r'\bADC\b|diffusion|DWI',s,re.I):entry['blinded_ADC_DWI_body_context'].append(blind(s))
   if 'extraskeletal myxoid chondrosarcoma' in s.lower():entry['body_EMC_labels'].append(blind(s))
  for table in body.findall('.//table-wrap'):
   entry['table_headers'].append({'id':table.get('id'),'headers':[text(x) for x in table.findall('.//thead//th')]})
  out.append(entry)
 preview={}
 for name in ['Kandoussi2024-preview.html','Kandoussi2024-table2.html']:
  path=CACHE/name;h=html.fromstring(path.read_bytes());sections=[]
  for e in h.xpath('//h2|//h3'):
   if e.text_content().strip() in ['Material and Methods','Data availability']:
    following=e.xpath('following-sibling::*[1]');sections.append({'heading':e.text_content().strip(),'text':following[0].text_content().strip() if following else None})
  preview[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'method_or_availability':sections,'table_headers':[[e.text_content().strip() for e in t.xpath('.//th')] for t in h.xpath('//table')],'ADC_word_occurrences':len(re.findall(r'\bADC\b|apparent diffusion|diffusion.weighted',path.read_text(),re.I))}
 data={'schema':'emc-r9-diffusion-source-method-identity-before-value/1','eligible_numeric_ADC_values_inspected':False,'nonmethod_case_numbers_masked':True,'sources':out,'publisher_preview_and_table_schema':preview}
 (CACHE/'before-values-source-observations.json').write_text(json.dumps(data,indent=2)+'\n')
 for e in out:
  print(json.dumps({'source':e['source'],'title':e['title'],'method_paragraphs':len(e['methods']),'ADC_DWI_body_contexts':len(e['blinded_ADC_DWI_body_context']),'EMC_labels':len(e['body_EMC_labels']),'headers':e['table_headers']}))
 print('PUBLISHER',json.dumps(preview))

if __name__=='__main__':main()
