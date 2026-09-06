"""Read-only integrity and specimen-link checks; no network or expression analysis."""
import hashlib, html, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parent
PRIOR=ROOT.parent/'atlas-primary-provenance-2026-09-06'
def read(name): return (ROOT/name).read_text(encoding='utf-8')
def clean(s): return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
def field(body,label):
    pat=r'<div class="col-form-label[^\"]*">'+re.escape(label)+r'</div>\s*<div[^>]*>(.*?)</div>'
    return clean(re.search(pat,body,re.S).group(1))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok):
    checks.append({'check':name,'pass':bool(ok)})
    if not ok: raise AssertionError(name)
records=json.loads(read('retrievals.json'))
for r in records:
    if 'sha256' in r:
        p=ROOT/r['file']; check('HTTP bytes '+r['file'],digest(p)==r['sha256'] and p.stat().st_size==r['bytes'])
for d in json.loads(read('input-manifest.json')):
    check('inherited bytes '+d['file'],digest(ROOT/d['file'])==d['sha256'])
rows=json.loads((PRIOR/'2017-controls-table-rows.json').read_text())['Blad1']
case_rows={r[0]:r for r in rows if r and isinstance(r[0],int) and 46<=r[0]<=51}
expected=[(46,3,'71','Male'),(47,5,'35','Female'),(48,4,'40','Male'),(49,7,'48','Female')]
derived=[]
for new,old,age,sex in expected:
    body=read(f'mitelman-case{old}.html'); r=case_rows[new]
    fields={key:field(body,key) for key in ['Sex','Age','Country','Series','Tissue']}
    check(f'S1 explicit publication case link {new}',r[20]==f'9736, Case {old}')
    check(f'case record reference and case {old}',f'Ref No: 9736' in body and f'Case No: {old}' in body)
    check(f'case record demographics {old}',fields['Age']==age and fields['Sex']==sex and r[15]==age+'/'+sex[0])
    check(f'case fields {old}',fields['Country']=='Sweden' and fields['Tissue']=='Tumor biopsy' and fields['Series']=='Unselected')
    derived.append({'case2017':new,'mitelman_reference':9736,'mitelman_case':old,'S1_array_label':None,'fields':fields,'S1_age_sex':r[15],'S1_site':r[16],'S1_sample_type':r[14],'S1_fusion':r[12], 'link_basis':'explicit primary S1 Published column, not demographic matching'})
inv=[r for r in json.loads(read('mitelman-case-page.json'))['data'] if r['CaseNo']=='7']
check('case7 investigations 1 and 2',sorted(r['InvNo'] for r in inv)==[1,2])
check('case7 inv2 patient fields',field(read('mitelman-case7-inv2.html'),'Age')=='48' and field(read('mitelman-case7-inv2.html'),'Sex')=='Female')
helptext=clean(read('mitelman-help.html'))
check('Country fallback definition','Case origin when stated in publication; otherwise, in general the residence of corresponding author.' in helptext)
check('Inv No definition','each consecutive investigation within a case or for a metastatic lesion at a different location.' in helptext)
check('Tissue scope','Tissue used for cytogenetic investigation.' in helptext)
stored=json.loads(read('case-evidence.json'))
check('saved derived case evidence matches source',derived==stored['explicit_case_links'])
check('remaining EMC cases lack prior Published link',case_rows[50][20] is None and case_rows[51][20] is None)
print(json.dumps({'scope':'HTTP hashes, inherited hashes, explicit published case links, curated field semantics; not independent scientific review or expression analysis','passed':len(checks),'failed':0,'checks':checks},indent=2))
