"""Independent read-only source check of R7 clinical linkage; no new retrieval."""
from pathlib import Path
from xml.etree import ElementTree as E
import json,zipfile,hashlib,datetime,collections
R=Path(__file__).resolve().parent
D=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round7/clinical_linkage')
j=json.loads((D/'linkage-evaluation.json').read_text(encoding='utf-8'))
def t(e):return ''.join(e.itertext())
def rows(x,id):return [[t(c) for c in r if c.tag in ['th','td']] for tw in x.findall('.//table-wrap') if tw.get('id')==id for r in tw.findall('.//tr')]
a=E.parse(D/'anthracycline2013.xml').getroot();aa=rows(a,'T2');assert len(aa[1:])==11
raw=[dict(zip(aa[0],r)) for r in aa[1:]]
assert all(r['NR4A3 rearrangement']=='yes' for r in raw)
assert collections.Counter(r['RECIST evaluation'] for r in raw)=={'PR':4,'SD':3,'PD':3,'NV':1}
assert rows(a,'T3')[0]==['Pt ID','S100','Synaptophysin','EMA','PPARγ']
tm=E.parse(D/'temozolomide2017.xml').getroot();tr={tw.get('id'):rows(tm,tw.get('id')) for tw in tm.findall('.//table-wrap')}; emc=[]
for rs in tr.values():
 for r in rs:
  if any('Extraskeletal myxoid chondrosarcoma' in c for c in r):emc.append(r)
assert emc==[['2','Extraskeletal myxoid chondrosarcoma','Sunitinib, radiation, nivolumab','19','SD'],['2','Extraskeletal myxoid chondrosarcoma','PD','2']]
assert any(r and r[0]=='Patient 2' and 'EWSR1-NR4A3' in ' '.join(r) for rs in tr.values() for r in rs)
dv=Path(j['sources']['davis2017']['file']);dx=E.parse(dv).getroot();dvr=[r for tw in dx.findall('.//table-wrap') for r in rows(dx,tw.get('id')) if r and r[0]=='MO-1582'];assert len(dvr)==1 and 'Pazopanib' in ' '.join(dvr[0])
sp=Path(j['sources']['davis2017_supplement2']['file']);w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
with zipfile.ZipFile(sp) as z:s=E.fromstring(z.read('word/document.xml'))
ps=[''.join(v.text or '' for v in p.iter(w+'t')) for p in s.iter(w+'p')]
start=next(i for i,p in enumerate(ps) if 'MO_1582: PATIENT HISTORY' in p);end=next(i for i in range(start+1,len(ps)) if 'MO_1582: SEQUENCING LIBRARIES' in ps[i]);history=ps[start:end]
assert any('10/2014: Started pazopanib' in p for p in history) and any('12/2015: D/C pazopanib' in p for p in history)
paths=[D/x for x in ['RESULTS.txt','COVERAGE.json','linkage-evaluation.json','evaluate_linkage.py','anthracycline2013.xml','sunitinib2012.xml','temozolomide2017.xml']]+[dv,sp]
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'functional_models','scope':'Independent narrow source/eligibility/value challenge from retained files only; no fresh downloads or all-literature audit',
'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
'checks':{'all11_anthracycline_NR4A3_rows':True,'responses':{'PR':4,'SD':3,'PD':3,'NV':1},'Table3_lacks_individual_fusion_columns':True,'temozolomide_all_EMC_rows':emc,'patient2_EWSR1_NR4A3':True,'Davis1582_main_row':dvr[0],'Davis1582_exact_history':history},
'interpretation':'Agree scoped SHELVE. Missing partner mapping and no alternate-fusion comparator prevent treatment-by-partner inference; published sequential courses cannot separate prognosis, selection and treatment effect.',
'material_cautions':['All11 anthracycline NR4A3 cases cannot be split into EWS versus TAF15 from aggregate9/11','Do not derive a treatment interval or growth-modulation ratio from contradictory Davis table/supplement','Temozolomide add-on follows selected pazopanib progression with dose change; no isolated causal effect','Suspected sunitinib2012/2014 extension/overlap lacks a verified individual crosswalk; do not assume12independent patients or prove which cases were reused','No PR/SD counts pooled across heterogeneous definitions/timepoints','Source gaps remain visible; no all-public-data absence claim'],
'no_required_corrections':True,'limits':'No independent full source review of all prior cohorts, blocked sources, or unavailable2014/2019tables; owner source summaries for already-published sunitinib linkage reviewed, no new effect recomputed.'}
(R/'clinical-linkage-independent-review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'review':'PASS','rows11':True,'EMC_temo_case2':True,'Davis_source_discordance_verified':True,'sha256':hashlib.sha256((R/'clinical-linkage-independent-review.json').read_bytes()).hexdigest()}))