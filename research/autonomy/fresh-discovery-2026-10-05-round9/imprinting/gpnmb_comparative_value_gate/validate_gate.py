#!/usr/bin/env python3
"""Replay only hashes, source identities and condition metadata; never matrix cells."""
import pathlib,json,hashlib,shutil,datetime
P=pathlib.Path(__file__).resolve().parent
h=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
checks=[]
def check(label,ok):
 checks.append({'check':label,'pass':bool(ok)})
 if not ok: raise AssertionError(label)
for x in json.loads((P/'REUSED-INPUT-BINDINGS.json').read_text()):
 check('reused:'+x['path'],h(x['path'])==x['sha256'])
for x in json.loads((P/'SOURCE-DISCOVERY-RECEIPTS.json').read_text()):
 f=P/'raw-cache'/pathlib.Path(x['cache_path']).name
 check('original:'+f.name,h(f)==x['sha256'] and f.stat().st_size==x['bytes'])
 d=json.loads(f.read_text());check('query count:'+x['name'],d['hitCount']==x['hit_count'] and len(d['resultList']['result'])==x['returned_count'])
covered=json.loads((P/'ALL-IDENTIFIABLE-NATIVE-CONDITION-REUSE.json').read_text())
check('13 native Hofvander conditions',len(covered['all13_Hofvander'])==13)
check('12 primary one recurrence',sum(bool(x['primary_lesion']) for x in covered['all13_Hofvander'])==12)
check('all 6 and10 native array conditions',[len(x['conditions']) for x in covered['all16_array_conditions']]==[6,10])
check('ALL four FFPE3SEQ conditions',len(covered['all4_FFPE_3SEQ_conditions'])==4)
card=json.loads((P/'EVALUATED-PRIMARY-PRIOR-ART.json').read_text())['cards'][0]
check('TCGA primary seven explicit groups',card['cohort']=={'DDLPS':50,'ULMS':27,'STLMS':53,'UPS':44,'MFS':17,'SS':10,'MPNST':5})
source=json.loads((P/'raw-cache/gpnmb_sarcoma_primary.json').read_text())
s=next(x for x in source['resultList']['result'] if x['id']=='34656365')
check('primary identity DOI',s['doi']==card['doi'])
check('qualitative published GPNMB conclusion','GPNMB was highly expressed in most sarcomas, with the exception of SS.' in s['abstractText'])
plan=json.loads((P/'PLAN.json').read_text())
check('initial plan exact frozen hash',h(P/'PLAN.json')=='1e635f9e3a2ca6e3f9186b2d891252cef59bb570915c411f033483d0dff1c514')
check('free floor',shutil.disk_usage(P).free>=10737418240)
raw=[x for x in (P/'raw-cache').rglob('*') if x.is_file()]
check('all retained new original/copy bytes within8MiB',sum(x.stat().st_size for x in raw)<=8388608)
output={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_pass':True,'checks':checks,'new_cache_files':len(raw),'new_cache_total_bytes':sum(x.stat().st_size for x in raw),'free_bytes':shutil.disk_usage(P).free,'new_emc_gene_values_statistics_matrices':False,'source_exposure_amendment':'AMENDMENT-01-EXPOSURE-AND-SOURCE-SCOPE.json'}
(P/'VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({'all_pass':True,'checks':len(checks),'raw_bytes':output['new_cache_total_bytes'],'free_bytes':output['free_bytes']}))
