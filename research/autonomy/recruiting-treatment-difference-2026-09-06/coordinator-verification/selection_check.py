from pathlib import Path
import json,gzip,zipfile,hashlib,datetime
root=Path(__file__).resolve().parents[4]
z=zipfile.ZipFile(root/'research/autonomy/trial-frozen-baseline-package-2026-09-06/frozen-experiment.zip')
audit=json.loads(z.read('trial-frozen-baseline-2026-09-06/version-audit.json'))
ranks=json.loads(z.read('trial-frozen-baseline-2026-09-06/rankings-EMC.json'))
pages={}
retained=[]
for r in ranks:
    n=r['nct_id'];a=audit[n]; page=a['selected_page']
    if page not in pages:
        data=json.loads(gzip.decompress(z.read('trial-discoverability-2026-09-05/'+page)))
        pages[page]={s['protocolSection']['identificationModule']['nctId']:s for s in data['studies']}
    s=pages[page][n]
    digest=hashlib.sha256(json.dumps(s,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    assert digest==a['selected_record_sha256'],n
    ps=s['protocolSection']; status=ps.get('statusModule',{}).get('overallStatus'); design=ps.get('designModule',{}); purpose=design.get('designInfo',{}).get('primaryPurpose'); st=design.get('studyType')
    assert (status,purpose,st)==(r['status'],r['primary_purpose'],r['study_type']),n
    if status=='RECRUITING' and purpose=='TREATMENT': retained.append(r)
orders={k:sorted([r for r in retained if r['methods'][k]['score']>0],key=lambda r:(-r['methods'][k]['score'],r['nct_id'])) for k in ('O','H','A')}
sets={k:{r['nct_id'] for r in v[:100]} for k,v in orders.items()}
o,h,a=(sets[k] for k in ('O','H','A'))
assert len(ranks)==6182 and len(retained)==737
assert all(r['study_type']=='INTERVENTIONAL' for r in retained)
assert (len(o),len(h&a),len(h-a),len(a-h),len((h|a)-o))==(77,96,4,4,27)
assert o<=h&a
cutoffs={k:[v[99]['methods'][k]['score'],v[100]['methods'][k]['score']] for k,v in orders.items() if len(v)>100}
assert all(x>y for x,y in cutoffs.values())
result={'status':'passed','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive_sha256':hashlib.sha256(Path(z.filename).read_bytes()).hexdigest(),'selected_source_versions_checked':len(ranks),'source_pages':len(pages),'retained':len(retained),'positive_score_counts':{k:len(v) for k,v in orders.items()},'O_selected':len(o),'H_A_common':len(h&a),'H_only':sorted(h-a),'A_only':sorted(a-h),'cutoff_and_next_score':cutoffs,'scope':'Independent structural metadata, source canonical digests and stored-score selection only; no relevance content inspection or labels.'}
Path(__file__).with_name('selection-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('H_only','A_only')}))
