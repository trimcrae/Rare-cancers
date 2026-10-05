#!/usr/bin/env python3
"""Offline source/identity/scope checks. No protein quantities or network."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET,datetime,shutil
P=Path(__file__).resolve().parent
load=lambda name:json.loads((P/name).read_bytes())
h=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
checks=[]
def check(label,value):
 checks.append({'check':label,'pass':bool(value)})
 if not value: raise AssertionError(label)
plan=load('PLAN.json'); closed=load('SOURCE-GATE-CLOSED.json'); port=load('PORTABILITY.json')
check('source stage within frozen deadline',datetime.datetime.fromisoformat(closed['utc'])<datetime.datetime.fromisoformat(plan['scientific_deadline']))
check('before-outcome scope',closed['outcomes_OFF'] and not load('DECISION.json')['numeric_stage'])
for r in port['source_cache']:
 check('exact cache SHA '+Path(r['path']).name,h(r['path'])==r['sha256'])
 check('exact cache byte count '+Path(r['path']).name,Path(r['path']).stat().st_size==r['bytes'])
check('new raw within eight MiB',sum(r['bytes'] for r in port['source_cache'])<=plan['resources']['raw_new_cap_bytes'])
check('free above ten GiB',shutil.disk_usage('/workspace').free>=plan['resources']['free_floor_bytes'])
for r in load('REUSED-INPUT-BINDINGS.json'):
 check('reused hash '+r['repo_relative'],h(r['path'])==r['sha256'])
xml=ET.fromstring((P/'raw/CAM-secretome-primary.xml').read_bytes())
wanted={r['title']:r['paragraphs'] for r in load('CAM-SELECTED-METHOD-OBSERVATIONS.json')}
actual={}
for s in xml.findall('.//body//sec'):
 title=' '.join(s.findtext('title','').split())
 if title in wanted: actual[title]=[' '.join(''.join(t.itertext()).split()) for t in s.findall('./p')]
check('five exact permitted primary-method sections',len(wanted)==5 and wanted==actual)
cell=' '.join(actual['Cell culture'])
for name in ['WEHI-164','U2OS','WEHI-164-Kat2S-T2A-Nluc','WEHI-164-Kat2S-T2A-Nluc-GFP','U2OS-Kat2S-T2A-Nluc','U2OS-Kat2S-T2A-Nluc-GFP']:
 check('specified model '+name,name in cell)
check('explicit mouse fibrosarcoma identity','mouse fibrosarcoma' in cell)
check('explicit human osteosarcoma identity','human osteosarcoma' in cell)
check('41-plex actual assay method','41 distinct' in ' '.join(actual['Multiplex Assay']))
check('no-contact control medium','without contacting cells' in ' '.join(actual['Harvesting of TCM']))
meta=json.loads((P/'raw/matched-protein-primary-metadata.json').read_bytes())['resultList']['result'][0]
proj=load('MATCHED-PROTEIN-PRIMARY-METADATA-PROJECTION.json')
check('exact matched-primary metadata fields',all(proj[k]==meta.get(k) for k in proj))
check('matched source exact PMID/DOI',meta['id']=='31419061' and meta['doi']=='10.1002/prca.201900054')
check('subscription metadata not universal absence',meta['isOpenAccess']=='N' and load('MATCHED-PROTEIN-DOI-ACCESS-RECEIPT.json')['status']==403)
for i,r in enumerate(load('SOURCE-QUERY-RECEIPTS.json'),1):
 raw=json.loads((P/'raw'/f'metadata_query{i}.json').read_bytes())
 check('partial catalogue source count '+str(i),r['hitCount']==raw['hitCount'] and r['returned']==len(raw['resultList']['result']) and r['returned']<r['hitCount'])
check('native count not inferred zero',load('COVERAGE.json')['new_EMC_source_denominator'] is None)
check('no campaign exhaustion',not load('DECISION.json')['campaign_exhausted'])
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'pass_count':len(checks),'failed':0,'scope':'Offline exact source identity, permitted-method extraction, case/condition, budget and scope validation only. No numerical protein or biological validation.'},indent=2))
