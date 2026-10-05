#!/usr/bin/env python3
"""Validate source identity/cohort/assay scope only; no biochemical endpoints."""
from pathlib import Path
import json, hashlib, xml.etree.ElementTree as ET, zipfile, datetime, shutil
BASE=Path(__file__).resolve().parent
ROOT=Path('/workspace/Rare-cancers')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def text(elem):
    return ' '.join(''.join(elem.itertext()).split())
checks=[]
def check(name, condition):
    checks.append({'name':name,'pass':bool(condition)})
    if not condition:
        raise AssertionError(name)
raw=BASE/'raw-cache/SDHB-UPS-primary.xml'
check('selected primary exact bytes',raw.stat().st_size==154004)
check('selected primary exact source SHA',sha(raw)=='b471db7dd5b58d3743a9332201bf148255d8886d4ce09e6c94e37ba2c519526d')
source=ET.fromstring(raw.read_bytes())
methods=None
for sec in source.findall('.//body/sec'):
    title=sec.find('title')
    if title is not None and text(title)=='Materials and Methods':
        methods=sec
check('exact Materials and Methods section',methods is not None)
cohorts=[]
for sec in methods.iter('sec'):
    title=sec.find('title')
    if title is not None and text(title)=='Tissue cohort':
        cohorts.append((sec.get('id'),[text(x) for x in sec.findall('./p')]))
check('two distinct source tissue cohorts',len(cohorts)==2)
ffpe=next(p[0] for ident,p in cohorts if ident=='s2-1-1')
nmr=next(p[0] for ident,p in cohorts if ident=='s2-3-1')
check('FFPE specimens102 and patients101 exact method tokens','102 formalin-fixed' in ffpe and '101 patients' in ffpe)
check('FFPE stated patient groups51UPS25LMS25DDLPS','51 patients with a UPS' in ffpe and '25 patients with a high-grade LMS' in ffpe and '25 patients with a DDLPS' in ffpe)
check('fresh source16 patients15 tumors','16 patients' in nmr and 'n = 15' in nmr)
check('fresh named chondrosarcoma identity ambiguous','chondrosarcoma' in nmr and 'extraskeletal' not in nmr.lower())
for label in ['three UPS','three LMS','two LPS','dermatofibrosarcoma protuberans','solitary fibrous tumor','synovial sarcoma','clear-cell sarcoma','endometrial stromal sarcoma','adamantinoma']:
    check('fresh source label '+label,label in nmr)
check('normal specimens named but not matched donor matrix','normal tissue samples' in nmr)
check('pathology review and surgical timeframe','dedicated sarcoma pathologist' in nmr and '2021 and 2023' in nmr)
projection=json.loads((BASE/'EXACT-NONRNA-METHOD-COHORT-PROJECTION.json').read_text())
check('compact methods source hash correct',projection['source_sha256']==sha(raw))
check('compact source cohorts replay',[(d['section_id'],d['permitted_method_or_cohort_text']) for d in projection['methods'] if d['section']=='Tissue cohort']==cohorts)
check('no new biochemical numeric authorization',json.loads((BASE/'DECISION.json').read_text())['numeric_authorization'] is False)
condition=json.loads((BASE/'ALL-SOURCE-CONDITION-AND-ASSAY-DISPOSITIONS.json').read_text())
check('15 tumor group accounting explicit',sum(condition['source_groups'][1]['tumor_histotype_counts'].values())==15)
check('16 surgical patients not inferred paired donors',condition['source_groups'][1]['patients']==16 and bool(condition['source_groups'][1]['identity_pending']))
check('native biochemical endpoints closed',condition['biological_quantitative_outcomes_inspected']==0)
check('public Figshare403 preserved',json.loads((BASE/'AUTHOR-LINKED-PUBLIC-DEPOSIT-ACCESS.json').read_text())['error_type']=='HTTPError')
check('supplement response not acceptedOOXML',not zipfile.is_zipfile(BASE/'raw-cache/published-Supplementary-Table8-source'))
check('supplement unavailable scope explicit',json.loads((BASE/'SUPPLEMENT-RESPONSE-DISPOSITION.json').read_text())['actual_document'] is False)
prior=json.loads((BASE/'PRIOR-DECISION-AND-CONDITION-REUSE.json').read_text())
for record in prior['sources']:
    path=ROOT/record['path']
    check('prior source '+record['path'],path.stat().st_size==record['bytes'] and sha(path)==record['sha256'])
locks=json.loads((BASE/'SOURCE-HASHES-AND-PORTABILITY.json').read_text())
for record in locks['raw_cache_only']:
    path=BASE/record['path']
    check('ignored original '+record['path'],path.stat().st_size==record['bytes'] and sha(path)==record['sha256'] and record['git_exported'] is False)
check('newraw budget',locks['new_raw_bytes']<=8388608)
check('free storage at validation',shutil.disk_usage(BASE).free>=10737418240)
output={'date':'2026-10-05','validated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Source hash/cohort/method/access/metadata accounting only. No enzyme, protein, metabolite, drug response or clinical endpoint cells read or recomputed.','checks':checks,'passed':len(checks),'failed':0,'no_outcome_analysis':True}
(BASE/'VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'failed':0,'raw_bytes':locks['new_raw_bytes'],'no_outcomes':True},indent=2))
