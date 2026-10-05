#!/usr/bin/env python3
"""Replay only bibliographic, method, identity and availability gates; no immune numeric outcomes."""
from pathlib import Path
import xml.etree.ElementTree as E
import json, re, hashlib, argparse
ROOT=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--owner-packet',type=Path,default=Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/spatial_protein_immune_gate'));a.add_argument('--raw-dir',type=Path,default=ROOT/'raw');a.add_argument('--output-dir',type=Path,default=ROOT);args=a.parse_args();D=args.owner_packet;OUT=args.output_dir;OUT.mkdir(parents=True,exist_ok=True)
def text(n): return ' '.join(''.join(n.itertext()).split())
raw=args.raw_dir/'PMC12419029.xml';x=E.fromstring(raw.read_bytes());methods=[]
for sec in x.findall('.//body//sec'):
    title=sec.findtext('title','')
    if title=='Clinical Workflow and Validation':
        for p in sec.findall('./p'):
            t=text(p)
            if not re.search(r'\bHLA\b|\bFAP\b|fibroblast activation protein',t,re.I):methods.append({'section':title,'text':t})
for f in x.findall('.//fig'):
    if f.get('id')=='fig1':
        for p in f.findall('./caption/p'):
            t=text(p)
            if t.startswith('(A) Schematic outlining the ImmunoProfile workflow'):
                methods.append({'section':'Figure1 caption workflow text only, no image','text':t.split('(B)')[0].strip()})
availability=[]
for sec in x.findall('.//sec'):
    title=sec.findtext('title','')
    if title in ['DATA SHARING STATEMENT','Data Availability Statement']:
        availability.extend({'section':title,'text':text(p)} for p in sec.findall('.//p'))
alias_paragraphs=[]
for p in x.findall('.//p'):
    t=text(p)
    if re.search(r'extraskeletal|myxoid chondrosarcoma|\bEMCS?\b',t,re.I):
        alias_paragraphs.append(t)
sibling={'source':{'path':str(raw),'bytes':raw.stat().st_size,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest()},'methods':methods,'data_sharing':availability,'explicit_EMC_alias_paragraphs':alias_paragraphs,'interpretation':'No explicit alias paragraph is not an absence proof; rare-type/source-condition roster remains unresolved. Supporting-data tag or data-sharing DOI pointer is not a public numerical matrix. No sibling/new source donor independence inferred.','not_analyzed':'Images, immune count/case outcome tables, other Results paragraphs, numerical spatial coordinates and FAP/HLA fields.'}
(OUT/'SIBLING-PRIMARY-METHOD-EXCERPTS.json').write_text(json.dumps(sibling,indent=2)+'\n')
core=json.loads((D/'source-cache/recent_broader_protein_imaging.json').read_text())
entry=next(a for a in core['resultList']['result'] if str(a.get('id'))=='41092903')
selected={k:entry.get(k) for k in ['id','source','title','doi','pmcid','authorString','isOpenAccess','inPMC','inEPMC','fullTextUrlList','dataLinksTagsList','abstractText']}
m=json.loads((D/'source-cache/pan2025-crossref').read_text())['message']
refs=[a for a in m.get('reference',[]) if a.get('key','').rsplit('_bib',1)[-1] in ['19','20','21','24','25','26']]
out={'official_primary_metadata':selected,'crossref_related_method_and_prior_cohort_references':refs,'crossref_public_data_relationships':m.get('relation',{}),'advertised_database':'Abstract reports curated spatial cells, but provides no donor or cell-matrix linkage. No individual counts or case outcomes inspected.','identity':'No EMC identity established by major type counts, generic sarcoma, title, spatial platform or this citation list.'}
(OUT/'PRIMARY-METADATA-PRIOR-ART-GATE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'sibling_method_excerpt_count':len(methods),'explicit_alias_paragraphs':len(alias_paragraphs),'sibling_data_sharing_sections':len(availability),'method_prior_references':len(refs)},indent=2))
